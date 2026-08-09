#!/usr/bin/env python3
"""Build WOFF2 files and verify the production charset survives conversion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

from build_serif_family_v060 import STYLES
from font_metrics_audit import load_charset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="0.090")
    args = parser.parse_args()
    root = args.root.resolve()
    version_tag = "v" + args.version.partition(".")[2]
    charset = load_charset(root / "data" / "document-charset.txt")
    output_dir = root / "build" / "web"
    output_dir.mkdir(parents=True, exist_ok=True)
    styles = {}
    css_blocks = []
    passed = True
    for style in STYLES:
        ttf_path = root / "build" / f"TishteSerif-{style.key}-{version_tag}.ttf"
        woff2_path = output_dir / f"TishteSerif-{style.key}-{version_tag}.woff2"
        with TTFont(ttf_path, recalcTimestamp=False) as font:
            font.flavor = "woff2"
            font.save(woff2_path, reorderTables=True)
        with TTFont(ttf_path, lazy=False) as ttf, TTFont(woff2_path, lazy=False) as webfont:
            ttf_cmap = ttf.getBestCmap()
            web_cmap = webfont.getBestCmap()
            missing = [f"U+{cp:04X}" for cp in charset if cp not in web_cmap]
            width_mismatches = []
            for codepoint in charset:
                ttf_glyph = ttf_cmap.get(codepoint)
                web_glyph = web_cmap.get(codepoint)
                if ttf_glyph is None or web_glyph is None:
                    continue
                ttf_width = ttf["hmtx"].metrics[ttf_glyph][0]
                web_width = webfont["hmtx"].metrics[web_glyph][0]
                if ttf_width != web_width:
                    width_mismatches.append(
                        {"codepoint": f"U+{codepoint:04X}", "ttf": ttf_width, "woff2": web_width}
                    )
            style_passed = not missing and not width_mismatches
            styles[style.key] = {
                "woff2": str(woff2_path),
                "bytes": woff2_path.stat().st_size,
                "missing": missing,
                "width_mismatches": width_mismatches,
                "passed": style_passed,
            }
            passed = passed and style_passed
            print(woff2_path)
        css_blocks.append(
            "\n".join(
                (
                    "@font-face {",
                    "  font-family: 'Tishte Serif';",
                    f"  src: url('{woff2_path.name}') format('woff2');",
                    f"  font-weight: {style.weight};",
                    f"  font-style: {'italic' if 'Italic' in style.subfamily else 'normal'};",
                    "  font-display: swap;",
                    "}",
                )
            )
        )
    css_path = output_dir / f"tishte-serif-{version_tag}.css"
    css_path.write_text("\n\n".join(css_blocks) + "\n", encoding="utf-8")
    result = {"version": args.version, "charset": len(charset), "css": str(css_path), "styles": styles, "passed": passed}
    report = root / "artifacts" / "reports" / f"webfonts-{version_tag}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
