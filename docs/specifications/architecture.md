# Technical architecture specification

## 1. Purpose and status

This document defines the target technical architecture for Papyr: the component boundaries, processing model, task and API contracts, storage lifecycle, security controls, observability, delivery boundary, and verification strategy that the launch product is designed against.

The current repository implements the five-tool platform: a Next.js web application with localized tool pages, a typed FastAPI service (app factory, strict configuration, health and readiness endpoints, request correlation, a stable error envelope, validation schemas, the pure server task state machine, and 9 versioned `/api/v1` routers including per-tool admission), deployment templates, and CI. The Phase 5/6 baseline is merged to `main` and deployed to production (release 1767ca8); the follow-up Phase 6 enterprise completion (PT-04 merge-password wiring, ad-placement E2E, SEO, and documentation reconciliation) was merged via PR #46 and is deployed as backend release p6-complete-1786951216 and frontend release p6-ads-all-1786954951 (2026-08-17). Every component described as a target service is specified here and is not yet available unless the status matrix in Section 16, or source code and automated tests, demonstrate otherwise. Documentation is never a substitute for runtime evidence; a component becomes implemented only when its code, tests, configuration, and operational constraints are present.

The companion [product specification](product.md) defines the user-visible behaviour and acceptance criteria. Where responsibilities meet, this document states the mechanism and the product specification states the experience.

## 2. System context and target topology

Papyr is designed as a browser-first PDF platform with an explicit, bounded server-processing path. The target production topology:

| Layer | Component | Responsibility |
| --- | --- | --- |
| Hosting | Next.js application on a VPS (mypapyr.com) plus Vercel (budgezen.com) | Localized product experience, browser processing, upload and result UI, public status experience |
| Edge | Cloudflare | DNS, TLS, proxying of the public domain and API, coarse country context, first-layer bot and attack filtering |
| Compute | Dedicated host (VPS) | Nginx reverse proxy, FastAPI application, Redis queue, bounded PDF workers, cleanup and operational tooling |
| Storage | Cloudflare R2 | Temporary server-processed source, intermediate, and result objects |
| Backups | S3-compatible destination | Recoverable host state for disaster recovery |
| Monitoring | Host resource monitoring plus external uptime checks | Service health and outside-in availability |
| Alerts | Configured incident-alert channel | Operational incident notifications |

The frontend and backend are independently deployable and independently operable. A backend incident must not take down the informational site or browser-capable tools.

### 2.1 Target data flow

Browser-only job:

1. The user selects files on a tool page.
2. The frontend validates within conservative browser limits and processes locally.
3. No bytes leave the device. Results exist only for the active tab session.

Server job:

1. The frontend uploads through the edge to the versioned API.
2. Nginx terminates TLS, applies request-size and rate enforcement, and proxies to the application.
3. The API validates the file, applies per-tool limits and fair-use controls, writes minimal task metadata to Redis, and enqueues the job.
4. A bounded worker claims the job, processes it in an isolated container, and writes source, intermediate, and result objects to R2.
5. The API exposes task status; the frontend polls while the tab is open.
6. On completion the frontend downloads the result directly from R2 through a short-lived signed URL.
7. All server-side objects are deleted no later than one hour after upload receipt by application-driven deletion. The R2 lifecycle rule is an independent, day-granular safety net and does not extend or replace that hard maximum.

## 3. Current versus target inventory

| Area | Current (available now) | Target (specified) |
| --- | --- | --- |
| Frontend | Localized product shell, five tool interfaces, browser processing, shared upload, progress, and result components (deployed in the Phase 5/6 baseline) | Ongoing polish and follow-up work per roadmap |
| Backend API | FastAPI service foundation: app factory, strict configuration, health and readiness endpoints, request correlation, stable error envelope, validation schemas, the pure server task state machine, versioned `/api/v1` capabilities, task status, signed-download endpoints, and upload/enqueue admission on all five tool routers (deployed in the Phase 5/6 baseline) | Cancellation and any additional admission surface |
| Queue | Redis-backed minimal-metadata task store and durable Streams queue (`jobs`/`workers`) with queue caps and admission wired to the upload path; adaptive fair-use controls implemented | Bounded scheduling with the upload path wired to the admission seam |
| Workers | One-worker processing foundation: single in-flight job, per-tool timeouts, stale-claim recovery, terminal acknowledgement, and five-tool executors; worker entrypoint (`__main__.py` + `entrypoint.py`) | One active worker executing one concurrent native job at launch |
| Storage | Cloudflare R2 client with opaque keys, presigned downloads, cleanup coordination, and a lifecycle rule template; live lifecycle rule applied at release | One-hour temporary-object lifecycle safety net in production |
| Edge and proxy | Nginx server-block template with `__SET_ME__` placeholders only | Hardened Nginx reverse proxy behind Cloudflare |
| Monitoring | Monitor and cleanup operations entrypoints; incident alerting not yet configured | Host resource monitoring, external uptime checks, automated status experience, incident alerts |
| Delivery | CI with 20 required checks (19 on pushes to main, where the PR-only dependency review is skipped) and no deployment steps | Twenty required CI checks with no deployment steps; separately authorized release and deployment procedures |

## 4. Component boundaries

Papyr separates four concerns: the web application, the API control plane, the processing plane, and the object lifecycle.

1. **Web application** owns localized product pages, browser-capable processing, capability checks, and result presentation. It receives only public configuration; provider credentials and private infrastructure identifiers never enter client bundles.
2. **API control plane** owns validation, admission, task state, download authorization, and cleanup coordination. It must never run blocking native PDF work on the event loop.
3. **Processing plane** owns bounded workers and isolated PDF engines.
4. **Object lifecycle** owns temporary inputs, intermediates, and results with deterministic expiry.

### 4.1 Web application

The target frontend is a Next.js application hosted independently from backend compute. It owns:

- Locale-aware routing and metadata.
- Accessible shared upload, progress, error, and result components.
- Browser capability checks and local processing.
- Explicit, visible transition to server processing when required.
- Short-lived task and download capability handling, with same-tab refresh recovery using minimal opaque state.

Tool pages remain accessible when the backend is unavailable. Browser-capable operations may continue locally; server-dependent processing clearly communicates temporary unavailability.

### 4.2 API

The target API uses versioned routes under `/api/v1`. It is asynchronous and admission-focused. Responsibilities:

- Input metadata validation and admission limits.
- Capability-based task access.
- Queue submission and state reads.
- Short-lived signed download issuance.
- Cancellation (queued jobs only) and expiry coordination.
- Stable, non-sensitive error responses.

The current backend implements `GET /health` and `GET /health/ready`, the pure server task state machine, and the versioned `/api/v1` contract (capabilities, task status, signed downloads, and upload/enqueue admission on all five tool routers) plus the support contact endpoint.

### 4.3 Queue

Redis is the target durable coordination store. It holds only opaque task identity, state, timestamps, expiry, route, and non-sensitive temporary object references. File contents, original filenames, passwords, previews, signed URLs, and analytics payloads are never written to Redis. Records expire no later than their task and artifact lifecycle.

### 4.4 Workers

Native processing executes in dedicated worker processes with per-job CPU, memory, wall-clock, file-count, page-count, and output limits; ephemeral writable directories and deterministic cleanup; no external network access unless a narrowly specified operation requires it; a minimal process environment; and sanitized logs that exclude user document data and engine command details.

### 4.5 Object storage

Cloudflare R2 is the target temporary object store with opaque, non-identifying keys; separate source, intermediate, and result namespaces or equivalent policy boundaries; application-driven deletion enforcing the hard 3600-second maximum; an independent R2 day-granular lifecycle safety net; and no document-derived data in object metadata.

## 5. Browser versus server processing decision model

Papyr uses a hybrid model that prefers local browser processing and routes to the server when quality, file complexity, device capability, or reliability requires it. Routing is based on measured capabilities and explicit rules, never hidden arbitrary behaviour.

### 5.1 Routing rules

- **Browser-first by default**: Merge PDF, Split PDF, JPG to PDF, and PDF to JPG prefer local processing within conservative limits.
- **Server by default**: Compress PDF uses server-side processing by default because true high-quality compression requires a capable native engine.
- **Automatic fallback**: when a file is corrupt, encrypted-unsupported, unsafe, or exceeds browser limits, or when browser processing fails on a safe and supported job, the job automatically transitions to the server with a visible transition message.
- **Fail closed**: security-policy failures, unsupported content, invalid passwords, user cancellation, and retention violations never force a server upload.
- **Active-content routing**: Merge and Split inputs detected to contain PDF JavaScript, launch actions, or embedded attachments route to the server sanitization path. When that path is unavailable, affected jobs fail closed.
- **No retry loops**: fallback must not create retry loops, duplicate jobs, duplicate downloads, or repeated uploads.

### 5.2 Initial conservative browser-processing targets

These are initial safety targets, subject to revision from production telemetry and real-device testing:

| Input class | Desktop | Non-iOS mobile | iOS and iPadOS |
| --- | --- | --- | --- |
| General PDF jobs | 100 MB total input, 500 pages | 50 MB total input, 200 pages | 25 MB total input, 100 pages |
| PDF to JPG | 200 pages | 50 pages | 50 pages |
| JPG to PDF | 50 images, 100 megapixels total | 40 megapixels total | 40 megapixels total |

Routing must also evaluate decoded image dimensions, page geometry, encryption, corruption, and estimated peak memory, not file size alone. PDF to JPG browser rendering is sequential with a 16-megapixel per-page ceiling.

### 5.3 Processing-location disclosure

The user-visible experience is specified in the product specification. The architectural obligation is that the localized privacy disclosure remains accurate about browser processing, automatic server fallback, temporary storage, providers, and the one-hour maximum retention, and that workflow states label uploading, queued, and server processing truthfully when they occur.

## 6. API and task contracts

### 6.1 API versioning

All public processing, task, cancellation, limits, and download-authorization endpoints live under `/api/v1`. The frontend configuration and proxy routing use one canonical API base. Legacy routes require an explicit migration or retirement disposition and must not remain accidentally active.

### 6.2 Capability and limits contract

The versioned API is the canonical source for server-processing capabilities and limits. The frontend reads and presents this machine-readable contract rather than maintaining an independent hardcoded copy, and falls back to conservative values if the contract is unavailable. Backend validation remains authoritative even when the frontend pre-validates. Browser-specific safety limits remain frontend logic and are clearly distinguished from server limits.

Per-tool server limits are defined independently and may combine total bytes, per-file bytes, file count, page count, pixel count, page geometry, estimated memory, and expected output size. Limits are conservative design and safety defaults, adjusted from production observations, with a documented procedure for raising them.

### 6.3 Task state machine

Server tasks use these states:

| State | Meaning | Transition |
| --- | --- | --- |
| queued | Admitted, waiting for a worker | to processing on worker claim; to cancelled on user cancellation |
| processing | Claimed and being executed by a worker | to done on result upload; to failed on engine error, timeout, or safety shutdown |
| done | Result ready and downloadable | to expired at the absolute deadline |
| failed | Terminal failure with a safe error category | to expired at the absolute deadline |
| cancelled | Terminal state from user cancellation while queued | final |

Expiry is not a separate state; the artifact lifecycle is driven by the absolute retention deadline. Job state, progress, timeout, retry policy, cancellation, result expiry, and failure reasons are explicitly modeled. Operational timeouts and safety shutdowns are system-controlled and distinct from user cancellation.

### 6.4 Status contract

Task status is exposed under the versioned API. Unknown or expired task IDs return a distinct not-found response. Status responses include state, authoritative timestamps, the authoritative expiry timestamp, measurable progress where available, and safe error categories. Status polling is rate-managed and never extends retention.

### 6.5 Signed downloads

Successful server results are downloaded through short-lived signed R2 URLs rather than proxied through the host. Signed URL expiry never exceeds the artifact's authoritative expiry. A refreshed URL may be issued for the same valid result without extending retention. Signed URLs are never written to analytics, application logs, browser persistence, or support reports.

## 7. Queue and worker scheduling

### 7.1 Queue behaviour

- API processes enqueue work and expose durable status; they do not own long-running processing.
- Available workers claim jobs immediately; the system introduces no artificial waiting period.
- Queueing is bounded by hard operational safety limits for queue length, storage, maximum wait, job expiry, and host health.
- Valid jobs remain queued during normal capacity pressure instead of being rejected with a retry response.
- Scheduling is fair and prevents starvation and queue monopolization. It is not pure smallest-job-first or unrestricted FIFO.

### 7.2 Launch capacity posture

Initial capacity is intentionally conservative: one active worker executing one concurrent native job until operational evidence supports a change. Valid jobs may wait in the bounded fair queue while the worker is busy; queued waiting is an expected state, not an error. Additional worker concurrency requires capacity evidence from production observability and explicit approval. There is no paid priority lane. If capacity becomes insufficient, the first response is to optimize worker bounds, queue behaviour, and processing configuration before scaling the host.

### 7.3 Cancellation

Users may cancel a server job only while it remains queued. Cancellation atomically prevents worker pickup, marks the terminal state clearly, and schedules prompt cleanup of associated temporary data. If processing has already started, the UI reports that cancellation is no longer available. Closing the tab does not cancel an accepted job.

## 8. PDF engine subprocess boundary

Native PDF engines never execute on the API event loop; they run as separate subprocesses inside bounded worker containers.

Compress PDF invokes the official, unmodified Ghostscript distribution as a separate hardened subprocess. This is the approved integration boundary:

- Papyr does not vendor, fork, modify, embed, or link Ghostscript source into the application.
- Ghostscript is obtained from an authoritative upstream distribution, version-pinned, and invoked with standard safety flags.
- Other native engines follow the same subprocess and resource-isolation boundary when server execution is required.
- Worker processes receive only the minimum required task context and operate with constrained resources and temporary storage.

The subprocess boundary is one defense layer among several; it is not presented as a guarantee of complete isolation.

## 9. Temporary object storage lifecycle

### 9.1 Retention clock

- The one-hour maximum retention period starts when the backend first accepts the uploaded file, not when processing begins or completes.
- One hour is a hard upper bound, not a guaranteed retention period; objects may be deleted earlier after processing, failure, or cancellation.
- Source, intermediate, and result objects all expire at the same absolute deadline.
- Retries, polling, downloads, page focus, or an open tab never reset or extend the deadline.
- A successful download does not trigger early deletion; the object remains subject to the absolute expiry.
- An expired result cannot be restored; the user runs a new job.
- The API exposes the authoritative expiry timestamp so client countdowns do not depend on client clocks.

### 9.2 Deletion model

The application actively deletes temporary objects according to each job's absolute deadline, which cannot exceed 3600 seconds from upload receipt. R2 lifecycle expiration is day-granular, so its one-day minimum rule provides independent backup cleanup and is not the primary timer or an extension of the hard maximum. Cleanup is idempotent, observable without logging content or sensitive identifiers, and recoverable after restarts. Cleanup telemetry records counts and timing only.

### 9.3 Object key hygiene

Object keys are opaque and carry no filenames, user identifiers, passwords, or sensitive metadata. Keys never appear in analytics, application logs, support reports, or public status data.

## 10. Threat model and security controls

### 10.1 Threat model

The main threats the design controls for:

| Threat | Primary controls |
| --- | --- |
| Malformed or hostile document input | Structure and resource validation, maintained malware scanning, sanitization, bounded resources, isolated processing |
| Resource exhaustion (CPU, memory, time, storage) | Per-job and per-service bounds, hard safety caps, bounded queue |
| Active PDF content executing or leaking data | Sanitization of PDF-producing outputs, server-path routing for detected active content, fail-closed behaviour |
| Unauthorized access to results | Capability-based task access, short-lived signed URLs, opaque identifiers |
| Sensitive-data leakage to logs or analytics | Data-minimization policy, prohibited-data register, tested guards |
| Abuse and denial of service | Edge and proxy filtering, rate limiting, adaptive fair-use controls |
| Compromise of processing services | Container hardening, non-root execution, network restrictions, least privilege |

Papyr does not claim perfect malware detection, universal sanitization, or complete isolation. Accepted files are not claimed malware-free, and security tooling is tuned through normal functional and security testing plus production observation.

### 10.2 Security controls

- Validate actual file structure and decoded-resource risk rather than trusting extensions or browser MIME values.
- Apply rate, size, page, count, and concurrency limits before expensive processing.
- Layered defenses: edge and proxy filtering, application-level validation, maintained general malware scanning, active-content sanitization, bounded resource controls, and hardened container isolation.
- Block files classified as threats to infrastructure; never process or return them, and run prompt cleanup within the retention ceiling.
- Run processing containers with non-root execution, read-only root filesystems where feasible, dropped capabilities, no-new-privileges, and ephemeral writable areas.
- Keep Redis and worker services on internal networks with no public exposure.
- Store production secrets outside source control and public images, with restrictive permissions and rotation procedures.
- Exclude document bodies, filenames, passwords, signed URLs, object keys, and extracted text from logs, traces, analytics, alerts, and backups.
- Return stable public error categories rather than internals.
- Pin CI actions by commit SHA and scan source with vulnerability and secret scanners.
- Treat all server inputs as untrusted, including inputs whose output does not represent the input (for example, rasterized PDF pages).

## 11. Observability

Target observability combines:

- Structured application logs with request and task correlation IDs, retained for a defined period (30 days is the target) and free of document-derived data.
- Host and container resource metrics.
- Outside-in uptime checks.
- Sanitized error reporting.
- Operational alerts that carry no document-derived data or credentials.
- Cleanup telemetry recording counts and timing only.

Monitoring coverage includes the API, queue, workers, Redis, processing engines, storage integration, cleanup health, and relevant public endpoints. Metrics must support capacity decisions without collecting sensitive document attributes.

### 11.1 Public status experience

A simple public status page shows material service availability and incidents in plain language without sensitive infrastructure details. It is hosted on the frontend platform so it stays useful during a backend outage, and is updated automatically from approved health signals rather than manual incident copy. Status wording distinguishes observable service availability from guarantees about every engine or request, and the page does not claim complete infrastructure independence.

## 12. Deployment topology and delivery boundary

### 12.1 Target host topology

The target backend topology is Nginx, FastAPI, Redis, and bounded workers in one Docker Compose stack on a dedicated host. Nginx is the only host service exposed to the public; Redis and worker ports are never published. The Compose template declares health checks for api, nginx, and redis, resource limits, restart behaviour, and bounded log rotation. Startup dependencies use service-health conditions where they exist: workers start after Redis is healthy and Nginx starts after the API is healthy. The API service runs standalone with no Redis or worker dependency in the foundation template, and the worker healthcheck is deferred until the worker image digest is published (`Dockerfile.worker` unwired).

### 12.2 Delivery boundary

CI is continuous integration only. The repository CI:

- Runs on every push and pull request to the main branch.
- Requires 20 checks on pull requests (19 on pushes to main, where the PR-only dependency review is skipped), across three groups: core quality (frontend format and lint, frontend unit tests with coverage, frontend production build, Playwright E2E, backend lint and format, backend strict mypy, backend tests with an 80 percent coverage floor), security and supply chain (Trivy filesystem and configuration scan, gitleaks full-history secret scan, dependency review, npm audit, pip audit), and repository QA (action pin verification, Dockerfile lint, production-image build and non-root smoke, Compose structural validation, workflow YAML lint, markdownlint, shellcheck).
- Third-party actions are pinned to immutable commit SHAs.
- Jobs use least-privilege read-only permissions and do not persist checkout credentials.
- Contains no deployment steps and consumes no production credentials.

Production release, infrastructure mutation, credential provisioning, TLS and firewall policy, backup configuration, and monitoring wiring are separate, explicitly authorized operational procedures. CI never changes production.

### 12.3 Release and rollback posture

Release artifacts are traceable: container images are referenced by immutable digest or unique tag, and generated security reports are retained as CI artifacts. Normal rollback restores the previously verified healthy image and matching configuration through the stack tooling; full host restore is a disaster-recovery mechanism, not the ordinary rollback path.

## 13. Failure behaviour and cleanup guarantees

- Frontend, backend, and storage are separate failure domains. A backend incident does not take down the informational site or browser-capable tools.
- Processing-engine failures are isolated by tool: a failed engine disables only the affected tool or path, and admission stops accepting work that cannot currently run rather than queuing it indefinitely.
- Browser-only and server-dependent paths fail and recover independently.
- Invalid, expired, unsupported, or unsafe work fails closed with stable user-facing categories rather than engine internals.
- A Redis outage degrades server-job admission and status; browser-only tools remain available. If Redis state is lost, in-flight server jobs fail within their timeouts and the storage lifecycle safety net still enforces the one-hour ceiling.
- Cleanup is guaranteed by two independent mechanisms: application-driven deletion per job deadline and a storage lifecycle rule. Either mechanism alone is insufficient; both must be verified.
- The frontend never redirects ordinary tool traffic to the status page and never globally disables tools during a backend incident.

## 14. Non-functional targets

The following are targets, not claims of achieved or measured performance. They become verifiable as the corresponding components are implemented and observed in operation.

| ID | Target | Current evidence |
| --- | --- | --- |
| NFR-01 | Server-side objects are removed no later than one hour after upload receipt | Implemented (cleanup coordinator + lifecycle template); live-bucket lifecycle rule application remains a separately authorized release action |
| NFR-02 | Operational logs retain no document-derived data and are kept for 30 days | Logging policy enforced by privacy-safe logger and leakage tests; 30-day retention in production operation |
| NFR-03 | Backend unit-test coverage floor of 80% | Enforced by CI (measured ~89%) |
| NFR-04 | One active worker executing one concurrent native job at launch | Worker capacity targets tuned from production observability |
| NFR-05 | Browser-capable tools remain usable during backend incidents | Design property; tool flows exist and are deployed |
| NFR-06 | Task status and download authorization complete within bounded, non-extending retention | Implemented; enforced by signed-URL cap and retention deadline |
| NFR-07 | Healthy Core Web Vitals and fast task completion | Targets; exact numeric targets are set during implementation planning and validated from production observation, not promised in advance |
| NFR-08 | Reliability, queue latency, and uptime measured on a 90-day operating basis | Target; no production SLO evidence exists today |

No service-level agreement, uptime percentage, delivery date, or production performance figure is claimed. Numeric thresholds are established during implementation planning and refined from real production observation.

## 15. Verification strategy

A target component becomes implemented only when its code, tests, configuration, and operational constraints are present. Verification layers:

| Layer | Coverage |
| --- | --- |
| Unit | Frontend logic (range parsing, merge, split, image and PDF utilities, naming), backend services (validation, sanitization, task transitions, naming), shared contracts |
| Integration | API admission against per-tool limits, queue enqueue, claim, and status behaviour, storage upload and delete with expiry enforcement, signed-URL issuance and refresh, cleanup idempotency and recovery |
| End to end | Complete tool flows across all five tools in all three launch languages, including auto and manual download, fallback routing, error states, and refresh recovery |
| Accessibility | Automated scans plus manual keyboard and assistive-technology passes against WCAG 2.2 Level AA, across the supported browser matrix |
| Security | Dependency and container scanning, secret scanning, sanitization and malware-scan behaviour, threat-blocking behaviour, data-leakage guards on logs, analytics, and task records |
| Production smoke | Post-deployment health verification on every authorized deployment |

Privacy and retention verification is explicit: automated tests assert that passwords, filenames, signed URLs, object keys, and document contents never reach logs, analytics, persisted task records, or backups, and that expiration and cleanup behave as specified. Passing tests and security scans are not claims of malware-free files, perfect sanitization, or legal compliance.

## 16. Architecture status matrix

Status values match the product specification: **Available now**, **Deployed**, **In branch**, **Specified**, and **Planned**.

| Component | Status | Basis |
| --- | --- | --- |
| Next.js frontend foundation | Available now | `frontend/` source and tests |
| FastAPI service foundation (app factory, strict configuration, health and readiness endpoints, request correlation, stable error envelope, validation schemas) | Available now | `backend/` source and tests |
| Deployment templates (Compose, Nginx, environment, runbook) | Available now | `deploy/` |
| Continuous integration (20 required checks: quality, security and supply chain, repository QA) | Available now | `.github/workflows/ci.yml` |
| Shared trilingual shell: locale routing, accessible navigation, supporting route shells, localized 404, and unit and E2E gates | Deployed | `frontend/src/app/[locale]/`, `frontend/src/components/`, `frontend/src/lib/i18n.ts`, `frontend/src/proxy.ts`; roadmap |
| Legal, support, and status route shells (privacy, terms, cookies and advertising, contact, status, roadmap) | Deployed | `frontend/src/app/[locale]/`; roadmap |
| Blog route shell | Available now | `frontend/src/app/[locale]/blog/` |
| Versioned `/api/v1` contract (capabilities, task status, signed downloads, upload/enqueue admission on all five tool routers, support contact) | Deployed | `backend/app/routers/` and their tests; roadmap |
| Capability and limits contract | Deployed | `backend/app/routers/capabilities.py` and its tests; roadmap |
| Server task state machine (pure transition core) | Available now | `backend/app/tasks/state_machine.py` and its tests |
| Task status API contract | Deployed | `backend/app/routers/status.py` and its tests; roadmap |
| Redis durable minimal-metadata queue | Deployed | `backend/app/queue/` and its tests; roadmap |
| Bounded workers and fair scheduling | Deployed | `backend/app/worker/`, `backend/app/security/fair_use.py`, and their tests; roadmap |
| Ghostscript subprocess boundary for Compress | Deployed | Section 8; roadmap |
| R2 object lifecycle and one-hour retention | Deployed | `backend/app/utils/r2.py`, `backend/app/tasks/cleanup.py`, `deploy/r2-lifecycle.json`, and their tests; the lifecycle rule is applied during a separately authorized release |
| Browser versus server routing model | Specified | Section 5 |
| Threat model and security controls | Specified | Section 10 |
| Observability and status experience | Specified | Section 11 |
| Full legal, support, and status content and functionality | Planned | Roadmap and operational procedures |
| Blog publishing programme | Planned | Roadmap |
| Hardened production deployment and release procedure | Planned | Roadmap and operational procedures |

## 17. Related documents

- [Product specification](product.md)
- [Architecture overview](../architecture.md)
- [Integration inventory](../integrations.md)
- [Product roadmap](../roadmap.md)
- [Security policy](../../SECURITY.md)
- [Contribution guide](../../CONTRIBUTING.md)
- [Repository readme](../../README.md)
