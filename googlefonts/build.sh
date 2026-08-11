#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python "$repo_root/scripts/fetch_sans_upstream.py"
python "$repo_root/scripts/build_googlefonts.py" --version 1.100
python "$repo_root/scripts/audit_googlefonts_reproducible.py" --version 1.100
python "$repo_root/scripts/audit_googlefonts.py"
