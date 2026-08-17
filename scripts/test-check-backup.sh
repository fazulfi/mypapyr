#!/bin/sh
#
# test-check-backup.sh — focused offline regression for OP-04 backup scope.
# Proves, without Docker, network, or restic:
#   1. Green:  valid backup script + restore drill + scope manifest PASS.
#   2. Absent: missing deliverables (script / drill / scope manifest) fail closed.
#   3. Scope:  the run branch backs up ONLY the allowlist scope manifest
#              (--files-from) and does not rely on loose exclude patterns.
#   4. Leak:   a scope manifest entry naming a prohibited/sensitive location
#              (uploads, objects, queue, redis, results, .env, *.key) fails.
#   5. Perm:   a password file that is not a regular file fails closed in run.
#   6. Perm:   a group/world-readable password file fails closed in run (0600).
#   7. Plan:   plan mode leaks no repository or sensitive-looking value.
#   8. Green2: a mode-0600 owner-only password file + narrow scope is accepted
#              up to the point it would invoke restic (guard-only).
#
# Standalone; does not weaken scripts/check-backup.sh.

set -eu

fail() {
    printf 'test-check-backup: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SCRIPTS="$ROOT/scripts"
GUARD="$SCRIPTS/check-backup.sh"
SCRIPT="$ROOT/deploy/backup/restic-backup.sh"
DRILL="$ROOT/deploy/backup/restore-drill.md"
SCOPE="$ROOT/deploy/backup/backup-scope.txt"
[ -f "$GUARD" ] || fail "check-backup.sh absent: $GUARD"

FIXTURE=$(mktemp -d) || fail "cannot create temp fixture"
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

BACKUP="$FIXTURE/deploy/backup"
mkdir -p "$BACKUP"
cp "$SCRIPT" "$BACKUP/restic-backup.sh"
chmod +x "$BACKUP/restic-backup.sh"

# A valid, narrow scope manifest: deployment configuration only.
cat > "$BACKUP/backup-scope.txt" <<'EOF'
# OP-04 backup scope allowlist (enforceable contract).
docker-compose.yml
nginx/conf.d/production.conf
r2-lifecycle.json
EOF

# A minimal valid restore drill covering every required term.
cat > "$BACKUP/restore-drill.md" <<'EOF'
# OP-04 monthly isolated restore drill

## Preconditions

- Confirm the allowlist scope manifest is enforced via `--files-from`, so only
  the listed configuration paths are read; document data, R2 objects, signed
  URLs, queue payloads, uploads, results, Redis, and credentials structurally
  cannot enter the repository.
- `RESTIC_PASSWORD_FILE` must be a mode-0600 regular file; stop if it is missing,
  not regular, or group/world-readable.

## Monthly sequence

- Run `--files-from` plan mode with `PAPYR_BACKUP_SCOPE` set to validate the
  configuration shape without invoking restic.
- Validate expected configuration shape. Do not restore `.env`, TLS private
  keys, certificates, signed URLs, R2 objects, queue payloads, or Redis.
- `restic check --read-data-subset` and a temporary isolated target.
EOF

run_guard() {
    (cd "$FIXTURE" && sh "$GUARD")
}

printf '=== 1. green: valid backup script + drill + scope manifest PASS ===\n'
OUT=$(run_guard) || fail "guard rejected valid OP-04 artifacts: $OUT"
printf '%s\n' "$OUT" | grep -q 'check-backup: PASS' \
    || fail "unexpected guard output: $OUT"
printf 'PASS — valid artifacts accepted\n'

printf '=== 2. absent: missing deliverables fail closed ===\n'
rm -f "$BACKUP/restic-backup.sh" "$BACKUP/restore-drill.md" "$BACKUP/backup-scope.txt"
if run_guard >/dev/null 2>&1; then
    fail "guard passed with deliverables absent"
fi
printf 'PASS — absent deliverables rejected\n'
cp "$SCRIPT" "$BACKUP/restic-backup.sh"
chmod +x "$BACKUP/restic-backup.sh"
cat > "$BACKUP/backup-scope.txt" <<'EOF'
docker-compose.yml
nginx/conf.d/production.conf
r2-lifecycle.json
EOF
cp "$DRILL" "$BACKUP/restore-drill.md"

printf '=== 3. scope: run branch uses --files-from allowlist, not excludes ===\n'
grep -q -e '--files-from' "$BACKUP/restic-backup.sh" \
    || fail "run branch does not use the --files-from allowlist scope manifest"
grep -q 'PAPYR_BACKUP_SCOPE' "$BACKUP/restic-backup.sh" \
    || fail "backup script does not reference PAPYR_BACKUP_SCOPE"
printf 'PASS — enforce-by-allowlist present\n'

printf '=== 4. leak: prohibited scope manifest entry rejected ===\n'
# a leaking manifest must be rejected by the guard
cat > "$FIXTURE/deploy/backup/backup-scope.txt" <<'EOF'
docker-compose.yml
uploads/2026/08/abc.pdf
objects/queue
EOF
if run_guard >/dev/null 2>&1; then
    fail "guard accepted a scope manifest listing uploads/objects"
fi
cat > "$BACKUP/backup-scope.txt" <<'EOF'
docker-compose.yml
nginx/conf.d/production.conf
r2-lifecycle.json
EOF
printf 'PASS — leaking scope manifest rejected\n'

# ---------------------------------------------------------------------------
# run-mode permission enforcement is exercised against the real backup script
# with a bad or good password file; the permission gate returns before any
# restic invocation, so no restic binary is required.
# ---------------------------------------------------------------------------
run_run() {
    pwfile=$1
    set +e
    RESTIC_PASSWORD_FILE="$pwfile" \
    RESTIC_REPOSITORY=s3:REDACTED \
    PAPYR_BACKUP_ROOT="$FIXTURE" \
    PAPYR_BACKUP_SCOPE="$BACKUP/backup-scope.txt" \
        sh "$SCRIPT" run >"$FIXTURE/out" 2>&1
    RC=$?
    set -e
    printf '%s' "$RC"
}

printf '=== 5. perm: non-regular password file fails closed in run ===\n'
RC=$(run_run "$BACKUP" run)   # a directory, not a regular file
[ "$RC" -eq 1 ] || fail "run with a non-regular password file must exit 1, got $RC"
grep -q 'regular file' "$FIXTURE/out" || fail "no regular-file diagnostic: $(cat "$FIXTURE/out")"
printf 'PASS — non-regular password file rejected\n'

printf '=== 6. perm: group/world-readable password file fails closed (0600) ===\n'
printf 'secret\n' > "$FIXTURE/badpw"
chmod 0666 "$FIXTURE/badpw"
RC=$(run_run "$FIXTURE/badpw" run)
[ "$RC" -eq 1 ] || fail "run with a 0666 password file must exit 1, got $RC"
grep -q '0600' "$FIXTURE/out" || fail "no 0600 diagnostic: $(cat "$FIXTURE/out")"

printf 'secret\n' > "$FIXTURE/badpw2"
chmod 0644 "$FIXTURE/badpw2"
RC=$(run_run "$FIXTURE/badpw2" run)
[ "$RC" -eq 1 ] || fail "run with a 0644 password file must exit 1, got $RC"
grep -q '0600' "$FIXTURE/out" || fail "no 0600 diagnostic: $(cat "$FIXTURE/out")"
printf 'PASS — group/world-readable password file rejected\n'

printf '=== 7. plan: plan mode leaks no repository or sensitive value ===\n'
OUT=$(RESTIC_REPOSITORY=s3:REDACTED RESTIC_PASSWORD_FILE=/nonexistent \
    PAPYR_BACKUP_ROOT="$FIXTURE" PAPYR_BACKUP_SCOPE="$BACKUP/backup-scope.txt" \
    sh "$SCRIPT" plan)
printf '%s\n' "$OUT" | grep -F 'value withheld' >/dev/null || fail "plan leaked repository"
printf '%s\n' "$OUT" | grep -F 'not executed' >/dev/null || fail "plan mode absent"
if printf '%s\n' "$OUT" | grep -E 'password|secret|token|sha256|https?://' >/dev/null; then
    fail "plan exposed sensitive-looking value: $OUT"
fi
printf 'PASS — plan mode stays clean\n'

printf '=== 8. green2: mode-0600 owner-only password file is accepted ===\n'
printf 'secret\n' > "$FIXTURE/goodpw"
chmod 0600 "$FIXTURE/goodpw"
# Some hosts (Windows/MSYS) cannot represent Unix mode 0600: chmod 0600 still
# reports group/other readable bits, so the acceptance case cannot be exercised
# there. Detect that capability; only assert acceptance where it is real.
if [ "$(ls -ld "$FIXTURE/goodpw" | awk '{print $1}')" = "-rw-------" ]; then
    RC=$(run_run "$FIXTURE/goodpw" run)
    # permission gate passes; failure (if any) is now the absent restic binary,
    # never the permission diagnostic
    if grep -q '0600' "$FIXTURE/out" || grep -q 'regular file' "$FIXTURE/out"; then
        fail "good 0600 password file was rejected by the permission gate: $(cat "$FIXTURE/out")"
    fi
    printf 'PASS — mode-0600 password file passes the permission gate\n'
else
    printf 'SKIP — host file model cannot represent mode 0600 (Windows/MSYS); acceptance verified on POSIX hosts\n'
fi

printf 'test-check-backup: PASS — green, absent, scope, leak, perm, plan, and green2 contracts hold\n'
