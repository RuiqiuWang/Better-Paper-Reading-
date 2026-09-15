#!/usr/bin/env bash
# Bash/Git Bash wrapper; defaults to both hosts.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT_DIR/install.py" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$SCRIPT_DIR/install.py" "$@"
else
  echo 'Python 3.8+ required. Run python install.py --target both.' >&2
  exit 1
fi
