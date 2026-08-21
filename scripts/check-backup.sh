#!/bin/sh
set -eu
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SCRIPT="$ROOT/deploy/backup/restic-backup.sh"
DRILL="$ROOT/deploy/backup/restore-drill.md"
SCOPE="$ROOT/deploy/backup/backup-scope.txt"
fail() { printf 'check-backup: FAIL — %s\n' "$1" >&2; exit 1; }
[ -x "$SCRIPT" ] || fail 'backup script must be executable'
[ -f "$DRILL" ] || fail 'restore drill missing'
[ -f "$SCOPE" ] || fail 'backup scope manifest missing'
sh -n "$SCRIPT" || fail 'shell syntax invalid'
for needle in RESTIC_REPOSITORY RESTIC_PASSWORD_FILE PAPYR_BACKUP_ROOT PAPYR_BACKUP_SCOPE RESTIC_KEEP_DAILY RESTIC_KEEP_MONTHLY '--files-from'; do grep -F -e "$needle" "$SCRIPT" >/dev/null || fail "missing $needle"; done
grep -F 'mode-0600' "$SCRIPT" >/dev/null || fail 'run must fail closed unless the password file is owner-only 0600'
for needle in 'read-data-subset' 'temporary isolated' 'Redis' '.env' 'TLS' 'R2 objects' 'signed URLs' 'queue payloads' 'scope manifest' 'regular file'; do grep -F "$needle" "$DRILL" >/dev/null || fail "restore drill missing $needle"; done
[ -s "$SCOPE" ] || fail 'scope manifest must not be empty'
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|'#'*) continue ;; esac
    case "$line" in
        /*) fail "scope path must be relative: $line" ;;
        *.env*|*.key|*.pem|*.crt|*uploads*|*objects*|*queue*|*redis*|*results*)
            fail "scope path is a prohibited/sensitive location: $line" ;;
    esac
done < "$SCOPE"
output=$(RESTIC_REPOSITORY=s3:REDACTED RESTIC_PASSWORD_FILE=/nonexistent PAPYR_BACKUP_ROOT=/srv/papyr PAPYR_BACKUP_SCOPE=/srv/papyr/backup-scope.txt "$SCRIPT" plan)
printf '%s\n' "$output" | grep -F 'value withheld' >/dev/null || fail 'plan leaked repository'
printf '%s\n' "$output" | grep -F 'not executed' >/dev/null || fail 'plan mode absent'
if printf '%s\n' "$output" | grep -E 'password|secret|token|sha256|https?://' >/dev/null; then fail 'plan exposed sensitive-looking value'; fi
printf 'check-backup: PASS — offline structure, scope manifest, plan mode, and 0600 enforcement\n'
