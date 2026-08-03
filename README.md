# PaperReading Skills

<p align="center">
  <em>A Claude Code skill suite that reads an arXiv paper or a GitHub repository and explains it the way a great advisor would — intuition first, then the math, then the code.</em>
</p>

<p align="center">
  <img alt="version" src="https://img.shields.io/badge/version-v1.0.0-blue">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="platform" src="https://img.shields.io/badge/platform-Claude%20Code-purple">
  <img alt="status" src="https://img.shields.io/badge/status-stable-brightgreen">
</p>

---

## What is this?

**PaperReading Skills** is a set of three Claude Code skills that turn *"read this paper and explain it to me"* into a single command. Point it at an arXiv link or a GitHub repository, and it fetches the paper, reads it in a focused way, and produces a structured, three-layer explanation — from a plain-language intuition of the problem, down to per-equation mathematical derivations and pseudocode of the reference implementation. Every explanation is rendered as a polished, LaTeX-ready HTML note you can keep and re-read.

It exists because **explaining a paper well is a repeatable craft, not a one-off.** The same ladder of understanding — *intuition → method → details* — applies whether the paper is about stereo vision, diffusion bridges, or rolling checksums. Encoding that ladder as a skill means you never have to re-explain *how* you want a paper explained. You just say `/read <url>`.

## The reading method: intuition → math → code

Every paper is explained in three escalating layers. The guiding principle is simple: **never drop the reader into equations before they know what the equations are *for*.**

### Layer 1 — The problem, in plain language
What problem does this paper solve? Why is it hard, why do prior approaches fall short, why does it matter? No math, no code. The bar: someone *outside* the field should grasp what's being attempted.

### Layer 2 — The method, intuitively
What did the authors actually do, stated without formulas? And the key question — *why does it work?* What insight did it capture? If there's a one-line "aha" (for example, rsync's *"slide the window instead of fixing block boundaries"*), it gets named explicitly here.

### Layer 3 — The details, with math and code
For each **core contribution** (not every section — the focus stays on the paper's real novelty):

1. **Intuition first** — what is this step doing, and why is it needed.
2. **Then the math** — the equations, with *every derivation step accompanied by a sentence on what it does and why*. A bare equation dump teaches nothing; walking the reader through "what this step means" does. Symbols are defined in plain language on first appearance.
3. **Then the code** — if the paper is open-sourced, the reference implementation is reduced to ~10–30 lines of annotated pseudocode, mapped back to the paper's steps. Where the code diverges from the paper (engineering shortcuts, tricks), it's called out.

## How notes are stored

Notes don't vanish into the chat. Every read produces a standalone HTML file in your configured library, opened automatically in your browser.

- **Output library** — set once with `/read-store <path>` (default: `D:/claude_paper_reading/`). Each paper becomes `<title>.html` and accumulates into a personal paper-notes collection.
- **Cache** — the fetched paper (arXiv HTML/PDF, fetched GitHub sources) lands in `<store>/_cache/`, so re-reading a paper doesn't refetch it.
- **Rendering** — HTML uses [MathJax](https://www.mathjax.org/) for LaTeX, with a clean light theme and color-coded callouts: <span style="color:#0b62c4">blue = intuition/scene</span>, <span style="color:#666">gray = meaning</span>, <span style="color:#b8791a">orange = conclusion</span>, <span style="color:#c0392b">red = caveat/uncertain</span>, <span style="color:#1a7f45">green = takeaway</green></span>.
- **Language** — switch the explanation language with `/read-language chinese|english` (default: Chinese). Both the chat summary and the HTML note follow this setting.

## The three commands

| Command | Purpose |
|---|---|
| `/read <arxiv-or-github-url>` | Read a paper and produce a three-layer explanation + HTML note. |
| `/read-store <path>` | Set where notes and the cache are saved (persists across sessions). |
| `/read-language <chinese\|english>` | Switch the explanation language (persists across sessions). |

`/read-store` and `/read-language` write a small JSON config (`~/.claude/paper_reading_config.json`) that `/read` consults on every run, so your preferences persist across sessions.

## Installation

These are standard Claude Code skills.

```bash
# 1. Clone the repo
git clone https://github.com/<your-github-username>/paper-reading-skills.git

# 2. Copy (or symlink) the skills into your Claude Code skills directory
cp -r paper-reading-skills/skills/* ~/.claude/skills/
#    On Windows (Git Bash), that's:  C:/Users/<you>/.claude/skills/

# 3. Start a new Claude Code session, then optionally set your note library:
#    /read-store D:/my/papers
```

**Requirements:**
- [Claude Code](https://claude.com/claude-code) (CLI / desktop / IDE extension).
- `curl` for fetching arXiv/GitHub (preinstalled on macOS/Linux; bundled with Git for Windows).
- Internet access to `arxiv.org` / `ar5iv.labs.arxiv.org` / `github.com`.

Then run:
```
/read https://arxiv.org/abs/2401.12345
```

## How it works under the hood

A few non-obvious design choices separate *"it ingested the PDF"* from *"it actually understood the paper"*:

- **arXiv HTML over PDF.** A paper's PDF renders math as glyphs; extracting text from it mangles subscripts, matrices, and Greek letters — which would destroy Layer 3. The skill prefers `arxiv.org/html/<id>` (and the `ar5iv` mirror), where equations are MathML and round-trip to clean LaTeX. PDF is the fallback, and the source of truth for figures.
- **Focused reading, not full-text ingestion.** A 30-page paper shoved wholesale into context is expensive and dilutes focus. The skill reads abstract + intro to frame the problem, jumps straight to the method section for Layer 3, then skims results — skipping the parts that don't serve understanding.
- **GitHub → paper resolution.** Given a repo, it reads the README, extracts the arXiv badge/link, and follows it to the paper. If the repo carries no paper link, it falls back to reading the code directly (clearly flagged as such).
- **Fetch, don't clone.** For open-sourced papers it pulls only the 1–3 core source files the README points at (model, training entry point, loss) — not the whole repo (which often carries multi-GB checkpoints). Pseudocode, not raw source, is what gets explained.
- **Honesty callouts.** Anything the paper leaves unclear, anywhere the code diverges from the formulas, and anything the skill infers rather than reads is flagged in a red callout — never silently passed off as certain.

## Project structure

```
paper-reading-skills/
├── README.md
├── LICENSE
└── skills/
    ├── read/                  # the main reading skill
    │   ├── SKILL.md
    │   └── assets/paper_template.html
    ├── read-store/            # set the note-library path
    │   └── SKILL.md
    └── read-language/         # switch explanation language
        └── SKILL.md
```

## Customizing the HTML

The note template lives at `skills/read/assets/paper_template.html`. It's a single self-contained file with all CSS and the MathJax config inline — swap the color palette, fonts, or callout styles there and every future note picks it up. Two placeholders are replaced at render time: `{{TITLE}}` (the `<h1>` and `<title>`) and `{{CONTENT}}` (the rendered explanation body).

## License

[MIT](./LICENSE) — read papers, keep notes, fork freely.
