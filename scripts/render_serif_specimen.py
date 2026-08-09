#!/usr/bin/env python3
"""Render a baseline PNG specimen for visual regression and review."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


WIDTH = 1800
HEIGHT = 2400
MARGIN = 150
INK = "#17211d"
ACCENT = "#8f2434"
MUTED = "#69736f"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, face: ImageFont.FreeTypeFont, fill: str = INK, spacing: int = 8) -> int:
    draw.multiline_text(xy, text, font=face, fill=fill, spacing=spacing)
    box = draw.multiline_textbbox(xy, text, font=face, spacing=spacing)
    return box[3]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: list[str] = []
    current: list[str] = []
    for word in text.split():
        candidate = " ".join((*current, word))
        if current and draw.textlength(candidate, font=face) > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def render(font_path: Path, output: Path) -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#f7f5ef")
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, 42, HEIGHT), fill=ACCENT)
    y = MARGIN
    y = draw_text(draw, (MARGIN, y), "TISHTE SERIF", font(font_path, 108), ACCENT)
    y += 18
    with TTFont(font_path, lazy=True) as metadata_font:
        version_label = metadata_font["name"].getDebugName(5) or "development version"
    y = draw_text(
        draw,
        (MARGIN, y),
        f"Инженерный метрический каркас · {version_label}",
        font(font_path, 34),
        MUTED,
    )
    y += 78

    sections = [
        ("КИРИЛЛИЦА", "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ\nабвгдеёжзийклмнопрстуфхцчшщъыьэюя", 42),
        ("МАРИЙСКИЕ БУКВЫ", "Ӓ ӓ   Ӧ ӧ   Ӱ ӱ   Ҥ ҥ", 72),
        ("ЛАТИНИЦА", "ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz", 46),
        ("ЦИФРЫ И ДОКУМЕНТНЫЕ ЗНАКИ", "0123456789   № 12/2026   1 250 000,00 ₽", 52),
        ("СПЕЦСИМВОЛЫ", "$ € £ ¥ ¢ ₽   § ¶ • † ‡ ※   ± × ÷ ≠ ≤ ≥   ← ↑ → ↓ ↔", 38),
    ]

    for label, content, size in sections:
        y = draw_text(draw, (MARGIN, y), label, font(font_path, 25), ACCENT)
        y += 14
        y = draw_text(draw, (MARGIN, y), content, font(font_path, size), INK, spacing=18)
        y += 55

    draw.line((MARGIN, y, WIDTH - MARGIN, y), fill="#b8b9b4", width=2)
    y += 55
    y = draw_text(draw, (MARGIN, y), "ПРАВИТЕЛЬСТВО РЕСПУБЛИКИ МАРИЙ ЭЛ", font(font_path, 45), INK)
    y += 20
    y = draw_text(draw, (MARGIN, y), "О развитии региональной типографической системы", font(font_path, 38), ACCENT)
    y += 42

    paragraph = (
        "Настоящий документ устанавливает единые требования к оформлению, обработке, "
        "хранению и использованию документов органов исполнительной власти Республики "
        "Марий Эл. Контрольная строка используется для оценки ритма, читаемости и "
        "сохранения документной раскладки."
    )
    paragraph_face = font(font_path, 31)
    paragraph = wrap_text(draw, paragraph, paragraph_face, WIDTH - 2 * MARGIN)
    y = draw_text(draw, (MARGIN, y), paragraph, paragraph_face, INK, spacing=16)
    y += 65

    for point_size, pixel_size in ((14, 37), (12, 32), (10, 27)):
        label = f"{point_size} pt"
        line = "Приказ, письмо, таблица: Ӓ Ӧ Ӱ Ҥ — 2026 год — № 125 — 48 750,00 ₽"
        y = draw_text(draw, (MARGIN, y), label, font(font_path, 23), ACCENT)
        y += 8
        y = draw_text(draw, (MARGIN, y), line, font(font_path, pixel_size), INK)
        y += 28

    draw_text(draw, (MARGIN, HEIGHT - 110), f"Tishte Serif · {version_label} · not for release", font(font_path, 24), MUTED)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=Path("build/TishteSerif-Regular.ttf"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/specimens/tishte-serif-v001.png"))
    args = parser.parse_args()
    render(args.font, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
