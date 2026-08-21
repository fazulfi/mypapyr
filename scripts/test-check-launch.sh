#!/bin/sh
set -eu

fail() {
    printf 'test-check-launch: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
GUARD="$ROOT/scripts/check-launch.sh"
[ -x "$GUARD" ] || fail "check-launch.sh absent or not executable: $GUARD"
FIXTURE=$(mktemp -d) || fail 'cannot create fixture'
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

printf '=== 1. green: guard exists and preflight can be invoked ===\n'
if ! PAPYR_LAUNCH_ROOT="$ROOT" sh "$GUARD" >/dev/null 2>&1; then
    fail 'guard rejected the repository baseline'
fi
printf 'PASS — baseline accepted\n'

printf '=== 2. mutation: placeholder fixture fails closed ===\n'
mkdir -p "$FIXTURE/deploy/nginx/conf.d" "$FIXTURE/frontend" "$FIXTURE/backend/app"
cp "$ROOT/deploy/docker-compose.yml" "$FIXTURE/deploy/docker-compose.yml"
cp "$ROOT/deploy/runbook-vps.md" "$FIXTURE/deploy/runbook-vps.md"
cp "$ROOT/deploy/nginx/conf.d/production.conf" "$FIXTURE/deploy/nginx/conf.d/production.conf"
printf '\nimage: example:__SET_ME__\n' >> "$FIXTURE/deploy/docker-compose.yml"
if PAPYR_LAUNCH_ROOT="$FIXTURE" sh "$GUARD" >/dev/null 2>&1; then
    fail 'guard accepted an unexpected __SET_ME__ fixture'
fi
printf 'PASS — placeholder mutation rejected\n'

printf '=== 3. mutation: wrong port mapping fails closed ===\n'
sed 's/3016/3999/g' "$ROOT/deploy/runbook-vps.md" > "$FIXTURE/deploy/runbook-vps.md"
if PAPYR_LAUNCH_ROOT="$FIXTURE" sh "$GUARD" >/dev/null 2>&1; then
    fail 'guard accepted a wrong port mapping fixture'
fi
printf 'PASS — port mutation rejected\n'

printf '=== 4. privacy: guard output contains no full digest or URL secret ===\n'
OUT=$(PAPYR_LAUNCH_ROOT="$ROOT" sh "$GUARD" 2>&1) || fail 'baseline guard failed during privacy check'
if printf '%s\n' "$OUT" | grep -Eiq 'signed|secret|password|token|[0-9a-f]{64}'; then
    fail 'guard output contains sensitive-looking material'
fi
printf 'PASS — output remains sanitized\n'
printf 'test-check-launch: PASS\n'
