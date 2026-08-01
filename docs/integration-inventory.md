# Third-party integration inventory

This document is the Phase 0 inventory of every third-party integration the Papyr rebuild consumes. It is a public-safe index: each row lists the integration name, the public endpoint scope, the purpose, and the Phase 0 status. No secret values, no real IP addresses, and no token shapes appear in this document. The authoritative evidence for the status of each integration is `audit-outputs/phase-0/integration-validation.md`; this inventory is a navigation surface over that evidence.

## Conventions used in this table

- **Integration** — the named third-party service the rebuild depends on.
- **Endpoint** — the public scope identifier (account, project, hostname, or bucket name). Real IPs are written as `<vps-ip>`; tokens, chat IDs, and access keys are never written.
- **Purpose** — what the rebuild uses the integration for.
- **Phase 0 status** — one of:
  - *Read-only validated* — the configuration contract was validated at the environment-variable **name** level, and (where applicable) an unauthenticated reachability probe was performed. No values were read, no authenticated call was issued, no mutation was attempted.
  - *Interface-only* — the configuration contract was validated at the **name** level only. No reachability probe, no value-level verification, no authenticated call.
- **Evidence** — the row in `audit-outputs/phase-0/integration-validation.md` that records the validation result.

## Inventory

| # | Integration | Endpoint | Purpose | Phase 0 status | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | GitHub (source control + Actions) | `fazulfi/mypapyr` (private) | Source-of-truth repository hosting and CI runtime. The legacy public repo `fazulfi/papyr` is read-only and excluded from the rebuild. | Read-only validated | §1a–1d |
| 2 | Vercel (frontend hosting) | `VERCEL_ORG=fazulfis-projects`, `VERCEL_PROJECT_NAME=papyr`, prod URL `https://mypapyr.com` | Hosts the Next.js frontend. Phase 0 does not deploy or trigger a build on Vercel. | Read-only validated | §2a–2d |
| 3 | Cloudflare (DNS + edge + R2) | zone `mypapyr.com`; R2 bucket `papyr-files` | Edge proxy for `mypapyr.com` and `api.mypapyr.com`; R2 bucket for temporary file storage. | Interface-only | §3a–3c |
| 4 | Cloudflare R2 (object storage) | `R2_BUCKET_NAME=papyr-files` | Stores temporary user-uploaded and processed PDF artifacts. Phase 0 does not upload, list, or modify any object. | Interface-only | §3b, §4 |
| 5 | AI gateway (OpenAI-compatible) | `https://router.budgezen.com/v1` (also referenced as `PAPYR_AI_BASE_URL`) | Hosts the upstream model gateway used by the backend. Phase 0 sends an unauthenticated `HEAD`/`GET` probe only; no key is sent, no model is invoked. | Read-only validated | §5a–5b |
| 6 | Adsterra (advertising) | `ADSTERRA_PUBLISHER_ID`, `ADSTERRA_PLACEMENT_IDS` (banner 300×250, single unit) | Source of advertising revenue. Phase 0 does not load any Adsterra script, request any impression, or authenticate against the Adsterra API. | Interface-only | §6a–6b |
| 7 | Telegram (owner alerting) | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Sends owner alerts from the backend. Phase 0 does not send any message; no token or chat ID is read. | Interface-only | §7a–7b |
| 8 | Backup S3 (operational backup) | `BACKUP_S3_BUCKET`, `BACKUP_S3_ENDPOINT` | Stores the recoverable VPS backup per DEC-173. Phase 0 does not list, write, or restore any object. | Interface-only | §3b, §4 |
| 9 | Sentry (error monitoring) | `SENTRY_DSN` | Receives frontend and backend error reports. Phase 0 does not send any event; no DSN is read. | Interface-only | §3b (env contract) |
| 10 | VPS (operational host) | `VPS_USER=root` over `<vps-ip>` (`VPS_HOST`, `VPS_SSH_PORT=22`); domain `VPS_DOMAIN` | Runs the FastAPI backend, Redis, workers, and Nginx behind Cloudflare. Phase 0 executed a single read-only SSH probe (`uname`, `cat /etc/os-release`, `free`, `nproc`, `swapon`, `docker --version`) only. | Read-only validated | §8a |

## Notable Phase 0 unknowns

The following items appear in the environment-variable contract but **could not** be fully validated in Phase 0 because doing so would require either installing tooling (forbidden by Phase 0) or using a credential value (not authorized by Phase 0). Each is therefore listed as `Interface-only` and is explicitly **deferred** to the phase that authorizes the operation.

- **Cloudflare R2 bucket existence and emptiness.** Confirmed by env-variable name only (`R2_BUCKET_NAME=papyr-files`); remote verification requires `wrangler r2 object list` with an authenticated token. Phase 0 has not authorized either the install or the credential use.
- **Backup S3 bucket existence.** Confirmed by env-variable name only (`BACKUP_S3_BUCKET`, `BACKUP_S3_ENDPOINT`); no S3-compatible CLI is installed locally.
- **Adsterra value-level placement identifier.** The single-unit banner 300×250 placement is documented in planning artifacts (DEC-022, DEC-045); the value inside `ADSTERRA_PLACEMENT_IDS` is not read in Phase 0.
- **Authenticated AI gateway model list.** The unauthenticated probe confirmed DNS, TLS, and JSON 401 response. An authenticated `GET /v1/models` call is gated by DEC-193/DEC-196.

## Items requiring explicit owner authorization for future runs

The validator's "Items requiring explicit owner authorization" section enumerates the next-step validations that are blocked on Phase 0 rules. They are reproduced here as a navigation pointer; the canonical list is in `audit-outputs/phase-0/integration-validation.md`.

1. Wrangler install + read-only R2 bucket-list to confirm `papyr-files` emptiness.
2. Adsterra value-level confirmation that `ADSTERRA_PLACEMENT_IDS` resolves to the single authorized banner 300×250 unit.
3. Authenticated AI gateway model-list call (`GET /v1/models` with `Authorization: Bearer <API_KEY>`).
4. Vercel domain inspection (`vercel domains ls`) to confirm `mypapyr.com` and `api.mypapyr.com` attachment to the `papyr` project.

## What this document does not do

- It does not embed any secret, token, API key, real IP address, real chat ID, or Netdata URL.
- It does not authorize any Phase 0 action against the listed integrations. All Phase 0 work is read-only.
- It does not guarantee that the integrations are correctly configured at the value level. Phase 0 verifies the **name** contract; value-level verification is gated by later owner authorization.
- It does not claim legal compliance, certification, or audit attestation. The limitations in `README.md` apply.
