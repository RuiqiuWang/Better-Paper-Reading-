---
name: read-store
description: Set where the /read skill saves paper notes and its download cache. Use when the user types /read-store <path> to change the output directory for paper-reading notes. Persists the choice to a config file so /read uses it on every future run.
version: 1.0.0
---

# read-store · set the paper-note library location

Tells `/read` where to save HTML notes and cached paper files. Run once; it persists across sessions.

## When invoked

`/read-store <path>` — e.g. `/read-store D:/my/papers` or `/read-store ~/papers`.

## Steps

1. Take the path from args. If no path is given, read the config file (below) and tell the user the current `store_dir`, then ask for a path.
2. Normalize it: expand `~` to the home directory, use forward slashes. A Windows drive path like `D:/...` is fine.
3. Read the config file at `~/.claude/paper_reading_config.json` if it exists (JSON with keys `store_dir` and `language`). Preserve any existing `language` value.
4. Write the config back with `store_dir` set to the normalized path, keeping `language` intact. Use the Write tool.
5. Ensure the directory exists: `mkdir -p "<path>/_cache"`.
6. Confirm to the user, e.g.:
   - Chinese: "论文笔记将保存到 `<path>`，缓存在 `<path>/_cache`。"
   - English: "Paper notes will be saved to `<path>`, cache at `<path>/_cache`."
   (Reply in whichever language the user has been using.)

## Notes

- The default `store_dir` (before this is ever run) is `D:/claude_paper_reading`.
- This skill only writes config; it does not read any paper. `/read` consults this config at the start of every run.
- Config file path resolves `~` to the user home (e.g. `C:/Users/<you>/.claude/paper_reading_config.json` on Windows).
