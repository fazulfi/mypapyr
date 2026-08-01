# C1 Evidence — Python Redis Queue/Worker Frameworks

- **Access date:** 2026-07-31
- **Purpose:** primary-source evidence for `c1-queue-workers-redis.md` (framework comparison for Alternative A)
- **Method:** read-only fetch of official documentation. No installs, no live services.

## 1. arq — v0.28.0 (2026-04-16)

Source: `https://arq-docs.helpmanual.io/` (accessed 2026-07-31). License: MIT (project repo github.com/samuelcolvin/arq).

- asyncio job queue and RPC on Redis; "conceived as a simple, modern and performant successor to rq".
- **Pessimistic execution:** jobs are not removed from the queue until they succeed or fail; on worker shutdown an in-flight job is cancelled and rerun later. Docs: "sometimes *exactly once* can be hard or impossible, *arq* favours multiple times over zero times" — jobs must be idempotent.
- `Worker` settings: `max_jobs` (max concurrent jobs in one worker process, default 10), `job_timeout` (default 300 s), `keep_result` (default 3600 s), `max_tries` (default 5), `poll_delay` (0.5 s), `queue_read_limit`, `health_check_interval` (writes a Redis key with live counters: `j_complete/j_failed/j_retried/j_ongoing/queued`), `allow_abort_jobs` (default False; `Job.abort()` can cancel a queued or in-progress job), `retry_jobs`, cron support (`arq.cron`).
- Enqueue: `enqueue_job(function_name, ..., _job_id=..., _queue_name=..., _defer_by/_defer_until=..., _expires=...)`. `_expires` = "do not start or retry a job after this duration; defaults to 24 hours plus deferring time". Job IDs enforce uniqueness via a Redis transaction.
- **Serialization:** default `pickle` for job payloads; **custom serializer/deserializer supported** (docs show msgpack). The function is referenced **by name** (frontend need not import worker code).
- Status API: `Job.status()` → `JobStatus` enum: `deferred`, `queued`, `in_progress`, `complete`, `not_found`. `Job.info()`/`result_info()` include results (stored in Redis, TTL via `keep_result`).
- Retry: raise `arq.worker.Retry(defer=...)`; retries run up to `max_tries`, then permanent failure.
- Health check: `arq --check` exits 0/1 based on the health-check key.
- Version history: v0.27.0 (2026-01-30), v0.28.0 (2026-04-16) add Python 3.13/3.14 support. Docs include a prominent warning about the v0.16 rewrite.

Fit notes for C1: retry/expiry/health built in; fairness (per-origin, weighted classes) and per-origin concurrency are NOT built in and require custom logic; results stored in Redis must be minimized (keep `keep_result=0` and store only opaque refs) to satisfy DEC-174; `_expires` caps total job lifetime (align with the one-hour deadline).

## 2. RQ (python-rq.org) — Redis Queue

Source: `https://python-rq.org/` (accessed 2026-07-31, referenced pages: /docs/, /docs/patterns/).

- Simple synchronous job queue; workers are separate processes (`rq worker`); jobs enqueued with `queue.enqueue(fn, ...)`; job payloads pickled.
- Worker concurrency via `Worker(queues, ...)`; timeouts per job; retry via `Retry`; failed jobs go to a failed-job registry.
- Queue length monitoring; proration for deferred jobs.
- Synchronous worker model complicates running asyncio-native FastAPI in the same process; separate worker containers are the natural deployment.
- No built-in consumer-group semantics; a crashed worker can leave a job "in progress" until its timeout.

## 3. Celery (docs.celeryq.dev)

Source: `https://docs.celeryq.dev/en/stable/getting-started/introduction.html` (accessed 2026-07-31, referenced).

- Distributed task queue with brokers incl. Redis; `worker_prefetch_multiplier` for fairness (default 4); `task_time_limit`/`soft_time_limit`; retries (`task_max_retries`, `retry_backoff`); result backend (Redis); `visibility_timeout` for redelivery of unacked messages; queues/routing; periodic tasks (celery beat).
- Operational weight: broker + result backend + beat + worker pool tuning; significant for a single-VPS five-tool service. Visibility/redelivery semantics must be tuned to respect a hard absolute deadline.

## 4. dramatiq (dramatiq.org)

Source: `https://dramatiq.org/` (accessed 2026-07-31, referenced).

- Actor-based background processing; Redis broker; `max_retries`, `time_limit`, `queue_name`, dead-letter queue (`--pid-file`/DLQ), middleware (Prometheus etc.), rate limits per actor.
- Smaller community than Celery/RQ; same minimal-metadata discipline needed.

## 5. Plain Redis Streams consumer groups (no framework)

Sources: redis.io streams doc (see c1-evidence-redis.md §5); redis-py `redis.asyncio` documentation (`https://redis-py.readthedocs.io/en/stable/`, referenced).

- `XADD`/`XREADGROUP`/`XACK`/`XAUTOCLAIM`/`XGROUP` give at-least-once delivery, visibility via the PEL, stale-claim recovery, and ack semantics; `MAXLEN` bounds stream growth.
- A hand-rolled queue must additionally implement: per-task TTL/expiry, retry policy, dead-letter handling, fair scheduling (per-origin classes), queue-depth caps, cancellation state machine, and metrics — each small and testable.
- Atomic multi-step transitions (cancel vs claim; enqueue vs per-origin cap) via Lua scripts.

## Comparison summary

| Criterion | arq | RQ | Celery | dramatiq | Custom Streams |
|---|---|---|---|---|---|
| Current version (access date) | v0.28.0 (2026-04-16) | current docs | current docs | current docs | n/a (commands) |
| asyncio-native | yes | no | pool-based | no | yes (redis-py asyncio) |
| Built-in retry/timeout | yes | yes | yes | yes | must build |
| Consumer-group claim/reclaim | no (pessimistic re-run) | no | visibility_timeout | no | yes (PEL/XAUTOCLAIM) |
| Fair scheduling classes | no | no | partial (prefetch) | no | must build |
| Per-origin concurrency | no | no | no | no | must build |
| Payload control | custom serializer; results TTL | pickle | serializers; backend | pickle | full control |
| Ops weight | low | low | high | medium | low (own code) |

## Uncertainties

- RQ/Celery/dramatiq details above are from their official docs/reference pages; versions were not deeply re-verified beyond the access date. Material claims in the C1 brief rely on arq (verified in detail) and on framework-agnostic requirements.

## Source list

| # | URL | Accessed |
|---|---|---|
| 1 | https://arq-docs.helpmanual.io/ | 2026-07-31 |
| 2 | https://python-rq.org/ | 2026-07-31 |
| 3 | https://docs.celeryq.dev/en/stable/getting-started/introduction.html | 2026-07-31 |
| 4 | https://dramatiq.org/ | 2026-07-31 |
| 5 | https://redis-py.readthedocs.io/en/stable/ | 2026-07-31 (referenced) |
