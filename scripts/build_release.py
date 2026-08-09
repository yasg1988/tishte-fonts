#!/usr/bin/env python3
"""Run the complete deterministic Tishte Serif production build pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def run(root: Path, script: str, *arguments: str) -> None:
    subprocess.run(
        [sys.executable, str(root / "scripts" / script), *arguments],
        cwd=root,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    version = ["--version", args.version]
    run(root, "build_serif_family.py", *version)
    run(root, "subset_production_fonts.py", *version)
    run(root, "normalize_release_metadata.py", *version)
    run(root, "add_production_mark_positioning.py", *version)
    run(root, "sync_metric_pair_contract.py", *version)
    run(root, "build_webfonts.py", *version)


if __name__ == "__main__":
    main()
