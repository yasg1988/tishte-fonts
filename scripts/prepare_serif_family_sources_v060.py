#!/usr/bin/env python3
"""Create editable v0.060 SFD sources for the four core Serif styles.

Run this file with FontForge's Python interpreter, not CPython.
"""

from __future__ import annotations

from pathlib import Path

import fontforge


ROOT = Path(__file__).resolve().parents[1]
ITERATIONS = ROOT / "sources" / "tishte-serif" / "iterations"
UPSTREAM = ROOT / "sources" / "upstream" / "tinos"

STYLES = {
    "Regular": ITERATIONS / "TishteSerif-Regular-v040.sfd",
    "Bold": UPSTREAM / "Tinos-Bold.ttf",
    "Italic": UPSTREAM / "Tinos-Italic.ttf",
    "BoldItalic": UPSTREAM / "Tinos-BoldItalic.ttf",
}


def prepare(style: str, source: Path) -> Path:
    output = ITERATIONS / f"TishteSerif-{style}-v060.sfd"
    font = fontforge.open(str(source))
    try:
        display_style = "Bold Italic" if style == "BoldItalic" else style
        font.familyname = "Tishte Serif Prototype"
        font.fontname = f"TishteSerifPrototype-{style}"
        font.fullname = f"Tishte Serif Prototype {display_style}"
        font.weight = "Bold" if "Bold" in style else "Regular"
        font.version = "0.060"
        font.sfntRevision = 0.060
        font.save(str(output))
    finally:
        font.close()
    return output


def main() -> None:
    ITERATIONS.mkdir(parents=True, exist_ok=True)
    for style, source in STYLES.items():
        output = prepare(style, source)
        print(output)


if __name__ == "__main__":
    main()
