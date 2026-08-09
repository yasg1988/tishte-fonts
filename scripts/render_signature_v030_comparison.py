#!/usr/bin/env python3
"""Render a focused comparison of the v0.030 cross-script terminal system."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASELINE = Path("build/TishteSerif-Regular-v020.ttf")
ITERATION = Path("build/TishteSerif-Regular-v030.ttf")
OUTPUT = Path("artifacts/specimens/tishte-signature-v030-comparison.png")


def face(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def main():
    image = Image.new("RGB", (1800, 1700), "#f7f5ef")
    draw = ImageDraw.Draw(image)
    ink, accent, muted = "#17211d", "#8f2434", "#69736f"
    draw.rectangle((0, 0, 42, 1700), fill=accent)
    draw.text((130, 80), "TISHTE SERIF · TERMINALS v0.030", font=face(ITERATION, 62), fill=accent)
    draw.text((130, 168), "Один характер среза для кириллицы, латиницы и цифр", font=face(ITERATION, 30), fill=muted)

    groups = [
        ("КИРИЛЛИЦА", "Ж ж   У   Я я"),
        ("ЛАТИНИЦА", "A M R"),
        ("ЦИФРЫ", "1 4 7"),
    ]
    y = 285
    for label, sample in groups:
        draw.text((130, y), label, font=face(ITERATION, 23), fill=accent)
        draw.text((330, y - 45), sample, font=face(BASELINE, 130), fill=ink)
        draw.text((1280, y), "v0.020", font=face(BASELINE, 22), fill=muted)
        y += 165
        draw.text((330, y - 45), sample, font=face(ITERATION, 130), fill=ink)
        draw.text((1280, y), "v0.030", font=face(ITERATION, 22), fill=accent)
        y += 185
        draw.line((130, y, 1670, y), fill="#c9c8c1", width=2)
        y += 45

    draw.text((130, 1580), "Малые углы рассчитаны для печати и экранных размеров 10–14 pt.", font=face(ITERATION, 27), fill=muted)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
