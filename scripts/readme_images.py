"""Build the board of docs/usage.md: one piece of every preset, draped in Blender and rendered.

Development tool, not part of the package. Needs Blender as a Python module (`pip install bpy`) and
Pillow:

    python scripts/readme_images.py [--out docs/images/all_presets.jpg] [--seed 2] [--samples 32]

Each preset: `maillage generate --preset <p> --count 1 --seed 2`, then `maillage drop-test
--pieces 1 --render` (the flag with `--wind 4`). Each tile is framed on its own piece, so scales
differ; the caption gives the piece's size, fabric, mass, pattern and drape coefficient, as measured.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from maillage.presets import PRESETS

TILE = (636, 358)
GAP = 13
BAND = 72
COLUMNS = 4
BACKGROUND = (242, 242, 242)
INK, INK2 = (22, 25, 29), (70, 74, 80)


def piece(work: Path, key: str, seed: int, samples: int) -> dict:
    """Generate and drape one piece of a preset; its render and what was measured."""
    subprocess.run(
        ["maillage", "generate", "--preset", key, "--count", "1", "--seed", str(seed), "--out", str(work)],
        check=True,
        capture_output=True,
    )
    folder = work / key
    args = ["maillage", "drop-test", str(folder), "--pieces", "1", "--render", "--samples", str(samples)]
    if PRESETS[key].get("pins"):
        args += ["--wind", "4"]
    subprocess.run(args, check=True, capture_output=True)
    report = json.loads((folder / "drop_test" / "drop_test.json").read_text())["pieces"][0]
    row = next(csv.DictReader((folder / "instances.csv").open()))
    return {
        "png": folder / "drop_test" / "drop_test.png",
        "width_cm": float(row["variation:width_m"]) * 100,
        "length_cm": float(row["variation:length_m"]) * 100,
        **report,
    }


def caption(key: str, p: dict) -> str:
    size = f"{p['width_cm']:.0f}×{p['length_cm']:.0f} cm"
    fabric = p["fabric"].replace("_", " ")
    pattern = p["pattern"].replace("_", " ")
    end = "hung, wind 4" if p["scenario"] == "hang" else f"drape {p['drape_coefficient']:.2f}"
    return f"{size} · {fabric} · {p['mass_kg'] * 1e3:.0f} g · {pattern} · {end}"


def font(size: int, bold: bool = False):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def board(pieces: dict, out: Path) -> None:
    rows = -(-len(pieces) // COLUMNS)
    w = COLUMNS * TILE[0] + (COLUMNS + 1) * GAP
    h = rows * (TILE[1] + BAND) + GAP
    img = Image.new("RGB", (w, h), BACKGROUND)
    d = ImageDraw.Draw(img)
    title, small = font(21, bold=True), font(15)
    for i, (key, p) in enumerate(pieces.items()):
        r, c = divmod(i, COLUMNS)
        x, y = GAP + c * (TILE[0] + GAP), GAP + r * (TILE[1] + BAND)
        tile = Image.open(p["png"]).convert("RGB").resize(TILE, Image.LANCZOS)
        img.paste(tile, (x, y))
        d.text((x + 4, y + TILE[1] + 8), key, fill=INK, font=title)
        d.text((x + 4, y + TILE[1] + 38), caption(key, p), fill=INK2, font=small)
    img.save(out, quality=88)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/images/all_presets.jpg")
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--samples", type=int, default=32)
    args = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as t:
        pieces = {key: piece(Path(t), key, args.seed, args.samples) for key in PRESETS}
        board(pieces, Path(args.out))
        for key, p in pieces.items():
            print(key, caption(key, p))


if __name__ == "__main__":
    main()
