#!/usr/bin/env python3
"""Render a focused before/after sheet for the first Tishte signature."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASELINE = Path("build/TishteSerif-Regular.ttf")
ITERATION = Path("build/TishteSerif-Regular-v010.ttf")
OUTPUT = Path("artifacts/specimens/tishte-signature-v010-comparison.png")


def face(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def main():
    image = Image.new("RGB", (1800, 1050), "#f7f5ef")
    draw = ImageDraw.Draw(image)
    ink = "#17211d"
    accent = "#8f2434"
    muted = "#69736f"

    draw.rectangle((0, 0, 42, 1050), fill=accent)
    draw.text((130, 90), "TISHTE SERIF · SIGNATURE v0.010", font=face(ITERATION, 65), fill=accent)
    draw.text((130, 180), "Первый собственный штрих при неизменных метриках", font=face(ITERATION, 31), fill=muted)

    sample = "Ӓ ӓ   Ӧ ӧ   Ӱ ӱ    1 4 7"
    draw.text((130, 310), "БАЗОВЫЙ КАРКАС", font=face(BASELINE, 24), fill=muted)
    draw.text((130, 360), sample, font=face(BASELINE, 132), fill=ink)

    draw.line((130, 575, 1670, 575), fill="#b8b9b4", width=2)
    draw.text((130, 635), "TISHTE v0.010", font=face(ITERATION, 24), fill=accent)
    draw.text((130, 685), sample, font=face(ITERATION, 132), fill=ink)

    draw.text(
        (130, 905),
        "Изменены: форма диакритики, верхний терминал 1 и диагональный срез 7.",
        font=face(ITERATION, 28),
        fill=muted,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
