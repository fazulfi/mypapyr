# Changelog

All notable changes to this project are tracked here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once a release version is cut. Branch-level work during a release cycle is recorded here before merge.

## [Unreleased] — Phase 6 enterprise completion

Phase 6 enterprise completion closes the remaining Phase 6 scope: PT-04 merge-password wiring, ad-placement E2E, SEO/hreflang, and documentation reconciliation. Merged via PR #46 and deployed 2026-08-17 as backend release `p6-complete-1786951216` and frontend release `p6-ads-all-1786954951` (BUILD_ID `HHzujraVbxQa5Q0LcI4dZ`). Verified by 780 frontend tests across 52 files (statements 91.27%, branches 86.15%, functions 91.71%, lines 93.10%) and 1360 backend tests with 44 opt-in skips (coverage 89.38%, gate 80%).

### Added

- **Encrypted-PDF password handling (PT-04) end to end** — client detection (`isEncryptedPdf`, first 4 KiB), per-file `PasswordInput` on the merge-pdf tool page, per-index `password_<i>` multipart fields, backend sanitizer password stage with a distinct `400 error.wrongPassword` envelope; passwords never persisted, logged, or echoed (DEC-174).
- **Ad-placement E2E and all-pages ad policy** — `e2e/ad-behavior.spec.ts` (presence/absence, DNT/GPC gating, house-promo fallback) plus an a11y E2E spec isolated from the third-party ad network. One symmetric ad slot per page (owner decision 2026-08-17): box-300x250 on the homepage (immediate) and on the five tool pages after the result phase, banner-468x60 on the supporting pages (contact, privacy, terms, cookies-advertising, roadmap, faq, status, blog).
- **SEO (ADR-06)** — hreflang alternates + canonical in `generateMetadata`, per-locale sitemap (42 URLs), robots alignment, and tests.
- **Privacy leakage suite refresh** — `frontend/src/__tests__/leakage.test.ts` holds 26 tests covering the closed-field schema and redaction contracts (PT-01).
- **Typecheck hardening (ADR-09)** — fixed 5 pre-existing `tsc --noEmit` errors and added a new `frontend-typecheck` CI job (CI is now 20 jobs, 19 on pushes to main).
- **Documentation reconciliation** — roadmap self-contradiction removed; README capability table and legend, product/architecture specifications, AGENTS.md facts, integrations inventory, API reference (merge `password_<i>` fields), and SECURITY.md aligned with the deployed state.

### Changed

- **All-pages advertising policy** — supersedes the prior status/legal/support exclusion (DEC-130): the 8 supporting pages render a banner-468x60 immediately via the shared `SupportingPageContent` container; ads remain gated by DNT/GPC (`isAdEnabled`) and never appear beside the Download control.
- **CI** — 20 jobs (19 on pushes to main, +1 `frontend-typecheck`); branch protection requires 7 status checks.

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

- **CI** — aligned the frontend build/e2e env var name to `NEXT_PUBLIC_API_BASE_URL` (was the mismatched `NEXT_PUBLIC_API_URL`, which never reached the rewrite). 20 CI jobs, CI-without-CD.
- README/SECURITY capability claims aligned with branch state; roadmap records branch and correction note.

### Removed

- Misspelled legacy `backend/app/routers/pdf_to_jgy.py` stub (superseded by the real consolidated `pdf_to_jpg.py` router).

### Security

- CI runs Trivy (critical/high), full-history gitleaks, dependency-review, npm/pip audit, hadolint, shellcheck; all GitHub Actions SHA-pinned with `# vX.Y.Z`; jobs use read-only permissions; **CI never deploys**.

## [Unreleased] — branch `feat/phase-4-complete-tools`

Redo of the five-tool end-to-end delivery: admission-to-download on all five backend tool routers, a richer trilingual tool UI, the fair-use and worker lifecycle fixes, HTTP E2E coverage, and hardened deployment artifacts.

### Redo (audit-driven fixes, 2026-08-14)

- **Fair-use isolation (I3)** — admission now threads a real origin fingerprint (`_resolve_origin`: `CF-Connecting-IP` → `x-forwarded-for` → client host, SHA-256) into `JobQueue.enqueue`; per-origin concurrency/frequency caps are no longer a single global bucket (`backend/app/routers/__init__.py`, all five routers).
- **Orphan-cleanup completeness (I4)** — mid-loop validation/scan/sanitize rejections in `merge-pdf` and `jpg-to-pdf` now delete inputs uploaded so far; no R2 objects leak on failed admissions (`backend/app/routers/{merge,image_to_pdf}.py`).
- **Worker PEL hygiene (M5)** — malformed and no-record stream entries are `XACK`ed alongside `XDEL`; recovered deleted ids are acked — no phantom pending-entry accumulation (`backend/app/worker/worker.py`).
- **Terminal polling errors (M6/M7)** — persistent status failures (404/expired) surface as an error state instead of looping silently; `derivePhase` treats missing status as `idle` not `queued` (`frontend/src/hooks/useTaskPolling.ts`, all five tool pages).
- **HTTP E2E for the five-tool lifecycle** — `backend/tests/test_tools_http_e2e.py` exercises admission (202) → status → download-grant over real HTTP routes with fakeredis/moto and a clean-scanner double; caught and fixed the `pdf-to-jpg` route typo and non-persisted task id.
- **UI richness parity with the legacy Papyr** — homepage hero pill, trust badges, tool-card CTA footers, privacy 3-card section; per-tool icon-chip headers + feature badges + `PrivacyNotice`; rich uploader/result cards (shimmer progress, before/after `−X%` compression card, emerald success header); 4-category nav/footer; `OtherTools` rail; FAQ page (8 items); full privacy page (7 sections); sitemap/robots/OG/Twitter images; Vercel Analytics + Speed Insights (`frontend/src/app`, `frontend/src/components`).
- **Coverage gate restored** — vitest branches threshold 74 → 80 (actual 87.5%); scripts `test-verify-pins.sh` + `check-r2-lifecycle.sh` restored (root `scripts/`).
- **Nginx + deploy hardening** — hardened vhost (Cloudflare real-IP, multi-zone rate limits, security headers, fail-closed 444, bot/path blocking); redis `read_only`/`cap_drop`/`no-new-privileges`; edge ports 80/443; env-name migration map documented (`docs/env-migration.md`).

### Added

- **Five-tool backend admission, end to end**
  - Upload/enqueue admission routers for all five tools — Compress, Merge, Split, JPG to PDF, PDF to JPG — wired into the application (`backend/app/routers/{compress,merge,split,image_to_pdf,pdf_to_jpg}.py`, `backend/app/main.py`), each enforcing per-tool limits, sanitization, opaque R2 upload of sanitized bytes, and queue admission (`202`).
  - Five-tool capabilities contract (`backend/app/routers/capabilities.py`): per-tool limits and the closed 19-code failure vocabulary for all five tool ids.
  - Split service with strict range parsing (`backend/app/services/split_service.py`).
  - Worker executors and the one-worker claim/execute/acknowledge loop (`backend/app/services/*`, `backend/app/worker/worker.py`).
- **Fair-use and lifecycle fixes (I3, I4, M5, M6, M7)**
  - Real origin fingerprint threaded into admission: fair-use concurrency/frequency controls are keyed by the SHA-256 origin fingerprint instead of a stub value (I3).
  - Mid-loop orphan cleanup, worker `XACK` ordering after terminal store writes, and terminal polling error handling (I4/M5/M6/M7).
- **UI richness (T3–T8)**
  - Restored homepage richness: hero, trust badges, privacy cards, and localized copy keys (T4).
  - Tool page chrome: icon header, feature badges, PrivacyNotice, and shared components (T5).
  - Rich uploader and result cards with shimmer and before/after states (T6).
  - Four-category nav/footer and OtherTools rail (T7).
  - FAQ and privacy pages, sitemap/robots/OG metadata, and analytics (T8).
  - Animation utilities, legacy catalog, and rich copy keys ported to the trilingual surface (T3).
- **HTTP E2E (T9)**
  - Backend HTTP E2E for the five-tool admission → poll → download lifecycle (`backend/tests/test_tools_http_e2e.py`).
- **Deployment hardening**
  - Hardened Nginx server block: rate limiting, security headers, bot/path blocking, and a fail-closed default server (T13, `deploy/nginx/conf.d/production.conf`).
  - R2 lifecycle policy gate (`scripts/check-r2-lifecycle.sh`, `deploy/r2-lifecycle.json`) verifying the one-day `tmp/` expiration safety net and the one-day incomplete-multipart abort rule.
  - Env migration map from the legacy deployment (`docs/env-migration.md`).
- **Documentation**
  - `docs/README.md` (documentation index), `docs/environment-variables.md` (authoritative env-var contract), `docs/api-reference.md`, `docs/ops-runbook.md`, `docs/upgrade.md`, and `docs/licensing.md` (decision record; no license granted).
  - CHANGELOG introduced.

### Changed

- **CI** — restored the 80% branch coverage gate and script parity (T11).
- README/SECURITY/architecture/roadmap/integrations claims aligned with the branch state: five-tool catalogue, localization, and Ghostscript compression are now marked "In branch" instead of "Specified"/"Planned".

### Security

- CI runs Trivy (critical/high), full-history gitleaks, dependency-review, npm/pip audit, hadolint, shellcheck; all GitHub Actions SHA-pinned with `# vX.Y.Z`; jobs use read-only permissions; **CI never deploys**.
- Admission runs validation → sanitization → fail-closed classification before any upload or enqueue; the concrete threat scanner remains behind the defined protocol seam on this branch.

---

## [0.1.0] — foundation (Phase 0–4)

Initial engineering foundation: Next.js 16 web application with strict TypeScript and a shared trilingual (EN/ES/ID) shell; typed FastAPI service (app factory, stable error envelope, task state machine, validation, health/readiness); Redis Streams queue and minimal-metadata task store; Cloudflare R2 client with opaque keys and one-hour retention; CI with format/lint/coverage/build/Playwright/Trivy/gitleaks/audit gates; public Compose/Nginx/env templates; product + architecture specifications. See git history for the Phase 0–4 commit series.
