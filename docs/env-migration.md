# Env Migration Map: REFERENCE (papyr-reference) → WORK (mypapyr)

This document is the single source of truth for migrating a provisioned
production `.env` from the REFERENCE deployment (`papyr-reference`, the live
`api.mypapyr.com` stack) to the WORK deployment in this repository.

The WORK contract is defined by `backend/app/config.py` (typed settings,
fail-closed required values) and `deploy/.env.production.example` (the
non-secret committed template). The REFERENCE contract comes from the
`papyr-reference` `backend/utils/config.py` and its `deploy/.env.production.example`.

## Renamed variables (must be renamed in the provisioned `.env`)

| REFERENCE name | WORK name | Notes |
|---|---|---|
| `ENVIRONMENT` | `APP_ENV` | Same semantics (`production`); renamed for clarity in `deploy/.env.production.example`. Not read by `backend/app/config.py`; kept for deployment/process context. |
| `CORS_ORIGINS` | `ALLOWED_ORIGINS` | Comma-separated origin allowlist. **Required** in WORK: `backend/app/config.py` rejects an empty value at boot (`_parse_allowed_origins`), and wildcard origins are rejected by the security middleware. |
| `FILE_RETENTION_MINUTES` | `RETENTION_SECONDS` | **Unit changed** (minutes → seconds). WORK enforces a hard one-hour ceiling (DEC-070): `RETENTION_SECONDS=3600` maximum; values above 3600 are rejected at boot. Convert: `minutes × 60`. |

## Removed variables (delete from the provisioned `.env`)

| REFERENCE name | WORK disposition |
|---|---|
| `RATE_LIMIT_PER_MINUTE` | Removed. Replaced by the queue/admission knobs `MAX_WAIT_SECONDS` (default 900), `MAX_QUEUE_LENGTH` (default 2000), `MAX_CONCURRENT_PER_ORIGIN` (default 4), and `DEFAULT_TIMEOUT_SECONDS` (default 180). Rate limiting at the edge is nginx-scope (`limit_req_zone` in `deploy/nginx/conf.d/production.conf`), not an app env knob. |
| `MAX_UPLOAD_SIZE_MB` | Removed. Upload caps are per-tool (BE-08), not a single global env knob; `backend/app/config.py` no longer reads it. |

## R2 variables

| REFERENCE name | WORK name | Notes |
|---|---|---|
| `R2_ACCOUNT_ID` | `R2_ACCOUNT_ID` | Unchanged; still required. |
| `R2_ACCESS_KEY_ID` | `R2_ACCESS_KEY_ID` | Unchanged; still required. |
| `R2_SECRET_ACCESS_KEY` | `R2_SECRET_ACCESS_KEY` | Unchanged; still required. Redacted from settings repr. |
| `R2_BUCKET_NAME` | `R2_BUCKET_NAME` | Unchanged; still required. |
| `R2_PUBLIC_URL` | `R2_ENDPOINT` / `R2_REGION` | Replaced: `R2_ENDPOINT` (optional endpoint override) and `R2_REGION` (default `auto`). |

## Added variables (not present in REFERENCE; optional unless noted)

| WORK name | Default | Notes |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Compose network binding for the task store; READ by the API image (`backend/app/config.py`). Provision `redis://redis:6379/0` (compose service name). May embed credentials; redacted from settings repr. |
| `REDIS_MAXMEMORY_BYTES` | `402653184` (384 MiB) | R-09; must stay consistent with the compose `redis` service `--maxmemory 384mb`. |
| `REDIS_EVICTION_POLICY` | `noeviction` | R-09. |
| `R2_REGION` | `auto` | R2 region override. |
| `LOG_LEVEL` | `info` | Validated against Python logging levels. |
| `RETENTION_SECONDS` | `3600` | R-03 one-hour ceiling (see renamed table). |
| `MAX_WAIT_SECONDS` | `900` | R-03. |
| `MAX_QUEUE_LENGTH` | `2000` | R-03. |
| `MAX_CONCURRENT_PER_ORIGIN` | `4` | R-03 (R-08). |
| `DEFAULT_TIMEOUT_SECONDS` | `180` | R-03. |
| `WORKER_CPUS` | `1.5` | R-07. |
| `WORKER_MEMORY_BYTES` | `2147483648` (2 GiB) | R-07. |

`API_PORT` (`3000`) documents the compose/nginx/image port contract; it is
declared in `deploy/.env.production.example` but not read by
`backend/app/config.py`.

## Fail-closed boot contract

The WORK template (`deploy/.env.production.example`) ships the five required
values **intentionally EMPTY** (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`,
`R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `ALLOWED_ORIGINS`).
`backend/app/config.py` rejects empty required variables at boot, so an
accidental load of the template crash-loops instead of booting with
placeholder credentials. The provisioned `.env.production` MUST supply real
values for all five; all other variables fall back to the approved defaults
above when unset.

## Migration checklist

1. Copy the REFERENCE `.env.production` to the new provisioned path (mode 0600, service-account owned).
2. Rename `ENVIRONMENT` → `APP_ENV`; `CORS_ORIGINS` → `ALLOWED_ORIGINS` (set a real origin list); `FILE_RETENTION_MINUTES` → `RETENTION_SECONDS` (value × 60, capped at 3600).
3. Delete `RATE_LIMIT_PER_MINUTE` and `MAX_UPLOAD_SIZE_MB`.
4. Rename `R2_PUBLIC_URL` → `R2_ENDPOINT`/`R2_REGION` if used; keep the four `R2_*` required variables.
5. Add `REDIS_URL=redis://redis:6379/0` (compose network) and any optional knobs to override.
6. Validate: `bash scripts/check-compose.sh` and `docker compose config --quiet` (with `PAPYR_ENV_FILE` pointing at the provisioned file and `PAPYR_API_IMAGE` set to a digest-form reference).
