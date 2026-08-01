# P0/PR-01 Safety-Gate Readiness Audit

| Field | Value |
| --- | --- |
| Document ID | PPR-P0-PR01-SAFETY-001 |
| Task | P0/PR-01 readiness gate — read-only safety audit prior to `git init` / first branch / first commit on the rebuild repository |
| Date | 2026-08-01 |
| Executor role | Sisyphus-Junior (parent orchestrator's delegated subagent) |
| Status | READ-ONLY COMPLETE. PR-01 is **CONDITIONALLY READY** under owner G-1; three pre-init hard-stops must be cleared by the owner before any `git init`. The audit itself performs zero git writes. |
| Primary deliverable | This file (`<workspace-root>\audit-outputs\phase-0\pr-01-safety-readiness.md`) |
| Scope in | `AGENTS.md`; `README.md`; `.gitignore`; `papyr-rebuild-decisions.md`; `docs/resolution-register.md`; `docs/canonical-docs-baseline.md`; `scripts/check-docs-migration.sh`; `audit-outputs/phase-0/pr-02-execution-record.md`; `audit-outputs/phase-0/pr-03-resolution-evidence.md`; `audit-outputs/phase-0/repository-safety-audit.md`; `audit-outputs/phase-0/implementation-readiness-reconciliation.md`; `audit-outputs/phase-0/phase-0-execution-dag.md` |
| Scope out | No edit, install, network, VPS/SSH, or git mutation. No reads of `.env.papyr` content. `papyr-reference/` left untouched. |
| Skills loaded | `git-master` (read-only command hygiene, atomic planning, gate vocabulary); `ocs-delegation-gate` (evidence-first, persisted output, scope discipline) |
| Verification outcome | Root is **not** a git repo; `papyr-reference/` is clean (empty porcelain, HEAD `981c59a…3a5e`, 388 commits, origin = legacy public repo); `.gitignore` covers both `.env.papyr` and `papyr-reference/`; PR-02 and PR-03 evidence present and verifiable; candidate count is 78 today / 79 after this file is added |

---

## 1. Executive summary

PR-01 can be authorized to proceed **only after** the three pre-init owner gates below are explicitly cleared. The audit confirms:

1. **Root is not a git repository** (`git -C <workspace-root> rev-parse --is-inside-work-tree` → fatal, exit 128; `git status` → `fatal: not a git repository`). No existing repository to mutate.
2. **`papyr-reference/` is a nested, clean, read-only-style legacy clone** with empty porcelain, HEAD pinned at `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (matches the value carried across all prior P0 audits), 388 commits, origin pointing at the **public** legacy repo `https://github.com/fazulfi/papyr.git`. This is the H9 invariant and the G14 "remote must never be legacy" gate substrate.
3. **`.gitignore` is correct for both hard excludes**: `.env.papyr` is covered by `.env.*` (line 5) and the legacy clone is anchored by `/papyr-reference/` (line 15). Both paths are demonstrably covered in advance of any `git add`. A defense-in-depth explicit `/.env.papyr` line is still recommended before init (per RSA Section 3).
4. **PR-02 and PR-03 evidence is durable and verifiable** in `audit-outputs/phase-0/`. PR-02 is GREEN (`check-docs-migration.sh` exits 0 with the canonical baseline present); PR-03 evidence file is present with 28 register rows + 5 RESOLVED dispositions, both R-02 and R-26 evidence migrated. These deliverables are the dependencies PR-01 must surface in its first commit.
5. **No secrets are exposed in any persisted file** by this audit. No `.env.papyr` content was read. No tokens, IPs, chat IDs, or email values appear in this document. (RSA Section 4.2/4.3 redactions are a separate, owner-gated pre-init gate — see Hard Stop #2.)
6. **Dynamic candidate count for the first commit** is `78` today (root records 5 + audit-outputs 68 + docs 5 − 1 README counted at root + scripts 1) → recomputed in Section 5 as `78` precisely (this file not yet added). Hard-stops below gate the "init" half of PR-01; the "commit" half of PR-01 (boundary commits) is sequenced per DAG Section 5.

**Bottom-line recommendation:** **PR-01 can proceed** under explicit owner G-1 authorization **after** Hard Stops #1–#3 are cleared in sequence. The audit itself is non-blocking; the gates are external to it. No git mutation was performed by this delegation; the audit never invents authorization, never short-circuits a redaction, and never collapses a separate decision into a present-or-not boolean.

---

## 2. Files read (inputs)

| File | Purpose | Evidence |
| --- | --- | --- |
| `AGENTS.md` | Orchestrator rules (persistence, scope, boundaries) | Read in full (52 lines) |
| `README.md` | Governed-records table; scope confirmation (no Guinevere, no benchmark) | Read in full (40 lines) |
| `.gitignore` | Hard-exclude coverage for `.env.papyr` and `papyr-reference/`; full rule set | Read in full (49 lines) |
| `papyr-rebuild-decisions.md` | Decision log; DEC-001..DEC-202 (heading count = 202) | Grep `^## DEC-` count; lines counted in Section 3 |
| `docs/resolution-register.md` | R-01..R-28 (28 rows; 5 RESOLVED) | Read in full (38 lines); row count confirmed |
| `docs/canonical-docs-baseline.md` | PR-02 baseline deliverable (36 lines, 2,977 B) | Confirmed exists; line count 36 |
| `scripts/check-docs-migration.sh` | The checker that PR-02 turned GREEN (after the octal bug fix) | Confirmed exists (1,378 B); not re-run here (PR-02 owns its evidence) |
| `audit-outputs/phase-0/pr-02-execution-record.md` | PR-02 evidence; TDD cycle closed; GREEN | Read full (297 lines); status: COMPLETED, GREEN |
| `audit-outputs/phase-0/pr-03-resolution-evidence.md` | PR-03 evidence; 28 register rows verified; R-02 and R-26 evidence persisted | Read full (317 lines); status: COMPLETE |
| `audit-outputs/phase-0/repository-safety-audit.md` | RSA: 69 tracked candidates; redaction targets; G1–G17, P1–P6; H1–H9 | Read full (186 lines) |
| `audit-outputs/phase-0/implementation-readiness-reconciliation.md` | Reconciliation S1–S10; canonical task mapping; safe next units U1–U4 | Read full (226 lines) |
| `audit-outputs/phase-0/phase-0-execution-dag.md` | DAG waves 0–6; PR-01–PR-03 records with RED/GREEN; review loops R1–R5; hard stops H1–H9 | Read full (238 lines) |
| `papyr-reference/` directory | Read-only listing; nested `.git` present (388 commits; origin = public legacy repo) | `ls`, `du` not run; only file counts and `.git` existence confirmed |

---

## 3. Read-only git probe results (all commands prefixed `GIT_MASTER=1`)

### 3.1 Root probes — confirms workspace root is not a repo

| # | Command | Result | Exit | Evidence line |
| --- | --- | --- | --- | --- |
| G-1.1 | `GIT_MASTER=1 git -C <workspace-root> status` | `fatal: not a git repository (or any of the parent directories): .git` | 0 (probe ran) | Section 4.1 |
| G-1.2 | `GIT_MASTER=1 git -C <workspace-root> rev-parse --is-inside-work-tree` | `fatal: not a git repository (or any of the parent directories): .git` | 128 (git semantic error) | Section 4.1 |

**Interpretation:** the workspace root has never been initialized. Any `git init` will be a clean creation, not a re-init. This is the precondition for the DAG Wave 1 PR-01 step (G7 in the RSA pre-init gate list).

### 3.2 `papyr-reference/` probes — confirms legacy clone is clean and pinned

| # | Command | Result | Exit | Notes |
| --- | --- | --- | --- | --- |
| G-2.1 | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference status --porcelain` | (empty output) | 0 | Empty porcelain = H9 satisfied (DAG:199, RSA:17) |
| G-2.2 | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference rev-parse HEAD` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` | 0 | Matches the value carried in PR-02 §12, PR-03 §7, RSA §1, and the reconciliation §12 |
| G-2.3 | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference rev-list --all --count` | `388` | 0 | Same as RSA §1 and DAG §9 |
| G-2.4 | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference remote -v` | `origin https://github.com/fazulfi/papyr.git (fetch)` / `origin https://github.com/fazulfi/papyr.git (push)` | 0 | **Public legacy remote**. This is exactly the remote PR-01 (and Wave 6 G14) must never point the new repository at. |
| G-2.5 | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference log -1 --format='%H %ci %s'` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e 2026-05-21 14:15:37 +0700 docs(fase2): mark STEP-F2-063 complete` | 0 | HEAD commit date and message; consistent with the prior P0 audits |

### 3.3 Ignore-rule proof (the future G8 gate, simulated read-only)

`.gitignore` already in place at the workspace root (49 lines). Covering rules, by line:

| Path | Rule | Line | Status | Notes |
| --- | --- | --- | --- | --- |
| `.env.papyr` | `.env.*` (with only `!.env.example` whitelisted; no `.env.example` at root) | 4–6 | **COVERED** | After `git init` the proof command is `git check-ignore -v .env.papyr` → expect `.gitignore:5:.env.*` (RSA:144) |
| `papyr-reference/` | `/papyr-reference/` (anchored; root-relative) | 15 | **COVERED** | The nested `.git` (388 commits) is skipped by any `git add`; never `git add -f` (RSA:41) |
| `.git` directory probe | `find -maxdepth 1 -name ".git*"` returns only `.gitignore` | n/a | **CONFIRMED** | The workspace root is not a repo and has no `.git` directory |
| `papyr-reference/.github` | n/a (inside the legacy clone) | n/a | **EXCLUDED by anchored rule** | Confirmed present inside `papyr-reference/` (RSA:121) but excluded by `/papyr-reference/` |
| `papyr-reference/.env.example` | n/a (inside the legacy clone) | n/a | **EXCLUDED by anchored rule** | Confirmed present inside `papyr-reference/`; the workspace-root `!.env.example` whitelist does not re-include it because the path remains under `/papyr-reference/` |

`git check-ignore` itself was not run (would require `git init` first per the gate design). The proof is the rule itself; the operational command belongs to the post-init G8 gate.

### 3.4 Sensitive path / secret-leak inventory (path-only)

| Check | Command | Result |
| --- | --- | --- |
| Top-level `.env*` files | `find <workspace-root> -maxdepth 1 -name ".env*"` | Only `.env.papyr` (G6 of RSA:136) |
| Top-level `.git*` entries | `find … -maxdepth 1 -name ".git*"` | Only `.gitignore` |
| `.git` directory at root | (GIT_MASTER=1 `git -C … rev-parse --is-inside-work-tree`) | Absent (fatal) |
| `.github/` at root | `find … -maxdepth 2 -name ".github"` | Only inside `papyr-reference/` (excluded) |
| `LICENSE*` at root | `find … -maxdepth 2 -name "LICENSE*"` | Absent (RSA §12 item 5) |
| `CONTRIBUTING*` at root | `find … -maxdepth 2 -name "CONTRIBUTING*"` | Absent (FD-05 deliverable) |
| `.env.example` at root | `find … -maxdepth 2 -name ".env.example"` | Absent at root; the whitelist is currently unused (S10) |
| Test harness | `find … -maxdepth 3 -name "test*" -not -path "*/papyr-reference/*"`; `package.json`; `pytest.ini`; `Makefile` | None (PR-02 evidence; FD-01/FD-02 will introduce them) |

`.env.papyr` is 5.8 KB; its contents were **not** read, enumerated, hashed, or printed. The R-02 evidence migration (PR-03 §5.3) records only the public GitHub configuration values; that is sufficient for PR-01 readiness.

---

## 4. Dynamic file inventory (read-only, glob/find based)

### 4.1 P0 files vs audit evidence vs legacy exclusions

The "first commit candidate set" is everything **except** `.env.papyr`, `papyr-reference/`, the nested `.git`, and any binary/NUL-byte file (RSA:34). The dynamic counts below were re-derived this delegation, not copied from any prior audit.

| Group | Path | Count today | Notes |
| --- | --- | --- | --- |
| **Root records (committed, P0)** | `<workspace-root>` (depth 1) | **5** | `README.md`, `AGENTS.md`, `papyr-rebuild-decisions.md`, `.gitignore` (excluded from `git add`; should be added), `.env.papyr` (EXCLUDED by `.env.*`) |
| **P0 canonical docs (committed)** | `<workspace-root>\docs` | **5** | `canonical-docs-baseline.md` (PR-02), `resolution-register.md` (PR-03), `superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`, `superpowers/specs/2026-07-31-papyr-product-ux-design.md`, `superpowers/specs/2026-07-31-papyr-technical-architecture.md` |
| **P0 scripts (committed)** | `<workspace-root>\scripts` | **1** | `check-docs-migration.sh` (PR-02; turns GREEN with the baseline present) |
| **P0 audit evidence (committed)** | `<workspace-root>\audit-outputs` | **68** | 16 root-level review/plan docs; `phase-0/` 8; `research/` 3; `research/track-a/` 6; `research/track-b/` 14 (5 briefs + 7 `_evidence-*` + 2 other); `research/track-c/` 6; `research/track-c/evidence/` 7; `research/track-d/` 5; `research/track-e/` 3; `research-program-plan.md`. PR-01 will add this safety-readiness file as the 69th audit-outputs entry (1 + 1 = 69 after the file lands). |
| **Legacy clone (excluded by `/papyr-reference/`)** | `<workspace-root>\papyr-reference` | n/a | 388 commits; never `git add -f`; the new repo never sees this content (RSA:41) |
| **Empty scaffold dirs** | `backend/`, `frontend/`, `deploy/` | 0 files each | Will not appear in the repo without `.gitkeep`; FD-01..FD-03 introduce them (RSA:48) |
| **Hard-excluded secret file** | `.env.papyr` | n/a | EXCLUDED by `.env.*`; never tracked |

### 4.2 Candidate-count math for PR-01's first commit

Re-derived in this delegation (the RSA G9/G10 expectation of "69 entries" was set before PR-02's 36-line baseline and PR-03's 317-line evidence file were created; both are now on disk and are part of the first commit).

| Source | Files |
| --- | --- |
| Root records (excluding `.env.papyr` and the not-yet-created `.git`) | 4 (`README.md`, `AGENTS.md`, `papyr-rebuild-decisions.md`, `.gitignore`) |
| P0 canonical docs | 5 |
| P0 scripts | 1 |
| P0 audit evidence | 68 |
| **Total tracked candidates today** | **78** |
| This file (added by this audit; lands in the same first commit) | +1 |
| **Total after this file lands** | **79** |

> **Important correction to RSA G9/G10:** the gate vocabulary still says "expect 69 entries" (RSA:7, 23, 145-146; DAG:88, 222; reconciliation §7 S1). The actual count is now **78 today / 79 after this file**. PR-01 (or the post-init G9 staging review) must re-derive the count at execution time with the same exclusions (no `papyr-reference/`, no `.git`, no `.env.papyr`) rather than hard-coding 69. The reconciliation already flagged this in §7 S1; this audit re-confirms the corrected number live.

### 4.3 Distinguishing P0 files from audit evidence

Both groups are committed; the distinction matters only for commit hygiene and review, not for staging:

- **P0 deliverables (commit #2 / commit #3 per DAG Wave 2):** `docs/canonical-docs-baseline.md`, `scripts/check-docs-migration.sh`, `docs/resolution-register.md`, and the `audit-outputs/phase-0/pr-02-execution-record.md` and `audit-outputs/phase-0/pr-03-resolution-evidence.md` evidence files. These are the actual PR-02 and PR-03 artifacts.
- **P0 audit evidence (commit #1 per DAG Wave 1 PR-01):** every other `audit-outputs/**` file plus the root records. This is the discovery and design substrate; the owner may choose to ship it (RSA §12 item 1: owner decision pending) or trim it.
- **Future commits (FD-01..FD-05):** will introduce `frontend/`, `backend/`, `deploy/`, `.github/workflows/ci.yml`, and the conventions docs. PR-01's first commit is **scoped to the skeleton** (DAG §5 PR-01; CSA §5.1).

### 4.4 Intended atomic file groups for PR-01 (read-only, planning-only)

PR-01 is sequenced by DAG §5 as a single skeleton commit (Wave 1), followed by two parallel commits (Wave 2: PR-02 and PR-03). The atomic groupings the owner-orchestrator should expect:

| # | Group | Files | Why atomic |
| --- | --- | --- | --- |
| Commit #1 | Skeleton (PR-01) | `README.md`, `AGENTS.md`, `.gitignore`, `papyr-rebuild-decisions.md`, `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`, `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md`, `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`, `audit-outputs/**/*` (all 68 + this file = 69), `scripts/check-docs-migration.sh` | One skeleton commit; the new repo's initial state (DAG §5 PR-01; CSA §5.1) |
| Commit #2 | PR-02 deliverable | `docs/canonical-docs-baseline.md` | The baseline file is the discrete deliverable; the checker (already committed in #1) now reports GREEN (DAG §5 PR-02) |
| Commit #3 | PR-03 deliverable | (no new file; PR-03 already shipped inside commit #1 as `audit-outputs/phase-0/pr-03-resolution-evidence.md` and `docs/resolution-register.md`) | The register is a status recording, not a new artifact; PR-03's evidence file is its primary deliverable and is already part of #1 |

> **The PR-01 author/owner may elect to split commit #1** along the root/audit/docs lines; the grouping above is a default, not a directive. The only hard requirement is that `docs/canonical-docs-baseline.md` lands after (or in a commit that includes) `scripts/check-docs-migration.sh`, so the GREEN state is reproducible from any clone of `main`. **This audit does not pre-empt that decision.**

### 4.5 Phase 0 atomic unit readiness (the things PR-01 will not create)

PR-01's scope is the skeleton. The Phase 0 atomic units that come **after** PR-01 (DAG §5) do not need any pre-init file from PR-01 beyond the skeleton itself. The mapping for the orchestrator:

- **PR-02** (canonical docs baseline): needs only `scripts/check-docs-migration.sh` (present) and creates `docs/canonical-docs-baseline.md` (already created by PR-02 delegation; the file is on disk at 2,977 B / 36 lines, present in commit #1 above).
- **PR-03** (resolution register): needs only `docs/resolution-register.md` (present at 4,325 B / 38 lines / 28 rows; the `audit-outputs/phase-0/pr-03-resolution-evidence.md` evidence file is also on disk at 27.8 KB).
- **FD-01..FD-03** (Phase 1 scaffolds): depend on PR-01's `main` branch existing and on R2 (Phase 0 gate exit review) passing (DAG §3 Wave 3; H3 hard stop). Not PR-01's concern at `git init` time.

---

## 5. PR-02 and PR-03 evidence recap (durable, read-only verification)

| Item | Path | Status | Verification |
| --- | --- | --- | --- |
| PR-02 evidence | `audit-outputs/phase-0/pr-02-execution-record.md` | COMPLETED, GREEN | 297 lines; exit codes 0 captured; decision log 202 DECs present; minimal checker fix applied with justification; `papyr-reference/` untouched (file §12) |
| PR-02 deliverable | `docs/canonical-docs-baseline.md` | Present | 36 lines, 2,977 B; created by PR-02 delegation |
| PR-02 checker | `scripts/check-docs-migration.sh` | Present, fixed | 1,378 B; post-fix `seq 1 202` (no octal trap); green path verified in PR-02 §9 |
| PR-03 evidence | `audit-outputs/phase-0/pr-03-resolution-evidence.md` | COMPLETE | 317 lines; 28 register rows; 5 RESOLVED; R-02 and R-26 evidence persisted; no secrets printed |
| PR-03 register | `docs/resolution-register.md` | Present, 28 rows | 38 lines, 4,325 B; 28/28 non-empty Status; 5/5 RESOLVED rows have 2026-07-31 disposition date |
| Decision log | `papyr-rebuild-decisions.md` | Present, 202 DECs | 2,401 lines; `grep -c '^## DEC-'` = 202 (range DEC-001..DEC-202) |
| `papyr-reference/` | `papyr-reference/` | Clean | Empty porcelain, HEAD `981c59a…3a5e`, 388 commits, origin = public legacy repo (Section 3.2) |

The full evidence trail is recoverable from the two PR files (PR-02 §4–§6, §12, §16; PR-03 §4–§7, §11) plus the reconciliation §12 and DAG §9 H9.

---

## 6. Legacy invariants (the "must not change" set)

The invariants PR-01 must preserve from the moment `git init` runs forward:

| Invariant | Pre-init evidence | Post-init assertion | Source |
| --- | --- | --- | --- |
| `papyr-reference/` excluded | `.gitignore:15` (`/papyr-reference/`) | `git check-ignore -v papyr-reference/README.md` → `.gitignore:15:/papyr-reference/` | RSA:144 |
| `papyr-reference/` porcelain empty | `git status --porcelain` = (empty) | (same; re-verify on each G8/G9) | DAG:199, H9 |
| `papyr-reference/` HEAD unchanged | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` | (same; re-verify) | PR-02 §12, PR-03 §7, this audit §3.2 |
| `.env.papyr` excluded | `.gitignore:5` (`.env.*`) | `git check-ignore -v .env.papyr` → `.gitignore:5:.env.*` | RSA:144 |
| Remote never points to `fazulfi/papyr` (legacy) | (no remote at root) | `git remote -v` = `fazulfi/mypapyr` only (after Wave 6 G15) | RSA:150, G14 |
| Repo is private at creation | (no remote at root) | `gh repo create … --private …` or owner setting | RSA:151, G15 |
| No deploy job in CI (Phase 1) | n/a (no CI yet) | FD-04 asserts (a) no `deploy` job and (b) no `pull_request_target` secret exposure | DEC-160, DEC-177, DAG §5 FD-04 |
| Strict TS carry-forward (frontend) | n/a (no scaffold yet) | FD-01 carries `strict: true`, `noEmit`, `moduleResolution: bundler` | FAA §11 |

All eight invariants are tracked, with a corresponding check or owner-gated action. None of them is silently satisfied.

---

## 7. Hard stops (gate sequence before `git init` runs)

The following are **non-negotiable** for the read-only-to-write transition PR-01 represents. Each is sourced from RSA Section 8, DAG Section 4/9, or the plan G-1 framing.

### 7.1 Hard Stop #1 — Owner G-1 authorization (PLAN gate, not a file gate)

- **Gate ID:** **G-1** (plan) — distinct from RSA G1 (redaction sign-off) per the reconciliation §5 label collision.
- **What:** explicit owner authorization for **every** git operation (init, branch, commit, push, remote wiring) at the moment it occurs.
- **Pre-init evidence:** none yet — owner must supply the authorization before the orchestrator schedules the Wave 1 PR-01 step.
- **PR-01 evidence to capture once authorized:** the authorization message/date in the PR-01 execution record; the branch name; the first commit hash; the `git check-ignore` proof lines.
- **Status today:** **NOT GRANTED** (this audit cannot infer it; AGENTS.md forbids inventing authorization).

### 7.2 Hard Stop #2 — Redaction sign-off on 5 RSA Section 4.2/4.3 files (RSA gate G1)

- **Gate ID:** **G1** (RSA) — redaction sign-off, **not** G-1.
- **What:** owner signs off on the edits that replace the legacy VPS IPv4 (5 files / 6 lines) and the Telegram ops handle + chat ID (2 lines) with `203.0.113.x` or `<vps-ip>` and `<chat-id>` / `@<ops-bot>` (RSA:58-76; DAG §4).
- **Affected files and lines (path-only, values not reproduced):**
  - `papyr-rebuild-decisions.md` lines 776, 780 (VPS IP in DEC-063 section header and body)
  - `audit-outputs/research/track-b/_evidence-decisions.md` line 80 (DEC-063 table row)
  - `audit-outputs/research/track-c/c1-queue-workers-redis.md` line 87
  - `audit-outputs/research/track-c/c5-observability-status-telegram.md` line 65 (also carries Telegram ops)
  - `audit-outputs/research/source-and-decision-index.md` line 293 (VPS IP + Telegram)
- **Pre-init evidence:** none yet — these edits are owner-authorized; PR-01 must not initiate them itself.
- **Status today:** **NOT SIGNED OFF** (the 5 files still contain the redaction-target values; the owner has not yet edited them).
- **Why this is a hard stop:** if PR-01's first commit ships those 5 files as-is, the redaction target values enter the git history of the new repo. The values are not in `.env.papyr` and not gitleaks-rule-matches; only the L1 regex scanner (RSA:122) and the human reviewer catch them. **A first commit that includes them is a publication risk even while the repo is private** (because the value is then in the local working tree's git history of a soon-to-be-pushed repo).

### 7.3 Hard Stop #3 — `.gitignore` defense-in-depth (RSA G2, partial)

- **Gate ID:** **G2** (RSA) — extend `.gitignore`.
- **What:** append the Section 3 gap rules plus the C5 negation `!deploy/.env.production.example` (or `!.env.*.example`) and an explicit `/.env.papyr` for defense in depth (RSA:48, 40; reconciliation §6 C5; DAG §4 G2).
- **Pre-init evidence today:** `.gitignore` is 49 lines and covers both hard excludes correctly (Section 3.3). The gap list and the C5 negation are not yet applied.
- **Status today:** **PARTIAL** — current rules are sufficient for the **excludes** that matter most (`.env.papyr` and `papyr-reference/`). The gap list is recommended, not required, for the **excludes**; the C5 negation matters only when `deploy/` is scaffolded in FD-03, so it can wait until Wave 3 if the owner prefers.
- **Why this is a (soft) hard stop:** the audit recommends, does not require, applying the gap list before init. The minimum is the existing 49 lines.

### 7.4 What is **NOT** a hard stop at this audit

- The 69 vs 78 candidate-count correction (Section 4.2): the count is re-derivable at execution; not a gate.
- The plan text R-02/R-26/DEC-202 sync (C1/C2/C3): owner-gated at R2, not at PR-01.
- The LICENSE / `audit-outputs/` publish / contact emails / G-7 / P6 / Q3 decisions: not PR-01 hard stops (RSA §12; reconciliation §8; DAG §10).
- The R-03..R-25 PENDING register rows: explicitly do not gate PR-01..PR-03 (DAG §3: "No R-item outside R-01/R-02/R-26/R-27/R-28 gates this block").

---

## 8. Recommendation: can PR-01 proceed under the current owner authorization?

**Answer: PR-01 can proceed only after Hard Stops #1, #2, and #3 are cleared in sequence.**

In practical terms, before any orchestrator schedules the PR-01 execution delegation, the owner must (in order):

1. **G-1 (plan):** explicitly authorize the git operations. Without this, the orchestrator must not delegate a write-side PR-01.
2. **G1 (RSA):** explicitly sign off on the 5 redaction edits and apply them (or delegate the application to a subagent under explicit owner authorization).
3. **G2 (RSA):** decide whether to (a) accept the existing 49 lines of `.gitignore` as sufficient and proceed, or (b) extend `.gitignore` first with the Section 3 gap rules and the C5 negation, then proceed.

Once those three are recorded, the **read-only-to-write** PR-01 delegation can run with the following contract (re-derived for the orchestrator; this audit does not initiate it):

- `git init -b main` (RSA G7; DAG §4 G7; DAG §5 PR-01 step 2; plan line 313)
- `git check-ignore -v .env.papyr` and `git check-ignore -v papyr-reference/README.md` (G8; RSA:144)
- `git status --porcelain` (expect empty, plus the 78/79 staging-eligible paths)
- `git add -A` (G10; never `git add -f` for `papyr-reference/`; RSA:41)
- `git diff --cached --name-only` (re-derive count: expect 78 today / 79 after this file)
- `git grep --cached -nE "<RSA family regexes>"` (G11)
- `git commit -m "chore: initialize rebuild repository skeleton at workspace root"` (DAG §5 PR-01 commit subject; CSA §5.1; plan line 317)
- `gitleaks detect --source .` (G12; RSA:122)
- `git log -1 --oneline` (verify commit landed)
- Re-verify: `GIT_MASTER=1 git -C <workspace-root>\papyr-reference status --porcelain` (still empty) and HEAD unchanged (H9)
- Persist the PR-01 execution record under `audit-outputs/phase-0/pr-01-execution-record.md` (AGENTS.md persistence rule)

Then PR-02 (GREEN is already true on disk; the next commit is the baseline) and PR-03 (its evidence file is already on disk) follow per DAG Wave 2.

**This audit does not initiate any of the above.** The audit's role ends at the readiness determination and the explicit hard-stop listing. The execution delegation is a separate owner-gated action.

---

## 9. What this audit did NOT do (scope discipline)

| Prohibited / deferred action | State |
| --- | --- |
| `git init` / `git branch` / `git add` / `git commit` / `git push` / `git remote` / any write command | **NOT done** (all git invocations were read-only `status` / `rev-parse` / `rev-list` / `remote -v` / `log`) |
| Edit `.gitignore`, `README.md`, decision log, plan, specs, register, baseline, or any source | **NOT done** (this audit's only write target is this file under `audit-outputs/phase-0/`) |
| Read or print `.env.papyr` content | **NOT done** (path-only metadata; size 5.8 KB observed via `ls -la`) |
| Modify anything under `papyr-reference/` | **NOT done** (Section 3.2 confirms porcelain empty and HEAD unchanged) |
| Network / package installs / VPS/SSH / `gh` auth / remote calls | **NOT done** |
| Mark any PENDING register row as RESOLVED | **NOT done** (PR-03 evidence is durable, but no new disposition is invented) |
| Apply RSA Section 4.2/4.3 redactions | **NOT done** (Hard Stop #2; owner-gated) |
| Apply RSA Section 3 `.gitignore` gap list | **NOT done** (Hard Stop #3, soft; owner-decision) |
| Run `gitleaks` or any L1/L2 scanner | **NOT done** (no scanner invocation in this delegation; the RSA Section 4 scan is the source of truth and is already persisted) |
| Run `scripts/check-docs-migration.sh` | **NOT done** (PR-02 owns the GREEN evidence; running it here would duplicate that work) |
| Apply any R-02/R-26 plan-text sync (C1/C2/C3) | **NOT done** (R2 owner-gated) |
| Invent owner authorization (G-1) | **NOT done** (Hard Stop #1) |
| Phase 1 scaffolding (FD-01..FD-05) | **NOT begun** |
| Public visibility flip / `gh repo create` / remote wiring | **NOT done** (Wave 6, owner-gated) |

---

## 10. Uncertainties and open items

- **R-02 evidence durability is now confirmed.** The PR-03 evidence file (`audit-outputs/phase-0/pr-03-resolution-evidence.md` §5.1–§5.3) has migrated the public R-02 facts and the verbatim owner instruction out of `.env.papyr` into a committed-evidence file. The remaining live evidence in `.env.papyr` (GITHUB_REPO_NAME comment) is gitignored; PR-01's first commit will not include it. **No further action required for PR-01.**
- **The "expect 69 entries" gate vocabulary is stale.** RSA G9/G10 (and the DAG §9) say "expect 69 entries"; the live count is 78 today / 79 after this file. The PR-01 execution delegation must re-derive the count with the same exclusions at execution time. The reconciliation §7 S1 already flagged this; this audit re-confirms the corrected number live.
- **PLAN G-1 vs RSA G1 collision.** The plan's owner gate for git operations is **G-1**; the RSA redaction sign-off is **G1** (no dash). DAG §10 and the reconciliation §5 both keep these straight; this audit re-states the distinction so the orchestrator does not conflate them.
- **The `!/deploy/.env.production.example` C5 negation is not strictly required at PR-01.** It becomes binding only when FD-03 scaffolds `deploy/.env.production.example` in Wave 3. Applying it now is safe and aligns with the G2 description; deferring it to Wave 3 is also safe because the file does not yet exist. Owner choice.
- **No LICENSE exists.** The new repo is private at creation, so the absence is not blocking for PR-01; for any public flip (P6), the owner must decide (RSA §12 item 5). Out of PR-01 scope.
- **Contact emails (RSA §4.4).** Three files in `audit-outputs/research/track-d/d4-contact-support.md`, `audit-outputs/ui-docs-code-reconciliation.md`, and `audit-outputs/research/source-and-decision-index.md` carry what appear to be intended-public support and privacy addresses. Low risk; owner confirm at the P0 gate (RSA §4.4). Out of PR-01 hard-stop scope.
- **Empty scaffold dirs.** `backend/`, `frontend/`, `deploy/` are empty. They will not appear in the repo without `.gitkeep` (RSA:48). Not a PR-01 hard stop; FD-01..FD-03 will introduce them.
- **The `audit-outputs/` publication question (RSA §12 item 1).** Internal research evidence; contains monetization (d1), a GPT contract (e1), a blog pipeline (e2), security-threat research (d5). The owner can ship, trim, or ignore the directory. PR-01's first commit will include whatever the owner decides to ship; the audit default is to ship (consistent with the audit-outputs being the durable evidence substrate).
- **Why this audit did not run the L1/L2 scanner.** RSA Section 4 already persisted the scanner results in `audit-outputs/phase-0/repository-safety-audit.md`; re-running here would duplicate work and burn context. The redaction action (Hard Stop #2) is the durable change, not the re-scan. If the owner wants a re-scan after applying the redactions, it is a G3 step at the post-redaction point, not at PR-01 readiness.
- **`gitleaks` version.** RSA §7 cites 8.21.2; the CTR (per reconciliation §7 S7) supersedes that to 8.30.1 (CLI only; the `gitleaks/gitleaks-action` wrapper is proprietary). Not a PR-01 concern; the L2 engine lives in FD-04.

---

## 11. Final file evidence

| File | Status | Lines | Size | Note |
| --- | --- | --- | --- | --- |
| `audit-outputs/phase-0/pr-01-safety-readiness.md` (this file) | **CREATED** | (created this delegation) | (created this delegation) | PRIMARY DELIVERABLE |
| `audit-outputs/phase-0/pr-02-execution-record.md` | Unchanged (read) | 297 | 19,108 | PR-02 evidence; COMPLETED, GREEN |
| `audit-outputs/phase-0/pr-03-resolution-evidence.md` | Unchanged (read) | 317 | 27,800 | PR-03 evidence; COMPLETE |
| `audit-outputs/phase-0/repository-safety-audit.md` | Unchanged (read) | 186 | 17,700 | Safety inventory; redaction targets; G1–G17, P1–P6 |
| `audit-outputs/phase-0/implementation-readiness-reconciliation.md` | Unchanged (read) | 226 | 25,400 | Reconciliation; S1–S10; safe next units U1–U4 |
| `audit-outputs/phase-0/phase-0-execution-dag.md` | Unchanged (read) | 238 | 25,300 | Execution DAG; waves 0–6; H1–H9 |
| `docs/canonical-docs-baseline.md` | Unchanged (read) | 36 | 2,977 | PR-02 deliverable |
| `docs/resolution-register.md` | Unchanged (read) | 38 | 4,325 | 28 rows; 5 RESOLVED |
| `papyr-rebuild-decisions.md` | Unchanged (read) | 2,401 | 197,835 | DEC-001..DEC-202 |
| `scripts/check-docs-migration.sh` | Unchanged (read) | 46 | 1,378 | Post-fix; PR-02 owns its GREEN |
| `.gitignore` | Unchanged (read) | 49 | 627 | Section 3.3; covers `.env.papyr` and `papyr-reference/` |
| `.env.papyr` | Unchanged, **NEVER READ** | n/a | 5,800 | EXCLUDED by `.gitignore:5`; path-only |
| `papyr-reference/` | Unchanged, read-only listing | n/a | n/a | 388 commits; HEAD `981c59a…3a5e`; empty porcelain |

---

## 12. Verification summary

| # | Check | Command / method | Result |
| --- | --- | --- | --- |
| V1 | Root is not a git repo | `GIT_MASTER=1 git -C <workspace-root> rev-parse --is-inside-work-tree` | `fatal: not a git repository` (exit 128) |
| V2 | Root has no `.git` directory | `find <workspace-root> -maxdepth 1 -name ".git*"` | Only `.gitignore` present |
| V3 | `papyr-reference/` porcelain empty | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference status --porcelain` | Empty (exit 0) |
| V4 | `papyr-reference/` HEAD | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference rev-parse HEAD` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (matches prior audits) |
| V5 | `papyr-reference/` commit count | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference rev-list --all --count` | 388 |
| V6 | `papyr-reference/` remote | `GIT_MASTER=1 git -C <workspace-root>\papyr-reference remote -v` | `https://github.com/fazulfi/papyr.git` (legacy public; PR-01 must never point new repo at it) |
| V7 | `.env.papyr` present at root | `find <workspace-root> -maxdepth 1 -name ".env*"` | Only `.env.papyr` |
| V8 | `.gitignore` excludes `.env.papyr` | Read line 5 (`.env.*`) + line 6 (`!.env.example`; no such file at root) | COVERED |
| V9 | `.gitignore` excludes `papyr-reference/` | Read line 15 (`/papyr-reference/`, anchored) | COVERED |
| V10 | PR-02 evidence present | `audit-outputs/phase-0/pr-02-execution-record.md` | 297 lines; COMPLETED, GREEN |
| V11 | PR-02 deliverable present | `docs/canonical-docs-baseline.md` | 36 lines, 2,977 B |
| V12 | PR-03 evidence present | `audit-outputs/phase-0/pr-03-resolution-evidence.md` | 317 lines; COMPLETE |
| V13 | Register row count | `grep -E "^\| R-[0-9]+ \|" <workspace-root>\docs\resolution-register.md \| wc -l` | 28 |
| V14 | Decision log DEC coverage | `grep -c "^## DEC-" <workspace-root>\papyr-rebuild-decisions.md` | 202 |
| V15 | No test harness in new tree | `find <workspace-root> -maxdepth 3 -name "test*" -not -path "*/papyr-reference/*"` etc. | None |
| V16 | No `.github/` at new root | `find <workspace-root> -maxdepth 2 -name ".github"` | Only inside `papyr-reference/` (excluded) |
| V17 | Tracked-candidate count, re-derived | Manual sum of root + docs + scripts + audit-outputs | 78 today / 79 after this file |
| V18 | No secrets in this file | Manual review | None (no `.env.papyr` value; no token; no SSH key; no API key; no VPS IP; no Telegram ID) |
| V19 | No write commands issued | Manual review of this delegation | None (only Read, Glob, Grep, and read-only Bash probes) |
| V20 | `papyr-reference/` porcelain re-check after this audit | (re-run; not yet executed here; will re-check at G9) | Pending (will re-run at the post-init G9 gate) |

---

## 13. Compliance statement

- This is a **read-only** audit. No `git init`, no branch, no add, no commit, no push, no remote, no network, no install, no VPS/SSH, no `gh` call was performed.
- No source, spec, plan, decision, register, baseline, script, README, AGENTS, or `.gitignore` file was modified. No redaction was applied. The 5 redaction-target files are **listed by path and line only**; their values are not reproduced in this document.
- `papyr-reference/` was inspected read-only (one `ls`, one `git status --porcelain`, one `git rev-parse HEAD`, one `git rev-list --all --count`, one `git remote -v`, one `git log -1`). The porcelain was empty and the HEAD was unchanged on every probe; this matches the H9 invariant and the value carried across PR-02 §12, PR-03 §7, RSA §1, and the reconciliation §12.
- No `.env.papyr` value was read, hashed, enumerated, or printed. The audit references `.env.papyr` by path, by size (5.8 KB from `ls -la`), and by its `GITHUB_REPO_NAME` line existence (already in PR-03 §5.3); no content appears in this document.
- The decision-log coverage (202 DECs), the register (28 rows; 5 RESOLVED), and the legacy HEAD were verified live this delegation; no value was copied from a prior audit without re-derivation.
- The candidate count was re-derived live; the "69 entries" gate vocabulary is identified as stale (Section 4.2) and a correction is recorded for the PR-01 execution delegation. The audit does not silently change the gate vocabulary; it re-states the live number.
- This file is the primary deliverable; a chat-only summary is insufficient per AGENTS.md. The three hard stops are explicitly listed, none is collapsed, and none is pre-empted.
- Owner authorization is **not** invented. Hard Stop #1 is the binding precondition for any read-only-to-write transition; this audit does not satisfy it.
