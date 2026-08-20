#!/usr/bin/env python3
"""Replace personal Office/ODF metadata in generated Tishte sample files."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
import re
import tempfile
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo


CREATOR = "Tishte Project"
TITLE = "Tishte office font test"
FIXED_DATE = "2026-08-20T00:00:00Z"
def replace_element(xml_text: str, element: str, value: str, *, required: bool = True) -> str:
    pattern = rf"(<{re.escape(element)}(?:\s[^>]*)?>).*?(</{re.escape(element)}>)"
    updated, count = re.subn(pattern, rf"\g<1>{value}\g<2>", xml_text, flags=re.DOTALL)
    if required and count != 1:
        raise ValueError(f"Expected one {element} element, got {count}")
    return updated


def scrub_xml(name: str, data: bytes) -> bytes:
    xml_text = data.decode("utf-8")
    if name == "docProps/core.xml":
        xml_text = replace_element(xml_text, "dc:creator", CREATOR)
        xml_text = replace_element(xml_text, "cp:lastModifiedBy", CREATOR)
        xml_text = replace_element(xml_text, "dc:title", TITLE, required=False)
        xml_text = replace_element(xml_text, "dcterms:created", FIXED_DATE)
        xml_text = replace_element(xml_text, "dcterms:modified", FIXED_DATE)
    elif name == "meta.xml":
        xml_text = replace_element(xml_text, "meta:initial-creator", CREATOR)
        xml_text = replace_element(xml_text, "dc:creator", CREATOR)
        xml_text = replace_element(xml_text, "dc:title", TITLE)
        xml_text = replace_element(xml_text, "meta:creation-date", FIXED_DATE)
        xml_text = replace_element(xml_text, "dc:date", FIXED_DATE)
    return xml_text.encode("utf-8")


def scrub(path: Path) -> None:
    with ZipFile(path) as source:
        infos = source.infolist()
        payloads = {info.filename: source.read(info.filename) for info in infos}
    metadata_name = "meta.xml" if path.suffix.lower() == ".odt" else "docProps/core.xml"
    if metadata_name not in payloads:
        raise ValueError(f"{path}: missing {metadata_name}")
    payloads[metadata_name] = scrub_xml(metadata_name, payloads[metadata_name])

    with tempfile.NamedTemporaryFile(delete=False, dir=path.parent, suffix=path.suffix) as handle:
        temporary = Path(handle.name)
    try:
        by_name = {info.filename: info for info in infos}
        names = [info.filename for info in infos]
        if "mimetype" in names:
            names.remove("mimetype")
            names.insert(0, "mimetype")
        with ZipFile(temporary, "w") as target:
            for name in names:
                info = copy.copy(by_name[name])
                info.compress_type = ZIP_STORED if name == "mimetype" else ZIP_DEFLATED
                target.writestr(info, payloads[name])
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    targets = sorted(
        path for path in args.directory.iterdir()
        if path.suffix.lower() in {".docx", ".xlsx", ".pptx", ".odt"}
    )
    if len(targets) != 4:
        raise ValueError(f"Expected four office samples, got {targets}")
    for path in targets:
        scrub(path)
        print(f"scrubbed {path.name}")


if __name__ == "__main__":
    main()
