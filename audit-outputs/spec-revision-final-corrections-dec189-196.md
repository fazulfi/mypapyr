# Spec Revision Final Corrections: DEC-189 through DEC-196

- **Date:** 2026-07-31
- **Author:** subagent (correction executor), delegated by Sisyphus
- **Deliverable:** this file (primary deliverable, per AGENTS.md mandatory delegated-output persistence); a chat-only summary is insufficient
- **Basis:** `audit-outputs/spec-revision-cross-review-dec189-196.md` (CONDITIONAL PASS verdict), which requires exactly M-1, L-1, L-2, and L-3 before final verification and owner approval.
- **Scope:** Apply only the four deterministic required corrections to exactly three files: `papyr-rebuild-decisions.md`, `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md`, and `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`. No optional editorial items (O-1, O-2, O-3) were applied except where O-2 is naturally absorbed by the M-1 intro rewrite (see Section 2, M-1).
- **Files touched this task:** the three listed source files (edited) and this audit file (created). No other file was created, edited, or deleted.

---

## 1. Method

1. Read `AGENTS.md` first (governing orchestrator rules, read at task start).
2. Read the cross-review verdict in full.
3. Read the decision log in full through DEC-196 (2330 lines), then re-read the Open decisions section and DEC-188 through DEC-196 exactly.
4. Read both specs at the exact target locations: UX header line 5 and §1 line 15; arch header line 10, §4.5 line 242, §25.3.1 line 1072, §25.3.12 line 1083.
5. Applied the four deterministic corrections via exact-string edits (Edit tool), then read back every changed region to verify.
6. Ran the verification checks in Section 5 (placeholder scan, secret scan, baseline scan, gate-presence scan, numbering scan, `papyr-reference` status).
7. No implementation, installs, builds, servers, Docker, VPS/SSH access, git writes, provider authentication, or remote mutation was performed. The only git command was a read-only `git status --porcelain` plus `git rev-parse HEAD` inside `papyr-reference/`.

## 2. Corrections applied (before/after, exact locations)

### M-1 — Decision log Open decisions status refresh (Medium)

- **File:** `papyr-rebuild-decisions.md`
- **Pre-edit locations:** section lines 2199-2219 (intro at 2201; item 2 at 2204; item 3 at 2205; item 4 at 2206; item 10 at 2212; item 12 at 2214; closing note at 2219).
- **Nature of edit:** status-list refresh only. No DEC-NNN decision history or body was altered. DEC-188 through DEC-196 remain untouched at lines 2221-2330 (verified positions unchanged: DEC-188 at 2221, DEC-189 at 2232, DEC-190 at 2244, DEC-191 at 2257, DEC-192 at 2268, DEC-193 at 2281, DEC-194 at 2293, DEC-195 at 2305, DEC-196 at 2318). Items 1, 5, 6, 7, 8, 9, 11, 13, 14, 15 and the closing sentence were preserved verbatim. This matches the corrections-report precedent of replacing the status section at the DEC-187 baseline without touching decision history.

- **Intro, before (line 2201):**
  "The discovery-era topics previously listed here (primary user segments, MVP tool set, processing boundaries, storage policy, limits and abuse prevention, privacy and advertising, brand and naming, SEO strategy, infrastructure and operations, analytics and launch criteria, and the Guinevere/OpenClaw disposition) have been resolved through DEC-001 through DEC-187. The genuinely unresolved or research-gated details that remain are listed below, each with its governing decisions and its canonical home in the two design specifications (Product and UX Design Specification Section 21; Technical Architecture Specification Section 25.3):"
- **Intro, after:** baseline changed to "DEC-001 through DEC-196", and two sentences added: "This section is a status list, not decision history; DEC-188 through DEC-196 are appended after it in the log, and the scope they resolved is recorded in the two design specifications (Product and UX Design Specification Section 21; Technical Architecture Specification Section 25.3)." This acknowledges the DEC-001 through DEC-196 baseline per M-1 and notes the append-order artifact per O-2 (which the cross-review folded into M-1's natural edit).

- **Item 2, before (line 2204):** "Compress engine selection, license validation, and the premium-screen profile thresholds (DEC-014, DEC-059; architecture spec §25.3.1 and §25.3.6)."
- **Item 2, after:** narrowed to "Compress license validation and the premium-screen profile thresholds", with "Engine selection is resolved: the official unmodified open-source Ghostscript executable runs as a separate hardened server-side subprocess" and DEC-195 added to the governing citations. Residuals match arch §25.3.1's "Remaining:" scope.

- **Item 3, before (line 2205):** "`gpt5.6-sol` provider documentation before technical design finalization: base URL, authentication, request/response schema, structured-output and tool-use capabilities, rate limits, cost, context limits, retry behavior, data retention, and availability (DEC-051; UX spec §21.21, architecture spec §25.3.21)."
- **Item 3, after:** narrowed to the remaining capability fields: "request and response schema deviations, structured-output and tool-use behavior, effective context, data retention, availability, and applicable safety/compliance policy", with "The base URL, exact gateway-facing model identifier, and authentication scheme are resolved" and DEC-193, DEC-196 added. Residual matches DEC-196's final consequence and arch §25.3.21's "Remaining capability documentation".

- **Item 4, before (line 2206):** "Paper-standard regional mapping where locale alone does not identify Letter versus A4 (DEC-083, DEC-085, DEC-089; UX spec §21.3, architecture spec §25.3.7)."
- **Item 4, after:** narrowed to "Paper-standard mapping implementation detail: which trusted headers carry the coarse edge country code and how spoofed or untrusted values are rejected", with "The region rule is resolved: Letter only for trusted US/CA edge codes, every other code selects A4, locale never decides" and DEC-191 added. Residual matches arch §25.3.7's "Remaining:" scope and Section 5.3.

- **Item 10, before (line 2212):** "Adsterra script, cookie, identifier, and regional behavior review against current terms and applicable law, including whether prior consent is required (DEC-022, DEC-045; UX spec §21.9, architecture spec §25.3.12)."
- **Item 10, after:** dropped "including whether prior consent is required" (resolved by DEC-190) and added "The prior-consent position is reaffirmed: approved light banner/native advertising loads without prior consent in all launch regions as an accepted risk" with DEC-190 added. The provider review itself remains open, matching arch §25.3.12.

- **Item 12, before (line 2214):** "Worker bounds, fair-scheduling parameters, Redis persistence mode, malware scanner selection, rate-limit and fair-use thresholds, monitoring and alert thresholds, and backup configuration (DEC-019, DEC-020, DEC-035, DEC-137, DEC-171, DEC-173, DEC-174, DEC-180, DEC-181, DEC-182; architecture spec §25.3.3-5, §25.3.8-10, §25.3.20)."
- **Item 12, after:** replaced "Worker bounds" with "Per-worker memory and time bounds" and added "Worker count is resolved: one active PDF-processing worker with one job at a time at launch" with DEC-189 added. Residual matches arch §25.3.3's "Remaining:" scope.

- **Post-edit locations:** identical line numbers (intro 2201; items 2, 3, 4, 10, 12 at 2204, 2205, 2206, 2212, 2214; closing note 2219), verified by read-back.

### L-1 — Add "ePrivacy" to the DEC-190 enumeration (Low)

- **File:** `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`
- **Locations:** §4.5 line 242; §25.3.12 line 1083 (both unchanged in position).
- **Before (both):** "Papyr must not state that the approach is GDPR, PECR, UK GDPR, or Swiss FADP compliant without qualified review"
- **After (both):** "Papyr must not state that the approach is GDPR, PECR, ePrivacy, UK GDPR, or Swiss FADP compliant without qualified review"
- **Basis:** DEC-190 (log line 2252) enumerates "GDPR, PECR, ePrivacy, UK GDPR, or Swiss FADP" verbatim; UX §14.8 already includes ePrivacy. Grep confirmed exactly two occurrences of the pre-edit phrase in the specs and zero remaining after the change.

### L-2 — Align both specs' Status fields with DEC-188 (Low)

- **UX header, before (line 5):** "- **Status:** For owner review (approved for writing by DEC-183; not an implementation authorization)"
- **UX header, after:** "- **Status:** Approved by DEC-188; revised to incorporate DEC-189 to DEC-196; not an implementation authorization"
- **UX §1 opening sentence, before (line 15):** "This specification is written and submitted for owner review."
- **UX §1 opening sentence, after:** "This specification is approved by DEC-188 and revised to incorporate DEC-189 to DEC-196; it is not an implementation authorization."
- **Arch header, before (line 10):** "| Status | Draft, ready for owner review; not an implementation authorization |"
- **Arch header, after:** "| Status | Approved by DEC-188; revised to incorporate DEC-189 to DEC-196; not an implementation authorization |"
- **Consistency:** both specs now use the identical Status phrasing "Approved by DEC-188; revised to incorporate DEC-189 to DEC-196; not an implementation authorization" (arch as a table cell, UX as a bullet). The "not an implementation authorization" clause is preserved verbatim in every location. This is consistent with the specs' own §1.1/§25.4 text, which already recorded approval under DEC-188, and with DEC-188's consequence that approval "does not authorize product implementation".

### L-3 — Restate DEC-195's future-modification gate (Low)

- **File:** `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`
- **Location:** §25.3.1 line 1072 (unchanged in position; appended at the end of item 1, after the "Remaining:" scope, so item numbering is untouched).
- **Before:** "...with a permissive engine path or a commercial Ghostscript license as the fallback if the review outcome is unacceptable (DEC-195, DEC-059, DEC-056)."
- **After:** same sentence, plus " Any future Ghostscript modification, linking, embedding, or architectural integration requires renewed license review and owner approval (DEC-195)."
- **Basis:** DEC-195 (log line 2315) verbatim.

## 3. Optional items not applied

- **O-1** (arch §19.4 `<sha>` notation): not applied, explicitly non-required.
- **O-2** (log ordering note): absorbed into the M-1 intro rewrite as the cross-review suggested; no separate edit.
- **O-3** (DEC-189 citation in arch §25.3.8): not applied, explicitly non-required.

## 4. Deliberate non-changes

- No DEC-NNN decision history or body was modified; the log edits were confined to the status section (lines 2199-2219).
- No decision was superseded; every DEC-189 through DEC-196 body is byte-identical in position and content (headers re-verified at lines 2221-2318).
- No stale baseline phrase "through DEC-001 through DEC-187" remains in the three touched files (grep verified; see Section 5).
- Stable numbering preserved: UX sections 1-22 and arch sections 1-26 with §25.3 items 1-21 continuous (items 13-21 re-verified at lines 1084-1092).
- DEC-066 (no benchmark program), DEC-143 (existing visual baseline), and the DEC-060/DEC-185 implementation-block gates remain present and untouched in both specs (counts in Section 5).
- No placeholder tokens, no secrets, no benchmark program, no compliance claim, and no implementation authorization were introduced by this correction pass.

## 5. Verification (commands and results)

| # | Check | Command / method | Result |
|---|---|---|---|
| 1 | `papyr-reference` clean at same HEAD | `git -C papyr-reference status --porcelain` (read-only); `git -C papyr-reference rev-parse HEAD` | Porcelain output empty (exit 0). HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` = `981c59a docs(fase2): mark STEP-F2-063 complete`, matching the cross-review §9, reconciliation report X2 §11, corrections report §4, and both revision evidence files. |
| 2 | Placeholder scan (TODO/TBD/FIXME/lorem/WIP) | Grep across both specs | Only self-descriptive prose: arch §26.1 line 1110 is the spec's own "no placeholder tokens" statement (pre-existing, verified by the cross-review). No new or remaining placeholder token. |
| 3 | Placeholder scan XXX | Grep across both specs | Zero matches. |
| 4 | Secret scan | Grep patterns `sk-[A-Za-z0-9]`, `AKIA[0-9A-Z]{16}`, `Bearer\s+[A-Za-z0-9_-]{8,}` across both specs | One match for `sk-` at arch line 656: "task-access" (DEC-072 opaque task-access state), a false positive on the substring `sk-a` in "task-access". No `AKIA`, no `Bearer <value>` (the only Bearer token is the DEC-196 scheme name `Authorization: Bearer <API_KEY>` at arch §25.3.21, cross-referenced from UX §21.21). No actual secret value exists. |
| 5 | Baseline statement | Grep "through DEC-001 through DEC-187" repo-wide | Remaining matches only in `audit-outputs/spec-revision-cross-review-dec189-196.md` (quoted finding text) and `audit-outputs/research/track-b_evidence-decisions.md` (historical evidence snapshot, out of scope, not edited). The decision log itself is refreshed. |
| 6 | DEC-188-196 bodies intact | Grep `^## DEC-(188..196)` | All 9 headers present at lines 2221-2318, positions unchanged. Edits were confined to the preceding status section by construction. |
| 7 | Gate preservation | Grep counts across both specs | DEC-066: 25 matches (arch 20, UX 5). DEC-143: 13 matches (UX 11, arch 2). DEC-060/DEC-185: 22 matches (arch 15, UX 7). All pre-existing, untouched. |
| 8 | Numbering stability | Read-back of §25.3 and Open decisions | Arch §25.3 items 1-21 continuous (lines 1072-1092); L-3 sentence appended within item 1 without renumbering. Decision log items 1-15 continuous with unchanged numbering. |
| 9 | L-1 phrase | Grep "GDPR, PECR, UK GDPR" | Zero remaining occurrences; both locations now read "GDPR, PECR, ePrivacy, UK GDPR, or Swiss FADP". |
| 10 | Edit read-back | Read tool on every changed line | All six decision-log lines, UX lines 5 and 15, and arch lines 10, 242, 1072, 1083 verified post-edit (Section 2). |

## 6. Tooling limitations

- `bun run lint:md:fix` and `bun run lint:md` could not be executed: verified by directory listing that `<workspace-root>` has no root `package.json`, `bun.lock`, `bun.lockb`, or `node_modules` exposing those scripts (command result in Section 5, row 1 context). No Markdown LSP server is configured. Per the OCS markdown-autofix skill's manual-fallback allowance and the architecture spec's own §26.5 note, Markdown conventions (ATX headings, continuous ordered lists, well-formed tables) were enforced manually; the changed content uses only ATX headings, continuous ordered numbering, and prose bullets consistent with the existing files.
- A repo-level `lint:md` run after tooling exists would remain the authoritative lint pass.

## 7. Uncertainties and unresolved questions

1. **Status wording (L-2):** the exact Status phrasing was chosen to be identical across both specs and to keep the "not an implementation authorization" clause verbatim, per the cross-review's deterministic correction. The architecture revision evidence previously recorded the old Status line as a deliberate non-change and an owner choice; if the owner prefers different wording (for example "Approved by DEC-188; version 1.1 incorporates DEC-189 to DEC-196"), it is a cosmetic-only follow-up that does not affect the approval state recorded in the log.
2. **Out-of-scope stale text:** `audit-outputs/research/track-b_evidence-decisions.md` line 1862 still contains the historical "through DEC-001 through DEC-187" Open decisions text. That file is a prior research evidence snapshot and was explicitly out of scope; it was not edited. It is noted here as a known historical artifact.
3. **Markdown lint:** full markdownlint verification remains impossible without tooling; manual structural checks passed (Section 5 rows 2-4, 8).
4. **Cross-review line-citation delta:** the cross-review cited item 10 at line 2211; the actual pre-edit line was 2212 (verified in this task's full-file read). This one-line delta does not affect any finding or correction.
5. **Legacy citations:** no legacy `papyr-reference/` citations were touched by any edit; the corrections are documentation-level wording changes only.

## 8. Verification statement

- Exactly the four required corrections (M-1, L-1, L-2, L-3) were applied to exactly the three assigned files. No optional O-1/O-3 edit was applied; O-2 was absorbed into the M-1 intro as the cross-review recommended.
- No DEC-NNN decision history or body was changed, and no decision was superseded. DEC-188 through DEC-196 are intact at lines 2221-2318.
- `papyr-reference/` is clean at HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`; no command or write touched that directory.
- No implementation, scaffolding, installs, builds, servers, VPS/SSH access, deployment, provider authentication, account operations, or remote mutation was performed. No web research was performed.
- No API key, token, or secret value appears in this file; the `<API_KEY>` notation referenced above is the DEC-196 scheme name only.
- This file is the primary deliverable; a chat-only summary is insufficient.

The two revised specifications and the decision log are now consistent with each other and with the DEC-001 through DEC-196 baseline. Per the cross-review verdict, the docs are ready for final verification and owner approval of the amendment.
