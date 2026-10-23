"""Piece formats: the nominal sizes and shapes a preset draws from.

A preset lists its own formats (presets.py); `generate_scene(formats=...)` and
`maillage generate --format ...` replace them. A format is a dict

    {"width": cm, "length": cm, "shape": "rect" | "ellipse", "weight": w}

where width is the shorter side, or one of these shorthands (sizes in cm):

    "50x70"          rectangle 50 × 70 cm (also "rect:50x70", "50×70")
    "oval:140x200"   ellipse 140 × 200 cm (also "ellipse:140x200")
    "round:150"      circle, 150 cm in diameter
    "50x70@3"        any of the above with a relative weight (default 1)

A tuple (width, length) or (width, length, shape) works too. Sizes given
longest first are swapped, so width is always the shorter side.
"""

from __future__ import annotations

import re

SHAPES = ("rect", "ellipse")
_ALIASES = {"rect": "rect", "rectangle": "rect", "oval": "ellipse", "ellipse": "ellipse", "round": "ellipse"}
_SIZE = r"(\d+(?:\.\d+)?)"


def parse_format(spec) -> dict:
    """One format from a dict, a tuple or a shorthand string (see module doc)."""
    if isinstance(spec, dict):
        fmt = {"shape": "rect", "weight": 1.0, **spec}
        fmt["shape"] = _ALIASES.get(fmt["shape"], fmt["shape"])
    elif isinstance(spec, (tuple, list)):
        if len(spec) not in (2, 3):
            raise ValueError(f"format {spec!r}: expected (width, length) or (width, length, shape)")
        shape = _ALIASES.get(spec[2], spec[2]) if len(spec) == 3 else "rect"
        fmt = {"width": spec[0], "length": spec[1], "shape": shape, "weight": 1.0}
    elif isinstance(spec, str):
        fmt = _parse_text(spec)
    else:
        raise ValueError(f"format {spec!r}: expected a dict, a tuple or a string such as '50x70'")
    try:
        w, ln, weight = float(fmt["width"]), float(fmt["length"]), float(fmt["weight"])
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError(f"format {spec!r}: width, length and weight must be numbers") from e
    if fmt["shape"] not in SHAPES:
        raise ValueError(f"format {spec!r}: shape must be one of {SHAPES} (or oval, round)")
    if min(w, ln) <= 0 or weight <= 0:
        raise ValueError(f"format {spec!r}: sizes and weight must be positive")
    w, ln = min(w, ln), max(w, ln)
    return {"width": w, "length": ln, "shape": fmt["shape"], "weight": weight}


def _parse_text(text: str) -> dict:
    t = text.strip().lower().replace("×", "x").replace(" ", "")
    weight = 1.0
    if "@" in t:
        t, _, wt = t.partition("@")
        try:
            weight = float(wt)
        except ValueError as e:
            raise ValueError(f"format {text!r}: weight after '@' must be a number") from e
    shape = "rect"
    if ":" in t:
        name, _, t = t.partition(":")
        if name not in _ALIASES:
            raise ValueError(f"format {text!r}: unknown shape {name!r} (rect, oval, ellipse, round)")
        shape = _ALIASES[name]
        if name == "round":
            m = re.fullmatch(_SIZE, t)
            if not m:
                raise ValueError(f"format {text!r}: expected round:DIAMETER, e.g. round:150")
            return {"width": m[1], "length": m[1], "shape": "ellipse", "weight": weight}
    m = re.fullmatch(_SIZE + "x" + _SIZE, t)
    if not m:
        raise ValueError(f"format {text!r}: expected WIDTHxLENGTH in cm, e.g. 50x70, oval:140x200, round:150")
    return {"width": m[1], "length": m[2], "shape": shape, "weight": weight}


def parse_formats(specs) -> list[dict]:
    """A list of formats; a comma-separated string is split first."""
    if isinstance(specs, str):
        specs = [s for s in specs.split(",") if s.strip()]
    formats = [parse_format(s) for s in specs]
    if not formats:
        raise ValueError("at least one format is needed")
    return formats


def describe(fmt: dict) -> str:
    """Short text for a format: 50×70, ⌀150, oval 140×200."""
    w, ln = (f"{round(v, 1):g}" for v in (fmt["width"], fmt["length"]))
    if fmt["shape"] == "rect":
        return f"{w}×{ln}"
    return f"⌀{w}" if w == ln else f"oval {w}×{ln}"
