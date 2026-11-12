"""Fill the table of contents (and page fields) of a .docx with LibreOffice, then
write the updated .docx and a PDF. Word re-computes the TOC on opening anyway
(updateFields is set); this makes the TOC visible in every viewer.

Usage: python3 docs/build/update_toc.py in.docx out.docx out.pdf
Needs LibreOffice and its Python 'uno' module (system python3 on Ubuntu).
"""
import subprocess
import sys
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue

src, dst, pdf = (Path(a).resolve() for a in sys.argv[1:4])
port = 2002
proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore",
                         f"--accept=socket,host=localhost,port={port};urp;"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ctx = None
local = uno.getComponentContext()
resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
for _ in range(60):
    try:
        ctx = resolver.resolve(f"uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext")
        break
    except Exception:
        time.sleep(1)
if ctx is None:
    proc.kill()
    sys.exit("could not connect to LibreOffice")


def prop(n, v):
    p = PropertyValue()
    p.Name, p.Value = n, v
    return p


desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
doc = desktop.loadComponentFromURL(src.as_uri(), "_blank", 0, (prop("Hidden", True),))
idx = doc.getDocumentIndexes()
n_idx = idx.getCount()
for i in range(idx.getCount()):
    idx.getByIndex(i).update()
doc.refresh()
doc.getTextFields().refresh()
doc.storeToURL(dst.as_uri(), (prop("FilterName", "MS Word 2007 XML"),))
doc.storeToURL(pdf.as_uri(), (prop("FilterName", "writer_pdf_Export"),))
doc.close(True)
try:
    desktop.terminate()
except Exception:
    pass
proc.wait(timeout=30)
print(f"updated {n_idx} index(es): {dst.name}, {pdf.name}")
