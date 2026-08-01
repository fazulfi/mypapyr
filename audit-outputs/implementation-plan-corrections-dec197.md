# Papyr Rebuild: Master Implementation Plan Corrections Evidence (DEC-197)

| Field | Value |
|---|---|
| Document ID | PPR-PLN-CORR-001 |
| Title | Evidence record for the deterministic corrections applied to the master implementation plan after the independent cross-review |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent; correction task continuing the plan authoring session) |
| Status | Complete; all 2 HIGH, 8 MEDIUM, and 3 LOW findings corrected deterministically; no owner decision was made |
| Governing inputs | `audit-outputs/implementation-plan-cross-review-dec197.md` (PPR-PLN-CR-001, verdict CONDITIONAL PASS); `AGENTS.md`; decision log DEC-001..DEC-197; both approved specifications; the prior authoring evidence `audit-outputs/implementation-plan-authoring-dec197.md` |
| Primary deliverables | corrected plan `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (1,437 lines after correction); this evidence file |
| Task constraints | Read, search, and edit only the master plan; write only the assigned evidence file; read-only git status on `papyr-reference`; no owner decisions; no implementation, installs, builds, servers, VPS access, provider authentication, deployment, commits, pushes, or remote operations |

---

## 1. Method

1. Read `AGENTS.md` in full (governing rules).
2. Read the complete cross-review `audit-outputs/implementation-plan-cross-review-dec197.md` in full (238 lines; 2 HIGH, 8 MEDIUM, 3 LOW findings).
3. Re-verified the review's baseline facts against the plan before editing: 1,417 lines, 313 line-start checkboxes, 27 R-rows, `papyr-reference/` clean at HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`.
4. Applied every deterministic correction top-to-bottom via the edit tool, without making any owner decision. Where a correction could be satisfied in two ways, the option that keeps the plan's task IDs, R-row numbering, and phase numbering stable was preferred (recorded per finding).
5. Re-ran the full manual verification battery (Section 6) against the corrected plan.
6. Re-verified `papyr-reference/` git cleanliness after all edits.
7. Wrote this evidence file.

The prior authoring evidence `implementation-plan-authoring-dec197.md` describes the pre-correction state and is left unchanged as a historical record; this file records the corrections.

## 2. Findings and exact edits applied

### 2.1 HIGH-1: Category-A engine and queue selections elevated without DEC-057 approval

**Edits applied (all in `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`):**

1. Tech Stack relabeled: the queue mechanism, every PDF/image engine (pdf-lib, pdf.js, pikepdf, img2pdf, Pillow, pypdfium2), and the CI provider are now marked as proposals under R-28 or R-02; Ghostscript remains normative under DEC-195 ("approved").
2. Proposed tree: `queue/` line now reads "queue per R-28 (proposal: Redis Streams)"; `.github/workflows/` line now reads "contingent on R-02"; `deploy/runbook-vps.md` line reworded (see LOW-13); a `scripts/` directory line was added to the tree.
3. Added resolution row R-28 "Queue mechanism and PDF/image engine matrix (X2 A-2..A-5, A-7; X1 A1/A3-A6/C1)" with stop condition "Owner approves the matrix before BE-04, BE-05, TL-03..TL-06, and SEC-02".
4. Added Section 6.1 "Engine and queue matrix (R-28)": one table with seven rows (queue data structure; Merge/Split browser happy path; Merge/Split server fallback and sanitization engine; JPG to PDF server engines; PDF to JPG server engine; PDF to JPG and page-count browser engine; image decode and browser JPG to PDF), each row carrying the proposed approach from the category-A findings, accepted risks, scope, and material conditions as DEC-057 requires. The row explicitly states that nothing in the matrix is an accepted decision until the owner approves R-28.
5. BE-05: "Redis Streams consumer-group queue (C1 brief)" changed to "the server-job queue per the approved R-28 disposition (proposal: Redis Streams consumer groups, C1 brief)"; Consumes adds R-28.
6. SEC-02: "pikepdf-based sanitization" and "the pikepdf sanitization API (A3 brief)" changed to R-28-approved-engine phrasing; Consumes adds R-28.
7. TL-03: "pdf-lib ... and pikepdf server fallback" changed to R-28-approved-engine phrasing in Produces.
8. TL-04: "browser-first pdf-lib with pikepdf server fallback" changed to R-28-approved-engine phrasing in Produces.
9. TL-05: "(img2pdf plus Pillow per the A5 brief)" changed to "the R-28-approved server engines (proposal: img2pdf plus Pillow per the A5 brief)".
10. TL-06: "(pypdfium2 with explicit white fill per the A6 brief)" changed to "the R-28-approved server engine (proposal: pypdfium2 with explicit white fill per the A6 brief)".
11. R-row count claims updated everywhere: Global Constraints bullet, Section 5 prefix line, PR-03 steps 1 and 3 (expects 28 rows), Section 9.2 row 25.1-25.4, Section 10 check 2 (now "R-01 through R-28").
12. ClamAV remains gated under the existing R-10 (unchanged). Ghostscript remains normative under DEC-195 (unchanged). No engine selection was made by this correction; all are owner-resolution proposals.

### 2.2 HIGH-2: Phase-ordering DAG violation (SEC-01/SEC-02 after their consumers)

Chosen correction (review option 1): moved SEC-01 and SEC-02 into Phase 3 as early security prerequisites, rather than declaring them early in Phase 5.

1. Phase table: P3 renamed "Backend core and early security prerequisites: settings, queue, worker, task model, R2, cleanup, API contract, threat classification, sanitization"; P3 exit gate adds "SEC-01 and SEC-02 prerequisites verified". P5 renamed "Security and hardening: scanner, container hardening, Nginx enforcement, dependency maintenance"; P5 "Depends on" changed from "P3, P4" to "P3" (after the move, no Phase 5 task consumes a Phase 4 output); P5 exit gate changed to "scanner fail-closed behavior, container hardening, and Nginx enforcement verified".
2. Phase 3 heading, goal, gate entry, and gate exit updated to include the two prerequisites; gate entry adds R-28.
3. SEC-01 and SEC-02 task blocks moved from Phase 5 to Phase 3 (after BE-10, before Phase 4), retitled "(early security prerequisite)"; SEC-01 Produces extended with the scanner and sanitization interface contracts so TL-03/TL-04 fail-closed tests can consume stubs before the concrete scanner client lands in SEC-03.
4. Phase 5 heading/goal/gate updated: goal now "the maintained scanner, container hardening, Nginx enforcement, and dependency maintenance"; gate entry "Phase 3 complete (SEC-01 and SEC-02 prerequisites satisfied); R-10 and R-11 dispositions recorded"; gate exit "scanner fail-closed behavior, container hardening, and Nginx enforcement verified (DEC-192, DEC-162)".
5. Phase 4 gate entry now reads: "Phases 2 and 3 complete (including the SEC-01 threat-classification and SEC-02 sanitization prerequisites produced in Phase 3); R-03, R-04, R-05, R-06, R-14, R-17 dispositions recorded."
6. Task index rows reordered so SEC-01 and SEC-02 follow BE-10 and precede TL-01; TL-02/TL-03/TL-04 Consumes cells now name "SEC-01, SEC-02" instead of the aggregate "SEC".
7. TL-03 step 1 clarified that scanner-unavailable fail-closed tests run against the SEC-01 scanner interface with a stub.
8. TL-02 block Consumes line verified consistent ("TL-01, BE-03, BE-05, BE-06, SEC-02, R-04, R-05").

### 2.3 MEDIUM-3: DEC-024 precondition wording

Section 1 precondition rewritten: the owner must define the exact numeric 90-day targets and baseline windows as part of approving this plan; the approval record must include the R-27 disposition; until recorded, no phase may start. The misleading "gates Phase 10 and Phase 11 acceptance, not the foundational phases" sentence was removed. R-27 stop condition updated to match ("as part of plan approval; until recorded, no phase may start"). No targets were invented.

### 2.4 MEDIUM-4: R-15 stop condition and Phase 2 gate

R-15 stop condition changed to "Owner approves slug table and disposition map before SH-01 (route names) and SEO-01". Phase 2 gate entry changed to "Phase 1 complete; R-15 slug dispositions recorded (route names depend on them)".

### 2.5 MEDIUM-5: R-05 in the Phase 4 gate

Phase 4 gate entry now lists R-05 alongside R-03, R-04, R-06, R-14, R-17.

### 2.6 MEDIUM-6: PR-02 pytest before Python tooling

PR-02 rewritten as a dependency-free task: it creates `scripts/check-docs-migration.sh` (uses `cmp -s` for byte-identical spec copies and `grep` for DEC-001..DEC-197 ID presence), verifies FAIL before copy and PASS after, then commits. All pytest references removed from PR-02. The Section 3 tree now includes a `scripts/` directory (also required by the named check scripts in FD-04, SEC-04, SEC-06, OP-01, OP-03, OP-04, SEO-01, VL-03, VL-05, PO-01, PO-03).

### 2.7 MEDIUM-7: Unnamed verification commands

- OP-03: new script `scripts/check-telegram-relay.sh` in Files; Step 2 and Step 4 now run it with FAIL/PASS expectations.
- SEC-04: new script `scripts/check-compose.sh` in Files; Step 1 creates it, Step 2 runs it (FAIL), Step 4 runs it plus `docker compose -f deploy/docker-compose.yml config --quiet` (PASS, exit 0).
- VL-02: `frontend/package.json` added to Files (adds the `test:a11y` script and axe-core); Step 2 and Step 4 run `npm run test:a11y -- axe` with FAIL/PASS expectations.
- VL-04: `frontend/package.json` added to Files (adds the `test:perf` script and Lighthouse CI); Step 2 and Step 4 run `npm run test:perf -- lighthouse` with FAIL/PASS expectations.
- VL-03 (consistency extension of the same rule): contrast script named `scripts/check-contrast.sh` and added to Files; steps updated.

### 2.8 MEDIUM-8: CT-04 G-5 gating

CT-04 Step 3 amended: article generation runs "with each generation run executed under the G-5 owner gate (no authenticated gateway call is authorized by this plan)".

### 2.9 MEDIUM-9: G-1 vs DEC-048 auto-publishing

G-1 amended with a carve-out: "except the owner-approved blog automation pipeline under DEC-048, CT-03, and PO-04, whose gate-passing PRs auto-merge through the normal build path; activation of that workflow is owner-gated."

### 2.10 MEDIUM-10: GitHub Actions contingent on R-02

Tech Stack now reads "CI provider per R-02 (proposal: GitHub Actions, CI core gate only)". FD-04 Files/Interfaces note the workflow artifact is contingent on R-02, and Step 3 covers the alternative-provider case. PO-02 wording changed to "the CI provider workflow definitions (proposal: GitHub Actions)". The tree `.github/workflows/` line is marked "contingent on R-02".

### 2.11 MEDIUM-LOW-11: Traceability matrix gaps

- Section 9.3 "SEO, localization, and content" cluster now includes DEC-004 (marked "expanded by DEC-115 and DEC-118"), DEC-044, and DEC-046, with mappings extended to SH-07 and PT-03.
- Section 9.3 "UI and UX baseline" cluster now includes DEC-062, mapped to VL-02.
- New Section 9.3 row "Availability and failure isolation | DEC-163, DEC-167 | TL-01, BE-08, OP-02".
- Coverage note amended to mention the DEC-004 supersession note and the R-28 engine and queue matrix.
- Section 9.2 row 25.1-25.4 updated to "Section 6 (R-03..R-28)".
- Verified after edits: the plan cites every DEC-001 through DEC-197 and nothing outside the range (Section 6).

### 2.12 LOW-12: R-14 owner/implementer ambiguity

R-14 stop condition changed to a single owner confirmation: "Owner confirms the trusted-header setup before TL-05". The register remains an owner register; the implementation-time nature of the detail (X1 M9) is noted in the row's proposal text. This option was chosen over removing and renumbering the row to keep R-row numbering and every R-14 reference stable across the plan.

### 2.13 LOW-13: runbook wording

Tree line for `deploy/runbook-vps.md` reworded to: "canonical operations runbook (replaces the legacy `papyr-reference/docs/runbook-vps.md` as the operating reference; the legacy file is never modified)".

## 3. Findings deliberately not changed (preserved)

- R-01 remains unresolved with its original stop condition; the proposed root is still labeled a proposal.
- DEC-066 no-benchmark constraint, DEC-143 visual baseline, the DEC-060/DEC-197 approval block, all gates G-1..G-11, and all owner-approved decisions remain unchanged.
- FD-05 and PO-05 keep their 4-step documentation-task format (the review explicitly approved this, Section 4 item 4 of PPR-PLN-CR-001).
- Optional items O-1/O-2/O-3 from the task instruction: none exist in the review; nothing extra was applied.
- The prior authoring evidence file was not modified.

## 4. Material owner questions still required (not decided here)

1. **DEC-024 numeric 90-day targets and baseline windows** (R-27): mandatory as part of plan approval; until recorded, no phase may start (DEC-024; UX §20.6 item 5; arch §24.2).
2. **R-28 engine and queue matrix**: queue data structure and each PDF/image engine selection (pdf-lib, pdf.js, pikepdf, img2pdf, Pillow, pypdfium2) with accepted risks, scope, and material conditions, per DEC-057.
3. **R-01** repository root confirmation (unresolved, as before).
4. All other by-design resolution items R-02..R-27 dispositions at their stop conditions.
5. Plan approval itself (DEC-060, DEC-197).

## 5. Files touched by this correction

- Modified: `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (1,417 to 1,437 lines; corrections as recorded above).
- Created: `audit-outputs/implementation-plan-corrections-dec197.md` (this file).
- Not modified: decision log, both specifications, all research and audit files, `AGENTS.md`, the prior authoring evidence, and `papyr-reference/`.

## 6. Verification performed on the corrected plan

| # | Check | Command or method | Result |
|---|---|---|---|
| 1 | File exists and header | Read first lines | 1,437 lines; header intact with agentic-workers note, Goal, Architecture, Tech Stack |
| 2 | Checkbox count | `grep -c '^- \[ \]'` | 313 line-start task markers (unchanged; all tasks still checkboxed) |
| 3 | R-row count | `grep -cE '^\| R-[0-9]{2} \|'` | 28 rows (R-01..R-28), matching every count claim in the plan |
| 4 | Placeholder scan | `grep -inE 'TODO\|TBD\|FIXME\|XXX\|lorem ipsum\|WIP'` | 2 hits, both the plan's own self-verification prose (lines 42, 1430) |
| 5 | Benchmark scan | `grep -in 'benchmark'` | 2 hits, both DEC-066 prohibition statements (lines 16, 1431) |
| 6 | DEC coverage | `comm -23` of extracted DEC set vs DEC-001..197 | Missing: none. Outside range: none. Full DEC-001..DEC-197 coverage |
| 7 | Unnamed commands | grep for "the relay test runner", "the axe job", "the Lighthouse job", "and the test script" | 0 hits; all four review-flagged commands named; VL-03 contrast script also named |
| 8 | Phase DAG | grep of phase and SEC-01/SEC-02 headings | SEC-01 at line 711 and SEC-02 at line 726 inside Phase 3; Phase 4 at line 741; Phase 5 at line 839; consumers follow producers |
| 9 | Task step counts | awk step audit | All tasks 5 steps except FD-05 and PO-05 (documentation tasks, 4 steps, review-approved) |
| 10 | Stale aggregate references | grep for bare "SEC" task references | None; remaining "SEC" hits are phase-prefix aggregates in the task index (intentional) |
| 11 | Engine phrasing | grep for engine names | Every hit either proposal-framed under R-28/R-02 or inside the Section 6.1 matrix; Ghostscript flagged approved (DEC-195); ClamAV still under R-10 |
| 12 | Authorization scan | manual review of Section 7 and gated-phrase grep | No task performs VPS access, deployment, provider authentication, or git remote operations; CT-04 Step 3 explicitly G-5-gated |
| 13 | Interface and path consistency | cross-check of every `scripts/` file referenced against task Files lists | All referenced scripts are listed in a task's Files (check-docs-migration, check-ci, check-compose, check-monitoring, check-telegram-relay, review-deps, check-seo-inventory, check-launch, check-dashboard, check-restore, check-contrast) |
| 14 | Legacy cleanliness (after edits) | `git -C papyr-reference status --porcelain`; `rev-parse HEAD`; `log --oneline -1` | Empty porcelain, exit 0; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`; top of history unchanged |
| 15 | No implementation performed | task log review | Only read, grep, and edit on the plan plus the two assigned writes; no commands that mutate anything outside the two deliverables |

## 7. Markdown structure verification (manual, per ocs-markdown-autofix fallback)

The `bun run lint:md:fix` and `bun run lint:md` scripts are not available at the workspace root (no root package.json or bun scripts; consistent with arch §26.5). Manual structural pass on both the corrected plan and this file: ATX heading hierarchy without jumps, well-formed tables with header and separator rows, checkbox lists on task steps, no em or en dashes, no placeholder tokens.

## 8. Prohibitions-compliance statement

- No owner decision was made. All open choices remain named resolution items with stop conditions; the engine and queue selections are exposed as proposals under DEC-057 (R-28), not decided.
- No DEC-024 metrics or baselines were invented.
- No implementation, scaffolding, dependency installation, repository initialization, git commit or push, service start, VPS/SSH access, deployment, account creation, provider authentication, API call, or remote mutation was performed.
- No benchmark or comparative performance work was added.
- The decision log, both specifications, all reconciliation and audit files, `AGENTS.md`, and `papyr-reference/` were not modified. The only files changed are the corrected master plan and this evidence file.
- This file is the primary correction evidence; a chat-only summary is insufficient.
