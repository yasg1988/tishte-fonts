#!/usr/bin/env python3
"""Audit all four styles against their Times New Roman references."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from font_compliance_audit import audit


STYLES = {
    "Regular": "times.ttf",
    "Bold": "timesbd.ttf",
    "Italic": "timesi.ttf",
    "BoldItalic": "timesbi.ttf",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.060")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    version_tag = "v" + args.version.partition(".")[2]
    charset = root / "data" / "document-charset.txt"
    reports = {}
    for style, reference_name in STYLES.items():
        reports[style] = audit(
            Path("C:/Windows/Fonts") / reference_name,
            root / "build" / f"TishteSerif-{style}-{version_tag}.ttf",
            charset,
        )
    summary = {
        "version": args.version,
        "styles": reports,
        "passed": all(report["passed"] for report in reports.values()),
    }
    output_arg = args.output or Path(f"artifacts/reports/tishte-serif-family-{version_tag}.json")
    output = output_arg if output_arg.is_absolute() else root / output_arg
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
