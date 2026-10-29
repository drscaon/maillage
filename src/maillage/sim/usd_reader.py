"""The cloth pieces of a generated OpenUSD scene, as an engine reads them."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pxr import Usd, UsdGeom


@dataclass
class Piece:
    name: str
    points: np.ndarray  # local vertex positions (m)
    triangles: np.ndarray  # (n, 3) vertex indices; quads split in two
    position: np.ndarray  # world translation of the piece (m)
    pin: np.ndarray  # per-vertex pin weight (0 or 1)
    attrs: dict  # maillage:* attributes, without the prefix

    @property
    def mass(self) -> float:
        return float(self.attrs["mass"])

    @property
    def size(self) -> tuple[float, float]:
        return tuple(self.attrs.get("size", (1.0, 1.0)))

    @property
    def area(self) -> float:
        p = self.points[self.triangles]
        return float(0.5 * np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1).sum())

    def edges(self) -> np.ndarray:
        t = self.triangles
        e = np.vstack([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
        return np.unique(np.sort(e, axis=1), axis=0)


def find_usd(path) -> Path:
    path = Path(path)
    if path.is_dir():
        found = sorted(p for p in path.glob("maillage_*.usd*") if "_omniphysics" not in p.stem)
        if not found:
            raise FileNotFoundError(f"no maillage_*.usd* file in {path}")
        return found[0]
    return path


def triangulate(counts, indices) -> np.ndarray:
    """Fan triangulation of polygons (triangles and quads as written by maillage)."""
    tris, i = [], 0
    for n in counts:
        f = indices[i : i + n]
        tris += [(f[0], f[k], f[k + 1]) for k in range(1, n - 1)]
        i += n
    return np.array(tris, np.int64)


def read_pieces(path) -> list[Piece]:
    stage = Usd.Stage.Open(str(find_usd(path)))
    cache = UsdGeom.XformCache()
    cloths = stage.GetPrimAtPath("/World/Cloths")
    out = []
    for prim in cloths.GetChildren() if cloths else []:
        if not prim.IsA(UsdGeom.Mesh):
            continue
        mesh = UsdGeom.Mesh(prim)
        attrs = {}
        for a in prim.GetAttributes():
            if a.GetName().startswith("maillage:"):
                v = a.Get()
                attrs[a.GetName()[len("maillage:") :]] = (
                    tuple(v) if hasattr(v, "__len__") and not isinstance(v, str) else v
                )
        pv = UsdGeom.PrimvarsAPI(prim).GetPrimvar("pin")
        pts = np.array(mesh.GetPointsAttr().Get(), float)
        out.append(
            Piece(
                name=prim.GetName(),
                points=pts,
                triangles=triangulate(
                    list(mesh.GetFaceVertexCountsAttr().Get()), list(mesh.GetFaceVertexIndicesAttr().Get())
                ),
                position=np.array(cache.GetLocalToWorldTransform(prim).ExtractTranslation(), float),
                pin=np.array(pv.Get(), float) if pv and pv.Get() is not None else np.zeros(len(pts)),
                attrs=attrs,
            )
        )
    return out
