#!/usr/bin/env python3
"""Génère les cartes de visite digitales (SVG, HTML) et les fichiers .vcf.

Usage : python3 cartes/build.py
- cartes/<slug>.svg / .html / .vcf sont régénérés à chaque exécution.
- Si cartes/<slug>.jpg (ou .png) existe, la photo est embarquée dans le .vcf
  (propriété PHOTO, base64) et affichée sur la carte SVG/HTML.
"""

import base64
import sys
from datetime import datetime, timezone
from pathlib import Path

CARTES = Path(__file__).resolve().parent
RED = "#db0000"
WHITE = "#ffffff"

REV = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

PEOPLE = [
    {
        "slug": "christophe-bonnici",
        "fn": "Christophe Bonnici",
        "first": "Christophe",
        "last": "Bonnici",
        "n": "Bonnici;Christophe;;;",
        "title": "Co-fondateur",
        "initials": "CB",
        "uid": "urn:uuid:399993ac-3b79-4282-955d-543d02efde93",
        "tel_display": "06 20 50 14 07",
        "tel_e164": "+33620501407",
    },
    {
        "slug": "roxane-gire",
        "fn": "Roxane Gire",
        "first": "Roxane",
        "last": "Gire",
        "n": "Gire;Roxane;;;",
        "title": "Co-fondatrice",
        "initials": "RG",
        "uid": "urn:uuid:10f6ac36-54d5-427e-a705-ebe10fdd3d8d",
        "tel_display": "06 99 04 47 01",
        "tel_e164": "+33699044701",
    },
]

VERBATIM = 'ᖇᗴᑕᗝᖇᗪᔕ ᒪᗩᗷᗴᒪ Ꭵᑎ ᑎîᗰᗴᔕ « ᒪᗩ ᗰᑌᔕᎥɊᑌᗴ ᑎ’ᗴᔕ丅 ᑭᗩᔕ ᔕᎥᗠᑭᒪᗰᗴᑎ丅 ᑌᑎᗴ ᕼᎥᔕ丅ᗝᎥᖇᗴ ᗪᗴ ᔕᗝᑎᔕ, ᑕ’ᗴᔕ丅 ᗩᐯᗩᑎ丅 丅ᗝᑌ丅 ᑌᑎᗴ ᗩᐯᗴᑎᗝᑌᖇᗴ ᑭᖇᗝᖴᗝᑎᗠéᗰᗴᑎ丅 ᕼᑌᗠᗩᎥᑎᗴ »'

RADIO = (
    "Le Label\u00b2 \u00e0 la radio : Rayvox (un lundi par mois, 20h, en direct) \u00b7 "
    "Raje Radio (mar. 20h \u00b7 102.5 FM N\u00eemes / 90.3 FM Avignon) \u00b7 "
    "Radio Alliance+ (jeu. 19h \u00b7 103.2 FM N\u00eemes + DAB+)"
)
RADIO_LINKS = [
    ("Rayvox", "https://www.rayvox.org/podcastFilter?e=70&t=&l=1"),
    ("Raje Radio", "https://raje.fr/programmes/le-label2"),
    ("Radio Alliance+", "https://radioallianceplus.fr/show/le-label-au-carre/"),
]

COMMON = {
    "org": "Le Label Records",
    "email": "lelabel@le-label.org",
    "adr": ";;8 rue Nationale;N\u00eemes;;30000;France",
    "url_site": "https://le-label.org",
    "linktree": "https://linktr.ee/le.label",
    "bandcamp": "https://lelabelrecords.bandcamp.com/",
    "note": VERBATIM + " " + RADIO,
}


def esc(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )



def fold(line: str) -> list:
    data = line.encode("utf-8")
    if len(data) <= 75:
        return [line]
    out, start, first = [], 0, True
    while start < len(data):
        limit = 75 if first else 74
        end = min(start + limit, len(data))
        while end < len(data) and end > start and (data[end] & 0xC0) == 0x80:
            end -= 1
        chunk = data[start:end].decode("utf-8")
        out.append(chunk if first else " " + chunk)
        first = False
        start = end
    return out


def vcf_lines(p: dict, photo_uri: str | None) -> list:
    lines = [
        "BEGIN:VCARD",
        "VERSION:4.0",
        f"UID:{p['uid']}",
        f"FN:{p['fn']}",
        f"N:{p['n']}",
        f"ORG:{COMMON['org']}",
        f"TITLE:{p['title']}",
        f"EMAIL;TYPE=work:{COMMON['email']}",
        f"TEL;TYPE=CELL,VOICE:{p['tel_e164']}",
        f"ADR;TYPE=work:{COMMON['adr']}",
        f"URL:{COMMON['url_site']}",
        f"SOCIALPROFILE;TYPE=linktree:{COMMON['linktree']}",
        f"SOCIALPROFILE;TYPE=bandcamp:{COMMON['bandcamp']}",
        f"NOTE:{esc(COMMON['note'])}",
    ]
    if photo_uri:
        mime = "png" if photo_uri.startswith("data:image/png") else "jpeg"
        b64 = photo_uri.split("base64,", 1)[1]
        lines.append(f"PHOTO;TYPE={mime.upper()};ENCODING=b:{b64}")
    lines += [f"REV:{REV}", "END:VCARD"]
    return lines


def write_vcf(p: dict) -> None:
    photo_uri = None
    for ext, mime in ((".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".png", "image/png")):
        f = CARTES / f"{p['slug']}{ext}"
        if f.exists():
            photo_uri = f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode("ascii")
            break
    lines = vcf_lines(p, photo_uri)
    folded = []
    for ln in lines:
        folded.extend(fold(ln))
    out = CARTES / f"{p['slug']}.vcf"
    out.write_bytes("\r\n".join(folded).encode("utf-8") + b"\r\n")
    print(f"vcf: {out.name} (photo={'oui' if photo_uri else 'non'})")


def logo_inner() -> str:
    import re

    logo = (CARTES / "assets" / "logo-contour-rouge.svg").read_text(encoding="utf-8")
    logo = re.sub(r"^\s*<\?xml[^>]*\?>", "", logo)
    return logo.split(">", 1)[1].rsplit("</svg>", 1)[0]


SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">
  <rect width="1080" height="1350" fill="__WHITE__"/>
  <rect x="28" y="28" width="1024" height="1294" fill="none" stroke="__RED__" stroke-width="3"/>
  <g transform="translate(72,64) scale(0.144)">__LOGO__</g>
  <text x="1008" y="112" text-anchor="end" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" font-size="34" letter-spacing="8" fill="__RED__">LE LABEL RECORDS</text>
  <text x="1008" y="154" text-anchor="end" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="700" font-size="24" letter-spacing="5" fill="__RED__">LABEL INDÉPENDANT — NÎMES</text>
  <line x1="72" y1="220" x2="1008" y2="220" stroke="__RED__" stroke-width="2"/>
  <rect x="72" y="264" width="360" height="360" fill="__WHITE__" stroke="__RED__" stroke-width="3"/>
__PHOTO__
__TAGLINE__
  <text x="480" y="500" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="700" font-size="24" letter-spacing="3" fill="__RED__">LE LABEL² — À LA RADIO</text>
  <text x="480" y="542" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="21" fill="__RED__">Rayvox — un lundi par mois, 20h, en direct</text>
  <text x="480" y="578" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="21" fill="__RED__">Raje Radio — mar. 20h · 102.5 / 90.3 FM</text>
  <text x="480" y="614" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="21" fill="__RED__">Radio Alliance+ — jeu. 19h · 103.2 FM + DAB+</text>
  <text x="72" y="762" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" font-size="96" letter-spacing="2" fill="__RED__">__FIRST__</text>
  <text x="72" y="870" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" font-size="96" letter-spacing="2" fill="__RED__">__LAST__</text>
  <text x="72" y="936" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="700" font-size="34" letter-spacing="3" fill="__RED__">__TITLE_UP__ · LE LABEL RECORDS</text>
  <line x1="72" y1="984" x2="1008" y2="984" stroke="__RED__" stroke-width="2"/>
  <text x="72" y="1036" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="32" fill="__RED__">lelabel@le-label.org</text>
  <text x="72" y="1082" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="32" fill="__RED__">__TEL_DISPLAY__</text>
  <text x="72" y="1128" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="32" fill="__RED__">le-label.org — linktr.ee/le.label</text>
  <text x="72" y="1174" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="32" fill="__RED__">8 rue Nationale, 30000 Nîmes</text>
  <rect x="72" y="1196" width="936" height="96" fill="__RED__"/>
  <text x="540" y="1256" text-anchor="middle" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" font-size="34" letter-spacing="3" fill="__WHITE__">AJOUTER À MES CONTACTS</text>
</svg>
"""


VERBATIM_LATIN = (
    "RECORDS LABEL IN N\u00ceMES \u00ab LA MUSIQUE N\u2019EST PAS SIMPLEMENT UNE "
    "HISTOIRE DE SENS, C\u2019EST AVANT TOUT UNE AVENTURE HUMAINE \u00bb"
)


def tagline_svg() -> str:
    import textwrap as _tw

    lines = _tw.wrap(VERBATIM_LATIN, width=38)
    out = []
    for i, ln in enumerate(lines[:4]):
        y = 332 + i * 38
        out.append(
            f'  <text x="480" y="{y}" font-family="Archivo, Helvetica, Arial, sans-serif" '
            f'font-weight="500" font-size="24" fill="{RED}">{ln}</text>'
        )
    return "\n".join(out)


def write_svg(p: dict) -> None:
    photo = None
    for ext in (".jpg", ".jpeg", ".png"):
        if (CARTES / f"{p['slug']}{ext}").exists():
            photo = f"{p['slug']}{ext}"
            break
    if photo:
        block = (
            f'  <image x="75" y="267" width="354" height="354" '
            f'preserveAspectRatio="xMidYMid slice" href="{photo}"/>'
        )
    else:
        block = (
            f'  <text x="252" y="500" text-anchor="middle" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" '
            f'font-size="140" fill="{RED}">{p["initials"]}</text>'
        )
    svg = (
        SVG_TEMPLATE.replace("__WHITE__", WHITE)
        .replace("__RED__", RED)
        .replace("__LOGO__", logo_inner())
        .replace("__PHOTO__", block)
        .replace("__FIRST__", p["first"].upper())
        .replace("__LAST__", p["last"].upper())
        .replace("__TITLE_UP__", p["title"].upper())
        .replace("__TEL_DISPLAY__", p["tel_display"])
        .replace("__TAGLINE__", tagline_svg())
    )
    out = CARTES / f"{p['slug']}.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"svg: {out.name} (photo={'oui' if photo else 'placeholder ' + p['initials']})")


HTML_TEMPLATE = """<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="color-scheme" content="light" />
    <meta name="theme-color" content="#db0000" />
    <title>__FN__ — Le Label Records</title>
    <meta name="description" content="Carte de visite digitale de __FN__, __TITLE__ du Le Label Records (Nîmes). Bouton pour importer la vCard (.vcf) dans les contacts." />
    <style>
      @font-face { font-family: 'Archivo'; src: url('fonts/archivo-latin-400-normal.woff2') format('woff2'); font-weight: 400; font-style: normal; font-display: swap; }
      @font-face { font-family: 'Archivo'; src: url('fonts/archivo-latin-500-normal.woff2') format('woff2'); font-weight: 500; font-style: normal; font-display: swap; }
      @font-face { font-family: 'Archivo'; src: url('fonts/archivo-latin-700-normal.woff2') format('woff2'); font-weight: 700; font-style: normal; font-display: swap; }
      @font-face { font-family: 'Archivo Black'; src: url('fonts/archivo-black-latin-400-normal.woff2') format('woff2'); font-weight: 400; font-style: normal; font-display: swap; }
      :root { --red: #db0000; --white: #ffffff; }
      * { box-sizing: border-box; }
      body { margin: 0; background: var(--white); color: var(--red); font-family: 'Archivo', 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.5; display: flex; justify-content: center; padding: 24px 16px; }
      .card { width: 100%; max-width: 480px; border: 2px solid var(--red); padding: 24px; }
      .card-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
      .card-head img { width: 56px; height: auto; display: block; }
      .card-head .brand { text-align: right; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.18em; text-transform: uppercase; line-height: 1.6; }
      hr { border: 0; border-top: 2px solid var(--red); margin: 20px 0; }
      .photo { position: relative; width: 100%; aspect-ratio: 1 / 1; border: 2px solid var(--red); overflow: hidden; margin: 0 0 20px; }
      .photo img { width: 100%; height: 100%; object-fit: cover; display: block; position: relative; z-index: 1; }
      .photo .mono { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-family: 'Archivo Black', 'Archivo', sans-serif; font-size: 6rem; }
      h1 { font-family: 'Archivo Black', 'Archivo', sans-serif; font-weight: 400; font-size: 2.4rem; line-height: 1.1; text-transform: uppercase; margin: 0 0 6px; letter-spacing: 0.02em; }
      .role { font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; font-size: 0.85rem; margin: 0 0 4px; }
      .tagline { font-weight: 500; margin: 0; }
      ul.contacts { list-style: none; padding: 0; margin: 0; font-size: 1.02rem; font-weight: 500; }
      ul.contacts li { padding: 10px 0; border-top: 1px solid var(--red); overflow-wrap: anywhere; }
      ul.contacts li:last-child { border-bottom: 1px solid var(--red); }
      ul.contacts a { color: inherit; text-decoration: none; }
      ul.contacts a:hover { text-decoration: underline; }
      .button { display: inline-flex; align-items: center; justify-content: center; width: 100%; height: 50px; padding: 0 25px; border: 1px solid var(--red); border-radius: 0; background: var(--red); color: var(--white); font: inherit; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; text-decoration: none; margin-top: 20px; }
      .button:hover { text-decoration: underline; }
    </style>
  </head>
  <body>
    <main class="card">
      <div class="card-head">
        <img src="assets/logo-contour-rouge.svg" alt="Logo contour Le Label Records" />
        <p class="brand">Le Label Records<br />Label indépendant — Nîmes</p>
      </div>
      <hr />
      <div class="photo">
        <div class="mono" id="mono">__INITIALS__</div>
        <img id="photo" src="__SLUG__.jpg" alt="Photo de __FN__" onload="this.dataset.ok='1';document.getElementById('mono').style.display='none'" onerror="this.remove()" />
      </div>
      <h1>__FIRST__<br />__LAST__</h1>
      <p class="role">__TITLE__ · Le Label Records</p>
      <p class="tagline">__VERBATIM__</p>
      <hr />
      <ul class="contacts">
        <li><a href="mailto:lelabel@le-label.org">lelabel@le-label.org</a></li>
        <li><a href="tel:__TEL_E164__">__TEL_DISPLAY__</a></li>
        <li><a href="https://le-label.org">le-label.org</a> — <a href="https://linktr.ee/le.label">linktr.ee/le.label</a></li>
        <li>8 rue Nationale, 30000 Nîmes</li>
        <li>__RADIO_HTML__</li>
      </ul>
      <a class="button" href="__SLUG__.vcf" download="__SLUG__.vcf">Ajouter à mes contacts</a>
    </main>
  </body>
</html>
"""


def radio_html() -> str:
    parts = []
    for label, url in RADIO_LINKS:
        parts.append(f'<a href="{url}">{label}</a>')
    slots = ["un lundi par mois, 20h, en direct", "mar. 20h \u00b7 102.5 / 90.3 FM", "jeu. 19h \u00b7 103.2 FM + DAB+"]
    bits = [f"{a} ({d})" for a, d in zip(parts, slots)]
    return "Le Label\u00b2 \u00e0 la radio : " + " \u00b7 ".join(bits)


def write_html(p: dict) -> None:
    html = (
        HTML_TEMPLATE.replace("__SLUG__", p["slug"])
        .replace("__FN__", p["fn"])
        .replace("__FIRST__", p["first"])
        .replace("__LAST__", p["last"])
        .replace("__TITLE__", p["title"])
        .replace("__INITIALS__", p["initials"])
        .replace("__UID__", p["uid"])
        .replace("__N__", p["n"])
        .replace("__REV__", REV)
        .replace("__TEL_E164__", p["tel_e164"])
        .replace("__TEL_DISPLAY__", p["tel_display"])
        .replace("__VERBATIM__", VERBATIM)
        .replace("__NOTE_ESC__", esc(COMMON["note"]))
        .replace("__RADIO_HTML__", radio_html())
    )
    out = CARTES / f"{p['slug']}.html"
    out.write_text(html, encoding="utf-8")
    print(f"html: {out.name}")


def main() -> None:
    for p in PEOPLE:
        write_vcf(p)
        write_svg(p)
        write_html(p)


if __name__ == "__main__":
    sys.exit(main())
