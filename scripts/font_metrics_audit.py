#!/usr/bin/env python3
"""Compare document-critical metrics of two OpenType fonts.

The tool reads fonts in place and never copies or modifies them. It is intended
for engineering verification, not as a legal conclusion that a candidate is a
metric analogue under a particular regulation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from fontTools.ttLib import TTFont


VERTICAL_FIELDS = {
    "hhea": ("ascent", "descent", "lineGap"),
    "OS/2": (
        "sTypoAscender",
        "sTypoDescender",
        "sTypoLineGap",
        "usWinAscent",
        "usWinDescent",
        "fsSelection",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_charset(path: Path | None) -> list[int]:
    if path is None:
        return []
    codepoints: set[int] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        codepoints.update(ord(char) for char in line)
    return sorted(codepoints)


def best_unicode_cmap(font: TTFont) -> dict[int, str]:
    cmap = font.getBestCmap()
    if not cmap:
        raise ValueError("Font has no usable Unicode cmap")
    return cmap


def normalized_advance(font: TTFont, glyph_name: str) -> float:
    advance, _lsb = font["hmtx"].metrics[glyph_name]
    return advance / font["head"].unitsPerEm


def normalized_vertical_metrics(font: TTFont) -> dict[str, float | int]:
    upm = font["head"].unitsPerEm
    result: dict[str, float | int] = {}
    for table_name, fields in VERTICAL_FIELDS.items():
        table = font[table_name]
        for field in fields:
            value = getattr(table, field)
            key = f"{table_name}.{field}"
            result[key] = value if field == "fsSelection" else value / upm
    return result


def font_name(font: TTFont) -> str:
    for name_id in (6, 4, 1):
        value = font["name"].getDebugName(name_id)
        if value:
            return value
    return "unknown"


def compare(reference_path: Path, candidate_path: Path, charset: list[int]) -> dict[str, Any]:
    with TTFont(reference_path, lazy=False) as reference, TTFont(candidate_path, lazy=False) as candidate:
        reference_cmap = best_unicode_cmap(reference)
        candidate_cmap = best_unicode_cmap(candidate)
        requested = charset or sorted(set(reference_cmap) | set(candidate_cmap))

        missing_reference: list[str] = []
        missing_candidate: list[str] = []
        width_mismatches: list[dict[str, Any]] = []
        compared = 0

        for codepoint in requested:
            ref_glyph = reference_cmap.get(codepoint)
            cand_glyph = candidate_cmap.get(codepoint)
            char_label = f"U+{codepoint:04X} {chr(codepoint)}"
            if ref_glyph is None:
                missing_reference.append(char_label)
                continue
            if cand_glyph is None:
                missing_candidate.append(char_label)
                continue
            compared += 1
            ref_width = normalized_advance(reference, ref_glyph)
            cand_width = normalized_advance(candidate, cand_glyph)
            if abs(ref_width - cand_width) > 1e-9:
                width_mismatches.append(
                    {
                        "character": char_label,
                        "reference": ref_width,
                        "candidate": cand_width,
                        "delta": cand_width - ref_width,
                    }
                )

        ref_vertical = normalized_vertical_metrics(reference)
        cand_vertical = normalized_vertical_metrics(candidate)
        vertical_mismatches = {
            key: {
                "reference": ref_vertical[key],
                "candidate": cand_vertical[key],
            }
            for key in ref_vertical
            if ref_vertical[key] != cand_vertical[key]
        }

        passed = not missing_candidate and not width_mismatches and not vertical_mismatches
        return {
            "passed": passed,
            "scope_note": "Advance widths and vertical metrics only; GPOS and application pagination require separate tests.",
            "reference": {
                "path": str(reference_path.resolve()),
                "sha256": sha256(reference_path),
                "font_name": font_name(reference),
                "units_per_em": reference["head"].unitsPerEm,
            },
            "candidate": {
                "path": str(candidate_path.resolve()),
                "sha256": sha256(candidate_path),
                "font_name": font_name(candidate),
                "units_per_em": candidate["head"].unitsPerEm,
            },
            "summary": {
                "requested_codepoints": len(requested),
                "compared_codepoints": compared,
                "missing_in_reference": len(missing_reference),
                "missing_in_candidate": len(missing_candidate),
                "width_mismatches": len(width_mismatches),
                "vertical_mismatches": len(vertical_mismatches),
            },
            "missing_in_reference": missing_reference,
            "missing_in_candidate": missing_candidate,
            "width_mismatches": width_mismatches,
            "vertical_mismatches": vertical_mismatches,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--charset", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = compare(
        args.reference,
        args.candidate,
        load_charset(args.charset),
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

