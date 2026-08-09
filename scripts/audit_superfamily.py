#!/usr/bin/env python3
"""Audit the shared release contract of Tishte Serif and Tishte Sans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

from font_metrics_audit import load_charset
from versioning import version_tag


def drawing(font: TTFont, glyph_name: str) -> tuple:
    glyph_set = font.getGlyphSet()
    pen = DecomposingRecordingPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    return tuple((operation, tuple(tuple(point) if isinstance(point, tuple) else point for point in points)) for operation, points in pen.value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    charset = load_charset(root / "data" / "document-charset.txt")
    serif_path = root / "build" / f"TishteSerif-Regular-{tag}.ttf"
    sans_path = root / "build" / f"TishteSans-Regular-{tag}.ttf"
    failures = []
    with TTFont(serif_path) as serif, TTFont(sans_path) as sans:
        serif_cmap, sans_cmap = serif.getBestCmap(), sans.getBestCmap()
        if set(serif_cmap) != set(charset) or set(sans_cmap) != set(charset):
            failures.append("shared_charset")
        if serif["name"].getDebugName(16) != "Tishte Serif" or sans["name"].getDebugName(16) != "Tishte Sans":
            failures.append("family_names")
        if serif["name"].getDebugName(9) != "Сергей Якунин" or sans["name"].getDebugName(9) != "Сергей Якунин":
            failures.append("designer")
        if serif["name"].getDebugName(5) != sans["name"].getDebugName(5):
            failures.append("version")
        exact = []
        for cp in charset:
            serif_drawing = drawing(serif, serif_cmap[cp])
            sans_drawing = drawing(sans, sans_cmap[cp])
            if serif_drawing and serif_drawing == sans_drawing:
                exact.append(f"U+{cp:04X}")
        if exact:
            failures.append("cross_family_duplicate_outlines")
    report = {"version": args.version, "charset": len(charset), "exact_cross_family_outlines": exact, "failures": failures, "passed": not failures}
    output = root / "artifacts" / "reports" / f"superfamily-audit-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Superfamily: {len(charset)} shared codepoints; {len(exact)} exact cross-family outlines; {'passed' if not failures else failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
