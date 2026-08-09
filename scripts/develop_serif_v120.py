#!/usr/bin/env python3
"""Apply the v0.120 service-capital system without changing advances."""

from __future__ import annotations

import json
import sys

import fontforge


LATIN_CAPS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
CYRILLIC_CAPS = tuple(f"uni{codepoint:04X}" for codepoint in range(0x0410, 0x0430)) + ("uni0401",)
TARGETS = LATIN_CAPS + CYRILLIC_CAPS


def shape_capital(glyph, italic: bool, bold: bool) -> bool:
    """Create a compact, open service capital with clipped outside feet."""
    if not glyph.isWorthOutputting() or not len(glyph.foreground):
        return False
    width = glyph.width
    x_min, y_min, x_max, y_max = glyph.boundingBox()
    span = x_max - x_min
    height = y_max - y_min
    if span <= 0 or height <= 0:
        return False
    center = (x_min + x_max) / 2
    # The family already has generous Times-compatible advances. A restrained
    # widening uses that space and lowers apparent contrast in office sizes.
    horizontal = 1.018 if bold else 1.022
    # Slightly calmer capitals distinguish the line from the tall Tinos model
    # while leaving all line and advance metrics untouched.
    vertical = 0.984
    cut = 34 if bold else 30
    outer = span * 0.055
    layer = glyph.foreground
    changed = False
    for contour in layer:
        for point in contour:
            old_x, old_y = point.x, point.y
            point.x = round(center + (point.x - center) * horizontal)
            if point.y > 0:
                point.y = round(point.y * vertical)
            # Directional baseline cuts are applied only to outside serif
            # corners. In italics the right cut is slightly stronger, matching
            # the direction of movement without mechanically slanting romans.
            at_left = old_x <= x_min + outer
            at_right = old_x >= x_max - outer
            if -8 <= old_y <= 62 and (at_left or at_right):
                point.y += cut + (6 if italic and at_right else 0)
            changed |= (point.x, point.y) != (old_x, old_y)
    if changed:
        glyph.setLayer(layer, glyph.activeLayer)
        glyph.width = width
        glyph.ttinstrs = b""
    return changed


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: develop_serif_v120.py INPUT.sfd OUTPUT.sfd VERSION")
    source, output, version = sys.argv[1:]
    font = fontforge.open(source)
    italic = "Italic" in font.fontname
    bold = "Bold" in font.fontname
    changed = []
    missing = []
    for name in TARGETS:
        if name not in font:
            missing.append(name)
        elif shape_capital(font[name], italic=italic, bold=bold):
            changed.append(name)
    if missing:
        raise ValueError(f"missing target glyphs: {missing}")
    font.version = version
    font.sfntRevision = float(version)
    font.save(output)
    font.close()
    print(json.dumps({
        "source": source,
        "output": output,
        "version": version,
        "changed": len(changed),
        "glyphs": changed,
    }))


if __name__ == "__main__":
    main()
