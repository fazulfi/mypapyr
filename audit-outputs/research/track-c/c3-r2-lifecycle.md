# C3 — R2 Lifecycle and Retention Enforcement Research Brief

| Field | Value |
|---|---|
| Brief ID | C3 |
| Path | `audit-outputs/research/track-c/c3-r2-lifecycle.md` |
| Track | C — Infrastructure and operations |
| Title | R2 lifecycle and retention enforcement research |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent, Track C Wave 1) |
| Status | Complete (draft for owner review under DEC-057) |
| Governing decisions | DEC-013, DEC-067, DEC-070, DEC-075, DEC-166; supporting: DEC-025, DEC-036, DEC-042, DEC-165, DEC-170, DEC-173, DEC-174, DEC-175 |
| Spec sections served | Technical Architecture Specification §2.2, §12, §15, §23.3, §25.3; Product and UX Design Specification §13.3, §21.1 |

**Files read for this brief**

- `<workspace-root>\AGENTS.md`
- `<workspace-root>\papyr-rebuild-decisions.md` (in full; DEC-013, DEC-067, DEC-070, DEC-075, DEC-166 govern this brief)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (in full; §2.2, §12, §15, §23, §25.3)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (in full; §13.3)
- `<workspace-root>\audit-outputs\research-program-plan.md` (§6.3, §7.3, §8)
- `<workspace-root>\audit-outputs\spec-cross-review.md`
- Legacy (read-only): `papyr-reference/backend/utils/r2.py`, `papyr-reference/backend/utils/cleanup.py`, `papyr-reference/backend/utils/config.py`, `papyr-reference/deploy/.env.production.example`, `papyr-reference/docs/runbook-vps.md:5.4`
- Evidence file (primary evidence deliverable): `audit-outputs/research/track-c/evidence/c3-evidence-r2.md`

---

## 2. Scope

This brief resolves the R2 object lifecycle design for temporary server-processed files:

- **R2 object model and key hygiene** (DEC-013, DEC-174, DEC-025): what is stored (source, intermediate, result), what is never stored, and the opaque-key scheme.
- **The absolute one-hour retention clock** (DEC-070): clock start (upload receipt), no extension by retries/polling/downloads/tab-open (DEC-067, DEC-075), authoritative expiry exposure (DEC-070).
- **Active deletion by the application** (DEC-166): who deletes, when, idempotently, observably, and recoverably after restarts.
- **R2 lifecycle rule as a safety net** (DEC-166): current R2 lifecycle capabilities and limits, the configuration that provides independent backup cleanup, and verification that it never becomes the primary timer.
- **Cleanup observability** (DEC-166, DEC-175): counts and timing only, never content or sensitive identifiers.
- **Interface to signed downloads** (DEC-170): signed URL expiry never exceeds the authoritative absolute expiry.

The user-visible expiry behavior (countdown, warning before deletion, expired-result messaging) is owned by the Product and UX Design Specification §13.3 and is not restated here except where it constrains the mechanism.

## 3. Non-goals

- **Per-tool server limits** (what sizes/files are admitted): C2 (Wave 2).
- **Queue and task metadata design** (where the authoritative deadline lives in Redis): C1; this brief defines the R2-side mechanics only.
- **The fair-use/threat-classification admission decisions** that decide what is uploaded: D5 and C4.
- **VPS backups**: R2 temporary objects are explicitly *not* part of the VPS backup set (DEC-173); C6 covers backups.
- **Monitoring thresholds**: C5 consumes the cleanup telemetry this brief defines; thresholds are C5.
- **Content scanning/sanitization**: C4.

## 4. Research questions

Restated from plan §7.3 (C3):

1. What is the R2 object model and the safest key-hygiene scheme for source/intermediate/result objects (DEC-013, DEC-174, DEC-025)?
2. How is the absolute one-hour deadline enforced "by the application" (DEC-166) in a way that is idempotent, observable without logging content, and recoverable after restarts?
3. What can the R2 lifecycle rule actually enforce (current capabilities: conditions, granularity, timing), and what is the correct safety-net configuration given that one hour is a hard maximum (DEC-013, DEC-067, DEC-166)?
4. How do signed URLs (DEC-170) stay within the authoritative expiry without extending retention?
5. What does cleanup observability record, and how is cleanup verified by normal functional/integration tests (DEC-013, DEC-067, DEC-166)?

## 5. Evidence

### 5.1 Legacy baseline evidence (read-only, `papyr-reference/`)

| Path and line | What it evidences |
|---|---|
| `backend/utils/r2.py:23-39` | Legacy boto3 S3-compatible client against `https://{account_id}.r2.cloudflarestorage.com`, SigV4, region `auto` — the integration pattern to retain. |
| `backend/utils/r2.py:64-71` | Legacy key scheme: `f"{uuid.uuid4().hex}{ext}"` — opaque, carries no filename/user identity; retains a file-type extension. |
| `backend/utils/r2.py:98-135` | Legacy signed URL: `generate_presigned_url("get_object")` with `SIGNED_URL_EXPIRY_SECONDS = file_retention_minutes * 60` (3600 s default) and `ResponseContentDisposition` attachment filename — the DEC-170 pattern. |
| `backend/utils/r2.py:42-95,138-157` | `upload_file` returns `key/size_bytes/uploaded_at`; `delete_file` is idempotent (delete of a missing object returns success). |
| `backend/utils/cleanup.py:21-66` | Legacy cleanup loop: 30-minute interval, `list_objects_v2` scanning **all** objects by `LastModified` vs a cutoff, paginated. O(N) listing; the baseline replaced by per-job deadline tracking (DEC-166). |
| `backend/utils/cleanup.py:97-145` | Legacy deletion logs `object_key` (the UUID key) in event data — retained key-hygiene practice; counts/timing metrics `scanned/deleted/failed/duration_ms`. |
| `backend/utils/config.py:102` | `FILE_RETENTION_MINUTES=60` — the one-hour default. |
| `deploy/.env.production.example:14-17` | `R2_BUCKET_NAME=papyr-files` — legacy bucket name. |
| `docs/runbook-vps.md:5.4` | Legacy R2 troubleshooting: key rotation, CORS, bucket name; connectivity test endpoint pattern. |

### 5.2 Primary web sources (official Cloudflare R2 documentation; access date 2026-07-31)

Current authoritative R2 documentation is collected in the evidence file `evidence/c3-evidence-r2.md` (research primary evidence deliverable, access date 2026-07-31, `cloudflare` skill guidance applied). Verified facts applied in this brief:

- **Lifecycle rules** (`https://developers.cloudflare.com/r2/buckets/object-lifecycles/`, page updated 2026-04-21): prefix-based rules with expiration by age in **whole days** (`Expiration: {Days: N}`) or an absolute date; transition-to-Infrequent-Access rules; `AbortIncompleteMultipartUpload` rules; 1000-rule maximum.
- **Deletion timing is eventual:** "Objects will typically be removed from a bucket within 24 hours of the `x-amz-expiration` value." R2 therefore cannot itself enforce a one-hour deadline; the application must remain the primary enforcer and the lifecycle rule the safety net (DEC-166).
- Buckets carry a **default lifecycle rule expiring multipart uploads 7 days after initiation**; an explicit earlier abort rule for the temporary prefix should be added if multipart uploads are used.
- Presigned URLs are S3-API SigV4 presigned GETs via `generate_presigned_url("get_object", ..., ExpiresIn=<seconds>)` (boto3 example uses `ExpiresIn=3600`); expiry never exceeds the artifact's authoritative absolute expiry (DEC-170).
- **Pricing** (`https://developers.cloudflare.com/r2/pricing/`): free tier 10 GB-month storage, 1M Class A and 10M Class B operations/month, free egress; `DeleteObject` is a free operation; Standard storage $0.015/GB-month; egress is free for all storage classes.
- Custom metadata (up to ~4 KB) can carry a non-sensitive `expires-at` marker; keys and metadata must never carry filenames, passwords, or sensitive data (DEC-174, DEC-025).
- Consistency, object-size limits, and per-second operation limits are documented in the R2 reference pages (cited in the evidence file).

## 6. Alternatives

### Alternative A — Active application deletion only (no lifecycle rule)

- **What it is:** the API/cleanup coordinator deletes each object at `expires_at`; no R2 lifecycle rule.
- **Trade-offs:** simplest and most precise; but a long-running application failure or operator error leaves orphaned objects with **no independent cleanup path**, violating DEC-166's explicit requirement for a lifecycle safety net. Rejected on decision grounds, not performance grounds.

### Alternative B — R2 lifecycle rule only (no active deletion)

- **What it is:** rely on an R2 lifecycle rule (whole-day granularity, eventual timing) as the sole enforcement.
- **Trade-offs:** lifecycle rules cannot express "delete exactly one hour after upload"; minimum granularity is days, so objects would persist for up to ~24 h+, violating the hard one-hour maximum of DEC-013 and DEC-067. Rejected.

### Alternative C — Active deletion as primary timer + R2 lifecycle safety net (recommended)

- **What it is:** the application actively deletes each source/intermediate/result object when its authoritative `expires_at` (upload receipt + 1 h, DEC-070) is reached; an R2 lifecycle rule on a dedicated prefix deletes any object older than a conservative whole-day bound as independent backup cleanup (DEC-166). The lifecycle rule is verified continuously to exist and be correctly configured, and is documented as the safety net, never the primary timer.
- **Trade-offs:** two independent enforcement paths (defense in depth per DEC-166); the lifecycle rule's coarseness (days) is acceptable because it only backs up a primary path that is normally exact to the minute. Costs: one bucket prefix structure (to keep the rule scoped to temporary objects), periodic rule-config verification, and cleanup telemetry.
- **Risks and mitigations:** (1) the safety net's day-granularity means a fully failed active-deletion path could hold objects up to the rule age — mitigated by monitoring cleanup health (C5) so the failure is detected long before it matters; (2) lifecycle deletes count against R2 operation classes — cost impact is negligible at MVP volume (see evidence file pricing notes); (3) clock skew between API and R2 — mitigated by an expiry margin (deletion scheduled at `expires_at`, signed URLs capped at `remaining_time - margin`).

### Alternative D — Per-object expiry via custom metadata without per-job tracking

- **What it is:** the lifecycle rule is skipped; deletion uses a periodic scanner that reads `expires-at` metadata from object listing (an evolution of the legacy `cleanup.py` scan).
- **Trade-offs:** works without Redis, but requires O(N) listing scans (the legacy pattern DEC-166 replaces) and still lacks the independent lifecycle net. Kept as a **fallback recovery mechanism** (documented in the runbook for the pathological case where both Redis task records and lifecycle rules are unavailable), not the primary design.

## 7. Recommendation

**Recommendation (not an accepted decision):** adopt **Alternative C** with these specifics:

- **Object model and key hygiene.** One bucket (legacy `papyr-files`; actual bucket name is deployment config). Keys: `tmp/<YYYY-MM-DD>/<32-hex-uuid><ext>` where `<ext>` is a safe lowercase type suffix (`.pdf`, `.jpg`, `.zip`) derived internally, never from the original filename. The date prefix is non-sensitive, keeps the lifecycle rule scoped, and enables cheap day-level listing for the fallback scanner; the UUID remains the only identity and carries no filename/user identifier (DEC-174, DEC-025). Original filenames, passwords, signed URLs, and content never appear in keys or metadata (DEC-042, DEC-036, DEC-170).
- **Authoritative deadline.** The API computes `expires_at = upload_received_at + 1 h` (DEC-070) at admission, stores it as the authoritative task field in Redis (C1) and, as defense-in-depth, as non-sensitive R2 custom metadata `expires-at` on every source/intermediate/result object (within the ~4 KB metadata limit). Retries, polling, downloads, focus, or open tabs never extend it (DEC-067, DEC-075). The API exposes `expires_at` on the status contract so UI countdowns use server time (DEC-070).
- **Active deletion.** A cleanup coordinator (a dedicated loop in the worker/operational service, independent of any client connection per DEC-071) scans Redis task records whose `expires_at` has passed, deletes the job's source/intermediate/result objects by key, and idempotently marks cleanup complete. Deletion of an already-missing object is success (legacy `delete_file` behavior, `r2.py:138-157`). On API/worker restart, recovery is automatic: pending tasks are still in Redis and are re-scanned (DEC-166). If Redis records are lost, the R2 lifecycle rule is the safety net and the optional fallback scanner (Alternative D) can be run manually from the runbook.
- **R2 lifecycle safety net.** A lifecycle rule scoped to prefix `tmp/` deletes objects with `Expiration: {Days: 1}` — the smallest whole-day granularity the service offers — so, accounting for R2's documented removal lag ("typically… within 24 hours of the `x-amz-expiration` value"), orphaned objects are removed at roughly 1–2 days of age. Rationale: strictly larger than the one-hour maximum (never becomes the effective timer) and strictly smaller than any acceptable orphan lifetime; the 24-hour removal lag is acceptable because the active-deletion path is primary and its health is monitored (C5). If multipart uploads are used, an explicit `AbortIncompleteMultipartUpload` rule for `tmp/` with a short `DaysAfterInitiation` overrides the bucket default 7-day rule. The rule's existence and configuration are verified automatically (a "rule present and correct" check), and its deletions counted in cleanup telemetry (DEC-166).
- **Signed URLs.** Presigned GET URLs are issued with `ExpiresIn = min(remaining_time_to_expires_at, 300 s)` (short-lived per DEC-170), with `ResponseContentDisposition` for the safe localized download name; refreshed for the same valid result until `expires_at` without extending retention (DEC-170, DEC-075). Signed URLs are never written to logs, analytics, support reports, or status data (DEC-170, DEC-175).
- **Cleanup observability.** Telemetry records counts, timings, and failures only: objects scanned, deleted, delete-failed, lifecycle-rule-present, and coordinator health. No content, keys (beyond the opaque UUID already permitted), filenames, or sensitive identifiers (DEC-166, DEC-175).
- **Verification (normal functional/integration tests, not benchmarks):** a short-retention test mode asserts deletion no later than the configured deadline; a simulated coordinator failure asserts the lifecycle rule still removes objects past the safety-net age; idempotent re-deletion returns success; expired-result status returns 404/expired and is not restorable (DEC-067); a signed URL never outlives the artifact (DEC-170).

**Owner decision prompts:** (1) whether the safety-net lifecycle age of 1 day is preferred (recommended; effective orphan removal at roughly 1–2 days including R2's documented removal lag) over 2 days for extra margin against clock/skew edge cases; (2) whether to keep the legacy bucket name `papyr-files` or adopt a rebuild name with a clear `tmp/` prefix policy (requires a rename/migration decision, deployment-config level).

## 8. Measurable acceptance criteria

1. In normal operation, every source, intermediate, and result object is deleted no later than the absolute one-hour deadline from upload receipt (DEC-013, DEC-070); verified by a functional test with a short retention override.
2. No retry, status poll, download, tab focus, or open tab extends the deadline (DEC-067, DEC-075); verified by integration tests that assert `expires_at` is unchanged after each event.
3. A successful download does not trigger early deletion; the result remains available until `expires_at` (DEC-075).
4. Cleanup is idempotent: re-running deletion over an already-deleted job succeeds without error and without duplicate effects (DEC-166).
5. The R2 lifecycle rule exists for prefix `tmp/` at the configured age and is verified automatically; objects older than the safety-net age are removed even when the active-deletion path is disabled (DEC-166).
6. Cleanup telemetry contains counts and timing only; a log-inspection test asserts no filenames, content, signed URLs, or sensitive identifiers appear (DEC-166, DEC-175).
7. Signed URL expiry never exceeds remaining time to `expires_at`, and a refreshed URL for the same result does not extend retention (DEC-170).
8. Expired results return a distinct not-found/expired response and are not restorable from server storage (DEC-067).
9. Restart recovery: killing and restarting the cleanup coordinator with pending expired tasks results in deletion completing without manual intervention (DEC-166).

## 9. Assumptions, uncertainties, and unresolved questions

- **Assumption:** R2 lifecycle rule minimum granularity is whole days and deletion is eventual (to be confirmed against the evidence file's current documentation; if finer granularity became available, the safety net could be tightened but the application remains the primary timer per DEC-166).
- **Assumption:** one bucket with a `tmp/` prefix is sufficient; the bucket name and any migration of the legacy bucket are deployment decisions requiring owner input (DEC-095).
- **Uncertainty:** lifecycle deletes' effect on R2 operation-class billing at MVP volume (see evidence file pricing); expected to be negligible.
- **Uncertainty:** the exact lifecycle delete timing lag after the condition is met; assumed acceptable because the primary path is application-driven.
- **Unresolved:** safety-net age (1 vs 2 days) — owner prompt above.

## 10. Dependencies and cross-track interfaces

- **C1:** the authoritative `expires_at` lives in Redis task records; C1 defines persistence so pending-deletion recovery works after restarts (DEC-166, DEC-174).
- **C2:** object count/size ceilings feed storage caps and signed-URL download sizing.
- **C4:** validation/sanitization occurs before upload; threat-classified objects are never uploaded beyond minimum inspection (DEC-088).
- **C5:** consumes cleanup telemetry (lag, failures, rule-present) for monitoring and alerting (DEC-182).
- **D5:** threat-blocked files and their cleanup fall under the same absolute deadline (DEC-088).
- **X1/X2:** recommendation and owner prompts feed the index and reconciliation report.

## 11. Source-date log and evidence-completeness notes

- Decisions and specifications read 2026-07-31; legacy files read 2026-07-31.
- Web evidence for R2 was researched directly (read-only official docs, `cloudflare` skill guidance) and persisted in `evidence/c3-evidence-r2.md` with per-source URLs and access date 2026-07-31. This brief's §5.2 summarizes it; exact rule syntax, versions, and pricing figures in the evidence file prevail, and any disagreement must be surfaced (DEC-183).
- Evidence-completeness: lifecycle rule capabilities (day granularity, prefix targeting, timing), presigned URL expiry bounds, and current free-tier/pricing numbers are the material items and are recorded in the evidence file.

## 12. Prohibitions-compliance statement

No prohibited action was taken: no installs, builds, containers, server starts, VPS/SSH access, deployment, provider authentication, account creation, remote mutation, writes to any live R2 bucket, or benchmark program (DEC-066, DEC-060, DEC-160, DEC-172). No source, spec, decision, or existing audit-output file was modified. All writes were confined to `audit-outputs/research/track-c/`. `papyr-reference/` was verified unchanged via read-only `git -C papyr-reference status --porcelain` (empty, exit 0) before and after this brief.
