#!/usr/bin/env python3
"""Report FontForge outline validation flags for every encoded glyph."""

from __future__ import annotations

import json
import sys

import fontforge


FLAGS = {
    0x01: "open_contour",
    0x02: "intersecting_contours",
    0x04: "self_intersection",
    0x08: "wrong_direction",
    0x10: "flipped_reference",
    0x20: "missing_extrema",
    0x40: "known_bad_glyph",
    0x80: "too_many_points",
    0x100: "too_many_hints",
    0x200: "invalid_glyph_name",
    0x400: "invalid_unicode",
    0x800: "duplicate_unicode",
    0x1000: "duplicate_glyph_name",
}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: report_outline_issues.py FONT")
    font = fontforge.open(sys.argv[1])
    issues = []
    counts = {label: 0 for label in FLAGS.values()}
    for glyph in font.glyphs():
        if not glyph.isWorthOutputting():
            continue
        state = glyph.validate(True)
        if not state:
            continue
        labels = [label for bit, label in FLAGS.items() if state & bit]
        for label in labels:
            counts[label] += 1
        issues.append(
            {
                "glyph": glyph.glyphname,
                "unicode": glyph.unicode,
                "mask": state,
                "flags": labels,
                "references": [reference[0] for reference in glyph.references],
                "contours": len(glyph.foreground),
            }
        )
    result = {
        "font": sys.argv[1],
        "font_mask": font.validate(),
        "affected_glyphs": len(issues),
        "counts": {key: value for key, value in counts.items() if value},
        "issues": issues,
    }
    font.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
