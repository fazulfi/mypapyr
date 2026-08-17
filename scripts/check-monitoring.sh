#!/bin/sh
#
# check-monitoring.sh — OP-01 health-signal and Netdata coverage guard.
# Structural assertions for deploy/monitoring/netdata-compose.yml and
# deploy/monitoring/health-signals.md: closed signal coverage for every
# monitored surface (API readiness, queue, workers, Redis, engines, storage
# integration, cleanup freshness, public endpoints), a privacy-safe signal
# vocabulary that rejects filenames, document terms, object keys, signed
# URLs, passwords, payload fields, and document metadata (DEC-175, DEC-182),
# and an internal-only digest-pinned Netdata companion Compose file with no
# published port and no Netdata Cloud / provider claim.
#
# Runnable without Docker; runtime `docker compose config` validation belongs
# on a Docker-capable deployment host. Also runs yamllint on the monitoring
# compose file when the binary is present (CI installs yamllint==1.38.0).
#
# The eight required surfaces map to the fixed backend monitor schema
# (backend/app/ops/monitor.py — api_ready, redis, clamd, queue_backlog,
# queue_pel, worker_health, cleanup_freshness, r2_ops) plus the OP-02
# public-endpoint signal; the backend fixed schema is NOT modified here.

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
NETDATA_COMPOSE="$ROOT/deploy/monitoring/netdata-compose.yml"
HEALTH_SIGNALS="$ROOT/deploy/monitoring/health-signals.md"

fail() {
    printf 'check-monitoring: FAIL — %s\n' "$1" >&2
    exit 1
}

[ -f "$NETDATA_COMPOSE" ] || fail "netdata compose file absent: $NETDATA_COMPOSE"
[ -f "$HEALTH_SIGNALS" ] || fail "health-signals contract absent: $HEALTH_SIGNALS"

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"
"$PYTHON" -c 'import yaml' >/dev/null 2>&1 || fail "pyyaml required (python3 -m pip install pyyaml)"

"$PYTHON" - "$NETDATA_COMPOSE" "$HEALTH_SIGNALS" <<'PY' || fail "structural assertions failed"
import re
import sys

import yaml

compose_path, signals_path = sys.argv[1], sys.argv[2]


def reject(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


# --------------------------------------------------------------------------
# 1. Netdata companion Compose contract (deploy/monitoring/netdata-compose.yml)
# --------------------------------------------------------------------------
try:
    with open(compose_path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
except OSError as exc:
    reject("netdata compose unreadable: %s" % exc)
except yaml.YAMLError as exc:
    reject("netdata compose YAML does not parse: %s" % exc)

if not isinstance(doc, dict) or "services" not in doc:
    reject("netdata compose has no top-level services map")
if doc.get("name") != "papyr-monitoring":
    reject("netdata compose top-level name must be papyr-monitoring; got %r" % doc.get("name"))
services = doc.get("services", {})
if set(services) != {"netdata"}:
    reject("netdata compose must declare exactly one service named netdata; got %s"
           % sorted(services))
svc = services["netdata"]

# --- immutable digest-pinned image; floating tags never accepted ----------
image = str(svc.get("image", ""))
if re.fullmatch(r"netdata/netdata:v[0-9]+\.[0-9]+\.[0-9]+@sha256:[0-9a-f]{64}", image) is None:
    reject(
        "netdata image must be an immutable digest pin "
        "(netdata/netdata:vX.Y.Z@sha256:<64 hex>); floating tags and "
        "__SET_ME__ are rejected: %r" % image
    )
if "__SET_ME__" in image:
    reject("netdata image must not carry the __SET_ME__ placeholder")

# --- internal-only: no published ports, no docker socket -------------------
if svc.get("ports"):
    reject("netdata must not publish ports (internal-only): %r" % svc.get("ports"))
volumes = [str(v) for v in svc.get("volumes", [])]
if any("docker.sock" in v.lower() for v in volumes):
    reject("netdata must not mount the docker socket: %r" % volumes)
if svc.get("env_file"):
    reject(
        "netdata must not load the app env_file (PAPYR_ENV_FILE carries R2 "
        "credentials; netdata declares only inline neutral env)"
    )

# --- no Netdata Cloud / provider claim; closed neutral env -----------------
env = [str(e) for e in svc.get("environment", [])]
for entry in env:
    upper = entry.upper()
    if "CLAIM" in upper:
        reject("netdata must not carry a provider claim variable: %r" % entry)
    if re.search(r"(_URL|_TOKEN|_SECRET|_PASSWORD|_ACCESS_KEY|_PRIVATE_KEY)=", upper):
        reject("netdata env must not carry URL/credential material: %r" % entry)
if not any(e.startswith("NETDATA_HOSTNAME=") for e in env):
    reject("netdata must declare a neutral NETDATA_HOSTNAME display name")
if any("netdata.cloud" in str(v).lower() for v in env + volumes):
    reject("netdata must not reference the Netdata Cloud endpoint")

# --- posture, bounds, logging, restart, state volumes ----------------------
if svc.get("profiles") != ["monitoring"]:
    reject("netdata must be on the single monitoring profile; got %r" % svc.get("profiles"))
if svc.get("restart") != "unless-stopped":
    reject("netdata restart must be unless-stopped")
if svc.get("read_only") is not True:
    reject("netdata read_only must be true")
if svc.get("security_opt") != ["no-new-privileges:true"]:
    reject("netdata security_opt must be [no-new-privileges:true]")
if not any(str(m).startswith("/tmp:") for m in svc.get("tmpfs", [])):
    reject("netdata must mount a /tmp tmpfs (read-only rootfs)")
if "cpus" not in svc or "mem_limit" not in svc or svc.get("pids_limit", 0) <= 0:
    reject("netdata must bound cpus, mem_limit, and pids_limit")
logging = svc.get("logging", {})
opts = logging.get("options", {})
if logging.get("driver") != "json-file" or opts.get("max-size") != "10m" \
        or opts.get("max-file") != "3":
    reject("netdata logging must be json-file 10m x 3")
for mount in ("netdata-lib:/var/lib/netdata", "netdata-cache:/var/cache/netdata"):
    if mount not in volumes:
        reject("netdata must mount the named state volume %r" % mount)
top_volumes = doc.get("volumes", {})
for name in ("netdata-lib", "netdata-cache"):
    if not isinstance(top_volumes, dict) or name not in top_volumes:
        reject("compose must declare the named volume %s" % name)

# --- attach to the single existing app network (BLKR-11 service DNS) -------
if svc.get("networks") != ["papyr"]:
    reject("netdata must attach to the single papyr network; got %r" % svc.get("networks"))
networks = doc.get("networks", {})
papyr_net = networks.get("papyr", {}) if isinstance(networks, dict) else {}
if papyr_net.get("external") is not True or papyr_net.get("name") != "papyr-app_papyr":
    reject(
        "netdata compose must declare the papyr network as external with "
        "name papyr-app_papyr (the single app-queue network); got %r" % papyr_net
    )

# --- compose secret-value scan ---------------------------------------------
text = open(compose_path, encoding="utf-8").read().lower()
for pattern in (
    r"sk-[a-z0-9]{8,}",
    r"akia[0-9a-z]{16}",
    r"begin [a-z ]*private key",
    r"(password|secret|token|access_key|private_key|bearer)\s*[:=]\s*\S+",
):
    if re.search(pattern, text):
        reject("netdata compose carries a credential-looking value (pattern %r)" % pattern)

# --------------------------------------------------------------------------
# 2. Health-signal contract (deploy/monitoring/health-signals.md)
# --------------------------------------------------------------------------
try:
    with open(signals_path, encoding="utf-8") as fh:
        md = fh.read()
except OSError as exc:
    reject("health-signals contract unreadable: %s" % exc)

# --- machine blocks --------------------------------------------------------
def block(start: str, end: str) -> str:
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), md, re.DOTALL)
    if match is None:
        reject("health-signals.md must delimit %s ... %s machine block" % (start, end))
    return match.group(1)


vocab_block = block("<!-- HEALTH-SIGNAL-VOCABULARY-START -->",
                    "<!-- HEALTH-SIGNAL-VOCABULARY-END -->")
privacy_block = block("<!-- PRIVACY-REJECTED-TERMS-START -->",
                      "<!-- PRIVACY-REJECTED-TERMS-END -->")

# --- vocabulary table ------------------------------------------------------
rows = [ln.strip() for ln in vocab_block.splitlines()
        if ln.strip().startswith("|") and not re.match(r"^\|\s*-+\s*\|", ln.strip())]
if len(rows) < 2:
    reject("health-signals vocabulary must contain a header row plus signal rows")
header = [c.strip() for c in rows[0].strip("|").split("|")]
expected_header = ["Signal", "Surface", "Owner", "Freshness", "Severity mapping",
                   "Source", "Closed data fields"]
if header != expected_header:
    reject("vocabulary table header must be %r; got %r" % (expected_header, header))

CLOSED_OWNERS = {"api", "queue", "worker", "redis", "engine", "storage",
                 "cleanup", "status"}
CLOSED_FIELDS = {
    "status", "status_code", "error_class", "count", "pending",
    "oldest_idle_ms", "group_exists", "worker_probe", "age_seconds",
    "reason", "region", "consecutive_failures", "state",
}
FRESHNESS = re.compile(r"^<=\s*\d+(\.\d+)?\s*[smh]$")
SEVERITY = re.compile(
    r"^ok\s*->\s*info;\s*(warn|degraded)\s*->\s*warning;\s*(fail|down)\s*->\s*critical$"
)
FORBIDDEN_TERM = re.compile(
    r"filename|file_name|\bdocument\b|\bextracted\b|\bcontent\b|object\s*key|"
    r"signed\s*url|signed_url|\bpassword\b|\bsecret\b|\btoken\b|\bpayload\b|"
    r"\burl\b|\bkey\b|\bmetadata\b|\bname\b",
    re.IGNORECASE,
)

required_surfaces = {
    "API readiness": {"api_ready"},
    "queue": {"queue_backlog", "queue_pel"},
    "workers": {"worker_health"},
    "Redis": {"redis"},
    "engines": {"clamd"},
    "storage integration": {"r2_ops"},
    "cleanup health": {"cleanup_freshness"},
    "public endpoints": {"public_endpoints"},
}

seen_surfaces: dict[str, set[str]] = {}
seen_signals: set[str] = set()
for row in rows[1:]:
    cells = [c.strip() for c in row.strip("|").split("|")]
    if len(cells) != 7:
        reject("vocabulary row must have exactly 7 columns: %r" % row)
    signal = cells[0].strip("`")
    surface, owner, freshness, severity, source, fields = cells[1:]
    if not re.fullmatch(r"[a-z0-9_]+", signal):
        reject("signal name must be closed lowercase [a-z0-9_]+: %r" % signal)
    if signal in seen_signals:
        reject("signal %r declared more than once (closed vocabulary)" % signal)
    seen_signals.add(signal)
    if surface not in required_surfaces:
        reject("signal %r references an unlisted surface %r" % (signal, surface))
    seen_surfaces.setdefault(surface, set()).add(signal)
    if owner not in CLOSED_OWNERS:
        reject("signal %r owner must be one of %s; got %r"
               % (signal, sorted(CLOSED_OWNERS), owner))
    if FRESHNESS.fullmatch(freshness) is None:
        reject("signal %r freshness must be <=N[smh]; got %r" % (signal, freshness))
    if SEVERITY.fullmatch(severity) is None:
        reject("signal %r severity mapping must be ok->info; warn->warning; fail->critical "
               "(warn|fail may read degraded|down): %r" % (signal, severity))
    for field in [f.strip() for f in fields.split(",") if f.strip()]:
        if field not in CLOSED_FIELDS:
            reject("signal %r data field %r is not in the closed field vocabulary"
                   % (signal, field))
    row_text = row.lower()
    if FORBIDDEN_TERM.search(row_text):
        reject("signal row carries a prohibited document/credential term "
               "(filenames, document terms, object keys, signed URLs, passwords, "
               "payloads, metadata): %r" % row)

computed_surfaces = sorted(required_surfaces, key=lambda name: name.lower())
missing = [name for name in computed_surfaces if not seen_surfaces.get(name)]
if missing:
    reject("missing monitored surface(s): %s" % ", ".join(missing))
for name in computed_surfaces:
    found = seen_surfaces[name]
    allowed = required_surfaces[name]
    unexpected = found - allowed
    if unexpected:
        reject("surface %r must map only to %s; also found %s"
               % (name, sorted(allowed), sorted(unexpected)))

# --- privacy boundary must reject every required category ------------------
lower_privacy = privacy_block.lower()
for required in ("filename", "document", "object key", "signed url",
                 "password", "payload"):
    if required not in lower_privacy:
        reject("privacy boundary must reject %r (DEC-175/DEC-182)" % required)

# --- contract-wide secret scan ---------------------------------------------
lower_md = md.lower()
for pattern in (
    r"sk-[a-z0-9]{8,}",
    r"akia[0-9a-z]{16}",
    r"begin [a-z ]*private key",
):
    if re.search(pattern, lower_md):
        reject("health-signals.md carries a credential-looking value (pattern %r)" % pattern)

ok_surfaces = ", ".join(
    "%s(%s)" % (name, ",".join(sorted(seen_surfaces[name]))) for name in computed_surfaces
)
print("check-monitoring: signals PASS — %s" % ok_surfaces)
print("check-monitoring: netdata PASS — internal-only digest-pinned companion (%s)" % image)
PY

if command -v yamllint >/dev/null 2>&1; then
    yamllint "$NETDATA_COMPOSE" || fail "yamllint reported violations"
fi

printf 'check-monitoring: PASS\n'