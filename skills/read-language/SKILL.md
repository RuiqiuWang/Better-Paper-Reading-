---
name: read-language
description: Switch the language the /read skill uses to explain papers. Use when the user types /read-language chinese or /read-language english. Persists the choice to a config file so /read uses it on every future run.
version: 1.0.0
---

# read-language · switch explanation language

Tells `/read` whether to explain papers in Chinese or English. Run once; it persists across sessions.

## When invoked

`/read-language <chinese|english>` — e.g. `/read-language english`.

## Steps

1. Take the language from args. Accept and normalize these aliases: `chinese`/`zh`/`中` → `chinese`; `english`/`en`/`英` → `english`. If missing or invalid, read the config (below), tell the user the current `language`, and list the valid options.
2. Read the config file at `~/.claude/paper_reading_config.json` if it exists (JSON with keys `store_dir` and `language`). Preserve any existing `store_dir` value.
3. Write the config back with `language` set to the normalized value, keeping `store_dir` intact. Use the Write tool.
4. Confirm to the user, e.g.:
   - After setting `chinese`: "论文讲解语言已切换为中文。"
   - After setting `english`: "Paper explanations will now be in English."
   (Reply in the newly selected language.)

## Notes

- The default `language` (before this is ever run) is `chinese`.
- `/read` reads this config at the start of every run and writes both the chat explanation and the HTML note in the chosen language.
- Config file path resolves `~` to the user home (e.g. `C:/Users/<you>/.claude/paper_reading_config.json` on Windows).
