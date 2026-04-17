# Live Smoke Validation

This document defines the human-operated validation checklist for Milestone 5.

The purpose of this checklist is to safely approve the first real Google Sheets write and the first real digest email send.

## When To Use

Use this checklist only after:

- `PLANS.md` shows the repository is at the Milestone 5 human gate
- the dry-run path has already completed successfully
- the operator is ready to approve the first live write and send

## Preconditions

Before running the live smoke:

- [x] You are in the repository root: `~/ws/gws-cv-mail-harness`
- [x] `PLANS.md` still indicates that live smoke is the current next step
- [x] `runtime/config.local.yaml` exists
- [x] the Gmail query in `runtime/config.local.yaml` is intentionally narrow
- [x] the target Google Sheet is a test sheet or a dedicated test tab
- [x] the digest recipient is confirmed and safe for test mail

## Preflight

Run:

    ./scripts/preflight.sh

Confirm:

- [x] `gws auth status` reports the expected account
- [x] Python environment sync completes
- [x] unit tests pass

If any of the above fail, stop. Do not continue to live smoke.

## Dry-Run Review

Run:

    uv run python -m apps.cli run-once --config runtime/config.local.yaml --dry-run

Review:

- [x] the command completes successfully
- [x] the reported Gmail query matches the intended test query
- [x] matched message count looks reasonable
- [x] the preview rows look like expected sheet data
- [x] the digest preview looks correct
- [x] the dry run does not claim to have written to Sheets or sent a digest

If the dry run output is surprising, stop and correct the config or code first.

## Live Run Approval Gate

Proceed only if all statements are true:

- [x] I approve the first real Google Sheet write for this test target
- [x] I approve the first real digest email send for this test target
- [x] I understand that this step will produce real side effects

## Live Run

Run:

    uv run python -m apps.cli run-once --config runtime/config.local.yaml

Confirm:

- [x] the command exits successfully
- [x] the target Google Sheet shows at least one new row or expected write result
- [x] the digest email is received by the confirmed test recipient
- [x] the CLI or logs indicate that run state was recorded

## Rerun Check

Run the exact same live command again:

    uv run python -m apps.cli run-once --config runtime/config.local.yaml

Confirm:

- [x] the rerun does not blindly duplicate the previous work
- [x] already-processed or skipped behavior is visible in output or digest
- [x] state remains internally consistent

## Failure Handling

If the live run fails:

- [ ] capture the exact command
- [ ] capture the terminal output
- [ ] check `runtime/` logs and state
- [ ] update `PLANS.md` with the failure and observed blocker
- [ ] do not improvise destructive recovery steps without documenting them

## Evidence To Record

After the smoke run, record:

- [ ] command used
- [ ] target test Gmail query
- [ ] target test Sheet or tab
- [ ] digest recipient used
- [ ] whether the first run succeeded
- [ ] whether the rerun avoided duplicate work
- [ ] any unexpected output or data-shape behavior

This evidence should be written back to `PLANS.md` and any other relevant task log.
