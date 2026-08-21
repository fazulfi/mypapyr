# Upgrade & migration path

This document describes how to move a running Papyr deployment forward
without breaking it, from the Phase 4 baseline to the Phase 5 unified
topology, and what you must never do. It is grounded in the actual deployed
assets: `deploy/docker-compose.yml`, `deploy/runbook-vps.md`, and
`backend/app/config.py`.

- [Baseline (Phase 4)](#baseline-phase-4)
- [Target (Phase 5)](#target-phase-5)
- [Upgrade order](#upgrade-order)
- [What invalidates state](#what-invalidates-state)
- [No-destructive-upgrade guard](#no-destructive-upgrade-guard)
- [Rollback](#rollback)

## Baseline (Phase 4)

- Single "undo" baseline commit `dabfbbd` ("Phase 4: Complete All Five PDF
  Tools Implementation (#21)"), which was deployed to production.
- At that commit the Compose skeleton carried `name: papyr` and declared four
  service slots — `api`, `nginx`, `redis`, `workers` — of which **only `api`**
  was activatable (`--profile app`). `nginx` and `workers` were deferred
  `__SET_ME__` placeholders and `MUST NOT` be deployed as-is
  (`deploy/runbook-vps.md`, foundation stage). There was no `cleanup` or
  `monitor`, and `/health/ready` covered only the foundation + Redis
  dependencies (the scanner dependency was added later).
- Redis was already digest-pinned and R-09-configured
  (`redis:7.4.10-alpine@sha256:…`, AOF on, `maxmemory-policy noeviction`) at the
  baseline; the persistence contract has not changed.

## Target (Phase 5)

The unified topology (Phase 5/6 baseline) consolidates the services:

- **One Compose project named `papyr-app`** (`name: papyr-app` in
  `deploy/docker-compose.yml`), one internal bridge network `papyr`.
- **Six services** behind immutable digest images:
  - `api` — profile `app`; control plane, internal `expose: "3000"`, image
    `${PAPYR_API_IMAGE:?...}`.
  - `redis` — profile `queue`; durable queue storage, digest-pinned,
    `--appendonly yes --appendfsync everysec`, `--maxmemory-policy noeviction`,
    volume `redis-data`.
  - `workers` — profile `queue`; 2 GiB / 1.5 cpus, one replica
    (`deploy: replicas: 1`), image `${PAPYR_WORKERS_IMAGE:?...}`.
  - `clamd` — profile `queue`; internal-only port 3310, image
    `${PAPYR_CLAMD_IMAGE:?...}`.
  - `cleanup` — profile `queue`; runs `python -m app.ops.cleanup_loop`, image
    `${PAPYR_API_IMAGE:?...}`, `CLEANUP_INTERVAL_SECONDS=300`.
  - `monitor` — profile `queue`; runs `python -m app.ops.monitor --watch 60`,
    image `${PAPYR_API_IMAGE:?...}`, probes `MONITOR_API_URL=http://api:3000/health/ready`.
  - `nginx` — profile `edge`; **deferred** (`nginx:__SET_ME__` placeholder),
    excluded from the app+queue activation command.
- **Project rename is the fix for the split-brain defect**: running under one
  project (`-p papyr-app`) gives one network, so the API resolves `redis` and
  `clamd` by stable in-project service DNS instead of a disconnected second
  network (`deploy/docker-compose.yml` header; `REDIS_URL=redis://redis:6379/0`
  and `CLAMD_HOST=clamd` are overridden inline in `environment:` precisely so
  the DNS names resolve across containers).
- **`/health/ready` now includes the scanner**: readiness is `ready` only when
  `foundation`, `redis`, **and** `scanner` all pass
  (`backend/app/health.py:181-201`). The worker is a `deferred` dependency and
  never probed there. `api` `depends_on` healthy `redis` and `clamd`, so the
  API container also cannot come up ready until the scanner backends are.

There are **no database migrations** in either baseline or target: this
system has **no relational database**. State lives in:

1. **Redis Streams** (task records, queue, worker group) — persisted by Redis
   AOF.
2. **Cloudflare R2 object storage** — artifact bytes under `tmp/<date>/…` with
   a hard one-hour expiration (`RETENTION_SECONDS` ceiling in
   `backend/app/config.py:35-36`).

## Upgrade order

The upgrade is **non-destructive and in place**: it recreates the affected
containers under the Phase 5 project while preserving the named volumes and
the Redis AOF. Follow this exact order:

```bash
# 1. Export session-only deploy variables (never stored in source):
#    the provisioned env file and the immutable digest image references.
export PAPYR_ENV_FILE=/opt/mypapyr/production/.env
export PAPYR_API_IMAGE=registry/papyr-api@sha256:<new-digest>
export PAPYR_WORKERS_IMAGE=registry/papyr-workers@sha256:<new-digest>
export PAPYR_CLAMD_IMAGE=registry/clamav@sha256:<new-digest>

# 2. Pull the new immutable images (never a mutable tag; :latest is rejected).
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml pull
#    Run check-compose.sh first to catch floating tags / placeholder images:
bash scripts/check-compose.sh

# 3. Structural validation — Compose refuses to proceed on twins: it rejects
#    an unset/empty/missing PAPYR_ENV_FILE and any non-digest image var.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml config --quiet

# 4. Activate per profile, app first, then queue.
#    --profile app starts ONLY api. --profile queue starts redis + workers +
#    clamd + cleanup + monitor. nginx (edge) stays deferred.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml --profile app up -d

# 5. Verify the control plane before activating the workers on the queue.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml exec api \
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=5)"
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml exec api \
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health/ready', timeout=5)"

# 6. Activate the queue profile: redis, workers, clamd, cleanup, monitor.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml --profile app --profile queue up -d
```

`--profile app` **alone is not production-ready**: it starts api only, with no
redis/worker/scanner, so `/health/ready` reports `not_ready`
(`deploy/docker-compose.yml` profile activation safety header). The full
stack is app **and** queue. Monitor (read-only) and cleanup are included in
the queue profile; both use `PAPYR_API_IMAGE` for their image and read the
API's `backend/app/ops/*` modules.

### Why app before queue

`api`, `workers`, and `monitor` all `depends_on` healthy `redis` and `clamd`,
so Compose starts the backends first regardless. Ordering app before queue in
the operator procedure is about *safe sequencing*: bring the control plane up
on the new image while the previous queue is still quiescent, confirm
`/health` and `/health/ready` are green, then activate the consumer side. If
you activate both at once, a worker image defect surfaces at the same moment
as an API defect; two unknowns in one window make first response harder.

### Verify health after each step

- `GET /health` → `200 {"status":"ok"}` (liveness; `backend/app/main.py:86-88`).
- `GET /health/ready` → `200 {"status":"ready","checks":{"foundation":"ok","redis":"ok","scanner":"ok"},"deferred":["worker"]}`.
  Any of the three checks failing yields `503` with `status: "not_ready"` and
  the failing check reported as `missing_required_config` /
  `unavailable` (`backend/app/health.py`).
- `docker compose ... ps` shows the api container `healthy`.
- After queue activation, `docker compose ... ps` shows `workers`, `clamd`,
  `redis` healthy; `cleanup` and `monitor` run a bounded loop (their compose
  health checks probe `/health` for the api, `:8000/health` for the worker).

## What invalidates state

- **Redis AOF persistence is preserved** across the upgrade. The `redis-data`
  volume is named and unchanged, and the `redis` service keeps
  `--appendonly yes --appendfsync everysec` plus the noeviction policy
  (`deploy/docker-compose.yml`, redis service). Upgrading the API/worker
  images **does not** drop the queue or task records, and in-place `up -d`
  recreates containers without deleting volumes.
- **No database migrations exist or are required.** There is no DBMS in the
  stack; this is a stated fact, not an omission. If a future phase introduces
  a database, it needs its own migration and recovery plan — it is out of
  scope here.
- **R2 objects expire by retention, not by migration.** Retention is bounded
  at **3,600 seconds** (`backend/app/config.py:35`, `RETENTION_SECONDS`
  ceiling, `deploy/.env.production.example`). Application cleanup
  (`backend/app/ops/cleanup_loop`) deletes expired task records and objects
  idempotently; `deploy/r2-lifecycle.json` declares an R2 lifecycle that
  expires the `tmp/` prefix after 1 day as a further safety net. Nothing in
  an upgrade needs to replay or migrate artifact bytes.
- **Object-format changes require a compatibility plan.** If the R2 key
  scheme (`tmp/<YYYY-MM-DD>/<32-hex><safe-ext>`, `backend/app/utils/r2.py`)
  or the worker output format changes, in-flight artifacts uploaded under the
  old format become unreadable by a new worker or unreachable by the download
  router. Because objects are hard-expired hourly, no long-lived migration is
  needed, but a short-window compatibility check (old-worker drains the
  remaining queue, or the new image accepts the old format) must be planned.
- **Unconsumed environment knobs do not invalidate state**, but overrides of
  contract axes do: `MAX_WAIT_SECONDS`, `MAX_QUEUE_LENGTH`,
  `MAX_CONCURRENT_PER_ORIGIN`, `DEFAULT_TIMEOUT_SECONDS`, and
  `RETENTION_SECONDS` are advertised truthfully to clients in the
  `/api/v1/capabilities` contract
  (`backend/app/routers/capabilities.py:406-423`), so a runtime override
  changes the advertised limits without any data loss.

## No-destructive-upgrade guard

The upgrade is designed to fail **closed**, never partially mutate state:

- Compose refuses to load when `PAPYR_ENV_FILE` is unset, empty, or missing
  (`${PAPYR_ENV_FILE:?...}` on `env_file` in `deploy/docker-compose.yml`).
- `pull`/`up` fail at image resolution if `PAPYR_API_IMAGE`,
  `PAPYR_WORKERS_IMAGE`, or `PAPYR_CLAMD_IMAGE` is not a real digest reference
  (`${...:?...}` with no default; `scripts/check-compose.sh` rejects floating
  tags and mutable fallbacks).
- `--profile app` activates only the api; `--profile queue` never leaks the
  queue services into an API-only command. nginx (`edge`) is never activated
  by either.
- The committed `.env.production.example` carries **empty** required values
  so an accidental load fails fast at boot instead of booting with
  placeholder credentials (`backend/app/config.py` rejects empty required
  vars; `deploy/.env.production.example` "Foundation required settings").
- No `down`, no `volume rm`, no destructive rebuild is ever part of the
  upgrade. Containers are recreated in place; the `redis-data` volume persists.

## Rollback

Rollback is the mirror of the upgrade with the **previous healthy digest**
(re-run `pull` + `config --quiet` + `up -d`), exactly as documented in
`deploy/runbook-vps.md`:

```bash
export PAPYR_API_IMAGE=registry/papyr-api@sha256:<previous-digest>
export PAPYR_WORKERS_IMAGE=registry/papyr-workers@sha256:<previous-digest>
export PAPYR_CLAMD_IMAGE=registry/clamav@sha256:<previous-digest>
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml config --quiet
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml --profile app --profile queue up -d
```

Retain the previous pinned image set and reviewed configuration so rollback
is a re-up, never a rebuild. Because Redis AOF and the R2 lifecycle are
unchanged, rollback does not lose in-flight work beyond the hourly retention
window — the queue and task records ride through the image swap.
