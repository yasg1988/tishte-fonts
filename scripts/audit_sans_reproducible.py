#!/usr/bin/env python3
"""Require byte-identical Tishte Sans TTF and WOFF2 rebuilds."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

from versioning import version_tag


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    paths = sorted((root / "build").glob(f"TishteSans-*-{tag}.ttf")) + sorted((root / "build" / "web").glob(f"TishteSans-*-{tag}.woff2"))
    if len(paths) != 16:
        raise ValueError(f"expected 16 Sans binaries, got {len(paths)}")
    before = {path: digest(path) for path in paths}
    subprocess.run([sys.executable, str(root / "scripts" / "build_sans_release.py"), "--version", args.version], cwd=root, check=True)
    mismatches = [path for path, value in before.items() if digest(path) != value]
    print(f"Sans reproducible build: {len(paths)} binaries, {len(mismatches)} mismatches")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
