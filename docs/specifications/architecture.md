# Technical architecture specification

## Scope and status

This document defines Papyr's target technical architecture. The current repository implements a minimal web shell, a FastAPI health endpoint, deployment templates, and CI. Components described as target services are not yet available unless source code and tests demonstrate otherwise.

## System boundaries

Papyr separates four concerns:

1. **Web application** — localized product pages and browser-capable processing.
2. **API control plane** — validation, admission, task state, authorization capabilities, and cleanup coordination.
3. **Processing plane** — bounded workers and isolated PDF engines.
4. **Object lifecycle** — temporary inputs, intermediates, and results with deterministic expiry.

The web application and backend are independently deployable. CI is not a deployment mechanism.

## Web application

The target frontend is a Next.js application hosted independently from backend compute. It owns:

- Locale-aware routing and metadata.
- Accessible shared upload, progress, error, and result components.
- Browser capability checks and local processing.
- Explicit transition to server processing when required.
- Short-lived task and download capability handling.

Browser code receives only public configuration. Provider credentials and private infrastructure identifiers never enter client bundles.

## API

The target API uses versioned routes under `/api/v1`. It is asynchronous and must not run blocking native engines on the event loop. Responsibilities include:

- Input metadata validation and admission limits.
- Capability-based task access.
- Queue submission and state reads.
- Short-lived signed download issuance.
- Cancellation and expiry coordination.
- Stable, non-sensitive error responses.

The current backend exposes only `GET /health`.

## Queue and scheduling

Redis is the target durable coordination store. Queue records contain only opaque task identity, state, timestamps, expiry, route, and non-sensitive temporary object references. They exclude file contents, original filenames, passwords, previews, signed URLs, and analytics payloads.

Scheduling is bounded and fair. Initial capacity is intentionally conservative: one active worker and one concurrent native job until operational evidence supports a change. Accepted work may queue rather than consuming unbounded resources. Paid priority is not part of the launch design.

## Worker isolation

Native processing executes in dedicated workers with:

- Per-job CPU, memory, wall-clock, file-count, page-count, and output limits.
- Ephemeral writable directories and deterministic cleanup.
- No external network access unless a narrowly specified operation requires it.
- Minimal process environment and no provider credentials unrelated to the job.
- Sanitized logs that exclude user document data and engine command details.
- Fail-closed cancellation and timeout handling.

Compress PDF invokes the official, unmodified Ghostscript distribution as a separate subprocess. The application does not vendor, fork, modify, embed, or link Ghostscript source. Other native engines follow the same process boundary.

## Temporary object storage

Cloudflare R2 is the target temporary object store. Requirements:

- Opaque, non-identifying object keys.
- Separate source, intermediate, and result namespaces or equivalent policy boundaries.
- Application-driven deletion on completion, failure, cancellation, and expiry.
- A storage lifecycle safety net enforcing a one-hour maximum-retention target.
- Short-lived signed downloads issued only after task authorization.
- No document-derived data in object metadata.

## Security controls

- Validate type and structure rather than trusting extensions or browser MIME values.
- Apply rate, size, page, count, and concurrency limits before expensive processing.
- Isolate native engines and drop unnecessary privileges.
- Keep Redis and worker services off the public network.
- Store production secrets outside source control and public images.
- Exclude document bodies, filenames, passwords, signed URLs, and extracted text from logs, traces, analytics, alerts, and backups.
- Return stable public error categories rather than internals.
- Pin CI actions and scan source with Trivy and gitleaks.

## Deployment topology

The target backend topology is Nginx, FastAPI, Redis, and bounded workers in a Docker Compose stack on a dedicated host. Nginx exposes only required HTTP entry points. Redis is internal. Production images, TLS, firewall policy, backups, monitoring, and credential provisioning are release concerns and are not implemented by the repository CI.

## Observability

Target observability combines:

- Structured application logs with request and task correlation IDs.
- Host and container resource metrics.
- Outside-in uptime checks.
- Sanitized error reporting.
- Operational alerts that carry no document-derived data or credentials.

Metrics must support capacity decisions without creating a benchmark programme or collecting sensitive document attributes.

## Continuous integration

Every push and pull request to `main` runs:

- Frontend format, lint, unit coverage, and production build.
- Backend lint, format, unit tests, and coverage.
- Trivy filesystem and configuration scan.
- Full-history gitleaks scan.

Third-party actions are pinned by commit SHA, checkout credentials are not persisted, and jobs have read-only repository permissions. CI contains no deployment steps and consumes no production credentials.

## Verification expectations

A target component becomes implemented only when its code, tests, configuration, and operational constraints are present. Documentation status must not substitute for runtime evidence. Product workflow acceptance requires tests for limits, cleanup, cancellation, authorization, failure paths, and sensitive-data exclusion in addition to successful processing.
