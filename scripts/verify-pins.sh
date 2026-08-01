#!/bin/sh
#
# verify-pins.sh — verify every `uses:` occurrence in every
# workflow YAML file under .github/workflows/ must be a full-SHA pin carrying
# a `# vX.Y.Z` comment, and the tag must resolve to the pinned SHA via the
# GitHub API (lightweight refs direct; annotated tags peeled). This is the
# Pin shape is not pin truth. Unpinned or floating
# references (e.g. `uses: actions/foo@v1`) fail here — they are never skipped.
#
# Needs network access to api.github.com. Uses `gh` when available (CI: the
# automatic GITHUB_TOKEN satisfies authentication), else curl + python3.
# Exits non-zero on any mismatch, unresolved tag, unpinned reference, or
# missing tool.

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

USE_GH=0
if command -v gh >/dev/null 2>&1 && \
   { [ -n "${GH_TOKEN:-}" ] || [ -n "${GITHUB_TOKEN:-}" ] || gh auth status >/dev/null 2>&1; }; then
    USE_GH=1
elif ! command -v curl >/dev/null 2>&1; then
    fail "neither an authenticated gh CLI nor curl is available"
fi

# resolve <owner/repo> <tag> -> commit sha (empty on failure)
resolve() {
    repo=$1
    tag=$2
    if [ "$USE_GH" -eq 1 ]; then
        ref_json=$(gh api "repos/$repo/git/ref/tags/$tag" 2>/dev/null) || return 1
    else
        ref_json=$(curl -fsSL "https://api.github.com/repos/$repo/git/ref/tags/$tag") || return 1
    fi
    obj_type=$(printf '%s' "$ref_json" | "$PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["object"]["type"])') || return 1
    obj_sha=$(printf '%s' "$ref_json" | "$PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["object"]["sha"])') || return 1
    if [ "$obj_type" = "tag" ]; then
        if [ "$USE_GH" -eq 1 ]; then
            tag_json=$(gh api "repos/$repo/git/tags/$obj_sha" 2>/dev/null) || return 1
        else
            tag_json=$(curl -fsSL "https://api.github.com/repos/$repo/git/tags/$obj_sha") || return 1
        fi
        printf '%s' "$tag_json" | "$PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["object"]["sha"])' || return 1
    else
        printf '%s\n' "$obj_sha"
    fi
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
