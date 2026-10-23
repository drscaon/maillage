"""Textile item presets: what kind of piece is generated.

Each preset describes *distributions*, not a single piece:

- formats: nominal sizes with weights; width and length in cm (width is the
  shorter side across the y axis, length along x), shape "rect" or "ellipse"
  (round and oval tablecloths); tolerance: relative standard deviation of the
  actual size around the nominal one (cutting and shrinkage);
- fabrics: fabric names (see fabrics.py) with weights;
- corner_radius: range of the corner rounding radius in cm (rect only);
- cut: irregularity of a real cut edge: waviness amplitude range in mm along
  each edge and maximum skew of the corners in degrees (a slightly
  parallelogram piece);
- hem: width of the hemmed band along the edges in cm (0: no hem); exported
  as the `hem` vertex primvar, stiffer in bending in Blender;
- pins: "hoist" pins the two corners of the left short edge (flags hung from a
  halyard); exported as the `pin` vertex primvar;
- patterns: printed or woven patterns with weights (see texture.py);
- base_colors / accent_colors: palettes (sRGB hex) the pattern colours are
  drawn from;
- category: display family (see CATEGORIES).

Sizes are common retail formats; values are realistic orders of magnitude.
"""

CATEGORIES = ["Bath", "Kitchen", "Table", "Bedding", "Cleaning", "Accessories", "Outdoor"]

_TOWEL_BASE = ["#f4f1ea", "#ffffff", "#c9d6df", "#2f4858", "#86a873", "#d9a5b3", "#e8c07d", "#7d8a96"]
_TOWEL_ACCENT = ["#ffffff", "#2f4858", "#c0392b", "#d4ac0d", "#5d6d7e"]
_KITCHEN_BASE = ["#f7f3e8", "#e9e4d8", "#d8c8a8", "#ffffff", "#b5c7b0"]
_KITCHEN_ACCENT = ["#b03a2e", "#1f4e79", "#2e7d32", "#5d4037", "#e1a33a", "#37474f"]

PRESETS = {
    # ------------------------------------------------------------------ Bath
    "bath_towel": {
        "category": "Bath",
        "label": "Bath towel",
        "formats": [
            {"width": 70, "length": 140, "shape": "rect", "weight": 0.7},
            {"width": 90, "length": 150, "shape": "rect", "weight": 0.3},
        ],
        "tolerance": 0.02,
        "fabrics": {"cotton_terry": 1.0},
        "corner_radius": (0.0, 1.5),
        "cut": {"waviness_mm": (1.0, 4.0), "skew_deg": 1.0},
        "hem": 1.0,
        "patterns": {"solid": 0.5, "end_bands": 0.5},
        "base_colors": _TOWEL_BASE,
        "accent_colors": _TOWEL_ACCENT,
    },
    "hand_towel": {
        "category": "Bath",
        "label": "Hand towel",
        "formats": [
            {"width": 50, "length": 100, "shape": "rect", "weight": 0.6},
            {"width": 40, "length": 60, "shape": "rect", "weight": 0.4},
        ],
        "tolerance": 0.02,
        "fabrics": {"cotton_terry": 1.0},
        "corner_radius": (0.0, 1.5),
        "cut": {"waviness_mm": (1.0, 3.0), "skew_deg": 1.0},
        "hem": 1.0,
        "patterns": {"solid": 0.5, "end_bands": 0.5},
        "base_colors": _TOWEL_BASE,
        "accent_colors": _TOWEL_ACCENT,
    },
    "washcloth": {
        "category": "Bath",
        "label": "Washcloth",
        "formats": [{"width": 30, "length": 30, "shape": "rect", "weight": 1.0}],
        "tolerance": 0.02,
        "fabrics": {"cotton_terry": 1.0},
        "corner_radius": (0.0, 1.0),
        "cut": {"waviness_mm": (0.5, 2.0), "skew_deg": 1.5},
        "hem": 0.8,
        "patterns": {"solid": 0.7, "end_bands": 0.3},
        "base_colors": _TOWEL_BASE,
        "accent_colors": _TOWEL_ACCENT,
    },
    # --------------------------------------------------------------- Kitchen
    "tea_towel": {
        "category": "Kitchen",
        "label": "Tea towel",
        "formats": [
            {"width": 50, "length": 70, "shape": "rect", "weight": 0.7},
            {"width": 45, "length": 65, "shape": "rect", "weight": 0.3},
        ],
        "tolerance": 0.015,
        "fabrics": {"cotton_waffle": 0.4, "linen": 0.4, "cotton_plain": 0.2},
        "corner_radius": (0.0, 0.3),
        "cut": {"waviness_mm": (0.5, 2.5), "skew_deg": 1.0},
        "hem": 1.0,
        "patterns": {"solid": 0.2, "stripes": 0.35, "gingham": 0.25, "end_bands": 0.2},
        "base_colors": _KITCHEN_BASE,
        "accent_colors": _KITCHEN_ACCENT,
    },
    # ----------------------------------------------------------------- Table
    "napkin": {
        "category": "Table",
        "label": "Napkin",
        "formats": [
            {"width": 40, "length": 40, "shape": "rect", "weight": 0.6},
            {"width": 50, "length": 50, "shape": "rect", "weight": 0.4},
        ],
        "tolerance": 0.01,
        "fabrics": {"linen": 0.6, "cotton_plain": 0.4},
        "corner_radius": (0.0, 0.3),
        "cut": {"waviness_mm": (0.3, 1.5), "skew_deg": 0.8},
        "hem": 0.8,
        "patterns": {"solid": 0.6, "border": 0.4},
        "base_colors": ["#ffffff", "#f3eee2", "#d8cfc0", "#8e9aaf", "#a3b18a", "#c08497"],
        "accent_colors": _KITCHEN_ACCENT,
    },
    "tablecloth": {
        "category": "Table",
        "label": "Tablecloth",
        "formats": [
            {"width": 140, "length": 180, "shape": "rect", "weight": 0.35},
            {"width": 140, "length": 240, "shape": "rect", "weight": 0.25},
            {"width": 150, "length": 150, "shape": "ellipse", "weight": 0.25},
            {"width": 140, "length": 200, "shape": "ellipse", "weight": 0.15},
        ],
        "tolerance": 0.01,
        "fabrics": {"cotton_plain": 0.5, "linen": 0.5},
        "corner_radius": (0.0, 1.0),
        "cut": {"waviness_mm": (1.0, 4.0), "skew_deg": 0.5},
        "hem": 1.5,
        "patterns": {"solid": 0.5, "gingham": 0.3, "border": 0.2},
        "base_colors": ["#ffffff", "#f5f0e6", "#e7dcc8", "#c9d6df", "#dfe7d3"],
        "accent_colors": _KITCHEN_ACCENT,
    },
    # --------------------------------------------------------------- Bedding
    "bed_sheet": {
        "category": "Bedding",
        "label": "Flat bed sheet",
        "formats": [
            {"width": 180, "length": 290, "shape": "rect", "weight": 0.4},
            {"width": 240, "length": 300, "shape": "rect", "weight": 0.4},
            {"width": 270, "length": 310, "shape": "rect", "weight": 0.2},
        ],
        "tolerance": 0.015,
        "fabrics": {"cotton_percale": 0.7, "linen": 0.3},
        "corner_radius": (0.0, 0.5),
        "cut": {"waviness_mm": (2.0, 6.0), "skew_deg": 0.5},
        "hem": 2.0,
        "patterns": {"solid": 0.7, "stripes": 0.3},
        "base_colors": ["#ffffff", "#f4f1ea", "#dfe6ec", "#c9c1b6", "#9fb4c7", "#b9c9b2"],
        "accent_colors": ["#ffffff", "#9fb4c7", "#7d8a96", "#c9c1b6"],
    },
    # -------------------------------------------------------------- Cleaning
    "microfiber_cloth": {
        "category": "Cleaning",
        "label": "Microfiber cleaning cloth",
        "formats": [
            {"width": 40, "length": 40, "shape": "rect", "weight": 0.7},
            {"width": 30, "length": 30, "shape": "rect", "weight": 0.3},
        ],
        "tolerance": 0.015,
        "fabrics": {"microfiber": 1.0},
        "corner_radius": (0.5, 2.5),
        "cut": {"waviness_mm": (0.3, 1.5), "skew_deg": 1.0},
        "hem": 0.4,  # overlocked edge
        "patterns": {"solid": 1.0},
        "base_colors": ["#1e88e5", "#43a047", "#fdd835", "#e53935", "#8e24aa", "#fb8c00", "#9e9e9e"],
        "accent_colors": ["#ffffff"],
    },
    # ----------------------------------------------------------- Accessories
    "bandana": {
        "category": "Accessories",
        "label": "Bandana",
        "formats": [{"width": 55, "length": 55, "shape": "rect", "weight": 1.0}],
        "tolerance": 0.015,
        "fabrics": {"cotton_plain": 1.0},
        "corner_radius": (0.0, 0.3),
        "cut": {"waviness_mm": (0.5, 2.0), "skew_deg": 1.0},
        "hem": 0.5,
        "patterns": {"border": 0.6, "gingham": 0.2, "solid": 0.2},
        "base_colors": ["#b71c1c", "#0d47a1", "#212121", "#1b5e20", "#f9a825", "#4e342e"],
        "accent_colors": ["#ffffff", "#212121", "#f5f0e6"],
    },
    "silk_scarf": {
        "category": "Accessories",
        "label": "Silk scarf",
        "formats": [
            {"width": 90, "length": 90, "shape": "rect", "weight": 0.6},
            {"width": 50, "length": 160, "shape": "rect", "weight": 0.4},
        ],
        "tolerance": 0.01,
        "fabrics": {"silk": 1.0},
        "corner_radius": (0.0, 0.3),
        "cut": {"waviness_mm": (0.3, 1.0), "skew_deg": 0.5},
        "hem": 0.5,  # rolled hem
        "patterns": {"solid": 0.3, "border": 0.4, "stripes": 0.3},
        "base_colors": ["#7b1fa2", "#c2185b", "#00838f", "#f57f17", "#283593", "#efebe9"],
        "accent_colors": ["#fff8e1", "#212121", "#ffd54f", "#80cbc4"],
    },
    "scarf": {
        "category": "Accessories",
        "label": "Knitted winter scarf",
        "formats": [
            {"width": 25, "length": 160, "shape": "rect", "weight": 0.5},
            {"width": 30, "length": 180, "shape": "rect", "weight": 0.3},
            {"width": 20, "length": 140, "shape": "rect", "weight": 0.2},
        ],
        "tolerance": 0.03,  # knits are less regular than wovens
        "fabrics": {"wool_knit": 1.0},
        "corner_radius": (0.0, 0.5),
        "cut": {"waviness_mm": (1.0, 4.0), "skew_deg": 1.0},
        "hem": 0.5,  # knitted edge
        "patterns": {"cross_stripes": 0.5, "solid": 0.3, "gingham": 0.2},
        "base_colors": ["#7b1e1e", "#1f3a5f", "#3e4a3d", "#5d4037", "#9e9e9e", "#d7c4a3", "#212121"],
        "accent_colors": ["#f5f0e6", "#c62828", "#f9a825", "#1565c0", "#212121"],
    },
    # --------------------------------------------------------------- Outdoor
    "flag": {
        "category": "Outdoor",
        "label": "Flag (generic bands, hung by the hoist)",
        "formats": [
            {"width": 100, "length": 150, "shape": "rect", "weight": 0.6},
            {"width": 60, "length": 90, "shape": "rect", "weight": 0.4},
        ],
        "tolerance": 0.01,
        "fabrics": {"polyester_knit": 1.0},
        "corner_radius": (0.0, 0.0),
        "cut": {"waviness_mm": (0.3, 1.5), "skew_deg": 0.5},
        "hem": 1.5,
        "pins": "hoist",
        "patterns": {"bands": 1.0},
        "base_colors": ["#ffffff", "#c62828", "#1565c0", "#2e7d32", "#f9a825", "#212121", "#ef6c00"],
        "accent_colors": ["#ffffff", "#c62828", "#1565c0", "#2e7d32", "#f9a825", "#212121"],
    },
}
