---
name: read-main
description: Open and refresh the PaperReading HTML workspace with a persistent left sidebar for reading sessions, projects, pins, search and archives. Use for /read-main (Claude Code), $read-main (Codex), or requests to browse and organize saved paper notes. Supports existing read, search and search_topic index entries.
---

# PaperReading · 阅读工作台

Read the host's shared `paper_reading_config.json`: `~/.claude/` for Claude Code or `~/.codex/` for Codex. Use its `store_dir`, default as resolved by `host_config.py`. Do not change the store or host configuration when opening the workspace.

Build and open it with Python 3.8+ (no third-party packages):

```text
python "<this-skill-dir>/build_dashboard.py" "<STORE>" --open
```

The command imports existing root-level HTML notes and outputs under `_search/` and `_topic/`. It excludes `_cache/`, preserves existing index IDs, and stops without resetting a malformed `_index.json`. Missing files remain visible with a recovery message. Markdown gets an escaped local HTML view, avoiding browser restrictions on fetching local files.

## Workspace behavior

- A fixed left sidebar remains visible while the selected HTML loads on the right. Session URLs use `index.html#session=<id>`; browser back/forward and independent opening work.
- Session creation is available inside each project's menu. Choose reading/search, enter a URL/topic, and create a draft belonging to that project. Copy the displayed command into the host assistant. The page does not itself invoke a model or start an app task. There is no global session-creation button, form or shortcut; ordinary `/read` commands automatically create their result sessions.
- Project: create, rename, collapse or remove a project. Move sessions via their menu or drag them onto a project. Removing a project leaves notes and sessions intact.
- Sessions: pin/unpin, rename, search, archive and restore. Pinned sessions also appear in their project for context.
- Output registration refreshes the data feed; an open visible workspace picks it up within about five seconds. A generated entry with the draft's ID replaces the draft, retaining its project and pin.
- After `/read` finishes, its default completion step opens `index.html#session=<this-session-id>` so the new paper is the initial content. A manual `/read-main` visit can resume the previously selected note or show the library's recent readings.
- The shell is static and has no CDN or server dependency. Nested notes retain their existing dependencies, such as MathJax.

## Storage boundaries

`_index.json` stores generated-note metadata. Browser localStorage stores projects, session names, pins, archive flags and drafts, scoped to the library path and browser origin/profile. Rebuilding the HTML does not clear these settings. They do not automatically sync across browsers, file/HTTP origins or computers.

The “本地阅读库” dialog exports/imports a JSON backup and selects `/read` or `$read` command spelling. Explain that backup contains organization and draft commands, not the note files. If browser storage is unavailable, the page shows a message and still allows export.

## Connecting other output skills

For /read, /read-search, or another skill that generates a reading HTML/Markdown output, follow [references/session-registration.md](references/session-registration.md). `append_index.py` retains the positional CLI used by earlier read-main installations, including `search_topic` and the optional topic count. Do not replace this helper with hand-written JSON editing.

## Delivering an open page

For Codex browser delivery follow the final section of `references/session-registration.md`: verify the selected paper, keep the deliverable tab and its loopback service open, and start the final answer with both clickable links. `serve_library.py` provides an optional loopback-only reader for in-app browsers; no server is required for ordinary file-based use.

## Host configuration

Before resolving the note library, run the installed sibling read-main `host_config.py --host codex` in Codex or `--host claude` in Claude Code. Its output is authoritative for the config path, store and language: it honors CODEX_HOME / CLAUDE_CONFIG_DIR and existing preferences. Without a configured store, use D:/claude_paper_reading only on Windows with a D: drive; otherwise use ~/PaperReading. Resolve scripts from the actual skill location, never a hardcoded ~/.claude/skills path. Use the host's available file/shell/browser tools; when no browser tool exists, use build_dashboard.py --open and report the printed links without claiming visual verification.
