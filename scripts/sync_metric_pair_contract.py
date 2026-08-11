#!/usr/bin/env python3
"""Apply sparse GPOS deltas from the portable Times numeric pair contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

from audit_metric_contract import Shaper
from kerning import append_delta_lookup
from versioning import version_tag


STYLES = ("Regular", "Bold", "Italic", "BoldItalic")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    contract = json.loads(
        (root / "data" / "times-new-roman-metrics.json").read_text(encoding="utf-8")
    )
    report = {"version": args.version, "styles": {}}
    for style in STYLES:
        expected = contract["styles"][style]
        codepoints = [int(token[2:], 16) for token in expected["advances"]]
        expected_pairs = expected["pair_adjustments"]
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        shaper = Shaper(path)
        with TTFont(path, lazy=True) as font:
            cmap = font.getBestCmap()
            deltas = {}
            for left_codepoint in codepoints:
                for right_codepoint in codepoints:
                    token = f"U+{left_codepoint:04X} U+{right_codepoint:04X}"
                    expected_value = expected_pairs.get(token, 0)
                    actual_value = shaper.adjustment(
                        chr(left_codepoint), chr(right_codepoint)
                    )
                    delta = expected_value - actual_value
                    if delta:
                        key = (cmap[left_codepoint], cmap[right_codepoint])
                        previous = deltas.get(key)
                        if previous is not None and previous != delta:
                            raise ValueError(f"conflicting delta for {key}: {previous} != {delta}")
                        deltas[key] = delta
        append_delta_lookup(path, deltas)
        values = list(deltas.values())
        report["styles"][style] = {
            "pairs": len(deltas),
            "minimum_delta": min(values, default=0),
            "maximum_delta": max(values, default=0),
        }
        print(f"{style}: applied {len(deltas)} pair deltas")
    output = root / "artifacts" / "reports" / f"metric-pair-deltas-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
