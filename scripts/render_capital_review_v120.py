#!/usr/bin/env python3
"""Render a large side-by-side review sheet for the v0.120 capital system."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


LINES = (
    "ABCDEFGHIJKLM",
    "NOPQRSTUVWXYZ",
    "АБВГДЕЁЖЗИЙКЛМ",
    "НОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
    "Ӓ Ӧ Ӱ Ӹ Ҥ · МАРИЙ ЭЛ",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    canvas = Image.new("RGB", (2600, 1900), "#f6f2ea")
    draw = ImageDraw.Draw(canvas)
    label = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
    title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
    before = ImageFont.truetype(args.before, 88)
    after = ImageFont.truetype(args.after, 88)
    draw.text((100, 55), f"TISHTE SERIF v0.920 · CAPITAL REVIEW · {args.style}", font=title, fill="#202a32")
    y = 155
    for line in LINES:
        draw.text((100, y), "v0.910", font=label, fill="#59636b")
        draw.text((280, y - 18), line, font=before, fill="#44484b")
        y += 135
        draw.text((100, y), "v0.920", font=label, fill="#8b2338")
        draw.text((280, y - 18), line, font=after, fill="#8b2338")
        y += 175
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
