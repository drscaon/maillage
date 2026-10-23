"""Piece outlines: the cut shape of a textile piece in its own plane.

An outline is a closed, counter-clockwise curve made of segments (straight
lines, circular arcs, a full ellipse), parametrised by arc length. The cut of a
real piece is never perfect, so an outline can carry a *cut* deformation:

- waviness: a smooth displacement along the outward normal, the sum of a few
  sines of the arc length (long, gentle deviations plus a small wobble);
- skew: a small shear of the whole piece (corners not exactly at 90 degrees).

Coordinates are in metres; the length of the piece runs along x, the width
along y, centred on the origin.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


class _Line:
    def __init__(self, p0, p1):
        self.p0 = np.asarray(p0, float)
        self.p1 = np.asarray(p1, float)
        d = self.p1 - self.p0
        self.length = float(np.hypot(*d))
        self._n = np.array([d[1], -d[0]]) / self.length  # outward for a CCW outline

    def point(self, u):
        u = np.atleast_1d(u)[:, None]
        return self.p0 + u * (self.p1 - self.p0)

    def normal(self, u):
        return np.repeat(self._n[None, :], len(np.atleast_1d(u)), axis=0)


class _Arc:
    def __init__(self, center, radius, a0, a1):
        self.c = np.asarray(center, float)
        self.r = float(radius)
        self.a0, self.a1 = a0, a1
        self.length = self.r * (a1 - a0)

    def _angle(self, u):
        return self.a0 + np.atleast_1d(u) * (self.a1 - self.a0)

    def point(self, u):
        a = self._angle(u)
        return self.c + self.r * np.stack([np.cos(a), np.sin(a)], axis=1)

    def normal(self, u):
        a = self._angle(u)
        return np.stack([np.cos(a), np.sin(a)], axis=1)


class _Ellipse:
    """Full ellipse, parametrised by arc length through a lookup table."""

    def __init__(self, a, b, samples=4096):
        self.a, self.b = float(a), float(b)
        th = np.linspace(0.0, 2.0 * math.pi, samples + 1)
        p = np.stack([self.a * np.cos(th), self.b * np.sin(th)], axis=1)
        s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])
        self.length = float(s[-1])
        self._th, self._s = th, s / s[-1]

    def _theta(self, u):
        return np.interp(np.atleast_1d(u), self._s, self._th)

    def point(self, u):
        th = self._theta(u)
        return np.stack([self.a * np.cos(th), self.b * np.sin(th)], axis=1)

    def normal(self, u):
        th = self._theta(u)
        n = np.stack([self.b * np.cos(th), self.a * np.sin(th)], axis=1)
        return n / np.linalg.norm(n, axis=1, keepdims=True)


@dataclass
class Cut:
    """Imperfections of the cut: normal waviness (sum of sines) and skew."""

    amplitudes: tuple = ()  # metres
    cycles: tuple = ()  # number of periods along the whole perimeter
    phases: tuple = ()
    skew: float = 0.0  # radians

    @classmethod
    def random(cls, rng: np.random.Generator, waviness_mm: float, skew_max_deg: float) -> Cut:
        if waviness_mm <= 0 and skew_max_deg <= 0:
            return cls()
        amp = waviness_mm * 1e-3
        weights = rng.dirichlet([2.0, 2.0, 2.0])
        cycles = [int(rng.integers(2, 6)), int(rng.integers(5, 12)), int(rng.integers(18, 40))]
        amplitudes = [amp * weights[0], amp * weights[1], 0.3 * amp * weights[2]]
        phases = rng.uniform(0.0, 2.0 * math.pi, 3)
        skew = math.radians(rng.uniform(-skew_max_deg, skew_max_deg))
        return cls(tuple(amplitudes), tuple(cycles), tuple(phases), skew)

    def displacement(self, t: np.ndarray, perimeter: float) -> np.ndarray:
        d = np.zeros_like(t, dtype=float)
        for a, k, ph in zip(self.amplitudes, self.cycles, self.phases, strict=True):
            d += a * np.sin(2.0 * math.pi * k * t / perimeter + ph)
        return d

    def shear(self, p: np.ndarray) -> np.ndarray:
        out = p.copy()
        out[:, 0] += math.tan(self.skew) * p[:, 1]
        return out


@dataclass
class Outline:
    shape: str  # "rect" or "ellipse"
    length: float  # along x, metres
    width: float  # along y, metres
    corner_radius: float = 0.0
    cut: Cut = field(default_factory=Cut)

    def __post_init__(self):
        if self.shape == "ellipse":
            self.segments = [_Ellipse(self.length / 2, self.width / 2)]
            return
        if self.shape != "rect":
            raise ValueError(f"unknown outline shape {self.shape!r}")
        hl, hw = self.length / 2, self.width / 2
        r = min(self.corner_radius, 0.45 * min(self.length, self.width))
        self.corner_radius = r
        hp = math.pi / 2
        segs = [_Line((-hl + r, -hw), (hl - r, -hw))]
        if r > 0:
            segs.append(_Arc((hl - r, -hw + r), r, -hp, 0.0))
        segs.append(_Line((hl, -hw + r), (hl, hw - r)))
        if r > 0:
            segs.append(_Arc((hl - r, hw - r), r, 0.0, hp))
        segs.append(_Line((hl - r, hw), (-hl + r, hw)))
        if r > 0:
            segs.append(_Arc((-hl + r, hw - r), r, hp, 2 * hp))
        segs.append(_Line((-hl, hw - r), (-hl, -hw + r)))
        if r > 0:
            segs.append(_Arc((-hl + r, -hw + r), r, 2 * hp, 3 * hp))
        self.segments = segs

    @property
    def perimeter(self) -> float:
        return float(sum(s.length for s in self.segments))

    @property
    def nominal_area(self) -> float:
        if self.shape == "ellipse":
            return math.pi * self.length * self.width / 4
        return self.length * self.width - (4 - math.pi) * self.corner_radius**2

    def _deform(self, p, n, t):
        p = p + self.cut.displacement(t, self.perimeter)[:, None] * n
        return self.cut.shear(p)

    def sample(self, spacing: float) -> np.ndarray:
        """Points along the cut outline, about `spacing` apart.
        Returns an (M, 2) counter-clockwise polygon (last point != first).

        Sharp corners are always vertices. A rounded corner longer than the
        spacing is followed point by point; a shorter one (a rounding below
        the mesh resolution) becomes a single vertex at its middle, so no
        sliver triangles appear next to it."""
        P = self.perimeter
        features, t0 = [], 0.0
        for s in self.segments:
            if isinstance(s, _Arc):
                if s.length >= spacing:
                    features += [t0, t0 + s.length]
                else:
                    features.append(t0 + s.length / 2)
            elif self.corner_radius == 0 and self.shape == "rect":
                features.append(t0)
            t0 += s.length
        if not features:
            n = max(8, round(P / spacing))
            return self.at(np.arange(n) * P / n)
        features = sorted(set(round(f, 12) for f in features))
        ts = []
        for i, a in enumerate(features):
            b = features[(i + 1) % len(features)] + (P if i == len(features) - 1 else 0.0)
            n = max(1, round((b - a) / spacing))
            ts.append(a + (b - a) * np.arange(n) / n)
        return self.at(np.concatenate(ts))

    def at(self, t: np.ndarray) -> np.ndarray:
        """Cut outline evaluated at arc lengths t (0 <= t < perimeter)."""
        t = np.mod(np.atleast_1d(np.asarray(t, float)), self.perimeter)
        pts = np.zeros((len(t), 2))
        nrm = np.zeros((len(t), 2))
        start = 0.0
        for s in self.segments:
            m = (t >= start) & (t < start + s.length)
            if np.any(m):
                u = (t[m] - start) / s.length
                pts[m] = s.point(u)
                nrm[m] = s.normal(u)
            start += s.length
        return self._deform(pts, nrm, t)
