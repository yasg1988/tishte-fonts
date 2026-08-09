#!/usr/bin/env python3
"""Build and normalize the four-style Tishte Serif family."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import math
import shutil
import subprocess

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph

from font_metrics_audit import load_charset
from versioning import version_tag


FAMILY = "Tishte Serif"
VERSION = "1.000"
LICENSE = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
LICENSE_URL = "https://openfontlicense.org"
# OpenType seconds since 1904-01-01 for 2026-01-01T00:00:00Z. Keeping this
# stable makes identical sources and dependencies produce identical binaries.
BUILD_TIMESTAMP = 3850070400


@dataclass(frozen=True)
class Style:
    key: str
    subfamily: str
    weight: int
    panose_weight: int
    reference_name: str

    @property
    def postscript(self) -> str:
        return f"TishteSerif-{self.key}"


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
    font["name"].setName(value, name_id, 3, 1, 0x0409)


def find_fontforge() -> Path:
    """Locate FontForge on Linux, macOS or a standard Windows install."""
    discovered = shutil.which("fontforge")
    if discovered:
        return Path(discovered)
    candidates = (
        Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        / "FontForgeBuilds/bin/fontforge.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))
        / "FontForgeBuilds/bin/fontforge.exe",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("FontForge was not found")


def clear_whitespace_ink(font: TTFont) -> None:
    """Remove inherited visible placeholders from Unicode whitespace glyphs."""
    cmap = font.getBestCmap()
    for codepoint in (0x2028, 0x2029, 0x205F, 0x2060, 0xFEFF):
        glyph_name = cmap.get(codepoint)
        if glyph_name is not None:
            font["glyf"][glyph_name] = Glyph()


def remove_empty_encoded_letters(font: TTFont) -> None:
    """Drop two broken, out-of-scope mappings inherited by the Bold source."""
    glyf = font["glyf"]
    for cmap_table in font["cmap"].tables:
        if not cmap_table.isUnicode():
            continue
        for codepoint in (0xAB48, 0xAB54):
            glyph_name = cmap_table.cmap.get(codepoint)
            if glyph_name is not None and glyf[glyph_name].numberOfContours == 0:
                del cmap_table.cmap[codepoint]


def add_static_stat(font: TTFont, style: Style) -> None:
    italic = "Italic" in style.subfamily
    weight_name = "Bold" if style.weight == 700 else "Regular"
    axes = [
        {
            "tag": "wght",
            "name": "Weight",
            "ordering": 0,
            "values": [
                {
                    "value": style.weight,
                    "name": weight_name,
                    "flags": 0x2 if style.weight == 400 else 0,
                }
            ],
        },
        {
            "tag": "ital",
            "name": "Italic",
            "ordering": 1,
            "values": [
                {
                    "value": 1 if italic else 0,
                    "name": "Italic" if italic else "Roman",
                    "flags": 0 if italic else 0x2,
                    **({"linkedValue": 1} if not italic else {}),
                }
            ],
        },
    ]
    buildStatTable(font, axes, windowsNames=True, macNames=False)


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


def sync_metrics(font: TTFont, metrics: dict, codepoints: list[int]) -> None:
    candidate_cmap = font.getBestCmap()
    for codepoint in codepoints:
        candidate_glyph = candidate_cmap.get(codepoint)
        reference_advance = metrics["advances"].get(f"U+{codepoint:04X}")
        if candidate_glyph is None or reference_advance is None:
            continue
        _candidate_advance, candidate_lsb = font["hmtx"].metrics[candidate_glyph]
        font["hmtx"].metrics[candidate_glyph] = (reference_advance, candidate_lsb)

    for table_name, values in metrics["vertical"].items():
        for field, value in values.items():
            setattr(font[table_name], field, value)


def normalize(
    path: Path,
    style: Style,
    metrics: dict,
    codepoints: list[int],
    version: str,
) -> None:
    with TTFont(path, recalcTimestamp=False) as font:
        family_name = FAMILY
        postscript_name = style.postscript
        font["name"].names = [
            record
            for record in font["name"].names
            if record.platformID != 1 and record.nameID not in PRIMARY_NAME_IDS
        ]
        unique_id = f"Version {version}; Tishte Serif; {style.key}"
        full_name = f"{family_name} {style.subfamily}"
        names = {
            1: family_name,
            2: style.subfamily,
            3: unique_id,
            4: full_name,
            5: f"Version {version}",
            6: postscript_name,
            13: LICENSE,
            14: LICENSE_URL,
            16: family_name,
            17: style.subfamily,
        }
        for name_id, value in names.items():
            set_name(font, name_id, value)

        sync_metrics(font, metrics, codepoints)
        os2 = font["OS/2"]
        os2.fsType = 0
        os2.achVendID = "MRIE"
        os2.usWeightClass = style.weight
        os2.fsSelection = metrics["fs_selection"]
        os2.panose.bFamilyType = 2
        os2.panose.bSerifStyle = 2
        os2.panose.bWeight = style.panose_weight
        os2.panose.bProportion = 3
        os2.xAvgCharWidth = os2.recalcAvgCharWidth(font)
        font["head"].macStyle = metrics["mac_style"]
        font["head"].fontRevision = float(version)
        font["head"].created = BUILD_TIMESTAMP
        font["head"].modified = BUILD_TIMESTAMP
        font["post"].underlineThickness = 100

        italic_angle = font["post"].italicAngle
        if italic_angle:
            font["hhea"].caretSlopeRise = font["head"].unitsPerEm
            font["hhea"].caretSlopeRun = round(
                math.tan(math.radians(-italic_angle)) * font["head"].unitsPerEm
            )
        else:
            font["hhea"].caretSlopeRise = 1
            font["hhea"].caretSlopeRun = 0

        clear_whitespace_ink(font)
        remove_empty_encoded_letters(font)
        add_static_stat(font, style)

        temporary = path.with_suffix(".normalized.ttf")
        font.save(temporary, reorderTables=True)
    temporary.replace(path)


def build(
    root: Path,
    version: str = VERSION,
) -> list[Path]:
    codepoints = load_charset(root / "data" / "document-charset.txt")
    metric_contract = json.loads(
        (root / "data" / "times-new-roman-metrics.json").read_text(encoding="utf-8")
    )
    tag = version_tag(version)
    outputs: list[Path] = []
    for style in STYLES:
        source = root / "sources" / "tishte-serif" / f"TishteSerif-{style.key}.sfd"
        output = root / "build" / f"TishteSerif-{style.key}-{tag}.ttf"
        generate(source, output)
        normalize(output, style, metric_contract["styles"][style.key], codepoints, version)
        outputs.append(output)
        print(output)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default=VERSION)
    args = parser.parse_args()
    build(args.root.resolve(), args.version)


if __name__ == "__main__":
    main()
