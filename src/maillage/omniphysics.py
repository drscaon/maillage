"""NVIDIA OmniPhysics export: the cloths as surface deformables (Isaac Sim 5+).

Written as an OpenUSD layer over the main file, ``maillage_<preset>_omniphysics.usda``,
which sublayers ``maillage_<preset>.usdc`` and adds only physics opinions: the
main file stays engine-neutral, and opening the layer in Omniverse or Isaac
Sim gives the same scene with deformable cloths.

Core OpenUSD has no deformable-body schema yet; this follows NVIDIA's
OmniPhysics deformable schema, applied by name (the file stays valid OpenUSD
for any tool):

  /World/PhysicsScene                 UsdPhysics scene
  /World/Cloths/<piece>               the cloth mesh is the body root and its
                                      simulation mesh (the schema allows the
                                      simulation mesh at the root):
                                      OmniPhysicsDeformableBodyAPI (omniphysics:mass)
                                      + OmniPhysicsSurfaceDeformableSimAPI
                                        (rest shape points and triangles,
                                        flat rest bend angles)
                                      + UsdPhysics CollisionAPI
                                      faces split into triangles if the mesh
                                      has quads (the schema requires triangles)
  /World/Looks/Phys_<fabric>          OmniPhysicsSurfaceDeformableMaterialAPI:
                                      Young's modulus and surface thickness
                                      from the fabric's tensile stiffness and
                                      bending rigidity (fabrics.shell), Poisson's
                                      ratio, density, friction

Not exported: pinned vertices (a flag's hoist corners) need an attachment,
not written yet; the stiffer hem (one material per piece).

This export has not been simulated: OmniPhysics needs an NVIDIA RTX GPU.
``check()`` verifies its structure.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from pxr import Sdf, Usd, UsdGeom, UsdPhysics, UsdShade, Vt

from .fabrics import FABRICS, shell
from .sim.usd_reader import find_usd, triangulate

BODY_APIS = ("OmniPhysicsDeformableBodyAPI", "OmniPhysicsSurfaceDeformableSimAPI")
MATERIAL_APIS = (
    "OmniPhysicsBaseMaterialAPI",
    "OmniPhysicsDeformableMaterialAPI",
    "OmniPhysicsSurfaceDeformableMaterialAPI",
)
_F = Sdf.ValueTypeNames


def overlay_path(usd: Path) -> Path:
    return usd.with_name(f"{usd.stem}_omniphysics.usda")


def _material(stage, fabric: str) -> UsdShade.Material:
    path = f"/World/Looks/Phys_{fabric}"
    mat = UsdShade.Material.Define(stage, path)
    prim = mat.GetPrim()
    for api in MATERIAL_APIS:
        prim.AddAppliedSchema(api)
    fab = FABRICS[fabric]
    E, t = shell(fab)
    for name, value in (
        ("omniphysics:youngsModulus", E),
        ("omniphysics:poissonsRatio", fab["poissons_ratio"]),
        ("omniphysics:surfaceThickness", t),
        ("omniphysics:density", fab["areal_density"] / t),  # kg/m³: areal density over the shell thickness
        ("omniphysics:staticFriction", fab["friction"]),
        ("omniphysics:dynamicFriction", fab["friction"]),
        # 0: membrane and bending follow Young's modulus and the thickness
        ("omniphysics:surfaceStretchStiffness", 0.0),
        ("omniphysics:surfaceShearStiffness", 0.0),
        ("omniphysics:surfaceBendStiffness", 0.0),
    ):
        prim.CreateAttribute(name, _F.Float).Set(float(value))
    return mat


def write_overlay(usd) -> Path:
    usd = find_usd(usd)
    out = overlay_path(usd)
    layer = Sdf.Layer.CreateNew(str(out))
    layer.subLayerPaths.append(f"./{usd.name}")
    stage = Usd.Stage.Open(layer)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)
    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")
    materials = {}
    for prim in stage.GetPrimAtPath("/World/Cloths").GetChildren():
        if not prim.IsA(UsdGeom.Mesh):
            continue
        mesh = UsdGeom.Mesh(prim)
        counts = list(mesh.GetFaceVertexCountsAttr().Get())
        tris = triangulate(counts, list(mesh.GetFaceVertexIndicesAttr().Get()))
        if any(n != 3 for n in counts):  # the simulation mesh must be made of triangles
            mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([3] * len(tris)))
            mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray.FromNumpy(tris.ravel().astype(np.int32)))
        for api in BODY_APIS:
            prim.AddAppliedSchema(api)
        UsdPhysics.CollisionAPI.Apply(prim)
        prim.CreateAttribute("omniphysics:deformableBodyEnabled", _F.Bool).Set(True)
        prim.CreateAttribute("omniphysics:mass", _F.Float).Set(
            float(prim.GetAttribute("maillage:mass").Get())
        )
        prim.CreateAttribute("omniphysics:restShapePoints", _F.Point3fArray).Set(mesh.GetPointsAttr().Get())
        prim.CreateAttribute("omniphysics:restTriVtxIndices", _F.Int3Array).Set(
            Vt.Vec3iArray.FromNumpy(tris.astype(np.int32))
        )
        prim.CreateAttribute(
            "omniphysics:restBendAnglesDefault", _F.Token, variability=Sdf.VariabilityUniform
        ).Set("flatDefault")
        fabric = prim.GetAttribute("maillage:fabric").Get()
        if fabric not in materials:
            materials[fabric] = _material(stage, fabric)
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(
            materials[fabric], UsdShade.Tokens.weakerThanDescendants, "physics"
        )
    layer.Save()
    return out


def check(path) -> list[str]:
    """Structural problems of an OmniPhysics layer (empty: none)."""
    stage = Usd.Stage.Open(str(path))
    problems = []
    if not stage.GetPrimAtPath("/World/PhysicsScene").IsA(UsdPhysics.Scene):
        problems.append("no physics scene")
    cloths = [p for p in stage.GetPrimAtPath("/World/Cloths").GetChildren() if p.IsA(UsdGeom.Mesh)]
    if not cloths:
        problems.append("no cloth")
    for prim in cloths:
        name = prim.GetName()
        listed = prim.GetMetadata("apiSchemas")
        names = set(listed.GetAddedOrExplicitItems()) if listed else set()
        missing = [a for a in (*BODY_APIS, "PhysicsCollisionAPI") if a not in names]
        if missing:
            problems.append(f"{name}: missing {', '.join(missing)}")
        mesh = UsdGeom.Mesh(prim)
        counts = list(mesh.GetFaceVertexCountsAttr().Get())
        if any(n != 3 for n in counts):
            problems.append(f"{name}: simulation mesh not made of triangles")
        rest = prim.GetAttribute("omniphysics:restTriVtxIndices").Get()
        if rest is None or len(rest) != len(counts):
            problems.append(f"{name}: rest triangles do not match the faces")
        pts = np.array(mesh.GetPointsAttr().Get())
        rest_pts = prim.GetAttribute("omniphysics:restShapePoints").Get()
        if rest_pts is None or not np.allclose(np.array(rest_pts), pts):
            problems.append(f"{name}: rest shape differs from the points")
        if abs(prim.GetAttribute("omniphysics:mass").Get() - prim.GetAttribute("maillage:mass").Get()) > 1e-6:
            problems.append(f"{name}: mass differs from maillage:mass")
        mat, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial("physics")
        if not mat:
            problems.append(f"{name}: no physics material")
            continue
        m = mat.GetPrim()
        for attr in ("omniphysics:youngsModulus", "omniphysics:surfaceThickness", "omniphysics:density"):
            v = m.GetAttribute(attr).Get()
            if v is None or not v > 0:
                problems.append(f"{name}: {attr} not positive")
        nu = m.GetAttribute("omniphysics:poissonsRatio").Get()
        if nu is None or not 0 <= nu < 0.5:
            problems.append(f"{name}: Poisson's ratio out of [0, 0.5)")
    return problems


def main(argv=None) -> int:
    """python -m maillage.omniphysics FILE_OR_FOLDER...: check OmniPhysics layers."""
    import sys

    paths = sys.argv[1:] if argv is None else argv
    files = []
    for p in map(Path, paths):
        files += sorted(p.rglob("*_omniphysics.usda")) if p.is_dir() else [p]
    bad = 0
    for f in files:
        problems = check(f)
        bad += bool(problems)
        for msg in problems:
            print(f"{f}: {msg}")
    print(f"{len(files)} OmniPhysics layers checked, {bad} with problems")
    return 1 if bad or not files else 0


if __name__ == "__main__":
    raise SystemExit(main())
