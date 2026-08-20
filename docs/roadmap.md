# Product roadmap

This roadmap distinguishes code available in the repository from intended product capability. It is directional, not a release commitment.

Status note: the Phase 5 (five tools end to end, hardened delivery) and Phase 6 (privacy, analytics, advertising, support) work is merged to `main` via PR #24 and deployed to production on 2026-08-15 (release 1767ca8; verified via <https://mypapyr.com> and <https://api.mypapyr.com> through Cloudflare). The Phase 6 enterprise completion (PT-04 merge passwords, ad-placement E2E, SEO, docs reconciliation) shipped via PR #46 and is deployed as backend release p6-complete-1786951216 and frontend release p6-ads-all-1786954951 (2026-08-17). The contact form's email delivery requires the owner to provision Cloudflare Email Sending credentials out of band; until then submissions validate and are accepted while delivery failures are counted only.

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

The Phase 6 baseline is merged to `main` (PR #24) and deployed to production on 2026-08-15 (release 1767ca8) on the VPS backend (`api.mypapyr.com`) and the Vercel frontend. The Phase 6 enterprise completion (PT-04 merge wiring and ad-placement E2E) shipped via PR #46 and is deployed as backend release p6-complete-1786951216 and frontend release p6-ads-all-1786954951 (2026-08-17). P8 SEO implementation is **In branch** on `feat/full-p8-seo-url-migration`; it has no commit, release, or deployment. The owner-confirmed target is `budgezen.com` as the primary production and canonical frontend host; `mypapyr.com` is legacy/redirect-only, with redirect completeness remaining an external edge concern. R-25 traffic, external indexing, ranking, and any SEO SLO remain NOT_VERIFIED. Test gates: the P6 baseline had 780 frontend tests across 52 files (statements 91.27%, branches 86.15%, functions 91.71%, lines 93.10%) and 1360 backend tests (44 opt-in Redis integration tests skipped) with ruff and mypy strict clean.

- **Analytics schema, redaction, and leakage tests (PT-01)** — a closed-field event schema (`frontend/src/lib/analytics-schema.ts`) enumerating allowed fields (page, locale, referrer, UTM, tool, mode, coarse size bands, funnel, timing, error categories, outcomes, web vitals, ad presence) and a forbidden list (filenames, object keys, signed URLs, passwords, contents, previews, raw error and message payloads, fingerprints). `frontend/src/lib/analytics.ts` provides a redaction pipeline (`redactPayload` strips non-allowed keys and coerces filename-like values), a closed `errorCategory` enum (raw errors are never sent), coarse size-band enforcement (never exact bytes), opt-out via DNT / Global Privacy Control / app flag, SSR-safe wrappers, and a `useAnalytics` hook. The leakage test suite (`frontend/src/__tests__/leakage.test.ts`, 26 tests) verifies the schema and redaction contracts.
- **Advertising slots with placement guards (PT-02)** — an Adsterra native unit (300x250) configured once (`frontend/src/lib/ads.ts`, `frontend/src/components/ads/AdSlot.tsx`, `frontend/src/components/ads/placement.ts`). One ad per page (commit `8d9fc04`, ADR-03): the homepage renders a single box-300x250 immediately; each of the five tool pages renders a single box-300x250 only after the primary experience reaches a result phase (per FR/DEC-151, enforced by a DOM-order guard test); supporting content pages (contact, privacy, terms, cookies-advertising, roadmap, faq, status, blog) render a single banner-468x60 immediately (all-pages policy, owner decision 2026-08-17). Six Adsterra zones are registered in `frontend/src/lib/ads.ts` (300x250, 728x90, 320x50, 468x60, 160x600, 160x300) with reserved dimensions and lazy client-side injection; the slot div reserves fixed dimensions to prevent layout shift, DNT/GPC/`_papyrAdsDisabled` gating disables delivery, and a first-party house-promo fallback fills the slot when the provider script fails or times out (`frontend/src/components/ads/fallback.ts`). aria-labels are localized per locale (Publicidad/Iklan) and the ad-behavior E2E asserts exactly one reserved slot per allowed page.
- **Contact form and result-problem report (PT-03)** — a trilingual (EN/ES/ID) categorized contact form (`frontend/src/app/[locale]/contact/page.tsx`, `frontend/src/components/support/ContactForm.tsx`, `frontend/src/lib/support.ts`) and a result-local problem report (`frontend/src/components/support/ResultProblemReport.tsx`) wired into all five tool pages. Minimal data model (closed-enum category, message ≤ 2000 characters, optional email, sanitized page/locale context; no names, phones, or attachments). Anti-spam: honeypot, client rate-limit, Cloudflare Turnstile (server-side siteverify on the backend endpoint). Redaction-safe errors, locale-matched confirmations, and delivery-monitoring counts only. Backend delivery: `POST /api/v1/support/contact` (`backend/app/routers/support.py`, `backend/app/services/contact_service.py`) validates server-side, rate-limits per origin, and delivers via the Cloudflare Email Sending REST API with server-side secrets, async best-effort semantics (202 accepted), counts-only metrics, and no message/email content in logs.
- **Password handling verification (PT-04)** — memory-only password entry (`frontend/src/components/PasswordInput.tsx`, `frontend/src/lib/password.ts`) wired into the merge-pdf tool page on this branch: per-file password fields (`frontend/src/lib/mergePasswordFields.ts` builds `password_<i>` multipart fields), each locked source validated independently, and never writes password material to analytics, logs, URLs, or storage. The backend `PdfSanitizer.sanitize(password="")` threads each per-file password into the pikepdf open at sanitization time only; a locked file with a wrong or absent password fails the whole job with a distinct `400 error.wrongPassword` (FR-SHARED-09/FR-MERGE-04, `backend/app/routers/merge.py`, `backend/app/security/sanitize.py`). Passwords are never persisted or logged (DEC-174).

Unit-test gating: frontend coverage measured at 91.27% statements, 86.15% branches, 91.71% functions, and 93.10% lines, meeting the 80% CI thresholds (branches threshold is 80, raised from the pre-existing 74 baseline); backend coverage measured at 89.38% with ruff and mypy strict clean.

## In branch: Phase 8 SEO and URL migration

P8 implements the three SEO workstreams without changing application business logic or deployment files:

- **SEO-01 governance:** `docs/seo/slug-table.md` records the 57 indexable localized URLs (5 tools × 3 locales, 8 supporting routes × 3 locales, 15 blog articles × 3 locales, and 3 locale home routes); `docs/seo/legacy-url-inventory.md` records exactly 15 legacy locale-less paths with 5 × 301, 8 × 410, and 2 × 307 dispositions. `scripts/check-seo-inventory.sh` and its self-test fail closed on drift.
- **SEO-02 URL behavior:** the Next.js 16 `proxy.ts` maps `/compress`, `/merge`, `/split`, `/image-to-pdf`, and `/pdf-to-image` to one-hop locale-prefixed 301 targets; returns localized 410 responses for `/rotate`, `/protect`, `/unlock`, `/watermark`, `/sign`, `/pdf-to-word`, `/ocr`, and `/pdf-to-excel`; and keeps `/faq` and `/privacy` as cookie/Accept-Language/EN-resolved 307 routes. The 301 path does not set a locale cookie. R-25 traffic evidence is NOT_VERIFIED; no deferred 410 exception is claimed.
- **SEO-03 metadata:** `SEO_BASE_URL` is pinned in code to the confirmed primary production host `https://budgezen.com`, with per-route canonical and `en`/`es`/`id`/`x-default` alternates, 57 sitemap entries, robots sitemap alignment, explicit non-indexable exclusions, and deterministic committed `LAST_MODIFIED = "2026-08-18"`. `mypapyr.com` is legacy/redirect-only; edge redirect completeness is not established by repository source. External indexing, ranking, R-25 traffic, and any SEO SLO remain NOT_VERIFIED.
- **Release boundary:** the VPS-only legacy-host cutover is deployed and verified: `mypapyr.com` and `www.mypapyr.com` return host-level 308 responses to `https://budgezen.com$request_uri`; the exact nginx source diff and timestamped rollback backup are recorded in the operator evidence. `budgezen.com` remained untouched and healthy. DNS/Cloudflare configuration is verified read-only with no mutation, and the R-25 baseline was captured on 2026-08-20 in [`docs/seo/seo-slo.md`](seo/seo-slo.md). The branch's application release is still not merged/deployed; external indexing, ranking, complete path-level R-25 traffic, and SLO attainment remain NOT_VERIFIED. Rollback is the preserved `/etc/nginx/sites-available/mypapyr.bak-cutover-<UTC timestamp>` file, restored only after a successful `nginx -t` check.

## Specified launch catalogue

The five-tool catalogue below is specified in the product specification and implemented; the Phase 5/6 baseline and the Phase 6 enterprise completion are deployed to production as described above.

1. **Compress PDF** — one automatic quality profile. The server path uses the official, unmodified Ghostscript distribution through a hardened subprocess boundary.
2. **Merge PDF** — ordered multi-file merging with preservation rules defined by the product specification.
3. **Split PDF** — range and per-page output with deterministic ordering.
4. **JPG to PDF** — image normalization, orientation handling, and predictable page fitting.
5. **PDF to JPG** — high-quality page rendering with transparent compositing.

Each tool is planned with browser-first capability detection, a transparent server fallback where needed, explicit limits, accessible states, and consistent retention rules.

## Planned platform services

- Abuse controls, incident alerts, and recovery procedures beyond the branch's monitor and cleanup entrypoints.
- Completion of the deploy skeletons and the separately authorized production release of the remaining topology gaps: worker image digest publication, full Compose project activation, and rollback drills are **DONE** (released with p6-complete-1786951216 / p6-ads-all-1786954951); the nginx `__SET_ME__` image/vhost and the R2 lifecycle application on the live bucket remain as separately authorized operator actions.
- Full legal, support, and status content and functionality beyond the route shells and the Phase 6 contact form (whose email delivery awaits owner-provisioned Cloudflare Email Sending credentials).

## In branch: Phase 9 Content, Legal & Blog

P9 is implemented on this feature branch and pending the authorized release process; it is not deployed, ranked, or indexed.

- Legal page audit and revision for Privacy, Terms, and Cookies & Advertising across EN/ES/ID, with DEC-045 version 1.0 footers effective 2026-08-20.
- Pure-MDX blog pipeline with typed content metadata, server rendering, and fail-closed blog-content CI gates.
- Fifteen localized articles covering 5 topics × 3 locales, each dated 2026-08-20 and attributed to Papyr Team.
- `/blog` listing with five localized articles per locale, plus article sitemap entries; the sitemap now contains 57 URLs with per-article real `lastmod` values.

Status: **In branch (PR #49)**. External indexing, ranking, and deployment remain NOT_VERIFIED.

## Changelog notes

- The squash merge of Phase 4 (`dabfbbd`) carries the misspelling `pdfToJag` in its message; the correct identifier is `pdfToJpg`. Public history is intentionally not rewritten; the correction is recorded here.

## Later opportunities

Additional PDF tools, organizational features, billing, public APIs, and advanced workflows are outside the launch catalogue and require separate product decisions.
