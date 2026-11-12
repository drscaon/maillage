"""Drape test in MuJoCo, the counterpart of the Blender drop test.

Same scenario and the same checks as maillage/blender/drop_test.py, built
from the OpenUSD file only (see mujoco_model.py):

* a piece is laid flat on a round pedestal 0.75 m high, its centre clamped
  as in a Cusick drape tester (the vertices over the pedestal are pinned),
  turned at random about the vertical; a piece with pinned vertices (a flag)
  hangs from them instead, its top edge at 2.4 m;
* the pieces fall for 5 s (the Blender test's 120 frames at 24 fps);
* checks: no invalid coordinate; the mass in MuJoCo is the mass in the file;
  limited stretch of the edges (99 % under 10 %, none over 60 %); at most
  0.5 % of the vertices inside the floor or the pedestal; at rest at the end
  (fastest vertex under 0.1 m/s); no MuJoCo warning (an unstable or
  ill-conditioned solve); the Cusick drape coefficient is measured.

Not modelled here: self-collision (Blender's test has it), the stiffer hem
(one stiffness per flex), wind.
"""

from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path

import numpy as np

from .mujoco_model import AIR_DAMPING, RADIUS, flex_xml, floor_friction, model_xml, timestep
from .usd_reader import Piece, find_usd, read_pieces

PEDESTAL_HEIGHT = 0.75
PEDESTAL_FRACTION = 0.6  # pedestal diameter / shorter side of the piece (Cusick tester: 18 / 30 cm)
HANG_TOP = 2.4
STRETCH_P99_MAX = 1.10
STRETCH_MAX = 1.6
PENETRATION_MAX = 0.005
REST_SPEED_MAX = 0.1  # m/s


def pedestal_radius(piece: Piece) -> float:
    return PEDESTAL_FRACTION * min(piece.size) / 2


def hull_area(xy) -> float:
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


def place(piece: Piece, origin_x: float, rng: random.Random):
    """World vertex positions, pinned vertices and the scenario of a piece."""
    p = piece.points - piece.points.mean(axis=0)
    p[:, 2] = 0.0
    L, W = piece.size
    if piece.pin.max() > 0:
        # vertical, hoist (x = -L/2) at the pole, top edge at HANG_TOP
        world = np.c_[p[:, 0] + L / 2 + origin_x, np.zeros(len(p)), p[:, 1] + HANG_TOP - W / 2]
        return world, np.nonzero(piece.pin > 0)[0], "hang"
    a = math.radians(rng.uniform(-45, 45))
    c, s = math.cos(a), math.sin(a)
    world = np.c_[c * p[:, 0] - s * p[:, 1] + origin_x, s * p[:, 0] + c * p[:, 1], p[:, 2]]
    world[:, 2] = PEDESTAL_HEIGHT + RADIUS + 1e-3
    r = pedestal_radius(piece)
    clamp = np.nonzero(np.linalg.norm(p[:, :2], axis=1) < 0.98 * r)[0]
    return world, clamp, "drape"


def run(target, out_dir=None, pieces=4, seconds=5.0, seed=1) -> dict:
    import mujoco

    usd = find_usd(target)
    out = Path(out_dir) if out_dir else usd.parent / "sim_test"
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    chosen = read_pieces(usd)[:pieces]
    dt = timestep(chosen)
    spacing = 1.7 * max(max(p.size) for p in chosen)
    flexes, world, setups = [], [], []
    for i, p in enumerate(chosen):
        x0 = i * spacing
        pts, pinned, scenario = place(p, x0, rng)
        flexes.append(flex_xml(p, pts, pinned, timestep=dt))
        mu = float(p.attrs.get("friction", 0.5))
        if scenario == "drape":
            r = pedestal_radius(p)
            world.append(
                f'<geom name="{p.name}_pedestal" type="cylinder" size="{r:.6g} {PEDESTAL_HEIGHT / 2}" '
                f'pos="{x0:.6g} 0 {PEDESTAL_HEIGHT / 2}" friction="{mu:.4g}" rgba="0.42 0.3 0.2 1"/>'
            )
        else:
            world.append(
                f'<geom name="{p.name}_pole" type="cylinder" size="0.015 1.3" pos="{x0:.6g} 0 1.3" '
                'contype="0" conaffinity="0" rgba="0.6 0.6 0.62 1"/>'
            )
        setups.append((p, pts, scenario, x0))
    xml = model_xml(flexes, "".join(world), timestep=dt, floor=floor_friction(usd))
    (out / "mujoco_drape.xml").write_text(xml + "\n", encoding="utf-8")
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)

    # air drag on every vertex: AIR_DAMPING times its share of the cloth area
    drag = np.zeros(m.nv)
    for f, (p, _, _, _) in enumerate(setups):
        c = AIR_DAMPING * p.area / len(p.points)
        for v in range(m.flex_vertadr[f], m.flex_vertadr[f] + m.flex_vertnum[f]):
            b = m.flex_vertbodyid[v]
            if m.body_dofnum[b]:
                a = m.body_dofadr[b]
                drag[a : a + m.body_dofnum[b]] = c
    steps = int(round(seconds / dt))
    t0 = time.time()
    for _ in range(steps):
        d.qfrc_applied[:] = -drag * d.qvel
        mujoco.mj_step(m, d)
    wall = time.time() - t0
    warnings = {int(i): int(w.number) for i, w in enumerate(d.warning) if w.number}
    xpos = d.flexvert_xpos.reshape(-1, 3)
    # vertex speeds: the free vertices' degrees of freedom
    report = {
        "usd": str(usd),
        "engine": f"MuJoCo {mujoco.__version__}",
        "simulated_s": steps * dt,
        "timestep_s": dt,
        "wall_s": round(wall, 1),
        "mujoco_warnings": warnings,
        "criteria": {
            "stretch_p99_max": STRETCH_P99_MAX,
            "stretch_max": STRETCH_MAX,
            "penetration_max": PENETRATION_MAX,
            "rest_speed_max_m_s": REST_SPEED_MAX,
        },
        "pieces": [],
    }
    for f, (p, start, scenario, x0) in enumerate(setups):
        a, n = m.flex_vertadr[f], m.flex_vertnum[f]
        pts = xpos[a : a + n]
        e = p.edges()
        r0 = np.linalg.norm(start[e[:, 0]] - start[e[:, 1]], axis=1)
        r1 = np.linalg.norm(pts[e[:, 0]] - pts[e[:, 1]], axis=1)
        ratio = r1 / np.maximum(r0, 1e-9)
        speeds = []
        for v in range(a, a + n):
            b = m.flex_vertbodyid[v]
            if m.body_dofnum[b]:
                j = m.body_dofadr[b]
                speeds.append(float(np.linalg.norm(d.qvel[j : j + 3])))
        speed = max(speeds) if speeds else 0.0
        tol = 0.002
        inside = pts[:, 2] < -tol
        drape = None
        if scenario == "drape":
            r = pedestal_radius(p)
            radial = np.linalg.norm(pts[:, :2] - np.array([x0, 0.0]), axis=1)
            inside |= (radial < r - tol) & (pts[:, 2] < PEDESTAL_HEIGHT - tol)
            disc = math.pi * r * r
            drape = (hull_area(pts[:, :2]) - disc) / (p.area - disc)
        # MuJoCo spreads a flex's mass evenly over its vertices; pinned vertices
        # are attached to the world and carry none
        bodies = [m.flex_vertbodyid[v] for v in range(a, a + n)]
        free = [b for b in bodies if m.body_dofnum[b]]
        mass = float(m.body_mass[free].sum())
        expected = p.mass * len(free) / n
        finite = bool(np.isfinite(pts).all())
        res = {
            "name": p.name,
            "fabric": p.attrs.get("fabric"),
            "scenario": scenario,
            "vertices": int(n),
            "mass_kg": round(p.mass, 5),
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
            "mass": bool(abs(mass - expected) <= 1e-4 * p.mass),
            "stretch": res["stretch_p99"] <= STRETCH_P99_MAX and res["stretch_max"] <= STRETCH_MAX,
            "penetration": res["penetration"] <= PENETRATION_MAX,
            "rest": finite and speed <= REST_SPEED_MAX,
            "solver": not warnings,
        }
        res["checks"] = checks
        res["passed"] = all(checks.values())
        report["pieces"].append(res)
    report["passed"] = all(r["passed"] for r in report["pieces"])
    (out / "sim_test.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report"] = str(out / "sim_test.json")
    return report


def summary_lines(report) -> list[str]:
    lines = []
    for r in report["pieces"]:
        failed = [k for k, v in r["checks"].items() if not v]
        lines.append(
            f"{'PASS' if r['passed'] else 'FAIL'}  {r['name']:<22} {r['fabric']:<15} {r['scenario']:<5} "
            f"stretch p99 {r['stretch_p99']:.3f}  speed {r['max_speed_m_s']:.3f} m/s  "
            + (f"drape {r['drape_coefficient']:.2f}  " if r["drape_coefficient"] is not None else "")
            + (f"failed: {', '.join(failed)}" if failed else "")
        )
    return lines


# ------------------------------------------------------------------ one sample per fabric
SAMPLE_CM = 30  # a Cusick sample: a 30 cm disc on an 18 cm pedestal (PEDESTAL_FRACTION)
ANCHORS = ("silk", "cotton_plain", "denim")  # limp, medium, stiff: must drape in that order
ANCHOR_GAP = 0.05  # at least this much drape coefficient between two anchors
SPREAD_MIN = 0.2  # between the fabric that drapes most and the one that drapes least
G = 9.81


def bending_length(fabric: dict) -> float:
    """Pierce's bending length (m), the length a fabric bends under its own weight:
    (bending rigidity / weight per unit area) ** (1/3)."""
    return (fabric["bending_rigidity"] / (fabric["areal_density"] * G)) ** (1 / 3)


def fabric_drape(fabrics=None, out_dir="output/fabric_test", vertices=300, seconds=4.0, seed=1) -> dict:
    """Drape the same sample of each fabric and compare them: fabrics must not drape alike.

    One disc of SAMPLE_CM per fabric, no variation, each in its own simulation (the time step
    follows the fabric). Checks: every drape passes the checks of ``run``; the anchors drape in
    order, limp to stiff, ANCHOR_GAP apart; the drape coefficients spread over SPREAD_MIN (the
    last two only when the fabrics tested include them)."""
    from ..fabrics import FABRICS
    from ..generator import Variations, generate_scene, write_outputs

    names = [fabrics] if isinstance(fabrics, str) else list(fabrics or FABRICS)
    unknown = [n for n in names if n not in FABRICS]
    if unknown:
        raise ValueError(f"unknown fabric(s) {', '.join(unknown)}; choose from {', '.join(FABRICS)}")
    out = Path(out_dir)
    still = Variations(size=False, cut=False, corners=False, fabric=False, color=False)
    rows = []
    for name in names:
        scene = generate_scene(
            "tea_towel", 1, seed, still, vertices=vertices, fabric=name, formats=f"round:{SAMPLE_CM}"
        )
        folder = write_outputs(scene, out / name)
        report = run(folder, pieces=1, seconds=seconds, seed=seed)
        piece = report["pieces"][0]
        rows.append(
            {
                "fabric": name,
                "areal_density_kg_m2": FABRICS[name]["areal_density"],
                "bending_rigidity_nm": FABRICS[name]["bending_rigidity"],
                "tensile_stiffness_n_m": FABRICS[name]["tensile_stiffness"],
                "bending_length_cm": round(bending_length(FABRICS[name]) * 100, 2),
                "drape_coefficient": piece["drape_coefficient"],
                "timestep_s": report["timestep_s"],
                "wall_s": report["wall_s"],
                "passed": piece["passed"],
                "failed": [k for k, v in piece["checks"].items() if not v],
            }
        )
    drape = {r["fabric"]: r["drape_coefficient"] for r in rows}
    checks = {"drapes": all(r["passed"] for r in rows)}
    if all(a in drape for a in ANCHORS):
        steps = [drape[b] - drape[a] for a, b in zip(ANCHORS, ANCHORS[1:], strict=False)]
        checks["anchors_in_order"] = all(step >= ANCHOR_GAP for step in steps)
    if len(rows) == len(FABRICS):
        checks["spread"] = max(drape.values()) - min(drape.values()) >= SPREAD_MIN
    report = {
        "engine": rows and report["engine"],
        "sample": f"disc of {SAMPLE_CM} cm on a pedestal of {SAMPLE_CM * PEDESTAL_FRACTION:g} cm",
        "vertices": vertices,
        "simulated_s": seconds,
        "criteria": {"anchors": list(ANCHORS), "anchor_gap_min": ANCHOR_GAP, "spread_min": SPREAD_MIN},
        "fabrics": rows,
        "checks": checks,
        "passed": all(checks.values()),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "fabric_test.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report"] = str(out / "fabric_test.json")
    return report


def fabric_lines(report) -> list[str]:
    lines = []
    for r in sorted(report["fabrics"], key=lambda r: r["drape_coefficient"]):
        lines.append(
            f"{'PASS' if r['passed'] else 'FAIL'}  {r['fabric']:<15} drape {r['drape_coefficient']:.2f}  "
            f"bending length {r['bending_length_cm']:.2f} cm  tensile {r['tensile_stiffness_n_m']:g} N/m"
            + (f"  failed: {', '.join(r['failed'])}" if r["failed"] else "")
        )
    failed = [k for k, v in report["checks"].items() if not v]
    lines.append(
        ("PASSED" if report["passed"] else f"FAILED: {', '.join(failed)}") + f" ({report['sample']})"
    )
    return lines
