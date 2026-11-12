# Progress

| Step | Status | Notes |
|------|--------|-------|
| Feasibility research + checkpoint | done | Approved 2026-11-11 with conditions (see DECISIONS.md) |
| OGS 6.5.9 + ogstools 0.8.2 installed on Linux (pip, venv) | done | Tested by Claude on Linux |
| starter/properties (CSV + H2 property check) | done | CoolProp vs ideal gas vs Peng-Robinson |
| starter/03_radial_h2 (TH2M axisymmetric, 3 cycles, 2 trapping brackets) | done | ~5-8 min per run on 4 cores; mass balance error < 0.8 % |
| starter/00_check_install (machine + install check) | done | Tested by Claude on Linux |
| starter/02_benchmarks: fetch at tag 6.5.9 + run 6 official benchmarks (Theis, Kirsch, confined compression, McWhorter, Liakopoulos, Bourgeat) | done | All PASS (official assert checks), < 1 min total |
| starter/04_fault_section: plane-strain TH2M with fault band, Coulomb analysis + sensitivity, 6 verification tests | done | Run 19 min on 4 cores; tests all PASS |
| Word guide docs/OGS_H2_Storage_Aetna_30Day_Guide.docx (88 pages) | draft built | docs/build/*.js; TOC filled with LibreOffice |
| PDF render + visual check | in progress | first pass fixed: day-title duplication, code wrap, keep-with-next |
| README.md | done | |
| Docker fallback (starter/docker) | done | built and tested on Linux: check_install ALL OK, radial 1-cycle RF 0.707 = host |
| Days 21-25 command loops run as printed | running | |
