"""Coulomb stress analysis of the fault band (post-processing, no slip modelled).

Conventions (stated once, used everywhere in this file):
* Library functions use COMPRESSION-POSITIVE stresses.
* OGS writes tension-positive stresses. In TH2M, `sigma` is the Bishop
  effective stress: sigma = sigma_total + (p_g - S_L p_c) I  (biot = 1). This was
  checked on the section run (difference < 0.3 kPa).
* Section frame: x = horizontal along the section (azimuth `section_azimuth`),
  y = vertical up, z = horizontal out of plane. Fault strike is along z, and its
  normal lies in the section plane: n = (sin dip, cos dip, 0).
* Coulomb failure function  CFF = tau - mu * sigma_n'   (cohesion 0)
  Coulomb stress change    dCFS = d(tau along background slip direction) - mu * d(sigma_n')
  dCFS > 0 moves the fault towards failure.

Usage: python coulomb.py out/section_drainage.pvd    -> CSV + PNG + sensitivity table
"""
import math

import numpy as np

# ------------------------------------------------------------------ library ---


def andersonian_tensor(Sv, SHmax, Shmin, shmax_azimuth_deg):
    """Compression-positive stress tensor in an (East, North, Up) frame."""
    a = math.radians(shmax_azimuth_deg)
    e_H = np.array([math.sin(a), math.cos(a), 0.0])   # direction of SHmax
    e_h = np.array([math.cos(a), -math.sin(a), 0.0])  # direction of Shmin
    e_v = np.array([0.0, 0.0, 1.0])
    return SHmax * np.outer(e_H, e_H) + Shmin * np.outer(e_h, e_h) + Sv * np.outer(e_v, e_v)


def to_section_frame(S_enu, section_azimuth_deg):
    """Rotate an ENU tensor into the section frame (x along section, y up, z out of plane)."""
    a = math.radians(section_azimuth_deg)
    R = np.array([[math.sin(a), math.cos(a), 0.0],    # x_s
                  [0.0, 0.0, 1.0],                    # y_s (up)
                  [math.cos(a), -math.sin(a), 0.0]])  # z_s
    return R @ S_enu @ R.T


def ogs2d_to_tensor(v):
    """OGS 2D symmetric tensor [xx, yy, zz, xy] (tension +) -> 3x3 compression-positive."""
    xx, yy, zz, xy = v
    return -np.array([[xx, xy, 0.0], [xy, yy, 0.0], [0.0, 0.0, zz]])


def fault_normal(dip_deg):
    d = math.radians(dip_deg)
    return np.array([math.sin(d), math.cos(d), 0.0])


def resolve(S, n):
    """Normal stress (compression +) and shear-traction vector on plane with normal n."""
    t = S @ n
    sn = float(n @ t)
    return sn, t - sn * n


def coulomb(S0, p0, dS_eff, n, mu):
    """Background CFF, slip tendency and Coulomb stress change on one plane.

    S0     background total stress (compression +), 3x3
    p0     background pore pressure
    dS_eff change of EFFECTIVE stress (compression +), 3x3
    """
    sn0, tv0 = resolve(S0, n)
    tau0 = float(np.linalg.norm(tv0))
    s_hat = tv0 / tau0 if tau0 > 0 else np.zeros(3)
    sn0_eff = sn0 - p0
    dsn_eff, dtv = resolve(dS_eff, n)
    dtau = float(s_hat @ dtv)
    dcfs = dtau - mu * dsn_eff
    return dict(sn_eff0=sn0_eff, tau0=tau0, cff0=tau0 - mu * sn0_eff,
                slip_tendency0=tau0 / sn0_eff, dtau=dtau, dsn_eff=dsn_eff, dcfs=dcfs)


# ---------------------------------------------------------- apply to OGS run ---

if __name__ == "__main__":
    import argparse
    import csv
    import sys
    from pathlib import Path

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import ogstools as ot

    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here.parent / "common"))
    import props

    ap = argparse.ArgumentParser()
    ap.add_argument("pvd")
    ap.add_argument("--window", type=float, default=150.0,
                    help="analyse fault cells within this distance [m] above/below the reservoir")
    ap.add_argument("--set", nargs="*", default=[])
    a = ap.parse_args()
    P = props.load(a.set)
    pvd = Path(a.pvd)
    ms = ot.MeshSeries(pvd)
    t = np.asarray(ms.timevalues)
    m0 = ms[0].point_data_to_cell_data()
    yc = ms[0].cell_centers().points[:, 1]
    ztop, zbot = -P["z_top_res"], -P["z_top_res"] - P["res_thickness"]
    import pyvista as pv
    mat = pv.read(here / "mesh" / "domain.vtu").cell_data["MaterialIDs"]  # same cell order as output
    sel = (mat == 4) & (yc < ztop + a.window) & (yc > zbot - a.window)
    idx = np.where(sel)[0]
    depth = -yc[idx]
    in_res = (yc[idx] <= ztop) & (yc[idx] >= zbot)
    g = 9.81

    def background(Pp, i):
        z = depth[i]
        Sv = Pp["Sv_grad"] * z
        S = andersonian_tensor(Sv, Pp["SHmax_ratio"] * Sv, Pp["Shmin_ratio"] * Sv, Pp["SHmax_azimuth"])
        p0 = Pp["p_init"] if in_res[i] else Pp["brine_density"] * g * z
        return to_section_frame(S, Pp["section_azimuth"]), p0

    sig0 = m0.cell_data["sigma"][idx]

    def run(Pp, dip, k_time):
        mk = ms[k_time].point_data_to_cell_data()
        dsig = mk.cell_data["sigma"][idx] - sig0
        n = fault_normal(dip)
        out = [coulomb(*background(Pp, i), ogs2d_to_tensor(dsig[i]), n, Pp["friction"]) for i in range(len(idx))]
        return out

    # time history of the maximum dCFS along the analysed fault segment
    hist = []
    for k in range(len(t)):
        r = run(P, P["fault_dip"], k)
        d = np.array([x["dcfs"] for x in r])
        hist.append((t[k] / 86400, d.max() / 1e6, d.min() / 1e6))
    hist = np.array(hist)
    k_max = int(np.argmax(hist[:, 1]))
    r = run(P, P["fault_dip"], k_max)
    stem = pvd.parent / pvd.stem
    with open(f"{stem}_coulomb_profile.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["depth_m", "in_reservoir", "sn_eff0_MPa", "tau0_MPa", "cff0_MPa",
                    "slip_tendency0", "dtau_MPa", "dsn_eff_MPa", "dcfs_MPa"])
        for i, x in enumerate(r):
            w.writerow([f"{depth[i]:.1f}", int(in_res[i])] + [f"{x[k] / 1e6:.4f}" if k != "slip_tendency0"
                       else f"{x[k]:.4f}" for k in ["sn_eff0", "tau0", "cff0", "slip_tendency0", "dtau", "dsn_eff", "dcfs"]])
    np.savetxt(f"{stem}_coulomb_history.csv", hist, delimiter=",",
               header="t_day,dcfs_max_MPa,dcfs_min_MPa", comments="")

    # sensitivity: friction, fault dip (stress resolved on rotated planes), stress state
    cases = [("base", {}, P["fault_dip"])]
    cases += [(f"friction={v}", {"friction": v}, P["fault_dip"]) for v in (0.4, 0.8)]
    cases += [(f"dip={v}", {}, v) for v in (45, 75)]
    cases += [(f"Shmin_ratio={v}", {"Shmin_ratio": v}, P["fault_dip"]) for v in (0.6, 0.8)]
    cases += [(f"SHmax_ratio={v}", {"SHmax_ratio": v}, P["fault_dip"]) for v in (1.15, 1.3)]
    cases += [(f"SHmax_azimuth={v}", {"SHmax_azimuth": v}, P["fault_dip"]) for v in (45, 115)]
    rows = []
    for label, ov, dip in cases:
        Pp = dict(P, **ov)
        res = run(Pp, dip, k_max)
        rows.append(dict(case=label,
                         dcfs_max_MPa=max(x["dcfs"] for x in res) / 1e6,
                         cff0_max_MPa=max(x["cff0"] for x in res) / 1e6,
                         cff_after_max_MPa=max(x["cff0"] + x["dcfs"] for x in res) / 1e6,
                         slip_tendency0_max=max(x["slip_tendency0"] for x in res)))
    with open(f"{stem}_coulomb_sensitivity.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for row in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in row.items()})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.2), dpi=150)
    ax1.plot(hist[:, 0], hist[:, 1], label="max along fault")
    ax1.plot(hist[:, 0], hist[:, 2], "--", label="min along fault")
    ax1.axhline(0, color="0.5", lw=0.5)
    ax1.set_xlabel("time [days]"); ax1.set_ylabel("ΔCFS [MPa]"); ax1.legend(fontsize=7, frameon=False)
    o = np.argsort(depth)
    ax2.plot([r[i]["dcfs"] / 1e6 for i in o], depth[o], ".", ms=3)
    ax2.axhspan(-ztop, -zbot, color="0.9")
    ax2.invert_yaxis(); ax2.set_xlabel(f"ΔCFS at t = {hist[k_max, 0]:.0f} d [MPa]"); ax2.set_ylabel("depth [m]")
    fig.tight_layout(); fig.savefig(f"{stem}_coulomb.png")
    print(f"max dCFS = {hist[k_max, 1]:.3f} MPa at t = {hist[k_max, 0]:.0f} d on {len(idx)} fault cells")
    for row in rows:
        print(f"  {row['case']:20s} dCFS_max {row['dcfs_max_MPa']:7.3f}  CFF0_max {row['cff0_max_MPa']:7.2f}"
              f"  CFF_after_max {row['cff_after_max_MPa']:7.2f}  Ts0_max {row['slip_tendency0_max']:.3f}")
