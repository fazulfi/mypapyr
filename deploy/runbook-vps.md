# Self-hosted deployment runbook

This document is a public template for a future, separately authorized deployment. The repository CI does not execute these steps.

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
- `.env.production` provisioned from a secret manager, never copied from the public example

## Deployment variables

Export these once in the deployment session; every command below uses them.

```bash
# Path to the provisioned environment file (mode 0600, service-account owned).
export PAPYR_ENV_FILE=/opt/papyr/production/.env

# Immutable api image reference produced by the release gates (digest).
export PAPYR_API_IMAGE=registry/papyr-api@sha256:<digest>
```

Fail-closed behavior (designed, not a regression):

- `docker compose` refuses to load when `PAPYR_ENV_FILE` is unset, empty, or points at a missing file: the api/workers `env_file` is `${PAPYR_ENV_FILE:?...}` and the error names the variable. The committed template is never a valid env source.
- `pull`/`up` fail at image resolution when `PAPYR_API_IMAGE` is not a real reference: the compose default is the `papyr-api:__SET_ME__` placeholder, which does not exist.
- `--profile app` selects only the API service. `redis` and `workers` live on the `queue` profile and `nginx` on `edge`; all three keep `__SET_ME__` image tags and cannot be activated by the API-only commands below.

## Isolated API deployment

This procedure activates **only the `api` service** of the four-slot skeleton. `redis`, `workers`, and `nginx` are deferred placeholders and must not be deployed.

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

> Full-stack note: generic `pull` and `up` sequences covering the whole skeleton apply only after the queue, worker, and edge services have real images and production configuration. Until then they are intentionally not runnable.

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
