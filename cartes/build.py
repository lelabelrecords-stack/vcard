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
    },
]

COMMON = {
    "org": "Le Label Records",
    "email": "lelabel@le-label.org",
    "adr": ";;8 rue Nationale;Nîmes;;30000;France",
    "url_site": "https://le-label.org",
    "url_repo": "https://github.com/lelabelrecords-stack/vcard",
    "linktree": "https://linktr.ee/le.label",
    "bandcamp": "https://lelabelrecords.bandcamp.com/",
    "note": (
        "Le Label Records — label indépendant à Nîmes, co-dirigé par Christophe "
        "Bonnici et Roxane Gire. Émission radio Le Label². 100 % des royalties "
        "nettes de distribution vont aux groupes."
    ),
}


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
        f"ADR;TYPE=work:{COMMON['adr']}",
        f"URL:{COMMON['url_site']}",
        f"URL:{COMMON['url_repo']}",
        f"SOCIALPROFILE;TYPE=linktree:{COMMON['linktree']}",
        f"SOCIALPROFILE;TYPE=bandcamp:{COMMON['bandcamp']}",
        f"NOTE:{COMMON['note']}",
    ]
    if photo_uri:
        mime = "image/png" if photo_uri.startswith("data:image/png") else "image/jpeg"
        lines.append(f"PHOTO;TYPE={mime.split('/')[1].upper()};ENCODING=b:{photo_uri}")
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
  <text x="480" y="330" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="30" fill="__RED__">Un label indépendant,</text>
  <text x="480" y="378" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="30" fill="__RED__">une heure, les morceaux</text>
  <text x="480" y="426" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="30" fill="__RED__">qui le définissent.</text>
  <text x="480" y="500" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="700" font-size="24" letter-spacing="3" fill="__RED__">LE LABEL² — À LA RADIO</text>
  <text x="72" y="762" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" font-size="96" letter-spacing="2" fill="__RED__">__FIRST__</text>
  <text x="72" y="870" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" font-size="96" letter-spacing="2" fill="__RED__">__LAST__</text>
  <text x="72" y="936" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="700" font-size="34" letter-spacing="3" fill="__RED__">__TITLE_UP__ · LE LABEL RECORDS</text>
  <line x1="72" y1="984" x2="1008" y2="984" stroke="__RED__" stroke-width="2"/>
  <text x="72" y="1044" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="32" fill="__RED__">lelabel@le-label.org</text>
  <text x="72" y="1096" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="32" fill="__RED__">le-label.org — linktr.ee/le.label</text>
  <text x="72" y="1148" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="32" fill="__RED__">8 rue Nationale, 30000 Nîmes</text>
  <rect x="72" y="1192" width="936" height="96" fill="__RED__"/>
  <text x="540" y="1252" text-anchor="middle" font-family="Archivo Black, Archivo, Helvetica, Arial, sans-serif" font-size="34" letter-spacing="3" fill="__WHITE__">AJOUTER AUX CONTACTS — .VCF</text>
  <text x="540" y="1308" text-anchor="middle" font-family="Archivo, Helvetica, Arial, sans-serif" font-weight="500" font-size="22" letter-spacing="2" fill="__RED__">github.com/lelabelrecords-stack/vcard</text>
</svg>
"""


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
      .button--ghost { background: var(--white); color: var(--red); margin-top: 10px; }
      .card-foot { display: flex; justify-content: space-between; gap: 12px; margin-top: 18px; font-size: 0.78rem; font-weight: 500; letter-spacing: 0.06em; }
      .card-foot a { color: inherit; }
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
      <p class="tagline">Un label indépendant, une heure, les morceaux qui le définissent — Le Label² à la radio.</p>
      <hr />
      <ul class="contacts">
        <li><a href="mailto:lelabel@le-label.org">lelabel@le-label.org</a></li>
        <li><a href="https://le-label.org">le-label.org</a> — <a href="https://linktr.ee/le.label">linktr.ee/le.label</a></li>
        <li>8 rue Nationale, 30000 Nîmes</li>
      </ul>
      <button class="button" id="add" type="button">Ajouter aux contacts — .vcf</button>
      <a class="button button--ghost" href="__SLUG__.vcf" download="__SLUG__.vcf">Télécharger la vCard (.vcf)</a>
      <div class="card-foot">
        <a href="https://github.com/lelabelrecords-stack/vcard">github.com/lelabelrecords-stack/vcard</a>
        <a href="./">Les deux cartes</a>
      </div>
    </main>
    <script>
      const SLUG = "__SLUG__";
      const LINES = [
        "BEGIN:VCARD",
        "VERSION:4.0",
        "UID:__UID__",
        "FN:__FN__",
        "N:__N__",
        "ORG:Le Label Records",
        "TITLE:__TITLE__",
        "EMAIL;TYPE=work:lelabel@le-label.org",
        "ADR;TYPE=work:;;8 rue Nationale;Nîmes;;30000;France",
        "URL:https://le-label.org",
        "URL:https://github.com/lelabelrecords-stack/vcard",
        "SOCIALPROFILE;TYPE=linktree:https://linktr.ee/le.label",
        "SOCIALPROFILE;TYPE=bandcamp:https://lelabelrecords.bandcamp.com/",
        "NOTE:Le Label Records — label indépendant à Nîmes, co-dirigé par Christophe Bonnici et Roxane Gire. Émission radio Le Label². 100 % des royalties nettes de distribution vont aux groupes.",
        "REV:__REV__"
      ];

      function fold(line) {
        const bytes = new TextEncoder().encode(line);
        if (bytes.length <= 75) return [line];
        const out = [];
        let start = 0, first = true;
        while (start < bytes.length) {
          const limit = first ? 75 : 74;
          let end = Math.min(start + limit, bytes.length);
          while (end < bytes.length && end > start && (bytes[end] & 0xC0) === 0x80) end--;
          const chunk = new TextDecoder().decode(bytes.subarray(start, end));
          out.push(first ? chunk : " " + chunk);
          first = false;
          start = end;
        }
        return out;
      }

      async function photoUri() {
        const img = document.getElementById("photo");
        if (!img || !img.dataset.ok) return null;
        try {
          const res = await fetch(img.getAttribute("src"));
          if (!res.ok) return null;
          const buf = new Uint8Array(await res.arrayBuffer());
          let bin = "";
          for (let i = 0; i < buf.length; i += 8192) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 8192));
          const mime = img.getAttribute("src").endsWith(".png") ? "image/png" : "image/jpeg";
          return "data:" + mime + ";base64," + btoa(bin);
        } catch (e) {
          return null;
        }
      }

      document.getElementById("add").addEventListener("click", async () => {
        const lines = LINES.slice();
        const uri = await photoUri();
        if (uri) {
          lines.push("PHOTO;TYPE=" + (uri.includes("image/png") ? "PNG" : "JPEG") + ";ENCODING=b:" + uri);
        }
        lines.push("END:VCARD");
        const folded = [];
        for (const ln of lines) folded.push(...fold(ln));
        const blob = new Blob([folded.join("\\r\\n") + "\\r\\n"], { type: "text/vcard;charset=utf-8" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = SLUG + ".vcf";
        document.body.appendChild(a);
        a.click();
        setTimeout(() => URL.revokeObjectURL(a.href), 5000);
        a.remove();
      });
    </script>
  </body>
</html>
"""


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
