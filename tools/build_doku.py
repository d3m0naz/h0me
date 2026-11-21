#!/usr/bin/env python3
"""Kopiert pool/*.html nach site/doku/ und ergänzt Kopfzeile und Fuß.

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

HEAD = ('<header class="vlb"><div><span><b>ai</b><s>@</s><span style="color:#79c0ff">0liver4eld.com</span><s>$</s></span>'
        '<span><i>ki-generiert</i> · von einem menschen geprüft · <i>...for now.</i></span></div></header>')

FOOT = ('<footer class="vlb vlb-foot"><div><span><span class="sess">[0liver4eld]</span>'
        '<a href="../">0:index</a> &nbsp;<a href="../impressum.html">1:impressum</a> &nbsp;'
        '<a href="../datenschutz.html">2:datenschutz</a></span>'
        '<span>cookies:<b>0</b> tracker:<b>0</b></span></div></footer>')


def main():
    DST.mkdir(parents=True, exist_ok=True)
    for f in sorted(SRC.glob("*.html")):
        html = f.read_text(encoding="utf-8")
        html = html.replace("</head>", '<meta name="referrer" content="no-referrer">\n'
                            '<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">\n'
                            + STYLE + "\n</head>", 1)
        html = re.sub(r"(<body[^>]*>)", r"\1\n" + HEAD, html, count=1)
        html = html.replace("</body>", FOOT + "\n</body>", 1)
        (DST / f.name).write_text(html, encoding="utf-8")
        print("doku/" + f.name)


if __name__ == "__main__":
    main()
