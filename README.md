# Better Research

**Composable skills for paper reading and research project management in Codex and Claude Code.**

[简体中文](README.zh-CN.md) · [Changelog](CHANGELOG.md) · [MIT license](LICENSE)

Evolved from Better Paper Reading. Existing reading commands and configurations remain compatible; the checkout and remote repository names are unchanged.

## Available modules

| Family | Skills | Capability |
|---|---|---|
| Reading | `read`, `read-main`, `read-search` | Paper explanations, workspace and discovery |
| Follow-ups and preferences | `read-rewrite`, `read-comment`, `read-store`, `read-language` | Contextual edits, annotations, storage and language |
| Research | `research-manage` | Topic navigation, method cards, experiment evidence and local Git checkpoints |
| Evaluation design | `research-evaluate` | Paper-grounded metrics, curves, tables, logs and fixed sample protocols for new topics |

See the [reading guide](docs/reading.md) and [research management guide](docs/research-management.md). Research skills use `research-<action>`; existing `read-*` names stay stable.

## Install

Python 3.8+ is required. Local version control also requires Git.

```sh
git clone https://github.com/RuiqiuWang/Better-Paper-Reading-.git
cd Better-Paper-Reading-
python install.py --target codex --profile all
```

Profiles: `reading` (default, original seven skills), `research` (management and evaluation design), or `all`. Use `--target both` for both hosts and `--dry-run` to preview. Existing skills are backed up; reading notes and personal configuration are preserved.

```powershell
./install.ps1 -Target codex -Profile all
```

```sh
bash install.sh --target both --profile all
```

Installation locations, legacy upgrades and reading configuration are documented in the [reading guide](docs/reading.md).

## Use

```text
$read <paper-url>
$research-manage Organize this topic, record experiment results, and maintain local Git history.
$research-evaluate Find relevant papers for this topic and define metrics, curves, tables, logs and fixed evaluation samples.
```

Claude Code uses `/read` and `/research-manage`. Code lives under `/home`, environments under `/data`; meaningful updates produce local commits of relevant code and small documents. **Push only when the user explicitly requests it.** Large datasets, weights, videos and environments stay outside ordinary Git.

## Layout

```text
skill_catalog.json       # installer source of truth for both families
skills/read*/            # compatible paper-reading workflows
skills/research-manage/  # instructions, references and local Git helper
skills/research-evaluate/ # evidence-based evaluation workflow and task references
docs/                    # user guides, development notes and proposals
tests/                   # reading, installation and Git behavior
install.py/.ps1/.sh      # common profile-based installer
```

See [development](docs/development.md) for checks and the [evaluation guide](docs/experiment-logging-proposal.md) for recording protocols. `research-evaluate` supplies agent instructions and templates; it is not a training logger or automatic plotting service. Integration into an actual trainer is a separate task. No training, server migration or background monitoring is started automatically.
