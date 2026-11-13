# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Breaking changes

- Pack files (Primvaria contract): `pieces.csv` and `summary.json` are replaced by
  `instances.csv` and `manifest.json`, the same in the four generators. The
  table is read back from the OpenUSD files, one row per asset: identity,
  aspects, `variation:<name>` and `measured:<name>` columns, then the
  generator's own; the former summary is the manifest's `summary`.
- The stage no longer carries `maillage:preset`, `maillage:version` and
  `maillage:seed` as custom data on `/World`: each piece has them as
  `primvaria:preset`, `primvaria:version` and `primvaria:seed` (Primvaria
  contract).

### Added

- `examples/`: four short scripts, each explained by its own comments (a first
  pack and its ground truth, one aspect switched off, reading the file with
  OpenUSD alone, the drape test in MuJoCo); a test runs each one.
- `maillage fabric-test` (`maillage.sim.mujoco_test.fabric_drape`): drapes the
  same Cusick sample (a 30 cm disc on an 18 cm pedestal) of every fabric in
  MuJoCo and checks that they do not drape alike: silk, plain cotton and
  denim in that order, at least 0.05 apart, and a spread of at least 0.2.
  Measured: 0.51 (polyester knit) to 0.83 (denim), where Blender gives
  0.35–0.42 for all. Run in CI; the README has the table and what it does
  not show.
- What was measured on each piece is written in the file as
  `primvaria:measured:<name>` (`mass_kg`, `area_m2`, `perimeter_m`, `vertices`, `faces`, `edge_mean_mm`, `min_angle_deg`…).
- `python -m maillage.conformance` also checks every pack it finds: the table must
  say what the files say. `pack.py` and `tests/test_pack.py` are shared by the
  four generators.
- Ground truth of the variation, in the file (Primvaria contract, variation
  model): `primvaria:variation:aspects`, the aspects that were switched on, and
  one `primvaria:variation:<name>` per drawn value (`length_m`, `width_m`, `format_length_m`, `corner_radius_m`, `cut_amplitudes_m`, `cut_skew_deg`, `fabric`, `pattern`, `colors`…).
  `python -m maillage.conformance` requires the aspects on every asset.
- `CONTRIBUTING.md`, issue templates (bug report, cloth preset request),
  `SECURITY.md` and `CITATION.cff`.
- Primvaria OpenUSD contract, version 0
  ([docs/contract.md](https://github.com/drscaon/primvaria/blob/main/docs/contract.md)):
  every piece is an asset any tool can find without knowing Maillage: a model of kind `component` with `assetInfo` (name,
  identifier, version) and the attributes `primvaria:contract`,
  `primvaria:generator`, `primvaria:version`, `primvaria:preset` and
  `primvaria:seed`; `/World` is an `assembly` and `/World/Cloths` a group.
- `python -m maillage.conformance`: checks files against the contract (stage
  units, model hierarchy, identity). Run in the tests and, in CI, on every
  preset.

### Changed

- The README is a third of its former length; the detail moved, unchanged, to
  `docs/`: `usage.md`, `openusd.md`, `engines.md`, `limits.md`,
  `development.md`. [primvaria.com/maillage](https://primvaria.com/maillage/)
  is built from these files.
- Continuous integration runs the checks shared by the four generators
  (Primvaria's reusable workflow).

### Fixed

- `maillage list` no longer fails on a console that is not UTF-8 (cp1252:
  Windows with redirected output, Git Bash): a sign the console lacks is
  printed as `?`.

### Removed

- `MUJOCO_LOG.TXT`, a MuJoCo warning log from a development run of 29 October
  that had been committed by mistake; it is now ignored by git. The current
  drape test writes no such warning.

## [0.2.0b1] - 2026-11-11 (beta)

### Breaking changes

- Python 3.11 or later (was 3.10): MuJoCo 4 requires it, and Python 3.10 reached
  its end of life in October 2026.
- `usd-core` 26.5 or later (was 24.0): the OpenUSD validators do not load from
  earlier wheels (25.5 lacks the validator libraries, 25.8 and 25.11 the
  UsdPreviewSurface definitions), and 24.x has no `UsdValidation` at all. A CI
  job runs the tests on exactly 26.5.
- MuJoCo 4 (`mujoco>=4.0`, was 3.2) for the `sim` and `dev` extras; MuJoCo 3 is no
  longer supported.
- The ground and physics scene are the same in every Primvaria project (`ground.py`, the
  same file in each): `/World/PhysicsScene`, gravity 9.81 m/s² along −Z; `/World/Ground`,
  a 2 cm box (`UsdGeom.Cube`) whose top is z = 0, covering the content with 0.5 m to
  spare, rendered, no PhysX attributes; `/World/GroundMaterial`, static friction 0.6,
  dynamic 0.5, restitution 0.1. A test checks every generated file against it.
  Maillage's main file had no PhysicsScene (only its OmniPhysics layer defined one, and
  no longer does), and its ground was a flat mesh without a physics material; the
  MuJoCo test takes the floor's friction from the file.

### Added

- Engine-neutral stiffness for every fabric, in SI units: tensile stiffness
  (N/m), bending rigidity (N·m) and Poisson's ratio, written as
  `maillage:tensileStiffness`, `maillage:bendingRigidity` and
  `maillage:poissonsRatio`; `fabrics.shell()` gives the shell's Young's
  modulus and thickness that match both.
- MuJoCo export: `maillage_<preset>.xml`, one flex cloth per piece with shell
  elasticity, mass and friction, read back from the OpenUSD file.
- `maillage sim-test`: the drape test in MuJoCo, same scenario and checks as
  the Blender test, plus mass and solver checks. Extra `sim`; CI runs it on
  every preset.
- NVIDIA OmniPhysics export: `maillage_<preset>_omniphysics.usda`, an OpenUSD
  layer over the main file with surface deformables (Isaac Sim 5+);
  `python -m maillage.omniphysics` checks its structure (CI, every preset).
  Not simulated yet (needs an NVIDIA RTX GPU).
- `python -m maillage.validate FILE_OR_FOLDER`: every OpenUSD `UsdValidation` validator
  (what `usdchecker` runs) on each file and each variant; the tests and a CI job
  (every preset) require no error and no warning.

### Changed

- README: the same header as the other Primvaria projects (PyPI and suite
  badges), an Engines table matching the suite's engine matrix, and links to
  primvaria.com.

## [0.1.0b2] - 2026-10-29 (beta)

First release on PyPI.

### Changed

- Released on PyPI (`pip install maillage`) by the release workflow, through Trusted Publishing.
- README images and links use absolute URLs, so that they show on PyPI; the README links to Primvaria, the suite the project belongs to.

## [0.1.0b1] - 2026-10-23 (beta)

First beta, and first published version (0.1.0a1 was never released; its
changes are included here).

### Added
- 12 textile presets in 7 categories: Bath (`bath_towel`, `hand_towel`,
  `washcloth`), Kitchen (`tea_towel`), Table (`napkin`, `tablecloth` with
  rectangular, round and oval formats), Bedding (`bed_sheet`), Cleaning
  (`microfiber_cloth`), Accessories (`bandana`, `silk_scarf`, knitted
  `scarf`), Outdoor (`flag`, hung by its hoist corners).
- 11 fabrics with areal density, thickness, friction, visual roughness, hem
  stiffness and Blender cloth stiffness: cotton terry, waffle, plain and
  percale, linen, denim, fleece, microfiber, polyester knit, silk, wool knit.
- Piece generation from distributions: retail formats and size tolerance,
  corner rounding, imperfect cut (wavy edges, skew), fabric mix, procedural
  patterns (solid, end bands, stripes along or across, gingham, border, flag
  bands with unequal, asymmetric widths) as PNG textures. Each aspect has its
  own random stream; `--no-size`, `--no-cut`, `--no-corners`, `--no-color`
  turn one off without changing the others.
- `--fabric` forces one fabric, or a list used in turn; `--format` replaces a
  preset's sizes and shapes with a weighted list in cm
  (`140x180@2,round:150,oval:140x220`; dicts and tuples in Python, module
  `maillage.formats`).
- Meshing: near-equilateral triangles for any outline (`--topology tri`) or a
  structured quad grid over the four cut edges (`--topology grid`), with a
  target vertex count; mesh metrics (area, perimeter, edge lengths, minimum
  angles).
- OpenUSD export: textured UsdPreviewSurface materials, `st`, `hem` and `pin`
  primvars, physical properties and Blender stiffness as `maillage:*`
  attributes, collision ground. `summary.json` (counts by fabric, pattern,
  shape and format; mass and mesh statistics) and `pieces.csv`, in UTF-8.
- Blender drape test (`maillage drop-test`, or `blender -b -P` with the
  standalone script): Cusick-style clamped pedestal or hanging flag (optional
  wind), stiffness rescaled to the mesh resolution and the real mass, checks
  (finite, stretch, penetration, at rest), drape coefficient, draped meshes
  exported to OpenUSD with their attributes, optional Cycles render and
  animated GIF (`--gif`).
- `maillage preview`: flat preview sheet with textures and mesh (matplotlib).
- `maillage list`, `maillage blender-script`.
- README with results tables, all presets draped side by side, GIFs; GitHub
  social preview image (`docs/images/social_preview.png`).
- Test suite (pytest), lint and format (ruff), continuous integration with a
  Blender drape test of every preset, release workflow, Dependabot, GitHub
  Flow `pre-push` hook.
