#!/usr/bin/env python3
"""Run the current Fontspector Google Fonts profile on staged families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


FAMILIES = ("tishteserif", "tishtesans")
BLOCKING_LEVELS = ("ERROR", "FATAL", "FAIL")
NETWORK_RETRIES = 3


def warning_counts(data: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sections in data.get("results", {}).values():
        for checks in sections.values():
            if not isinstance(checks, list):
                continue
            for check in checks:
                for subresult in check.get("subresults", []):
                    if subresult.get("severity") != "WARN":
                        continue
                    key = f"{check['check_id']}:{subresult.get('code', '-')}"
                    counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def has_only_transient_namecheck_errors(data: dict) -> bool:
    blocking = []
    for sections in data.get("results", {}).values():
        for checks in sections.values():
            if not isinstance(checks, list):
                continue
            for check in checks:
                for subresult in check.get("subresults", []):
                    if subresult.get("severity") in BLOCKING_LEVELS:
                        blocking.append((check.get("check_id"), subresult.get("message", "")))
    return bool(blocking) and all(
        check_id == "fontdata_namecheck" and "network error" in message.lower()
        for check_id, message in blocking
    )


def audit(root: Path, executable: str, network: bool = False) -> dict:
    source_root = root / "build" / "googlefonts" / "ofl"
    report_root = root / "artifacts" / "reports" / "fontspector"
    report_root.mkdir(parents=True, exist_ok=True)
    accepted_path = root / "data" / "googlefonts-accepted-warnings.json"
    accepted = json.loads(accepted_path.read_text(encoding="utf-8"))
    result = {"tool": "Fontspector", "profile": "googlefonts", "families": {}, "passed": True}

    # Fontspector's Windows build may misread non-ASCII paths. Staging also
    # ensures that each family is audited together with its package metadata.
    with tempfile.TemporaryDirectory(prefix="tishte-fontspector-") as temporary:
        staging = Path(temporary)
        for family in FAMILIES:
            source = source_root / family
            if not source.exists():
                raise FileNotFoundError(f"Build package first: {source}")
            target = staging / family
            shutil.copytree(source, target)
            fonts = sorted(target.glob("*.ttf"))
            if not fonts:
                raise FileNotFoundError(f"No TTF files found in {source}")

            json_path = report_root / f"{family}.json"
            markdown_path = report_root / f"{family}.md"
            command = [
                executable,
                "--profile",
                "googlefonts",
                "--loglevel",
                "warn",
                "--succinct",
                "--json",
                str(json_path),
                "--ghmarkdown",
                str(markdown_path),
            ]
            if not network:
                command.append("--skip-network")
            command.extend(str(path) for path in fonts)
            for attempt in range(1, NETWORK_RETRIES + 1):
                completed = subprocess.run(command, cwd=staging, check=False)
                data = json.loads(json_path.read_text(encoding="utf-8"))
                if not has_only_transient_namecheck_errors(data) or attempt == NETWORK_RETRIES:
                    break
                print(f"{family}: transient namecheck network error; retry {attempt}/{NETWORK_RETRIES}")
                time.sleep(2)
            counts = {level: data.get("summary", {}).get(level, 0) for level in (
                "SKIP", "INFO", "PASS", "WARN", "FAIL", "FATAL", "ERROR"
            )}
            warnings = warning_counts(data)
            allowed = accepted[family]
            unexpected = {
                key: count for key, count in warnings.items()
                if key not in allowed or count > allowed[key]
            }
            passed = (
                completed.returncode == 0
                and not any(counts[level] for level in BLOCKING_LEVELS)
                and not unexpected
            )
            result["families"][family] = {
                "counts": counts,
                "warnings": warnings,
                "unexpected_warnings": unexpected,
                "passed": passed,
            }
            result["passed"] = result["passed"] and passed
            print(f"{family}: {counts}")
            if unexpected:
                print(f"{family}: unexpected warnings: {unexpected}")

    (report_root / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    if not result["passed"]:
        raise SystemExit(1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--fontspector", default=shutil.which("fontspector"))
    parser.add_argument(
        "--network", action="store_true",
        help="also run network checks; transient Fontdata errors are retried",
    )
    args = parser.parse_args()
    if not args.fontspector:
        raise SystemExit("fontspector executable was not found")
    audit(args.root.resolve(), args.fontspector, args.network)


if __name__ == "__main__":
    main()
