# C6 Evidence — restic and S3-compatible Backups

- **Access date:** 2026-07-31
- **Purpose:** primary-source evidence for `c6-backups-restores.md` (backup scope, schedule, retention, encryption, restore verification)
- **Method:** read-only fetch of official restic documentation. No installs, no repositories, no buckets.

## 1. restic overview

Sources: `https://restic.readthedocs.io/en/stable/` and `https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html` (accessed 2026-07-31).

- Open source (BSD-2-Clause) backup program; repositories of snapshots, packs, and indexes; data encrypted with AES-256 (authenticated encryption) keyed by the repository password.
- **Repository password:** "knowledge of your password is required to access the repository. Losing your password means that your data is irrecoverably lost." Multiple keys can unlock one repository.
- Automation: `RESTIC_REPOSITORY` env var or `--repository-file`; password via `RESTIC_PASSWORD` / `--password-file` / `RESTIC_PASSWORD_FILE` / `--password-command` / `RESTIC_PASSWORD_COMMAND`.
- **S3 backend:** `restic -r s3:s3.us-east-1.amazonaws.com/bucket_name init`; credentials via `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (plus `AWS_SESSION_TOKEN` for temporary creds). S3-compatible (non-Amazon): `restic -r s3:https://server:port/bucket_name init`. Path-style URLs are expected for Amazon; `-o s3.bucket-lookup=auto|dns|path` for compatibility; `-o s3.region=...` for region; `-o s3.list-objects-v1=true` for backends with broken ListObjectsV2.
- Repository version 2 (compression support) is the current default and requires restic ≥ 0.14.0.
- Note on append-only: the rest-server project offers append-only mode; most S3 backends do not natively (rclone `serve restic` can act as a complement). For policy-based snapshot removal in append-only repositories, the docs recommend `--keep-within` over `--keep-*` (security consideration).
- restic `0.17.0+` adds `--insecure-no-password` (not applicable; we require a password).

## 2. Retention: forget + prune

Source: `https://restic.readthedocs.io/en/stable/060_forget.html` (accessed 2026-07-31).

- Removing snapshots = `forget` (remove snapshot metadata) then `prune` (remove unreferenced data). Automate with `forget --prune`.
- **Policy options:** `--keep-last n`; `--keep-hourly/daily/weekly/monthly/yearly n` (natural time boundaries; days 00:00-23:59, weeks Mon-Sun; only periods that contain snapshots count); `--keep-tag`; `--keep-within duration` (e.g., `2y5m7d3h`) and `--keep-within-daily/weekly/monthly/hourly`. Snapshots are evaluated against all keep options, ORed.
- Prune is time-consuming and **locks the repository during pruning** (backups cannot complete during prune) — "Please plan your pruning so that there's time to complete it and it doesn't interfere with regular backup runs."
- "It is advisable to run `restic check` after pruning."
- `prune` options: `--max-unused` (default 5%), `--max-repack-size`, `--repack-cacheable-only`, `--dry-run`; recovery from no-free-space via `--unsafe-recover-no-free-space` (last resort).
- `forget --dry-run` previews policy actions without removing anything.

## 3. Integrity and restore

- `restic check` (repository integrity) and `restic check --read-data` (verify all data can be read) are documented commands (`https://restic.readthedocs.io/en/stable/040_backup.html` and reference; referenced).
- `restic restore <snapshot> --target <dir>` restores to a directory; `--include`/`--exclude` filters (legacy runbook §7.4 uses `--include`); `restic snapshots` lists snapshots (`--json` for scripting); `restic ls`/`restic find` inspect contents.
- Restore target = a local/scratch directory; restoring never requires a running production system and is inherently isolated when pointed at a scratch path (design conclusion for DEC-181).

## 4. Scheduling

- restic docs describe automated backups via cron/systemd; no single canonical scheduler is mandated. The legacy runbook uses a script + cron-like cadence (`/opt/papyr/backups/backup.sh`, runbook §7.1-7.2). A systemd timer or cron entry running `backup` then `forget --prune` (then `check`) with exit-code-based failure detection is the standard pattern (design conclusion, supported by the forget/prune docs).
- Backup of live databases/Redis: for Redis, the official guidance (see c1-evidence-redis.md §2) recommends RDB/AOF snapshot copying or the Redis 8.10 BACKUP family; C6 recommends excluding Redis persistence by default (DEC-174 minimization) — a design decision, not a restic requirement.

## Uncertainties

- Current restic stable version and any CHANGELOG/security items: the docs reference repository version 2 default and the append-only security considerations; the exact latest release number should be confirmed at implementation (`https://github.com/restic/restic/releases`).
- S3-compatible endpoint specifics (bucket layout, ListObjectsV2 support) depend on the chosen destination; use `-o s3.bucket-lookup`/`list-objects-v1` options as needed.

## Source list

| # | URL | Accessed |
|---|---|---|
| 1 | https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html | 2026-07-31 |
| 2 | https://restic.readthedocs.io/en/stable/060_forget.html | 2026-07-31 |
| 3 | https://restic.readthedocs.io/en/stable/040_backup.html | 2026-07-31 (referenced) |
| 4 | https://github.com/restic/restic/releases | 2026-07-31 (referenced) |
