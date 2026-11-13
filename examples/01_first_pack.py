"""Generate a first pack of cloth pieces and read its ground truth.

A pack is the folder Maillage writes for one preset: an OpenUSD file with the
pieces (meshes ready for cloth simulation, with their fabric), their textures,
and a table (instances.csv) with one row per piece. The table is read back
from the OpenUSD file, so the two cannot disagree.

Run it:

    python examples/01_first_pack.py            # writes under output/examples/
    python examples/01_first_pack.py some/dir   # or under a folder of your choice
"""

import sys

from maillage import FABRICS, PRESETS, generate_scene, write_outputs
from maillage.pack import read_manifest, read_table

out = sys.argv[1] if len(sys.argv) > 1 else "output/examples"

# Presets are kinds of pieces (towels, napkins, flags...); fabrics are what
# they are made of (areal density, thickness, stiffness).
print(f"{len(PRESETS)} presets, for example: {', '.join(list(PRESETS)[:5])}")
print(f"{len(FABRICS)} fabrics, for example: {', '.join(list(FABRICS)[:5])}")

# Four tea towels of about 300 vertices each. The seed fixes every random
# draw: the same call always gives the same pieces.
scene = generate_scene("tea_towel", count=4, vertices=300, seed=1)
folder = write_outputs(scene, out)
print(f"pack written to {folder}")

# manifest.json says what the pack is; its summary counts fabrics and patterns.
summary = read_manifest(folder)["summary"]
print(f"fabrics: {summary['fabrics']}, patterns: {summary['patterns']}")

# instances.csv is the ground truth of each piece: what was drawn for it
# (variation:*) and what was measured on its mesh once generated (measured:*).
print(f"\n{'piece':15s} {'size (cm)':>12s} {'fabric':>15s} {'pattern':>9s} {'mass':>8s} {'vertices':>9s}")
for row in read_table(folder):
    size = f"{float(row['variation:length_m']) * 100:.1f} x {float(row['variation:width_m']) * 100:.1f}"
    mass_g = float(row["measured:mass_kg"]) * 1000
    fabric, pattern, vertices = row["variation:fabric"], row["variation:pattern"], row["measured:vertices"]
    print(f"{row['name']:15s} {size:>12s} {fabric:>15s} {pattern:>9s} {mass_g:6.1f} g {vertices:>9s}")
