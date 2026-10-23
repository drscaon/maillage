"""OpenUSD export.

Stage layout (Z up, metres, kilograms):

    /World                       default prim
      /Looks/<piece>             UsdPreviewSurface material with the pattern texture
      /Cloths/<piece>            UsdGeom.Mesh, flat, laid on the ground
      /Ground                    collision ground (UsdPhysics.CollisionAPI)

Each cloth mesh carries:

- geometry: points, faces, `subdivisionScheme = none`, double sided;
- primvars: `st` (texture coordinates, vertex), `hem` (1 on the hemmed band
  along the edges, 0 elsewhere), `pin` (1 on pinned vertices, e.g. a flag's
  hoist corners), `displayColor` (mean colour of the texture);
- engine-neutral physical properties, as custom attributes: `maillage:fabric`,
  `maillage:arealDensity` (kg/m²), `maillage:mass` (kg), `maillage:thickness`
  (m), `maillage:friction`, nominal and actual sizes, pattern;
- stiffness for Blender's cloth solver, for a mesh with 1 cm edges
  (`maillage:blender:*`, see fabrics.py).

OpenUSD has no standard schema for cloth simulation (UsdPhysics covers rigid
bodies and joints), so these properties are custom attributes, documented
here and read by the Blender drop test (maillage/blender/drop_test.py).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade, Vt

from . import __version__
from .fabrics import BLENDER_REFERENCE_EDGE, FABRICS
from .texture import srgb_to_linear

_F = Sdf.ValueTypeNames


def _attr(prim, name, type_name, value):
    prim.CreateAttribute(name, type_name, custom=True).Set(value)


def _material(stage, path: str, texture_path: str, roughness: float) -> UsdShade.Material:
    mat = UsdShade.Material.Define(stage, path)
    surf = UsdShade.Shader.Define(stage, f"{path}/Surface")
    surf.CreateIdAttr("UsdPreviewSurface")
    surf.CreateInput("roughness", _F.Float).Set(float(roughness))
    surf.CreateInput("metallic", _F.Float).Set(0.0)
    reader = UsdShade.Shader.Define(stage, f"{path}/UV")
    reader.CreateIdAttr("UsdPrimvarReader_float2")
    reader.CreateInput("varname", _F.String).Set("st")
    tex = UsdShade.Shader.Define(stage, f"{path}/Texture")
    tex.CreateIdAttr("UsdUVTexture")
    tex.CreateInput("file", _F.Asset).Set(Sdf.AssetPath(texture_path))
    tex.CreateInput("sourceColorSpace", _F.Token).Set("sRGB")
    tex.CreateInput("wrapS", _F.Token).Set("clamp")
    tex.CreateInput("wrapT", _F.Token).Set("clamp")
    tex.CreateInput("st", _F.Float2).ConnectToSource(reader.ConnectableAPI(), "result")
    rgb = tex.CreateOutput("rgb", _F.Float3)
    surf.CreateInput("diffuseColor", _F.Color3f).ConnectToSource(rgb)
    mat.CreateSurfaceOutput().ConnectToSource(surf.ConnectableAPI(), "surface")
    return mat


def _ground(stage, scene) -> None:
    xs = [p.position[0] for p in scene.pieces]
    ys = [p.position[1] for p in scene.pieces]
    m = 1.0 + max(max(p.length, p.width) for p in scene.pieces)
    lo = Gf.Vec3f(min(xs) - m, min(ys) - m, 0.0)
    hi = Gf.Vec3f(max(xs) + m, max(ys) + m, 0.0)
    g = UsdGeom.Mesh.Define(stage, "/World/Ground")
    g.CreatePointsAttr([lo, Gf.Vec3f(hi[0], lo[1], 0), hi, Gf.Vec3f(lo[0], hi[1], 0)])
    g.CreateFaceVertexCountsAttr([4])
    g.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    g.CreateExtentAttr([lo, hi])
    g.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
    g.CreateDisplayColorAttr([Gf.Vec3f(0.18, 0.18, 0.18)])
    UsdPhysics.CollisionAPI.Apply(g.GetPrim())


def export_stage(path: str | Path, scene) -> Path:
    path = Path(path)
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)
    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    world.GetPrim().SetCustomDataByKey("maillage:preset", scene.preset["label"])
    world.GetPrim().SetCustomDataByKey("maillage:version", __version__)
    world.GetPrim().SetCustomDataByKey("maillage:seed", int(scene.seed))
    UsdGeom.Scope.Define(stage, "/World/Looks")
    UsdGeom.Scope.Define(stage, "/World/Cloths")

    for p in scene.pieces:
        fab = FABRICS[p.fabric]
        mat = _material(stage, f"/World/Looks/{p.name}", f"./textures/{p.name}.png", fab["roughness"])
        mesh = UsdGeom.Mesh.Define(stage, f"/World/Cloths/{p.name}")
        pts = p.mesh.points.astype(np.float32)
        mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(pts))
        mesh.CreateFaceVertexCountsAttr(Vt.IntArray.FromNumpy(p.mesh.face_counts.astype(np.int32)))
        mesh.CreateFaceVertexIndicesAttr(Vt.IntArray.FromNumpy(p.mesh.face_indices.astype(np.int32)))
        mesh.CreateExtentAttr(
            [Gf.Vec3f(*map(float, pts.min(axis=0))), Gf.Vec3f(*map(float, pts.max(axis=0)))]
        )
        mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
        mesh.CreateDoubleSidedAttr(True)
        mesh.CreateDisplayColorAttr([Gf.Vec3f(*map(float, srgb_to_linear(p.color)))])
        mesh.AddTranslateOp().Set(Gf.Vec3d(*p.position))

        pv = UsdGeom.PrimvarsAPI(mesh)
        st = pv.CreatePrimvar("st", _F.TexCoord2fArray, UsdGeom.Tokens.vertex)
        st.Set(Vt.Vec2fArray.FromNumpy(p.uv.astype(np.float32)))
        pv.CreatePrimvar("hem", _F.FloatArray, UsdGeom.Tokens.vertex).Set(
            Vt.FloatArray.FromNumpy(p.hem.astype(np.float32))
        )
        pv.CreatePrimvar("pin", _F.FloatArray, UsdGeom.Tokens.vertex).Set(
            Vt.FloatArray.FromNumpy(p.pin.astype(np.float32))
        )

        prim = mesh.GetPrim()
        _attr(prim, "maillage:fabric", _F.String, p.fabric)
        _attr(prim, "maillage:pattern", _F.String, p.pattern["pattern"])
        _attr(prim, "maillage:shape", _F.Token, p.shape)
        _attr(prim, "maillage:arealDensity", _F.Float, float(fab["areal_density"]))
        _attr(prim, "maillage:mass", _F.Float, float(p.mass))
        _attr(prim, "maillage:thickness", _F.Float, float(fab["thickness"]))
        _attr(prim, "maillage:friction", _F.Float, float(fab["friction"]))
        _attr(prim, "maillage:nominalSize", _F.Float2, Gf.Vec2f(*p.nominal))
        _attr(prim, "maillage:size", _F.Float2, Gf.Vec2f(float(p.length), float(p.width)))
        _attr(prim, "maillage:cornerRadius", _F.Float, float(p.corner_radius))
        _attr(prim, "maillage:hemBendingFactor", _F.Float, float(fab["hem_bending_factor"]))
        bl = fab["blender"]
        for name, value in (
            ("tensionStiffness", bl["tension"]),
            ("compressionStiffness", bl["tension"]),
            ("shearStiffness", bl["shear"]),
            ("bendingStiffness", bl["bending"]),
            ("airDamping", bl["air_damping"]),
            ("referenceEdge", BLENDER_REFERENCE_EDGE),
        ):
            _attr(prim, f"maillage:blender:{name}", _F.Float, float(value))

        UsdShade.MaterialBindingAPI.Apply(prim)
        UsdShade.MaterialBindingAPI(prim).Bind(mat)

    _ground(stage, scene)
    stage.GetRootLayer().Save()
    return path
