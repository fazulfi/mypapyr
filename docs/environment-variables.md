# Environment variables

This is the authoritative contract for every environment variable used by Papyr. It lists each variable, whether it is **required** or **optional**, its source (which process reads it), the approved default, and the reference.

Two bugs are recorded here because they were real: **CI once set `NEXT_PUBLIC_API_URL` while the code reads `NEXT_PUBLIC_API_BASE_URL`** — the dummy value never reached the rewrite. Both are now aligned on `NEXT_PUBLIC_API_BASE_URL`. Keep the name in sync across `.github/workflows/ci.yml` and `frontend/next.config.ts` when you touch either.

## Boot-required (backend fail-fast)

The FastAPI service **fails fast at startup** if any of these is missing or empty (`backend/app/config.py`, `config.from_env`). These are the only boot requirements — every support/contact and scanner variable below is optional and never enters `REQUIRED_ENV_VARS`.

| Variable | Required | Default | Read by |
| --- | --- | --- | --- |
| `R2_ACCOUNT_ID` | yes | — | `backend/app/config.py` |
| `R2_ACCESS_KEY_ID` | yes | — | `backend/app/config.py` |
| `R2_SECRET_ACCESS_KEY` | yes | — | `backend/app/config.py` |
| `R2_BUCKET_NAME` | yes | — | `backend/app/config.py` |
| `ALLOWED_ORIGINS` | yes | — | `backend/app/security/middleware.py` (CORS allowlist) |

The committed template (`deploy/.env.production.example`) leaves these **intentionally EMPTY** so an accidental load fails at boot instead of booting with placeholder credentials. Provision real values out of band into a `mode 0600` `.env.production`.

## Backend optional knobs (approved defaults)

Read by `backend/app/config.py`. When unset or empty the approved default applies; see `backend/app/config.py` and `deploy/.env.production.example` for the authoritative copy.

| Variable | Default | Purpose |
| --- | --- | --- |
| `R2_ENDPOINT` | `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` | R2 S3-compatible endpoint |
| `R2_REGION` | `auto` | R2 region (SigV4) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL. The code default is `localhost`; the compose stack overrides it to `redis://redis:6379/0` for in-project service DNS (see `deploy/docker-compose.yml`). |
| `REDIS_MAXMEMORY_BYTES` | `402653184` (384 MiB) | Redis maxmemory |
| `REDIS_EVICTION_POLICY` | `noeviction` | Redis eviction policy |
| `RETENTION_SECONDS` | `3600` | Hard one-hour object retention ceiling |
| `MAX_WAIT_SECONDS` | `900` | Max queue wait |
| `MAX_QUEUE_LENGTH` | `2000` | Max queued jobs |
| `MAX_CONCURRENT_PER_ORIGIN` | `4` | Fair-use concurrency per origin |
| `DEFAULT_TIMEOUT_SECONDS` | `180` | Default per-tool execution timeout |
| `WORKER_CPUS` | `1.5` | Worker CPU bound |
| `WORKER_MEMORY_BYTES` | `2147483648` (2 GiB) | Worker memory bound |
| `LOG_LEVEL` | `info` | Structured log level |
| `CLAMD_HOST` | `localhost` | ClamAV scanner host. The compose stack overrides it to `clamd` (service DNS). |
| `CLAMD_PORT` | `3310` | ClamAV scanner port (bounded to 65535) |
| `SCANNER_ENABLED` | `true` | Boolean; `false` explicitly disables the ClamAV threat gate (default enabled) |
| `SCANNER_TIMEOUT_SECONDS` | `10` | Per-file scanner verdict timeout (bounded to 3600) |

## Contact delivery (PT-03) — all optional

Read by `backend/app/config.py`. These are **delivery-required, not boot-required**: the API boots and accepts submissions without them. `CF_EMAIL_API_TOKEN` is the only variable that enables real outbound email; without it the `/api/v1/support/contact` endpoint still returns `202` and the background delivery task counts the failure. Delivery additionally requires Cloudflare dashboard onboarding (sending domain verified, token with the correct permission) before the provider accepts mail.

| Variable | Default | Purpose |
| --- | --- | --- |
| `CF_EMAIL_API_TOKEN` | unset (delivery disabled) | Cloudflare Email Sending API token. Secret; redacted from `Settings` repr/str. |
| `CF_EMAIL_ACCOUNT_ID` | unset (falls back to `R2_ACCOUNT_ID`) | Cloudflare account id used in the Email Sending REST URL. |
| `CONTACT_RECIPIENT` | `privacy@mypapyr.com` | Owner inbox receiving contact submissions. |
| `CONTACT_FROM_DOMAIN` | `mypapyr.com` | Sending domain; the payload `from` address is `no-reply@<domain>`. |
| `TURNSTILE_SITE_SECRET` | unset (verification skipped) | Turnstile server-side secret for `siteverify`. Soft gate: failures are counted, never rejected. Secret; redacted from `Settings` repr/str. |

## Frontend (build-time)

| Variable | Required | Default | Read by |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | no | `https://api.mypapyr.com` | `frontend/next.config.ts` (rewrites `/api/v1/*` to this origin) |
| `NEXT_PUBLIC_TURNSTILE_SITE_KEY` | no | unset (widget disabled) | `frontend/src/components/support/ContactForm.tsx` (client-side Turnstile explicit render, injected only when the key is present) |

The client issues same-origin `/api/v1/*` requests; the Next.js rewrite forwards them to this backend origin. Set it at **build** time to a non-default origin. See `deploy/runbook-vps.md` → "Frontend connectivity". `NEXT_PUBLIC_TURNSTILE_SITE_KEY` is build-time; when unset the Turnstile script is never injected and the form requires no token.

## Repository / CI (template-only, `__SET_ME__`)

Listed in the root `.env.example` as an out-of-band provision contract. CI uses none of these (CI supplies only the two `NEXT_PUBLIC_*` dummy values and backend test dummies); they exist for operators, Vercel, Cloudflare, and third parties:

`GITHUB_ACCOUNT`, `GITHUB_REPO_NAME`, `GITHUB_DEFAULT_BRANCH`, `VERCEL_ORG`, `VERCEL_PROJECT_NAME`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `BACKUP_S3_BUCKET`, `BACKUP_S3_ENDPOINT`, `BACKUP_S3_ACCESS_KEY_ID`, `BACKUP_S3_SECRET_ACCESS_KEY`, `PAPYR_AI_API_KEY`, `PAPYR_AI_BASE_URL`, `PAPYR_AI_MODEL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `SENTRY_DSN`, `VPS_HOST`, `VPS_USER`, `VPS_SSH_PORT`, `VPS_DOMAIN`.

The three Adsterra names listed in the root `.env.example` (`ADSTERRA_PUBLISHER_ID`, `ADSTERRA_PLACEMENT_IDS`, `ADSTERRA_API_KEY`) are **not read by any code**: the frontend keeps the owner-approved zone keys hardcoded in `frontend/src/lib/ads.ts` (client-side public identifiers) and reads no Adsterra variables from the environment. They are documented as a dead contract only.

Rules:

- Values are never committed. The root `.env.example` and `deploy/.env.production.example` carry names/placeholders only.
- `.env.papyr` is a **gitignored live credential record**; never commit it, and rotate any token it exposes (`gitleaks` scans history for leaked secrets).
- CI is CI-without-CD and uses no real secrets; every GitHub Actions in `.github/workflows/ci.yml` uses read-only permissions and no `secrets:` mapping.
