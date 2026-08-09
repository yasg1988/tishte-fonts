#!/usr/bin/env python3
"""Develop the v0.100 Regular reading texture without changing advances."""

from __future__ import annotations

import json
import sys

import fontforge


LATIN_LOWER = "abcdefghijklmnopqrstuvwxyz"
CYRILLIC_LOWER = tuple(f"uni{codepoint:04X}" for codepoint in range(0x0430, 0x0450)) + ("uni0451",)
ROUND_GLYPHS = (
    "B", "C", "D", "G", "O", "P", "Q", "R",
    "b", "c", "d", "e", "g", "o", "p", "q",
    "zero", "two", "three", "five", "six", "eight", "nine",
    "uni0411", "uni0412", "uni0417", "uni041E", "uni0420", "uni0421", "uni0424", "uni042D", "uni042E",
    "uni0431", "uni0432", "uni0437", "uni043E", "uni0440", "uni0441", "uni0444", "uni044D", "uni044E",
)


def transform_points(glyph, transform) -> bool:
    if not glyph.isWorthOutputting() or not len(glyph.foreground):
        return False
    width = glyph.width
    layer = glyph.foreground
    changed = False
    for contour in layer:
        for point in contour:
            x, y = transform(point.x, point.y)
            if (x, y) != (point.x, point.y):
                point.x, point.y = x, y
                changed = True
    if changed:
        glyph.setLayer(layer, glyph.activeLayer)
        glyph.width = width
        glyph.ttinstrs = b""
    return changed


def increase_x_height(glyph) -> bool:
    # A one-percent lift gives the face a calmer service-text colour while
    # keeping capitals, baseline, descenders, line metrics and advances fixed.
    return transform_points(glyph, lambda x, y: (x, round(y * 1.012)) if y > 0 else (x, y))


def broaden_round(glyph) -> bool:
    x_min, _y_min, x_max, _y_max = glyph.boundingBox()
    center = (x_min + x_max) / 2
    return transform_points(glyph, lambda x, y: (round(center + (x - center) * 1.012), y))


def main() -> None:
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: develop_serif_v100.py INPUT.sfd OUTPUT.sfd [VERSION]")
    source, output = sys.argv[1:3]
    version = sys.argv[3] if len(sys.argv) == 4 else "0.100"
    font = fontforge.open(source)
    changed = set()
    for name in (*LATIN_LOWER, *CYRILLIC_LOWER):
        if name in font and increase_x_height(font[name]):
            changed.add(name)
    for name in ROUND_GLYPHS:
        if name in font and broaden_round(font[name]):
            changed.add(name)
    font.version = version
    font.sfntRevision = float(version)
    font.save(output)
    font.close()
    print(json.dumps({"source": source, "output": output, "changed": len(changed), "glyphs": sorted(changed)}))


if __name__ == "__main__":
    main()
