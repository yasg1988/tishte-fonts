#!/usr/bin/env python3
"""Measure exact outline identity against the Tinos upstream scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from font_metrics_audit import load_charset


STYLES = {
    "Regular": "Tinos-Regular.ttf",
    "Bold": "Tinos-Bold.ttf",
    "Italic": "Tinos-Italic.ttf",
    "BoldItalic": "Tinos-BoldItalic.ttf",
}


def recording(font: TTFont, glyph_name: str):
    pen = RecordingPen()
    font.getGlyphSet()[glyph_name].draw(pen)
    return pen.value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.910")
    parser.add_argument("--max-identical-ratio", type=float)
    args = parser.parse_args()
    root = args.root.resolve()
    tag = "v" + args.version.partition(".")[2]
    charset = load_charset(root / "data" / "document-charset.txt")
    report = {"version": args.version, "method": "exact decomposed outline command equality", "styles": {}, "passed": True}

    for style, upstream_name in STYLES.items():
        with TTFont(root / "sources" / "upstream" / "tinos" / upstream_name) as upstream, TTFont(root / "build" / f"TishteSerif-{style}-{tag}.ttf") as candidate:
            upstream_cmap = upstream.getBestCmap()
            candidate_cmap = candidate.getBestCmap()
            common = [codepoint for codepoint in charset if codepoint in upstream_cmap and codepoint in candidate_cmap]
            identical = []
            changed = []
            for codepoint in common:
                same = recording(upstream, upstream_cmap[codepoint]) == recording(candidate, candidate_cmap[codepoint])
                (identical if same else changed).append(f"U+{codepoint:04X}")
        ratio = len(identical) / len(common) if common else 1.0
        passed = args.max_identical_ratio is None or ratio <= args.max_identical_ratio
        report["styles"][style] = {
            "common": len(common),
            "identical": len(identical),
            "changed": len(changed),
            "identical_ratio": round(ratio, 6),
            "identical_codepoints": identical,
            "changed_codepoints": changed,
            "passed": passed,
        }
        report["passed"] &= passed
        print(f"{style}: {len(identical)}/{len(common)} exact upstream outlines ({ratio:.1%})")

    output = root / "artifacts" / "reports" / f"outline-originality-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
