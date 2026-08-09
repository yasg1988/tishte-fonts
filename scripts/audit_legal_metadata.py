#!/usr/bin/env python3
"""Audit OFL provenance, user-facing names and proprietary-font exclusions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

from versioning import version_tag


STYLES = ("Regular", "Bold", "Italic", "BoldItalic")
UPSTREAM_COPYRIGHT = "Copyright 2026 The Tinos Project Authors"
MODIFICATION_NOTICE = "Copyright 2026 Tishte Project contributors; modified for the Tishte Project"
PROJECT_URL = "https://github.com/yasg1988/tishte-fonts"


def values(font: TTFont, name_id: int) -> list[str]:
    result = []
    for record in font["name"].names:
        if record.nameID == name_id:
            try:
                result.append(record.toUnicode())
            except UnicodeDecodeError:
                result.append("<decode-error>")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    license_text = (root / "LICENSE.txt").read_text(encoding="utf-8")
    license_checks = {
        "current_upstream_copyright": license_text.startswith(UPSTREAM_COPYRIGHT),
        "project_modification_notice": MODIFICATION_NOTICE in license_text,
        "ofl_1_1": "SIL OPEN FONT LICENSE Version 1.1" in license_text,
        "no_stale_reserved_names": "Reserved Font Arimo, Tinos and Cousine" not in license_text,
    }
    forbidden_files = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".ttf", ".otf", ".ttc"}
        and "times" in path.name.lower()
    )
    report = {
        "version": args.version,
        "license": license_checks,
        "forbidden_proprietary_font_files": forbidden_files,
        "styles": {},
        "passed": all(license_checks.values()) and not forbidden_files,
    }

    for style in STYLES:
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        with TTFont(path) as font:
            primary = values(font, 1) + values(font, 4) + values(font, 6) + values(font, 16) + values(font, 17)
            copyright_values = values(font, 0)
            trademark_values = values(font, 7)
            vendor_values = values(font, 8)
            designer_values = values(font, 9)
            description_values = values(font, 10)
            vendor_urls = values(font, 11) + values(font, 12)
            license_values = values(font, 13)
            license_urls = values(font, 14)
        failures = []
        if any("Tinos" in value for value in primary):
            failures.append("upstream name appears in primary user-facing names")
        if not copyright_values or not all(
            UPSTREAM_COPYRIGHT in value and MODIFICATION_NOTICE in value for value in copyright_values
        ):
            failures.append("incomplete upstream copyright or modification notice")
        if trademark_values:
            failures.append("stale trademark field present")
        if vendor_values != ["Tishte Project"]:
            failures.append("unexpected vendor")
        if designer_values != ["Сергей Якунин"]:
            failures.append("unexpected designer")
        if not description_values or not all("modified version of Tinos" in value for value in description_values):
            failures.append("derivative provenance absent from description")
        if not vendor_urls or any(value != PROJECT_URL for value in vendor_urls):
            failures.append("unexpected project URL")
        if not license_values or any("Open Font License, Version 1.1" not in value for value in license_values):
            failures.append("OFL name absent")
        if license_urls != ["https://openfontlicense.org"]:
            failures.append("unexpected license URL")
        style_report = {"failures": failures, "passed": not failures}
        report["styles"][style] = style_report
        report["passed"] &= style_report["passed"]
        print(f"{style}: {'passed' if not failures else '; '.join(failures)}")

    output = root / "artifacts" / "reports" / f"legal-metadata-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
