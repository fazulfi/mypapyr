# Papyr Rebuild: Phase 0 Foundation Architecture Audit

| Field | Value |
|---|---|
| Document ID | PPR-P0-FA-001 |
| Title | Phase 0 foundation architecture and file tree audit (frontend, backend, contracts, workspace tooling, CI boundaries, legacy patterns) |
| Date | 2026-08-01 |
| Author role | Foundation-architecture auditor (subagent, context-grooming loaded) |
| Status | Complete. Primary deliverable is this file; chat output is insufficient per AGENTS.md |
| Task constraints | Read-only except this audit file. No implementation, no dependency installation, no benchmarks. `papyr-reference/` must remain unchanged (verified: HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`, empty porcelain, exit 0) |

---

## 1. Task and intent

Map the exact Phase 0 foundation architecture and file tree from the canonical plan/specs: frontend, backend, contracts, workspace tooling, CI boundaries, and known legacy patterns. Produce proposed exact ownership boundaries, a dependency DAG, TDD units, version/tooling questions, and an acceptance mapping for FD-01..FD-05.

The delegation context additionally requires the foundation to include: strict TypeScript, typed Python, env schemas, i18n EN/ES/ID, accessibility foundations, CI without CD, and a >=80% unit coverage target. Section 11 maps each of these to canonical sources and flags which are approved versus new recommendations.

## 2. Method and sources

All commands were read-only except the creation of this audit file. No installs, builds, servers, git writes, or network operations were performed. `papyr-reference/` was read only.

Primary canonical sources (all absolute paths):

| Source | Path | Role |
|---|---|---|
| Implementation plan | `<workspace-root>\docs\superpowers\plans\2026-07-31-papyr-rebuild-implementation-plan.md` (1,450 lines) | Approved master plan (DEC-202); Phase 0 = PR-01..PR-03, Phase 1 = FD-01..FD-05 |
| Technical architecture spec | `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (1,203 lines) | PPR-TA-001 v1.1; monorepo boundaries (s3), CI gate (s19), testing strategy (s22), data classification (s23) |
| Product/UX spec | `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (732 lines) | PPR-UX-001; tokens (s10.1), i18n (s9), a11y (s16), acceptance (s20) |
| Decision log | `<workspace-root>\papyr-rebuild-decisions.md` (2,401 lines; 202 headings DEC-001..DEC-202) | Authoritative decision baseline; line anchors in Section 3 |
| Resolution register | `<workspace-root>\docs\resolution-register.md` (38 lines) | R-01..R-28 dispositions; contains dispositions newer than plan text (R-02, R-26) |
| Legacy clone | `<workspace-root>\papyr-reference\` | Read-only legacy baseline; patterns cited in Section 13 |
| Prior audits | `<workspace-root>\audit-outputs\implementation-plan-final-review-dec201.md`, `implementation-plan-final-targets-dec201.md` | Prior PASS verdict and DEC-201 sync evidence |

Precedence applied (plan s1; arch s1.4): decisions > specifications > audit/research evidence > legacy reference.

## 3. Canonical baseline summary (approved status as of this audit)

- **Plan approval:** DEC-202 (`papyr-rebuild-decisions.md:2390`) explicitly approves the master implementation plan. Product implementation may begin per phase order, gates, and resolution register. Separately gated actions (G-1..G-11) remain individually owner-authorized. **Known stale text:** the plan file itself still asserts "this plan remains unapproved" at lines 55, 1433, 1450 — written before DEC-202 and not re-synced; flag for the first correction pass (Section 15).
- **Repository root:** DEC-198 (`decisions:2344`); workspace root `<workspace-root>` (R-01 RESOLVED).
- **Engine/queue matrix:** DEC-199 (`decisions:2356`); Redis Streams consumer groups; pdf-lib, pikepdf (qpdf), img2pdf+Pillow, pypdfium2, pdf.js, `createImageBitmap` (R-28 RESOLVED; plan s6.1 rows 264-272).
- **90-day targets:** DEC-200 (`decisions:2368`), DEC-201 (`decisions:2379`) (R-27 RESOLVED).
- **R-02 (git hosting):** RESOLVED per `docs/resolution-register.md:10` and `<workspace-root>\.env.papyr` (path referenced; contents contain secrets and must never be committed or copied): GitHub, private repo `fazulfi/mypapyr`, default branch `main`. The repo was created 2026-07-31. This confirms the FD-04 CI path `.github/workflows/ci.yml` on GitHub Actions (plan FD-04 line 411 treats GitHub Actions as the proposal contingent on R-02; the register disposition now makes it the confirmed default).
- **R-26 (VPS host):** RESOLVED (`resolution-register.md:34`): read-only probe 2026-07-31 — Ubuntu 24.04.4 LTS, 15 GiB RAM, 4 cores, 2 GiB swap, Docker 29.6.2, SSH port 22. Supersedes the plan's ~8 GB/4.5 GB-swap assumption.
- **R-01, R-27, R-28:** RESOLVED. R-03..R-25 remain PENDING at their stop conditions.

## 4. Current workspace state (evidence collected 2026-08-01)

| Path | State | Evidence |
|---|---|---|
| `<workspace-root>\frontend\` | Empty directory (0 entries) | `read` directory |
| `<workspace-root>\backend\` | Empty directory (0 entries) | `read` directory |
| `<workspace-root>\deploy\` | Empty directory (0 entries) | `read` directory |
| `<workspace-root>\scripts\` | Contains `check-docs-migration.sh` | `read`; script checks DEC-001..DEC-202 presence, both specs, and `docs/canonical-docs-baseline.md` (PR-02 deliverable, currently absent -> script FAILs until PR-02 step 3) |
| `<workspace-root>\docs\` | `resolution-register.md` + `superpowers/specs/` + `superpowers/plans/`; no `canonical-docs-baseline.md` | glob + read |
| `<workspace-root>\audit-outputs\phase-0\` | Empty directory | `read` (this file now written here) |
| `<workspace-root>\.gitignore` | Exists; excludes `/papyr-reference/`, `.env*` (except `.env.example`), node_modules, `.next`, `__pycache__`, caches | `read` |
| `<workspace-root>\.env.papyr` | Local secret/config record (owner-authorized 2026-07-31; gitignored). Contains live credentials (Cloudflare, R2, AI gateway, Telegram, backup S3, Vercel/GitHub facts). NOT reproduced here; must be rotated per DEC-017/DEC-176 before production use | `read` (no values copied) |
| `<workspace-root>\README.md` | Minimal rebuild-workspace README; records governed records and approved scope; notes plan approved (DEC-202) | `read` |
| `<workspace-root>\AGENTS.md` | Orchestrator rules governing delegated work | supplied in context |
| `<workspace-root>\papyr-reference\` | Read-only legacy clone; clean at HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`; empty porcelain, exit 0 | `git status --porcelain` + `git rev-parse HEAD` (read-only) |

Phase 0 gate status: PR-01 step 2 (skeleton dirs + .gitignore) is effectively pre-created; remote repo exists (G-1 repository creation exercised). PR-02 (baseline record) and PR-03 (register: exists, but plan expects creation as PR-03 deliverable) are not yet completed as gated tasks. No Phase 1 (FD) work exists.

## 5. Phase 0 and Phase 1 task map (canonical, plan s5 and s8)

Phase 0 - Pre-execution prerequisites and owner gates (plan lines 296-347). Gate entry: owner approves the plan (done, DEC-202). Gate exit: repository exists at workspace root (done), branch strategy recorded, canonical docs baseline-recorded, every R-item disposition recorded (partially done - register has 28 rows, 5 resolved).

| Task | Deliverable (canonical files) | Plan lines |
|---|---|---|
| PR-01 | `.gitignore`, `README.md`; git init + branch (G-1 gated) | 304-317 |
| PR-02 | `scripts/check-docs-migration.sh`, `docs/canonical-docs-baseline.md` | 319-332 |
| PR-03 | `docs/resolution-register.md` (28 rows) | 334-347 |

Phase 1 - Monorepo foundation and CI core gate (plan lines 349-429
). Gate entry: Phase 0 complete. Gate exit: lint, test, build, and security-scan jobs pass on the wired skeleton; core gate documented per DEC-177 (plan line 355).

| Task | Deliverable (canonical files) | Plan lines |
|---|---|---|
| FD-01 | `frontend/package.json`, `frontend/tsconfig.json`, `frontend/next.config.ts`, `frontend/eslint.config.mjs`, `frontend/postcss.config.mjs`, `frontend/.prettierrc`, `frontend/src/app/globals.css` (empty token shell), `frontend/src/app/page.tsx` (minimal) | 357-370 |
| FD-02 | `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/ruff.toml`, `backend/pytest.ini`, `backend/app/__init__.py`, `backend/app/main.py` (minimal FastAPI shell with `/health`) | 372-385 |
| FD-03 | `deploy/docker-compose.yml` (skeleton), `deploy/nginx/conf.d/production.conf` (skeleton), `deploy/.env.production.example`, `deploy/runbook-vps.md` (outline) | 387-400 |
| FD-04 | `.github/workflows/ci.yml` (contingent on R-02 - now resolved to GitHub), `scripts/check-ci.sh` | 402-415 |
| FD-05 | `README.md` (complete), `CONTRIBUTING.md`, `docs/plan/index.md` | 417-429 |

Task-index edges (plan lines 157-221): FD-01 produces for SH, TL; FD-02 for BE; FD-03 for BE, SEC, OP; FD-04 for all; FD-05 for all. FD-04 consumes FD-01..FD-03 and R-02; FD-05 consumes FD-01..FD-04.

## 6. Proposed Phase 0/1 foundation file tree (exact)

Paths relative to the workspace root `<workspace-root>` (DEC-198; plan s3, lines 71-126). Items marked (P1) are Phase 1 FD deliverables; unmarked items exist today. Later-phase files are NOT created in Phase 1.

```
<workspace-root>
├── .gitignore                         PR-01 (exists)
├── README.md                          PR-01 minimal (exists) / FD-05 complete (later)
├── AGENTS.md                          governed record (exists)
├── papyr-rebuild-decisions.md         governed record (exists, DEC-001..DEC-202)
├── audit-outputs/                     governed records (exists; phase-0/ now holds this audit)
├── docs/
│   ├── resolution-register.md         PR-03 (exists; 28 rows)
│   ├── canonical-docs-baseline.md     PR-02 (absent - create)
│   ├── plan/index.md                  FD-05 (absent)
│   └── superpowers/                   specs + plan (exist)
├── scripts/
│   ├── check-docs-migration.sh        PR-02 (exists; checks DEC-001..DEC-202)
│   └── check-ci.sh                    FD-04 (absent)
├── frontend/                          FD-01
│   ├── package.json                   (P1)
│   ├── tsconfig.json                  (P1) carry strict:true from legacy
│   ├── next.config.ts                 (P1)
│   ├── eslint.config.mjs              (P1)
│   ├── postcss.config.mjs             (P1)
│   ├── .prettierrc                    (P1)
│   ├── src/app/globals.css            (P1, empty token shell)
│   └── src/app/page.tsx               (P1, minimal)
├── backend/                           FD-02
│   ├── requirements.txt               (P1)
│   ├── requirements-dev.txt           (P1)
│   ├── ruff.toml                      (P1)
│   ├── pytest.ini                     (P1)
│   ├── app/__init__.py                (P1)
│   ├── app/main.py                    (P1, minimal FastAPI + /health)
│   └── tests/test_health.py           (P1, TDD unit)
├── deploy/                            FD-03
│   ├── docker-compose.yml             (P1, skeleton; services nginx, api, redis, workers; scanner later)
│   ├── nginx/conf.d/production.conf   (P1, skeleton)
│   ├── .env.production.example        (P1, non-secret template)
│   └── runbook-vps.md                 (P1, outline; canonical ops runbook)
├── .github/workflows/ci.yml           FD-04 (GitHub Actions per R-02; core gate only, NO deploy job)
└── papyr-reference/                   read-only legacy clone (excluded; untouched)
```

Notes:
- `backend/Dockerfile.production` is listed in the plan tree (line 110) but FD-02 does not create it; it is a Phase 5 (SEC-04) target. Do not create in Phase 1.
- `frontend/src/app/[locale]/` and i18n/a11y surfaces arrive in Phase 2 (SH-01..SH-08).
- CI artifacts (SBOM, vuln scans, test reports) are generated outputs, never maintained source (DEC-026; plan line 132).
- `docs/canonical-docs-baseline.md` is required by `scripts/check-docs-migration.sh`; the script currently FAILs on its absence (PR-02 step 2 expected state).

## 7. Proposed ownership boundaries

Boundary rule (arch s3.1-3.3, plan s3): one monorepo at the workspace root; explicit directory ownership; `papyr-reference/` excluded and read-only; secrets never committed (DEC-176); generated reports are CI artifacts (DEC-026).

| Boundary | Owns | Does not own | Consumes from |
|---|---|---|---|
| `frontend/` (Vercel) | Next.js App Router app, unit tests, Playwright E2E, i18n messages, components/lib/hooks, catalog | server processing, queue, engines, page rendering of backend | BE-06/BE-08 contract APIs (later), FD-01 scaffold |
| `backend/` (VPS FastAPI) | FastAPI app shell, /health, Settings (BE-01), routers/services/queue/tasks/security/utils (later phases) | page rendering, browser logic | FD-02 scaffold |
| `deploy/` (VPS compose) | compose stack, nginx conf, env template, runbook | application code | FD-03 scaffold; completed by SEC-04, OP-01, OP-04 |
| `scripts/` (repo) | dependency-free verification/config-check scripts (check-docs-migration, check-ci, later check-compose, check-nginx, etc.) | production code | PR-02, FD-04 |
| `.github/workflows/` (CI) | core gate only: lint, test, build, production-build verification, Trivy scan; never deploys (DEC-160, DEC-177) | deployment, secrets delivery | FD-01..FD-03, R-02 |
| `docs/` (canonical) | specs, plan, resolution register, baseline record, plan index | research outputs | PR-02, PR-03, FD-05 |
| `audit-outputs/` (discovery) | durable research/audit records | canonical decisions | ongoing |
| `papyr-reference/` | read-only legacy evidence only | any modification | n/a |

CI boundary details (FD-04, plan lines 402-415; DEC-177 decisions:2076-2085; DEC-160 decisions:1884-1894): workflow may build, test, scan artifacts; must never change production. `scripts/check-ci.sh` asserts (a) no `deploy` job exists and (b) no secret is exposed to `pull_request_target` events. Model job structure on legacy `papyr-reference/.github/workflows/ci.yml` (5 jobs) and add production-build + security-scan (Trivy) stages. The legacy `deploy-vps.yml` (build, Trivy, SBOM, GHCR, SSH deploy, smoke, rollback) becomes evidence for a manual agent-executed procedure, not an automated pipeline (arch s19.2).

## 8. Dependency DAG (Phase 0 -> Phase 1 -> consumers)

Derived from the plan's phase table (lines 136-151), task index (157-221), and each FD task's Consumes/Produces.

```
Phase 0 (PR):
  PR-01 (repo skeleton + branch, G-1)
    ├──> PR-02 (docs baseline)      consumes PR-01, DEC-198
    ├──> PR-03 (resolution register) consumes PR-01, Section 6 dispositions
    ├──> FD-01 (frontend scaffold)  consumes PR-01
    ├──> FD-02 (backend scaffold)   consumes PR-01
    └──> FD-03 (deploy scaffold)    consumes PR-01

Phase 1 (FD):
  FD-01, FD-02, FD-03  (independent, parallelizable)
    └──> FD-04 (CI core gate)       consumes FD-01..FD-03 + R-02 (RESOLVED -> GitHub Actions)
           └──> FD-05 (root tooling conventions) consumes FD-01..FD-04
                  └──> Phase 2 (SH-01..SH-08) consumes FD-01 (route names also need R-15)
                  └──> Phase 3 (BE-01..BE-10, SEC-01, SEC-02) consumes FD-02
                  └──> SEC-04 / OP-01 / OP-04 consume FD-03
                  └──> SEC-06 / CT-03 consume FD-04 (dependency pipeline, blog workflow)
                  └──> all later phases consume FD-05 conventions
```

Key ordering constraints:
- FD-04 must not exist before FD-01..FD-03 (its jobs run against the wired skeleton).
- FD-05's `docs/plan/index.md` links to the master plan by relative path; verify with `grep -rn 'docs/superpowers/plans' docs/` (plan line 427).
- Phase 1 exit gate (plan line 355) is the first place the full CI core gate must pass.
- R-15 (slugs) gates SH-01 route names; R-03 gates BE-08; R-07/R-08/R-09 gate BE-04/BE-05; none of these block Phase 1 FD tasks.

## 9. TDD units for FD-01..FD-05

Every implementation task follows: write failing test -> verify fail -> minimal implementation -> verify pass -> review and commit boundary (plan s2 rule 2, line 60; DEC-177 core gate).

### FD-01 Frontend workspace scaffold (plan lines 357-370)
- Unit TDD: Vitest smoke test asserting the workspace exports a buildable config (e.g. `next.config.ts` exists and exports a config object).
- FAIL: `npm test` (no test runner yet). PASS: `npm test` + `npm run lint`.
- Boundary commit: `chore(frontend): scaffold Next.js workspace`.
- Script names required: `dev`, `build`, `start`, `lint`, `test` (Vitest), `test:e2e` (Playwright), `format:check`.
- Dependency floors: next, react, react-dom, tailwindcss v4, typescript (plan line 364). Versions pinned at install time from current official releases (DEC-056, plan line 368).

### FD-02 Backend workspace scaffold (plan lines 372-385)
- Unit TDD: `backend/tests/test_health.py` asserting `GET /health` returns 200 with `status: ok`.
- FAIL: `pytest tests/test_health.py -v` (no app module). PASS: `pytest tests/ -v` + `ruff check .`.
- Boundary commit: `chore(backend): scaffold FastAPI workspace`.
- Script names required: `ruff check`, `ruff format --check`, `pytest` (plan line 379).

### FD-03 Deploy workspace scaffold (plan lines 387-400)
- Config TDD: shell test `docker compose -f deploy/docker-compose.yml config --quiet`.
- FAIL: non-zero exit (file absent). PASS: exit 0 (config validation only; Docker never started).
- Skeleton services: `nginx`, `api`, `redis`, `workers` (`scanner` added later in SEC-03); env template carries non-secret variable names only.
- Boundary commit: `chore(deploy): scaffold compose and nginx skeleton`.

### FD-04 CI core gate skeleton (plan lines 402-415)
- Gate TDD: `scripts/check-ci.sh` parses the workflow YAML and asserts (a) no `deploy` job exists, (b) no secret exposed to `pull_request_target` events.
- FAIL: `scripts/check-ci.sh` (workflow absent). PASS: script exits 0 + local equivalents of the jobs pass on the skeleton.
- Jobs (DEC-177): frontend lint/test/build; backend ruff/test; production build verification; Trivy security scan on built images. Never deploys.
- Boundary commit: `ci: add core gate without deployment`.
- R-02 resolved to GitHub Actions (register line 10), so the workflow path is `.github/workflows/ci.yml`; legacy `papyr-reference/.github/workflows/ci.yml` is the job-structure baseline (Node 20, Python 3.11, 5 jobs).

### FD-05 Root tooling conventions (plan lines 417-429)
- Documentation TDD: write `README.md` (complete), `CONTRIBUTING.md`, `docs/plan/index.md` with conventions: task branch naming, commit prefixes (`feat`, `fix`, `docs`, `chore`, `test`, `ci`, `refactor`, `security`), TDD requirement, phase-plan expansion rule under `docs/superpowers/plans/`.
- Verify: `grep -rn 'docs/superpowers/plans' docs/` resolves to the real master plan.
- Boundary commit: `docs: add contribution and planning conventions`.

## 10. FD-01..FD-05 acceptance mapping

Acceptance derives from each task's Interfaces/Produces (plan lines 357-429) and the Phase 1 exit gate (line 355): lint, test, build, and security-scan jobs pass on the wired skeleton; core gate documented per DEC-177.

| Task | Produces (canonical contract) | Pass evidence (commands) | Gated consumers |
|---|---|---|---|
| FD-01 | Next.js workspace with scripts `dev`, `build`, `start`, `lint`, `test` (Vitest), `test:e2e` (Playwright), `format:check`; dep floors next/react/react-dom/tailwindcss v4/typescript | `npm test` PASS; `npm run lint` PASS; buildable `next.config.ts` smoke test | SH-01..SH-08, TL-01..TL-06, PT-01, PT-02, VL-02, VL-04, SEO-03 |
| FD-02 | FastAPI workspace with `ruff check`, `ruff format --check`, `pytest`; `/health` returns 200 `status: ok` | `pytest tests/ -v` PASS; `ruff check .` PASS | BE-01..BE-10, SEC-01..SEC-03 |
| FD-03 | Deploy workspace: compose skeleton (`nginx`, `api`, `redis`, `workers`; `scanner` later), nginx skeleton, non-secret env template, runbook outline | `docker compose -f deploy/docker-compose.yml config --quiet` exit 0 | SEC-04, SEC-05, OP-01, OP-04, VL-05 |
| FD-04 | CI core gate: frontend lint/test/build, backend ruff/test, production-build verification, Trivy scan; no deploy job; no `pull_request_target` secret exposure | `scripts/check-ci.sh` PASS (asserts the two prohibitions); local equivalents of jobs PASS on skeleton | all phases; SEC-06; CT-03 workflow wiring |
| FD-05 | Complete `README.md`, `CONTRIBUTING.md`, `docs/plan/index.md` with branch naming, commit prefixes, TDD rule, phase-plan expansion rule | `grep -rn 'docs/superpowers/plans' docs/` resolves to the master plan | all phases (conventions) |

Phase 1 gate completion checklist: (1) all five FD tasks pass their TDD verifications; (2) FD-04 core gate passes end-to-end; (3) `scripts/check-ci.sh` green; (4) `papyr-reference/` still clean; (5) review boundary passed at each FD commit (plan s2 rule 5, line 63).

## 11. Foundation requirement coverage map (delegation context vs canonical)

The delegation requires: strict TS, typed Python, env schemas, i18n EN/ES/ID, accessibility foundations, CI without CD, >=80% unit coverage target. Status per source:

| Requirement | Canonical source (approved) | Coverage in Phase 0/1 | Status |
|---|---|---|---|
| Strict TypeScript | Legacy `papyr-reference/frontend/tsconfig.json:7` (`"strict": true`); FD-01 creates `frontend/tsconfig.json` (plan 357-370) | Carry `strict: true`, `noEmit`, `moduleResolution: bundler`, `@/*` path alias into the new tsconfig; type-check in CI build | APPROVED direction (plan + DEC-028 baseline retention); exact tsconfig contents recommended, low risk |
| Typed Python | Legacy frozen dataclass `Settings` with full annotations (`papyr-reference/backend/utils/config.py:52-76`); plan BE-01 "frozen Settings (replaces legacy utils/config.py)" (plan 577) | FD-02 scaffold is minimal; typed settings land in BE-01. Type enforcement = ruff only in canonical docs | APPROVED for Settings shape; mypy/pyright enforcement is a NEW recommendation (Section 12 Q6) |
| Env schemas | DEC-176 (decisions:2065-2074); legacy `.env.production.example`; legacy `config.py` `_require()` raising on missing vars; FD-03 `.env.production.example` (non-secret names only, plan 398) | Env template at FD-03; runtime validation at BE-01 (frozen Settings raising on missing/typed defaults) | APPROVED pattern; mechanism (pydantic vs dataclass) open (Section 12 Q5) |
| i18n EN/ES/ID | DEC-118 (decisions:1419-1428); UX s9; SH-01 creates `frontend/src/i18n/config.ts` + `messages/{en,es,id}.json` (plan 442) | Phase 1 has NO i18n deliverable; i18n foundations begin Phase 2 (SH-01). Phase 1 must not hardcode locale assumptions | APPROVED but Phase 2-owned; confirm no Phase 1 i18n expectation (Section 15 Q10) |
| Accessibility foundations | DEC-062 (decisions:764-774); UX s16; D8-D13 corrections (UX 10.6) | Phase 1 scaffold carries no a11y behavior; skip link / focus-visible / aria land in SH-02/SH-03 (Phase 2); a11y verification program is VL-02 | APPROVED but Phase 2-owned; same confirmation as i18n |
| CI without CD | DEC-160 (decisions:1884-1894), DEC-177 (decisions:2076-2085); FD-04 (plan 402-415) | FD-04 workflow never deploys; `check-ci.sh` asserts no `deploy` job and no `pull_request_target` secrets; deploy remains manual (G-3) | APPROVED and enforced by test |
| >=80% unit coverage target | NOT in any canonical approved doc. Legacy non-canonical stepprompts claimed 90% (`papyr-reference/stepprompts/step-prompts-fase2.md:99-100,119`). Legacy tooling exists: `@vitest/coverage-v8` in frontend devDeps (package.json:42) and `pytest-cov` in backend dev reqs (requirements-dev.txt:3), but no threshold is configured anywhere | No Phase 1 file sets a coverage threshold | NEW requirement from delegation context -> needs owner decision (Section 12 Q3); recommended wiring: `vitest run --coverage --coverage.thresholds.100` style thresholds and `pytest --cov=app --cov-fail-under=80` as CI gate jobs in FD-04 |

Findings: the first six requirements trace to approved decisions; the >=80% coverage target is the only one absent from canonical sources and must be formally recorded (new decision or register disposition) before it becomes a CI gate.

## 12. Version and tooling questions

Versions are pinned at install time from current official releases (DEC-056; plan line 368). Legacy pins below are baseline evidence, not binding. Open questions need an owner decision or an implementation-time confirmation (M-items in X1 research index).

| # | Tool | Legacy pin (evidence) | Canonical constraint | Question / recommendation | Owner action |
|---|---|---|---|---|---|
| Q1 | Node.js | 20 in CI (`papyr-reference/.github/workflows/ci.yml:26,50,74`); Vercel project verified on Node 24.x (`.env.papyr`) | none explicit | CI `setup-node` version vs Vercel runtime (24.x); recommend matching Vercel 24.x | Confirm at FD-01/FD-04 |
| Q2 | Next.js / React / TS | next 16.2.4, react/react-dom 19.2.4, typescript ^5 (frontend package.json:29-49) | App Router baseline retained (arch s4.1); strict TS required | Pin current stable at install; keep `strict: true` | None (DEC-056 pin at install) |
| Q3 | Unit coverage threshold | no threshold anywhere; legacy stepprompts (non-canonical) 90% | none in approved docs | >=80% per delegation context; recommend `pytest --cov=app --cov-fail-under=80` and Vitest coverage thresholds wired into FD-04 CI jobs | New decision or R-register disposition required |
| Q4 | Python | 3.11 in CI (ci.yml:99); ruff target py311 (ruff.toml:1) | none explicit | 3.11 vs newer; recommend pinning what CI uses | Confirm at FD-02 |
| Q5 | Backend Settings mechanism | frozen dataclass + `_require()` (config.py:52-113) | BE-01 "frozen Settings" (plan 577) | pydantic-settings v2 vs dataclass; recommendation: pydantic-settings (typed env schema) but dataclass is DEC-approved legacy carry | Decide at BE-01 (Phase 3) |
| Q6 | Python type-checker | ruff only (E,F,I,W,UP,B; ruff.toml:5) | "typed Python" from delegation context | mypy or pyright as CI job is a NEW recommendation; not in canonical docs | Decide if required |
| Q7 | FastAPI/uvicorn | fastapi 0.115.12, uvicorn 0.34.2 (requirements.txt:1-2) | FastAPI behind Nginx (arch s6) | Pin current at install | None |
| Q8 | R2 client | boto3 1.38.10 (requirements.txt:4) | R2 S3-compatible (arch s12) | Pin at install; keep UUID opaque keys (DEC-174) | None |
| Q9 | Redis client | not in legacy MVP reqs | Redis Streams consumer groups (DEC-199); version pin at implementation (M11) | redis-py version pinned at BE-04; R-09 still PENDING | R-09 disposition before BE-04 |
| Q10 | Ruff / pytest stack | ruff 0.7.4, pytest 8.3.5, pytest-asyncio 0.25.3, pytest-cov 5.0.0, httpx 0.28.1 (requirements-dev.txt) | ruff + pytest in CI (DEC-177) | Pin current at install; pytest-cov retained for Q3 | None |
| Q11 | CI provider / scanning | GitHub Actions (ci.yml, deploy-vps.yml) | R-02 RESOLVED -> GitHub; DEC-177 core gate; Trivy + SBOM precedent in deploy-vps.yml | Workflow path `.github/workflows/ci.yml`; Trivy scan on built images; SBOM as CI artifact (syft, DEC-026) | None (R-02 resolved) |
| Q12 | Ghostscript | legacy compress_service.py (no `-dSAFER`, a confirmed gap per plan 780) | DEC-195; R-05 PENDING | Distribution/version pin + focused license review before launch; fallback path if review fails | R-05 disposition before TL-02 |

Stop conditions relevant to Phase 0/1 execution (plan s6): R-02 RESOLVED (register:10) unlocks FD-04's path. R-15 gates SH-01 route names (Phase 2). R-03 gates BE-08; R-07/R-08 gate BE-05; R-09 gates BE-04 (Phase 3). No pending R-item blocks Phase 1 FD tasks. G-1 (commits/pushes) remains owner-authorized per commit per plan s7; the repository creation part of G-1 was already exercised (repo exists at github.com/fazulfi/mypapyr, private, main).

## 13. Legacy patterns inventory (read-only evidence, never copied wholesale)

Precedence: legacy behavior is reference, must be re-justified (DEC-001, DEC-059). All paths under `<workspace-root>\papyr-reference\`.

| Area | Path | Pattern / lesson for the rebuild |
|---|---|---|
| FE config | `frontend/package.json` | Script set (dev/build/start/lint/test/test:e2e/format:check), Vitest + coverage-v8 devDep, Playwright, prettier scripts |
| FE config | `frontend/tsconfig.json:7` | `strict: true` baseline for FD-01 tsconfig |
| FE config | `frontend/vitest.config.ts` | environment node, `@` alias, e2e excluded |
| FE config | `frontend/playwright.config.ts` | 3 projects (chromium/firefox/mobile-chrome), baseURL localhost:3000 |
| FE src | `frontend/src/app/*/page.tsx` | Legacy unprefixed routes (compress, merge, split, image-to-pdf, pdf-to-image, plus deferred tools); rebuild moves under `[locale]/` (DEC-023) |
| FE src | `frontend/src/components/{Navbar,Footer,OtherTools,PageRangeInput,PDFUploader,PasswordInput,PrivacyNotice}.tsx` | Component baseline for SH-05/SH-06/TL-01; D1-D13 corrections apply (UX 10.6) |
| FE src | `frontend/src/hooks/useAsyncTask.ts` | Legacy 3s-poll/180s-timeout hook replaced by `useTaskPolling` (plan tree line 95) |
| FE src | `frontend/src/lib/{pdfUtils,format,config,analytics}.ts` | Browser merge/split/image-to-pdf utils; mirrored limits removed per DEC-165; analytics leakage fixed per PT-01 (plan 932) |
| BE shell | `backend/main.py` | Lifespan cleanup loop, slowapi limiter, CORS allowlist, router mounting, `/health`; BE-10 replaces per-process limiter with Redis-shared counters (plan 716) |
| BE config | `backend/utils/config.py` | Frozen dataclass Settings, `_require()` missing-var raise -> BE-01 frozen Settings (plan 577) |
| BE utils | `backend/utils/{r2,cleanup,pdf_validator,logging_config}.py` | R2 UUID keys (BE-03), 30-min cleanup loop replaced by per-job deadline (BE-07, arch 12.3), validation order (BE-02), JSON structured logging (BE-01) |
| BE services | `backend/services/async_task.py` | In-memory `_tasks` store replaced by Redis queue (DEC-019, arch 6.3) |
| BE services | `backend/services/compress_service.py` | Lacks `-dSAFER`; rebuild adds safety flags (DEC-195; plan 780) |
| BE deps | `backend/requirements.txt` | Contains non-MVP OCR/office stacks (ocrmypdf, pdf2docx, camelot-py, opencv) -> excluded by SEC-06 (plan 909-911; arch s21) |
| BE image | `backend/Dockerfile.production` | Multi-stage, user UID 1001, tini PID 1, HEALTHCHECK, quarterly base refresh; SEC-04 modernizes (plan 879) |
| Deploy | `deploy/docker-compose.yml` | Hardening baseline: read_only, cap_drop ALL + minimal cap_add, no-new-privileges, tmpfs, CPU/mem limits, healthchecks, json-file log caps (arch s7.3) |
| Deploy | `deploy/nginx/conf.d/production.conf` | Rate zones (30r/m + 2r/s burst), Cloudflare real-IP ranges (lines 59-74), `real_ip_header CF-Connecting-IP`, `server_tokens off`, `X-Frame-Options DENY`; SEC-05 modernizes with R-11 values |
| Deploy | `deploy/.env.production.example` | Non-secret template, mode-600 install at /opt/papyr/production/.env (DEC-176) |
| CI | `.github/workflows/ci.yml` | 5 jobs (FE lint/test/build, BE ruff/test) -> core gate model for FD-04 |
| CI | `.github/workflows/deploy-vps.yml` | Automated deploy (build/Trivy/SBOM/GHCR/SSH/smoke/rollback) -> reworked into manual agent procedure per DEC-160 |

## 14. Verification evidence (read-only commands run 2026-08-01)

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Workspace layout | `read` of root, frontend, backend, deploy, scripts, audit-outputs | frontend/backend/deploy empty; scripts has check-docs-migration.sh; audit-outputs/phase-0 empty (now holds this file) |
| 2 | Legacy cleanliness | `git -C papyr-reference status --porcelain`; `git -C papyr-reference rev-parse HEAD` | Empty porcelain, exit 0; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (matches plan self-review line 1446 and all prior audits) |
| 3 | Plan line anchors | `read` of plan (1,450 lines, full) | FD-01..FD-05 at 357-429; Phase tables 136-151; task index 157-221; tree 71-126; CI gate FD-04 402-415 |
| 4 | Spec anchors | `read` of arch spec (1,203 lines) and UX spec (732 lines), full | arch s3 (177-206), s19 (863-899), s22 (938-974), s23 (977-1016); UX s9 (175-185), s10.1 (191-208), s16 (556-586), s20 (629-697) |
| 5 | Decision anchors | `grep '^## DEC-'` + targeted reads | 202 headings; DEC-062:764, DEC-118:1419, DEC-160:1884, DEC-176:2065, DEC-177:2076, DEC-197:2332, DEC-198:2344, DEC-199:2356, DEC-200:2368, DEC-201:2379, DEC-202:2390 |
| 6 | Resolution register | `read docs/resolution-register.md` (38 lines) | 28 rows; R-01, R-02, R-26, R-27, R-28 RESOLVED; R-03..R-25 PENDING |
| 7 | Coverage target scan | `grep -i 'coverage'` on plan; `grep '80%|coverage'` on docs | No numeric unit-coverage threshold in any canonical doc; legacy stepprompts (non-canonical) claim 90% |
| 8 | Legacy configs | `read` frontend package.json/tsconfig/next.config/vitest.config/playwright.config; backend requirements/requirements-dev/ruff.toml/pytest.ini/main.py/utils/config.py; deploy compose/.env.production.example; ci.yml | Strict TS confirmed; frozen dataclass Settings confirmed; 5-job CI confirmed; hardening baseline confirmed; env template confirmed |
| 9 | Nginx/Dockerfile key lines | `grep` on production.conf and Dockerfile.production | Rate zones, CF ranges 59-74, server_tokens off, X-Frame-Options DENY; user 1001, tini, HEALTHCHECK |
| 10 | Root skeleton | `read` .gitignore, scripts/check-docs-migration.sh | .gitignore excludes papyr-reference + secrets; check script targets DEC-001..DEC-202 and requires docs/canonical-docs-baseline.md (absent -> expected PR-02 FAIL state) |

## 15. Uncertainties and unresolved questions

1. **Plan approval text stale:** the plan file still asserts "this plan remains unapproved" (lines 55, 1433, 1450) after DEC-202 approved it (decisions:2390). Needs a plan sync/correction pass.
2. **Plan not synced with DEC-202:** PR-02 text (lines 328, 330) still says DEC-001..DEC-201 while `scripts/check-docs-migration.sh` already targets DEC-202.
3. **Coverage target not canonical:** the >=80% unit coverage requirement exists only in delegation context. Needs an owner decision and, once decided, wiring into FD-04 CI (Q3).
4. **Backend production-build verification in Phase 1:** FD-04 requires "production build verification" and Trivy scanning, but `backend/Dockerfile.production` is not created until SEC-04 (Phase 5). Scope question: does the Phase 1 core gate scan/build only the frontend image, or does a minimal backend Dockerfile need to exist earlier? Plan FD-04 Step 4 says "run the local equivalents of the jobs on the skeleton" - ambiguous for the backend image. Recommend: frontend `next build` as Phase 1 production-build evidence; Trivy/SBOM stage wired but gated on image availability (SEC-06).
5. **R-02 vs plan text:** register marks R-02 RESOLVED (GitHub, fazulfi/mypapyr, private, main) while plan Tech Stack (line 9) and FD-04 still say "proposal: GitHub Actions". Register is authoritative/newer; plan needs sync.
6. **Commit/push authorization model:** plan G-1 requires owner authorization per commit/push, while `.env.papyr` records "GITHUB (Autonomous through production, 2026-07-31)". Clarify whether per-commit authorization is relaxed for Phase 1 execution before starting FD tasks.
7. **Python/Node version floors:** Q1/Q4 - CI version vs Vercel runtime (Node 24.x) and Python 3.11 vs newer.
8. **Settings mechanism and type-checker depth:** Q5/Q6 - pydantic-settings vs dataclass; mypy/pyright adoption for "typed Python" are new recommendations with no canonical anchor.
9. **i18n/a11y are Phase 2-owned:** SH-01 (i18n) and SH-02/SH-03 (tokens, skip link) deliver the delegation's i18n/a11y "foundations"; Phase 1 FD tasks carry none. Confirm this split matches expectations (it follows the approved plan).
10. **`.env.papyr` secret hygiene:** file contains live credentials (Cloudflare, R2, gateway, Telegram, backup S3). It is gitignored. Per DEC-017/DEC-176 legacy credentials must be rotated before production use; audit never reproduced any value. Note the file also records R-21 gateway blocker as resolved (model `mypapyr` verified 200) and Adsterra placement 5949840 (R-18 input partially supplied) - these are operational facts for later phases, not Phase 0/1.

## 16. Approved versus recommended (summary)

**Approved (binding, from decisions/plan/specs):**
- Workspace root as repository root (DEC-198); plan approved (DEC-202).
- GitHub hosting, repo `fazulfi/mypapyr`, private, main (R-02 register:10).
- Monorepo directory boundaries and tree (arch s3; plan s3).
- FD-01..FD-05 task contracts, file lists, TDD sequence, boundary commits (plan 357-429).
- CI core gate without CD (DEC-160, DEC-177; FD-04); Trivy + SBOM as CI artifacts (DEC-026).
- Env template non-secret + protected VPS env config (DEC-176; FD-03).
- Frozen Settings pattern (plan BE-01) replacing legacy config.py.
- Strict TS carry-forward (legacy tsconfig; DEC-028 baseline retention; FD-01).
- i18n EN/ES/ID (DEC-118) and WCAG 2.2 AA (DEC-062) as Phase 2+ obligations.

**Recommended (new, require owner confirmation):**
- >=80% unit coverage threshold as a CI gate (Q3; needs decision + wiring in FD-04).
- pydantic-settings v2 for typed env schema (Q5) - dataclass remains the approved fallback.
- mypy or pyright as a backend CI type-check job (Q6).
- Node 24.x to match Vercel runtime (Q1); Python version pin choice (Q4).
- Phase 1 production-build scope limited to frontend `next build` until backend image exists (Section 15 Q4).

## 17. Files touched and compliance statement

- Created: `<workspace-root>\audit-outputs\phase-0\foundation-architecture-audit.md` (this file, the primary deliverable).
- Read (read-only): plan, both specs, decision log, resolution register, README, AGENTS.md, .gitignore, .env.papyr (path referenced, values never reproduced), scripts/check-docs-migration.sh, and the listed `papyr-reference/` files.
- Modified: nothing else. `papyr-reference/` remains unchanged (HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`, empty porcelain, exit 0).
- No implementation, dependency installation, build, server start, git write, VPS access, deployment, provider authentication, benchmark, or network operation was performed.
- Secret values in `.env.papyr` were not copied into this audit; rotation remains required before production use (DEC-017, DEC-176).
- A chat-only summary is insufficient; this file is the primary deliverable.

--- END OF AUDIT ---
