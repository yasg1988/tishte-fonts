#!/usr/bin/env python3
"""Build a compact, deterministic end-user distribution archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from versioning import version_tag


STYLES = ("Regular", "Bold", "Italic", "BoldItalic")
ZIP_TIME = (2026, 8, 9, 0, 0, 0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    tag = version_tag(args.version)
    package_name = f"Tishte-Serif-v{args.version}"
    stage = root / "dist" / package_name
    archive = root / "dist" / f"{package_name}.zip"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    copies = {
        root / "README.md": stage / "README.md",
        root / "LICENSE.txt": stage / "LICENSE.txt",
        root / "THIRD_PARTY_NOTICES.md": stage / "THIRD_PARTY_NOTICES.md",
        root / "scripts" / "Install-TishteSerif.ps1": stage / "tools" / "Install-TishteSerif.ps1",
        root / "scripts" / "Uninstall-TishteSerif.ps1": stage / "tools" / "Uninstall-TishteSerif.ps1",
        root / "build" / "web" / f"tishte-serif-{tag}.css": stage / "fonts" / "web" / f"tishte-serif-{tag}.css",
    }
    for style in STYLES:
        copies[root / "build" / f"TishteSerif-{style}-{tag}.ttf"] = (
            stage / "fonts" / "ttf" / f"TishteSerif-{style}-{tag}.ttf"
        )
        copies[root / "build" / "web" / f"TishteSerif-{style}-{tag}.woff2"] = (
            stage / "fonts" / "web" / f"TishteSerif-{style}-{tag}.woff2"
        )
    for source, target in copies.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    files = sorted(path for path in stage.rglob("*") if path.is_file())
    manifest = {
        "package": package_name,
        "version": args.version,
        "developer": "Сергей Якунин",
        "license": "SIL Open Font License 1.1",
        "files": [
            {
                "path": path.relative_to(stage).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ],
    }
    manifest_path = stage / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files.append(manifest_path)
    sums = "".join(
        f"{sha256(path)}  {path.relative_to(stage).as_posix()}\n"
        for path in sorted(files)
    )
    (stage / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")

    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for path in sorted(p for p in stage.rglob("*") if p.is_file()):
            relative = f"{package_name}/{path.relative_to(stage).as_posix()}"
            info = zipfile.ZipInfo(relative, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes(), compresslevel=9)
    (archive.with_suffix(".zip.sha256")).write_text(
        f"{sha256(archive)}  {archive.name}\n", encoding="ascii"
    )
    print(f"{archive} ({archive.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
