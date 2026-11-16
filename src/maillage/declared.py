"""What every cloth piece draws, declared once: the tables of docs/variation.md are written from
this module and from the presets (presets.PRESETS), and tests/test_distributions.py checks that the
generator follows them.

Each row is (column, aspect, how it is drawn), applied to its preset's own numbers. The pattern's
own sizes depend on the pattern drawn: PATTERNS lists them, each a uniform range in metres
(``times`` gives a stripe as a share of its period) or a probability for a yes/no.
"""

from __future__ import annotations

from .presets import PRESETS

CLIP = 2.5  # the size's normal draws are kept within ±2.5 standard deviations

DECLARED = [
    ("format_shape", "size", "the shape of a format drawn from the preset's `formats`, with their weights"),
    ("format_length_m", "size", "the length of that format"),
    ("format_width_m", "size", "the width of that format"),
    ("length_m", "size", f"format length × (1 + `tolerance` × e), e normal, kept within ±{CLIP:g}"),
    ("width_m", "size", f"format width × (1 + `tolerance` × e), another e, kept within ±{CLIP:g}"),
    (
        "corner_radius_m",
        "corners",
        "uniform within the preset's `corner_radius` (cm); 0 for an ellipse or the grid topology",
    ),
    (
        "cut_amplitudes_m",
        "cut",
        "three waves: a uniform amplitude within `cut.waviness_mm`, shared by Dirichlet(2, 2, 2) weights, "
        "the third wave at 0.3 times its share",
    ),
    ("cut_cycles", "cut", "whole numbers of waves along the outline: 2 to 5, 5 to 11, 18 to 39"),
    ("cut_skew_deg", "cut", "uniform within ± `cut.skew_deg`"),
    ("fabric", "fabric", "one of the preset's `fabrics`, with their weights"),
    ("pattern", "color", "one of the preset's `patterns`, with their weights"),
    (
        "colors",
        "color",
        "a base from `base_colors`, each as likely; then an accent from `accent_colors` that is not the base "
        "(not for `solid`, which has one colour); `bands`: 2 or 3 colours (3 at 70 %)",
    ),
]

# the pattern's own drawn values: column (pattern_<name>_m or pattern_<name>) -> rule
PATTERNS = {
    "solid": {},
    "end_bands": {"inset": ("uniform", 0.05, 0.12), "band": ("uniform", 0.02, 0.07), "double": ("yes", 0.4)},
    "cross_stripes": {"period": ("uniform", 0.06, 0.2), "stripe": ("times", "period", 0.3, 0.5)},
    "stripes": {"period": ("uniform", 0.02, 0.12), "stripe": ("times", "period", 0.1, 0.4)},
    "gingham": {"period": ("uniform", 0.01, 0.04)},
    "border": {"inset": ("uniform", 0.015, 0.06), "band": ("uniform", 0.005, 0.03)},
    "bands": {"vertical": ("yes", 0.5)},
}


def pattern_column(name: str, rule) -> str:
    return f"pattern_{name}" if rule[0] == "yes" else f"pattern_{name}_m"


def _rule(rule) -> str:
    kind, *args = rule
    if kind == "uniform":
        return f"uniform, {args[0]:g} to {args[1]:g} m"
    if kind == "times":
        return f"the {args[0]} × uniform {args[1]:g} to {args[2]:g}"
    return f"yes at {args[0]:.0%}".replace("%", " %")


def _weights(d: dict) -> str:
    total = sum(d.values())
    return ", ".join(f"{k} {100 * v / total:g} %" for k, v in d.items())


def table() -> str:
    """The Markdown of docs/variation.md between its markers."""
    out = ["### Rules", "", "| Column | Aspect | Drawn as |", "|---|---|---|"]
    out += [f"| `variation:{c}` | {a} | {how} |" for c, a, how in DECLARED]
    out += ["", "### The pattern's own values", "", "| Pattern | Column | Drawn as |", "|---|---|---|"]
    for pattern, params in PATTERNS.items():
        if not params:
            out.append(f"| `{pattern}` | (none) | |")
        for name, rule in params.items():
            out.append(f"| `{pattern}` | `variation:{pattern_column(name, rule)}` | {_rule(rule)} |")
    out += [
        "",
        "### The presets' numbers",
        "",
        "| Preset | `formats` (cm, weight) | `tolerance` | `corner_radius` (cm) | `cut.waviness_mm` "
        "| `cut.skew_deg` | `fabrics` | `patterns` | colours (base, accent) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for key, p in PRESETS.items():
        formats = ", ".join(
            f"{f['shape']} {f['length']:g} × {f['width']:g} ({f['weight']:g})" for f in p["formats"]
        )
        lo, hi = p["corner_radius"]
        w_lo, w_hi = p["cut"]["waviness_mm"]
        out.append(
            f"| `{key}` | {formats} | {p['tolerance']:g} | {lo:g} to {hi:g} | {w_lo:g} to {w_hi:g} "
            f"| ±{p['cut']['skew_deg']:g} | {_weights(p['fabrics'])} | {_weights(p['patterns'])} "
            f"| {len(p['base_colors'])}, {len(p['accent_colors'])} |"
        )
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    print(table())
