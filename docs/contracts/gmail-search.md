# Gmail Search Contract

This contract defines the stable meaning of Gmail search inside this repository.

## Purpose

The Gmail search step identifies candidate messages for processing before any message body is read or any side effect occurs.

## Inputs

- `query`
  Gmail search expression
- `max_results`
  upper bound on returned messages
- optional `date_from`
- optional `date_to`

## Output Shape

Each result must provide:

- `message_id`
- `thread_id`
- `internal_date` or received timestamp
- `subject` when available
- minimal snippet or summary metadata when available

## Repository Rules

- Search must be read-only.
- Search results alone must not mark a message as processed.
- The wrapper should preserve enough metadata for dry-run output and logging.

## First Live Version

The first live version may support only a single query string and `max_results`, as long as the date range can be expressed inside the query itself.
