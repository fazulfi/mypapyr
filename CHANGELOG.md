# Changelog

All notable changes to this project are tracked here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once a release version is cut. Branch-level work during a release cycle is recorded here before merge.

## [Unreleased] — branch `feat/phase-5-production-readiness`

Phase 5 hardens the platform toward production readiness: five-tool completion end to end, worker + queue + scanner + monitoring services, hardened delivery, and the production networking contract (frontend `/api/v1` → nginx → API origin) that was the historical gate-exit blocker.

### Added

- **Five-tool end-to-end delivery**
  - Frontend tool pages for all five tools: Compress, Merge, Split (with localized ranges input and live preview), JPG to PDF, PDF to JPG (`frontend/src/app/[locale]/*`) — complete, localized EN/ES/ID, unit + E2E tested.
  - Backend worker executors for all five tools with a five-tool executor registry (`backend/app/worker/registry.py`, `backend/app/worker/entrypoint.py`).
  - Strict split range parser validated fail-closed at admission; `SplitOptions` schema; persisted options in the task store (`backend/app/services/split_service.py`).
- **Operational services** (`backend/app/`)
  - Production worker entrypoint with truthful health probe (`python -m app.worker`).
  - Bounded cleanup service for expired tasks + graceful-shutdown loop (`app.ops.cleanup_loop`).
  - Production monitor with eight health checks (`app.ops.monitor`).
  - R2 lifecycle policy gate with contract verification (`app.ops.r2_lifecycle`, `scripts/check-r2-lifecycle.sh`).
  - Unified Compose topology: `api`, `nginx`, `redis`, `workers`, `clamd`, `cleanup`, `monitor` with profiles `app`/`edge`/`queue`.
- **Security**
  - ClamAV threat scanning enforced across all five tool admission paths (`backend/app/security/scanner.py`).
  - Canonical hostile PDF acceptance fixtures.
  - Frontend/environment hardening: `NEXT_PUBLIC_API_BASE_URL`-configurable `/api/v1` rewrite in `frontend/next.config.ts` (the frontend→backend origin contract).
  - Pinned conversion engines and Ghostscript 10.07.1; `python-multipart` 0.0.31; `nanoid` 3.3.17 security override.
- **Documentation**
  - Consolidated `pdf_to_jpg` router (dropped the misspelled `pdf_to_jgy` stub).
  - This CHANGELOG; `docs/environment-variables.md` (authoritative env-var contract); frontend-connectivity section in `deploy/runbook-vps.md`.

### Changed

- **CI** — aligned the frontend build/e2e env var name to `NEXT_PUBLIC_API_BASE_URL` (was the mismatched `NEXT_PUBLIC_API_URL`, which never reached the rewrite). 19 CI jobs, CI-without-CD.
- README/SECURITY capability claims aligned with branch state; roadmap records branch and correction note.

### Removed

- Misspelled legacy `backend/app/routers/pdf_to_jgy.py` stub (superseded by the real consolidated `pdf_to_jpg.py` router).

### Security

- CI runs Trivy (critical/high), full-history gitleaks, dependency-review, npm/pip audit, hadolint, shellcheck; all GitHub Actions SHA-pinned with `# vX.Y.Z`; jobs use read-only permissions; **CI never deploys**.

---

## [0.1.0] — foundation (Phase 0–4)

Initial engineering foundation: Next.js 16 web application with strict TypeScript and a shared trilingual (EN/ES/ID) shell; typed FastAPI service (app factory, stable error envelope, task state machine, validation, health/readiness); Redis Streams queue and minimal-metadata task store; Cloudflare R2 client with opaque keys and one-hour retention; CI with format/lint/coverage/build/Playwright/Trivy/gitleaks/audit gates; public Compose/Nginx/env templates; product + architecture specifications. See git history for the Phase 0–4 commit series.