#!/usr/bin/env python3
"""Render the Tishte Sans specimen card using the real release fonts."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 3072, 2048
MARGIN = 68
PAPER, INK, ACCENT, MUTED, RULE = "#f7f8f7", "#101923", "#851a32", "#657078", "#c8cdd0"


def face(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def fit(draw: ImageDraw.ImageDraw, path: Path, text: str, width: int, size: int, minimum: int = 15) -> ImageFont.FreeTypeFont:
    while size > minimum and draw.textbbox((0, 0), text, font=face(path, size))[2] > width:
        size -= 1
    return face(path, size)


def label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, regular: Path, width: int) -> None:
    draw.text((x, y), text.upper(), font=fit(draw, regular, text.upper(), width, 23), fill=ACCENT)


def line(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.line((MARGIN, y, WIDTH - MARGIN, y), fill=RULE, width=2)


def vertical(draw: ImageDraw.ImageDraw, x: int, y1: int, y2: int) -> None:
    draw.line((x, y1, x, y2), fill=RULE, width=2)


def fitted(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, path: Path, width: int, size: int, color: str = INK) -> None:
    draw.text((x, y), text, font=fit(draw, path, text, width, size), fill=color)


def render(font_dir: Path, output: Path) -> None:
    style_names = (
        "Regular", "Italic", "Medium", "MediumItalic", "SemiBold",
        "SemiBoldItalic", "Bold", "BoldItalic", "ExtraBold", "ExtraBoldItalic",
    )
    paths = {name: font_dir / f"TishteSans-{name}-v1100.ttf" for name in style_names}
    for path in paths.values():
        if not path.is_file(): raise FileNotFoundError(path)
    regular = paths["Regular"]
    canvas = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((MARGIN, 52, MARGIN + 12, 302), fill=ACCENT)
    draw.text((MARGIN + 34, 32), "Tishte Sans", font=face(regular, 166), fill=INK)
    draw.text((MARGIN + 42, 222), "ЭКРАННАЯ И ИНТЕРФЕЙСНАЯ ГАРНИТУРА", font=face(paths["SemiBold"], 24), fill=ACCENT)
    draw.text((MARGIN + 42, 263), "Сайты · Android и iOS · интерфейсы · панели данных · презентации", font=face(regular, 28), fill=MUTED)
    cx = 1830
    vertical(draw, cx - 42, 52, 302)
    label(draw, cx, 58, "Экранный характер", regular, 1100)
    draw.text((cx, 102), "Открытые формы. Крупная строчная.\nРомбовидные точки и диакритика.\nДесять согласованных начертаний.", font=face(regular, 31), fill=INK, spacing=14)
    draw.text((cx, 248), "Версия 1.100 · SIL Open Font License 1.1", font=face(regular, 23), fill=MUTED)
    line(draw, 330)

    mid = WIDTH // 2
    vertical(draw, mid, 358, 920)
    lx, rx, cw = MARGIN + 8, mid + 42, mid - MARGIN - 46
    label(draw, lx, 370, "Русский и марийские языки", regular, cw)
    fitted(draw, lx, 418, "А Б В Г Д Е Ё Ж З И Й К Л М Н О П", regular, cw, 49)
    fitted(draw, lx, 480, "Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я", regular, cw, 49)
    fitted(draw, lx, 550, "а б в г д е ё ж з и й к л м н о п", regular, cw, 49)
    fitted(draw, lx, 612, "р с т у ф х ц ч ш щ ъ ы ь э ю я", regular, cw, 49)
    label(draw, lx, 687, "Луговой и горный марийский", regular, cw)
    fitted(draw, lx, 730, "Ӓ ӓ   Ӧ ӧ   Ӱ ӱ   Ҥ ҥ   Ӹ ӹ", regular, cw, 68)
    fitted(draw, lx, 828, "Марий Эл · Кугыжаныш · шачмы йӹлмӹ", regular, cw, 38)

    label(draw, rx, 370, "Латиница", regular, cw)
    fitted(draw, rx, 418, "A B C D E F G H I J K L M", regular, cw, 53)
    fitted(draw, rx, 482, "N O P Q R S T U V W X Y Z", regular, cw, 53)
    fitted(draw, rx, 550, "a b c d e f g h i j k l m", regular, cw, 53)
    fitted(draw, rx, 614, "n o p q r s t u v w x y z", regular, cw, 53)
    label(draw, rx, 687, "Расширенная латиница", regular, cw)
    fitted(draw, rx, 730, "À Á Â Ã Ä Å Æ Ç È É Ê Ë Ñ Ö Ø Œ", regular, cw, 42)
    fitted(draw, rx, 790, "Š Ü Ý Ÿ Ž Ð Þ ß  à á â ã ä å æ ç", regular, cw, 42)
    fitted(draw, rx, 850, "è é ê ë ñ ö ø œ š ü ý ÿ ž", regular, cw, 42)
    line(draw, 944)

    split = 1030
    vertical(draw, split, 970, 1214)
    label(draw, lx, 976, "Цифры и данные", regular, 900)
    fitted(draw, lx, 1020, "0 1 2 3 4 5 6 7 8 9", regular, 900, 70)
    fitted(draw, lx, 1110, "12.08.2026   № 147-р   2 583 640,70 ₽", regular, 900, 34)
    sx = split + 38
    label(draw, sx, 976, "Знаки и интерфейсные символы", regular, WIDTH - MARGIN - sx)
    fitted(draw, sx, 1020, "№ ₽ $ € £ ¥ © ® ™ § ¶ • · † ‡ ※", regular, WIDTH - MARGIN - sx, 43)
    fitted(draw, sx, 1083, "+ − × ÷ = ≠ < > ≤ ≥ ± ∞ √ ∑ ∆ µ", regular, WIDTH - MARGIN - sx, 43)
    fitted(draw, sx, 1146, "— – ‑ … « » „ “ ( ) [ ] { } / \\ @ & % ‰ °", regular, WIDTH - MARGIN - sx, 38)
    line(draw, 1238)

    thirds = (MARGIN, 1074, 2078, WIDTH - MARGIN)
    for x in (thirds[1] - 24, thirds[2] - 24): vertical(draw, x, 1264, 1498)
    samples = (("Русский", "Единая цифровая среда Республики Марий Эл.\nПоказатели обновлены в 12:45.\nДоступность сервисов — 99,9 %."), ("Луговой марийский", "Марий Эл Республикын Вуйлатышыже.\nТӱвыра да калык-влакын пашашт.\nКонтроль: Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ҥ ҥ."), ("Горномарийский", "Шачмы йӹлмем ылеш сӹлнӹ.\nЯратыда ӹшке туан йӹлмӹдӓм!\nКонтроль: Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ӹ ӹ."))
    for i, (heading, text) in enumerate(samples):
        x = thirds[i] + 8
        label(draw, x, 1268, heading, regular, thirds[i + 1] - x - 36)
        draw.multiline_text((x, 1314), text, font=face(regular, 29), fill=INK, spacing=15)
    line(draw, 1522)

    style_order = ("Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Italic", "MediumItalic", "SemiBoldItalic", "BoldItalic", "ExtraBoldItalic")
    display_names = {
        "MediumItalic": "Medium Italic",
        "SemiBold": "SemiBold",
        "SemiBoldItalic": "SemiBold Italic",
        "BoldItalic": "Bold Italic",
        "ExtraBold": "ExtraBold",
        "ExtraBoldItalic": "ExtraBold Italic",
    }
    cell_w = (WIDTH - 2 * MARGIN - 4 * 22) // 5
    for i, name in enumerate(style_order):
        row, col = divmod(i, 5)
        x = MARGIN + col * (cell_w + 22)
        y = 1547 + row * 202
        if col: vertical(draw, x - 13, y, y + 178)
        label(draw, x, y, display_names.get(name, name), regular, cell_w)
        fitted(draw, x, y + 40, "Цифровая среда · Digital", paths[name], cell_w, 31)
        fitted(draw, x, y + 86, "Ӓӓ Ӧӧ Ӱӱ Ҥҥ Ӹӹ  0123456789", paths[name], cell_w, 27)
        fitted(draw, x, y + 127, "№ 147-р  ·  2 583,70 ₽", paths[name], cell_w, 27)
    line(draw, 1942)
    draw.text((MARGIN + 8, 1967), "Tishte Sans · v1.100 · 425 символов · 10 начертаний · TTF + WOFF2", font=face(regular, 23), fill=MUTED)
    footer = "Разработчик: Сергей Якунин"
    ff = face(regular, 21); fw = draw.textbbox((0, 0), footer, font=ff)[2]
    draw.text((WIDTH - MARGIN - fw, 1969), footer, font=ff, fill=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True, dpi=(180, 180))
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, default=Path("build"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/specimens/tishte-sans-v1100-card.png"))
    args = parser.parse_args(); render(args.font_dir, args.output)


if __name__ == "__main__": main()
