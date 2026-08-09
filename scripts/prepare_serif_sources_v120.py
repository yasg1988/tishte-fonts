#!/usr/bin/env python3
"""Build four v0.120 SFD sources with the service-capital design pass."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

from build_serif_from_sfd import find_fontforge


SOURCE_TIMESTAMP = 1767225600  # 2026-01-01T00:00:00Z


def normalize_timestamp(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized, count = re.subn(
        r"^ModificationTime: \d+$",
        f"ModificationTime: {SOURCE_TIMESTAMP}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"expected one ModificationTime in {path}, got {count}")
    normalized = "\n".join(line.rstrip() for line in normalized.splitlines()) + "\n"
    path.write_text(normalized, encoding="utf-8", newline="\n")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    iterations = root / "sources" / "tishte-serif" / "iterations"
    script = root / "scripts" / "develop_serif_v120.py"
    for style in ("Regular", "Bold", "Italic", "BoldItalic"):
        source = iterations / f"TishteSerif-{style}-v110.sfd"
        output = iterations / f"TishteSerif-{style}-v120.sfd"
        arguments = [str(path.relative_to(root)) for path in (script, source, output)]
        subprocess.run(
            [str(find_fontforge()), "-lang=py", "-script", *arguments, "0.120"],
            cwd=root,
            check=True,
        )
        normalize_timestamp(output)
        print(output)


if __name__ == "__main__":
    main()
