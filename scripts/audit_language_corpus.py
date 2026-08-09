#!/usr/bin/env python3
"""Shape the multilingual production corpus and report exercised coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import unicodedata

import uharfbuzz as hb
from fontTools.ttLib import TTFont

from font_metrics_audit import load_charset
from versioning import version_tag


REQUIRED_BY_SECTION = {
    "meadow_mari": "ӒӓӦӧӰӱҤҥ",
    "hill_mari": "ӒӓӦӧӰӱӸӹ",
}


def shape(path: Path, text: str) -> dict:
    data = path.read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return {
        "glyphs": len(buffer.glyph_infos),
        "notdef": sum(info.codepoint == 0 for info in buffer.glyph_infos),
        "advance": sum(position.x_advance for position in buffer.glyph_positions),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    corpus = json.loads((root / "data" / "language-corpus.json").read_text(encoding="utf-8"))
    charset = load_charset(root / "data" / "document-charset.txt")
    sections = corpus["sections"]
    text_by_section = {name: " ".join(lines) for name, lines in sections.items()}
    inventory = "".join(chr(codepoint) for codepoint in charset)
    all_text = " ".join(text_by_section.values())
    tag = version_tag(args.version)

    linguistic_failures = []
    for section, required in REQUIRED_BY_SECTION.items():
        missing = sorted(set(required) - set(text_by_section.get(section, "")))
        if missing:
            linguistic_failures.append({"section": section, "missing": missing})

    styles = {}
    for style in ("Regular", "Bold", "Italic", "BoldItalic"):
        path = root / "build" / f"TishteSerif-{style}-{tag}.ttf"
        with TTFont(path, lazy=True) as ttfont:
            cmap_missing = [f"U+{codepoint:04X}" for codepoint in charset if codepoint not in ttfont.getBestCmap()]
        forms = {
            form: shape(path, unicodedata.normalize(form, all_text))
            for form in ("NFC", "NFD")
        }
        styles[style] = {
            "path": str(path),
            "forms": forms,
            "cmap_missing": cmap_missing,
            "passed": not cmap_missing and all(value["notdef"] == 0 for value in forms.values()),
        }

    textual_codepoints = sorted({ord(char) for char in "\n".join(text_by_section.values())})
    report = {
        "version": args.version,
        "sections": {name: {"lines": len(lines), "codepoints": len(set("".join(lines)))} for name, lines in sections.items()},
        "declared_charset": len(charset),
        "textual_codepoints": len(textual_codepoints),
        "inventory_codepoints": len(set(inventory)),
        "linguistic_inventory_failures": linguistic_failures,
        "styles": styles,
    }
    report["passed"] = not linguistic_failures and all(item["passed"] for item in styles.values())
    output = root / "artifacts" / "reports" / f"language-corpus-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
