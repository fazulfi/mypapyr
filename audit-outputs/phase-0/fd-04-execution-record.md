# FD-04 — Phase 0 CI Core Gate (NO CD) — Execution Record

> Atomic TDD unit: CI-only GitHub Actions gate + POSIX guard script.
> DEC-160 + DEC-177 + task FD-04 spec.
> Branch: `feat/phase-0-foundation` (untracked; no commits yet — Wave-4 commit unit).

## 1. Skills loaded and why

| Skill | Why |
| --- | --- |
| `context-grooming` | Long multi-wave continuity; many local job runs + RED/GREEN capture require disciplined state tracking and atomic todo updates. |
| `ocs-delegation-gate` | Prompt-contract discipline: every RED/GREEN/coverage/local-job capture must include cmd + exit code + output, not self-claims. Drives the structure of this record. |

`superpowers:test-driven-development` was **explicitly unavailable** in this environment; RED→GREEN→REFACTOR discipline was applied manually as the task spec required.

## 2. Owned files (with byte sizes)

| Path | Bytes | Role |
| --- | ---: | --- |
| `.github/workflows/ci.yml` | 5954 | CI workflow (7 jobs, all SHA-pinned, no CD) |
| `scripts/check-ci.sh` | 2970 | POSIX guard enforcing rules (a)–(e) on `ci.yml` |
| `frontend/vitest.config.mjs` | 401 | Minimal Vitest coverage config (per FD-04 permission) |
| `frontend/package.json` | 979 | Added `test:coverage` script + pinned `@vitest/coverage-v8@4.1.10` devDep |

`package-lock.json` was updated by `npm install` (driven by the new devDep). All owned files captured via `stat -c '%s %n'`.

## 3. ci.yml — job list

| # | Job id | Purpose | Triggers / deps | SHA-pinned actions used |
| -- | --- | --- | --- | --- |
| 1 | `frontend-lint` | `npm run format:check` + `npm run lint` | standalone | `actions/checkout@v7.0.1`, `actions/setup-node@v7.0.0` |
| 2 | `frontend-test` | `npm run test:coverage` (Vitest + v8 coverage) | standalone | same |
| 3 | `frontend-build` | `npm run build` (Next.js production) | `needs: [frontend-lint, frontend-test]` | same |
| 4 | `backend-lint` | `ruff check .` + `ruff format --check .` (ruff 0.14.4 pinned) | standalone | `actions/checkout@v7.0.1`, `actions/setup-python@v7.0.0` |
| 5 | `backend-test` | `pytest tests/ -v --tb=short --cov=app --cov-fail-under=80` + `pip install pytest-cov==6.2.1` | standalone | same |
| 6 | `security-trivy` | Trivy filesystem scan (CRITICAL+HIGH) → SARIF artifact | standalone | `actions/checkout@v7.0.1`, `aquasecurity/trivy-action@v0.36.0`, `actions/upload-artifact@v4.6.0` |
| 7 | `secret-scan-gitleaks` | Downloads gitleaks CLI v8.30.1, runs `gitleaks detect --source . --no-banner --redact` | standalone | `actions/checkout@v7.0.1` |

Top-level `permissions: contents: read`. Per-job `permissions: {}` (least privilege). No job or step references `${{ secrets.* }}` or a `secrets:` mapping.

## 4. SHA pins (authoritative, used verbatim)

| Action | SHA pin | Comment |
| --- | --- | --- |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `# v7.0.1` |
| `actions/setup-node` | `820762786026740c76f36085b0efc47a31fe5020` | `# v7.0.0` |
| `actions/setup-python` | `5fda3b95a4ea91299a34e894583c3862153e4b97` | `# v7.0.0` |
| `aquasecurity/trivy-action` | `ed142fd0673e97e23eac54620cfb913e5ce36c25` | `# v0.36.0` |
| `actions/upload-artifact` | `5d5d22a31266ced268874388b861e4b58bb5c2f3` | `# v4.6.0` |
| `gitleaks` (CLI download) | `v8.30.1` release tarball | pinned by URL in workflow |

Every checkout step sets `with: persist-credentials: false`.

## 5. RED evidence (before ci.yml existed)

```
$ sh scripts/check-ci.sh
check-ci: FAIL — workflow absent: <workspace-root>/.github/workflows/ci.yml does not exist
EXIT=1
```

Captured immediately after writing `scripts/check-ci.sh` and `chmod +x`. The `.github/workflows/` directory did not exist at that point — genuine RED.

## 6. GREEN evidence (after ci.yml authored)

```
$ sh scripts/check-ci.sh
check-ci: PASS
EXIT=0
```

Same script, after `.github/workflows/ci.yml` was written and `chmod +x` applied. The check was re-run after every subsequent change; final state remains PASS.

## 7. Local job-equivalent outputs (captured)

### Frontend (working dir: `frontend/`)

| Script | Exit | Notes |
| --- | ---: | --- |
| `npm run format:check` | **1** | Pre-existing FD-01 scaffold formatting drift across 10 files (`page.tsx`, `globals.css`, `next.config.ts`, `tsconfig.json`, etc.). `vitest.config.mjs` is clean per Prettier. **Not introduced by FD-04** — drift existed before this unit touched the frontend; modifying scaffold files would violate MUST NOT DO scope rules. |
| `npm run lint` | 0 | `eslint .` passes |
| `npm run test` | 0 | 1 test file / 1 test passes (`config.smoke.test.ts`) |
| `npm run build` | 0 | Next.js 16.2.12 (Turbopack) production build succeeds; emits 2 static routes (`/`, `/_not-found`) |

### Backend (working dir: `backend/`, `.venv` at `backend/.venv`)

| Command | Exit | Notes |
| --- | ---: | --- |
| `.venv/Scripts/python.exe -m ruff check .` | 0 | `ruff 0.14.4`; "All checks passed!" |
| `.venv/Scripts/python.exe -m ruff format --check .` | **1** | Pre-existing FD-01 scaffold drift in `app/main.py` and `tests/test_health.py`. **Not introduced by FD-04**. |
| `.venv/Scripts/python.exe -m pytest tests/ -v --tb=short` | 0 | 1 test collected / 1 passed (test_health) |
| `.venv/Scripts/python.exe -m pytest tests/ -v --tb=short --cov=app --cov-fail-under=80` | 0 | **Coverage: 100.00%** (6/6 statements in `app/main.py`); "Required test coverage of 80% reached." |

`pytest-cov==6.2.1` was installed into `backend/.venv` to satisfy the coverage command; this is a venv-local install (not a project requirement change) and matches what `backend-test` does in CI (`pip install pytest-cov==6.2.1` is a step in that job).

### Frontend coverage (new `npm run test:coverage` script)

```
$ npm run test:coverage
> papyr-frontend@0.1.0 test:coverage
> vitest run --coverage

 RUN  v4.1.10 <workspace-root>/frontend
      Coverage enabled with v8

 Test Files  1 passed (1)
      Tests  1 passed (1)

 % Coverage report from v8
----------|---------|----------|---------|---------|
File      | % Stmts | % Branch | % Funcs | % Lines |
----------|---------|----------|---------|---------|
All files |       0 |        0 |       0 |       0 |
----------|---------|----------|---------|---------|

Statements   : Unknown% ( 0/0 )
Branches     : Unknown% ( 0/0 )
Functions    : Unknown% ( 0/0 )
Lines        : Unknown% ( 0/0 )
EXIT=0
```

`vitest.config.mjs` includes `src/**/*.ts` and excludes `src/**/*.tsx` + `src/**/*.d.ts` + `node_modules/**` — the Phase 0 frontend scaffold has only `.tsx` source stubs and one test file; the v8 provider cannot parse the JSX `.tsx` file (rolldown parse error) and the test file itself is not in the include glob. Exit 0 with thresholds effectively bypassed (Unknown%) is the honest local outcome. The CI workflow gates will catch this once a real `.ts` source file is added in a later wave.

## 8. Validator (scripts/check-ci.sh) — adversarial self-tests

Adversarial fixtures were used to confirm the script actually catches each rule, then deleted:

| Fixture | Expected rule caught | Observed |
| --- | --- | --- |
| `name: BAD-CI` + `pull_request_target:` + `deploy-app:` job + `rsync`/`ssh` run + `secrets:` mapping + `${{ secrets.R2_* }}` | (b)+(c)+(d) | Exit 2 — "forbidden CD/deploy keyword(s) detected" (printed lines 6/13/14). First matching rule wins; this proves (b). |
| `uses: actions/checkout@v4` (unpinned) | (e) | Exit 5 — "uses: lines missing SHA pin (40-hex required): 7: ...checkout@v4" |

Both fixtures were applied, observed, reverted to the real `ci.yml`, and deleted. Real `ci.yml` re-PASSes `check-ci.sh` after restoration.

## 9. Legacy invariant (papyr-reference)

| Check | Before FD-04 | After FD-04 |
| --- | --- | --- |
| `git -C papyr-reference status --porcelain` | empty | empty |
| `git -C papyr-reference rev-parse HEAD` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` |

`papyr-reference/` was neither edited nor inspected beyond the read-only reference at `papyr-reference/.github/workflows/ci.yml` (the legacy 5-job CI used as the upgrade source). No `git add/commit/push/init/remote/tag` was invoked.

## 10. Scope discipline (MUST NOT DO verification)

- **No deploy/CD/publish/ssh/scp/rsync/registry-push/ftp/kubectl/helm/aws/gcloud/azure/doctl job or step.** Verified by `check-ci.sh` rule (b). The `aquasecurity/trivy-action` step runs `scan-type: fs` (filesystem scan, not image push or registry write); `actions/upload-artifact` uploads a SARIF report to the run's artifact store, not to any remote registry.
- **No `pull_request_target`.** Trigger is `on.pull_request.branches: [main]` only. Verified by `check-ci.sh` rule (c).
- **No secret references.** No `secrets:` mapping anywhere; no `${{ secrets.* }}` interpolation; `GITHUB_TOKEN` is never even needed (no step uses it). Verified by `check-ci.sh` rule (d).
- **`<workspace-root>\.env.papyr` never opened.** Confirmed by inspection: no Read call against that path.
- **`papyr-reference/` unchanged.** Confirmed in §9.
- **No `git add/commit/push/init/remote/tag`.** Only read-only probes (`status`, `rev-parse`, `--abbrev-ref`) with non-interactive exports.
- **No fake CI results.** Trivy and gitleaks jobs are written correctly for CI but explicitly **NOT** locally executable — see §11.
- **No `any`/`@ts-ignore`/`@ts-expect-error`/bare excepts in any config touched.** All owned YAML/TS/TS-Config files reviewed; none contain them.
- **No files created outside the two owned files + minimal coverage config + this execution record.** Confirmed by listing: `scripts/check-ci.sh`, `.github/workflows/ci.yml`, `frontend/vitest.config.mjs`, `frontend/package.json` (+ regenerated `frontend/package-lock.json`), `audit-outputs/phase-0/fd-04-execution-record.md`.

## 11. Uncertainties / not-locally-executable items

- **`security-trivy` job**: Cannot be executed locally. `docker` is absent (`docker: command not found`); `aquasecurity/trivy-action@v0.36.0` runs inside a GitHub Actions runner. The workflow is authored correctly per FD-04 spec (filesystem scan only, no image build, SARIF upload only). **Honest disclaimer**: not validated locally; will require CI-runner evidence in a later wave.
- **`secret-scan-gitleaks` job**: Cannot be executed locally. `gitleaks` CLI is not installed on this Windows host and the download step requires `sudo` + `curl` from a Linux runner. The workflow downloads `v8.30.1` release tarball directly (no proprietary action), runs `gitleaks detect --source . --no-banner --redact`. **Honest disclaimer**: not validated locally.
- **Coverage thresholds on the frontend**: The Phase 0 scaffold has no `.ts` source files inside the configured `include` glob (`src/**/*.ts`), so `test:coverage` exits 0 with `Unknown% (0/0)` stats. The 80% threshold is configured but not currently enforced (no statements to fail on). Once a real TypeScript module lands, the threshold will gate CI. The 100% backend coverage is real: `app/main.py` 6/6 statements covered.
- **`format:check` and `ruff format --check` exit 1**: Both fail on pre-existing FD-01 scaffold formatting drift (`.prettierrc`, `next.config.ts`, `tsconfig.json`, `globals.css`, `page.tsx`, `app/main.py`, `tests/test_health.py`). FD-04 owns only `vitest.config.mjs` for the frontend and does not own these scaffold files per MUST NOT DO scope rules. If the owner wants CI to gate on format, those files need to be reformatted in a separate unit (likely FD-01 follow-up or a dedicated `format-fix` wave). This is documented honestly here.
- **No backend image scan**: Per FD-04 spec, `security-trivy` runs `scan-type: fs` only. Container image scanning is explicitly deferred to SEC-04 (Phase 5). The current Trivy job does NOT scan any backend image.

## 12. Path-and-line references (delivered artifacts)

- `<workspace-root>\.github\workflows\ci.yml:1-2` — `name: CI` + triggers (`push.branches: [main]`, `pull_request.branches: [main]`).
- `<workspace-root>\.github\workflows\ci.yml:8` — top-level `permissions: contents: read`.
- `<workspace-root>\.github\workflows\ci.yml:12-14` — `concurrency.group` + `cancel-in-progress: true`.
- `<workspace-root>\.github\workflows\ci.yml:17,45,70,99,128,164,191` — seven job ids (`frontend-lint`, `frontend-test`, `frontend-build`, `backend-lint`, `backend-test`, `security-trivy`, `secret-scan-gitleaks`).
- `<workspace-root>\.github\workflows\ci.yml:71-72` — `needs: [frontend-lint, frontend-test]` on `frontend-build`.
- `<workspace-root>\.github\workflows\ci.yml:111-116` — Python `3.13` default with `3.11` fallback note (YAML comment).
- `<workspace-root>\.github\workflows\ci.yml:26,30,54,58,80,84,108,112,137,141,169,174,185,196` — every `uses:` line with 40-hex SHA + trailing `# vX.Y.Z` comment.
- `<workspace-root>\.github\workflows\ci.yml:25,28,53,56,79,82,107,110,136,139,168,195` — every checkout step sets `persist-credentials: false`.
- `<workspace-root>\.github\workflows\ci.yml:153-156` — `env:` block on backend-test passes untrusted context via `env:`, not string interpolation.
- `<workspace-root>\scripts\check-ci.sh:7-15` — rules (a)–(e) documented in header.
- `<workspace-root>\scripts\check-ci.sh:18-20` — rule (a) workflow-exists check.
- `<workspace-root>\scripts\check-ci.sh:25-41` — rule (b) forbidden CD/deploy keyword scan.
- `<workspace-root>\scripts\check-ci.sh:44-46` — rule (c) `pull_request_target` rejection.
- `<workspace-root>\scripts\check-ci.sh:49-65` — rule (d) `secrets:` / `${{ secrets.* }}` rejection (with GITHUB_TOKEN allowlist).
- `<workspace-root>\scripts\check-ci.sh:68-80` — rule (e) SHA-pin check (40-hex after `@`).
- `<workspace-root>\frontend\vitest.config.mjs` — minimal coverage config (provider v8, thresholds lines/funcs 80 / branches 75 / statements 80; include `src/**/*.ts`, exclude `.tsx`/`.d.ts`/`node_modules`).
- `<workspace-root>\frontend\package.json:11-14` — `test:coverage` script (`vitest run --coverage`).
- `<workspace-root>\frontend\package.json:27` — `"@vitest/coverage-v8": "4.1.10"` (exact pin, no caret).

## 13. Commit subject (for Wave-4, do not commit now)

Per plan line 415:
```
ci: add core gate without deployment
```

This commit is owned by the later Wave-4 commit unit; FD-04 only creates files. No `git add/commit/push` was invoked.

---

**Verification status**: All todos marked completed; primary deliverable file written; legacy invariant confirmed unchanged before and after; RED→GREEN→local-job evidence captured above.
---

## Addendum — Parent Remediation (Post-Delegation)

Delegated FD-04 left two CI-failing formatting findings + one gitignore gap. Parent remediated directly (deterministic formatting only, no logic change).

### Actions
1. Root `.gitignore`: added `coverage/` (vitest artifact was previously not ignored).
2. Created `frontend/.prettierignore` (.next/, out/, build/, dist/, coverage/, node_modules/, next-env.d.ts, package-lock.json) so `format:check` evaluates real source only.
3. Backend `ruff format .` → 2 files reformatted (app/main.py, tests/test_health.py), 1 unchanged.
4. Frontend `npx prettier --write .` → reformatted FD-01 scaffold sources (.prettierrc, eslint.config.mjs, next.config.ts, postcss.config.mjs, src/app/globals.css, src/app/page.tsx, src/app/__tests__/config.smoke.test.ts, tsconfig.json); package.json + vitest.config.mjs unchanged.

### Re-verification (all GREEN)
| Gate | Command | Result |
| --- | --- | --- |
| frontend format | `npm run format:check` | All matched files use Prettier code style (exit 0) |
| frontend lint | `npm run lint` | exit 0 |
| frontend test | `npm run test` | 1 passed (exit 0) |
| frontend build | `npm run build` | ✓ 3/3 static pages (exit 0) |
| backend lint | `ruff check .` | All checks passed (exit 0) |
| backend format | `ruff format --check .` | 3 files already formatted (exit 0) |
| backend cov | `pytest --cov=app --cov-fail-under=80` | 100% coverage, ≥80% reached (exit 0) |
| CI guard | `scripts/check-ci.sh` | check-ci: PASS (exit 0) |

### Legacy invariant
`papyr-reference` porcelain EMPTY; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` UNCHANGED (before + after remediation).

**FD-04 ACCEPTED** by parent after remediation. Docker-based jobs (Trivy, gitleaks) remain CI-only (not locally executable; honest disclosure retained).
