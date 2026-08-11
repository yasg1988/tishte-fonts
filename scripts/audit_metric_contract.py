#!/usr/bin/env python3
"""Audit built fonts against the portable numeric metric contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont
import uharfbuzz as hb

from versioning import version_tag


FEATURES = {"kern": True, "liga": False, "clig": False}


class Shaper:
    def __init__(self, path: Path):
        data = path.read_bytes()
        self.face = hb.Face(data)
        self.font = hb.Font(self.face)
        self.font.scale = (self.face.upem, self.face.upem)
        self.singles: dict[str, int] = {}

    def advance(self, text: str) -> int:
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.font, buffer, FEATURES)
        return sum(position.x_advance for position in buffer.glyph_positions)

    def adjustment(self, left: str, right: str) -> int:
        if left not in self.singles:
            self.singles[left] = self.advance(left)
        if right not in self.singles:
            self.singles[right] = self.advance(right)
        return self.advance(left + right) - self.singles[left] - self.singles[right]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = json.loads((root / "data" / "times-new-roman-metrics.json").read_text(encoding="utf-8"))
    tag = version_tag(args.version)
    report = {"version": args.version, "styles": {}, "passed": True}
    for style, expected in contract["styles"].items():
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        with TTFont(path) as font:
            cmap = font.getBestCmap()
            mismatches = []
            for token, advance in expected["advances"].items():
                codepoint = int(token[2:], 16)
                glyph = cmap.get(codepoint)
                actual = None if glyph is None else font["hmtx"].metrics[glyph][0]
                if actual != advance:
                    mismatches.append({"codepoint": token, "expected": advance, "actual": actual})
            vertical = []
            for table_name, fields in expected["vertical"].items():
                for field, value in fields.items():
                    actual = getattr(font[table_name], field)
                    if actual != value:
                        vertical.append({"table": table_name, "field": field, "expected": value, "actual": actual})
            pair_mismatches = []
            expected_pairs = expected.get("pair_adjustments", {})
            codepoints = [int(token[2:], 16) for token in expected["advances"]]
            shaper = Shaper(path)
            for left_codepoint in codepoints:
                for right_codepoint in codepoints:
                    token = f"U+{left_codepoint:04X} U+{right_codepoint:04X}"
                    expected_adjustment = expected_pairs.get(token, 0)
                    actual_adjustment = shaper.adjustment(
                        chr(left_codepoint), chr(right_codepoint)
                    )
                    if actual_adjustment != expected_adjustment:
                        pair_mismatches.append({
                            "pair": token,
                            "expected": expected_adjustment,
                            "actual": actual_adjustment,
                        })
            passed = not mismatches and not vertical and not pair_mismatches
            report["styles"][style] = {
                "codepoints": len(expected["advances"]),
                "advance_mismatches": mismatches,
                "vertical_mismatches": vertical,
                "pair_checks": len(codepoints) ** 2,
                "pair_mismatch_count": len(pair_mismatches),
                "pair_mismatches": pair_mismatches[:100],
                "passed": passed,
            }
            report["passed"] &= passed
    output = root / "artifacts" / "reports" / f"metric-contract-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
