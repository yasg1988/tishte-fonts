#!/usr/bin/env python3
"""Validate the generated website and npm distribution surface."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile


class LocalReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        key = "href" if tag in {"a", "link"} else "src" if tag in {"img", "script"} else None
        if key and values.get(key):
            self.references.append(values[key] or "")


def audit(root: Path) -> None:
    publishing = root / "build" / "publishing"
    site = publishing / "site"
    package = publishing / "npm"
    parser = LocalReferences()
    parser.feed((site / "index.html").read_text(encoding="utf-8"))
    missing = []
    for reference in parser.references:
        parsed = urlparse(reference)
        if parsed.scheme or reference.startswith(('#', 'mailto:')):
            continue
        target = site / parsed.path
        if not target.exists():
            missing.append(reference)
    if missing:
        raise ValueError(f"Broken local site references: {missing}")

    metadata = json.loads((package / "package.json").read_text(encoding="utf-8"))
    expected = {
        "name": "@yasg1988/tishte-fonts",
        "version": "1.0.0",
        "license": "OFL-1.1",
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(f"package.json {key}: expected {value!r}, got {metadata.get(key)!r}")
    woff2 = sorted((package / "woff2").glob("*.woff2"))
    ttf = sorted((package / "ttf").glob("*.ttf"))
    if len(woff2) != 12 or len(ttf) != 12:
        raise ValueError(f"Expected 12 WOFF2 and TTF files, got {len(woff2)} and {len(ttf)}")
    for css_name in ("index.css", "serif.css", "sans.css"):
        if not (package / css_name).exists():
            raise FileNotFoundError(package / css_name)

    submissions = publishing / "submissions"
    for family, expected_styles in (("Serif", 4), ("Sans", 8)):
        bundle = submissions / f"Tishte-{family}-v1.000-catalog.zip"
        with ZipFile(bundle) as source:
            names = source.namelist()
        font_names = [name for name in names if name.endswith(".ttf")]
        required = {"LICENSE.txt", "THIRD_PARTY_NOTICES.md", "PREVIEW.png", "README.txt"}
        if len(font_names) != expected_styles or not required.issubset(names):
            raise ValueError(f"Invalid catalog archive {bundle.name}: {names}")
        forbidden = [name for name in names if name.endswith((".woff", ".woff2", ".css", ".exe", ".ps1"))]
        if forbidden:
            raise ValueError(f"Catalog archive contains extra distribution files: {forbidden}")
    print(
        f"Publishing assets: {len(parser.references)} site references, "
        "12 WOFF2, 12 TTF, 2 catalog archives — OK"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    audit(args.root.resolve())


if __name__ == "__main__":
    main()
