#!/usr/bin/env python3
"""Apply the first restrained Tishte signature to the editable serif source.
Run with FontForge's Python interpreter, not the system Python:

    fontforge -script scripts/apply_signature_v010.py input.sfd output.sfd

The transformation is idempotent and preserves all advance widths.
"""

from __future__ import annotations

import sys

import fontforge


def replace_dieresis(font):
    glyph = font["dieresis"]
    width = glyph.width
    glyph.clear()
    pen = glyph.glyphPen()

    # Two compact lozenges. Their bounds match the upstream dots so composite
    # glyph bounding boxes and line metrics remain stable.
    for left, right, center in ((63, 262, 163), (420, 618, 519)):
        pen.moveTo((center, 1294))
        pen.lineTo((right, 1194))
        pen.lineTo((center, 1093))
        pen.lineTo((left, 1194))
        pen.closePath()
    pen = None
    glyph.width = width


def rebuild_uppercase_u_dieresis(font):
    glyph = font["uni04F0"]
    width = glyph.width
    glyph.clear()
    pen = glyph.glyphPen()
    pen.addComponent("uni0423", (1, 0, 0, 1, 0, 0))
    pen.addComponent("dieresis", (1, 0, 0, 1, 384, 365))
    pen = None
    glyph.width = width


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
    replace_dieresis(font)
    rebuild_uppercase_u_dieresis(font)

    # Angular terminal cuts on document digits. The changes are deliberately
    # small and do not alter the advance width or baseline footprint.
    move_point(font, "one", 0, 10, y=1300)
    move_point(font, "seven", 0, 4, x=925, y=1238)

    font.version = "0.010"
    font.sfntRevision = 0.010


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: apply_signature_v010.py INPUT.sfd OUTPUT.sfd")
    source, output = sys.argv[1:]
    font = fontforge.open(source)
    apply(font)
    font.save(output)
    font.close()


if __name__ == "__main__":
    main()
