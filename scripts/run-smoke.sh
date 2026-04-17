#!/bin/bash

set -euo pipefail

echo "[smoke] running preflight first"
"$(dirname "$0")/preflight.sh"

echo "[smoke] dry-run before any live side effects"
uv run python -m apps.cli run-once --config runtime/config.local.yaml --dry-run

cat <<'EOF'
[smoke] Human gate reached.
Review the dry-run output, confirm the test Gmail query, test Sheet, and digest recipient,
then rerun the live command manually:

  uv run python -m apps.cli run-once --config runtime/config.local.yaml
EOF
