# This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

## Purpose / Big Picture

Build a local-first software system that can search Gmail, read messages, extract structured information, write results to Google Sheets, and send digest emails, while being maintainable by coding agents working from repository files and tests rather than hidden conversational context.

The user-visible proof is simple: a human can run a local command, observe new rows appear in a test Google Sheet, receive a digest email, and rerun the same command without duplicate processing.

This repository is intentionally CLI-first. The first successful version does not need a local web UI. It needs a stable build-test-run loop, observable state, and clear contracts so a coding agent can progress through milestones without repeatedly asking the user what to do next.

## Progress

- [x] (2026-04-17 11:20+08:00) Bootstrapped the root repository scaffold and pushed the initial commit.
- [x] (2026-04-17 11:35+08:00) Added ExecPlan rules to `AGENTS.md` so future agents are required to treat this file as the primary execution contract.
- [x] (2026-04-17 11:35+08:00) Added first-pass contract docs and helper scripts so the next agent has stable starting points.
- [x] (2026-04-17 14:57+08:00) Milestone 1: implemented repository-safe `gws` preflight and typed Gmail / Sheets wrapper helpers in `packages/google_workspace/`, including deterministic JSON parsing for noisy CLI output and request previews for dry-run write/send operations.
- [x] (2026-04-17 14:57+08:00) Milestone 2: implemented local SQLite state and idempotency tracking in `packages/state_store/` for runs, processed messages, and digest events.
- [x] (2026-04-17 14:57+08:00) Milestone 3: replaced CLI placeholders with working `preflight`, `run-once`, and `show-state` commands backed by YAML config, runner logic, digest building, and SQLite state.
- [x] (2026-04-17 14:57+08:00) Milestone 4: added unit and integration tests for wrappers, config, state, and runner behavior; verified the CLI preflight and `run-once --dry-run` path against the local environment.
- [x] (2026-04-17 16:00+08:00) Milestone 5: completed live smoke validation against the configured test Gmail query and test Google Sheet, including first real Sheet append, digest send, state recording, rerun verification, and a follow-up idempotency fix when the first rerun check exposed duplicate-prevention drift.

## Surprises & Discoveries

- Observation: The initial scaffold alone is not enough to make a future agent autonomous.
  Evidence: Before this revision, the repository had structure but lacked explicit next-step rules, human gates, and stable contract files.
- Observation: `gws gmail +read --format json` can return address-shaped fields as either objects or lists, even in otherwise similar message payloads.
  Evidence: The first real `uv run python -m apps.cli run-once --config runtime/config.local.yaml --dry-run` at 2026-04-17 14:56+08:00 partially failed with `"'list' object has no attribute 'get'"` for Gmail thread `19d96ca9ab88ac82`; normalizing list-shaped address payloads fixed the rerun and the second dry-run completed with `matched_count=3`, `processed_count=3`, `failed_count=0`.
- Observation: The dry-run path is still useful with live Gmail reads because the write/send layers expose request previews while the state store avoids marking messages as processed.
  Evidence: The validated dry-run recorded run metadata and digest preview state, showed the exact Sheets append payload, and left `processed_messages` empty in `show-state`.
- Observation: Live reruns could duplicate prior work because Gmail search returns Gmail API message ids while `gws gmail +read` exposes the RFC `Message-ID` header under `message_id`.
  Evidence: `show-state` on 2026-04-17 16:xx+08:00 showed successful live runs with `processed_count=3`, but `processed_messages` contained RFC-style ids such as `...@mail.gmail.com` while future search results were matched against Gmail API ids. The runner now records the search result id as the durable processed key and includes a compatibility check against legacy header-based state rows.
- Observation: The live smoke checklist was executed through the `Failure Handling` section and confirmed the happy path before the rerun bug was corrected.
  Evidence: `docs/workflows/live-smoke-validation.md` is now checked through preflight, dry-run review, live run, rerun check, and failure handling preparation based on the operator’s completed validation steps.

## Decision Log

- Decision: Start CLI-first and postpone any local web UI.
  Rationale: CLI is the shortest path to proving the core workflow.
  Date/Author: 2026-04-17 / Codex

- Decision: Treat `docs/contracts/` as the stable home for Gmail, Sheets, digest, and config meaning.
  Rationale: Without stable contract files, future agents are forced to infer semantics from code and may drift in behavior.
  Date/Author: 2026-04-17 / Codex

- Decision: The first live Gmail or Google Sheets write is a human gate.
  Rationale: This keeps early development safe while still allowing agents to make progress through local code, tests, and dry runs.
  Date/Author: 2026-04-17 / Codex

- Decision: `run-once --dry-run` should perform live Gmail search/read operations but keep Sheets append and Gmail send in request-preview mode.
  Rationale: This gives a human a realistic preview of rows and digest content without crossing the first live-write gate.
  Date/Author: 2026-04-17 / Codex

- Decision: Treat `runtime/config.local.yaml` as the operator-local config path and commit `runtime/config.local.example.yaml` as the shareable template.
  Rationale: The repo needs a concrete convention for repeatable dry-run and smoke commands without committing local secrets or operator-specific values.
  Date/Author: 2026-04-17 / Codex

- Decision: Idempotency in `processed_messages` is keyed by the Gmail API message id from search results, not the RFC `Message-ID` header.
  Rationale: Gmail API search and rerun eligibility operate on Gmail message ids; storing a different identifier breaks duplicate prevention across runs.
  Date/Author: 2026-04-17 / Codex

## Outcomes & Retrospective

- Current outcome: The repository now has a working local-first implementation path through wrapper parsing, SQLite state, digest construction, CLI commands, dry-run validation, and an exercised live smoke path.
- Current gap: Existing duplicate rows already written during the pre-fix live rerun remain in the test Sheet; cleanup or reconciliation is still operator-directed work rather than a built-in command.
- Lesson so far: Both the dry-run path and the first live rerun surfaced real data-shape and identity issues that fixtures alone would not have revealed, so the repo benefits from preserving both validation layers.

## Context and Orientation

This repository separates stable contracts, active tasks, implementation modules, and runtime artifacts so a coding agent can navigate it without depending on prior conversation context. `docs/contracts/` holds stable behavior definitions. `packages/` holds implementation modules. `tests/` proves behavior. `runtime/` contains logs and local state, but it is not the primary source of truth.

The Google Workspace boundary is intentionally narrow. Rather than calling Gmail or Sheets from many locations, the implementation must route all such calls through `packages/google_workspace/`. This makes the system easier to test and easier for a future agent to reason about.

The runtime loop this plan expects is:

1. inspect code and contracts
2. implement one bounded milestone
3. run the most relevant tests
4. update this file
5. continue unless a human gate or external blocker is reached

## Plan of Work

### Milestone 1: Google boundary and preflight

Create `packages/google_workspace/` wrapper modules and a shared command execution helper. Implement:

- preflight authentication check
- Gmail search wrapper
- Gmail read wrapper
- Sheets write wrapper
- Gmail send wrapper

At the end of this milestone, the code should be able to parse deterministic command outputs and expose typed interfaces without yet running a real end-to-end job.

### Milestone 2: State and idempotency

Create SQLite-backed state tracking in `packages/state_store/`. The state layer must record processed message identifiers, job run metadata, and digest send status. At the end of this milestone, rerun semantics should be testable without touching live Gmail or Sheets.

### Milestone 3: Runner and CLI

Replace the CLI placeholders in `apps/cli/__main__.py` with real commands:

- `preflight`
- `run-once`
- `show-state`

The `run-once` path must support `--dry-run` and a local config file so a human can inspect intent before any side effects occur.

### Milestone 4: Tests

Add unit tests for parser and state logic, plus integration-style tests that use fixture outputs from `gws` commands. At the end of this milestone, the repository should have a trustworthy non-live verification path.

### Milestone 5: Live smoke

Run the documented preflight, choose a narrow test Gmail query, write to a test Google Sheet, and send a digest to a confirmed recipient. This is the first mandatory human gate. Stop after recording evidence and do not continue into broader live usage without explicit approval.

## Concrete Steps

Work from the repository root:

    uv sync
    uv run pytest tests/unit

Preflight before live operations:

    ./scripts/preflight.sh

Run the application in dry-run mode first:

    uv run python -m apps.cli run-once --config runtime/config.local.yaml --dry-run

Then run the real smoke path only after the human gate is cleared:

    ./scripts/run-smoke.sh

## Validation and Acceptance

Acceptance requires:

1. `uv run pytest tests/unit` passes
2. `uv run pytest tests/integration` passes once those tests exist
3. `uv run python -m apps.cli preflight` reports a usable environment
4. `uv run python -m apps.cli run-once --dry-run` shows intended work without side effects
5. the live smoke path finds a matching Gmail message, writes at least one row, sends a digest, and records state
6. rerunning the same live smoke path does not blindly duplicate work

## Human Validation Gates

Stop and wait for a human when:

1. a live Gmail write or send is about to happen for the first time
2. a live Google Sheet write is about to happen for the first time
3. a contract is missing and there are multiple valid product directions
4. authentication or permissions fail in a way the repository cannot self-correct

## Idempotence and Recovery

The local state store must record processed message identifiers and job run outcomes. If a run fails midway, the rerun path must either retry safely or explicitly mark the partial state so the operator can understand what happened.

Do not hide important recovery information in ephemeral agent context. If a milestone ends with a blocker or partial success, record it here under `Progress`, `Surprises & Discoveries`, and `Decision Log`.

## Artifacts and Notes

Important files:

    AGENTS.md
    README.md
    ARCHITECTURE.md
    PLANS.md
    docs/contracts/gmail-search.md
    docs/contracts/sheet-schema.md
    docs/contracts/digest-format.md
    docs/contracts/config-model.md
    packages/google_workspace/
    packages/state_store/
    apps/cli/
    tests/
    scripts/preflight.sh
    scripts/run-smoke.sh

## Interfaces and Dependencies

The repository should expose stable interfaces equivalent to:

    search_messages(query: str, max_results: int) -> list[MessageRef]
    read_message(message_id: str) -> MessagePacket
    write_rows(sheet_id: str, rows: list[RowPayload]) -> WriteResult
    build_digest(summary: RunSummary) -> DigestMessage
    send_digest(digest: DigestMessage) -> SendResult
    has_processed(message_id: str) -> bool
    mark_processed(message_id: str, run_id: str) -> None

Use a single implementation path first. Add abstractions only when the second implementation path is real.
