#!/bin/sh
#
# test-verify-pins.sh — focused offline regression for verify-pins.sh.
# Uses a stub `gh` (no network) to prove three properties of the resolver:
#   1. Cache:   the same action@tag referenced twice resolves via ONE API call.
#   2. Auth:    with GH_TOKEN set and gh available, the gh transport is used.
#   3. Drift:   a tag that resolves to a SHA different from the pin fails closed.
#
# Standalone; does not weaken scripts/test-check-ci.sh.

set -eu

fail() {
    printf 'test-verify-pins: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SCRIPTS="$ROOT/scripts"
VERIFY="$SCRIPTS/verify-pins.sh"
[ -f "$VERIFY" ] || fail "verify-pins.sh absent: $VERIFY"

FIXTURE=$(mktemp -d) || fail "cannot create temp fixture"
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

# The pinned SHA in the fixture workflow must equal the SHA the stub returns,
# so the happy path resolves as a match.
PIN_SHA="1111111111111111111111111111111111111111"

mkdir -p "$FIXTURE/.github/workflows"
# actions/checkout@<sha> appears TWICE -> with caching, ONE api call total.
cat > "$FIXTURE/.github/workflows/pin-test.yml" <<EOF
name: pin-test
on: push
jobs:
  first:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@${PIN_SHA} # v3.0.0
  second:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@${PIN_SHA} # v3.0.0
EOF

GH_LOG="$FIXTURE/gh.log"
: > "$GH_LOG"

# Stub gh CLI: logs every `api` invocation, returns a commit-typed ref whose
# sha equals PIN_SHA. The log line count is the cache assertion.
cat > "$FIXTURE/gh" <<STUB
#!/bin/sh
if [ "\$1" = "api" ]; then
    echo "\$2" >> "$GH_LOG"
    printf '{"object":{"type":"commit","sha":"${PIN_SHA}"}}'
    exit 0
fi
exit 1
STUB
chmod +x "$FIXTURE/gh"

# Verify pins must run from within fixture so git rev-parse fails and ROOT defaults to pwd.
run_verify() {
    (cd "$FIXTURE" && sh "$VERIFY")
}

export GH_TOKEN="stub-token"
export GITHUB_TOKEN=""
export PATH="$FIXTURE:$PATH"
export VERIFY_PINS_RETRY_MAX=2
export VERIFY_PINS_RETRY_DELAY=0

printf '=== 1. cache + auth: duplicate pin resolves via a single API call ===\n'
OUT=$(run_verify) || fail "verify-pins rejected a matching pin: $OUT"
CALLS=$(grep -c 'git/ref/tags' "$GH_LOG" || true)
[ "$CALLS" -eq 1 ] || fail "expected 1 API call for a duplicated pin, saw $CALLS"
printf '%s\n' "$OUT" | grep -q 'PASS (2 pins match their tags)' \
    || fail "unexpected verify-pins output: $OUT"
printf 'PASS — 1 API call for 2 identical pins (cache + gh auth transport)\n'

printf '=== 2. drift rejection: tag resolves to a different SHA ===\n'
DRIFT_SHA="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
sed "s/${PIN_SHA}/${DRIFT_SHA}/" \
    "$FIXTURE/.github/workflows/pin-test.yml" \
    > "$FIXTURE/.github/workflows/pin-test.yml.new"
mv "$FIXTURE/.github/workflows/pin-test.yml.new" "$FIXTURE/.github/workflows/pin-test.yml"

if run_verify >/dev/null 2>&1; then
    fail "drifted pin was NOT rejected (verify-pins exited 0)"
fi
printf 'PASS — drifted pin rejected (fail-closed)\n'

printf '=== 3. unresolvable tag fails closed ===\n'
sed "s/# v3.0.0/# v9.9.9/" \
    "$FIXTURE/.github/workflows/pin-test.yml" \
    > "$FIXTURE/.github/workflows/pin-test.yml.new"
mv "$FIXTURE/.github/workflows/pin-test.yml.new" "$FIXTURE/.github/workflows/pin-test.yml"

# Stub fails for any tag other than the one it knows -> resolution error path.
cat > "$FIXTURE/gh" <<STUB
#!/bin/sh
if [ "\$1" = "api" ]; then
    case "\$2" in
        *v3.0.0*) printf '{"object":{"type":"commit","sha":"${PIN_SHA}"}}'; exit 0 ;;
        *) exit 1 ;;
    esac
fi
exit 1
STUB
chmod +x "$FIXTURE/gh"

if run_verify >/dev/null 2>&1; then
    fail "unresolvable tag was NOT rejected (verify-pins exited 0)"
fi
printf 'PASS — unresolvable tag rejected (fail-closed)\n'

printf 'test-verify-pins: PASS — cache, auth transport, drift, and unresolvable-tag contracts hold\n'
