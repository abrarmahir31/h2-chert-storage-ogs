"""Compute H2 and water properties at reservoir temperature with CoolProp and
compare them to the Peng-Robinson equation that OGS uses (PengRobinson type).

Why: OGS has no built-in hydrogen. You must supply density and viscosity.
CoolProp implements the reference EOS for normal hydrogen (Leachman et al. 2009)
and the viscosity correlation of Muzny et al. (2013). This script tells you how
large the error of Peng-Robinson is, so you can report it in the paper.
Run:  python compute_h2_properties.py      (needs: pip install CoolProp)
"""
import csv
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

here = Path(__file__).parent
P = {r["key"]: float(r["value"]) for r in csv.DictReader(open(here / "properties.csv"))}
R = 8.314462618
T = P["T_res"]
Tc, pc, w, M = CP.PropsSI("Tcrit", "Hydrogen"), CP.PropsSI("Pcrit", "Hydrogen"), \
    CP.PropsSI("acentric", "Hydrogen"), CP.PropsSI("M", "Hydrogen")


def rho_pr(p, T):
    """Peng-Robinson density, same formula as OGS MaterialLib/MPL/Properties/PengRobinson.cpp"""
    a = 0.45724 * R**2 * Tc**2 / pc
    b = 0.07780 * R * Tc / pc
    kappa = 0.37464 + 1.5422 * w - 0.26992 * w**2  # as in OGS source
    alpha = (1 + kappa * (1 - np.sqrt(T / Tc))) ** 2
    A, B = a * alpha * p / (R * T) ** 2, b * p / (R * T)
    Z = np.roots([1, -(1 - B), A - 3 * B**2 - 2 * B, -(A * B - B**2 - B**3)])
    Z = max(z.real for z in Z if abs(z.imag) < 1e-12 and z.real > 0)
    return p * M / (Z * R * T)


rows = []
for p in np.arange(2e6, 20.1e6, 2e6):
    d = CP.PropsSI("D", "T", T, "P", p, "Hydrogen")
    rows.append((p / 1e6, d, rho_pr(p, T), p * M / (R * T),
                 CP.PropsSI("V", "T", T, "P", p, "Hydrogen"),
                 CP.PropsSI("Z", "T", T, "P", p, "Hydrogen")))
print(f"T = {T} K;  Tc={Tc:.4f} K pc={pc:.0f} Pa omega={w} M={M}")
print(" p[MPa] rho_ref  rho_PR  err_PR%  rho_ideal err_ideal%  mu[Pa s]   Z")
for p, d, dpr, did, mu, Z in rows:
    print(f"{p:6.1f} {d:7.3f} {dpr:7.3f} {100*(dpr-d)/d:7.2f} {did:8.3f} {100*(did-d)/d:8.2f}"
          f"  {mu:.3e} {Z:.4f}")
print("water (IAPWS-95) at 8 MPa: rho=%.1f kg/m3 mu=%.3e Pa s" % (
    CP.PropsSI("D", "T", T, "P", 8e6, "Water"), CP.PropsSI("V", "T", T, "P", 8e6, "Water")))
