#!/usr/bin/env python3
"""Fetch the pinned OFL Tinos binaries used only by the originality audit."""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import urlopen


COMMIT = "3b4482a99b80ea5fc75f187b1be3120a3f5905b3"
FILES = {
    "Tinos-Regular.ttf": "60a0e8ef0c04dd5dd69ffe91025fa2ae5836cbd35600a82ba031977557e2cb61",
    "Tinos-Bold.ttf": "393269dbab8899f938db19783eca5eac92eb431f7ae0ab45b8349ca895f1a06b",
    "Tinos-Italic.ttf": "5942266ed398b155d7dc23e36833e7ec6be988f2439bdbeb8ef1bede808eaa91",
    "Tinos-BoldItalic.ttf": "a5de79f0fe863ea0954757acb3d47b3ccd0a930ce3dd5b97230cd3866790a06e",
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / ".cache" / "upstream" / "tinos"
    destination.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES.items():
        path = destination / name
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == expected:
            print(f"{name}: cached")
            continue
        url = f"https://raw.githubusercontent.com/googlefonts/tinos/{COMMIT}/fonts/ttf/{name}"
        with urlopen(url, timeout=60) as response:
            data = response.read()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {name}: {actual}")
        path.write_bytes(data)
        print(f"{name}: downloaded and verified")


if __name__ == "__main__":
    main()
