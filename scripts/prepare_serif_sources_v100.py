#!/usr/bin/env python3
"""Prepare four v0.100 sources, with the originalisation pass on Regular."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from build_serif_from_sfd import find_fontforge


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    iterations = root / "sources" / "tishte-serif" / "iterations"
    for style in ("Regular", "Bold", "Italic", "BoldItalic"):
        source = iterations / f"TishteSerif-{style}-v070.sfd"
        output = iterations / f"TishteSerif-{style}-v100.sfd"
        if style == "Regular":
            arguments = [
                str(path.relative_to(root))
                for path in (root / "scripts" / "develop_serif_v100.py", source, output)
            ]
            subprocess.run(
                [str(find_fontforge()), "-lang=py", "-script", *arguments],
                check=True,
                cwd=root,
            )
        else:
            shutil.copy2(source, output)
        print(output)


if __name__ == "__main__":
    main()
