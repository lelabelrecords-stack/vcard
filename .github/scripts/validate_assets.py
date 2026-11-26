import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARTES = ROOT / "cartes"


def fail(msg):
    print(f"ERREUR: {msg}")
    sys.exit(1)


svgs = sorted(CARTES.glob("*.svg"))
if not svgs:
    fail("aucun SVG dans cartes/")
for s in svgs:
    try:
        ET.parse(s)
    except Exception as e:
        fail(f"SVG invalide {s.name}: {e}")
    print(f"SVG OK {s.name}")

for p in sorted(CARTES.glob("*.png")):
    data = p.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        fail(f"PNG invalide: {p.name}")
    w, h = struct.unpack(">II", data[16:24])
    if w == 0 or h == 0:
        fail(f"PNG dimensions nulles: {p.name}")
    print(f"PNG OK {p.name} {w}x{h}")

for h in sorted(CARTES.glob("*.html")):
    text = h.read_text(encoding="utf-8")
    if 'id="add"' in text and "BEGIN:VCARD" not in text:
        fail(f"{h.name}: bouton vCard présent mais aucun générateur (BEGIN:VCARD)")
    for ref in re.findall(r'(?:href|src)="([^"]+)"', text):
        if ref.startswith(("http://", "https://", "#", "data:", "mailto:")):
            continue
        if ref.lower().endswith((".jpg", ".jpeg")):
            continue
        if not (h.parent / ref).exists() and not (h.parent / (ref + ".html")).exists():
            fail(f"{h.name}: référence locale manquante: {ref}")
    print(f"HTML OK {h.name}")

root_html = ROOT / "index.html"
if root_html.exists():
    text = root_html.read_text(encoding="utf-8")
    for ref in re.findall(r'(?:href|src)="([^"]+)"', text):
        if ref.startswith(("http://", "https://", "#", "data:", "mailto:")):
            continue
        if not (ROOT / ref.rstrip("/")).exists():
            fail(f"index.html: référence locale manquante: {ref}")
    print("HTML OK index.html (racine)")

print("Assets OK")
