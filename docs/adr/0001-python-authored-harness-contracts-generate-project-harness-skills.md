# Python-authored harness contracts generate project harness skills

Status: accepted

Roboharness will expose a public `roboharness.contract` layer where a trusted Python-authored `HarnessContract` is the source of truth for a project's semantic phases, hard metric gates, visual review dimensions, evidence boundaries, approval policy, and validation commands. Deterministic compilation from that contract will generate the project harness skill, normalized contract snapshot, schemas, and optional runnable stubs under `agent-skill/<project-slug>-harness/`; generated artifacts are drift-checked and are not edited as source.

This keeps the agent-facing skill soft and self-extensible without making prompt text authoritative. A coding agent may read the repository, draft a Harness Scope Brief, and propose a `contract.py`, but the user approves the scope before the contract becomes authoritative. Existing contracts can be used directly; out-of-scope requests route through contract improvement before the agent treats new checks as approved review paths.

Roboharness will dogfood the workflow with `agent-skill/roboharness-harness/contract.py`, generated skill artifacts beside it, and no root `SKILL.md`. One project harness skill may contain multiple named harness workflows rather than creating one skill per validation path.

Considered alternatives included YAML-first contracts, handwritten `SKILL.md` prompts, LLM-regenerated skill prose, keeping a flat root `SKILL.md`, and generating one skill per workflow. These were rejected because they either make review criteria less type-safe, make drift checks unreliable, scatter the source of truth, or make downstream projects feel like a collection of disconnected harness fragments instead of one project-level review capability.
