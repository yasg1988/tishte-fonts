"""Shared release-version helpers."""

from __future__ import annotations

import re


VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.([0-9]{3})$")


def version_tag(version: str) -> str:
    """Convert 0.960 to v960 and 1.000 to v1000 without collisions."""
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise ValueError(f"version must use MAJOR.MINOR with three minor digits: {version!r}")
    major, minor = match.groups()
    return f"v{minor}" if major == "0" else f"v{major}{minor}"
