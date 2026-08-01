#!/bin/sh
#
# check-compose.sh — structural assertions for deploy/docker-compose.yml.
# The guard verifies service structure, healthchecks, unpublished internal
# ports, dependency conditions, standalone API activation, hardened container
# posture, profile separation, the PAPYR_ENV_FILE source gate, and the absence
# of placeholder host ports.
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
            "security_opt", "cap_drop", "cap_add", "tmpfs", "cpus", "mem_limit",
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
for cap in ("CHOWN", "DAC_OVERRIDE", "SETGID", "SETUID"):
    if cap not in api.get("cap_add", []):
        print("api cap_add missing %s" % cap, file=sys.stderr)
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

# --- Redis persistence for queue metadata ---------------------------------
if svcs["redis"].get("command") != ["redis-server", "--appendonly", "yes"]:
    print("redis command must enable appendonly", file=sys.stderr)
    sys.exit(1)
if "redis-data:/data" not in svcs["redis"].get("volumes", []):
    print("redis must mount redis-data:/data", file=sys.stderr)
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
fi

printf 'check-compose: PASS\n'
