"""Generation of a set of textile pieces from a preset."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from . import mesh as meshing
from . import texture
from .fabrics import FABRICS
from .formats import describe, parse_formats
from .outline import Cut, Outline
from .presets import PRESETS

# independent random streams per piece, one per aspect: turning a variation off
# leaves the draws of the other aspects unchanged
_STREAMS = {"format": 0, "size": 1, "corners": 2, "cut": 3, "fabric": 4, "color": 5, "mesh": 6, "weave": 7}


@dataclass
class Variations:
    """Which aspects vary from one piece to the next (all on by default)."""

    size: bool = True  # format drawn from the preset, size around it (off: first format, exact)
    cut: bool = True  # wavy edges and skew (off: perfect cut)
    corners: bool = True  # corner radius drawn (off: middle of the range)
    fabric: bool = True  # fabric drawn from the preset's mix (off: first fabric)
    color: bool = True  # pattern and colours drawn (off: first pattern, first colours)


@dataclass
class Piece:
    name: str
    fabric: str
    shape: str
    nominal: tuple  # (length, width) in m
    length: float
    width: float
    corner_radius: float
    pattern: dict
    mesh: meshing.SurfaceMesh
    uv: np.ndarray
    hem: np.ndarray
    pin: np.ndarray
    metrics: dict
    mass: float
    image: np.ndarray
    position: tuple = (0.0, 0.0, 0.0)

    @property
    def color(self) -> np.ndarray:
        return texture.mean_color(self.image)


@dataclass
class Scene:
    preset_key: str
    preset: dict
    pieces: list
    seed: int
    topology: str
    vertices: int
    variations: Variations = field(default_factory=Variations)


def _rng(seed: int, index: int, stream: str) -> np.random.Generator:
    return np.random.default_rng([seed, index, _STREAMS[stream]])


def _weighted(rng, weights: dict):
    keys = list(weights)
    p = np.asarray([weights[k] for k in keys], float)
    return keys[int(rng.choice(len(keys), p=p / p.sum()))]


def _hoist_pins(points: np.ndarray, length: float, width: float, radius: float) -> np.ndarray:
    pin = np.zeros(len(points))
    xy = points[:, :2]
    for corner in ((-length / 2, -width / 2), (-length / 2, width / 2)):
        d = np.linalg.norm(xy - np.asarray(corner), axis=1)
        pin[d <= max(radius, d.min() + 1e-9)] = 1.0
    return pin


def make_piece(
    preset_key: str,
    index: int,
    seed: int,
    var: Variations,
    topology: str,
    vertices: int,
    fabric: str | None = None,
    formats: list[dict] | None = None,
) -> Piece:
    pr = PRESETS[preset_key]
    formats = formats or pr["formats"]
    if topology == "grid":
        formats = [f for f in formats if f["shape"] == "rect"]
        if not formats:
            raise ValueError("the grid topology needs at least one rectangular format")

    if var.size:
        fmt = formats[_weighted(_rng(seed, index, "format"), {i: f["weight"] for i, f in enumerate(formats)})]
        k = 1.0 + pr["tolerance"] * _rng(seed, index, "size").standard_normal(2).clip(-2.5, 2.5)
    else:
        fmt, k = formats[0], np.ones(2)
    L, W = fmt["length"] / 100 * k[0], fmt["width"] / 100 * k[1]

    r_lo, r_hi = pr["corner_radius"]
    if topology == "grid" or fmt["shape"] != "rect":
        radius = 0.0
    elif var.corners:
        radius = _rng(seed, index, "corners").uniform(r_lo, r_hi) / 100
    else:
        radius = (r_lo + r_hi) / 200

    if var.cut:
        rng = _rng(seed, index, "cut")
        w_lo, w_hi = pr["cut"]["waviness_mm"]
        cut = Cut.random(rng, rng.uniform(w_lo, w_hi), pr["cut"]["skew_deg"])
    else:
        cut = Cut()

    if fabric is None:
        rng = _rng(seed, index, "fabric")
        fabric = _weighted(rng, pr["fabrics"]) if var.fabric else next(iter(pr["fabrics"]))

    if var.color:
        rng = _rng(seed, index, "color")
        pattern = texture.draw_pattern(
            rng, _weighted(rng, pr["patterns"]), pr["base_colors"], pr["accent_colors"]
        )
    else:
        rng = np.random.default_rng(0)
        first = next(iter(pr["patterns"]))
        pattern = texture.draw_pattern(
            rng, first, pr["base_colors"][:1], pr["accent_colors"][:1] + ["#000000"]
        )

    outline = Outline(fmt["shape"], L, W, radius, cut)
    m = meshing.build(outline, topology, vertices, _rng(seed, index, "mesh"))
    met = meshing.metrics(m)

    pts = m.points
    uv = np.stack([(pts[:, 0] + L / 2) / L, (pts[:, 1] + W / 2) / W], axis=1)
    bnd = pts[m.boundary, :2]
    hem = (meshing.distance_to_polygon(bnd, pts[:, :2]) <= pr["hem"] / 100 + 1e-9).astype(float)
    if pr.get("pins") == "hoist":
        pin = _hoist_pins(pts, L, W, max(0.025, 1.1 * met["edge_mean_mm"] / 1000))
    else:
        pin = np.zeros(len(pts))

    fab = FABRICS[fabric]
    return Piece(
        name=f"{preset_key}_{index:03d}",
        fabric=fabric,
        shape=fmt["shape"],
        nominal=(fmt["length"] / 100, fmt["width"] / 100),
        length=L,
        width=W,
        corner_radius=outline.corner_radius,
        pattern=pattern,
        mesh=m,
        uv=uv,
        hem=hem,
        pin=pin,
        metrics=met,
        mass=fab["areal_density"] * met["area_m2"],
        image=texture.render(pattern, L, W, _rng(seed, index, "weave")),
    )


def _layout(pieces: list, gap: float = 0.1) -> None:
    """Lay the pieces flat on the ground, in rows."""
    cols = math.ceil(math.sqrt(len(pieces)))
    cell_x = max(p.length for p in pieces) + gap
    cell_y = max(p.width for p in pieces) + gap
    for i, p in enumerate(pieces):
        r, c = divmod(i, cols)
        z = FABRICS[p.fabric]["thickness"] / 2
        p.position = (c * cell_x, -r * cell_y, z)


def generate_scene(
    preset: str = "tea_towel",
    count: int = 12,
    seed: int = 1,
    variations: Variations | None = None,
    topology: str = "tri",
    vertices: int = 1500,
    fabric: str | list[str] | None = None,
    formats=None,
) -> Scene:
    """Generate `count` distinct pieces of a preset, laid flat side by side.

    `fabric` forces one fabric for every piece instead of the preset's mix; a
    list of fabrics is used in turn (piece i gets fabric[i % len]).
    `formats` replaces the preset's sizes and shapes: a list of formats, or a
    comma-separated string, drawn by weight, e.g. "50x70, oval:140x200@2,
    round:150" (see formats.py)."""
    if preset not in PRESETS:
        raise ValueError(f"unknown preset {preset!r}; see `maillage list`")
    if count < 1:
        raise ValueError(f"count must be at least 1, got {count}")
    if vertices < 16:
        raise ValueError(f"vertices must be at least 16, got {vertices}")
    if topology not in meshing.TOPOLOGIES:
        raise ValueError(f"unknown topology {topology!r}, expected one of {meshing.TOPOLOGIES}")
    fabrics = [fabric] if isinstance(fabric, str) else list(fabric or [])
    for f in fabrics:
        if f not in FABRICS:
            raise ValueError(f"unknown fabric {f!r}; see `maillage list`")
    custom = parse_formats(formats) if formats is not None else None
    var = variations or Variations()
    pieces = [
        make_piece(
            preset, i, seed, var, topology, vertices, fabrics[i % len(fabrics)] if fabrics else None, custom
        )
        for i in range(count)
    ]
    _layout(pieces)
    return Scene(preset, PRESETS[preset], pieces, seed, topology, vertices, var)


def summarize(scene: Scene) -> dict:
    ps = scene.pieces

    def stat(key):
        v = np.asarray([p.metrics[key] for p in ps], float)
        return {"min": float(v.min()), "mean": float(v.mean()), "max": float(v.max())}

    return {
        "preset": scene.preset_key,
        "label": scene.preset["label"],
        "count": len(ps),
        "seed": scene.seed,
        "topology": scene.topology,
        "target_vertices": scene.vertices,
        "variations": asdict(scene.variations),
        "fabrics": dict(Counter(p.fabric for p in ps)),
        "patterns": dict(Counter(p.pattern["pattern"] for p in ps)),
        "shapes": dict(Counter(p.shape for p in ps)),
        "formats": dict(
            Counter(
                describe({"width": p.nominal[1] * 100, "length": p.nominal[0] * 100, "shape": p.shape})
                for p in ps
            )
        ),
        "mass_kg": {k: round(v, 4) for k, v in _minmeanmax([p.mass for p in ps]).items()},
        "vertices": stat("vertices"),
        "edge_mean_mm": stat("edge_mean_mm"),
        "min_angle_deg": stat("min_angle_deg"),
    }


def _minmeanmax(values):
    v = np.asarray(values, float)
    return {"min": float(v.min()), "mean": float(v.mean()), "max": float(v.max())}


def write_outputs(scene: Scene, out_root: str | Path = "output") -> Path:
    """Write the OpenUSD scene, its OmniPhysics layer and MuJoCo model, textures, a CSV table
    and a summary. Returns the folder."""
    from .usd_export import export_stage

    out = Path(out_root) / scene.preset_key
    (out / "textures").mkdir(parents=True, exist_ok=True)
    for p in scene.pieces:
        texture.write_png(out / "textures" / f"{p.name}.png", p.image)
    usd = export_stage(out / f"maillage_{scene.preset_key}.usdc", scene)
    # engine-specific exports, read back from the file
    from .omniphysics import write_overlay
    from .sim.mujoco_model import export as export_mjcf

    write_overlay(usd)
    export_mjcf(usd)

    with open(out / "pieces.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["name", "fabric", "shape", "pattern", "length_m", "width_m", "corner_radius_m", "mass_kg"]
            + list(scene.pieces[0].metrics)
        )
        for p in scene.pieces:
            w.writerow(
                [p.name, p.fabric, p.shape, p.pattern["pattern"], f"{p.length:.4f}", f"{p.width:.4f}"]
                + [f"{p.corner_radius:.4f}", f"{p.mass:.5f}"]
                + [round(v, 5) if isinstance(v, float) else v for v in p.metrics.values()]
            )
    (out / "summary.json").write_text(
        json.dumps(summarize(scene), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return out
