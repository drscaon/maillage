# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Documentation

- The README links to Primvaria's note on how standards are used; the pull request checklist gains a line for it.

### Changed

- `tests/test_contract.py`, `test_pack.py` and `test_golden.py` import the shared tests of primvaria-contract 0.3.0b1 (`primvaria_contract.testing`) instead of keeping a copy of them; the same tests run, one for one. Requires primvaria-contract 0.3.0b1.
- The code of the Primvaria contract comes from the new package primvaria-contract, which
  this generator now requires, instead of copies kept identical in the four generators.
  `contract`, `pack`, `ground` and `conformance` stay as modules of this package and give
  the same names as before, filled in with this generator's name and version: nothing
  changes for code that imports them or for `python -m maillage.conformance`. The contract
  tests on stages written by hand moved to primvaria-contract; `tests/test_contract.py`
  keeps the tests of this generator's files.
- `maillage.validate` (the OpenUSD validators) comes from primvaria-contract too, which this
  generator now requires at 0.2.0b1 or later; `python -m maillage.validate` works as before. It now also reports a path that does not exist (`not found`) and fails, as Filaire's did.
- CI runs at two levels. On a commit (push to main, pull request): the tests not marked
  `slow` on Ubuntu and Python 3.12 only, and the engine checks on two presets, the first one and one picked from the commit's hash (`.github/ci_presets.py`). Before a release and with the "Run
  workflow" button: every test, platform and Python, the oldest OpenUSD and every
  preset, as before. `release.yml` runs that full level first and releases nothing
  unless it passes. Tests of 8 s or more are marked `slow` (`pytest -m "not slow"` runs
  the others).

### Added

- `generate --usdz`: also write the pack's file as one `.usdz` package, with the textures and files it references and its engine layers inside (`primvaria_contract.usdz`, primvaria-contract 0.5.0b1); off by default, so the output is unchanged. Each package passes OpenUSD's validators with their packaging rules and opens in Blender.
- Every material says what it is made of with a semantic label (`semantics:labels:material`, Primvaria contract section 5), as NVIDIA's SimReady profiles ask; the shared ground is labelled `ground` and rendered with its own grey material (`concrete`). Requires primvaria-contract 0.4.0b1. The cloth's label is the fabric (`linen`).

## [0.5.0b1] - 2026-11-24 (beta)

### Added

- A Newton layer beside every file, `maillage_<preset>_newton.usda` (contract section 9, a
  new engine layer): the cloths as surface deformables with the AOUSD proposal's schemas,
  which Newton 1.8 reads (`PhysicsDeformableBodyAPI`, `PhysicsSurfaceDeformableSimAPI`,
  `PhysicsSurfaceDeformableMaterialAPI`), the same values as the OmniPhysics layer. The file
  is unchanged; `python -m maillage.newton` checks the layer.
- `generate --engines LIST`: the engine layers to write (`physx`, `omniphysics`, `newton`,
  comma-separated, or `none`); by default all of them, as the four Primvaria generators do.

## [0.4.0b1] - 2026-11-20 (beta)

### Breaking changes

- A piece's material is inside it, `/World/Cloths/<piece>/Looks/surface`,
  instead of `/World/Looks/<piece>`; the OmniPhysics layer's deformable
  material too (`Looks/Phys_<fabric>`, one per piece). A piece referenced
  alone into another stage lost its texture; it now keeps it (PRV-40).

### Changed values

- Every physical value now names its source (PRV-33), and the values that
  did not match theirs were corrected: areal densities of `cotton_waffle`
  220 → 290 g/m² (kitchen waffle towels, 250 to 350), `cotton_percale` 120 →
  130 g/m² (125 to 132), `linen` 180 → 200 g/m² (linen tea towels, 190 to
  220), `denim` 400 → 407 g/m² (12 oz/yd²); thickness of `fleece` 3 → 1.5 mm
  (polar fleece, 0.8 to 1.5 mm) and of `polyester_knit` 0.2 → 0.3 mm (a
  knitted flag fabric). The Blender stiffness of the four fabrics follows
  their areal density by the rules of `fabrics.py`. Pieces of `tea_towel`,
  `napkin`, `tablecloth` and `bed_sheet` in those fabrics are heavier.
- A `solid` piece records the one colour its texture paints: its
  `variation:colors` no longer holds an accent that was drawn but never
  painted. The draws and the pieces are unchanged (PRV-34).

### Added

- `docs/sources.md` and `maillage/sources.py`: the source of every physical
  value (fabric and product specifications, or an estimate with what it
  rests on) and the range each source gives. `tests/test_sources.py` fails
  on a value with no source, on a value outside its source's range, and when
  the page is not the module's tables (PRV-33).
- The conformance check (shared by the four generators) checks that an asset
  is whole on its own (contract, section 4): every relationship or connection
  inside an asset root (a material binding, a physics material, a joint's
  bodies) points inside it, in every variant (PRV-40).
- The conformance check (`contract.conformance`, `python -m maillage.conformance`,
  shared by the four generators) checks sections 7 and 8 of the contract: a
  variant set and its variants are named in `snake_case`, have a default
  selection, and the set is one section 7 lists, with its meaning, for the
  asset's generator (`contract.VARIANT_SETS`); no variant changes what identifies the asset (its `assetInfo`,
  `primvaria:*` identity and semantic labels), each variant being selected in
  turn on a copy of the stage; a mate frame is an `Xform` named `MateFrame` or
  `MateFrame_<feature>`, inside an asset, in every variant; nothing is written
  under `primvaria:mate:*`, which is not in the contract yet (PRV-35).
- `generate --no-vary ASPECTS` and `--nominal`, as in the other generators of
  the suite, `fabric` included: `--no-vary cut,color` keeps those aspects
  nominal, and an unknown aspect is refused. `--no-cut`, `--no-color`… still
  work, and are deprecated (PRV-35).
- `docs/variation.md`: how every drawn value follows its preset, what each
  pattern draws, and every preset's numbers, written from
  `maillage/declared.py` and the presets; `tests/test_distributions.py` draws
  a thousand pieces of every preset and checks each value's range and
  distribution, and that a piece records exactly the declared values and
  those of its pattern (PRV-34).
- Reproducibility references (`tests/test_golden.py`, shared by the four
  generators): four cases of fixed preset, seed and options whose pack tables
  must give the same drawn and measured values on every Python and platform
  of the CI. Contract, section 6, rule 1 (PRV-32).

### Changed

- README and docs images rendered again with the sourced values of PRV-33
  (areal densities, thicknesses): the board of the 12 presets, the tea towel
  drape, the fabric squares and the flags GIFs. The board now has its script,
  `scripts/readme_images.py`.
- `docs/engines.md` is now `docs/physics.md`, the name the other generators
  use for the same page (PRV-35).

## [0.3.0b1] - 2026-11-13 (beta)

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

- Semantic labels on every asset, with OpenUSD's `UsdSemantics.LabelsAPI`:
  `semantics:labels:class` (`cloth` and the preset (`tea_towel`)) and
  `semantics:labels:instance` (the asset's name). `instances.csv` gains a
  `classes` column and `manifest.json` lists the classes of the pack; the
  conformance check requires the labels (`contract.write_labels`,
  `contract.labels`).
- `python -m maillage.conformance` refuses engine data in a file (schemas and
  attributes of PhysX or OmniPhysics belong in an engine layer, contract
  section 9) and checks that an engine layer lies over the file it is named
  after and over nothing else. `contract.py` and `tests/test_contract.py`
  stay the same in the four generators.
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

- The README's table of outputs says that `instances.csv` holds each asset's classes, with a link to the
  semantic labels.
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
