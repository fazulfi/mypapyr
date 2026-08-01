#!/bin/sh
#
# check-ci.sh — deterministic CI-without-CD and workflow-integrity guard.
# Exits non-zero on the first failure.
#   a  workflow file exists                 (b/h)  no CD keywords after comment strip
#   c  no pull_request_target               j      no workflow_run
#   d  no secrets mapping/interpolation     e      EVERY uses: is a full-SHA pin
#   f  only ci.yml under .github/workflows  g      dependabot.yml present + valid
#   i  no write scope anywhere              k      every checkout credential-free
#   l  workflow YAML parses (pyyaml)        m      every SHA pin carries `# vX.Y.Z`
#   n  pin truth (scripts/verify-pins.sh)   —      (needs network to api.github.com)
#
# Check (e) enumerates every `uses:` occurrence in every workflow YAML file
# under .github/workflows/ — not just lines that already look pinned — so an
# unpinned or floating reference (e.g. `uses: actions/foo@v1`) fails the gate
# instead of being silently skipped by the collection regex.

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WF_DIR="$ROOT/.github/workflows"
DEPENDABOT="$ROOT/.github/dependabot.yml"

fail() {
    printf 'check-ci: FAIL — %s\n' "$1" >&2
    exit 1
}

WORKFLOW_FILES=$(find "$WF_DIR" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort || true)
[ -n "$WORKFLOW_FILES" ] || fail "no workflow files under $WF_DIR"

for WF in $WORKFLOW_FILES; do
    # (a) workflow file exists
    [ -f "$WF" ] || fail "workflow absent: $WF"

    if grep -q "$(printf '\r')" "$WF"; then
        fail "workflow contains CRLF line endings: $WF"
    fi

    STRIPPED=$(sed -e 's/[[:space:]]*#.*$//' "$WF")

    # (b)+(h) forbidden deployment/supply-chain keywords after comment strip
    FORBIDDEN_KEYWORDS='deploy|publish|scp|ssh|rsync|registry-push|ftp|kubectl|helm|aws|gcloud|azure|doctl|vercel|netlify|heroku|firebase|fly\.io|render|wrangler|cloudflared|ghcr|docker[[:space:]]+login|docker[[:space:]]+push|docker[[:space:]]+buildx|workflow_dispatch|environments:|id-token:|registry'
    MATCH=$(printf '%s\n' "$STRIPPED" | grep -nE -i "($FORBIDDEN_KEYWORDS)" || true)
    [ -z "$MATCH" ] || fail "forbidden deployment keyword detected in $WF"

    # (c)+(j) privileged triggers
    if grep -qE '^[[:space:]]*pull_request_target[[:space:]]*:' "$WF"; then
        fail "pull_request_target trigger present in $WF"
    fi
    if grep -qE '^[[:space:]]*workflow_run[[:space:]]*:' "$WF"; then
        fail "workflow_run trigger present in $WF"
    fi

    # (d) secrets
    if grep -qE '^[[:space:]]*secrets[[:space:]]*:' "$WF"; then
        fail "secrets mapping present in $WF"
    fi
    if grep -qE '\$\{\{[[:space:]]*secrets\.' "$WF"; then
        fail "secrets interpolation present in $WF"
    fi

    # (i) no write scope (no `key: write` / `permissions: write-all`)
    WRITE_SCOPE=$(grep -nE '^[[:space:]]*[a-zA-Z_-]+:[[:space:]]*(write|write-all)([[:space:]]|$)' "$WF" || true)
    [ -z "$WRITE_SCOPE" ] || fail "write scope present in $WF: $WRITE_SCOPE"

    # (e) every uses: occurrence must be a full 40-hex SHA pin. Collect ALL
    # uses: lines (any reference), then reject any that is not SHA-pinned.
    FILE_USES=$(grep -nE '^[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^[:space:]]+' "$WF" || true)
    [ -n "$FILE_USES" ] || fail "no actions found in $WF"

    BAD_USES=$(printf '%s\n' "$FILE_USES" \
        | grep -vE '^[[:digit:]]+:[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^@[:space:]]+@[0-9a-f]{40}([[:space:]]|$)' \
        || true)
    [ -z "$BAD_USES" ] || fail "an action is not pinned to a full commit SHA in $WF: $BAD_USES"

    # (m) every SHA pin carries a `# vX.Y.Z` comment (Dependabot requirement)
    BAD_COMMENT=$(printf '%s\n' "$FILE_USES" | grep -vE '@[0-9a-f]{40}[[:space:]]+#[[:space:]]*v[0-9]' || true)
    [ -z "$BAD_COMMENT" ] || fail "a SHA pin lacks its '# vX.Y.Z' comment in $WF: $BAD_COMMENT"

    # (k) every checkout is credential-free
    CHECKOUT_VIOLATION=$(awk '
      /- *uses: *actions\/checkout/ { pending=1; found=0; next }
      pending {
        if ($0 ~ /persist-credentials: *false/) found=1
        if ($0 ~ /^[[:space:]]*-[[:space:]]*uses:/) {
          if (!found) print "line " NR
          pending=0
        }
      }
      END { if (pending && !found) print "end of file" }
    ' "$WF")
    [ -z "$CHECKOUT_VIOLATION" ] || fail "checkout without persist-credentials: false in $WF ($CHECKOUT_VIOLATION)"

    PYTHON=python3
    command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
    command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"
    "$PYTHON" -c 'import yaml' >/dev/null 2>&1 || fail "pyyaml required (python3 -m pip install pyyaml)"

    # (l) workflow YAML parses
    "$PYTHON" -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1], encoding="utf-8"))' "$WF" \
        || fail "workflow YAML does not parse: $WF"
done

# (f) only ci.yml may exist under .github/workflows
EXTRA_WF=$(printf '%s\n' "$WORKFLOW_FILES" | grep -v '/ci\.yml$' || true)
[ -z "$EXTRA_WF" ] || fail "unexpected workflow file(s): $EXTRA_WF"

# (g) dependabot config present, parses, and covers the repo ecosystems
[ -f "$DEPENDABOT" ] || fail "dependabot config absent: $DEPENDABOT"
"$PYTHON" -c '
import sys, yaml
with open(sys.argv[1], encoding="utf-8") as fh:
    cfg = yaml.safe_load(fh)
pairs = [(u.get("package-ecosystem"), u.get("directory")) for u in cfg.get("updates", [])]
required = [("github-actions", "/"), ("npm", "/frontend"), ("npm", "/qa-tools"), ("pip", "/backend")]
missing = ["%s@%s" % (e, d) for e, d in required if (e, d) not in pairs]
if missing:
    print("missing dependabot entries: " + ", ".join(missing), file=sys.stderr)
    sys.exit(1)
' "$DEPENDABOT" || fail "dependabot config invalid"

# (n) pin truth (network to api.github.com required)
"$ROOT/scripts/verify-pins.sh" || fail "pin truth verification failed"

printf 'check-ci: PASS\n'
