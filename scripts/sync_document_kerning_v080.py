#!/usr/bin/env python3
"""Add GPOS deltas so Tishte document pairs match Times New Roman kerning."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
import uharfbuzz as hb

from build_serif_family_v060 import STYLES
from font_metrics_audit import load_charset


FEATURES = {"kern": True, "liga": False, "clig": False}
SAFE_GLYPH_NAME = re.compile(r"^[A-Za-z_.][A-Za-z0-9_.]*$")


class Shaper:
    def __init__(self, path: Path):
        data = path.read_bytes()
        self.face = hb.Face(data)
        self.font = hb.Font(self.face)
        self.font.scale = (self.face.upem, self.face.upem)
        self.single_advances: dict[str, int] = {}

    def advance(self, text: str) -> int:
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.font, buffer, FEATURES)
        return sum(position.x_advance for position in buffer.glyph_positions)

    def single(self, char: str) -> int:
        if char not in self.single_advances:
            self.single_advances[char] = self.advance(char)
        return self.single_advances[char]

    def pair_adjustment(self, left: str, right: str) -> int:
        return self.advance(left + right) - self.single(left) - self.single(right)


def feature_glyph(name: str) -> str:
    return name if SAFE_GLYPH_NAME.match(name) else f"\\{name}"


def measure_deltas(reference: Path, candidate: Path, codepoints: list[int]) -> dict[tuple[str, str], int]:
    reference_shaper = Shaper(reference)
    candidate_shaper = Shaper(candidate)
    with TTFont(candidate, lazy=True) as font:
        cmap = font.getBestCmap()
        chars = [(chr(codepoint), cmap[codepoint]) for codepoint in codepoints]
    deltas: dict[tuple[str, str], int] = {}
    for left_char, left_glyph in chars:
        for right_char, right_glyph in chars:
            delta = (
                reference_shaper.pair_adjustment(left_char, right_char)
                - candidate_shaper.pair_adjustment(left_char, right_char)
            )
            if delta:
                key = (left_glyph, right_glyph)
                previous = deltas.get(key)
                if previous is not None and previous != delta:
                    raise ValueError(f"conflicting delta for {key}: {previous} != {delta}")
                deltas[key] = delta
    return deltas


def append_delta_lookup(path: Path, deltas: dict[tuple[str, str], int]) -> None:
    if not deltas:
        return
    statements = [
        f"  pos {feature_glyph(left)} {feature_glyph(right)} {value};"
        for (left, right), value in sorted(deltas.items())
    ]
    feature_text = "feature kern {\n" + "\n".join(statements) + "\n} kern;\n"

    with TTFont(path, recalcTimestamp=False) as compiler_font:
        addOpenTypeFeaturesFromString(compiler_font, feature_text, tables=["GPOS"])
        generated_lookups = compiler_font["GPOS"].table.LookupList.Lookup
        if len(generated_lookups) != 1:
            raise ValueError(f"expected one generated lookup, got {len(generated_lookups)}")
        delta_lookup = deepcopy(generated_lookups[0])

    with TTFont(path, recalcTimestamp=False) as font:
        gpos = font["GPOS"].table
        lookup_index = len(gpos.LookupList.Lookup)
        gpos.LookupList.Lookup.append(delta_lookup)
        gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
        kern_features = [
            record.Feature
            for record in gpos.FeatureList.FeatureRecord
            if record.FeatureTag == "kern"
        ]
        if not kern_features:
            raise ValueError("candidate GPOS has no kern feature")
        for feature in kern_features:
            feature.LookupListIndex.append(lookup_index)
            feature.LookupCount = len(feature.LookupListIndex)
        temporary = path.with_suffix(".kerning.ttf")
        font.save(temporary, reorderTables=True)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version-tag", default="v080")
    args = parser.parse_args()
    root = args.root.resolve()
    codepoints = load_charset(root / "data" / "document-charset.txt")
    report = {"version": "0.080", "styles": {}}
    for style in STYLES:
        reference = Path("C:/Windows/Fonts") / style.reference_name
        candidate = root / "build" / f"TishteSerif-{style.key}-{args.version_tag}.ttf"
        deltas = measure_deltas(reference, candidate, codepoints)
        append_delta_lookup(candidate, deltas)
        values = list(deltas.values())
        report["styles"][style.key] = {
            "pairs": len(deltas),
            "minimum_delta": min(values, default=0),
            "maximum_delta": max(values, default=0),
        }
        print(f"{style.key}: {len(deltas)} pairs")
    output = root / "artifacts" / "reports" / "kerning-deltas-v080.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
