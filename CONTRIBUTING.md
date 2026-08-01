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

## Engineering standards

- Keep TypeScript strict; do not add `any`, `@ts-ignore`, or `@ts-expect-error` to bypass type safety.
- Keep Python interfaces typed and Ruff-clean.
- Never commit credentials, private environment files, real infrastructure addresses, or sensitive operational identifiers.
- Do not weaken CI, test coverage, Trivy, or gitleaks to make a change pass.
- Keep CI deployment-free. Release and production operations are separate procedures.
- Treat user documents as sensitive. Do not log filenames, document contents, passwords, signed URLs, or extracted text.
- Prefer bounded resource use, deterministic cleanup, and explicit error states.
- Update public specifications when product or architecture contracts change.

## Product-scope discipline

The current implementation is intentionally small. Do not describe planned product capabilities as available until they are implemented and verified. The public roadmap and specifications distinguish current foundation code from target functionality.

Compress PDF may use the official, unmodified Ghostscript distribution as a separate server subprocess. Contributions must preserve the process boundary and must not vendor or modify Ghostscript source in this repository.

## Security reports

Do not disclose vulnerabilities or sensitive reproduction details in public issues. Follow the private reporting instructions in [SECURITY.md](SECURITY.md).
