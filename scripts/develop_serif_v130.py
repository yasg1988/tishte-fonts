#!/usr/bin/env python3
"""Apply the v0.130 service numeral and symbol system at fixed advances."""

from __future__ import annotations

import json
import sys

import fontforge


DIGITS = tuple(("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"))
DELIMITERS = (
    "parenleft", "parenright", "bracketleft", "bracketright", "braceleft", "braceright",
    "guillemotleft", "guillemotright",
)
HORIZONTAL_SIGNS = (
    "hyphen", "endash", "emdash", "underscore", "plus", "equal", "less", "greater",
    "plusminus", "multiply", "divide", "approxequal", "notequal", "lessequal", "greaterequal",
)
DIRECTIONAL_SIGNS = (
    "slash", "backslash", "bar", "arrowleft", "arrowup", "arrowright", "arrowdown", "arrowboth",
)
OFFICIAL_SIGNS = (
    "dollar", "percent", "ampersand", "cent", "sterling", "yen", "Euro", "uni20BD",
    "uni2116", "section", "paragraph", "copyright", "registered", "trademark", "perthousand",
)
PUNCTUATION = (
    "exclam", "quotedbl", "quotesingle", "asterisk", "comma", "period", "colon", "semicolon",
    "question", "at", "quotedblleft", "quotedblbase", "dagger", "daggerdbl", "bullet", "ellipsis",
    "uni00B7", "uni203B", "degree",
)
SCIENTIFIC_SIGNS = (
    "uni2206", "summation", "radical", "infinity",
)


def reshape(glyph, sx: float, sy: float, cut: int = 0, italic: bool = False) -> bool:
    if not glyph.isWorthOutputting() or not len(glyph.foreground):
        return False
    width = glyph.width
    x_min, y_min, x_max, y_max = glyph.boundingBox()
    span = x_max - x_min
    height = y_max - y_min
    if span <= 0 or height <= 0:
        return False
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    outer = span * 0.06
    layer = glyph.foreground
    changed = False
    for contour in layer:
        for point in contour:
            old_x, old_y = point.x, point.y
            point.x = round(cx + (point.x - cx) * sx)
            point.y = round(cy + (point.y - cy) * sy)
            if cut and -8 <= old_y <= 62 and (old_x <= x_min + outer or old_x >= x_max - outer):
                point.y += cut + (5 if italic and old_x >= x_max - outer else 0)
            changed |= (point.x, point.y) != (old_x, old_y)
    if changed:
        glyph.setLayer(layer, glyph.activeLayer)
        glyph.width = width
        glyph.ttinstrs = b""
    return changed


def apply_group(font, names, sx: float, sy: float, cut: int, italic: bool, changed: set[str]) -> None:
    for name in names:
        if name in font and reshape(font[name], sx=sx, sy=sy, cut=cut, italic=italic):
            changed.add(name)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: develop_serif_v130.py INPUT.sfd OUTPUT.sfd VERSION")
    source, output, version = sys.argv[1:]
    font = fontforge.open(source)
    italic = "Italic" in font.fontname
    bold = "Bold" in font.fontname
    changed: set[str] = set()

    # Tabular figures gain a broad, low service rhythm while retaining their
    # exact Times advances. Outside feet follow the capital terminal system.
    apply_group(font, DIGITS, 1.020 if bold else 1.026, 0.985, 32 if bold else 28, italic, changed)
    # Brackets and quotation delimiters open visibly around text.
    apply_group(font, DELIMITERS, 1.055, 0.985, 0, italic, changed)
    # Horizontal and mathematical bars are shorter, leaving robust side air in
    # tables; vertical and directional signs are slightly more compact.
    apply_group(font, HORIZONTAL_SIGNS, 0.945, 0.985, 0, italic, changed)
    apply_group(font, DIRECTIONAL_SIGNS, 0.965, 0.965, 0, italic, changed)
    # Currency and official-document marks share the broad capital colour.
    apply_group(font, OFFICIAL_SIGNS, 1.020 if bold else 1.024, 0.988, 20, italic, changed)
    # Small punctuation is made firmer and more compact without moving its
    # advance or baseline position.
    apply_group(font, PUNCTUATION, 0.965, 0.970, 0, italic, changed)
    apply_group(font, SCIENTIFIC_SIGNS, 0.970, 0.985, 0, italic, changed)

    font.version = version
    font.sfntRevision = float(version)
    font.save(output)
    font.close()
    print(json.dumps({
        "source": source,
        "output": output,
        "version": version,
        "changed": len(changed),
        "glyphs": sorted(changed),
    }))


if __name__ == "__main__":
    main()
