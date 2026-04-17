# ARCHITECTURE.md

This file explains the repository-level structure of `gws-cv-mail-harness`.

It focuses on:

- why the repository is partitioned this way
- how content moves between areas
- which locations are usually the current source of truth

## Relationship To Other Root Files

- `README.md`
  overview and quick navigation
- `AGENTS.md`
  agent navigation and reading order
- `PLANS.md`
  living implementation path for major work

## Partition Model

- `docs/`
  stable contracts, workflows, and methods
- `tasks/`
  active task context and scoped investigations
- `apps/`
  runnable entrypoints
- `packages/`
  reusable implementation modules
- `tests/`
  validation layers
- `runtime/`
  execution artifacts
- `archive/`
  historical task context

## Content Lifecycle

1. A new requirement starts in `tasks/active/`.
2. Stable contracts discovered during implementation move into `docs/contracts/`.
3. Reusable workflow rules move into `docs/workflows/`.
4. Runtime evidence lands in `runtime/`.
5. When a task is complete, its temporary context moves to `archive/`.

## Source-of-Truth Heuristics

1. Start from `AGENTS.md` and `README.md`.
2. Use `ARCHITECTURE.md` to resolve boundary questions.
3. Use `PLANS.md` for the main delivery path.
4. Once inside a directory, follow local guides.
5. Trust `docs/contracts/` over ad hoc code comments when interface meaning is unclear.

## Boundary Rules

### Google Workspace Boundary

- Only `packages/google_workspace/` may call `gws`.
- All Gmail / Sheets operations must flow through typed wrappers.

### State Boundary

- Durable run state belongs in `runtime/state/` and is managed through `packages/state_store/`.
- Do not treat in-memory agent context as durable state.

### Validation Boundary

- `tests/unit/` proves logic
- `tests/integration/` proves wrappers and contracts
- `tests/smoke/` proves real environment behavior

No single layer substitutes for the others.
