#!/bin/sh

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WF="$ROOT/.github/workflows/ci.yml"

fail() {
    printf 'check-ci: FAIL — %s\n' "$1" >&2
    exit 1
}

[ -f "$WF" ] || fail "workflow absent: $WF"

if grep -q "$(printf '\r')" "$WF"; then
    fail "workflow contains CRLF line endings"
fi

STRIPPED=$(sed -e 's/[[:space:]]*#.*$//' "$WF")
FORBIDDEN_KEYWORDS='deploy|publish|scp|ssh|rsync|registry-push|ftp|kubectl|helm|aws|gcloud|azure|doctl'
MATCH=$(printf '%s\n' "$STRIPPED" | grep -nE -i "($FORBIDDEN_KEYWORDS)" || true)
[ -z "$MATCH" ] || fail "forbidden deployment keyword detected"

if grep -qE '^[[:space:]]*pull_request_target[[:space:]]*:' "$WF"; then
    fail "pull_request_target trigger present"
fi

if grep -qE '^[[:space:]]*secrets[[:space:]]*:' "$WF"; then
    fail "secrets mapping present"
fi

if grep -qE '\$\{\{[[:space:]]*secrets\.' "$WF"; then
    fail "secrets interpolation present"
fi

USES_LINES=$(grep -nE '^[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^[:space:]]+' "$WF" || true)
[ -n "$USES_LINES" ] || fail "no actions found"

BAD_USES=$(printf '%s\n' "$USES_LINES" \
    | grep -vE '^[[:digit:]]+:[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^@[:space:]]+@[0-9a-f]{40}([[:space:]]|$)' \
    || true)
[ -z "$BAD_USES" ] || fail "an action is not pinned to a full commit SHA"

printf 'check-ci: PASS\n'
