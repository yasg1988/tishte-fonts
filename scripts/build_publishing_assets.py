#!/usr/bin/env python3
"""Build the GitHub Pages site and npm package from signed release archives."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
from zipfile import ZipFile


FAMILIES = {
    "Serif": ("Tishte-Serif", "tishte-serif-v1000.css", 4),
    "Sans": ("Tishte-Sans", "tishte-sans-v1000.css", 8),
}


def clean_exact(path: Path, expected: Path) -> None:
    if path.resolve() != expected.resolve():
        raise ValueError(f"Refusing to clean unexpected path: {path.resolve()}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def archive(root: Path, slug: str, version: str) -> Path:
    path = root / "dist" / f"{slug}-v{version}.zip"
    if not path.exists():
        raise FileNotFoundError(f"Missing release archive: {path}")
    return path


def read_member(bundle: Path, suffix: str) -> bytes:
    with ZipFile(bundle) as source:
        matches = [name for name in source.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise ValueError(f"Expected one {suffix!r} in {bundle}, got {matches}")
        return source.read(matches[0])


def matching_members(bundle: Path, suffix: str) -> list[str]:
    with ZipFile(bundle) as source:
        return sorted(name for name in source.namelist() if name.endswith(suffix))


def extract_files(bundle: Path, members: list[str], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with ZipFile(bundle) as source:
        for member in members:
            target = destination / Path(member).name
            target.write_bytes(source.read(member))


def build(root: Path, version: str) -> tuple[Path, Path]:
    output = root / "build" / "publishing"
    clean_exact(output, root / "build" / "publishing")
    site_output = output / "site"
    npm_output = output / "npm"
    shutil.copytree(root / "site", site_output)
    shutil.copytree(root / "npm", npm_output)

    site_fonts = site_output / "fonts"
    site_fonts.mkdir()
    npm_woff2 = npm_output / "woff2"
    npm_ttf = npm_output / "ttf"
    css_by_family: dict[str, str] = {}
    total_woff2 = 0
    total_ttf = 0

    for family, (slug, css_name, expected_styles) in FAMILIES.items():
        bundle = archive(root, slug, version)
        webfonts = matching_members(bundle, ".woff2")
        desktop_fonts = matching_members(bundle, ".ttf")
        if len(webfonts) != expected_styles or len(desktop_fonts) != expected_styles:
            raise ValueError(
                f"{family}: expected {expected_styles} WOFF2/TTF files, "
                f"got {len(webfonts)}/{len(desktop_fonts)}"
            )
        extract_files(bundle, webfonts, site_fonts)
        extract_files(bundle, webfonts, npm_woff2)
        extract_files(bundle, desktop_fonts, npm_ttf)
        css = read_member(bundle, f"/fonts/web/{css_name}").decode("utf-8")
        css_by_family[family] = css
        total_woff2 += len(webfonts)
        total_ttf += len(desktop_fonts)

    (site_fonts / "fonts.css").write_text(
        css_by_family["Serif"].rstrip() + "\n\n" + css_by_family["Sans"].rstrip() + "\n",
        encoding="utf-8",
    )
    (npm_output / "serif.css").write_text(
        css_by_family["Serif"].replace("url('", "url('./woff2/").rstrip() + "\n",
        encoding="utf-8",
    )
    (npm_output / "sans.css").write_text(
        css_by_family["Sans"].replace("url('", "url('./woff2/").rstrip() + "\n",
        encoding="utf-8",
    )

    images = site_output / "images"
    images.mkdir()
    for name in ("tishte-serif-specimen.png", "tishte-sans-specimen.png"):
        shutil.copy2(root / "docs" / "images" / name, images / name)
    shutil.copy2(root / "LICENSE.txt", npm_output / "LICENSE.txt")
    shutil.copy2(root / "THIRD_PARTY_NOTICES.md", npm_output / "THIRD_PARTY_NOTICES.md")

    if total_woff2 != 12 or total_ttf != 12:
        raise ValueError(f"Expected 12 styles, got {total_woff2} WOFF2 and {total_ttf} TTF")
    print(f"Site: {site_output}")
    print(f"npm package: {npm_output}")
    return site_output, npm_output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    build(args.root.resolve(), args.version)


if __name__ == "__main__":
    main()
