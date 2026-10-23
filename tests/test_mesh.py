import numpy as np
import pytest

from maillage import mesh
from maillage.outline import Cut, Outline


@pytest.fixture
def rng():
    return np.random.default_rng(0)


@pytest.mark.parametrize("shape,radius", [("rect", 0.0), ("rect", 0.02), ("ellipse", 0.0)])
def test_triangle_mesh_quality(shape, radius, rng):
    o = Outline(shape, 0.9, 0.6, radius, Cut.random(rng, 2.0, 1.0))
    m = mesh.build(o, "tri", 1200, rng)
    met = mesh.metrics(m)
    assert met["area_m2"] == pytest.approx(o.nominal_area, rel=0.02)
    assert 0.8 * 1200 < met["vertices"] < 1.25 * 1200
    assert met["min_angle_deg"] > 15
    assert met["min_angle_p05_deg"] > 35
    assert set(m.face_counts) == {3}
    assert np.all(m.points[:, 2] == 0)


def test_faces_point_up(rng):
    m = mesh.build(Outline("ellipse", 1.0, 0.8), "tri", 500, rng)
    p = m.points[m.faces]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    assert np.all(n[:, 2] > 0)


def test_every_vertex_is_used(rng):
    m = mesh.build(Outline("rect", 0.5, 0.5, 0.01), "tri", 400, rng)
    assert len(np.unique(m.face_indices)) == len(m.points)
    assert m.boundary.max() < len(m.points)


def test_quad_grid(rng):
    o = Outline("rect", 1.4, 0.7, 0.0, Cut.random(rng, 3.0, 1.0))
    m = mesh.build(o, "grid", 1000, rng)
    met = mesh.metrics(m)
    assert set(m.face_counts) == {4}
    assert met["area_m2"] == pytest.approx(0.98, rel=0.02)
    assert met["min_angle_deg"] > 80
    # boundary: every grid vertex on the outer ring, once
    nu_nv = len(m.points)
    assert len(np.unique(m.boundary)) == len(m.boundary) < nu_nv


def test_grid_needs_a_sharp_rectangle(rng):
    with pytest.raises(ValueError):
        mesh.build(Outline("ellipse", 1.0, 1.0), "grid", 100, rng)
    with pytest.raises(ValueError):
        mesh.build(Outline("rect", 1.0, 1.0, 0.02), "grid", 100, rng)


def test_unknown_topology(rng):
    with pytest.raises(ValueError):
        mesh.build(Outline("rect", 1.0, 1.0), "hex", 100, rng)


def test_distance_to_polygon():
    square = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
    d = mesh.distance_to_polygon(square, np.array([[0.5, 0.5], [0.5, 0.1], [2.0, 0.5]]))
    assert d == pytest.approx([0.5, 0.1, 1.0])
