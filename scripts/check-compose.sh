#!/bin/sh
#
# check-compose.sh — structural assertions for deploy/docker-compose.yml.
# The guard verifies service structure, healthchecks, unpublished internal
# ports, dependency conditions, standalone API activation, hardened container
# posture, profile separation, the PAPYR_ENV_FILE source gate, immutable API
# image selection, and the absence of placeholder host ports.
#
# Runnable without Docker; runtime `docker compose config` validation belongs
# on a Docker-capable deployment host. Also runs yamllint on
# the file when the binary is present (CI installs yamllint==1.38.0 first).

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
COMPOSE="$ROOT/deploy/docker-compose.yml"

fail() {
    printf 'check-compose: FAIL — %s\n' "$1" >&2
    exit 1
}

[ -f "$COMPOSE" ] || fail "compose file absent: $COMPOSE"

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"
"$PYTHON" -c 'import yaml' >/dev/null 2>&1 || fail "pyyaml required (python3 -m pip install pyyaml)"

"$PYTHON" - "$COMPOSE" <<'PY' || fail "structural assertions failed"
import json
import os
import re
import sys

import yaml

path = sys.argv[1]
with open(path, encoding="utf-8") as fh:
    doc = yaml.safe_load(fh)

if not isinstance(doc, dict) or "services" not in doc:
    print("compose file has no top-level services map", file=sys.stderr)
    sys.exit(1)

expected = {"api", "nginx", "redis", "workers"}
actual = set(doc["services"].keys())
if actual != expected:
    print("services = %s, expected %s" % (sorted(actual), sorted(expected)), file=sys.stderr)
    sys.exit(1)

svcs = doc["services"]

# --- required keys per service --------------------------------------------
required = {
    "api": ["image", "profiles", "env_file", "expose", "restart", "read_only",
            "security_opt", "cap_drop", "tmpfs", "cpus", "mem_limit",
            "pids_limit", "logging", "healthcheck"],
    "nginx": ["image", "profiles", "depends_on", "ports", "volumes", "restart",
              "logging", "healthcheck"],
    "redis": ["image", "profiles", "command", "volumes", "restart", "logging",
              "healthcheck"],
    "workers": ["image", "profiles", "env_file", "depends_on", "restart", "logging"],
}
for svc, keys in required.items():
    missing = [k for k in keys if k not in svcs[svc]]
    if missing:
        print("%s missing keys: %s" % (svc, missing), file=sys.stderr)
        sys.exit(1)

# --- restart policy (every service) ---------------------------------------
for name, svc in svcs.items():
    if svc.get("restart") != "unless-stopped":
        print("%s restart must be unless-stopped" % name, file=sys.stderr)
        sys.exit(1)

# --- published ports: only nginx publishes --------------------------------
for name in ("api", "redis", "workers"):
    if "ports" in svcs[name]:
        print("%s must not publish ports" % name, file=sys.stderr)
        sys.exit(1)

# --- healthchecks: api/nginx/redis; worker probe awaits its real image -----
for name in ("api", "nginx", "redis"):
    if "healthcheck" not in svcs[name]:
        print("%s missing healthcheck" % name, file=sys.stderr)
        sys.exit(1)

# --- depends_on conditions ------------------------------------------------
nginx_dep = svcs["nginx"].get("depends_on", {})
if nginx_dep.get("api", {}).get("condition") != "service_healthy":
    print("nginx -> api must use condition: service_healthy", file=sys.stderr)
    sys.exit(1)
workers_dep = svcs["workers"].get("depends_on", {})
if workers_dep.get("redis", {}).get("condition") != "service_healthy":
    print("workers -> redis must use condition: service_healthy", file=sys.stderr)
    sys.exit(1)

# --- API isolation: the service runs standalone ---------------------------
if "depends_on" in svcs["api"]:
    print("api must not depend on any service (no Redis/worker assumptions)", file=sys.stderr)
    sys.exit(1)

# --- API hardened posture -------------------------------------------------
api = svcs["api"]
if api.get("read_only") is not True:
    print("api read_only must be true", file=sys.stderr)
    sys.exit(1)
if api.get("security_opt") != ["no-new-privileges:true"]:
    print("api security_opt must be [no-new-privileges:true]", file=sys.stderr)
    sys.exit(1)
if api.get("cap_drop") != ["ALL"]:
    print("api cap_drop must be [ALL]", file=sys.stderr)
    sys.exit(1)
if api.get("cap_add"):
    print("api must not add Linux capabilities after cap_drop: [ALL]", file=sys.stderr)
    sys.exit(1)
api_image = str(api.get("image", ""))
api_image_pattern = r"\$\{PAPYR_API_IMAGE:\?[^}]+\}"
if re.fullmatch(api_image_pattern, api_image) is None:
    print(
        "api image must require PAPYR_API_IMAGE; mutable defaults/tags are rejected: %r"
        % api_image,
        file=sys.stderr,
    )
    sys.exit(1)
for mount in ("/tmp:", "/opt/papyr/temp:", "/home/appuser/.cache:"):
    if not any(m.startswith(mount) for m in api.get("tmpfs", [])):
        print("api tmpfs missing %s" % mount, file=sys.stderr)
        sys.exit(1)
if "cpus" not in api or "mem_limit" not in api or api.get("pids_limit", 0) <= 0:
    print("api must bound cpus, mem_limit, and pids_limit", file=sys.stderr)
    sys.exit(1)

# --- bounded json-file logging (every service) ------------------------------
for name, svc in svcs.items():
    logging = svc.get("logging", {})
    opts = logging.get("options", {})
    if logging.get("driver") != "json-file" or opts.get("max-size") != "10m" \
            or opts.get("max-file") != "3":
        print("%s logging must be json-file 10m x 3" % name, file=sys.stderr)
        sys.exit(1)

# --- Redis persistence/eviction policy (R-09) ------------------------------
# Approved defaults (audit-outputs/phase-3/gate-entry.md section 5): AOF
# with appendfsync everysec plus RDB snapshots (explicit save points) as
# secondary recovery aid; named volume for /data; maxmemory ~384 MB with
# noeviction (valid tasks are never silently evicted; OOM writes fail
# loudly); a mandatory memory-warning watermark on the health probe; the
# image pinned by immutable digest at implementation (M11, DEC-056).
_REDIS_COMMAND = [
    "redis-server",
    "--appendonly",
    "yes",
    "--appendfsync",
    "everysec",
    "--save",
    "3600 1 300 100 60 10000",
    "--maxmemory",
    "384mb",
    "--maxmemory-policy",
    "noeviction",
]
if svcs["redis"].get("command") != _REDIS_COMMAND:
    print(
        "redis command must declare the R-09 policy "
        "(appendonly yes, appendfsync everysec, RDB save points, 384mb noeviction)",
        file=sys.stderr,
    )
    sys.exit(1)
if "redis-data:/data" not in svcs["redis"].get("volumes", []):
    print("redis must mount redis-data:/data", file=sys.stderr)
    sys.exit(1)
redis_image = str(svcs["redis"].get("image", ""))
if re.fullmatch(r"redis:[0-9]+\.[0-9]+\.[0-9]+-alpine@sha256:[0-9a-f]{64}", redis_image) is None:
    print(
        "redis image must be an immutable digest pin "
        "(redis:X.Y.Z-alpine@sha256:<64 hex>); floating tags and __SET_ME__ are rejected: %r"
        % redis_image,
        file=sys.stderr,
    )
    sys.exit(1)
try:
    redis_mem = svcs["redis"].get("mem_limit", "0M")
    if isinstance(redis_mem, (int, float)):
        redis_mem_mb = int(redis_mem) // (1024 * 1024)
    else:
        redis_mem_mb = int(str(redis_mem).rstrip("M"))
except (ValueError, AttributeError):
    redis_mem_mb = 0
if redis_mem_mb < 512:
    print(
        "redis mem_limit must be >= 512M (maxmemory 384mb + AOF/RDB/fork headroom; "
        "a hard cgroup limit below maxmemory would kernel-OOM-kill the server)",
        file=sys.stderr,
    )
    sys.exit(1)
_redis_health = svcs["redis"].get("healthcheck", {}).get("test", [])
if not any("used_memory" in str(part) and "WARNING" in str(part) for part in _redis_health):
    print(
        "redis healthcheck must surface the R-09 memory-warning watermark "
        "(probe prints used_memory/maxmemory and a WARNING at the threshold)",
        file=sys.stderr,
    )
    sys.exit(1)

# --- Worker bounds (R-07, DEC-189) ------------------------------------------
# Approved defaults (gate-entry.md section 3): memory 2G, cpus 1.5, tmpfs
# workspace bound to a per-job ceiling (one job per instance per DEC-189,
# so the container ceiling IS the per-job ceiling), one active worker
# (deploy.replicas 1). The worker image reference stays a __SET_ME__
# placeholder until a real worker image is built by the repo (documented
# blocker: pinning a digest for an image that does not exist would be
# fabrication); every other bound is declared now.
workers = svcs["workers"]
if workers.get("cpus") != "1.5" or workers.get("mem_limit") != "2G":
    print("workers must declare the R-07 bounds cpus 1.5 / mem_limit 2G", file=sys.stderr)
    sys.exit(1)
if workers.get("deploy", {}).get("replicas") != 1:
    print("workers must declare deploy.replicas 1 (DEC-189: one active worker)", file=sys.stderr)
    sys.exit(1)
if not any(
    m.startswith("/opt/papyr/workspace:") and "size=" in m for m in workers.get("tmpfs", [])
):
    print("workers must mount a per-job tmpfs workspace ceiling", file=sys.stderr)
    sys.exit(1)
if workers.get("read_only") is not True:
    print("workers read_only must be true", file=sys.stderr)
    sys.exit(1)
if workers.get("security_opt") != ["no-new-privileges:true"]:
    print("workers security_opt must be [no-new-privileges:true]", file=sys.stderr)
    sys.exit(1)
if workers.get("cap_drop") != ["ALL"]:
    print("workers cap_drop must be [ALL]", file=sys.stderr)
    sys.exit(1)

# --- R2 lifecycle declaration (approved contract) ---------------------------
# deploy/r2-lifecycle.json is the machine-readable, deploy-owned lifecycle
# declaration: exactly the approved rule set (tmp/ objects expire at the
# R2-supported one-day boundary; incomplete multipart uploads abort after
# 1 day), in the PUT request-body shape accepted by the R2 lifecycle API /
# wrangler `r2 bucket lifecycle set`. Application cleanup independently
# enforces the hard 3600-second retention ceiling. Declarative only: no
# secrets, no live mutation; the bucket name is supplied out-of-band at
# apply time.
lifecycle_path = os.path.join(os.path.dirname(path), "r2-lifecycle.json")
try:
    with open(lifecycle_path, encoding="utf-8") as fh:
        lifecycle = json.load(fh)
except (OSError, ValueError) as exc:
    print("r2-lifecycle.json missing or invalid: %s" % exc, file=sys.stderr)
    sys.exit(1)
rules = lifecycle.get("Rules", [])
if len(rules) != 2:
    print("r2-lifecycle.json must declare exactly two rules", file=sys.stderr)
    sys.exit(1)
by_id = {rule.get("ID"): rule for rule in rules}
if set(by_id) != {
    "papyr-tmp-objects-expire-r2-minimum-1-day-safety-net",
    "papyr-abort-incomplete-multipart-r2-minimum-1-day",
}:
    print("r2-lifecycle.json must declare exactly the approved rule ids", file=sys.stderr)
    sys.exit(1)
tmp_rule = by_id["papyr-tmp-objects-expire-r2-minimum-1-day-safety-net"]
if (
    tmp_rule.get("Status"),
    tmp_rule.get("Filter", {}).get("Prefix"),
    tmp_rule.get("Expiration", {}).get("Days"),
) != ("Enabled", "tmp/", 1):
    print(
        "tmp rule must be Enabled with Filter.Prefix tmp/ and the R2 minimum Expiration.Days 1",
        file=sys.stderr,
    )
    sys.exit(1)
mp_rule = by_id["papyr-abort-incomplete-multipart-r2-minimum-1-day"]
if (
    mp_rule.get("Status"),
    mp_rule.get("AbortIncompleteMultipartUpload", {}).get("DaysAfterInitiation"),
) != ("Enabled", 1):
    print(
        "multipart rule must be Enabled and abort incomplete uploads at the R2 minimum of 1 day",
        file=sys.stderr,
    )
    sys.exit(1)
for rule in rules:
    if any(secret in str(rule).lower() for secret in ("secret", "token", "password", "access_key")):
        print("r2-lifecycle.json must not carry secret material", file=sys.stderr)
        sys.exit(1)

# --- activation safety -----------------------------------------------------
# Profile separation: `--profile app` must select only the API. Deferred
# slots live behind their own profiles.
profile_contract = {"api": ["app"], "nginx": ["edge"], "redis": ["queue"], "workers": ["queue"]}
for name, want in profile_contract.items():
    if svcs[name].get("profiles") != want:
        print("%s profiles = %s, expected %s" % (name, svcs[name].get("profiles"), want), file=sys.stderr)
        sys.exit(1)

# The container environment must come from `${PAPYR_ENV_FILE:?...}`—never from the
# committed template, which carries intentionally empty required values.
for name in ("api", "workers"):
    envs = svcs[name].get("env_file", [])
    if any("env.production.example" in str(e) for e in envs):
        print("%s env_file must not reference the committed template" % name, file=sys.stderr)
        sys.exit(1)
    if name == "api" and not any("PAPYR_ENV_FILE" in str(e) for e in envs):
        print("api env_file must gate on ${PAPYR_ENV_FILE:?...}", file=sys.stderr)
        sys.exit(1)

# No placeholder host port may exist in `ports`; the deployment skeleton
# publishes nothing (nginx ports: []).
for name, svc in svcs.items():
    for spec in svc.get("ports", []):
        if "__SET_ME__" in str(spec):
            print("%s ports contain the __SET_ME__ placeholder" % name, file=sys.stderr)
            sys.exit(1)

print("check-compose: structural PASS — services = %s" % sorted(actual))
PY

if command -v yamllint >/dev/null 2>&1; then
    yamllint "$COMPOSE" || fail "yamllint reported violations"
    yamllint "$ROOT/deploy/r2-lifecycle.json" || fail "yamllint reported violations on r2-lifecycle.json"
fi

printf 'check-compose: PASS\n'
