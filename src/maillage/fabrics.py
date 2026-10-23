"""Fabric presets: what a textile piece is made of.

Each fabric gives:

- areal_density: mass per unit area (kg/m²), the "grammage" of the fabric
  (g/m² / 1000); with the piece area it gives the piece mass;
- thickness: fabric thickness (m), used for collision distances and for the
  solidified render in Blender;
- friction: dry kinetic friction coefficient against a smooth hard surface
  (order of magnitude);
- roughness: visual roughness for UsdPreviewSurface (matte cotton ~0.9,
  satin silk ~0.35);
- hem_bending_factor: how much stiffer a hemmed edge (fabric folded twice and
  stitched) is in bending than the plain fabric;
- blender: stiffness for Blender's cloth solver (a mass-spring model), see
  below.

Blender's cloth stiffness acts per edge of the mesh and is not divided by the
vertex mass, so the same numbers give a stiffer or softer fabric depending on
the mesh resolution and the vertex mass. Maillage gives the stiffness for a
reference mesh with 1 cm edges (BLENDER_REFERENCE_EDGE) and the real fabric
mass; the drop test rescales it to the actual mesh so the behaviour does not
depend on the resolution:

- tension, shear (applied as tension/compression and shear stiffness) scale
  with the edge length h: k = k_ref * h / h_ref (constant membrane stiffness);
- bending is used as is (constant bending rigidity);
- air_damping scales with the area per vertex: a_ref * (h / h_ref)².

How the values were set (with the drop test itself, maillage/blender/):

- tension = 0.03 × areal density for woven fabrics (0.02 for knits, wool
  knit and fleece, 0.04 for denim): about 3 % stretch when a piece drapes;
- bending: Blender's angular bending model vibrates instead of settling once
  the bending stiffness is too high for the vertex mass (stiff fabric, fine
  mesh). Measured on 1 cm edges, the limit is about 0.015 × areal density;
  the values stay below 0.0104 × areal density, hem included. Each fabric
  gets a fraction of that, from 5 % (silk) to 100 % (denim), so that softer
  fabrics drape more.

These are **plausible, consistent values, not calibrated** against measured
fabric properties, and because of that stability limit stiff fabrics (denim,
terry) drape more in Blender than real ones.
"""

BLENDER_REFERENCE_EDGE = 0.01  # m

FABRICS = {
    "cotton_terry": {
        "label": "Cotton terry (towelling)",
        "areal_density": 0.45,
        "thickness": 0.004,
        "friction": 0.8,
        "roughness": 0.95,
        "hem_bending_factor": 3.0,
        "blender": {"tension": 0.0135, "shear": 0.0054, "bending": 0.0014, "air_damping": 9e-05},
    },
    "cotton_waffle": {
        "label": "Cotton waffle weave",
        "areal_density": 0.22,
        "thickness": 0.0015,
        "friction": 0.6,
        "roughness": 0.9,
        "hem_bending_factor": 3.0,
        "blender": {"tension": 0.0066, "shear": 0.00264, "bending": 0.000381, "air_damping": 7.33e-05},
    },
    "cotton_plain": {
        "label": "Cotton plain weave",
        "areal_density": 0.14,
        "thickness": 0.0003,
        "friction": 0.5,
        "roughness": 0.85,
        "hem_bending_factor": 4.0,
        "blender": {"tension": 0.0042, "shear": 0.00168, "bending": 0.000127, "air_damping": 4.67e-05},
    },
    "cotton_percale": {
        "label": "Cotton percale (bed linen)",
        "areal_density": 0.12,
        "thickness": 0.00025,
        "friction": 0.5,
        "roughness": 0.85,
        "hem_bending_factor": 4.0,
        "blender": {"tension": 0.0036, "shear": 0.00144, "bending": 7.8e-05, "air_damping": 4e-05},
    },
    "linen": {
        "label": "Linen",
        "areal_density": 0.18,
        "thickness": 0.00035,
        "friction": 0.55,
        "roughness": 0.85,
        "hem_bending_factor": 3.0,
        "blender": {"tension": 0.0054, "shear": 0.00216, "bending": 0.000374, "air_damping": 6e-05},
    },
    "denim": {
        "label": "Denim (cotton twill, ~12 oz)",
        "areal_density": 0.4,
        "thickness": 0.0007,
        "friction": 0.6,
        "roughness": 0.85,
        "hem_bending_factor": 2.0,
        "blender": {"tension": 0.016, "shear": 0.0064, "bending": 0.00208, "air_damping": 4e-05},
    },
    "fleece": {
        "label": "Polyester fleece",
        "areal_density": 0.25,
        "thickness": 0.003,
        "friction": 0.8,
        "roughness": 0.95,
        "hem_bending_factor": 2.0,
        "blender": {"tension": 0.005, "shear": 0.0015, "bending": 0.00065, "air_damping": 8.33e-05},
    },
    "microfiber": {
        "label": "Microfiber (cleaning cloth)",
        "areal_density": 0.3,
        "thickness": 0.002,
        "friction": 0.9,
        "roughness": 0.9,
        "hem_bending_factor": 1.5,
        "blender": {"tension": 0.009, "shear": 0.0036, "bending": 0.000832, "air_damping": 0.0001},
    },
    "polyester_knit": {
        "label": "Polyester knit (flag fabric)",
        "areal_density": 0.115,
        "thickness": 0.0002,
        "friction": 0.4,
        "roughness": 0.6,
        "hem_bending_factor": 4.0,
        "blender": {"tension": 0.0023, "shear": 0.00069, "bending": 2.99e-05, "air_damping": 0.000115},
    },
    "silk": {
        "label": "Silk (habotai / satin)",
        "areal_density": 0.06,
        "thickness": 0.0001,
        "friction": 0.3,
        "roughness": 0.35,
        "hem_bending_factor": 4.0,
        "blender": {"tension": 0.0018, "shear": 0.00072, "bending": 7.8e-06, "air_damping": 4e-05},
    },
    "wool_knit": {
        "label": "Wool knit (winter scarf)",
        "areal_density": 0.35,
        "thickness": 0.003,
        "friction": 0.7,
        "roughness": 0.95,
        "hem_bending_factor": 1.5,
        "blender": {"tension": 0.007, "shear": 0.0021, "bending": 0.00146, "air_damping": 0.00012},
    },
}
