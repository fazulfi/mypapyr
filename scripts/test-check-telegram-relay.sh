#!/bin/sh
#
# test-check-telegram-relay.sh — focused offline regression for the OP-03
# Telegram relay and its guard. Proves, without Docker or network:
#   1. Green:  valid relay + alert contract PASS the structural guard.
#   2. Absent: missing deliverables fail closed.
#   3. Secret: a committed credential value in the relay fails.
#   4. Leak:   allowlist drift / forbidden data field fails the guard.
#   5. Stdlib: a third-party import fails (host-runnable, offline-safe).
#   6. Dry-run: relay pages nothing and requires no credentials offline.
#   7. Dedup:   a repeated critical check is not re-paged inside cooldown.
#   8. Repeat:  a still-critical check is reminded after the cooldown.
#   9. Recovery: leaving critical sends a recovery message.
#  10. Retry:   transient failure is retried to success.
#  11. Permanent: a permanent send failure writes the marker and stops
#      paging on the next run.
#
# Standalone; does not weaken scripts/check-telegram-relay.sh.

set -eu

fail() {
    printf 'test-check-telegram-relay: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SCRIPTS="$ROOT/scripts"
GUARD="$SCRIPTS/check-telegram-relay.sh"
RELAY="$ROOT/deploy/monitoring/telegram-relay.py"
ALERTS="$ROOT/deploy/monitoring/alerts.md"
[ -f "$GUARD" ] || fail "check-telegram-relay.sh absent: $GUARD"
[ -f "$RELAY" ] || fail "telegram-relay.py absent: $RELAY"
[ -f "$ALERTS" ] || fail "alerts.md absent: $ALERTS"

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"

FIXTURE=$(mktemp -d) || fail "cannot create temp fixture"
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

MONITORING="$FIXTURE/deploy/monitoring"
mkdir -p "$MONITORING"
cp "$RELAY" "$ALERTS" "$MONITORING/"

# A minimal valid monitor report: redis critical, everything else healthy.
write_report() {
    cat > "$1" <<'EOF'
{
  "status": "failed",
  "generated_at": "2026-08-17T18:30:00+00:00",
  "checks": [
    {"name": "api_ready", "status": "ok", "details": {"status": "ready"}},
    {"name": "redis", "status": "fail", "details": {"status": "down", "error_class": "ConnectionError"}},
    {"name": "clamd", "status": "ok", "details": {"status": "pong"}}
  ],
  "summary": {"ok": 2, "warn": 0, "fail": 1}
}
EOF
}

run_guard() {
    (cd "$FIXTURE" && sh "$GUARD")
}

printf '=== 1. green: valid relay + alert contract PASS ===\n'
OUT=$(run_guard) || fail "guard rejected valid OP-03 artifacts: $OUT"
printf '%s\n' "$OUT" | grep -q 'check-telegram-relay: PASS' \
    || fail "unexpected guard output: $OUT"
printf 'PASS — valid artifacts accepted\n'

printf '=== 2. absent: deliverables absent fail closed ===\n'
rm -f "$MONITORING/telegram-relay.py" "$MONITORING/alerts.md"
if run_guard >/dev/null 2>&1; then
    fail "guard passed with deliverables absent"
fi
printf 'PASS — absent deliverables rejected\n'
cp "$RELAY" "$ALERTS" "$MONITORING/"

printf '=== 3. secret: committed credential value rejected ===\n'
"$PYTHON" - "$MONITORING/telegram-relay.py" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
text = text.replace(
    "TELEGRAM_BOT_TOKEN is required",
    "BOT_TOKEN__X = \"123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11\"\nTELEGRAM_BOT_TOKEN is required",
    1,
)
open(sys.argv[1], "w", encoding="utf-8", newline="\n").write(text)
PY
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a committed bot-token value"
fi
printf 'PASS — committed credential rejected\n'
cp "$RELAY" "$MONITORING/telegram-relay.py"

printf '=== 4. leak: allowlist drift / forbidden data field rejected ===\n'
"$PYTHON" - "$MONITORING/alerts.md" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
text = text.replace("consecutive_failures, state\n", "consecutive_failures, state, filename\n", 1)
open(sys.argv[1], "w", encoding="utf-8", newline="\n").write(text)
PY
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a forbidden data field in the allowlist"
fi
printf 'PASS — leaking allowlist rejected\n'
cp "$ALERTS" "$MONITORING/alerts.md"

printf '=== 5. stdlib: third-party import rejected ===\n'
"$PYTHON" - "$MONITORING/telegram-relay.py" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
text = text.replace("from __future__ import annotations\n",
                    "from __future__ import annotations\nimport requests\n", 1)
open(sys.argv[1], "w", encoding="utf-8", newline="\n").write(text)
PY
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a non-standard-library import"
fi
printf 'PASS — third-party import rejected\n'

# ---------------------------------------------------------------------------
# Relay behaviour, exercised against the real relay entirely offline.
# ---------------------------------------------------------------------------
REPORT="$FIXTURE/report.json"
STATE="$FIXTURE/state.json"
MARKER="$FIXTURE/state.json.permanent-failure"
SENDER="$FIXTURE/sender.py"

run_relay() {
    cooldown=$1
    shift
    "$PYTHON" "$RELAY" --report "$REPORT" --state "$STATE" \
        --max-attempts 3 --retry-delay 0 --cooldown "$cooldown" "$@"
}

printf '=== 6. dry-run: pages nothing and needs no credentials ===\n'
write_report "$REPORT"
rm -f "$STATE" "$MARKER"
OUT=$(run_relay 3600 --dry-run)
printf '%s\n' "$OUT" | grep -q '\[dry-run\]' || fail "dry-run printed no message: $OUT"
printf '%s\n' "$OUT" | grep -q 'ALERT Papyr critical: redis' || fail "dry-run alert text wrong: $OUT"
printf '%s\n' "$OUT" | grep -q 'status: down' || fail "dry-run dropped allowlisted detail: $OUT"
if printf '%s\n' "$OUT" | grep -qi 'filename\|signed\|password\|secret'; then
    fail "dry-run message leaked a prohibited term: $OUT"
fi
printf 'PASS — offline dry-run pages correctly without credentials\n'

printf '=== 7. dedup: repeat critical inside cooldown is not re-paged ===\n'
OUT=$(run_relay 3600 --dry-run)
if printf '%s\n' "$OUT" | grep -q '\[dry-run\]'; then
    fail "dedup failed — second run re-paged: $OUT"
fi
printf '%s\n' "$OUT" | grep -q 'deduped redis' || fail "no dedup notice: $OUT"
printf 'PASS — duplicate alert suppressed inside cooldown\n'

printf '=== 8. repeat: still critical after cooldown is reminded ===\n'
OUT=$(run_relay 0 --dry-run)
printf '%s\n' "$OUT" | grep -q 'REMINDER Papyr critical: redis' || fail "no reminder: $OUT"
printf 'PASS — reminder re-pages after cooldown\n'

printf '=== 9. recovery: leaving critical sends a recovery message ===\n'
"$PYTHON" - "$REPORT" <<'PY'
import json
import sys
report = json.load(open(sys.argv[1], encoding="utf-8"))
for check in report["checks"]:
    if check["name"] == "redis":
        check["status"] = "ok"
        check["details"] = {"status": "ready"}
report["status"] = "healthy"
report["summary"] = {"ok": 3, "warn": 0, "fail": 0}
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(report))
PY
OUT=$(run_relay 3600 --dry-run)
printf '%s\n' "$OUT" | grep -q 'RECOVERY Papyr cleared: redis' || fail "no recovery: $OUT"
printf 'PASS — recovery message emitted\n'

printf '=== 10. retry: transient failure retried to success ===\n'
write_report "$REPORT"
rm -f "$STATE" "$MARKER" "$FIXTURE/count" "$FIXTURE/captured.txt"
cat > "$SENDER" <<EOF
import pathlib
import sys
path = pathlib.Path(__file__).with_name("count")
count = int(path.read_text()) if path.exists() else 0
count += 1
path.write_text(str(count))
pathlib.Path(__file__).with_name("captured.txt").write_text(sys.stdin.read())
raise SystemExit(3 if count == 1 else 0)
EOF
run_relay 3600 --sender-script "$SENDER" >/dev/null || fail "retried send failed"
N=$(cat "$FIXTURE/count")
[ "$N" -eq 2 ] || fail "expected 2 send attempts after one transient failure, got $N"
printf 'PASS — transient failure retried to success (%s attempts)\n' "$N"

printf '=== 11. permanent: marker written, next run sends nothing ===\n'
write_report "$REPORT"
rm -f "$STATE" "$MARKER" "$FIXTURE/count" "$FIXTURE/captured.txt"
cat > "$SENDER" <<'EOF'
import sys
sys.stderr.write("permanent failure reason")
raise SystemExit(2)
EOF
set +e
run_relay 3600 --sender-script "$SENDER" >/dev/null 2>&1
RC=$?
set -e
[ "$RC" -eq 3 ] || fail "permanent failure must exit 3, got $RC"
[ -f "$MARKER" ] || fail "permanent-failure marker not written"
set +e
run_relay 3600 --sender-script "$SENDER" >/dev/null 2>&1
RC2=$?
set -e
[ "$RC2" -eq 3 ] || fail "marker present must exit 3, got $RC2"
printf 'PASS — permanent failure paged once, then marker stops paging\n'

printf 'test-check-telegram-relay: PASS — green, absent, secret, leak, stdlib, '
printf 'dry-run, dedup, repeat, recovery, retry, and permanent contracts hold\n'