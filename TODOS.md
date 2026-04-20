# TODOS

This file captures deferred work from approved planning and review artifacts.

## 1. Add temporal evidence when still images are ambiguous

- What: Add a short clip, scrubber, or temporal overlay for failure cases where paired
  still images are suggestive but not decisive.
- Why: The approved phase-2 plan explicitly keeps still-image evidence as the first
  wedge, but some motion-rooted failures will remain under-explained.
- Pros: Improves trust for trajectory and timing regressions, reduces false confidence
  from a single frame, and strengthens the agent rerun loop.
- Cons: Adds asset weight, UI complexity, and new decisions about encoding, playback,
  and report portability.
- Context: Deferred by the approved review in
  `docs/designs/mujoco-alarmed-grasp-loop-phase-2-plan-reviewed.md`. The current plan
  already introduces an explicit `ambiguous still-image evidence` state so this work
  has a clear trigger.
- Depends on / blocked by: Phase 2 implementation landing first, plus at least one real
  ambiguous failure observed in MuJoCo or a second stack.

## 2. Add click-to-zoom or lightbox support for evidence cards

- What: Let users enlarge the new phase-2 comparison cards without dropping into the
  deeper checkpoint gallery.
- Why: The approved plan keeps evidence cards passive to stay wedge-tight, but detailed
  image inspection may still benefit from a lighter-weight zoom path.
- Pros: Faster visual inspection, better use of the new evidence cards, less context
  switching between summary and gallery.
- Cons: Broadens the UI surface, adds focus/keyboard/a11y work, and duplicates some of
  the value of the existing checkpoint gallery.
- Context: Explicitly deferred in the approved design review because the deeper gallery
  already exists and the phase-2 bottleneck is proof ordering, not interaction chrome.
- Depends on / blocked by: Phase 2 evidence cards shipping first and proving useful
  enough to justify a richer interaction.

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

## 6. Build a seeded evaluator corpus before treating the queue as trustworthy

- What: Assemble seeded `good`, `bad`, and `ambiguous` cases for the MuJoCo wedge and
  measure surfaced-case precision before the approval queue is treated as trustworthy.
- Why: The reviewed CEO, engineering, and DX passes all converged on the same point:
  a small queue that misses or misclassifies cases is worse than a larger honest one.
- Pros: Makes queue trust measurable, catches suppressed-case failures early, and gives
  the README/front door a defensible story.
- Cons: Adds fixture and eval maintenance work.
- Context: Deferred by the reviewed contract-first plan in
  `showcase-repo-plan.md`. This is the gating follow-up for the "conditional trust"
  decision, not optional polish.
- Depends on / blocked by: the surfaced/suppressed-case implementation existing first.

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

## 8. Split the canonical spec from the review log once implementation starts

- What: Separate the clean product/design contract from the long `/autoplan` review log
  so implementers have one concise spec artifact to follow.
- Why: The design and DX reviews both flagged that the current plan file is becoming a
  mix of accepted product truth and review commentary.
- Pros: Reduces implementation ambiguity, makes handoff cleaner, and keeps the repo's
  canonical design artifacts easier to maintain.
- Cons: Creates one more artifact to keep current.
- Context: Deferred by the reviewed design phase in `showcase-repo-plan.md`.
- Depends on / blocked by: final approval of the reviewed plan, then the start of the
  implementation pass.
