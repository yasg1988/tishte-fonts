#!/usr/bin/env python3
"""Build and normalize the four-style Tishte Serif engineering family."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess

from fontTools.ttLib import TTFont

from build_serif_from_sfd import find_fontforge
from build_serif_prototype import LICENSE, LICENSE_URL
from font_metrics_audit import load_charset


FAMILY = "Tishte Serif Prototype"
VERSION = "0.060"


@dataclass(frozen=True)
class Style:
    key: str
    subfamily: str
    weight: int
    panose_weight: int
    reference_name: str

    @property
    def postscript(self) -> str:
        return f"TishteSerifPrototype-{self.key}"


STYLES = (
    Style("Regular", "Regular", 400, 5, "times.ttf"),
    Style("Bold", "Bold", 700, 8, "timesbd.ttf"),
    Style("Italic", "Italic", 400, 5, "timesi.ttf"),
    Style("BoldItalic", "Bold Italic", 700, 8, "timesbi.ttf"),
)

PRIMARY_NAME_IDS = {1, 2, 3, 4, 5, 6, 16, 17}
VERTICAL_FIELDS = {
    "hhea": ("ascent", "descent", "lineGap"),
    "OS/2": (
        "sTypoAscender",
        "sTypoDescender",
        "sTypoLineGap",
        "usWinAscent",
        "usWinDescent",
    ),
}


def set_name(font: TTFont, name_id: int, value: str) -> None:
    for platform_id, encoding_id, language_id in ((3, 1, 0x0409), (1, 0, 0)):
        font["name"].setName(value, name_id, platform_id, encoding_id, language_id)


def generate(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(find_fontforge()),
            "-lang=ff",
            "-c",
            "Open($1); Generate($2);",
            str(source),
            str(output),
        ],
        check=True,
    )


def sync_metrics(font: TTFont, reference: TTFont, codepoints: list[int]) -> None:
    candidate_cmap = font.getBestCmap()
    reference_cmap = reference.getBestCmap()
    for codepoint in codepoints:
        candidate_glyph = candidate_cmap.get(codepoint)
        reference_glyph = reference_cmap.get(codepoint)
        if candidate_glyph is None or reference_glyph is None:
            continue
        _candidate_advance, candidate_lsb = font["hmtx"].metrics[candidate_glyph]
        reference_advance, _reference_lsb = reference["hmtx"].metrics[reference_glyph]
        font["hmtx"].metrics[candidate_glyph] = (reference_advance, candidate_lsb)

    for table_name, fields in VERTICAL_FIELDS.items():
        for field in fields:
            setattr(font[table_name], field, getattr(reference[table_name], field))


def normalize(path: Path, reference_path: Path, style: Style, codepoints: list[int]) -> None:
    with TTFont(path, recalcTimestamp=False) as font, TTFont(reference_path, lazy=False) as reference:
        font["name"].names = [
            record for record in font["name"].names if record.nameID not in PRIMARY_NAME_IDS
        ]
        unique_id = f"Version {VERSION}; Tishte Serif engineering prototype; {style.key}"
        full_name = f"{FAMILY} {style.subfamily}"
        names = {
            1: FAMILY,
            2: style.subfamily,
            3: unique_id,
            4: full_name,
            5: f"Version {VERSION}",
            6: style.postscript,
            13: LICENSE,
            14: LICENSE_URL,
            16: FAMILY,
            17: style.subfamily,
        }
        for name_id, value in names.items():
            set_name(font, name_id, value)

        sync_metrics(font, reference, codepoints)
        os2 = font["OS/2"]
        os2.fsType = 0
        os2.achVendID = "MRIE"
        os2.usWeightClass = style.weight
        os2.fsSelection = reference["OS/2"].fsSelection
        os2.panose.bFamilyType = 2
        os2.panose.bSerifStyle = 2
        os2.panose.bWeight = style.panose_weight
        os2.panose.bProportion = 3
        font["head"].macStyle = reference["head"].macStyle

        temporary = path.with_suffix(".normalized.ttf")
        font.save(temporary, reorderTables=True)
    temporary.replace(path)


def build(root: Path) -> list[Path]:
    codepoints = load_charset(root / "data" / "document-charset.txt")
    outputs: list[Path] = []
    for style in STYLES:
        source = root / "sources" / "tishte-serif" / "iterations" / f"TishteSerif-{style.key}-v060.sfd"
        output = root / "build" / f"TishteSerif-{style.key}-v060.ttf"
        reference = Path("C:/Windows/Fonts") / style.reference_name
        generate(source, output)
        normalize(output, reference, style, codepoints)
        outputs.append(output)
        print(output)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build(args.root.resolve())


if __name__ == "__main__":
    main()
