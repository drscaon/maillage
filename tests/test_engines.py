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


def test_fabrics_do_not_drape_alike(tmp_path):
    pytest.importorskip("mujoco")
    from maillage.sim.mujoco_test import ANCHOR_GAP, ANCHORS, bending_length, fabric_drape, fabric_lines

    report = fabric_drape(ANCHORS, tmp_path, vertices=200, seconds=3.0)
    assert report["passed"], fabric_lines(report)
    drape = [r["drape_coefficient"] for r in report["fabrics"]]
    assert drape[0] + ANCHOR_GAP <= drape[1] <= drape[2] - ANCHOR_GAP  # silk, plain cotton, denim
    lengths = [bending_length(FABRICS[name]) for name in ANCHORS]
    assert lengths == sorted(lengths) and 0.01 < lengths[0] < lengths[2] < 0.04
    assert "spread" not in report["checks"]  # only when every fabric is tested
    assert (tmp_path / "fabric_test.json").exists()


def test_fabric_test_refuses_an_unknown_fabric(tmp_path):
    from maillage.sim.mujoco_test import fabric_drape

    with pytest.raises(ValueError, match="unknown fabric"):
        fabric_drape(["velvet"], tmp_path)


@pytest.mark.parametrize("fixture", ["towels", "grid"])
def test_newton_layer(fixture, request):
    from maillage import contract, newton

    folder = request.getfixturevalue(fixture)
    (layer,) = folder.glob("*_newton.usda")
    assert newton.check(layer) == []
    assert validate(layer) == []
    assert contract.check(layer) == []
    main = folder / f"{layer.stem.removesuffix('_newton')}.usdc"
    text = main.read_bytes().decode("latin-1")
    assert "SurfaceDeformable" not in text and "youngsModulus" not in text  # the file stays neutral
    stage = Usd.Stage.Open(str(layer))
    for prim in stage.GetPrimAtPath("/World/Cloths").GetChildren():
        if prim.GetTypeName() != "Mesh":
            continue
        E, t = shell(FABRICS[prim.GetAttribute("maillage:fabric").Get()])
        assert list(prim.GetAttribute("physics:thicknesses").Get()) == [pytest.approx(t)]
        assert prim.GetAttribute("physics:mass").Get() == pytest.approx(
            prim.GetAttribute("maillage:mass").Get()
        )
        from pxr import UsdShade

        mat, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial("physics")
        assert mat.GetPrim().GetAttribute("physics:youngsModulus").Get() == pytest.approx(E, rel=1e-6)


@pytest.mark.parametrize(
    ("engines", "omni", "newton_"), [("none", 0, 0), ("omniphysics", 1, 0), ("newton", 0, 1)]
)
def test_engines_chooses_the_layers(tmp_path, engines, omni, newton_):
    from maillage.cli import main

    assert (
        main(["generate", "--preset", "napkin", "--count", "1", "--out", str(tmp_path), "--engines", engines])
        == 0
    )
    assert len(list(tmp_path.rglob("*_omniphysics.usda"))) == omni
    assert len(list(tmp_path.rglob("*_newton.usda"))) == newton_
