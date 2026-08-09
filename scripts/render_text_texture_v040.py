#!/usr/bin/env python3
"""Compare the v0.040 lowercase texture with its v0.030 baseline."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASELINE = Path("build/TishteSerif-Regular-v030.ttf")
ITERATION = Path("build/TishteSerif-Regular-v040.ttf")
OUTPUT = Path("artifacts/specimens/tishte-text-texture-v040-comparison.png")


def face(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def main():
    image = Image.new("RGB", (1800, 1700), "#f7f5ef")
    draw = ImageDraw.Draw(image)
    ink, accent, muted = "#17211d", "#8f2434", "#69736f"
    draw.rectangle((0, 0, 42, 1700), fill=accent)
    draw.text((130, 80), "TISHTE SERIF · TEXT TEXTURE v0.040", font=face(ITERATION, 60), fill=accent)
    draw.text((130, 165), "Частотные строчные в кириллице и латинице", font=face(ITERATION, 30), fill=muted)

    draw.text((130, 285), "КОНТРОЛЬНЫЕ ФОРМЫ", font=face(ITERATION, 23), fill=accent)
    sample = "а е н о р с у   a e n o p c u"
    draw.text((130, 335), sample, font=face(BASELINE, 92), fill=ink)
    draw.text((130, 455), sample, font=face(ITERATION, 92), fill=ink)
    draw.text((1450, 365), "v0.030", font=face(BASELINE, 22), fill=muted)
    draw.text((1450, 485), "v0.040", font=face(ITERATION, 22), fill=accent)

    draw.line((130, 600, 1670, 600), fill="#c9c8c1", width=2)
    samples = [
        "Настоящее решение направлено на развитие региона и повышение качества услуг.",
        "Марий Эл — республика с современной цифровой и документной средой.",
        "Regional services remain clear, stable and readable in every document.",
    ]
    y = 665
    for text in samples:
        draw.text((130, y), "v0.030", font=face(BASELINE, 20), fill=muted)
        draw.text((285, y - 12), text, font=face(BASELINE, 34), fill=ink)
        y += 72
        draw.text((130, y), "v0.040", font=face(ITERATION, 20), fill=accent)
        draw.text((285, y - 12), text, font=face(ITERATION, 34), fill=ink)
        y += 125

    draw.line((130, 1290, 1670, 1290), fill="#c9c8c1", width=2)
    draw.text((130, 1350), "МАЛЫЙ КЕГЛЬ", font=face(ITERATION, 23), fill=accent)
    small = "Распоряжение № 147: региональные органы обеспечивают хранение документов."
    draw.text((130, 1410), small, font=face(BASELINE, 25), fill=ink)
    draw.text((130, 1470), small, font=face(ITERATION, 25), fill=ink)
    draw.text((130, 1590), "Все строки сохраняют исходную документную длину.", font=face(ITERATION, 25), fill=muted)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
