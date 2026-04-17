# Sheet Schema Contract

This contract defines the minimum Google Sheet writeback shape for the first live version.

## Purpose

The Sheet is the human-visible record of processed work. It must be predictable enough that a coding agent can write to it without guessing column meaning.

## Minimum Row Fields

The first version should support at least:

- `message_id`
- `thread_id`
- `received_at`
- `subject`
- `sender`
- `summary`
- `status`
- `processed_at`

## Repository Rules

- Column order must be documented before the first live write.
- The write layer must support either append-only writes or explicit range updates, but the chosen mode must be consistent.
- The sheet contract must remain stable across dry-run, tests, and live smoke.

## First Live Version

If the target Sheet already exists, writeback should target a dedicated test tab rather than a production tab for the first smoke run.
