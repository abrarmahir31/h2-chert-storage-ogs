"""Check your machine and your OGS installation in one go.

Run inside the activated virtual environment:
    python check_install.py
It prints CPU cores, RAM, free disk, the versions of ogs / ogstools / gmsh /
pyvista, and then runs a tiny OGS simulation that ships with ogstools.
Every line ends with OK, WARN or FAIL.
"""
import importlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ok = True


def line(label, value, status="OK"):
    global ok
    ok &= status != "FAIL"
    print(f"{label:28s} {str(value):40s} {status}")


# ---- machine ---------------------------------------------------------------
line("Python", sys.version.split()[0],
     "OK" if (3, 10) <= sys.version_info[:2] <= (3, 13) else "WARN")
line("Operating system", f"{platform.system()} {platform.release()}"[:40])
line("Logical CPU cores", os.cpu_count())
try:
    mem_kb = int(next(l for l in open("/proc/meminfo") if l.startswith("MemTotal")).split()[1])
    gb = mem_kb / 1024**2
    line("RAM visible here [GB]", f"{gb:.1f}", "OK" if gb >= 8 else "WARN")
except (OSError, StopIteration):
    line("RAM visible here [GB]", "unknown (not Linux/WSL)", "WARN")
free = shutil.disk_usage(Path.home()).free / 1024**3
line("Free disk in home [GB]", f"{free:.0f}", "OK" if free >= 20 else "WARN")

# ---- packages ----------------------------------------------------------------
for mod in ["ogs", "ogstools", "gmsh", "pyvista", "matplotlib", "numpy"]:
    try:
        m = importlib.import_module(mod)
        line(f"import {mod}", getattr(m, "__version__", "imported"))
    except Exception as e:  # e.g. gmsh: libGLU.so.1 missing on WSL
        line(f"import {mod}", f"{type(e).__name__}: {e}"[:40], "FAIL")

exe = shutil.which("ogs")
line("ogs executable on PATH", exe or "not found", "OK" if exe else "FAIL")
if exe:
    v = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout
    ver = next((x for x in v.splitlines() if "version" in x), "?")
    line("ogs --version", ver.replace("ogs  version: ", "")[:40])

# ---- a real simulation ----------------------------------------------------------
try:
    import ogstools as ot
    from ogstools import examples

    # small 2D liquid-flow model shipped with ogstools: a 12 m x 4 m box,
    # pressure 29 MPa on the left and 31 MPa on the right, gravity on
    model = examples.load_model_liquid_flow_simple()
    tmp = Path(tempfile.mkdtemp(prefix="ogs_check_"))
    sim = model.run(tmp, overwrite=True)
    ms = ot.MeshSeries(next(tmp.rglob("*.pvd")))
    p = ms[-1].point_data["pressure"]
    line("test run (ogstools example)", f"{len(ms)} time steps written", "OK")
    line("pressure range [MPa]", f"{p.min()/1e6:.2f} .. {p.max()/1e6:.2f}",
         "OK" if 28.5e6 < p.min() and p.max() < 31.5e6 else "WARN")
except Exception as e:
    line("test run (ogstools example)", f"{type(e).__name__}: {e}"[:40], "FAIL")

print("\nRESULT:", "ALL OK" if ok else "SOME CHECKS FAILED - see the troubleshooting table")
sys.exit(0 if ok else 1)
