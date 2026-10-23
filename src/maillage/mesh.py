"""Surface meshes of textile pieces, and their quality metrics.

Two topologies:

- "tri": near-equilateral triangles. The cut outline is sampled at the target
  edge length, the inside is filled with a jittered hexagonal lattice, and the
  points are joined by a Delaunay triangulation. Works for any outline
  (rounded corners, round tablecloths). Recommended for cloth solvers.
- "grid": a structured quad grid stretched over the four cut edges of a
  rectangular piece (transfinite / Coons interpolation), the topology of a
  woven fabric. Corners stay sharp (no rounding); rectangles only.

The mesh lies in the z = 0 plane, faces oriented towards +z.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.spatial import Delaunay

from .outline import Outline

TOPOLOGIES = ("tri", "grid")


@dataclass
class SurfaceMesh:
    points: np.ndarray  # (N, 3) float, metres
    face_counts: np.ndarray  # (F,) int, 3 or 4
    face_indices: np.ndarray  # (sum(face_counts),) int
    boundary: np.ndarray  # (M,) vertex indices of the outline, CCW

    @property
    def faces(self) -> np.ndarray:
        """(F, k) vertex indices; every face of a mesh has the same size k (3 or 4)."""
        return self.face_indices.reshape(len(self.face_counts), -1)

    def edges(self) -> np.ndarray:
        """Unique undirected edges (E, 2)."""
        f = self.faces
        e = np.stack([f, np.roll(f, -1, axis=1)], axis=-1).reshape(-1, 2)
        return np.unique(np.sort(e, axis=1), axis=0)


def target_spacing(area: float, vertices: int) -> float:
    """Edge length giving about `vertices` vertices on a hexagonal lattice."""
    return math.sqrt(area / (vertices * math.sqrt(3) / 2))


def _inside(poly: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Even-odd point-in-polygon test, vectorised over points p (N, 2)."""
    x, y = p[:, 0][:, None], p[:, 1][:, None]
    x0, y0 = poly[:, 0][None, :], poly[:, 1][None, :]
    x1, y1 = np.roll(poly[:, 0], -1)[None, :], np.roll(poly[:, 1], -1)[None, :]
    crosses = (y0 > y) != (y1 > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
    return np.count_nonzero(crosses & (x < xi), axis=1) % 2 == 1


def distance_to_polygon(poly: np.ndarray, p: np.ndarray, chunk: int = 4096) -> np.ndarray:
    """Distance from points p (N, 2) to the closed polygon's edges."""
    a = poly
    b = np.roll(poly, -1, axis=0)
    ab = b - a
    ab2 = np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-30)
    out = np.empty(len(p))
    for s in range(0, len(p), chunk):
        q = p[s : s + chunk, None, :]
        u = np.clip(np.einsum("nmj,mj->nm", q - a[None], ab) / ab2, 0.0, 1.0)
        c = a[None] + u[..., None] * ab[None]
        out[s : s + chunk] = np.sqrt(np.min(np.sum((q - c) ** 2, axis=2), axis=1))
    return out


def triangulate(outline: Outline, vertices: int, rng: np.random.Generator) -> SurfaceMesh:
    h = target_spacing(outline.nominal_area, vertices)
    boundary = outline.sample(h)
    lo, hi = boundary.min(axis=0) - h, boundary.max(axis=0) + h
    dy = h * math.sqrt(3) / 2
    rows = []
    for j, y in enumerate(np.arange(lo[1], hi[1] + dy, dy)):
        xs = np.arange(lo[0] + (h / 2 if j % 2 else 0.0), hi[0] + h, h)
        rows.append(np.stack([xs, np.full_like(xs, y)], axis=1))
    lattice = np.vstack(rows) + rng.uniform(-0.12, 0.12, (sum(len(r) for r in rows), 2)) * h
    keep = _inside(boundary, lattice)
    lattice = lattice[keep]
    lattice = lattice[distance_to_polygon(boundary, lattice) > 0.55 * h]

    pts2 = np.vstack([boundary, lattice])
    tri = Delaunay(pts2).simplices
    centroids = pts2[tri].mean(axis=1)
    tri = tri[_inside(boundary, centroids)]
    # orient counter-clockwise (normal +z) and drop degenerate triangles
    a, b, c = pts2[tri[:, 0]], pts2[tri[:, 1]], pts2[tri[:, 2]]
    area2 = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    tri[area2 < 0] = tri[area2 < 0][:, [0, 2, 1]]
    tri = tri[np.abs(area2) > 1e-6 * h * h]

    used = np.unique(tri)
    remap = -np.ones(len(pts2), dtype=np.int64)
    remap[used] = np.arange(len(used))
    pts3 = np.zeros((len(used), 3))
    pts3[:, :2] = pts2[used]
    bnd = remap[np.arange(len(boundary))]
    return SurfaceMesh(
        points=pts3,
        face_counts=np.full(len(tri), 3, dtype=np.int32),
        face_indices=remap[tri].astype(np.int32).ravel(),
        boundary=bnd[bnd >= 0].astype(np.int32),
    )


def quad_grid(outline: Outline, vertices: int) -> SurfaceMesh:
    if outline.shape != "rect":
        raise ValueError("the grid topology needs a rectangular piece; use topology 'tri'")
    L, W = outline.length, outline.width
    if outline.corner_radius > 0:
        raise ValueError("the grid topology keeps sharp corners; set the corner radius to 0")
    nv = max(2, round(math.sqrt(vertices * W / L)))
    nu = max(2, round(vertices / nv))
    u = np.linspace(0.0, 1.0, nu)
    v = np.linspace(0.0, 1.0, nv)
    bottom = outline.at(u * L)
    right = outline.at(L + v * W)
    top = outline.at(L + W + (1.0 - u) * L)
    left = outline.at(2 * L + W + (1.0 - v) * W)
    # corners shared by two edges: take them from the edge evaluations
    c00, c10, c11, c01 = bottom[0], bottom[-1], top[-1], top[0]
    U, V = np.meshgrid(u, v, indexing="xy")  # (nv, nu)
    P = (
        (1 - V)[..., None] * bottom[None, :, :]
        + V[..., None] * top[None, :, :]
        + (1 - U)[..., None] * left[:, None, :]
        + U[..., None] * right[:, None, :]
        - (
            ((1 - U) * (1 - V))[..., None] * c00
            + (U * (1 - V))[..., None] * c10
            + (U * V)[..., None] * c11
            + ((1 - U) * V)[..., None] * c01
        )
    )
    pts3 = np.zeros((nu * nv, 3))
    pts3[:, :2] = P.reshape(-1, 2)
    idx = np.arange(nu * nv).reshape(nv, nu)
    quads = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], axis=-1).reshape(-1, 4)
    boundary = np.concatenate([idx[0, :-1], idx[:-1, -1], idx[-1, :0:-1], idx[:0:-1, 0]])
    return SurfaceMesh(
        points=pts3,
        face_counts=np.full(len(quads), 4, dtype=np.int32),
        face_indices=quads.astype(np.int32).ravel(),
        boundary=boundary.astype(np.int32),
    )


def build(outline: Outline, topology: str, vertices: int, rng: np.random.Generator) -> SurfaceMesh:
    if topology == "tri":
        return triangulate(outline, vertices, rng)
    if topology == "grid":
        return quad_grid(outline, vertices)
    raise ValueError(f"unknown topology {topology!r}, expected one of {TOPOLOGIES}")


def metrics(mesh: SurfaceMesh) -> dict:
    """Size and quality of the mesh: area, perimeter, edge lengths, angles."""
    p = mesh.points[:, :2]
    q = p[mesh.faces]  # (F, k, 2)
    x, y = q[..., 0], q[..., 1]
    area = 0.5 * float(np.sum(x * np.roll(y, -1, axis=1) - y * np.roll(x, -1, axis=1)))
    e_next = np.roll(q, -1, axis=1) - q
    e_prev = np.roll(q, 1, axis=1) - q
    cosang = np.sum(e_next * e_prev, axis=2) / (
        np.linalg.norm(e_next, axis=2) * np.linalg.norm(e_prev, axis=2)
    )
    angles = np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0))).min(axis=1)
    e = mesh.edges()
    lengths = np.linalg.norm(p[e[:, 0]] - p[e[:, 1]], axis=1)
    b = p[mesh.boundary]
    perimeter = float(np.sum(np.linalg.norm(np.roll(b, -1, axis=0) - b, axis=1)))
    return {
        "vertices": len(p),
        "faces": len(mesh.face_counts),
        "area_m2": area,
        "perimeter_m": perimeter,
        "edge_mean_mm": float(lengths.mean() * 1e3),
        "edge_cv": float(lengths.std() / lengths.mean()),
        "min_angle_deg": float(angles.min()),
        "min_angle_p05_deg": float(np.percentile(angles, 5)),
    }
