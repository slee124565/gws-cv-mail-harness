# State Store Contract

This contract defines the minimum durable state required for safe reruns.

## Purpose

The local state store is the source of truth for idempotency and recent run history.

## Required Records

- job runs:
  - run id
  - started and finished timestamps
  - dry-run flag
  - Gmail query used
  - matched, processed, skipped, and failed counts
  - final status
- processed messages:
  - message id
  - thread id when available
  - run id that first marked the message as processed
  - processed timestamp
- digest events:
  - run id
  - recipient
  - status
  - sent timestamp
  - message or draft id when available

## Repository Rules

- Durable state lives under `runtime/state/`.
- Dry runs record run metadata and digest preview status but must not mark messages as processed.
- Live sheet writes must mark messages as processed only after the write succeeds.
- Reruns must consult durable state before attempting another write for the same message id.
