# Config Model Contract

This contract defines the minimum runtime configuration model.

## Sources

The first version may read configuration from:

- environment variables
- a local YAML file

## Required Fields

- Gmail query
- target Google Sheet id
- target sheet tab or range
- digest recipient
- max results
- dry-run default
- SQLite state database path

## Repository Rules

- A config file must be human-readable and safe to diff.
- Secrets must not be committed.
- The repository must include `.env.example` and a sample local config path convention.
- The concrete local config path is `runtime/config.local.yaml`, and that file must remain gitignored.

## First Implementation Keys

The v1 YAML keys are:

- `gmail_query`
- `sheet_id`
- `sheet_range`
- `digest_recipient`
- `max_results`
- `dry_run_default`
- `state_db_path`
- `digest_subject`

## First Live Version

The repository may use a single file such as `runtime/config.local.yaml`, but that file must remain gitignored.
