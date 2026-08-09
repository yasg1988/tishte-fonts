#!/usr/bin/env python3
"""Fetch pinned OFL Arimo variable fonts used as the Sans scaffold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "data" / "arimo-upstream.json").read_text(encoding="utf-8"))
    output = root / "sources" / "upstream" / "arimo"
    output.mkdir(parents=True, exist_ok=True)
    for item in manifest["files"]:
        path = output / item["name"]
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]:
            print(f"{item['name']}: cached")
            continue
        with urlopen(item["url"], timeout=60) as response:
            data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != item["bytes"] or digest != item["sha256"]:
            raise ValueError(f"upstream verification failed for {item['name']}")
        path.write_bytes(data)
        print(f"{item['name']}: fetched and verified")


if __name__ == "__main__":
    main()
