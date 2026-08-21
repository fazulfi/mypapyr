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
| [architecture.md](architecture.md) | contributors, operators, reviewers | Operational | Architecture overview of the web application, API control plane, processing plane, and object lifecycle. |
| [roadmap.md](roadmap.md) | contributors | Directional | Implementation status and planned milestones, from foundation to the five-tool launch catalogue and platform services. |
| [integrations.md](integrations.md) | contributors, operators, reviewers | Authoritative | Third-party integration inventory and each provider's role. |
| [specifications/product.md](specifications/product.md) | contributors | Authoritative | Product specification: the five tools, behaviour contracts, privacy commitments, and localized surface. |
| [specifications/architecture.md](specifications/architecture.md) | contributors, operators | Authoritative | Technical architecture specification: components, data flow, security boundaries, and versioned `/api/v1` contracts. |
| [environment-variables.md](environment-variables.md) | operators, contributors | Authoritative | Every environment variable: required vs optional, source, default, and reference. |
| [upgrade.md](upgrade.md) | operators | Operational | Backend, worker, and deployment upgrade procedure (Phase 4 -> Phase 5 topology, upgrade order, state invalidation). |
| [api-reference.md](api-reference.md) | operators, reviewers | Authoritative | Versioned `/api/v1` endpoint reference: schemas, failure codes, state machine, headers. |
| [ops-runbook.md](ops-runbook.md) | operators | Operational | Day-to-day operations: monitor probes, cleanup loop, worker health, incident response. |
| [deploy/runbook-vps.md](../deploy/runbook-vps.md) | operators | Operational | Authoritative VPS deployment, environment provisioning, and rollout/rollback runbook. |
| [testing.md](testing.md) | contributors, reviewers | Authoritative | Test layers, privacy/security test coverage, gate commands, and measured baselines. |
| [release-checklist.md](release-checklist.md) | operators, release managers | Operational | End-to-end release checklist: gates, CI, release build, activation, post-deploy verification. |
| [p6-completion-report.md](p6-completion-report.md) | contributors, operators, reviewers | Operational | Phase 6 enterprise completion: workstreams, evidence, deployment, verification, and known limitations. |
| [p7-completion-report.md](p7-completion-report.md) | contributors, operators, reviewers | Operational | Phase 7 operations completion: monitoring, derived status, Telegram relay, encrypted backups, owner gates, and deployment blockers. |
| [accessibility/exceptions-register.md](accessibility/exceptions-register.md) | contributors, reviewers | Authoritative | WCAG 2.2 accessibility program (DEC-062): scan scope, rule set, and the register of documented exceptions. |
| [verification/visual-baseline.md](verification/visual-baseline.md) | contributors, reviewers | Operational | Rendered visual verification baseline: route/viewport matrix, token and WCAG contrast contract, artifact location (VL-03). |
| [verification/performance.md](verification/performance.md) | contributors, reviewers | Operational | Core Web Vitals and performance gates: R-27 targets per DEC-200/201, ad-slot stability, measurement procedure (VL-04). |
| [verification/smoke.md](verification/smoke.md) | operators | Operational | Pre-launch smoke procedure: offline preflight, HTTP smoke, and rollback-preflight evidence modes (VL-05). |
| [verification/launch-checklist.md](verification/launch-checklist.md) | operators, release managers | Operational | Launch activation checklist: gates, evidence capture, owner authorization (G-3), and post-launch verification (VL-05). |
| [CHANGELOG.md](../CHANGELOG.md) | contributors, operators, reviewers | Operational | User- and operator-facing change history. |
| [licensing.md](licensing.md) | contributors, reviewers | Authoritative | Licensing decision record: no license granted yet (all rights reserved), inbound=outbound note. |

## How to use this index

- **Contributors** start at the [contribution guide](../CONTRIBUTING.md), then read the two specifications that bound the scope: [product](specifications/product.md) and [architecture](specifications/architecture.md).
- **Operators** start at the [VPS deployment runbook](../deploy/runbook-vps.md) and the [environment variables](environment-variables.md) contract.
- **Reviewers** hold claims against the [capability status](../README.md#capability-status) in the root README: the source tree and its tests are the authority for what exists today, and the specifications are the authority for what is designed.

The `Planned` status is reserved for documents not yet published; every operational document above is present in this repository. Open a `docs/` contribution if you want to add coverage.
