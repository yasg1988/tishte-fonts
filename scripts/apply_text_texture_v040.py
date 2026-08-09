#!/usr/bin/env python3
"""Shape the first high-frequency lowercase text texture for Tishte Serif."""

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


def transform_contour(font, glyph_name, contour_index, matrix):
    glyph = font[glyph_name]
    width = glyph.width
    layer = glyph.foreground
    layer[contour_index].transform(matrix)
    glyph.setLayer(layer, glyph.activeLayer)
    glyph.width = width


def clear_stale_instructions(font, glyph_names):
    for name in glyph_names:
        font[name].ttinstrs = b""


def apply(font):
    # a / Cyrillic а: clipped service foot and a cleaner upper entry.
    move_point(font, "a", 0, 7, y=42)
    move_point(font, "a", 0, 29, x=195, y=704)
    move_point(font, "a", 0, 30, x=195)

    # e / Cyrillic е: a slightly rising crossbar opens the reading aperture.
    move_point(font, "e", 0, 0, x=282, y=490)
    move_point(font, "e", 0, 27, x=806, y=458)

    # n: lower, calmer shoulder with more interior air.
    move_point(font, "n", 0, 3, y=948)
    move_point(font, "n", 0, 5, y=948)
    move_point(font, "n", 0, 19, x=560, y=852)
    move_point(font, "n", 0, 20, x=462, y=852)

    # o / Cyrillic о: widen both contours together around x=512. This creates
    # a slightly broader reading shape without disturbing stroke contrast.
    transform_contour(font, "o", 0, (1.025, 0, 0, 1, -12.8, 0))
    transform_contour(font, "o", 1, (1.025, 0, 0, 1, -12.8, 0))

    # p / Cyrillic р: more open bowl and a clipped descender serif.
    move_point(font, "p", 1, 4, y=880)
    move_point(font, "p", 1, 7, x=297)
    move_point(font, "p", 1, 9, y=44)
    move_point(font, "p", 0, 24, y=-402)

    # c / Cyrillic с: open aperture with paired directional terminals.
    move_point(font, "c", 0, 0, x=818, y=78)
    move_point(font, "c", 0, 13, x=798, y=700)
    move_point(font, "c", 0, 14, x=748, y=682)
    move_point(font, "c", 0, 25, x=818, y=126)

    # Latin u and Cyrillic у/y receive the same terminal logic.
    move_point(font, "u", 0, 11, y=42)
    move_point(font, "y", 0, 3, y=-188)

    # Cyrillic н keeps its own construction: a restrained rising crossbar.
    move_point(font, "uni043D", 0, 6, y=510)
    move_point(font, "uni043D", 0, 7, y=530)
    move_point(font, "uni043D", 0, 20, y=451)
    move_point(font, "uni043D", 0, 21, y=431)

    # The source scaffold carries TrueType bytecode for its original outlines.
    # Keeping that bytecode after contour edits causes raster distortion.
    clear_stale_instructions(
        font,
        ("a", "e", "n", "o", "p", "c", "u", "y", "uni043D"),
    )

    font.version = "0.040"
    font.sfntRevision = 0.040


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: apply_text_texture_v040.py INPUT.sfd OUTPUT.sfd")
    source, output = sys.argv[1:]
    font = fontforge.open(source)
    apply(font)
    font.save(output)
    font.close()


if __name__ == "__main__":
    main()
