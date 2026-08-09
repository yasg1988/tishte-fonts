#!/usr/bin/env python3
"""Audit the static-family OpenType contract for Tishte Serif v0.120+."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont
import uharfbuzz as hb


REQUIRED_TABLES = ("GDEF", "GSUB", "GPOS", "STAT")
REQUIRED_GSUB = {"ccmp"}
REQUIRED_GPOS = {"kern", "mark", "mkmk"}
SHAPING_CASES = {
    "latin_marks": "A\u0308 a\u0328",
    "cyrillic_marks": "А\u0308 а\u0308",
    "meadow_mari": "Ӓӓ Ӧӧ Ӱӱ Ҥҥ",
    "hill_mari": "Ӓӓ Ӧӧ Ӱӱ Ӹӹ",
}


def feature_tags(font: TTFont, table: str) -> set[str]:
    feature_list = font[table].table.FeatureList
    return set() if feature_list is None else {record.FeatureTag for record in feature_list.FeatureRecord}


def shape(path: Path, text: str, features: dict[str, bool] | None = None) -> dict:
    data = path.read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, features)
    return {
        "glyph_ids": [info.codepoint for info in buffer.glyph_infos],
        "advances": [position.x_advance for position in buffer.glyph_positions],
        "notdef": sum(info.codepoint == 0 for info in buffer.glyph_infos),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.120")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = "v" + args.version.partition(".")[2]
    styles = {}
    for style in ("Regular", "Bold", "Italic", "BoldItalic"):
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        with TTFont(path) as font:
            missing_tables = sorted(set(REQUIRED_TABLES) - set(font.keys()))
            missing_gsub = sorted(REQUIRED_GSUB - feature_tags(font, "GSUB")) if "GSUB" in font else sorted(REQUIRED_GSUB)
            missing_gpos = sorted(REQUIRED_GPOS - feature_tags(font, "GPOS")) if "GPOS" in font else sorted(REQUIRED_GPOS)
            cmap = font.getBestCmap()
            digit_widths = [font["hmtx"].metrics[cmap[codepoint]][0] for codepoint in range(0x30, 0x3A)]
            combining_widths = {
                f"U+{codepoint:04X}": font["hmtx"].metrics[cmap[codepoint]][0]
                for codepoint in (0x0300, 0x0308, 0x0328)
            }
        shaping = {name: shape(path, text) for name, text in SHAPING_CASES.items()}
        kerning = {}
        for name, text in {"latin": "AV", "cyrillic": "ТА"}.items():
            enabled = shape(path, text, {"kern": True})
            disabled = shape(path, text, {"kern": False})
            kerning[name] = {
                "enabled": sum(enabled["advances"]),
                "disabled": sum(disabled["advances"]),
                "active": enabled["advances"] != disabled["advances"],
            }
        failures = []
        if missing_tables: failures.append({"missing_tables": missing_tables})
        if missing_gsub: failures.append({"missing_gsub": missing_gsub})
        if missing_gpos: failures.append({"missing_gpos": missing_gpos})
        if len(set(digit_widths)) != 1: failures.append({"non_tabular_digits": digit_widths})
        if any(combining_widths.values()): failures.append({"combining_widths": combining_widths})
        if any(value["notdef"] for value in shaping.values()): failures.append({"shaping_notdef": shaping})
        if not all(value["active"] for value in kerning.values()): failures.append({"inactive_kerning": kerning})
        styles[style] = {
            "missing_tables": missing_tables,
            "missing_gsub_features": missing_gsub,
            "missing_gpos_features": missing_gpos,
            "digit_widths": digit_widths,
            "combining_widths": combining_widths,
            "shaping": shaping,
            "kerning": kerning,
            "failures": failures,
            "passed": not failures,
        }
    report = {"version": args.version, "styles": styles, "passed": all(item["passed"] for item in styles.values())}
    output = root / "artifacts" / "reports" / f"opentype-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
