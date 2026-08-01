# Papyr Rebuild: Master Implementation Plan Cross-Review (DEC-197)

| Field | Value |
|---|---|
| Document ID | PPR-PLN-CR-001 |
| Title | Independent cross-review of the master implementation plan for correctness, completeness, executability, and fidelity to approved constraints |
| Date | 2026-07-31 |
| Reviewer role | Sisyphus-Junior (executor subagent; review-only task, no file edits except this deliverable) |
| Plan under review | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (1,417 lines; 313 task checkboxes; 27 resolution rows R-01..R-27) |
| Governing rules | `AGENTS.md` (Papyr Rebuild Orchestrator Rules) |
| Verdict | **CONDITIONAL PASS** (2 HIGH findings must be corrected before plan approval; 8 MEDIUM and 3 LOW findings require deterministic corrections; 1 material owner-input precondition — DEC-024 numeric targets — must be supplied at plan approval) |

---

## 1. Scope and method

1. Read `AGENTS.md` in full before any other action; obeyed its rules throughout (read-only review, single assigned output file, no edits to the plan, decision log, specs, audit files, or `papyr-reference/`, no delegated-output substitution).
2. Read the canonical plan in full (1,417 lines, Sections 1-10, all 66 tasks PR-01..PO-05, all 27 resolution rows, all 11 gates).
3. Read the authoring evidence `audit-outputs/implementation-plan-authoring-dec197.md` in full (215 lines).
4. Read the living decision log `papyr-rebuild-decisions.md` in full (2,343 lines, DEC-001 through DEC-197 plus the Open decisions status list).
5. Read both approved canonical specifications in full:
   - `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` (732 lines)
   - `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` (1,203 lines)
6. Read the three research navigation/reconciliation deliverables in full:
   - `audit-outputs/research/reconciliation-report.md` (X2, 299 lines)
   - `audit-outputs/research/research-brief-verification.md` (PPR-VER-001, 266 lines)
   - `audit-outputs/research/source-and-decision-index.md` (X1, 605 lines)
7. Ran read-only verification commands (Section 6): checkbox counts, resolution-row counts, placeholder scan, benchmark scan, unique DEC-ID extraction with set-difference against DEC-001..DEC-197, engine-name presence scans across the plan and both specs, and `papyr-reference/` git evidence.
8. Loaded `context-grooming` (long cross-document review) and `ocs-markdown-autofix` (markdown structure; its `bun run lint:md:fix` scripts are not available at the workspace root — no root package.json or bun scripts exist — so markdown structure was verified manually per the skill's fallback path and the plan's own arch §26.5 note).

Precedence applied throughout: decisions, then the two specifications, then audit and research evidence, then the legacy reference (plan Section 1; arch §1.4).

## 2. Verified facts (mechanical checks)

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Plan line count / size | 1,417 lines; 122,551 bytes | Read tool, full-file read |
| 2 | Checkbox markers | 313 line-start `- [ ]` task markers; the 314th raw occurrence is the inline-code mention at plan line 3 ("checkbox (`- [ ]`) syntax"), not a task step | `grep -c '^- \[ \]'` = 313; `grep -oE '\- \[ \]' \| wc -l` = 314 |
| 3 | Resolution rows | 27 (R-01..R-27), one per open choice | `grep -cE '^\| R-'` = 27 |
| 4 | Placeholder scan | 0 tokens; the only 2 hits are the plan's own self-verification prose (lines 42, 1410) | `grep -inE 'TODO\|TBD\|FIXME\|XXX\|lorem ipsum\|WIP'` |
| 5 | Benchmark scan | 0 violations; the only 2 hits are DEC-066 prohibition statements (lines 16, 1411) | `grep -in 'benchmark'` |
| 6 | DEC citation coverage | 193 of 197 decisions cited; **DEC-004, DEC-044, DEC-163, DEC-167 are absent from the entire plan**; no DEC outside 001-197 is cited | `comm -23` of plan DEC set vs generated DEC-001..197 set |
| 7 | Section 9.3 cluster matrix | Omits DEC-004, DEC-044, DEC-046, DEC-062 (DEC-046 and DEC-062 are cited elsewhere in the plan body: lines 30-31/936 and 35/1178); the matrix's coverage note (line 1403) is therefore overstated | Full read of Section 9.3 |
| 8 | Engine-name presence | `redis streams`, `pikepdf`, `img2pdf`, `pillow`, `pypdfium2`, `pdf-lib`, `pdf.js` appear **only in the plan**, never in either approved spec (grep exit 1 on both specs) | See Finding HIGH-1 |
| 9 | `papyr-reference/` unchanged | HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`; `git status --porcelain` empty, exit 0; top of history `981c59a` → `8d0d09e` → `cce59e1` | Section 8 |

## 3. Severity-ranked findings

### 3.1 HIGH-1 — Category-A engine and queue-mechanism recommendations elevated to normative implementation choices without owner approval (DEC-057 violation)

**Location.** Plan lines 9 (Tech Stack), 102 (proposed tree `queue/ Redis Streams queue`), 612 (BE-05 "Redis Streams consumer-group queue (C1 brief)"), 740 (TL-03 "pdf-lib for the unencrypted happy path (A3 brief) and pikepdf server fallback"), 755 (TL-04 "browser-first pdf-lib with pikepdf server fallback"), 774 (TL-05 "img2pdf plus Pillow per the A5 brief"), 789 (TL-06 "pypdfium2 with explicit white fill per the A6 brief"), 823 and 827 (SEC-02 "pikepdf-based sanitization" / "the pikepdf sanitization API (A3 brief)").

**Evidence.**

1. Neither approved spec names any of these technologies. `grep -inE 'redis streams|pikepdf|img2pdf|pillow|pypdfium|pdf-lib|pdf\.js|clamav|qpdf'` over both `docs/superpowers/specs/*.md` returns zero matches. The arch spec's engine statements are limited to Ghostscript (approved by DEC-195, arch §11.2 and §25.3 item 1) and legacy reference material.
2. X2 Section 4 classifies every one of these as a **Category-A compatible recommendation** "safe to carry into later implementation planning (still subject to DEC-057 approval of the resulting design)": A-2 (pikepdf/qpdf merge-split fallback and sanitization), A-3 (pdf-lib browser happy path), A-4 (img2pdf + Pillow), A-5 (pypdfium2 + pdf.js), A-7 (minimal custom queue over Redis Streams consumer groups). X2 C-2 additionally records the "maintained-framework-vs-custom" queue preference as a deferred owner confirmation. X1 records the same items as unresolved owner questions (X1 §5.1 C1: "owner preference between a maintained framework and the custom queue"; A3/A4/A5/A6 "Material unresolved questions").
3. DEC-057 (decision log lines 706-716): "A feature may proceed from research into approved design and implementation planning only after the project owner explicitly approves it. Approval must identify the selected approach, accepted risks, scope boundaries, and material conditions." Arch §25.1 (line 1062): "Category-A recommendations remain recommendations subject to the approval gate (DEC-057) and are not requirements of this specification."
4. The plan's own Section 2 rule 4 (line 59) promises: "Category-A research recommendations (X2 Section 4) are design inputs only and remain subject to owner approval (DEC-057). Resolution tasks carry them as proposals with the governing decision cited." **No resolution row R-01..R-27 carries any of these engines as a proposal.** R-03 (limits), R-07 (worker memory/time bounds), R-09 (Redis persistence mode) carry C1/C2 numeric defaults only; R-10 correctly carries ClamAV as a proposal (the one technology properly gated); no row covers the Redis queue data structure, the sanitization engine, or any browser/server tool engine.
5. The plan's own Section 2 rule 3 (line 58) and Global Constraint line 42 promise that open choices are named resolution items, never invented or silently fixed.

**Distinction applied (accepted vs still-gated).** Ghostscript as the Compress engine is owner-approved (DEC-195) and correctly asserted. ClamAV is a research recommendation carried correctly as a proposal in R-10. Every other engine in the Tech Stack — Redis Streams consumer groups, pdf-lib, pdf.js, pikepdf, img2pdf, Pillow, pypdfium2 — is still gated by DEC-057 and is asserted as if approved. "GitHub Actions" is likewise asserted (line 9, FD-04) while R-02 ("GitHub recommended as default") is unresolved (see MEDIUM-6).

**Risk.** If the owner approves the plan as-is, the plan's approval would silently ratify engine selections that per DEC-057 required per-feature approval identifying the selected approach, accepted risks, scope boundaries, and material conditions — and the plan's own resolution register, which it designates as the DEC-057 record, would show them as never approved. An execution agent would then install and integrate these engines as a matter of course. This contradicts the plan's own governance structure.

**Correction (deterministic).**

1. Re-label line 9 to mark the gated items as proposals, e.g.: "FastAPI; Redis queue (mechanism per R-28; proposal: Redis Streams consumer groups per C1 brief); Ghostscript as an unmodified subprocess (DEC-195, approved); engine selections per R-28 (proposals: pdf-lib and pdf.js browser engines, pikepdf server fallback and sanitization, img2pdf plus Pillow, pypdfium2); Docker Compose; Nginx; Cloudflare R2; CI provider per R-02 (proposal: GitHub Actions, CI core gate only)."
2. Add resolution rows (e.g., R-28 "Queue data structure and engine matrix (X2 A-2..A-5, A-7; X1 A1/A3-A6/C1)") with a stop condition "Owner approves the engine matrix and queue mechanism before BE-04/BE-05, TL-03..TL-06, and SEC-02", carrying the A-brief recommendations as proposals with the governing DEC-057 citation. Optionally split per engine if the owner prefers per-feature approval (which DEC-057 literally requires); a single matrix row is acceptable only if each engine's selected approach, accepted risks, and material conditions are identified in the row.
3. Edit BE-05 line 612 ("Redis Streams consumer-group queue (C1 brief)") to "queue per the approved R-28 disposition (proposal: Redis Streams consumer groups, C1 brief)", and similarly mark TL-03 (740), TL-04 (755), TL-05 (774), TL-06 (789), SEC-02 (823, 827) and tree line 102 as contingent on R-28.
4. Update PR-03's row-count expectation if rows are added (currently `grep -c '^| R-'` expects 27).

**Severity rationale.** HIGH, bordering on BLOCKER: it violates a hard approved gate (DEC-057) and the plan's own rule 4, but it is fully visible at the owner review of the plan and requires no execution to correct; a deterministic edit at approval time restores compliance. It must be corrected before the plan is approved.

### 3.2 HIGH-2 — Phase-ordering DAG violation: Phase 4 tool tasks consume Phase 5 security outputs, and the Phase 5 gate entry contradicts the phase table

**Location.** Phase table lines 128-143 (P4 depends on P2, P3; P5 depends on P3, P4); TL-02 Consumes at line 724 ("SEC-02"); TL-03 Consumes at line 739 ("SEC-01, SEC-02"); TL-04 Consumes at line 754 ("SEC-01, SEC-02"); SEC-01/SEC-02 live in Phase 5 (lines 801-829); Phase 5 gate entry line 797 says "**Gate entry:** Phase 3 complete; R-10 and R-11 dispositions recorded"; Phase 4 gate entry line 699 lists "R-03, R-04, R-06, R-14, R-17" only.

**Evidence.** A task that "Consumes" another task's output cannot execute before that output exists. TL-02 (Phase 4) requires SEC-02 (Phase 5); TL-03 and TL-04 require SEC-01 and SEC-02 (Phase 5). Phase 5 cannot begin until Phase 4 completes (table) — so Compress, Merge, and Split (three of the five launch tools) cannot be completed as specified under any literal phase-order execution. The Phase 5 gate entry text omits Phase 4 entirely, making the contradiction explicit: the table requires P3+P4 before P5, the gate text requires only P3. The Section 6 general rule ("No task that consumes a resolution item may proceed...") does not help here because SEC-01/SEC-02 are tasks, not resolution items.

**Correction (deterministic).** Choose one of:

1. Move SEC-01 (threat classification and fail-closed matrix, BE-02/BE-08 consumable) and SEC-02 (sanitization pass) into Phase 3/4 as prerequisite tasks of TL-02..TL-04, and update the phase table (P5 then depends on P3, P4 as before; P4 gate entry adds SEC-01/SEC-02 completion), or
2. Declare explicitly in Section 4 that SEC-01 and SEC-02 are *early security prerequisites* produced before TL-02..TL-04 despite living in Phase 5's section, add them to the Phase 4 gate entry, and fix the Phase 5 gate entry to "Phases 3 and 4 complete" to match the table.

Either way the phase table, the Phase 4 gate entry, the Phase 5 gate entry, and the Consumes edges must be mutually consistent.

### 3.3 MEDIUM-3 — DEC-024 numeric targets and baseline windows are a hard prerequisite to plan approval; the plan's "not the foundational phases" phrasing is misleading

**Question asked:** Are DEC-024's exact 90-day numeric targets and baseline windows truly a prerequisite to owner approval of this implementation plan?

**Answer:** Yes. DEC-024 (decision log lines 304-314, specifically line 313) states verbatim: "Exact numeric targets and baseline measurement windows must be defined before implementation planning is approved." UX §20.6 item 5 (line 686) and arch §24.2 (line 1037) repeat the requirement. The plan cannot be approved without them.

**Plan treatment.** Line 52 records the precondition (R-27) and R-27's stop condition (line 247) says "Owner defines the targets before plan approval (precondition, Section 1)" — correct in substance. **However**, line 52 also states the precondition "gates Phase 10 and Phase 11 acceptance, not the foundational phases." If the targets must exist before approval, they exist from day one; the "gates Phase 10/11, not the foundational phases" sentence invites an owner to approve the plan while deferring the targets to Phase 10, which would violate DEC-024. VL-04 (line 1208) and PO-01 (line 1246) correctly assume the targets exist ("against the R-27 targets"), so only the Section 1 wording needs correction.

**Correction (deterministic).** Rewrite line 52 to: "**Plan-approval precondition (DEC-024):** the owner must define the exact numeric targets and baseline measurement windows for the 90-day success criteria (job success and failure, processing and queue latency, uptime, Core Web Vitals, organic entrances, tool usage distribution, completed downloads) as part of approving this plan; the approval record must include the R-27 disposition. Until then no phase may start." Remove or reword "gates Phase 10 and Phase 11 acceptance, not the foundational phases."

**Smallest material owner questions (required at plan approval):**

1. Exact numeric targets per metric family: job success rate, job failure rate, p50/p95 processing latency, p50/p95 queue latency, uptime, Core Web Vitals (LCP/CLS/INP thresholds), organic entrances (absolute or growth), per-tool usage distribution (minimum share per tool), and completed-download rate.
2. Baseline measurement windows: what constitutes the baseline (pre-launch data, first N days post-launch, or none), when the 90-day window starts, and whether targets are absolute or relative to the baseline.

### 3.4 MEDIUM-4 — R-15 stop condition conflicts with SH-01's consumption of R-15

**Location.** R-15 (line 235) stop condition: "Owner approves slug table and disposition map before SEO-01." SH-01 (line 421) Consumes: "FD-01, R-15 (slug table feeds route names)." Phase 2 gate entry (line 412) is only "Phase 1 complete."

**Evidence.** Route names in SH-01 depend on the R-15 slug table, but the R-15 stop condition names only SEO-01 (Phase 8) as the blocking point, and the Phase 2 gate does not require R-15. The Section 6 general rule ("No task that consumes a resolution item may proceed past the item until the owner disposes it") technically rescues consistency, but the specific stop-condition text and the Phase 2 gate entry contradict it, leaving two readings (SH-01 may proceed with invented slugs, or is blocked).

**Correction (deterministic).** Change R-15's stop condition to "Owner approves slug table and disposition map before SH-01 (route names) and SEO-01", and add "R-15" to the Phase 2 gate entry.

### 3.5 MEDIUM-5 — Phase 4 gate entry omits R-05, which TL-02 consumes

**Location.** Phase 4 gate entry (line 699) lists "R-03, R-04, R-06, R-14, R-17" — no R-05. TL-02 Consumes (line 724) includes "R-04, R-05". R-05's stop condition (line 225) is "License review outcome recorded; fallback path chosen if unacceptable."

**Correction (deterministic).** Add R-05 to the Phase 4 gate entry, or explicitly note that R-05's stop condition binds TL-02 under the Section 6 general rule.

### 3.6 MEDIUM-6 — PR-02 executes pytest at Phase 0 before any Python tooling exists, and the root `tests/` directory is absent from the proposed tree

**Location.** PR-02 steps 1-2 (lines 303-304): "Write the migration test" at `papyr-rebuild/tests/test_docs_migration.py` and "Run: `pytest papyr-rebuild/tests/test_docs_migration.py -v`" — executed in Phase 0. The Section 3 tree (lines 68-118) contains no root-level `tests/` directory and no root Python tooling; `backend/pytest.ini` and `backend/requirements-dev.txt` are created only in FD-02 (Phase 1, lines 350-354). No Python environment or pytest installation exists at Phase 0.

**Evidence.** The plan's own Section 2 rule 3 promises "exact file paths, interfaces, verification commands" and Section 2 rule 7 that tasks are executable in phase order. PR-02 is not executable as written: the command will fail for the wrong reason (no pytest/venv) even after Step 3 copies the files.

**Correction (deterministic).** Either (a) add a root-level Python tooling prerequisite to the Phase 0 gate (e.g., a documented venv + `pip install pytest` step in FD-05 or a PR task, with `tests/` added to the Section 3 tree), or (b) move the docs-migration test into Phase 1 (FD-02) with PR-02 reduced to the copy steps and a root-level check script that does not require pytest.

### 3.7 MEDIUM-7 — Undefined verification commands contradict the plan's own exactness rule

**Location.** OP-03 Step 2 (line 1007): "Run: the relay test runner" (no command named); SEC-04 Step 2 (line 856): "and the test script" (unnamed); VL-02 Step 2 (line 1181): "Run: the axe job" (unnamed); VL-04 Step 2 (line 1211): "Run: the Lighthouse job" (unnamed).

**Evidence.** Plan Section 2 rule 3 (line 58): "tasks specify exact file paths, interfaces, verification commands, and expected outcomes." These four steps name no command, so an execution agent cannot know what to run or what "FAIL" means.

**Correction (deterministic).** Name the commands, consistent with the plan's existing naming convention, e.g., `scripts/check-telegram-relay.sh`, `scripts/check-compose.sh`, `npm run test:a11y -- axe`, `npm run test:perf -- lighthouse`, each with the expected FAIL/PASS outcome and the script path added to the task's Files list.

### 3.8 MEDIUM-8 — CT-04 Step 3 performs authenticated gateway calls without an explicit G-5 gate, contradicting Section 2 rule 7

**Location.** CT-04 Step 3 (line 1144): "Generate the articles through the approved workflow for the R-22-approved topics, subject to the R-25 demand evidence." G-5 (line 261): "Gateway access and any authenticated call to `https://router.budgezen.com/v1` — Owner; no authenticated call is authorized by any planning artifact." Section 2 rule 7 (line 62): "No task in this plan performs them; tasks only prepare the artifacts."

**Evidence.** Generating the fifteen launch articles through the blog workflow is an authenticated call to the gateway. Section 2 rule 7's blanket claim that no task performs a gated action is therefore false for CT-04 Step 3; DEC-193/DEC-196 state no authenticated call is authorized by any planning artifact, so the owner must authorize each generation run under G-5 at execution time. (PO-04's daily cadence is the approved DEC-048 automated publishing model and is acceptable once the workflow itself is owner-activated; the pre-launch CT-04 generation is the gap.)

**Correction (deterministic).** Amend CT-04 Step 3 to: "Generate the articles through the approved workflow for the R-22-approved topics, subject to the R-25 demand evidence, with each generation run executed under the G-5 owner gate (no authenticated gateway call is authorized by this plan)."

### 3.9 MEDIUM-9 — G-1 "per commit or push" conflicts with the owner-approved auto-publishing model (DEC-048) carried in CT-03

**Location.** G-1 (line 257): "Repository creation, git commits, pushes, remote setup — Owner at Phase 0 and per commit or push." CT-03 (lines 1121-1131) and PO-04 (lines 1286-1297) carry the E2-brief architecture (X2 A-18): a scheduled content-bot workflow that opens gate-passing PRs and auto-merges through the normal build path.

**Evidence.** DEC-048 (decision log lines 596-608) explicitly approves fully automated LLM-assisted publishing "without requiring human approval for every article." A workflow that auto-merges gate-passing PRs performs git merges/pushes without a per-commit owner authorization, which G-1 as written forbids.

**Correction (deterministic).** Add a carve-out to G-1: "except the owner-approved blog automation pipeline under DEC-048, CT-03, and PO-04, whose gate-passing PRs auto-merge through the normal build path; activation of that workflow is owner-gated."

### 3.10 MEDIUM-10 — GitHub Actions asserted normatively while R-02 (git hosting) is unresolved

**Location.** Tech Stack line 9 ("GitHub Actions (CI core gate only)"); FD-04 (lines 377-390) creates `.github/workflows/ci.yml` and `scripts/check-ci.sh` parsing a GitHub workflow YAML; R-02 (line 222) records "GitHub recommended as default" with stop condition "Owner confirms hosting and authorizes repository creation at P0."

**Correction (deterministic).** Re-label line 9 as "CI provider per R-02 (proposal: GitHub Actions, CI core gate only)" and note in FD-04 that the workflow artifact is contingent on the R-02 disposition.

### 3.11 MEDIUM-LOW-11 — Traceability matrix and coverage note gaps

**Location.** Section 9.3 (lines 1379-1403); coverage note line 1403 claims "every accepted decision DEC-001 through DEC-197 maps to at least one phase or task."

**Evidence.** Four decisions are absent from the entire plan: DEC-004 (launch EN+ES; expanded/superseded in effect by DEC-115/DEC-118), DEC-044 (tool-page SEO content + blog; materially covered by CT-03/CT-04 but uncited), DEC-163 (tool pages available during backend outages, no redirect to status; behavior covered by TL-01's capabilities fallback and OP-02 but uncited), DEC-167 (per-tool engine-failure isolation; behavior covered by OP-02/status derivation and BE-08 admission but uncited). DEC-046 and DEC-062 are cited in the plan body (PT-03 line 936; lines 35 and 1178) but missing from the 9.3 clusters.

**Correction (deterministic).** Add DEC-046 and DEC-062 to the appropriate clusters; add rows (or explicit supersession notes) for DEC-004 (governed by DEC-115/118) and DEC-044 (map to CT-03/CT-04/SH-07); add DEC-163 and DEC-167 to a cluster mapping them to TL-01, BE-08, and OP-02; then amend the coverage note to match.

### 3.12 LOW-12 — R-14 mixes owner decisions and implementer confirmations in the Owner Resolution Register

**Location.** R-14 (line 234) stop condition: "Owner **or implementer** confirms trusted-header setup before TL-05." Section 6 heading (line 215) is "Owner Resolution Register (Unresolved-Item Blockers and Stop Conditions)." Arch §25.3 item 7 and X1 M9 treat the trusted-header detail as implementation-time confirmation.

**Correction (deterministic).** Either keep it an owner confirmation (consistent with the register), or move it out of the register and record it as an implementation-time re-check on the TL-05 task, citing X1 M9.

### 3.13 LOW-13 — "runbook-vps.md ... (updates legacy)" wording

**Location.** Section 3 tree line 114: `deploy/runbook-vps.md  canonical operations runbook (updates legacy)`. The intent (per the authoring audit) is that the rebuild repo's runbook replaces the legacy runbook's canonical status; the wording could be misread as editing `papyr-reference/`.

**Correction (deterministic).** Reword to "canonical operations runbook (replaces the legacy `papyr-reference/docs/runbook-vps.md` as the operating reference; the legacy file is never modified)."

## 4. Verified-OK areas (explicitly checked, no defect found)

1. **R-01 root selection is NOT silently accepted.** Line 66 labels the tree "implementation-level and subject to owner confirmation as resolution item R-01"; line 69 shows "proposed monorepo root (R-01; own git repository)"; R-01's stop condition (line 221) is "Owner confirms the root path before PR-01 runs"; PR-01 Step 1 (line 288) logs the disposition before any git operation. All task paths are written relative to the proposed root with the caveat stated. PASS.
2. **Benchmark-program leakage: none.** Only two "benchmark" hits, both DEC-066 prohibition statements. VL-03's side-by-side visual comparison is DEC-143 continuity verification (X2 A-17/B5 §8 precedent, explicitly "not a benchmark" per PPR-VER-001 §6.1); VL-04 Lighthouse runs are Core Web Vitals verification against owner-supplied R-27 targets (DEC-024), not a comparative performance study. PASS.
3. **Separately gated operations cannot execute as ordinary steps.** G-1..G-11 (Section 7) isolate repository/git, VPS access, deployment, provider accounts, gateway calls, Adsterra integration, legal review, credential rotation, spending, worker concurrency, and per-URL disposition deviations. PR-01 Step 4 requires G-1 before `git init`; FD-04 Step 3 defers GitHub secrets/environments to G-4; VL-05 Step 3 runs under G-3; OP-04/PO-03 reference G-4; PO-05 ends in a separate owner decision; CT-03's adapter writes no credentials (tested). The only gap is MEDIUM-8 (CT-04 Step 3). PASS with one exception.
4. **TDD red-green-refactor is real and useful.** Every implementation task (PR-01..PO-04 except the deliberate planning doc PO-05) follows write-failing-test → verify FAIL → minimal implementation → verify PASS → review/commit boundary, with named commands and expected outcomes. Where TDD is forced (PR-02/PR-03/FD-03 docs and config tasks) the assertions are testable. PO-05's 4-step format is appropriate for a planning deliverable.
5. **Executability without hidden follow-up plans.** Each task names its files, interfaces, verification commands, and stop conditions; phase plans are *optional* expansions under FD-05 ("may be expanded"), not dependencies. The only hidden dependency is HIGH-1's engine selections, which must become R-items. PASS after HIGH-1 correction.
6. **Interface/type/function consistency across tasks.** Spot-checked: BE-06 status route (`/api/v1/tools/{tool}/tasks/{task_id}/status`, DEC-164/arch §13.5); BE-08 `GET /api/v1/capabilities` (C2/DEC-165); BE-03 signed-URL cap `min(remaining, 300 s)` (X2 A-8); BE-05 Lua-atomic queued→cancelled and XAUTOCLAIM-style reclaim (C1); TL-01 state vocabulary matches UX §13.1; PT-01 field schema matches X2 A-13/D3; OP-02 N-consecutive-failure / 2-region logic matches X2 A-10; VL-02 tool set matches X2 A-16; VL-03 viewports 375/768/1280/1440 matches B5; SEO-01 16-URL inventory baseline matches B4. PASS.
7. **Dependency ordering at the resolution-item level.** Verified each task's Consumes vs the R-item stop conditions and phase gate entries: R-03→BE-08/TL, R-07/R-08→BE-05, R-09→BE-04, R-10→SEC-03, R-11→SEC-05, R-12→OP-01, R-13→OP-04, R-16→SEO-01, R-18→PT-02, R-20→PT-03, R-21→CT-03, R-22/R-25→CT-04, R-23→VL-03, R-26→VL-05/PO-05 — all consistent. The three gate-entry omissions are MEDIUM-4, MEDIUM-5, and HIGH-2.
8. **Decision fidelity on emphasized items.** DEC-024 (precondition; MEDIUM-3 wording only), DEC-057 (HIGH-1 only), DEC-060/DEC-197 (plan-approval gate, lines 15 and 49), DEC-066 (PASS), DEC-143 (baseline constraint lines 29, VL-03), DEC-189 (one worker, line 22 and throughout), DEC-195 (Ghostscript lines 41, 725), DEC-192 (fail-closed sanitization routing lines 25, 740, 755), DEC-193/DEC-196 (gateway identity line 40 — exact base URL, `mypapyr` identifier, bearer auth — PASS; MEDIUM-8 only), DEC-194 (410 default lines 39, 1057), DEC-024/DEC-100/DEC-103 (one-month target, line 36).
9. **No invented numeric values.** Where the plan names numbers, they are decision-bound (3600 s retention, 300 s signed-URL cap, 16-MP ceiling, DEC-015 limits, one worker) or explicitly proposed defaults inside R-items (R-03 C2 table, R-04 A2 starting values, R-07/R-08/R-09 C1 defaults, R-11 C4 values, R-12 C5, R-13 C6). PASS.
10. **Spec coverage.** Section 9.1 maps UX §1-22 and Section 9.2 maps arch §1-26 plus appendices to phases/tasks. PASS (independent of the 9.3 decision-matrix gap in MEDIUM-LOW-11).
11. **Internal marker counts.** 313 checkboxes and 27 R-rows verified (Section 2), matching the stated expectations; the 314th raw occurrence is the line-3 inline-code mention.

## 5. Uncertainties and material unresolved owner questions

Recorded uncertainties (not defects): the trusted-edge header configuration detail (X1 M9, R-14), Redis version pin (X1 M11, R-09), Email Sending beta vs `email()` handler (X1 M16, R-20), pdf.js legacy floor (X1 M18, TL-06), Vercel analytics retention (X1 M23, PT-01), and the post-launch legacy-tool sequence (arch §25.3.18, PO-05) remain implementation-time re-checks assigned to consuming tasks — correct handling, no re-resolution needed here.

Material unresolved owner questions (beyond the by-design R-item dispositions):

1. DEC-024 exact numeric 90-day targets and baseline windows (Section 3.3; precondition of plan approval).
2. The HIGH-1 engine/queue-mechanism dispositions (queue data structure; pdf-lib/pdf.js/pikepdf/img2pdf/Pillow/pypdfium2 matrix), which currently lack any resolution vehicle.
3. R-01 repository root confirmation (correctly surfaced; must be recorded before PR-01).

## 6. Command evidence

All commands were read-only; run from `<workspace-root>`:

- `grep -c '^- \[ \]' docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` → 313
- `grep -oE '\- \[ \]' ... | wc -l` → 314 (includes line-3 inline-code mention)
- `grep -cE '^\| R-' ...` → 27
- `grep -inE 'TODO|TBD|FIXME|XXX|lorem ipsum|WIP' ...` → 2 hits, both self-verification prose (lines 42, 1410)
- `grep -in 'benchmark' ...` → 2 hits, both DEC-066 prohibition statements (lines 16, 1411)
- DEC set extraction and `comm -23` vs generated DEC-001..197 → missing: DEC-004, DEC-044, DEC-163, DEC-167; nothing outside the range
- `grep -inE 'redis streams|pikepdf|img2pdf|pillow|pypdfium|pdf-lib|pdf\.js|clamav|qpdf'` on both specs → no matches (exit 1); on the plan → 10 matches (lines 9, 102, 230, 612, 740, 755, 774, 789, 823, 827)
- `git -C papyr-reference rev-parse HEAD` → `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`
- `git -C papyr-reference status --porcelain` → empty, exit 0
- `git -C papyr-reference log --oneline -3` → `981c59a docs(fase2): mark STEP-F2-063 complete`; `8d0d09e test(fase2): schedule security scanning heartbeat`; `cce59e1 feat(fase2): wire security scanning agent`

## 7. `papyr-reference/` unchanged — evidence

HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`, empty porcelain (exit 0), top-of-history as above. This matches the HEAD recorded by PPR-VER-001, X1, X2, both specs, and the authoring evidence. No tracked or untracked change exists; this review performed no write to any `papyr-reference/` path (AGENTS.md compliance).

## 8. Files touched by this review

- Created: `audit-outputs/implementation-plan-cross-review-dec197.md` (this file).
- Modified: none. The plan, decision log, both specs, all audit/research files, `AGENTS.md`, and `papyr-reference/` remain untouched.

## 9. Markdown structure verification (manual, per ocs-markdown-autofix fallback)

The `bun run lint:md:fix` / `bun run lint:md` scripts are not available at the workspace root (no root package.json or bun scripts; consistent with arch §26.5). Manual structural pass performed on this file: ATX heading hierarchy `#` → `##` → `###` without jumps; all tables have header rows, separator rows, and equal column counts; list continuity in ordered lists; no TODO/TBD/FIXME/XXX/lorem/WIP tokens; checkbox-free deliverable (no task checkboxes needed).

## 10. Conclusion

**CONDITIONAL PASS.**

The master implementation plan is decision-faithful, benchmark-free, correctly gated, internally well-specified, and executable in phase order once corrected. It faithfully preserves DEC-024 as a precondition (with a wording fix), correctly surfaces R-01 rather than silently accepting the `papyr-rebuild/` root, keeps separately gated operations out of ordinary steps (with one CT-04/G-5 exception), and maintains strong task-level interface consistency and TDD discipline. It is NOT a FAIL because no defect is fatal to the plan's structure and every correction is deterministic and review-time.

Approval is conditional on the following, in order of materiality:

1. **Before approval:** resolve HIGH-1 (convert the elevated engine/queue selections into resolution rows with stop conditions and relabel the Tech Stack as proposals) and HIGH-2 (make the Phase 4/5 ordering and gate entries mutually consistent); supply the DEC-024 numeric targets and baseline windows as the R-27 disposition (MEDIUM-3).
2. **At approval or in the first review pass:** apply the MEDIUM-4 through MEDIUM-10 corrections (R-15 stop condition and Phase 2 gate; R-05 in the Phase 4 gate; PR-02 pytest tooling; unnamed verification commands; CT-04 G-5 gating; G-1 blog-automation carve-out; GitHub Actions contingency on R-02) and the LOW-11 through LOW-13 corrections.
3. **No further owner decisions are hidden:** the remaining unresolved items are the by-design R-item dispositions plus the three material questions in Section 5.

A chat-only summary is insufficient; this file is the primary deliverable.
