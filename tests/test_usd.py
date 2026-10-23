import json

import pytest
from pxr import Usd, UsdGeom, UsdShade

from maillage import generate_scene, write_outputs


@pytest.fixture(scope="module")
def folder(tmp_path_factory):
    scene = generate_scene("flag", count=2, vertices=300)
    return write_outputs(scene, tmp_path_factory.mktemp("out"))


def test_files_written(folder):
    assert (folder / "maillage_flag.usdc").exists()
    assert (folder / "pieces.csv").read_text(encoding="utf-8").count("\n") == 3
    assert sorted(p.name for p in (folder / "textures").iterdir()) == ["flag_000.png", "flag_001.png"]
    assert json.loads((folder / "summary.json").read_text(encoding="utf-8"))["count"] == 2


def test_stage_conventions(folder):
    stage = Usd.Stage.Open(str(folder / "maillage_flag.usdc"))
    assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z
    assert UsdGeom.GetStageMetersPerUnit(stage) == 1.0
    assert stage.GetDefaultPrim().GetPath() == "/World"


def test_cloth_mesh(folder):
    stage = Usd.Stage.Open(str(folder / "maillage_flag.usdc"))
    prim = stage.GetPrimAtPath("/World/Cloths/flag_000")
    mesh = UsdGeom.Mesh(prim)
    assert mesh.GetSubdivisionSchemeAttr().Get() == UsdGeom.Tokens.none
    assert mesh.GetDoubleSidedAttr().Get()
    pv = UsdGeom.PrimvarsAPI(mesh)
    n = len(mesh.GetPointsAttr().Get())
    for name in ("st", "hem", "pin"):
        primvar = pv.GetPrimvar(name)
        assert primvar.GetInterpolation() == UsdGeom.Tokens.vertex
        assert len(primvar.Get()) == n
    assert max(pv.GetPrimvar("pin").Get()) == 1.0
    for attr in (
        "fabric",
        "arealDensity",
        "mass",
        "thickness",
        "friction",
        "size",
        "blender:bendingStiffness",
    ):
        assert prim.GetAttribute(f"maillage:{attr}").HasValue(), attr
    assert prim.GetAttribute("maillage:fabric").Get() == "polyester_knit"


def test_material_and_texture(folder):
    stage = Usd.Stage.Open(str(folder / "maillage_flag.usdc"))
    prim = stage.GetPrimAtPath("/World/Cloths/flag_001")
    mat, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
    assert mat.GetPath() == "/World/Looks/flag_001"
    tex = UsdShade.Shader(stage.GetPrimAtPath("/World/Looks/flag_001/Texture"))
    asset = tex.GetInput("file").Get()
    assert (folder / asset.path).resolve() == (folder / "textures" / "flag_001.png").resolve()
    assert asset.resolvedPath  # the texture resolves from the layer
