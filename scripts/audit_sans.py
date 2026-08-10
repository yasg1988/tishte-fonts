#!/usr/bin/env python3
"""Audit Tishte Sans coverage, naming, OpenType behavior and screen-family structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import unicodedata

from fontTools.ttLib import TTFont
import uharfbuzz as hb

from build_sans_family import STYLES
from font_metrics_audit import load_charset
from versioning import version_tag


REQUIRED_TABLES = {"cmap", "glyf", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post", "GDEF", "GSUB", "GPOS", "STAT", "gasp", "prep"}
REQUIRED_GLYPHS = "Русский Ёё Ӓӓ Ӧӧ Ӱӱ Ҥҥ Ӹӹ Latin ß 0123456789 № ₽ − ‑"
SMART_DROPOUT = b"\xb8\x01\xff\x85\xb0\x04\x8d"


def shape(path: Path, text: str) -> tuple[list[int], int]:
    data = path.read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return [info.codepoint for info in buffer.glyph_infos], sum(pos.x_advance for pos in buffer.glyph_positions)


def features(font: TTFont, table: str) -> set[str]:
    if table not in font:
        return set()
    records = font[table].table.FeatureList.FeatureRecord if font[table].table.FeatureList else []
    return {record.FeatureTag for record in records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    charset = load_charset(root / "data" / "document-charset.txt")
    report = {"version": args.version, "styles": {}, "passed": True}
    for style in STYLES:
        path = root / "build" / f"TishteSans-{style.key}-{tag}.ttf"
        with TTFont(path) as font:
            cmap = font.getBestCmap()
            missing = [f"U+{cp:04X}" for cp in charset if cp not in cmap]
            unexpected = [f"U+{cp:04X}" for cp in cmap if cp not in set(charset)]
            missing_tables = sorted(REQUIRED_TABLES - set(font.keys()))
            names = {name_id: font["name"].getDebugName(name_id) for name_id in (0, 1, 2, 4, 5, 6, 9, 10, 13, 14, 16, 17)}
            digits = [font["hmtx"].metrics[cmap[ord(char)]][0] for char in "0123456789"]
            operators = [font["hmtx"].metrics[cmap[ord(char)]][0] for char in "+=<>±×÷−≈≠≤≥"]
            gsub = features(font, "GSUB")
            gpos = features(font, "GPOS")
            no_variations = not any(table in font for table in ("fvar", "gvar", "HVAR", "MVAR"))
            no_glyph_hints = not any(table in font for table in ("fpgm", "cvt "))
            smart_dropout = SMART_DROPOUT in font["prep"].program.getBytecode()
            zero_line_gap = font["hhea"].lineGap == 0 and font["OS/2"].sTypoLineGap == 0
            expected_regular = style.weight < 700 and not style.italic
            regular_flag = bool(font["OS/2"].fsSelection & 64)
            digit_pair_widths = {
                pair: shape(path, pair)[1]
                for pair in ("00", "01", "10", "11", "12", "21", "99")
            }
            nfc_ids, nfc_width = shape(path, unicodedata.normalize("NFC", REQUIRED_GLYPHS))
            nfd_ids, nfd_width = shape(path, unicodedata.normalize("NFD", REQUIRED_GLYPHS))
            failures = []
            if missing or unexpected: failures.append("charset")
            if missing_tables: failures.append("tables")
            if names[9] != "Сергей Якунин": failures.append("designer")
            if "Copyright 2020 The Arimo Project Authors" not in (names[0] or ""): failures.append("copyright")
            expected_legacy_family = (
                "Tishte Sans"
                if style.weight in (400, 700)
                else f"Tishte Sans {'Medium' if style.weight == 500 else 'SemiBold'}"
            )
            expected_legacy_subfamily = (
                ("Bold Italic" if style.italic else "Bold")
                if style.weight == 700
                else ("Italic" if style.italic else "Regular")
            )
            if names[1] != expected_legacy_family or names[2] != expected_legacy_subfamily:
                failures.append("legacy_names")
            if names[16] != "Tishte Sans" or names[17] != style.subfamily: failures.append("typographic_names")
            if "Arimo" not in (names[10] or ""): failures.append("provenance")
            if names[13] is None or "SIL Open Font License" not in names[13]: failures.append("license")
            if len(set(digits)) != 1: failures.append("tabular_digits")
            if len(set(operators)) != 1: failures.append("math_widths")
            if len(set(digit_pair_widths.values())) != 1: failures.append("digit_kerning")
            if "ccmp" not in gsub or not {"kern", "mark", "mkmk"}.issubset(gpos): failures.append("layout_features")
            if not no_variations: failures.append("static_tables")
            if not no_glyph_hints: failures.append("stale_glyph_hints")
            if not smart_dropout: failures.append("smart_dropout")
            if not zero_line_gap: failures.append("line_gap")
            if regular_flag != expected_regular: failures.append("fsselection_regular")
            if 0 in nfc_ids or 0 in nfd_ids or nfc_width != nfd_width: failures.append("normalization")
            passed = not failures
            report["styles"][style.key] = {"path": str(path), "codepoints": len(cmap), "missing": missing, "unexpected": unexpected, "missing_tables": missing_tables, "names": names, "digit_widths": digits, "operator_widths": operators, "digit_pair_widths": digit_pair_widths, "zero_line_gap": zero_line_gap, "smart_dropout": smart_dropout, "gsub": sorted(gsub), "gpos": sorted(gpos), "nfc_glyphs": len(nfc_ids), "nfd_glyphs": len(nfd_ids), "normalization_width": nfc_width, "failures": failures, "passed": passed}
            report["passed"] &= passed
            print(f"{style.key}: {'passed' if passed else ', '.join(failures)}")
    output = root / "artifacts" / "reports" / f"sans-audit-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
