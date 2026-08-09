#!/usr/bin/env python3
"""Audit HarfBuzz shaping widths for the Tishte v0.070 document family."""

from __future__ import annotations

import json
from pathlib import Path

import uharfbuzz as hb

from build_serif_family_v060 import STYLES


CORPUS = {
    "russian": "Правительство Республики Марий Эл № 125 от 09.08.2026",
    "meadow_mari": "Ӓ ӓ Ӧ ӧ Ӱ ӱ Ҥ ҥ · Марий Эл Республикын Кугыжаныш Погынжо",
    "hill_mari": "Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ · Шачмы йӹлмем ылеш сӹлнӹ",
    "latin": "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz",
    "numbers": "0123456789 · 1 250 000,00 ₽ · € £ ¥ · ± × ÷ ≠ ≤ ≥",
    "kerning_pairs": "AV AW AY AT FA LT LV PA TA TO Tr Ty VA WA Yo ТА АУ ЛТ РА",
}

DOCUMENT_FEATURES = {"kern": False, "liga": False, "clig": False}


def shape(path: Path, text: str, features: dict[str, bool] | None = None) -> dict:
    data = path.read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, features)
    return {
        "advance": sum(position.x_advance for position in buffer.glyph_positions),
        "glyphs": len(buffer.glyph_infos),
        "notdef": sum(info.codepoint == 0 for info in buffer.glyph_infos),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    styles = {}
    for style in STYLES:
        reference = Path("C:/Windows/Fonts") / style.reference_name
        candidate = root / "build" / f"TishteSerif-{style.key}-v070.ttf"
        cases = {}
        for name, text in CORPUS.items():
            times_document = shape(reference, text, DOCUMENT_FEATURES)
            tishte_document = shape(candidate, text, DOCUMENT_FEATURES)
            times_default = shape(reference, text)
            tishte_default = shape(candidate, text)
            cases[name] = {
                "document_features": {
                    "times": times_document,
                    "tishte": tishte_document,
                    "advance_difference": tishte_document["advance"] - times_document["advance"],
                },
                "default_features": {
                    "times": times_default,
                    "tishte": tishte_default,
                    "advance_difference": tishte_default["advance"] - times_default["advance"],
                },
            }
        styles[style.key] = cases
    document_differences = [
        case["document_features"]["advance_difference"]
        for cases in styles.values()
        for case in cases.values()
    ]
    notdefs = [
        shaped[side]["notdef"]
        for cases in styles.values()
        for case in cases.values()
        for shaped in (case["document_features"], case["default_features"])
        for side in ("times", "tishte")
    ]
    result = {
        "version": "0.070",
        "policy": "Document compatibility is audited with discretionary kerning and ligatures disabled.",
        "styles": styles,
        "passed": all(value == 0 for value in document_differences) and all(value == 0 for value in notdefs),
    }
    output = root / "artifacts" / "reports" / "shaping-v070.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
