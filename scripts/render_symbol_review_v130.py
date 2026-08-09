#!/usr/bin/env python3
"""Render large v0.920/v0.930 numeral and symbol comparison sheets."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


LINES = (
    "0123456789 · 48 750,00",
    "₽ $ € £ ¥ ¢ · № 125 · 25% 5‰",
    "+ - × ÷ = ≠ ≈ ≤ ≥ ∞ √ ∑ ∆",
    "( ) [ ] { } « » · — – / \\",
    "! ? : ; … • † ‡ § ¶ © ® ™",
    "← ↑ → ↓ ↔",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    canvas = Image.new("RGB", (2700, 2200), "#f6f2ea")
    draw = ImageDraw.Draw(canvas)
    label = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
    title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 46)
    before = ImageFont.truetype(args.before, 84)
    after = ImageFont.truetype(args.after, 84)
    draw.text((90, 50), f"TISHTE SERIF v0.930 · SYMBOL REVIEW · {args.style}", font=title, fill="#202a32")
    y = 145
    for line in LINES:
        draw.text((90, y), "v0.920", font=label, fill="#59636b")
        draw.text((270, y - 18), line, font=before, fill="#44484b")
        y += 125
        draw.text((90, y), "v0.930", font=label, fill="#8b2338")
        draw.text((270, y - 18), line, font=after, fill="#8b2338")
        y += 165
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
