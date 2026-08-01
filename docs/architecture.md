# Architecture overview

Papyr is designed as a browser-first PDF platform with an explicit, bounded server-processing path. The repository currently implements only the frontend, backend health service, deployment templates, and CI foundation described below. Queueing, storage, native processing, and the five PDF workflows remain planned capabilities.

## Current implementation

- A minimal Next.js application with strict TypeScript and automated quality gates.
- A minimal typed FastAPI application exposing `GET /health`.
- Public-safe Docker Compose and Nginx templates for `nginx`, `api`, `redis`, and `workers` services.
- CI-only GitHub Actions for formatting, linting, tests, coverage, builds, Trivy, and gitleaks.

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

## PDF engine boundary

Compress PDF is specified to invoke the official, unmodified Ghostscript distribution as a separate hardened subprocess. Papyr does not vendor, fork, modify, or link Ghostscript source into the application. Other PDF engines follow the same subprocess and resource-isolation boundary when server execution is required.

## Availability and failure behaviour

The frontend and backend are independently deployable. Browser-capable operations should remain available during a backend outage. Server-dependent operations report unavailability clearly. Invalid, expired, unsupported, or unsafe work fails closed with stable user-facing categories rather than engine internals.

## Delivery boundary

The repository CI verifies source quality and security but does not deploy. Production release, infrastructure mutation, credential provisioning, and data migration are separate operational procedures.

For detailed target contracts, see the [product specification](specifications/product.md), [technical architecture specification](specifications/architecture.md), and [roadmap](roadmap.md).
