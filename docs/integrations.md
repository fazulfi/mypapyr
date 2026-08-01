# Integration inventory

This public inventory lists the target external services and dependencies without credentials or private operational identifiers. A listed integration is not evidence that production wiring is complete.

| Integration | Purpose | Repository status |
| --- | --- | --- |
| GitHub | Source hosting, pull requests, and CI | Active for this repository |
| Vercel | Target frontend hosting and independent status surface | Configuration contract documented |
| Cloudflare | Target DNS, TLS, edge proxying, and coarse abuse controls | Configuration contract documented |
| Cloudflare R2 | Target temporary object storage for server-processed documents | Configuration contract documented |
| VPS and Nginx | Target API, Redis, and bounded worker hosting | Public-safe templates only |
| Redis | Target durable queue and minimal task-state store | Service template only |
| Ghostscript | Planned Compress PDF engine, invoked as an official unmodified subprocess | Approved architecture dependency; workflow not implemented |
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

The planned compression workflow uses the official, unmodified Ghostscript distribution. Papyr invokes it as a separate hardened server-side subprocess with pinned versions and bounded execution. The project does not fork, modify, vendor, or link Ghostscript source into its application code.
