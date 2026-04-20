# TODOS

This file captures deferred work from approved planning and review artifacts.

## Completed

### Sync README and docs to the new evidence contract

- **Completed:** PR #201 (2026-04-15)
- Updated `README.md`, `CONTRIBUTING.md`, and `ARCHITECTURE.md` so the MuJoCo grasp
  example explains the paired-evidence summary, explicit evidence states, the
  `failed phase -> proof -> rerun` loop, and the current contributor verification flow.

### Run post-implementation boomerang reviews

- **Completed:** 2026-04-20
- Repo-local boomerang review is mirrored in
  `docs/designs/unattended-refactor-harness-boomerang-review-20260420.md`.
- Outcome: the report design contract held, but the README front door needed an honest
  split between package-first integration and the repo-only MuJoCo wedge demo.

### Build a seeded evaluator corpus before treating the queue as trustworthy

- **Completed:** 2026-04-20
- Added `tests/test_mujoco_grasp_seeded_corpus.py` with seeded `good`, `bad`, and
  `ambiguous` cases for the MuJoCo wedge.
- The corpus locks surfaced-case precision `1.0`, surfaced-case recall `1.0`, and the
  trust boundary that ambiguous still-image evidence must stay review-required.

### Add temporal evidence when still images are ambiguous

- **Completed:** 2026-04-20
- Ambiguous MuJoCo wedge cases now render checkpoint-ordered temporal evidence strips
  in the approval report.
- The first implementation stays wedge-tight: it adds phase-ordered visual context
  without introducing a full clip or video pipeline.

### Add click-to-zoom or lightbox support for evidence cards

- **Completed:** 2026-04-20
- Evidence cards and temporal thumbnails now expand in-place with a keyboard-closeable
  lightbox instead of forcing users into the deeper checkpoint gallery.

### Split the canonical spec from the review log once implementation starts

- **Completed:** 2026-04-20
- `docs/designs/unattended-refactor-harness-v1.md` is the canonical product/design
  contract.
- `showcase-repo-plan.md` remains the reviewed plan and rationale log, and both files
  now state that split explicitly.

## 4. Extract a shared evidence contract only after a second stack needs it

- What: Promote the phase-local evidence-pair resolver into a shared abstraction only
  when another task or simulator genuinely needs the same contract.
- Why: The approved CEO and engineering reviews both flagged premature extraction as
  strategy debt.
- Pros: Avoids calcifying a one-off example seam, keeps the first implementation
  explicit, and forces the abstraction to be justified by a second concrete use case.
- Cons: Leaves some local duplication in place for now and delays platform leverage.
- Context: The approved plan locks phase 2 to example-local code and states the
  extraction trigger explicitly.
- Depends on / blocked by: A second task or stack proving it needs the same
  `manifest-selected paired evidence` contract.

## 7. Revisit freeform prompt-to-contract compilation only after presets prove out

- What: Expand from template-first contract compilation to broader prompt-assisted
  authoring only after the schema, error envelope, and wedge defaults prove themselves.
- Why: The reviewed plan explicitly rejected open-ended NL-to-contract compilation as a
  v1 bet. It is a later expansion, not part of the first trust loop.
- Pros: Keeps the first wedge boring and reliable while preserving the longer-term
  ambition.
- Cons: Delays the most magical version of the product story.
- Context: Deferred by the reviewed CEO and engineering phases in
  `showcase-repo-plan.md`.
- Depends on / blocked by: preset adoption, schema stability, and evidence that the
  current wedge is already trustworthy.
