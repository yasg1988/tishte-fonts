#!/usr/bin/env python3
"""Subset Tishte binaries to the declared production charset and layout closure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

from font_metrics_audit import load_charset


STYLES = ("Regular", "Bold", "Italic", "BoldItalic")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.910")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = "v" + args.version.partition(".")[2]
    unicodes = load_charset(root / "data" / "document-charset.txt")
    report = {"version": args.version, "declared_codepoints": len(unicodes), "styles": {}, "passed": True}

    for style in STYLES:
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        with TTFont(path) as before:
            before_glyphs = len(before.getGlyphOrder())
            before_unicode = len(before.getBestCmap())
            before_bytes = path.stat().st_size

        options = subset.Options()
        options.layout_features = ["*"]
        options.layout_scripts = ["*"]
        options.name_IDs = ["*"]
        options.name_languages = ["*"]
        options.glyph_names = True
        options.hinting = True
        options.notdef_glyph = True
        options.notdef_outline = True
        # Keep only .notdef plus glyphs reachable from the declared charset and
        # layout closure. Legacy .null/nonmarkingreturn glyphs are not useful in
        # modern OpenType fonts and otherwise remain unreachable.
        options.recommended_glyphs = False
        options.recalc_average_width = True
        options.recalc_max_context = True
        options.canonical_order = True

        font = TTFont(path, recalcTimestamp=False)
        worker = subset.Subsetter(options=options)
        worker.populate(unicodes=unicodes)
        worker.subset(font)
        temporary = path.with_suffix(".subset.ttf")
        font.save(temporary, reorderTables=True)
        font.close()
        temporary.replace(path)

        with TTFont(path) as after:
            cmap = after.getBestCmap()
            missing = [f"U+{codepoint:04X}" for codepoint in unicodes if codepoint not in cmap]
            unexpected = [f"U+{codepoint:04X}" for codepoint in cmap if codepoint not in set(unicodes)]
            details = {
                "before": {"glyphs": before_glyphs, "unicode": before_unicode, "bytes": before_bytes},
                "after": {"glyphs": len(after.getGlyphOrder()), "unicode": len(cmap), "bytes": path.stat().st_size},
                "missing": missing,
                "unexpected_encoded": unexpected,
                "passed": not missing and not unexpected,
            }
            report["styles"][style] = details
            report["passed"] &= details["passed"]
            print(f"{style}: {before_glyphs} -> {details['after']['glyphs']} glyphs; {before_unicode} -> {details['after']['unicode']} encoded")

    output = root / "artifacts" / "reports" / f"production-subset-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
