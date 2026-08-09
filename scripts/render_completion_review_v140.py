#!/usr/bin/env python3
"""Render v0.930/v0.940 residual glyph comparison sheets."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


LINES = (
    "Г П  Ҥ ҥ  Ӹ ӹ",
    "Æ Ð Ø Þ  æ ð ø þ  Œ œ  Ŋ ŋ",
    "Đ đ  Ħ ħ  Ł ł  Ŧ ŧ  ı ĵ",
    "ì í î ï  ĩ ī ĭ  Å",
    "¹ ² ³  ¼ ½ ¾  µ  ·  ≈",
    "À Á Â Ã Ā Ă Ȧ Ä Å A̋ Ǎ A̧ Ą",
    "à á â ã ā ă ȧ ä å a̋ ǎ a̧ ą",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    canvas = Image.new("RGB", (2800, 2300), "#f6f2ea")
    draw = ImageDraw.Draw(canvas)
    label = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
    title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
    before = ImageFont.truetype(args.before, 88)
    after = ImageFont.truetype(args.after, 88)
    draw.text((90, 50), f"TISHTE SERIF v0.940 · COMPLETION REVIEW · {args.style}", font=title, fill="#202a32")
    y = 145
    for line in LINES:
        draw.text((90, y), "v0.930", font=label, fill="#59636b")
        draw.text((270, y - 20), line, font=before, fill="#44484b")
        y += 120
        draw.text((90, y), "v0.940", font=label, fill="#8b2338")
        draw.text((270, y - 20), line, font=after, fill="#8b2338")
        y += 175
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
