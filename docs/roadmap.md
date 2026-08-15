# Product roadmap

This roadmap distinguishes code available in the repository from intended product capability. It is directional, not a release commitment.

Status note: the Phase 5 (five tools end to end, hardened delivery) and Phase 6 (privacy, analytics, advertising, support) work is merged to `main` via PR #24 and deployed to production on 2026-08-15 (release 1767ca8; verified via <https://mypapyr.com> and <https://api.mypapyr.com> through Cloudflare). The contact form's email delivery requires the owner to provision Cloudflare Email Sending credentials out of band; until then submissions validate and are accepted while delivery failures are counted only.

## Available foundation

- Minimal Next.js application and strict TypeScript configuration.
- FastAPI service foundation: app factory, strict environment configuration, health and readiness endpoints, request correlation, a stable error envelope, file and job validation schemas, and the pure server task state machine, with full unit coverage.
- Public-safe Compose, Nginx, and environment templates.
- CI with format, lint, unit-test, coverage, build, Playwright E2E, Trivy, gitleaks, dependency and package audit, and repository QA gates.
- Public product, architecture, security, integration, and contribution documentation.

## Available now: backend service contracts

The versioned backend contracts for the API, queue, storage, and security foundation are implementation-complete on the merged foundation and covered by unit, real-Redis, and R2 integration tests with coverage above the 80 percent gate. CI and container-security checks run on the pull request; review, deployment, runtime, and rollback validation are separate later gates.

- Versioned `/api/v1` endpoints for capabilities, task status, and signed downloads, with a stable failure-code vocabulary and per-tool and global limits.
- Redis-backed durable queue and minimal-metadata task store with a one-worker processing loop, queue caps, and adaptive fair-use controls.
- Cloudflare R2 client with opaque keys, presigned download grants, and a cleanup coordinator enforcing the hard one-hour retention maximum, with R2's day-granular one-day-minimum lifecycle rule template as an independent safety net. Applying that lifecycle rule to a live bucket remains a separately authorized deploy-time operator action.
- Privacy-safe logging and records: request and task correlation, redacted settings, and no document bodies, filenames, passwords, signed URLs, or extracted text in logs or store records.
- Validation, sanitizer, and threat-classification prerequisites: typed file validation, a PDF sanitizer that refuses unsanitizable input, and a fail-closed classification matrix.

## Now available: shared trilingual shell

The shared trilingual shell that lands the locale routing, accessibility navigation, and supporting pages is implemented and tested.

- English, Spanish, and Indonesian locale routing with persistent preference via cookie and Accept-Language fallback; non-supported two-letter prefixes are stripped so requests resolve under EN without redirect loops.
- Accessible navigation across all three locales: SkipLink as the first focusable element, sticky Navbar with categorized tool menus, Footer with tools and support columns, LanguageSwitcher with equivalent-path resolution, and a single `main` landmark per locale.
- Localized homepage, localized 404 with `lang` and locale-resolved copy, and localized supporting route shells for privacy, terms, cookies and advertising, contact, status, roadmap, and blog.
- Unit and Playwright E2E gates cover locale routing, cookie preference, the SkipLink and focus target, contrast on the focused SkipLink, the localized 404, and the supporting route headings across all three locales.

## Deployed: five tools end to end

The five-tool work is merged to `main` and active in production since 2026-08-15 (release 1767ca8), verified by unit, integration, and E2E gates.

- Five localized tool pages (English, Spanish, Indonesian) with localized slugs — `/en/compress-pdf` (`/es/comprimir-pdf`, `/id/kompres-pdf`), `/en/merge-pdf` (`/es/combinar-pdf`, `/id/gabungkan-pdf`), `/en/split-pdf` (`/es/dividir-pdf`, `/id/pisahkan-pdf`), `/en/jpg-to-pdf` (`/es/jpg-a-pdf`, `/id/gambar-ke-pdf`), `/en/pdf-to-jpg` (`/es/pdf-a-jpg`, `/id/pdf-ke-gambar`) — plus canonical EN route aliases for translated slugs, a shared task download helper, and Playwright E2E coverage of the five tools.
- Upload and enqueue admission on all five tool routers, with the five-tool executor registry (`compress-pdf`, `merge-pdf`, `split-pdf`, `jpg-to-pdf`, `pdf-to-jpg`) dispatching worker jobs; pinned conversion engines and Ghostscript 10.07.1 in the worker image; a truthful worker entrypoint with health probe and graceful shutdown.
- Concrete ClamAV threat scanning wired into all five admission paths with fail-closed semantics, plus canonical hostile-PDF acceptance fixtures.
- Unified Compose topology (profiles `app`, `edge`, `queue`) covering `api`, `nginx`, `redis`, `workers`, `clamd`, `cleanup`, and `monitor` with digest-form image variables.
- R2 lifecycle policy gate: the approved two-rule contract (one-day `tmp/` expiration safety net and one-day incomplete-multipart abort) is verified by `python -m app.ops.r2_lifecycle --check deploy/r2-lifecycle.json` / `scripts/check-r2-lifecycle.sh`; applying the policy to the live bucket stays a separately authorized deploy-time action.
- Operations entrypoints active in production as compose services (cleanup, monitor): `python -m app.ops.cleanup_loop` (bounded cleanup passes with graceful shutdown) and `python -m app.ops.monitor` (eight health checks: api readiness, redis, clamd, queue backlog, queue PEL, worker health, cleanup freshness, R2 ops probe) with stable exit codes 0/1/2.

## Deployed: privacy, analytics, advertising, and support (P6)

The Phase 6 work is merged to `main` (PR #24) and active in production since 2026-08-15 (release 1767ca8), verified by 710 frontend tests across 47 files (statements 92.11%, branches 88.09%, functions 93.24%, lines 93.58%) and 1346 backend tests with ruff and mypy strict clean. It is not merged to `main` and not active in production.

- **Analytics schema, redaction, and leakage tests (PT-01)** — a closed-field event schema (`frontend/src/lib/analytics-schema.ts`) enumerating allowed fields (page, locale, referrer, UTM, tool, mode, coarse size bands, funnel, timing, error categories, outcomes, web vitals, ad presence) and a forbidden list (filenames, object keys, signed URLs, passwords, contents, previews, raw error and message payloads, fingerprints). `frontend/src/lib/analytics.ts` provides a redaction pipeline (`redactPayload` strips non-allowed keys and coerces filename-like values), a closed `errorCategory` enum (raw errors are never sent), coarse size-band enforcement (never exact bytes), opt-out via DNT / Global Privacy Control / app flag, SSR-safe wrappers, and a `useAnalytics` hook. The leakage test suite (`frontend/src/__tests__/leakage.test.ts`, 36 tests) verifies the schema and redaction contracts.
- **Advertising slots with placement guards (PT-02)** — an Adsterra native unit (300x250) configured once (`frontend/src/lib/ads.ts`, `frontend/src/components/ads/AdSlot.tsx`, `frontend/src/components/ads/placement.ts`). Reserved dimensions prevent layout shift; lazy client-side script injection triggers only after the slot scrolls into view; placements follow the 2026-08-15 owner decision: the homepage carries a top leaderboard and a result-page box, each tool page renders a leaderboard immediately (idle), the 300x250 box after the result/download card (per FR/DEC-151, enforced by a DOM-order guard test), and a bottom skyscraper; supporting content pages (contact, privacy, terms, cookies-advertising, roadmap, faq) carry a 468x60 banner (plus a half-page unit on contact and faq). The status page stays ad-free so incident information remains immediately readable (DEC-130). Six Adsterra zones are registered in `frontend/src/lib/ads.ts` (300x250, 728x90, 320x50, 468x60, 160x600, 160x300) with reserved dimensions and lazy client-side injection.
- **Contact form and result-problem report (PT-03)** — a trilingual (EN/ES/ID) categorized contact form (`frontend/src/app/[locale]/contact/page.tsx`, `frontend/src/components/support/ContactForm.tsx`, `frontend/src/lib/support.ts`) and a result-local problem report (`frontend/src/components/support/ResultProblemReport.tsx`) wired into all five tool pages. Minimal data model (closed-enum category, message ≤ 2000 characters, optional email, sanitized page/locale context; no names, phones, or attachments). Anti-spam: honeypot, client rate-limit, Cloudflare Turnstile (server-side siteverify on the backend endpoint). Redaction-safe errors, locale-matched confirmations, and delivery-monitoring counts only. Backend delivery: `POST /api/v1/support/contact` (`backend/app/routers/support.py`, `backend/app/services/contact_service.py`) validates server-side, rate-limits per origin, and delivers via the Cloudflare Email Sending REST API with server-side secrets, async best-effort semantics (202 accepted), counts-only metrics, and no message/email content in logs.
- **Password handling verification (PT-04)** — memory-only password entry (`frontend/src/components/PasswordInput.tsx`, `frontend/src/lib/password.ts`) that appears only for encrypted inputs, validates each locked source independently for Merge, distinguishes wrong-password from corrupt/unsupported errors, and never writes password material to analytics, logs, URLs, or storage.

Unit-test gating: frontend branch coverage raised from a pre-existing ~74% sub-80 baseline to 88.09% branches (statements 92.11%, functions 93.24%, lines 93.58%), meeting the 80% CI threshold; backend coverage and lint/type gates pass on the branch.

## Specified launch catalogue

The five-tool catalogue below is specified in the product specification and implemented in the feature branch as described above; production availability follows merge and deployment.

1. **Compress PDF** — one automatic quality profile. The server path uses the official, unmodified Ghostscript distribution through a hardened subprocess boundary.
2. **Merge PDF** — ordered multi-file merging with preservation rules defined by the product specification.
3. **Split PDF** — range and per-page output with deterministic ordering.
4. **JPG to PDF** — image normalization, orientation handling, and predictable page fitting.
5. **PDF to JPG** — high-quality page rendering with transparent compositing.

Each tool is planned with browser-first capability detection, a transparent server fallback where needed, explicit limits, accessible states, and consistent retention rules.

## Planned platform services

- Abuse controls, incident alerts, and recovery procedures beyond the branch's monitor and cleanup entrypoints.
- Separately authorized production release and deployment of the branch topology (single Compose project, worker, scanner, cleanup, monitor), including the R2 lifecycle application and rollback drills.
- Full legal, support, and status content and functionality beyond the route shells and the Phase 6 contact form, and the blog publishing programme.

## Changelog notes

- The squash merge of Phase 4 (`dabfbbd`) carries the misspelling `pdfToJag` in its message; the correct identifier is `pdfToJpg`. Public history is intentionally not rewritten; the correction is recorded here.

## Later opportunities

Additional PDF tools, organizational features, billing, public APIs, and advanced workflows are outside the launch catalogue and require separate product decisions.
