#!/bin/sh
#
# test-check-monitoring.sh — focused offline regression for check-monitoring.sh.
# Proves five properties without Docker or network:
#   1. Green:  a valid netdata companion compose + health-signals contract PASS.
#   2. Absent: missing deliverables fail closed.
#   3. Leak:   a signal data field carrying a signed-URL/filename term fails.
#   4. Port:   a published port on the netdata service fails (internal-only).
#   5. Float:  a floating (non-digest) netdata image fails (immutability).
#   6. Cloud:  a provider claim variable (NETDATA_CLAIM_URL) fails.
#
# Standalone; does not weaken scripts/check-monitoring.sh.

set -eu

fail() {
    printf 'test-check-monitoring: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SCRIPTS="$ROOT/scripts"
GUARD="$SCRIPTS/check-monitoring.sh"
[ -f "$GUARD" ] || fail "check-monitoring.sh absent: $GUARD"

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"

FIXTURE=$(mktemp -d) || fail "cannot create temp fixture"
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

MONITORING="$FIXTURE/deploy/monitoring"
mkdir -p "$MONITORING"

# A valid, minimal netdata companion compose (digest-pinned, internal-only).
cat > "$MONITORING/netdata-compose.yml" <<'EOF'
name: papyr-monitoring

services:
  netdata:
    image: netdata/netdata:v2.11.0@sha256:c45c71eb23ff3f1012bcda7832bf08c0b09954363557e84511bcfaf6cafa3aa8
    profiles: ["monitoring"]
    environment:
      - NETDATA_HOSTNAME=papyr-monitor
      - NETDATA_LISTENER_PORT=19999
    networks:
      - papyr
    volumes:
      - netdata-lib:/var/lib/netdata
      - netdata-cache:/var/cache/netdata
    restart: unless-stopped
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M
    cpus: "0.25"
    mem_limit: 256M
    pids_limit: 128
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        labels: "com.papyr.service=netdata"

networks:
  papyr:
    external: true
    name: papyr-app_papyr

volumes:
  netdata-lib:
    driver: local
  netdata-cache:
    driver: local
EOF

# A valid, minimal health-signals contract covering every required surface.
cat > "$MONITORING/health-signals.md" <<'EOF'
# Papyr health-signal contract

<!-- HEALTH-SIGNAL-VOCABULARY-START -->
| Signal | Surface | Owner | Freshness | Severity mapping | Source | Closed data fields |
| --- | --- | --- | --- | --- | --- | --- |
| `api_ready` | API readiness | api | <=60s | ok->info; warn->warning; fail->critical | monitor check_api_ready | status, status_code, error_class |
| `queue_backlog` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_backlog | count |
| `queue_pel` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_pel | pending, oldest_idle_ms, group_exists |
| `worker_health` | workers | worker | <=60s | ok->info; warn->warning; fail->critical | monitor check_worker_health | group_exists, pending, oldest_idle_ms, worker_probe |
| `redis` | Redis | redis | <=60s | ok->info; warn->warning; fail->critical | monitor check_redis | status, error_class |
| `clamd` | engines | engine | <=60s | ok->info; warn->warning; fail->critical | monitor check_clamd | status, error_class |
| `r2_ops` | storage integration | storage | <=300s | ok->info; warn->warning; fail->critical | monitor check_r2_ops | status, error_class |
| `cleanup_freshness` | cleanup health | cleanup | <=3600s | ok->info; warn->warning; fail->critical | monitor check_cleanup_freshness | age_seconds, reason |
| `public_endpoints` | public endpoints | status | <=300s | ok->info; degraded->warning; down->critical | OP-02 multi-region snapshot | region, consecutive_failures, state |
<!-- HEALTH-SIGNAL-VOCABULARY-END -->

## Privacy boundary

<!-- PRIVACY-REJECTED-TERMS-START -->
filename, document name, document content, extracted text, object key, signed url, password, token, payload, document metadata
<!-- PRIVACY-REJECTED-TERMS-END -->
EOF

run_guard() {
    (cd "$FIXTURE" && sh "$GUARD")
}

printf '=== 1. green: valid monitoring artifacts PASS ===\n'
OUT=$(run_guard) || fail "guard rejected a valid contract: $OUT"
printf '%s\n' "$OUT" | grep -q 'check-monitoring: PASS' \
    || fail "unexpected guard output: $OUT"
printf 'PASS — valid compose + contract accepted\n'

printf '=== 2. absent: deliverables absent fail closed ===\n'
rm -f "$MONITORING/netdata-compose.yml" "$MONITORING/health-signals.md"
if run_guard >/dev/null 2>&1; then
    fail "guard passed with deliverables absent"
fi
printf 'PASS — absent deliverables rejected\n'
cat > "$MONITORING/netdata-compose.yml" <<'EOF'
name: papyr-monitoring
services:
  netdata:
    image: netdata/netdata:v2.11.0@sha256:c45c71eb23ff3f1012bcda7832bf08c0b09954363557e84511bcfaf6cafa3aa8
    profiles: ["monitoring"]
    environment:
      - NETDATA_HOSTNAME=papyr-monitor
    networks:
      - papyr
    volumes:
      - netdata-lib:/var/lib/netdata
      - netdata-cache:/var/cache/netdata
    restart: unless-stopped
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M
    cpus: "0.25"
    mem_limit: 256M
    pids_limit: 128
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        labels: "com.papyr.service=netdata"

networks:
  papyr:
    external: true
    name: papyr-app_papyr

volumes:
  netdata-lib:
    driver: local
  netdata-cache:
    driver: local
EOF
cat > "$MONITORING/health-signals.md" <<'EOF'
# Papyr health-signal contract

<!-- HEALTH-SIGNAL-VOCABULARY-START -->
| Signal | Surface | Owner | Freshness | Severity mapping | Source | Closed data fields |
| --- | --- | --- | --- | --- | --- | --- |
| `api_ready` | API readiness | api | <=60s | ok->info; warn->warning; fail->critical | monitor check_api_ready | status, status_code, error_class |
| `queue_backlog` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_backlog | count |
| `queue_pel` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_pel | pending, oldest_idle_ms, group_exists |
| `worker_health` | workers | worker | <=60s | ok->info; warn->warning; fail->critical | monitor check_worker_health | group_exists, pending, oldest_idle_ms, worker_probe |
| `redis` | Redis | redis | <=60s | ok->info; warn->warning; fail->critical | monitor check_redis | status, error_class |
| `clamd` | engines | engine | <=60s | ok->info; warn->warning; fail->critical | monitor check_clamd | status, error_class |
| `r2_ops` | storage integration | storage | <=300s | ok->info; warn->warning; fail->critical | monitor check_r2_ops | status, error_class |
| `cleanup_freshness` | cleanup health | cleanup | <=3600s | ok->info; warn->warning; fail->critical | monitor check_cleanup_freshness | age_seconds, reason |
| `public_endpoints` | public endpoints | status | <=300s | ok->info; degraded->warning; down->critical | OP-02 multi-region snapshot | region, consecutive_failures, state |
<!-- HEALTH-SIGNAL-VOCABULARY-END -->

## Privacy boundary

<!-- PRIVACY-REJECTED-TERMS-START -->
filename, document name, document content, extracted text, object key, signed url, password, token, payload, document metadata
<!-- PRIVACY-REJECTED-TERMS-END -->
EOF

printf '=== 3. leak: signed-url/filename data field rejected ===\n'
sed 's/| status, status_code, error_class |/| status, signed_url, error_class |/' \
    "$MONITORING/health-signals.md" > "$MONITORING/health-signals.md.new"
mv "$MONITORING/health-signals.md.new" "$MONITORING/health-signals.md"
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a signed-url data field"
fi
sed 's/| status, signed_url, error_class |/| status, filename, error_class |/' \
    "$MONITORING/health-signals.md" > "$MONITORING/health-signals.md.new"
mv "$MONITORING/health-signals.md.new" "$MONITORING/health-signals.md"
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a filename data field"
fi
printf 'PASS — leaking signal rejected\n'

printf '=== 4. port: published port rejected (internal-only) ===\n'
# restore the leak-free contract, then corrupt the compose with a published port
cat > "$MONITORING/health-signals.md" <<'EOF'
# Papyr health-signal contract

<!-- HEALTH-SIGNAL-VOCABULARY-START -->
| Signal | Surface | Owner | Freshness | Severity mapping | Source | Closed data fields |
| --- | --- | --- | --- | --- | --- | --- |
| `api_ready` | API readiness | api | <=60s | ok->info; warn->warning; fail->critical | monitor check_api_ready | status, status_code, error_class |
| `queue_backlog` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_backlog | count |
| `queue_pel` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_pel | pending, oldest_idle_ms, group_exists |
| `worker_health` | workers | worker | <=60s | ok->info; warn->warning; fail->critical | monitor check_worker_health | group_exists, pending, oldest_idle_ms, worker_probe |
| `redis` | Redis | redis | <=60s | ok->info; warn->warning; fail->critical | monitor check_redis | status, error_class |
| `clamd` | engines | engine | <=60s | ok->info; warn->warning; fail->critical | monitor check_clamd | status, error_class |
| `r2_ops` | storage integration | storage | <=300s | ok->info; warn->warning; fail->critical | monitor check_r2_ops | status, error_class |
| `cleanup_freshness` | cleanup health | cleanup | <=3600s | ok->info; warn->warning; fail->critical | monitor check_cleanup_freshness | age_seconds, reason |
| `public_endpoints` | public endpoints | status | <=300s | ok->info; degraded->warning; down->critical | OP-02 multi-region snapshot | region, consecutive_failures, state |
<!-- HEALTH-SIGNAL-VOCABULARY-END -->

## Privacy boundary

<!-- PRIVACY-REJECTED-TERMS-START -->
filename, document name, document content, extracted text, object key, signed url, password, token, payload, document metadata
<!-- PRIVACY-REJECTED-TERMS-END -->
EOF
"$PYTHON" - "$MONITORING/netdata-compose.yml" "$MONITORING/netdata-compose.yml.new" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
text = text.replace("    networks:\n      - papyr\n",
                    "    ports:\n      - \"19999:19999\"\n    networks:\n      - papyr\n", 1)
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(text)
PY
mv "$MONITORING/netdata-compose.yml.new" "$MONITORING/netdata-compose.yml"
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a published port on netdata"
fi
printf 'PASS — published port rejected\n'

printf '=== 5. float: floating image tag rejected (immutability) ===\n'
sed 's|netdata/netdata:v2.11.0@sha256:[0-9a-f]*|netdata/netdata:latest|' \
    "$MONITORING/netdata-compose.yml" > "$MONITORING/netdata-compose.yml.new"
mv "$MONITORING/netdata-compose.yml.new" "$MONITORING/netdata-compose.yml"
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a floating netdata image tag"
fi
sed 's|netdata/netdata:latest|netdata/netdata:v2.11.0@sha256:c45c71eb23ff3f1012bcda7832bf08c0b09954363557e84511bcfaf6cafa3aa8|' \
    "$MONITORING/netdata-compose.yml" > "$MONITORING/netdata-compose.yml.new"
mv "$MONITORING/netdata-compose.yml.new" "$MONITORING/netdata-compose.yml"
printf 'PASS — floating tag rejected\n'

printf '=== 6. cloud: provider claim variable rejected ===\n'
sed 's|      - NETDATA_HOSTNAME=papyr-monitor|      - NETDATA_HOSTNAME=papyr-monitor\n      - NETDATA_CLAIM_URL=https://app.netdata.cloud|' \
    "$MONITORING/netdata-compose.yml" > "$MONITORING/netdata-compose.yml.new"
mv "$MONITORING/netdata-compose.yml.new" "$MONITORING/netdata-compose.yml"
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a Netdata Cloud claim variable"
fi
printf 'PASS — provider claim rejected\n'

printf '=== 7. surface: missing public-endpoints coverage rejected ===\n'
cp "$MONITORING/health-signals.md" "$MONITORING/health-signals.md.orig"
sed '/public_endpoints/d' "$MONITORING/health-signals.md" \
    > "$MONITORING/health-signals.md.new"
mv "$MONITORING/health-signals.md.new" "$MONITORING/health-signals.md"
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a contract without public-endpoints coverage"
fi
mv "$MONITORING/health-signals.md.orig" "$MONITORING/health-signals.md"
printf 'PASS — missing surface rejected\n'

printf 'test-check-monitoring: PASS — green, absent, leak, port, float, cloud, and surface contracts hold\n'