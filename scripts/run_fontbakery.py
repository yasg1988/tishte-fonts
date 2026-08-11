#!/usr/bin/env python3
"""Run the project FontBakery gate with documented compatibility exceptions."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from versioning import version_tag


# These checks conflict with the fixed Times New Roman layout contract or apply
# only to inherited, out-of-scope historic glyphs. The rationale is maintained
# in docs/quality-policy-v090.md.
EXCLUDED_CHECKS = (
    "family/vertical_metrics",
    "family/win_ascent_and_descent",
    "freetype_rasterizer",
    "os2_metrics_match_hhea",
    "tabular_kerning",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    fonts = [Path("build") / f"TishteSerif-{style}-{tag}.ttf" for style in ("Regular", "Bold", "Italic", "BoldItalic")]
    report_dir = root / "artifacts" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "fontbakery",
        "check-universal",
        *(str(font) for font in fonts),
        "--skip-network",
        "--succinct",
        "-J",
        "1",
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
    result = subprocess.run(command, cwd=root).returncode
    if result:
        return result
    # fontbakery 1.1 / freetype-py can report a false "cannot open resource"
    # on Windows when this check follows other checks in a multi-font run.
    # Running the exact check per file is deterministic and still gates every
    # binary; Linux CI uses the same sequence.
    for font in fonts:
        check = subprocess.run(
            [
                "fontbakery",
                "check-universal",
                str(font),
                "-c",
                "freetype_rasterizer",
                "--skip-network",
                "--succinct",
                "-J",
                "1",
                "-n",
                "-C",
                "-l",
                "WARN",
            ],
            cwd=root,
        )
        if check.returncode:
            return check.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
