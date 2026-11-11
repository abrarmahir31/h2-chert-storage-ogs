"""Build the 2D axisymmetric (r, z) mesh around one well with gmsh.

r = horizontal distance from the well axis, z = elevation inside the reservoir.
Cells are small near the well (where pressure changes fast) and grow outward
(geometric progression). Defaults (well radius, compartment radius, thickness) come from properties.csv.
Run:  python make_mesh.py  [--nr 60 --nz 10 --out mesh]
"""
import argparse
from pathlib import Path

import sys

import gmsh
import ogstools as ot

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "common"))
import props  # noqa: E402

P = props.load()
ap = argparse.ArgumentParser()
ap.add_argument("--rw", type=float, default=P["r_well"], help="well radius [m]")
ap.add_argument("--re", type=float, default=P["re_compartment"], help="outer radius [m]")
ap.add_argument("--h", type=float, default=P["res_thickness"], help="reservoir thickness [m]")
ap.add_argument("--nr", type=int, default=60, help="cells in r")
ap.add_argument("--nz", type=int, default=10, help="cells in z")
ap.add_argument("--grow", type=float, default=1.10, help="cell growth factor in r")
ap.add_argument("--out", default=str(here / "mesh"))
a = ap.parse_args()

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("radial")
g = gmsh.model.geo
p1, p2 = g.addPoint(a.rw, 0, 0), g.addPoint(a.re, 0, 0)
p3, p4 = g.addPoint(a.re, a.h, 0), g.addPoint(a.rw, a.h, 0)
bottom, outer = g.addLine(p1, p2), g.addLine(p2, p3)
top, well = g.addLine(p3, p4), g.addLine(p4, p1)
surf = g.addPlaneSurface([g.addCurveLoop([bottom, outer, top, well])])
g.mesh.setTransfiniteCurve(bottom, a.nr + 1, "Progression", a.grow)
g.mesh.setTransfiniteCurve(top, a.nr + 1, "Progression", 1 / a.grow)
g.mesh.setTransfiniteCurve(outer, a.nz + 1)
g.mesh.setTransfiniteCurve(well, a.nz + 1)
g.mesh.setTransfiniteSurface(surf)
g.mesh.setRecombine(2, surf)  # quadrilaterals
g.synchronize()
for dim, tags, name in [(2, [surf], "domain"), (1, [well], "well"),
                        (1, [outer], "outer"), (1, [top], "top"),
                        (1, [bottom], "bottom")]:
    gmsh.model.addPhysicalGroup(dim, tags, name=name)
gmsh.model.mesh.generate(2)
out = Path(a.out)
out.mkdir(exist_ok=True)
msh = out / "radial.msh"
gmsh.write(str(msh))
gmsh.finalize()

meshes = ot.Meshes.from_gmsh(msh, dim=2, log=False)
# The domain itself is also used as a "boundary" mesh for the temperature
# Dirichlet condition (isothermal model). OGS then needs these two id arrays.
import numpy as np  # noqa: E402
dom = meshes.domain
dom.point_data["bulk_node_ids"] = np.arange(dom.n_points, dtype=np.uint64)
dom.cell_data["bulk_element_ids"] = np.arange(dom.n_cells, dtype=np.uint64)
meshes.save(out, overwrite=True)
print("meshes written:", sorted(meshes.keys()), "cells in domain:", meshes.domain.n_cells)
