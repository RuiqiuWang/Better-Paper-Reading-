# Development

Better Research contains two installable families. `read-*` keeps paper discovery, explanations and follow-ups compatible; `research-*` contains project management and paper-grounded evaluation design. Start with the [contribution guide](../CONTRIBUTING.md); `main` is the shared integration branch.

`skill_catalog.json` is the installer source of truth. Add a real skill there only after its entrypoint and resources are ready. Skills remain direct children of `skills/` so their existing imports, asset paths and installation names remain stable.

```text
skill_catalog.json       # installable families
install.py / .ps1 / .sh   # shared profile-based installer
skills/read*/            # existing paper-reading workflows
skills/research-manage/  # documentation, experiment records, local Git helper
skills/research-evaluate/ # paper evidence, evaluation contracts and task profiles
docs/                    # installation, topic workflow and module guides
tests/                   # reading, installation and Git behavior
.github/workflows/       # validation on Linux and Windows
```

Run from the repository root:

```sh
python -X utf8 -m unittest discover -s tests -v
node --check skills/read-main/assets/dashboard.js
node --check skills/read-main/assets/comments.js
python install.py --target codex --profile all --dry-run
git diff --check
```

Tests use temporary repositories and fixture identities; they must not push or modify a real research server. The local Git tests verify selection boundaries, staged-work preservation, interrupted commits and unchanged remote refs.

For documentation changes, check repository-relative links outside fenced examples and keep English/Chinese entrypoints consistent. Skill instructions are canonical for their workflow; guides link to them instead of copying full templates. The legacy `docs/experiment-logging-proposal.md` is a compatibility pointer to `docs/evaluation.md`.

The test workflow runs on pushes and pull requests on Linux and Windows. It checks the Python suite, reading UI JavaScript syntax and an installation dry run. A local passing run does not establish that remote CI has completed; report its status separately when available.

Default installation stays `reading` for compatibility; `research` and `all` are explicit choices. Retain legacy configuration names and `paper-reading-backups` so existing users retain their preferences and upgrade path. Source folder and remote repository names need not change with the product title.

New behavior must have an observable check where appropriate. Do not describe a planned skill or a proposal as installed functionality. Local commits are welcome; remote pushes require the user's explicit request.
