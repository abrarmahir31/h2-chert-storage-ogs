"""Make the diagrams and summary charts embedded in the Word guide.
Run from the repo root:  python docs/build/make_figures.py
Inputs are the expected/ results committed in starter/; outputs go to docs/build/fig/.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent / "fig"
out.mkdir(exist_ok=True)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"   # validated categorical slots 1-3
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
FILL = {"a": "#eaf2fc", "b": "#fdeee7", "c": "#e6f6f0", "d": "#f3f2ef"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})


def box(ax, x, y, w, h, text, fill, size=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fill, ec=INK2, lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK,
            weight="bold" if bold else "normal", wrap=True)


def arrow(ax, p, q, text="", style="-|>", color=INK2, rad=0.0, size=7.5, off=(0, 0.06)):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=11, color=color, lw=1.1,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center",
                va="bottom", fontsize=size, color=INK2)


# 1. workflow overview ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 2.9), dpi=200)
ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
steps = [("Days 1-3\nInstall &\nverify", "d"), ("Days 4-8\nOGS basics\n(flow, M, HM)", "d"),
         ("Days 9-12\nTwo-phase\nbenchmarks", "a"), ("Days 13-16\nProperties\n(cited table)", "b"),
         ("Days 17-20\nRadial +\nfault models", "c")]
steps2 = [("Days 21-25\nCycles, trapping\nbracket, ΔCFS", "c"), ("Days 26-30\nFigures, draft,\nreproducibility", "d")]
w, h = 1.7, 1.25
for i, (t, f) in enumerate(steps):
    box(ax, 0.15 + i * 1.97, 2.45, w, h, t, FILL[f])
    if i:
        arrow(ax, (0.15 + i * 1.97 - 0.27, 3.07), (0.15 + i * 1.97, 3.07))
for i, (t, f) in enumerate(steps2):
    box(ax, 4.9 + i * 2.85, 0.35, 2.2, h, t, FILL[f])
arrow(ax, (8.95, 2.45), (6.0, 1.6), rad=-0.15)
arrow(ax, (7.1, 0.97), (7.75, 0.97))
ax.text(0.15, 1.5, "Milestone checks: day 7, 14, 21, 28\nEvery number → properties.csv (with source)\n"
        "Every run → saved .prj + log + expected/ result", fontsize=7.5, color=INK2, va="top")
fig.savefig(out / "fig_workflow.png", bbox_inches="tight"); plt.close(fig)

# 2. coupling diagram ----------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
box(ax, 0.2, 3.4, 2.6, 1.3, "Fluid properties\nH2: ideal gas, μ, Henry\nbrine: ρ(p, c), μ", FILL["d"], 8)
box(ax, 3.6, 3.2, 2.8, 1.6, "Two-phase flow (TH2M)\ngas pressure p_g\ncapillary pressure p_c\nsaturation S_L(p_c)", FILL["a"], 8.5, True)
box(ax, 3.6, 0.3, 2.8, 1.6, "Mechanics\ndisplacement u\neffective stress σ'\n(linear elastic)", FILL["b"], 8.5, True)
box(ax, 7.2, 0.3, 2.6, 1.6, "Fault band (post-proc.)\nresolve σ on plane\nΔCFS = Δτ − μ Δσ'n\n(no slip modelled)", FILL["c"], 8)
box(ax, 7.2, 3.4, 2.6, 1.3, "Well schedule\ninject / rest / withdraw\n(Neumann / Dirichlet)", FILL["d"], 8)
arrow(ax, (2.8, 4.05), (3.6, 4.05))
arrow(ax, (7.2, 4.05), (6.4, 4.05))
arrow(ax, (4.5, 3.2), (4.5, 1.9), "p_eff = p_g − S_L p_c\n(Bishop)", off=(-1.25, 0.0))
arrow(ax, (5.5, 1.9), (5.5, 3.2), "volumetric strain\n→ pore storage", off=(0.95, -0.35))
arrow(ax, (6.4, 1.1), (7.2, 1.1), "σ', p")
fig.savefig(out / "fig_coupling.png", bbox_inches="tight"); plt.close(fig)

# 3. folder tree ---------------------------------------------------------------
tree = """h2-chert-storage-ogs/
├── README.md, PROGRESS.md, DECISIONS.md
├── docs/  OGS_H2_Storage_Aetna_30Day_Guide.docx (+ .pdf)
└── starter/
    ├── requirements.txt          pinned versions
    ├── properties/               properties.csv  ← ALL numbers + sources
    ├── common/                   props.py, schedule.py
    ├── 00_check_install/         check_install.py
    ├── 02_benchmarks/            fetch + run 6 official benchmarks
    ├── 03_radial_h2/             axisymmetric well model (TH2M)
    │   ├── make_mesh.py → build_prj.py → ogs → postprocess.py
    │   └── expected/             results to compare with
    └── 04_fault_section/         plane-strain section + fault band
        ├── make_mesh.py → build_prj.py → ogs → coulomb.py
        └── test_coulomb.py       verification (known answers)"""
fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=200)
ax.axis("off")
ax.add_patch(FancyBboxPatch((0.0, 0.0), 1, 1, transform=ax.transAxes, boxstyle="round,pad=0.01",
                            fc=FILL["d"], ec=INK2, lw=0.8))
ax.text(0.03, 0.95, tree, family="DejaVu Sans Mono", fontsize=8, va="top", color=INK, transform=ax.transAxes)
fig.savefig(out / "fig_folder_tree.png", bbox_inches="tight"); plt.close(fig)

# 4. recovery factor per cycle, both trapping brackets ------------------------------
rf = {}
for b in ("drainage", "imbibition"):
    rows = list(csv.DictReader(open(root / f"starter/03_radial_h2/expected/radial_{b}_summary.csv")))
    rf[b] = [float(r["recovery_factor"]) for r in rows]
fig, ax = plt.subplots(figsize=(5.2, 2.7), dpi=200)
n = len(rf["drainage"])
x = range(1, n + 1)
wb = 0.36
b1 = ax.bar([i - wb / 2 - 0.01 for i in x], rf["drainage"], wb, color=BLUE, label="Bracket A: no trapping (drainage curves)")
b2 = ax.bar([i + wb / 2 + 0.01 for i in x], rf["imbibition"], wb, color=ORANGE, hatch="///", edgecolor="white",
            lw=0, label="Bracket B: Land trapping (C = 2)")
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.015, f"{r.get_height():.2f}",
                ha="center", fontsize=7.5, color=INK)
ax.set_xticks(list(x)); ax.set_xticklabels([f"cycle {i}" for i in x])
ax.set_ylim(0, 1.05); ax.set_ylabel("H2 recovery factor [-]")
ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(fontsize=7.5, frameon=False, loc="upper left", bbox_to_anchor=(0, 1.18), ncol=1)
fig.savefig(out / "fig_recovery_bracket.png", bbox_inches="tight"); plt.close(fig)

# 5. H2 density: reference EOS vs Peng-Robinson vs ideal gas -----------------------
p, ref, pr, ide = [], [], [], []
for line in open(root / "starter/properties/h2_properties_check.txt"):
    s = line.split()
    if len(s) == 8 and s[0].replace(".", "").isdigit():
        p.append(float(s[0])); ref.append(float(s[1])); pr.append(float(s[3])); ide.append(float(s[5]))
fig, ax = plt.subplots(figsize=(5.2, 2.6), dpi=200)
ax.plot(p, ide, color=BLUE, lw=2, marker="o", ms=4, label="ideal gas (used in OGS model)")
ax.plot(p, pr, color=ORANGE, lw=2, ls="--", marker="s", ms=4, label="Peng-Robinson (not usable, see D6)")
ax.axhline(0, color=INK2, lw=0.6)
ax.axvspan(4, 8, color=GRID, alpha=0.6, lw=0)
ax.text(6, max(ide) * 0.6, "operating\nrange (base case)", ha="center", fontsize=7, color=INK2)
ax.set_xlabel("pressure [MPa] at 50 °C"); ax.set_ylabel("density error vs.\nreference EOS [%]")
ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(fontsize=7.5, frameon=False, loc="lower right")
fig.savefig(out / "fig_h2_density_error.png", bbox_inches="tight"); plt.close(fig)
print("figures written to", out)
