import math

import numpy as np
import pytest

from maillage.outline import Cut, Outline


def test_rect_perimeter_and_corners():
    o = Outline("rect", 0.7, 0.5)
    assert o.perimeter == pytest.approx(2.4)
    pts = o.sample(0.05)
    for corner in [(-0.35, -0.25), (0.35, -0.25), (0.35, 0.25), (-0.35, 0.25)]:
        assert np.min(np.linalg.norm(pts - corner, axis=1)) < 1e-12


def test_rounded_rect_area():
    r = 0.02
    o = Outline("rect", 0.7, 0.5, r)
    assert o.nominal_area == pytest.approx(0.35 - (4 - math.pi) * r * r)
    assert o.perimeter == pytest.approx(2 * (0.7 + 0.5) - 8 * r + 2 * math.pi * r)


def test_ellipse_perimeter():
    a, b = 1.0, 0.7
    o = Outline("ellipse", 2 * a, 2 * b)
    h = ((a - b) / (a + b)) ** 2
    ramanujan = math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))
    assert o.perimeter == pytest.approx(ramanujan, rel=1e-4)


def test_sampled_outline_is_counter_clockwise():
    for o in (Outline("rect", 1.0, 0.6, 0.03), Outline("ellipse", 1.5, 1.5)):
        p = o.sample(0.03)
        area = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - p[:, 1] * np.roll(p[:, 0], -1))
        assert area > 0


def test_small_corner_radius_gives_one_vertex():
    # a rounding below the mesh spacing must not create close vertices
    p = Outline("rect", 1.0, 0.6, 0.005).sample(0.05)
    gaps = np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1)
    assert gaps.min() > 0.02


def test_cut_waviness_is_bounded():
    rng = np.random.default_rng(3)
    cut = Cut.random(rng, waviness_mm=4.0, skew_max_deg=0.0)
    o = Outline("rect", 1.0, 0.6, 0.0, cut)
    d = cut.displacement(np.linspace(0, o.perimeter, 5000), o.perimeter)
    assert np.abs(d).max() <= 4e-3 + 1e-12
    assert np.abs(d).max() > 0.5e-3


def test_skew_shears_the_piece():
    cut = Cut(skew=math.radians(1.0))
    p = Outline("rect", 1.0, 0.6, 0.0, cut).sample(0.1)
    top_left = p[np.argmax(p[:, 1] - p[:, 0])]
    assert top_left[0] == pytest.approx(-0.5 + math.tan(math.radians(1.0)) * 0.3)


def test_unknown_shape():
    with pytest.raises(ValueError):
        Outline("triangle", 1.0, 1.0)
