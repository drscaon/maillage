# Sources of the physical values

Every value of Maillage that describes the real world (a fabric's areal
density, thickness, friction and stiffness, a piece's size) names its source
below: the specification of fabrics or products of that kind, or, where none
was found, an estimate with what it rests on. Where a source gives a range,
the value lies within it (`tests/test_sources.py`).

A fabric is a kind of fabric, not a product: its source is the specification
of a few fabrics or products of that kind (bath towels for the terry, flag
fabrics for the polyester knit). No source gives a fabric's stiffness as the
shell models take it: every tensile stiffness and bending rigidity is an
estimate, and nothing is calibrated (see [Physics](physics.md)). The Blender
stiffness is a setting of Blender's solver, derived from the areal density
by the rules of `maillage/fabrics.py`.

The tables are written from `maillage/sources.py`
(`python -m maillage.sources`).

Part of the [Maillage](../README.md) documentation.

<!-- sources: begin -->
| Value | | Unit | Range the source gives | Source |
|---|---|---|---|---|
| `FABRICS.cotton_terry.areal_density` | 450 | g/m² | 400 to 600 | [towel_gsm](#towel_gsm) |
| `FABRICS.cotton_terry.thickness` | 4 | mm |  | [thickness](#thickness) |
| `FABRICS.cotton_terry.friction` | 0.8 |  |  | [friction](#friction) |
| `FABRICS.cotton_terry.tensile_stiffness` | 600 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_terry.bending_rigidity` | 4e-05 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_terry.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.cotton_terry.hem_bending_factor` | 3 |  |  | [hem](#hem) |
| `FABRICS.cotton_waffle.areal_density` | 290 | g/m² | 250 to 350 | [waffle_gsm](#waffle_gsm) |
| `FABRICS.cotton_waffle.thickness` | 1.5 | mm |  | [thickness](#thickness) |
| `FABRICS.cotton_waffle.friction` | 0.6 |  |  | [friction](#friction) |
| `FABRICS.cotton_waffle.tensile_stiffness` | 800 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_waffle.bending_rigidity` | 1.5e-05 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_waffle.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.cotton_waffle.hem_bending_factor` | 3 |  |  | [hem](#hem) |
| `FABRICS.cotton_plain.areal_density` | 140 | g/m² | 100 to 150 | [poplin_gsm](#poplin_gsm) |
| `FABRICS.cotton_plain.thickness` | 0.3 | mm |  | [thickness](#thickness) |
| `FABRICS.cotton_plain.friction` | 0.5 |  |  | [friction](#friction) |
| `FABRICS.cotton_plain.tensile_stiffness` | 1500 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_plain.bending_rigidity` | 6e-06 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_plain.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.cotton_plain.hem_bending_factor` | 4 |  |  | [hem](#hem) |
| `FABRICS.cotton_percale.areal_density` | 130 | g/m² | 125 to 132 | [percale_gsm](#percale_gsm) |
| `FABRICS.cotton_percale.thickness` | 0.25 | mm |  | [thickness](#thickness) |
| `FABRICS.cotton_percale.friction` | 0.5 |  |  | [friction](#friction) |
| `FABRICS.cotton_percale.tensile_stiffness` | 1500 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_percale.bending_rigidity` | 4e-06 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.cotton_percale.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.cotton_percale.hem_bending_factor` | 4 |  |  | [hem](#hem) |
| `FABRICS.linen.areal_density` | 200 | g/m² | 190 to 220 | [linen_gsm](#linen_gsm) |
| `FABRICS.linen.thickness` | 0.35 | mm |  | [thickness](#thickness) |
| `FABRICS.linen.friction` | 0.55 |  |  | [friction](#friction) |
| `FABRICS.linen.tensile_stiffness` | 2500 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.linen.bending_rigidity` | 1.5e-05 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.linen.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.linen.hem_bending_factor` | 3 |  |  | [hem](#hem) |
| `FABRICS.denim.areal_density` | 407 | g/m² | 340 to 475 | [denim_gsm](#denim_gsm) |
| `FABRICS.denim.thickness` | 0.7 | mm |  | [thickness](#thickness) |
| `FABRICS.denim.friction` | 0.6 |  |  | [friction](#friction) |
| `FABRICS.denim.tensile_stiffness` | 4000 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.denim.bending_rigidity` | 0.00012 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.denim.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.denim.hem_bending_factor` | 2 |  |  | [hem](#hem) |
| `FABRICS.fleece.areal_density` | 250 | g/m² | 200 to 260 | [fleece_spec](#fleece_spec) |
| `FABRICS.fleece.thickness` | 1.5 | mm | 0.8 to 1.5 | [fleece_spec](#fleece_spec) |
| `FABRICS.fleece.friction` | 0.8 |  |  | [friction](#friction) |
| `FABRICS.fleece.tensile_stiffness` | 200 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.fleece.bending_rigidity` | 2e-05 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.fleece.poissons_ratio` | 0.35 |  |  | [stiffness](#stiffness) |
| `FABRICS.fleece.hem_bending_factor` | 2 |  |  | [hem](#hem) |
| `FABRICS.microfiber.areal_density` | 300 | g/m² | 300 to 300 | [microfiber_gsm](#microfiber_gsm) |
| `FABRICS.microfiber.thickness` | 2 | mm |  | [thickness](#thickness) |
| `FABRICS.microfiber.friction` | 0.9 |  |  | [friction](#friction) |
| `FABRICS.microfiber.tensile_stiffness` | 500 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.microfiber.bending_rigidity` | 1.5e-05 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.microfiber.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.microfiber.hem_bending_factor` | 1.5 |  |  | [hem](#hem) |
| `FABRICS.polyester_knit.areal_density` | 115 | g/m² | 104.5 to 117 | [flag_fabric](#flag_fabric) |
| `FABRICS.polyester_knit.thickness` | 0.3 | mm | 0.3 to 0.3 | [flag_fabric](#flag_fabric) |
| `FABRICS.polyester_knit.friction` | 0.4 |  |  | [friction](#friction) |
| `FABRICS.polyester_knit.tensile_stiffness` | 600 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.polyester_knit.bending_rigidity` | 1.5e-06 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.polyester_knit.poissons_ratio` | 0.35 |  |  | [stiffness](#stiffness) |
| `FABRICS.polyester_knit.hem_bending_factor` | 4 |  |  | [hem](#hem) |
| `FABRICS.silk.areal_density` | 60 | g/m² | 51.67 to 68.89 | [silk_momme](#silk_momme) |
| `FABRICS.silk.thickness` | 0.1 | mm |  | [thickness](#thickness) |
| `FABRICS.silk.friction` | 0.3 |  |  | [friction](#friction) |
| `FABRICS.silk.tensile_stiffness` | 300 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.silk.bending_rigidity` | 1e-06 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.silk.poissons_ratio` | 0.3 |  |  | [stiffness](#stiffness) |
| `FABRICS.silk.hem_bending_factor` | 4 |  |  | [hem](#hem) |
| `FABRICS.wool_knit.areal_density` | 350 | g/m² |  | [wool_knit](#wool_knit) |
| `FABRICS.wool_knit.thickness` | 3 | mm |  | [thickness](#thickness) |
| `FABRICS.wool_knit.friction` | 0.7 |  |  | [friction](#friction) |
| `FABRICS.wool_knit.tensile_stiffness` | 150 | N/m |  | [stiffness](#stiffness) |
| `FABRICS.wool_knit.bending_rigidity` | 3e-05 | N·m |  | [stiffness](#stiffness) |
| `FABRICS.wool_knit.poissons_ratio` | 0.35 |  |  | [stiffness](#stiffness) |
| `FABRICS.wool_knit.hem_bending_factor` | 1.5 |  |  | [hem](#hem) |
| `PRESETS.bath_towel.formats.0.width` | 70 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bath_towel.formats.0.length` | 140 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bath_towel.formats.1.width` | 90 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bath_towel.formats.1.length` | 150 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bath_towel.tolerance` | 0.02 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.bath_towel.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.bath_towel.corner_radius.max` | 1.5 | cm |  | [cut](#cut) |
| `PRESETS.bath_towel.cut.waviness_mm.min` | 1 | mm |  | [cut](#cut) |
| `PRESETS.bath_towel.cut.waviness_mm.max` | 4 | mm |  | [cut](#cut) |
| `PRESETS.bath_towel.cut.skew_deg` | 1 | ° |  | [cut](#cut) |
| `PRESETS.bath_towel.hem` | 1 | cm |  | [cut](#cut) |
| `PRESETS.hand_towel.formats.0.width` | 50 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.hand_towel.formats.0.length` | 100 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.hand_towel.formats.1.width` | 40 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.hand_towel.formats.1.length` | 60 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.hand_towel.tolerance` | 0.02 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.hand_towel.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.hand_towel.corner_radius.max` | 1.5 | cm |  | [cut](#cut) |
| `PRESETS.hand_towel.cut.waviness_mm.min` | 1 | mm |  | [cut](#cut) |
| `PRESETS.hand_towel.cut.waviness_mm.max` | 3 | mm |  | [cut](#cut) |
| `PRESETS.hand_towel.cut.skew_deg` | 1 | ° |  | [cut](#cut) |
| `PRESETS.hand_towel.hem` | 1 | cm |  | [cut](#cut) |
| `PRESETS.washcloth.formats.0.width` | 30 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.washcloth.formats.0.length` | 30 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.washcloth.tolerance` | 0.02 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.washcloth.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.washcloth.corner_radius.max` | 1 | cm |  | [cut](#cut) |
| `PRESETS.washcloth.cut.waviness_mm.min` | 0.5 | mm |  | [cut](#cut) |
| `PRESETS.washcloth.cut.waviness_mm.max` | 2 | mm |  | [cut](#cut) |
| `PRESETS.washcloth.cut.skew_deg` | 1.5 | ° |  | [cut](#cut) |
| `PRESETS.washcloth.hem` | 0.8 | cm |  | [cut](#cut) |
| `PRESETS.tea_towel.formats.0.width` | 50 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tea_towel.formats.0.length` | 70 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tea_towel.formats.1.width` | 45 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tea_towel.formats.1.length` | 65 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tea_towel.tolerance` | 0.015 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.tea_towel.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.tea_towel.corner_radius.max` | 0.3 | cm |  | [cut](#cut) |
| `PRESETS.tea_towel.cut.waviness_mm.min` | 0.5 | mm |  | [cut](#cut) |
| `PRESETS.tea_towel.cut.waviness_mm.max` | 2.5 | mm |  | [cut](#cut) |
| `PRESETS.tea_towel.cut.skew_deg` | 1 | ° |  | [cut](#cut) |
| `PRESETS.tea_towel.hem` | 1 | cm |  | [cut](#cut) |
| `PRESETS.napkin.formats.0.width` | 40 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.napkin.formats.0.length` | 40 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.napkin.formats.1.width` | 50 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.napkin.formats.1.length` | 50 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.napkin.tolerance` | 0.01 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.napkin.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.napkin.corner_radius.max` | 0.3 | cm |  | [cut](#cut) |
| `PRESETS.napkin.cut.waviness_mm.min` | 0.3 | mm |  | [cut](#cut) |
| `PRESETS.napkin.cut.waviness_mm.max` | 1.5 | mm |  | [cut](#cut) |
| `PRESETS.napkin.cut.skew_deg` | 0.8 | ° |  | [cut](#cut) |
| `PRESETS.napkin.hem` | 0.8 | cm |  | [cut](#cut) |
| `PRESETS.tablecloth.formats.0.width` | 140 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.formats.0.length` | 180 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.formats.1.width` | 140 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.formats.1.length` | 240 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.formats.2.width` | 150 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.formats.2.length` | 150 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.formats.3.width` | 140 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.formats.3.length` | 200 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.tablecloth.tolerance` | 0.01 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.tablecloth.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.tablecloth.corner_radius.max` | 1 | cm |  | [cut](#cut) |
| `PRESETS.tablecloth.cut.waviness_mm.min` | 1 | mm |  | [cut](#cut) |
| `PRESETS.tablecloth.cut.waviness_mm.max` | 4 | mm |  | [cut](#cut) |
| `PRESETS.tablecloth.cut.skew_deg` | 0.5 | ° |  | [cut](#cut) |
| `PRESETS.tablecloth.hem` | 1.5 | cm |  | [cut](#cut) |
| `PRESETS.bed_sheet.formats.0.width` | 180 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bed_sheet.formats.0.length` | 290 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bed_sheet.formats.1.width` | 240 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bed_sheet.formats.1.length` | 300 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bed_sheet.formats.2.width` | 270 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bed_sheet.formats.2.length` | 310 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bed_sheet.tolerance` | 0.015 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.bed_sheet.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.bed_sheet.corner_radius.max` | 0.5 | cm |  | [cut](#cut) |
| `PRESETS.bed_sheet.cut.waviness_mm.min` | 2 | mm |  | [cut](#cut) |
| `PRESETS.bed_sheet.cut.waviness_mm.max` | 6 | mm |  | [cut](#cut) |
| `PRESETS.bed_sheet.cut.skew_deg` | 0.5 | ° |  | [cut](#cut) |
| `PRESETS.bed_sheet.hem` | 2 | cm |  | [cut](#cut) |
| `PRESETS.microfiber_cloth.formats.0.width` | 40 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.microfiber_cloth.formats.0.length` | 40 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.microfiber_cloth.formats.1.width` | 30 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.microfiber_cloth.formats.1.length` | 30 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.microfiber_cloth.tolerance` | 0.015 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.microfiber_cloth.corner_radius.min` | 0.5 | cm |  | [cut](#cut) |
| `PRESETS.microfiber_cloth.corner_radius.max` | 2.5 | cm |  | [cut](#cut) |
| `PRESETS.microfiber_cloth.cut.waviness_mm.min` | 0.3 | mm |  | [cut](#cut) |
| `PRESETS.microfiber_cloth.cut.waviness_mm.max` | 1.5 | mm |  | [cut](#cut) |
| `PRESETS.microfiber_cloth.cut.skew_deg` | 1 | ° |  | [cut](#cut) |
| `PRESETS.microfiber_cloth.hem` | 0.4 | cm |  | [cut](#cut) |
| `PRESETS.bandana.formats.0.width` | 55 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bandana.formats.0.length` | 55 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.bandana.tolerance` | 0.015 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.bandana.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.bandana.corner_radius.max` | 0.3 | cm |  | [cut](#cut) |
| `PRESETS.bandana.cut.waviness_mm.min` | 0.5 | mm |  | [cut](#cut) |
| `PRESETS.bandana.cut.waviness_mm.max` | 2 | mm |  | [cut](#cut) |
| `PRESETS.bandana.cut.skew_deg` | 1 | ° |  | [cut](#cut) |
| `PRESETS.bandana.hem` | 0.5 | cm |  | [cut](#cut) |
| `PRESETS.silk_scarf.formats.0.width` | 90 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.silk_scarf.formats.0.length` | 90 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.silk_scarf.formats.1.width` | 50 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.silk_scarf.formats.1.length` | 160 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.silk_scarf.tolerance` | 0.01 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.silk_scarf.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.silk_scarf.corner_radius.max` | 0.3 | cm |  | [cut](#cut) |
| `PRESETS.silk_scarf.cut.waviness_mm.min` | 0.3 | mm |  | [cut](#cut) |
| `PRESETS.silk_scarf.cut.waviness_mm.max` | 1 | mm |  | [cut](#cut) |
| `PRESETS.silk_scarf.cut.skew_deg` | 0.5 | ° |  | [cut](#cut) |
| `PRESETS.silk_scarf.hem` | 0.5 | cm |  | [cut](#cut) |
| `PRESETS.scarf.formats.0.width` | 25 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.scarf.formats.0.length` | 160 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.scarf.formats.1.width` | 30 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.scarf.formats.1.length` | 180 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.scarf.formats.2.width` | 20 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.scarf.formats.2.length` | 140 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.scarf.tolerance` | 0.03 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.scarf.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.scarf.corner_radius.max` | 0.5 | cm |  | [cut](#cut) |
| `PRESETS.scarf.cut.waviness_mm.min` | 1 | mm |  | [cut](#cut) |
| `PRESETS.scarf.cut.waviness_mm.max` | 4 | mm |  | [cut](#cut) |
| `PRESETS.scarf.cut.skew_deg` | 1 | ° |  | [cut](#cut) |
| `PRESETS.scarf.hem` | 0.5 | cm |  | [cut](#cut) |
| `PRESETS.flag.formats.0.width` | 100 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.flag.formats.0.length` | 150 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.flag.formats.1.width` | 60 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.flag.formats.1.length` | 90 | cm |  | [retail_sizes](#retail_sizes) |
| `PRESETS.flag.tolerance` | 0.01 |  |  | [size_tolerance](#size_tolerance) |
| `PRESETS.flag.corner_radius.min` | 0 | cm |  | [cut](#cut) |
| `PRESETS.flag.corner_radius.max` | 0 | cm |  | [cut](#cut) |
| `PRESETS.flag.cut.waviness_mm.min` | 0.3 | mm |  | [cut](#cut) |
| `PRESETS.flag.cut.waviness_mm.max` | 1.5 | mm |  | [cut](#cut) |
| `PRESETS.flag.cut.skew_deg` | 0.5 | ° |  | [cut](#cut) |
| `PRESETS.flag.hem` | 1.5 | cm |  | [cut](#cut) |

### Sources

- <a id="towel_gsm"></a>**towel_gsm** (datasheet): Cotton bath towels: medium weight 400 to 600 g/m² (Fine Linen and Bath); The Towel Shop's bath towels 400 to 600 GSM, 500 GSM the most usual. <https://flandb.com/blogs/by-flandb/a-guide-to-buying-luxury-bath-towels-fabric-gsm-and-more>, <https://www.thetowelshop.co.uk/Towels>
- <a id="waffle_gsm"></a>**waffle_gsm** (datasheet): Cotton waffle towels: kitchen waffle weaves 250 to 350 g/m² (KitchPrep); Brooklinen waffle hand towel, 290 GSM. <https://kitchprep.com/?p=117785>, <https://brooklinen.com/products/waffle-hand-towels>
- <a id="poplin_gsm"></a>**poplin_gsm** (datasheet): Cotton poplin (plain weave): 100 to 150 g/m² (Maker's Row); Fabriclore 40s poplin, 140 GSM. <https://makersrow.com/blog/what-is-poplin-fabric/>, <https://fabriclore.com/products/off-white-plain-40s-cotton-poplin-fabric-72-132-g-ctpp00013>
- <a id="percale_gsm"></a>**percale_gsm** (datasheet): Cotton percale bed linen: Lemieux et Cie, 125 GSM, 200 thread count; Manufactum, 132 g/m², 200 threads. <https://lemieuxetcie.com/blogs/the-edit/good-thread-count-sheets>, <https://www.manufactum.com/fitted-sheet-percale-a44741/>
- <a id="linen_gsm"></a>**linen_gsm** (datasheet): Linen tea towels: Magic Linen, 190 GSM; Restatrade, approx. 200 g/m²; Manufactum (Schlitzer), 220 g/m². <https://magiclinen.com/products/linen-tea-towel-in-calm-sage>, <https://www.restatrade.ee/en/?p=127365>, <https://www.manufactum.com/tea-towel-slash-linen-a84187/>
- <a id="denim_gsm"></a>**denim_gsm** (handbook): Denim weight: 1 oz/yd² = 33.906 g/m², 12 oz ≈ 407 g/m², mid-weight denim 10 to 14 oz (340 to 475 g/m²). <https://fumaofabric.com/?p=5017>
- <a id="fleece_spec"></a>**fleece_spec** (datasheet): Polar fleece (MH): mid-weight 200 to 260 gsm, thickness 0.8 to 1.5 mm. <https://www.mh-chine.com/blog/products/polar-fleece-fabric>
- <a id="microfiber_gsm"></a>**microfiber_gsm** (datasheet): Microfiber cleaning cloths, 80 % polyester / 20 % polyamide: Hospeco heavy duty, 300 GSM; Paragon premium, 300 gsm. <https://zogics.com/en/cleaning-supplies/heavy-duty-black-microfiber-cloths-300-gsm-16x16-1-dozen>, <https://eu.paragonmicrofibre.com/products/premium-microfibre-cloths-300-gsm>
- <a id="flag_fabric"></a>**flag_fabric** (datasheet): Knitted polyester flag fabrics: Soyang ST-118, 115 g/m²; be.flag Wind, 110 g/m², 0.30 mm thick; G.O. Friedrich Re-Jetflag GS, 110 g/m² ± 5 %; Soyang ST-110, 117 gsm. <https://soyang.co.uk/wp-content/uploads/2023/08/Soyang-ST-118-spec.pdf>, <https://verla.ro/f/MF009536%5CG%20Flag%20117%20FR%20%20Fisa%20tehnica%20EN.pdf>, <https://g-o-friedrich.com/en/produkt/6144rcgs-re-jetflag-gs>, <https://soyang.co.uk/product/st-110/>
- <a id="silk_momme"></a>**silk_momme** (handbook): Silk weight in momme: 1 momme = 4.3056 g/m² (Maison de la Soie); habotai 12 to 16 momme (51.7 to 68.9 g/m², A Silk Life). <https://www.maisondelasoie.com/en/pages/what-is-a-momme>, <https://asilklife.com/blogs/blog/what-is-momme-in-silk-fabric-what-is-thread-count>
- <a id="wool_knit"></a>**wool_knit** (estimate): areal density of a knitted wool scarf. Estimate: a chunky hand-feel knit, heavier than a fleece; no specification was consulted.
- <a id="thickness"></a>**thickness** (estimate): thickness of the fabrics without a specification of it. Estimate: from the areal density and the kind of fabric: a woven a little over its yarns (0.1 mm silk to 0.7 mm denim), a pile or a knit several millimetres (terry 4 mm, wool knit 3 mm); used for the collision distance and the render, not for the stiffness.
- <a id="stiffness"></a>**stiffness** (estimate): tensile stiffness and bending rigidity of each fabric, and its Poisson ratio. Estimate: orders of magnitude of published Kawabata (KES-FB2) bending rigidity, 1 gf·cm²/cm = 9.81e-5 N·m: 0.018 to 0.119 gf·cm²/cm (1.8e-6 to 1.2e-5 N·m) for plain-woven shirting fabrics, 0.002 to 0.05 for knit cottons; denim, terry and the knits set by kind. Tensile stiffness 1e2 N/m for weft knits to a few 1e3 N/m for wovens. Not measured on these fabrics, not calibrated. <https://core.ac.uk/download/pdf/229215627.pdf>, <https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5427156>
- <a id="hem"></a>**hem** (estimate): how much stiffer a hemmed edge is in bending. Estimate: a hem folds the fabric twice and stitches it: three layers bend as about 3 times one, more for thin fabrics whose seam dominates, less for thick or knitted edges.
- <a id="friction"></a>**friction** (estimate): dry friction of each fabric against a smooth hard surface. Estimate: 0.3 for silk to 0.9 for a microfiber's split fibres; pile and brushed fabrics grip more than smooth wovens. No measurement of these fabrics was consulted.
- <a id="retail_sizes"></a>**retail_sizes** (estimate): the nominal sizes of each kind of piece. Estimate: the sizes such pieces are commonly sold in (face cloth 30 × 30 cm, hand towel 50 × 85, bath towel 70 × 130, bath sheet 90 × 150 at The Towel Shop); their weights are a choice, not a statistic. <https://www.thetowelshop.co.uk/Towels>
- <a id="size_tolerance"></a>**size_tolerance** (estimate): spread of a piece's size around its nominal size (relative standard deviation). Estimate: cutting and shrinkage: cotton poplin shrinks 3 to 5 %, a linen tea towel about 3 %; 1 % to 3 % of standard deviation, more for knits. <https://cdn.shopify.com/s/files/1/1566/9911/files/fabric-info-Cotton_Poplin.pdf>, <https://www.manufactum.com/tea-towel-slash-linen-a84187/>
- <a id="cut"></a>**cut** (estimate): corner rounding, waviness and skew of a cut edge, and the hem's width. Estimate: the look of real pieces: rounded corners of a few millimetres to 2.5 cm (overlocked cloths), edges wavy by up to a few millimetres, corners off square by up to 1.5°; hems 0.4 to 2 cm.

### Numbers that are not physical values

- `FABRICS.*.blender, BLENDER_REFERENCE_EDGE`: the stiffness Blender's mass-spring cloth solver takes, set by the rules of fabrics.py from the areal density and the solver's stability (docs/physics.md).
- `FABRICS.*.roughness`: render appearance, not a physical property.
- `PRESETS.*.formats weights, fabrics, patterns, colours`: how often each size, fabric, pattern and colour is drawn: a choice, declared in docs/variation.md.
- `declared.CLIP`: the size's normal draws are kept within ±2.5 standard deviations: a choice.
- `ground.GROUND_*`: the shared ground of the Primvaria suite (ground.py), the same in every generator.
<!-- sources: end -->
