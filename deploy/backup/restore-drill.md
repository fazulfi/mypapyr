# OP-04 monthly isolated restore drill

This is a procedure only; it has not been run against production. The operator must use a separately provisioned, encrypted S3-compatible restic repository and a temporary isolated host or VM.

## Preconditions

- Obtain owner approval for R-13 retention values and repository credentials.
- Provide `RESTIC_REPOSITORY`, `RESTIC_PASSWORD_FILE`, and `PAPYR_BACKUP_SCOPE` out of band; never paste any value into logs or this repository.
- `RESTIC_PASSWORD_FILE` must be a mode-`0600` regular file owned by the operator; stop if it is missing, not a regular file, or group/world-readable.
- Use neutral host metadata: `PAPYR_RESTORE_DRILL=1`, a non-production hostname, and no production DNS, TLS, or service credentials.
- Confirm the allowlist scope manifest (`deploy/backup/backup-scope.txt`, passed via `--files-from`) is enforced, so document data (filenames, contents, metadata), R2 objects, signed URLs, queue payloads, uploads, results, and Redis structurally cannot enter the repository. Scope is enforced by allowlist, not by exclude patterns.

## Monthly sequence

1. Create a temporary isolated restore target with mode `0700`; do not mount production paths.
2. Run `RESTIC_PASSWORD_FILE=/path/to/password RESTIC_REPOSITORY=s3:REDACTED PAPYR_BACKUP_ROOT=/srv/papyr PAPYR_BACKUP_SCOPE=/srv/papyr/deploy/backup/backup-scope.txt deploy/backup/restic-backup.sh plan` to validate the configuration shape without invoking restic.
3. On the isolated host, run a structural repository check: `restic check --password-file "$RESTIC_PASSWORD_FILE" --repo "$RESTIC_REPOSITORY"`.
4. Read a bounded data subset: `restic check --read-data-subset=1/30 ...` (rotate the subset each month; this is not a full restore).
5. Restore into the temporary target only: `restic restore latest --target "$RESTORE_TARGET" ...`.
6. Validate expected configuration shape and permissions. Do not restore `.env`, TLS private keys, certificates, signed URLs, R2 objects, queue payloads, or Redis; the allowlist scope guarantees no document data was captured.
7. Record only pass/fail, duration, restic version, repository label, neutral host identifier, and concern summary. Remove the target and any temporary credentials.

## R-13 retention placeholders

Until R-13 is approved, defaults remain placeholders: daily `7`, weekly `4`, monthly `12`, yearly `3`. Approval must replace these through deployment configuration, not source secrets. The backup script applies them only in `run` mode.

## Stop conditions

Stop without restoring if the repository is not encrypted, the password file is missing, not a regular file, or group/world-readable, the scope manifest is missing or lists a non-configuration path, the target is not isolated, or any command would access production DNS, TLS keys, R2, signed URLs, queue data, uploads, results, document data, or Redis.
