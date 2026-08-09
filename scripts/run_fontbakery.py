#!/usr/bin/env python3
"""Run the project FontBakery gate with documented compatibility exceptions."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


# These checks conflict with the fixed Times New Roman layout contract or apply
# only to inherited, out-of-scope historic glyphs. The rationale is maintained
# in docs/quality-policy-v090.md.
EXCLUDED_CHECKS = (
    "base_has_width",
    "case_mapping",
    "family/vertical_metrics",
    "family/win_ascent_and_descent",
    "os2_metrics_match_hhea",
    "tabular_kerning",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.090")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = "v" + args.version.partition(".")[2]
    fonts = [root / "build" / f"TishteSerif-{style}-{tag}.ttf" for style in ("Regular", "Bold", "Italic", "BoldItalic")]
    report_dir = root / "artifacts" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "fontbakery",
        "check-universal",
        *(str(font) for font in fonts),
        "--skip-network",
        "--succinct",
        "-n",
        "-C",
        "-l",
        "WARN",
        "--json",
        str(report_dir / f"fontbakery-{tag}.json"),
        "--ghmarkdown",
        str(report_dir / f"fontbakery-{tag}.md"),
    ]
    for check in EXCLUDED_CHECKS:
        command.extend(("-x", check))
    return subprocess.run(command, cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
