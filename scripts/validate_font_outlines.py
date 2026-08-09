#!/usr/bin/env python3
"""Run FontForge's outline validation for a generated font or SFD source."""

from __future__ import annotations

import argparse

import fontforge


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font")
    parser.add_argument("--allowed-mask", type=int, default=0)
    return parser.parse_args()


def main():
    args = parse_args()
    font = fontforge.open(args.font)
    result = font.validate()
    font.close()
    unexpected = result & ~args.allowed_mask
    print(f"validation_mask={result} allowed_mask={args.allowed_mask} unexpected_mask={unexpected}")
    return 0 if unexpected == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
