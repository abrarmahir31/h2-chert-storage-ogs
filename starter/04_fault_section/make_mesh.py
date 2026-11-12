"""2D plane-strain cross-section (x horizontal, y vertical = elevation) with
layers and a dipping fault band, meshed with gmsh.

MaterialIDs: 0 overburden, 1 caprock, 2 reservoir, 3 underburden, 4 fault band
The fault is a thin band of ordinary elements (no interface elements), so it
can have its own permeability and stiffness. Slip is NOT modelled.
The injection "well" is the reservoir part of the left boundary (symmetry plane).

Run: python make_mesh.py [--dip 60 --width 10 --xf 600 --lc 10]
"""
import argparse
import math
import sys
from pathlib import Path

import gmsh
import numpy as np
import ogstools as ot

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "common"))
import props  # noqa: E402

P = props.load()
ap = argparse.ArgumentParser()
ap.add_argument("--L", type=float, default=3000.0, help="section length [m]")
ap.add_argument("--zbot", type=float, default=2500.0, help="depth of model bottom [m]")
ap.add_argument("--dip", type=float, default=P["fault_dip"], help="fault dip [deg]")
ap.add_argument("--width", type=float, default=10.0, help="fault band width [m]")
ap.add_argument("--xf", type=float, default=600.0, help="x where fault crosses reservoir top [m]")
ap.add_argument("--hcap", type=float, default=50.0, help="caprock thickness [m]")
ap.add_argument("--lc", type=float, default=10.0, help="element size in reservoir/fault [m]")
ap.add_argument("--lc_far", type=float, default=200.0, help="element size far away [m]")
ap.add_argument("--out", default=str(here / "mesh"))
a = ap.parse_args()

ztop_res = -P["z_top_res"]                 # elevation of reservoir top (negative)
zbot_res = ztop_res - P["res_thickness"]
ztop_cap = ztop_res + a.hcap
zbot = -a.zbot

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("section")
occ = gmsh.model.occ
layers = {  # name: (y_bottom, y_top)
    "overburden": (ztop_cap, 0.0), "caprock": (ztop_res, ztop_cap),
    "reservoir": (zbot_res, ztop_res), "underburden": (zbot, zbot_res)}
rect = {n: occ.addRectangle(0, y0, 0, a.L, y1 - y0) for n, (y0, y1) in layers.items()}
# fault band: long thin rectangle, rotated to the dip, centred on (xf, ztop_res)
lf = 2.0 * (abs(zbot) + 100) / math.sin(math.radians(a.dip))
band = occ.addRectangle(-lf / 2, -a.width / 2, 0, lf, a.width)
occ.rotate([(2, band)], 0, 0, 0, 0, 0, 1, -math.radians(a.dip))
occ.translate([(2, band)], a.xf, ztop_res, 0)
box = occ.addRectangle(0, zbot, 0, a.L, -zbot)
occ.intersect([(2, band)], [(2, box)], removeObject=True, removeTool=True)
occ.synchronize()
frags, _ = occ.fragment([(2, t) for t in rect.values()],
                        [(2, s) for _, s in gmsh.model.getEntities(2) if s not in rect.values()])
occ.synchronize()

# classify surfaces by the position of their centre of mass
dip = math.radians(a.dip)
nrm = np.array([math.sin(dip), math.cos(dip)])  # normal to the fault trace


def in_band(x, y):
    return abs(np.dot([x - a.xf, y - ztop_res], nrm)) < a.width / 2 * 1.001


groups = {k: [] for k in ["overburden", "caprock", "reservoir", "underburden", "fault"]}
for _, s in gmsh.model.getEntities(2):
    x, y, _ = occ.getCenterOfMass(2, s)
    if in_band(x, y):
        groups["fault"].append(s)
        continue
    for n, (y0, y1) in layers.items():
        if y0 <= y <= y1:
            groups[n].append(s)
            break

# mesh size: fine in reservoir, caprock and fault, coarse elsewhere
f = gmsh.model.mesh.field
dist = f.add("Distance")
f.setNumbers(dist, "SurfacesList", groups["reservoir"] + groups["caprock"] + groups["fault"])
thr = f.add("Threshold")
f.setNumber(thr, "InField", dist)
f.setNumber(thr, "SizeMin", a.lc)
f.setNumber(thr, "SizeMax", a.lc_far)
f.setNumber(thr, "DistMin", 0)
f.setNumber(thr, "DistMax", 600)
f.setAsBackgroundMesh(thr)
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)

for mid, n in enumerate(["overburden", "caprock", "reservoir", "underburden", "fault"]):
    gmsh.model.addPhysicalGroup(2, groups[n], tag=mid + 1, name=n)


def curves_on(cond):
    out = []
    for _, c in gmsh.model.getEntities(1):
        x0, y0, _, x1, y1, _ = gmsh.model.getBoundingBox(1, c)
        if cond(x0, y0, x1, y1):
            out.append(c)
    return out


eps = 1e-6
bnd = {
    "left": curves_on(lambda x0, y0, x1, y1: x1 < eps),
    "right": curves_on(lambda x0, y0, x1, y1: x0 > a.L - eps),
    "bottom": curves_on(lambda x0, y0, x1, y1: y1 < zbot + eps),
    "top": curves_on(lambda x0, y0, x1, y1: y0 > -eps),
    "well": curves_on(lambda x0, y0, x1, y1: x1 < eps and y0 >= zbot_res - eps and y1 <= ztop_res + eps),
}
for n, c in bnd.items():
    gmsh.model.addPhysicalGroup(1, c, name=n)
gmsh.model.mesh.generate(2)
out = Path(a.out)
out.mkdir(exist_ok=True)
msh = out / "section.msh"
gmsh.write(str(msh))
gmsh.finalize()

meshes = ot.Meshes.from_gmsh(msh, dim=2, log=False)
dom = meshes.domain
dom.cell_data["MaterialIDs"] = (dom.cell_data["MaterialIDs"] - 1).astype(np.int32) \
    if dom.cell_data["MaterialIDs"].min() == 1 else dom.cell_data["MaterialIDs"]
dom.point_data["bulk_node_ids"] = np.arange(dom.n_points, dtype=np.uint64)
dom.cell_data["bulk_element_ids"] = np.arange(dom.n_cells, dtype=np.uint64)
meshes.save(out, overwrite=True)
ids, counts = np.unique(dom.cell_data["MaterialIDs"], return_counts=True)
print("cells:", dom.n_cells, "| cells per MaterialID:", dict(zip(ids.tolist(), counts.tolist())),
      "| boundary meshes:", sorted(k for k in meshes.keys() if k != "domain"))
