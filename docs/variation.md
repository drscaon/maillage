# What each piece draws

Every Maillage piece draws its own values, aspect by aspect (see
[openusd.md](openusd.md) for where they are written). Each value follows a
rule applied to its preset's own numbers: the rules first, then the values
each pattern draws, then the numbers of every preset.

The tables are written from `maillage/declared.py` and the presets, and
`tests/test_distributions.py` draws a thousand pieces of every preset to
check that the generator follows them: every value lies in its declared
range and follows its rule (chi-square for choices, Kolmogorov-Smirnov for
numbers, at p > 0.001), and each piece records exactly the declared values
and those of its pattern. Regenerate the tables with
`python -m maillage.declared`.

A piece records the colours its texture paints: a `solid` piece has one.
Drawn but not recorded: the phases of the cut's waves, the widths of a
`bands` pattern, and where the mesh's interior points fall. The fabric's
own properties (areal density, stiffness) come from the fabric drawn, not
from a draw of their own: see [physics.md](physics.md).

<!-- declared: begin -->

### Rules

| Column | Aspect | Drawn as |
|---|---|---|
| `variation:format_shape` | size | the shape of a format drawn from the preset's `formats`, with their weights |
| `variation:format_length_m` | size | the length of that format |
| `variation:format_width_m` | size | the width of that format |
| `variation:length_m` | size | format length × (1 + `tolerance` × e), e normal, kept within ±2.5 |
| `variation:width_m` | size | format width × (1 + `tolerance` × e), another e, kept within ±2.5 |
| `variation:corner_radius_m` | corners | uniform within the preset's `corner_radius` (cm); 0 for an ellipse or the grid topology |
| `variation:cut_amplitudes_m` | cut | three waves: a uniform amplitude within `cut.waviness_mm`, shared by Dirichlet(2, 2, 2) weights, the third wave at 0.3 times its share |
| `variation:cut_cycles` | cut | whole numbers of waves along the outline: 2 to 5, 5 to 11, 18 to 39 |
| `variation:cut_skew_deg` | cut | uniform within ± `cut.skew_deg` |
| `variation:fabric` | fabric | one of the preset's `fabrics`, with their weights |
| `variation:pattern` | color | one of the preset's `patterns`, with their weights |
| `variation:colors` | color | a base from `base_colors`, each as likely; then an accent from `accent_colors` that is not the base (not for `solid`, which has one colour); `bands`: 2 or 3 colours (3 at 70 %) |

### The pattern's own values

| Pattern | Column | Drawn as |
|---|---|---|
| `solid` | (none) | |
| `end_bands` | `variation:pattern_inset_m` | uniform, 0.05 to 0.12 m |
| `end_bands` | `variation:pattern_band_m` | uniform, 0.02 to 0.07 m |
| `end_bands` | `variation:pattern_double` | yes at 40 % |
| `cross_stripes` | `variation:pattern_period_m` | uniform, 0.06 to 0.2 m |
| `cross_stripes` | `variation:pattern_stripe_m` | the period × uniform 0.3 to 0.5 |
| `stripes` | `variation:pattern_period_m` | uniform, 0.02 to 0.12 m |
| `stripes` | `variation:pattern_stripe_m` | the period × uniform 0.1 to 0.4 |
| `gingham` | `variation:pattern_period_m` | uniform, 0.01 to 0.04 m |
| `border` | `variation:pattern_inset_m` | uniform, 0.015 to 0.06 m |
| `border` | `variation:pattern_band_m` | uniform, 0.005 to 0.03 m |
| `bands` | `variation:pattern_vertical` | yes at 50 % |

### The presets' numbers

| Preset | `formats` (cm, weight) | `tolerance` | `corner_radius` (cm) | `cut.waviness_mm` | `cut.skew_deg` | `fabrics` | `patterns` | colours (base, accent) |
|---|---|---|---|---|---|---|---|---|
| `bath_towel` | rect 140 × 70 (0.7), rect 150 × 90 (0.3) | 0.02 | 0 to 1.5 | 1 to 4 | ±1 | cotton_terry 100 % | solid 50 %, end_bands 50 % | 8, 5 |
| `hand_towel` | rect 100 × 50 (0.6), rect 60 × 40 (0.4) | 0.02 | 0 to 1.5 | 1 to 3 | ±1 | cotton_terry 100 % | solid 50 %, end_bands 50 % | 8, 5 |
| `washcloth` | rect 30 × 30 (1) | 0.02 | 0 to 1 | 0.5 to 2 | ±1.5 | cotton_terry 100 % | solid 70 %, end_bands 30 % | 8, 5 |
| `tea_towel` | rect 70 × 50 (0.7), rect 65 × 45 (0.3) | 0.015 | 0 to 0.3 | 0.5 to 2.5 | ±1 | cotton_waffle 40 %, linen 40 %, cotton_plain 20 % | solid 20 %, stripes 35 %, gingham 25 %, end_bands 20 % | 5, 6 |
| `napkin` | rect 40 × 40 (0.6), rect 50 × 50 (0.4) | 0.01 | 0 to 0.3 | 0.3 to 1.5 | ±0.8 | linen 60 %, cotton_plain 40 % | solid 60 %, border 40 % | 6, 6 |
| `tablecloth` | rect 180 × 140 (0.35), rect 240 × 140 (0.25), ellipse 150 × 150 (0.25), ellipse 200 × 140 (0.15) | 0.01 | 0 to 1 | 1 to 4 | ±0.5 | cotton_plain 50 %, linen 50 % | solid 50 %, gingham 30 %, border 20 % | 5, 6 |
| `bed_sheet` | rect 290 × 180 (0.4), rect 300 × 240 (0.4), rect 310 × 270 (0.2) | 0.015 | 0 to 0.5 | 2 to 6 | ±0.5 | cotton_percale 70 %, linen 30 % | solid 70 %, stripes 30 % | 6, 4 |
| `microfiber_cloth` | rect 40 × 40 (0.7), rect 30 × 30 (0.3) | 0.015 | 0.5 to 2.5 | 0.3 to 1.5 | ±1 | microfiber 100 % | solid 100 % | 7, 1 |
| `bandana` | rect 55 × 55 (1) | 0.015 | 0 to 0.3 | 0.5 to 2 | ±1 | cotton_plain 100 % | border 60 %, gingham 20 %, solid 20 % | 6, 3 |
| `silk_scarf` | rect 90 × 90 (0.6), rect 160 × 50 (0.4) | 0.01 | 0 to 0.3 | 0.3 to 1 | ±0.5 | silk 100 % | solid 30 %, border 40 %, stripes 30 % | 6, 4 |
| `scarf` | rect 160 × 25 (0.5), rect 180 × 30 (0.3), rect 140 × 20 (0.2) | 0.03 | 0 to 0.5 | 1 to 4 | ±1 | wool_knit 100 % | cross_stripes 50 %, solid 30 %, gingham 20 % | 7, 5 |
| `flag` | rect 150 × 100 (0.6), rect 90 × 60 (0.4) | 0.01 | 0 to 0 | 0.3 to 1.5 | ±0.5 | polyester_knit 100 % | bands 100 % | 7, 6 |

<!-- declared: end -->
