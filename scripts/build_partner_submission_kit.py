#!/usr/bin/env python3
"""Build a deterministic, two-family evaluation kit for office-suite vendors."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ZIP_TIMESTAMP = (2026, 8, 20, 0, 0, 0)
FAMILIES = {
    "Tishte-Serif": 4,
    "Tishte-Sans": 10,
}
REPORTS = (
    "document-layout-v1100.json",
    "fontbakery-v1100.md",
    "fontbakery-sans-v1100.md",
    "language-corpus-v1100.json",
    "legal-metadata-v1100.json",
    "opentype-v1100.json",
    "reproducible-build-v1100.json",
    "sans-build-v1100.json",
    "superfamily-audit-v1100.json",
    "unicode-normalization-v1100.json",
)


def zip_version(version: str) -> str:
    return version.replace(".", "")


def add_bytes(target: ZipFile, name: str, data: bytes) -> None:
    info = ZipInfo(name.replace("\\", "/"), ZIP_TIMESTAMP)
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    target.writestr(info, data)


def add_file(target: ZipFile, source: Path, name: str) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    add_bytes(target, name, source.read_bytes())


def release_members(bundle: Path, suffix: str) -> list[str]:
    with ZipFile(bundle) as source:
        return sorted(name for name in source.namelist() if name.endswith(suffix))


def release_member_bytes(bundle: Path, member: str) -> bytes:
    with ZipFile(bundle) as source:
        return source.read(member)


def build(root: Path, version: str) -> Path:
    output_dir = root / "build" / "publishing" / "submissions"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"Tishte-v{version}-office-suite-kit.zip"
    version_token = zip_version(version)

    entries: dict[str, bytes] = {}

    for family, expected_count in FAMILIES.items():
        bundle = root / "dist" / f"{family}-v{version}.zip"
        if not bundle.is_file():
            raise FileNotFoundError(f"Missing official release archive: {bundle}")
        ttf_members = release_members(bundle, ".ttf")
        woff2_members = release_members(bundle, ".woff2")
        if len(ttf_members) != expected_count or len(woff2_members) != expected_count:
            raise ValueError(
                f"{family}: expected {expected_count} TTF/WOFF2 files, "
                f"got {len(ttf_members)}/{len(woff2_members)}"
            )
        for member in ttf_members:
            entries[f"fonts/ttf/{Path(member).name}"] = release_member_bytes(bundle, member)
        for member in woff2_members:
            entries[f"fonts/web/{Path(member).name}"] = release_member_bytes(bundle, member)
        css_members = release_members(bundle, f"v{version_token}.css")
        if len(css_members) != 1:
            raise ValueError(f"{family}: expected one versioned CSS file, got {css_members}")
        css_member = css_members[0]
        entries[f"fonts/web/{Path(css_member).name}"] = release_member_bytes(bundle, css_member)

    legal_files = (
        "LICENSE.txt",
        "THIRD_PARTY_NOTICES.md",
        "AUTHORS.txt",
        "CONTRIBUTORS.txt",
    )
    for name in legal_files:
        entries[f"legal/{name}"] = (root / name).read_bytes()

    partner_root = root / "partner-kit"
    for source in sorted(path for path in partner_root.rglob("*") if path.is_file()):
        relative = source.relative_to(partner_root).as_posix()
        if relative.startswith("samples/"):
            name = relative
        elif relative.startswith("letters/"):
            name = relative
        else:
            name = relative
        entries[name] = source.read_bytes()

    for family in ("serif", "sans"):
        source = root / "docs" / "images" / f"tishte-{family}-specimen.png"
        entries[f"specimens/{source.name}"] = source.read_bytes()

    for name in REPORTS:
        source = root / "artifacts" / "reports" / name
        if source.is_file():
            entries[f"reports/{name}"] = source.read_bytes()

    manifest = {
        "schema": 1,
        "project": "Tishte",
        "version": version,
        "vendor_id": "MRIE",
        "families": {"Tishte Serif": 4, "Tishte Sans": 10},
        "license": "SIL Open Font License 1.1",
        "source_release_archives": [
            f"Tishte-Serif-v{version}.zip",
            f"Tishte-Sans-v{version}.zip",
        ],
        "files": sorted(entries),
    }
    entries["MANIFEST.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")

    sums = [
        f"{hashlib.sha256(data).hexdigest()}  {name}"
        for name, data in sorted(entries.items())
    ]
    entries["SHA256SUMS.txt"] = ("\n".join(sums) + "\n").encode("ascii")

    with ZipFile(output, "w") as target:
        for name, data in sorted(entries.items()):
            add_bytes(target, name, data)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="ascii"
    )
    print(f"{output}: {len(entries)} files, sha256={digest}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    build(args.root.resolve(), args.version)


if __name__ == "__main__":
    main()
