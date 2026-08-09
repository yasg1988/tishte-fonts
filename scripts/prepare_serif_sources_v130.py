#!/usr/bin/env python3
"""Build four canonical v0.130 SFD sources with numeral/symbol design."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

from build_serif_from_sfd import find_fontforge


SOURCE_TIMESTAMP = 1767225600


def normalize(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(
        r"^ModificationTime: \d+$",
        f"ModificationTime: {SOURCE_TIMESTAMP}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"expected one ModificationTime in {path}, got {count}")
    text = re.sub(r"e([+-])0+(\d+)", r"e\1\2", text)
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    iterations = root / "sources" / "tishte-serif" / "iterations"
    script = root / "scripts" / "develop_serif_v130.py"
    for style in ("Regular", "Bold", "Italic", "BoldItalic"):
        source = iterations / f"TishteSerif-{style}-v120.sfd"
        output = iterations / f"TishteSerif-{style}-v130.sfd"
        arguments = [str(path.relative_to(root)) for path in (script, source, output)]
        subprocess.run(
            [str(find_fontforge()), "-lang=py", "-script", *arguments, "0.130"],
            cwd=root,
            check=True,
        )
        normalize(output)
        print(output)


if __name__ == "__main__":
    main()
