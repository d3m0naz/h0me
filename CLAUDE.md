# ai@oliverheld.com

Statische Website (HTML/CSS, kein Build-Framework). Quelle in `site/`, live auf
https://oliverheld.com über GitHub Pages (Repo `d3m0naz/h0me`, Branch `gh-pages`).

## Harte Regeln

- **Keine personenbezogenen Daten im Klartext** (Name, Anschrift, Mail) in HTML, Repo oder Commits.
  Das Impressum ist nur `site/assets/impressum.svg` aus Glyphenpfaden (siehe unten).
  Vor jedem Commit mit `command grep -ri` nach Name/Adresse/Mail suchen.
- **Keine Cookies, kein localStorage/sessionStorage, keine externen Ressourcen**
  (keine Fonts, kein CDN, keine Embeds). Bilder liegen lokal in `site/assets/`.
- **„nichts klauen und verlinken“**: fremde Inhalte nur als Link, keine Embeds,
  keine fremden Screenshots/Thumbnails, keine Songtexte; eigener Text.
  Neben Links mit Cookies (z. B. YouTube) einen Hinweis setzen.
  Jeden neuen externen Linkzieltyp in `site/datenschutz.html` Punkt 5 ergänzen.
- **KI-Herkunft offenlegen**: Inhalte sind größtenteils KI-generiert („...for now.“).
  Footer auf allen Seiten: `88% ai (inkl. slop)`.
- **Design bleibt immer eingehalten**: geekig, Terminal-Optik, unaufdringlich.
  Neue Inhalte immer aus bestehenden Bausteinen bauen (`.sh`-Prompt-Überschrift,
  `.intro`, `.term`-Fenster, `.inc`-Karten, `.hist`-Liste, `.btw`-Badges, go-retro-Buttons)
  und in Dark, Light und Mobil per Screenshot prüfen.
- **Commits** nur mit Identität `d3m0naz` / `11614755+d3m0naz@users.noreply.github.com`.
- **Erst nach „publish“ / „veröffentlichen“ deployen.** Vorher lokal mit `open` zeigen.

## Namen

- Marke oben links und in den Titeln: `ai@oliverheld.com` (`… · ai@oliverheld.com`).
- Name im Text, neofetch (`oliverheld.com@h0me`), finger (`Login: oliverheld.com`)
  und tmux-Footer (`[oliverheld.com]`): `oliverheld.com`.

## Seiten

- `index.html`: Landing (Hero, neofetch, `#themen`-Karten, `#wie`).
- `ueber-mich.html`: finger, `#werdegang` (C116 → … → Arch-Derivat „btw“), `#damals`.
- `docs.html`: `.inc`-Karten auf `doku/*`. Neue Doku → Karte hier und Peek/Zähler
  der Docs-Karte in `index.html` anpassen.
- `projekte.html`: Repo-Karten, Thumbnails lokal in `assets/thumbs/`.
- `musik.html`, `impressum.html`, `datenschutz.html` (geht von Hosting auf GitHub Pages aus).
- Stil in `site/assets/style.css`. Innere Links in `.inc`-Karten brauchen
  `position:relative; z-index:1` (die Überschrift legt einen Overlay-Link über die Karte).

## Dokus und Demos aus `pool/`

`python3 tools/build_doku.py` erzeugt aus `pool/`:

- `pool/*.html` → `site/doku/`, `pool/<x>/*.html` → `site/doku/<x>/` mit Site-Kopf/-Fuß.
  localStorage-Aufrufe und Google-Fonts-Links werden entfernt (Asserts gegen Storage und
  externe `src`/`<link>`; externe `<a>`-Links sind erlaubt → datenschutz §5 prüfen).
  Pool-Dateien mit Leerzeichen im Namen bekommen über das Dict `NAMES` einen sauberen
  Ausgabenamen (z. B. `headscale-vps.html`).
- Vollbild-Demos (Dict `DEMOS`) → `site/demo/` ohne Doku-Kopf, mit kleiner Linkleiste
  (← über mich · ki-generiert · impressum · datenschutz). Google-Fonts-Links werden
  entfernt, Asserts gegen externe URLs und Storage. Textkorrekturen über die
  `REPLACE`-Liste; die Originale in `pool/` bleiben unverändert.
- Demos sind im Werdegang als `<a class="btw demo" href="demo/…">▶ demo</a>` verlinkt:
  - C116 → `demo/c116-rosette.html`
  - Amiga 500 → `demo/neon-raster.html`
  - Amiga 2000 → `demo/a2000-ncomm.html`
  - Arch-Derivat (Rolling Release) → `demo/aur-warnung.html`
- Neue Demo vorher komplett lesen: externe Loads, Storage, echte Namen/Nummern, Schadcode.

## Impressum

`tools/impressum/make_svg.py` (fontTools, JetBrains Mono) rendert
`tools/impressum/impressum.txt` (**gitignored**, enthält die Klardaten; Vorlage
`impressum.example.txt`) nach `site/assets/impressum.svg`, nur `<path>`, kein Text.
fontTools braucht eine venv (`python3 -m venv … && pip install fonttools`).
Nach Änderung `width`/`height` des `<img>` in `site/impressum.html` prüfen.
Das SVG hat feste helle Farben, die `.imprint`-Box ist in beiden Themes dunkel.

## Deploy

`tools/deploy.sh` macht es im Prinzip. Aus der Claude-Sandbox scheitert SSH-Push, deshalb:

```sh
git add site tools/build_doku.py && git commit -m "…"
git remote set-url origin https://github.com/d3m0naz/h0me.git
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin main
git branch -f gh-pages "$(git subtree split --prefix site 2>/dev/null)"
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push -f origin gh-pages
git remote set-url origin git@github.com:d3m0naz/h0me.git
```

Danach warten, bis `gh api repos/d3m0naz/h0me/pages/builds/latest --jq .status` `built`
liefert (baut Pages nicht, `gh api -X POST repos/d3m0naz/h0me/pages/builds`), und live mit
`curl "https://oliverheld.com/…?v=$RANDOM"` prüfen (CDN-Cache hängt nach).
Keine Action, weil dem gh-Token der `workflow`-Scope fehlt.

DNS bei All-Inkl: Apex A auf 185.199.108–111.153, `www` CNAME `d3m0naz.github.io`,
Custom Domain über `site/CNAME`, HTTPS erzwungen.

## Werkzeuge

- Screenshots: `tools/shot/shot.swift` (WKWebView, mit `swiftc` kompilieren),
  `shot <datei|url> <out.png> <w> <h> [dark]`. Zum Scrollen eine Kopie mit
  `<script>scrollTo(…)</script>` nehmen. Canvas-/rAF-Inhalte erscheinen evtl. nicht.
- `grep` ist auf `rg` aliasiert (respektiert .gitignore) → `command grep` nutzen.
- Kein nacktes `sleep 60`, stattdessen `until …; do sleep 5; done`.
