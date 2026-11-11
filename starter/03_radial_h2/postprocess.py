"""Post-process a radial H2 run: H2 inventory, mass-balance check, recovery.

H2 mass in a cell = porosity * (S_g * rho_g * 1  +  S_L * rho_L * (1 - xmWL)) * V
(gas phase is pure H2 because vapour_pressure = 0; xmWL = water mass fraction
in the liquid, so 1 - xmWL is dissolved H2).  V = 2*pi*r*area (axisymmetric).

Usage: python postprocess.py out/radial_drainage.pvd  [--prj radial_drainage.prj]
Writes <name>_summary.csv and <name>_inventory.png next to the .pvd file.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import ogstools as ot  # noqa: E402

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "common"))
import props  # noqa: E402

DAY = 86400.0
ap = argparse.ArgumentParser()
ap.add_argument("pvd")
ap.add_argument("--prj", default=None, help="prj used (to read the schedule)")
a = ap.parse_args()
pvd = Path(a.pvd)
name = pvd.stem
prj = Path(a.prj) if a.prj else here / f"{name}.prj"

# schedule = injection curve stored in the prj
txt = prj.read_text()
curve = re.search(r"<curves>(.*?)</curves>", txt, re.S).group(1)
coords = np.array(re.search(r"<coords>(.*?)</coords>", curve).group(1).split(), float)
values = np.array(re.search(r"<values>(.*?)</values>", curve).group(1).split(), float)
wd = [(float(s), float(e)) for s, e in re.findall(r"<start>(.*?)</start><end>(.*?)</end>", txt)]

ms = ot.MeshSeries(pvd)
t = np.asarray(ms.timevalues)
m0 = ms[0]
cells = m0.compute_cell_sizes(length=False, volume=False)
r_c = cells.cell_centers().points[:, 0]
V = 2 * np.pi * r_c * cells.cell_data["Area"]      # axisymmetric cell volume


def h2_mass(mesh):
    c = mesh.point_data_to_cell_data()
    phi, S_L = c["porosity"], c["saturation"]
    m = phi * ((1 - S_L) * c["gas_density"] + S_L * c["liquid_density"] * (1 - c["xmWL"]))
    m_dis = phi * S_L * c["liquid_density"] * (1 - c["xmWL"])
    return float(np.sum(m * V)), float(np.sum(m_dis * V))


inv = np.array([h2_mass(ms[i]) for i in range(len(t))])
M, M_dis = inv[:, 0], inv[:, 1]
# injected mass = integral of rate; rate = flux * well area (2 pi r_w H)
P = props.load()
q_to_rate = P["rate_inj"] / values.max() if values.max() > 0 else 0.0
tt = np.linspace(0, t[-1], 200001)
rate = np.interp(tt, coords, values) * q_to_rate
cum_inj = np.concatenate([[0], np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(tt))])
inj_at_t = np.interp(t, tt, cum_inj)

rows = []
# mass-balance check at end of cushion / injection periods (no withdrawal yet)
first_wd = wd[0][0] if wd else t[-1]
mask = t <= first_wd
err = np.max(np.abs((M[mask] - M[0]) - inj_at_t[mask])) / max(inj_at_t[mask].max(), 1)
print(f"mass-balance error before first withdrawal: {100*err:.3f} % of injected mass")

# recovery per cycle: produced in withdrawal window / injected in preceding window
inj_windows = []
on = values > 0
start = coords[0]
for i in range(1, len(coords)):
    if on[i] and not on[i - 1]:
        start = coords[i]
    if on[i - 1] and not on[i]:
        inj_windows.append((start, coords[i - 1]))
cushion = inj_windows[0][1] - inj_windows[0][0]
m_cushion = P["rate_inj"] * cushion
for k, (s, e) in enumerate(wd):
    i_s, i_e = np.argmin(abs(t - s)), np.argmin(abs(t - e))
    s_inj, e_inj = inj_windows[k + 1]
    m_inj = P["rate_inj"] * (e_inj - s_inj)
    m_prod = M[i_s] - M[i_e]
    rows.append(dict(cycle=k + 1, injected_t=m_inj / 1e3, produced_t=m_prod / 1e3,
                     recovery_factor=m_prod / m_inj,
                     cushion_fraction=m_cushion / (m_cushion + m_inj),
                     dissolved_end_t=M_dis[i_e] / 1e3,
                     pg_max_MPa=float(np.max([ms[i].point_data["gas_pressure"].max()
                                              for i in range(i_s + 1)])) / 1e6))
    print("cycle %d: injected %.0f t, produced %.0f t, RF = %.3f, cushion fraction %.2f"
          % (k + 1, m_inj / 1e3, m_prod / 1e3, m_prod / m_inj, m_cushion / (m_cushion + m_inj)))

with open(pvd.parent / f"{name}_summary.csv", "w", newline="") as f:
    if rows:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
np.savetxt(pvd.parent / f"{name}_inventory.csv",
           np.c_[t / DAY, M / 1e3, M_dis / 1e3, inj_at_t / 1e3], delimiter=",",
           header="t_day,H2_in_place_t,H2_dissolved_t,H2_injected_cumulative_t", comments="")

fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=150)
ax.plot(t / DAY, (M - M[0]) / 1e3, label="H2 in place minus initial (model)")
ax.plot(t / DAY, inj_at_t / 1e3, "--", label="cumulative injected (schedule)")
ax.plot(t / DAY, M_dis / 1e3, ":", label="dissolved in brine")
for s, e in wd:
    ax.axvspan(s / DAY, e / DAY, color="0.9", lw=0)
ax.set_xlabel("time [days]")
ax.set_ylabel("H2 mass [t]")
ax.legend(fontsize=7, frameon=False)
ax.set_title(name, fontsize=8)
fig.tight_layout()
fig.savefig(pvd.parent / f"{name}_inventory.png")
print("wrote", f"{name}_summary.csv, {name}_inventory.csv, {name}_inventory.png")
