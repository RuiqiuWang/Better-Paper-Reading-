#!/usr/bin/env bash
# Install PaperReading Skills into ~/.claude/skills/
# Works in git bash (Windows), macOS, and Linux.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.claude/skills"
mkdir -p "$SKILLS_DIR"

for skill in read read-store read-language read-search; do
  if [ -d "${SCRIPT_DIR}/skills/${skill}" ]; then
    cp -r "${SCRIPT_DIR}/skills/${skill}" "${SKILLS_DIR}/"
    echo "  installed: ${skill}"
  else
    echo "  MISSING:   skills/${skill} (skipped)" >&2
  fi
done

cat <<EOF

Done. Skills copied to: ${SKILLS_DIR}

Restart Claude Code (or start a new session) so the skills are picked up, then try:

  /read https://arxiv.org/abs/2409.07447
  /read-search self-evolution like AlphaEvolve

Optional setup:
  /read-store <path>            # set where notes are saved (default D:/claude_paper_reading)
  /read-language <chinese|english>

EOF
