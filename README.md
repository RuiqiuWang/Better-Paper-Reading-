# PaperReading Skills

**Read papers, keep an organized HTML library, and resolve questions in context — in Codex or Claude Code.**

[简体中文](README.zh-CN.md) · [Changelog](CHANGELOG.md) · [MIT license](LICENSE)

## What is included

- **Paper explanations:** a technical overview, then an intuitive overview; key ideas explained through motivation, source-grounded reasoning and intuitive interpretation as needed.
- **Reading workspace:** persistent left sidebar with projects, pins, search, archives and reading history. Click a session to open its HTML. New drafts can be created inside projects.
- **Automatic delivery:** completing a reading opens its workspace session and returns clickable workspace and note links. If opening fails, the assistant reports it and supplies the links.
- **Rewrite follow-ups:** integrate an answer into the relevant passage while preserving context, formulas, sources and existing annotations.
- **Comment follow-ups:** underline a knowledge point and add a square numbered badge. Click to read the question and answer in the right sidebar. Switch between Global and numbered threads; continue related questions in the same thread.
- **Paper discovery:** search a topic, optionally constrain results to verified conference acceptances, expand around seed papers and collect paper/code links.

## Install

Requires **Python 3.8+** and a local Codex or Claude Code environment with file and shell access. The reading workspace and follow-up helpers use Python's standard library. `openreview-py` is optional and needed only for searches using the OpenReview helper. Internet access is needed to fetch papers and external assets such as MathJax.

```sh
git clone https://github.com/RuiqiuWang/Better-Paper-Reading-.git
cd Better-Paper-Reading-
python install.py --target both
```

Use `--target codex` or `--target claude` to install for one host. On systems where Python is named `python3`, use that executable instead.

```powershell
# Windows PowerShell alternative
.\install.ps1 -Target both
# Custom Python location: add -Python "C:/path/to/python.exe"
```

```sh
# macOS / Linux / Git Bash alternative
bash install.sh --target both
```

Preview without writing: `python install.py --target both --dry-run`.

| Host | Personal skill directory | Explicit invocation |
|---|---|---|
| Codex | `~/.agents/skills` for a new installation | `$read URL` |
| Claude Code | `~/.claude/skills` (honors `CLAUDE_CONFIG_DIR`) | `/read URL` |

The installer reuses an existing PaperReading installation under `~/.codex/skills` (or `CODEX_HOME/skills`) instead of creating duplicates. To choose another directory, use `--target codex --skills-dir PATH` or `--target claude --skills-dir PATH`. Existing skill folders are backed up under the destination parent's `paper-reading-backups/`. Installation does not copy or reset your reading settings, credentials or notes. Start a new task or reload the host if its skill menu has not refreshed.

Host conventions: [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills), [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

## Commands

Enter these in the assistant conversation, not a shell:

| Codex | Claude Code | Purpose |
|---|---|---|
| `$read URL` | `/read URL` | Explain a paper or paper-linked GitHub repository |
| `$read-main` | `/read-main` | Open and organize the reading workspace |
| `$read-search [venue] topic` | `/read-search [venue] topic` | Discover papers, optionally at a specific conference |
| `$read-rewrite question` | `/read-rewrite question` | Rewrite the relevant explanation in the original HTML |
| `$read-comment question` | `/read-comment question` | Add or continue an inline/global question thread |
| `$read-store PATH` | `/read-store PATH` | Set the note and cache directory |
| `$read-language english` | `/read-language english` | Choose `english` or `chinese` |

The follow-up instructions also recognize `/read_rewrite` and `/read_comment` as natural-language requests. Native skill menus use the hyphenated names above.

### First reading

1. Set your library with `$read-store ~/PaperReading` or `/read-store ~/PaperReading`.
2. Run `$read https://arxiv.org/abs/2409.07447` or the Claude `/read` equivalent.
3. The assistant saves the note, registers a session and opens that paper in the workspace. Use the sidebar to revisit it, pin it or move it to a project.
4. Ask a follow-up in the same task. Add `--session ID` when you need to specify a different saved paper.

### Follow-up examples

```text
# Codex
$read-rewrite Why does this step need that assumption?
$read-comment How should I interpret this equation?
$read-comment --comment 1 Can you give a concrete example?
$read-comment --comment global How do these components fit together?

# Claude Code
/read-rewrite Why does this step need that assumption?
/read-comment --comment 1 Can you give a concrete example?
```

A rewrite edits the relevant passage in place. A comment preserves the passage, adds an underline and badge, and stores the question/answer in the right sidebar. Global holds questions about the whole paper; it is separate from the numbered threads. Answers inherit the same reading style as the main explanation.

The right sidebar offers a Codex/Claude Code command selector. Its input copies a continuation command; **send that command in the assistant to generate the answer**. The HTML does not call a model itself. Follow-ups update the original session, keep earlier questions, and back up the previous HTML before editing. A stale file hash or ambiguous anchor stops the edit for reinspection.

## Reading style

Start with the whole paper: explain the task, bottleneck and proposed method in professional technical terms, then describe the same mechanism intuitively. Dive into important parts as useful:

1. What is this part trying to solve, and what is the approach?
2. What does the original paper actually define, derive, prove or implement? Explain assumptions and reasoning with source locations.
3. After the formal details, what did this step really accomplish, and how should we understand it?

Adapt the depth to the material. Do not force three sections, proofs, analogies or code into every explanation. Distinguish the authors' claims, proofs, experimental support, supplementary derivations and intuitive examples. Finally reconnect the components to the original problem. Full guidance: [reading-style.md](skills/read/references/reading-style.md).

## Storage and configuration

| Setting | Codex | Claude Code |
|---|---|---|
| Reading config | `$CODEX_HOME/paper_reading_config.json`, default `~/.codex/` | `$CLAUDE_CONFIG_DIR/paper_reading_config.json`, default `~/.claude/` |
| OpenReview credentials | `openreview_credentials.json` in the same config directory | `openreview_credentials.json` in the same config directory |

Existing `store_dir` is always preserved. For a new configuration, the default is `D:/claude_paper_reading` on Windows with a D: drive; otherwise `~/PaperReading`. Default explanation language is Chinese. Both hosts can use the same note library by explicitly selecting the same directory; configuration and credentials remain separate.

- Notes: `<title>--<session-id>.html`; paper/source cache: `_cache/`.
- Searches: `_search/`; generated-note metadata: `_index.json`.
- Workspace: `index.html`, refreshed by the registration helpers. Legacy root HTML and `_search/` / `_topic/` outputs can be imported. The optional `read-search-topic` skill is not bundled, but its `search_topic` entries are supported.
- Follow-up backups: `.reading-history/`. Annotations and answers are embedded in the note HTML.
- Projects, pins, renamed titles, archive flags and drafts: browser localStorage, scoped to library and browser origin/profile. Export/import organization through the bottom-left library dialog when changing browsers or origins. That backup does not include the note files.
- Optional `dashboard_url`: a verified loopback HTTP address. The included `serve_library.py` supports in-app browsers that cannot open local files. It binds only to 127.0.0.1 and does not expose configuration files or hidden backups. Keep the process running while using its links.

OpenReview credentials are optional. If needed, set `OPENREVIEW_USERNAME` and `OPENREVIEW_PASSWORD` locally and run the installed `read-search/save_credentials.py --host codex` (or `--host claude`). Never paste passwords into a repository or generated notes. Access failures must be reported; preprints must not be presented as accepted conference papers.

## Repository layout

```text
install.py / install.sh / install.ps1   # shared installer and shell entry points
skills/
  read/                                # explanation style, figures, HTML template
  read-main/                           # dashboard, server, registration, config, follow-ups
  read-comment/                        # numbered and global questions
  read-rewrite/                        # contextual passage edits
  read-search/                         # discovery and OpenReview helpers
  read-store/                          # output directory preference
  read-language/                       # explanation language preference
tests/                                 # persistence, annotations and host installation checks
```

## Validation

```sh
python -m unittest discover -s tests -v
node --check skills/read-main/assets/dashboard.js
node --check skills/read-main/assets/comments.js
```

The HTML interactions have been manually checked in the Codex in-app browser. Automated tests cover shared helpers and both installation targets; this does not substitute for an end-to-end model run in every Claude Code or Codex version.
