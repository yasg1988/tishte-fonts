#!/usr/bin/env python3
"""Build the renamed Tishte Serif engineering prototype from an OFL scaffold.

This stage validates naming, embedding permissions, packaging and metric tests.
It is not the final visual design: upstream outlines must be replaced by Tishte
outlines before a public release.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont


FAMILY = "Tishte Serif Prototype"
POSTSCRIPT = "TishteSerifPrototype-Regular"
VERSION = "Version 0.001"
LICENSE = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
LICENSE_URL = "https://openfontlicense.org"


def set_name(font: TTFont, name_id: int, value: str) -> None:
    name_table = font["name"]
    for platform_id, encoding_id, language_id in (
        (3, 1, 0x0409),
        (1, 0, 0),
    ):
        name_table.setName(value, name_id, platform_id, encoding_id, language_id)


def build(source: Path, output: Path) -> None:
    with TTFont(source, recalcTimestamp=False) as font:
        names = {
            1: FAMILY,
            2: "Regular",
            3: f"{VERSION}; Tishte Serif engineering prototype",
            4: f"{FAMILY} Regular",
            5: VERSION,
            6: POSTSCRIPT,
            13: LICENSE,
            14: LICENSE_URL,
            16: FAMILY,
            17: "Regular",
        }
        for name_id, value in names.items():
            set_name(font, name_id, value)

        os2 = font["OS/2"]
        os2.fsType = 0  # Installable embedding.
        os2.achVendID = "MRIE"
        # PANOSE: Latin Text, cove serif, medium weight, modern proportions.
        # This metadata supports font classification in document systems; it
        # does not replace visual review of the actual outlines.
        os2.panose.bFamilyType = 2
        os2.panose.bSerifStyle = 2
        os2.panose.bWeight = 5
        os2.panose.bProportion = 3

        output.parent.mkdir(parents=True, exist_ok=True)
        font.save(output, reorderTables=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("sources/upstream/tinos/Tinos-Regular.ttf"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/TishteSerifPrototype-Regular.ttf"),
    )
    args = parser.parse_args()
    build(args.source, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
