#!/usr/bin/env python3
"""Kopiert pool/*.html und pool/<ordner>/*.html nach site/doku/ und ergänzt Kopfzeile und Fuß.

localStorage-Aufrufe werden entfernt (Seite speichert nichts im Browser).

Die Originale in pool/ bleiben unverändert. Einfach nach jeder Änderung
im pool erneut ausführen:  python3 tools/build_doku.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "pool", ROOT / "site" / "doku"

STYLE = """<style>
.vlb{font:12.5px/1.5 ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;background:#13161a;color:#7d8791;border-bottom:1px solid #262c33}
.vlb div{max-width:880px;margin:0 auto;padding:9px 24px;display:flex;flex-wrap:wrap;gap:4px 18px;justify-content:space-between;align-items:center}
.vlb a{color:#d4d9d0;text-decoration:none}.vlb a:hover{color:#7ee787}
.vlb b{color:#7ee787;font-weight:400}.vlb s{color:#535c66;text-decoration:none}.vlb i{font-style:normal;color:#c49bff}
.vlb-foot{border-top:1px solid #262c33;border-bottom:0;margin-top:32px}
.vlb-foot .sess{background:#7ee787;color:#0d0f11;padding:2px 8px;font-weight:600;margin-right:8px}
@media print{.vlb{display:none}}
</style>"""

HEAD = ('<header class="vlb"><div><a href="{R}" style="text-decoration:none"><b>ai</b><s>@</s><span style="color:#79c0ff">oliverheld.com</span><s>$</s></a>'
        '<a href="{R}docs.html">← docs</a><span><i>ki-generiert</i> · von einem menschen geprüft · <i>...for now.</i></span></div></header>')

FOOT = ('<footer class="vlb vlb-foot"><div><span><span class="sess">[oliverheld.com]</span>'
        '<a href="{R}">0:index</a> &nbsp;<a href="{R}ueber-mich.html">1:über-mich</a> &nbsp;<a href="{R}docs.html">2:docs</a> &nbsp;<a href="{R}projekte.html">3:projekte</a> &nbsp;<a href="{R}musik.html">4:musik</a> &nbsp;'
        '<a href="{R}impressum.html">5:impressum</a> &nbsp;<a href="{R}datenschutz.html">6:datenschutz</a></span>'
        '<span>cookies:<b>0</b> tracker:<b>0</b></span></div></footer>')


STORAGE = re.compile(r"try \{[^{}]*localStorage[^{}]*\} catch \(e\) \{\}")


def build(f, out, R):
    html = f.read_text(encoding="utf-8")
    html = STORAGE.sub("", html)
    assert "localStorage" not in html and "sessionStorage" not in html, f
    html = html.replace("</head>", '<meta name="referrer" content="no-referrer">\n'
                        f'<link rel="icon" href="{R}assets/favicon.svg" type="image/svg+xml">\n'
                        + STYLE + "\n</head>", 1)
    html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + HEAD.replace("{R}", R), html, count=1)
    html = html.replace("</body>", FOOT.replace("{R}", R) + "\n</body>", 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(out.relative_to(DST.parent))


# Vollbild-Demos: eigene Seite ohne Doku-Kopf, nur Rücklink + Pflichtlinks in der Leiste.
DEMOS = {"NEON RASTER – Amiga-Style Demo.html": "demo/neon-raster.html"}
DEMO_BAR = ('<span class="sitebar"><a href="../ueber-mich.html#werdegang">← über mich</a>'
            '<i>ki-generiert</i><a href="../impressum.html">impressum</a>'
            '<a href="../datenschutz.html">datenschutz</a></span>')
DEMO_STYLE = """<style>
.sitebar{display:inline-flex;gap:10px;margin-left:10px;font-size:11px}
.sitebar a{color:#7d8791;text-decoration:none}.sitebar a:hover{color:#7ee787}
.sitebar i{font-style:normal;color:#c49bff}
#bar{height:auto!important;min-height:44px;padding:4px 8px}
</style>"""


def build_demo(f, out):
    html = f.read_text(encoding="utf-8")
    html = html.replace("SONDERN DIREKT AUF DEINEM MAC !!!", "SONDERN DIREKT IN DEINEM BROWSER !!!")
    assert "localStorage" not in html and "sessionStorage" not in html, f
    assert not re.search(r'(src|href)="(https?:)?//', html), f
    html = html.replace("</head>", '<meta name="referrer" content="no-referrer">\n'
                        '<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">\n'
                        + DEMO_STYLE + "\n</head>", 1)
    html = re.sub(r'(<div id="bar">.*?)(\n</div>)', lambda m: m.group(1) + "\n  " + DEMO_BAR + m.group(2),
                  html, count=1, flags=re.S)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(out.relative_to(DST.parent))


def main():
    for name, rel in DEMOS.items():
        build_demo(SRC / name, DST.parent / rel)
    for f in sorted(SRC.glob("*.html")):
        if f.name in DEMOS:
            continue
        build(f, DST / f.name, "../")
    for f in sorted(SRC.glob("*/*.html")):
        build(f, DST / f.parent.name / f.name, "../../")


if __name__ == "__main__":
    main()
