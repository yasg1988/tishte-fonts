#!/usr/bin/env python3
"""Build Google Fonts review packages for Tishte Serif and Tishte Sans."""

from __future__ import annotations

import argparse
from math import ceil
from pathlib import Path
import shutil
import subprocess
import tempfile

from fontTools import subset
from fontTools.ttLib import TTFont, newTable
from PIL import Image

from build_sans_family import STYLES as SANS_STYLES
from build_sans_family import build as build_sans
from build_sans_family import normalize_screen_metrics
from build_sans_family import remove_tabular_digit_kerning
from build_serif_family import STYLES as SERIF_STYLES
from build_serif_family import build as build_serif
from build_serif_family import find_fontforge
from font_metrics_audit import load_charset
from add_production_mark_positioning import append_mark_lookup, append_soft_dotted_substitution
from render_sans_card import render as render_sans_card
from render_type_card import render as render_serif_card


VERSION = "1.000"
PROJECT_URL = "https://github.com/yasg1988/tishte-fonts"
GF_LICENSE_DESCRIPTION = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org"
)


def combined_charset(root: Path, work: Path) -> tuple[Path, list[int]]:
    codepoints = sorted(
        set(load_charset(root / "data" / "document-charset.txt"))
        | set(load_charset(root / "data" / "googlefonts-extra-charset.txt"))
    )
    # Google Fonts strips discretionary soft hyphens while serving subsets.
    codepoints.remove(0x00AD)
    path = work / "googlefonts-charset.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Generated union of the Tishte document set and GF Latin Core additions.\n"
        + "\n".join(
            " ".join(f"U+{cp:04X}" for cp in codepoints[index : index + 12])
            for index in range(0, len(codepoints), 12)
        )
        + "\n",
        encoding="utf-8",
    )
    return path, codepoints


def subset_font(source: Path, destination: Path, codepoints: list[int]) -> None:
    with TTFont(source, recalcTimestamp=False) as font:
        options = subset.Options()
        options.layout_features = ["*"]
        options.layout_scripts = ["*"]
        options.name_IDs = ["*"]
        options.name_languages = ["*"]
        options.glyph_names = True
        options.hinting = False
        options.notdef_glyph = True
        options.notdef_outline = True
        options.recommended_glyphs = False
        options.recalc_average_width = True
        options.recalc_max_context = True
        options.canonical_order = True
        worker = subset.Subsetter(options=options)
        worker.populate(unicodes=codepoints)
        worker.subset(font)
        destination.parent.mkdir(parents=True, exist_ok=True)
        font.save(destination, reorderTables=True)


def merge_duplicate_nbspace(path: Path) -> None:
    """Map NBSP to the identical space glyph and remove Arimo's legacy alias."""
    with TTFont(path, recalcTimestamp=False) as font:
        glyph_order = font.getGlyphOrder()
        if "nbspace" not in glyph_order:
            return
        # Decompile glyph-indexed tables before changing the order so fontTools
        # can remap every GSUB/GPOS/GDEF reference when it recompiles them.
        for tag in font.keys():
            font[tag]
        glyf = font["glyf"]
        hmtx = font["hmtx"]
        if hmtx.metrics["space"] != hmtx.metrics["nbspace"]:
            raise ValueError("space and nbspace metrics differ")
        if glyf["space"].compile(glyf) != glyf["nbspace"].compile(glyf):
            raise ValueError("space and nbspace outlines differ")
        for table in font["cmap"].tables:
            if table.isUnicode() and table.cmap.get(0x00A0) == "nbspace":
                table.cmap[0x00A0] = "space"
        glyph_order.remove("nbspace")
        glyf.glyphs.pop("nbspace")
        hmtx.metrics.pop("nbspace")
        font.setGlyphOrder(glyph_order)
        font["maxp"].numGlyphs = len(glyph_order)
        temporary = path.with_suffix(".nbspace.ttf")
        font.save(temporary, reorderTables=True)
    temporary.replace(path)


def family_bounds(paths: list[Path]) -> tuple[int, int, int]:
    y_min = 0
    y_max = 0
    upm = 0
    for path in paths:
        with TTFont(path) as font:
            upm = font["head"].unitsPerEm
            y_min = min(y_min, font["head"].yMin)
            y_max = max(y_max, font["head"].yMax)
    return y_min, y_max, upm


def google_metrics(paths: list[Path]) -> tuple[int, int]:
    y_min, y_max, upm = family_bounds(paths)
    minimum_span = ceil(upm * 1.2)
    ascent = y_max
    descent = y_min
    deficit = max(0, minimum_span - (ascent - descent))
    ascent += ceil(deficit * 2 / 3)
    descent -= deficit // 3
    return ascent, descent


def normalize_family(
    paths: list[Path], ribbi_styles: set[str], copyright_notice: str,
    smart_dropout: bool,
) -> None:
    ascent, descent = google_metrics(paths)
    for path in paths:
        style = path.stem.split("-", 1)[1]
        with TTFont(path, recalcTimestamp=False) as font:
            os2 = font["OS/2"]
            hhea = font["hhea"]
            hhea.ascent = ascent
            hhea.descent = descent
            hhea.lineGap = 0
            os2.sTypoAscender = ascent
            os2.sTypoDescender = descent
            os2.sTypoLineGap = 0
            os2.usWinAscent = ascent
            os2.usWinDescent = abs(descent)
            os2.fsSelection |= 1 << 7
            # The generated family/subfamily names are WWS-conformant.
            os2.fsSelection |= 1 << 8
            remove_tabular_digit_kerning(font)
            if smart_dropout:
                normalize_screen_metrics(font)
            for name_id, value in ((0, copyright_notice), (13, GF_LICENSE_DESCRIPTION)):
                font["name"].removeNames(nameID=name_id)
                font["name"].setName(value, name_id, 3, 1, 0x0409)
            meta = newTable("meta")
            meta.data = {"dlng": "Cyrl,Latn", "slng": "Cyrl,Latn"}
            font["meta"] = meta
            if style in ribbi_styles:
                font["name"].removeNames(nameID=16)
                font["name"].removeNames(nameID=17)
            temporary = path.with_suffix(".normalized.ttf")
            font.save(temporary, reorderTables=True)
        temporary.replace(path)


def ofl_text(root: Path, family: str) -> str:
    # FontBakery pins the canonical OFL line wrapping used by Google Fonts.
    from fontbakery.constants import OFL_BODY_TEXT

    copyright_notice = (
        f"Copyright 2026 The Tinos and Tishte Project Authors ({PROJECT_URL})"
        if family == "serif"
        else f"Copyright 2020-2026 The Arimo and Tishte Project Authors ({PROJECT_URL})"
    )
    return (
        copyright_notice
        + "\n"
        + OFL_BODY_TEXT
        + "\n"
    )


def metadata(family: str, styles: tuple, category: str) -> str:
    copyright_notice = (
        f"Copyright 2026 The Tinos and Tishte Project Authors ({PROJECT_URL})"
        if family == "Tishte Serif"
        else f"Copyright 2020-2026 The Arimo and Tishte Project Authors ({PROJECT_URL})"
    )
    records = []
    for style in styles:
        style_name = "italic" if "Italic" in style.key else "normal"
        records.append(
            "fonts {\n"
            f'  name: "{family}"\n'
            f'  style: "{style_name}"\n'
            f"  weight: {style.weight}\n"
            f'  filename: "{family.replace(" ", "")}-{style.key}.ttf"\n'
            f'  post_script_name: "{family.replace(" ", "")}-{style.key}"\n'
            f'  full_name: "{family} {style.subfamily}"\n'
            f'  copyright: "{copyright_notice}"\n'
            "}\n"
        )
    return (
        f'name: "{family}"\n'
        'designer: "Sergey Yakunin"\n'
        'license: "OFL"\n'
        f'category: "{category}"\n'
        'date_added: "2026-08-10"\n'
        + "".join(records)
        + 'subsets: "cyrillic"\nsubsets: "cyrillic-ext"\n'
        + 'subsets: "latin"\nsubsets: "latin-ext"\nsubsets: "menu"\n'
        + f'source {{\n  repository_url: "{PROJECT_URL}"\n'
        + '  branch: "main"\n}\n'
    )


def copy_documents(root: Path, destination: Path, slug: str) -> None:
    source = root / "googlefonts" / slug
    shutil.copy2(source / "README.md", destination / "README.md")
    shutil.copytree(source / "article", destination / "article", dirs_exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tishte-card-") as temporary:
        temporary_dir = Path(temporary)
        prefix = "TishteSerif" if slug == "tishte-serif" else "TishteSans"
        for path in destination.glob(f"{prefix}-*.ttf"):
            style = path.stem.split("-", 1)[1]
            shutil.copy2(path, temporary_dir / f"{prefix}-{style}-v1000.ttf")
        large = temporary_dir / "specimen-large.png"
        if slug == "tishte-serif":
            render_serif_card(temporary_dir, large)
        else:
            render_sans_card(temporary_dir, large)
        image_dir = destination / "article" / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        with Image.open(large) as image:
            image.resize((1536, 1024), Image.Resampling.LANCZOS).save(
                image_dir / "specimen.png", optimize=True
            )


def export_ufo_sources(root: Path, output: Path, slug: str, paths: list[Path]) -> None:
    source_dir = output / "upstream" / slug / "sources"
    source_dir.mkdir(parents=True, exist_ok=True)
    for path in paths:
        destination = source_dir / f"{path.stem}.ufo"
        subprocess.run(
            [
                str(find_fontforge()),
                "-lang=ff",
                "-c",
                "Open($1); Generate($2);",
                str(path),
                str(destination),
            ],
            check=True,
        )
    if slug == "tishte-serif":
        for source in sorted((root / "sources" / "tishte-serif").glob("*.sfd")):
            shutil.copy2(source, source_dir / source.name)
    (source_dir.parent / "BUILD.md").write_text(
        "# Generated review sources\n\n"
        "These UFOs are editable review exports of the canonical Google Fonts TTFs.\n"
        "The authoritative Tishte Serif SFDs and all transformation scripts remain in\n"
        "the repository. Tishte Sans is reproduced from the pinned Arimo input by\n"
        "`scripts/fetch_sans_upstream.py` and `scripts/build_sans_family.py`.\n",
        encoding="utf-8",
    )


def build(root: Path, version: str) -> list[Path]:
    output = root / "build" / "googlefonts"
    resolved = output.resolve()
    expected = (root / "build" / "googlefonts").resolve()
    if resolved != expected:
        raise ValueError(f"Refusing to clean unexpected path: {resolved}")
    if output.exists():
        shutil.rmtree(output)
    work = output / "work"
    charset_path, codepoints = combined_charset(root, work)

    raw_serif = work / "serif"
    raw_sans = work / "sans"
    build_serif(root, version, raw_serif, True)
    build_sans(root, version, charset_path, raw_sans, True)

    families = [
        ("tishte-serif", "Tishte Serif", SERIF_STYLES, "SERIF", raw_serif),
        ("tishte-sans", "Tishte Sans", SANS_STYLES, "SANS_SERIF", raw_sans),
    ]
    outputs: list[Path] = []
    for slug, family, styles, category, raw in families:
        destination = output / "ofl" / family.replace(" ", "").lower()
        destination.mkdir(parents=True, exist_ok=True)
        paths = []
        for style in styles:
            source = raw / f"{family.replace(' ', '')}-{style.key}.ttf"
            target = destination / source.name
            if slug == "tishte-serif":
                subset_font(source, target, codepoints)
            else:
                shutil.copy2(source, target)
            paths.append(target)
        copyright_notice = (
            f"Copyright 2026 The Tinos and Tishte Project Authors ({PROJECT_URL})"
            if slug == "tishte-serif"
            else f"Copyright 2020-2026 The Arimo and Tishte Project Authors ({PROJECT_URL})"
        )
        if slug == "tishte-serif":
            for path in paths:
                append_mark_lookup(path, codepoints)
        for path in paths:
            append_soft_dotted_substitution(path)
            if slug == "tishte-sans":
                merge_duplicate_nbspace(path)
        normalize_family(
            paths,
            {"Regular", "Italic", "Bold", "BoldItalic"},
            copyright_notice,
            slug == "tishte-serif",
        )
        (destination / "OFL.txt").write_text(ofl_text(root, "serif" if slug.endswith("serif") else "sans"), encoding="utf-8")
        (destination / "METADATA.pb").write_text(metadata(family, styles, category), encoding="utf-8")
        copy_documents(root, destination, slug)
        export_ufo_sources(root, output, slug, paths)
        outputs.extend(paths)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default=VERSION)
    args = parser.parse_args()
    outputs = build(args.root.resolve(), args.version)
    print(f"Built {len(outputs)} Google Fonts review binaries.")


if __name__ == "__main__":
    main()
