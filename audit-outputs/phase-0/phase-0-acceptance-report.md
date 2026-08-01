# Phase 0 Acceptance Report

Date: 2026-08-01
Repository: `fazulfi/mypapyr` (public)
Default branch: `main` at `06aec2e58e1f178a363693482839457698931cf4`
Pull request: <https://github.com/fazulfi/mypapyr/pull/1> (MERGED, rebase)
Green CI run: <https://github.com/fazulfi/mypapyr/actions/runs/30677125921>

## 1. Verdict

Phase 0 is complete and accepted. Every task in the approved Phase 0 scope was
implemented, independently reviewed, remediated where reviews found defects, and
verified with reproducible commands. The repository is public, continuous
integration is green, and no deployment or production mutation was performed.

## 2. Scope delivered

| Task | Deliverable | Status |
| --- | --- | --- |
| PR-01 | Repository foundation, hardened `.gitignore`, `git init -b main`, feature branch | Complete |
| PR-02 | `docs/canonical-docs-baseline.md`, fixed `scripts/check-docs-migration.sh` | Complete |
| PR-03 | `docs/resolution-register.md` verified R-01..R-28, R-02 and R-26 evidence | Complete |
| FD-01 | `frontend/` Next.js workspace, strict TypeScript, Vitest, ESLint, Prettier | Complete |
| FD-02 | `backend/` FastAPI workspace, `/health`, pytest, Ruff | Complete |
| FD-03 | `deploy/` compose and nginx skeleton, non-secret env template, runbook outline | Complete |
| FD-04 | `.github/workflows/ci.yml` core gate without deployment, `scripts/check-ci.sh` | Complete |
| FD-05 | `README.md`, `CONTRIBUTING.md`, `docs/plan/index.md` | Complete |
| P0 docs | `.env.example`, `SECURITY.md`, `docs/architecture.md`, `docs/deployment-boundary.md`, `docs/integration-inventory.md` | Complete |

## 3. Verification evidence

All commands were executed locally and produced the results below.

| Gate | Command | Result |
| --- | --- | --- |
| Frontend format | `npm run format:check` | All matched files use Prettier code style, exit 0 |
| Frontend lint | `npm run lint` | exit 0, no diagnostics |
| Frontend test | `npm run test` | 1 file, 1 test passed, exit 0 |
| Frontend build | `npm run build` | production build succeeded, exit 0 |
| Backend lint | `ruff check .` | All checks passed, exit 0 |
| Backend format | `ruff format --check .` | 3 files already formatted, exit 0 |
| Backend test and coverage | `pytest tests/ -q --cov=app --cov-fail-under=80` | 1 passed, total coverage 100.00 percent against the 80 percent floor, exit 0 |
| CI guard | `bash scripts/check-ci.sh` | `check-ci: PASS`, exit 0 |
| Governed docs guard | `bash scripts/check-docs-migration.sh` | `check-docs-migration: PASS`, exit 0 |
| Secret scan, full history | `gitleaks detect --source . --config .gitleaks.toml --no-banner --redact` | 20 commits scanned, no leaks found, exit 0 |

CI run 30677125921 passed all seven jobs: Frontend lint and format, Frontend
Vitest and coverage, Frontend production build, Backend Ruff, Backend pytest and
coverage threshold, Security Trivy filesystem and config scan, Security gitleaks
secret scan.

## 4. Independent review outcomes

| Review | Record | Verdict |
| --- | --- | --- |
| Frontend | `review-frontend.md` | Accept |
| Backend | `review-backend.md` | Accept |
| Documentation | `review-docs.md` | Accept with non-blocking findings |
| CI and security | `review-ci-security.md` | Accept after remediation of finding CI-F1 |
| Public safety | `review-public-safety.md` | Redact before public, remediated in full |

Material findings and their remediation:

1. CI-F1. A pinned action SHA carried a version comment that did not match the
   commit that tag actually resolves to. The pin was replaced with the verified
   commit for the claimed version, and the guard script was re-run.
2. Public safety. Operator, host, and messaging identifiers appeared in
   documentation and audit evidence. A redaction pass replaced them with
   placeholders before the first commit, so no sensitive literal ever entered
   Git history. Evidence: `public-safety-remediation.md`.
3. Workflow permissions. Empty per-job permission maps prevented checkout on a
   private repository. Each job now receives `contents: read`, which is the
   minimum required and no more.
4. Secret scanner false positives. Two findings matched Indonesian interface
   copy, not credentials. A narrow allowlist scoped to both the exact line and
   the two documented files was added, with the reasoning recorded in
   `ci-gitleaks-allowlist.md`. The scanner remains blocking and still scans the
   full history with redaction enabled.

## 5. Repository state

| Property | Value |
| --- | --- |
| Visibility | public |
| Default branch | `main` |
| Merge strategy used | rebase, so the 19 atomic commits remain individually reviewable |
| Branch protection | pull request required, 7 required status checks, strict up-to-date checks, linear history required, conversation resolution required |
| Force pushes | disabled |
| Branch deletion | disabled |
| Administrator enforcement | disabled deliberately, so the owner retains an override and cannot be locked out |
| Owner administrative access | confirmed present after protection was applied |

## 6. Anonymous access validation

Unauthenticated requests, with no credentials supplied:

| Target | Result |
| --- | --- |
| Repository web page | HTTP 200 |
| Repository API endpoint | HTTP 200 |
| `README.md` on `main` via raw endpoint | HTTP 200 |

## 7. Safety confirmations

- No continuous deployment exists. The workflow contains no deployment job, and
  the guard script fails the build if one is introduced.
- No deployment was performed. No production service, container, database,
  storage bucket, DNS record, or edge configuration was created, changed, or
  removed.
- Third-party integrations were validated read-only. The virtual private server
  was inspected with read-only commands only; nothing on it was modified.
- Credentials remain outside the repository. The local credential file is
  ignored by Git, was never staged, and its values were never printed.
- The legacy reference clone was never modified. It remained clean with an
  unchanged head commit `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` before and
  after every wave of work.
- The legacy public repository was never contacted or altered. The new remote
  points only at the rebuild repository.

## 8. Out of scope for Phase 0

The five document tools, the complete product interface, production data
migrations, deployment of the stack, live domain and edge configuration changes,
live advertising placements, production backup jobs, monitoring rollout, and
account, billing, or administration surfaces were all deliberately excluded and
were not built.

## 9. Known limitations recorded honestly

- The container runtime was unavailable locally, so the container based security
  scan and the secret scan were first executed in continuous integration rather
  than on the workstation. Both now pass there.
- The end to end browser test script exists but was not executed, because the
  browser binaries are not installed and installing them was out of scope.
- A markdown lint runner is not configured at the repository root, so markdown
  quality was verified structurally instead. This is stated rather than claimed
  as a passing tool run.
- The frontend workspace exposes one additional script beyond the original
  eight, added to serve the coverage gate. It is a superset, not a deviation
  from the required set.
- Two governed records were sanitised to remove sensitive literals. Only the
  literals changed. No decision identifier, ordering, or normative statement was
  altered.

## 10. Outstanding owner decisions

These items are recorded for the owner and were intentionally not decided
unilaterally.

1. Whether the master plan text should be updated to reflect its own approval
   and the resolved register rows, which is a governed record edit.
2. Whether the audit evidence directory should remain published in full, be
   trimmed, or be moved, now that the repository is public.
3. The dependency licence allow list, which requires legal input.
4. Rotation timing for the credentials held in the local ignored file.
