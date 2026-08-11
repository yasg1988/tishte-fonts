#!/usr/bin/env python3
"""Build the ten-style Tishte Sans family from a pinned OFL scaffold."""

from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass
import json
import math
from pathlib import Path

from fontTools import subset
from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.varLib.instancer import instantiateVariableFont

from font_metrics_audit import load_charset
from versioning import version_tag


FAMILY = "Tishte Sans"
VERSION = "1.100"
BUILD_TIMESTAMP = 3850070400
PROJECT_URL = "https://github.com/yasg1988/tishte-fonts"
LICENSE = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
LICENSE_URL = "https://openfontlicense.org"
COPYRIGHT = (
    "Copyright 2020 The Arimo Project Authors (https://github.com/googlefonts/arimo). "
    "Copyright 2026 Tishte Project contributors; modified for the Tishte Project "
    "(https://github.com/yasg1988/tishte-fonts)."
)
DESCRIPTION = (
    "Tishte Sans is a modified version of Arimo, developed as a free screen and "
    "interface typeface with Russian, Meadow Mari, Hill Mari and Latin coverage."
)


@dataclass(frozen=True)
class Style:
    key: str
    subfamily: str
    weight: int
    italic: bool

    @property
    def postscript(self) -> str:
        return f"TishteSans-{self.key}"

    @property
    def source(self) -> str:
        return "Arimo-Italic-wght.ttf" if self.italic else "Arimo-wght.ttf"


STYLES = (
    Style("Regular", "Regular", 400, False),
    Style("Italic", "Italic", 400, True),
    Style("Medium", "Medium", 500, False),
    Style("MediumItalic", "Medium Italic", 500, True),
    Style("SemiBold", "SemiBold", 600, False),
    Style("SemiBoldItalic", "SemiBold Italic", 600, True),
    Style("Bold", "Bold", 700, False),
    Style("BoldItalic", "Bold Italic", 700, True),
    Style("ExtraBold", "ExtraBold", 800, False),
    Style("ExtraBoldItalic", "ExtraBold Italic", 800, True),
)


def instantiate_weight(variable: TTFont, weight: int) -> TTFont:
    """Instantiate a weight, extrapolating a genuine 800 beyond Arimo's 700 master."""
    axis = next(axis for axis in variable["fvar"].axes if axis.axisTag == "wght")
    if weight <= axis.maxValue:
        return instantiateVariableFont(variable, {"wght": weight}, inplace=False, optimize=True)

    regular_weight = axis.defaultValue
    bold_weight = axis.maxValue
    if regular_weight >= bold_weight:
        raise ValueError("Cannot extrapolate a weight axis without a regular-to-bold range")
    factor = (weight - bold_weight) / (bold_weight - regular_weight)
    regular = instantiateVariableFont(variable, {"wght": regular_weight}, inplace=False, optimize=True)
    bold = instantiateVariableFont(variable, {"wght": bold_weight}, inplace=False, optimize=True)
    regular_glyf = regular["glyf"]
    bold_glyf = bold["glyf"]
    regular_metrics = regular["hmtx"].metrics
    bold_metrics = bold["hmtx"].metrics
    for glyph_name in bold.getGlyphOrder():
        regular_coordinates, _ = regular_glyf._getCoordinatesAndControls(glyph_name, regular_metrics)
        bold_coordinates, _ = bold_glyf._getCoordinatesAndControls(glyph_name, bold_metrics)
        if len(regular_coordinates) != len(bold_coordinates):
            raise ValueError(f"Cannot extrapolate incompatible glyph {glyph_name}")
        extrapolated = GlyphCoordinates(
            (
                round(bold_x + (bold_x - regular_x) * factor),
                round(bold_y + (bold_y - regular_y) * factor),
            )
            for (regular_x, regular_y), (bold_x, bold_y) in zip(regular_coordinates, bold_coordinates)
        )
        bold_glyf._setCoordinates(glyph_name, extrapolated, bold_metrics)
    bold["hhea"].advanceWidthMax = max(width for width, _ in bold_metrics.values())
    regular.close()
    return bold


def set_name(font: TTFont, name_id: int, value: str) -> None:
    font["name"].removeNames(nameID=name_id)
    font["name"].setName(value, name_id, 3, 1, 0x0409)


def clear_hints(font: TTFont) -> None:
    for glyph in font["glyf"].glyphs.values():
        if hasattr(glyph, "program"):
            glyph.program = Program()
    for tag in ("cvt ", "fpgm", "prep"):
        if tag in font:
            del font[tag]
    font["maxp"].maxSizeOfInstructions = 0


def apply_tishte_tension(font: TTFont) -> None:
    """Apply a restrained vertical taper while preserving advance widths."""
    glyf = font["glyf"]
    upem = font["head"].unitsPerEm
    for glyph in glyf.glyphs.values():
        if glyph.isComposite() or glyph.numberOfContours <= 0:
            continue
        coordinates = glyph.coordinates
        if not coordinates:
            continue
        xs = [point[0] for point in coordinates]
        center = (min(xs) + max(xs)) / 2
        transformed = []
        for x, y in coordinates:
            vertical = max(-0.8, min(1.4, y / upem))
            factor = 0.994 + 0.018 * vertical
            new_x = round(center + (x - center) * factor)
            if x > center:
                new_x += 2
            elif x < center:
                new_x -= 2
            transformed.append((new_x, y))
        glyph.coordinates = GlyphCoordinates(transformed)


def diamondize(font: TTFont) -> int:
    """Turn dot contours into the diamond motif shared by the Tishte family."""
    cmap = font.getBestCmap()
    targets = ".:;!?·•…ijİ̇̈"
    names = {cmap[ord(char)] for char in targets if ord(char) in cmap}
    changed = 0
    for name in names:
        glyph = font["glyf"][name]
        if glyph.isComposite() or glyph.numberOfContours <= 0:
            continue
        old_coordinates = list(glyph.coordinates)
        old_flags = list(glyph.flags)
        starts = [0] + [end + 1 for end in glyph.endPtsOfContours[:-1]]
        ends = list(glyph.endPtsOfContours)
        coordinates: list[tuple[int, int]] = []
        flags: list[int] = []
        end_points: list[int] = []
        local_changes = 0
        for start, end in zip(starts, ends):
            points = old_coordinates[start : end + 1]
            contour_flags = old_flags[start : end + 1]
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            ratio = width / height if height else 99
            if 35 <= width <= 420 and 35 <= height <= 360 and 0.45 <= ratio <= 2.2:
                cx = round((min(xs) + max(xs)) / 2)
                cy = round((min(ys) + max(ys)) / 2)
                rx = max(22, round(width / 2))
                ry = max(22, round(height / 2))
                points = [(cx, cy + ry), (cx + rx, cy), (cx, cy - ry), (cx - rx, cy)]
                contour_flags = [1, 1, 1, 1]
                local_changes += 1
            coordinates.extend(points)
            flags.extend(contour_flags)
            end_points.append(len(coordinates) - 1)
        if local_changes:
            glyph.coordinates = GlyphCoordinates(coordinates)
            glyph.flags = array("B", flags)
            glyph.endPtsOfContours = end_points
            changed += local_changes
    return changed


def decompose_overlap_prone_components(font: TTFont) -> None:
    """Flatten localized cedilla composites that FontForge flags as intersecting."""
    glyph_set = font.getGlyphSet()
    for name in (
        "Tcommaaccent",
        "Lcommaaccent.loclMAH",
        "lcommaaccent.loclMAH",
        "Aogonek",
        "aogonek",
        "Eogonek",
        "eogonek",
        "Iogonek",
        "iogonek",
        "Uogonek",
        "uogonek",
    ):
        if name not in font.getGlyphOrder() or not font["glyf"][name].isComposite():
            continue
        for component in font["glyf"][name].components:
            if component.glyphName == "ogonek":
                component.x -= 4
        recording = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(recording)
        pen = TTGlyphPen(None)
        recording.replay(pen)
        font["glyf"][name] = pen.glyph()


def subset_font(font: TTFont, codepoints: list[int]) -> None:
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


def add_stat(font: TTFont, style: Style) -> None:
    weight_names = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}
    axes = [
        {"tag": "wght", "name": "Weight", "ordering": 0, "values": [{"value": style.weight, "name": weight_names[style.weight], "flags": 0x2 if style.weight == 400 else 0}]},
        {"tag": "ital", "name": "Italic", "ordering": 1, "values": [{"value": 1 if style.italic else 0, "name": "Italic" if style.italic else "Roman", "flags": 0 if style.italic else 0x2, **({"linkedValue": 1} if not style.italic else {})}]},
    ]
    buildStatTable(font, axes, windowsNames=True, macNames=False)


def normalize_screen_metrics(font: TTFont) -> None:
    """Use a zero-gap vertical metric model and modern grayscale rasterization."""
    font["hhea"].lineGap = 0
    font["OS/2"].sTypoLineGap = 0
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {65535: 0x000F}
    font["gasp"] = gasp
    prep = newTable("prep")
    prep.program = Program()
    prep.program.fromBytecode(b"\xb8\x01\xff\x85\xb0\x04\x8d")
    font["prep"] = prep
    font["maxp"].maxSizeOfInstructions = 7


def normalize_math_widths(font: TTFont) -> None:
    """Center common operators on one advance width for stable UI alignment."""
    cmap = font.getBestCmap()
    operators = "+=<>±×÷−≈≠≤≥"
    names = [cmap[ord(char)] for char in operators if ord(char) in cmap]
    if not names:
        return
    target = font["hmtx"].metrics[cmap[ord("+")]][0]
    for name in names:
        width, lsb = font["hmtx"].metrics[name]
        font["hmtx"].metrics[name] = (target, lsb + round((target - width) / 2))


def remove_tabular_digit_kerning(font: TTFont) -> None:
    """Keep tabular digits invariant by removing GPOS kern pairs involving them."""
    if "GPOS" not in font:
        return
    cmap = font.getBestCmap()
    digits = {cmap[ord(char)] for char in "0123456789" if ord(char) in cmap}
    gpos = font["GPOS"].table
    if not gpos.FeatureList or not gpos.LookupList:
        return
    kern_lookups = {
        index
        for record in gpos.FeatureList.FeatureRecord
        if record.FeatureTag == "kern"
        for index in record.Feature.LookupListIndex
    }
    for index in kern_lookups:
        lookup = gpos.LookupList.Lookup[index]
        if lookup.LookupType != 2:
            continue
        for subtable in lookup.SubTable:
            if subtable.Format != 1:
                continue
            kept_glyphs = []
            kept_sets = []
            for first, pair_set in zip(subtable.Coverage.glyphs, subtable.PairSet):
                if first in digits:
                    continue
                pair_set.PairValueRecord = [
                    record for record in pair_set.PairValueRecord if record.SecondGlyph not in digits
                ]
                pair_set.PairValueCount = len(pair_set.PairValueRecord)
                if pair_set.PairValueRecord:
                    kept_glyphs.append(first)
                    kept_sets.append(pair_set)
            subtable.Coverage.glyphs = kept_glyphs
            subtable.PairSet = kept_sets
            subtable.PairSetCount = len(kept_sets)


def normalize_metadata(font: TTFont, style: Style, version: str) -> None:
    legacy_weight_names = {500: "Medium", 600: "SemiBold", 800: "ExtraBold"}
    legacy_family = FAMILY if style.weight in (400, 700) else f"{FAMILY} {legacy_weight_names[style.weight]}"
    if style.weight in (400, 700):
        if style.weight == 700 and style.italic:
            legacy_subfamily = "Bold Italic"
        elif style.weight == 700:
            legacy_subfamily = "Bold"
        elif style.italic:
            legacy_subfamily = "Italic"
        else:
            legacy_subfamily = "Regular"
    else:
        legacy_subfamily = "Italic" if style.italic else "Regular"
    names = {
        0: COPYRIGHT,
        1: legacy_family,
        2: legacy_subfamily,
        3: f"Version {version}; Tishte Sans; {style.key}",
        4: f"{FAMILY} {style.subfamily}",
        5: f"Version {version}",
        6: style.postscript,
        8: "Tishte Project",
        9: "Сергей Якунин",
        10: DESCRIPTION,
        11: PROJECT_URL,
        12: PROJECT_URL,
        13: LICENSE,
        14: LICENSE_URL,
        16: FAMILY,
        17: style.subfamily,
    }
    font["name"].names = [record for record in font["name"].names if record.platformID != 1]
    for name_id, value in names.items():
        set_name(font, name_id, value)
    os2 = font["OS/2"]
    os2.fsType = 0
    os2.achVendID = "MRIE"
    os2.usWeightClass = style.weight
    os2.fsSelection &= ~0x61
    os2.fsSelection |= (1 if style.italic else 0) | (32 if style.weight == 700 else 0) | (64 if style.weight != 700 and not style.italic else 0)
    os2.panose.bFamilyType = 2
    os2.panose.bSerifStyle = 11
    os2.panose.bWeight = {400: 5, 500: 6, 600: 7, 700: 8, 800: 9}[style.weight]
    os2.xAvgCharWidth = os2.recalcAvgCharWidth(font)
    font["head"].macStyle = (1 if style.weight == 700 else 0) | (2 if style.italic else 0)
    font["head"].fontRevision = float(version)
    font["head"].created = BUILD_TIMESTAMP
    font["head"].modified = BUILD_TIMESTAMP
    if style.italic:
        angle = font["post"].italicAngle
        font["hhea"].caretSlopeRise = font["head"].unitsPerEm
        font["hhea"].caretSlopeRun = round(math.tan(math.radians(-angle)) * font["head"].unitsPerEm)
    else:
        font["hhea"].caretSlopeRise = 1
        font["hhea"].caretSlopeRun = 0
    add_stat(font, style)


def build(
    root: Path,
    version: str = VERSION,
    charset: Path | None = None,
    output_dir: Path | None = None,
    canonical_names: bool = False,
) -> list[Path]:
    from fontTools.ttLib.removeOverlaps import removeOverlaps

    tag = version_tag(version)
    source_dir = root / "sources" / "upstream" / "arimo"
    codepoints = load_charset(charset or root / "data" / "document-charset.txt")
    output_dir = output_dir or root / "build"
    outputs = []
    report = {"version": version, "charset": len(codepoints), "styles": {}}
    for style in STYLES:
        variable = TTFont(source_dir / style.source, recalcTimestamp=False)
        font = instantiate_weight(variable, style.weight)
        font.recalcTimestamp = False
        variable.close()
        clear_hints(font)
        apply_tishte_tension(font)
        diamonds = diamondize(font)
        decompose_overlap_prone_components(font)
        removeOverlaps(font, removeHinting=True, ignoreErrors=False)
        subset_font(font, codepoints)
        normalize_screen_metrics(font)
        normalize_math_widths(font)
        remove_tabular_digit_kerning(font)
        normalize_metadata(font, style, version)
        suffix = "" if canonical_names else f"-{tag}"
        path = output_dir / f"TishteSans-{style.key}{suffix}.ttf"
        path.parent.mkdir(parents=True, exist_ok=True)
        font.save(path, reorderTables=True)
        font.close()
        with TTFont(path) as check:
            missing = [f"U+{cp:04X}" for cp in codepoints if cp not in check.getBestCmap()]
            report["styles"][style.key] = {"path": str(path), "bytes": path.stat().st_size, "diamond_contours": diamonds, "missing": missing, "passed": not missing and diamonds > 0}
        outputs.append(path)
        print(f"{style.key}: {path.name}; {diamonds} diamond contours")
    output = root / "artifacts" / "reports" / f"sans-build-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(item["passed"] for item in report["styles"].values()):
        raise ValueError("Sans build contract failed")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default=VERSION)
    parser.add_argument("--charset", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--canonical-names", action="store_true")
    args = parser.parse_args()
    charset = args.charset.resolve() if args.charset else None
    output_dir = args.output_dir.resolve() if args.output_dir else None
    build(args.root.resolve(), args.version, charset, output_dir, args.canonical_names)


if __name__ == "__main__":
    main()
