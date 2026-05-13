# Roboharness

Visual testing harness for AI coding agents in robot simulation. Python 3.10+,
numpy core, optional MuJoCo/Meshcat/Rerun backends.

Follow repo-wide instructions in `AGENTS.md`; this file only adds
Claude-specific notes and quick orientation.

## Quick Orientation

- `src/roboharness/core/` - `Harness`, checkpointing, capture, protocols, and
  controller interfaces.
- `src/roboharness/backends/` - simulator adapter implementations.
- `src/roboharness/wrappers/` - Gymnasium wrappers for zero-change integration.
- `src/roboharness/storage/` - task-oriented file storage and evaluation
  history.
- `src/roboharness/evaluate/` - metric assertions, batch evaluation, and
  LeRobot evaluation helpers.
- `src/roboharness/approval/` - paired current-vs-baseline evidence and review
  decisions.
- Public API: `Harness`, `Checkpoint`, `CheckpointStore`, `CaptureResult`.

Key local pattern: `SimulatorBackend` is a Protocol. New backends implement its
methods without inheriting from a base class.

## Claude-Specific Workflow

Use subagents only when the environment supports them and the work can be split
cleanly. Keep repo-wide rules, validation gates, and commit hygiene from
`AGENTS.md` authoritative.

For GitHub interactions in Claude web/cloud environments, use GitHub MCP tools
when available; `gh` is usually not authorized there. In local CLI/IDE
environments, `gh` may be used when already authenticated. If an MCP call fails
because the service is temporarily unavailable, wait briefly and retry before
changing approach.

## Agent Runbooks

- Release process: `docs/agents/release.md`
- CI failure investigation: `docs/agents/ci-debugging.md`
- Testing standards: `docs/agents/testing.md`
- Development environments and GPU boundaries: `docs/agents/environments.md`
- GitHub and PR workflow: `docs/agents/github-workflow.md`
- Design/planning artifact persistence: `docs/agents/design-workflow.md`
