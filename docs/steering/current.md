# Steering Cockpit (Current)

## North Star

Trust compression for unattended robot-code changes.

## Current Milestone

**v0.3 — Trust Loop (MuJoCo contract-first approval loop)**

## Must Do

- Seed and maintain a deterministic evaluator corpus for the MuJoCo wedge.
- Keep `CONTRACT_INVALID` behavior fail-closed.
- Ensure `AMBIGUOUS` results never self-promote to `PASS`.
- Keep migration `PASS` gated behind explicit baseline blessing.
- Keep release truth aligned across repo version, GitHub Releases, and PyPI.

## Must Not Do (During v0.3)

- Add new simulator backends.
- Split into new showcase repos.
- Expand SONIC backend scope without real-model validation evidence.
- Prioritize outreach/docs polish over trust-loop calibration.

## Review Gate

Changes that affect approval semantics, release semantics, or strategic direction must receive human review before merge.
