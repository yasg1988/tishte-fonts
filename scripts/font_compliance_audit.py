#!/usr/bin/env python3
"""Audit machine-checkable parts of the Tishte Serif document profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

from font_metrics_audit import compare, load_charset


RESERVED_NAMES = ("Tinos", "Liberation")


def name_values(font: TTFont) -> list[str]:
    values: list[str] = []
    for record in font["name"].names:
        try:
            value = record.toUnicode()
        except UnicodeDecodeError:
            continue
        if value not in values:
            values.append(value)
    return values


def audit(reference: Path, candidate: Path, charset_path: Path) -> dict:
    metric_report = compare(reference, candidate, load_charset(charset_path))
    with TTFont(candidate, lazy=False) as font:
        os2 = font["OS/2"]
        post = font["post"]
        names = name_values(font)
        joined_names = "\n".join(names)

        checks = {
            "metric_core": {
                "passed": metric_report["passed"],
                "detail": metric_report["summary"],
            },
            "installable_embedding": {
                "passed": os2.fsType == 0,
                "detail": {"OS/2.fsType": os2.fsType},
            },
            "proportional": {
                "passed": post.isFixedPitch == 0 and os2.panose.bProportion != 9,
                "detail": {
                    "post.isFixedPitch": post.isFixedPitch,
                    "PANOSE.bProportion": os2.panose.bProportion,
                },
            },
            "serif_panose": {
                "passed": os2.panose.bFamilyType == 2 and os2.panose.bSerifStyle not in (0, 1, 11, 12, 13, 14, 15),
                "detail": {
                    "PANOSE.bFamilyType": os2.panose.bFamilyType,
                    "PANOSE.bSerifStyle": os2.panose.bSerifStyle,
                    "note": "PANOSE is supporting metadata; final serif classification also requires visual review.",
                },
            },
            "ofl_metadata": {
                "passed": any("Open Font License" in value for value in names),
                "detail": {"license_name_present": any("Open Font License" in value for value in names)},
            },
            "reserved_names_removed": {
                "passed": not any(name.lower() in joined_names.lower() for name in RESERVED_NAMES),
                "detail": {
                    "reserved_names": list(RESERVED_NAMES),
                    "note": "Copyright and license strings are excluded from primary-name policy by manual review.",
                },
            },
        }

        # Reserved names are allowed in copyright/license notices, but not in
        # family, full or PostScript names. Recalculate this check narrowly.
        primary_ids = {1, 3, 4, 6, 16, 17}
        primary_names = []
        for record in font["name"].names:
            if record.nameID not in primary_ids:
                continue
            try:
                primary_names.append(record.toUnicode())
            except UnicodeDecodeError:
                pass
        checks["reserved_names_removed"]["passed"] = not any(
            reserved.lower() in value.lower()
            for reserved in RESERVED_NAMES
            for value in primary_names
        )
        checks["reserved_names_removed"]["detail"]["primary_names"] = sorted(set(primary_names))

    return {
        "passed": all(check["passed"] for check in checks.values()),
        "candidate": str(candidate.resolve()),
        "checks": checks,
        "manual_reviews_required": [
            "traditional document style",
            "business style",
            "visual serif classification",
            "DOCX/XLSX/PPTX pagination corpus",
            "Mari-language typographic review",
            "legal conclusion on regulatory conformity",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--charset", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = audit(args.reference, args.candidate, args.charset)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

