# Self-hosted deployment runbook

This document is a public template for a future, separately authorized deployment. The repository CI does not execute these steps.

## Prerequisites

- A dedicated Linux host with Docker Engine and the Compose plugin.
- A dedicated non-root service account with key-based SSH access.
- DNS, TLS, firewall, and image-registry decisions completed outside this repository.
- A real `.env.production` provisioned out of band with mode `0600` and owned by the service account.
- Version-pinned production images that have passed the release security gates.

## Files

Place the reviewed release versions under a dedicated application directory:

- `deploy/docker-compose.yml`
- `deploy/nginx/conf.d/production.conf`
- `.env.production` provisioned from a secret manager, never copied from the public example

## Validation sequence

```bash
docker compose --env-file .env.production -f deploy/docker-compose.yml config
docker compose --env-file .env.production -f deploy/docker-compose.yml pull
docker compose --env-file .env.production -f deploy/docker-compose.yml up -d
docker compose --env-file .env.production -f deploy/docker-compose.yml ps
```

Review health checks and logs before changing traffic. Do not deploy placeholder image tags or example environment values.

## Operations

- Rotate credentials out of band and restart only affected services.
- Keep Redis and worker services on internal networks.
- Apply bounded log rotation and host resource alerts.
- Test backup restoration independently of backup creation.
- Capture sanitized diagnostics for incidents; never paste credentials or document-derived data.

## Rollback

Retain the previous version-pinned image set and reviewed configuration. Roll back by restoring those pins, validating Compose configuration, and recreating affected services. Database or object-format changes require an explicit compatibility and recovery plan.

## Boundaries

This template does not provision the host, modify DNS, issue certificates, create storage lifecycles, migrate production data, or authorize a release. Those actions require a separate reviewed procedure.
