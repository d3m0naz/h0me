#!/usr/bin/env python3
"""Kopiert pool/*.html und pool/<ordner>/*.html nach site/doku/
und ergänzt Kopfzeile, Fuß und die Farben der Website.

localStorage-Aufrufe werden entfernt (Seite speichert nichts im Browser).

Die Originale in pool/ bleiben unverändert. Einfach nach jeder Änderung
im pool erneut ausführen:  python3 tools/build_doku.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "pool", ROOT / "site" / "doku"

STYLE = """<style>
.vlb{--v-bg:#13161a;--v-line:#262c33;--v-ink:#d4d9d0;--v-muted:#7d8791;--v-dim:#535c66;--v-green:#7ee787;--v-violet:#c49bff;--v-cyan:#79c0ff;--v-on:#0d0f11}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]) .vlb{--v-bg:#ecebe4;--v-line:#dddbd2;--v-ink:#2a2f2b;--v-muted:#68706a;--v-dim:#9aa098;--v-green:#2f7d32;--v-violet:#7a46c9;--v-cyan:#1f6fb2;--v-on:#f4f3ee}}
:root[data-theme="light"] .vlb{--v-bg:#ecebe4;--v-line:#dddbd2;--v-ink:#2a2f2b;--v-muted:#68706a;--v-dim:#9aa098;--v-green:#2f7d32;--v-violet:#7a46c9;--v-cyan:#1f6fb2;--v-on:#f4f3ee}
.vlb .tgl{font:inherit;color:var(--v-muted);background:none;border:0;padding:2px 6px;border-radius:4px;cursor:pointer;display:inline-flex;align-items:center}
.vlb .tgl:hover{color:var(--v-green)}
@media (max-width:900px){header.vlb div>a:nth-child(2){margin-left:auto}header.vlb .tgl{order:1;margin-right:-6px}header.vlb div>span{order:2;flex-basis:100%}}  /* mobil: Umschalter neben die Marke */
.vlb{font:12.5px/1.5 ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;background:var(--v-bg);color:var(--v-muted);border-bottom:1px solid var(--v-line)}
.vlb div{max-width:880px;margin:0 auto;padding:9px 24px;display:flex;flex-wrap:wrap;gap:4px 18px;justify-content:space-between;align-items:center}
.vlb a{color:var(--v-ink);text-decoration:none}.vlb a:hover{color:var(--v-green)}
.vlb b{color:var(--v-green);font-weight:400}.vlb s{color:var(--v-dim);text-decoration:none}.vlb i{font-style:normal;color:var(--v-violet)}
.vlb .h{color:var(--v-cyan)}
header.vlb,footer.vlb{margin:0;padding:0;max-width:none}  /* allgemeine header/footer-Regeln der Dokus nicht erben */
footer.vlb-foot{border-top:1px solid var(--v-line);border-bottom:0;margin-top:32px}
.vlb-foot .sess{background:var(--v-green);color:var(--v-on);padding:2px 8px;font-weight:600;margin-right:8px}
@media print{.vlb{display:none}}
</style>"""

# Farben der Dokus an die Website angleichen (Palette aus site/assets/style.css).
# Die Pool-Dokus benennen ihre Variablen unterschiedlich, deshalb werden alle
# bekannten Namen gesetzt. :root:root:root schlägt die Selektoren der Originale.
PAL = {
    "dark": dict(bg="#0d0f11", bg2="#13161a", surface="#161a1e", surface2="#1c2126", line="#262c33",
                 line2="#323a43", ink="#d4d9d0", muted="#7d8791", green="#7ee787", amber="#f0b45a",
                 red="#ff7b72", cyan="#79c0ff", scheme="dark"),
    "light": dict(bg="#f4f3ee", bg2="#ecebe4", surface="#fbfaf6", surface2="#f0efe8", line="#dddbd2",
                  line2="#cfccc1", ink="#2a2f2b", muted="#68706a", green="#2f7d32", amber="#a86400",
                  red="#c4372c", cyan="#1f6fb2", scheme="light"),
}


def theme_vars(c):
    soft = lambda col: f"color-mix(in srgb,{col} 12%,{c['bg']})"
    v = {
        "bg": c["bg"], "surface": c["surface"], "card": c["surface"], "sidebar": c["bg2"],
        "code": c["surface2"], "code-bg": c["surface2"], "soft": c["surface2"],
        "pre-bg": c["surface2"], "pre-text": c["ink"],
        "fg": c["ink"], "ink": c["ink"], "text": c["ink"], "muted": c["muted"],
        "line": c["line2"], "border": c["line2"],
        "accent": c["green"], "accent-soft": soft(c["green"]), "ok": c["green"], "bad": c["red"],
        "warn": c["amber"], "warn-soft": soft(c["amber"]), "warnbg": soft(c["amber"]),
        "warn-bg": soft(c["amber"]), "warn-line": c["amber"],
        "note-bg": soft(c["amber"]), "note-border": c["amber"],
    }
    return "".join(f"--{k}:{val};" for k, val in v.items()) + f"color-scheme:{c['scheme']};"


D, L = theme_vars(PAL["dark"]), theme_vars(PAL["light"])
THEME = ("<style>\n"
         f":root:root:root,:root:root:root[data-theme=\"dark\"]{{{D}}}\n"
         f"@media (prefers-color-scheme: light){{:root:root:root:not([data-theme=\"dark\"]){{{L}}}}}\n"
         f":root:root:root[data-theme=\"light\"]{{{L}}}\n"
         "body{background:var(--bg)!important}\n"
         ".copy{background:var(--surface)!important;color:var(--muted)!important;border-color:var(--line)!important}\n"
         ".copy:hover{color:var(--accent)!important}\n"
         "#theme.theme{display:none!important}\n"  # eigener Umschalter der Ollama-Doku, ersetzt durch assets/theme.js
         "</style>")

HEAD = ('<header class="vlb"><div><a href="{R}" style="text-decoration:none"><b>ai</b><s>@</s><span class="h">oliverheld.com</span><s>$</s></a>'
        '<a href="{R}{BACK}.html">← {BACK}</a><span><i>ki-generiert</i> · von einem menschen geprüft · <i>...for now.</i></span></div></header>')

FOOT = ('<footer class="vlb vlb-foot"><div><span><span class="sess">[oliverheld.com]</span>'
        '<a href="{R}">0:index</a> &nbsp;<a href="{R}ueber-mich.html">1:über-mich</a> &nbsp;<a href="{R}docs.html">2:docs</a> &nbsp;<a href="{R}projekte.html">3:projekte</a> &nbsp;<a href="{R}musik.html">4:musik</a> &nbsp;'
        '<a href="{R}impressum.html">5:impressum</a> &nbsp;<a href="{R}datenschutz.html">6:datenschutz</a></span>'
        '<span>cookies:<b>0</b> tracker:<b>0</b></span></div></footer>')


STORAGE = re.compile(r"try \{[^{}]*localStorage[^{}]*\} catch \(e\) \{\}")


def build(f, out, R, back="docs"):
    html = f.read_text(encoding="utf-8")
    html = STORAGE.sub("", html)
    html = FONTS.sub("", html)  # keine externen Schriften, Fallback auf Systemschriften
    assert "localStorage" not in html and "sessionStorage" not in html, f
    assert not re.search(r'(src|<link[^>]*href)="(https?:)?//', html), f  # externe Links per <a> erlaubt
    html = html.replace("</head>", '<meta name="referrer" content="no-referrer">\n'
                        f'<link rel="icon" href="{R}assets/favicon.svg" type="image/svg+xml">\n'
                        + STYLE + "\n" + THEME + "\n"
                        f'<script src="{R}assets/theme.js"></script>\n</head>', 1)
    html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + HEAD.replace("{R}", R).replace("{BACK}", back), html, count=1)
    html = html.replace("</body>", FOOT.replace("{R}", R) + "\n</body>", 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(out.relative_to(DST.parent))


# Vollbild-Demos: eigene Seite ohne Doku-Kopf, nur Rücklink + Pflichtlinks in der Leiste.
# Datei → (Ziel, Regex, nach dessen Treffer die Leiste eingefügt wird)
DEMOS = {
    "NEON RASTER – Amiga-Style Demo.html": ("demo/neon-raster.html", r'<div id="bar">.*?(?=\n</div>)'),
    "c116-rosette.html": ("demo/c116-rosette.html", r'<header>.*?(?=\n</header>)'),
    "Amiga 2000 · NComm · Nowosibirsk BBS.html": ("demo/a2000-ncomm.html", r'<div class="foot">[^<]*'),
    "AUR-Warnung_ Angriffs-Demo.html": ("demo/aur-warnung.html", r'<div class="foot">[^<]*?(?=\s*</div>)'),
}
# Textkorrekturen beim Kopieren (Originale im pool bleiben unverändert)
REPLACE = [
    ("SONDERN DIREKT AUF DEINEM MAC !!!", "SONDERN DIREKT IN DEINEM BROWSER !!!"),
    ("<b>Ein Zeile reicht:</b>", "<b>Eine Zeile reicht:</b>"),
    ("AUR-Sicherheits-Demo · Simulation · Quellen zu den Vorfällen siehe Begleittext",
     "AUR-Sicherheits-Demo · Simulation"),
]
FONTS = re.compile(r'<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>\n?')
DEMO_BAR = ('<span class="sitebar"><a href="../ueber-mich.html#werdegang">← über mich</a>'
            '<i>ki-generiert</i><a href="../impressum.html">impressum</a>'
            '<a href="../datenschutz.html">datenschutz</a></span>')
DEMO_STYLE = """<style>
.sitebar{display:inline-flex;flex-wrap:wrap;gap:4px 10px;margin-left:10px;font-size:11px;white-space:nowrap}
.sitebar a{color:#7d8791;text-decoration:none}.sitebar a:hover{color:#7ee787}
.sitebar i{font-style:normal;color:#c49bff}
#bar{height:auto!important;min-height:44px;padding:4px 8px}
header .sitebar{margin-left:auto;font-size:12px}
</style>"""


def build_demo(f, out, anchor):
    html = f.read_text(encoding="utf-8")
    html = FONTS.sub("", html)  # keine externen Schriften, Fallback monospace
    for old, new in REPLACE:
        html = html.replace(old, new)
    assert "localStorage" not in html and "sessionStorage" not in html, f
    assert not re.search(r'(src|href)="(https?:)?//', html), f
    html = html.replace("</head>", '<meta name="referrer" content="no-referrer">\n'
                        '<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">\n'
                        + DEMO_STYLE + "\n</head>", 1)
    html, n = re.subn(anchor, lambda m: m.group(0) + "\n  " + DEMO_BAR, html, count=1, flags=re.S)
    assert n == 1, f
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(out.relative_to(DST.parent))


# saubere Dateinamen für Pool-Dokus mit Leerzeichen
NAMES = {"Headscale auf eigenem VPS.html": "headscale-vps.html"}
SKIP = {"headscale-neuer-vps.html"}  # Überarbeitung, nicht veröffentlichen


def main():
    for name, (rel, anchor) in DEMOS.items():
        build_demo(SRC / name, DST.parent / rel, anchor)
    for f in sorted(SRC.glob("*.html")):
        if f.name in DEMOS or f.name in SKIP:
            continue
        build(f, DST / NAMES.get(f.name, f.name), "../")
    for f in sorted(SRC.glob("*/*.html")):
        build(f, DST / f.parent.name / f.name, "../../")


if __name__ == "__main__":
    main()
