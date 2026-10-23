"""CPU previews (matplotlib): the generated pieces laid flat, with their
pattern and their mesh. Reads what `maillage generate` wrote, so it also works
on folders generated earlier."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as Path_  # noqa: E402
from pxr import Usd, UsdGeom  # noqa: E402


def _pieces(folder: Path):
    usd = sorted(folder.glob("maillage_*.usd*"))
    if not usd:
        raise FileNotFoundError(f"no maillage_*.usd* file in {folder}")
    stage = Usd.Stage.Open(str(usd[0]))
    for prim in stage.GetPrimAtPath("/World/Cloths").GetChildren():
        mesh = UsdGeom.Mesh(prim)
        pts = np.asarray(mesh.GetPointsAttr().Get(), float)[:, :2]
        counts = np.asarray(mesh.GetFaceVertexCountsAttr().Get())
        idx = np.asarray(mesh.GetFaceVertexIndicesAttr().Get())
        st = np.asarray(UsdGeom.PrimvarsAPI(mesh).GetPrimvar("st").Get(), float)
        faces = idx.reshape(len(counts), -1)
        yield {
            "name": prim.GetName(),
            "points": pts,
            "faces": faces,
            "st": st,
            "fabric": prim.GetAttribute("maillage:fabric").Get(),
            "size": tuple(prim.GetAttribute("maillage:size").Get()),
            "texture": folder / "textures" / f"{prim.GetName()}.png",
        }


def _triangles(faces: np.ndarray) -> np.ndarray:
    if faces.shape[1] == 3:
        return faces
    return np.vstack([faces[:, [0, 1, 2]], faces[:, [0, 2, 3]]])


def sheet(
    folder: str | Path, output: str | Path | None = None, wireframe: bool = True, cols: int = 0
) -> Path:
    """All the pieces of a generated folder, flat, at the same scale."""
    folder = Path(folder)
    pieces = list(_pieces(folder))
    n = len(pieces)
    cols = cols or math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    span = max(max(p["size"]) for p in pieces)
    fig, axes = plt.subplots(rows, cols, figsize=(3.2 * cols, 3.0 * rows), squeeze=False)
    fig.patch.set_facecolor("#e6e6e6")
    for ax in axes.ravel():
        ax.set_axis_off()
    for ax, p in zip(axes.ravel(), pieces, strict=False):
        img = mpimg.imread(p["texture"])[..., :3]
        L, W = p["size"]
        # the texture coordinates are linear in x and y: show the image over the
        # nominal rectangle, clipped by the triangles of the cut piece
        tri = p["points"][_triangles(p["faces"])]
        verts = np.concatenate([tri, tri[:, :1]], axis=1).reshape(-1, 2)
        codes = np.tile([Path_.MOVETO, Path_.LINETO, Path_.LINETO, Path_.CLOSEPOLY], len(tri))
        clip = PathPatch(Path_(verts, codes), transform=ax.transData, facecolor="none", edgecolor="none")
        ax.add_patch(clip)
        im = ax.imshow(img, extent=(-L / 2, L / 2, -W / 2, W / 2), interpolation="bilinear")
        im.set_clip_path(clip)
        if wireframe:
            f = p["faces"]
            seg = np.stack([p["points"][f], p["points"][np.roll(f, -1, axis=1)]], axis=2).reshape(-1, 2, 2)
            ax.add_collection(LineCollection(seg, colors="k", linewidths=0.15, alpha=0.25))
        ax.set_xlim(-span / 2, span / 2)
        ax.set_ylim(-span / 2, span / 2)
        ax.set_aspect("equal")
        ax.set_title(f"{p['name']}\n{p['fabric']}, {L * 100:.0f}×{W * 100:.0f} cm", fontsize=8)
    fig.tight_layout()
    out = Path(output) if output else folder / "sheet.png"
    fig.savefig(out, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out
