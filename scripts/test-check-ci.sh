#!/bin/sh
#
# test-check-ci.sh — guard regression: an unpinned `uses:` reference and a
# missing production-image contract must be rejected. Builds temp fixtures
# from the canonical workflow, injects `uses: actions/foo@v1` as a real step
# and removes the qa-production-api job in turn, runs the guard against each
# fixture, and asserts non-zero exits. The canonical workflow is never modified.

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

"$PYTHON" - "$FIXTURE/.github/workflows/ci.yml" <<'PY'
import sys
p = sys.argv[1]
with open(p, encoding="utf-8") as fh:
    s = fh.read()
start = s.find("  qa-production-api:\n")
if start < 0:
    raise SystemExit("fixture: qa-production-api anchor not found")
end = s.find("\n  qa-", start + 1)
if end < 0:
    raise SystemExit("fixture: qa-production-api end anchor not found")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(s[:start] + s[end + 1:])
PY

if (cd "$FIXTURE" && sh scripts/check-ci.sh >/dev/null 2>&1); then
    fail "missing production-image job was NOT rejected (guard exit 0)"
fi

# ----- runtime contract regressions ---------------------------------------
# The prior removal test erased qa-production-api above; restore the canonical
# workflow before injecting the runtime-defect fixtures.
cp "$WF_DIR/ci.yml" "$FIXTURE/.github/workflows/ci.yml"

grep -q 'Non-root health' "$FIXTURE/.github/workflows/ci.yml" \
    || fail "fixture: production smoke step absent after restore"
grep -q 'Compose config gate' "$FIXTURE/.github/workflows/ci.yml" \
    || fail "fixture: compose config step absent after restore"

# Inject the two known runtime defects:
#   (A) the smoke `docker run ... papyr-api:ci sh -c 'probe'` — the trailing
#       command REPLACES the image CMD (uvicorn), so the API never starts;
#   (B) PAPYR_API_IMAGE / PAPYR_ENV_FILE are placed AFTER `config --quiet`,
#       making them positional arguments that never reach Compose.
"$PYTHON" - "$FIXTURE/.github/workflows/ci.yml" <<'PY'
import re
import sys

p = sys.argv[1]
with open(p, encoding="utf-8") as fh:
    s = fh.read()


def replace_step(s: str, name: str, body: str) -> str:
    """Replace the `run: |` body of the step whose `- name:` equals `name`."""
    idx = s.find("- name: " + name)
    if idx < 0:
        raise SystemExit("fixture: step not found: " + name)
    run_idx = s.find("run: |", idx)
    if run_idx < 0:
        raise SystemExit("fixture: run: | not found in step: " + name)
    body_start = s.find("\n", run_idx) + 1
    nxt = s.find("\n      - name:", body_start)
    if nxt < 0:
        m = re.search(r"\n[ ]+[A-Za-z_]", s[body_start:])
        nxt = (body_start + m.start()) if m else len(s)
    else:
        nxt = nxt + 1
    return s[:run_idx] + "run: |\n" + body + s[nxt:]


broken_smoke = r'''          set -euo pipefail
          docker run \
            --rm \
            --user 1001:1001 \
            --cap-drop ALL \
            --read-only \
            --tmpfs /tmp:exec,mode=1777,size=64M \
            --tmpfs /opt/papyr/temp:exec,mode=1777,size=64M \
            --tmpfs /home/appuser/.cache:size=64M \
            -e R2_ACCOUNT_ID=test \
            -e R2_ACCESS_KEY_ID=test \
            -e R2_SECRET_ACCESS_KEY=test \
            -e R2_BUCKET_NAME=test \
            -e ALLOWED_ORIGINS=http://localhost:3000 \
            --name papyr-api-smoke \
            papyr-api:ci \
            sh -c 'test "$(id -u)" = "1001" && python -c "import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:3000/health\", timeout=10)"'
'''

broken_compose = r'''          set -euo pipefail
          docker compose \
            --project-directory "$PAPYR_COMPOSE_DIR" \
            -f "$PAPYR_COMPOSE_DIR/docker-compose.yml" \
            config --quiet \
            PAPYR_API_IMAGE=papyr-api@sha256:0000000000000000000000000000000000000000000000000000000000000000 \
            PAPYR_ENV_FILE="$PAPYR_COMPOSE_DIR/.env.test"
'''

s = replace_step(
    s,
    "Non-root health smoke (cap_drop ALL, read-only rootfs)",
    broken_smoke,
)
s = replace_step(
    s,
    "Compose config gate with non-secret fixtures (digest-form image)",
    broken_compose,
)

with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(s)
PY

if (cd "$FIXTURE" && sh scripts/check-ci.sh >/dev/null 2>&1); then
    fail "CMD-overriding smoke and/or post-subcommand compose env were NOT rejected (guard exit 0)"
fi

# ----- repo-level fixture contract -----------------------------------------
# deploy/.env.test is the non-secret Compose fixture. It must be present,
# must be visible to git (the narrow .gitignore exception, not `.env.*`), and
# must never carry secret-shaped values.
DEPLOY_ENV_TEST="$ROOT/deploy/.env.test"
[ -f "$DEPLOY_ENV_TEST" ] || fail "deploy/.env.test fixture absent"
if (cd "$ROOT" && GIT_MASTER=1 git check-ignore -q deploy/.env.test); then
    fail "deploy/.env.test is STILL git-ignored; add the narrow .gitignore exception"
fi
ENV_SECRETS=$(grep -nE \
    'AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=|sk-[A-Za-z0-9]{20,}|-----BEGIN[[:space:]]+' \
    "$DEPLOY_ENV_TEST" || true)
[ -z "$ENV_SECRETS" ] \
    || fail "deploy/.env.test contains secret-shaped material: $ENV_SECRETS"

# ----- RED: PAPYR_COMPOSE_DIR must be a GitHub-evaluated path ------------
# Final blocker regression: the job env previously carried a literal
# `$(printf ...)` shell fragment that GitHub Actions never evaluates, so the
# Compose gate resolved a nonexistent directory on a real runner. The guard
# must reject ANY `$(`-style fragment in a job env value and require the
# canonical `${{ github.workspace }}/deploy` path for qa-production-api.
cp "$WF_DIR/ci.yml" "$FIXTURE/.github/workflows/ci.yml"
"$PYTHON" - "$FIXTURE/.github/workflows/ci.yml" <<'PY'
import re
import sys

p = sys.argv[1]
with open(p, encoding="utf-8") as fh:
    s = fh.read()
# inject a shell COMMAND STRING unique to this harness so the canonical-file
# guard below can tell the two apart even before the canonical workflow is fixed
s, n = re.subn(
    r'(PAPYR_COMPOSE_DIR: )"[^"\n]*"',
    r'\1"${{ github.workspace }}/$(echo obfuscaded)"',
    s,
    count=1,
)
if n != 1:
    raise SystemExit("fixture: PAPYR_COMPOSE_DIR env line not found (canonical env contract changed)")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(s)
PY

grep -q '$(echo obfuscaded' "$FIXTURE/.github/workflows/ci.yml" \
    || fail "fixture: expected fragment injection failed"
grep -q '$(echo obfuscaded' "$WF_DIR/ci.yml" \
    && fail "canonical workflow was modified"

if (cd "$FIXTURE" && sh scripts/check-ci.sh >/dev/null 2>&1); then
    fail "job env shell fragment (\$(echo ...)) was NOT rejected (guard exit 0)"
fi

# ----- positive regression ------------------------------------------------
# With the defects fixed, the canonical workflow must pass the full guard
# (including pin truth) so the fixed workflow is proven to pass, not just the
# broken mutations to fail.
cp "$WF_DIR/ci.yml" "$FIXTURE/.github/workflows/ci.yml"
if ! OUT=$(cd "$FIXTURE" && sh scripts/check-ci.sh 2>&1); then
    printf '%s\n' "$OUT" >&2
    fail "canonical (fixed) workflow was rejected by check-ci (must pass)"
fi

printf 'test-check-ci: PASS — unpinned action, missing job, CMD-override / compose-env contract, and .env.test fixture verified\n'
