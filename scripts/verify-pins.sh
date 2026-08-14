#!/bin/sh
#
# verify-pins.sh — verify every `uses:` occurrence in every
# workflow YAML file under .github/workflows/ must be a full-SHA pin carrying
# a `# vX.Y.Z` comment, and the tag must resolve to the pinned SHA via the
# GitHub API (lightweight refs direct; annotated tags peeled). This is the
# Pin shape is not pin truth. Unpinned or floating
# references (e.g. `uses: actions/foo@v1`) fail here — they are never skipped.
#
# Authenticated resolution: when GH_TOKEN / GITHUB_TOKEN is present the API is
# called authenticated (gh CLI inherits the token; curl sends an Authorization
# header). This avoids the unauthenticated rate limit (60 req/h) that turns a
# repeated canonical regression into HTTP 403. Each unique `repo@tag` is
# resolved at most ONCE per process via a file-backed cache, so the many
# references to the same action (e.g. actions/checkout in every job) do not
# re-hit the API. Genuine drift or an unresolvable tag still fails closed.
#
# Needs network access to api.github.com. Uses `gh` when available, else
# curl + python3. Exits non-zero on any mismatch, unresolved tag, unpinned
# reference, or missing tool.

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WF_DIR="$ROOT/.github/workflows"

fail() {
    printf 'verify-pins: FAIL — %s\n' "$1" >&2
    exit 1
}

[ -d "$WF_DIR" ] || fail "workflows dir absent: $WF_DIR"

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required for JSON parsing"
"$PYTHON" -c 'import json' >/dev/null 2>&1 || fail "python json module unavailable"

# Token inherited from the environment; never hardcoded. GH_TOKEN wins so the
# gh CLI and curl agree on which credential is in effect.
TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"

USE_GH=0
if command -v gh >/dev/null 2>&1 && \
   { [ -n "$TOKEN" ] || gh auth status >/dev/null 2>&1; }; then
    USE_GH=1
elif ! command -v curl >/dev/null 2>&1; then
    fail "neither an authenticated gh CLI nor curl is available"
fi

# File-backed per-process cache: one line per unique repo@tag -> sha. A file
# (not a shell variable) is required because resolve() runs in a command
# substitution subshell, where variable mutations would be discarded.
CACHE=$(mktemp 2>/dev/null) || CACHE="${TMPDIR:-/tmp}/verify-pins-cache.$$"
: > "$CACHE"
trap 'rm -f "$CACHE"' EXIT HUP INT TERM

# Retry tuning is bounded and overridable (tests set the delay to 0).
RETRY_MAX="${VERIFY_PINS_RETRY_MAX:-3}"
RETRY_DELAY="${VERIFY_PINS_RETRY_DELAY:-1}"

cache_get() {
    awk -v k="$1" '$1 == k { print $2; exit }' "$CACHE"
}

cache_put() {
    printf '%s %s\n' "$1" "$2" >> "$CACHE"
}

# api_get <path> — one authenticated GET against api.github.com, bounded retry.
api_get() {
    path=$1
    attempt=0
    while [ "$attempt" -lt "$RETRY_MAX" ]; do
        if [ "$USE_GH" -eq 1 ]; then
            if body=$(gh api "$path" 2>/dev/null); then
                printf '%s' "$body"
                return 0
            fi
        elif [ -n "$TOKEN" ]; then
            if body=$(curl -fsSL -H "Authorization: Bearer $TOKEN" \
                "https://api.github.com/$path" 2>/dev/null); then
                printf '%s' "$body"
                return 0
            fi
        else
            if body=$(curl -fsSL "https://api.github.com/$path" 2>/dev/null); then
                printf '%s' "$body"
                return 0
            fi
        fi
        attempt=$((attempt + 1))
        if [ "$attempt" -lt "$RETRY_MAX" ] && [ "$RETRY_DELAY" -gt 0 ]; then
            sleep "$RETRY_DELAY"
        fi
    done
    return 1
}

# resolve <owner/repo> <tag> -> commit sha (empty on failure), cached per key.
resolve() {
    repo=$1
    tag=$2
    key="$repo@$tag"

    cached=$(cache_get "$key")
    if [ -n "$cached" ]; then
        printf '%s\n' "$cached"
        return 0
    fi

    ref_json=$(api_get "repos/$repo/git/ref/tags/$tag") || return 1
    obj_type=$(printf '%s' "$ref_json" | "$PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["object"]["type"])') || return 1
    obj_sha=$(printf '%s' "$ref_json" | "$PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["object"]["sha"])') || return 1
    if [ "$obj_type" = "tag" ]; then
        tag_json=$(api_get "repos/$repo/git/tags/$obj_sha") || return 1
        commit_sha=$(printf '%s' "$tag_json" | "$PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["object"]["sha"])') || return 1
    else
        commit_sha=$obj_sha
    fi

    cache_put "$key" "$commit_sha"
    printf '%s\n' "$commit_sha"
}

WORKFLOW_FILES=$(find "$WF_DIR" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort || true)
[ -n "$WORKFLOW_FILES" ] || fail "no workflow files under $WF_DIR"

count=0
for WF in $WORKFLOW_FILES; do
    USES_LINES=$(grep -nE '^[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^[:space:]]+' "$WF" || true)
    [ -n "$USES_LINES" ] || fail "no actions found in $WF"

    while IFS= read -r line; do
        repo=$(printf '%s' "$line" | sed -nE 's/.*uses:[[:space:]]*([^@[:space:]]+)@[0-9a-f]{40}.*/\1/p')
        sha=$(printf '%s' "$line" | sed -nE 's/.*@([0-9a-f]{40}).*/\1/p')
        ver=$(printf '%s' "$line" | sed -nE 's/.*#[[:space:]]*v([0-9][^[:space:]]*).*/\1/p')
        if [ -z "$repo" ] || [ -z "$sha" ]; then
            fail "unpinned or malformed uses reference in $WF: $line"
        fi
        if [ -z "$ver" ]; then
            fail "SHA pin without '# vX.Y.Z' comment in $WF: $line"
        fi
        resolved=$(resolve "$repo" "v$ver") || fail "cannot resolve $repo tag v$ver (from $WF)"
        if [ "$resolved" = "$sha" ]; then
            printf 'verify-pins: OK   %s @ v%s -> %s\n' "$repo" "$ver" "$resolved"
        else
            fail "$repo @ v$ver -> $resolved (workflow pins $sha) in $WF"
        fi
        count=$((count + 1))
    done <<EOF
$USES_LINES
EOF
done

printf 'verify-pins: PASS (%s pins match their tags)\n' "$count"
