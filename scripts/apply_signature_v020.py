#!/usr/bin/env python3
"""Extend the Tishte signature to Latin, punctuation and document symbols."""

from __future__ import annotations

import sys

import fontforge


def diamond(left, bottom, right, top, is_quadratic):
    contour = fontforge.contour()
    contour.is_quadratic = is_quadratic
    center_x = round((left + right) / 2)
    center_y = round((bottom + top) / 2)
    contour += (center_x, top)
    contour += (right, center_y)
    contour += (center_x, bottom)
    contour += (left, center_y)
    contour.closed = True
    return contour


def replace_contour(font, glyph_name, contour_index, bounds):
    glyph = font[glyph_name]
    width = glyph.width
    layer = glyph.foreground
    del layer[contour_index]
    layer += diamond(*bounds, layer.is_quadratic)
    glyph.setLayer(layer, glyph.activeLayer)
    glyph.width = width


def replace_two_contours(font, glyph_name, first_bounds, second_bounds):
    glyph = font[glyph_name]
    width = glyph.width
    layer = glyph.foreground
    # Delete from the end so indices stay stable.
    del layer[1]
    del layer[0]
    layer += diamond(*first_bounds, layer.is_quadratic)
    layer += diamond(*second_bounds, layer.is_quadratic)
    glyph.setLayer(layer, glyph.activeLayer)
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
    # Latin signature: diamond dots and a small cut at the A apex.
    replace_contour(font, "i", 0, (162, 1139, 379, 1356))
    replace_contour(font, "j", 0, (176, 1139, 393, 1356))
    move_point(font, "A", 0, 6, y=1318)

    # Punctuation and document markers use the same compact lozenge language.
    replace_contour(font, "period", 0, (135, -29, 377, 213))
    replace_contour(font, "exclam", 0, (219, -29, 461, 213))
    replace_contour(font, "question", 1, (289, -29, 530, 213))
    replace_two_contours(font, "colon", (162, -29, 403, 213), (162, 719, 403, 961))
    replace_contour(font, "bullet", 0, (115, 434, 602, 922))

    # Cyrillic/Mari service cuts. Descenders keep their original depth.
    move_point(font, "uni0414", 1, 2, y=-400)
    move_point(font, "uni0414", 1, 15, y=-400)
    move_point(font, "uni0434", 0, 7, y=-360)
    move_point(font, "uni0434", 0, 12, y=-360)
    move_point(font, "uni04A4", 0, 0, x=1655)
    move_point(font, "uni04A5", 0, 0, x=1215)

    # The numero underline becomes a restrained directional wedge.
    move_point(font, "uni2116", 0, 0, y=86)
    move_point(font, "uni2116", 0, 3, y=16)

    # Times New Roman uses a full-em advance for the reference mark. Tinos does
    # not, so align this document symbol explicitly with the metric contract.
    font["uni203B"].width = 2048

    font.version = "0.020"
    font.sfntRevision = 0.020


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: apply_signature_v020.py INPUT.sfd OUTPUT.sfd")
    source, output = sys.argv[1:]
    font = fontforge.open(source)
    apply(font)
    font.save(output)
    font.close()


if __name__ == "__main__":
    main()
