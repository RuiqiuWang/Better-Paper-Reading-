# PaperReading Skills

<p align="center">
  <em>A Claude Code skill suite that reads an arXiv paper or GitHub repository the way a great advisor would — intuition first, then the math, then the code — and surveys a research area to surface every paper worth reading.</em>
</p>

<p align="center">
  <img alt="version" src="https://img.shields.io/badge/version-v2.0.0-blue">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="platform" src="https://img.shields.io/badge/platform-Claude%20Code-purple">
  <img alt="status" src="https://img.shields.io/badge/status-stable-brightgreen">
  <a href="./README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/README-中文-red"></a>
</p>

<p align="center">
  <sub><a href="./README.md">English</a> &nbsp;|&nbsp; <b>中文</b> &nbsp;|&nbsp; <a href="./README.zh-CN.md">简体中文</a></sub>
</p>

---

## What is this?

**PaperReading Skills** is a set of four Claude Code skills that turn *"read this paper and explain it to me"* and *"find me the papers in this area"* into single commands. Point it at an arXiv link or a GitHub repository, and it fetches the paper, reads it in a focused way, and produces a structured, three-layer explanation — from a plain-language intuition of the problem, down to per-equation mathematical derivations and pseudocode of the reference implementation. Every explanation is rendered as a polished, LaTeX-ready HTML note you can keep and re-read. Point it at a research topic instead, and it runs a multi-source sweep to list every relevant paper with arXiv links, code, and one-line summaries.

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

## The four commands

| Command | Purpose |
|---|---|
| `/read <arxiv-or-github-url>` | Read a paper and produce a three-layer explanation + HTML note. |
| `/read-search [conference] <topic>` | Discover papers on a topic — comprehensively — optionally scoped to a top-tier venue. |
| `/read-store <path>` | Set where notes and the cache are saved (persists across sessions). |
| `/read-language <chinese\|english>` | Switch the explanation language (persists across sessions). |

`/read-store` and `/read-language` write a small JSON config (`~/.claude/paper_reading_config.json`) that `/read` and `/read-search` consult on every run, so your preferences persist across sessions.

## Discovering papers with /read-search

`/read` reads one paper. `/read-search` finds the papers worth reading — comprehensively. Give it a topic, optionally scoped to a top-tier venue, and it runs an independent, multi-angle sweep so you don't end up with two hits and a false sense of coverage.

```text
/read-search self-evolution like AlphaEvolve
/read-search cvpr2027 stereo video generation
/read-search 2D-to-3D video conversion like StereoCrafter
```

The conference part is **optional** and restricted to the venues that matter (CCF-A plus top-tier B like ECCV/EMNLP): `neurips`, `icml`, `iclr`, `aaai`, `ijcai`, `cvpr`, `iccv`, `eccv`, `acl`, `emnlp`, `naacl`, `siggraph`, … with or without a year. If the first token isn't a recognized venue, the whole input is treated as the topic.

The point is breadth. For *"2D-to-3D like StereoCrafter"* the expectation is the seed **and** its neighborhood — StereoPilot, M2SVID, StereoWorld, Elastic3D, Deep3D — not just StereoCrafter twice. So the skill:

- **Routes by venue family** — this is the key to the hard filter:
  - **OpenReview venues (ICLR / NeurIPS / ICML)**: logs in via the official `openreview-py` SDK to bypass OpenReview's Cloudflare JS challenge (anonymous curl/requests all get `403 ChallengeRequired`, regardless of IP or VPN). Credentials are stored locally at `~/.claude/openreview_credentials.json` and prompted for once on first use. It then queries `content.venueid=<venue>.cc/<year>/Conference` to fetch the **verified accepted list**, with each paper's acceptance tier (`Oral`/`Spotlight`/`Poster`/`regular`) read straight from the `content.venue` field.
  - **CVF venues (CVPR / ICCV / WACV / ECCV)**: scrapes `openaccess.thecvf.com` directly (no Cloudflare).
  - **ACL / AAAI / SIGGRAPH / ACM**: fetches the proceedings pages.
- **arXiv over plain HTTPS** — `https://export.arxiv.org/api/query` is directly reachable from mainland China (no proxy needed); queries are built with `+AND+` joins or quoted phrases to avoid the loose-OR false positives a bare space-separated query produces.
- **Parses seeds** — named anchor papers (AlphaEvolve, StereoCrafter) *and* the conceptual task (self-evolution, 2D-to-3D) — then searches around both.
- **Sweeps multiple sources in parallel** — arXiv API, Semantic Scholar, Papers With Code, and DBLP (all free, no keys), plus 4–8 web searches with synonym variants.
- **Snowballs the citation graph** — for the top seeds it pulls both their *references* (predecessors) and *citations* (successors) via Semantic Scholar. This is the step that surfaces the neighbors a flat keyword search misses.
- **Finds real code repos** — for each hit (especially seeds) it scrapes the arXiv HTML full text for GitHub/project links, then cross-checks with GitHub reverse search; repos are never invented, and the field is omitted when none is found.
- **Dedups and curates** — by arXiv id then fuzzy title, then groups into Anchor / Related / Recent-SOTA / Foundational.

The result is a **list** (not a table) in chat — each item is a one-line intuition plus `arXiv`/`forum`/`code`/`page` links (lines omitted when absent) — and a dated digest saved to `<store>/_search/` alongside your reading notes. Same honesty rules as `/read`: never invent a paper, arXiv id, or repo; tag snippet-only matches; if a venue's accepted list is genuinely unobtainable (and the user won't provide OpenReview credentials), say so and offer the no-venue preprint search instead — never substitute preprints for accepted papers.

## Installation

These are standard Claude Code skills.

```bash
# 1. Clone the repo
git clone https://github.com/RuiqiuWang/Better-Paper-Reading-.git

# 2. Copy (or symlink) the skills into your Claude Code skills directory
cp -r paper-reading-skills/skills/* ~/.claude/skills/
#    On Windows (Git Bash), that's:  C:/Users/<you>/.claude/skills/

# 3. Start a new Claude Code session, then optionally set your note library:
#    /read-store D:/my/papers
```

**Requirements:**
- [Claude Code](https://claude.com/claude-code) (CLI / desktop / IDE extension).
- `curl` for fetching arXiv/GitHub (preinstalled on macOS/Linux; bundled with Git for Windows).
- Python 3.8+ with `openreview-py` (for `/read-search` on OpenReview venues — ICLR/NeurIPS/ICML). Install: `pip install openreview-py` (in China: `-i https://pypi.tuna.tsinghua.edu.cn/simple`). On first use of an OpenReview venue, you'll be prompted for your openreview.net credentials (free to register); they're stored locally at `~/.claude/openreview_credentials.json`.
- Internet access to `arxiv.org` / `github.com` / `openreview.net`.

Then run:
```
/read https://arxiv.org/abs/2401.12345
/read-search self-evolution like AlphaEvolve
/read-search icml2026 stereo video generation
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
├── README.zh-CN.md            # 中文版 README
├── LICENSE
├── install.sh                 # copies the skills into ~/.claude/skills/
└── skills/
    ├── read/                  # the main reading skill
    │   ├── SKILL.md
    │   └── assets/paper_template.html
    ├── read-store/            # set the note-library path
    │   └── SKILL.md
    ├── read-language/         # switch explanation language
    │   └── SKILL.md
    └── read-search/           # discover papers on a topic
        ├── SKILL.md
        ├── openreview_fetch.py    # login + fetch OpenReview accepted lists
        └── save_credentials.py    # store OpenReview credentials locally
```

## Customizing the HTML

The note template lives at `skills/read/assets/paper_template.html`. It's a single self-contained file with all CSS and the MathJax config inline — swap the color palette, fonts, or callout styles there and every future note picks it up. Two placeholders are replaced at render time: `{{TITLE}}` (the `<h1>` and `<title>`) and `{{CONTENT}}` (the rendered explanation body).

## License

[MIT](./LICENSE) — read papers, keep notes, fork freely.
