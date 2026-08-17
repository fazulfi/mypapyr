# Testing strategy

This document describes how Papyr is tested across both workspaces, what each layer covers, and which commands produce the gate evidence used by CI and by the release process. The source tree and its tests are the authority for what exists today.

## Test layers

| Layer | Tooling | Location | Gate |
| --- | --- | --- | --- |
| Backend unit + integration | pytest 9.1.1, pytest-cov, fakeredis, moto | `backend/tests/` (60+ modules) | `pytest -q` + `pytest --cov=app --cov-fail-under=80` |
| Backend static analysis | ruff 0.14.4, mypy 2.3.0 (strict) | whole `backend/` | `ruff check .`, `ruff format --check .`, `mypy app tests --strict --no-incremental` |
| Frontend unit + component | Vitest 4, @testing-library/react, jsdom | `frontend/src/**/__tests__/` | `npm run test:coverage` (thresholds: lines 80 / funcs 80 / branches 80 / stmts 80) |
| Frontend static analysis | ESLint flat config, Prettier, tsc | whole `frontend/` | `npm run lint`, `npm run format:check`, `npm run typecheck` (`tsc --noEmit`) |
| Frontend build | Next.js 16 | whole `frontend/` | `npm run build` (production build, all routes prerendered/compiled) |
| End-to-end | Playwright 1.62.1, Chromium desktop + Pixel 7 | `frontend/e2e/` | `npm run test:e2e` (builds + serves locally; start-only in CI) |
| Repository QA | scripts in `scripts/`, qa-tools | repo root | `bash scripts/check-ci.sh` (no-CD guard, pin truth) |

## What each layer covers

### Backend

- **Unit tests** cover the app factory, settings contract (fail-fast on missing required env), error envelope and status table, task state machine transitions, queue admission (Lua check-and-XADD), CAS store transitions, fair-use policy, validation (BE-02), PDF sanitization (SEC-02, fail-closed), classification, R2 client (opaque keys, presigned URL ≤ 300 s), and per-tool engines.
- **Router tests** exercise every `/api/v1/tools/{tool}/tasks` admission path including multipart parsing, per-file limits, sanitizer refusals, orphan-input cleanup on failure, and the merge per-file password contract (`password_<i>`, distinct `error.wrongPassword` envelope, never persisted).
- **Object-seam tests** (`test_*_objects_seam.py`) lock the `TransitionPayload.objects` pairing on terminal transitions so output keys are always recorded.
- **Integration tests** (opt-in, `REDIS_URL=...`) run against real Redis on db 15; they are skipped by default. Real-R2 integration is opt-in the same way.
- **Security acceptance tests** (`test_security_acceptance.py`) assert fail-closed behaviour against hostile fixtures in `backend/tests/fixtures/hostile/`.

### Frontend

- **Lib tests** cover i18n, tool catalog, task polling, state cards, zip (fflate), password helpers (`validatePassword`), encrypted-PDF detection (`isEncryptedPdf`, first 4 KiB scan), merge password-field building (per-index fields only for encrypted files, whole-submit validation), analytics schema + redaction + leakage, and ad placement config.
- **Component tests** cover Dropzone, the five state cards, PasswordInput, ContactForm (honeypot, client rate limit, Turnstile), ResultProblemReport, PrivacyAnalytics (DNT/GPC gating of both Vercel components), and ad behaviour (reserved slot, one unit per page, house-promo fallback, no provider script under DNT/GPC).
- **Page tests** cover the tool pages (idle → uploading → queued → processing → done/error states), supporting pages, shell layout, locale routing, and sitemap/robots metadata.
- **E2E specs** in `frontend/e2e/` cover locale routing, a11y shell (SkipLink, focus, overflow, rich UI), catalog routes, support routes, not-found/contrast/favicon, all tool flows, and ad behaviour. The a11y spec aborts `**/highperformanceformat.com/**` so focus/overflow assertions never depend on non-deterministic third-party ad responses; ad behaviour itself is asserted by `ad-behavior.spec.ts`.

## Privacy and security testing

- `leakage.test.ts` (26 tests) proves the analytics pipeline never emits prohibited fields (filenames, passwords, contents, signed URLs).
- The merge password path is asserted end-to-end: passwords are consumed at the sanitizer stage, never written to `TaskRecord`, logs, error envelopes, or analytics.
- The sanitizer refuses encrypted input without the correct password (fail-closed), and password/corrupt/unsupported are distinct refusal reasons with distinct public error keys.
- gitleaks scans full repository history in CI; Adsterra zone keys are allowlisted because they are public client-side constants by design.

## Gate commands (must exit 0)

Backend (from `backend/`):

```bash
python -m pytest -q
python -m pytest --cov=app --cov-fail-under=80
ruff check .
ruff format --check .
python -m mypy app tests --strict --no-incremental
```

Frontend (from `frontend/`):

```bash
npm ci
npm run test:coverage
npm run lint
npm run format:check
npm run typecheck
npm run build
npm run test:e2e        # Playwright (builds + serves locally)
```

Repo guard (root):

```bash
bash scripts/check-ci.sh
```

## Coverage baseline (measured at the P6 completion release)

- Backend: 89.38% total statements (gate 80%); 1360 passed, 44 opt-in skips.
- Frontend: statements 91.27%, branches 86.15%, functions 91.71%, lines 93.10% (thresholds all 80).
- Frontend test count: 780 tests across 52 files; E2E suite passes 244 assertions across the Playwright projects.
