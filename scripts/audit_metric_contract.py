#!/usr/bin/env python3
"""Audit built fonts against the portable numeric metric contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.090")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = json.loads((root / "data" / "times-new-roman-metrics.json").read_text(encoding="utf-8"))
    tag = "v" + args.version.partition(".")[2]
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
            passed = not mismatches and not vertical
            report["styles"][style] = {
                "codepoints": len(expected["advances"]),
                "advance_mismatches": mismatches,
                "vertical_mismatches": vertical,
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
