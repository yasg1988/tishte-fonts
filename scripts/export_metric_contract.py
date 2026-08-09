#!/usr/bin/env python3
"""Export the numeric Times New Roman metric contract without font outlines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

from font_metrics_audit import load_charset


STYLES = {
    "Regular": "times.ttf",
    "Bold": "timesbd.ttf",
    "Italic": "timesi.ttf",
    "BoldItalic": "timesbi.ttf",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--reference-dir", type=Path, default=Path("C:/Windows/Fonts"))
    parser.add_argument("--output", type=Path, default=Path("data/times-new-roman-metrics.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    codepoints = load_charset(root / "data" / "document-charset.txt")
    styles = {}
    for style, filename in STYLES.items():
        with TTFont(args.reference_dir / filename) as font:
            cmap = font.getBestCmap()
            styles[style] = {
                "reference_filename": filename,
                "units_per_em": font["head"].unitsPerEm,
                "mac_style": font["head"].macStyle,
                "fs_selection": font["OS/2"].fsSelection,
                "vertical": {
                    "hhea": {
                        key: getattr(font["hhea"], key)
                        for key in ("ascent", "descent", "lineGap")
                    },
                    "OS/2": {
                        key: getattr(font["OS/2"], key)
                        for key in (
                            "sTypoAscender",
                            "sTypoDescender",
                            "sTypoLineGap",
                            "usWinAscent",
                            "usWinDescent",
                        )
                    },
                },
                "advances": {
                    f"U+{codepoint:04X}": font["hmtx"].metrics[cmap[codepoint]][0]
                    for codepoint in codepoints
                },
            }
    payload = {
        "schema": 1,
        "description": "Numeric layout metrics only; contains no Times New Roman outlines.",
        "charset": "data/document-charset.txt",
        "styles": styles,
    }
    output = args.output if args.output.is_absolute() else root / args.output
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
