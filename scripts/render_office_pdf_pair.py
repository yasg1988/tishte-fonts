#!/usr/bin/env python3
"""Rasterize a Times/Tishte PDF pair and create a visual QA contact sheet."""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


def render(pdf: Path, output_dir: Path, scale: float) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []
    with fitz.open(pdf) as document:
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            output = output_dir / f"page-{index}.png"
            pixmap.save(output)
            pages.append(output)
    return pages


def build_sheet(times: list[Path], tishte: list[Path], output: Path, title: str) -> None:
    if len(times) != len(tishte):
        raise ValueError(f"page-count mismatch: {len(times)} != {len(tishte)}")
    left = [Image.open(path).convert("RGB") for path in times]
    right = [Image.open(path).convert("RGB") for path in tishte]
    try:
        width = max(image.width for image in (*left, *right))
        height = max(image.height for image in (*left, *right))
        gap, header = 32, 72
        sheet = Image.new("RGB", (width * 2 + gap * 3, (height + gap) * len(left) + header), "#d8d6d2")
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        draw.text((gap, 20), f"{title} · TIMES NEW ROMAN", font=font, fill="#24211f")
        draw.text((width + gap * 2, 20), "TISHTE SERIF v0.060", font=font, fill="#8f2434")
        y = header
        for times_page, tishte_page in zip(left, right):
            sheet.paste(times_page, (gap, y))
            sheet.paste(tishte_page, (width + gap * 2, y))
            y += height + gap
        output.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(output, optimize=True)
    finally:
        for image in (*left, *right):
            image.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--times", type=Path, required=True)
    parser.add_argument("--tishte", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--scale", type=float, default=1.35)
    args = parser.parse_args()
    root = args.output.parent / "pages"
    times = render(args.times, root / "times", args.scale)
    tishte = render(args.tishte, root / "tishte", args.scale)
    build_sheet(times, tishte, args.output, args.title)
    print(f"pages={len(times)} output={args.output}")


if __name__ == "__main__":
    main()
