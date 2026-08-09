#!/usr/bin/env python3
"""Replace inherited upstream marketing metadata with Tishte provenance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from versioning import version_tag


STYLES = ("Regular", "Bold", "Italic", "BoldItalic")
COPYRIGHT_NOTICE = (
    "Copyright 2026 The Tinos Project Authors "
    "(https://github.com/googlefonts/tinos). "
    "Copyright 2026 Tishte Project contributors; modified for the Tishte Project "
    "(https://github.com/yasg1988/tishte-fonts)."
)
DESCRIPTION = (
    "Tishte Serif is a modified version of Tinos, developed as a free "
    "Times New Roman-metric document typeface with Russian, Meadow Mari, "
    "Hill Mari and Latin coverage."
)
PROJECT_URL = "https://github.com/yasg1988/tishte-fonts"
LICENSE = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
LICENSE_URL = "https://openfontlicense.org"


def set_windows_english(name_table, value: str, name_id: int) -> None:
    name_table.removeNames(nameID=name_id)
    name_table.setName(value, name_id, 3, 1, 0x0409)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    report = {"version": args.version, "styles": {}, "passed": True}

    for style in STYLES:
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        font = TTFont(path, recalcTimestamp=False)
        names = font["name"]
        set_windows_english(names, COPYRIGHT_NOTICE, 0)
        names.removeNames(nameID=7)
        set_windows_english(names, "Tishte Project", 8)
        set_windows_english(names, "Сергей Якунин", 9)
        set_windows_english(names, DESCRIPTION, 10)
        set_windows_english(names, PROJECT_URL, 11)
        set_windows_english(names, PROJECT_URL, 12)
        set_windows_english(names, LICENSE, 13)
        set_windows_english(names, LICENSE_URL, 14)
        font.save(path, reorderTables=True)
        font.close()
        report["styles"][style] = {
            "path": str(path),
            "removed_trademark_field": True,
            "project_url": PROJECT_URL,
            "passed": True,
        }
        print(f"{style}: normalized legal and provenance metadata")

    output = root / "artifacts" / "reports" / f"release-metadata-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
