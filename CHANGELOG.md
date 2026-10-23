# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Custom formats: `--format` (Python: `generate_scene(formats=...)`) replaces
  a preset's sizes and shapes with a weighted list in cm, e.g.
  `140x180@2,round:150,oval:140x220`; dicts and tuples work in Python
  (`maillage.formats`). `summary.json` counts the pieces of each format drawn.
- `maillage list` shows round and oval formats as `⌀150` and `oval 140×200`.
- `scarf` preset (Accessories): knitted winter scarf, 20×140 to 30×180 cm,
  in the new `wool_knit` fabric (350 g/m², 3 mm), solid, gingham or with the
  new `cross_stripes` pattern (stripes across the width).
- README: all presets side by side, draped in Blender.
- GitHub social preview image (`docs/images/social_preview.png`).

### Changed
- Flag bands have unequal, asymmetric widths, so that random colours are
  unlikely to reproduce a real national flag (these mostly use equal or
  symmetric bands).

## [0.1.0a1] - 2026-10-23 (alpha)

First version.

### Added
- 11 textile presets in 7 categories: Bath (`bath_towel`, `hand_towel`,
  `washcloth`), Kitchen (`tea_towel`), Table (`napkin`, `tablecloth` with
  rectangular, round and oval formats), Bedding (`bed_sheet`), Cleaning
  (`microfiber_cloth`), Accessories (`bandana`, `silk_scarf`), Outdoor (`flag`,
  hung by its hoist corners).
- 10 fabrics with areal density, thickness, friction, visual roughness, hem
  stiffness and Blender cloth stiffness: cotton terry, waffle, plain and
  percale, linen, denim, fleece, microfiber, polyester knit, silk.
- Piece generation from distributions: retail formats and size tolerance,
  corner rounding, imperfect cut (wavy edges, skew), fabric mix, procedural
  patterns (solid, end bands, stripes, gingham, border, flag bands) as PNG
  textures. Each aspect has its own random stream; `--no-size`, `--no-cut`,
  `--no-corners`, `--no-color` turn one off without changing the others;
  `--fabric` forces one fabric.
- Meshing: near-equilateral triangles for any outline (`--topology tri`) or a
  structured quad grid over the four cut edges (`--topology grid`), with a
  target vertex count; mesh metrics (area, perimeter, edge lengths, minimum
  angles).
- OpenUSD export: textured UsdPreviewSurface materials, `st`, `hem` and `pin`
  primvars, physical properties and Blender stiffness as `maillage:*`
  attributes, collision ground.
- Blender drape test (`maillage drop-test`, or `blender -b -P` with the
  standalone script): Cusick-style clamped pedestal or hanging flag (optional
  wind), stiffness rescaled to the mesh resolution and the real mass, checks
  (finite, stretch, penetration, at rest), drape coefficient, draped meshes
  exported to OpenUSD with their attributes, optional Cycles render.
- `maillage preview`: flat preview sheet with textures and mesh (matplotlib).
- `maillage list`, `maillage blender-script`.
- Test suite (pytest), lint and format (ruff), continuous integration with a
  Blender drape test of every preset, release workflow, Dependabot, GitHub
  Flow `pre-push` hook.
