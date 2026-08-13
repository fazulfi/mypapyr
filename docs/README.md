# Papyr documentation index

This index maps every repository document to its intended audience and its status, so each reader can find the authoritative source for the question they are trying to answer.

Status legend:

- **Authoritative** — the live contract. The code and tests are the authority for what exists today; these documents are the authority for required behaviour, conventions, and values. Discrepancies between code and these documents are defects.
- **Operational** — step-by-step procedures for running, deploying, and operating the system.
- **Directional** — intent and trajectory; explicitly not a release commitment.
- **Planned** — the document is planned but not yet published in this repository.

| Document | Audience | Status | Purpose |
| --- | --- | --- | --- |
| [README.md](../README.md) | contributors, operators, reviewers | Authoritative (entry point) | Project overview, architecture, quickstart, capability status. |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | contributors | Authoritative | Development workflow, required local checks, what CI runs on your PR, engineering standards. |
| [SECURITY.md](../SECURITY.md) | contributors, reviewers | Authoritative | Private vulnerability reporting and the full security control inventory. |
| [docs/architecture.md](docs/architecture.md) | contributors, operators, reviewers | Operational | Architecture overview of the web application, API control plane, processing plane, and object lifecycle. |
| [docs/roadmap.md](docs/roadmap.md) | contributors | Directional | Implementation status and planned milestones, from foundation to the five-tool launch catalogue and platform services. |
| [docs/integrations.md](docs/integrations.md) | contributors, operators, reviewers | Authoritative | Third-party integration inventory and each provider's role. |
| [docs/specifications/product.md](docs/specifications/product.md) | contributors | Authoritative | Product specification: the five tools, behaviour contracts, privacy commitments, and localized surface. |
| [docs/specifications/architecture.md](docs/specifications/architecture.md) | contributors, operators | Authoritative | Technical architecture specification: components, data flow, security boundaries, and versioned `/api/v1` contracts. |
| [docs/environment-variables.md](docs/environment-variables.md) | operators, contributors | Authoritative | Every environment variable: required vs optional, source, default, and reference. |
| [docs/upgrade.md](docs/upgrade.md) | operators | Operational | Backend, worker, and deployment upgrade procedure (Phase 4 -> Phase 5 topology, upgrade order, state invalidation). |
| [docs/api-reference.md](docs/api-reference.md) | operators, reviewers | Authoritative | Versioned `/api/v1` endpoint reference: schemas, failure codes, state machine, headers. |
| [docs/ops-runbook.md](docs/ops-runbook.md) | operators | Operational | Day-to-day operations: monitor probes, cleanup loop, worker health, incident response. |
| [deploy/runbook-vps.md](../deploy/runbook-vps.md) | operators | Operational | Authoritative VPS deployment, environment provisioning, and rollout/rollback runbook. |
| [CHANGELOG.md](../CHANGELOG.md) | contributors, operators, reviewers | Operational | User- and operator-facing change history. |
| [docs/licensing.md](licensing.md) | contributors, reviewers | Authoritative | Licensing decision record: no license granted yet (all rights reserved), inbound=outbound note. |

## How to use this index

- **Contributors** start at the [contribution guide](../CONTRIBUTING.md), then read the two specifications that bound the scope: [product](docs/specifications/product.md) and [architecture](docs/specifications/architecture.md).
- **Operators** start at the [VPS deployment runbook](../deploy/runbook-vps.md) and the [environment variables](docs/environment-variables.md) contract.
- **Reviewers** hold claims against the [capability status](../README.md#capability-status) in the root README: the source tree and its tests are the authority for what exists today, and the specifications are the authority for what is designed.

The `Planned` status is reserved for documents not yet published; every operational document above is present in this repository. Open a `docs/` contribution if you want to add coverage.
