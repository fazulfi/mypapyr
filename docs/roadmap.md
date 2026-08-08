# Product roadmap

This roadmap distinguishes code available in the repository from intended product capability. It is directional, not a release commitment.

Status note: the work described under "In this feature branch" below is implemented on `feat/phase-5-production-readiness`, not yet merged to `main`, and not deployed. Production still runs the prior Phase 4 release, whose readiness probe reports unavailable until the Phase 5 topology (single Compose project, worker, scanner, cleanup, monitor) is deployed under separate authorization.

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

The following is implemented on `feat/phase-5-production-readiness` and verified by the branch's unit, integration, and E2E gates. It is not merged to `main` and not active in production.

- Five localized tool pages (English, Spanish, Indonesian) with localized slugs — `/en/compress-pdf` (`/es/comprimir-pdf`, `/id/kompres-pdf`), `/en/merge-pdf` (`/es/combinar-pdf`, `/id/gabungkan-pdf`), `/en/split-pdf` (`/es/dividir-pdf`, `/id/pisahkan-pdf`), `/en/jpg-to-pdf` (`/es/jpg-a-pdf`, `/id/gambar-ke-pdf`), `/en/pdf-to-jpg` (`/es/pdf-a-jpg`, `/id/pdf-ke-gambar`) — plus canonical EN route aliases for translated slugs, a shared task download helper, and Playwright E2E coverage of the five tools.
- Upload and enqueue admission on all five tool routers, with the five-tool executor registry (`compress-pdf`, `merge-pdf`, `split-pdf`, `jpg-to-pdf`, `pdf-to-jpg`) dispatching worker jobs; pinned conversion engines and Ghostscript 10.07.1 in the worker image; a truthful worker entrypoint with health probe and graceful shutdown.
- Concrete ClamAV threat scanning wired into all five admission paths with fail-closed semantics, plus canonical hostile-PDF acceptance fixtures.
- Unified Compose topology (profiles `app`, `edge`, `queue`) covering `api`, `nginx`, `redis`, `workers`, `clamd`, `cleanup`, and `monitor` with digest-form image variables.
- R2 lifecycle policy gate: the approved two-rule contract (one-day `tmp/` expiration safety net and one-day incomplete-multipart abort) is verified by `python -m app.ops.r2_lifecycle --check deploy/r2-lifecycle.json` / `scripts/check-r2-lifecycle.sh`; applying the policy to the live bucket stays a separately authorized deploy-time action.
- Operations entrypoints implemented but not yet active in production: `python -m app.ops.cleanup_loop` (bounded cleanup passes with graceful shutdown) and `python -m app.ops.monitor` (eight health checks: api readiness, redis, clamd, queue backlog, queue PEL, worker health, cleanup freshness, R2 ops probe) with stable exit codes 0/1/2.

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

## Changelog notes

- The squash merge of Phase 4 (`dabfbbd`) carries the misspelling `pdfToJag` in its message; the correct identifier is `pdfToJpg`. Public history is intentionally not rewritten; the correction is recorded here.

## Later opportunities

Additional PDF tools, organizational features, billing, public APIs, and advanced workflows are outside the launch catalogue and require separate product decisions.
