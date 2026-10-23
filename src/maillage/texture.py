"""Printed and woven patterns, rendered as small PNG textures.

A texture covers the nominal piece (length along u, width along v). Patterns:

- solid: one colour;
- end_bands: one or two bands across the width near both ends (towel dobby
  border, tea towel);
- stripes: stripes running along the length, regular period;
- cross_stripes: stripes across the width, repeated along the length (knitted
  scarves);
- gingham: checks from two crossing stripe sets (the crossing is darker);
- border: a frame band inset from the edges (napkin, bandana, scarf);
- bands: two or three wide bands across or along the piece (generic flag:
  colours drawn at random, adjacent bands always differ, widths unequal and
  asymmetric so that real national flags are unlikely).

A faint per-pixel noise imitates the weave. Texture coordinates follow the
fabric, not the cut: a slightly skewed or wavy cut shows as a pattern that is
not perfectly parallel to the edge, as on real pieces.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np

PATTERNS = ("solid", "end_bands", "stripes", "cross_stripes", "gingham", "border", "bands")


def hex_to_rgb(color: str) -> np.ndarray:
    c = color.lstrip("#")
    return np.array([int(c[i : i + 2], 16) for i in (0, 2, 4)], float) / 255.0


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _pick_other(rng, pool, avoid):
    choices = [c for c in pool if c not in avoid] or list(pool)
    return choices[int(rng.integers(len(choices)))]


def _band_widths(rng: np.random.Generator, n: int) -> list[float]:
    """Unequal, asymmetric band widths (fractions summing to 1). National flags
    almost always use equal or symmetric bands, so random colours on such
    bands are unlikely to reproduce one."""
    while True:
        w = rng.dirichlet(np.full(n, 2.0))
        if w.min() < 0.12:
            continue
        if n == 2 and abs(w[0] - w[1]) >= 0.2:
            return [float(x) for x in w]
        if n == 3 and w.max() / w.min() >= 1.6 and abs(w[0] - w[2]) >= 0.12:
            return [float(x) for x in w]


def draw_pattern(rng: np.random.Generator, pattern: str, base_pool, accent_pool) -> dict:
    """Draw the parameters of a pattern (colours, periods, widths), in metres."""
    base = base_pool[int(rng.integers(len(base_pool)))]
    accent = _pick_other(rng, accent_pool, {base})
    spec = {"pattern": pattern, "base": base, "accent": accent}
    if pattern == "end_bands":
        spec.update(
            inset=float(rng.uniform(0.05, 0.12)),
            band=float(rng.uniform(0.02, 0.07)),
            double=bool(rng.random() < 0.4),
        )
    elif pattern == "cross_stripes":
        period = float(rng.uniform(0.06, 0.2))
        spec.update(period=period, stripe=float(rng.uniform(0.3, 0.5)) * period)
    elif pattern == "stripes":
        period = float(rng.uniform(0.02, 0.12))
        spec.update(period=period, stripe=float(rng.uniform(0.1, 0.4)) * period)
    elif pattern == "gingham":
        spec.update(period=float(rng.uniform(0.01, 0.04)))
    elif pattern == "border":
        spec.update(inset=float(rng.uniform(0.015, 0.06)), band=float(rng.uniform(0.005, 0.03)))
    elif pattern == "bands":
        n = 3 if rng.random() < 0.7 else 2
        colors = [base]
        for _ in range(n - 1):
            colors.append(_pick_other(rng, list(base_pool) + list(accent_pool), {colors[-1]}))
        spec.update(colors=colors, widths=_band_widths(rng, n), vertical=bool(rng.random() < 0.5))
    elif pattern != "solid":
        raise ValueError(f"unknown pattern {pattern!r}")
    return spec


def render(spec: dict, length: float, width: float, rng: np.random.Generator, max_px: int = 1024):
    """Texture image (H, W, 3) floats in [0, 1], sRGB, row 0 at the top."""
    ppm = max_px / max(length, width)
    nx, ny = max(32, round(length * ppm)), max(32, round(width * ppm))
    x = (np.arange(nx) + 0.5) / nx * length
    y = (np.arange(ny) + 0.5) / ny * width
    X, Y = np.meshgrid(x, y)  # (ny, nx), y increasing upwards
    base, accent = hex_to_rgb(spec["base"]), hex_to_rgb(spec["accent"])
    img = np.broadcast_to(base, (ny, nx, 3)).copy()
    p = spec["pattern"]
    if p == "end_bands":
        d = np.minimum(X, length - X)
        m = (d >= spec["inset"]) & (d < spec["inset"] + spec["band"])
        if spec["double"]:
            d2 = spec["inset"] + spec["band"] * 1.6
            m |= (d >= d2) & (d < d2 + 0.3 * spec["band"])
        img[m] = accent
    elif p == "stripes":
        m = np.mod(Y, spec["period"]) < spec["stripe"]
        img[m] = accent
    elif p == "cross_stripes":
        m = np.mod(X, spec["period"]) < spec["stripe"]
        img[m] = accent
    elif p == "gingham":
        per = spec["period"]
        a = np.mod(X, 2 * per) < per
        b = np.mod(Y, 2 * per) < per
        mix = 0.5 * base + 0.5 * accent
        img[a ^ b] = mix
        img[a & b] = accent
    elif p == "border":
        d = np.minimum.reduce([X, length - X, Y, width - Y])
        img[(d >= spec["inset"]) & (d < spec["inset"] + spec["band"])] = accent
    elif p == "bands":
        colors = [hex_to_rgb(c) for c in spec["colors"]]
        coord, extent = (X, length) if spec["vertical"] else (Y, width)
        edges = np.cumsum(spec["widths"])[:-1] * extent
        k = np.searchsorted(edges, coord, side="right")
        for i, c in enumerate(colors):
            img[k == i] = c
    weave = 1.0 + 0.035 * rng.standard_normal((ny, nx, 1))
    img = np.clip(img * weave, 0.0, 1.0)
    return img[::-1]  # row 0 at the top, as image files store it


def mean_color(img: np.ndarray) -> np.ndarray:
    return img.reshape(-1, 3).mean(axis=0)


def write_png(path: str | Path, img: np.ndarray) -> Path:
    """Minimal 8-bit RGB PNG writer (no external dependency)."""
    path = Path(path)
    data = (np.clip(img, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    h, w, _ = data.shape
    raw = b"".join(b"\x00" + data[r].tobytes() for r in range(h))

    def chunk(tag, payload):
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)
    return path
