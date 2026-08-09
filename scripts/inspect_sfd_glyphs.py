#!/usr/bin/env python3
"""Print contour coordinates for selected glyphs in an editable SFD source."""

from __future__ import annotations

import sys

import fontforge


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: inspect_sfd_glyphs.py FONT.sfd GLYPH [GLYPH ...]")
    font = fontforge.open(sys.argv[1])
    for name in sys.argv[2:]:
        glyph = font[name]
        print(f"\n{name} width={glyph.width} bbox={glyph.boundingBox()}")
        for contour_index, contour in enumerate(glyph.foreground):
            points = " ".join(
                f"{index}:{round(point.x)},{round(point.y)}{'o' if point.on_curve else 'c'}"
                for index, point in enumerate(contour)
            )
            print(f"  c{contour_index} {points}")
    font.close()


if __name__ == "__main__":
    main()
