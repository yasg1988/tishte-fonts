#!/usr/bin/env python3
"""Apply shared Tishte reading-shape traits to non-Regular Serif styles."""

from __future__ import annotations

import json
import sys

import fontforge


def edit_layer(glyph, editor) -> None:
    width = glyph.width
    layer = glyph.foreground
    editor(layer)
    glyph.setLayer(layer, glyph.activeLayer)
    glyph.width = width
    glyph.ttinstrs = b""


def broaden_round(glyph) -> None:
    x_min, _y_min, x_max, _y_max = glyph.boundingBox()
    center = (x_min + x_max) / 2

    def editor(layer):
        for contour in layer:
            for point in contour:
                point.x = center + (point.x - center) * 1.025

    edit_layer(glyph, editor)


def shape_c(glyph) -> None:
    def editor(layer):
        contour = layer[0]
        # Open the aperture and give the upper/lower terminals opposite
        # directions, matching the Regular reading rhythm.
        x_min, y_min, x_max, y_max = glyph.boundingBox()
        x_gate = x_min + (x_max - x_min) * 0.78
        lower_gate = y_min + (y_max - y_min) * 0.23
        upper_gate = y_min + (y_max - y_min) * 0.62
        for point in contour:
            if point.x < x_gate:
                continue
            if point.y < lower_gate:
                point.x += 14
            elif point.y > upper_gate:
                point.x -= 12

    edit_layer(glyph, editor)


def shape_e(glyph) -> None:
    def editor(layer):
        if len(layer) != 2:
            raise ValueError("unexpected e topology")
        # A restrained rising crossbar improves differentiation from c.
        if len(layer[0]) == 28 and len(layer[1]) == 11:
            layer[0][6].y -= 10
            layer[0][5].y += 10
            layer[1][4].y -= 10
            layer[1][5].y += 10
        elif len(layer[1]) == 14:
            layer[1][0].y -= 8
            layer[1][2].y += 8
            layer[1][3].y += 8
        elif len(layer[1]) == 12:
            layer[1][0].y -= 8
            layer[1][2].y += 8
            layer[1][3].y += 8
        else:
            raise ValueError("unexpected e topology")

    edit_layer(glyph, editor)


def calm_n(glyph) -> None:
    def editor(layer):
        contour = layer[0]
        x_min, _y_min, x_max, y_max = glyph.boundingBox()
        span = x_max - x_min
        for point in contour:
            relative_x = (point.x - x_min) / span
            if point.y > y_max * 0.98 and relative_x > 0.45:
                point.y -= 10
            elif y_max * 0.80 < point.y < y_max * 0.93 and 0.35 < relative_x < 0.75:
                point.y -= 7

    edit_layer(glyph, editor)


def rise_cyrillic_en_bar(glyph) -> None:
    def editor(layer):
        contour = layer[0]
        x_min, _y_min, x_max, _y_max = glyph.boundingBox()
        center = (x_min + x_max) / 2
        candidates = [point for point in contour if point.x > center and 350 < point.y < 600]
        if len(candidates) != 2:
            raise ValueError(f"unexpected Cyrillic en crossbar: {len(candidates)} points")
        for point in candidates:
            point.y += 10

    edit_layer(glyph, editor)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: apply_family_signature_v070.py INPUT.sfd OUTPUT.sfd")
    source, output = sys.argv[1:]
    font = fontforge.open(source)
    if font.fontname.endswith("-Regular"):
        raise SystemExit("Regular already carries the v0.040 Tishte signature")
    operations = {
        "o": broaden_round,
        "c": shape_c,
        "e": shape_e,
        "n": calm_n,
        "uni043D": rise_cyrillic_en_bar,
    }
    changed = []
    for name, operation in operations.items():
        operation(font[name])
        changed.append(name)
    font.version = "0.070"
    font.sfntRevision = 0.070
    font.save(output)
    font.close()
    print(json.dumps({"source": source, "output": output, "changed": changed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
