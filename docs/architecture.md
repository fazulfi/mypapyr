# Architecture overview

This document is a high-level overview of the Papyr rebuild monorepo. It intentionally does **not** duplicate the authoritative content in the technical architecture specification or the product & UX specification. It exists only to give a reader enough context to navigate those specs and the rest of the repository.

## Authoritative specifications

The complete, authoritative description of the system, its components, data flows, and boundaries lives in:

- Technical architecture specification — [`docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`](superpowers/specs/2026-07-31-papyr-technical-architecture.md)
- Product & UX specification — [`docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md`](superpowers/specs/2026-07-31-papyr-product-ux-design.md)
- Master implementation plan — [`docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`](superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md)
- Canonical documentation baseline — [`canonical-docs-baseline.md`](canonical-docs-baseline.md)
- Owner resolution register — [`resolution-register.md`](resolution-register.md)
- Planning index — [`plan/index.md`](plan/index.md)

Any architecture question that this overview does not answer must be resolved by reading the technical architecture specification and the relevant decision in `papyr-rebuild-decisions.md`.

## Monorepo layout at a glance

The rebuild repository is a single monorepo with the following top-level areas. The complete path inventory and rationale are recorded in the README's "Monorepo layout" table; the table below is a navigation pointer only.

| Path | Role | Hosted / built for |
| --- | --- | --- |
| `frontend/` | Next.js application (TypeScript, Vitest, ESLint 9). | Vercel. |
| `backend/` | FastAPI service with Redis queue and bounded workers. | The VPS. |
| `deploy/` | Docker Compose skeleton: Nginx, API, Redis, workers. Includes Nginx config, `deploy/.env.production.example`, and the operational runbook. | The VPS. |
| `.github/workflows/ci.yml` | The CI pipeline. Runs lint, format, unit tests, coverage, production build, Trivy scan, and gitleaks scan. **CI only — no deployment.** | GitHub Actions. |
| `docs/` | Canonical documentation: baseline, resolution register, specs, plans, supplementary docs. | Repository. |
| `scripts/` | Repository check and verification scripts (CI, docs migration). | Repository. |
| `papyr-reference/` | Read-only legacy clone. **Never modify.** Excluded from the rebuild repository. | Operator workstation only. |

## Frontend — Next.js on Vercel

The frontend is the user-facing web product. It is a Next.js application built and deployed (in a later, owner-authorized phase) to Vercel under the project identifier `papyr` and the production domain `mypapyr.com`. Local development, test, lint, and build commands are documented in the README's "Local development quickstart" section; the *behaviour* of the application, its routing, and its localized content are specified in the product & UX specification and the technical architecture specification (§4).

## Backend — FastAPI on the VPS

The backend exposes the `/api/v1` endpoints used by the frontend. It is a Python FastAPI service that runs on the same VPS as the Redis queue and the bounded PDF workers, fronted by Nginx. The service inventory, hardening baseline, resource bounds, and startup dependencies are specified in the technical architecture specification (§7). The backend is **not** deployed by Phase 0; see [`docs/deployment-boundary.md`](deployment-boundary.md) for the explicit boundary.

## Deploy — Docker Compose skeleton

The `deploy/` directory holds the Docker Compose skeleton for the VPS, the Nginx configuration, the public-safe `deploy/.env.production.example` template, and the operational runbook. The stack follows the "one production Docker Compose stack" model (DEC-162): Nginx, API, Redis, and workers are managed together. Detailed service definitions, restart policies, and resource limits are specified in the technical architecture specification (§7).

## CI — `.github/workflows/ci.yml`

The CI pipeline is defined in `.github/workflows/ci.yml`. It runs on every push and pull request and consists of the following job families:

- Frontend lint + format (Prettier, ESLint).
- Frontend unit tests + coverage (Vitest).
- Frontend production build (Next.js).
- Backend lint + format (Ruff).
- Backend tests + coverage gate (Pytest, 80% floor).
- Security — Trivy filesystem and config scan (SARIF artifact).
- Security — gitleaks secret scan.

All third-party GitHub Actions are referenced by full commit SHA. **There is no deployment step in CI.** This is the foundation contract and is reinforced by `CONTRIBUTING.md` and [`docs/deployment-boundary.md`](deployment-boundary.md).

## Documentation layout

The `docs/` directory is organized into:

- `docs/canonical-docs-baseline.md` — the governed-record baseline.
- `docs/resolution-register.md` — the owner resolution register (R-01..R-28).
- `docs/plan/index.md` — the planning index.
- `docs/superpowers/specs/` — the product & UX specification and the technical architecture specification.
- `docs/superpowers/plans/` — the master implementation plan and any phase-specific plans.
- `docs/architecture.md` — this document.
- `docs/deployment-boundary.md` — the explicit CI-only / no-CD boundary.
- `docs/integration-inventory.md` — the third-party integration inventory for Phase 0.
- `docs/SECURITY.md` is referenced from `SECURITY.md` at the repository root.

## What this document does not do

- It does not restate the topology, data flows, or service boundaries from the technical architecture specification. Read the spec.
- It does not list every convention, branch name, or commit prefix; those are in `CONTRIBUTING.md`.
- It does not describe the deployment procedure or operational runbook; those live in `deploy/` and are gated by [`docs/deployment-boundary.md`](deployment-boundary.md).
- It does not claim compliance, certification, or a definitive security posture. The limitations in `README.md` apply.
