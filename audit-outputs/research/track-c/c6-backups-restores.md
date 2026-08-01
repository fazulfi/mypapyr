# C6 — Backups and Restore Verification Research Brief

| Field | Value |
|---|---|
| Brief ID | C6 |
| Path | `audit-outputs/research/track-c/c6-backups-restores.md` |
| Track | C — Infrastructure and operations |
| Title | Backups and restore verification research |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent, Track C Wave 1) |
| Status | Complete (draft for owner review under DEC-057) |
| Governing decisions | DEC-173, DEC-181, DEC-178; supporting: DEC-095, DEC-097, DEC-160, DEC-174, DEC-175, DEC-176, DEC-179, DEC-182 |
| Spec sections served | Technical Architecture Specification §18.4, §19.3, §24.3, §25.3 item 20 |

**Files read for this brief**

- `<workspace-root>\AGENTS.md`
- `<workspace-root>\papyr-rebuild-decisions.md` (in full; DEC-173, DEC-181, DEC-178 govern this brief)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (in full; §18.4, §19.3, §24.3, §25.3)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (relevant sections)
- `<workspace-root>\audit-outputs\research-program-plan.md` (§7.3, §8)
- `<workspace-root>\audit-outputs\spec-cross-review.md`
- Legacy (read-only): `papyr-reference/docs/runbook-vps.md` (§7 Backup & Restore, §8 incident response, §9 updates), `papyr-reference/deploy/docker-compose.yml`, `papyr-reference/deploy/.env.production.example`, `papyr-reference/backend/utils/config.py`
- Evidence file (primary evidence deliverable): `audit-outputs/research/track-c/evidence/c6-evidence-backups.md`

---

## 2. Scope

This brief resolves the backup and restore-verification design:

- **Backup scope** (DEC-173): the complete VPS state required for operational recovery — configuration, deployment state, service data, and recovery material — backed up to an approved S3-compatible destination; ephemeral processing workspaces, uploads, intermediates, results, passwords, signed URLs, and temporary queue payloads are explicitly **not** recoverable state.
- **Schedule, retention, encryption, and restore-target configuration** (DEC-173, arch §25.3 item 20).
- **Monthly isolated restore verification** (DEC-181): an isolated restore that never affects production, with results/failures recorded without exposing credentials, and repeated failures triggering an alert.
- **Restore versus rollback** (DEC-178): full S3 restore is disaster recovery only; ordinary release rollback uses the previous healthy image.

The user files (R2 temporary objects) are governed by C3's one-hour lifecycle and are not part of this backup set (DEC-173, DEC-013).

## 3. Non-goals

- **R2 temporary-object lifecycle** (C3): explicitly excluded from the backup set (DEC-173).
- **Redis task-record design** (C1): this brief covers what of the Redis persistence state is (and is not) worth backing up; the record schema is C1.
- **Application release rollback mechanics** (image tags/digests, compose rollback): DEC-178 and the deployment design (§19) own them; this brief only fixes the boundary between rollback and restore.
- **Monitoring/alert thresholds** (C5): this brief requires backup failure alerts; thresholds are C5.
- **A benchmark or DR drill program beyond the mandated monthly restore** (DEC-066, DEC-181).

## 4. Research questions

Restated from plan §7.3 (C6):

1. What exactly is "the complete VPS state required for operational recovery" for this stack (DEC-173), and what must be excluded from backup archives?
2. What schedule, retention window, and restore-target configuration are appropriate for the S3-compatible destination (DEC-173, arch §25.3 item 20)?
3. How is backup encryption and credential handling performed, and how is backup health monitored (DEC-173, DEC-176, DEC-182)?
4. How is the monthly isolated restore verification performed without affecting production or introducing user temporary files into retained test environments (DEC-181)?
5. How is restore distinguished from rollback, and when is each used (DEC-178)?

## 5. Evidence

### 5.1 Legacy baseline evidence (read-only, `papyr-reference/`)

| Path and line | What it evidences |
|---|---|
| `docs/runbook-vps.md:7.1-7.2` | Legacy restic backup: backup log at `/opt/papyr/logs/backup.log`, `restic.env` with repository config, manual trigger `/opt/papyr/backups/backup.sh`. |
| `docs/runbook-vps.md:7.3` | Legacy full-restore DR procedure: restore latest snapshot to `/tmp/restore-*`, copy `/opt/papyr/production/*`, `/opt/papyr/nginx/conf.d/*`, `/etc/letsencrypt/live/*`, fix userns-remap permissions, `compose up -d`. |
| `docs/runbook-vps.md:7.4` | Legacy partial restore: `restic restore <snapshot> --target ... --include <path>`. |
| `docs/runbook-vps.md:8.1` | Incident response: on confirmed compromise, restore from last known-good backup **before** compromise and rotate all secrets — restore is a security DR path. |
| `docs/runbook-vps.md:11` | Legacy cadence: restic DR drill **quarterly** (DEC-181 now mandates **monthly**); secret rotation quarterly. |
| `docs/runbook-vps.md:5.1,6` | OOM/reboot procedures; auto-start via systemd + compose. |
| `deploy/.env.production.example:1-11` | Env template: real values at `/opt/papyr/production/.env`, mode 600, mounted read-only — the secrets posture DEC-176 and DEC-173 exclude from backups where inappropriate. |
| `deploy/docker-compose.yml:17-24` | VPS budget and container resource layout (basis for deciding what host state is recoverable). |
| `backend/utils/config.py:102` | `FILE_RETENTION_MINUTES=60` — user files are ephemeral, reinforcing their exclusion from backups (DEC-173). |

### 5.2 Primary web sources (official documentation; access date 2026-07-31)

Current authoritative restic documentation is collected in the evidence file `evidence/c6-evidence-backups.md` (research primary evidence deliverable, access date 2026-07-31). Verified facts applied in this brief:

- **restic repository model** (`https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html`): snapshots/packs/index; **encryption keyed by the repository password — "Losing your password means that your data is irrecoverably lost"**; automation via `RESTIC_REPOSITORY` and `--password-file`/`RESTIC_PASSWORD`; **S3 backend** `restic -r s3:https://server:port/bucket_name` with `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`, path-style URLs expected for Amazon, `-o s3.bucket-lookup=auto|dns|path` for compatibility, `-o s3.region=...`; repository version 2 (compression) is the current default and requires restic ≥ 0.14.0. Append-only repositories (rest-server/rclone) have documented security considerations for policy-based removal.
- **Retention** (`https://restic.readthedocs.io/en/stable/060_forget.html`): `forget` removes snapshots, `prune` removes unreferenced data, `forget --prune` automates both; keep policies `--keep-last`, `--keep-daily`, `--keep-weekly`, `--keep-monthly`, `--keep-yearly`, `--keep-within <duration>`; **prune locks the repository during pruning (backups cannot run concurrently)**; "It is advisable to run `restic check` after pruning"; `forget --dry-run` previews.
- **Integrity/restore:** `restic check --read-data` verifies data readability; `restic restore <snapshot> --target <dir>` restores to a directory (`--include`/`--exclude` filters); `restic snapshots` (with `--json`) and `restic ls`/`find` inspect contents.
- **Scheduling:** no single mandated scheduler; a systemd timer or cron entry running `backup` → `forget --prune` → `check` with exit-code-based failure detection is the standard pattern (design conclusion grounded in the docs above; the legacy runbook uses `/opt/papyr/backups/backup.sh`).

## 6. Alternatives

### Backup tooling

**Alternative A1 — restic to the approved S3-compatible destination, evolved from the legacy baseline (recommended).**
- The legacy runbook already operates restic (runbook §7); restic gives native S3 backend, built-in authenticated encryption (repository password + AEAD), snapshots, retention (`forget`/`prune`), and `check --read-data` integrity verification. Continuing restic minimizes tool churn while fixing the gaps the decisions require: monthly restore verification (DEC-181) instead of the legacy quarterly drill, explicit exclusions (DEC-173), explicit retention policy, and monitored backups.
- Trade-offs: repository password management and recovery are a single point of failure (mitigated by owner password-manager custody per legacy practice and DEC-176 documentation); large-volume prune operations consume bandwidth/time (bounded because the recovery set is small and user files are excluded).
- Cost/operational impact: modest S3 storage cost (small recovery set); one cron/systemd timer; monthly restore-verification run in the DEC-181 cadence.

**Alternative A2 — borg/borgmatic to a local or SSH destination.**
- Mature deduplication/encryption; but borg's primary backends are local/SSH (an S3-style remote needs borg-server or a VPS), adding an extra remote host or storage surface that the decisions do not approve; restic's S3-native model matches DEC-173 directly. Kept as a documented alternative, not recommended.

**Alternative A3 — Provider-managed VPS snapshots only (no restic).**
- Simple but provider-locked, not S3-compatible, does not satisfy DEC-173's explicit S3-compatible destination, and does not give per-file restore or isolated verification ergonomics. Rejected.

### Restore-target configuration

**Alternative B1 — Isolated monthly restore to a scratch directory/throwaway container on a non-production host (recommended).**
- `restic restore <snapshot> --target /tmp/restore-verification` on a non-production machine (or a disposable container with the restic binary and repo access), then assert the restored tree exists, key files are readable (not the secret values themselves — redacted presence checks), service configs parse, and the restored Redis data (if any) loads in an isolated instance. Never restored over production; never introduces user temporary files (they are excluded from the archive by construction, DEC-173). Results, duration, and failures recorded without exposing credentials (DEC-181); repeated failures raise an operational alert (DEC-181, C5).
- Trade-offs: requires a machine/container with repo access for the drill; recording redacted results requires discipline.

**Alternative B2 — Monthly restore verification directly on the production host to a scratch directory.**
- Simpler (uses existing host access) but riskier: a misdirected restore could touch production state. Recommendation: prefer B1; if B2 is used, it must restore to an isolated path and never under `/opt/papyr` production paths. The runbook must make this explicit.

### Restore vs rollback (DEC-178)

- **Rollback** (application releases): reuse the previous healthy container image and matching compose configuration — fast, deterministic, no restore involved; artifacts retained for the defined rollback window (arch §19.3).
- **Restore** (disaster recovery): only for full-VPS loss or confirmed compromise requiring a clean-image rebuild (legacy runbook §8.1); restores the complete recovery set and then requires secret re-provisioning/rotation per DEC-176. The two paths never blur: a failing deploy does not trigger an S3 restore.

## 7. Recommendation

**Recommendation (not an accepted decision):** adopt **A1 (restic to the S3-compatible destination) + B1 (isolated monthly restore verification)** with these specifics:

- **Backup scope (included):** `/opt/papyr` deployment tree minus excluded paths (compose files, nginx conf, `.env` handling per below), host config needed to rebuild the stack (systemd unit/crontab files that run services and backup), and — as service data appropriate to retain — nothing document-bearing: Redis persistence files are excluded **or** backed up only after confirming they contain no document content (C1's allow-listed minimal metadata makes Redis recovery data acceptable, but the decision is to exclude them by default and rely on task-loss tolerance, keeping the archive strictly sanitized). Certificates (`/etc/letsencrypt/live`) are included per the legacy DR procedure; they are regenerable but speed recovery.
- **Excluded (DEC-173):** ephemeral processing workspaces, uploads, intermediate artifacts, results, `/tmp` and tmpfs content, passwords (env secret values are excluded from the archive — the `.env` template ships in the repo and the live `.env` is restored by re-provisioning from the owner's password manager, not from backup), signed URLs, and temporary queue payloads. Exclusions are enforced in the backup command and verified by a test that lists archive contents.
- **Encryption and credentials:** restic repository password and S3 access/secret live in a protected env file with mode 600 (legacy `restic.env` pattern, refreshed under DEC-176); the password is held by the owner in the password manager; loss of the password is documented as unrecoverable-data risk.
- **Schedule and retention (conservative defaults, adjustable, DEC-066):** **daily** backup at a quiet-hour time (e.g., 03:30 server time) via a systemd timer (fallback: cron), followed by `forget --prune` with retention **keep-last 7, keep-daily 7, keep-weekly 4, keep-monthly 6** (≈ 6-month restore horizon); retention values are design choices subject to owner confirmation and cost observation.
- **Health monitoring (DEC-182):** the backup timer's exit code and a `restic check` (weekly, or after each prune) drive a backup-health metric; any failure raises a Telegram alert through C5's contract; monthly restore verification under DEC-181; `restic check --read-data` on the monthly cadence for integrity.
- **Isolated restore procedure (monthly, DEC-181):** restore the latest snapshot to a scratch directory on a non-production host/container; assert tree completeness and redacted file presence (config parse checks, never secret values); record results/duration/failures in the audit output without credentials; repeated failures alert and trigger corrective work. The restored environment never contains user temporary files by construction.
- **Restore/rollback boundary (DEC-178):** documented in the runbook: application rollback = previous healthy image + matching config; full restore = DR only (VPS loss or confirmed compromise). A deploy failure never triggers a restore.

**Owner decision prompts:** (1) retention window (proposed ≈ 6 months; cost and recovery-horizon trade-off); (2) whether Redis persistence files are excluded from the archive by default (recommended) or included given C1's data-minimization; (3) confirmation that the backup destination is the owner's existing S3-compatible endpoint (the exact provider/bucket is deployment config; no account is created during research).

## 8. Measurable acceptance criteria

1. The backup archive contains exactly the documented include set and none of the excluded classes; an archive-content inspection test asserts no uploads, results, temp workspaces, passwords, signed URLs, or queue payloads appear (DEC-173).
2. A backup job runs on the documented schedule and produces a snapshot; a backup-success metric is exported (DEC-182).
3. Retention runs (`forget --prune`) keep exactly the configured window; a snapshot-count test asserts the policy (DEC-173).
4. Encryption is verified: without the repository password, snapshot data is unrecoverable; a documented password-loss procedure exists in the runbook (DEC-176).
5. `restic check --read-data` passes on the monthly cadence (DEC-181).
6. The monthly isolated restore executes on a non-production target, asserts restored-tree completeness with redacted checks, and records results/duration/failures without credentials (DEC-181).
7. The isolated restore does not affect production: production state (checksums of the compose tree) is unchanged before and after the drill (DEC-181).
8. Repeated restore failures raise an operational alert (DEC-181; C5 contract).
9. The runbook documents the restore-vs-rollback boundary: rollback uses the previous healthy image; restore is used only for DR; a failing deploy never triggers a restore (DEC-178).
10. R2 temporary objects are verifiably absent from all backup archives (DEC-173, DEC-013).

## 9. Assumptions, uncertainties, and unresolved questions

- **Assumption:** restic remains the approved tool (legacy baseline) and the owner has an S3-compatible destination available (DEC-173, DEC-095); the exact provider/bucket is deployment config requiring owner input — no account is created during research.
- **Uncertainty:** exact S3 storage cost for the recovery set at MVP volume; expected small, but to be confirmed at deployment (DEC-095).
- **Uncertainty:** whether the host is the legacy Linode/IDCloudHost VPS (runbook §1) with the documented paths; unverifiable without access (DEC-172, DEC-160).
- **Unresolved:** retention window and Redis-persistence inclusion (owner prompts above).
- **Unresolved:** whether the monthly restore drill runs on the owner's workstation, a disposable container, or a second small host — the procedure supports all three; the owner confirms the routine.

## 10. Dependencies and cross-track interfaces

- **C1:** Redis persistence records (if excluded from backups by default) mean task state is lost on full-VPS loss — acceptable because user files are R2-governed (C3) and in-flight jobs fail within timeouts; the C1 recommendation already tolerates Redis state loss.
- **C3:** R2 temporary objects are excluded by construction; the lifecycle net is the "backup" for user files.
- **C4:** restored host state must preserve the hardened compose profiles; restore verification includes a config-parse check.
- **C5:** backup success/failure and restore-drill results feed monitoring/alerts (DEC-182, DEC-181).
- **D5:** a compromise incident (runbook §8.1) triggers the restore path; the boundary with rollback is documented.
- **X1/X2:** recommendation and owner prompts feed the index and reconciliation report.

## 11. Source-date log and evidence-completeness notes

- Decisions and specifications read 2026-07-31; legacy files read 2026-07-31.
- Web evidence for restic was researched directly (read-only official docs) and persisted in `evidence/c6-evidence-backups.md` with per-source URLs and access date 2026-07-31. This brief's §5.2 summarizes it; exact restic version, command syntax, and any security advisories in the evidence file prevail, and any disagreement must be surfaced (DEC-183).
- Evidence-completeness: restic current version/CHANGELOG items, `forget`/`prune` semantics, and `check --read-data` are the material items recorded in the evidence file.

## 12. Prohibitions-compliance statement

No prohibited action was taken: no installs, builds, containers, server starts, VPS/SSH access, deployment, provider authentication, account creation (including any backup destination account), bucket creation, remote mutation, backup runs, or benchmark program (DEC-066, DEC-060, DEC-160, DEC-172, DEC-173). No source, spec, decision, or existing audit-output file was modified. All writes were confined to `audit-outputs/research/track-c/`. `papyr-reference/` was verified unchanged via read-only `git -C papyr-reference status --porcelain` (empty, exit 0) before and after this brief.
