#!/usr/bin/env python3
"""Render every declared Serif codepoint from the real release font."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

from font_metrics_audit import load_charset
from versioning import version_tag


COLS = 17
CELL_W = 232
CELL_H = 196
MARGIN = 64
HEADER = 230
PAPER = "#f8f7f3"
INK = "#111923"
ACCENT = "#851a32"
MUTED = "#68717a"
RULE = "#d0d3d6"
WHITESPACE_NAMES = {
    0x0020: "SPACE",
    0x00A0: "NBSP",
    0x00AD: "SOFT HYPHEN",
    0x2002: "EN SPACE",
    0x2003: "EM SPACE",
    0x2007: "FIGURE SPACE",
    0x2009: "THIN SPACE",
    0x200A: "HAIR SPACE",
    0x202F: "NARROW NBSP",
    0x200B: "ZERO WIDTH SPACE",
    0x2060: "WORD JOINER",
}


def face(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def render(root: Path, version: str, output: Path, family: str = "serif") -> None:
    tag = version_tag(version)
    prefix = "TishteSerif" if family == "serif" else "TishteSans"
    family_name = "Tishte Serif" if family == "serif" else "Tishte Sans"
    font_path = root / "build" / f"{prefix}-Regular-{tag}.ttf"
    codepoints = load_charset(root / "data" / "document-charset.txt")
    cmap = TTFont(font_path).getBestCmap()
    missing = [cp for cp in codepoints if cp not in cmap]
    if missing:
        raise ValueError(f"missing codepoints: {missing}")

    rows = math.ceil(len(codepoints) / COLS)
    width = MARGIN * 2 + COLS * CELL_W
    height = HEADER + rows * CELL_H + MARGIN
    image = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(image)
    title = face(font_path, 76)
    body = face(font_path, 84)
    small = face(font_path, 20)
    tiny = face(font_path, 16)

    draw.text((MARGIN, 38), f"{family_name} — полная карта знаков", font=title, fill=INK)
    draw.text((MARGIN, 132), f"Версия {version} · {len(codepoints)} кодовых точек · реальный TTF", font=face(font_path, 27), fill=ACCENT)
    draw.line((MARGIN, 190, width - MARGIN, 190), fill=RULE, width=2)

    for index, cp in enumerate(codepoints):
        row, col = divmod(index, COLS)
        x = MARGIN + col * CELL_W
        y = HEADER + row * CELL_H
        draw.rectangle((x, y, x + CELL_W, y + CELL_H), outline=RULE, width=1)
        glyph = chr(cp)
        if cp in WHITESPACE_NAMES:
            label = WHITESPACE_NAMES[cp]
            bbox = draw.textbbox((0, 0), label, font=tiny)
            draw.text((x + (CELL_W - (bbox[2] - bbox[0])) / 2, y + 69), label, font=tiny, fill=MUTED)
        else:
            bbox = draw.textbbox((0, 0), glyph, font=body)
            gx = x + (CELL_W - (bbox[2] - bbox[0])) / 2 - bbox[0]
            gy = y + 18 - bbox[1]
            draw.text((gx, gy), glyph, font=body, fill=INK)
        code = f"U+{cp:04X}"
        bbox = draw.textbbox((0, 0), code, font=small)
        draw.text((x + (CELL_W - (bbox[2] - bbox[0])) / 2, y + 157), code, font=small, fill=ACCENT)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True, dpi=(180, 180))
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    parser.add_argument("--family", choices=("serif", "sans"), default="serif")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    default_name = f"tishte-{args.family}-v1100-glyph-map.png"
    requested = args.output or Path("artifacts") / "specimens" / default_name
    output = requested if requested.is_absolute() else args.root / requested
    render(args.root.resolve(), args.version, output, args.family)


if __name__ == "__main__":
    main()
