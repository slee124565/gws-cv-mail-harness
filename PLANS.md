# This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

## Purpose / Big Picture

Build a local-first software system that can search Gmail, read messages, extract structured information, write results to Google Sheets, and send digest emails, while being maintainable by coding agents working from repository files and tests rather than hidden conversational context.

The user-visible proof is simple: a human can run a local command, observe new rows appear in a test Google Sheet, receive a digest email, and rerun the same command without duplicate processing.

## Progress

- [ ] Scaffold the root repository files and module directories.
- [ ] Define the Gmail, Sheets, digest, and config contracts in `docs/contracts/`.
- [ ] Implement Google Workspace wrappers in `packages/google_workspace/`.
- [ ] Implement local state and idempotency in `packages/state_store/`.
- [ ] Implement the end-to-end runner and CLI entrypoint.
- [ ] Add unit and integration tests.
- [ ] Run a human-approved live smoke validation.

## Surprises & Discoveries

- Observation: None yet.
  Evidence: Repository scaffold only.

## Decision Log

- Decision: Start CLI-first and postpone any local web UI.
  Rationale: CLI is the shortest path to proving the core workflow.
  Date/Author: YYYY-MM-DD / AUTHOR

## Outcomes & Retrospective

- Outcome: Not started.
- Gap: Not started.
- Lesson: Not started.

## Context and Orientation

This repository separates stable contracts, active tasks, implementation modules, and runtime artifacts so a coding agent can navigate it without depending on prior conversation context. `docs/contracts/` holds stable behavior definitions. `packages/` holds implementation modules. `tests/` proves behavior. `runtime/` contains logs and local state, but it is not the primary source of truth.

The Google Workspace boundary is intentionally narrow. Rather than calling Gmail or Sheets from many locations, the implementation must route all such calls through `packages/google_workspace/`. This makes the system easier to test and easier for a future agent to reason about.

## Plan of Work

First, create the repository scaffold and commit the root files, contract directories, and test directories. Do not begin with application code before the root navigation and contract files exist.

Second, define the core contracts in prose: Gmail search inputs and outputs, message read outputs, row writeback format, digest format, and config model. Keep these contracts stable and repository-relative so an agent can find them quickly.

Third, implement the deterministic Google Workspace wrappers. These wrappers should accept typed inputs, execute `gws`, parse the outputs, and return typed results or explicit errors.

Fourth, implement the local state store and idempotency rules. A rerun must distinguish new work from already-processed work.

Fifth, implement the runner and CLI so a human can invoke the end-to-end flow with a small test query.

Sixth, validate in three layers: unit, integration, and live smoke. Update this plan at every stopping point.

## Concrete Steps

Work from the repository root:

    uv sync
    uv run pytest tests/unit

Preflight before live operations:

    gws auth status

Run the application in dry-run mode first:

    uv run python -m apps.cli run-once --config runtime/config.local.yaml --dry-run

Then run the real smoke path:

    uv run python -m apps.cli run-once --config runtime/config.local.yaml

## Validation and Acceptance

Acceptance requires:

1. the CLI command completes successfully
2. a matching Gmail message is found
3. at least one structured row is produced
4. the target Sheet is updated
5. a digest email is sent
6. rerunning does not create duplicate work

## Idempotence and Recovery

The local state store must record processed message identifiers and job run outcomes. If a run fails midway, the rerun path must either retry safely or explicitly mark the partial state so the operator can understand what happened.

## Artifacts and Notes

Important files:

    AGENTS.md
    README.md
    ARCHITECTURE.md
    PLANS.md
    docs/contracts/
    packages/google_workspace/
    packages/state_store/
    apps/cli/
    tests/

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
