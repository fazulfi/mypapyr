# Contributing to Papyr

Thank you for your interest in Papyr. This document is the contribution convention for the rebuild repository at the workspace root. It applies to every task — feature, fix, documentation, test, refactor, security, CI, and chore.

The master implementation plan is the source of truth for what is being built and in what order. See [`docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`](docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md). The phase planning entry point is [`docs/plan/index.md`](docs/plan/index.md).

## Branch naming

Use one branch per task or feature. Branch names are short, lower-case, and slash-separated.

| Prefix | Use for |
| --- | --- |
| `feat/<scope>` | New user-facing capability. |
| `fix/<scope>` | Bug fix. |
| `docs/<scope>` | Documentation-only change. |
| `phase-0/<task>` | Phase 0 monorepo, tooling, CI, and convention tasks. |
| `chore/<scope>` | Maintenance that is not a fix or a feature (renames, dependency housekeeping). |
| `refactor/<scope>` | Code restructure with no behavior change. |
| `test/<scope>` | Test-only changes that add or repair coverage. |
| `security/<scope>` | Security hardening or vulnerability remediation. |
| `ci/<scope>` | CI workflow changes only. |

`<scope>` is a short, kebab-case token that names the area of the codebase affected (for example `compress-pdf`, `nginx-rate-limit`, `frontend-format`).

## Commit messages

Use the following prefixes in the commit subject line. The subject is followed by a colon, a space, and a concise imperative summary. Body and footer are optional and used for context and references.

| Prefix | Use for |
| --- | --- |
| `feat` | New user-facing capability. |
| `fix` | Bug fix. |
| `docs` | Documentation only. |
| `chore` | Maintenance, dependency housekeeping, non-functional edits. |
| `test` | Test-only changes. |
| `ci` | CI workflow changes only. |
| `refactor` | Code restructure with no behavior change. |
| `security` | Security hardening or vulnerability remediation. |

Examples:

```text
feat: add JPG-to-PDF tool landing page
fix: enforce 80 MiB upload limit on compress endpoint
docs: add contribution and planning conventions
ci: pin trivy-action to commit SHA
```

## Test-driven development (TDD) requirement

Every behavioral change ships with tests. The discipline is RED then GREEN then REFACTOR, applied manually in this project:

1. **RED** — write a failing test (or extend an existing one) that captures the desired behavior. Run the relevant test command and confirm the failure.
2. **GREEN** — implement the minimum code needed to make that test pass. Keep the change small and focused on the test that drove it.
3. **REFACTOR** — clean up the implementation and tests while keeping them green. Do not introduce new behavior in this step.

Implementation rules:

- No production code without a paired test in the same change.
- Minimal implementation: only what is needed to turn RED into GREEN. Avoid speculative features.
- Tests live next to the code they cover (frontend: `frontend/tests/`; backend: `backend/tests/`).
- Coverage floor is enforced in CI at 80% for both frontend and backend. Local changes are expected to keep or raise coverage; do not disable tests or coverage gates to make CI pass.

## Phase-plan expansion rule

Each phase in the master implementation plan MAY be expanded into its own plan file under `docs/superpowers/plans/`. An expanded plan file:

- Follows the master plan's template and gates.
- Cross-references the master plan by relative path and names the phase it expands.
- Inherits the master's stop conditions and adds phase-specific ones where the owner has approved them.
- Is appended to the list in `docs/plan/index.md` when created.

Phase-plan files are governed records. They are not edited casually; any change is logged in `papyr-rebuild-decisions.md` with a stable decision ID and recorded in the owner resolution register where it affects a stop condition.

## CI gates

CI is defined in `.github/workflows/ci.yml` and runs on every push and pull request:

- Frontend: Prettier format check, ESLint, Vitest with coverage, Next.js production build.
- Backend: Ruff lint and format check, Pytest with a coverage floor of 80%.
- Security: Trivy filesystem scan and gitleaks secret scan.

CI is **continuous integration only** — it does not deploy. No commit, push, or remote operation is initiated from CI.

## What not to do

- Do not modify anything under `papyr-reference/`. The legacy clone is read-only.
- Do not commit secrets. Use `.env.production.example` for placeholders and document required variables by name only.
- Do not claim legal compliance, certification, guaranteed malware removal, or privacy or legal sufficiency in code, comments, docs, or copy. The "Limitations" section of `README.md` applies to all contributions.
- Do not introduce benchmark programs. The benchmark program was explicitly rejected (DEC-066).
- Do not bypass CI gates, disable tests, or suppress coverage thresholds.

## Reporting issues

Open an issue in this repository with a clear description, reproduction steps where relevant, and the affected scope. Security-sensitive reports should not be filed as public issues; follow the disclosure process described in the security documentation when one is published.