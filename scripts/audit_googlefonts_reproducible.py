#!/usr/bin/env python3
"""Verify byte-for-byte reproducibility of the complete Google Fonts staging tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    output = root / "build" / "googlefonts"
    if not output.exists():
        raise SystemExit("Build Google Fonts packages before auditing reproducibility")
    before = hashes(output)
    subprocess.run(
        [sys.executable, str(root / "scripts" / "build_googlefonts.py"), "--version", args.version],
        cwd=root,
        check=True,
    )
    after = hashes(output)
    keys = sorted(set(before) | set(after))
    mismatches = [key for key in keys if before.get(key) != after.get(key)]
    report = {
        "version": args.version,
        "files": len(keys),
        "mismatches": mismatches,
        "passed": not mismatches,
    }
    report_path = root / "artifacts" / "reports" / "googlefonts" / "reproducibility.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Google Fonts staging: {len(keys)} files, {len(mismatches)} mismatches")
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
