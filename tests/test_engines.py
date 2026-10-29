"""Engine exports read back from the OpenUSD file: MuJoCo flex model and OmniPhysics layer."""

import importlib.util

import pytest
from pxr import Usd

from maillage import generate_scene, write_outputs
from maillage.fabrics import FABRICS, shell
from maillage.omniphysics import check
from maillage.validate import validate

HAS_MUJOCO = importlib.util.find_spec("mujoco") is not None


@pytest.fixture(scope="module")
def towels(tmp_path_factory):
    return write_outputs(generate_scene("tea_towel", count=2, vertices=300), tmp_path_factory.mktemp("t"))


@pytest.fixture(scope="module")
def grid(tmp_path_factory):
    scene = generate_scene("bath_towel", count=1, topology="grid", vertices=300)
    return write_outputs(scene, tmp_path_factory.mktemp("g"))


@pytest.mark.parametrize("name", sorted(FABRICS))
def test_shell_gives_the_fabric_stiffness(name):
    f = FABRICS[name]
    E, t = shell(f)
    nu = f["poissons_ratio"]
    assert E * t == pytest.approx(f["tensile_stiffness"])
    assert E * t**3 / (12 * (1 - nu * nu)) == pytest.approx(f["bending_rigidity"])


def test_engine_neutral_attributes(towels):
    stage = Usd.Stage.Open(str(towels / "maillage_tea_towel.usdc"))
    prim = stage.GetPrimAtPath("/World/Cloths/tea_towel_000")
    fab = FABRICS[prim.GetAttribute("maillage:fabric").Get()]
    assert prim.GetAttribute("maillage:tensileStiffness").Get() == pytest.approx(fab["tensile_stiffness"])
    assert prim.GetAttribute("maillage:bendingRigidity").Get() == pytest.approx(fab["bending_rigidity"])


@pytest.mark.parametrize("fixture", ["towels", "grid"])
def test_omniphysics_layer(fixture, request):
    folder = request.getfixturevalue(fixture)
    layer = next(folder.glob("*_omniphysics.usda"))
    assert check(layer) == []
    assert validate(layer) == []
    # the main file stays engine-neutral (quads kept in the grid topology)
    assert "omniphysics" not in (
        folder / f"{layer.stem.removesuffix('_omniphysics')}.usdc"
    ).read_bytes().decode("latin-1")


@pytest.mark.skipif(not HAS_MUJOCO, reason="MuJoCo not installed")
@pytest.mark.parametrize("fixture", ["towels", "grid"])
def test_mujoco_model_loads(fixture, request):
    import mujoco

    folder = request.getfixturevalue(fixture)
    model = mujoco.MjModel.from_xml_path(str(next(folder.glob("maillage_*.xml"))))
    assert model.nflex >= 1


@pytest.mark.skipif(not HAS_MUJOCO, reason="MuJoCo not installed")
def test_mujoco_drape(towels):
    from maillage.sim import mujoco_test

    report = mujoco_test.run(towels, pieces=1, seconds=3.0)
    piece = report["pieces"][0]
    assert piece["checks"]["finite"] and piece["checks"]["mass"] and piece["checks"]["stretch"]
    assert piece["checks"]["penetration"] and piece["checks"]["solver"]
    assert 0 < piece["drape_coefficient"] < 1
