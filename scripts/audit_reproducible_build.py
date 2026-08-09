#!/usr/bin/env python3
"""Rebuild Tishte Serif and require byte-identical TTF and WOFF2 outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root: Path, tag: str) -> list[Path]:
    return sorted((root / "build").glob(f"*-{tag}.ttf")) + sorted(
        (root / "build" / "web").glob(f"*-{tag}.woff2")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.960")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = "v" + args.version.partition(".")[2]
    before_paths = files(root, tag)
    if len(before_paths) != 8:
        raise ValueError(f"expected 8 existing binaries, got {len(before_paths)}")
    before = {path.relative_to(root).as_posix(): digest(path) for path in before_paths}
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "build_release.py"),
            "--version",
            args.version,
        ],
        cwd=root,
        check=True,
    )
    after_paths = files(root, tag)
    after = {path.relative_to(root).as_posix(): digest(path) for path in after_paths}
    mismatches = [
        {"file": name, "first": before.get(name), "second": after.get(name)}
        for name in sorted(set(before) | set(after))
        if before.get(name) != after.get(name)
    ]
    report = {
        "version": args.version,
        "files": len(after),
        "hashes": after,
        "mismatches": mismatches,
        "passed": not mismatches and len(after) == 8,
    }
    output = root / "artifacts" / "reports" / f"reproducible-build-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Reproducible build: {len(after)} binaries, {len(mismatches)} mismatches")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
