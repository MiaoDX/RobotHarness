# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-04-20

### Added

- Added a shared paired-evidence contract in `roboharness.approval.evidence`,
  including bounded path resolution plus reusable lightbox/image helpers for
  approval surfaces.
- Added a second concrete consumer of that contract with
  `examples/g1_cross_framework_report.py`, backed by the committed
  `assets/g1/X36_Y28_Z13/` Meshcat-vs-MuJoCo proof bundle.
- Added a seeded MuJoCo approval corpus covering `good`, `bad`, and `ambiguous`
  review outcomes to lock the surfaced-case trust boundary.
- Added a script-level regression test proving `examples/mujoco_grasp.py`
  exits cleanly and writes `contract_compile_error.json` when contract
  compilation fails before execution.

### Changed

- Refactored the MuJoCo unattended-approval wedge to use the shared evidence
  contract instead of keeping paired-evidence logic local to the example.
- Expanded the MuJoCo proof surface with temporal evidence strips and
  click-to-zoom lightbox support for ambiguous or detail-heavy review cases.
- Added reviewed contract preset selection plus constrained prompt-assisted
  preset selection to `examples/mujoco_grasp.py`, while keeping unsupported
  open-ended authoring fail-closed.
- Rewrote the README front door around the unattended approval wedge, with a
  clearer split between package-first integration and the repo-only MuJoCo demo.

## [0.2.2] - 2026-04-15

### Fixed

- Fixed generated MuJoCo grasp reports so embedded Meshcat scenes resolve from the
  report output root instead of shipping dead iframes.
- Contained wide report tables and the Meshcat viewer on small screens so the report
  no longer forces horizontal scrolling on mobile or split-screen layouts.
- Cleared pass-state artifact metadata so successful runs show `Root cause: none` and
  `Rerun hint: No rerun required` instead of failure-only hints.

### Added

- Added regression tests covering Meshcat embed paths, responsive report containment,
  and pass-state metadata consistency.
- Added a repo-local mirror of the MuJoCo grasp report design audit under
  `docs/designs/`.
