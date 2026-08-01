#!/bin/sh
# scripts/check-ci.sh — Papyr Phase 0 CI guard (DEC-160, DEC-177).
# Enforces: (a) ci.yml exists; (b) no deploy/CD keywords; (c) no pull_request_target;
# (d) no secrets: mapping / ${{ secrets.* }} except explicit GITHUB_TOKEN;
# (e) every uses: line SHA-pinned (40-hex). Exit 0 on PASS, non-zero on first violation.

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WF="$ROOT/.github/workflows/ci.yml"

fail() {
    printf 'check-ci: FAIL — %s\n' "$1" >&2
    exit 1
}

# (a) workflow file must exist
if [ ! -f "$WF" ]; then
    fail "workflow absent: $WF does not exist"
fi

if grep -q $'\r' "$WF"; then
    fail "workflow contains CRLF line endings (use LF)"
fi

# (b) forbidden CD/deploy keywords. Strip YAML comments first to avoid noise.
STRIPPED=$(sed -e 's/[[:space:]]*#.*$//' "$WF")
FORBIDDEN_KEYWORDS='deploy|publish|scp|ssh|rsync|registry-push|ftp|kubectl|helm|aws|gcloud|azure|doctl'
MATCH=$(printf '%s\n' "$STRIPPED" | grep -nE -i "($FORBIDDEN_KEYWORDS)" || true)
if [ -n "$MATCH" ]; then
    printf 'check-ci: FAIL — forbidden CD/deploy keyword(s) detected:\n%s\n' "$MATCH" >&2
    printf 'check-ci: hint — CI must not deploy, publish, push images, or reach a registry.\n' >&2
    exit 2
fi

# (c) no pull_request_target
if grep -qE '^[[:space:]]*pull_request_target[[:space:]]*:' "$WF"; then
    fail "pull_request_target trigger present (forbidden — use 'pull_request')"
fi

# (d) no secrets: mapping except explicit GITHUB_TOKEN; no ${{ secrets.* }} except GITHUB_TOKEN
if grep -qE '^[[:space:]]*secrets[[:space:]]*:[[:space:]]*[^[:space:]]+' "$WF"; then
    SECRETS_LINE=$(grep -nE '^[[:space:]]*secrets[[:space:]]*:[[:space:]]*[^[:space:]]+' "$WF" || true)
    if printf '%s\n' "$SECRETS_LINE" | grep -vqE '^[[:digit:]]+:[[:space:]]*secrets[[:space:]]*:[[:space:]]*GITHUB_TOKEN[[:space:]]*$'; then
        printf 'check-ci: FAIL — non-GITHUB_TOKEN secrets: mapping detected:\n%s\n' "$SECRETS_LINE" >&2
        exit 3
    fi
fi
if grep -qE '\$\{\{[[:space:]]*secrets\.' "$WF"; then
    SECRET_REFS=$(grep -nE '\$\{\{[[:space:]]*secrets\.' "$WF" || true)
    if printf '%s\n' "$SECRET_REFS" | grep -vqE '\$\{\{[[:space:]]*secrets\.GITHUB_TOKEN[[:space:]]*\}\}'; then
        printf 'check-ci: FAIL — non-GITHUB_TOKEN secrets.* interpolation detected:\n%s\n' "$SECRET_REFS" >&2
        exit 4
    fi
fi

# (e) every uses: must be SHA-pinned (40-hex after @)
USES_LINES=$(grep -nE '^[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^[:space:]]+' "$WF" || true)
if [ -z "$USES_LINES" ]; then
    fail "no 'uses:' lines found — workflow is not invoking any actions"
fi

BAD_USES=$(printf '%s\n' "$USES_LINES" \
    | grep -vE '^[[:digit:]]+:[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^@[:space:]]+@[0-9a-f]{40}([[:space:]]|$)' \
    || true)
if [ -n "$BAD_USES" ]; then
    printf 'check-ci: FAIL — uses: lines missing SHA pin (40-hex required):\n%s\n' "$BAD_USES" >&2
    exit 5
fi

printf 'check-ci: PASS\n'
exit 0