# Deployment boundary — Phase 0

This document defines the explicit, line-in-the-sand boundary between what Phase 0 of the Papyr rebuild delivers and what it does **not** deliver. It is the public-safe counterpart to the more detailed deployment procedure that will be authored in a later, owner-authorized phase.

## Phase 0 delivers CI only, no CD

Phase 0 is a **continuous-integration-only** foundation. The CI pipeline in `.github/workflows/ci.yml` builds, tests, lints, formats, scans, and packages. It does not deploy.

Concretely, CI does **not**:

- Push to Vercel or trigger any Vercel deployment.
- Push to Cloudflare or update any DNS record, worker, or R2 binding.
- Connect to the VPS, run `docker compose up`, or restart any service.
- Write to the R2 bucket or the backup S3-compatible bucket.
- Send any Telegram message, Adsterra impression, or Sentry event.
- Apply any database migration, schema change, or persistent state change.
- Run any `git push` to a deployment remote, create any release tag, or rotate any credential.

The above list is enforced by `CONTRIBUTING.md`'s "CI gates" section, by the README's "Continuous integration overview" section, and by the absence of any deployment step in `.github/workflows/ci.yml`. The decision is recorded as DEC-160 and refined by DEC-177.

## VPS is read-only validation only

The VPS is the operational destination for the backend, the Redis queue, the workers, and the Nginx reverse proxy. In Phase 0, the VPS is treated as a **read-only validation target**.

What this means:

- A read-only SSH probe was executed once during the Phase 0 validator run to confirm the recorded environment facts (Ubuntu 24.04.4, 15 GiB RAM, 4 cores, 2.0 GiB swap, Docker 29.6.2). The probe executed only `uname`, `cat /etc/os-release`, `free`, `nproc`, `swapon`, and `docker --version`. Evidence: `audit-outputs/phase-0/integration-validation.md` §8.
- No `docker run`, `docker stop`, `docker rm`, `docker compose up`, `docker compose down`, `systemctl start`, `systemctl stop`, `apt install`, `ufw`, `iptables`, `mv`, `rm`, `chmod`, or `sed -i` was issued against the VPS during Phase 0.
- The VPS IP is recorded as `<vps-ip>` in this repository and in all public artifacts. The real address is treated as an authorized asset of the operator and is not committed, screenshot, pasted into chat, or echoed in any other artifact that may be published.

The future deployment user model is documented in DEC-172: a dedicated non-root SSH user with passwordless sudo for authorized administration, with direct root SSH login disabled and key-based authentication required. Phase 0 does **not** authorize creation of that user, does **not** authorize key installation, and does **not** authorize any VPS configuration change.

## What Phase 0 does not do

Phase 0 publishes the foundation but explicitly does **not** perform or authorize the following actions. Each item requires an explicit owner instruction in a later, separately authorized phase.

- **No production migrations.** No database, queue, or persistent-state migration is run from CI or by the agent. The schema and migration plan are specified in the technical architecture specification and will be executed only when the owner explicitly authorizes the production rollout.
- **No live DNS or Cloudflare production changes.** No `wrangler` install, no DNS record update, no Cloudflare Worker publish, no Cloudflare API token use, no R2 bucket creation, no R2 object upload. The configuration contract is validated at the environment-variable **name** level only (`audit-outputs/phase-0/integration-validation.md` §3).
- **No live ad placement.** No Adsterra script is loaded, no Adsterra impression is requested, no Adsterra publisher API authentication is performed. The configuration contract is validated at the **name** level only; value-level confirmation is deferred to the phase that authorizes it (`audit-outputs/phase-0/integration-validation.md` §6).
- **No production backup jobs.** No `BACKUP_S3_*` credential is read or used; no backup job is scheduled; no backup bucket is listed. The backup contract is validated at the **name** level only (`audit-outputs/phase-0/integration-validation.md` §4).
- **No monitoring stack.** No Sentry event is sent; no monitoring agent is installed; no alerting rule is created. The Sentry configuration contract is validated at the **name** level only. Telegram alerts are validated at the **name** level only — no message is sent (`audit-outputs/phase-0/integration-validation.md` §7).

## Decision references

The Phase 0 boundary is anchored in the following decisions. The full text of each decision lives in `papyr-rebuild-decisions.md`.

| Decision | Topic | Boundary it anchors |
| --- | --- | --- |
| DEC-160 | Production backend deployment is manually executed by the agent after approval. | CI may build, test, and scan artifacts but must not independently change production. Each production deployment requires an explicit owner instruction. |
| DEC-177 | Use a core automated production deployment gate. | Reinforces DEC-160: CI does not deploy; deployment is gated, manual, and owner-authorized. |
| DEC-172 | Use a dedicated SSH user with passwordless sudo for authorized administration. | Future VPS interaction uses a non-root SSH user; Phase 0 does not authorize creating that user or installing any key. |
| DEC-176 | Manage production secrets through protected VPS environment configuration. | Production env files require restrictive ownership and permissions (mode `0600`) and are excluded from source control, images, backups where inappropriate, logs, and audit outputs. |

## How to read this boundary

If a task asks for any of the items in the "What Phase 0 does not do" list, the correct response is:

- Confirm the boundary to the operator.
- Reference this document and the cited decision IDs.
- Stop the work and request explicit owner authorization before continuing.

The boundary is not a temporary limitation that an engineer can route around. It is a structural property of the Phase 0 foundation and is enforced by the same review process that enforces the test-driven development requirement and the coverage floor.

## What this document does not claim

This document does not claim legal compliance, certification, audit attestation, or guaranteed security posture. It does not represent that the privacy, data-handling, or operational posture of the system is sufficient for any particular use case, jurisdiction, or threat model. The limitations in `README.md` apply to this document as to every other public artifact in the repository.
