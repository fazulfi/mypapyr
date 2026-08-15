# Architecture overview

Papyr is designed as a browser-first PDF platform with an explicit, bounded server-processing path. This feature branch implements the frontend foundation (including the shared trilingual shell), the backend service foundation with its API, queue, and storage contracts, deployment templates, and CI foundation described below. Native PDF processing via five tool executors, upload and enqueue admission endpoints, worker dispatch, and R2 object lifecycle cleanup are implemented in this feature branch; production release requires merge to main and separate authorization. The five PDF workflows are implemented with localized EN/ES/ID routes; progress is tracked on the [roadmap](roadmap.md).

## Current implementation

- A Next.js application with strict TypeScript and automated quality gates, including the shared trilingual shell: English, Spanish, and Indonesian locale routing with persistent preference, Navbar, Footer, LanguageSwitcher, and SkipLink navigation, a localized homepage, supporting route shells for privacy, terms, cookies and advertising, contact, status, roadmap, and blog, and a localized 404, with unit and Playwright E2E gates.
- A typed FastAPI service foundation: app factory with strict configuration, `GET /health` and `GET /health/ready` endpoints, request correlation headers, a stable error envelope, file and job validation schemas, the pure server task state machine, and versioned `/api/v1` contracts for capabilities, task status, and signed downloads.
- A Redis-backed backend foundation: a minimal-metadata task store, a durable Streams queue with queue caps and fair-use controls, a one-worker processing loop (executors implemented per tool), an R2 client with opaque-key storage and presigned downloads, and a cleanup coordinator that enforces the hard one-hour (3,600-second) retention maximum. Typed file validation, PDF sanitization, and fail-closed threat classification are implemented in this feature branch.
- Privacy-safe logging and records: request and task correlation, redacted settings, and no document bodies, filenames, passwords, signed URLs, or extracted text in logs or store records.
- Public-safe Docker Compose and Nginx templates for `nginx`, `api`, `redis`, and `workers` services.
- CI-only GitHub Actions for formatting, linting, tests, coverage, builds, Playwright E2E, Trivy, gitleaks, dependency and package audits, and repository QA checks.

## Backend service contracts

The versioned backend contracts below are implemented and covered by unit and integration tests (branch state; pending merge to main): capabilities, task status, signed downloads under `/api/v1`, plus upload/enqueue admission on all five tool routers, five-tool executors, and worker dispatch. These describe the branch implementation awaiting production deployment.

| Endpoint | Purpose | Behaviour |
| --- | --- | --- |
| `GET /api/v1/capabilities` | Per-tool limits, global queue and retention values, and the stable failure-code vocabulary | 200 with a versioned envelope and `Cache-Control: public, max-age=3600` |
| `GET /api/v1/tools/{tool}/tasks/{task_id}/status` | Task state and progress | 200 with the task record; unknown, expired, or mismatched work returns one stable 404 category |
| `GET /api/v1/tools/{tool}/tasks/{task_id}/download/{output}` | Signed download grant | 200 with `{url, expires_at}` and `Cache-Control: no-store`; every denial returns the same 404 category, never engine or store internals |

- **Stable failure vocabulary.** Nineteen stable failure codes cover validation, limits, queue, and rate outcomes. Only four are retryable: `queue_full`, `max_wait_exceeded`, `too_many_concurrent`, and `rate_limited`.
- **Limits.** Per-tool limits cover file count and size, total bytes, pages, pixels, estimated memory, execution seconds, and zip and result sizes. Global values: one-hour retention, 900-second maximum wait, 2,000 queued jobs, 4 concurrent jobs per origin, and a 180-second default timeout. The capabilities contract publishes them; admission enforcement lands with the upload endpoint.
- **Privacy-safe logs and store.** Settings redact credentials, and task records never store document bodies, filenames, passwords, signed URLs, or extracted text — prohibited at serialization. Task keys are opaque, every record carries a TTL within the retention target, and cleanup telemetry records counts and timing only.
- **Redis Streams and one-worker posture.** A `jobs` stream with a `workers` consumer group carries only minimal task metadata. Each worker instance processes one in-flight job, recovers stale claims, and acknowledges work only after a terminal state transition, with at-most-once behaviour for stale processing. The queue is capped at 2,000 entries with a 900-second oldest-wait ceiling, and admission pauses fail closed when Redis is unavailable. Adaptive fair-use controls keyed by SHA-256 origin fingerprints enforce per-origin concurrency and frequency limits with allow, delay, challenge, and reject levels; the shipped admission default allows all requests until the upload path exists.
- **R2 signed URLs and lifecycle.** Download grants are presigned URLs capped at 300 seconds or the remaining artifact lifetime, whichever is shorter, and never extend beyond the hard one-hour retention maximum. The cleanup coordinator removes source, intermediate, and result objects at their 3,600-second deadline before deleting task records, idempotently and in pages. R2 lifecycle expiry is day-granular, so its one-day-minimum template is an independent safety net and is applied during a separately authorized release.
- **Sanitizer and classification.** Typed file validation runs before classification; classification is fail-closed — blocked before sanitize, never downgraded. The PDF sanitizer removes JavaScript, external access, and attachments, verifies the result, and refuses encrypted, malformed, or unsanitizable files. The concrete threat scanner remains behind the defined protocol seam; admission currently enforces validation, sanitization, and the fail-closed classification matrix.

## Target topology

| Layer | Target component | Responsibility |
| --- | --- | --- |
| Web | Next.js on Vercel | Localized product experience, browser processing, upload and result UI. |
| Edge | Cloudflare | DNS, TLS, routing, coarse abuse controls, and API proxying. |
| API | FastAPI behind Nginx | Validation, admission, task state, capabilities, and cleanup coordination. |
| Queue | Redis | Minimal durable task metadata and bounded scheduling. |
| Workers | Isolated processes | Native PDF execution with CPU, memory, time, filesystem, and network limits. |
| Objects | Cloudflare R2 | Temporary server-side inputs and results with deterministic deletion. |
| Operations | External monitoring and alerts | Availability, resource health, and incident notification. |

## Processing model

Papyr prefers local browser processing when the selected operation, input, and device can complete reliably. Server processing is reserved for work that needs native engines, stronger isolation, sanitization, or a more predictable resource envelope. The interface must tell the user where processing occurs and must not silently upload a file that was expected to remain local.

The server path is designed around a versioned API, a durable queue, and bounded workers. Native engines never execute on the asynchronous API event loop. Worker processes receive only the minimum required task context and operate with constrained resources and temporary storage.

## Data lifecycle

The target lifecycle for server-processed documents is:

1. Validate metadata and admission limits before accepting work.
2. Store temporary objects under opaque, non-identifying keys.
3. Queue only minimal task metadata; never queue document bodies, passwords, signed URLs, or extracted text.
4. Execute the operation in an isolated worker.
5. Issue a short-lived download capability after successful completion.
6. Actively remove source, intermediate, and result objects, with a one-hour maximum retention target and a storage lifecycle rule as a safety net.

Steps 2, 3, 5, and 6 are implemented in the current foundation: opaque temporary storage, minimal-metadata queueing, signed downloads, and cleanup coordination. Step 1 is implemented as validation schemas and published limit values, with admission enforcement landing alongside the upload endpoint. Step 4, isolated native execution via five executors, is implemented in this feature branch. R2 lifecycle expiry is day-granular so its one-day-minimum template is an independent safety net applied during separately authorized deployment.

## PDF engine boundary

Compress PDF is specified to invoke the official, unmodified Ghostscript distribution as a separate hardened subprocess. Papyr does not vendor, fork, modify, or link Ghostscript source into the application. Other PDF engines follow the same subprocess and resource-isolation boundary when server execution is required.

## Availability and failure behaviour

The frontend and backend are independently deployable. Browser-capable operations should remain available during a backend outage. Server-dependent operations report unavailability clearly. Invalid, expired, unsupported, or unsafe work fails closed with stable user-facing categories rather than engine internals.

## Delivery boundary

The repository CI verifies source quality and security but does not deploy. Production release, infrastructure mutation, credential provisioning, and data migration are separate operational procedures.

For detailed target contracts, see the [product specification](specifications/product.md), [technical architecture specification](specifications/architecture.md), and [roadmap](roadmap.md).
