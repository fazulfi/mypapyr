# C1 — Queue, Workers, and Redis Research Brief

| Field | Value |
|---|---|
| Brief ID | C1 |
| Path | `audit-outputs/research/track-c/c1-queue-workers-redis.md` |
| Track | C — Infrastructure and operations |
| Title | Queue, workers, and Redis research |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent, Track C Wave 1) |
| Status | Complete (draft for owner review under DEC-057) |
| Governing decisions | DEC-019, DEC-020, DEC-035, DEC-137, DEC-174; supporting: DEC-054 to DEC-060, DEC-066, DEC-069, DEC-070, DEC-071, DEC-072, DEC-073, DEC-134, DEC-162, DEC-167 |
| Spec sections served | Technical Architecture Specification §7, §8, §9, §13, §14, §25.3 items 3, 4, 5 (and partial item 9); Product and UX Design Specification §13, §21.1 |

**Files read for this brief**

- `<workspace-root>\AGENTS.md`
- `<workspace-root>\papyr-rebuild-decisions.md` (in full; DEC-019, DEC-020, DEC-035, DEC-054–060, DEC-066, DEC-069, DEC-070, DEC-071, DEC-072, DEC-073, DEC-134, DEC-137, DEC-162, DEC-174 govern this brief)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (in full; §7, §8, §9, §13, §14, §25.3)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (in full; §13, §21)
- `<workspace-root>\audit-outputs\research-program-plan.md` (§7.3, §8 template, §11 verification)
- `<workspace-root>\audit-outputs\spec-cross-review.md`
- `<workspace-root>\audit-outputs\spec-corrections-report.md`
- Legacy (read-only): `papyr-reference/backend/services/async_task.py`, `papyr-reference/backend/utils/config.py`, `papyr-reference/backend/main.py`, `papyr-reference/backend/Dockerfile.production`, `papyr-reference/deploy/docker-compose.yml`, `papyr-reference/deploy/.env.production.example`, `papyr-reference/frontend/src/hooks/useAsyncTask.ts`, `papyr-reference/backend/routers/status.py`
- Evidence files (primary evidence deliverables): `audit-outputs/research/track-c/evidence/c1-evidence-redis.md`, `audit-outputs/research/track-c/evidence/c1-evidence-queue-frameworks.md`

---

## 2. Scope

This brief resolves the queue, worker, and Redis design choices for server-side PDF processing:

- **Queue design** (DEC-019): the Redis-backed task queue replacing the legacy in-memory task store; immediate dispatch when worker capacity exists; explicitly modeled job state, progress, timeout, retry policy, cancellation, result expiry, and failure reasons.
- **Worker bounds** (DEC-019, DEC-162, DEC-169): worker count, per-worker memory and time bounds for the single-VPS Docker Compose stack, tuned from production observability rather than benchmark-proven (DEC-066, DEC-098). Architecture §25.3 item 3.
- **Queue-depth safety caps and bounded queueing** (DEC-035): valid jobs remain queued during normal capacity pressure; queue length, storage, maximum wait, job expiry, and VPS health caps are explicit. Architecture §25.3 items 3 and 9 (partial).
- **Fair scheduling** (DEC-137, DEC-134): fairness classes, concurrency bounds, starvation prevention, per-origin concurrency; no paid priority lane. Architecture §25.3 item 4.
- **Redis persistence, eviction, and recovery** (DEC-174): only minimal task metadata persists; persistence mode, eviction policy, and recovery procedure. Architecture §25.3 item 5.
- **Adaptive anonymous fair-use controls** (DEC-020): signals considered, enforcement levels, and cross-process consistency via Redis. Architecture §25.3 item 9 (partial).

The current approved Papyr behavior being designed for: the FastAPI application enqueues work and exposes durable status instead of owning long-running processing in module-global memory (DEC-019); users see real queued status with honest estimates (DEC-033); jobs are cancellable only while queued (DEC-069); jobs continue after tab close (DEC-071) and are recoverable on same-tab refresh via `sessionStorage` (DEC-072); all server-side objects obey the absolute one-hour deadline (DEC-013, DEC-070).

## 3. Non-goals

This brief does **not** cover:

- **Per-tool server limits** (bytes, pages, pixels, output counts, estimated memory): these are C2 (Wave 2), consuming A2–A6 and C1 findings (DEC-034, DEC-066).
- **R2 object lifecycle and deletion mechanics**: C3 (active deletion, lifecycle safety net, key hygiene).
- **Container and process hardening details** (non-root, capabilities, seccomp, filesystem): C4 (DEC-169). This brief only sets the *sizing* of worker bounds that C4 hardens.
- **Malware scanning selection**: C4 (DEC-171).
- **Nginx rate-limit values**: C4 (this brief sets the application-side fair-use thresholds that Nginx complements; the split of responsibilities is noted in §6).
- **Monitoring and alert thresholds**: C5 (this brief states which queue metrics must exist; C5 sets thresholds).
- **Deadline-prediction admission control**: explicitly excluded by DEC-073.
- **Queues for the removed Guinevere runtime** (BullMQ, PostgreSQL/Drizzle): excluded by DEC-016; the queue Redis here is governed by DEC-019 and DEC-174.
- **A multi-VPS or distributed queue**: excluded by DEC-098.

## 4. Research questions

Restated from plan §7.3 (C1):

1. What worker count, per-worker memory and time bounds, and queue-depth safety caps are appropriate conservative design/safety choices for a single ~8 GB / 4-core VPS (DEC-019, DEC-035, DEC-066, DEC-098)?
2. What fair-scheduling classes, concurrency bounds, and starvation-prevention parameters satisfy DEC-137 without exposing exploitable defensive detail, and without a paid priority lane (DEC-134)?
3. What Redis persistence mode, eviction policy, and recovery procedure satisfy the minimal-metadata durability requirement of DEC-174 — surviving service restarts without persisting document content — and how does the queue behave if Redis state is lost?
4. How are adaptive anonymous fair-use controls enforced consistently across multiple API processes rather than per-process counters (DEC-020), using Redis as the shared store?
5. How does the queue honor the absolute one-hour server-retention deadline (DEC-070) and queued-only cancellation (DEC-069) without deadline-prediction admission control (DEC-073)?
6. How do workers isolate processing-engine failures per tool (DEC-167) and continue independently of any client connection (DEC-071)?

## 5. Evidence

### 5.1 Legacy baseline evidence (read-only, `papyr-reference/`)

| Path and line | What it evidences |
|---|---|
| `backend/services/async_task.py:22-29` | Legacy in-memory task states `queued/processing/done/failed`; no `cancelled`, no `expired` state (DEC-019's fix target). |
| `backend/services/async_task.py:47-48` | `_tasks: dict[str, TaskInfo]` module-global store with 2-hour TTL: restart loss, cross-process inconsistency, uncontrolled fire-and-forget (DEC-019 rationale). |
| `backend/services/async_task.py:116-186` | `run_task_in_background` with `asyncio.wait_for(timeout=120)`: per-task timeout precedent (120 s), failure reasons are raw exception strings (not safe categories). |
| `backend/utils/config.py:101-103` | Legacy settings: `MAX_UPLOAD_SIZE_MB=20`, `FILE_RETENTION_MINUTES=60`, `RATE_LIMIT_PER_MINUTE=10`. |
| `backend/main.py:38-61` | Cleanup cron loop and app lifespan; in-process background work inside the API process (the pattern DEC-019 moves to workers). |
| `backend/main.py:33-84` | `slowapi` limiter with `get_remote_address`; 429 handler. Per-process in-memory counters: the pattern DEC-020 supersedes. |
| `backend/Dockerfile.production:103-134` | Non-root `appuser` (UID 1001), `tini` PID 1, healthcheck on `/health`, **4 uvicorn workers**. |
| `backend/Dockerfile.production:74-101` | Runtime native deps: ghostscript, poppler-utils, tesseract, LibreOffice (engine footprint the rebuild reduces per DEC-010). |
| `deploy/docker-compose.yml:17-24` | VPS budget comment: "8GB RAM, 4 cores total → leave 4GB + 0.5 core for system + Nginx"; backend limits `cpus: 3.5`, `memory: 4G`, reservation 1G. |
| `deploy/docker-compose.yml:27-64` | Hardening baseline: `read_only: true`, `no-new-privileges`, `cap_drop ALL`, tmpfs, read-only env mount, internal `expose`, no published backend port. |
| `deploy/.env.production.example:22-25` | `RATE_LIMIT_PER_MINUTE=10`, `MAX_UPLOAD_SIZE_MB=20`, `FILE_RETENTION_MINUTES=60` template values. |
| `frontend/src/hooks/useAsyncTask.ts:32,167-171` | Legacy polling: 3000 ms interval, 180000 ms client timeout, `GET /status/{task_id}`. |
| `backend/routers/status.py:17-29` | Legacy `/api/status/{task_id}` returning 404 "Task not found" for unknown/expired tasks. |
| `docs/runbook-vps.md:5.1` | OOM precedent: containers exit 137; 4.5 GB swap; restart as immediate relief. |
| `docs/runbook-vps.md:1,6` | VPS: "Linode Jakarta (via IDCloudHost)", IPv4 `<vps-ip>` (legacy host; no current access authorized — DEC-172, DEC-160, DEC-066). |

Legacy VPS resource basis (for sizing): 8 GB RAM, 4 vCPU, 4.5 GB swap (runbook §5.1; compose comment at `deploy/docker-compose.yml:17`). These are legacy deployment observations, not measured benchmarks; all sizes below are conservative design/safety recommendations (DEC-066).

### 5.2 Primary web sources (official documentation; access date 2026-07-31)

Current authoritative Redis and queue-framework sources are collected in the evidence files `evidence/c1-evidence-redis.md` and `evidence/c1-evidence-queue-frameworks.md` (research primary deliverables, access date 2026-07-31). Verified facts applied in this brief:

- **Redis version:** Redis Open Source **8.8** is the current open-source release per `https://redis.io/downloads/` (accessed 2026-07-31); official docs also reference newer features (LRM eviction in 8.6, the `BACKUP` command family in 8.10), so the exact pinned minor version is confirmed at implementation.
- **Persistence:** RDB, AOF, both, or none. AOF `appendfsync everysec` is "the suggested (and default) policy" and bounds loss to ~1 second of writes; combining AOF + RDB is the general recommendation for PostgreSQL-comparable durability (`https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/`).
- **Eviction:** `noeviction` — "Keys are not evicted but the server will return an error when you try to execute commands that cache new data"; read-only commands keep working. `volatile-ttl` evicts keys with the shortest remaining TTL and behaves like `noeviction` if no keys have expirations (`https://redis.io/docs/latest/develop/reference/eviction/`).
- **TTL/expiry:** expiration is a background+lazy process, not a precisely-timed boundary; the application must remain the authoritative enforcer of the one-hour absolute deadline (DEC-070), with Redis TTL as a complementary bound (DEC-174).
- **Streams:** consumer groups (`XGROUP CREATE`, `XREADGROUP`, `XACK`, `XAUTOCLAIM`, `XNACK` in 8.2+, PEL, `MAXLEN` trimming) provide at-least-once delivery, visibility, and stale-claim recovery; Redis Lists (`LPUSH`/`BRPOP`) are the simpler FIFO primitive without consumer-group semantics; sorted sets serve as a weighted-fair-queue primitive (`https://redis.io/docs/latest/develop/data-types/streams/`).
- **Atomicity:** Lua scripts (`EVAL`) run atomically and are the recommended mechanism for multi-step state transitions; `MULTI`/`EXEC`/`WATCH` are the transaction alternatives (`https://redis.io/docs/latest/develop/programmability/`, `/develop/reference/transactions/`).
- **Security:** `requirepass`, ACLs, TLS, and `protected-mode` are documented; a queue Redis is never publicly exposed (DEC-162).
- **Framework comparison:** arq is current at **v0.28.0** (2026-04-16) with pessimistic execution (jobs may run more than once — idempotency required), built-in `job_timeout`/`max_tries`/`_expires`/health checks, and pickle-by-default serialization with a custom-serializer option; RQ, Celery, and dramatiq are documented in the evidence file; fair scheduling and per-origin concurrency are not built into any of them (see evidence file).

## 6. Alternatives

### Alternative A — Existing Python Redis queue framework (arq / RQ / Celery / dramatiq)

- **What it is:** adopt a maintained framework that already implements claim/ack, retries, timeouts, and failure handling over Redis.
- **Trade-offs:**
  - *arq*: asyncio-native (fits FastAPI), built-in job timeouts, retries, `max_jobs` concurrency, healthchecks; but it serializes job payloads with pickle/msgspec and stores function references, needs explicit controls to keep payloads to opaque IDs only, and fair-scheduling classes/per-origin concurrency are not built in (requires custom middleware or pre-queue logic). Restart behavior is decent (queued jobs survive with persistence).
  - *RQ*: simple, synchronous workers, separate worker processes, failed-job registry; but synchronous workers complicate engine isolation from the asyncio API process, prefetch/fairness are minimal, and pickled job data again must be restricted to minimal metadata.
  - *Celery*: mature, rich features (prefetch multiplier, visibility timeout, result backend, queues); but it is heavy for a single-VPS five-tool service, adds broker/result-backend operational surface, and its redelivery/visibility model needs careful tuning to honor a hard absolute deadline.
  - *dramatiq*: actor model, DLQ, middleware; smaller community than Celery/RQ; same minimal-metadata discipline needed.
- **Risks:** framework serialization may inadvertently persist payload content (violating DEC-174 unless tightly constrained); fairness classes (DEC-137) and per-origin concurrency (DEC-020) are not provided out of the box; each framework's retry/backoff semantics can conflict with the absolute one-hour deadline (DEC-070) and with the "no artificial waiting period" rule (DEC-019).
- **Cost/operational impact:** lowest implementation cost initially (battle-tested claim/retry code); moderate-to-high integration cost to bolt on fair scheduling and metadata minimization; Celery adds notable operational weight.
- **Privacy/security:** frameworks store whatever payload you hand them; with payloads limited to opaque task IDs + minimal routing metadata, the surface is acceptable, but the framework's own result/error storage must be audited against DEC-174 and DEC-175.

### Alternative B — Minimal custom queue over Redis Streams with consumer groups (recommended)

- **What it is:** a thin internal queue layer (own code) using Redis Streams consumer groups (`XADD`/`XREADGROUP`/`XACK`/`XAUTOCLAIM`) with a Lua-scripted atomic claim/cancel transition, storing only the fields DEC-174 permits: opaque `task_id`, `tool`, processing route, state, timing, `expires_at`, and non-sensitive temporary object references. A companion sorted-set or hash-based fair-use counter store provides per-origin concurrency and sliding-window frequency limits.
- **Trade-offs:**
  - Full control over what is persisted (the payload schema is defined in code and asserted by tests), satisfying DEC-174 directly.
  - Full control over fairness: per-origin concurrency caps, fairness classes, maximum-wait enforcement, and stale-job expiry (DEC-137, DEC-035) are implemented as small, testable units.
  - Explicit alignment with the absolute one-hour deadline: `expires_at` is authoritative; TTL is complementary; signed-URL expiry derives from remaining time (DEC-170, DEC-070).
  - Immediate dispatch with no artificial wait: workers `XREADGROUP` with short block; `XAUTOCLAIM` reclaims stuck claims (DEC-019, DEC-071).
  - **Cost:** the team owns claim/ack/retry/DLQ correctness; mitigated by the small state machine (queued/processing/done/failed/cancelled + expiry), heavy functional tests, and the fact that a lost job is bounded by the one-hour window and the R2 lifecycle safety net (DEC-166).
- **Risks:** hand-rolled queues are a classic correctness trap; mitigated by: (1) using Redis Streams consumer groups (battle-tested visibility/claim semantics rather than inventing them), (2) Lua-scripted state transitions for atomicity, (3) an explicit dead-letter/`processing`-stuck reclaim path (`XAUTOCLAIM` with a stuck threshold), and (4) bounded blast radius: at most one job is duplicated on worker crash, and duplicate result uploads are idempotent by object key.
- **Privacy/security:** payload minimization is structural (fields allow-listed); no pickle of arbitrary objects; Lua scripts are the only multi-step atomic paths and are reviewed.
- **Cost/operational impact:** modest implementation cost; low runtime weight; the queue is fully observable (queue length, wait time, exec time, failures, retries, stuck jobs per DEC-019) because the team writes the metric hooks.

### Alternative C — Redis Lists (`LPUSH`/`BRPOP`) simple FIFO with separate state hashes

- **What it is:** the classic Redis list queue; state kept in per-task hashes with TTL.
- **Trade-offs:** simplest possible queue; but BRPOP gives no built-in visibility timeout or consumer-group claim (a worker crash hides an item until the queue is re-injected), no ack, and fairness requires building the same machinery as B on top of sorted sets — effectively paying B's cost without B's primitives. Considered and rejected for the crash-recovery and fair-scheduling requirements (DEC-019, DEC-035, DEC-137).

## 7. Recommendation

**Recommendation (not an accepted decision):** adopt **Alternative B — a minimal custom queue over Redis Streams consumer groups** for the Papyr rebuild, with the following conservative design/safety values:

- **Worker count and bounds.** Two worker container replicas, each executing **one job at a time** (no intra-process fan-out), for 2 concurrent PDF jobs on the VPS. Rationale: native PDF engines (Ghostscript-class) are memory- and CPU-heavy; a single huge job must not monopolize memory; 4 uvicorn API workers remain as the admission/status layer (legacy precedent `Dockerfile.production:134`). Per-worker container bounds: `memory: 2G` limit, `cpus: 1.5`, tmpfs workspace bound to a per-job ceiling (concrete per-tool disk ceilings are C2). Default per-job execution timeout: **180 s** (extends the legacy 120 s precedent to cover heavier engine work) with per-tool overrides defined in C2; a job that exceeds its timeout fails with a safe category, never retries in a loop (DEC-019, DEC-065). These are conservative defaults documented as design choices, adjusted from production observability (DEC-066, DEC-098).
- **Queue-depth safety caps** (hard operational caps, DEC-035): maximum queue length **2000 queued jobs**; maximum wait **15 minutes** (jobs exceeding it are failed with a clear retryable error); per-origin cap **4 concurrent queued+processing jobs** per origin fingerprint; global admission pause when Redis memory pressure or worker health degrades. Job records carry TTL = time to `expires_at` (never longer), complementing the application-authoritative deadline.
- **Fair scheduling** (DEC-137, DEC-134): fairness classes are **per-origin** (the anonymous substitute for user identity under DEC-012 and DEC-020), with a small number of weighted classes (e.g., ordinary jobs weight 1; retried jobs weight 1; no paid class). Concurrency bounds: per-origin cap (above) and global concurrency 2 (worker count). Starvation prevention: maximum-wait bound (above), stale-claim reclaim via `XAUTOCLAIM`, and per-origin round-robin so one origin cannot monopolize the global slots. No job is ever prioritized by payment (DEC-134).
- **Redis persistence.** AOF enabled with `appendfsync everysec`, RDB snapshots retained as a secondary recovery aid; a named volume for `/data` on the host stack. Justification: task metadata must survive API/worker restarts (DEC-019, DEC-174); ≤1 s of task-state loss on crash is acceptable because in-flight work is bounded by timeouts and the R2 lifecycle safety net enforces the one-hour ceiling (arch §8.4, DEC-166). Data-minimization is structural: the persistence file then contains only minimal metadata.
- **Eviction policy.** `maxmemory` set (e.g., 384 MB) with **`noeviction`**: every key has a TTL, valid tasks must never be silently evicted before their lifecycle, and OOM writes fail loudly to the monitored error path rather than corrupting queue integrity.
- **Recovery procedure.** Health checks (`redis-cli ping`) gate API/worker startup (`depends_on: condition: service_healthy`, legacy pattern `docker-compose.yml:113-115`); restart behavior documented in the runbook; if Redis state is lost, in-flight jobs fail within their timeouts, Redis record TTLs mean no stale tasks linger, and the R2 lifecycle safety net still enforces the one-hour ceiling (arch §8.4).
- **Cross-process fair-use consistency (DEC-020).** Redis is the shared counter store: sliding-window frequency counters, per-origin concurrency, queue-pressure metrics, and cost-weighted limits are read/written atomically (Lua/INCR+EXPIRE), so all API processes enforce identical decisions; enforcement levels are allow / delay (exponential backoff with clear messaging) / challenge (429 with `Retry-After`) / reject (with safe category), applied **before** upload where possible (per-origin concurrency and frequency) and at admission (input size/complexity vs C2 limits).
- **Deadline and cancellation mechanics.** The queue never predicts completion (DEC-073): admission rejects only when caps are exceeded; jobs that cannot complete before `expires_at` fail with a clear, safe, localized error (DEC-070, DEC-033). Cancellation (queued only) is a Lua-scripted atomic transition `queued → cancelled` that prevents worker pickup; if a worker already claimed, the UI reports cancellation unavailable (DEC-069).
- **Failure isolation per tool (DEC-167).** Workers are tool-parametric (the same worker binary runs tool-specific engine entrypoints behind a per-tool readiness flag stored in Redis), so an unhealthy engine disables only its tool's admission and the public status shows general per-tool availability (C5).

**Owner decision prompts (not silently decided here):** (1) whether the owner prefers a maintained framework (Alternative A) over the custom stream-based queue despite the DEC-174 fairness integration cost; (2) the specific worker-count budget (2 replicas × 1 job) versus 3 replicas on the 4-core VPS, trading engine headroom against concurrency; (3) whether 384 MB `maxmemory` for Redis is the right budget given queue-depth caps.

## 8. Measurable acceptance criteria

Functional (no benchmark wording; DEC-066):

1. A job enqueued while a worker is idle is claimed without an artificial waiting period; the state machine transitions `queued → processing → done` with authoritative timestamps and an authoritative `expires_at` (DEC-019, DEC-033, DEC-070).
2. Cancellation of a queued job atomically prevents worker pickup and marks `cancelled`; a cancel racing a claim resolves to exactly one terminal outcome (DEC-069). Verified by a deterministic race test.
3. A worker that crashes while processing is reclaimed via `XAUTOCLAIM` after the stuck threshold and either completes idempotently or fails with a safe category; no job is lost without a bounded duplicate at most once (DEC-019, DEC-071).
4. Queue caps are enforced: queue length cap, maximum-wait bound, and per-origin concurrency cap each reject or fail jobs with clear, retryable, machine-readable responses (DEC-035, DEC-020, DEC-165).
5. Redis state loss (delete volume) is simulated in a test environment: in-flight jobs fail within their timeouts, no task record survives beyond its TTL, and the R2 lifecycle safety net independently deletes all objects by the absolute deadline (arch §8.4, DEC-166).
6. Redis `AOF`/RDB persistence files contain **no** file contents, filenames, passwords, signed URLs, previews, extracted content, or unnecessary document metadata (DEC-174); a dump-parsing test asserts the allow-listed field set.
7. Fair-use decisions are identical across ≥2 API processes when the same Redis state is presented (DEC-020); verified by an integration test with two API workers.
8. A task that cannot finish before `expires_at` fails with a safe localized category; no completion-time guarantee is ever presented (DEC-070, DEC-073, DEC-033).
9. Queue metrics exist and are exported for C5: queue depth, wait time, execution time, failures, retries, stuck claims, per-tool readiness (DEC-019, DEC-035, DEC-167).
10. Redis and worker health checks are wired into the Compose stack and gate API/worker startup (DEC-162, DEC-019).

Operational (documented, not benchmarked):

- A runbook section documents Redis persistence, eviction, restart, and recovery procedures and the behavior when Redis state is lost (DEC-019).
- Per-worker memory/CPU limits and per-job timeouts are declared in executable Compose configuration, adjustable only through the documented operational override path (DEC-160, DEC-097, DEC-066).

## 9. Assumptions, uncertainties, and unresolved questions

- **Assumption:** the VPS remains an ~8 GB / 4-core host with ~4.5 GB swap (legacy evidence: `deploy/docker-compose.yml:17`, `docs/runbook-vps.md:5.1`). No current VPS access exists to verify this (DEC-172, DEC-160); the budget must be re-verified before first deployment.
- **Assumption:** per-tool engine memory/CPU profiles (C2) fit within the per-worker 2 GB / 180 s bounds; if an engine cannot, the bound or the tool's limits must change through the documented raising procedure (DEC-034, DEC-066).
- **Assumption:** the C4 malware scanner (ClamAV) reserves a deliberate memory budget within the same ~8 GB envelope — the official clamd recommendation is 3–4 GiB RAM, with a documented "may get by with less" allowance; the API/worker/Redis/scanner/Netdata totals must be reconciled in design so the host never over-commits (C1 ↔ C4 interface).
- **Uncertainty:** exact queue-cap values (2000 jobs, 15 min wait, 4/origin, 384 MB Redis) are conservative design choices pending production telemetry; they are not measured (DEC-066).
- **Uncertainty:** Redis stable version and redis-py current version at the access date; the evidence files record the versions verified on 2026-07-31 and any material release notes affecting streams/persistence.
- **Unresolved:** owner preference between a maintained framework and the custom stream-based queue (see §7 prompts).
- **Unresolved:** whether `noeviction` should be paired with a Redis memory warning alert threshold (C5) rather than a hard OOM write failure as the only signal.

## 10. Dependencies and cross-track interfaces

- **C2 (Wave 2):** consumes worker bounds and queue caps from this brief; provides per-tool limits that feed admission and per-tool timeouts.
- **C3:** the `expires_at` deadline is shared with R2 active deletion; Redis TTL is complementary, never the primary timer (DEC-166).
- **C4:** this brief's worker container sizes are enforced by C4's hardening baseline (non-root, read-only fs, tmpfs, caps); C4 sets Nginx rate-limit values that complement the application fair-use controls.
- **C5:** consumes queue metrics (depth, wait, exec, failures, retries, stuck, per-tool readiness) and Redis health for monitoring and status signals.
- **A1–A6:** per-tool processing routes and engine entrypoints define the worker job schema fields (`tool`, `route`).
- **D5:** threat-blocking and validation run before enqueue; queue records never carry document data (DEC-088, DEC-174).
- **X1/X2:** this brief's recommendation and owner prompts feed the source/decision index and the reconciliation report.

## 11. Source-date log and evidence-completeness notes

- Decisions and specifications read 2026-07-31; legacy files read 2026-07-31.
- Web evidence (Redis, queue frameworks) was researched directly (read-only official docs) and persisted in `evidence/c1-evidence-redis.md` and `evidence/c1-evidence-queue-frameworks.md`, each carrying per-source URLs and access date 2026-07-31. This brief's §5.2 summarizes those files; where this brief and the evidence files disagree, the evidence files' explicit citations prevail and the discrepancy must be surfaced (DEC-183).
- Evidence-completeness: the material open items are (a) Redis current stable version and any persistence/streams changes in the 7.x/8.x series, (b) framework version/license/restart details; both are recorded in the evidence files.

## 12. Prohibitions-compliance statement

No prohibited action was taken: no installs, builds, containers, server starts, VPS/SSH access, deployment, provider authentication, account creation, remote mutation, or benchmark program (DEC-066, DEC-060, DEC-160, DEC-172). No source, spec, decision, or existing audit-output file was modified. All writes were confined to `audit-outputs/research/track-c/` (this file plus the evidence directory). `papyr-reference/` was verified unchanged via read-only `git -C papyr-reference status --porcelain` (empty, exit 0) before and after this brief.
