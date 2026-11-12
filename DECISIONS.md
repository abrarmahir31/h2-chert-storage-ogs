# Decisions log

Each entry: date, decision, reason, evidence. Newest last.

| # | Date | Decision | Reason / evidence |
|---|------|----------|-------------------|
| D1 | 2026-11-11 | Study is a generic "Aetna-style" screening model, not a site prediction. | Approved at checkpoint. No site-calibrated data in this repo yet. |
| D2 | 2026-11-11 | Trapping reported only as a bracket: drainage curves (S_gr = 0) vs. curves with Land-type trapped gas S_gr = S_gi/(1 + C S_gi). | OGS 6.5.9 has no relative-permeability or capillary hysteresis (no "hyster" in MaterialLib/MPL, ProcessLib/TH2M). |
| D3 | 2026-11-11 | "Cushion gas" = H2 left in place. No purity, no CH4/N2 mixing. Native residual gas is represented by the same gas component (H2). | TH2M gas phase = one gas component + water vapour. |
| D4 | 2026-11-11 | Chert micro-porosity enters only via effective properties (immobile water S_Lr, upscaled k, capillary curve). | No dual-porosity/dual-permeability for two-phase flow in OGS. |
| D5 | 2026-11-11 | Faults: 2D plane-strain section with a thin band of ordinary elements (own MaterialID); Coulomb stress change in Python; slip not modelled. | LIE interface elements exist only for single-phase HYDRO_MECHANICS_WITH_LIE. |
| D6 | 2026-11-11 | Gas density = IdealGasLawBinaryMixture, not PengRobinson. Error vs. reference EOS 2.2% at 4 MPa, 4.5% at 8 MPa, 5.7% at 10 MPa (starter/properties/h2_properties_check.txt). | Tested: PengRobinson and IdealGasLaw abort in TH2M with phase transition ("dValue is implemented for derivatives with respect to gas phase pressure or temperature only"). |
| D7 | 2026-11-11 | Dissolved H2 represented through brine density depending on `concentration` (slope M_H2/rho_ref). | Found by test: without it xmWL = 1 (no dissolution). Same construction as OGS benchmark bourgeat.prj. |
| D8 | 2026-11-11 | Radial model: closed compartment (no-flow outer boundary) of radius re_compartment = 500 m; withdrawal by DirichletWithinTimeInterval gas pressure = p_init (gas-only producer). | With re = 1000 m the pressure rise was too small for useful withdrawal (RF 0.19 in test). BHP = p_init avoids producing "native" gas, which the model cannot distinguish from H2 (D3). |
| D9 | 2026-11-11 | Isothermal model (temperature Dirichlet everywhere), vapour_pressure = 0, no gravity in the base case. | Keeps the starter robust on a laptop; gravity is a Day-18 exercise. |
| D10 | 2026-11-11 | All properties in starter/properties/properties.csv with tag + source; the user's neural-field repo is not read. | User instruction. |
| D11 | 2026-11-11 | Repo pushed directly to `main` (new empty repo created by the user for this project). | Empty repository; no other branches. |
| D12 | 2026-11-11 | Section model: uniform initial capillary pressure (capillary equilibrium); seals get p_b = 20 MPa so they stay > 99.5 % brine-saturated. | Tested: negative pc (gas phase absent) in seals made the Eigen SparseLU solver fail at step 1; uniform pc runs (187 steps, 0 rejected). |
| D13 | 2026-11-11 | Shared schedule module starter/common/schedule.py. | Diff showed the first hand-written curve ramped injection linearly through rest periods (bug). Radial runs repeated with the fixed curve. |
| D14 | 2026-11-11 | Section stresses are changes from the (depleted) initial state; in-situ stress added analytically (superposition, linear elasticity). OGS `sigma` = tension-positive Bishop effective stress. | Checked on run: sigma - sigma_total = p_g - S_L p_c within 0.3 kPa. |
| D15 | 2026-11-11 | Fault-orientation sensitivity is done by resolving the modelled stress change on planes of other dips at the same cells (approximation); a full re-mesh with --dip is listed as a Day-24 task. | Saves one 20-min run per dip on a laptop. |
| D16 | 2026-11-12 | Stress inputs: SHmax azimuth N85E, SHmax/Sv = 1.0, Shmin/Sv = 0.65 (strike-slip/normal). | Alt & Zoback (2017, BSSA 107(1)) for Oklahoma/southern Kansas; extrapolation to Barber County is TO-VERIFY. |
| D17 | 2026-11-12 | Per-cycle recovery factor is reported together with H2 in place after each cycle (cumulative balance). | Tested: 360-day cushion gave RF 1.19/1.11/1.06 because withdrawal at BHP = p_init also produces cushion gas. Alternative for the paper: raise p_bhp_min to protect the cushion. |
| D18 | 2026-11-12 | Dip sensitivity must use full re-meshing; the plane-rotation shortcut is only a quick screen. | Tested: dip 45 re-meshed gave max dCFS 0.92 MPa vs 1.23 MPa from rotating the plane (overestimate ~1/3). Supersedes the shortcut in D15. |
| D19 | 2026-11-12 | postprocess.py reads the injection rate from the run (.prj curve x well area), not from properties.csv. | Bug found: --set rate_inj runs showed 50-99 % mass-balance error; after the fix ~1.1 %. |
