# OpenUSD layout and contract

How a piece is laid out in the file, the ground and physics scene, OpenUSD compliance, and what the Primvaria contract writes on every piece.

Part of the [Maillage](../README.md) documentation.

## OpenUSD layout

Z up, metres, kilograms. `/World` is the default prim.

```
/World
  /Looks/<piece>      UsdPreviewSurface + UsdUVTexture (textures/<piece>.png)
  /Cloths/<piece>     UsdGeom.Mesh, flat on the ground, laid out in rows
  /PhysicsScene       gravity (shared, see below)
  /Ground             the shared ground, its top face at z = 0 (CollisionAPI)
  /GroundMaterial     its physics material
```

## Ground and physics scene (the same in every Primvaria project)

Every file with physics carries the same two prims, so that assets from
different generators can share one scene and every engine gets the same floor:

| Prim | What it is |
|---|---|
| `/World/PhysicsScene` | gravity 9.81 m/s² along −Z |
| `/World/Ground` | a static box (`UsdGeom.Cube`, `CollisionAPI`), its top face at z = 0, 2 cm thick, covering the content with 0.5 m to spare on each side (1 m × 1 m at least), grey and rendered, no PhysX attributes (engines derive their contact offsets) |
| `/World/GroundMaterial` | its physics material: static friction 0.6, dynamic friction 0.5, restitution 0.1, a wooden or concrete floor |

The code is one file, `ground.py`, identical in Granulaire, Maillage, Filaire
and Quincaillerie; a test checks every generated file against it. The MuJoCo
checks and the Blender rigid-body checks take the ground's friction from the
file (Blender's cloth, in Maillage, has its own collision settings).

Each cloth mesh has `subdivisionScheme = none`, is double sided, and carries:

| Property | Content |
|---|---|
| `primvars:st` | texture coordinates (vertex) |
| `primvars:hem` | 1 on the hemmed band along the edges, 0 elsewhere (vertex) |
| `primvars:pin` | 1 on pinned vertices: the hoist corners of a flag (vertex) |
| `primvars:displayColor` | mean colour of the texture |
| `maillage:fabric`, `maillage:pattern`, `maillage:shape` | what the piece is |
| `maillage:arealDensity`, `maillage:mass`, `maillage:thickness`, `maillage:friction` | physical properties (SI units) |
| `maillage:nominalSize`, `maillage:size`, `maillage:cornerRadius` | retail and actual size (m) |
| `maillage:hemBendingFactor` | how much stiffer the hem is in bending |
| `maillage:tensileStiffness`, `maillage:bendingRigidity`, `maillage:poissonsRatio` | engine-neutral stiffness: N/m, N·m (see [Engines](engines.md#engines)) |
| `maillage:blender:*` | stiffness for Blender's cloth solver, for 1 cm edges (see [Blender values](engines.md#blender-values)) |

OpenUSD has no standard schema for cloth simulation (`UsdPhysics` covers
rigid bodies and joints), so these properties are custom attributes. Blender's
USD importer reads the geometry, UVs, material, texture and the `hem` and
`pin` primvars (as mesh attributes); the drape test reads the `maillage:*`
attributes with the OpenUSD bindings shipped with Blender.

## OpenUSD compliance

```bash
python -m maillage.validate output/tea_towel
```

This runs every validator of OpenUSD's `UsdValidation` registry on each file,
the checks `usdchecker` runs: composition, stage metadata (meters, Z up),
geometry, material bindings, shaders, UsdPhysics rigid bodies and colliders.
Each file is checked once per variant, since a variant that is not selected is
not composed. The tests and CI require no error and no warning, on every
preset.

## Primvaria contract

```bash
python -m maillage.conformance output/tea_towel
```

Maillage is part of [Primvaria](https://primvaria.com) and follows its
[mission](https://github.com/drscaon/primvaria/blob/main/MISSION.md) and its
[OpenUSD contract](https://github.com/drscaon/primvaria/blob/main/docs/contract.md),
version 0, which the four generators share. Every piece is an asset any tool can find without knowing Maillage: a model of kind
`component` with `assetInfo` (name, identifier, version) and the attributes
`primvaria:contract`, `primvaria:generator`, `primvaria:version`,
`primvaria:preset` and `primvaria:seed`; `/World` is an `assembly` and `/World/Cloths` a group. The command above checks
the stage units, the model hierarchy and this identity; the tests and CI
require it on every preset.

What was drawn for each piece is in the file too, its ground truth:
`primvaria:variation:aspects` lists the aspects that were switched on
(`size`, `cut`, `corners`, `fabric`, `color`) and `primvaria:variation:<name>` holds each drawn value
(`length_m`, `width_m`, `format_length_m`, `corner_radius_m`, `cut_amplitudes_m`, `cut_skew_deg`, `fabric`, `pattern`, `colors`…). An aspect that is switched off is still recorded, at its
nominal value, and the other aspects keep their draws.

What was measured on each piece once generated is there as well, as
`primvaria:measured:<name>` (`mass_kg`, `area_m2`, `perimeter_m`, `vertices`, `faces`, `edge_mean_mm`, `min_angle_deg`…).
The pack's `instances.csv` is read back from the OpenUSD files, one row per
asset with the same names (`variation:<name>`, `measured:<name>`), and
`manifest.json` says what the pack is; both have the same shape in the four
generators, and the command above fails when the table and the files disagree.
