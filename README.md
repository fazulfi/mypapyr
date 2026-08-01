# Papyr

Fast, simple, free PDF tools for the web — compress, merge, split, JPG to PDF, and PDF to JPG.

This repository is the Papyr rebuild workspace. The legacy application and full history live in the read-only clone at `papyr-reference/` (excluded from this repository).

## What this is

Papyr is a public web product offering five launch PDF tools:

- Compress PDF
- Merge PDF
- Split PDF
- JPG to PDF
- PDF to JPG

Languages at launch: English, Spanish, Indonesian.

## Monorepo layout

| Path | Purpose |
| --- | --- |
| `frontend/` | Next.js application (TypeScript, Vitest, ESLint 9). Targets Vercel. |
| `backend/` | FastAPI service with Redis queue and bounded workers. Targets the VPS. |
| `deploy/` | Docker Compose skeleton (Nginx, API, Redis, workers), Nginx config, `.env.production.example`, runbook. |
| `.github/workflows/ci.yml` | Continuous integration only — no deployment. |
| `docs/` | Canonical documentation: baseline, resolution register, specs, plans. |
| `scripts/` | Repository check and verification scripts (CI, docs migration). |
| `papyr-reference/` | Read-only legacy clone. EXCLUDED from this repository. Never modify. |

## Governed records

| Record | Path |
| --- | --- |
| Master implementation plan | [`docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`](docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md) |
| Product & UX specification | `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` |
| Technical architecture specification | `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` |
| Living decision log | `papyr-rebuild-decisions.md` (append-only, DEC-001..DEC-202+) |
| Canonical documentation baseline | `docs/canonical-docs-baseline.md` |
| Owner resolution register | `docs/resolution-register.md` (R-01..R-28 dispositions) |
| Orchestrator rules | `AGENTS.md` |

## Local development quickstart

All commands assume you are at the repository root unless noted otherwise.

### Frontend (`frontend/`)

```bash
cd frontend
npm ci                  # install dependencies
npm run dev             # local development server
npm test                # unit tests (Vitest)
npm run lint            # ESLint
npm run build           # production build
```

Additional npm scripts defined in `frontend/package.json`: `start`, `test:e2e`, `format:check`.

### Backend (`backend/`)

```bash
cd backend
python -m venv .venv
# activate the venv per your shell/OS
pip install -r requirements.txt -r requirements-dev.txt
pytest                  # run the test suite
ruff check .            # lint
ruff format --check .   # format check
```

## Continuous integration overview

CI is defined in `.github/workflows/ci.yml` and is continuous integration only — **there is no deployment step in CI**. CI runs on every push and pull request and consists of the following jobs:

- **Frontend lint + format** — Prettier format check and ESLint.
- **Frontend unit tests + coverage** — Vitest with coverage.
- **Frontend production build** — Next.js production build.
- **Backend lint + format** — Ruff lint and format check.
- **Backend tests + coverage gate** — Pytest with a coverage floor of 80%.
- **Security — Trivy** — Filesystem and config scan, SARIF report uploaded as an artifact.
- **Security — gitleaks** — Secret scan.

All third-party GitHub Actions are referenced by full commit SHA. No CD: deployment is performed outside of CI in a later, explicitly authorized phase.

## Documentation

- Phase planning entry point: [`docs/plan/index.md`](docs/plan/index.md).
- Contribution conventions: [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Master implementation plan: [`docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`](docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md).

## Limitations

This repository and the project it describes are provided **as-is**. Nothing in this README, in the documentation, or in the code constitutes:

- Legal advice, legal compliance, or certification of compliance with any law, regulation, or standard.
- A guarantee that any particular file, page, document, or input is or is not malicious, harmful, infringing, or otherwise unsuitable.
- A representation that the privacy, data-handling, or security posture of the system is sufficient for any particular use case, jurisdiction, or threat model.
- A representation of legal sufficiency for any contract, policy, or user-facing claim.

Papyr is a working tool product under active development. Outputs depend on third-party libraries and infrastructure whose behavior may change. Use at your own discretion; consult qualified professionals before relying on the system for any purpose that carries legal, security, privacy, or safety implications.