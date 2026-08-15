#!/bin/sh
#
# check-r2-lifecycle.sh — deterministic lifecycle gate (U-R2; ARC-06, PE-03).
#
# Verifies deploy/r2-lifecycle.json against the approved R2 lifecycle contract:
#   0 = exact match to approved policy (safe to apply)
#   1 = drift detected or secret-like material present (reject)
#   2 = artifact absent, malformed JSON, or invalid schema
#
# Uses system python3 + stdlib only (json module); no network access; no secrets.
# Wrangler apply contract documented by this gate's output and rendered via
# ``--print-apply-contract``. The application step itself stays manual/out-of-band:
#   wrangler r2 bucket lifecycle set <BUCKET_NAME> --file deploy/r2-lifecycle.json

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
PATH_LIFECYCLE="$ROOT/deploy/r2-lifecycle.json"
PYTHON=python3

[ -f "$PATH_LIFECYCLE" ] || { printf 'check-r2-lifecycle: FAIL — lifecycle absent: %s\n' "$PATH_LIFECYCLE"; exit 2; }

command -v "$PYTHON" >/dev/null 2>&1 || { printf 'check-r2-lifecycle: FAIL — python3 required\n'; exit 2; }
"$PYTHON" -c 'import json' >/dev/null 2>&1 || { printf 'check-r2-lifecycle: FAIL — json module unavailable\n'; exit 2; }

cd "$ROOT/backend" || exit 2

exec "$PYTHON" -m app.ops.r2_lifecycle --check "$PATH_LIFECYCLE"
