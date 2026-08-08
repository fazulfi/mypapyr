# Self-hosted deployment runbook

This document is a public template for a future, separately authorized deployment. The repository CI does not execute these steps. The feature branch introduces a unified Compose topology (profiles `app`, `edge`, `queue`) covering `api`, `nginx`, `redis`, `workers`, `clamd`, `cleanup`, and `monitor`; activating that full topology in production is a separately authorized release action described below.

## Prerequisites

- A dedicated Linux host with Docker Engine and the Compose plugin.
- A dedicated non-root service account with key-based SSH access.
- DNS, TLS, firewall, and image-registry decisions completed outside this repository.
- A real `.env.production` provisioned out of band with mode `0600` and owned by the service account. Never copy the public example: its required values are intentionally EMPTY so an accidental load fails fast at boot instead of booting with placeholder credentials.
- Version-pinned production images that have passed the release security gates (never `:latest`; `PAPYR_API_IMAGE` carries an immutable digest).

## Files

Place the reviewed release versions under a dedicated application directory:

- `deploy/docker-compose.yml`
- `deploy/nginx/conf.d/production.conf`
- `deploy/r2-lifecycle.json` (R2's one-day-minimum, day-granular lifecycle safety-net template; application cleanup remains the hard 3,600-second enforcement and the rule is applied out of band during release)
- `.env.production` provisioned from a secret manager, never copied from the public example

## Deployment variables

Export these once in the deployment session; every command below uses them.

```bash
# Path to the provisioned environment file (mode 0600, service-account owned).
export PAPYR_ENV_FILE=/opt/papyr/production/.env

# Immutable api image reference produced by the release gates (digest).
export PAPYR_API_IMAGE=registry/papyr-api@sha256:<digest>

# Full-topology release only (branch topology; separately authorized):
# immutable worker and ClamAV daemon image references (digest form).
export PAPYR_WORKERS_IMAGE=registry/papyr-workers@sha256:<digest>
export PAPYR_CLAMD_IMAGE=registry/clamav@sha256:<digest>
```

Fail-closed behavior (designed, not a regression):

- `docker compose` refuses to load when `PAPYR_ENV_FILE` is unset, empty, or points at a missing file: the api/workers/cleanup/monitor `env_file` is `${PAPYR_ENV_FILE:?...}` and the error names the variable. The committed template is never a valid env source.
- `pull`/`up` fail at image resolution when `PAPYR_API_IMAGE`, `PAPYR_WORKERS_IMAGE`, or `PAPYR_CLAMD_IMAGE` is not a real reference: each `image` is `${...:?...}` with no default, and `check-compose.sh` rejects floating tags and any mutable fallback for them.
- `--profile app` selects only the API service. `redis`, `workers`, `clamd`, `cleanup`, and `monitor` live on the `queue` profile and `nginx` on `edge`. Redis 7.4.10 is digest-pinned (`redis:7.4.10-alpine@sha256:…`) and R-09-configured; only `nginx` keeps a `__SET_ME__` image placeholder. None of the queue/edge services can be activated by the API-only commands below.
- The R2 lifecycle policy (`deploy/r2-lifecycle.json`) is verified by `bash scripts/check-r2-lifecycle.sh` but applied to the live bucket only as a separately authorized deploy-time operator action; application cleanup remains the hard 3,600-second enforcement.

## Isolated API deployment (foundation stage)

This procedure activates **only the `api` service** from the unified topology skeleton. In production, deploy only after separately authorizing the full topology with worker/ClamAV images (`PAPYR_WORKERS_IMAGE`, `PAPYR_CLAMD_IMAGE`). The queue profile remains unactivated during this foundation-stage API-only deployment until release gates pass.

```bash
# 1. Build the foundation image locally (immutable base digest is pinned in
#    backend/Dockerfile.production; tag uniquely, never :latest).
docker build --file backend/Dockerfile.production --tag papyr-api:release-candidate backend

# 2. Structural validation (no Docker daemon required).
bash scripts/check-compose.sh

# 3. Validate on a Docker-capable host.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml config --quiet

# 4. Pull only the api image (never the deferred slots).
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml pull api

# 5. Activate in an ISOLATED compose project so no legacy project is touched.
#    --profile app selects ONLY api (redis/workers are on the "queue"
#    profile); the explicit service name is the second guard.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml --profile app up -d api

# 6. Smoke: api publishes no host port (internal only); probe inside the
#    container, then confirm the compose health state.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml exec api \
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=5)"
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" -f deploy/docker-compose.yml ps
```

The deploy-time image reference must be immutable: `PAPYR_API_IMAGE` must be the pushed image digest (e.g. `registry/papyr-api@sha256:…`) before `up`. Rolling back to the previous healthy image means re-running step 5 with the previous digest. The app image digest gate (registry push) is completed by the release procedure, not by this template.

Full-topology activation (Phase 5 branch): the unified topology includes `redis`, `workers`, `clamd`, `cleanup`, `monitor` in profile `queue` plus `nginx` in profile `edge`. After release gates publish `PAPYR_WORKERS_IMAGE` and `PAPYR_CLAMD_IMAGE` digests, a separately authorized deployment runs the stack under the single project name `papyr-app` with all required profiles. Until then, these services remain off the critical path for foundation-stage API verification.

## Operations

- Rotate credentials out of band and restart only affected services.
- Keep Redis and worker services on internal networks.
- Apply bounded log rotation and host resource alerts.
- Test backup restoration independently of backup creation.
- Capture sanitized diagnostics for incidents; never paste credentials or document-derived data.

## Rollback

Retain the previous version-pinned image set and reviewed configuration. Roll back by restoring those pins, validating Compose configuration, and recreating affected services. Concretely, with the previous digest and the same `PAPYR_ENV_FILE`:

```bash
export PAPYR_API_IMAGE=registry/papyr-api@sha256:<previous-digest>
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml config --quiet
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml --profile app up -d api
```

Database or object-format changes require an explicit compatibility and recovery plan.

## Boundaries

This template does not provision the host, modify DNS, issue certificates, create storage lifecycles, migrate production data, or authorize a release. Those actions require a separate reviewed procedure.

## Full-stack Phase 5 topology (separately authorized)

The feature branch introduces `workers`, `clamd`, `cleanup`, and `monitor` services in profile `queue`, plus `nginx` in profile `edge`. A separate authorized release procedure performs these steps:

1. **Topology consolidation**: bring up a single compose project with all required profiles (`--profile app --profile queue`) under the established name `papyr-app` per D-1 of the deployment plan; verify Redis resolves from the API container.

2. **Image parameterization**: export `PAPYR_API_IMAGE`, `PAPYR_WORKERS_IMAGE`, and `PAPYR_CLAMD_IMAGE` digests for the session only (never stored in source); build/push worker images from the merged SHA.

3. **Activation**: `docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" --profile app --profile queue pull` and `up -d`; confirm `/health` and `/health/ready` return 200 from the API container; verify worker health probe responds on the configured port.

4. **Gate verification**: run `scripts/check-r2-lifecycle.sh` to validate the lifecycle contract; apply it to the bucket as a separately authorized action. Execute a read-only monitor check (`python -m app.ops.monitor`) to confirm eight checks: api readiness, redis, clamd, queue backlog, queue PEL, worker health, cleanup freshness, R2 ops probe.

5. **Production E2E**: enqueue a valid document through each tool router, observe admission → worker claim → execution → R2 upload → signed download; test fail-closed rejection by uploading a hostile PDF fixture; confirm scanner is available via `/health/ready`.

6. **Drills**: perform rollback to the previous healthy digest; measure recovery time; then restore forward state; optionally drill Redis persistence restoration if applicable.

These steps remain unexecuted here until authorization. Production operations should follow the owner's approved deployment checklist and use non-root routine commands (`mypapyr` service account) as permitted by policy.
