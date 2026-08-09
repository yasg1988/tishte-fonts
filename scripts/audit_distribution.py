#!/usr/bin/env python3
"""Verify a Tishte ZIP, its outer checksum and every manifest entry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    archive = args.archive.resolve()
    expected = archive.with_suffix(".zip.sha256").read_text(encoding="ascii").split()[0]
    if digest(archive.read_bytes()) != expected:
        raise ValueError("outer SHA-256 mismatch")
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        roots = {name.split("/", 1)[0] for name in names}
        if len(roots) != 1 or any(".." in Path(name).parts for name in names):
            raise ValueError("unsafe or inconsistent archive paths")
        root = next(iter(roots))
        manifest = json.loads(package.read(f"{root}/MANIFEST.json"))
        for entry in manifest["files"]:
            data = package.read(f"{root}/{entry['path']}")
            if len(data) != entry["bytes"] or digest(data) != entry["sha256"]:
                raise ValueError(f"manifest mismatch: {entry['path']}")
        sums = package.read(f"{root}/SHA256SUMS.txt").decode("utf-8").splitlines()
        for line in sums:
            checksum, relative = line.split("  ", 1)
            if digest(package.read(f"{root}/{relative}")) != checksum:
                raise ValueError(f"SHA256SUMS mismatch: {relative}")
    print(f"{archive.name}: {len(manifest['files'])} manifest entries verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
