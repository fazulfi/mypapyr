# Papyr

Papyr is an open PDF utility platform focused on a fast, clear, and privacy-respectful workflow. The planned launch catalogue includes Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG in English, Spanish, and Indonesian.

This repository currently provides the tested engineering foundation for that product: a minimal Next.js application, a typed FastAPI health service, deployment configuration templates, secure continuous integration, and public product and architecture specifications. The five PDF workflows are specified but are not implemented in the current codebase.

## Product direction

- Five focused PDF utilities with consistent upload, progress, and download experiences.
- Browser-first processing where practical, with an explicit server path for work that requires native engines or stronger isolation.
- Anonymous use without accounts or stored cross-device history at launch.
- English, Spanish, and Indonesian as first-class launch languages.
- A strict one-hour maximum retention target for temporary server-processed objects.
- Transparent processing location, failures, and reported compression results.

See the [product specification](docs/specifications/product.md) and [technical architecture](docs/specifications/architecture.md) for the target behaviour and boundaries.

## Current repository status

| Area | Available now | Planned next |
| --- | --- | --- |
| Frontend | Minimal Next.js shell, strict TypeScript, linting, formatting, unit-test and build configuration | Product shell, localization, upload flow, and five tool interfaces |
| Backend | Minimal typed FastAPI service with `/health` and full unit coverage | Versioned tool APIs, validation, queue coordination, workers, and lifecycle controls |
| Infrastructure | Public-safe Compose, Nginx, and environment templates | Hardened images, production wiring, storage lifecycle, and operations automation |
| Delivery | Seven required CI checks with no deployment steps | Separately authorized release and deployment procedures |

## Repository layout

| Path | Purpose |
| --- | --- |
| `frontend/` | Next.js and React frontend foundation. |
| `backend/` | FastAPI backend foundation. |
| `deploy/` | Public-safe Docker Compose, Nginx, environment, and runbook templates. |
| `.github/workflows/ci.yml` | CI-only quality and security gates. |
| `docs/specifications/` | Public product and technical specifications. |
| `docs/roadmap.md` | Honest implementation status and planned milestones. |
| `scripts/` | Repository validation scripts. |

## Technology foundation

- **Frontend:** Next.js 16, React 19, TypeScript 6, Tailwind CSS 4, Vitest, ESLint, Prettier, and Playwright.
- **Backend:** FastAPI, Python, Uvicorn, Pytest, Ruff, and typed interfaces.
- **Target processing architecture:** browser-capable PDF libraries plus isolated server subprocesses. Compress PDF is specified to use the official, unmodified Ghostscript distribution as a separate hardened subprocess.
- **Target platform:** Vercel for the web application, Cloudflare at the edge, Cloudflare R2 for temporary objects, and a bounded backend stack behind Nginx.

## Local development

### Frontend

```bash
cd frontend
npm ci
npm run dev
npm run format:check
npm run lint
npm run test:coverage
npm run build
```

### Backend

```bash
cd backend
python -m venv .venv
# Activate the virtual environment for your shell.
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
ruff format --check .
pytest tests/ --cov=app --cov-fail-under=80
```

## Continuous integration

CI runs on pushes and pull requests to `main` and requires:

- Prettier and ESLint checks.
- Vitest with coverage and a Next.js production build.
- Ruff lint and format checks.
- Pytest with an 80% coverage floor.
- Trivy filesystem and configuration scanning.
- Full-history gitleaks scanning.

Third-party GitHub Actions are pinned to immutable commit SHAs. CI does not deploy, publish images, connect to production hosts, or consume production credentials.

## Documentation

- [Product specification](docs/specifications/product.md)
- [Technical architecture specification](docs/specifications/architecture.md)
- [Architecture overview](docs/architecture.md)
- [Integration inventory](docs/integrations.md)
- [Roadmap](docs/roadmap.md)
- [Security policy](SECURITY.md)
- [Contribution guide](CONTRIBUTING.md)

## Project limitations

Papyr is under active development. The present source tree is a foundation, not a completed PDF service or a production deployment. Product specifications and roadmap entries describe intended behaviour, not guaranteed delivery dates or currently available features.

The project does not claim legal compliance, certification, guaranteed malware removal, or suitability for a particular jurisdiction, security model, or regulated use case. Review the implementation and third-party dependencies for your own requirements before deployment.
