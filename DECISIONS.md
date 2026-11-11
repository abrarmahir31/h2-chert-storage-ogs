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
