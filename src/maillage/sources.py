"""Where every physical value of Maillage comes from (PRV-33).

Each value that describes the real world (a fabric's areal density, thickness, friction and stiffness, a
piece's size) names its source: the specification of a fabric or a product of that kind, or, where none
was found, an estimate with what it rests on. Where the source gives a range, the value lies within it;
tests/test_sources.py checks it, and that no value is left without a source.

A fabric is a kind of fabric, not a product: its source is the specification of a few fabrics or
products of that kind (bath towels for the terry, flag fabrics for the polyester knit). No source gives a
fabric's stiffness as the shell models take it: every tensile stiffness and bending rigidity is an
estimate, and nothing is calibrated.

The Blender stiffness (`FABRICS.*.blender`) is not a property of the fabric but of Blender's solver, set
by the rules of fabrics.py from the areal density.

    python -m maillage.sources     # the tables of docs/sources.md
"""

from __future__ import annotations

from dataclasses import dataclass

from .fabrics import FABRICS
from .presets import PRESETS

KINDS = ("standard table", "datasheet", "handbook", "estimate")
MOMME = 4.3056  # g/m² per momme, the weight unit of silk


@dataclass(frozen=True)
class Source:
    kind: str  # one of KINDS
    title: str
    urls: tuple = ()
    note: str = ""  # for an estimate: what it rests on


SOURCES = {
    "towel_gsm": Source(
        "datasheet",
        "Cotton bath towels: medium weight 400 to 600 g/m² (Fine Linen and Bath); The Towel Shop's bath "
        "towels 400 to 600 GSM, 500 GSM the most usual",
        (
            "https://flandb.com/blogs/by-flandb/a-guide-to-buying-luxury-bath-towels-fabric-gsm-and-more",
            "https://www.thetowelshop.co.uk/Towels",
        ),
    ),
    "waffle_gsm": Source(
        "datasheet",
        "Cotton waffle towels: kitchen waffle weaves 250 to 350 g/m² (KitchPrep); Brooklinen waffle hand "
        "towel, 290 GSM",
        ("https://kitchprep.com/?p=117785", "https://brooklinen.com/products/waffle-hand-towels"),
    ),
    "poplin_gsm": Source(
        "datasheet",
        "Cotton poplin (plain weave): 100 to 150 g/m² (Maker's Row); Fabriclore 40s poplin, 140 GSM",
        (
            "https://makersrow.com/blog/what-is-poplin-fabric/",
            "https://fabriclore.com/products/off-white-plain-40s-cotton-poplin-fabric-72-132-g-ctpp00013",
        ),
    ),
    "percale_gsm": Source(
        "datasheet",
        "Cotton percale bed linen: Lemieux et Cie, 125 GSM, 200 thread count; Manufactum, 132 g/m², "
        "200 threads",
        (
            "https://lemieuxetcie.com/blogs/the-edit/good-thread-count-sheets",
            "https://www.manufactum.com/fitted-sheet-percale-a44741/",
        ),
    ),
    "linen_gsm": Source(
        "datasheet",
        "Linen tea towels: Magic Linen, 190 GSM; Restatrade, approx. 200 g/m²; Manufactum (Schlitzer), "
        "220 g/m²",
        (
            "https://magiclinen.com/products/linen-tea-towel-in-calm-sage",
            "https://www.restatrade.ee/en/?p=127365",
            "https://www.manufactum.com/tea-towel-slash-linen-a84187/",
        ),
    ),
    "denim_gsm": Source(
        "handbook",
        "Denim weight: 1 oz/yd² = 33.906 g/m², 12 oz ≈ 407 g/m², mid-weight denim 10 to 14 oz (340 to "
        "475 g/m²)",
        ("https://fumaofabric.com/?p=5017",),
    ),
    "fleece_spec": Source(
        "datasheet",
        "Polar fleece (MH): mid-weight 200 to 260 gsm, thickness 0.8 to 1.5 mm",
        ("https://www.mh-chine.com/blog/products/polar-fleece-fabric",),
    ),
    "microfiber_gsm": Source(
        "datasheet",
        "Microfiber cleaning cloths, 80 % polyester / 20 % polyamide: Hospeco heavy duty, 300 GSM; Paragon "
        "premium, 300 gsm",
        (
            "https://zogics.com/en/cleaning-supplies/heavy-duty-black-microfiber-cloths-300-gsm-16x16-1-dozen",
            "https://eu.paragonmicrofibre.com/products/premium-microfibre-cloths-300-gsm",
        ),
    ),
    "flag_fabric": Source(
        "datasheet",
        "Knitted polyester flag fabrics: Soyang ST-118, 115 g/m²; be.flag Wind, 110 g/m², 0.30 mm thick; "
        "G.O. Friedrich Re-Jetflag GS, 110 g/m² ± 5 %; Soyang ST-110, 117 gsm",
        (
            "https://soyang.co.uk/wp-content/uploads/2023/08/Soyang-ST-118-spec.pdf",
            "https://verla.ro/f/MF009536%5CG%20Flag%20117%20FR%20%20Fisa%20tehnica%20EN.pdf",
            "https://g-o-friedrich.com/en/produkt/6144rcgs-re-jetflag-gs",
            "https://soyang.co.uk/product/st-110/",
        ),
    ),
    "silk_momme": Source(
        "handbook",
        "Silk weight in momme: 1 momme = 4.3056 g/m² (Maison de la Soie); habotai 12 to 16 momme "
        "(51.7 to 68.9 g/m², A Silk Life)",
        (
            "https://www.maisondelasoie.com/en/pages/what-is-a-momme",
            "https://asilklife.com/blogs/blog/what-is-momme-in-silk-fabric-what-is-thread-count",
        ),
    ),
    # ------------------------------------------------------------------ estimates
    "wool_knit": Source(
        "estimate",
        "areal density of a knitted wool scarf",
        note="a chunky hand-feel knit, heavier than a fleece; no specification was consulted",
    ),
    "thickness": Source(
        "estimate",
        "thickness of the fabrics without a specification of it",
        note="from the areal density and the kind of fabric: a woven a little over its yarns (0.1 mm silk to "
        "0.7 mm denim), a pile or a knit several millimetres (terry 4 mm, wool knit 3 mm); used for the "
        "collision distance and the render, not for the stiffness",
    ),
    "stiffness": Source(
        "estimate",
        "tensile stiffness and bending rigidity of each fabric, and its Poisson ratio",
        (
            "https://core.ac.uk/download/pdf/229215627.pdf",
            "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5427156",
        ),
        note="orders of magnitude of published Kawabata (KES-FB2) bending rigidity, "
        "1 gf·cm²/cm = 9.81e-5 N·m: 0.018 to 0.119 gf·cm²/cm (1.8e-6 to 1.2e-5 N·m) for plain-woven shirting "
        "fabrics, 0.002 to 0.05 "
        "for knit cottons; denim, terry and the knits set by kind. Tensile stiffness 1e2 N/m for weft knits "
        "to a few 1e3 N/m for wovens. Not measured on these fabrics, not calibrated",
    ),
    "hem": Source(
        "estimate",
        "how much stiffer a hemmed edge is in bending",
        note="a hem folds the fabric twice and stitches it: three layers bend as about 3 times one, more for "
        "thin fabrics whose seam dominates, less for thick or knitted edges",
    ),
    "friction": Source(
        "estimate",
        "dry friction of each fabric against a smooth hard surface",
        note="0.3 for silk to 0.9 for a microfiber's split fibres; pile and brushed fabrics grip more than "
        "smooth wovens. No measurement of these fabrics was consulted",
    ),
    "retail_sizes": Source(
        "estimate",
        "the nominal sizes of each kind of piece",
        ("https://www.thetowelshop.co.uk/Towels",),
        note="the sizes such pieces are commonly sold in (face cloth 30 × 30 cm, hand towel 50 × 85, "
        "bath towel 70 × 130, bath sheet 90 × 150 at The Towel Shop); their weights are a "
        "choice, not a statistic",
    ),
    "size_tolerance": Source(
        "estimate",
        "spread of a piece's size around its nominal size (relative standard deviation)",
        (
            "https://cdn.shopify.com/s/files/1/1566/9911/files/fabric-info-Cotton_Poplin.pdf",
            "https://www.manufactum.com/tea-towel-slash-linen-a84187/",
        ),
        note="cutting and shrinkage: cotton poplin shrinks 3 to 5 %, a linen tea towel about 3 %; 1 % to 3 % "
        "of standard deviation, more for knits",
    ),
    "cut": Source(
        "estimate",
        "corner rounding, waviness and skew of a cut edge, and the hem's width",
        note="the look of real pieces: rounded corners of a few millimetres to 2.5 cm (overlocked cloths), "
        "edges wavy by up to a few millimetres, corners off square by up to 1.5°; hems 0.4 to 2 cm",
    ),
}

AREAL = {  # fabric: (source, range the source gives in g/m²)
    "cotton_terry": ("towel_gsm", 400.0, 600.0),
    "cotton_waffle": ("waffle_gsm", 250.0, 350.0),
    "cotton_plain": ("poplin_gsm", 100.0, 150.0),
    "cotton_percale": ("percale_gsm", 125.0, 132.0),
    "linen": ("linen_gsm", 190.0, 220.0),
    "denim": ("denim_gsm", 340.0, 475.0),
    "fleece": ("fleece_spec", 200.0, 260.0),
    "microfiber": ("microfiber_gsm", 300.0, 300.0),
    "polyester_knit": ("flag_fabric", 110.0 * 0.95, 117.0),
    "silk": ("silk_momme", 12 * MOMME, 16 * MOMME),
    "wool_knit": ("wool_knit", None, None),
}

THICKNESS = {  # fabric: (source, range the source gives in mm); the rest are estimates
    "fleece": ("fleece_spec", 0.8, 1.5),
    "polyester_knit": ("flag_fabric", 0.30, 0.30),
}


@dataclass(frozen=True)
class Value:
    path: str  # where it is in the code: FABRICS.linen.areal_density
    value: float
    unit: str
    source: str  # a key of SOURCES
    low: float | None = None  # the range the source gives, when it gives one
    high: float | None = None


def _fabrics() -> list[Value]:
    out = []
    for key, f in FABRICS.items():
        name = f"FABRICS.{key}"
        out.append(Value(f"{name}.areal_density", round(f["areal_density"] * 1e3, 6), "g/m²", *AREAL[key]))
        src, lo, hi = THICKNESS.get(key, ("thickness", None, None))
        out.append(Value(f"{name}.thickness", round(f["thickness"] * 1e3, 6), "mm", src, lo, hi))
        out.append(Value(f"{name}.friction", f["friction"], "", "friction"))
        out.append(Value(f"{name}.tensile_stiffness", f["tensile_stiffness"], "N/m", "stiffness"))
        out.append(Value(f"{name}.bending_rigidity", f["bending_rigidity"], "N·m", "stiffness"))
        out.append(Value(f"{name}.poissons_ratio", f["poissons_ratio"], "", "stiffness"))
        out.append(Value(f"{name}.hem_bending_factor", f["hem_bending_factor"], "", "hem"))
    return out


def _presets() -> list[Value]:
    out = []
    for key, p in PRESETS.items():
        name = f"PRESETS.{key}"
        for i, fmt in enumerate(p["formats"]):
            out.append(Value(f"{name}.formats.{i}.width", fmt["width"], "cm", "retail_sizes"))
            out.append(Value(f"{name}.formats.{i}.length", fmt["length"], "cm", "retail_sizes"))
        out.append(Value(f"{name}.tolerance", p["tolerance"], "", "size_tolerance"))
        for end, x in zip(("min", "max"), p["corner_radius"], strict=True):
            out.append(Value(f"{name}.corner_radius.{end}", x, "cm", "cut"))
        for end, x in zip(("min", "max"), p["cut"]["waviness_mm"], strict=True):
            out.append(Value(f"{name}.cut.waviness_mm.{end}", x, "mm", "cut"))
        out.append(Value(f"{name}.cut.skew_deg", p["cut"]["skew_deg"], "°", "cut"))
        out.append(Value(f"{name}.hem", p["hem"], "cm", "cut"))
    return out


def values() -> list[Value]:
    """Every physical value of the generator, with its source."""
    return _fabrics() + _presets()


# Numbers in the code that are not about the real world, and so have no source: what they are.
NOT_PHYSICAL = {
    "FABRICS.*.blender, BLENDER_REFERENCE_EDGE": "the stiffness Blender's mass-spring cloth solver takes, "
    "set by the rules of fabrics.py from the areal density and the solver's stability (docs/physics.md)",
    "FABRICS.*.roughness": "render appearance, not a physical property",
    "PRESETS.*.formats weights, fabrics, patterns, colours": "how often each size, fabric, pattern and "
    "colour is drawn: a choice, declared in docs/variation.md",
    "declared.CLIP": "the size's normal draws are kept within ±2.5 standard deviations: a choice",
    "ground.GROUND_*": "the shared ground of the Primvaria suite (ground.py), the same in every generator",
}


def _fmt(x) -> str:
    return "" if x is None else f"{x:.4g}"


def table() -> str:
    """The Markdown tables of docs/sources.md."""
    out = ["| Value | | Unit | Range the source gives | Source |", "|---|---|---|---|---|"]
    for v in values():
        span = f"{_fmt(v.low)} to {_fmt(v.high)}" if v.low is not None or v.high is not None else ""
        span = "" if span == " to " else span.strip()
        out.append(f"| `{v.path}` | {v.value:g} | {v.unit} | {span} | [{v.source}](#{v.source}) |")
    out += ["", "### Sources", ""]
    for key, s in SOURCES.items():
        links = ", ".join(f"<{u}>" for u in s.urls)
        note = f" Estimate: {s.note}." if s.note else ""
        line = f'- <a id="{key}"></a>**{key}** ({s.kind}): {s.title}.{note}'
        out.append(line + (f" {links}" if links else ""))
    out += ["", "### Numbers that are not physical values", ""]
    out += [f"- `{name}`: {why}." for name, why in NOT_PHYSICAL.items()]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    print(table())
