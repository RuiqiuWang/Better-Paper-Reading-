# Better Research

**A research workspace for AI agents — from understanding papers to organizing projects, designing reproducible evaluation and preparing efficient experiments.**

[简体中文](README.zh-CN.md) · [Documentation](docs/README.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

Better Research brings paper reading, research project management, evidence-based evaluation and performance preparation into one skill collection for **Codex and Claude Code**. It evolved from Better Paper Reading and preserves its reading commands, HTML library and personal configuration.

## Research workflow

| Stage | Skills | What you get |
|---|---|---|
| Discover and understand | `read-search`, `read` | Relevant papers, source-grounded explanations and HTML notes |
| Organize knowledge | `read-main`, `read-comment`, `read-rewrite` | A reading workspace, inline discussions and revised explanations |
| Coordinate automatically | `research-workflow` | Match natural-language requests to the shared trigger table and continue through the required stages |
| Manage a topic | `research-manage` | File navigation, method cards, experiment evidence and local Git history |
| Define evaluation | `research-evaluate` | Paper evidence, metric definitions, fixed samples, curves, tables and logging protocols |
| Prepare efficient experiments | `research-optimize` | Small-budget diagnosis, correctness checks, video pipelines and a two-stage 2Dto3D recipe |

`read-store` and `read-language` configure the reading library and explanation language. All **eleven skills** are registered in [skill_catalog.json](skill_catalog.json).

The reading workspace and local Git helper include executable tools. Evaluation and optimization are agent workflows with templates and task references; logging, scoring and plotting must be integrated with each topic's actual training or inference code. The skills do not start training or background monitoring on installation.

## Quick start

Requires **Python 3.8+**, an agent host with local file/shell access, and **Git** for version control. Paper discovery and retrieval require network access.

Run in a terminal:

```sh
git clone https://github.com/RuiqiuWang/Better-Research.git Better-Research
cd Better-Research
python install.py --target codex --profile all
```

Use `--target claude` or `--target both` for Claude Code. On systems where Python is named `python3`, use that executable.

| Profile | Installed skills |
|---|---|
| `all` | Reading and research; recommended for a new Better Research installation |
| `reading` | Seven reading skills; retained as the CLI default for compatibility |
| `research` | Automatic workflow, project management, evaluation and optimization; leaves reading settings intact |

Existing skills are backed up before updates. See [installation and upgrades](docs/installation.md) for locations, shell wrappers and dry runs.

Describe the research goal **in the agent conversation**. Skill commands are optional; [automatic routing](docs/automatic-workflow.md) selects and connects the required stages:

```text
$read-search monocular-to-stereo video generation
$read <paper-url>
Train and evaluate this new research topic on the allocated GPUs.
Run inference over the full dataset, reusing an applicable validated configuration.
Plan this topic first; do not start experiments yet.
```

Explicit skill commands remain available; Claude Code uses `/` instead of `$`. Follow the [topic workflow](docs/workflow.md) to connect these steps and record experiment results.

## Research records

Default server conventions separate code, shared assets and personal outputs:

```text
/home/<account>/code/<topic>/        # code, topic docs, protocols and local Git
/data/<topic>/                      # shared datasets, baseline assets and models
/data/<account>/envs/                # actual environments
/data/<account>/env_specs/           # environment recipes
/data/<account>/projects/<topic>/runs/<run-id>/
                                    # configs, metrics, checkpoints, predictions and logs
```

Topic and method documents explain **what is where, when it changed and why**. Run records retain concrete results and source evidence. Fixed manifests and versioned evaluation protocols keep comparisons traceable; stereo-video and depth-estimation references are included.

Small code and documentation changes are committed locally. **Remote pushes require an explicit user request.** Large datasets, environments, weights and videos stay outside ordinary Git. Existing research directories are documented before any separately authorized migration.

## Documentation and maintenance

- [Documentation index](docs/README.md): reading, research management, evaluation, optimization and installation.
- [Automatic trigger table](skills/research-workflow/references/triggers.md): scenarios, skill order and conditions for continuing into full runs.
- [Optimization guide](docs/optimization.md): cross-domain workflow → general video pipelines → two-stage 2Dto3D; load only the relevant references.
- [Contributing](CONTRIBUTING.md): small changes, validation and review.
- [Development](docs/development.md): repository structure and verification commands.
- [Roadmap](docs/roadmap.md): current capabilities and future work.

`main` is the shared integration branch. Continue development in this repository, normally on focused `codex/<topic>` branches.

The repository is now **RuiqiuWang/Better-Research**. Existing clones can update their remote using the [upgrade guide](docs/installation.md). Legacy reading configuration and backup names are retained for upgrades.

[MIT License](LICENSE).
