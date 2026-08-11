#!/usr/bin/env python3
"""Run the deterministic Tishte Sans build pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def run(root: Path, script: str, *arguments: str) -> None:
    subprocess.run([sys.executable, str(root / "scripts" / script), *arguments], cwd=root, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = args.root.resolve()
    run(root, "fetch_sans_upstream.py")
    run(root, "build_sans_family.py", "--version", args.version)
    run(root, "build_sans_webfonts.py", "--version", args.version)


if __name__ == "__main__":
    main()
