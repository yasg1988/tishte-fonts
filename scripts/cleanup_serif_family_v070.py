#!/usr/bin/env python3
"""Clean affected Tishte Serif outlines while preserving advance widths."""

from __future__ import annotations

import json
import sys

import fontforge


SELF_INTERSECTION = 0x04
MISSING_EXTREMA = 0x20

# Zero-area two-unit hooks inherited from the Regular scaffold. They are
# invisible at document sizes but FontForge correctly reports them as contour
# self-intersections. Indices are deleted from right to left per contour.
REGULAR_HOOK_POINTS = {
    "A": {0: ((9, 1464, 55),)},
    "M": {0: ((20, 1761, 55),)},
    "R": {0: ((21, 1363, 55),)},
    "uni0416": {0: ((30, 1835, 55), (16, 689, 1290), (3, 0, 55))},
    "uni042F": {0: ((2, 8, 55),)},
}

# Two obscure Latin Extended-E glyphs in the Bold upstream source contain
# malformed quadratic splines that FontForge cannot boolean-clean. They are
# outside Tishte's declared document charset and are intentionally omitted.
UNSUPPORTED_MALFORMED_GLYPHS = {"uniAB48", "uniAB54"}


def prune_known_hooks(glyph) -> bool:
    targets = REGULAR_HOOK_POINTS.get(glyph.glyphname)
    if not targets:
        return False
    width = glyph.width
    layer = glyph.foreground
    for contour_index, points in targets.items():
        for point_index, expected_x, expected_y in points:
            point = layer[contour_index][point_index]
            if (point.x, point.y) != (expected_x, expected_y):
                return False
    for contour_index, points in targets.items():
        for point_index, _expected_x, _expected_y in sorted(points, reverse=True):
            del layer[contour_index][point_index]
    glyph.setLayer(layer, glyph.activeLayer)
    glyph.width = width
    glyph.ttinstrs = b""
    return True


def clean_glyph(glyph) -> dict | None:
    before = glyph.validate(True)
    pruned = prune_known_hooks(glyph) if before & SELF_INTERSECTION else False
    if pruned:
        before_cleanup = glyph.validate(True)
        if not before_cleanup & (SELF_INTERSECTION | MISSING_EXTREMA):
            return {
                "glyph": glyph.glyphname,
                "unicode": glyph.unicode,
                "before": before,
                "after": before_cleanup,
            }
    targeted = before & (SELF_INTERSECTION | MISSING_EXTREMA)
    if not targeted:
        return None

    width = glyph.width
    if targeted & SELF_INTERSECTION:
        if glyph.references:
            # Composite accents such as cedilla and ogonek intentionally touch
            # the base. Decompose them before boolean union so the exported
            # glyph contains one valid filled outline.
            glyph.unlinkRef()
        # Imported TrueType outlines can contain zero-area hooks and nearly
        # collinear fragments inside a single contour. Simplify those before
        # boolean overlap removal; removeOverlap alone only resolves contour
        # against contour intersections.
        glyph.simplify(1, ("mergelines",))
        glyph.removeOverlap()
        glyph.correctDirection()
    if glyph.validate(True) & MISSING_EXTREMA:
        glyph.addExtrema("only_good_rm")
        if glyph.validate(True) & MISSING_EXTREMA:
            glyph.addExtrema("all")
    glyph.width = width
    glyph.ttinstrs = b""
    after = glyph.validate(True)
    if after & (SELF_INTERSECTION | MISSING_EXTREMA) and glyph.glyphname in UNSUPPORTED_MALFORMED_GLYPHS:
        glyph.clear()
        glyph.width = width
        after = glyph.validate(True)
    return {
        "glyph": glyph.glyphname,
        "unicode": glyph.unicode,
        "before": before,
        "after": after,
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: cleanup_serif_family_v070.py INPUT.sfd OUTPUT.sfd")
    source, output = sys.argv[1:]
    font = fontforge.open(source)
    changes = []
    for glyph in font.glyphs():
        if glyph.isWorthOutputting():
            # Contour edits invalidate upstream TrueType bytecode. Use one
            # consistent unhinted engineering build instead of mixing stale
            # and cleared instructions across related glyphs.
            glyph.ttinstrs = b""
            result = clean_glyph(glyph)
            if result is not None:
                changes.append(result)
    font.version = "0.070"
    font.sfntRevision = 0.070
    font.save(output)
    remaining = [item for item in changes if item["after"] & (SELF_INTERSECTION | MISSING_EXTREMA)]
    result = {
        "source": source,
        "output": output,
        "changed_glyphs": len(changes),
        "remaining_targeted_issues": len(remaining),
        "remaining": remaining,
    }
    font.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if remaining:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
