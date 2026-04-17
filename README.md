# gws-cv-mail-harness

Local-first Gmail + Google Sheets + LLM workflow system, designed to be developed by coding agents and validated through repeatable tests and live smoke runs.

## How To Read This Repo

- `AGENTS.md`
  Repository-wide navigation and operating rules for agents
- `README.md`
  Overview and first-pass navigation
- `ARCHITECTURE.md`
  Structure boundaries, lifecycle rules, and source-of-truth heuristics
- `PLANS.md`
  Living implementation plan for the main delivery path
- `docs/`
  Stable contracts, workflows, and validation guidance

## Repo Structure

- `apps/`
  Human-facing entrypoints such as CLI and optional local API
- `packages/`
  Core modules for Google access, extraction, state, digest, scheduling, and orchestration
- `tests/`
  Unit, integration, and smoke validation
- `docs/`
  Stable repository-level contracts and workflows
- `tasks/`
  Active scoped work and short-lived investigation files
- `scripts/`
  Repeatable helper commands for preflight, smoke runs, and sync tasks
- `runtime/`
  Local runtime artifacts such as logs, cache, and SQLite state

## Directory Rules

- Stable repository guidance: store in `docs/`
- Production code: store in `apps/` and `packages/`
- Active implementation work: store in `tasks/active/`
- Test data and verification logic: store in `tests/`
- Local execution artifacts: store in `runtime/`

## Success Bar

This repository is considered healthy when:

- a new coding agent can find the current implementation path from `AGENTS.md` and `PLANS.md`
- contracts for Gmail, Sheets, digest output, and config are explicit in `docs/contracts/`
- the main workflow can be validated at unit, integration, and live smoke levels
- failures can be diagnosed from repo files plus runtime logs without relying on hidden chat context
