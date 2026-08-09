#!/usr/bin/env python3
"""Audit canonical SFD metadata independently from generated binaries."""

from __future__ import annotations

import json
from pathlib import Path


EXPECTED = {
    "TishteSerif-Regular.sfd": ("TishteSerif-Regular", "Tishte Serif Regular"),
    "TishteSerif-Bold.sfd": ("TishteSerif-Bold", "Tishte Serif Bold"),
    "TishteSerif-Italic.sfd": ("TishteSerif-Italic", "Tishte Serif Italic"),
    "TishteSerif-BoldItalic.sfd": ("TishteSerif-BoldItalic", "Tishte Serif Bold Italic"),
}
REQUIRED = ("FamilyName: Tishte Serif", "Version: 1.000", "The Tinos Project Authors", "Tishte Project contributors", "Сергей Якунин", "SIL Open Font License")
FORBIDDEN = ("Tishte Serif Prototype", "Tinos is a trademark", "Monotype Imaging Inc.", '"Steve Matteson"')


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = {"files": {}, "passed": True}
    for filename, (font_name, full_name) in EXPECTED.items():
        path = root / "sources" / "tishte-serif" / filename
        text = path.read_text(encoding="utf-8")
        missing = [value for value in REQUIRED if value not in text]
        if f"FontName: {font_name}" not in text:
            missing.append(f"FontName: {font_name}")
        if f"FullName: {full_name}" not in text:
            missing.append(f"FullName: {full_name}")
        forbidden = [value for value in FORBIDDEN if value in text]
        passed = not missing and not forbidden
        report["files"][filename] = {"missing": missing, "forbidden": forbidden, "passed": passed}
        report["passed"] &= passed
        print(f"{filename}: {'passed' if passed else 'failed'}")
    output = root / "artifacts" / "reports" / "source-metadata-v1000.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
