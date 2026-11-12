"""Verification of coulomb.py on cases with a known (hand-calculated) answer.
Run:  python test_coulomb.py     -> prints PASS for each test, exits 1 on failure
"""
import math

import numpy as np

from coulomb import (andersonian_tensor, coulomb, fault_normal, ogs2d_to_tensor,
                     resolve, to_section_frame)


def check(name, cond):
    print(f"{'PASS' if cond else 'FAIL'}  {name}")
    return cond


ok = True
# 1. Uniaxial stress s1 along x; plane normal at angle th to x:
#    sigma_n = s1 cos^2(th), |tau| = s1 sin(th) cos(th)   (Mohr circle)
s1, th = 10.0, math.radians(30)
S = np.diag([s1, 0.0, 0.0])
n = np.array([math.cos(th), math.sin(th), 0.0])
sn, tv = resolve(S, n)
ok &= check("uniaxial: normal stress = s1 cos^2", abs(sn - s1 * math.cos(th) ** 2) < 1e-12)
ok &= check("uniaxial: shear = s1 sin cos", abs(np.linalg.norm(tv) - s1 * math.sin(th) * math.cos(th)) < 1e-12)

# 2. Pore-pressure increase dp with unchanged total stress: effective stress
#    (compression +) drops by dp on every plane -> dCFS = mu * dp
mu, dp = 0.6, 2.0e6
S0 = np.diag([30e6, 20e6, 25e6])
dS_eff = -dp * np.eye(3)
r = coulomb(S0, 10e6, dS_eff, fault_normal(60), mu)
ok &= check("pore pressure only: dCFS = mu*dp", abs(r["dcfs"] - mu * dp) < 1e-6)

# 3. Normal-faulting regime (Sv > SHmax > Shmin), section along Shmin:
#    the most critically stressed dip is 45 + atan(mu)/2 = 60.48 deg for mu = 0.6
Sv = 35e6
S_enu = andersonian_tensor(Sv, 0.8 * Sv, 0.6 * Sv, shmax_azimuth_deg=0)  # SHmax N-S
S_sec = to_section_frame(S_enu, section_azimuth_deg=90)                    # section E-W = Shmin
dips = np.arange(30, 90, 0.01)
cff = [coulomb(S_sec, 14e6, np.zeros((3, 3)), fault_normal(d), mu)["cff0"] for d in dips]
best = dips[int(np.argmax(cff))]
ok &= check(f"optimal dip = 45 + atan(mu)/2 = {45 + math.degrees(math.atan(mu)) / 2:.2f} (got {best:.2f})",
            abs(best - (45 + math.degrees(math.atan(mu)) / 2)) < 0.02)

# 4. Rotation: with section along SHmax, the in-plane horizontal stress is SHmax
S_sec = to_section_frame(andersonian_tensor(Sv, 1.1 * Sv, 0.7 * Sv, 75), 75)
ok &= check("rotation: S_xx = SHmax, S_zz = Shmin, S_yy = Sv",
            np.allclose(np.diag(S_sec), [1.1 * Sv, Sv, 0.7 * Sv]))

# 5. OGS vector order [xx, yy, zz, xy], tension positive -> compression positive tensor
T = ogs2d_to_tensor([-1.0, -2.0, -3.0, 0.5])
ok &= check("OGS [xx,yy,zz,xy] mapping and sign", np.allclose(T, [[1, -0.5, 0], [-0.5, 2, 0], [0, 0, 3]]))

print("ALL PASS" if ok else "SOME TESTS FAILED")
raise SystemExit(0 if ok else 1)
