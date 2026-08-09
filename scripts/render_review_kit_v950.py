#!/usr/bin/env python3
"""Rasterize native Word review PDFs and record page images."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("artifacts/review/v0950"))
    parser.add_argument("--scale", type=float, default=1.7)
    args = parser.parse_args()
    pdf_dir = args.root / "pdf"
    png_root = args.root / "png"
    manifest = {"documents": {}}
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        output_dir = png_root / pdf_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        pages = []
        with fitz.open(pdf_path) as document:
            for index, page in enumerate(document, start=1):
                pixmap = page.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), alpha=False)
                output = output_dir / f"page-{index}.png"
                pixmap.save(output)
                pages.append(str(output))
        manifest["documents"][pdf_path.name] = {"pages": len(pages), "images": pages}
        print(f"{pdf_path.name}: {len(pages)} pages")
    output = args.root / "render-manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
