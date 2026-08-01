# Papyr Rebuild: Final R-27 Numeric Targets Evidence (DEC-201)

| Field | Value |
|---|---|
| Document ID | PPR-PLN-OWN-002 |
| Title | Evidence record for appending DEC-201 to the decision log and synchronizing the master implementation plan to complete DEC-024/R-27 |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent; continuation of the plan authoring and owner-decision session) |
| Status | Complete; DEC-201 appended, R-27 marked RESOLVED in the plan, plan approval still explicitly not granted |
| Governing inputs | `AGENTS.md`; owner-supplied final numbers (p95 queue wait at or below 60 seconds per tool; p95 server processing at or below 180 seconds per tool; p50 observed without a separate target; each launch tool at or above 5 percent of total completed downloads during days 29 through 90); decision log DEC-001..DEC-201; the master plan; the prior owner-decision evidence `audit-outputs/implementation-plan-owner-decisions-r01-r27-r28.md` (PPR-PLN-OWN-001) |
| Primary deliverables | `papyr-rebuild-decisions.md` (appended DEC-201); `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (synchronized through DEC-201, R-27 RESOLVED); this evidence file |
| Task constraints | Read and edit only the decision log and the master plan; write only the assigned evidence file; read-only git status on `papyr-reference`; no plan approval on the owner's behalf; no invented metrics; no implementation, installs, builds, servers, git operations, VPS access, deployment, authentication, or remote actions |

---

## 1. Method

1. Read `AGENTS.md` in full (append-only decision log rule; read-only legacy clone rule; mandatory delegated-output persistence rule).
2. Verified the baseline state: `papyr-reference/` clean at HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (empty porcelain, exit 0); workspace root is not a git repository (no `git init` performed); decision log ended at DEC-200 (2,378 lines); plan had 313 task checkboxes and 28 R rows.
3. Read the decision log tail (DEC-190..DEC-200), the DEC-024 entry, the full R-27/R-28 register rows and status semantics, Phase 0 tasks PR-02/PR-03, VL-04, PO-01, Section 9 traceability, and Section 10 self-review, plus the prior owner-decision evidence file.
4. Appended DEC-201 after DEC-200 in the log's established format without rewriting any prior entry.
5. Synchronized the master plan top-to-bottom through DEC-201: Section 1 sources and precondition, Section 6 register row R-27, Phase 0 tasks, VL-04 and PO-01, Section 9 traceability, and Section 10 self-review.
6. Re-ran the full manual verification battery (Section 6) and re-verified `papyr-reference/` git cleanliness after all edits.
7. Wrote this evidence file.

## 2. Decision log append (`papyr-rebuild-decisions.md`)

One decision appended after DEC-200 in the file's established format. The heading uses the file's established `## DEC-NNN — Title` convention (em dash, as used by all 200 prior headings); the decision body uses no em or en dashes.

- **DEC-201 (Accepted):** The owner supplies the exact numeric fields DEC-200 left open: p95 queue wait at or below 60 seconds per tool; p95 server processing at or below 180 seconds per tool; p50 latency remains observed and reported per tool without a separate numeric target; and each of the five launch tools contributes at or above 5 percent of total completed downloads during days 29 through 90 of the 90-day evaluation period. The baseline remains the first 28 post-launch days and evaluation is at day 90 from relaunch (DEC-200).
- The consequences state that DEC-201 completes the numeric fields left open by DEC-200 and fully resolves R-27 and the DEC-024 exact-numeric-target precondition, that the plan records R-27 as resolved with the precondition fully met, and explicitly that DEC-201 does NOT approve the implementation plan: the plan remains pending explicit owner approval and no phase may start before that approval (DEC-060, DEC-197).
- No value was invented. Every number in DEC-201 is the owner-supplied value recorded verbatim in meaning.
- Prior entries DEC-001..DEC-200 were not altered. The log now has 201 `## DEC-NNN` headings and ends at line 2,389.

## 3. Master plan synchronization (`docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`)

Fifteen precise edits, all preserving the prior cross-review corrections, DEC-066, DEC-143, the DEC-060/DEC-197 approval block, all gates G-1..G-11, all other R-items, and the 313 checkbox structure:

1. **Section 1 Sources (line 52):** decision baseline now DEC-001 through DEC-201; the parenthetical records DEC-201 as appended after DEC-197 alongside DEC-198, DEC-199, and DEC-200, adding "the final R-27 numeric targets".
2. **Section 1 plan-approval precondition (line 54):** retitled from "partially resolved by DEC-200" to "resolved by DEC-200 and DEC-201"; the approved measure list now records p50 and p95 processing and queue latency per tool without the "without an initial numeric target" caveat; a new sentence records the DEC-201 exact fields (p95 queue wait at or below 60 seconds per tool, p95 server processing at or below 180 seconds per tool, p50 observed and reported per tool without a separate target, each launch tool at or above 5 percent of total completed downloads during days 29 through 90); states every DEC-024 exact-numeric field now has a value, the precondition is fully met, and no field remains open; plan approval itself remains pending the owner's explicit decision and no phase may start before that approval.
3. **Section 1 approval status (line 55):** "DEC-198 through DEC-200 resolve the R-01, R-28, and most of R-27 dispositions only" changed to "DEC-198 through DEC-201 resolve the R-01, R-28, and R-27 dispositions only"; the unapproved status and the full approval block are unchanged.
4. **Section 6 register row R-27 (line 257):** marker changed from `(PARTIALLY RESOLVED: DEC-200)` to `(RESOLVED: DEC-201)`; the evidence cell appends the four DEC-201 fields to the DEC-200 measure set; governed-by now reads DEC-024, DEC-200, DEC-201; the stop condition now reads "Resolved by DEC-200 and DEC-201; no stop condition remains; the disposition is recorded in PR-03. The plan remains unapproved, and no phase may start before explicit owner approval".
5. **PR-02 Step 1 (line 328):** the check script verifies decision IDs DEC-001 through DEC-201.
6. **PR-02 Step 3 (line 330):** the baseline record documents the DEC-001 through DEC-201 decision range.
7. **PR-03 Step 1 (line 343):** the register shell pre-fill now reads "R-01 RESOLVED (DEC-198), R-28 RESOLVED (DEC-199), R-27 RESOLVED (DEC-201)"; the stale PARTIALLY RESOLVED pre-fill with the two open fields is removed.
8. **VL-04 Produces (line 1236):** Lighthouse results recorded against "the R-27 measures and targets approved by DEC-200 and DEC-201"; the "two remaining DEC-024 fields applied once the owner supplies them" clause is removed.
9. **VL-04 Step 2 (line 1239):** expected failure is against "the R-27 measures and targets approved by DEC-200 and DEC-201".
10. **PO-01 Produces (line 1274):** dashboard measures against "the R-27 measures and targets approved by DEC-200 and DEC-201 (DEC-024)"; the residual-fields clause is removed.
11. **Section 9.3 heading (line 1405):** "Decisions DEC-001 through DEC-201 to phases and tasks".
12. **Section 9.3 cluster row (line 1431):** the "Plan and owner decisions after DEC-197" row now lists DEC-201 (final R-27 numeric targets) alongside DEC-198, DEC-199, and DEC-200; the mapping targets (Section 1, Section 6 R-01/R-27/R-28, PR-01, PR-03, PO-01, VL-04) are unchanged.
13. **Coverage note (line 1433):** every accepted decision DEC-001 through DEC-201 maps to at least one phase or task; DEC-200 approved the 90-day measures and DEC-201 supplied the final numeric fields (full values restated), fully resolving R-27 and the DEC-024 exact-numeric precondition; the plan itself remains unapproved pending explicit owner approval and no phase may start before that approval.
14. **Self-review item 5 (line 1443):** traceability check now covers DEC-001 through DEC-201.
15. **Self-review item 12 (line 1450):** retitled "DEC-024 completeness and approval status"; records that DEC-200 and DEC-201 fully resolve R-27 and the DEC-024 exact-numeric precondition, that this plan remains unapproved pending explicit owner approval, and that no phase may start before that approval.

## 4. What was preserved

- All prior cross-review corrections (HIGH-1, HIGH-2, MEDIUM-3..10, LOW-11..13) and the PPR-PLN-OWN-001 synchronization of DEC-198..DEC-200.
- DEC-066 no benchmark program; DEC-143 visual baseline; DEC-060/DEC-197 plan-approval block; DEC-057 approval limits; all gates G-1..G-11; DEC-189 one-worker posture; DEC-195 Ghostscript; DEC-199/R-28 matrix conditions; DEC-198 repository root wording.
- All other R-items R-01..R-28: R-01 and R-28 remain RESOLVED (DEC-198, DEC-199), R-02..R-26 remain pending at their stop conditions, and the register keeps 28 rows.
- The plan's 313 task checkboxes and TDD skeleton; the status-semantics paragraph and disposition-handling paragraph in Section 6 (the PARTIALLY RESOLVED convention stays documented even though no current row uses it).
- The decision log's DEC-001..DEC-200 bodies untouched.

## 5. Remaining owner questions (not decided here)

1. **Plan approval itself** (DEC-060, DEC-197): this plan remains unapproved. The DEC-024 exact-numeric precondition is now fully met, so the plan is ready for the owner's explicit approval decision; no phase may start before it.
2. All by-design resolution items R-02..R-26 at their stop conditions (unchanged by this task).
3. R-02 git hosting and repository creation authorization (owner-gated at Phase 0, gate G-1).

## 6. Verification performed

| # | Check | Command or method | Result |
|---|---|---|---|
| 1 | Decision log append | Read lines 2368-2389; `grep -E '^## DEC-[0-9]{3}'` count | 201 headings; DEC-201 present after DEC-200; prior entries untouched; log now 2,389 lines |
| 2 | DEC coverage in plan | `comm -23` of plan DEC set vs DEC-001..DEC-201 | Missing: none; outside range: none |
| 3 | Stale R-27 language | grep "PARTIALLY RESOLVED: DEC-200", "partially resolved by DEC-200", "remaining DEC-024", "two remaining DEC-024", "once the owner supplies", "DEC-024 residual", "DEC-001 through DEC-200" | 0 hits |
| 4 | DEC-201 references | `grep -c "DEC-201"` | 15 occurrences, all in the expected locations (lines 52, 54, 55, 257, 328, 330, 343, 1236, 1239, 1274, 1405, 1431, 1433, 1443, 1450) |
| 5 | Checkbox count | `grep -c '^- \[ \]'` | 313 line-start task markers (unchanged) |
| 6 | R-row count | `grep -cE '^\| R-[0-9]{2} '` | 28 rows (R-01..R-28) |
| 7 | Placeholder scan | `grep -inE 'TODO|TBD|FIXME|XXX|lorem ipsum|WIP'` | Only the plan's own self-verification prose (lines 42, 1440); no tokens |
| 8 | Benchmark scan | `grep -in 'benchmark'` | 2 hits, both DEC-066 prohibition statements (lines 16, 1441) |
| 9 | Root path consistency | `grep -n 'papyr-rebuild/'` | 3 hits, all historical or explanatory (R-01 row, PR-01 step 1, self-review item 10); zero implementation paths |
| 10 | Em/en dash scan on plan | `grep -nP '\x{e2}\x{80}\x{94}|\x{e2}\x{80}\x{93}'` | 0 hits; the plan remains dash-free |
| 11 | Decision-log heading format | `od -c` on headings; `tail -3` | DEC-201 heading matches the established `## DEC-NNN — Title` convention (em dash) used by all 200 prior headings |
| 12 | Legacy cleanliness (before and after) | `git -C papyr-reference status --porcelain`; `rev-parse HEAD` | Empty porcelain, exit 0; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` both runs |
| 13 | No repository operation | `git -C . rev-parse --is-inside-work-tree` | "not a git repository" at the workspace root; no `git init` was performed |
| 14 | No implementation performed | task log review | Only read, edit, and grep on the two target files plus the assigned evidence write |

## 7. Markdown structure verification (manual, per ocs-markdown-autofix fallback)

The `bun run lint:md:fix` and `bun run lint:md` scripts are not available at the workspace root (no root package.json or bun scripts). Manual structural pass on all three touched files: ATX heading hierarchy without jumps; tables with header and separator rows and equal column counts (the R-27 row keeps 5 cells matching the register header); checkbox lists on task steps; no placeholder tokens; no em or en dashes in the plan or this evidence file; the DEC-201 heading follows the decision log's established `## DEC-NNN — Title` format, and the DEC-201 body uses no em or en dashes.

## 8. Prohibitions-compliance statement

- The implementation plan was not approved on the owner's behalf. The approval block remains in force: product implementation, dependency installation, repository creation, commits, pushes, VPS access, infrastructure changes, deployment, provider authentication, and remote operations all remain blocked until the owner reviews and explicitly approves the plan. No phase may start before that approval.
- No metric value was invented. The four DEC-201 fields are the owner-supplied numbers recorded verbatim in meaning in both the decision log and the plan.
- No implementation, dependency installation, build, server start, `git init`, commit, push, VPS/SSH access, deployment, provider authentication, or remote action was performed.
- No benchmark or comparative performance work was added.
- The specifications, AGENTS.md, research and reconciliation files, `papyr-reference/`, and the DEC-001..DEC-200 decision bodies were not modified. Only `papyr-rebuild-decisions.md` (appended DEC-201), the master plan, and this evidence file were touched.
- This file is the primary audit output; a chat-only summary is insufficient.
