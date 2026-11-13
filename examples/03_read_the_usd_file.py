"""Read what Maillage wrote, with OpenUSD alone.

You do not need Maillage to use a pack. Everything is in the OpenUSD file,
under the attribute namespace of the Primvaria contract:

    primvaria:generator, primvaria:preset, primvaria:seed   what made this asset
    primvaria:variation:<name>                              what was drawn for it
    primvaria:measured:<name>                               what was measured on it

This script generates a small pack, then opens it with pxr only, as a
simulator or a data pipeline would.

    python examples/03_read_the_usd_file.py
"""

import sys
from pathlib import Path

from pxr import Usd, UsdGeom

from maillage import generate_scene, write_outputs

out = sys.argv[1] if len(sys.argv) > 1 else "output/examples"
folder = write_outputs(generate_scene("hand_towel", count=3, vertices=300, seed=7), out)
usd_file = next(Path(folder).glob("*.usdc"))

# ---- from here on, no Maillage: only OpenUSD ----
stage = Usd.Stage.Open(str(usd_file))
units, up = UsdGeom.GetStageMetersPerUnit(stage), UsdGeom.GetStageUpAxis(stage)
print(f"{usd_file.name}: {units} m per unit, up axis {up}")

# An asset of the contract says which generator made it and which aspects varied.
pieces = [p for p in stage.Traverse() if p.HasAttribute("primvaria:variation:aspects")]
aspects = pieces[0].GetAttribute("primvaria:variation:aspects").Get()
made_by = pieces[0].GetAttribute("primvaria:generator").Get()
print(f"{len(pieces)} pieces made by {made_by}, aspects that varied: {', '.join(aspects)}")

for prim in pieces:
    fabric = prim.GetAttribute("primvaria:variation:fabric").Get()
    mass = prim.GetAttribute("primvaria:measured:mass_kg").Get()
    area = prim.GetAttribute("primvaria:measured:area_m2").Get()
    # The cloth itself is a standard mesh, somewhere under the asset.
    meshes = [UsdGeom.Mesh(p) for p in Usd.PrimRange(prim) if p.IsA(UsdGeom.Mesh)]
    points = len(meshes[0].GetPointsAttr().Get())
    print(f"  {prim.GetPath()}  {fabric}, {area:.3f} m2, {mass * 1000:.0f} g, mesh of {points} points")
