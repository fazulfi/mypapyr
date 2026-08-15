# Integration inventory

This public inventory lists the target external services and dependencies without credentials or private operational identifiers. A listed integration is not evidence that production wiring is complete.

| Integration | Purpose | Repository status |
| --- | --- | --- |
| GitHub | Source hosting, pull requests, and CI | Active for this repository |
| Vercel | Target frontend hosting and independent status surface | Configuration contract documented |
| Cloudflare | Target DNS, TLS, edge proxying, and coarse abuse controls | Configuration contract documented |
| Cloudflare R2 | Target temporary object storage for server-processed documents | Implemented in repository: client, signed downloads, cleanup, and lifecycle template |
| VPS and Nginx | Target API, Redis, and bounded worker hosting | Public-safe templates only |
| Redis | Target durable queue and minimal task-state store | Implemented in repository: Streams queue, task store, and one-worker processing |
| Ghostscript | Compress PDF engine, invoked as an official unmodified subprocess | Implemented in branch: pinned 10.07.1 build in the worker image; pending merge/deployment |
| AI gateway | Planned model gateway for explicitly specified server features | Environment contract only |
| Sentry | Planned sanitized application error reporting | Environment contract only |
| Telegram | Planned operational incident alerts | Environment contract only |
| S3-compatible backup storage | Planned encrypted operational backups | Environment contract only |
| Advertising provider | Adsterra native unit with placement guards, frontend-only | Implemented in branch: reserved-dimension slot, lazy injection, placement guards; pending merge/deployment |

## Integration rules

- Secrets are provisioned outside the repository.
- Public templates use placeholders only.
- User document contents, filenames, passwords, signed URLs, and extracted text must not be sent to analytics, error monitoring, alerting, or advertising services.
- Temporary object storage must use opaque keys and deterministic expiry.
- CI never authenticates to or mutates production integrations.
- Value-level configuration is verified during a separately authorized release procedure.

## Ghostscript

The compression workflow uses the official, unmodified Ghostscript distribution, implemented in the feature branch. Papyr invokes it as a separate hardened server-side subprocess with pinned versions (10.07.1, checksum-verified at image build) and bounded execution. The project does not fork, modify, vendor, or link Ghostscript source into its application code.

## Redis

The repository implements Redis as the durable queue and minimal task-state store. A `jobs` stream with a `workers` consumer group carries only minimal task metadata — never document bodies, passwords, signed URLs, or extracted text — and each worker instance processes one in-flight job with automatic recovery of stale claims. The queue is bounded at 2,000 entries with a 900-second oldest-wait ceiling, and adaptive fair-use controls keyed by SHA-256 origin fingerprints enforce per-origin concurrency and frequency limits with allow, delay, challenge, and reject levels, failing closed when Redis is unavailable. Every task record carries a TTL within the one-hour retention target, and the approved operating contract pins a bounded-memory `noeviction` configuration.

## Cloudflare R2

The repository implements temporary object storage for server-processed documents. Objects are stored under opaque, non-identifying keys in a dated prefix, and uploads mirror the artifact deadline with an 8,192-byte ASCII metadata limit. Download grants are presigned URLs capped at 300 seconds or the remaining artifact lifetime, whichever is shorter, and never extend beyond the one-hour retention target. A cleanup coordinator actively removes source, intermediate, and result objects at their hard 3,600-second deadline before deleting task records, with counts-and-timing telemetry only. R2 lifecycle expiration is day-granular, so its one-day-minimum template on the temporary and multipart prefixes is an independent safety net, not an extension of or substitute for application-driven cleanup.

## Advertising (Adsterra, frontend-only)

The branch adds a single Adsterra native unit (300x250) with reserved dimensions to prevent layout shift. The slot is injected lazily on the client after it scrolls into view, renders only on the five tool pages after the primary task experience (result/download), never beside the Download control, and never on status, legal, or support surfaces. Ad presence is tracked only through the privacy-reviewed analytics schema; user documents, filenames, and passwords are never sent to the advertising provider.