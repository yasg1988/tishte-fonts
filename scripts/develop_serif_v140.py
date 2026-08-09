#!/usr/bin/env python3
"""Complete the v0.140 residual glyph system without changing advances."""

from __future__ import annotations

import json
import sys

import fontforge


SUPERSCRIPTS_AND_FRACTIONS = (0x00B2, 0x00B3, 0x00B5, 0x00B9, 0x00BC, 0x00BD, 0x00BE)
LATIN_STRUCTURAL = (
    0x00C5, 0x00C6, 0x00D0, 0x00D8, 0x00DE,
    0x00E6, 0x00F0, 0x00F8, 0x00FE,
    0x0110, 0x0111, 0x0126, 0x0127, 0x0131, 0x0135,
    0x0141, 0x0142, 0x014A, 0x014B, 0x0152, 0x0153, 0x0166, 0x0167,
)
LATIN_ACCENTED_LOWER = (
    0x00EC, 0x00ED, 0x00EE, 0x00EF,
    0x0129, 0x012B, 0x012D,
)
COMBINING_MARKS = (
    0x0300, 0x0301, 0x0302, 0x0303, 0x0304, 0x0306, 0x0307,
    0x0308, 0x030A, 0x030B, 0x030C, 0x0327, 0x0328,
)
CYRILLIC_RESIDUALS = (0x0413, 0x041F, 0x04A4, 0x04A5, 0x04F8, 0x04F9)
MISCELLANEOUS = (0x00B7, 0x2248)


def reshape(glyph, sx: float, sy: float, cut: int = 0, italic: bool = False) -> bool:
    """Apply a restrained optical correction around the glyph's ink centre."""
    if not glyph.isWorthOutputting():
        return False
    # Several residual Cyrillic, fraction and mark glyphs are references to
    # upstream components. Detach only the target glyph so its own outline can
    # be corrected without altering an unrelated shared component.
    if glyph.references:
        glyph.unlinkRef()
    if not len(glyph.foreground):
        return False
    width = glyph.width
    x_min, y_min, x_max, y_max = glyph.boundingBox()
    span = x_max - x_min
    height = y_max - y_min
    if span <= 0 or height <= 0:
        return False
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    outer = span * 0.055
    layer = glyph.foreground
    changed = False
    for contour in layer:
        for point in contour:
            old_x, old_y = point.x, point.y
            point.x = round(cx + (point.x - cx) * sx)
            point.y = round(cy + (point.y - cy) * sy)
            at_left = old_x <= x_min + outer
            at_right = old_x >= x_max - outer
            if cut and -8 <= old_y <= 62 and (at_left or at_right):
                point.y += cut + (4 if italic and at_right else 0)
            changed |= (point.x, point.y) != (old_x, old_y)
    if changed:
        glyph.setLayer(layer, glyph.activeLayer)
        glyph.width = width
        glyph.ttinstrs = b""
    return changed


def apply_group(font, codepoints, sx, sy, cut, italic, changed, missing) -> None:
    for codepoint in codepoints:
        try:
            glyph = font[codepoint]
        except TypeError:
            missing.append(f"U+{codepoint:04X}")
            continue
        if reshape(glyph, sx=sx, sy=sy, cut=cut, italic=italic):
            changed.add(f"U+{codepoint:04X}")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: develop_serif_v140.py INPUT.sfd OUTPUT.sfd VERSION")
    source, output, version = sys.argv[1:]
    font = fontforge.open(source)
    italic = "Italic" in font.fontname
    bold = "Bold" in font.fontname
    changed: set[str] = set()
    missing: list[str] = []

    # Small numerals and fractions gain the same compact service colour as the
    # v0.130 tabular figures, without disturbing their vertical placement.
    apply_group(font, SUPERSCRIPTS_AND_FRACTIONS, 1.018, 0.988, 0, italic, changed, missing)
    # Independent extended-Latin forms receive a restrained widening and the
    # clipped outside feet established by the capital/lowercase family system.
    apply_group(font, LATIN_STRUCTURAL, 1.014 if bold else 1.018, 0.992, 20, italic, changed, missing)
    # Precomposed dotted and accented i forms are corrected as whole glyphs so
    # their legacy copied outlines agree optically with current base letters.
    apply_group(font, LATIN_ACCENTED_LOWER, 1.016, 0.994, 0, italic, changed, missing)
    # Combining marks keep their zero advances and anchor positioning. Only
    # their ink is made slightly broader and calmer for office-size rendering.
    apply_group(font, COMBINING_MARKS, 1.050 if bold else 1.060, 0.965, 0, italic, changed, missing)
    # The final Cyrillic and Mari residuals use the same service-terminal rule.
    apply_group(font, CYRILLIC_RESIDUALS, 1.014 if bold else 1.018, 0.992, 22, italic, changed, missing)
    # Middle dot and approximate receive a minute optical correction only.
    apply_group(font, MISCELLANEOUS, 0.972, 0.982, 0, italic, changed, missing)

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
        "codepoints": sorted(changed),
    }))


if __name__ == "__main__":
    main()
