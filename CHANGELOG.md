# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
