# Starter files: installation and use

## Install (Windows 10 build 19041+ or Windows 11, WSL2)

Verified by the user on Windows 10 Pro (build 19045) with WSL2, unless marked otherwise.

1. **PowerShell as Administrator.** The download takes a few minutes. Then create the Linux user and password. A question about sending usage metrics to Canonical can be answered `y` or `n`.

   ```bash
   wsl --install -d Ubuntu
   ```

2. **In Ubuntu: start in your Linux home.** New windows can start in `/mnt/c/Windows/system32`.

   ```bash
   cd ~
   ```

3. **Install basic tools.** A red "Job for systemd-binfmt.service failed" message is harmless in WSL; ignore it.

   ```bash
   sudo apt update
   ```

   ```bash
   sudo apt install -y python3 python3-venv python3-pip git curl
   ```

4. **Check the Python version.**

   ```bash
   python3 --version
   ```

   OGS's pip package supports Python 3.10-3.13 only. The current Ubuntu release ("resolute") ships 3.14, so do **not** use the system Python. Use uv with Python 3.12 instead.

5. **Install uv.**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

6. **Create a Python 3.12 environment and install OGS.**

   ```bash
   uv venv --python 3.12 ~/ogs-env
   ```

   ```bash
   source ~/ogs-env/bin/activate
   ```

   ```bash
   uv pip install "ogstools[ogs]"
   ```

7. **Verify.**

   ```bash
   ogs --version          # ogs  version: 6.5.9 (build options include OGS_USE_MFRONT=ON)
   ```

   ```bash
   uv pip show ogstools   # Version: 0.8.2, Location: ~/ogs-env/...
   ```

   ```bash
   ogs --help
   ```

8. **Clone this repository into ~/work.** Create the folders before you `cd` into them.

   ```bash
   mkdir -p ~/work/ogs-tests
   ```

   ```bash
   cd ~/work
   ```

   ```bash
   git clone https://github.com/abrarmahir31/h2-chert-storage-ogs.git
   ```

9. **System libraries, CoolProp and the install check.** Tested by Claude on Linux; *not tested on Windows yet*.

   ```bash
   sudo apt install -y libgl1 libglu1-mesa libgomp1 libxcursor1 libxinerama1 libxft2 libxrender1 libosmesa6
   ```

   ```bash
   uv pip install CoolProp==8.0.0
   ```

   ```bash
   cd ~/work/h2-chert-storage-ogs
   ```

   ```bash
   python starter/00_check_install/check_install.py     # must end with: RESULT: ALL OK
   ```

**Every new Ubuntu terminal:** run these before anything else.

```bash
cd ~
```

```bash
export PATH="$HOME/.local/bin:$PATH"
```

```bash
source ~/ogs-env/bin/activate
```

The other routes are *not tested on Windows*:

- **System-Python venv:** only if `python3 --version` is 3.10-3.13. Uses `pip install -r starter/requirements.txt`.
- **Native Windows pip.**
- **Docker:** `starter/docker/Dockerfile`, tested by Claude on Linux.

## Typical beginner mistakes

| Symptom | Fix |
|---|---|
| `AttributeError` from `python -c "import ogstools; print(ogstools._version_)"` | It is `__version__`, with two underscores on each side. Safer: `uv pip show ogstools`. |
| `cd ~/work`: No such file or directory | Create the folder first: `mkdir -p ~/work`. |
| Files appear in `/mnt/c/Windows/system32` | Run `cd ~` first in every new window. |
| `ogs` cannot be installed; Python is 3.14 | Use the uv Python 3.12 environment (step 6). |
| `uv: command not found` | `export PATH="$HOME/.local/bin:$PATH"` |

## What is in here

| Folder | Purpose |
|---|---|
| `properties/` | `properties.csv`: every model number, with a tag and a source |
| `common/` | Shared helpers: properties reader and storage schedule |
| `00_check_install/` | Machine and installation check, including one real OGS run |
| `02_benchmarks/` | Fetch and run six official OGS benchmarks (tag 6.5.9) |
| `03_radial_h2/` | 2D axisymmetric TH2M well model (cycles, trapping brackets) |
| `04_fault_section/` | 2D plane-strain TH2M section with a fault band, Coulomb analysis and tests |
| `docker/` | Container fallback |

Full instructions: `docs/OGS_H2_Storage_Aetna_30Day_Guide.docx` (Days 1-30).
