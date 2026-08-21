#!/bin/sh
# OP-04: encrypted restic backup plan. No live operation is performed by plan mode.
#
# Scope is PRIVACY-ENFORCED BY ALLOWLIST, not by exclude patterns: only the
# relative configuration paths listed in $PAPYR_BACKUP_SCOPE are read from
# $PAPYR_BACKUP_ROOT, so document data (filenames, contents, metadata), R2
# objects, signed URLs, queue payloads, uploads, results, Redis state, and
# credentials structurally cannot enter the repository.
set -eu

: "${RESTIC_REPOSITORY:?set RESTIC_REPOSITORY to an encrypted S3-compatible repository URL}"
: "${RESTIC_PASSWORD_FILE:?set RESTIC_PASSWORD_FILE to a mode-0600 password file}"
: "${PAPYR_BACKUP_ROOT:?set PAPYR_BACKUP_ROOT to the directory holding the deployment configuration}"
: "${PAPYR_BACKUP_SCOPE:?set PAPYR_BACKUP_SCOPE to the allowlist scope manifest path}"
: "${RESTIC_KEEP_DAILY:=7}"
: "${RESTIC_KEEP_WEEKLY:=4}"
: "${RESTIC_KEEP_MONTHLY:=12}"
: "${RESTIC_KEEP_YEARLY:=3}"

# password_file_ok: exit 0 only when $1 is a REGULAR file with owner-only
# mode 0600 (no group/other bits). Fails closed on directory, symlink, FIFO,
# group/world-readable, or any non-0600 mode. Portable across GNU and BSD.
password_file_ok() {
    [ -f "$1" ] || return 1
    mode=$(ls -ld "$1" 2>/dev/null | awk '{print $1}')
    case "$mode" in
        -rw-------) return 0 ;;
        *) return 1 ;;
    esac
}

MODE=${1:-plan}
case ${MODE} in
  plan|--dry-run)
    printf '%s\n' 'restic backup plan (not executed):'
    printf '  repository: encrypted S3-compatible RESTIC_REPOSITORY (value withheld)\n'
    printf '  source root: %s\n' "${PAPYR_BACKUP_ROOT}"
    printf '  scope: allowlist manifest %s (only the listed config paths)\n' "${PAPYR_BACKUP_SCOPE}"
    printf '%s\n' '  excluded structurally: document data, R2 objects, signed URLs, queue payloads, uploads, results, Redis, credentials'
    printf '  retention: daily=%s weekly=%s monthly=%s yearly=%s (R-13 placeholders)\n' "${RESTIC_KEEP_DAILY}" "${RESTIC_KEEP_WEEKLY}" "${RESTIC_KEEP_MONTHLY}" "${RESTIC_KEEP_YEARLY}"
    printf '%s\n' '  commands: restic backup --files-from $PAPYR_BACKUP_SCOPE; restic forget --prune; restic check; restic check --read-data-subset=1/30'
    ;;
  run)
    password_file_ok "${RESTIC_PASSWORD_FILE}" \
        || { printf '%s\n' 'password file must be a mode-0600 regular file owned by the operator (no group/world bits)' >&2; exit 1; }
    [ -f "${PAPYR_BACKUP_SCOPE}" ] || { printf '%s\n' 'backup scope manifest missing' >&2; exit 1; }
    (
        cd "${PAPYR_BACKUP_ROOT}"
        restic backup --password-file "${RESTIC_PASSWORD_FILE}" --repo "${RESTIC_REPOSITORY}" --files-from "${PAPYR_BACKUP_SCOPE}"
    ) || { printf '%s\n' 'backup run failed' >&2; exit 1; }
    restic forget --password-file "${RESTIC_PASSWORD_FILE}" --repo "${RESTIC_REPOSITORY}" --keep-daily "${RESTIC_KEEP_DAILY}" --keep-weekly "${RESTIC_KEEP_WEEKLY}" --keep-monthly "${RESTIC_KEEP_MONTHLY}" --keep-yearly "${RESTIC_KEEP_YEARLY}" --prune
    restic check --password-file "${RESTIC_PASSWORD_FILE}" --repo "${RESTIC_REPOSITORY}"
    ;;
  *) printf '%s\n' 'usage: restic-backup.sh [plan|run|--dry-run]' >&2; exit 2 ;;
esac
