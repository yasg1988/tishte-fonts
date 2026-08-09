#!/usr/bin/env python3
"""Render the public Tishte Serif type card using the real release fonts."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 3072
HEIGHT = 2048
MARGIN = 68
GAP = 28
PAPER = "#f8f7f3"
INK = "#111923"
ACCENT = "#851a32"
MUTED = "#626a73"
RULE = "#c7cbd0"


def face(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def fit_face(draw: ImageDraw.ImageDraw, path: Path, text: str, max_width: int, start: int, minimum: int = 18) -> ImageFont.FreeTypeFont:
    size = start
    while size > minimum and draw.textbbox((0, 0), text, font=face(path, size))[2] > max_width:
        size -= 1
    return face(path, size)


def label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, regular: Path, max_width: int) -> None:
    draw.text((x, y), text.upper(), font=fit_face(draw, regular, text.upper(), max_width, 23), fill=ACCENT)


def rule(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.line((MARGIN, y, WIDTH - MARGIN, y), fill=RULE, width=2)


def v_rule(draw: ImageDraw.ImageDraw, x: int, y1: int, y2: int) -> None:
    draw.line((x, y1, x, y2), fill=RULE, width=2)


def text_line(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font_path: Path, size: int, max_width: int, fill: str = INK) -> None:
    draw.text(xy, text, font=fit_face(draw, font_path, text, max_width, size), fill=fill)


def render(font_dir: Path, output: Path) -> None:
    regular = font_dir / "TishteSerif-Regular-v960.ttf"
    bold = font_dir / "TishteSerif-Bold-v960.ttf"
    italic = font_dir / "TishteSerif-Italic-v960.ttf"
    bold_italic = font_dir / "TishteSerif-BoldItalic-v960.ttf"
    for path in (regular, bold, italic, bold_italic):
        if not path.exists():
            raise FileNotFoundError(path)

    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    # Masthead
    draw.rectangle((MARGIN, 54, MARGIN + 12, 305), fill=ACCENT)
    draw.text((MARGIN + 34, 38), "Tishte Serif", font=face(regular, 164), fill=INK)
    draw.text((MARGIN + 42, 224), "СВОБОДНАЯ ТИПОГРАФИЧЕСКАЯ СИСТЕМА", font=face(bold, 24), fill=ACCENT)
    draw.text((MARGIN + 42, 266), "Документы · печать · длинные тексты · цифровые публикации", font=face(regular, 28), fill=MUTED)

    concept_x = 1810
    v_rule(draw, concept_x - 44, 54, 304)
    label(draw, concept_x, 58, "Характер", regular, 1070)
    draw.text((concept_x, 100), "Ясная структура. Спокойный ритм.\nТочная документная верстка.\nЧетыре согласованных начертания.", font=face(regular, 31), fill=INK, spacing=14)
    draw.text((concept_x, 248), "Версия 0.960 · SIL Open Font License 1.1", font=face(regular, 23), fill=MUTED)
    rule(draw, 330)

    # Alphabets
    mid = WIDTH // 2
    v_rule(draw, mid, 358, 982)
    left_x, right_x = MARGIN + 8, mid + 42
    col_w = mid - MARGIN - 46

    label(draw, left_x, 370, "Кириллица — прописные", regular, col_w)
    text_line(draw, (left_x, 414), "А Б В Г Д Е Ё Ж З И Й К Л М Н О П", regular, 50, col_w)
    text_line(draw, (left_x, 476), "Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я", regular, 50, col_w)
    label(draw, left_x, 552, "Кириллица — строчные", regular, col_w)
    text_line(draw, (left_x, 596), "а б в г д е ё ж з и й к л м н о п", regular, 50, col_w)
    text_line(draw, (left_x, 658), "р с т у ф х ц ч ш щ ъ ы ь э ю я", regular, 50, col_w)
    label(draw, left_x, 734, "Марийские буквы", regular, col_w)
    text_line(draw, (left_x, 775), "Ӓ ӓ    Ӧ ӧ    Ӱ ӱ    Ҥ ҥ    Ӹ ӹ", regular, 67, col_w)
    draw.text((left_x, 869), "ЛУГОВОЙ МАРИЙСКИЙ  Ҥ ҥ", font=face(regular, 22), fill=MUTED)
    draw.text((left_x + 510, 869), "ГОРНОМАРИЙСКИЙ  Ӹ ӹ", font=face(regular, 22), fill=MUTED)
    text_line(draw, (left_x, 911), "Йошкар-Ола · Марий Эл · шачмы йӹлмӹ", regular, 40, col_w)

    label(draw, right_x, 370, "Латиница — прописные", regular, col_w)
    text_line(draw, (right_x, 414), "A B C D E F G H I J K L M", regular, 53, col_w)
    text_line(draw, (right_x, 478), "N O P Q R S T U V W X Y Z", regular, 53, col_w)
    label(draw, right_x, 552, "Латиница — строчные", regular, col_w)
    text_line(draw, (right_x, 596), "a b c d e f g h i j k l m", regular, 53, col_w)
    text_line(draw, (right_x, 660), "n o p q r s t u v w x y z", regular, 53, col_w)
    label(draw, right_x, 734, "Расширенная латиница", regular, col_w)
    text_line(draw, (right_x, 776), "À Á Â Ã Ä Å Æ Ç È É Ê Ë", regular, 44, col_w)
    text_line(draw, (right_x, 834), "Ñ Ö Ø Œ Š Ü Ý Ÿ Ž Ð Þ ß", regular, 44, col_w)
    text_line(draw, (right_x, 892), "à á â ã ä å æ ç è é ê ë ñ ö ø œ š ü ý ÿ ž", regular, 39, col_w)
    rule(draw, 1006)

    # Numerals and symbols
    num_split = 1040
    v_rule(draw, num_split, 1032, 1268)
    label(draw, left_x, 1038, "Цифры", regular, 900)
    text_line(draw, (left_x, 1080), "0 1 2 3 4 5 6 7 8 9", regular, 70, 900)
    text_line(draw, (left_x, 1170), "12.08.2026   № 147-р", regular, 38, 900)
    sx = num_split + 38
    label(draw, sx, 1038, "Знаки, валюты и символы", regular, WIDTH - MARGIN - sx)
    text_line(draw, (sx, 1080), "№  ₽  $  €  £  ¥  ¢   ©  ®  ™  §  ¶  •  †  ‡  ※", regular, 42, WIDTH - MARGIN - sx)
    text_line(draw, (sx, 1140), "+  -  ×  ÷  =  ≠  <  >  ≤  ≥  ±  ∞  √  ∑  ∆  µ", regular, 42, WIDTH - MARGIN - sx)
    text_line(draw, (sx, 1200), "—  –  …  « »  „ “  ( )  [ ]  { }  /  \\  @  &  %  ‰  °", regular, 38, WIDTH - MARGIN - sx)
    rule(draw, 1294)

    # Language samples
    thirds = (MARGIN, 1074, 2078, WIDTH - MARGIN)
    v_rule(draw, thirds[1] - 24, 1320, 1574)
    v_rule(draw, thirds[2] - 24, 1320, 1574)
    samples = [
        (thirds[0] + 8, "Русский", "Правительство Республики Марий Эл.\nПостановление № 125 от 12.08.2026.\nСумма 2 583 640,70 ₽; срок — 30 дней."),
        (thirds[1] + 8, "Луговомарийский", "Марий Эл Республикын Кугыжаныш Погынжо.\nТӱвыра да калык-влакын пашашт.\nКонтроль: Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ҥ ҥ."),
        (thirds[2] + 8, "Горномарийский", "Шачмы йӹлмем ылеш сӹлнӹ.\nЯратыда ӹшке туан йӹлмӹдӓм!\nКонтроль: Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ӹ ӹ."),
    ]
    for index, (x, heading, sample) in enumerate(samples):
        max_w = thirds[index + 1] - x - 38
        label(draw, x, 1324, heading, regular, max_w)
        draw.multiline_text((x, 1372), sample, font=face(regular, 29), fill=INK, spacing=16)
    rule(draw, 1598)

    # Four real styles
    style_width = (WIDTH - 2 * MARGIN - 3 * GAP) // 4
    styles = [
        ("REGULAR", regular),
        ("BOLD", bold),
        ("ITALIC", italic),
        ("BOLD ITALIC", bold_italic),
    ]
    for index, (name, font_path) in enumerate(styles):
        x = MARGIN + index * (style_width + GAP)
        if index:
            v_rule(draw, x - GAP // 2, 1626, 1908)
        label(draw, x, 1630, f"Tishte Serif {name}", regular, style_width)
        text_line(draw, (x, 1678), "Цифровая трансформация", font_path, 34, style_width)
        text_line(draw, (x, 1727), "для развития региона", font_path, 34, style_width)
        text_line(draw, (x, 1784), "Digital transformation", font_path, 31, style_width)
        text_line(draw, (x, 1831), "0123456789  № 147-р", font_path, 29, style_width)
        text_line(draw, (x, 1874), "Aa Бб Ӓӓ Ӹӹ Ҥҥ & ₽", font_path, 29, style_width)

    rule(draw, 1936)
    draw.text((MARGIN + 8, 1962), "Tishte Serif · v0.960 · 423 символа · TTF + WOFF2", font=face(regular, 23), fill=MUTED)
    footer = "Разработчик: Сергей Якунин"
    footer_face = face(regular, 21)
    footer_w = draw.textbbox((0, 0), footer, font=footer_face)[2]
    draw.text((WIDTH - MARGIN - footer_w, 1964), footer, font=footer_face, fill=MUTED)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True, dpi=(180, 180))
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, default=Path("build"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/specimens/tishte-serif-v0960-card.png"))
    args = parser.parse_args()
    render(args.font_dir, args.output)


if __name__ == "__main__":
    main()
