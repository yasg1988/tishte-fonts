#!/usr/bin/env python3
"""Audit practical line wrapping and pagination against the numeric contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import uharfbuzz as hb

from build_serif_family import STYLES
from versioning import version_tag


FEATURES = {"kern": True, "liga": False, "clig": False}
LINE_WIDTHS = (9000, 12000, 16000, 22000)
LINES_PER_PAGE = (28, 36, 48)


def shape_width(path: Path, text: str) -> int:
    data = path.read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, FEATURES)
    return sum(position.x_advance for position in buffer.glyph_positions)


def wrap(words: list[str], width: int, measure) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if current and measure(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def line_digest(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    corpus = json.loads((root / "data" / "language-corpus.json").read_text(encoding="utf-8"))
    reference = json.loads((root / "data" / "times-new-roman-layout.json").read_text(encoding="utf-8"))
    paragraphs = [line for lines in corpus["sections"].values() for line in lines]
    report = {"version": args.version, "styles": {}, "passed": True}

    for style in STYLES:
        font_path = root / "build" / f"TishteSerif-{style.key}-{tag}.ttf"
        reference_style = reference["styles"][style.key]
        mismatches = []
        total_cases = 0
        page_cases = []
        expected_cases = {(case["paragraph"], case["width"]): case for case in reference_style["cases"]}
        for paragraph_index, paragraph in enumerate(paragraphs):
            words = paragraph.split()
            for width in LINE_WIDTHS:
                actual = wrap(words, width, lambda text: shape_width(font_path, text))
                expected = expected_cases[(paragraph_index, width)]["lines"]
                total_cases += 1
                if actual != expected:
                    mismatches.append({"width": width, "text": paragraph, "expected": expected, "actual": actual})
        long_document = " ".join(paragraphs * 20).split()
        for width in LINE_WIDTHS:
            actual_lines = wrap(long_document, width, lambda text: shape_width(font_path, text))
            expected_page_cases = {(case["width"], case["lines_per_page"]): case for case in reference_style["pagination"]}
            for page_size in LINES_PER_PAGE:
                actual_pages = (len(actual_lines) + page_size - 1) // page_size
                expected_case = expected_page_cases[(width, page_size)]
                expected_pages = expected_case["pages"]
                page_cases.append({"width": width, "lines_per_page": page_size, "pages": actual_pages})
                if actual_pages != expected_pages:
                    mismatches.append({"width": width, "lines_per_page": page_size, "expected_pages": expected_pages, "actual_pages": actual_pages, "expected_line_count": expected_case["line_count"], "actual_line_count": len(actual_lines), "actual_digest": line_digest(actual_lines)})
        style_passed = not mismatches
        report["styles"][style.key] = {"line_wrap_cases": total_cases, "page_cases": page_cases, "mismatches": mismatches, "passed": style_passed}
        report["passed"] &= style_passed
        print(f"{style.key}: {total_cases} line-wrap cases, {len(page_cases)} pagination cases, {len(mismatches)} mismatches")

    output = root / "artifacts" / "reports" / f"document-layout-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
