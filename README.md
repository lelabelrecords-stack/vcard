# vCard — Le Label Records

Carte de visite du **Le Label Records** au format [vCard 4.0 (RFC 6350)](https://www.rfc-editor.org/rfc/rfc6350) : [le-label-records.vcf](le-label-records.vcf).

- Dépôt GitHub : [lelabelrecords-stack/vcard](https://github.com/lelabelrecords-stack/vcard)
- Site : [https://le-label.org](https://le-label.org)

## Contenu de la vCard

- Nom / organisation : Le Label Records (label indépendant, Nîmes)
- E-mails : `le.label.contact@gmail.com` (contact) et `lelabel@le-label.org` (démos)
- Adresse : 8 rue Nationale, 30000 Nîmes, France
- URLs : site `le-label.org` et dépôt GitHub `lelabelrecords-stack/vcard`
- Réseaux : Bandcamp, Linktree, YouTube

## Import du fichier .vcf

- **iOS / macOS** : ouvrir `le-label-records.vcf` → « Ajouter à un contact »
- **Android** : Contacts → Importer → sélectionner le fichier `.vcf`
- **Thunderbird / Outlook** : importer le fichier `.vcf` dans le carnet d'adresses

Le fichier utilise des fins de ligne CRLF et des lignes pliées à 75 octets, conformément au RFC 6350.

## Cartes de visite digitales (`cartes/`)

Cartes minimalistes de **Christophe Bonnici** (co-fondateur) et **Roxane Gire** (co-fondatrice), aux couleurs du site (`#db0000` sur blanc, bordures 1 px, Archivo / Archivo Black, logo contour) :

```
cartes/
├── index.html                  # les deux cartes
├── christophe-bonnici.html     # carte digitale + bouton « Ajouter aux contacts »
├── roxane-gire.html
├── christophe-bonnici.svg/.png # carte statique (1080×1350, PNG 2160×2700)
├── roxane-gire.svg/.png
├── christophe-bonnici.vcf      # vCard 4.0 importable
├── roxane-gire.vcf
├── assets/logo-contour-rouge.svg
├── fonts/*.woff2               # Archivo auto-hébergée
└── build.py                    # régénère .svg/.html/.vcf
```

Le bouton **« Ajouter aux contacts — .vcf »** de chaque page HTML génère côté client une vCard 4.0 (CRLF, lignes pliées à 75 octets) et la télécharge : sur smartphone, le `.vcf` s'ouvre dans l'app Contacts pour un import en un geste. Si `cartes/<slug>.jpg` (ou `.png`) est présent, la photo est embarquée dans la vCard (`PHOTO;ENCODING=b`) et affichée sur la carte.

### Ajouter les photos

1. Déposer `cartes/christophe-bonnici.jpg` et `cartes/roxane-gire.jpg`.
2. `python3 cartes/build.py` → régénère `.vcf` (avec `PHOTO`), `.svg`, `.html`.
3. Re-rendre les PNG (2×) depuis les SVG avec n'importe quel rasteriseur SVG (rsvg-convert, Inkscape, sharp…).

## CI

`.github/workflows/validate-vcard.yml` valide à chaque PR et push sur `main` :
- tous les `.vcf` (CRLF, lignes ≤ 75 octets, `BEGIN:VCARD`/`VERSION:4.0`/`FN`/`UID`/`END:VCARD`) via `.github/scripts/validate_vcard.py` ;
- les assets des cartes (SVG bien formés, PNG valides, références locales des HTML) via `.github/scripts/validate_assets.py`.
