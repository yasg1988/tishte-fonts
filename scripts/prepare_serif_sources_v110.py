#!/usr/bin/env python3
"""Apply the v0.100 reading-shape system across the four-style family."""

from __future__ import annotations

from pathlib import Path
import subprocess

from build_serif_from_sfd import find_fontforge


def run(root: Path, script: Path, source: Path, output: Path, version: str) -> None:
    arguments = [str(path.relative_to(root)) for path in (script, source, output)]
    subprocess.run(
        [str(find_fontforge()), "-lang=py", "-script", *arguments, version],
        check=True,
        cwd=root,
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    iterations = root / "sources" / "tishte-serif" / "iterations"
    for style in ("Regular", "Bold", "Italic", "BoldItalic"):
        source = iterations / f"TishteSerif-{style}-v100.sfd"
        output = iterations / f"TishteSerif-{style}-v110.sfd"
        script = root / "scripts" / ("stamp_sfd_version.py" if style == "Regular" else "develop_serif_v100.py")
        run(root, script, source, output, "0.110")
        print(output)


if __name__ == "__main__":
    main()
