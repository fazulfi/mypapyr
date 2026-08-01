# FD-05 Execution Record — Root Tooling & Contribution Conventions Docs

Unit: Phase 0, FD-05 (root tooling conventions / docs)
Workspace root: `<workspace-root>`
Date executed: 2026-08-01

## Skills loaded + why

- `context-grooming` — task is multi-step (RED → GREEN → deliverable record) with explicit evidence capture; keep todos disciplined and plan state single-source.
- `ocs-delegation-gate` — task is documentation domain (Markdown structure / link integrity); explicit skill mapping required even though no subagents were used (the three-author scope is a single self-execution pass).
- `ocs-markdown-autofix` — `ocs-markdown-autofix` workflow was applied as structural checks because the repo root has **no** `package.json` with a `bun run lint:md` script (per the task instructions). No fake PASS was claimed; the substitution is documented below.

## RED evidence (commands + outputs captured)

All commands run from the workspace root with `GIT_MASTER=1` prefix on every git invocation. Output trimmed to the relevant lines.

### Legacy invariant before edits

```text
$ GIT_MASTER=1 git -C "<workspace-root>/papyr-reference" status --porcelain
(empty)

$ GIT_MASTER=1 git -C "<workspace-root>/papyr-reference" rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
```

Result: papyr-reference working tree clean, HEAD matches the expected `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`.

### Baseline file shape before edits

```text
$ wc -l "<workspace-root>/README.md"
41 <workspace-root>/README.md
```

```text
$ ls "<workspace-root>/CONTRIBUTING.md" "<workspace-root>/docs/plan/index.md"
ls: cannot access '<workspace-root>/CONTRIBUTING.md': No such file or directory
ls: cannot access '<workspace-root>/docs/plan/index.md': No such file or directory
```

Result: README is the 41-line minimal skeleton; CONTRIBUTING.md and `docs/plan/index.md` are absent (confirmed fail-state before GREEN).

### Initial grep (RED — reference not yet resolved from docs/plan/index.md)

```text
$ grep -rn 'docs/superpowers/plans' "<workspace-root>/docs/"
docs/resolution-register.md:5:Reference: `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` §6 (Owner Resolution Register).
docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md:69:... (master plan body, line 69) ...
docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md:424:... (master plan FD-05 description) ...
docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md:427:- [ ] **Step 2: Verify internal links.** Run: `grep -rn 'docs/superpowers/plans' docs/`. ...
```

Result: the master plan reference does NOT yet resolve from `docs/plan/index.md` (file does not exist). RED state confirmed.

## Files created

Three files, all under the workspace root. Sizes verified with `wc -c`.

| Path | State | Bytes | Lines (wc -l) |
| --- | --- | --- | --- |
| `README.md` | REPLACED (was 41-line minimal skeleton) | 4,803 | (see file) |
| `CONTRIBUTING.md` | NEW | 5,373 | (see file) |
| `docs/plan/index.md` | NEW | 1,832 | (see file) |

Directory `docs/plan/` was created implicitly as part of writing `docs/plan/index.md`.

## GREEN evidence

### Re-run of the grep — reference now resolves from docs/plan/index.md

```text
$ grep -rn 'docs/superpowers/plans' "<workspace-root>/docs/"
docs/plan/index.md:16:Each phase in the master plan MAY be expanded into its own plan file under `docs/superpowers/plans/` following the master's template and gates. ...
docs/resolution-register.md:5:Reference: `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` §6 ...
docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md:69:...
docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md:424:...
docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md:427:...
```

Result: `docs/plan/index.md:16` now resolves the `docs/superpowers/plans/` reference. The line was added intentionally to satisfy Step 2 of the master plan's FD-05 acceptance.

### Link target exists (relative path verification)

```text
$ ls -la "<workspace-root>/docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md"
-rw-r--r-- 1 faizz 197609 138912 Jul 31 22:32 .../2026-07-31-papyr-rebuild-implementation-plan.md
```

Result: relative link target file exists. Size 138,912 bytes ≈ 135.7 KiB, consistent with the task-supplied "~135.7K" figure.

### Relative-link verification table (every relative link from the three new docs)

| Source | Relative target | Resolved path | Exists |
| --- | --- | --- | --- |
| `README.md` | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | yes |
| `README.md` | `docs/plan/index.md` | `docs/plan/index.md` | yes |
| `README.md` | `CONTRIBUTING.md` | `CONTRIBUTING.md` | yes |
| `CONTRIBUTING.md` | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | yes |
| `CONTRIBUTING.md` | `docs/plan/index.md` | `docs/plan/index.md` | yes |
| `docs/plan/index.md` | `../superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | yes |
| `docs/plan/index.md` | `../canonical-docs-baseline.md` | `docs/canonical-docs-baseline.md` | yes |
| `docs/plan/index.md` | `../resolution-register.md` | `docs/resolution-register.md` | yes |
| `docs/plan/index.md` | `../../CONTRIBUTING.md` | `CONTRIBUTING.md` | yes |

All relative links resolve to real files on disk.

### Legacy invariant after edits

```text
$ GIT_MASTER=1 git -C "<workspace-root>/papyr-reference" status --porcelain
(empty, exit 0)

$ GIT_MASTER=1 git -C "<workspace-root>/papyr-reference" rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
```

Result: papyr-reference unchanged. No files in `papyr-reference/` were touched, edited, copied, or read beyond the read-only git status/rev-parse calls explicitly authorized in this unit.

## Content coverage check

Every topic the unit required is documented in the new files:

- Task/feature branch naming convention (feat, fix, docs, phase-0, chore, refactor, test, security, ci) — `CONTRIBUTING.md` § "Branch naming".
- Commit message prefixes (feat, fix, docs, chore, test, ci, refactor, security) — `CONTRIBUTING.md` § "Commit messages" + `README.md` does not enumerate, `CONTRIBUTING.md` is authoritative.
- TDD requirement (RED → GREEN → REFACTOR, tests paired with code, coverage floor 80%) — `CONTRIBUTING.md` § "Test-driven development (TDD) requirement" + CI summary in `README.md`.
- Phase-plan expansion rule — `CONTRIBUTING.md` § "Phase-plan expansion rule" + `docs/plan/index.md` § "Phase-specific plans" (table intentionally empty at start of Phase 0).
- README references master plan via relative path `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` — confirmed (see GREEN grep).
- `docs/plan/index.md` links master plan + `docs/canonical-docs-baseline.md` + `docs/resolution-register.md` — confirmed (relative-link table above).
- README includes project name (Papyr), one-line purpose, monorepo layout (frontend/ Next.js, backend/ FastAPI, deploy/ compose skeleton, `.github/workflows/ci.yml`, docs/, scripts/), local dev quickstart (frontend `npm ci`/`npm run dev`/`npm test`/`npm run lint`/`npm run build`; backend venv + `pip install -r requirements.txt -r requirements-dev.txt` + `pytest` + `ruff`), CI overview (lint/test/build/coverage≥80%/trivy/gitleaks, NO deployment in CI), and "Limitations / no guarantees" note (no legal compliance, certification, guaranteed malware removal, privacy sufficiency, or legal sufficiency claimed).
- All three files are public-safe and factual. No `.env.papyr` values were read, printed, copied, or referenced; only variable *names* would appear in env-example copy, and this unit did not modify `.env.production.example`.

## Markdown check note (ocs-markdown-autofix substitution)

`bun run lint:md` and `bun run lint:md:fix` were NOT executed because there is no `package.json` at the repo root that defines those scripts. Per the unit's explicit instruction, no fake PASS was claimed. As the substitute for the missing lint pass, the following structural checks were applied manually to the three new files:

- Headings are sequential (`#`, `##`, `###`) without skipped levels in the new files.
- List items in tables are aligned and contiguous.
- All relative links target real files (see relative-link table).
- No trailing-whitespace-only lines introduced.
- Code fences opened and closed correctly in every block.
- `papyr-reference/` is referenced as read-only in all three files; no reference to live edits.

Any pre-existing markdown debt outside the scope of this unit (e.g. inside `docs/superpowers/specs/*.md`) is unchanged by this unit and is not hidden; it remains an explicit, owner-gated follow-up.

## Scope discipline statement

- Touched paths (this unit):
  - `README.md` — replaced.
  - `CONTRIBUTING.md` — created.
  - `docs/plan/index.md` — created (with `docs/plan/` directory created implicitly).
- NOT touched (verified): `frontend/`, `backend/`, `deploy/`, `.github/`, `scripts/`, `papyr-reference/`, `docs/superpowers/specs/`, `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`, `docs/canonical-docs-baseline.md`, `docs/resolution-register.md`, `papyr-rebuild-decisions.md`, `AGENTS.md`, any `*.env*` file (including `.env.papyr` and `.env.production.example`).
- No git add / commit / push / init / remote operations were executed. Only read-only `git status --porcelain` and `git rev-parse HEAD` on the `papyr-reference/` clone.
- No `.env.papyr` value was read, printed, copied, or referenced. No benchmark program was introduced.

## Uncertainties

- The master plan line 427 marks Step 2 ("Verify internal links") as a `- [ ]` checkbox. This unit performed the command and verified the GREEN result; flipping that checkbox to `[x]` is a master-plan edit, which is intentionally NOT made in FD-05 (master-plan edits are owner-gated and belong to a later phase).
- The phase-specific plan table in `docs/plan/index.md` is intentionally empty at the start of Phase 0. A unit author later in Phase 0 (or later phases) may populate it as authorized.
- The repo root has no `bun run lint:md` script, so the strict `ocs-markdown-autofix` pass criteria could not be met literally. The substitute structural checks are documented above; a future unit that adds a root-level lint harness could close that gap.