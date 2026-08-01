# Phase 0 Execution DAG: PR-01..PR-03 and FD-01..FD-05

| Field | Value |
|---|---|
| Document ID | PPR-P0-DAG-001 |
| Title | Verified Phase 0 execution DAG derived from the four Phase 0 audit artifacts |
| Date | 2026-08-01 |
| Author role | Sisyphus subagent (execution-plan delegation; the only file written is this deliverable) |
| Status | Complete; primary deliverable is this file; a chat-only summary is insufficient |
| Sources | `context-and-scope-audit.md`, `foundation-architecture-audit.md`, `repository-safety-audit.md`, `current-tooling-research.md`, all under `<workspace-root>\audit-outputs\phase-0\` |
| Governing rules | `AGENTS.md` (every subagent persists output to a file); `context-grooming`; `ocs-delegation-gate`; `ocs-markdown-autofix` |
| Delegation constraints | Read-only except this exact output path; no network, no installs, no git writes, no VPS access; `papyr-reference\` untouched; no secret values printed |
| Precedence | Decision log > specs > plan > audits > legacy clone (decision log DEC-202 approves the plan) |

## 1. Skills loaded and why

- **context-grooming**: this DAG is one unit inside a multi-workstream rebuild. The skill requires atomic task decomposition, a single source of truth for plan and decision state, and concrete evidence before a unit is marked complete. Each wave below carries its own RED/GREEN commands and acceptance check so an executor can verify without re-deriving state.
- **ocs-delegation-gate**: every execution task that follows this DAG will be delegated to specialized sub-agents. The skill mandates a strict domain to skill mapping and explicit verification criteria in each delegation prompt. The DAG therefore records per-task ownership, commands, and acceptance so a delegation prompt can carry `load_skills` and evidence requirements without re-reading all audits.
- **ocs-markdown-autofix**: this is a markdown deliverable under `audit-outputs\`, which is a governed discovery space. The skill requires clean markdown structure (ATX headings, well-formed tables, list continuity, no em/en dashes). Root lint tooling is unavailable (no `bun run lint:md` scripts exist; verified by context-and-scope-audit.md Section 10 item 14), so the manual structural pass was applied here.

## 2. Source audit paths (cited throughout as short names)

| Short name | Full path |
|---|---|
| CSA | `<workspace-root>\audit-outputs\phase-0\context-and-scope-audit.md` |
| FAA | `<workspace-root>\audit-outputs\phase-0\foundation-architecture-audit.md` |
| RSA | `<workspace-root>\audit-outputs\phase-0\repository-safety-audit.md` |
| CTR | `<workspace-root>\audit-outputs\phase-0\current-tooling-research.md` |

## 3. Execution waves (parallel DAG)

Plan-faithful ordering: PR-01..PR-03 before FD-01..FD-05; within Phase 1, FD-01..FD-03 before FD-04, FD-01..FD-04 before FD-05 (CSA Section 4). Safety gates interleave because no git operation may happen before the pre-init gates pass (RSA Section 8).

```
Wave 0  Safety pre-init        G1 (owner redaction sign-off) -> G2 (.gitignore) -> G3 (L1 rescan)
                                -> G4 (gitleaks) -> G5 (legacy clean) -> G6 (no .env leaks)
Wave 1  PR-01                  verify skeleton; git init (owner G-1); branch; first commit (+G8-G12); commit #1
Wave 2  PARALLEL               PR-02 (commit #2)   |   PR-03 (commit #3)
        REVIEW LOOP 2          Phase 0 gate exit, owner review (plan line 302; incl. PR-03 step 4)
Wave 3  PARALLEL               FD-01 (commit #4)   |   FD-02 (commit #5)   |   FD-03 (commit #6)
        REVIEW LOOP 3          commit-boundary review at each FD boundary commit (plan s2 rule 5, line 63)
Wave 4  FD-04                  core gate + gitleaks CI job + coverage wiring if owner decides (commit #7)
Wave 5  FD-05                  conventions (commit #8)
        REVIEW LOOP 4          FD-05 step 3 conventions review with the execution agent
        REVIEW LOOP 5          Phase 1 exit gate, owner review (plan line 355)
Wave 6  Remote, owner-gated    G14-G16 -> push (G-1) -> P1-P6 later (public flip is owner-only, P6)
```

Dependency edges (CSA Section 6; FAA Section 8):

```
PR-01 (DEC-202, R-01, R-02)
  +-> PR-02  (consumes PR-01, DEC-198)
  +-> PR-03  (consumes R-01..R-28 dispositions, status recording only)
  +-> FD-01  (consumes PR-01)         -> later SH, TL
  +-> FD-02  (consumes PR-01)         -> later BE
  +-> FD-03  (consumes PR-01)         -> later BE, SEC, OP
FD-01 + FD-02 + FD-03 + R-02 (resolved) -> FD-04 -> all later phases
FD-01..FD-04 -> FD-05 -> all later phases
```

No R-item outside R-01/R-02/R-26/R-27/R-28 gates this block. R-15 gates SH-01 (Phase 2); R-03 gates BE-08, R-07/R-08 gate BE-05, R-09 gates BE-04 (Phase 3). None blocks Phase 1 (CSA Section 6; FAA Section 8).

## 4. Wave 0: safety pre-init gates (before any git operation)

Owner sign-off is required at G1. Redaction targets are the 5 files from RSA Section 4.2/4.3: `papyr-rebuild-decisions.md` lines 776/780, `audit-outputs\research\track-b\_evidence-decisions.md` line 80, `audit-outputs\research\track-c\c1-queue-workers-redis.md` line 87, `audit-outputs\research\track-c\c5-observability-status-telegram.md` line 65, `audit-outputs\research\source-and-decision-index.md` line 293. Replace the legacy VPS IPv4 with documentation range `203.0.113.x` or the token `<vps-ip>`; replace the Telegram ops handle and chat ID with `<chat-id>` / `@<ops-bot>` (RSA Section 4.2/4.3). Contact emails in the track-d files are low risk and likely intended public; confirm at review (RSA Section 4.4).

| Gate | Check | Pass condition |
|---|---|---|
| G1 | Owner signs off redactions; edits applied | diff shows only redactions (RSA Section 8) |
| G2 | Extend `.gitignore` with RSA Section 3 gap rules | new rules only; includes C5 negation and `/.env.papyr`, `gitleaks-report.json` |
| G3 | Re-run L1 scanner | 0 matches in the redacted families (RSA Section 8) |
| G4 | `gitleaks dir <workspace-root>` | 0 findings |
| G5 | `git -C papyr-reference status --porcelain` | empty output |
| G6 | `find . -maxdepth 1 -name ".env*"` | only `.env.papyr` |
| G7 | `git init -b main` | repo created; runs inside PR-01 after owner G-1 |

G1 is REVIEW LOOP 1. G2 also fixes conflict C5 (negation for `deploy/.env.production.example`; see Section 8). Hard stop: if G3 or G4 finds a match, stop and escalate; do not init.

## 5. Task records with TDD RED/GREEN, ownership, commits, acceptance

File ownership per FAA Section 6. Commands run from the workspace root unless a task says otherwise.

### PR-01: Repository creation and branch strategy (owner-gated)

- **Ownership**: root skeleton `.gitignore`, `README.md` (adopt existing, do not recreate; CSA Section 8).
- **Steps**: verify skeleton dirs exist and are empty (`ls frontend backend deploy scripts docs`); re-verify `papyr-reference\` porcelain empty; then, after owner G-1, `git init` and create the working branch per the recorded strategy (protected `main`, feature branches per task boundary); verify `git status --porcelain` shows `papyr-reference\` excluded and untracked (CSA Section 5.1).
- **Gates interleaved**: G8 (ignore-rule proof: `git check-ignore -v .env.papyr` and `git check-ignore -v papyr-reference/README.md`), G9 (staging review, expect 69 entries), G10 (`git add -A`; `git diff --cached --name-only` shows 69 files, no `.env*`, no `papyr-reference\`, no nested-repo warning), G11 (index secret scan), G12 (first commit + `gitleaks detect --source .`). See RSA Section 9.
- **TDD**: this task has no red/green test; its acceptance is the gate list itself.
- **Commit subject**: `chore: initialize rebuild repository skeleton at workspace root` (CSA Section 5.1; plan line 317).
- **Acceptance**: skeleton dirs present with zero production code; `papyr-reference\` porcelain empty; repository initialized at root under G-1; `papyr-reference\` excluded and untracked; branch strategy recorded; first atomic commit exists.

### PR-02: Canonical documentation baseline

- **Ownership**: `scripts/check-docs-migration.sh` (exists; KEEP), `docs/canonical-docs-baseline.md` (create; CSA Section 5.2).
- **Resume note (C6)**: the check script already exists and already FAILs because the baseline file is absent. Resume at step 2 verification, then create the baseline (CSA Section 7 C6).
- **TDD RED**: `scripts/check-docs-migration.sh`; expected FAIL, baseline record absent (already true today).
- **GREEN**: create `docs/canonical-docs-baseline.md` documenting canonical paths, the DEC-001..DEC-202 range, and governed-record status under DEC-198; re-run the script; expected PASS.
- **Commit subject**: `docs: record canonical documentation baseline at repository root` (plan line 332).
- **Acceptance**: script FAIL before baseline, PASS after; every DEC ID present; baseline records governed-record status (CSA Section 5.2). The script is dependency-free per the cross-review fix (CSA Section 5.2 note).
- **Conflict applied**: C2 range sync to DEC-001..DEC-202 (script already targets DEC-202).

### PR-03: Resolution register

- **Ownership**: `docs/resolution-register.md` (exists, 38 lines, 28 rows; adopt as deliverable; CSA Section 8).
- **Steps**: verify 28 rows with non-empty status via `grep -c '^| R-' docs/resolution-register.md` (expect 28); confirm R-01/R-02/R-26/R-27/R-28 resolved rows carry disposition dates; persist an evidence record for R-02 (migrate the owner-quoted comment out of `.env.papyr`) and for R-26 (probe evidence is missing; CSA Section 11 items 1-2).
- **TDD**: none; verification is the row-count and status check.
- **Commit subject**: `docs: add owner resolution register` (plan line 347).
- **Acceptance**: 28 rows with non-empty status; resolved rows carry disposition dates; register reviewed with the owner at the P0 gate (plan line 346; part of REVIEW LOOP 2).

### FD-01: Frontend workspace scaffold

- **Ownership**: `frontend/package.json`, `frontend/tsconfig.json` (carry `strict: true`, `noEmit`, `moduleResolution: bundler`, `@/*` alias from the legacy baseline; FAA Section 11), `frontend/next.config.ts`, `frontend/eslint.config.mjs`, `frontend/postcss.config.mjs`, `frontend/.prettierrc`, `frontend/src/app/globals.css` (empty token shell), `frontend/src/app/page.tsx` (minimal). Do not create `[locale]/`, i18n, or a11y surfaces; those are Phase 2 (SH-01..SH-03) (FAA Section 6).
- **TDD RED**: write a Vitest smoke test asserting `next.config.ts` exists and exports a config object; run `npm test` in `frontend\`; expected FAIL, no test runner yet.
- **GREEN**: scaffold the eight files; `npm test` and `npm run lint`; expected PASS.
- **Script names**: `dev`, `build`, `start`, `lint`, `test` (Vitest), `test:e2e` (Playwright), `format:check`. Dependency floors: next, react, react-dom, tailwindcss v4, typescript; versions pinned at install time from current official releases (DEC-056; CSA Section 5.4). Per CTR Section 4, pin TypeScript 6.0.x (typescript-eslint does not support TS 7), ESLint 9.x (not 10), Node 24 for the runtime.
- **Commit subject**: `chore(frontend): scaffold Next.js workspace` (plan line 370).
- **Acceptance**: eight named scripts present; dependency floors present; smoke test and lint pass; `globals.css` is an empty token shell.

### FD-02: Backend workspace scaffold

- **Ownership**: `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/ruff.toml`, `backend/pytest.ini`, `backend/app/__init__.py`, `backend/app/main.py` (minimal FastAPI shell with `/health`), `backend/tests/test_health.py`. Do not create `Dockerfile.production`; that is a SEC-04 Phase 5 target (FAA Section 6). No legacy modules carried over (CSA Section 5.5).
- **TDD RED**: `pytest tests/test_health.py -v` in `backend\`; expected FAIL, no app module.
- **GREEN**: minimal `app/main.py` with the FastAPI app and `/health` only; `pytest tests/ -v` and `ruff check .`; expected PASS.
- **Commit subject**: `chore(backend): scaffold FastAPI workspace` (plan line 385).
- **Acceptance**: `/health` returns 200 `status: ok`; pytest and ruff pass; no legacy modules carried over.

### FD-03: Deploy workspace scaffold

- **Ownership**: `deploy/docker-compose.yml` (skeleton), `deploy/nginx/conf.d/production.conf` (skeleton), `deploy/.env.production.example` (non-secret variable names only), `deploy/runbook-vps.md` (outline) (CSA Section 5.6). The `.gitignore` negation from G2 (C5) must already be in place so the env template is not ignored.
- **TDD RED**: `docker compose -f deploy/docker-compose.yml config --quiet` from the repo root; expected non-zero exit, file absent.
- **GREEN**: write the skeleton with service names `nginx`, `api`, `redis`, `workers` (`scanner` later in SEC-03); re-run the command; expected exit 0. Docker is never started; config validation only.
- **Commit subject**: `chore(deploy): scaffold compose and nginx skeleton` (plan line 400).
- **Acceptance**: compose parses (exit 0) with the four service names; env template holds non-secret names only (mode-600 install per DEC-176; CSA Section 5.6).

### FD-04: CI core gate skeleton

- **Ownership**: `.github/workflows/ci.yml` (GitHub Actions per R-02, resolved; remove the "contingent on R-02" framing per C4), `scripts/check-ci.sh` (CSA Section 5.7).
- **TDD RED**: `scripts/check-ci.sh`; expected FAIL, workflow absent.
- **GREEN**: write the workflow; `scripts/check-ci.sh` PASS; then run the local equivalents of the jobs on the skeleton (frontend lint/test/build, backend ruff/test).
- **No-CD boundary (enforced, DEC-160/DEC-177)**: the workflow never deploys. `check-ci.sh` asserts (a) no `deploy` job exists and (b) no secret is exposed to `pull_request_target` events. Per CTR Section 8: triggers `pull_request` against `main` plus `push` to `main`; never `pull_request_target`; top-level `permissions: contents: read` with `permissions: {}` where no token is needed; no `secrets:` mapping anywhere; SHA-pinned actions with a trailing `# vX.Y.Z` comment (checkout v7.0.1 `3d3c42e...`, setup-node v7.0.0 `8207627...`, setup-python v7.0.0 `5fda3b9...`; CTR Section 3 table); `concurrency` group with `cancel-in-progress: true`; untrusted context passed via `env:` variables, never string interpolation; `persist-credentials: false` on checkout.
- **Jobs (DEC-177)**: frontend lint/test/build; backend ruff/test; production-build verification; Trivy security scan on built images. Model the job structure on the legacy `papyr-reference\.github\workflows\ci.yml` (RSA/FAA: 5 jobs). Production-build scope in Phase 1 is the frontend `next build`; the backend image arrives in SEC-04, so wire the Trivy/SBOM stage gated on image availability (FAA Section 15 item 4).
- **Coverage wiring (owner decision, Section 11)**: if the owner approves the >=80% target at the P0 gate, add `pytest --cov=app --cov-fail-under=80` (backend) and Vitest coverage thresholds (frontend) as gate jobs here.
- **G13**: add the gitleaks CI job (CLI 8.30.1, MIT; not the proprietary action; RSA Section 7, CTR Section 5.2) on push and PR.
- **Commit subject**: `ci: add core gate without deployment` (plan line 415).
- **Acceptance**: no deploy job; no secrets to `pull_request_target`; frontend lint/test/build and backend ruff/test pass locally; production-build and Trivy stages present per DEC-177; workflow never deploys (DEC-160, DEC-177).

### FD-05: Root tooling conventions

- **Ownership**: `README.md` (complete; REPLACE the minimal skeleton at FD-05), `CONTRIBUTING.md`, `docs/plan/index.md` (CSA Section 8).
- **Steps**: write the files with task branch naming, commit prefixes (`feat`, `fix`, `docs`, `chore`, `test`, `ci`, `refactor`, `security`), the TDD requirement, and the phase-plan expansion rule (each phase may expand into its own plan file under `docs/superpowers/plans\` following the master plan template and gates); reference the master plan by relative path.
- **TDD GREEN**: `grep -rn 'docs/superpowers/plans' docs/`; the master plan link must resolve to a real file (plan line 427).
- **Review**: step 3 is REVIEW LOOP 4, conventions reviewed with the execution agent so task branches and commit boundaries apply consistently (plan line 428).
- **Commit subject**: `docs: add contribution and planning conventions` (plan line 429).
- **Acceptance**: conventions documented; relative link to the master plan resolves; TDD requirement and phase-plan expansion rule recorded.

## 6. Five explicit review loops

| # | Loop | When | Who | Evidence required |
|---|---|---|---|---|
| R1 | Pre-init safety review | Wave 0, G1 | Owner | Redaction diff on the 5 RSA Section 4.2/4.3 files; owner sign-off recorded |
| R2 | Phase 0 gate exit review | After Wave 2 | Owner | Repo exists at root, branch strategy recorded, canonical docs baseline recorded, every R-item has a disposition; includes PR-03 step 4 register review (plan line 346, line 302) |
| R3 | Per-FD commit-boundary review | Before each of the 5 FD boundary commits | Executor + reviewer | Boundary commit subject matches the plan; TDD GREEN evidence captured (plan s2 rule 5, line 63) |
| R4 | FD-05 conventions review | FD-05 step 3 | Execution agent | Branch naming and commit prefixes agreed before later phases start (plan line 428) |
| R5 | Phase 1 exit gate review | After FD-04 end-to-end pass | Owner | Lint, test, build, and security-scan jobs pass on the wired skeleton; core gate documented per DEC-177 (plan line 355) |

## 7. TDD RED/GREEN command summary

| Task | RED command (expected FAIL) | GREEN command (expected PASS) |
|---|---|---|
| PR-02 | `scripts/check-docs-migration.sh` (baseline absent) | baseline created; script exits 0 |
| FD-01 | `npm test` (no runner in `frontend\`) | `npm test`; `npm run lint` |
| FD-02 | `pytest tests/test_health.py -v` (no app module) | `pytest tests/ -v`; `ruff check .` |
| FD-03 | `docker compose -f deploy/docker-compose.yml config --quiet` (file absent) | same command, exit 0 |
| FD-04 | `scripts/check-ci.sh` (workflow absent) | script exits 0; local job equivalents pass on the skeleton |
| FD-05 | (documentation task) | `grep -rn 'docs/superpowers/plans' docs/` resolves to the master plan |

## 8. Conflict reconciliation (C1-C6)

| Conflict | Summary | Resolution point in the DAG | Status |
|---|---|---|---|
| C1 | Plan text still self-describes as unapproved after DEC-202 (CSA Section 7) | Owner-authorized governed-record edit: sync plan Section 1 and coverage note to cite DEC-202; do this before or at R2, via superseding note or a new DEC | Owner decision required |
| C2 | PR-02 plan text says DEC-001..DEC-201; script already checks DEC-202 | Sync plan text, baseline record, and script to DEC-001..DEC-202 during PR-02 | Executed in PR-02 |
| C3 | Register marks R-02/R-26 RESOLVED; plan Section 6 still PENDING | Sync plan rows during the C1 edit; persist R-02/R-26 evidence records at PR-03 (CSA Section 11 items 1-2) | Owner decision for the plan edit; PR-03 records evidence |
| C4 | FD-04 was "contingent on R-02"; R-02 is now RESOLVED to GitHub | Drop the contingency framing in the FD-04 workflow; keep the G-4 note that CI secrets/environments are configured at execution | Executed in FD-04 |
| C5 | Root `.gitignore` ignores `deploy/.env.production.example` | Add `!deploy/.env.production.example` (or `!.env.*.example`) at G2/Wave 0 so FD-03's template is committed | Executed at G2 |
| C6 | PR-02 is mid-flight: script exists, baseline absent | Resume PR-02 at step 2 verification, then step 3 (CSA Section 7) | Executed in PR-02 |

## 9. Hard stops

- **H1**: no git operation (init, add, commit, push, remote) without owner G-1 authorization at the moment it occurs; the R-02 disposition must already be recorded (it is).
- **H2**: no `git init` before G1-G7 pass.
- **H3**: no FD-01..FD-03 start before R2 passes (Phase 1 gate entry, plan line 353).
- **H4**: no FD-04 start before FD-01..FD-03 pass their TDD verifications.
- **H5**: no FD-05 start before the FD-04 core gate passes end-to-end.
- **H6**: no push before G14-G16 pass and the owner authorizes.
- **H7**: no public visibility change without P1-P6 and explicit owner authorization.
- **H8**: if any L1/L2 scan matches a tracked candidate at any gate, stop and escalate; never force-add anything.
- **H9**: if `papyr-reference\` porcelain is non-empty at any check, stop; it must stay clean at HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`.

## 10. Owner-only gates in this block

| Gate | What |
|---|---|
| G-1 | `git init`, working-branch creation, each commit, push/remote wiring against `fazulfi/mypapyr` (CSA Section 9 item 1) |
| G1 | Redaction sign-off (Wave 0) |
| R2 | Phase 0 gate exit review, including PR-03 step 4 register review |
| C1/C2/C3 | Plan text synchronization as a governed-record edit (superseding note or new DEC) |
| Q3 | >=80% unit coverage threshold decision before it becomes an FD-04 CI gate (FAA Section 11/12 Q3) |
| License | No LICENSE exists; the new public repo needs an explicit license decision (RSA Section 12 item 5) |
| audit-outputs | Whether `audit-outputs\` ships public or is trimmed/ignored (RSA Section 12 item 1) |
| G-7 | CI license allow-list policy (owner/legal; AGPL engines; CTR Section 5.7) |
| `.env.papyr` | Credential rotation/disposition before production (DEC-017, DEC-176, G-8; CSA Section 9 item 5) |
| P6 | Public visibility flip, owner action only |

## 11. The >=80% coverage requirement (owner-requested, not yet canonical)

The >=80% unit coverage target comes from the delegation context, not from any approved canonical document (FAA Section 11: no numeric threshold exists in the plan, specs, or decisions; the legacy non-canonical stepprompts claimed 90%). Recommendation: record it as a new DEC or register disposition at R2, then wire it into FD-04 as `pytest --cov=app --cov-fail-under=80` (backend, pytest-cov 7.1.0) and Vitest coverage thresholds (frontend, `@vitest/coverage-v8`). Risk if not decided: the Phase 1 gate would not enforce coverage, and the owner-requested target would drift. The first coverage measurement lands on the FD-01/FD-02 smoke tests; the target bites at later phases.

## 12. Post-init and pre-push gates (G8-G17) and public gates (P1-P6)

Post-init and pre-push (RSA Section 9): G8 ignore-rule proof, G9 staging review (69 entries), G10 stage and index review, G11 index secret scan, G12 first commit plus `gitleaks detect --source .`, G13 gitleaks CI job (wired in FD-04), G14 remote separation (`git remote -v` must point to the new repo, never legacy `fazulfi/papyr`), G15 create private repo via `gh repo create <name> --private --source=. --push`, G16 enable secret scanning and push protection and verify the gitleaks job is green. G14-G16 sit in Wave 6 and need owner G-1.

Pre-public (RSA Section 10, owner-gated): P1 all G1-G17 pass with recorded evidence; P2 CI gitleaks green on the pushed default branch; P3 secret scanning and push protection confirmed enabled; P4 no open secret-scanning alerts; P5 owner reviews business-sensitive artifacts (RSA Section 6 item 10: `d1-adsterra.md`, `e1-gpt5-6-sol-contract.md`, `e2-automated-mdx-blog-pipeline.md`, `d5-security-threat-privacy.md`) or documents their exclusion; P6 visibility change to public, owner action only.

## 13. Confirmed decisions, recommendations, risks, unresolved questions

**Confirmed (binding, from the audits)**: DEC-202 approves plan execution; workspace root is the repository root (DEC-198); GitHub hosting for `fazulfi/mypapyr`, private, default `main` (R-02); the engine/queue matrix (R-28, DEC-199); VPS probe facts (R-26); monorepo boundaries and the exact Phase 0/1 tree; FD-01..FD-05 task contracts, TDD sequence, and boundary commits; CI core gate without CD (DEC-160, DEC-177); env template non-secret (DEC-176); strict TS carry-forward; i18n EN/ES/ID (DEC-118) and a11y (DEC-062) as Phase 2+ obligations (FAA Section 16).

**Recommendations (require owner confirmation)**: >=80% coverage as an FD-04 gate (Q3); pydantic-settings v2 for typed env schema (Q5); mypy/pyright as a backend CI type-check job (Q6); Node 24.x to match the Vercel runtime and Python 3.13 in CI (CTR Section 4; FAA Q1/Q4); Phase 1 production-build scope limited to frontend `next build` until the backend image exists (FAA Section 15 item 4); TypeScript 6.0.x and ESLint 9.x at FD-01 install (CTR Section 4.3/4.2); npm as the package manager; gitleaks CLI over the proprietary action (CTR Section 5.2).

**Risks**: an undecided coverage threshold lets the owner-requested target drift; an un-migrated R-02 evidence comment is lost if `.env.papyr` is rotated (CSA Section 11 item 2); plan text staying stale after DEC-202 keeps governed records inconsistent; AGPL-adjacent engines (Ghostscript) need the G-7 license decision before CI license gates; a backend production-build gap exists in Phase 1 until SEC-04 (FAA Section 15 item 4).

**Unresolved questions**: R-26 probe evidence has no audit file (CSA Section 11 item 1); whether the parent agent edits the approved plan directly or records a superseding note (CSA Section 11 item 3); whether per-commit G-1 authorization is relaxed during Phase 1 (FAA Section 15 item 6); whether `audit-outputs\` publishes (RSA Section 12 item 1); which exact contact emails are intended public (RSA Section 12 item 2); the LICENSE choice (RSA Section 12 item 5). None of these blocks Wave 0 through Wave 5 execution; R2 and the owner-only gates are the decision points.

## 14. Compliance statement

This delegation wrote exactly one file: `<workspace-root>\audit-outputs\phase-0\phase-0-execution-dag.md`. All other activity was reading the four cited audits. No implementation, `git init`, commits, pushes, dependency installation, network access, VPS access, or modification of `papyr-reference\` was performed. No secret values are reproduced; redaction targets are cited by path and line only.
