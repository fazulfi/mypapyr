# Product roadmap

This roadmap distinguishes code available in the repository from intended product capability. It is directional, not a release commitment.

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

## In this feature branch: five tools end to end (pending merge and deployment)

The following is implemented on this feature branch and verified by unit, integration, and E2E gates. It is not merged to `main` and not active in production.

- Five backend tool executors (compress-pdf, merge-pdf, split-pdf, jpg-to-pdf, pdf-to-jpg) dispatching worker jobs with pinned engines and Ghostscript in the worker image; a one-worker processing loop with truthful health probe and graceful shutdown.
- Upload and enqueue admission on all five tool routers, with the five-tool executor registry dispatching worker jobs and pinned conversion engines.
- Localized tool page routes for compress, merge, and split; localized catalog entries, tool-ids, and trilingual (EN/ES/ID) message keys across all five tools.
- HTTP E2E coverage of the five-tool admission-poll-download lifecycle.
- Hardened Nginx server block with rate limiting, security headers, bot/path blocking, and a fail-closed default server.
- R2 lifecycle policy gate: the approved two-rule contract (one-day `tmp/` expiration safety net and one-day incomplete-multipart abort) is verified by `scripts/check-r2-lifecycle.sh`; applying the policy to the live bucket stays a separately authorized deploy-time action.

## Specified launch catalogue

The five-tool catalogue below is specified in the product specification and implemented in the feature branch as described above; production availability follows merge and deployment.

1. **Compress PDF** — one automatic quality profile. The server path uses the official, unmodified Ghostscript distribution through a hardened subprocess boundary.
2. **Merge PDF** — ordered multi-file merging with preservation rules defined by the product specification.
3. **Split PDF** — range and per-page output with deterministic ordering.
4. **JPG to PDF** — image normalization, orientation handling, and predictable page fitting.
5. **PDF to JPG** — high-quality page rendering with transparent compositing.

Each tool is planned with browser-first capability detection, a transparent server fallback where needed, explicit limits, accessible states, and consistent retention rules.


## In this feature branch: privacy, analytics, advertising, and support (P6, pending merge and deployment)

The following Phase 6 work is implemented on the `feat/phase-6-privacy-analytics-support` branch and verified by frontend unit + coverage gates (43 test files, 638 tests, branch coverage 88.3%). It is not merged to `main` and not active in production.

- **Analytics schema, redaction, and leakage tests (PT-01)** — a closed-field event schema (`frontend/src/lib/analytics-schema.ts`) enumerating allowed fields (page, locale, referrer, UTM, tool, mode, coarse size bands, funnel, timing, error categories, outcomes, web vitals, ad presence) and a forbidden list (filenames, object keys, signed URLs, passwords, contents, previews, raw error and message payloads, fingerprints). `frontend/src/lib/analytics.ts` provides a redaction pipeline (`redactPayload` strips non-allowed keys and coerces filename-like values), a closed `errorCategory` enum (raw errors are never sent), coarse size-band enforcement (never exact bytes), opt-out via DNT / Global Privacy Control / app flag, SSR-safe wrappers, and a `useAnalytics(locale, toolId?)` hook. The leakage test suite (`src/__tests__/leakage.test.ts`) asserts every guard.
- **Advertising slots with placement guards (PT-02)** — an Adsterra native unit (300x250) configured once (`frontend/src/lib/ads.ts`, `frontend/src/components/ads/AdSlot.tsx`, `frontend/src/components/ads/placement.ts`). Reserved dimensions prevent layout shift; lazy client-side script injection triggers only after the slot scrolls into view; the slot renders only on the five tool pages and only after the primary task experience (after result/download), never beside the Download control, and never on status, legal, or support surfaces. Wired into the four tool pages that reach result states (compress, merge, jpg-to-pdf, pdf-to-jpg).
- **Contact form and result-problem report (PT-03)** — a trilingual (EN/ES/ID) categorized contact form (`frontend/src/app/[locale]/contact/page.tsx`, `frontend/src/components/support/ContactForm.tsx`, `frontend/src/lib/support.ts`) and a result-local problem report (`frontend/src/components/support/ResultProblemReport.tsx`). Minimal data model (closed-enum category, message ≤ 2000 characters, optional email, sanitized page/locale context; no names, phones, or attachments). Anti-spam: honeypot, client rate-limit (3 / 10 min via `localStorage`), and a Cloudflare Turnstile placeholder gated by `NEXT_PUBLIC_TURNSTILE_SITE_KEY`. Redaction-safe errors, locale-matched confirmations, and delivery-monitoring counts only.
- **Password handling verification (PT-04)** — memory-only password entry (`frontend/src/components/PasswordInput.tsx`, `frontend/src/lib/password.ts`) that appears only for encrypted inputs, validates each locked source independently for Merge, distinguishes wrong-password from corrupt/unsupported errors, and never writes password material to analytics, logs, URLs, or storage.

Unit-test gating: branch coverage raised from a pre-existing ~74% sub-80 baseline to 88.3% (lines 92.7%, statements 91.5%, functions 92.7%), meeting the 80% CI threshold.

## Later opportunities

Additional PDF tools, organizational features, billing, public APIs, and advanced workflows are outside the launch catalogue and require separate product decisions.
