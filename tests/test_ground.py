"""The ground and physics scene shared by every Primvaria project (maillage/ground.py)."""

import pytest
from pxr import Usd

from maillage.generator import generate_scene, write_outputs
from maillage.ground import conformance, read_ground


def test_ground_and_physics_scene_follow_the_shared_convention(tmp_path):
    folder = write_outputs(generate_scene("tea_towel", count=2, vertices=200), tmp_path)
    files = sorted(f for f in folder.rglob("*") if f.suffix in (".usd", ".usda", ".usdc"))
    assert files
    for f in files:
        stage = Usd.Stage.Open(str(f))
        assert conformance(stage) == [], f  # the main file and its OmniPhysics layer
        g = read_ground(stage)
        assert g["top"] == pytest.approx(0.0, abs=1e-9)
        assert g["dynamic_friction"] == pytest.approx(0.5)
