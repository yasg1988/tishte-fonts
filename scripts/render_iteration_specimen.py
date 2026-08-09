#!/usr/bin/env python3
"""Render a compact two-version visual comparison for design review."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


LINES = (
    "Tishte Serif · Правительство Республики Марий Эл",
    "Марий Эл Республикын Кугыжаныш Погынжо",
    "Шачмы йӹлмем ылеш сӹлнӹ · Ӓ Ӧ Ӱ Ӹ Ҥ",
    "Д Ж Л У Я · д ж л у я · ABCDEFG · abcdefg",
    "№ 125 · 48 750,00 ₽ · 0123456789 · € £ ¥",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--label-before", required=True)
    parser.add_argument("--label-after", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    canvas = Image.new("RGB", (2200, 1500), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    sans = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
    fonts = [
        (args.label_before, ImageFont.truetype(args.before, 54), "#4b4b4b"),
        (args.label_after, ImageFont.truetype(args.after, 54), "#7b2638"),
    ]
    draw.text((100, 65), "TISHTE SERIF · DESIGN ITERATION", font=ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 44), fill="#1f2933")
    y = 155
    for line in LINES:
        for label, font, colour in fonts:
            draw.text((100, y + 14), label, font=sans, fill=colour)
            draw.text((310, y), line, font=font, fill=colour)
            y += 100
        y += 32
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
