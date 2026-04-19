# AGENTS.md

## Repo Purpose

This repository contains a local-first Gmail + Google Sheets + LLM workflow system that replaces a Google Apps Script implementation with an agent-developable, testable, and resumable software codebase.

The repository is also an agent harness. Its root files are expected to act as an external memory and control system for long-running implementation work. A future coding agent should be able to resume from repository files rather than from hidden chat history.

## Start Here

1. Read `AGENTS.md` for repository-wide navigation rules.
2. Read `README.md` for the overall repository picture.
3. Read `ARCHITECTURE.md` when you need structure boundaries and lifecycle rules.
4. Read `PLANS.md` before implementing any major feature or refactor.
5. Before editing a specific area, read its local `README.md` if one exists.

## Top-Level Map

- `docs/`: stable repository-level contracts, workflows, and validation rules
- `tasks/`: active implementation tasks and temporary investigation files
- `apps/`: human-facing entrypoints such as CLI and optional local API
- `packages/`: core application modules
- `tests/`: unit, integration, and smoke validation
- `scripts/`: deterministic helper commands
- `runtime/`: local runtime artifacts, logs, and state files
- `archive/`: historical task context that is no longer active

## Source-of-Truth Rules

- Root `AGENTS.md` is the shared entry point; deeper guides own the details.
- Trust local `README.md` / `AGENTS.md` over filename guesses.
- `docs/contracts/` is the stable home of interface contracts.
- `tasks/active/` is active context by default; `archive/` is historical context by default.
- `runtime/` is execution artifact space, not the primary source of truth.
- `PLANS.md` is the living implementation plan for long-running work and must stay synchronized with actual progress.
- If `PLANS.md` and the repository drift apart, fix `PLANS.md` or the drift itself before continuing with large implementation work.

## Working Rules

- Prefer additive, testable changes.
- Do not bypass the `packages/google_workspace/` boundary to call `gws` from arbitrary modules.
- Run the documented preflight before any live Gmail or Sheets operation.
- Do not treat live smoke validation as a substitute for unit or integration tests.

## ExecPlan Rule

When writing a complex feature or significant refactor, use `PLANS.md` as the primary execution contract. Treat it as both:

- external memory: the durable context a future agent needs in order to resume
- control plane: the ordered action system that tells the next agent what to do next

### When To Create Or Rewrite The ExecPlan

Create or rewrite `PLANS.md` when:

- the work will span multiple sessions or handoffs
- the work has significant unknowns or research requirements
- the work crosses multiple modules, contracts, or human gates
- a future agent would likely make the wrong tradeoff without explicit design guidance

If the current `PLANS.md` is no longer self-contained enough for a novice agent to resume safely, update the plan first.

### ExecPlan Authoring Rules

When authoring or restructuring `PLANS.md`:

- Make it self-contained enough that a novice agent can resume from the working tree plus `PLANS.md` alone.
- Define non-obvious terms in plain language near where they appear.
- Name repository-relative files and modules explicitly.
- Record the current active action, the next queued actions, and any blocked or deferred actions.
- For each action, include enough detail for the next agent to know what to inspect, what to edit, what to run, and what evidence proves completion.
- Summarize any external-system facts that are required for implementation inside `PLANS.md` itself. External fetch steps may exist as refresh paths, but they should not be the only place the facts live.

### ExecPlan Implementation Rules

When implementing from `PLANS.md`:

- Do not ask the user for next steps if the next action is already defined in `PLANS.md`.
- Follow the current active action or the first eligible queued action according to the selection rules in `PLANS.md`.
- Prefer this loop:
  1. inspect current code and contracts
  2. implement one bounded action
  3. run the most relevant validation
  4. update `PLANS.md` with progress, decisions, discoveries, and next action state
  5. continue unless a human validation gate is reached
- At every stopping point, update:
  - `PLANS.md`
  - affected contract docs in `docs/contracts/`
  - any new implementation notes needed to resume the task

### ExecPlan Revision Rules

When discussing, revising, or changing course:

- Record design changes in `Decision Log`.
- Record unexpected behavior, failed assumptions, or useful evidence in `Surprises & Discoveries`.
- Split partially completed work into explicit done and remaining action states.
- Add a change note at the bottom of `PLANS.md` when the plan structure or implementation strategy materially changes.

### Stop Conditions

Stop only when:

- a human approval gate in `PLANS.md` is reached
- authentication or environment preflight fails
- the current action is blocked by missing external information
- `PLANS.md` is too stale or ambiguous to safely continue and must be repaired first

## Human Gates

The agent may continue autonomously until one of these gates is reached:

- a live Gmail or Google Sheets write is about to happen for the first time
- a destructive or irreversible operation is required
- the repository contracts are no longer sufficient to choose between multiple valid product directions

If blocked, the agent must record:

- what it tried
- what failed
- the exact missing input or decision
- the safest next resumption point
