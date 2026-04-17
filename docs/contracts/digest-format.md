# Digest Format Contract

This contract defines the first digest email format.

## Purpose

The digest gives a human quick proof of what the job did without opening logs or the Sheet immediately.

## Required Sections

- run timestamp
- query used
- counts:
  - matched messages
  - processed messages
  - skipped messages
  - failed messages
- a short itemized summary of processed rows
- a note describing whether this was a dry run or live run

## Repository Rules

- The digest must be buildable from recorded run summary data.
- The digest format should be stable enough for tests to validate key phrases.
- A rerun digest must make skipped or already-processed behavior visible.
