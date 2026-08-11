#!/usr/bin/env python3
"""Build Tishte Sans WOFF2 files and CSS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

from build_sans_family import STYLES
from font_metrics_audit import load_charset
from versioning import version_tag


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.100")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    charset = load_charset(root / "data" / "document-charset.txt")
    output_dir = root / "build" / "web"
    output_dir.mkdir(parents=True, exist_ok=True)
    blocks = []
    report = {"version": args.version, "styles": {}, "passed": True}
    for style in STYLES:
        ttf_path = root / "build" / f"TishteSans-{style.key}-{tag}.ttf"
        woff2_path = output_dir / f"TishteSans-{style.key}-{tag}.woff2"
        with TTFont(ttf_path, recalcTimestamp=False) as font:
            font.flavor = "woff2"
            font.save(woff2_path, reorderTables=True)
        with TTFont(ttf_path) as ttf, TTFont(woff2_path) as web:
            missing = [f"U+{cp:04X}" for cp in charset if cp not in web.getBestCmap()]
            passed = not missing and len(ttf.getBestCmap()) == len(web.getBestCmap())
        report["styles"][style.key] = {"path": str(woff2_path), "bytes": woff2_path.stat().st_size, "missing": missing, "passed": passed}
        report["passed"] &= passed
        blocks.append("\n".join(("@font-face {", "  font-family: 'Tishte Sans';", f"  src: url('{woff2_path.name}') format('woff2');", f"  font-weight: {style.weight};", f"  font-style: {'italic' if style.italic else 'normal'};", "  font-display: swap;", "}")))
        print(woff2_path)
    css = output_dir / f"tishte-sans-{tag}.css"
    css.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    output = root / "artifacts" / "reports" / f"sans-webfonts-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
