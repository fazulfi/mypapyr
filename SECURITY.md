# Security policy

This document describes the security policy for the Papyr rebuild repository at the workspace root. It is the public-facing counterpart to the secret-handling, scanning, and deployment-boundary rules already recorded in [`README.md`](README.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), and [`docs/deployment-boundary.md`](docs/deployment-boundary.md). Nothing in this document claims legal compliance, certification, or guaranteed security posture; the limitations in [`README.md`](README.md) apply.

## Supported scope

The security policy supports the **Phase 0 foundation** of the Papyr rebuild, which is a continuous-integration-only (CI-only) workload. In Phase 0:

- The repository is a monorepo skeleton with frontend, backend, deploy, and CI scaffolding.
- CI runs on every push and pull request: lint, format, unit tests, coverage, production build, Trivy filesystem scan, and gitleaks secret scan.
- There is **no continuous deployment (CD)**. CI does not push to Vercel, Cloudflare, the VPS, R2, the backup bucket, or any third-party integration. See [`docs/deployment-boundary.md`](docs/deployment-boundary.md) for the explicit boundary.
- The legacy clone at `papyr-reference/` is read-only and excluded from the rebuild repository. It is never modified, never deployed, and never used as a deployment source.

Anything outside this scope — a later release phase, a production deployment, an operational runbook, a third-party service integration — is **not covered** by this policy and requires an expanded, owner-approved security update.

## Reporting a vulnerability

Report a vulnerability, suspected vulnerability, or any security-sensitive issue through **private disclosure**. Do not open a public issue, do not post screenshots, and do not include real secret values, real IP addresses, real tokens, real chat IDs, or any specific exploit detail in any public channel.

When reporting:

- Use the dedicated private contact channel agreed with the project owner.
- Provide a short description, the affected scope, reproduction steps where available, and impact assessment.
- Allow a reasonable response window before any public disclosure. The project owner will coordinate the remediation timeline.

Public issues, public discussions, and public CI annotations are **not** acceptable channels for unredacted vulnerability reports. Security-sensitive reports should remain private until the owner approves disclosure.

## Secret-handling policy

The Papyr repository treats secret values as restricted artifacts at every stage of the lifecycle.

### Secrets never enter the repository

- Real secret values, tokens, API keys, signing keys, chat IDs, passwords, private DSNs, and real IP addresses **must not** be committed to any file in the repository.
- The repository-shipped template `.env.example` only lists **variable names**; every value is the literal placeholder `__SET_ME__`.
- The deploy template `deploy/.env.production.example` exists for the same reason: it is a public-safe placeholder file for the production environment contract.

### Local-only secret file

- The file `.env.papyr` is the operator's working secret store. It is **gitignored** and must remain so.
- Real secret values are never copied from `.env.papyr` into `README.md`, `CONTRIBUTING.md`, `docs/`, `audit-outputs/`, screenshots, chat transcripts, commit messages, or any other artifact that may be published, archived, or shared.
- Redaction before publication is mandatory: any value-shaped token, key, address, or identifier that appears in public artifacts must be replaced with a placeholder (`__SET_ME__`, `<vps-ip>`, `<token>`, `<chat-id>`) before the artifact is committed, shared, or cited.

### Production secret handling

- Production secrets are installed and rotated through the protected VPS environment-configuration procedure (DEC-176). Production environment files require restrictive ownership and permissions and must be excluded from source control, container images, backups where inappropriate, logs, and audit outputs.
- The rebuild requires rotation of legacy credentials and investigation of any historical exposure before production use.

### CI secret scanning

- **gitleaks** runs in CI as a secret-scanning job. It fails the build on any commit, push, or pull request that introduces a value matching its secret rules.
- **GitHub secret scanning** is enabled on the repository. Any token that is accidentally committed is reported by GitHub and revoked by the issuing provider.
- **Trivy** filesystem and config scan runs in CI as an additional preventive layer for misconfigurations and known-vulnerable patterns.

If a secret is committed accidentally, treat it as compromised: rotate the credential at the issuing provider, revoke the leaked value, audit downstream usage, and remove the value from history according to the provider's incident response procedure.

## Dependency scanning

Dependencies are scanned in CI on every push and pull request.

- **Trivy** produces a filesystem and configuration scan and uploads the SARIF report as a CI artifact.
- **gitleaks** scans the working tree for committed secrets.
- Coverage gates and tests do not directly scan for dependency vulnerabilities, but the bundled scans above cover the most common supply-chain and secret-leak vectors in Phase 0.

Phase 0 does not include a dedicated Software Composition Analysis (SCA) job, a runtime vulnerability scanner, or a periodic scheduled scan. Those are out of scope for the CI-only foundation and will be expanded when a later phase authorizes them.

## No-CD boundary

The CI pipeline does not deploy. There is no `deploy:` job, no `vercel deploy`, no `wrangler publish`, no `docker compose up`, no `ansible-playbook`, no `kubectl apply`, no `git push` to a deployment remote, and no operator-triggered production change issued by CI. This is the Phase 0 contract and is also enforced by `CONTRIBUTING.md` and the README's "Continuous integration overview" section. The detailed boundary is documented in [`docs/deployment-boundary.md`](docs/deployment-boundary.md).

Any change that would introduce deployment behavior into CI is a regression and must be rejected before merge.

## What this policy does not promise

This policy does not claim:

- Legal compliance, certification, or audit attestation.
- A guarantee that scanning tools catch every secret, vulnerability, or misconfiguration.
- A representation that the privacy, data-handling, or security posture of the system is sufficient for any particular use case, jurisdiction, or threat model.
- A representation of legal sufficiency for any contract, policy, or user-facing claim.

Papyr is a working tool product under active development. Outputs depend on third-party libraries and infrastructure whose behavior may change. Use at your own discretion; consult qualified professionals before relying on the system for any purpose that carries legal, security, privacy, or safety implications.
