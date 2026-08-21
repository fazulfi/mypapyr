#!/bin/sh
# check-launch.sh — Phase 10 VL-05 pre-launch, smoke, and rollback-readiness gate.
# Read-only: it never changes deployment state, connects by SSH, or prints secrets.

set -eu

fail() {
    printf 'check-launch: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=${PAPYR_LAUNCH_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}
COMPOSE="$ROOT/deploy/docker-compose.yml"
PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python

redact_ref() {
    case "$1" in
        *@sha256:*) printf '%s@sha256:<redacted>\n' "${1%%@sha256:*}" ;;
        *) printf '<unset-or-nondigest>\n' ;;
    esac
}

require_path() { [ -e "$ROOT/$1" ] || fail "required path absent: $1"; }

compose_preflight() {
    tmp=${TMPDIR:-/tmp}/papyr-launch-env-$$
    trap 'rm -f "$tmp"' EXIT HUP INT TERM
    : > "$tmp"
    PAPYR_ENV_FILE="$tmp" \
    PAPYR_API_IMAGE='registry.example/papyr-api@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
    PAPYR_WORKERS_IMAGE='registry.example/papyr-workers@sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' \
    PAPYR_CLAMD_IMAGE='registry.example/clamav@sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc' \
    docker compose -f "$COMPOSE" config --quiet >/dev/null 2>&1 \
        || fail 'docker compose config --quiet failed with digest-form preflight values'
    rm -f "$tmp"
    trap - EXIT HUP INT TERM
}

preflight() {
    printf '=== 1. repository layout ===\n'
    require_path frontend
    require_path backend/app
    require_path deploy/docker-compose.yml
    require_path deploy/runbook-vps.md
    printf 'PASS — required layout present\n'

    printf '=== 2. compose configuration and image contract ===\n'
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        compose_preflight
        printf 'PASS — docker compose config accepted; injected image refs are digest-form (values withheld)\n'
    else
        command -v "$PYTHON" >/dev/null 2>&1 || fail 'python3/python is required for offline compose validation'
        "$PYTHON" - "$COMPOSE" <<'PY' || fail 'compose YAML is not structurally readable'
import sys
from pathlib import Path
import yaml
value = yaml.safe_load(Path(sys.argv[1]).read_text(encoding='utf-8'))
if not isinstance(value, dict) or not isinstance(value.get('services'), dict):
    raise SystemExit(1)
PY
        grep -q 'PAPYR_API_IMAGE' "$COMPOSE" || fail 'API image contract is absent'
        grep -q 'PAPYR_WORKERS_IMAGE' "$COMPOSE" || fail 'worker image contract is absent'
        grep -q 'PAPYR_CLAMD_IMAGE' "$COMPOSE" || fail 'ClamAV image contract is absent'
        printf 'PASS — Docker unavailable; compose YAML and digest injection contracts validated offline\n'
    fi

    printf '=== 3. deployment placeholders and environment paths ===\n'
    # The public compose/nginx skeleton intentionally retains its documented edge
    # slot placeholder. Any additional marker is an accidental release leak.
    if "$PYTHON" - "$ROOT" <<'PY'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
allowed = {
    "deploy/docker-compose.yml": {"nginx:__SET_ME__"},
    "deploy/nginx/conf.d/production.conf": {"__SET_ME__"},
    "deploy/runbook-vps.md": {"__SET_ME__"},
}
for path in root.joinpath("deploy").rglob("*"):
    if not path.is_file() or path.name == ".env.production.example":
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if "__SET_ME__" not in text:
        continue
    permitted = allowed.get(path.relative_to(root).as_posix(), set())
    for line in text.splitlines():
        if "__SET_ME__" in line and not any(marker in line for marker in permitted):
            print(path.relative_to(root), file=sys.stderr)
            raise SystemExit(1)
raise SystemExit(0)
PY
    then :; else fail 'unexpected __SET_ME__ placeholder in deploy templates'; fi
    if "$PYTHON" - "$ROOT" <<'PY'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
for base in (root / 'deploy', root / 'docs'):
    for path in base.rglob('*'):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        if '/opt/papyr/production/.env' in text:
            raise SystemExit(1)
raise SystemExit(0)
PY
    then fail 'stale /opt/papyr environment path remains in deployment documentation'; fi
    printf 'PASS — placeholders are confined to documented skeleton slots and paths are reconciled\n'

    printf '=== 4. services, profiles, and port contract ===\n'
    "$PYTHON" - "$COMPOSE" <<'PY' || fail 'compose service/profile/port contract failed'
import sys
from pathlib import Path
import yaml
p = Path(sys.argv[1])
d = yaml.safe_load(p.read_text(encoding='utf-8'))
expected = {'api','nginx','redis','workers','clamd','cleanup','monitor'}
if set(d.get('services', {})) != expected:
    raise SystemExit('service set mismatch')
profiles = {name: set(svc.get('profiles', [])) for name, svc in d['services'].items()}
if profiles['api'] != {'app'} or profiles['nginx'] != {'edge'}:
    raise SystemExit('app/edge profile mismatch')
for name in ('redis','workers','clamd','cleanup','monitor'):
    if profiles[name] != {'queue'}:
        raise SystemExit(f'{name} queue profile mismatch')
# The deployment override owns the public 3016 -> internal 3000 mapping.
override = p.with_name('compose.override.deploy.yml')
runbook = p.with_name('runbook-vps.md').read_text(encoding='utf-8')
if '3016' not in runbook or '3000' not in runbook:
    raise SystemExit('3016 to 3000 mapping is not documented')
if override.exists() and '3016:3000' not in override.read_text(encoding='utf-8').replace(' ', ''):
    raise SystemExit('override does not contain 3016:3000')
PY
    printf 'PASS — seven services, expected profiles, and 3016→3000 contract present\n'

    printf '=== 5. image evidence (masked) ===\n'
    printf 'api=%s workers=%s clamd=%s\n' "$(redact_ref "${PAPYR_API_IMAGE:-}")" "$(redact_ref "${PAPYR_WORKERS_IMAGE:-}")" "$(redact_ref "${PAPYR_CLAMD_IMAGE:-}")"
    printf 'check-launch: PASS\n'
}

http_body() {
    url=$1
    body=$(curl -fsS --max-time 20 "$url") || fail "HTTP request failed: $url"
    printf '%s' "$body"
}

expect_json_field() {
    url=$1; field=$2; expected=$3
    body=$(http_body "$url")
    "$PYTHON" - "$field" "$expected" "$body" <<'PY' || fail "unexpected JSON response: $1"
import json, sys
field, expected, body = sys.argv[1:]
data = json.loads(body)
value = data.get(field)
if value != expected:
    raise SystemExit(f'{field}={value!r}, expected {expected!r}')
PY
}

smoke() {
    printf '=== 1. API health ===\n'
    expect_json_field https://api.mypapyr.com/health status ok
    printf 'PASS — /health returned 200 status=ok\n'
    printf '=== 2. API readiness ===\n'
    expect_json_field https://api.mypapyr.com/health/ready status ready
    printf 'PASS — /health/ready returned 200 status=ready\n'
    printf '=== 3. API capabilities ===\n'
    body=$(http_body https://api.mypapyr.com/api/v1/capabilities)
    "$PYTHON" - "$body" <<'PY' || fail 'capabilities response lacks required fields'
import json, sys
d = json.loads(sys.argv[1])
for key in ('maxRetries', 'defaultTimeoutSeconds'):
    if key not in d:
        raise SystemExit(key)
PY
    printf 'PASS — capabilities returned 200 with required contract fields\n'
    printf '=== 4. canonical frontend routes ===\n'
    for path in / /en /sitemap.xml /robots.txt /en/compress-pdf; do
        curl -fsS --max-time 20 -o /dev/null "https://budgezen.com$path" || fail "frontend route failed: $path"
        printf 'PASS — %s returned 200\n' "$path"
    done
    printf '=== 5. legacy host redirects ===\n'
    for host in mypapyr.com www.mypapyr.com; do
        headers=$(curl -sI --max-time 20 --max-redirs 0 "http://$host/") || fail "redirect probe failed: $host"
        printf '%s\n' "$headers" | grep -Eiq '^HTTP/[0-9.]+ 308([[:space:]]|$)' || fail "$host did not return 308"
        location=$(printf '%s\n' "$headers" | tr -d '\r' | awk 'tolower($1)=="location:" {print substr($0,10); exit}')
        case "$location" in
            https://budgezen.com*) : ;;
            *) fail "$host Location is not on https://budgezen.com" ;;
        esac
        printf 'PASS — %s returns 308 to canonical host\n' "$host"
    done
    printf 'check-launch: PASS\n'
}

rollback_preflight() {
    printf '=== 1. frontend rollback evidence ===\n'
    if [ "${PAPYR_FRONTEND_RELEASE_URL:-}" ]; then
        printf 'current frontend release URL: <operator-supplied value withheld>\n'
    else
        printf 'current frontend release URL: operator must record the Vercel production deployment URL\n'
    fi
    if [ "${PAPYR_BUILD_ID:-}" ]; then
        printf 'current frontend BUILD_ID: <operator-supplied value withheld>\n'
    else
        printf 'current frontend BUILD_ID: operator must read the deployed Vercel build marker\n'
    fi
    printf 'PASS — frontend rollback evidence instruction recorded\n'
    printf '=== 2. nginx cutover rollback artifact ===\n'
    printf 'backup convention: /etc/nginx/sites-available/mypapyr.bak-cutover-<UTC timestamp>\n'
    grep -q 'mypapyr.bak-cutover-<UTC timestamp>' "$ROOT/deploy/runbook-vps.md" || fail 'nginx rollback backup convention missing from runbook'
    printf 'PASS — timestamped nginx backup convention documented\n'
    printf '=== 3. backend rollback procedure ===\n'
    grep -q 'PAPYR_API_IMAGE=registry/papyr-api@sha256:<previous-digest>' "$ROOT/docs/upgrade.md" || fail 'upgrade rollback pointer missing'
    for name in PAPYR_WORKERS_IMAGE PAPYR_CLAMD_IMAGE; do
        grep -q "$name=registry/" "$ROOT/docs/upgrade.md" || fail "upgrade rollback pointer missing: $name"
    done
    printf 'pointer: docs/upgrade.md rollback (all three immutable images); no SSH or mutation performed\n'
    printf 'PASS — backend rollback evidence documented\n'
    printf 'check-launch: PASS\n'
}

mode=${1:-preflight}
case "$mode" in
    preflight) preflight ;;
    smoke) smoke ;;
    rollback-preflight) rollback_preflight ;;
    *) fail "unknown mode: $mode (use preflight, smoke, or rollback-preflight)" ;;
esac
