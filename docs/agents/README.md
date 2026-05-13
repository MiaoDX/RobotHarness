# Agent Runbooks

This directory holds repo-specific procedures that are useful to coding agents
but too long for the root startup files.

Read the root files first:

1. `AGENTS.md`
2. `CLAUDE.md`
3. the dependency, pytest, and coverage sections of `pyproject.toml`

Then use the runbook that matches the task:

- `release.md` - release branch, version, PyPI, and post-release checks.
- `ci-debugging.md` - how to investigate failing CI without guessing.
- `testing.md` - test quality standards and validation gates.
- `environments.md` - CPU, GPU, MuJoCo, and local/CI environment boundaries.
- `github-workflow.md` - PR fix strategy and GitHub tooling rules.
- `design-workflow.md` - design/planning artifact mirroring and persistence.
