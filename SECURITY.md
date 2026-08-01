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

The current codebase is an engineering foundation. These product-level controls become enforceable as the corresponding workflows are implemented.

## Dependency posture

Third-party libraries and executables are consumed as pinned upstream dependencies. The planned compression path invokes the official, unmodified Ghostscript distribution as a separate hardened subprocess; its source is not vendored, forked, modified, or linked into the application.

## Scope and limitations

Security tooling reduces risk but does not guarantee that every vulnerability, secret, or malicious input will be detected. This policy is not a certification, compliance statement, or warranty. Teams deploying Papyr must evaluate their own threat model, dependencies, infrastructure, and legal obligations.
