# Self-hosted deployment runbook

This document is a public template for a separately authorized deployment. The repository CI does not execute these steps. The Phase 5/6 baseline introduced a unified Compose topology (profiles `app`, `edge`, `queue`) covering `api`, `nginx`, `redis`, `workers`, `clamd`, `cleanup`, and `monitor`; the API-only foundation is deployed in production, and activating the full topology (nginx vhost, worker/scanner images, monitor/cleanup services) is a separately authorized release action described below.

## Prerequisites

- A dedicated Linux host with Docker Engine and the Compose plugin.
- A dedicated non-root service account with key-based SSH access.
- DNS, TLS, firewall, and image-registry decisions completed outside this repository.
- A real `.env.production` provisioned out of band with mode `0600` and owned by the service account. Never copy the public example: its required values are intentionally EMPTY so an accidental load fails fast at boot instead of booting with placeholder credentials.
- Version-pinned production images that have passed the release security gates (never `:latest`; `PAPYR_API_IMAGE` carries an immutable digest).

## VPS host target (resolved)

The production host is `root@82.25.62.204` with the application directory `/opt/mypapyr` and service account `mypapyr`. The earlier conflicting `<HOST_A>`/`<HOST_B>` targets are resolved to this single authoritative host. The owner should confirm current host state (R-12/R-26) before any deployment command below is run.

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
export PAPYR_ENV_FILE=/opt/mypapyr/production/.env

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

## API deployment (foundation stage)

The `api` service declares `depends_on: redis + clamd` (both
`condition: service_healthy`), so **Compose refuses to start `api` without
them** — activating `api` alone is impossible and would fail with "service
redis/clamd is required by api but is disabled". The foundation stage therefore
activates `api` together with its two healthy dependencies (`redis`,
`clamd`) from the `queue` profile. `workers`, `cleanup`, and `monitor` remain
quiet until release gates publish `PAPYR_WORKERS_IMAGE` (see "Full-stack
activation" below).

```bash
# 1. Build the foundation image locally (immutable base digest is pinned in
#    backend/Dockerfile.production; tag uniquely, never :latest).
docker build --file backend/Dockerfile.production --tag papyr-api:release-candidate backend

# 2. Structural validation (no Docker daemon required).
bash scripts/check-compose.sh

# 3. Validate on a Docker-capable host.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml config --quiet

# 4. Pull the needed images (never the deferred worker slot).
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml pull api redis

# 5. Activate api with its required healthy dependencies (redis + clamd).
#    `--profile app` selects api; `--profile queue` supplies the redis and
#    clamd it depends on. The explicit service names are the second guard.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml --profile app --profile queue \
  up -d api redis clamd

# 6. Smoke: api publishes no host port (internal only); probe inside the
#    container, then confirm the compose health state.
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml exec api \
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=5)"
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" -f deploy/docker-compose.yml ps
```

The deploy-time image reference must be immutable: `PAPYR_API_IMAGE` must be the pushed image digest (e.g. `registry/papyr-api@sha256:…`) before `up`. Rolling back to the previous healthy image means re-running the activation command with the previous digest (and, in the full stack, the previous `PAPYR_WORKERS_IMAGE`). The app image digest gate (registry push) is completed by the release procedure, not by this template.

Full-topology activation (Phase 5 baseline): the unified topology includes `redis`, `workers`, `clamd`, `cleanup`, `monitor` in profile `queue` plus `nginx` in profile `edge`. After release gates publish `PAPYR_WORKERS_IMAGE` and `PAPYR_CLAMD_IMAGE` digests, a separately authorized deployment runs the stack under the single project name `papyr-app` with all required profiles. Until then, `workers`, `cleanup`, and `monitor` remain off the critical path for foundation-stage API verification.

## Operations

For the Phase 10 launch gate, run `bash scripts/check-launch.sh` for the offline
preflight, `bash scripts/check-launch.sh smoke` for public read-only smoke, and
`bash scripts/check-launch.sh rollback-preflight` for rollback evidence. Record the
coordinated gate in [docs/verification/launch-checklist.md](../docs/verification/launch-checklist.md)
and use [docs/verification/smoke.md](../docs/verification/smoke.md) for the smoke
contract. These checks never SSH, deploy, reload nginx, or print secrets.

- Rotate credentials out of band and restart only affected services.
- Keep Redis and worker services on internal networks.
- Apply bounded log rotation and host resource alerts.
- Test backup restoration independently of backup creation.
- Capture sanitized diagnostics for incidents; never paste credentials or document-derived data.

## Backup operations (P7 OP-04)

The repository contains a public-safe encrypted restic procedure at `deploy/backup/restic-backup.sh`. Schedule `run` daily from the host scheduler after owner approval of the R-13 retention values; the script requires `RESTIC_REPOSITORY`, `RESTIC_PASSWORD_FILE`, `PAPYR_BACKUP_ROOT`, and `PAPYR_BACKUP_SCOPE`, and never stores credentials. `run` fails closed unless `RESTIC_PASSWORD_FILE` is a mode-`0600` regular file owned by the operator. Scope is enforced by the allowlist manifest `deploy/backup/backup-scope.txt` via `--files-from`: restic reads only the listed configuration paths, so document data (filenames, contents, metadata), R2 objects, signed URLs, queue payloads, uploads, results, Redis, and secrets structurally cannot enter the repository. Use `plan`/`--dry-run` for offline validation. Perform the monthly isolated restore drill in `deploy/backup/restore-drill.md`; it is not production evidence and must use a temporary target.

## Rollback

Retain the previous version-pinned image set and reviewed configuration. Roll back by restoring those pins, validating Compose configuration, and recreating affected services. Concretely, with the previous digest and the same `PAPYR_ENV_FILE`:

```bash
export PAPYR_API_IMAGE=registry/papyr-api@sha256:<previous-digest>
export PAPYR_WORKERS_IMAGE=registry/papyr-workers@sha256:<previous-digest>
export PAPYR_CLAMD_IMAGE=registry/clamav@sha256:<previous-digest>
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml config --quiet
docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" \
  -f deploy/docker-compose.yml --profile app --profile queue \
  up -d
```

Restore the frontend through the authorized Vercel rollback process using the recorded
previous deployment URL and BUILD_ID. For the legacy host cutover, retain and restore
`/etc/nginx/sites-available/mypapyr.bak-cutover-<UTC timestamp>` after a read-only
`nginx -t` passes; never reload a failed configuration. These are pointer restores,
not destructive operations.

Database or object-format changes require an explicit compatibility and recovery plan.

## Boundaries

This template does not provision the host, modify DNS, issue certificates, create storage lifecycles, migrate production data, or authorize a release. Those actions require a separate reviewed procedure.

## Full-stack Phase 5 topology (separately authorized)

The unified topology introduces `workers`, `clamd`, `cleanup`, and `monitor` services in profile `queue`, plus `nginx` in profile `edge`. A separate authorized release procedure performs these steps:

1. **Topology consolidation**: bring up a single compose project with all required profiles (`--profile app --profile queue`) under the established name `papyr-app` per D-1 of the deployment plan; verify Redis resolves from the API container.

2. **Image parameterization**: export `PAPYR_API_IMAGE`, `PAPYR_WORKERS_IMAGE`, and `PAPYR_CLAMD_IMAGE` digests for the session only (never stored in source). The worker image is built from `backend/Dockerfile.worker` by the release procedure (the repository has no CI build producer for `PAPYR_WORKERS_IMAGE`); its digest is captured at release and pinned here.

3. **Activation**: `docker compose -p papyr-app --env-file "$PAPYR_ENV_FILE" --profile app --profile queue pull` and `up -d`; confirm `/health` and `/health/ready` return 200 from the API container; verify worker health probe responds on the configured port.

4. **Gate verification**: run `scripts/check-r2-lifecycle.sh` to validate the lifecycle contract; apply it to the bucket as a separately authorized action. Execute a read-only monitor check (`python -m app.ops.monitor`) to confirm eight checks: api readiness, redis, clamd, queue backlog, queue PEL, worker health, cleanup freshness, R2 ops probe.

5. **Production E2E**: enqueue a valid document through each tool router, observe admission → worker claim → execution → R2 upload → signed download; test fail-closed rejection by uploading a hostile PDF fixture; confirm scanner is available via `/health/ready`.

6. **Drills**: perform rollback to the previous healthy digest; measure recovery time; then restore forward state; optionally drill Redis persistence restoration if applicable.

These steps remain unexecuted here until authorization. Production operations should follow the owner's approved deployment checklist and use non-root routine commands (`mypapyr` service account) as permitted by policy.

## Frontend connectivity: `/api/v1` origin and nginx

The web application (Vercel or self-hosted Next.js) issues **same-origin** `/api/v1/*` requests. A build-time rewrite forwards them to the backend origin. The path is:

```text
Browser ── /api/v1/* (same-origin) ──> Next.js rewrite (next.config.ts)
        ── https://api.mypapyr.com/api/v1/* ──> Cloudflare (DNS, TLS)
        ── nginx (api.mypapyr.com vhost) ──> FastAPI (:3000, internal)
```

### Backend origin

- The rewrite destination is `NEXT_PUBLIC_API_BASE_URL` (build-time, default `https://api.mypapyr.com`); see `frontend/next.config.ts`. Set it at build for any non-default origin.
- The API service publishes **no host port** in the base template (internal `expose: "3000"` only). The production compose override publishes host port `3016` to the API container's port `3000` (`3016:3000`). It must be reachable by nginx on the compose network at `api:3000`, and by a public origin through an nginx/Cloudflare vhost that terminates TLS.

### nginx `api.mypapyr.com` vhost (release-time, not in this template)

`deploy/nginx/conf.d/production.conf` is a skeleton (`__SET_ME__` vhost, no TLS). For production the release procedure provisions a real vhost:

- `server_name api.mypapyr.com;` with TLS (e.g. Cloudflare origin certificate or Let's Encrypt), terminating TLS in front of the API service.
- `location / { proxy_pass http://papyr_api_upstream; }` forwarding `/api/v1/*` and `/health` to the API container, preserving the X-Forwarded-* headers the app expects.
- Retain the fail-closed `default_server → 444` block so an unknown Host is dropped.
- Keep the VPS firewall (e.g. `ufw`/Cloudflare) open only on `:443` (TLS) for the origin.

### Legacy frontend host cutover

The live frontend vhost is `/etc/nginx/sites-available/mypapyr` (enabled as
`/etc/nginx/sites-enabled/mypapyr`) and proxies `mypapyr.com` and
`www.mypapyr.com` to the systemd Next.js service on `:3017`. The final legacy
cutover is intentionally host-scoped: both its HTTP and HTTPS server blocks
must contain exactly `location / { return 308 https://budgezen.com$request_uri; }`.
Do not add `budgezen.com` to the VPS config, redirect `api.mypapyr.com`, change
DNS/Cloudflare, or use a path-specific destination. Preserve the existing
`/etc/nginx/sites-available/mypapyr.bak-cutover-<UTC timestamp>` backup.

Run `sudo nginx -t` and capture its output before `sudo systemctl reload nginx`.
If the test fails, do not reload; restore the timestamped backup and retest.
After reload, verify both apex and `www` through the Cloudflare edge with
`curl -I --max-redirs 0`, including a path with a query, `/faq`, and `/rotate`.
Each HTTPS request must return 308 with `Location: https://budgezen.com$request_uri`.
HTTP requests may first receive Cloudflare's HTTP-to-HTTPS redirect; follow the
HTTPS hop separately. Verify `budgezen.com` root, `/en`, a tool page,
`/sitemap.xml`, and `/robots.txt` remain healthy and do not loop.

### Verification

After both sides are deployed:

```bash
# From the frontend host / a client:
curl -s -o /dev/null -w "%{http_code}\n" https://api.mypapyr.com/health     # expect 200
curl -s -o /dev/null -w "%{http_code}\n" https://api.mypapyr.com/api/v1/capabilities  # expect 200
# Then confirm the deployed frontend serves a tool page and its /api/v1 calls return 200,
# not 404 (the historical gate-exit blocker).
```

The git history records that the frontend reaching the backend over `/api/v1` was the sole blocker to a prior gate-exit; keep this connectivity check in the release checklist until the full request path is proven green in production.
