"""Run the official OGS benchmarks used on Days 4-12 and keep their figures.

Each official script compares OGS with an analytical solution and contains
`assert` checks; if a check fails the script raises an error and this runner
reports FAIL. Figures are saved to ./figures/<name>_<n>.png.

First run:  bash fetch_benchmarks.sh
Then:       python run_benchmarks.py              (all)
            python run_benchmarks.py theis        (one)
"""
import os
import runpy
import subprocess
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

here = Path(__file__).resolve().parent
data = here / "ogs_src" / "Tests" / "Data"
figs = here / "figures"
figs.mkdir(exist_ok=True)

# name: (folder, official script or None, prj run directly when no script)
BENCH = {
    "theis": ("Parabolic/LiquidFlow/AxiSymTheis", "axisym_theis.py", None),
    "kirsch": ("Mechanics/Linear/DiscWithHole", "Linear_Disc_with_hole.py", None),
    "confined_compression": ("HydroMechanics/Linear/Confined_Compression", None, "square_1e2.prj"),
    "mcwhorter": ("TH2M/H2/mcWhorter", "mcWhorter.py", None),
    "liakopoulos": ("TH2M/H2M/Liakopoulos", "ogs-jupyter-lab-h2m-2d-liakopoulos.py", None),
    "bourgeat": ("TH2M/H2/dissolution_diffusion", None, "bourgeat.prj"),
}

if not data.exists():
    sys.exit("Benchmarks not found. Run first:  bash fetch_benchmarks.sh")
wanted = sys.argv[1:] or list(BENCH)
results = {}
for name in wanted:
    folder, script, prj = BENCH[name]
    wd = data / folder
    out = wd / "_out"
    out.mkdir(exist_ok=True)
    t0 = time.time()
    cwd = os.getcwd()
    os.chdir(wd)
    try:
        if script:
            os.environ["OGS_TESTRUNNER_OUT_DIR"] = str(out)
            plt.close("all")
            runpy.run_path(script, run_name="__main__")
            for k, num in enumerate(plt.get_fignums()):
                plt.figure(num).savefig(figs / f"{name}_{k}.png", dpi=110)
        else:
            subprocess.run(["ogs", "-o", str(out), prj], check=True,
                           stdout=open(out / "log.txt", "w"), stderr=subprocess.STDOUT)
        results[name] = "PASS"
    except Exception as e:  # report and continue with the next benchmark
        results[name] = f"FAIL ({type(e).__name__}: {str(e)[:120]})"
    finally:
        os.chdir(cwd)
    print(f"{name:22s} {results[name]:6s} {time.time() - t0:6.1f} s", flush=True)

sys.exit(0 if all(v == "PASS" for v in results.values()) else 1)
