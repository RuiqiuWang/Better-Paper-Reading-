---
name: read-search
description: Discover academic papers on a topic — comprehensively — optionally scoped to a top-tier conference. Use when the user types /read-search [conference] [topic], e.g. /read-search icml2026 stereo video generation, or /read-search self-evolution like AlphaEvolve. The conference part is optional and, when given, is a HARD filter — only papers actually accepted at that venue count. For OpenReview-hosted venues (ICLR/NeurIPS/ICML) it logs in via openreview-py (credentials stored locally, prompted once) to bypass Cloudflare and fetch the verified accepted list; for CVF venues (CVPR/ICCV/WACV/ECCV) it scrapes openaccess.thecvf.com; arXiv is queried over plain HTTPS (direct, no proxy needed in CN). Runs citation/reference snowballing around seed papers and finds each paper's code repo via arXiv HTML scraping + GitHub reverse search. Returns a list (not a table) of one-line intuitions + paper/code/project links; saves a markdown digest. Trigger whenever the user wants to find/survey/list papers in an area.
version: 2.0.0
---

# read-search · comprehensive paper discovery

Find papers on a research topic — comprehensively — optionally scoped to a top-tier venue. Two inviolable rules:

1. **If a conference is given, it is a HARD filter.** "ICML 2026" means *only papers actually accepted at ICML 2026* — not arXiv preprints. If the accepted list is unobtainable, say so and stop; do **not** pad with preprints.
2. **Code repos are real, not invented.** Found via arXiv HTML scraping + GitHub reverse search; if none found, omit the field.

## When invoked

`/read-search [conference] <topic>`

- `conference` is **optional**. If the first token(s) match a recognized venue (with/without year), it's the filter; else the whole input is the topic.
- Examples: `/read-search icml2026 self-evolution like AlphaEvolve`; `/read-search 2D-to-3D video conversion` (no venue); `/read-search cvpr2027 stereo video generation`.

## Config

Read `~/.claude/paper_reading_config.json` (shared with `/read`) for `store_dir` (default `D:/claude_paper_reading`) and `language` (default `chinese`). Save digests to `<store_dir>/_search/`; cache to `<store_dir>/_cache/search_<slug>/`. Output in the configured language.

## Step 0 · Parse args + venue routing

1. Match first token(s) against venues. **Recognized**: `neurips`/`nips`, `icml`, `iclr`, `aaai`, `ijcai`, `cvpr`, `iccv`, `eccv`, `wacv`, `acl`, `emnlp`, `naacl`, `coling`, `siggraph`, `siggraph-asia`, `kdd`, `sigir`, `www`. Accept `icml` or `icml2026` or `icml 2026`.
2. If matched → `conference={venue,year?}`, topic=rest. Else `conference=null`, topic=all.
3. From the topic extract **seeds** (named anchor papers like "AlphaEvolve"/"StereoCrafter" → drive citation snowballing) and the **conceptual task** (e.g. "LLM self-evolution" → drive keyword sweeps).
4. **Route by venue family** — this determines Step 1:
   - **OpenReview-hosted**: ICLR, NeurIPS, ICML → Step 1A (`openreview-py` login).
   - **CVF-hosted**: CVPR, ICCV, WACV, ECCV → Step 1B (scrape CVF).
   - **ACL/EMNLP/NAACL/COLING** → ACL Anthology (`aclanthology.org/events/<venue>-<year>/`).
   - **AAAI** → `ojs.aaai.org`; **SIGGRAPH/EG** → DLib; **KDD/SIGIR/WWW** → ACM DL (use WebFetch).
   - **No venue** → skip Step 1, go straight to Step 2 (arXiv + snowball).

## Step 1 · Get the accepted-paper list (HARD FILTER — only if a venue is given)

### Step 1A · OpenReview venues (ICLR / NeurIPS / ICML) — `openreview-py` login

**Why login**: OpenReview's API (`api2.openreview.net`) is behind Cloudflare JS challenge. Anonymous curl/requests/scrapy all get `403 ChallengeRequired` — verified regardless of IP, headers, or VPN proxy. The **only** reliable bypass is authenticated access via `openreview-py` (the official SDK), which uses a login session that Cloudflare lets through.

**Credentials** — stored in `~/.claude/openreview_credentials.json`:
```json
{"username": "your@email", "password": "yourpassword"}
```
- If the file exists and has both fields → use it.
- If missing/empty → **stop and prompt the user**: "首次使用:请提供 OpenReview 账号(邮箱)和密码,用于登录拉取录用列表。凭据会存到 `~/.claude/openreview_credentials.json`。如无账号去 openreview.net 免费注册。" Collect username + password, write the file (chmod 600 if possible), then proceed. **Never echo the password back.**
- The helper script `openreview_fetch.py` (in this skill's directory) reads this file, OR accepts `OPENREVIEW_USERNAME`/`OPENREVIEW_PASSWORD` env vars. Call it:
```bash
python <skill_dir>/openreview_fetch.py <venue> <year> [--proxy http://127.0.0.1:7890]
```
  It prints `SUMMARY: <venue><year> total=N by_venue={...}` and `FILE: <path>` to stdout. `--proxy` is optional (use only if direct fails; a local VPN like 7890 can help with TLS, though login itself bypasses Cloudflare).
- Requires `openreview-py`: install once (`pip install openreview-py`, or `-i https://pypi.tuna.tsinghua.edu.cn/simple` in CN). If missing, install it.

**What it fetches**: `content={'venueid': '<venue>.cc/<year>/Conference'}` → all papers whose venue has been set to that conference = **the accepted list**. The `content.venue` field (e.g. `"ICML 2026 spotlight"`, `"ICML 2026 regular"`, `"ICLR 2026 Oral"`) gives the acceptance tier. (Note: ICML has only spotlight + regular; ICLR/NeurIPS have oral/spotlight/poster.)

**Fallback if login/auth fails**: if `openreview-py` is unavailable AND the user won't provide credentials, you **cannot** get the ICLR/NeurIPS/ICML accepted list — tell the user plainly and offer the no-venue preprint search instead. Do not substitute preprints for accepted papers.

### Step 1B · CVF venues (CVPR / ICCV / WACV / ECCV)

CVF Open Access is **not** behind Cloudflare — scrape directly:
```bash
curl -sL "https://openaccess.thecvf.com/search?q=<q>" # then extract titles + PDF links
```
For a full accepted list by year, hit `https://openaccess.thecvf.com/CVPR2024?day=all` etc. ECCV uses `https://www.ecva.net/papers.php`. These carry acceptance status implicitly (everything listed is accepted); oral/spotlight are marked on the paper page.

### Step 1C · Other venues (ACL/AAAI/SIGGRAPH/ACM)

Use the WebFetch tool or curl+browser-UA on the proceedings pages listed in Step 0. These are mostly not behind Cloudflare.

### Hard-filter rule

A paper counts for `<venue> <year>` ONLY if it's in the accepted list from Step 1. An arXiv preprint mentioning "we target ICML 2026" does **not** count. If Step 1 fails entirely and the venue isn't obtainable → stop, tell the user, offer the no-venue search. Today's date (from context) tells you whether the venue has convened/released (ICML≈Jul, ICLR≈Apr-May, NeurIPS≈Dec, CVPR≈Jun, ICCV≈Oct, ECCV≈Aug-Oct, ACL≈Jul, AAAI≈Jan-Feb).

## Step 2 · Multi-source sweep (topic search + snowball)

Run when (a) no venue given, or (b) venue given AND accepted list obtained (use Step 1 to filter/rank within it). Parallelize.

**A. arXiv API (direct HTTPS, works in CN without proxy — verified).** Use `https://export.arxiv.org/api/query` (not http). **Query syntax matters** — a bare `all:stereo video generation` parses as loose OR; build explicitly:
- AND-join: `search_query=all:stereo+AND+all:video+AND+all:generation`
- phrase: `search_query=all:%22stereo%20video%20generation%22`
- `sortBy=relevance&max_results=40`. Run 2–3 variants (phrase + AND-join + synonym). Parse Atom: `<entry>`→`<title>`,`<id>`(arxiv id),`<summary>`,`<published>` year.
```bash
curl -sL --max-time 20 "https://export.arxiv.org/api/query?search_query=<built>&max_results=40&sortBy=relevance" -o <cache>/arxiv_<slug>.xml
```

**B. Semantic Scholar** (`api.semanticscholar.org/graph/v1/paper/search?...&fields=title,year,venue,externalIds,citationCount,abstract`). **Rate-limited (429)** — back off 5–20s, retry 2–3×; if still throttled, skip. **Snowball** the top 1–3 seeds: fetch `references` AND `citations` via `.../paper/arXiv:<id>/references` and `.../citations`. This catches neighbors flat search misses.

**C. DBLP** (`dblp.org/search/publ/api?q=<q>&format=json&h=60`) — each hit has real `venue`+`year`; good cross-check when a venue filter is active, and fallback for S2.

**D. Papers With Code** (`paperswithcode.com/api/v1/search/?q=<q>`) — may 302 under Cloudflare; skip if empty.

**E. WebSearch** — 4–8 queries with synonyms (`stereo`/`stereoscopic`/`3D`; `evolution`/`self-improve`/`self-evolve`). If it returns narrative instead of links, lean on the APIs.

**F. Conference proceedings** (only past venues): CVF/OpenReview/ACL Anthology/MLR/AAAI/EG.

Cache every raw response under `<store_dir>/_cache/search_<slug>/`. **Resilience**: free endpoints rate-limit; many independent sources means one failure doesn't sink the search — note dropped sources in caveats.

## Step 3 · Find the code repo for each hit (real repos only)

For every paper to be listed — **especially seeds** — three routes, stop at first repo:

1. **arXiv HTML full-text scrape (highest yield).** Abstracts usually have *no* links, but the HTML full text does:
```bash
curl -sL "https://arxiv.org/html/<id>" -o <cache>/<id>.html
grep -oE "https?://[A-Za-z0-9./_-]+" <cache>/<id>.html | grep -iE "github|gitlab|huggingface|\.io|\.page|zenodo" | grep -viE "arXiv/html_feedback|LaTeXML|jsdelivr|bootstrap"
```
Keep the GitHub repo URL + any project page. (Some papers, e.g. DeepMind's, have no HTML version — 404 is normal, fall through.) Also check `<arxiv:comment>` on the abs page.
2. **GitHub reverse search** (catches repos whose README cites the paper): `curl -sL "https://api.github.com/search/repositories?q=<title-or-project-name>&sort=stars"`. Pick the repo whose `description` mentions the arXiv id/title or whose owner matches authors. **GitHub search API limits ~10/min anonymous** — sleep 6–7s between calls; if 403, wait or skip.
3. **Project page first**: if Step 1 gives a project page, WebFetch it — it usually links the official repo.

If none yields a repo, **omit the code link**. Mark project-page-only papers accordingly.

## Step 4 · Dedup + select

Dedup by arxiv id (normalize `2401.12345v2`→`2401.12345`) then fuzzy title. Keep: title, short authors (`et al.` after 3), venue+year, arXiv link, code repo (Step 3), project page, one-line intuition. **If a venue filter is active**: keep ONLY papers confirmed accepted (Step 1) — drop everything else. Tag snippet-only matches (abstract not fetched) with `*`.

## Step 5 · Curate

Group: **Anchor/seed** (repos must be present) · **Directly related** · **Recent/SOTA** · **Foundational/predecessors** (from references). Sort by relevance then recency. Spotlight/Oral before Poster.

## Step 6 · Output (LIST, not table)

In chat, in the configured language, as **list items** — never a markdown table:
```
<短名> (venue/year)
  <一句话直觉,大白话,1–2句>
  arXiv: https://arxiv.org/abs/<id>      ← 没有就省略(OpenReview论文给 forum 链接)
  forum: https://openreview.net/forum?id=<id>   ← OpenReview论文用这个
  code:  https://github.com/<owner>/<repo>       ← 没找到就整行省略
  page:  https://<project-page>                  ← 没有就省略
```
Lead with a short framing (topic parse, seeds, sources run, caveats — including if the accepted list was unobtainable → stopped). End with **gaps/next steps** + offer to `/read <link>` any item.

Save the same content as `<store_dir>/_search/<YYYY-MM-DD>_<slug>.md`; tell the user the path.

## Honesty rules

- **Never invent** a paper, arxiv id, author, repo, or project page. Unknown → omit.
- **The conference filter is sacred.** Venue given + accepted list unobtainable → stop, don't substitute preprints.
- Distinguish verified (abstract fetched) vs snippet-only (`*`).
- Code links come only from Step 3's three routes — never guessed.
- **Credentials**: store only in `~/.claude/openreview_credentials.json`; never print the password; never write it into scripts, digests, or commits.
- Today's date from context; don't call `Date.now()`.

## Appendix · the verified access methods (2026-08, CN environment)

| Source | Method | Verified? |
|---|---|---|
| OpenReview API (ICLR/NeurIPS/ICML) | `openreview-py` login → `content={'venueid':...}` | ✅ got 6341 ICML2026 papers |
| OpenReview API anonymous (curl/requests) | `403 ChallengeRequired` — Cloudflare JS challenge | ❌ dead, regardless of IP/proxy |
| arXiv API | `https://export.arxiv.org/api/query` direct, no proxy | ✅ works in CN |
| arXiv HTML full text | `https://arxiv.org/html/<id>` direct | ✅ (some papers have no HTML — 404 normal) |
| CVF Open Access | `https://openaccess.thecvf.com/...` direct | ✅ no Cloudflare |
| GitHub search API | `api.github.com/search/repositories` | ✅ but ~10/min anonymous rate limit |
| Semantic Scholar | `api.semanticscholar.org/graph/v1/...` | ⚠️ frequent 429 |
| DBLP | `dblp.org/search/publ/api?format=json` | ✅ |
