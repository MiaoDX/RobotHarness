# Design And Planning Artifact Persistence

Long design, planning, and review sessions need a repo-local source of truth.
Do not rely on chat context alone once decisions start getting locked in.

## Mirroring External Artifacts

When a design or planning skill writes artifacts outside the repo, keep that
external copy if the skill needs it for cross-session discovery, but mirror the
approved project-facing artifact into `docs/designs/` so the repository remains
self-contained.

For `/office-hours` outputs:

- mirror the approved design doc into `docs/designs/`
- mirror project-relevant sketch HTML into `docs/designs/` when available
- do not treat `/tmp` files as canonical project artifacts

## Decision Persistence

After each approved review block or major decision set, mirror accepted
decisions into a repo-local artifact under `docs/designs/` or another
task-appropriate docs path.

Before implementation from a long interactive review:

1. Ensure the latest approved decisions exist in a repo-local file.
2. Save a checkpoint or equivalent handoff if context may be lost.
3. Treat repo-local docs as the canonical project record.

Use `~/.gstack/projects/...` checkpoints as a handoff layer when relevant, not
as the only durable project record.
