#!/usr/bin/env python3
"""Rendert das Impressum als SVG, in dem jeder Buchstabe ein Pfad ist.

Im Ergebnis steht kein einziges Textzeichen: kein <text>, keine Metadaten,
kein Titel mit Klarnamen. Crawler und E-Mail-Harvester finden nichts zum
Kopieren. Menschen lesen es ganz normal.

Aufruf:
    pip install fonttools
    python3 tools/impressum/make_svg.py            # liest impressum.txt
    python3 tools/impressum/make_svg.py daten.txt  # andere Quelldatei

Format der Quelldatei:
    # Überschrift      -> fett, etwas größer
    normale Zeile      -> normal
    (Leerzeile)        -> Abstand

Die Quelldatei enthält deine Klardaten und gehört NICHT ins Repo
(steht in .gitignore). Ins Repo kommt nur das erzeugte SVG.
"""
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "impressum.txt"
OUT = ROOT / "site" / "assets" / "impressum.svg"

SIZE_BODY = 15
SIZE_HEAD = 16
LINE = 24
GAP = 12
PAD = 24


class Face:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    def line(self, text, x, y, size):
        """Gibt (Pfaddaten, Breite) für eine Zeile zurück."""
        s = size / self.upm
        parts = []
        for ch in text:
            name = self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))
            pen = SVGPathPen(self.glyphs)
            self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
            d = pen.getCommands()
            if d:
                parts.append(d)
            x += self.hmtx[name][0] * s
        return " ".join(parts), x


def r(d):
    # Koordinaten auf 1 Nachkommastelle kürzen -> kleinere Datei
    out, num = [], ""
    for c in d + " ":
        if c in "0123456789.-":
            num += c
            continue
        if num:
            v = round(float(num), 1)
            out.append(str(int(v)) if v == int(v) else str(v))
            num = ""
        out.append(c)
    return "".join(out).strip()


def main():
    if not SRC.exists():
        sys.exit(f"Quelldatei fehlt: {SRC}\nVorlage: {HERE / 'impressum.example.txt'}")
    regular = Face(HERE / "fonts" / "JetBrainsMono-Regular.ttf")
    bold = Face(HERE / "fonts" / "JetBrainsMono-Bold.ttf")

    heads, body = [], []
    y, width = PAD - 8, 0
    first = True
    for raw in SRC.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line:
            y += GAP
            continue
        if line.startswith("# "):
            if not first:
                y += GAP
            y += LINE
            d, w = bold.line(line[2:], PAD, y, SIZE_HEAD)
            heads.append(r(d))
        else:
            y += LINE
            d, w = regular.line(line, PAD, y, SIZE_BODY)
            body.append(r(d))
        width = max(width, w)
        first = False

    W, H = int(width + PAD), int(y + PAD)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">
<style>
.h{{fill:#3d7a2a}}.b{{fill:#1d2125}}
@media (prefers-color-scheme:dark){{.h{{fill:#7ee787}}.b{{fill:#d4d9d0}}}}
</style>
<path class="h" d="{' '.join(heads)}"/>
<path class="b" d="{' '.join(body)}"/>
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"geschrieben: {OUT.relative_to(ROOT)}  ({W}x{H}px, {len(svg)//1024} KB)")


if __name__ == "__main__":
    main()
