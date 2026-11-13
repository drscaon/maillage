# Limits and roadmap

Everything Maillage does not do or has not verified, stated plainly, and what comes next.

Part of the [Maillage](../README.md) documentation.

## Limits

- **OmniPhysics not simulated.** The OmniPhysics layer is checked for
  structure and by the OpenUSD validators, but has not been run in Isaac Sim
  (no NVIDIA GPU here); flags are not attached by their hoist corners there.
- **Stiffness not calibrated.** The engine-neutral stiffness values are
  orders of magnitude, not measurements of these fabrics.
- **Fabrics drape alike in Blender.** Blender's bending stiffness is kept
  low for every fabric (see the [roadmap](#roadmap)): silk and denim drape
  with nearly the same coefficient there. In MuJoCo they differ (see the
  [fabric drape test](engines.md#fabric-drape-test)); use MuJoCo, or the
  engine-neutral stiffness in another shell solver, when the fabric's drape
  matters. No value is calibrated against measurements (no Kawabata or
  Cusick data behind them).
- **Flat pieces only.** No garments (sewn panels), no holes or grommets (a
  flag is pinned at its hoist corners instead), no folded or crumpled starting
  states, no wet cloth.
- **Textures are procedural.** Patterns are clean and regular; no prints,
  logos, stains or wear.

## Roadmap

1. **Stiff fabrics that drape like real ones in Blender.** In MuJoCo the
   fabrics already drape differently (see the
   [fabric drape test](engines.md#fabric-drape-test)). Blender's angular bending
   model (the only one that works on triangle meshes) becomes unstable when
   the bending stiffness is high relative to the vertex mass, as with stiff
   fabrics on fine meshes: instead of settling, the cloth keeps vibrating,
   and adding damping makes it worse. Every fabric's bending stiffness is
   therefore kept below this limit (about 0.015 × areal density for 1 cm
   edges, measured), so a 40 cm square drapes with a coefficient of
   0.35–0.42 whether it is silk or denim. Next steps: more solver steps or a
   coarser simulation mesh for stiff fabrics, quad-grid meshes with
   Blender's linear bending model, and other engines.
2. Pre-draped and crumpled states as OpenUSD variants (the drape test already
   exports draped meshes), and folded states for laundry-folding tasks.
3. A simulation run of the OmniPhysics layer in Isaac Sim, and attachments
   for pinned vertices.
4. Calibration against published fabric measurements.
5. Simple garments from sewing patterns.
