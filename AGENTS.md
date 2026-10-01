# Better Research

- Preserve the existing `read-*` workflows, configuration and user libraries.
- Add research capabilities under `research-*`, registered in `skill_catalog.json`.
- Work in small increments. Keep proposals clearly separate from implemented behavior.
- After meaningful authorized changes, validate and make a local Git commit containing only relevant files. Preserve unrelated working/staged changes; never reset or clean them to make a commit.
- Do not add/change remotes or push unless the user explicitly requests it.
- Keep credentials, environments, large data, model weights and generated media out of this source repository.
- Use `docs/development.md` for the verification commands.
- Treat `main` as the integration branch; use focused `codex/<topic>` branches for new work. Merge/push only within the user's authorization; preserve shared history.
- Keep the project entrypoints and `docs/README.md` aligned. Protocol instructions live in skills; real topic assets and experimental data belong in their own projects.
