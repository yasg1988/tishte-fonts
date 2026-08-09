#!/usr/bin/env python3
"""Copy an SFD while updating its internal engineering version."""

from __future__ import annotations

import sys
import fontforge


if len(sys.argv) != 4:
    raise SystemExit("usage: stamp_sfd_version.py INPUT.sfd OUTPUT.sfd VERSION")

font = fontforge.open(sys.argv[1])
font.version = sys.argv[3]
font.sfntRevision = float(sys.argv[3])
font.save(sys.argv[2])
font.close()
