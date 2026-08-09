#!/usr/bin/env python3
"""Measure exact Sans outline identity against the pinned Arimo scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from build_sans_family import STYLES
from font_metrics_audit import load_charset
from versioning import version_tag


def drawing(font: TTFont, glyph_name: str) -> list:
    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[glyph_name].draw(pen)
    return pen.value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    parser.add_argument("--max-identical-ratio", type=float, default=0.01)
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    codepoints = load_charset(root / "data" / "document-charset.txt")
    report = {"version": args.version, "styles": {}, "passed": True}
    for style in STYLES:
        variable = TTFont(root / "sources" / "upstream" / "arimo" / style.source)
        upstream = instantiateVariableFont(variable, {"wght": style.weight}, inplace=False, optimize=True)
        candidate = TTFont(root / "build" / f"TishteSans-{style.key}-{tag}.ttf")
        upstream_cmap = upstream.getBestCmap()
        candidate_cmap = candidate.getBestCmap()
        comparable = [cp for cp in codepoints if cp in upstream_cmap and cp in candidate_cmap and drawing(candidate, candidate_cmap[cp])]
        identical = [cp for cp in comparable if drawing(upstream, upstream_cmap[cp]) == drawing(candidate, candidate_cmap[cp])]
        ratio = len(identical) / len(comparable) if comparable else 1
        passed = ratio <= args.max_identical_ratio
        report["styles"][style.key] = {"comparable": len(comparable), "identical": len(identical), "ratio": ratio, "passed": passed}
        report["passed"] &= passed
        print(f"{style.key}: {len(identical)}/{len(comparable)} exact outlines ({ratio:.1%})")
        variable.close(); upstream.close(); candidate.close()
    output = root / "artifacts" / "reports" / f"sans-originality-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
