# Security policy

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub Security Advisories for this repository. Do not open a public issue containing exploit details, credentials, private infrastructure information, user documents, or sensitive logs.

A useful report includes:

- A concise description of the issue.
- The affected component and revision.
- Reproduction steps or a minimal proof of concept.
- Expected impact and any known mitigations.

Please allow time for triage and remediation before public disclosure.

## Repository security controls

- Real credentials and private environment files are excluded from source control.
- Public environment templates contain names and placeholders only.
- GitHub Actions are pinned to immutable commit SHAs.
- CI uses least-privilege read permissions and does not deploy.
- Trivy scans the repository for high- and critical-severity filesystem and configuration findings.
- gitleaks scans full Git history for committed secrets.
- Frontend and backend tests enforce coverage thresholds.

## Application security direction

The product specifications require:

- Strict input validation and bounded file, page, memory, CPU, and execution limits.
- Browser-first processing where practical and isolated native subprocesses for server work.
- No document bodies, filenames, passwords, signed URLs, or extracted content in analytics or logs.
- Short-lived capabilities and deterministic deletion of temporary server-side objects.
- Fail-closed behaviour for unsupported, unsafe, expired, or unauthorized work.
- Network-restricted workers and a minimal runtime attack surface.

The current codebase is an engineering foundation, and this feature branch adds the product-level controls for the five-tool server path: strict admission validation, fail-closed ClamAV threat scanning wired into every tool router, a PDF sanitizer that refuses unsanitizable input, bounded worker execution, and deterministic cleanup. These controls are implemented in the branch and become enforceable in production after merge and separately authorized deployment.

The Phase 6 enterprise controls are implemented, tested, and deployed (release p6-complete-1786951216, 2026-08-17):

- **Contact (PT-03):** server-side validation, honeypot, Cloudflare Turnstile siteverify (soft gate), per-origin in-memory rate limiting (3 requests per 60 seconds), and best-effort Cloudflare Email Sending with counts-only delivery metrics — no message content or addresses in logs.
- **Advertising (PT-02):** reserved-dimension slots only, one ad unit per page, delivery gated by Do Not Track / Global Privacy Control, house-promo fallback on provider failure, and never beside the Download control or on status/legal/support surfaces.
- **Analytics (PT-01):** closed-field schema, redaction pipeline, and DNT/GPC-gated injection — no document bodies, filenames, passwords, signed URLs, or extracted content in telemetry.
- **Encrypted-PDF passwords (PT-04):** memory-only prompts in the merge flow, per-file validation at the admission sanitizer, passwords never persisted, logged, or echoed (enforced by a banned-field contract, DEC-174).

## Dependency posture

Third-party libraries and executables are consumed as pinned upstream dependencies. The compression path invokes the official, unmodified Ghostscript distribution (pinned 10.07.1, checksum-verified at image build) as a separate hardened subprocess; its source is not vendored, forked, modified, or linked into the application.

## Scope and limitations

Security tooling reduces risk but does not guarantee that every vulnerability, secret, or malicious input will be detected. This policy is not a certification, compliance statement, or warranty. Teams deploying Papyr must evaluate their own threat model, dependencies, infrastructure, and legal obligations.
