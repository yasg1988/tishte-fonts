#!/usr/bin/env python3
"""Rebuild the four cleaned v0.070 SFD sources from the v0.060 sources."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from build_serif_from_sfd import find_fontforge


STYLES = ("Regular", "Bold", "Italic", "BoldItalic")


def run_fontforge(root: Path, script: Path, source: Path, output: Path) -> None:
    arguments = [str(path.relative_to(root)) for path in (script, source, output)]
    subprocess.run(
        [str(find_fontforge()), "-lang=py", "-script", *arguments],
        check=True,
        cwd=root,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    scripts = root / "scripts"
    iterations = root / "sources" / "tishte-serif" / "iterations"
    temporary = root / "build" / "v070-sources"
    temporary.mkdir(parents=True, exist_ok=True)
    for style in STYLES:
        source = iterations / f"TishteSerif-{style}-v060.sfd"
        cleaned = temporary / f"TishteSerif-{style}-cleaned.sfd"
        final = iterations / f"TishteSerif-{style}-v070.sfd"
        run_fontforge(root, scripts / "cleanup_serif_family_v070.py", source, cleaned)
        if style == "Regular":
            cleaned.replace(final)
        else:
            signed = temporary / f"TishteSerif-{style}-signed.sfd"
            run_fontforge(root, scripts / "apply_family_signature_v070.py", cleaned, signed)
            run_fontforge(root, scripts / "cleanup_serif_family_v070.py", signed, final)
        print(final)


if __name__ == "__main__":
    main()
