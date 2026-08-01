# Architecture Specification Revision: DEC-189 to DEC-196 and the Completed Cross-Domain Reconciliation

- **Date:** 2026-07-31
- **Author:** Sisyphus-Junior (executor subagent), revising the canonical Technical Architecture Specification per the owner's task authorization
- **Deliverable:** this file (primary delegated evidence, per AGENTS.md mandatory delegated-output persistence; a chat-only summary is insufficient)
- **Files changed (only these):**
  1. `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (the assigned specification; version bumped to 1.1)
  2. `<workspace-root>\audit-outputs\architecture-spec-revision-dec189-196.md` (this file)
- **Files verified unchanged:** `papyr-reference/` (read-only git status, porcelain output empty, exit 0; HEAD `981c59a`), `AGENTS.md`, `papyr-rebuild-decisions.md`, the Product and UX Design Specification, the reconciliation report, and all other `audit-outputs/` files.

---

## 1. Task and scope

Revise `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` to incorporate DEC-189 through DEC-196 and the final cross-domain reconciliation, per the owner's explicit authorization. Constraints honored:

- Modify only the assigned spec; write complete delegated evidence to this file. No other file was edited.
- No code, install, build, server, VPS, deploy, or git write operations; no web research. The only git command was a read-only `git status --porcelain` inside `papyr-reference/`.
- Never include an API key. The literal placeholder `<API_KEY>` is used in the spec only to name the `Authorization: Bearer <API_KEY>` scheme decided by DEC-196, exactly as the decision log itself writes it.
- Update the decision baseline to DEC-196; cite the completed reconciliation; preserve stable section and item numbering; narrow §25.3; update Appendix A.
- Preserve DEC-066 (no benchmark program), the no-implementation-authorization posture, and do not turn unaccepted category-A recommendations into requirements.

## 2. Inputs read in full

| Input | Path | Lines |
|---|---|---|
| Orchestrator rules | `<workspace-root>\AGENTS.md` | full |
| Decision log | `<workspace-root>\papyr-rebuild-decisions.md` | 2185-2330 (DEC-187 through DEC-196; full DEC-189-196 bodies) |
| Final cross-domain reconciliation | `<workspace-root>\audit-outputs\research\reconciliation-report.md` | full (299 lines) |
| Technical Architecture Specification | `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` | full (1188 lines pre-edit; 1203 post-edit) |
| Spec cross-review | `<workspace-root>\audit-outputs\spec-cross-review.md` | full (148 lines) |
| Spec corrections report | `<workspace-root>\audit-outputs\spec-corrections-report.md` | full (146 lines) |

## 3. Decisions incorporated (DEC-189 to DEC-196)

Evidence: `papyr-rebuild-decisions.md`, lines 2232-2330.

- **DEC-189** (lines 2232-2242): initial production backend runs one active PDF-processing worker with one job at a time; queueing, fairness, timeouts, and safety caps remain; worker limits, scanner settings, and other service memory budgets are designed around one concurrent processing job; additional concurrency requires capacity evidence and explicit approval; scaling follows DEC-098 with no benchmark program.
- **DEC-190** (lines 2244-2255): reaffirms DEC-022 no-prior-consent advertising as an accepted business/legal risk, not a compliance claim; no GDPR/PECR/UK GDPR/Swiss FADP compliance statements without qualified review; if binding terms, qualified legal review, or applicable law requires prior consent, Papyr must implement consent controls, use demonstrably non-tracking contextual ads, or suppress ads in affected regions; critical functionality and legal/support/status content must remain available if ad scripts are blocked.
- **DEC-191** (lines 2257-2266): Letter only when the trusted coarse edge country code is the United States or Canada; every other country, missing code, or invalid code selects A4; the active content locale does not independently select paper size; DEC-085/089 are the operative mechanism and fallback (resolves DEC-083 ambiguity); country code ephemeral, not persisted, not sent to analytics; UI may disclose the selected size but exposes no manual controls in the MVP.
- **DEC-192** (lines 2268-2279): when browser inspection detects PDF JavaScript, embedded attachments, launch actions, or other active content in a Merge or Split input, the job routes to the temporary server path for sanitization; no separate browser sanitization engine for the MVP; initial processing disclosure and live stages must truthfully show server processing may occur; server removes or neutralizes active content per DEC-090; if the maintained malware-scanner or sanitization path is unavailable, affected jobs fail closed rather than bypassing the control; ordinary safe files may still use the browser path within DEC-015 limits; no malware-free guarantee.
- **DEC-193** (lines 2281-2291): blog automation integrates `gpt5.6-sol` through the owner's OpenAI-compatible gateway at `https://router.budgezen.com/v1`, accessed only from server-side or protected automation environments; provider adapter isolates gateway configuration; credentials never enter client code, repository content, logs, generated articles, or analytics; remaining contract fields still require documentation; no authenticated call, account operation, or remote mutation is authorized.
- **DEC-194** (lines 2293-2303): legacy URLs for tools not in the five-tool MVP return an intentional localized 410 Gone by default; a specific URL may instead get a targeted relevant redirect only when credible traffic or intent evidence justifies it; the disposition inventory must identify every deferred tool URL and its localized variants; sitemap, navigation, canonical links, and internal links must exclude 410 URLs; the 410 experience explains the tool is unavailable and links to relevant live tools; meaningful traffic evidence may supersede a disposition through a later explicit decision.
- **DEC-195** (lines 2305-2316): Compress uses the official unmodified open-source Ghostscript executable as a separate server-side subprocess; no modification, linking, or embedding into proprietary code; Ghostscript obtained from an authoritative distribution, version-pinned, hardened, and invoked with safety flags including `-dSAFER`; Papyr must preserve Ghostscript copyright/AGPL notices and make the corresponding unmodified source available; must not claim the subprocess model eliminates every licensing obligation; exact production distribution and integration model requires a focused license review before public launch; any future modification/linking/embedding requires renewed review and owner approval; if review requires disclosure the owner does not accept, Compress moves to a permissive engine path or a commercial Ghostscript license before launch.
- **DEC-196** (lines 2318-2330): requests use base URL `https://router.budgezen.com/v1`, exact JSON model identifier `mypapyr`, and `Authorization: Bearer <API_KEY>`; API key stored only in protected server-side or automation secrets; the adapter must not substitute the public name `gpt5.6-sol` into API requests; no key may be committed, logged, returned to clients, inserted into generated MDX, or exposed through analytics; the gateway is owner-managed and treated as having no known application-level rate or spending limit; no internal spending guard at launch (owner-selected); reliability controls remain mandatory and separate from spending controls (bounded request timeout, finite retries with backoff, idempotency where supported, one bounded publication workflow, repeated-failure pause, kill switch per DEC-048/DEC-053); structured-output, tool-use, request/response deviations, effective context, retention, availability, and safety policy remain documentation items before blog automation technical design finalizes.

## 4. Reconciliation linkage (category-B questions Q1-Q7 to decisions)

Evidence: `audit-outputs/research/reconciliation-report.md`, Section 5 (category B) and Section 8 (collapsed questions).

| Reconciliation question | Resolved by | Where incorporated |
|---|---|---|
| Q1 Ghostscript licensing / Compress engine (B-1) | DEC-195 | Spec §11.2, §25.3.1, Appendix A row 11 |
| Q2 VPS memory envelope / worker count (B-2) | DEC-189 | §2.1, §2.3, §7.2, §9.2, §9.4, §16.4, §24.3, §25.3.2-3, Appendix A rows 2, 9, 24 |
| Q3 EEA/UK/CH ad consent (B-3) | DEC-190 | §4.5, §25.3.12-13, Appendix A rows 4, 25 |
| Q4 `gpt5.6-sol` provider contract (B-4 + D-1) | DEC-193, DEC-196 | §4.4, §18.1, §25.3.21, §25.4, Appendix A rows 4, 18, 25 |
| Q5 Regional paper policy (B-5) | DEC-191 | §5.3, §11.5, §25.3.7, Appendix A rows 5, 11 |
| Q6 Browser-path sanitization + fail-closed scanner (B-6) | DEC-192 | §10.3, §10.4, §11.3-11.4, §17.3, §17.5, §25.3.8, §25.3.17, Appendix A rows 10, 11, 17, 25 |
| Q7 Legacy URL dispositions (B-7) | DEC-194 | §4.2, §25.3.15, §25.4, Appendix A row 4 |

Category-A recommendations (engine-matrix pairings such as pikepdf, img2pdf, pypdfium2, pdf.js, pdf-lib; queue framework details; monitoring stack details) remain recommendations and were **not** elevated into requirements anywhere in the spec. Category-C defaults and category-D source/contract blockers remain recorded as such in §25.1 and §25.3. DEC-066 (no benchmark program) is untouched and restated in §25.1 and the unchanged testing sections.

## 5. Complete change log (specification edits)

The spec was edited from 1188 to 1203 lines. Section numbers and the §25.3 item numbers 1-21 were preserved exactly (no renumbering), consistent with the requirement to preserve stable numbering and with the decision log's Open decisions section, which references specific §25.3 numbers (e.g., §25.3.1-5, §25.3.7-21).

1. **Header table:** Version `1.0 (draft for owner review)` to `1.1 (incorporates DEC-189 to DEC-196 and the completed cross-domain reconciliation)`; Decision baseline `DEC-001 through DEC-187` to `DEC-001 through DEC-196`. Status line left unchanged (DEC-188 approval is recorded in §1.1 and §25.4; changing the status wording was outside the task's stated scope).
2. **§1.1 Status:** added paragraph recording that the final cross-domain reconciliation (`audit-outputs/research/reconciliation-report.md`) is complete, its category-B questions resolved through DEC-189 to DEC-196, and that these are documentation-level refinements under DEC-188 that do not authorize implementation, VPS access, gateway access, account operations, or remote mutation.
3. **§1.2 Scope:** added a bullet listing the owner resolutions of the reconciliation (DEC-189 to DEC-196).
4. **§1.5 Design versus implementation authorization:** added a bullet that DEC-189 to DEC-196 are documentation-level refinements with no implementation authorization.
5. **§2.1 topology table:** Compute row now reads "bounded PDF worker (one active at launch, DEC-189)".
6. **§2.3 components:** Workers row now states one active worker executing one concurrent job at launch (DEC-189).
7. **§4.2 routing and localization:** added DEC-194 sentence: deferred legacy tool URLs returning 410 are excluded from sitemap, navigation, canonical links, and internal links.
8. **§4.4 frontend config:** client-secrets citation extended with DEC-193.
9. **§4.5 analytics and advertising:** rewrote the advertising bullet to state the reaffirmed accepted business/legal risk, the no-compliance-claim rule, the mandatory-consent consequence clause, and ad-block resilience (DEC-190); third-party script bullet citation extended with DEC-190.
10. **§5.3 edge-derived country context:** rewrote the opening paragraph to the exact DEC-191 rule (US/CA Letter only, A4 otherwise including missing/invalid, locale never decides); ephemeral bullet now also states the country code is never sent to analytics.
11. **§7.2 service inventory:** workers row now "one active worker, one concurrent job at launch (DEC-189)" (was "one or more replicas").
12. **§9.2 bounds:** added the DEC-189 bullet (one active worker, one concurrent job; memory budgets designed around one concurrent job; valid jobs may wait in the bounded fair queue; additional concurrency needs capacity evidence and approval).
13. **§9.4 queueing under pressure:** parenthetical noting the one-active-worker posture is the expected busy condition during load (DEC-189).
14. **§10.3 automatic server fallback:** added DEC-192 bullet (active-content Merge/Split inputs route to the temporary server sanitization path; no separate browser sanitization engine; safe files may still use the browser path).
15. **§10.4 disclosure:** added that the initial processing disclosure and live stages must truthfully show server processing may occur, including for active-content jobs routed under DEC-192.
16. **§11.2 Compress PDF:** replaced the "engine selection is an implementation-level choice" sentence with the DEC-195 engine decision (official unmodified Ghostscript subprocess, `-dSAFER`, no embedding, notice/source obligations, focused license review before launch, permissive/commercial fallback).
17. **§11.3 Merge PDF:** added DEC-192 routing bullet.
18. **§11.4 Split PDF:** appended DEC-192 routing sentence to the browser-first/server-fallback bullet.
19. **§11.5 JPG to PDF:** rewrote the paper bullet to the DEC-191 rule and added "no manual paper controls (DEC-191)".
20. **§16.4 scaling policy:** added the one-active-worker initial posture and the capacity-evidence/approval gate for added concurrency (DEC-189, DEC-098).
21. **§17.3 active-content sanitization:** added the DEC-192 routing bullet.
22. **§17.5 malware scanning:** added the fail-closed requirement when the maintained scanner or sanitization path is unavailable (DEC-192).
23. **§18.1 secrets management:** added the blog-automation gateway key rule (DEC-193, DEC-196): protected server-side/automation secrets only; never committed, logged, returned to clients, inserted into MDX, or exposed through analytics.
24. **§24.3 operating cadences:** VPS-optimization row source now `DEC-098, DEC-189`.
25. **§25.1 research gate:** added the reconciliation-status paragraph: briefs verified and reconciled; category-B resolved by DEC-189 to DEC-196; category-A recommendations remain recommendations (DEC-057), category-C defaults remain conservative choices (DEC-066), and category-D inputs remain required.
26. **§25.3 unresolved items:** intro rewritten to record resolved-vs-remaining scope; items 1, 2, 3, 7, 8, 12, 13, 15, 17, 21 narrowed with explicit "Resolved:" and "Remaining:" structure. All 21 numbers preserved.
27. **§25.4 owner decisions still required:** replaced the stale spec-approval bullet with review of this revision under DEC-188; added concurrency-approval (DEC-189), per-URL deviation (DEC-194), and blog-design approval with no gateway access authorized (DEC-196).
28. **§26.2 contradiction check:** baseline updated to DEC-001 to DEC-196; added DEC-083-by-DEC-191 as an example of supersession and a reconciliation-consistency statement (Q1-Q7 resolved, no contradiction remains).
29. **§26.4 scope check:** noted the DEC-189 to DEC-196 owner resolutions are covered.
30. **§26.5 tooling limitations:** added the second revision-pass record pointing to this file.
31. **Appendix A decision map:** rows 1, 2, 4, 5, 9, 10, 11, 17, 18, 24, 25 updated to add the governing DEC-189 to DEC-196 citations matching the sections actually changed.

## 6. Deliberate non-changes

- **Decision log, UX spec, reconciliation report, AGENTS.md, research briefs, papyr-reference:** not modified (task prohibition). The decision log's Open decisions section (written at the DEC-187 baseline) still lists items that DEC-189 to DEC-196 partially resolve (e.g., Open items 2-4, 10, 12); the architecture spec §25.3 is now the canonical record of the resolved scope. This is a documented limitation, not an edit opportunity.
- **Category-A recommendations** (permissive engine pairings, queue framework choice, monitoring stack, backup tooling): left out of the spec; they remain recommendations pending owner approval (DEC-057).
- **Status line** "Draft, ready for owner review": kept; DEC-188 approval is reflected in §1.1 and §25.4 instead.
- **§1.1 historical wording** "established through DEC-001 to DEC-182": kept as the description of the DEC-183 design scope.
- **§26.5 first-pass record** referencing `audit-outputs/spec-corrections-report.md`: kept, with the new record appended after it.

## 7. Verification performed

1. **Placeholder scan:** `grep -iE 'TODO|TBD|FIXME|XXX|PLACEHOLDER|lorem'` over the spec after edits. Only hit: the §26.1 self-review sentence that states no such tokens exist (the word "placeholder" appears in that prose describing the scan). No leftover tokens. The `<API_KEY>` token in §25.3.21 and the legacy `<sha>` token in §19.4 are deliberate notation mirroring the decision log's own `Authorization: Bearer <API_KEY>` wording and the legacy workflow's digest capture; neither is an unfinished placeholder.
2. **Baseline consistency:** grep confirmed no remaining `DEC-001 to DEC-187` / `through DEC-187` / `to DEC-187` baseline statements; the only remaining DEC-186/DEC-187 mentions are the accepted JPG-to-PDF formats decision (§11.5) and the historical corrections record (§26.5). Header and §26.2 now state DEC-196.
3. **DEC-189-196 coverage grep:** all eight decisions appear with correct, decision-faithful wording in the spec (57 citation-bearing lines; see the change log for placement).
4. **List continuity:** §25.3 items 1-21 continuous with no renumbering (verified by read-back of lines 1072-1092). UX-spec cross-reference in item 21 (`§21.21`) unchanged and valid.
5. **Cross-references:** new in-spec references resolve: §25.3.7 points to Section 5.3 (exists); §25.3.21 and §11.2 point to Section 25 (exists); reconciliation path `audit-outputs/research/reconciliation-report.md` exists; this evidence file path referenced in §26.5 now exists. No heading was renamed, so no pre-existing reference broke.
6. **Markdown structure:** ATX headings, table rows, and ordered lists were checked manually by read-back. The two markdown tooling layers documented in §26.5 remain unavailable: there is no root `package.json`/bun configuration exposing `bun run lint:md:fix` / `lint:md` (confirmed by directory listing), and no Markdown LSP server is configured (the corrections report recorded the same limitation). No tooling was installed.
7. **`papyr-reference/` unchanged:** `git -C papyr-reference status --porcelain` returned empty output with exit 0; HEAD `981c59a` (`981c59a docs(fase2): mark STEP-F2-063 complete`), identical to the HEAD recorded by the reconciliation report and the corrections report.
8. **No API key:** the only credential-like string added is the literal `Authorization: Bearer <API_KEY>` scheme name taken verbatim from DEC-196; no actual key or value appears in the spec or in this file.
9. **DEC-066 preservation:** the spec's no-benchmark statements (§1.3, §7.4, §9.2, §16.4, §22.1, §22.5, §25.1, §26.1) are untouched; the new §25.1 text explicitly restates that category-C defaults are conservative choices adjustable from production observability.
10. **No implementation authorization:** §1.1, §1.5, §25.1, and §25.4 all restate that this revision and DEC-189 to DEC-196 do not authorize implementation, VPS/gateway access, account operations, or remote mutation.

## 8. Uncertainties and unresolved questions

- The decision log's Open decisions section and its §25.3 cross-references were written at the DEC-187 baseline; DEC-189 to DEC-196 resolve several listed items. The log was not edited (task prohibition and AGENTS.md append-only rule); the architecture spec now records the resolved scope. If the owner later wants the log updated, that is a separate append-only task.
- Item 21 remains the last open provider path: DEC-193/196 supply the contract identity and authentication but the capability fields (schema deviations, structured-output/tool-use behavior, effective context, retention, availability, safety policy) remain owner-supplied documentation before the blog automation technical design finalizes (reconciliation D-1, now partially closed).
- The status line of the spec header still reads "Draft, ready for owner review" despite DEC-188 approval; kept deliberately (see Section 6). Owner may choose to amend.
- A repo-level `bun run lint:md` pass would be the authoritative markdown lint once tooling exists; not runnable here and none was installed.

## 9. Verification statement

- Only the assigned specification and this evidence file were written. `papyr-reference/` was only read (git status, empty, exit 0) and remains unchanged. No decision log, UX spec, reconciliation report, AGENTS.md, research brief, or other audit file was modified.
- No implementation, scaffolding, installs, builds, servers, VPS/SSH access, deployment, provider authentication, or remote mutation was performed. No web research was performed. No API key or secret value is contained in either file produced by this task.
- This file is the primary deliverable; a chat-only summary is insufficient.
