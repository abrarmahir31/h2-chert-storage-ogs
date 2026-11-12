# Cyclic H2 storage in a depleted chert reservoir with OpenGeoSys

A step-by-step guide and verified starter files for a **generic "Aetna-style" screening study** of cyclic underground hydrogen storage in a depleted, microporous Mississippian chert ("chat") gas reservoir with nearby faults (Barber County, Kansas analogue). Tools: OpenGeoSys (OGS) 6.5.9, process TH2M.

**Main document:** [`docs/OGS_H2_Storage_Aetna_30Day_Guide.docx`](docs/OGS_H2_Storage_Aetna_30Day_Guide.docx) (PDF copy next to it)

## How to use the guide

1. Read section 1, **Feasibility and honesty**. It explains what OGS can and cannot do for this topic, and states the three limits:
   - no hysteresis, so trapping is reported as a bracket;
   - only one gas component, so the cushion gas is H2;
   - chert is treated as an effective single continuum.
2. Install with section 2. The primary route is Windows 10 (build 19041+) or 11, with WSL2 + Ubuntu + uv + Python 3.12. It was verified on Windows 10 Pro build 19045; see [`starter/README.md`](starter/README.md).
3. Follow the 30 day pages in section 4: 6 h per day, each with steps, expected output, a checklist and a 3-hour fallback.
4. Use sections 5-6 and the appendices for lookup: risk register, manuscript skeleton, glossary, cheat sheet, troubleshooting and references.

Status tags in the guide:

| Tag | Meaning |
|---|---|
| **[Tested by Claude on Linux]** | Run in a Linux sandbox; the output shown is real. |
| **[Not tested on Windows]** | Written from the official docs; you test it. |
| **TO-VERIFY** | Not confirmed yet. |

## Quick start (WSL2 Ubuntu, verified on Windows 10 Pro build 19045)

```bash
cd ~
```

```bash
sudo apt update
```

```bash
sudo apt install -y python3 python3-venv python3-pip git curl
```

```bash
python3 --version     # 3.14 is NOT supported by OGS -> use uv + Python 3.12 below
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
export PATH="$HOME/.local/bin:$PATH"
```

```bash
uv venv --python 3.12 ~/ogs-env
```

```bash
source ~/ogs-env/bin/activate
```

```bash
uv pip install "ogstools[ogs]"
```

```bash
ogs --version         # ogs  version: 6.5.9
```

```bash
mkdir -p ~/work
```

```bash
cd ~/work
```

```bash
git clone https://github.com/abrarmahir31/h2-chert-storage-ogs.git
```

For the system libraries and the install check, see [`starter/README.md`](starter/README.md).

## Starter files (all run with OGS 6.5.9 / ogstools 0.8.2)

| Folder | What it does | Run time (4 cores) |
|---|---|---|
| `starter/properties/` | `properties.csv` holds **every** model number, each with a tag and a source. `compute_h2_properties.py` computes H2 properties with CoolProp. | seconds |
| `starter/common/` | `props.py` reads the properties table; `schedule.py` builds the shared injection/withdrawal schedule. | - |
| `starter/00_check_install/` | Checks the machine and the installation, and runs one real OGS model. | 10 s |
| `starter/02_benchmarks/` | `fetch_benchmarks.sh` downloads six official benchmarks (tag 6.5.9); `run_benchmarks.py` runs them and their checks. | < 1.5 min |
| `starter/03_radial_h2/` | 2D axisymmetric TH2M well model: cushion filling plus 3 seasonal cycles, run for both trapping brackets, with mass-balance and recovery post-processing. | 5-8 min |
| `starter/04_fault_section/` | 2D plane-strain TH2M section with a fault band. `coulomb.py` computes the Coulomb stress change and sensitivities; `test_coulomb.py` checks it against hand-calculated answers. | 19 min |
| `starter/docker/` | Ubuntu 24.04 container with OGS (the reproducibility fallback). | build 5 min |

Each model folder has an `expected/` subfolder with the results to compare against.

To replace synthetic values with log-derived ones, edit only `starter/properties/properties.csv` (`value`, `tag`, `source`). All model builders read it.

## Rebuilding the document

```bash
python docs/build/make_figures.py
```

```bash
node docs/build/build_guide.js
```

```bash
python3 docs/build/update_toc.py docs/OGS_H2_Storage_Aetna_30Day_Guide.docx docs/OGS_H2_Storage_Aetna_30Day_Guide.docx docs/OGS_H2_Storage_Aetna_30Day_Guide.pdf
```

```bash
python3 docs/build/check_commands.py    # commands in the guide vs. starter files
```

`node` needs the `docx` npm package. `update_toc.py` needs LibreOffice, which fills the table of contents.

## Project logs

- `PROGRESS.md` records what is done.
- `DECISIONS.md` records every modelling decision, with the evidence behind it.

## Scope and honesty

This is a screening study built from cited literature values and clearly labelled synthetic values. It is **not** a site-specific prediction for the Aetna Gas Area.
