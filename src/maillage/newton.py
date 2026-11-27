"""Newton export: the cloths as surface deformables, with the AOUSD proposal's schemas.

Written as an OpenUSD layer over the main file, ``maillage_<preset>_newton.usda``, which
sublayers ``maillage_<preset>.usdc`` and adds only physics opinions: the main file stays
engine-neutral. Newton 1.8 reads the deformable schemas of the AOUSD Physics working group's
proposal (``Physics*Deformable*``, ``physics:*``), not NVIDIA's OmniPhysics ones; this layer is
the OmniPhysics layer (omniphysics.py) written with those names:

  /World/Cloths/<piece>               the cloth mesh, its own simulation mesh:
                                      PhysicsDeformableBodyAPI (physics:mass = maillage:mass)
                                      + PhysicsSurfaceDeformableSimAPI (rest shape points and
                                        triangles, flat rest bend angles, the shell thickness
                                        as physics:thicknesses, one for the whole piece)
                                      + UsdPhysics CollisionAPI
                                      faces split into triangles if the mesh has quads
  /World/Cloths/<piece>/Looks/PhysNewton_<fabric>
                                      PhysicsSurfaceDeformableMaterialAPI: Young's modulus
                                      from the fabric's tensile stiffness and bending rigidity
                                      (fabrics.shell), Poisson's ratio, density, friction

The proposal is a draft: its names may change, and this layer with them. Not exported, as in
the OmniPhysics layer: pinned vertices (a flag's hoist corners), the stiffer hem.

``check()`` verifies the structure; Primvaria's CI opens the layers in Newton
(scripts/newton_check.py).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from pxr import Sdf, Usd, UsdGeom, UsdPhysics, UsdShade, Vt

from .contract import write_material_label
from .fabrics import FABRICS, shell
from .sim.usd_reader import find_usd, triangulate

SUFFIX = "_newton"
BODY_APIS = ("PhysicsDeformableBodyAPI", "PhysicsSurfaceDeformableSimAPI")
MATERIAL_API = "PhysicsSurfaceDeformableMaterialAPI"
_F = Sdf.ValueTypeNames


def overlay_path(usd: Path) -> Path:
    return Path(usd).with_name(f"{Path(usd).stem}{SUFFIX}.usda")


def _material(stage, piece, fabric: str) -> UsdShade.Material:
    """The deformable material of a piece, inside it: a piece referenced alone keeps it."""
    mat = UsdShade.Material.Define(stage, f"{piece.GetPath()}/Looks/PhysNewton_{fabric}")
    write_material_label(mat, fabric)
    prim = mat.GetPrim()
    prim.AddAppliedSchema(MATERIAL_API)
    fab = FABRICS[fabric]
    E, t = shell(fab)
    for name, value in (
        ("physics:youngsModulus", E),
        ("physics:poissonsRatio", fab["poissons_ratio"]),
        ("physics:density", fab["areal_density"] / t),  # kg/m³: areal density over the shell thickness
        ("physics:staticFriction", fab["friction"]),
        ("physics:dynamicFriction", fab["friction"]),
    ):
        prim.CreateAttribute(name, _F.Float).Set(float(value))
    return mat


def write_overlay(usd) -> Path:
    usd = find_usd(usd)
    out = overlay_path(usd)
    out.unlink(missing_ok=True)
    layer = Sdf.Layer.CreateNew(str(out))
    layer.subLayerPaths.append(f"./{usd.name}")
    stage = Usd.Stage.Open(layer)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)
    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    for prim in stage.GetPrimAtPath("/World/Cloths").GetChildren():
        if not prim.IsA(UsdGeom.Mesh):
            continue
        mesh = UsdGeom.Mesh(prim)
        counts = list(mesh.GetFaceVertexCountsAttr().Get())
        tris = triangulate(counts, list(mesh.GetFaceVertexIndicesAttr().Get()))
        if any(n != 3 for n in counts):  # the simulation mesh must be made of triangles
            mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([3] * len(tris)))
            mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray.FromNumpy(tris.ravel().astype(np.int32)))
        for api in BODY_APIS:
            prim.AddAppliedSchema(api)
        UsdPhysics.CollisionAPI.Apply(prim)
        prim.CreateAttribute("physics:mass", _F.Float).Set(float(prim.GetAttribute("maillage:mass").Get()))
        prim.CreateAttribute("physics:restShapePoints", _F.Point3fArray).Set(mesh.GetPointsAttr().Get())
        prim.CreateAttribute("physics:restTriVertexIndices", _F.Int3Array).Set(
            Vt.Vec3iArray.FromNumpy(tris.astype(np.int32))
        )
        prim.CreateAttribute(
            "physics:restBendAnglesDefault", _F.Token, variability=Sdf.VariabilityUniform
        ).Set("flat")
        fabric = prim.GetAttribute("maillage:fabric").Get()
        _, t = shell(FABRICS[fabric])
        prim.CreateAttribute("physics:thicknesses", _F.FloatArray).Set([float(t)])
        prim.CreateAttribute("physics:thicknesses:elementType", _F.Token).Set("constant")
        material = _material(stage, prim, fabric)
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(
            material, UsdShade.Tokens.weakerThanDescendants, "physics"
        )
    layer.Save()
    return out


def check(path) -> list[str]:
    """Structural problems of a Newton layer (empty: none)."""
    path = Path(path)
    stage = Usd.Stage.Open(str(path))
    problems = []
    below = list(Sdf.Layer.FindOrOpen(str(path)).subLayerPaths)
    if len(below) != 1 or Path(below[0]).stem != path.stem.removesuffix(SUFFIX):
        problems.append(f"its only sublayer must be the file it is named after: {below}")
    cloths = [p for p in stage.GetPrimAtPath("/World/Cloths").GetChildren() if p.IsA(UsdGeom.Mesh)]
    if not cloths:
        problems.append("no cloth")
    for prim in cloths:
        name = prim.GetName()
        listed = prim.GetMetadata("apiSchemas")
        names = set(listed.GetAddedOrExplicitItems()) if listed else set()
        missing = [a for a in (*BODY_APIS, "PhysicsCollisionAPI") if a not in names]
        if missing:
            problems.append(f"{name}: missing {', '.join(missing)}")
        mesh = UsdGeom.Mesh(prim)
        counts = list(mesh.GetFaceVertexCountsAttr().Get())
        if any(n != 3 for n in counts):
            problems.append(f"{name}: simulation mesh not made of triangles")
        rest = prim.GetAttribute("physics:restTriVertexIndices").Get()
        if rest is None or len(rest) != len(counts):
            problems.append(f"{name}: rest triangles do not match the faces")
        rest_pts = prim.GetAttribute("physics:restShapePoints").Get()
        if rest_pts is None or not np.allclose(np.array(rest_pts), np.array(mesh.GetPointsAttr().Get())):
            problems.append(f"{name}: rest shape differs from the points")
        mass = prim.GetAttribute("physics:mass").Get()
        if mass is None or abs(mass - prim.GetAttribute("maillage:mass").Get()) > 1e-6:
            problems.append(f"{name}: mass differs from maillage:mass")
        t = prim.GetAttribute("physics:thicknesses").Get()
        if not t or len(t) != 1 or not t[0] > 0:
            problems.append(f"{name}: no positive thickness")
        mat, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial("physics")
        if not mat:
            problems.append(f"{name}: no physics material")
            continue
        m = mat.GetPrim()
        for attr in ("physics:youngsModulus", "physics:density"):
            v = m.GetAttribute(attr).Get()
            if v is None or not v > 0:
                problems.append(f"{name}: {attr} not positive")
        nu = m.GetAttribute("physics:poissonsRatio").Get()
        if nu is None or not 0 <= nu < 0.5:
            problems.append(f"{name}: Poisson's ratio out of [0, 0.5)")
    return problems


def main(argv=None) -> int:
    """python -m maillage.newton FILE_OR_FOLDER...: check Newton layers."""
    import sys

    paths = sys.argv[1:] if argv is None else argv
    files = []
    for p in map(Path, paths):
        files += sorted(p.rglob(f"*{SUFFIX}.usda")) if p.is_dir() else [p]
    bad = 0
    for f in files:
        problems = check(f)
        bad += bool(problems)
        for msg in problems:
            print(f"{f}: {msg}")
    print(f"{len(files)} Newton layers checked, {bad} with problems")
    return 1 if bad or not files else 0


if __name__ == "__main__":
    raise SystemExit(main())
