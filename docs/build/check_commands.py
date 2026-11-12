"""Check that the commands printed in the Word guide match the starter files.

For every `python <script> ...` line in the .docx it checks that the script
exists in starter/ and that every --option used is defined in that script.
It also checks benchmark names and that each referenced starter path exists.
Run from the repo root:  python docs/build/check_commands.py
"""
import re
import sys
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
docx = root / "docs" / "OGS_H2_Storage_Aetna_30Day_Guide.docx"
xml = zipfile.ZipFile(docx).read("word/document.xml").decode("utf8")
# paragraphs -> plain text lines
paras = [re.sub(r"<[^>]+>", "", p) for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S)]
text = "\n".join(p.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
                 for p in paras)

scripts = {}
for p in list((root / "starter").rglob("*.py")) + list((root / "docs").rglob("*.py")):
    if "ogs_src" not in str(p):
        scripts.setdefault(p.name, []).append(p)   # e.g. two make_mesh.py (radial, section)
bench = re.findall(r'^\s+"(\w+)": \(', (root / "starter/02_benchmarks/run_benchmarks.py").read_text(), re.M)
problems, checked = [], 0
for line in text.splitlines():
    for m in re.finditer(r"python3? (?:-c .*|-\s*<<.*|([\w/.-]+\.py))(.*)", line):
        if not m.group(1):
            continue
        name = Path(m.group(1)).name
        if name not in scripts and name not in ("axisym_theis.py",):
            problems.append(f"script not in starter/: {m.group(1)}  [{line.strip()}]")
            continue
        checked += 1
        if name in scripts:
            src = "".join(f.read_text() for f in scripts[name])
            for opt in re.findall(r"(--[a-z_]+)", m.group(2)):
                if f'"{opt}"' not in src:
                    problems.append(f"option {opt} not defined in {name}  [{line.strip()}]")
            if name == "run_benchmarks.py" and line.strip().startswith("python"):
                for arg in m.group(2).split():
                    if re.fullmatch(r"[a-z_]+", arg) and arg not in bench:
                        problems.append(f"unknown benchmark '{arg}'")
for path in set(re.findall(r"starter/[\w/.-]+", text)):
    p = root / path.rstrip(".,)")
    if not p.exists() and not any(s in path for s in ("out", "*", "figures", "results", "ogs_src", "pip_freeze")):
        problems.append(f"path in guide does not exist: {path}")
print(f"checked {checked} python commands")
print("\n".join(problems) if problems else "OK: all commands and paths match the starter files")
sys.exit(1 if problems else 0)
