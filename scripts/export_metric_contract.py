#!/usr/bin/env python3
"""Export the numeric Times New Roman metric contract without font outlines."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont
import uharfbuzz as hb

from font_metrics_audit import load_charset


STYLES = {
    "Regular": "times.ttf",
    "Bold": "timesbd.ttf",
    "Italic": "timesi.ttf",
    "BoldItalic": "timesbi.ttf",
}
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


def pair_adjustments(path: Path, codepoints: list[int]) -> dict[str, int]:
    shaper = Shaper(path)
    chars = [(codepoint, chr(codepoint)) for codepoint in codepoints]
    pairs = {}
    for left_codepoint, left in chars:
        for right_codepoint, right in chars:
            value = shaper.adjustment(left, right)
            if value:
                pairs[f"U+{left_codepoint:04X} U+{right_codepoint:04X}"] = value
    return pairs


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
        reference_path = args.reference_dir / filename
        with TTFont(reference_path) as font:
            cmap = font.getBestCmap()
            styles[style] = {
                "reference_filename": filename,
                "reference_sha256": hashlib.sha256(reference_path.read_bytes()).hexdigest(),
                "reference_size": reference_path.stat().st_size,
                "reference_version": font["name"].getDebugName(5),
                "reference_unique_id": font["name"].getDebugName(3),
                "font_revision": font["head"].fontRevision,
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
                "pair_adjustments": pair_adjustments(reference_path, codepoints),
            }
        print(f"{style}: {len(styles[style]['pair_adjustments'])} non-zero pairs")
    payload = {
        "schema": 2,
        "description": "Numeric layout metrics only; contains no Times New Roman outlines.",
        "charset": "data/document-charset.txt",
        "styles": styles,
    }
    output = args.output if args.output.is_absolute() else root / args.output
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
