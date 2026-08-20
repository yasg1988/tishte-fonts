#!/usr/bin/env python3
"""Audit the deterministic Tishte office-suite evaluation kit."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

from fontTools.ttLib import TTFont


REQUIRED = {
    "README.ru.md",
    "TECHNICAL_PROFILE.ru.md",
    "contacts.json",
    "legal/LICENSE.txt",
    "legal/THIRD_PARTY_NOTICES.md",
    "letters/commercial-partner.ru.md",
    "letters/libreoffice.ru.md",
    "letters/browser-form-short.ru.md",
    "MANIFEST.json",
    "SHA256SUMS.txt",
    "samples/sample-text.txt",
    "samples/Tishte-office-test.docx",
    "samples/Tishte-office-test.odt",
    "samples/Tishte-office-test.pptx",
    "samples/Tishte-office-test.xlsx",
    "specimens/tishte-serif-specimen.png",
    "specimens/tishte-sans-specimen.png",
}


def audit(root: Path, version: str) -> None:
    archive = root / "build" / "publishing" / "submissions" / (
        f"Tishte-v{version}-office-suite-kit.zip"
    )
    sidecar = archive.with_suffix(archive.suffix + ".sha256")
    expected_archive_hash = sidecar.read_text(encoding="ascii").split()[0]
    actual_archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual_archive_hash != expected_archive_hash:
        raise ValueError("Archive SHA-256 sidecar does not match")

    with ZipFile(archive) as source:
        names = set(source.namelist())
        missing = REQUIRED - names
        if missing:
            raise ValueError(f"Missing required files: {sorted(missing)}")

        ttf_names = sorted(name for name in names if name.startswith("fonts/ttf/") and name.endswith(".ttf"))
        woff2_names = sorted(name for name in names if name.startswith("fonts/web/") and name.endswith(".woff2"))
        css_names = sorted(name for name in names if name.startswith("fonts/web/") and name.endswith(".css"))
        if (len(ttf_names), len(woff2_names), len(css_names)) != (14, 14, 2):
            raise ValueError(
                "Expected 14 TTF, 14 WOFF2 and 2 CSS files, got "
                f"{len(ttf_names)}, {len(woff2_names)}, {len(css_names)}"
            )

        for name in ttf_names:
            font = TTFont(io.BytesIO(source.read(name)), lazy=True)
            try:
                vendor_id = font["OS/2"].achVendID
                if vendor_id != "MRIE":
                    raise ValueError(f"{name}: unexpected vendor ID {vendor_id!r}")
                if "name" not in font or "cmap" not in font:
                    raise ValueError(f"{name}: missing required OpenType table")
            finally:
                font.close()

        package_markers = {
            "samples/Tishte-office-test.docx": ("word/document.xml", "word/document.xml"),
            "samples/Tishte-office-test.xlsx": ("xl/workbook.xml", "xl/workbook.xml"),
            "samples/Tishte-office-test.pptx": ("ppt/presentation.xml", "ppt/slides/slide1.xml"),
            "samples/Tishte-office-test.odt": ("content.xml", "content.xml"),
        }
        for name, (marker, content_part) in package_markers.items():
            with ZipFile(io.BytesIO(source.read(name))) as package:
                if marker not in package.namelist():
                    raise ValueError(f"{name}: missing package part {marker}")
                xml_text = package.read(content_part).decode("utf-8")
                if "Tishte" not in xml_text:
                    raise ValueError(f"{name}: test content does not mention Tishte")
                embedded_fonts = [
                    part for part in package.namelist()
                    if Path(part).suffix.lower() in {".ttf", ".otf", ".woff", ".woff2"}
                ]
                if embedded_fonts:
                    raise ValueError(f"{name}: unexpectedly embeds fonts: {embedded_fonts}")
                metadata_part = "meta.xml" if name.endswith(".odt") else "docProps/core.xml"
                metadata = package.read(metadata_part).decode("utf-8")
                if "Tishte Project" not in metadata:
                    raise ValueError(f"{name}: creator metadata was not scrubbed")

        declared = {}
        for line in source.read("SHA256SUMS.txt").decode("ascii").splitlines():
            digest, name = line.split("  ", 1)
            declared[name] = digest
        checksum_targets = names - {"SHA256SUMS.txt"}
        if set(declared) != checksum_targets:
            raise ValueError("Internal SHA256SUMS.txt file list does not match archive")
        for name in sorted(checksum_targets):
            actual = hashlib.sha256(source.read(name)).hexdigest()
            if actual != declared[name]:
                raise ValueError(f"Checksum mismatch: {name}")

        manifest = json.loads(source.read("MANIFEST.json"))
        if manifest["version"] != version or manifest["vendor_id"] != "MRIE":
            raise ValueError("Manifest version or vendor ID mismatch")

    print(
        f"PASS: {archive.name}; 14 TTF, 14 WOFF2, 2 CSS, "
        f"vendor ID MRIE, all SHA-256 checks valid"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    audit(args.root.resolve(), args.version)


if __name__ == "__main__":
    main()
