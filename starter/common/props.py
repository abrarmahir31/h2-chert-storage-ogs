"""Read starter/properties/properties.csv into a dict {key: float}.

Every number used by the model builders comes from this one file, so that
log-derived values can later replace the synthetic/literature ones without
editing any model script. Values can be overridden from the command line
(see build_prj.py --set key=value) for sensitivity runs.
"""
import csv
from pathlib import Path

CSV = Path(__file__).resolve().parents[1] / "properties" / "properties.csv"


def load(overrides=None):
    rows = list(csv.DictReader(open(CSV, newline="")))
    p = {r["key"]: float(r["value"]) for r in rows}
    for item in overrides or []:
        k, v = item.split("=")
        if k not in p:
            raise KeyError(f"unknown property '{k}' (see {CSV})")
        p[k] = float(v)
    return p


def vg_pc(S_L, pb, m, S_Lr, S_gr):
    """Capillary pressure [Pa] for a liquid saturation, inverse of the
    van Genuchten curve used by OGS (SaturationVanGenuchten):
    S_e = (S_L - S_Lr) / (1 - S_Lr - S_gr),  S_e = (1 + (pc/pb)^(1/(1-m)))^(-m)
    """
    Se = (S_L - S_Lr) / (1.0 - S_Lr - S_gr)
    return pb * (Se ** (-1.0 / m) - 1.0) ** (1.0 - m)


def land_trapped(S_gi, C):
    """Land (1968): trapped gas saturation after imbibition from S_gi."""
    return S_gi / (1.0 + C * S_gi)
