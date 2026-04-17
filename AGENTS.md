# AGENTS.md

## Repo Purpose

This repository contains a local-first Gmail + Google Sheets + LLM workflow system that replaces a Google Apps Script implementation with an agent-developable, testable, and resumable software codebase.

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

## Working Rules

- Prefer additive, testable changes.
- Do not bypass the `packages/google_workspace/` boundary to call `gws` from arbitrary modules.
- Run the documented preflight before any live Gmail or Sheets operation.
- Do not treat live smoke validation as a substitute for unit or integration tests.
