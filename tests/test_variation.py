"""What was drawn for each piece is written into the file (primvaria:variation:*)."""

import pytest
from pxr import Usd

from maillage import Variations, generate_scene, write_outputs
from maillage.contract import asset_roots, variation


def _drawn(tmp_path, **variations):
    scene = generate_scene("tea_towel", count=4, seed=2, vertices=300, variations=Variations(**variations))
    folder = write_outputs(scene, tmp_path)
    stage = Usd.Stage.Open(str(folder / "maillage_tea_towel.usdc"))
    return scene, {prim.GetName(): variation(prim) for prim in asset_roots(stage)}


def test_every_piece_carries_its_draws(tmp_path):
    scene, drawn = _drawn(tmp_path)
    assert len(drawn) == len(scene.pieces)
    for p in scene.pieces:
        d = drawn[p.name]
        assert d["aspects"] == ["size", "cut", "corners", "fabric", "color"]
        assert (d["length_m"], d["width_m"]) == pytest.approx((p.length, p.width))
        assert (d["format_length_m"], d["format_width_m"]) == pytest.approx(p.nominal)
        assert d["corner_radius_m"] == pytest.approx(p.corner_radius)
        assert d["fabric"] == p.fabric and d["pattern"] == p.pattern["pattern"]
        assert len(d["cut_amplitudes_m"]) == 3 and d["colors"]


def test_an_aspect_switched_off_is_recorded_at_its_nominal_value(tmp_path):
    _, on = _drawn(tmp_path / "on")
    _, off = _drawn(tmp_path / "off", cut=False)
    for name, d in off.items():
        assert "cut" not in d["aspects"]
        assert d["cut_amplitudes_m"] == [] and d["cut_skew_deg"] == 0.0
        # the other aspects keep their draws
        for key in ("length_m", "width_m", "corner_radius_m", "fabric", "pattern", "colors"):
            assert d[key] == on[name][key]
