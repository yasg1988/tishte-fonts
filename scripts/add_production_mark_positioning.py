#!/usr/bin/env python3
"""Add deterministic mark-to-base positioning for the declared production charset."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import unicodedata

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

from font_metrics_audit import load_charset
from versioning import version_tag


TOP_MARKS = (0x0300, 0x0301, 0x0302, 0x0303, 0x0304, 0x0306, 0x0307,
             0x0308, 0x030A, 0x030B, 0x030C)
BOTTOM_MARKS = (0x0327, 0x0328)
STYLES = ("Regular", "Bold", "Italic", "BoldItalic")


def glyph_name(name: str) -> str:
    """Return an unambiguous Adobe feature-file glyph reference."""
    return "\\" + name


def bounds(font: TTFont, name: str) -> tuple[int, int, int, int]:
    glyph_set = font.getGlyphSet()
    pen = BoundsPen(glyph_set)
    glyph_set[name].draw(pen)
    if pen.bounds is None:
        return (0, 0, 0, 0)
    return tuple(round(value) for value in pen.bounds)


def feature_source(font: TTFont, codepoints: list[int]) -> str:
    cmap = font.getBestCmap()
    mark_groups = {"top": TOP_MARKS, "bottom": BOTTOM_MARKS}
    lines: list[str] = []
    for group, points in mark_groups.items():
        seen = set()
        for codepoint in points:
            name = cmap[codepoint]
            if name in seen:
                continue
            seen.add(name)
            x_min, y_min, x_max, y_max = bounds(font, name)
            x = round((x_min + x_max) / 2)
            y = y_min if group == "top" else y_max
            lines.append(
                f"markClass {glyph_name(name)} <anchor {x} {y}> @MC_{group};"
            )

    base_names: list[str] = []
    seen_bases = set()
    for codepoint in codepoints:
        if unicodedata.category(chr(codepoint)).startswith("L") or codepoint == 0x25CC:
            name = cmap[codepoint]
            if name not in seen_bases:
                seen_bases.add(name)
                base_names.append(name)

    lines.append("feature mark {")
    for name in base_names:
        x_min, y_min, x_max, y_max = bounds(font, name)
        x = round((x_min + x_max) / 2)
        lines.append(
            f"  pos base {glyph_name(name)} <anchor {x} {y_max + 20}> mark @MC_top"
            f" <anchor {x} {y_min - 20}> mark @MC_bottom;"
        )
    lines.append("} mark;")
    return "\n".join(lines) + "\n"


def attach_feature_to_scripts(gpos: otTables.GPOS, feature_index: int) -> None:
    if gpos.ScriptList is None:
        raise ValueError("candidate GPOS has no ScriptList")
    for script_record in gpos.ScriptList.ScriptRecord:
        script = script_record.Script
        lang_systems = []
        if script.DefaultLangSys is not None:
            lang_systems.append(script.DefaultLangSys)
        lang_systems.extend(record.LangSys for record in script.LangSysRecord)
        for lang_system in lang_systems:
            if feature_index not in lang_system.FeatureIndex:
                lang_system.FeatureIndex.append(feature_index)
                lang_system.FeatureCount = len(lang_system.FeatureIndex)


def sort_feature_records(gpos: otTables.GPOS) -> None:
    """Sort feature tags as required by OTS and remap LangSys indices."""
    records = gpos.FeatureList.FeatureRecord
    order = sorted(range(len(records)), key=lambda index: records[index].FeatureTag)
    if order == list(range(len(records))):
        return
    old_to_new = {old: new for new, old in enumerate(order)}
    gpos.FeatureList.FeatureRecord = [records[index] for index in order]
    for script_record in gpos.ScriptList.ScriptRecord:
        script = script_record.Script
        lang_systems = []
        if script.DefaultLangSys is not None:
            lang_systems.append(script.DefaultLangSys)
        lang_systems.extend(record.LangSys for record in script.LangSysRecord)
        for lang_system in lang_systems:
            lang_system.FeatureIndex = sorted(
                old_to_new[index] for index in lang_system.FeatureIndex
            )
            if lang_system.ReqFeatureIndex != 0xFFFF:
                lang_system.ReqFeatureIndex = old_to_new[lang_system.ReqFeatureIndex]


def append_mark_lookup(path: Path, codepoints: list[int]) -> None:
    with TTFont(path, recalcTimestamp=False) as source_font:
        source = feature_source(source_font, codepoints)

    with TTFont(path, recalcTimestamp=False) as compiler_font:
        addOpenTypeFeaturesFromString(compiler_font, source, tables=["GPOS"])
        generated = compiler_font["GPOS"].table
        mark_records = [
            record for record in generated.FeatureList.FeatureRecord
            if record.FeatureTag == "mark"
        ]
        if len(mark_records) != 1:
            raise ValueError(f"expected one generated mark feature, got {len(mark_records)}")
        generated_indices = mark_records[0].Feature.LookupListIndex
        generated_lookups = [deepcopy(generated.LookupList.Lookup[i]) for i in generated_indices]
        if not generated_lookups:
            raise ValueError("generated mark feature contains no lookups")

    with TTFont(path, recalcTimestamp=False) as font:
        gpos = font["GPOS"].table
        new_indices = []
        for lookup in generated_lookups:
            new_indices.append(len(gpos.LookupList.Lookup))
            gpos.LookupList.Lookup.append(lookup)
        gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)

        mark_records = [
            record for record in gpos.FeatureList.FeatureRecord
            if record.FeatureTag == "mark"
        ]
        if mark_records:
            for record in mark_records:
                for index in new_indices:
                    if index not in record.Feature.LookupListIndex:
                        record.Feature.LookupListIndex.append(index)
                record.Feature.LookupCount = len(record.Feature.LookupListIndex)
        else:
            record = otTables.FeatureRecord()
            record.FeatureTag = "mark"
            record.Feature = otTables.Feature()
            record.Feature.FeatureParams = None
            record.Feature.LookupListIndex = new_indices
            record.Feature.LookupCount = len(new_indices)
            gpos.FeatureList.FeatureRecord.append(record)
            gpos.FeatureList.FeatureCount = len(gpos.FeatureList.FeatureRecord)
            attach_feature_to_scripts(gpos, gpos.FeatureList.FeatureCount - 1)

        sort_feature_records(gpos)

        temporary = path.with_suffix(".marks.ttf")
        font.save(temporary, reorderTables=True)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    codepoints = load_charset(root / "data" / "document-charset.txt")
    for style in STYLES:
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        append_mark_lookup(path, codepoints)
        print(f"{style}: added production mark positioning")


if __name__ == "__main__":
    main()
