# Contributing to Papyr

Papyr welcomes focused contributions to the application foundation, documentation, tests, security controls, and planned PDF workflows.

## Development workflow

1. Create a branch with a concise prefix such as `feat/`, `fix/`, `docs/`, `test/`, `security/`, `refactor/`, `ci/`, or `chore/`.
2. Write or update a test that demonstrates the required behaviour.
3. Confirm the test fails for the expected reason.
4. Implement the smallest correct change.
5. Run the relevant local quality gates.
6. Open a pull request with the user impact, verification evidence, and any remaining limitations.

## Commit messages

Use an imperative semantic subject:

```text
feat: add merge input validation
fix: preserve page ordering in split results
docs: clarify temporary-object lifecycle
security: harden subprocess environment
ci: pin dependency scanning action
```

Keep implementation and its direct tests together. Separate unrelated concerns into independent commits.

## Required checks

### Frontend

```bash
cd frontend
npm ci
npm run format:check
npm run lint
npm run test:coverage
npm run test:e2e
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

### Repository guards

```bash
bash scripts/check-ci.sh
```

## What CI runs on your PR

Pushing a branch runs the same CI pipeline that gates merges to `main` (`.github/workflows/ci.yml`). CI is **CI-without-CD**: it never deploys, and every job uses read-only permissions and no real secrets.

The pipeline runs **19 checks**, grouped as follows.

**Frontend**

- Frontend (Lint + Format)
- Frontend (Vitest + Coverage), gated at the project's coverage thresholds (\`npm run test:coverage\`)
- Frontend (Next.js production build)
- Frontend (Playwright E2E)

**Backend**

- Backend (Ruff lint + format)
- Backend (Strict mypy)
- Backend (Pytest + coverage threshold, gated at ≥80% measured coverage)

**Security**

- Security (Trivy filesystem/config scan, critical and high severity)
- Security (gitleaks secret scan, full repository history)

**Supply chain**

- Supply chain (dependency review on PRs — **PR-only**, not run on pushes)
- Supply chain (npm audit)
- Supply chain (pip-audit)

**Repository QA**

- QA (action pin truth)
- QA (hadolint)
- QA (compose structural gate)
- QA (production API image build + non-root smoke + compose config)
- QA (yamllint CI YAML)
- QA (markdownlint)
- QA (shellcheck)

**18 of 19** checks also run on every push to `main`; the **supply chain dependency review** runs only on pull requests. A merge to `main` is a squash merge, and it requires **all jobs that apply to the event to pass** (the PR-only dependency review applies to the PR itself, so effectively all 19 pass before merge).

The shared [repository guard](scripts/check-ci.sh) runs the local equivalents of these gates; keep it green before opening a PR, and never weaken CI, coverage thresholds, Trivy, or gitleaks to make a change pass.

## License and contributions

This repository has no declared `LICENSE` file and the owner has not issued a written open-source license decision; the root [README](README.md) states the source is provided for evaluation only until one is published. Contributor code is accepted on an **inbound = outbound** basis: accepted contributions are covered by the license the owner selects, matching how the existing project code is stewarded. Nothing in this guide grants any reuse, modification, or redistribution rights beyond what a future published license provides.

## Engineering standards

- Keep TypeScript strict; do not add `any`, `@ts-ignore`, or `@ts-expect-error` to bypass type safety.
- Keep Python interfaces typed and Ruff-clean.
- Never commit credentials, private environment files, real infrastructure addresses, or sensitive operational identifiers.
- Do not weaken CI, test coverage, Trivy, or gitleaks to make a change pass.
- Keep CI deployment-free. Release and production operations are separate procedures.
- Treat user documents as sensitive. Do not log filenames, document contents, passwords, signed URLs, or extracted text.
- Prefer bounded resource use, deterministic cleanup, and explicit error states.
- Update public specifications when product or architecture contracts change.
- Contributor code is accepted under the project's inbound = outbound licensing model; see the "License and contributions" section above.

## Product-scope discipline

The current implementation is intentionally small. Do not describe planned product capabilities as available until they are implemented and verified. The public roadmap and specifications distinguish current foundation code from target functionality.

Compress PDF may use the official, unmodified Ghostscript distribution as a separate server subprocess. Contributions must preserve the process boundary and must not vendor or modify Ghostscript source in this repository.

## Security reports

Do not disclose vulnerabilities or sensitive reproduction details in public issues. Follow the private reporting instructions in [SECURITY.md](SECURITY.md).
