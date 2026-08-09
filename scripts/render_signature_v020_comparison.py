#!/usr/bin/env python3
"""Render the v0.020 signature across every required writing-system group."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASELINE = Path("build/TishteSerif-Regular-v010.ttf")
ITERATION = Path("build/TishteSerif-Regular-v020.ttf")
OUTPUT = Path("artifacts/specimens/tishte-signature-v020-comparison.png")


def face(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def main():
    image = Image.new("RGB", (1800, 1600), "#f7f5ef")
    draw = ImageDraw.Draw(image)
    ink = "#17211d"
    accent = "#8f2434"
    muted = "#69736f"

    draw.rectangle((0, 0, 42, 1600), fill=accent)
    draw.text((130, 80), "TISHTE SERIF · SIGNATURE v0.020", font=face(ITERATION, 62), fill=accent)
    draw.text((130, 168), "Латиница, марийские буквы, цифры и документные знаки", font=face(ITERATION, 30), fill=muted)

    groups = [
        ("ЛАТИНИЦА", "A i j   Ä Ö Ü   á é ñ ç"),
        ("КИРИЛЛИЦА И МАРИЙСКИЙ", "Д д   Ҥ ҥ   Ӓ ӓ Ӧ ӧ Ӱ ӱ"),
        ("ЦИФРЫ И ЗНАКИ", "1 4 7   . ! ? : •   № ※"),
    ]
    y = 280
    for label, sample in groups:
        draw.text((130, y), label, font=face(ITERATION, 23), fill=accent)
        y += 45
        draw.text((130, y), "каркас", font=face(BASELINE, 21), fill=muted)
        draw.text((310, y - 22), sample, font=face(BASELINE, 70), fill=ink)
        y += 105
        draw.text((130, y), "v0.020", font=face(ITERATION, 21), fill=accent)
        draw.text((310, y - 22), sample, font=face(ITERATION, 70), fill=ink)
        y += 145
        draw.line((130, y, 1670, y), fill="#c9c8c1", width=2)
        y += 48

    draw.text(
        (130, 1470),
        "Ромбовидные точки · направленные срезы · неизменная документная ширина",
        font=face(ITERATION, 27),
        fill=muted,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
