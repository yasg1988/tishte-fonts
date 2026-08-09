#!/usr/bin/env python3
"""Print per-glyph FontForge validation masks for outline diagnosis."""

from __future__ import annotations

import argparse
import fontforge


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font")
    args = parser.parse_args()
    opened = fontforge.open(args.font)
    for glyph in opened.glyphs():
        mask = glyph.validate(True)
        if mask:
            print(f"{glyph.glyphname}: {mask}")
    opened.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
