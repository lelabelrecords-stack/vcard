import sys

MAX_OCTETS = 75


def fail(msg):
    print(f"ERREUR: {msg}")
    sys.exit(1)


def main(path):
    with open(path, "rb") as f:
        raw = f.read()

    if b"\n" in raw.replace(b"\r\n", b""):
        fail("fins de ligne non CRLF detectees")
    lines = raw.split(b"\r\n")
    if lines and lines[-1] == b"":
        lines = lines[:-1]
    for i, line in enumerate(lines, 1):
        if len(line) > MAX_OCTETS:
            fail(f"ligne {i} depasse {MAX_OCTETS} octets ({len(line)})")

    try:
        text_lines = [l.decode("utf-8") for l in lines]
    except UnicodeDecodeError as e:
        fail(f"UTF-8 invalide: {e}")

    if not text_lines or text_lines[0] != "BEGIN:VCARD":
        fail("premiere ligne != BEGIN:VCARD")
    if text_lines[-1] != "END:VCARD":
        fail("derniere ligne != END:VCARD")

    unfolded = []
    for l in text_lines:
        if l[:1] in (" ", "\t") and unfolded:
            unfolded[-1] += l[1:]
        else:
            unfolded.append(l)

    props = {}
    for l in unfolded:
        if ":" not in l:
            fail(f"ligne sans ':' : {l[:40]}")
        name, value = l.split(":", 1)
        prop = name.split(";", 1)[0].upper()
        props.setdefault(prop, []).append(value)

    if props.get("VERSION", [""])[0] != "4.0":
        fail("VERSION:4.0 manquante ou incorrecte")
    for required in ("FN", "UID"):
        if required not in props:
            fail(f"propriete obligatoire manquante: {required}")

    print(f"vCard OK: FN={props['FN'][0]} VERSION={props['VERSION'][0]} ({len(unfolded)} proprietes)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: validate_vcard.py <fichier.vcf>")
    main(sys.argv[1])
