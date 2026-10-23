import numpy as np
import pytest

from maillage import FABRICS, PRESETS, Variations, generate_scene
from maillage.texture import PATTERNS


def test_presets_are_consistent():
    for key, p in PRESETS.items():
        assert set(p["fabrics"]) <= set(FABRICS), key
        assert set(p["patterns"]) <= set(PATTERNS), key
        assert all(f["shape"] in ("rect", "ellipse") for f in p["formats"]), key
        lo, hi = p["corner_radius"]
        assert 0 <= lo <= hi, key


def test_same_seed_same_scene():
    a = generate_scene("napkin", count=3, seed=7, vertices=300)
    b = generate_scene("napkin", count=3, seed=7, vertices=300)
    c = generate_scene("napkin", count=3, seed=8, vertices=300)
    assert np.array_equal(a.pieces[0].mesh.points, b.pieces[0].mesh.points)
    assert not np.array_equal(a.pieces[0].mesh.points, c.pieces[0].mesh.points)


def test_turning_a_variation_off_keeps_the_others():
    on = generate_scene("tea_towel", count=4, seed=2, vertices=300)
    off = generate_scene("tea_towel", count=4, seed=2, vertices=300, variations=Variations(color=False))
    for a, b in zip(on.pieces, off.pieces, strict=True):
        assert np.array_equal(a.mesh.points, b.mesh.points)
        assert a.fabric == b.fabric
    assert len({p.pattern["pattern"] for p in off.pieces}) == 1


def test_no_size_no_cut_gives_the_nominal_piece():
    var = Variations(size=False, cut=False, corners=False)
    s = generate_scene("bath_towel", count=2, variations=var, vertices=400)
    for p in s.pieces:
        assert (p.length, p.width) == pytest.approx((1.40, 0.70))
        assert p.metrics["area_m2"] == pytest.approx(1.40 * 0.70, rel=0.002)


def test_mass_from_areal_density():
    s = generate_scene("bath_towel", count=2, vertices=300)
    for p in s.pieces:
        assert p.mass == pytest.approx(FABRICS[p.fabric]["areal_density"] * p.metrics["area_m2"])
        assert 0.3 < p.mass < 0.8  # a 70×140 to 90×150 cm towel at 450 g/m²


def test_hem_is_along_the_edges():
    p = generate_scene("tablecloth", count=1, vertices=800).pieces[0]
    pts = p.mesh.points
    assert p.hem[p.mesh.boundary].min() == 1.0
    center = np.argmin(np.linalg.norm(pts[:, :2], axis=1))
    assert p.hem[center] == 0.0


def test_flag_pins_the_hoist_corners_only():
    for p in generate_scene("flag", count=3, vertices=500).pieces:
        pinned = p.mesh.points[p.pin > 0]
        assert 2 <= len(pinned) <= 40
        assert np.all(pinned[:, 0] < -p.length / 2 + 0.12)  # within ~one edge of the hoist
    assert all(p.pin.max() == 0 for p in generate_scene("napkin", count=2, vertices=200).pieces)


def test_grid_topology_skips_round_formats():
    s = generate_scene("tablecloth", count=12, topology="grid", vertices=300)
    assert {p.shape for p in s.pieces} == {"rect"}
    assert all(p.corner_radius == 0 for p in s.pieces)


def test_uv_cover_the_piece():
    p = generate_scene("napkin", count=1, vertices=300).pieces[0]
    assert p.uv.min() > -0.05 and p.uv.max() < 1.05


def test_pieces_do_not_overlap_when_laid_out():
    s = generate_scene("hand_towel", count=5, vertices=200)
    boxes = []
    for p in s.pieces:
        x, y, _ = p.position
        xy = p.mesh.points[:, :2] + (x, y)
        boxes.append((xy.min(axis=0), xy.max(axis=0)))
    for i, (lo1, hi1) in enumerate(boxes):
        for lo2, hi2 in boxes[i + 1 :]:
            assert np.any(hi1 < lo2) or np.any(hi2 < lo1)


@pytest.mark.parametrize("kwargs", [{"count": 0}, {"vertices": 5}, {"topology": "hex"}, {"preset": "sock"}])
def test_invalid_arguments(kwargs):
    with pytest.raises(ValueError):
        generate_scene(**kwargs)


def test_fabric_list_is_used_in_turn():
    s = generate_scene("napkin", count=5, vertices=150, fabric=["silk", "denim"])
    assert [p.fabric for p in s.pieces] == ["silk", "denim", "silk", "denim", "silk"]
    with pytest.raises(ValueError):
        generate_scene("napkin", count=1, fabric=["velvet"])
