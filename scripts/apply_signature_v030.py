#!/usr/bin/env python3
"""Apply the first cross-script Tishte terminal system.

The changes connect Cyrillic, Latin and numerals with restrained directional
cuts. Advance widths and document vertical metrics remain untouched.
"""

from __future__ import annotations

import sys

import fontforge


def move_point(font, glyph_name, contour_index, point_index, x=None, y=None):
    glyph = font[glyph_name]
    width = glyph.width
    layer = glyph.foreground
    point = layer[contour_index][point_index]
    if x is not None:
        point.x = x
    if y is not None:
        point.y = y
    glyph.setLayer(layer, glyph.activeLayer)
    glyph.width = width


def apply(font):
    # Cyrillic: clipped free terminals and a restrained central-spine cut.
    move_point(font, "uni0416", 0, 3, y=55)
    move_point(font, "uni0416", 0, 30, y=55)
    move_point(font, "uni0416", 0, 16, y=1290)
    move_point(font, "uni0436", 0, 3, y=42)
    move_point(font, "uni0436", 0, 30, y=42)
    move_point(font, "uni0436", 0, 16, y=898)

    # Ya and Latin R share the same diagonal-leg terminal language.
    move_point(font, "uni042F", 0, 2, y=55)
    move_point(font, "uni044F", 0, 2, y=42)
    move_point(font, "R", 0, 21, y=55)

    # Latin capitals use the cut only at the outer right foot.
    move_point(font, "A", 0, 9, y=55)
    move_point(font, "M", 0, 20, y=55)

    # A clipped service terminal on U and a matching open arm on four.
    move_point(font, "uni0423", 0, 23, y=220)
    move_point(font, "four", 0, 4, y=360)

    font.version = "0.030"
    font.sfntRevision = 0.030


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: apply_signature_v030.py INPUT.sfd OUTPUT.sfd")
    source, output = sys.argv[1:]
    font = fontforge.open(source)
    apply(font)
    font.save(output)
    font.close()


if __name__ == "__main__":
    main()
