#!/usr/bin/env python3
"""Render a real-font UI and small-size proof for Tishte Sans."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "artifacts" / "specimens" / "tishte-sans-v1000-screen-audit.png"
    paths = {style: root / "build" / f"TishteSans-{style}-v1000.ttf" for style in ("Regular", "Medium", "SemiBold", "Bold")}
    canvas = Image.new("RGB", (1920, 1280), "#eef1f3")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1920, 124), fill="#13202b")
    draw.text((58, 28), "Tishte Sans — экранная проверка", font=font(paths["SemiBold"], 48), fill="white")
    draw.text((60, 87), "Реальные TTF · кегли 11–32 px · русский · два марийских языка · Latin", font=font(paths["Regular"], 19), fill="#bbc8d1")
    panels = [(48, 164, 928, 602), (992, 164, 1872, 602), (48, 642, 928, 1230), (992, 642, 1872, 1230)]
    for box in panels:
        draw.rounded_rectangle(box, radius=18, fill="white", outline="#d8dde1", width=2)
    x, y = 82, 194
    draw.text((x, y), "Панель показателей", font=font(paths["SemiBold"], 29), fill="#13202b")
    cards = [(x, y + 65, "Заявки", "1 284", "+12,4 %"), (x + 270, y + 65, "Бюджет", "₽ 2,58 млн", "+4,1 %"), (x + 540, y + 65, "Срок", "12.08.2026", "№ 147-р")]
    for cx, cy, title, value, note in cards:
        draw.rounded_rectangle((cx, cy, cx + 240, cy + 170), radius=12, fill="#f5f7f8")
        draw.text((cx + 18, cy + 16), title, font=font(paths["Medium"], 18), fill="#67747d")
        draw.text((cx + 18, cy + 58), value, font=font(paths["Bold"], 29), fill="#13202b")
        draw.text((cx + 18, cy + 117), note, font=font(paths["Regular"], 17), fill="#851a32")
    draw.text((x, y + 278), "Последнее обновление: сегодня, 09:42", font=font(paths["Regular"], 16), fill="#67747d")
    draw.rounded_rectangle((x, y + 324, x + 215, y + 374), radius=9, fill="#851a32")
    draw.text((x + 26, y + 337), "Открыть отчёт", font=font(paths["SemiBold"], 18), fill="white")

    x, y = 1026, 194
    draw.text((x, y), "Навигация и состояния", font=font(paths["SemiBold"], 29), fill="#13202b")
    items = ["Обзор", "Документы", "Жители", "Кугыжаныш", "Настройки"]
    for i, item in enumerate(items):
        iy = y + 67 + i * 57
        if i == 1:
            draw.rounded_rectangle((x, iy - 9, x + 460, iy + 38), radius=8, fill="#f4e8eb")
        draw.text((x + 18, iy), item, font=font(paths["Medium"] if i == 1 else paths["Regular"], 20), fill="#851a32" if i == 1 else "#27343d")
    draw.text((x + 530, y + 68), "Статус", font=font(paths["Medium"], 16), fill="#67747d")
    draw.rounded_rectangle((x + 530, y + 101, x + 748, y + 148), radius=23, fill="#e5f3eb")
    draw.text((x + 557, y + 113), "•  Опубликовано", font=font(paths["Medium"], 16), fill="#22633d")
    draw.text((x + 530, y + 184), "Введите запрос", font=font(paths["Regular"], 15), fill="#67747d")
    draw.rounded_rectangle((x + 530, y + 214, x + 790, y + 266), radius=8, outline="#aeb7bd", width=2)
    draw.text((x + 547, y + 228), "Поиск…", font=font(paths["Regular"], 17), fill="#849099")

    x, y = 82, 672
    draw.text((x, y), "Малые экранные кегли", font=font(paths["SemiBold"], 29), fill="#13202b")
    samples = [11, 12, 14, 16, 20, 24, 32]
    sy = y + 62
    for size in samples:
        draw.text((x, sy), f"{size} px", font=font(paths["Medium"], 16), fill="#851a32")
        draw.text((x + 85, sy), "Марий Эл · Ӓвылым · Ӧндалан · Ӱдыр · Кугыжаныш", font=font(paths["Regular"], size), fill="#13202b")
        sy += max(48, size + 20)

    x, y = 1026, 672
    draw.text((x, y), "Начертания и символы", font=font(paths["SemiBold"], 29), fill="#13202b")
    rows = [("Regular", paths["Regular"]), ("Medium", paths["Medium"]), ("SemiBold", paths["SemiBold"]), ("Bold", paths["Bold"])]
    sy = y + 64
    for name, path in rows:
        draw.text((x, sy), name, font=font(path, 22), fill="#851a32")
        draw.text((x + 170, sy), "Aa Бб Ӓӓ Ӧӧ Ӱӱ Ҥҥ Ӹӹ 012 № ₽ %", font=font(path, 25), fill="#13202b")
        sy += 68
    draw.line((x, sy + 4, 1835, sy + 4), fill="#d8dde1", width=2)
    sy += 35
    draw.text((x, sy), "← ↑ → ↓ ↔   + − × ÷ = ≠ ≤ ≥   © ® ™", font=font(paths["Regular"], 28), fill="#13202b")
    draw.text((x, sy + 70), "Latin: Interface, Dashboard & Search", font=font(paths["Medium"], 25), fill="#13202b")
    draw.text((x, sy + 132), "Кириллица: документы и уведомления", font=font(paths["Regular"], 25), fill="#13202b")

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
