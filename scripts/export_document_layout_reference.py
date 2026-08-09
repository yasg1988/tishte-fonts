#!/usr/bin/env python3
"""Export non-outline Times New Roman line-wrap and pagination reference data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_document_layout import LINE_WIDTHS, LINES_PER_PAGE, shape_width, wrap


REFERENCES = {
    "Regular": "times.ttf",
    "Bold": "timesbd.ttf",
    "Italic": "timesi.ttf",
    "BoldItalic": "timesbi.ttf",
}


def line_digest(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--reference-dir", type=Path, default=Path("C:/Windows/Fonts"))
    parser.add_argument("--output", type=Path, default=Path("data/times-new-roman-layout.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    corpus = json.loads((root / "data" / "language-corpus.json").read_text(encoding="utf-8"))
    paragraphs = [line for lines in corpus["sections"].values() for line in lines]
    result = {"schema": 1, "description": "Line-break and pagination results only; contains no Times New Roman outlines.", "styles": {}}

    for style, filename in REFERENCES.items():
        font_path = args.reference_dir / filename
        cases = []
        for paragraph_index, paragraph in enumerate(paragraphs):
            for width in LINE_WIDTHS:
                lines = wrap(paragraph.split(), width, lambda text: shape_width(font_path, text))
                cases.append({"paragraph": paragraph_index, "width": width, "lines": lines, "digest": line_digest(lines)})
        long_document = " ".join(paragraphs * 20).split()
        pagination = []
        for width in LINE_WIDTHS:
            lines = wrap(long_document, width, lambda text: shape_width(font_path, text))
            for page_size in LINES_PER_PAGE:
                pagination.append({"width": width, "lines_per_page": page_size, "line_count": len(lines), "pages": (len(lines) + page_size - 1) // page_size})
        result["styles"][style] = {"reference_filename": filename, "cases": cases, "pagination": pagination}
        print(f"{style}: {len(cases)} line-wrap cases, {len(pagination)} pagination cases")

    output = args.output if args.output.is_absolute() else root / args.output
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
