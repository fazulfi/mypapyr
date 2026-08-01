#!/bin/sh
#
# test-check-ci.sh — guard regression: an unpinned `uses:` reference must be
# rejected. Builds a temp fixture from the canonical workflow, injects
# `uses: actions/foo@v1` as a real step, runs the guard against the fixture,
# and asserts a non-zero exit. The canonical workflow is never modified.
# Catches regressions that would let the pin check false-pass again.

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WF_DIR="$ROOT/.github/workflows"
SCRIPTS="$ROOT/scripts"

fail() {
    printf 'test-check-ci: FAIL — %s\n' "$1" >&2
    exit 1
}

[ -f "$WF_DIR/ci.yml" ] || fail "canonical workflow absent: $WF_DIR/ci.yml"
[ -f "$SCRIPTS/check-ci.sh" ] || fail "guard absent: $SCRIPTS/check-ci.sh"
[ -f "$SCRIPTS/verify-pins.sh" ] || fail "pin verifier absent: $SCRIPTS/verify-pins.sh"

FIXTURE=$(mktemp -d) || fail "cannot create temp fixture"
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

mkdir -p "$FIXTURE/.github/workflows" "$FIXTURE/.github" "$FIXTURE/scripts"
cp "$WF_DIR/ci.yml" "$FIXTURE/.github/workflows/ci.yml"
cp "$SCRIPTS/check-ci.sh" "$SCRIPTS/verify-pins.sh" "$FIXTURE/scripts/"
if [ -f "$ROOT/.github/dependabot.yml" ]; then
    cp "$ROOT/.github/dependabot.yml" "$FIXTURE/.github/dependabot.yml"
fi

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"

"$PYTHON" - "$FIXTURE/.github/workflows/ci.yml" <<'PY'
import sys
p = sys.argv[1]
with open(p, encoding="utf-8") as fh:
    s = fh.read()
anchor = "      - uses: actions/checkout@"
if anchor not in s:
    raise SystemExit("fixture: checkout anchor not found")
s = s.replace(anchor, "      - uses: actions/foo@v1\n" + anchor, 1)
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(s)
PY

grep -q 'uses: actions/foo@v1' "$FIXTURE/.github/workflows/ci.yml" \
    || fail "mutation injection failed"
grep -q 'uses: actions/foo@v1' "$WF_DIR/ci.yml" \
    && fail "canonical workflow was modified"

if (cd "$FIXTURE" && sh scripts/check-ci.sh >/dev/null 2>&1); then
    fail "unpinned action was NOT rejected (guard exit 0)"
fi
if (cd "$FIXTURE" && sh scripts/verify-pins.sh >/dev/null 2>&1); then
    fail "unpinned action was NOT rejected by verify-pins (exit 0)"
fi

printf 'test-check-ci: PASS — unpinned action rejected by guard and verify-pins\n'
