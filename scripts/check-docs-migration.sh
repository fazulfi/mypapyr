#!/usr/bin/env bash
# Governed-record baseline verification per DEC-006, DEC-026, DEC-198:
# decision log, every DEC-001..DEC-202 ID, both specs, baseline record.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILURES=0

report_fail() {
  echo "FAIL: $1"
  FAILURES=$((FAILURES + 1))
}

if [ ! -f "$ROOT/papyr-rebuild-decisions.md" ]; then
  report_fail "papyr-rebuild-decisions.md is absent"
fi

if [ -f "$ROOT/papyr-rebuild-decisions.md" ]; then
  # Decimal iteration: `seq -w` zero-pads and printf '%d' would parse values
  # such as 008/009 as octal, corrupting IDs (see pr-02-execution-record.md).
  for i in $(seq 1 202); do
    id=$(printf 'DEC-%03d' "$i")
    if ! grep -q "^## ${id} " "$ROOT/papyr-rebuild-decisions.md"; then
      report_fail "decision log lacks ${id}"
    fi
  done
fi

if [ ! -f "$ROOT/docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md" ]; then
  report_fail "Product/UX specification is absent"
fi
if [ ! -f "$ROOT/docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md" ]; then
  report_fail "Technical Architecture specification is absent"
fi

if [ ! -f "$ROOT/docs/canonical-docs-baseline.md" ]; then
  report_fail "docs/canonical-docs-baseline.md is absent"
fi

if [ "$FAILURES" -ne 0 ]; then
  echo "check-docs-migration: FAIL ($FAILURES issue(s))"
  exit 1
fi

echo "check-docs-migration: PASS"
exit 0
