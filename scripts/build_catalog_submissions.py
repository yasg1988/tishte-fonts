#!/usr/bin/env python3
"""Build minimal one-family ZIP archives for curated font catalogs."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from build_publishing_assets import FAMILIES, archive, matching_members


ZIP_TIMESTAMP = (2026, 8, 10, 0, 0, 0)


def add_bytes(target: ZipFile, name: str, data: bytes) -> None:
    info = ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    target.writestr(info, data)


def description(family: str) -> str:
    purpose = (
        "a document serif with Times New Roman-compatible metrics"
        if family == "Serif"
        else "a screen-oriented sans serif for interfaces, presentations and the web"
    )
    styles = "Regular, Italic, Bold and Bold Italic" if family == "Serif" else (
        "Regular, Italic, Medium, Medium Italic, SemiBold, SemiBold Italic, Bold and Bold Italic"
    )
    return (
        f"Tishte {family} is {purpose}.\n\n"
        "It supports Meadow Mari, Hill Mari, Russian and extended Latin, including numerals, "
        "currency signs, punctuation, mathematical and document symbols.\n\n"
        f"Styles: {styles}.\n"
        "Designer: Sergey Yakunin\n"
        "Version: 1.000\n"
        "License: SIL Open Font License 1.1\n"
        "Website: https://yasg1988.github.io/tishte-fonts/\n"
        "Source: https://github.com/yasg1988/tishte-fonts\n"
    )


def build(root: Path, version: str) -> list[Path]:
    destination = root / "build" / "publishing" / "submissions"
    destination.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for family, (slug, _css_name, expected_styles) in FAMILIES.items():
        bundle = archive(root, slug, version)
        members = matching_members(bundle, ".ttf")
        if len(members) != expected_styles:
            raise ValueError(f"{family}: expected {expected_styles} TTF files, got {len(members)}")
        output = destination / f"{slug}-v{version}-catalog.zip"
        with ZipFile(bundle) as source, ZipFile(output, "w") as target:
            for member in members:
                add_bytes(target, Path(member).name, source.read(member))
            add_bytes(target, "LICENSE.txt", (root / "LICENSE.txt").read_bytes())
            add_bytes(target, "THIRD_PARTY_NOTICES.md", (root / "THIRD_PARTY_NOTICES.md").read_bytes())
            specimen = root / "docs" / "images" / f"tishte-{family.lower()}-specimen.png"
            add_bytes(target, "PREVIEW.png", specimen.read_bytes())
            add_bytes(target, "README.txt", description(family).encode("utf-8"))
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        output.with_suffix(output.suffix + ".sha256").write_text(
            f"{digest}  {output.name}\n", encoding="ascii"
        )
        outputs.append(output)
        print(f"{output.name}: {len(members)} TTF, {digest}")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    build(args.root.resolve(), args.version)


if __name__ == "__main__":
    main()
