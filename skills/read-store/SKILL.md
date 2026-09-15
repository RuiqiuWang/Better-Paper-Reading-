---
name: read-store
description: Set the paper note and cache directory. Use for /read-store or $read-store PATH. Preserve other host settings.
---

# read-store

Supports Claude Code `/read-store` and Codex `$read-store`.

1. Resolve sibling `../read-main/host_config.py`. Run it with `--host codex` in Codex or `--host claude` in Claude Code to read the effective configuration and its actual path. An installed host marker provides the default; explicit host takes precedence.
2. Parse the requested path; expand ~ and use an absolute path. If missing or invalid, report the current value and ask for a valid value without changing configuration.
3. Run the helper with `--host HOST --store VALUE`, quoting filesystem arguments safely. It preserves unknown fields and the other preferences. Changing the store clears the old dashboard URL, creates the new cache directory, and leaves existing notes in place. Do not claim to migrate notes.
4. Confirm the resulting note directory and its _cache directory.

Configuration: Codex uses `$CODEX_HOME/paper_reading_config.json` (default `~/.codex`); Claude Code uses `$CLAUDE_CONFIG_DIR/paper_reading_config.json` (default `~/.claude`). Never copy credentials or settings between hosts implicitly. Both hosts can share notes by explicitly choosing the same store directory.
