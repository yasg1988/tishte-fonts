#!/usr/bin/env python3
"""Reject deprecated Russian spellings of the Meadow Mari language name."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


TEXT_SUFFIXES = {".html", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
SKIP_PARTS = {".git", "build", "dist"}
FORBIDDEN = re.compile("луго(?:во)?[-‑–—]?(?:" + "марий|марйи" + ")", re.IGNORECASE)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    violations: list[str] = []
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    for relative in sorted(filter(None, tracked)):
        path = root / relative
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if SKIP_PARTS.intersection(Path(relative).parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, 1):
            if FORBIDDEN.search(line):
                violations.append(f"{path.relative_to(root)}:{line_number}: {line.strip()}")
    if violations:
        raise SystemExit("Use ‘луговой марийский’ instead:\n" + "\n".join(violations))
    print("Russian terminology: ‘луговой марийский’ — OK")


if __name__ == "__main__":
    main()
