#!/bin/bash

set -euo pipefail

echo "[preflight] checking Google Workspace authentication"
gws auth status

echo "[preflight] checking Python project setup"
uv sync

echo "[preflight] running unit tests"
uv run pytest tests/unit
