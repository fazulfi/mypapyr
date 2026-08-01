# Papyr Rebuild: Owner Decisions R-01, R-27, R-28 Evidence (DEC-198..DEC-200)

| Field | Value |
|---|---|
| Document ID | PPR-PLN-OWN-001 |
| Title | Evidence record for appending DEC-198, DEC-199, and DEC-200 to the decision log and synchronizing the master implementation plan |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent; continuation of the plan authoring and correction session) |
| Status | Complete; three owner decisions appended, plan synchronized, plan approval still explicitly not granted |
| Governing inputs | `AGENTS.md`; owner confirmations (repository root, engine and queue matrix, 90-day measures); decision log DEC-001..DEC-200; the corrected master plan; the cross-review `audit-outputs/implementation-plan-cross-review-dec197.md`; the corrections evidence `audit-outputs/implementation-plan-corrections-dec197.md` |
| Primary deliverables | `papyr-rebuild-decisions.md` (appended DEC-198..DEC-200); `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (synchronized); this evidence file |
| Task constraints | Read and edit only the decision log and the master plan; write only the assigned evidence file; read-only git status on `papyr-reference`; no plan approval; no invented metric values; no implementation, installs, builds, servers, git operations, VPS access, deployment, authentication, or remote actions |

---

## 1. Method

1. Read `AGENTS.md` in full (append-only decision log rule; read-only legacy clone rule).
2. Verified the baseline state: `papyr-reference/` clean at HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`; plan at 1,437 lines; 15 `papyr-rebuild/` path occurrences; decision log ending at DEC-197.
3. Appended three stable new decisions after DEC-197 (DEC-198, DEC-199, DEC-200) without rewriting any prior history.
4. Synchronized the master plan top-to-bottom: Tech Stack, Global Constraints, Section 1 authority and precondition, Section 3 tree, Section 4 phase table, Section 6 resolution register and matrix, Phase 0 tasks, Phase 1 task paths, task engine wording (BE-05, SEC-02, TL-03..TL-06), VL-04 and PO-01 dashboard references, Section 9 traceability, and Section 10 self-review.
5. Re-ran the full manual verification battery (Section 6).
6. Re-verified `papyr-reference/` git cleanliness after all edits and confirmed the workspace root itself is not yet a git repository (no `git init` performed).
7. Wrote this evidence file.

## 2. Decision log appends (`papyr-rebuild-decisions.md`)

Three decisions appended after DEC-197 in the log's established format (heading separator, Date, Status, Decision, Rationale, Consequences):

- **DEC-198 (Accepted):** The rebuild Git repository root is the workspace `<workspace-root>` itself, not a nested `papyr-rebuild/` directory. `papyr-reference/` remains a separate nested read-only legacy clone excluded from the rebuild repository. `audit-outputs/`, the decision log, and the canonical specifications and plans are preserved as governed project records unless a later explicit decision changes the tracking policy. No git operation is authorized by the decision.
- **DEC-199 (Accepted):** The owner approves the complete R-28 engine and queue matrix exactly as presented: minimal custom queue over Redis Streams consumer groups; pdf-lib (Merge/Split browser happy path and browser JPG-to-PDF); pikepdf (qpdf) (Merge/Split server fallback and sanitization); img2pdf plus Pillow (JPG-to-PDF server); pypdfium2 (PDF-to-JPG server); pdf.js (browser rendering and page count); platform `createImageBitmap` (WebP decode). Every documented accepted risk, scope boundary, material condition, fallback, dependency and version review, and DEC-057 approval limit remains in force. This is approval of the matrix, not implementation authorization.
- **DEC-200 (Accepted with remaining open fields):** The owner approves the 90-day measures as the R-27 disposition: job success at or above 98 percent; system failure at or below 2 percent; uptime at or above 99.5 percent; Core Web Vitals passing for at least 75 percent of visits; completed downloads at or above 85 percent of successful jobs; organic traffic increasing relative to the first 28 post-launch days, represented as greater than zero percent growth evaluated at day 90; all five tools receiving meaningful usage; processing and queue latency measured as p50 and p95 per tool without an initial numeric target. Baseline is the first 28 post-launch days; evaluation at day 90. The decision records honestly that DEC-024's exact-numeric-targets gate remains only partially resolved because latency has no numeric target and meaningful usage lacks a numeric threshold, and that the plan-approval gate stays blocked on those two fields. No value for either field is invented.

The decision log headings use the file's established `## DEC-NNN - Title` convention (all 200 headings use it); the append does not alter any prior entry.

## 3. Master plan synchronization (`docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`)

All edits preserve the prior cross-review corrections (HIGH-1, HIGH-2, MEDIUM-3..10, LOW-11..13), DEC-066, DEC-143, the DEC-060/DEC-197 approval block, and all gates G-1..G-11.

1. **Tech Stack:** engine and queue selections changed from proposal framing to approved selections under DEC-199/R-28 (Redis Streams consumer groups, pdf-lib, pikepdf (qpdf), img2pdf plus Pillow, pypdfium2, pdf.js, platform `createImageBitmap`), with the documented risks and fallbacks noted as in force. Ghostscript stays normative (DEC-195); CI provider stays per R-02 (proposal).
2. **Global Constraints:** "Open choices" bullet notes resolved items carry their status in the register; two new bullets added: rebuild repository root (DEC-198, `papyr-reference/` excluded, nested `.git` never touched, no git operation authorized) and engine and queue matrix (DEC-199 approved, conditions normative, not implementation authorization).
3. **Section 1:** Sources now cite DEC-001 through DEC-200 and the three new decisions; the plan-approval precondition rewritten to reflect DEC-200's partial resolution with the exact wording of the approved measures, and to block plan approval and all phase starts on the two remaining DEC-024 fields; a new "Approval status" bullet states the plan remains unapproved and that DEC-198..DEC-200 resolve only the R-01, R-28, and most of R-27 dispositions.
4. **Section 3 tree:** root line changed to the workspace root per DEC-198; the tree now lists the new-repository directories (frontend, backend, deploy, docs, scripts, .github/workflows, .gitignore) plus the governed records (`papyr-reference/` read-only and excluded with its nested `.git` never touched, `audit-outputs/`, `papyr-rebuild-decisions.md`, `AGENTS.md`); notes updated accordingly. `queue/` line now reads "Redis Streams consumer groups (R-28, DEC-199)".
5. **Section 4:** P0 row exit gate now reads "repository exists at the workspace root per R-01 (DEC-198)".
6. **Section 6 register:** added status-semantics paragraph (RESOLVED / PARTIALLY RESOLVED markers); R-01 row marked `(RESOLVED: DEC-198)` with the superseded nested proposal and no remaining stop condition; R-27 row marked `(PARTIALLY RESOLVED: DEC-200)` with the full approved measure set and the stop condition that plan approval remains blocked on numeric latency targets and a numeric per-tool meaningful-usage threshold; R-28 row marked `(RESOLVED: DEC-199)` with conditions in force and "not implementation authorization". Section 6.1 retitled "(R-28, approved by DEC-199)"; the matrix intro and column header changed from proposal to approved-selection framing; every "Material conditions" cell rewritten from "Owner approves" to "Approved by DEC-199" with the conditions and fallbacks (pdf-lib dependency review, pypdf fallback, img2pdf metadata verification, white-compositing fixtures, pdf.js legacy floor re-check) kept normative. Disposition-handling paragraph extended to record resolved and partially resolved items with dates.
7. **Phase 0:** PR-01 rewritten for root-as-repository (`.gitignore` excludes `papyr-reference/` and its nested `.git`; `ls frontend backend deploy scripts docs` plus a `git -C papyr-reference status --porcelain` cleanliness check; `git init` at the workspace root only under G-1 with verification that `papyr-reference/` stays excluded). PR-02 renamed "Canonical documentation baseline": a dependency-free `scripts/check-docs-migration.sh` verifying the decision log at the root covers DEC-001..DEC-200 and both specs exist, and creating `docs/canonical-docs-baseline.md` (no copies are created because the documents already live in the repository root). PR-03 writes `docs/resolution-register.md`, pre-fills R-01/R-28/R-27 statuses, and checks 28 rows.
8. **Phase 1:** all `papyr-rebuild/` path prefixes removed from FD-01..FD-05 file lists and commands.
9. **Task engine wording:** BE-05 queue, SEC-02 sanitization, TL-03 and TL-04 browser/server engines, TL-05 image-to-PDF engines, and TL-06 render engine changed from "R-28-approved ... (proposal: X)" to "approved ... (DEC-199, R-28)" phrasing.
10. **VL-04 and PO-01:** "R-27 targets" replaced with "the R-27 measures approved by DEC-200 (with the two remaining DEC-024 fields applied once the owner supplies them)".
11. **Section 9:** 9.3 heading now "Decisions DEC-001 through DEC-200"; a new row maps DEC-198, DEC-199, and DEC-200 to Section 1, Section 6 (R-01, R-27, R-28), PR-01, PR-03, PO-01, and VL-04; the coverage note records the DEC-200 partial resolution and the two remaining DEC-024 fields.
12. **Section 10 self-review:** traceability check updated to DEC-001 through DEC-200; three new checks added (root path consistency with `papyr-rebuild/` only as a historical reference; engine approval consistency with no proposal framing on approved items; DEC-024 residual stating the plan remains unapproved with the two remaining fields unresolved and no invented values).
13. **Section 2 rule 4:** records that the R-28 matrix is the exception to proposal framing (approved by DEC-199) while all other category-A recommendations remain proposals until disposed.
14. **Task index:** PR-01, PR-02, PR-03 rows updated for the resolved root, the renamed baseline task, and the R-01..R-28 disposition range.

## 4. What was preserved

- All prior cross-review corrections: HIGH-1 (engine gating), HIGH-2 (Phase 3 SEC-01/SEC-02 prerequisites), MEDIUM-3..10, LOW-11..13.
- DEC-066 no benchmark program (only prohibition statements remain); DEC-143 visual baseline; DEC-060/DEC-197 plan-approval block; DEC-057 approval limits; all gates G-1..G-11; DEC-022/DEC-190 advertising risk; DEC-189 one-worker posture; DEC-195 Ghostscript; DEC-192 sanitization routing; DEC-194 410 default.
- R-01's disposition recorded as resolved while `papyr-reference/` exclusion and its untouched nested `.git` remain mandatory.
- R-28's conditions, fallbacks, and dependency and version review requirements as normative.
- The plan's own checkbox structure (313 task markers) and TDD skeleton (all tasks 5 steps except the two review-approved documentation tasks).

## 5. Remaining owner questions (not decided here)

1. **DEC-024 residual fields (blocking plan approval):** exact numeric latency targets and a numeric per-tool meaningful-usage threshold. Until recorded, no phase may start and the plan cannot be approved (DEC-024, DEC-200, R-27).
2. **Plan approval itself** (DEC-060, DEC-197): this plan remains unapproved; approval also requires the R-27 residual fields.
3. All other by-design resolution items R-02..R-26 at their stop conditions (unchanged by this task).
4. R-02 git hosting and repository creation authorization (owner-gated at Phase 0, gate G-1).

## 6. Verification performed

| # | Check | Command or method | Result |
|---|---|---|---|
| 1 | Decision log append | Read lines 2344-2378; `grep '^## DEC-19[8-9]\|^## DEC-200'` | DEC-198, DEC-199, DEC-200 present after DEC-197; prior entries untouched; log now 2,378 lines |
| 2 | DEC coverage in plan | `comm -23` of plan DEC set vs DEC-001..DEC-200 | Missing: none; outside range: none |
| 3 | Root path consistency | `grep -n 'papyr-rebuild/'` on the plan | 3 hits, all historical or explanatory (R-01 row, PR-01 step 1, self-review item 10); zero implementation paths |
| 4 | Engine approval consistency | grep for stale "proposal:" engine phrasing and "R-28-approved" | 0 hits; approved phrasing with DEC-199/R-28 citations in place |
| 5 | R-27 stale references | grep "R-27 targets" | 0 hits; VL-04 and PO-01 reference the DEC-200-approved measures with the residual fields noted |
| 6 | Placeholder scan | `grep -inE 'TODO|TBD|FIXME|XXX|lorem ipsum|WIP'` | Only the plan's own self-verification prose; no tokens |
| 7 | Benchmark scan | `grep -in 'benchmark'` | 2 hits, both DEC-066 prohibition statements |
| 8 | Checkbox count | `grep -c '^- \[ \]'` | 313 line-start task markers (unchanged) |
| 9 | R-row count | `grep -cE '^\| R-[0-9]{2} '` | 28 rows (R-01..R-28) with status markers; PR-03 expects 28 |
| 10 | Task step counts | awk step audit | All tasks 5 steps except FD-05 and PO-05 (documentation tasks, review-approved) |
| 11 | Markdown structure | manual pass (ocs-markdown-autofix fallback; no root lint scripts) | ATX heading hierarchy, well-formed tables, checkbox lists, no em or en dashes in the plan or this evidence file; decision-log headings match the file's established convention |
| 12 | Legacy cleanliness (before and after) | `git -C papyr-reference status --porcelain`; `rev-parse HEAD` | Empty porcelain, exit 0; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` both runs |
| 13 | No repository operation | `git -C . rev-parse --is-inside-work-tree` | "not a git repository" at the workspace root; no `git init` was performed |
| 14 | No implementation performed | task log review | Only read, edit, and grep on the two target files plus the assigned evidence write |

## 7. Markdown structure verification (manual, per ocs-markdown-autofix fallback)

The `bun run lint:md:fix` and `bun run lint:md` scripts are not available at the workspace root (no root package.json or bun scripts). Manual structural pass on all three touched files: ATX heading hierarchy without jumps; tables with header and separator rows and equal column counts; checkbox lists on task steps; no placeholder tokens; no em or en dashes in the plan or this evidence file; the decision log's appended headings follow the file's established `## DEC-NNN - Title` format.

## 8. Prohibitions-compliance statement

- The implementation plan was not approved. The approval block and the DEC-024 residual stop condition remain in force.
- No latency target or per-tool meaningful-usage threshold was invented; both remaining fields are recorded as unresolved.
- No implementation, dependency installation, build, server start, `git init`, commit, push, VPS/SSH access, deployment, provider authentication, or remote action was performed.
- No benchmark or comparative performance work was added.
- The specifications, AGENTS.md, research and reconciliation files, and `papyr-reference/` were not modified. Only `papyr-rebuild-decisions.md` (appended DEC-198..DEC-200), the master plan, and this evidence file were touched.
- This file is the primary audit output; a chat-only summary is insufficient.
