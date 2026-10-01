# Changelog

## 2026-10-02

- Add implicitly selected `research-workflow` with one maintained scenario trigger table: prepare/evaluate, reuse or benchmark, validate, continue the authorized full run, and record results. Preserve planning-only, benchmarking-only and recovery boundaries.
- Make natural-language research requests the default documented entrypoint and include all four research skills in research/all profiles.

- Add `research-optimize`: bounded performance diagnosis before large training/inference runs, with reusable configurations, correctness checks and fallback decisions.
- Organize guidance into cross-domain workflow, general video pipelines, and two-stage 2Dto3D. Include a sanitized measured case summary; distinguish verified short-window inference from untested training/long-video candidates.
- Register the third research skill in research/all installation, route evaluation and project records to performance preparation, and update bilingual entrypoints and documentation. No production model or server changes are included.

## 2026-10-01

- Rename the GitHub repository to `RuiqiuWang/Better-Research`; update clone URLs and document remote migration for existing checkouts. Preserve repository history and reading configuration compatibility.
- Consolidate Better Research as the maintained project: rewrite bilingual entrypoints around the research workflow, add installation/workflow/contribution guides and a scoped roadmap, and promote evaluation documentation while preserving its old link.
- Keep the legacy repository URL, reading commands and configuration compatible; maintain research and reading modules together on main. Extend CI with a full-profile installer dry run.
- Add `research-evaluate`: research relevant papers and official evaluation code, then define sourced metrics, curves, tables, logs and versioned fixed-sample protocols for each topic.
- Include stereo-video and depth-estimation guidance, raw result retention, timing/resource records and checkpoint/continuation rules. This release adds agent instructions and templates, not a running training logger.
- Include both research skills in the research/all install profiles; preserve reading defaults and document the adopted evaluation workflow.
- Reframe the project as Better Research, with a short entrypoint, preserved paper-reading guides, a research guide and a validated skill catalog.
- Add local-only Git initialization/status/checkpoints to `research-manage`; select explicit files, preserve unrelated staged work, and perform no remote operations.
- Record the curve/fixed-video discussion as a proposal, not implemented experiment behavior.
- Add optional `research-manage`: topic paths, method cards, change history, experiment index and evidence-linked run results, including failed/partial runs and corrections.
- Keep code under `/home` and personal environments under `/data`; preserve existing `read-*` commands.
- Add `--profile reading|research|all` (`-Profile` in PowerShell). Default installation remains the seven reading skills; research-only installs preserve reading customization.

## 2026-09-16

- Add a reading workspace with persistent sessions, projects, pins, search, archives and legacy-note import.
- Open each completed reading at its own session and return clickable workspace and note links.
- Change explanations to technical/intuitive overviews and adaptive, source-grounded deep reading.
- Add contextual rewrites and portable numbered/global comment threads with a right sidebar.
- Preserve reading sessions during follow-ups, back up HTML, and reject stale or ambiguous edits.
- Support Codex and Claude Code through shared Python, Bash and PowerShell installers; back up existing skills and reuse legacy Codex installations.
- Resolve reading settings and optional OpenReview credentials per host; preserve existing notes and configuration.
- Document both command formats, installation paths, storage boundaries and verification limits in English and Chinese.
