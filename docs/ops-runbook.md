# Operations & observability runbook

Ground truth for operating Papyr's backend: the bounded ops entrypoints, the
readiness contract, the eight monitor probes, log provenance, incident
response, and the (documented, not provisioned) alert wiring. Every command
and JSON shape below is grounded in files under `backend/app/`.

- [Entrypoints & how to run them](#entrypoints--how-to-run-them)
- [Monitor report & exit codes](#monitor-report--exit-codes)
- [The eight probes](#the-eight-probes)
- [Logs: location, rotation, retention, sanitization](#logs-location-rotation-retention-sanitization)
- [Incident response checklist](#incident-response-checklist)
- [Alert wiring (placeholders)](#alert-wiring-placeholders)

## Entrypoints & how to run them

All three run inside the `api` image (`backend/Dockerfile.production` hosts
the `backend/app/ops/*` and `backend/app/worker/*` modules). In compose they
are long-running services; locally they are `python -m` modules.

### Health & readiness (served by the api service, port 3000)

- `GET /health` → `200 {"status":"ok"}` liveness (`backend/app/main.py:86-88`).
- `GET /health/ready` → `200 ready` / `503 not_ready`
  (`backend/app/health.py`). Readiness is **additive**: `foundation` (the five
  required env vars load), `redis` (task-store ping), and `scanner` (ClamAV
  `CLEAN` verdict) must all pass. The worker is in `deferred: ["worker"]`
  and never probed. Compose `api` depends on healthy `redis` and `clamd`, so
  a down scanner or Redis prevents `/health/ready` from ever being green.

### `python -m app.ops.monitor [--watch SECONDS]`

Bounded production monitor — one-shot or a fixed-interval watch loop
(`backend/app/ops/monitor.py`, `main` at `:507-535`).

- No `--watch`: run all eight checks once, print the full JSON report
  (with `indent=2`), exit `0` if healthy/degraded, `1` if `failed`.
- `--watch SECONDS`: run all checks immediately, then again every `SECONDS`,
  printing one compact JSON line per run (`flush=True`); SIGTERM/SIGINT stops
  cleanly; exit `0`.
- `--watch` with a non-numeric value prints usage to stderr and exits `2`.
- If the monitor cannot even be built (config error — missing required env
  var or unusable setting), it prints a single `{"status":"failed","error":"<ExcName>"}`
  JSON line and exits `2`.
- Compose runs it as `python -m app.ops.monitor --watch 60` with
  `MONITOR_API_URL=http://api:3000/health/ready` (`deploy/docker-compose.yml`,
  monitor service).

**Exit codes:**

| code | meaning |
| ---- | ---- |
| 0 | run completed; report status is `healthy` or `degraded` |
| 1 | run completed; report status is `failed` (at least one probe `fail`) |
| 2 | configuration/build error (see `monitor.py:515-522`) — the monitor could not run |

### `python -m app.ops.cleanup_loop [--once] [--dry-run] [--watch SECONDS]`

Dedicated bounded scheduler for expired-task cleanup
(`backend/app/ops/cleanup_loop.py`, `main` at `:253-276`).

- No flags: run continuously on the configured interval
  (`CLEANUP_INTERVAL_SECONDS`, default **300 s**) until signaled.
- `--once`: run a single pass and exit (returns `1` if the pass failed).
- `--dry-run`: report what would be cleaned without deleting (combined with
  `--once` or the loop).
- `--watch SECONDS`: override the interval (must be numeric; error → stderr +
  exit `2`).
- Each pass prints one JSON line. Success:
  `{"pass":"ok","outcome":…,"cleaned":…,"examined":…,"elapsed_ms":…}`; a failed
  pass prints `{"pass":"failed","error":"unavailable"}` (`cleanup_loop.py:190-207,240-243`).
- A missing required env var (`_build_runtime`) prints
  `{"error":"missing_env","field":…}`, an invalid setting
  `{"error":"invalid_setting","message":…}`, other init errors
  `{"error":"init_error"}` — all exit `2` (`:211-225`).
- Compose runs it as `python -m app.ops.cleanup_loop` with
  `CLEANUP_INTERVAL_SECONDS=300` (`deploy/docker-compose.yml`, cleanup service).

### `python -m app.worker`

Production worker — the bounded one-job loop that consumes the Redis Streams
queue (`backend/app/worker/__main__.py` → `entrypoint.main`:
`backend/app/worker/entrypoint.py:233-241`).

- Loads settings fail-fast, installs SIGTERM/SIGINT handlers, builds the
  worker + a loopback-only HTTP health server.
- Worker health: `GET /health` on `WORKER_HEALTH_PORT` (default **8000**)
  → `200 {"status":"ok"}` healthy, `503 {"status":"degraded"}` otherwise
  (`entrypoint.py:64-68`). Compose `workers` healthcheck probes
  `http://127.0.0.1:8000/health`.
- Degradation (Redis/queue unavailable, `WorkerUnavailableError`) is logged
  and the loop keeps trying — it never crashes the container
  (`entrypoint.py:192-216`).

## Monitor report & exit codes

The monitor aggregates the **eight** production checks
(`monitor.py:331-369`). Overall status is `healthy` (all `ok`), `degraded`
(any `warn`, none `fail`), or `failed` (any `fail`). Report shape
(`monitor.py:96-115`):

```json
{
  "status": "healthy",
  "generated_at": "2026-08-13T10:00:00+00:00",
  "checks": [
    {"name": "api_ready", "status": "ok", "details": {"status_code": 200}},
    {"name": "redis", "status": "ok", "details": {}},
    {"name": "clamd", "status": "ok", "details": {}},
    {"name": "queue_backlog", "status": "ok", "details": {"count": 12}},
    {"name": "queue_pel", "status": "ok", "details": {"pending": 0, "oldest_idle_ms": 0, "group_exists": true}},
    {"name": "worker_health", "status": "ok", "details": {"group_exists": true, "pending": 0, "oldest_idle_ms": 0, "worker_probe": "ok"}},
    {"name": "cleanup_freshness", "status": "ok", "details": {"age_seconds": 18}},
    {"name": "r2_ops", "status": "ok", "details": {}}
  ],
  "summary": {"ok": 8, "warn": 0, "fail": 0}
}
```

Each `CheckResult` is `{name, status, details}` where `status` ∈
`ok|warn|fail` (`monitor.py:86-93`). The report dtype prints `generated_at`
with second precision and a `summary` count. See exit-code table above for
how the process code maps to the report.

## The eight probes

Check names and their exact conditions are implemented in
`backend/app/ops/monitor.py`. Defaults: `MONITOR_API_URL=http://api:3000/health/ready`,
timeout 5 s, queue warn 1000 / fail 1800, PEL fail count 16, PEL idle fail
900000 ms, cleanup max age 3600 s (`monitor.py:41-47`). Thresholds are
overridable via `MONITOR_API_URL`, `MONITOR_QUEUE_WARN`, `MONITOR_QUEUE_FAIL`,
`MONITOR_PEL_FAIL_COUNT`, `MONITOR_PEL_IDLE_FAIL_MS`,
`MONITOR_CLEANUP_MAX_AGE_SECONDS`, `MONITOR_WORKER_HEALTH_URL`
(`monitor.py:451-479`).

| # | Check | What it verifies | Fails when | First response when unhealthy |
| --- | --- | --- | --- | --- |
| 1 | `api_ready` | `GET /health/ready` returns 200 and body `status == "ready"` (`:130-145`) | non-200, unparseable body, or non-`ready` status | Is the api container up (`compose ps`)? Are `redis` and `clamd` healthy (`compose ps`)? Check api logs for readiness detail. |
| 2 | `redis` | `redis.ping()` succeeds (`:148-155`) | ping raises or client not configured | `compose up -d redis`; check Redis logs for crash/eviction; AOF recovery if it lost data. |
| 3 | `clamd` | TCP connect + `zPING` → reply starts `PONG` (`:158-175`) | connect fails, timeout, or non-PONG reply | `compose up -d clamd`; check clamd logs and the clamd-db volume; the daemon must answer PING→PONG on 3310. |
| 4 | `queue_backlog` | stream `XLEN jobs` against warn/fail thresholds (`:178-194`) | `count ≥ 1800` → fail; `≥ 1000` → warn | Are workers running (`compose ps`)? Did the worker crash or stop claiming? Watch worker logs. |
| 5 | `queue_pel` | pending entries in group `workers` — count and oldest idle (`:213-230`) | `pending > 16` or `oldest_idle_ms > 900000` (or group missing errors) | Stuck/in-flight jobs: is a worker crashed mid-claim, or an engine hung? XAUTOCLAIM recovery window; restart `workers`. |
| 6 | `worker_health` | group exists + no PEL older than the idle cap; optional worker `/health` probe (`:233-263`) | group missing, oldest idle too old, or worker probe non-ok | Worker process unhealthy (`curl :8000/health` → 503/degraded); restart `workers`; check for `WorkerUnavailableError` in logs. |
| 7 | `cleanup_freshness` | cleanup marker `last_outcome == "ok"` and age ≤ 3600 s (`:266-289`) | marker absent, `last_run_failed`, unparseable timestamp, or `age_seconds > 3600` | Is the `cleanup` container running? If stale, expired artifacts are accumulating beyond the hard 1-hour retention — restart cleanup; verify a pass prints `{"pass":"ok"}`. |
| 8 | `r2_ops` | read-only R2 probe: `list_objects_v2` on `tmp/` MaxKeys=1, never mutates (`:292-297,372-385`) | probe throws, or R2 client not configured | R2 credentials/endpoint (see `config.py`), network to Cloudflare R2; check api/cleanup logs for `StoreUnavailableError`. |

`queue_pel` and `worker_health` both draw on the same pending-summary
(`_pending_summary`, `:197-210`); NOGROUP (group not yet created) is not a
failure for `queue_pel` (it reports `ok` with `group_exists: false`) but IS a
failure for `worker_health` (`:251-252`) — if the group exists but PEL idle
exceeds the cap, both fail.

## Logs: location, rotation, retention, sanitization

- **Driver**: every compose service uses `json-file` with
  `max-size: 10m` and `max-file: 3`
  (`deploy/docker-compose.yml`, each service `logging:` block). Per service:
  `api` 512M, `nginx` 256M, `workers` 2G, `clamd` 2G, `cleanup` 256M,
  `monitor` 256M, `redis` 768M.
- **Rotation**: Docker `json-file` rotates at 10 MiB per file, keeping 3 files
  (≈30 MiB per service) with labels `com.papyr.service=<name>`. `docker
  compose logs <service>` reads the JSON-backed stream; host-level rotation
  (logrotate on `/var/lib/docker/containers/*/*.json`) is a deployment scope
  decision covered by the runbook ("apply bounded log rotation",
  `deploy/runbook-vps.md`).
- **Format**: backend app logs are one redacted JSON line per record
  (`backend/app/utils/logging.py`), installed by `setup_logging(settings.log_level)`
  in `main.py:78`. uvicorn runs with `--no-access-log`
  (`backend/Dockerfile.production` CMD): task ids in status/download paths are
  capability tokens, so access records are never emitted.
- **Sanitized-diagnostics rule**: do **not** paste credentials or
  document-derived data into diagnostics (`deploy/runbook-vps.md`, Operations).
  Enforced in code by `redact()` + the sensitive-stem redactor
  (`utils/logging.py:28-50,62-86`): key stems won't prevent
  `authorization`, `cookie`, `password`, `secret`, `token`, `filename`,
  `content`, `objectkey`, `signedurl`, `url`, `key` from being redacted to
  `[REDACTED]` or scrubbed — fail closed on any match
  (`utils/logging.py:67-86`). The error envelope embeds request ids but never
  payload details (`errors.py:196-214`).

## Incident response checklist

- **Backend (api) outage** — browser tools stay up. The FastAPI control plane
  serves the tool pages' `/api/v1` calls; if `api` is down, `GET /health`
  fails and `compose --profile app up -d` recreates it. Admission (upload +
  enqueue) is unavailable during the outage, but the **frontend static site
  is not served by the backend**; it runs separately (Vercel/self-hosted Next). An
  api outage means tools stop accepting new tasks and polling status fails,
  but the site shell is unaffected. Restore: `compose --profile app up -d`,
  verify `/health` → `/health/ready` green, then re-check queue so workers
  resume the pending stream.
- **Redis outage** — admission fails closed. Every task-store read (status,
  download) and write (enqueue) reads Redis; `redis_ready` fails →
  `/health/ready` 503, and enqueue raises `StoreUnavailableError` → the
  stable 503 envelope. Redis runs with AOF (`--appendonly yes`) and
  noeviction; on restart it replays the AOF. No new tasks are accepted until
  Redis is healthy again. Because admission is fail-closed, a Redis outage
  never yields half-written tasks. Restore `redis`, then verify `workers`
  and `queue_pel` recover (in-flight jobs are XAUTOCLAIM-ed).
- **Worker outage** — tasks queue up but never process: `queue_backlog` and
  `queue_pel` climb; `worker_health` fails. Admission still works (202), so
  the queue grows toward `queue_full` under load. Restart `workers`
  (`compose --profile queue up -d workers`); monitoring catches it via probes
  4–6.
- **Scanner/clamd outage** — admission and readiness both fail closed: the
  scanner gate rejects uploads with 429 (`scanner_unavailable`) and
  `/health/ready` reports `scanner: unavailable`. Fix clamd (probe 3), then
  admission resumes.

General triage sequence: `compose ps` → which container is unhealthy →
`compose logs <service>` (JSON, in the `10m×3` window) → correlate the error
envelope `request_id` → restart the affected service. Check the monitor's
one-line report (or `--watch 60`) for the failing probe names above.

## Alert wiring (placeholders)

**Documented, not provisioned.** Two integration seams are declared as
environment placeholders, but nothing in the repo sends alerts yet
(`integrations.md`): Sentry and Telegram are "environment contract only."

- `SENTRY_DSN=__SET_ME__` (root `.env.example:88`).
- `TELEGRAM_BOT_TOKEN=__SET_ME__`, `TELEGRAM_CHAT_ID=__SET_ME__`
  (root `.env.example:82-83`).

Until provisioned, incident detection is the compose `healthcheck`s +
`restart: unless-stopped` + the `monitor` service (probes 1–8, exit codes
above) + host-level alerting the operator wires out of band. Do not rely on
these placeholders for paging; treat the runbook checklist as the response
path.
