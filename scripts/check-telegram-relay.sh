#!/bin/sh
#
# check-telegram-relay.sh — OP-03 Telegram incident relay guard.
# Structural assertions for deploy/monitoring/telegram-relay.py and
# deploy/monitoring/alerts.md: standard-library-only delivery (host-runnable,
# no app dependency), a closed message payload allowlist that is byte-identical
# between the contract (alerts.md) and the implementation (the relay's
# ALLOWED_DETAIL_FIELDS literal), the dedup/cooldown/reminder, retry, recovery,
# and permanent-failure marker behaviour, environment-only credentials with no
# committed secrets and no __SET_ME__ placeholders, and a privacy boundary that
# rejects filenames, document terms, object keys, signed URLs, passwords,
# tokens, payloads, and document metadata (DEC-175, DEC-182).
#
# Runnable without Docker and without network. The backend monitor schema and
# the OP-01 health-signal contract (backend/app/ops/monitor.py,
# deploy/monitoring/health-signals.md) are NOT modified here.

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
RELAY="$ROOT/deploy/monitoring/telegram-relay.py"
ALERTS="$ROOT/deploy/monitoring/alerts.md"

fail() {
    printf 'check-telegram-relay: FAIL — %s\n' "$1" >&2
    exit 1
}

[ -f "$RELAY" ] || fail "telegram relay absent: $RELAY"
[ -f "$ALERTS" ] || fail "alerts contract absent: $ALERTS"

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"

# --- the relay must compile ------------------------------------------------
"$PYTHON" -m py_compile "$RELAY" || fail "telegram-relay.py does not compile"

"$PYTHON" - "$RELAY" "$ALERTS" <<'PY' || fail "structural assertions failed"
import ast
import re
import sys


def reject(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


relay_path, alerts_path = sys.argv[1], sys.argv[2]

try:
    with open(relay_path, encoding="utf-8") as fh:
        source = fh.read()
    with open(alerts_path, encoding="utf-8") as fh:
        alerts_md = fh.read()
except OSError as exc:
    reject("artifact unreadable: %s" % exc)

if re.search(r"(?:TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID)\s*=\s*['\"][^'\"]+['\"]", source):
    reject("Telegram credentials must not be committed as source literals")
if "BOT_TOKEN__X" in source or "123456:ABC" in source:
    reject("Telegram credential-looking test value must not ship in the relay")
if "__SET_ME__" in alerts_md:
    reject("placeholder values must never ship in the alert contract")
if "__SET_ME__" in source:
    reject("placeholder values must never ship in the relay")

# --- standard-library-only imports (host-runnable, offline-safe) -----------
stdlib = set(getattr(sys, "stdlib_module_names", ()))
tree = ast.parse(source)
imported: set[str] = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            imported.add(alias.name.split(".")[0])
    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
        imported.add(node.module.split(".")[0])
non_stdlib = sorted(imported - stdlib)
if non_stdlib:
    reject("relay imports non-standard-library module(s): %s" % ", ".join(non_stdlib))

# --- required alert behaviour markers must exist ---------------------------
for marker in (
    "ALLOWED_DETAIL_FIELDS",
    "--cooldown",
    "--state",
    "--max-attempts",
    "--dry-run",
    "--sender-script",
    "RECOVERY",
    "permanent-failure",
):
    if marker not in source:
        reject("relay must implement %r (dedup/cooldown, retry, recovery, "
               "permanent-failure marker)" % marker)
for env_name in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
    if env_name not in source:
        reject("relay must read %s from the environment only" % env_name)

# --- payload allowlist: contract (alerts.md) == implementation (relay) -----
block = re.search(
    re.escape("<!-- ALERT-PAYLOAD-ALLOWLIST-START -->")
    + r"(.*?)"
    + re.escape("<!-- ALERT-PAYLOAD-ALLOWLIST-END -->"),
    alerts_md,
    re.DOTALL,
)
if block is None:
    reject("alerts.md must delimit the ALERT-PAYLOAD-ALLOWLIST machine block")
contract_fields = {
    field.strip() for field in block.group(1).split(",") if field.strip()
}

relay_set: set[str] | None = None
for node in ast.walk(tree):
    target = None
    if isinstance(node, ast.AnnAssign):
        target = node.target
    elif isinstance(node, ast.Assign):
        target = node.targets[0] if len(node.targets) == 1 else None
    if not isinstance(target, ast.Name) or target.id != "ALLOWED_DETAIL_FIELDS":
        continue
    value = node.value
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) \
            and value.func.id == "frozenset" and value.args:
        relays_fields = ast.literal_eval(value.args[0])
        if isinstance(relays_fields, (set, frozenset)):
            relay_set = set(relays_fields)
if relay_set is None:
    reject("relay must define ALLOWED_DETAIL_FIELDS as a frozenset literal")

if relay_set != contract_fields:
    reject(
        "payload allowlist drift — alerts.md and the relay ALLOWED_DETAIL_FIELDS "
        "must be identical\n  missing in relay: %s\n  missing in contract: %s"
        % (
            ", ".join(sorted(contract_fields - relay_set)),
            ", ".join(sorted(relay_set - contract_fields)),
        )
    )
if not relay_set:
    reject("payload allowlist must not be empty")

# --- privacy: no forbidden data field may enter the allowlist ---------------
FORBIDDEN_TERM = re.compile(
    r"filename|file_name|\bdocument\b|\bextracted\b|\bcontent\b|object\s*key|"
    r"signed\s*url|signed_url|\bpassword\b|\bsecret\b|\btoken\b|\bpayload\b|"
    r"\burl\b|\bkey\b|\bmetadata\b|\bname\b",
    re.IGNORECASE,
)
for field in relay_set:
    if FORBIDDEN_TERM.search(field):
        reject("allowlist field %r is a prohibited document/credential term "
               "(DEC-175/DEC-182)" % field)

# --- the privacy boundary must reject every required category --------------
privacy = re.search(
    re.escape("<!-- ALERT-PRIVACY-REJECTED-TERMS-START -->")
    + r"(.*?)"
    + re.escape("<!-- ALERT-PRIVACY-REJECTED-TERMS-END -->"),
    alerts_md,
    re.DOTALL,
)
if privacy is None:
    reject("alerts.md must delimit the ALERT-PRIVACY-REJECTED-TERMS machine block")
lower_privacy = privacy.group(1).lower()
for required in ("filename", "document", "object key", "signed url",
                 "password", "token", "payload"):
    if required not in lower_privacy:
        reject("alerts.md privacy boundary must reject %r (DEC-175/DEC-182)" % required)

# --- secret scan across the audit surface ----------------------------------
for name, text in (("relay source", source), ("alerts.md", alerts_md)):
    lower = text.lower()
    for pattern in (
        r"sk-[a-z0-9]{8,}",
        r"akia[0-9a-z]{16}",
        r"begin [a-z ]*private key",
        r"(password|secret|auth_token|bearer)\s*[:=]\s*['\"][^'\"]+['\"]",
    ):
        if re.search(pattern, lower):
            reject("%s carries a credential-looking value (pattern %r)" % (name, pattern))

print("check-telegram-relay: PASS — relay allows %d closed fields: %s"
      % (len(relay_set), ", ".join(sorted(relay_set))))
print("check-telegram-relay: PASS — stdlib-only imports, env-only credentials, "
      "no committed secrets")
print("check-telegram-relay: PASS — dedup/cooldown, retry, recovery, and "
      "permanent-failure marker behaviour present")
PY

printf 'check-telegram-relay: PASS\n'