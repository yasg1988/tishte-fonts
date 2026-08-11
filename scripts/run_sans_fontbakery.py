#!/usr/bin/env python3
"""Run the FontBakery quality gate for all Tishte Sans styles."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from build_sans_family import STYLES
from versioning import version_tag


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    fonts = [Path("build") / f"TishteSans-{style.key}-{tag}.ttf" for style in STYLES]
    report_dir = root / "artifacts" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    command = ["fontbakery", "check-universal", *(str(font) for font in fonts), "--skip-network", "--succinct", "-J", "1", "-n", "-C", "-l", "WARN", "--json", str(report_dir / f"fontbakery-sans-{tag}.json"), "--ghmarkdown", str(report_dir / f"fontbakery-sans-{tag}.md")]
    result = subprocess.run(command, cwd=root)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
