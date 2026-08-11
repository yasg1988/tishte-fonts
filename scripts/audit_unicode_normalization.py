#!/usr/bin/env python3
"""Verify that NFC and canonical NFD text shape identically in every style."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import unicodedata

import uharfbuzz as hb

from build_serif_family import STYLES
from font_metrics_audit import load_charset
from versioning import version_tag


def shape(path: Path, text: str) -> list[tuple[int, int, int, int, int]]:
    data = path.read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return [
        (
            info.codepoint,
            position.x_advance,
            position.y_advance,
            position.x_offset,
            position.y_offset,
        )
        for info, position in zip(buffer.glyph_infos, buffer.glyph_positions)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    charset = set(load_charset(root / "data" / "document-charset.txt"))
    canonical_cases = []
    for codepoint in sorted(charset):
        char = chr(codepoint)
        nfd = unicodedata.normalize("NFD", char)
        if nfd != char and all(ord(part) in charset for part in nfd):
            canonical_cases.append((codepoint, char, nfd))

    styles = {}
    passed = True
    for style in STYLES:
        path = root / "build" / f"TishteSerif-{style.key}-{tag}.ttf"
        failures = []
        for codepoint, nfc, nfd in canonical_cases:
            shaped_nfc = shape(path, nfc)
            shaped_nfd = shape(path, nfd)
            if shaped_nfc != shaped_nfd or any(item[0] == 0 for item in shaped_nfd):
                failures.append(
                    {
                        "codepoint": f"U+{codepoint:04X}",
                        "nfd": [f"U+{ord(char):04X}" for char in nfd],
                        "nfc_shape": shaped_nfc,
                        "nfd_shape": shaped_nfd,
                    }
                )
        styles[style.key] = {"cases": len(canonical_cases), "failures": failures}
        passed = passed and not failures

    result = {
        "version": args.version,
        "canonical_cases_per_style": len(canonical_cases),
        "styles": styles,
        "passed": passed,
    }
    output = root / "artifacts" / "reports" / f"unicode-normalization-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
