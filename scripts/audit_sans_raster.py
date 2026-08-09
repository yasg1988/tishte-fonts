#!/usr/bin/env python3
"""Exercise every Tishte Sans style at practical UI pixel sizes with Pillow/FreeType."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import ImageFont

from build_sans_family import STYLES
from versioning import version_tag


SIZES = (11, 12, 14, 16, 20, 24, 32)
CORPORA = (
    "Русский интерфейс: документы, отчёты и уведомления",
    "Луговомарийский: Марий Эл, Ӓ ӓ Ӧ ӧ Ӱ ӱ Ҥ ҥ",
    "Горномарийский: Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ",
    "Latin UI: Settings, Dashboard, Search & Export",
    "0123456789 12,4 % № 147-р ₽ 2 583 640,70",
    "← ↑ → ↓ ↔ + − × ÷ = ≠ ≤ ≥ @ # &",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", default="1.000")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = version_tag(args.version)
    report = {"version": args.version, "sizes": list(SIZES), "styles": {}, "passed": True}
    for style in STYLES:
        path = root / "build" / f"TishteSans-{style.key}-{tag}.ttf"
        failures = []
        samples = []
        for size in SIZES:
            font = ImageFont.truetype(str(path), size=size)
            ascent, descent = font.getmetrics()
            if ascent <= 0 or descent < 0:
                failures.append(f"metrics@{size}")
            for text in CORPORA:
                bbox = font.getbbox(text)
                length = font.getlength(text)
                if bbox is None or bbox[2] <= bbox[0] or bbox[3] <= bbox[1] or length <= 0:
                    failures.append(f"empty@{size}:{text[:12]}")
                samples.append({"size": size, "text": text, "bbox": bbox, "advance": round(length, 3)})
        passed = not failures
        report["styles"][style.key] = {"path": str(path), "samples": samples, "failures": failures, "passed": passed}
        report["passed"] &= passed
        print(f"{style.key}: {len(samples)} raster samples; {'passed' if passed else failures}")
    output = root / "artifacts" / "reports" / f"sans-raster-{tag}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
