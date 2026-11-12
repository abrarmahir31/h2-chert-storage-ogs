// Build docs/OGS_H2_Storage_Aetna_30Day_Guide.docx
// Run from the repo root:  node docs/build/build_guide.js
const fs = require("fs");
const path = require("path");
const L = require("./lib");
const { days } = require("./days");
const { d, P, H1, H2, H3, bullets, numbered, code, callout, table, image, dayPage, checklist } = L;
const { Document, Packer, Paragraph, TextRun, AlignmentType, Footer, Header, PageNumber, TableOfContents, LevelFormat, HeadingLevel, PageBreak } = d;

const ROOT = path.resolve(__dirname, "..", "..");
const FIG = (f) => path.join(__dirname, "fig", f);
const S = (f) => path.join(ROOT, "starter", f);
const body = [];
const add = (...xs) => xs.forEach((x) => (Array.isArray(x) ? body.push(...x) : body.push(x)));

// ============================================================ title page
const TITLE = "Hydro-mechanical screening of cyclic hydrogen storage in a depleted, microporous chert gas reservoir near critically stressed Midcontinent faults";
add(new Paragraph({ spacing: { before: 1800, after: 200 }, children: [new TextRun({ text: "OpenGeoSys from zero to a publishable study", size: 26, color: L.C.ink2 })] }));
add(new Paragraph({ spacing: { after: 300 }, children: [new TextRun({ text: TITLE, bold: true, size: 40, color: L.C.head })] }));
add(new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "An \u201CAetna-style\u201D generic screening model (Barber County, Kansas analogue)", size: 26, italics: true })] }));
add(new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Installation \u00B7 OGS set-up \u00B7 30-day workflow \u00B7 starter models \u00B7 verified references", size: 22, color: L.C.ink2 })] }));
add(...L.table(null, [
  ["**Software**", "OpenGeoSys 6.5.9 and ogstools 0.8.2 (pip), Python 3.12/3.13, gmsh 4.15, ParaView"],
  ["**Platform**", "Windows 11 + WSL2 Ubuntu 24.04 (primary); native Windows pip and Docker as fallbacks"],
  ["**Companion files**", "Repository abrarmahir31/h2-chert-storage-ogs, folder starter/ (all scripts were run)"],
  ["**Status tags**", "{T}  = run by Claude in a Linux sandbox.   {W}  = written from official docs.   {V}  = not yet verified."],
  ["**Version**", "1.0, 12 November 2026"],
], [1.4, 6]));
add(...callout("Warning", "This is a generic screening study built from cited literature values and clearly labelled synthetic values. It is not a site-specific prediction for the Aetna Gas Area. Every model property carries a source tag in starter/properties/properties.csv."));

// ============================================================ TOC
add(new Paragraph({ pageBreakBefore: true, children: [new TextRun({ text: "Contents", bold: true, size: 32, color: L.C.head })], spacing: { after: 200 } }));
add(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));

// ============================================================ 0 how to use
add(H1("0. How to use this guide"));
add(P("This guide takes you from no OpenGeoSys (OGS) experience to a first manuscript draft in 30 days of 6 hours (180 hours). Read sections 1-3 once (they are your reference), then work through the day pages in section 4. Sections 5-6 and the appendices are for looking things up."));
add(...table(["Marker", "Meaning"], [
  ["{T}", "Claude ran this exact command or file in a Linux sandbox (Ubuntu 24.04 container and Linux host, 4 cores, 16 GB) and saw it work. Output shown is real."],
  ["{W}", "Windows-only step written from official Microsoft/OGS documentation. Claude could not run Windows. You test it."],
  ["{V}", "A value or statement Claude could not confirm. Do not cite it until you have checked it."],
  ["Tip / Warning / Check / Why this matters", "Call-out boxes. \u201CWhy this matters\u201D gives the physics or numerical reason for a step."],
], [1.6, 6]));
add(P("Commands are in grey boxes. Type them exactly. Lines starting with `#` inside a box are comments. In every new Ubuntu terminal, first activate the Python environment:"));
add(...code("source ~/ogs-env/bin/activate\ncd ~/h2-chert-storage-ogs"));
add(...image(FIG("fig_workflow.png"), 6.3, "Figure 1. Workflow of the 30-day plan."));

// ============================================================ 1 feasibility
add(H1("1. Feasibility and honesty"));
add(P("Before any modelling, five questions decide what this study can and cannot claim. Each answer below comes from the OGS source code (GitHub mirror ufz/ogs, master of 11 Nov 2026 and tag 6.5.9) and from test runs, not from memory."));
add(H2("1.1 Working title options"));
add(P("The original title promised dual-porosity and micro-pore trapping physics that OGS cannot resolve. Three honest alternatives:"));
add(...numbered([
  `**${TITLE}** (recommended; used on the title page).`,
  "**Safe operating windows for cyclic hydrogen storage in a depleted Mississippian chert reservoir: a coupled two-phase flow and geomechanics screening study** ",
  "**Pressure, trapping bounds and fault stress during seasonal hydrogen cycling in a high-porosity, low-permeability chert reservoir (Kansas analogue)**",
]));
add(H2("1.2 Q1: Is dual porosity / dual permeability available for two-phase flow?"));
add(P("**Answer: No.** The two-phase processes (`TH2M`, `TWOPHASE_FLOW_PP`) contain no dual-continuum formulation. The only micro-porosity model in OGS belongs to `RICHARDS_MECHANICS` (a single mobile phase, written for swelling clays; property `saturation_micro`)."));
add(P("**Best defensible approximation (used here): an effective single continuum.** Micro-pore water is represented as immobile water (residual liquid saturation `res_S_Lr` = 0.45), the chert's permeability is an upscaled effective value, and the capillary curve represents the combined pore system. A second option for later is explicit zoning by MaterialIDs (fractured layers vs. matrix layers)."));
add(...callout("Warning", "Limits: matrix-fracture transfer rates, delayed drainage of micro-pores and any dual-porosity time-scale cannot be resolved. \u201CMicro-pore trapping\u201D can only appear through the residual saturations and the capillary curve, as a bounded estimate, never as a prediction."));
add(H2("1.3 Q2: Is there relative-permeability or capillary hysteresis?"));
add(P("**Answer: No.** No hysteresis model exists in the material library or in the two-phase processes (searched source code). All saturation and relative-permeability models are single-valued (van Genuchten, Brooks-Corey, Udell, Liakopoulos, generalized power, tabulated Curve)."));
add(P("**Consequence:** gas trapped behind a retreating gas front during withdrawal is not simulated, so a single run over-estimates recovery. Hysteresis is strong for H2-brine systems (Lysyy et al. 2022)."));
add(P("**What we do: a trapping bracket.** Bracket A uses drainage curves with residual gas saturation 0 (no trapping, upper bound on recovery). Bracket B uses curves whose residual gas saturation is the Land (1968) trapped saturation S_gr = S_gi/(1 + C S_gi) with S_gi = 1 - S_Lr, applied everywhere (maximum trapping, lower bound). With C = 2, S_gr = 0.262."));
add(...image(FIG("fig_recovery_bracket.png"), 4.6, "Figure 2. Recovery factor per cycle for the two trapping brackets (starter radial model, synthetic properties). {T}"));
add(H2("1.4 Q3: Are hydrogen properties built in?"));
add(P("**Answer: No.** There is no hydrogen entry in the OGS material library; you supply every H2 property. What the starter does:"));
add(...table(["Property", "In the model", "Source / evidence"], [
  ["Gas density", "`IdealGasLawBinaryMixture` (ideal gas of H2 + vapour)", "Peng-Robinson (`PengRobinson`) and `IdealGasLaw` abort in TH2M with phase transition: \u201CdValue is implemented for derivatives with respect to gas phase pressure or temperature only\u201D {T}"],
  ["Density error", "+2.2 % at 4 MPa, +4.5 % at 8 MPa, +5.7 % at 10 MPa", "vs. reference EOS of Leachman et al. (2009) via CoolProp; starter/properties/h2_properties_check.txt {T}"],
  ["Viscosity", "9.5e-6 Pa s (constant)", "Muzny et al. (2013) via CoolProp; varies < 2 % over 4-15 MPa {T}"],
  ["Solubility (Henry)", "7.8e-6 mol/(m3 Pa)", "Sander (2023), pure water at 298 K. Brine salting-out and temperature ignored {V}"],
  ["Dissolved H2 mass", "brine density depends on `concentration`", "Without it dissolved mass was zero (tested); same as OGS benchmark bourgeat.prj {T}"],
], [1.3, 2.2, 3.5]));
add(...image(FIG("fig_h2_density_error.png"), 4.6, "Figure 3. Error of the H2 density models usable in OGS versus the reference equation of state, 50 \u00B0C. {T}"));
add(H2("1.5 Q4: How can a fault be represented, and how is Coulomb stress computed?"));
add(P("**Interface elements are not available for two-phase flow.** Lower-dimensional interface elements (LIE) exist only for `SMALL_DEFORMATION_WITH_LIE` and `HYDRO_MECHANICS_WITH_LIE` (single phase). For TH2M the fault is a **thin band of ordinary elements** (10 m wide, MaterialID 4) with its own permeability and stiffness. **Slip is not modelled.**"));
add(P("**Coulomb stress change** is computed afterwards in Python (starter/04_fault_section/coulomb.py) on each fault-band cell:"));
add(...code("CFF   = tau - mu * sigma_n'                 (compression positive, cohesion 0)\ndCFS  = d(tau along background slip direction) - mu * d(sigma_n')\nsigma_n' = sigma_n - p_eff,   p_eff = p_g - S_L * p_c   (Bishop, chi = S_L, biot = 1)"));
add(P("The background stress comes from an Andersonian stress state (Sv, SHmax, Shmin, SHmax azimuth) rotated into the section; the change comes from OGS. OGS `sigma` is the tension-positive Bishop effective stress; the run confirmed sigma - sigma_total = p_g - S_L p_c to within 0.3 kPa {T}. Six verification tests with hand-calculated answers pass (Mohr circle, pore-pressure-only change, Andersonian optimal dip 60.48\u00B0 for mu = 0.6, rotation, OGS tensor order) {T}."));
add(H2("1.6 Q5: What is already published, and what is new?"));
add(...table(["Work", "What it did", "Relevance"], [
  ["Pfeiffer & Bauer (2015); Pfeiffer (2017, PhD)", "H2 storage in porous media, OGS coupled with ECLIPSE (multi-component gas)", "Closest OGS-related UHS work; flow-focused, sandstone"],
  ["Grunwald et al. (2022); Pitz et al. (2023)", "TH2M formulation in OGS and its benchmarks (nuclear waste)", "Verification basis; not storage"],
  ["Hogeweg et al. (2022)", "UHS benchmark (ECLIPSE, DuMux)", "Generic sandstone reservoir"],
  ["Ramesh Kumar et al. (2023)", "Review of geomechanics of UHS (depleted fields, caverns)", "Fault reactivation context"],
  ["Lysyy et al. (2022)", "Measured H2 relative-permeability hysteresis", "Justifies the trapping bracket"],
], [2.1, 2.7, 2.2]));
add(P("Two web searches did not find a published TH2M (OpenGeoSys) study of hydrogen storage in a depleted reservoir with fault stress. A search is not proof of absence; check Scopus and Google Scholar again before submission {V}."));
add(...callout("Warning", "\u201CFirst study with OGS\u201D is a weak novelty claim (it is about software, not science). The sharpened claim approved for this study: a hydro-mechanical safe operating window for cyclic H2 storage in high-porosity, low-permeability, high-water-saturation chert near critically stressed Midcontinent faults, with log-derived heterogeneity and bracketed (not predicted) trapping. The strength of the paper will come from the chert setting, the bracketed uncertainty, and the coupling of recovery with fault stress."));
add(H2("1.7 The three limits (repeat these in the manuscript)"));
add(...table(["#", "Limit", "Exact wording to use"], [
  ["1", "No hysteresis", "Trapping is reported only as a bracket: one run with the drainage curve (no trapping) and one with an imbibition curve carrying a Land-type trapped-gas saturation. Neither is a prediction."],
  ["2", "No gas mixing", "\u201CCushion gas fraction\u201D means hydrogen left in place as cushion. Purity and mixing with methane or nitrogen are not modelled. Residual native gas is represented by the same gas component (H2)."],
  ["3", "Effective-continuum chert", "Micro-pore effects enter only through effective properties (immobile water, upscaled permeability, capillary curve). Matrix-fracture transfer is not resolved."],
], [0.3, 1.5, 5.2]));
add(P("**Further simplifications (also stated in the manuscript):** isothermal (temperature fixed); water evaporation off (vapour_pressure = 0); ideal-gas H2 density (+2 to +6 % in the operating range); 2D geometry (axisymmetric well; plane-strain section); no gravity in the base case (tested: gravity changes cycle-1 recovery from 0.707 to 0.708 in the 20 m layer); linear elasticity; fault slip not modelled; no geochemistry or microbial H2 consumption; withdrawal at a bottom-hole gas pressure equal to the initial depleted pressure (gas-only producer)."));
add(H2("1.8 Compute plan for your PC"));
add(P("Your PC: 32 GB RAM, 6-8 cores, 30-100 GB free disk, Windows 11. Run times measured in the 4-core sandbox (your PC will be similar or faster):"));
add(...table(["Model", "Cells", "Run time", "Memory"], [
  ["Six official benchmarks", "small", "< 1.5 min total", "< 1 GB"],
  ["Radial model, 1 cycle", "600", "\u2248 2.5 min", "< 1 GB"],
  ["Radial model, 3 cycles (drainage / imbibition)", "600", "\u2248 5 / 8 min", "< 1 GB"],
  ["Fault section, 1 cycle", "9 372", "\u2248 19 min", "\u2248 1-2 GB"],
  ["Coarse 3D sector (optional, not built)", "50k-200k", "hours (estimate)", "8-24 GB (estimate) {V}"],
], [3, 1, 1.4, 1.6]));
add(P("**Plan:** all paper runs in 2D. Run two OGS jobs at the same time (one per brackets/scenario), each using 3 threads (`export OMP_NUM_THREADS=3`). Each run writes 50-150 MB, so keep about 20 GB free and delete `out*/` folders you no longer need. 3D is optional and only after the 2D results are complete."));
add(H2("1.9 What was verified, and how"));
add(...table(["Item", "Status"], [
  ["pip install ogstools[ogs]==0.8.2 \u2192 ogs 6.5.9 (Linux, Python 3.13 host and 3.12 container)", "{T}"],
  ["System libraries needed on clean Ubuntu 24.04 (libgl1, libglu1-mesa, libgomp1, X libs, libosmesa6)", "{T} (found by container test)"],
  ["check_install.py, six official benchmarks (all PASS)", "{T}"],
  ["Radial TH2M model: 3 cycles x 2 brackets; mass balance < 1 %; 1-cycle run identical in container (RF 0.707)", "{T}"],
  ["Fault section TH2M + Coulomb analysis + 6 verification tests", "{T}"],
  ["Docker container (starter/docker/Dockerfile) build and check", "{T} on Linux; Docker Desktop on Windows {W}"],
  ["WSL install, .wslconfig, VS Code WSL extension, ParaView on Windows, native Windows pip", "{W}"],
  ["Site values (depth, temperature, brine, stress magnitudes, fault geometry)", "{V} synthetic/literature"],
], [5.2, 1.8]));

// ============================================================ 2 installation
add(H1("2. Installing OGS on Windows 11"));
add(P("**OGS** (OpenGeoSys) is an open-source finite-element program for coupled thermal (T), hydraulic (H) and mechanical (M) processes in porous media. **ogstools** is its Python companion (meshes, running, reading results). The pip package `ogstools[ogs]` installs both, plus gmsh (mesher) and pyvista (3D data)."));
add(...table(["Route", "When to use", "MFront / PETSc", "Status"], [
  ["A. WSL2 + pip in a venv (primary)", "Default for this study", "MFront yes / PETSc no", "Linux part {T}; Windows part {W}"],
  ["B. Native Windows pip", "If WSL is not allowed on your PC", "no / no (official table)", "{W}"],
  ["C. Docker container", "Reproducibility package; fallback", "MFront yes / PETSc no", "{T} on Linux; Docker Desktop {W}"],
], [2.2, 2, 1.6, 1.6]));
add(P("MFront is a library for advanced rock constitutive models (not needed for the linear-elastic starter). PETSc enables parallel MPI runs (not needed on a laptop)."));
add(H2("2.1 Check your PC"));
add(...code("# PowerShell (Windows)\nGet-CimInstance Win32_ComputerSystem | Select TotalPhysicalMemory\nGet-CimInstance Win32_Processor | Select NumberOfCores,NumberOfLogicalProcessors\nGet-PSDrive C\nwinver"));
add(P("{W} Minimum for this plan: 16 GB RAM, 4 cores, 30 GB free. You have 32 GB and 6-8 cores: comfortable for all 2D work."));
add(H2("2.2 Route A: WSL2 + Ubuntu 24.04 + Python venv (primary)"));
add(P("**WSL2** (Windows Subsystem for Linux) runs a real Linux kernel inside Windows. The OGS team recommends WSL for Windows users and tests on Ubuntu 24.04."));
add(...numbered([
  "Install WSL and Ubuntu (PowerShell as Administrator), restart when asked {W}:",
  { code: "wsl --install -d Ubuntu-24.04" },
  "Optional: limit WSL resources with `C:\\Users\\<you>\\.wslconfig`, then `wsl --shutdown` {W}:",
  { code: "[wsl2]\nmemory=24GB\nprocessors=6" },
  "In Ubuntu: system libraries, repository, venv, OGS {T}:",
  { code: "sudo apt update\nsudo apt install -y python3-venv git libgl1 libglu1-mesa libgomp1 \\\n    libxcursor1 libxinerama1 libxft2 libxrender1 libosmesa6\ncd ~\ngit clone https://github.com/abrarmahir31/h2-chert-storage-ogs.git\npython3 -m venv ~/ogs-env\nsource ~/ogs-env/bin/activate\npip install --upgrade pip\npip install -r ~/h2-chert-storage-ogs/starter/requirements.txt\nogs --version" },
]));
add(...callout("Tip", "Keep your work in the Linux file system (~/...), not under /mnt/c/. File access across the Windows boundary is much slower, and OGS writes many files."));
add(H2("2.3 VS Code and ParaView"));
add(...bullets([
  "VS Code: install on Windows, add the **WSL** extension, then in Ubuntu run `code .` inside the repository {W}.",
  "ParaView (paraview.org, Windows installer): open results through `\\\\wsl.localhost\\Ubuntu-24.04\\home\\<user>\\h2-chert-storage-ogs\\...`. Running `explorer.exe .` in Ubuntu opens the current folder in Windows Explorer {W}.",
]));
add(H2("2.4 Route B: native Windows pip"));
add(P("From the official OGS install page (Python 3.10-3.13 required) {W}:"));
add(...code("python -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1      # PowerShell\npip install ogstools[ogs]"));
add(P("If PowerShell refuses to run Activate.ps1, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once {W}. The bash scripts of the starter (fetch_benchmarks.sh) need Git Bash on this route."));
add(H2("2.5 Route C: Docker container"));
add(P("starter/docker/Dockerfile builds Ubuntu 24.04 + the system libraries + the pinned pip packages. On Windows use Docker Desktop with the WSL2 backend {W}. Commands {T}:"));
add(...code("cd ~/h2-chert-storage-ogs\ndocker build -t ogs-h2 -f starter/docker/Dockerfile .\ndocker run --rm -v \"$PWD:/work\" -w /work ogs-h2 \\\n    python starter/00_check_install/check_install.py"));
add(P("The OGS project also provides Apptainer (Singularity) images for Linux (`apptainer exec ogs-6.x.x-serial.squashfs ogs ...`, see the container page of the OGS user guide) {W}."));
add(H2("2.6 Verify the installation with real runs"));
add(...code(`source ~/ogs-env/bin/activate\ncd ~/h2-chert-storage-ogs\npython starter/00_check_install/check_install.py`));
add(P("Real output from the sandbox (your CPU/RAM lines will differ) {T}:"));
add(...code("Python                       3.13.18                                  OK\nLogical CPU cores            4                                        OK\nRAM visible here [GB]        15.7                                     OK\nimport ogstools              0.8.2                                    OK\nimport gmsh                  4.15.2                                   OK\nogs executable on PATH       /home/user/work/.venv/bin/ogs            OK\nogs --version                6.5.9                                    OK\ntest run (ogstools example)  11 time steps written                    OK\npressure range [MPa]         29.00 .. 31.00                           OK\n\nRESULT: ALL OK"));
add(P("Then run the six official benchmarks (Day 3): `bash fetch_benchmarks.sh` and `python run_benchmarks.py` in starter/02_benchmarks. All six must PASS."));
add(H2("2.7 Updating OGS"));
add(...code("source ~/ogs-env/bin/activate\npip install --upgrade \"ogstools[ogs]\"\nogs --version\npython starter/00_check_install/check_install.py\ncd starter/02_benchmarks\nbash fetch_benchmarks.sh <new-version-tag>\npython run_benchmarks.py"));
add(...callout("Warning", "Never update OGS in the middle of the paper runs. Finish a batch, then update, rerun the benchmarks and the 1-cycle radial test, and compare with starter/*/expected/. Record the new versions in starter/pip_freeze_tested.txt and DECISIONS.md."));
add(H2("2.8 Most common errors and how to fix them"));
add(...table(["Error message / symptom", "Cause", "Fix"], [
  ["`ogs: command not found`", "venv not active", "`source ~/ogs-env/bin/activate` {T}"],
  ["`OSError: libGLU.so.1` (or `libGL.so.1`, `libgomp.so.1`) on `import gmsh`", "missing system libraries", "apt install line of 2.2 {T}"],
  ["`libOSMesa not found` / crash when plotting", "no off-screen renderer", "`sudo apt install libosmesa6`; `export PYVISTA_OFF_SCREEN=true` {T}"],
  ["pip: no matching distribution for ogs", "Python outside 3.10-3.13", "use Ubuntu 24.04's python3 (3.12)"],
  ["`Mismatch in numerical Jacobian perturbation configuration`", "`<epsilons>` count wrong", "TH2M: 3 values (p_g, p_c, T) {T}"],
  ["`Key <x> has been read 0 times` / `read 1 time(s) less`", "misspelled/unused XML tag (or follow-up of an earlier error)", "fix the first error in the log; copy tags from working files"],
  ["`The required bulk node ids map does not exist in the boundary mesh`", "a mesh used for a BC lacks `bulk_node_ids`", "create boundary meshes with ogstools; add ids to the domain if it is used as a BC mesh {T}"],
  ["`PengRobinson::dValue is implemented for derivatives ...`", "PR not supported with TH2M phase transition", "use `IdealGasLawBinaryMixture` (D6) {T}"],
  ["`Newton: The linear solver failed in the compute() step` at step 1", "gas phase absent in parts of the domain (negative p_c) / singular system", "uniform initial p_c, high p_b in seals (D12) {T}"],
  ["Many rejected time steps", "too large steps / sharp schedule switches", "reduce maximum_dt, initial_dt; keep switches as output times"],
  ["PowerShell: running scripts is disabled", "execution policy", "`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` {W}"],
  ["Very slow file access", "working under /mnt/c", "work in ~/ inside WSL"],
], [2.6, 2, 2.4], { size: 17 }));

// ============================================================ 3 setup
add(H1("3. Setting up OGS for this study"));
add(H2("3.1 Project folder layout"));
add(...image(FIG("fig_folder_tree.png"), 6.3, "Figure 4. Repository layout. Only properties.csv holds numbers; scripts read it."));
add(H2("3.2 How a project file (.prj) is organised"));
add(P("A `.prj` file is an XML text file that tells OGS everything about one simulation. Below are the real blocks of starter/03_radial_h2/radial_drainage.prj (shortened)."));
const prjParts = [
  ["meshes", "Which mesh files to read. The first is the domain; the others are boundary meshes used by boundary conditions. `axially_symmetric=\"true\"` makes the 2D (r, z) mesh a revolved body.", "<meshes>\n    <mesh axially_symmetric=\"true\">mesh/domain.vtu</mesh>\n    <mesh axially_symmetric=\"true\">mesh/well.vtu</mesh>\n</meshes>"],
  ["processes", "Which physics (process type) and its settings: the constitutive model of the solid, the process variables, extra outputs (secondary variables), gravity (`specific_body_force`).", "<process>\n    <name>TH2M</name><type>TH2M</type><integration_order>2</integration_order>\n    <constitutive_relation><type>LinearElasticIsotropic</type>\n        <youngs_modulus>E</youngs_modulus><poissons_ratio>nu</poissons_ratio>\n    </constitutive_relation>\n    <jacobian_assembler><type>CentralDifferences</type>\n        <epsilons>0.01 0.01 1e-06</epsilons></jacobian_assembler>\n    <specific_body_force>0 0</specific_body_force>\n</process>"],
  ["media", "Material properties: one medium per MaterialID, each with phases (AqueousLiquid, Gas, Solid), components (H2, W) and medium-level properties (permeability, porosity, saturation curve, relative permeabilities, Biot coefficient, Bishop stress).", "<property><name>saturation</name><type>SaturationVanGenuchten</type>\n    <residual_liquid_saturation>0.45</residual_liquid_saturation>\n    <residual_gas_saturation>0.0</residual_gas_saturation>\n    <p_b>500000.0</p_b><exponent>0.5</exponent></property>"],
  ["time_loop", "How to step through time (time stepping scheme, convergence criterion, non-linear solver) and what to write out (output).", "<time_stepping><type>IterationNumberBasedTimeStepping</type>\n    <t_initial>0</t_initial><t_end>95904000.0</t_end>\n    <initial_dt>60</initial_dt><minimum_dt>1</minimum_dt>\n    <maximum_dt>172800</maximum_dt>\n    <number_iterations>2 4 8 12 20</number_iterations>\n    <multiplier>1.6 1.3 1.0 0.7 0.5</multiplier></time_stepping>"],
  ["parameters / curves", "Named values used elsewhere (Young's modulus, initial values) and time curves (the injection schedule).", "<parameter><name>h2_flux</name><type>CurveScaled</type>\n    <curve>injection_schedule</curve><parameter>one</parameter></parameter>"],
  ["process_variables", "The unknowns (gas_pressure, capillary_pressure, temperature, displacement) with initial conditions and boundary conditions.", "<boundary_condition><mesh>well</mesh><type>Neumann</type>\n    <component>0</component><parameter>h2_flux</parameter></boundary_condition>\n<boundary_condition><mesh>well</mesh><type>DirichletWithinTimeInterval</type>\n    <parameter>p_bhp_min</parameter>\n    <time_interval><start>28512000.0</start><end>38880000.0</end></time_interval>\n</boundary_condition>"],
  ["nonlinear_solvers / linear_solvers", "Newton settings and the linear solver (here the direct sparse solver SparseLU of the Eigen library).", "<nonlinear_solver><name>basic_newton</name><type>Newton</type>\n    <max_iter>25</max_iter><linear_solver>direct</linear_solver></nonlinear_solver>"],
];
for (const [name, txt, xml] of prjParts) { add(H3(`<${name}>`)); add(P(txt)); add(...code(xml)); }
add(...callout("Why this matters", "OGS stops if a tag is misspelled or unused. Never type tags from memory: copy them from a working file (benchmarks or the starter). All tags in this guide come from files that ran with OGS 6.5.9."));
add(H2("3.3 Making meshes"));
add(P("A **mesh** divides the domain into small cells (elements); OGS solves the equations on them. The starter uses the **gmsh** Python API: define points, lines and surfaces, mark **physical groups** (named sets such as `well`), mesh, then `ogstools.Meshes.from_gmsh(..., dim=2)` writes the domain and one boundary mesh per group, with the `bulk_node_ids` and `bulk_element_ids` arrays OGS needs {T}."));
add(...code("import ogstools as ot\nmeshes = ot.Meshes.from_gmsh(\"mesh/radial.msh\", dim=2, log=False)\nmeshes.save(\"mesh\", overwrite=True)      # domain.vtu, well.vtu, outer.vtu, ..."));
add(H2("3.4 Running a simulation"));
add(...code("ogs radial_drainage.prj -o out > out/radial_drainage.log 2>&1\nogs --help        # -o output dir, -m mesh dir, -l log level, -p xml patch, --version"));
add(P("Output: one `.vtu` file per output time plus a `.pvd` index file that ParaView and ogstools read as a time series."));
add(H2("3.5 Post-processing"));
add(H3("ParaView"));
add(...numbered(["File > Open the `.pvd`, press Apply.", "Choose a variable (saturation, gas_pressure, sigma) in the colour menu; press play to animate.", "Filters > Plot Over Line for profiles; Filters > Warp By Vector (displacement) to see deformation; Filters > Threshold on MaterialIDs to isolate the fault band."]));
add(H3("ogstools in Python {T}"));
add(...code("import ogstools as ot\nms = ot.MeshSeries(\"out/radial_drainage.pvd\")\nprint(ms.timevalues[-1] / 86400, \"days\")\nm = ms[-1]                                   # last output (a pyvista mesh)\nprint(m.point_data[\"gas_pressure\"].max() / 1e6, \"MPa\")"));
add(H2("3.6 Choosing the process"));
add(...table(["Process type (verified name)", "Physics", "Use in this study"], [
  ["`LIQUID_FLOW`", "single-phase flow", "Day 4 learning (Theis)"],
  ["`HYDRO_MECHANICS`", "single-phase flow + mechanics", "Day 6 learning; single-phase approximation only"],
  ["`HYDRO_MECHANICS_WITH_LIE`", "single-phase HM with interface elements", "Only for a single-phase fault-slip side study"],
  ["`TWOPHASE_FLOW_PP`", "two-phase flow, no mechanics", "Optional cross-check of flow"],
  ["`RICHARDS_MECHANICS`", "unsaturated single mobile phase + mechanics (has micro-porosity)", "Not suitable: gas is not a mobile phase"],
  ["`TH2M`", "two-phase two-component flow + heat + mechanics, dissolution", "**Main process** (run isothermally)"],
], [2.2, 2.6, 2.2]));
add(...image(FIG("fig_coupling.png"), 6.2, "Figure 5. Couplings in the model: flow and mechanics in TH2M, fault stress in post-processing."));
add(H2("3.7 The starter models"));
add(H3("3.7.1 Radial well model (starter/03_radial_h2)"));
add(...bullets([
  "Geometry: 2D axisymmetric, r = 0.1-500 m (closed compartment), 20 m thick, 600 quadrilaterals refined toward the well.",
  "Initial state: depleted, p_g = 4 MPa, S_L = 0.60 (p_c = 1.764 MPa from van Genuchten), 50 \u00B0C.",
  "Well: H2 injection 0.1 kg/s as a Neumann mass flux; withdrawal by `DirichletWithinTimeInterval` gas pressure = 4 MPa (gas-only producer, never below the initial pressure, so native gas is not produced).",
  "Schedule (starter/common/schedule.py): 180 d cushion filling, 30 d rest, then 3 x (120 d injection, 30 d rest, 120 d withdrawal, 30 d rest).",
  "Recovery factor (per cycle) = H2 produced in the withdrawal window / H2 injected in that cycle. Cushion fraction = cushion mass / (cushion + working mass) = 0.60.",
  "Self-check: H2 inventory change vs. injected mass before the first withdrawal; error < 1 % {T}.",
]));
add(...image(path.join(ROOT, "starter/03_radial_h2/expected/radial_drainage_inventory.png"), 5.4, "Figure 6. H2 inventory vs. injected mass, drainage bracket (grey = withdrawal). {T}"));
add(H3("3.7.2 Fault section (starter/04_fault_section)"));
add(...bullets([
  "Geometry: 2D plane strain, 3 km long, surface to 2.5 km depth; overburden, 50 m caprock, 20 m reservoir at 1450 m, underburden; 10 m fault band dipping 60\u00B0 crossing the reservoir 600 m from the well (left boundary = symmetry plane).",
  "Initial capillary pressure uniform (capillary equilibrium); seals stay > 99.5 % brine-saturated because of their high p_b (D12).",
  "Stress: changes from the depleted initial state (no gravity, no initial stress); in-situ stress added in coulomb.py (superposition).",
  "Output: dCFS history and profile, plus a sensitivity table for friction, dip (stress rotated onto other planes), Shmin/Sv, SHmax/Sv and SHmax azimuth.",
]));
add(...image(path.join(ROOT, "starter/04_fault_section/expected/section_drainage_coulomb.png"), 6.0, "Figure 7. Coulomb stress change on the fault band (synthetic stress state). {T}"));
add(...callout("Check", "Base case: max dCFS = +0.86 MPa at the end of the first injection; the most critical fault cell goes from CFF0 = -0.29 MPa to +0.55 MPa. With Shmin/Sv = 0.6 or mu = 0.4 the synthetic fault already exceeds failure before injection (CFF0 > 0), which is physically inconsistent and shows that the stress state must be calibrated before any conclusion about fault safety."));

// ============================================================ 4 plan
add(H1("4. The 30-day plan"));
add(P("30 consecutive days, 6 hours per day, 180 hours. Changes from the suggested arc, and why: (1) the fault model is a 2D plane-strain section rather than a 3D sector, because fault stress depends more on vertical layering than on the third dimension, and 2D fits your laptop; (2) days 13-16 are a dedicated property block, because OGS has no hydrogen data and every number must be cited; (3) model building (days 17-20) therefore starts one day later than suggested."));
add(...table(["Days", "Block", "Main result"], [
  ["1-3", "Install and verify; official benchmarks", "ALL OK + 6 x PASS"],
  ["4-8", "OGS basics: flow, mechanics, HM, meshing, time stepping", "3 small models understood; radial mesh built (milestone day 7)"],
  ["9-12", "Two-phase and TH2M verification (McWhorter, Liakopoulos, Bourgeat)", "3 verification notes"],
  ["13-16", "Property block (fluids, chat, curves, mechanics/stress)", "Sourced properties.csv (milestone day 14)"],
  ["17-20", "Radial well model and fault section", "Both models run; Coulomb analysis"],
  ["21-25", "Cushion, trapping, sensitivity, safe window, convergence", "Results database (milestone day 21)"],
  ["26-30", "Figures, tables, methods, manuscript, reproducibility, review", "Manuscript skeleton (milestone day 28)"],
], [0.8, 3.6, 2.6]));
for (const day of days) add(...dayPage(day));

// ============================================================ 5 risk register
add(H1("5. Risk register"));
add(...table(["Risk", "Signs", "Remedy", "Seen here?"], [
  ["Non-convergence (Newton fails)", "rejected steps, `linear solver failed`", "smaller max/initial dt; avoid gas-free zones (uniform p_c); check BC switch times", "yes, D12"],
  ["Phase appearance / disappearance", "failure where S_g -> 0", "small residual gas in seals via high p_b; keep S_gr < initial S_g", "yes"],
  ["Units error", "mass balance off by 2pi, 1000, 86400", "everything SI (Pa, s, kg, m); check mass balance every run", "checked"],
  ["Schedule bug", "injection during rest", "use common/schedule.py; plot the curve", "yes, D13"],
  ["Memory limit", "WSL killed, swap", ".wslconfig memory; 2D only; fewer outputs", "no"],
  ["Disk full", "write errors", "delete out*/ folders; fewer output times", "no"],
  ["Wrong stress sign", "dCFS sign flips", "test_coulomb.py; check sigma - sigma_total = p_eff", "checked"],
  ["Uncalibrated stress", "CFF0 > 0 before injection", "calibrate with field data; report scenarios", "yes"],
  ["Version drift", "results change after update", "pin versions; rerun expected/ comparisons", "-"],
  ["Overclaiming", "site-specific wording", "\u201CAetna-style screening\u201D; repeat the three limits", "-"],
], [1.6, 1.6, 2.6, 0.9], { size: 17 }));

// ============================================================ 6 manuscript
add(H1("6. Manuscript skeleton"));
add(H2("6.1 Outline"));
add(...numbered(["Introduction: need for seasonal H2 storage; depleted fields; Midcontinent seismicity (Rubinstein et al. 2018); chat reservoirs (Watney et al. 2001); gap and objective.", "Geological setting: Mississippian chat, Barber County analogue (literature only), stress regime (Alt & Zoback 2017).", "Methods: OGS TH2M formulation; verification; models; properties (Table 1 with tags); schedule; trapping bracket; Coulomb analysis; convergence.", "Results: pressure and plume; recovery vs cycle and cushion; trapping bracket; sensitivity; fault stress; safe operating window.", "Discussion: what controls recovery in microporous chert; seismicity implications; comparison with sandstone studies; limitations.", "Conclusions.", "Data and code availability (repository + Zenodo DOI)."]));
add(H2("6.2 Methods template"));
add(P("\u201CWe used OpenGeoSys 6.5.9 (Bilke et al. 2019; Kolditz et al. 2012) with its TH2M process (Grunwald et al. 2022), run isothermally at [T] \u00B0C. TH2M solves mass balances of the gas component (H2) and water in a liquid and a gas phase with equilibrium dissolution (Henry's law, [H] mol m-3 Pa-1; Sander 2023), coupled to linear-elastic deformation through Bishop's effective stress with chi = S_L. H2 density followed the ideal-gas law (error +2 to +6 % vs. Leachman et al. 2009 over [p range]); viscosity was [mu] Pa s (Muzny et al. 2013). The implementation was verified against the McWhorter and Sunada (1990) solution, the Liakopoulos drainage test and the Bourgeat et al. (2013) phase-appearance benchmark (Supplement S1). A 2D axisymmetric model ([N] cells) of a closed compartment of radius [re] m ... A 2D plane-strain section with a [w] m fault band ... Coulomb stress changes were computed on the fault band as ... Trapping was bracketed by ... Mesh and time-step convergence ... \u201D"));
add(H2("6.3 Limitations (copy into the paper)"));
add(...numbered([
  "No relative-permeability or capillary hysteresis in OGS; trapping is reported as a bracket (drainage curve vs. Land-type trapped-gas curve), not predicted.",
  "Single gas component: cushion gas is H2 left in place; purity and mixing with CH4 or N2 are not modelled; native residual gas is represented as H2.",
  "Effective-continuum chert: micro-pore effects only via immobile water, upscaled permeability and capillary curve; no matrix-fracture transfer.",
  "Ideal-gas H2 density (overestimates density by 2-6 % in the operating range).",
  "Isothermal; no water evaporation; no geochemical or microbial H2 loss.",
  "2D geometries; closed compartment; fault as an element band without slip; linear elasticity.",
  "Synthetic/literature properties and stress state (tags in Table 1); results are screening-level for an Aetna-style setting, not site predictions.",
]));
add(H2("6.4 Reproducibility package"));
add(...bullets(["Repository with starter/, properties.csv (tags + sources), DECISIONS.md, pinned requirements and pip freeze.", "Dockerfile tested from a clean build; run_all.sh; expected/ results for comparison.", "Archived release with DOI; data-availability statement naming OGS version 6.5.9."]));
add(H2("6.5 Self-review checklist for a Q1 journal"));
add(...checklist([
  "Novelty stated as a scientific gap, not a software first", "Every property has a source or tag; synthetic values clearly labelled",
  "Verification shown (3 benchmarks) with error numbers", "Mesh and time-step convergence shown", "Mass balance error reported",
  "Trapping bracket explained; no hysteresis claim", "Cushion = H2 only; no purity claim", "No dual-porosity claim",
  "Stress-state uncertainty shown (scenarios); fault slip not claimed", "All figures colour-blind safe, single y-axis, units",
  "Limitations section complete", "Code/data availability with DOI", "Software versions given", "Every number in the text traceable to a CSV",
]));

// ============================================================ appendices
add(H1("Appendix A. Glossary"));
add(...table(["Term", "Plain-language definition"], [
  ["Axisymmetric", "A 2D (r, z) model that represents a 3D body by rotating it around an axis (here the well)."],
  ["Biot coefficient", "Fraction of pore pressure that acts against the rock skeleton (1 = all of it)."],
  ["Bishop effective stress", "Effective stress for two fluids: pressure acting on the solid is p_g - chi p_c, here chi = S_L."],
  ["Boundary condition (BC)", "What happens at the edge of the model: fixed value (Dirichlet) or fixed flux (Neumann)."],
  ["Capillary pressure p_c", "Gas pressure minus liquid pressure; high in small pores."],
  ["Coulomb failure function CFF", "tau - mu sigma_n'; failure when it reaches 0 (no cohesion)."],
  ["Cushion gas", "Gas left permanently in the reservoir to keep pressure up; here it is H2."],
  ["Depleted reservoir", "A gas reservoir whose pressure has dropped after production."],
  ["Dirichlet / Neumann", "Prescribed value / prescribed flux boundary condition."],
  ["Dual porosity", "A model with two overlapping pore systems (e.g. fractures and matrix) exchanging fluid; not available for two-phase flow in OGS."],
  ["Effective stress", "Stress carried by the rock skeleton (total stress corrected for pore pressure)."],
  ["FEM", "Finite element method: the equations are solved on small cells and assembled into a large system."],
  ["Henry's law", "Dissolved gas concentration = Henry constant x gas partial pressure."],
  ["Hysteresis", "Curves that differ between drainage and imbibition (history dependence)."],
  ["Imbibition / drainage", "Brine re-entering / brine being pushed out of pores."],
  ["Land trapping", "Model of how much gas gets trapped when brine re-enters: S_gr = S_gi/(1 + C S_gi)."],
  ["MaterialIDs", "Integer per cell telling OGS which medium (material) the cell belongs to."],
  ["Newton iteration", "Repeated linearised solve until the non-linear equations are satisfied."],
  ["Plane strain", "2D model assuming no strain in the third direction (long structures)."],
  ["Recovery factor", "H2 produced / H2 injected (per cycle, in this guide)."],
  ["Relative permeability", "Fraction of the rock's permeability available to one phase when two share the pores."],
  ["Residual saturation", "Saturation below which a phase cannot flow."],
  ["SHmax, Shmin, Sv", "Maximum and minimum horizontal stress, vertical stress."],
  ["TH2M", "OGS process for heat (T), two-phase two-component flow (H2) and mechanics (M)."],
  ["van Genuchten", "Common capillary-pressure/saturation model with parameters p_b and m."],
  ["venv", "Python virtual environment: an isolated folder of packages."],
  ["VTU / PVD", "VTK unstructured mesh file / index of a time series of VTU files."],
  ["WSL2", "Windows Subsystem for Linux, version 2: real Linux inside Windows."],
], [1.8, 5.2], { size: 18 }));

add(H1("Appendix B. Cheat sheet (verified)"));
add(P("All entries were used in files that ran with OGS 6.5.9 / ogstools 0.8.2 {T}."));
add(...table(["Item", "Where / example"], [
  ["`ogs file.prj -o out`", "run; `-m` mesh dir; `-l` log level; `-p` XML patch; `--version`"],
  ["`<type>TH2M</type>`", "process; variables gas_pressure, capillary_pressure, temperature, displacement"],
  ["`<mesh axially_symmetric=\"true\">`", "axisymmetric meshes"],
  ["`LinearElasticIsotropic`", "solid model; `youngs_modulus`, `poissons_ratio`"],
  ["`CentralDifferences` + `<epsilons>`", "numerical Jacobian; 3 epsilons for TH2M"],
  ["`AqueousLiquid`, `Gas`, `Solid`", "phase types; components named H2 and W"],
  ["`henry_coefficient`, `diffusion`, `vapour_pressure`, `molar_mass`", "component properties"],
  ["`IdealGasLawBinaryMixture`", "gas density in TH2M with phase transition"],
  ["`Linear` with `liquid_phase_pressure` and `concentration`", "brine density (carries dissolved H2)"],
  ["`SaturationVanGenuchten`", "`residual_liquid_saturation`, `residual_gas_saturation`, `p_b`, `exponent`"],
  ["`RelativePermeabilityVanGenuchten`", "liquid k_r; `minimum_relative_permeability_liquid`"],
  ["`RelativePermeabilityNonWettingPhaseVanGenuchtenMualem`", "gas k_r; `min_relative_permeability`"],
  ["`BishopsPowerLaw`", "`bishops_effective_stress`, `exponent` 1 (chi = S_L)"],
  ["`EffectiveThermalConductivityPorosityMixing`", "medium thermal conductivity"],
  ["`IterationNumberBasedTimeStepping`", "`number_iterations`, `multiplier`"],
  ["`PerComponentDeltaX`", "convergence; `abstols` (5 values for 2D TH2M)"],
  ["`Neumann`, `Dirichlet`, `DirichletWithinTimeInterval`", "BCs; `<time_interval><start/><end/>`"],
  ["`Constant`, `CurveScaled`, `MeshNode`, `Group`", "parameter types (Group: by MaterialIDs)"],
  ["`<medium id=\"0\">`", "one medium per MaterialID"],
  ["secondary variables", "`sigma` (effective), `sigma_total`, `saturation`, `gas_density`, `liquid_density`, `porosity`, `velocity_gas`, `mass_fraction_liquid`"],
  ["`ot.Meshes.from_gmsh(msh, dim=2)`", "domain + boundary meshes from gmsh physical groups"],
  ["`ot.MeshSeries(pvd)`, `.timevalues`, `[i]`", "read results"],
], [3.2, 3.8], { size: 17 }));

add(H1("Appendix C. Troubleshooting guide"));
add(...numbered([
  "Read the **first** `error` or `critical` line in the log: `grep -n -m3 -E '^(error|critical)' out/run.log`. Later errors are often consequences.",
  "Config errors (tag names, counts): compare with a working starter or benchmark file.",
  "Convergence errors: reduce `initial_dt` and `maximum_dt`; check initial conditions are consistent (no gas-free zones next to gas zones); check that boundary values switch at output times.",
  "Wrong-looking results: check mass balance (postprocess.py), units (SI), signs (tension positive), and the schedule curve.",
  "Installation errors: run check_install.py and use the table in 2.8.",
  "Still stuck: search the OGS Discourse forum (discourse.opengeosys.org) with the exact error text; post a minimal example.",
]));

add(H1("Appendix D. References"));
add(P("Status: \u2714 = bibliographic details checked by Claude with a web search on 11-12 Nov 2026 (title, journal, volume, pages/DOI); \u25CB = standard reference not individually re-checked (check the DOI before citing)."));
const refs = [
  ["\u2714", "Alt, R.C. II, Zoback, M.D. (2017). In situ stress and active faulting in Oklahoma. Bulletin of the Seismological Society of America 107(1). doi:10.1785/0120160156"],
  ["\u25CB", "Bell, I.H., Wronski, J., Quoilin, S., Lemort, V. (2014). Pure and pseudo-pure fluid thermophysical property evaluation and the open-source thermophysical property library CoolProp. Ind. Eng. Chem. Res. 53(6), 2498-2508."],
  ["\u2714", "Bilke, L., Flemisch, B., Kalbacher, T., Kolditz, O., Helmig, R., Nagel, T. (2019). Development of open-source porous media simulators: principles and experiences. Transport in Porous Media 130, 337-361. doi:10.1007/s11242-019-01310-1"],
  ["\u2714", "Bourgeat, A.P., Granet, S., Sma\u00EF, F. (2013). Compositional two-phase flow in saturated-unsaturated porous media: benchmarks for phase appearance/disappearance. In: Simulation of Flow in Porous Media, De Gruyter, 1-29. doi:10.1515/9783110282245.81"],
  ["\u25CB", "Byerlee, J. (1978). Friction of rocks. Pure and Applied Geophysics 116, 615-626."],
  ["\u2714", "Grunwald, N., Ma\u00DFmann, J., Naumov, D., Kolditz, O., Nagel, T. (2022). Non-isothermal two-phase flow in deformable porous media: systematic open-source implementation and verification procedure. Geomech. Geophys. Geo-Energy Geo-Resour. 8, 107. doi:10.1007/s40948-022-00394-2"],
  ["\u2714", "Heinemann, N., et al. (2021). Enabling large-scale hydrogen storage in porous media - the scientific challenges. Energy & Environmental Science 14, 853-864. doi:10.1039/D0EE03536J"],
  ["\u2714", "Hogeweg, S., Strobel, G., Hagemann, B. (2022). Benchmark study for the simulation of Underground Hydrogen Storage operations. Computational Geosciences 26, 1367-1378. doi:10.1007/s10596-022-10163-5"],
  ["\u25CB", "King, G.C.P., Stein, R.S., Lin, J. (1994). Static stress changes and the triggering of earthquakes. Bull. Seismol. Soc. Am. 84(3), 935-953."],
  ["\u2714", "Kolditz, O., et al. (2012). OpenGeoSys: an open-source initiative for numerical simulation of thermo-hydro-mechanical/chemical (THM/C) processes in porous media. Environmental Earth Sciences 67(2), 589-599. doi:10.1007/s12665-012-1546-x"],
  ["\u25CB", "Land, C.S. (1968). Calculation of imbibition relative permeability for two- and three-phase flow from rock properties. SPE Journal 8(2), 149-156."],
  ["\u2714", "Leachman, J.W., Jacobsen, R.T., Penoncello, S.G., Lemmon, E.W. (2009). Fundamental equations of state for parahydrogen, normal hydrogen, and orthohydrogen. J. Phys. Chem. Ref. Data 38, 721-748. doi:10.1063/1.3160306"],
  ["\u2714", "Lysyy, M., F\u00F8yen, T., Johannesen, E.B., Fern\u00F8, M., Ersland, G. (2022). Hydrogen relative permeability hysteresis in underground storage. Geophysical Research Letters 49(17). doi:10.1029/2022GL100364"],
  ["\u25CB", "McWhorter, D.B., Sunada, D.K. (1990). Exact integral solutions for two-phase flow. Water Resources Research 26(3), 399-413."],
  ["\u2714", "Muzny, C.D., Huber, M.L., Kazakov, A.F. (2013). Correlation for the viscosity of normal hydrogen obtained from symbolic regression. J. Chem. Eng. Data 58, 969-979. doi:10.1021/je301273j (erratum 2022, doi:10.1021/acs.jced.2c00523)"],
  ["\u2714", "Pfeiffer, W.T., Bauer, S. (2015). Subsurface porous media hydrogen storage - scenario development and simulation. Energy Procedia 76, 565-572. doi:10.1016/j.egypro.2015.07.872"],
  ["\u2714", "Pitz, M., Grunwald, N., Graupner, B., Kurgyis, K., Radeisen, E., Ma\u00DFmann, J., Ziefle, G., Thiedau, J., Nagel, T. (2023). Benchmarking a new TH2M implementation in OGS-6 with regard to processes relevant for nuclear waste disposal. Environmental Earth Sciences 82, 319. doi:10.1007/s12665-023-10971-7"],
  ["\u2714", "Ramesh Kumar, K., Honorio, H., Chandra, D., Lesueur, M., Hajibeygi, H. (2023). Comprehensive review of geomechanics of underground hydrogen storage in depleted reservoirs and salt caverns. Journal of Energy Storage 73, 108912. doi:10.1016/j.est.2023.108912"],
  ["\u2714", "Rubinstein, J.L., Ellsworth, W.L., Dougherty, S.L. (2018). The 2013-2016 induced earthquakes in Harper and Sumner Counties, southern Kansas. Bull. Seismol. Soc. Am. 108(2), 674-689. doi:10.1785/0120170209"],
  ["\u2714", "Sander, R. (2023). Compilation of Henry's law constants (version 5.0.0) for water as solvent. Atmospheric Chemistry and Physics 23, 10901-12440. doi:10.5194/acp-23-10901-2023"],
  ["\u25CB", "van Genuchten, M.Th. (1980). A closed-form equation for predicting the hydraulic conductivity of unsaturated soils. Soil Sci. Soc. Am. J. 44, 892-898."],
  ["\u2714", "Watney, W.L., Guy, W.J., Byrnes, A.P. (2001). Characterization of the Mississippian chat in south-central Kansas. AAPG Bulletin 85(1), 85-113. doi:10.1306/8626C767-173B-11D7-8645000102C1865D"],
  ["\u2714", "Kansas Geological Survey (2002). Characterization of Mississippian Osage chat in south-central Kansas (poster series; Aetna Gas Area discovered 1935, ~209.6 Bcf cumulative gas to May 1999). kgs.ku.edu/PRS/Poster/2002/2002-50/"],
  ["\u2714", "OpenGeoSys documentation and source code, version 6.5.9 (github.com/ufz/ogs, tag 6.5.9; opengeosys.org)."],
];
add(...table(["", "Reference"], refs, [0.3, 6.7], { size: 17 }));

add(H1("Appendix E. Verification log (what Claude ran)"));
add(...table(["Check", "Result"], [
  ["check_install.py (host and container)", "ALL OK"],
  ["run_benchmarks.py (6 official benchmarks, tag 6.5.9)", "6 x PASS"],
  ["Radial drainage, 3 cycles", "580 steps, 0 rejected; RF 0.71 / 0.79 / 0.85; mass balance 1.0 %"],
  ["Radial imbibition, 3 cycles", "645 steps, 20 rejected; RF 0.40 / 0.39 / 0.38; mass balance 0.9 %"],
  ["Radial 1 cycle in Docker container", "RF 0.707 (identical to host)"],
  ["Radial 1 cycle with gravity", "280 steps, 0 rejected; RF 0.708"],
  ["Fault section", "9 372 cells, 187 steps, 0 rejected, 1133 s"],
  ["sigma - sigma_total vs. p_g - S_L p_c", "max difference 0.25 kPa"],
  ["test_coulomb.py", "6 x PASS"],
  ["compute_h2_properties.py", "ideal-gas error 2.2 % (4 MPa) - 11.5 % (20 MPa)"],
  ["Commands in this guide vs. starter scripts", "checked by docs/build/check_commands.py"],
], [3.2, 3.8]));

add(H1("Appendix F. Model properties and their sources"));
add(P("Printed automatically from starter/properties/properties.csv when the guide is built. Tags: **synthetic/literature** = generic or literature-based placeholder; **literature** = taken from a cited source; **computed** = computed by a script (CoolProp). Replace values here only; every model reads this file."));
{
  const lines = fs.readFileSync(path.join(ROOT, "starter/properties/properties.csv"), "utf8").trim().split("\n").slice(1);
  const rows = lines.map((l) => { const c = l.split(","); return [`\`${c[0]}\``, c[1], c[2], c[4], c.slice(5).join(",").replace(/TO-VERIFY/g, "{V}")]; });
  add(...table(["Key", "Value", "Unit", "Tag", "Source"], rows, [1.7, 0.9, 0.8, 1.2, 3.4], { size: 15, keep: false }));
}

// ============================================================ document
const doc = new Document({
  creator: "Claude (Anthropic) for a graduate research project",
  title: "OGS H2 storage 30-day guide",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: L.FONT, size: 22, color: L.C.ink } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: L.FONT, size: 34, bold: true, color: L.C.head }, paragraph: { spacing: { before: 240, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: L.FONT, size: 27, bold: true, color: L.C.head }, paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: L.FONT, size: 23, bold: true, color: "2E5597" }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }, { level: 1, format: LevelFormat.BULLET, text: "\u2013", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 260 } } } }] },
    { reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 360 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "OGS hydrogen-storage guide \u00B7 Aetna-style screening study", size: 16, color: L.C.ink2 })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Page ", size: 18, color: L.C.ink2 }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: L.C.ink2 }), new TextRun({ text: " of ", size: 18, color: L.C.ink2 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: L.C.ink2 })] })] }) },
    children: body,
  }],
});

const out = path.join(ROOT, "docs", "OGS_H2_Storage_Aetna_30Day_Guide.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log("wrote", out, (buf.length / 1024).toFixed(0), "kB");
  if (L.warnings.length) { console.log("WARNINGS:"); L.warnings.forEach((w) => console.log("  " + w)); }
});
