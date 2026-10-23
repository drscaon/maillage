"""Blender drop test for Maillage pieces.

Runs inside Blender (it does not import maillage, so Blender's own Python
needs nothing installed):

    blender -b -P drop_test.py -- output/tea_towel [--pieces 4] [--frames 120] [--render]

or, when the `bpy` module is installed (pip install "maillage[blender]"):

    maillage drop-test output/tea_towel --render

For each of the first pieces of a generated scene, it:

1. imports the OpenUSD scene with Blender's USD importer (geometry, UVs,
   textured material, `hem` and `pin` primvars);
2. reads the `maillage:*` attributes (mass, thickness, friction, Blender cloth
   stiffness) with the OpenUSD Python bindings shipped with Blender;
3. sets up Blender's cloth solver: stiffness from the fabric, rescaled to
   the mesh resolution and the piece's real mass, stiffer bending on the hem, pinned vertices,
   collisions and self-collisions;
4. lays the piece flat on a round pedestal, its centre clamped as in a
   Cusick drape tester, and lets the rest fall (or hangs a piece by its
   pinned vertices), then simulates it;
5. checks the result: no invalid coordinates, limited stretch of the edges,
   no penetration of the pedestal or the floor, at rest at the end (draped
   pieces); it also measures how much the piece drapes (Cusick drape
   coefficient);
6. writes drop_test.json, the draped meshes as draped.usdc (with the
   maillage:* attributes copied back) and, with --render, a Cycles image.

Exit code 0 when every piece passes, 1 otherwise.

The cloth parameters are starting values, not calibrated: passing this test
means the asset imports and simulates sanely in Blender, not that it drapes
like the real fabric.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector
from pxr import Usd, UsdGeom

PEDESTAL_HEIGHT = 0.75
BLENDER_VERTEX_MASS = 0.3  # kg, Blender's default cloth vertex mass
PEDESTAL_FRACTION = 0.6  # pedestal diameter / shorter side of the piece (Cusick tester: 18 / 30 cm)
STRETCH_P99_MAX = 1.10  # 99 % of the edges stretched by less than 10 %
STRETCH_MAX = 1.6
PENETRATION_MAX = 0.005  # fraction of vertices allowed inside an obstacle
REST_SPEED_MAX = 0.1  # m/s, fastest vertex over the last frame


# ----------------------------------------------------------------- inputs


def find_usd(path: Path) -> Path:
    if path.is_dir():
        found = sorted(path.glob("maillage_*.usd*"))
        if not found:
            raise SystemExit(f"no maillage_*.usd* file in {path}")
        return found[0]
    return path


def read_pieces(usd_path: Path) -> dict:
    """maillage:* attributes of every cloth mesh, by prim name."""
    stage = Usd.Stage.Open(str(usd_path))
    out = {}
    cloths = stage.GetPrimAtPath("/World/Cloths")
    for prim in cloths.GetChildren() if cloths else []:
        if not prim.IsA(UsdGeom.Mesh):
            continue
        attrs = {}
        for a in prim.GetAttributes():
            name = a.GetName()
            if name.startswith("maillage:"):
                v = a.Get()
                attrs[name[len("maillage:") :]] = (
                    tuple(v) if hasattr(v, "__len__") and not isinstance(v, str) else v
                )
        out[prim.GetName()] = attrs
    return out


# -------------------------------------------------------------- the scene


def _material(name, rgb, roughness=0.6):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:  # Blender < 5: node trees are opt-in
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def _pedestal(name, xy, radius, material):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=radius, depth=PEDESTAL_HEIGHT, location=(xy[0], xy[1], PEDESTAL_HEIGHT / 2)
    )
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o


def _collider(o, friction):
    o.modifiers.new("Collision", "COLLISION")
    o.collision.thickness_outer = 0.002
    o.collision.cloth_friction = friction
    o.collision.damping = 0.1


def _vertex_group(o, attr_name):
    a = o.data.attributes.get(attr_name)
    if a is None:
        return None
    w = np.zeros(len(o.data.vertices), np.float32)
    a.data.foreach_get("value", w)
    idx = np.nonzero(w > 0)[0]
    if len(idx) == 0:
        return None
    g = o.vertex_groups.new(name=attr_name)
    for i in idx:
        g.add([int(i)], float(w[i]), "REPLACE")
    return g.name


def pedestal_radius(props):
    L, W = props.get("size", (1.0, 1.0))
    return PEDESTAL_FRACTION * min(L, W) / 2


def _clamp_group(o, radius):
    co = rest_points(o)
    idx = np.nonzero(np.linalg.norm(co[:, :2], axis=1) < 0.98 * radius)[0]
    g = o.vertex_groups.new(name="clamp")
    g.add([int(i) for i in idx], 1.0, "REPLACE")
    return g.name


def setup_cloth(o, props, frames, self_collision, quality=10):
    nverts = len(o.data.vertices)
    mod = o.modifiers.new("Cloth", "CLOTH")
    s, c = mod.settings, mod.collision_settings
    s.quality = quality
    # Stiffness is given for 1 cm edges and the real vertex mass, rescaled to
    # this mesh so the behaviour does not depend on the resolution (see
    # fabrics.py). The solver then runs with Blender's usual 0.3 kg vertex mass
    # and every stiffness and damping multiplied by the same factor: the
    # accelerations, hence the motion, are unchanged, and Blender's solver
    # tolerances (tuned for that mass range) stay effective; with the real,
    # much smaller mass, stiff fabrics vibrate instead of coming to rest.
    real_mass = float(props.get("mass", 0.1)) / nverts
    lam = BLENDER_VERTEX_MASS / real_mass
    o["maillage_mass_scale"] = lam  # external forces (wind) must be scaled too
    e = edges(o)
    rest = rest_points(o)
    h = float(np.mean(np.linalg.norm(rest[e[:, 0]] - rest[e[:, 1]], axis=1)))
    r = h / float(props.get("blender:referenceEdge", 0.01))
    s.mass = BLENDER_VERTEX_MASS
    s.tension_stiffness = lam * r * props["blender:tensionStiffness"]
    s.compression_stiffness = lam * r * props["blender:compressionStiffness"]
    s.shear_stiffness = lam * r * props["blender:shearStiffness"]
    s.bending_stiffness = lam * props["blender:bendingStiffness"]
    s.air_damping = lam * r * r * props["blender:airDamping"]

    # spring damping: same damping ratio c / sqrt(k m) as Blender's defaults
    # (vertex mass 0.3; tension 15 / 5, shear 5 / 5, bending 0.5 / 0.5)
    def damping(k, k0, c0):
        return c0 * math.sqrt(k / k0)

    s.tension_damping = damping(s.tension_stiffness, 15.0, 5.0)
    s.compression_damping = damping(s.compression_stiffness, 15.0, 5.0)
    s.shear_damping = damping(s.shear_stiffness, 5.0, 5.0)
    s.bending_damping = damping(s.bending_stiffness, 0.5, 0.5)
    s.bending_model = "ANGULAR"
    hem = _vertex_group(o, "hem")
    if hem:
        s.vertex_group_bending = hem
        s.bending_stiffness_max = s.bending_stiffness * props.get("hemBendingFactor", 3.0)
    pin = _vertex_group(o, "pin")
    pinned = bool(pin)
    if not pinned:
        # drape test: the centre is clamped on the pedestal, as between the two
        # discs of a Cusick drape tester
        pin = _clamp_group(o, pedestal_radius(props))
    s.vertex_group_mass = pin
    s.pin_stiffness = 50.0  # maximum: a firm clamp / hoist
    thickness = float(props.get("thickness", 0.5e-3))
    c.collision_quality = 3
    c.distance_min = max(0.004, thickness)
    c.use_self_collision = self_collision
    c.self_distance_min = max(0.003, 0.75 * thickness)
    c.self_friction = 5.0
    mod.point_cache.frame_start = 1
    mod.point_cache.frame_end = frames
    return mod, pinned


def place(o, props, origin, rng, pinned, clearance):
    """Flat on the pedestal (drape test), or hanging for pinned pieces."""
    L, W = props.get("size", (1.0, 1.0))
    if pinned:
        # vertical, hoist (x = -L/2) at the pole, top edge at 2.4 m
        rot = Euler((math.pi / 2, 0.0, 0.0))
        loc = Vector((origin[0] + L / 2, origin[1], 2.4 - W / 2))
    else:
        # flat on the pedestal, clamped at the centre; random turn about z
        rot = Euler((0.0, 0.0, math.radians(rng.uniform(-45, 45))))
        loc = Vector((origin[0], origin[1], PEDESTAL_HEIGHT + clearance))
    o.parent = None
    o.matrix_world = Matrix.Translation(loc) @ rot.to_matrix().to_4x4()


# ------------------------------------------------------------ measurement


def world_points(o, depsgraph):
    ev = o.evaluated_get(depsgraph)
    me = ev.data
    co = np.empty(len(me.vertices) * 3, np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    m = np.array(ev.matrix_world)
    return co @ m[:3, :3].T + m[:3, 3]


def rest_points(o):
    co = np.empty(len(o.data.vertices) * 3, np.float64)
    o.data.vertices.foreach_get("co", co)
    return co.reshape(-1, 3)


def edges(o):
    e = np.empty(len(o.data.edges) * 2, np.int64)
    o.data.edges.foreach_get("vertices", e)
    return e.reshape(-1, 2)


def hull_area(xy):
    """Area of the convex hull of 2-D points (monotone chain)."""
    pts = np.unique(np.round(xy, 9), axis=0)
    if len(pts) < 3:
        return 0.0
    pts = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def half(ps):
        h = []
        for p in ps:
            while len(h) >= 2 and cross(h[-2], h[-1], p) <= 0:
                h.pop()
            h.append(p)
        return h

    hull = np.array(half(pts)[:-1] + half(pts[::-1])[:-1])
    x, y = hull[:, 0], hull[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def flat_area(o):
    p = rest_points(o)[:, :2]
    area = 0.0
    for poly in o.data.polygons:
        q = p[list(poly.vertices)]
        area += 0.5 * (np.dot(q[:, 0], np.roll(q[:, 1], -1)) - np.dot(q[:, 1], np.roll(q[:, 0], -1)))
    return abs(area)


# ------------------------------------------------------------- outputs


def copy_attributes(src_usd: Path, dst_usd: Path, names):
    """Copy the maillage:* attributes onto the meshes of the draped export."""
    src = Usd.Stage.Open(str(src_usd))
    dst = Usd.Stage.Open(str(dst_usd))
    for prim in dst.Traverse():
        if not prim.IsA(UsdGeom.Mesh) or prim.GetName() not in names:
            continue
        sp = src.GetPrimAtPath(f"/World/Cloths/{prim.GetName()}")
        if not sp:
            continue
        for a in sp.GetAttributes():
            if a.GetName().startswith("maillage:"):
                prim.CreateAttribute(a.GetName(), a.GetTypeName(), custom=True).Set(a.Get())
    dst.GetRootLayer().Save()


def setup_render(objects, out_png: Path, samples: int):
    sc = bpy.context.scene
    pts = np.vstack([np.array([o.matrix_world @ Vector(c) for c in o.bound_box]) for o in objects])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    radius = float(np.linalg.norm(hi - lo)) / 2
    # framed on the cloths, a little below their start: they fall and drape
    center = Vector(((lo + hi) / 2).tolist()) - Vector((0.0, 0.0, 0.12 * radius))
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 40
    cam = bpy.data.objects.new("Camera", cam_data)
    sc.collection.objects.link(cam)
    cam.location = center + Vector((0.35 * radius, -2.2 * radius, 1.2 * radius))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.5
    sun.data.angle = math.radians(8)
    sun.rotation_euler = Euler((math.radians(40), math.radians(15), math.radians(30)))
    sc.collection.objects.link(sun)
    world = bpy.data.worlds.new("World")
    if world.node_tree is None:  # Blender < 5
        world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    bg.inputs["Strength"].default_value = 0.6
    sc.world = world
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except (AttributeError, TypeError):
        sc.cycles.use_denoising = False
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    sc.render.filepath = str(out_png)
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"


# ------------------------------------------------------------------ main


def run(
    target,
    out_dir=None,
    pieces=4,
    frames=120,
    seed=1,
    render=False,
    samples=32,
    wind=0.0,
    self_collision=True,
    quality=10,
    animate=0,
) -> dict:
    usd_path = find_usd(Path(target))
    out = Path(out_dir) if out_dir else usd_path.parent / "drop_test"
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    props = read_pieces(usd_path)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.usd_import(filepath=str(usd_path), read_mesh_attributes=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.fps = 24

    names = [n for n in props if n in bpy.data.objects][:pieces]
    for o in list(bpy.data.objects):  # keep only the tested pieces
        if o.name not in names:
            bpy.data.objects.remove(o, do_unlink=True)

    wood = _material("Pedestal", (0.42, 0.30, 0.20), 0.5)
    floor = _material("Floor", (0.30, 0.30, 0.30), 0.8)
    steel = _material("Pole", (0.6, 0.6, 0.62), 0.3)
    spacing = 1.7 * max(max(props[n].get("size", (1, 1))) for n in names)
    objs, pedestals, pinned_any = [], {}, False
    for i, name in enumerate(names):
        o = bpy.data.objects[name]
        p = props[name]
        L, W = p.get("size", (1.0, 1.0))
        origin = (i * spacing, 0.0)
        mod, pinned = setup_cloth(o, p, frames, self_collision, quality)
        mu = float(p.get("friction", 0.5))
        if pinned:
            pinned_any = True
            bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=2.6, location=(origin[0], 0.0, 1.3))
            bpy.context.object.data.materials.append(steel)
            bpy.context.object.name = f"{name}_pole"
            mod.settings.effector_weights.wind = 1.0
        else:
            t = _pedestal(f"{name}_pedestal", origin, pedestal_radius(p), wood)
            _collider(t, 10.0 * mu)
            pedestals[name] = t
            mod.settings.effector_weights.wind = 0.0
        place(o, p, origin, rng, pinned, mod.collision_settings.distance_min + 0.001)
        objs.append(o)

    ground_size = spacing * (len(names) + 2) + 6.0
    bpy.ops.mesh.primitive_plane_add(size=ground_size, location=((len(names) - 1) * spacing / 2, 0.0, 0.0))
    ground = bpy.context.object
    ground.name = "Floor"
    ground.data.materials.append(floor)
    _collider(ground, 5.0)

    if wind > 0 and pinned_any:
        bpy.ops.object.effector_add(type="WIND", location=(-2.0, -0.5, 1.8))
        w = bpy.context.object
        w.rotation_euler = Euler((0.0, math.radians(90), math.radians(-10)))
        # Blender's wind is a force: with the vertex mass scaled up by lam, the
        # force is scaled by lam too, per piece through its effector weight
        hung = [o for o in objs if o.modifiers["Cloth"].settings.effector_weights.wind > 0]
        lam_max = max(o["maillage_mass_scale"] for o in hung)
        for o in hung:
            o.modifiers["Cloth"].settings.effector_weights.wind = o["maillage_mass_scale"] / lam_max
        w.field.strength = wind * lam_max
        w.field.noise = 0.6 * wind
        w.field.seed = seed

    frames_dir = None
    if animate:
        # small Cycles renders of every `animate`-th frame, for an animated GIF
        frames_dir = out / "frames"
        frames_dir.mkdir(exist_ok=True)
        for old in frames_dir.glob("frame_*.png"):
            old.unlink()
        setup_render(objs, out / "drop_test.png", samples)
        sc.render.resolution_x, sc.render.resolution_y = 800, 450

    # simulate frame by frame (the cloth cache needs every frame in order)
    rest = {o.name: rest_points(o) for o in objs}
    prev = None
    for f in range(1, frames + 1):
        sc.frame_set(f)
        if frames_dir is not None and (f == 1 or f % animate == 0):
            sc.render.filepath = str(frames_dir / f"frame_{f:04d}.png")
            bpy.ops.render.render(write_still=True)
        if f >= frames - 1:
            dg = bpy.context.evaluated_depsgraph_get()
            cur = {o.name: world_points(o, dg) for o in objs}
            if f == frames:
                last, before = cur, prev
            prev = cur

    report = {
        "usd": str(usd_path),
        "frames": frames,
        "fps": sc.render.fps,
        "blender": bpy.app.version_string,
        "criteria": {
            "stretch_p99_max": STRETCH_P99_MAX,
            "stretch_max": STRETCH_MAX,
            "penetration_max": PENETRATION_MAX,
            "rest_speed_max_m_s": REST_SPEED_MAX,
        },
        "pieces": [],
    }
    for o in objs:
        p = props[o.name]
        pts = last[o.name]
        e = edges(o)
        r0 = np.linalg.norm(rest[o.name][e[:, 0]] - rest[o.name][e[:, 1]], axis=1)
        r1 = np.linalg.norm(pts[e[:, 0]] - pts[e[:, 1]], axis=1)
        ratio = r1 / np.maximum(r0, 1e-9)
        speed = float(np.max(np.linalg.norm(pts - before[o.name], axis=1))) * sc.render.fps
        tol = 0.002
        inside = pts[:, 2] < -tol
        t = pedestals.get(o.name)
        drape = None
        if t is not None:
            r = t.dimensions.x / 2
            c = np.array(t.location)
            radial = np.linalg.norm(pts[:, :2] - c[:2], axis=1)
            inside |= (radial < r - tol) & (pts[:, 2] < PEDESTAL_HEIGHT - tol)
            # Cusick drape coefficient: 1 = stays flat, 0 = hangs straight down
            disc, flat = math.pi * r * r, flat_area(o)
            drape = (hull_area(pts[:, :2]) - disc) / (flat - disc)
        pinned = any(g.name == "pin" for g in o.vertex_groups)
        finite = bool(np.all(np.isfinite(pts)))
        res = {
            "name": o.name,
            "fabric": p.get("fabric"),
            "pattern": p.get("pattern"),
            "scenario": "hang" if pinned else "drape",
            "vertices": len(pts),
            "mass_kg": round(float(p.get("mass", 0.0)), 5),
            "finite": finite,
            "stretch_p99": round(float(np.percentile(ratio, 99)), 4),
            "stretch_max": round(float(ratio.max()), 4),
            "compression_p01": round(float(np.percentile(ratio, 1)), 4),
            "penetration": round(float(inside.mean()), 5),
            "max_speed_m_s": round(speed, 4),
            "drape_coefficient": None if drape is None else round(float(drape), 4),
            "lowest_point_m": round(float(pts[:, 2].min()), 4),
        }
        checks = {
            "finite": finite,
            "stretch": res["stretch_p99"] <= STRETCH_P99_MAX and res["stretch_max"] <= STRETCH_MAX,
            "penetration": res["penetration"] <= PENETRATION_MAX,
            "at_rest": pinned or speed <= REST_SPEED_MAX,
        }
        res["checks"] = checks
        res["passed"] = all(checks.values())
        report["pieces"].append(res)
    report["passed"] = all(r["passed"] for r in report["pieces"])

    # draped meshes, with the physical attributes copied back
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    draped = out / "draped.usdc"
    bpy.ops.wm.usd_export(
        filepath=str(draped),
        selected_objects_only=True,
        export_animation=False,
        export_materials=True,
        relative_paths=True,
    )
    copy_attributes(usd_path, draped, set(names))
    report["draped_usd"] = str(draped)

    if render:
        for o in objs:
            sol = o.modifiers.new("Thickness", "SOLIDIFY")
            sol.thickness = max(0.001, float(props[o.name].get("thickness", 0.5e-3)))
            sol.offset = 0.0
        if sc.camera is None:
            setup_render(objs, out / "drop_test.png", samples)
        sc.render.resolution_x, sc.render.resolution_y = 1600, 900
        sc.render.filepath = str(out / "drop_test.png")
        bpy.ops.render.render(write_still=True)
        report["render"] = str(out / "drop_test.png")

    if frames_dir is not None:
        report["frames_dir"] = str(frames_dir)
    (out / "drop_test.json").write_text(json.dumps(report, indent=2) + "\n")
    report["report"] = str(out / "drop_test.json")
    return report


def build_parser():
    ap = argparse.ArgumentParser(prog="drop_test.py", description="Blender cloth drop test for Maillage")
    ap.add_argument("target", help="a generated folder (output/<preset>) or a maillage_*.usdc file")
    ap.add_argument("--out", default=None, help="output folder (default: <folder>/drop_test)")
    ap.add_argument("--pieces", type=int, default=4, help="number of pieces tested (default: 4)")
    ap.add_argument("--frames", type=int, default=120, help="frames simulated at 24 fps (default: 120)")
    ap.add_argument("--seed", type=int, default=1, help="random drop poses (default: 1)")
    ap.add_argument("--render", action="store_true", help="render a Cycles image of the result")
    ap.add_argument("--samples", type=int, default=32, help="Cycles samples (default: 32)")
    ap.add_argument("--wind", type=float, default=0.0, help="wind strength on hung pieces (default: 0)")
    ap.add_argument(
        "--animate",
        type=int,
        default=0,
        help="render every N-th frame to frames/ for a GIF (default: 0, off)",
    )
    ap.add_argument("--quality", type=int, default=10, help="cloth solver steps per frame (default: 10)")
    ap.add_argument(
        "--self-collision",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="cloth self-collisions (slower, more realistic folds)",
    )
    return ap


def summary_lines(report):
    lines = []
    for r in report["pieces"]:
        status = "PASS" if r["passed"] else "FAIL " + ",".join(k for k, v in r["checks"].items() if not v)
        lines.append(
            f"{r['name']:<22} {r['scenario']:<6} stretch p99 {r['stretch_p99']:.3f}  "
            f"penetration {r['penetration']:.2%}  speed {r['max_speed_m_s']:.3f} m/s  "
            + (f"drape {r['drape_coefficient']:.2f}  " if r["drape_coefficient"] is not None else "")
            + status
        )
    return lines


def main(argv=None):
    if argv is None:
        if "--" in sys.argv:  # blender -b -P drop_test.py -- ...
            argv = sys.argv[sys.argv.index("--") + 1 :]
        elif Path(sys.argv[0]).name == Path(__file__).name:  # python drop_test.py ... (bpy module)
            argv = sys.argv[1:]
        else:
            argv = []
    args = build_parser().parse_args(argv)
    report = run(
        args.target,
        args.out,
        args.pieces,
        args.frames,
        args.seed,
        args.render,
        args.samples,
        args.wind,
        args.self_collision,
        args.quality,
        args.animate,
    )
    for line in summary_lines(report):
        print(line)
    print(f"report: {report['report']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
