#!/usr/bin/env python3
"""Run the Google Fonts FontBakery profile on both staged families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


FAMILIES = ("tishteserif", "tishtesans")


def audit(root: Path, executable: str) -> dict:
    source_root = root / "build" / "googlefonts" / "ofl"
    report_root = root / "artifacts" / "reports" / "googlefonts"
    report_root.mkdir(parents=True, exist_ok=True)
    result = {"families": {}, "passed": True}
    # Some Windows FreeType builds cannot open font paths containing non-ASCII
    # characters. A temporary staging directory keeps the audit portable.
    with tempfile.TemporaryDirectory(prefix="tishte-gf-") as temporary:
        staging = Path(temporary)
        for family in FAMILIES:
            source = source_root / family
            if not source.exists():
                raise FileNotFoundError(f"Build package first: {source}")
            target = staging / family
            shutil.copytree(source, target)
            fonts = sorted(target.glob("*.ttf"))
            json_path = report_root / f"{family}.json"
            markdown_path = report_root / f"{family}.md"
            command = [
                executable,
                "check-googlefonts",
                *(str(path) for path in fonts),
                "--skip-network",
                "--succinct",
                "--loglevel",
                "WARN",
                "--json",
                str(json_path),
                "--ghmarkdown",
                str(markdown_path),
                "--jobs",
                "4",
            ]
            completed = subprocess.run(command, cwd=staging, check=False)
            data = json.loads(json_path.read_text(encoding="utf-8"))
            counts = data["result"]
            passed = not any(counts.get(level, 0) for level in ("ERROR", "FATAL", "FAIL"))
            result["families"][family] = {"counts": counts, "passed": passed}
            result["passed"] = result["passed"] and passed and completed.returncode == 0
            print(f"{family}: {counts}")
    summary = report_root / "summary.json"
    summary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if not result["passed"]:
        raise SystemExit(1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--fontbakery", default=shutil.which("fontbakery"))
    args = parser.parse_args()
    if not args.fontbakery:
        raise SystemExit("fontbakery executable was not found")
    audit(args.root.resolve(), args.fontbakery)


if __name__ == "__main__":
    main()
