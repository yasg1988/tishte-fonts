#!/usr/bin/env python3
"""Rasterize native Word PDFs and build side-by-side QA contact sheets."""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


KINDS = ("order", "letter", "protocol", "table", "languages")


def rasterize(pdf_path: Path, output_dir: Path, scale: float = 1.7) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []
    document = fitz.open(pdf_path)
    try:
        matrix = fitz.Matrix(scale, scale)
        for index, page in enumerate(document):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            output = output_dir / f"page-{index + 1}.png"
            pixmap.save(output)
            pages.append(output)
    finally:
        document.close()
    return pages


def contact_sheet(kind: str, times_pages: list[Path], tishte_pages: list[Path], output: Path) -> None:
    if len(times_pages) != len(tishte_pages):
        raise ValueError(f"page-count mismatch for {kind}")
    opened_times = [Image.open(path).convert("RGB") for path in times_pages]
    opened_tishte = [Image.open(path).convert("RGB") for path in tishte_pages]
    try:
        page_width = max(image.width for image in (*opened_times, *opened_tishte))
        page_height = max(image.height for image in (*opened_times, *opened_tishte))
        gap, header = 40, 90
        canvas = Image.new(
            "RGB",
            (page_width * 2 + gap * 3, (page_height + gap) * len(opened_times) + header),
            "#d7d7d7",
        )
        draw = ImageDraw.Draw(canvas)
        label_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
        draw.text((gap, 22), f"{kind.upper()} · TIMES NEW ROMAN", font=label_font, fill="#202020")
        draw.text((page_width + gap * 2, 22), "TISHTE SERIF v0.040", font=label_font, fill="#8f2434")
        y = header
        for index, (times, tishte) in enumerate(zip(opened_times, opened_tishte), start=1):
            canvas.paste(times, (gap, y))
            canvas.paste(tishte, (page_width + gap * 2, y))
            draw.text((8, y + 8), str(index), font=small_font, fill="#555555")
            y += page_height + gap
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output, optimize=True)
    finally:
        for image in (*opened_times, *opened_tishte):
            image.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("artifacts/document-tests/v050"))
    args = parser.parse_args()
    pdf_dir = args.root / "pdf"
    png_root = args.root / "png"
    comparisons = args.root / "comparisons"
    for kind in KINDS:
        times = rasterize(pdf_dir / f"{kind}-times.pdf", png_root / f"{kind}-times")
        tishte = rasterize(pdf_dir / f"{kind}-tishte.pdf", png_root / f"{kind}-tishte")
        output = comparisons / f"{kind}-comparison.png"
        contact_sheet(kind, times, tishte, output)
        print(output)


if __name__ == "__main__":
    main()
