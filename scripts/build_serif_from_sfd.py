#!/usr/bin/env python3
"""Build the editable Tishte Serif source with FontForge and normalize metadata."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess

from fontTools.ttLib import TTFont

from build_serif_prototype import FAMILY, LICENSE, LICENSE_URL, POSTSCRIPT, set_name


def find_fontforge() -> Path:
    discovered = shutil.which("fontforge")
    if discovered:
        return Path(discovered)
    candidates = [
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "FontForgeBuilds/bin/fontforge.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "FontForgeBuilds/bin/fontforge.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("FontForge was not found")


def normalize_metadata(font_path: Path, version_number: str) -> None:
    with TTFont(font_path, recalcTimestamp=False) as font:
        names = {
            1: FAMILY,
            2: "Regular",
            3: f"Version {version_number}; Tishte Serif engineering prototype",
            4: f"{FAMILY} Regular",
            5: f"Version {version_number}",
            6: POSTSCRIPT,
            13: LICENSE,
            14: LICENSE_URL,
            16: FAMILY,
            17: "Regular",
        }
        for name_id, value in names.items():
            set_name(font, name_id, value)
        os2 = font["OS/2"]
        os2.fsType = 0
        os2.achVendID = "MRIE"
        os2.panose.bFamilyType = 2
        os2.panose.bSerifStyle = 2
        os2.panose.bWeight = 5
        os2.panose.bProportion = 3

        temporary = font_path.with_suffix(".normalized.ttf")
        font.save(temporary, reorderTables=True)
    temporary.replace(font_path)


def build(source: Path, output: Path, version_number: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(find_fontforge()),
        "-lang=ff",
        "-c",
        "Open($1); Generate($2);",
        str(source),
        str(output),
    ]
    subprocess.run(command, check=True)
    normalize_metadata(output, version_number)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("sources/tishte-serif/TishteSerif-Regular.sfd"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/TishteSerif-Regular.ttf"),
    )
    parser.add_argument("--version", default="0.001")
    args = parser.parse_args()
    build(args.source, args.output, args.version)
    print(args.output)


if __name__ == "__main__":
    main()
