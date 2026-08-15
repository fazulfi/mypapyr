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
| Ghostscript | Compress PDF engine, invoked as an official unmodified subprocess | Implemented in branch: pinned build in the worker image; pending merge and deployment |
| AI gateway | Planned model gateway for explicitly specified server features | Environment contract only |
| Sentry | Planned sanitized application error reporting | Environment contract only |
| Telegram | Planned operational incident alerts | Environment contract only |
| S3-compatible backup storage | Planned encrypted operational backups | Environment contract only |
| Advertising provider | Planned non-obstructive banner placement | Environment contract only |

## Integration rules

- Secrets are provisioned outside the repository.
- Public templates use placeholders only.
- User document contents, filenames, passwords, signed URLs, and extracted text must not be sent to analytics, error monitoring, alerting, or advertising services.
- Temporary object storage must use opaque keys and deterministic expiry.
- CI never authenticates to or mutates production integrations.
- Value-level configuration is verified during a separately authorized release procedure.

## Ghostscript

The compression workflow uses the official, unmodified Ghostscript distribution, implemented in this feature branch. Papyr invokes it as a separate hardened server-side subprocess with pinned versions and bounded execution. The project does not fork, modify, vendor, or link Ghostscript source into its application code.

## Redis

The repository implements Redis as the durable queue and minimal task-state store. A `jobs` stream with a `workers` consumer group carries only minimal task metadata — never document bodies, passwords, signed URLs, or extracted text — and each worker instance processes one in-flight job with automatic recovery of stale claims. The queue is bounded at 2,000 entries with a 900-second oldest-wait ceiling, and adaptive fair-use controls keyed by SHA-256 origin fingerprints enforce per-origin concurrency and frequency limits with allow, delay, challenge, and reject levels, failing closed when Redis is unavailable. Every task record carries a TTL within the one-hour retention target, and the approved operating contract pins a bounded-memory `noeviction` configuration with AOF and RDB persistence. The Compose queue profile remains unactivated until worker images and production configuration are released.

## Cloudflare R2

The repository implements temporary object storage for server-processed documents. Objects are stored under opaque, non-identifying keys in a dated prefix, and uploads mirror the artifact deadline with an 8,192-byte ASCII metadata limit. Download grants are presigned URLs capped at 300 seconds or the remaining artifact lifetime, whichever is shorter, and never extend beyond the one-hour retention target. A cleanup coordinator actively removes source, intermediate, and result objects at their hard 3,600-second deadline before deleting task records, with counts-and-timing telemetry only. R2 lifecycle expiration is day-granular, so its one-day-minimum template on the temporary and multipart prefixes is an independent safety net, not an extension of or substitute for the hard maximum; it is applied to the bucket out of band during a separately authorized release. Moto-based tests verify client behaviour, while real-R2 authentication and expiry are validated during release.
