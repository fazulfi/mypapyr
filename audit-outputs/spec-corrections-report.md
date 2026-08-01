# Spec Corrections Report: Owner Decisions and Cross-Review Fixes

- **Date:** 2026-07-31
- **Author:** Sisyphus-Junior (executor subagent), applying owner-confirmed decisions and the deterministic corrections from `audit-outputs/spec-cross-review.md`
- **Deliverable:** this file (primary audit deliverable, per AGENTS.md mandatory delegated-output persistence)
- **Files changed (only these):**
  1. `<workspace-root>\papyr-rebuild-decisions.md`
  2. `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md`
  3. `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md`
- **Files verified unchanged:** `papyr-reference/` (read-only git status, porcelain output empty, exit 0), `AGENTS.md`, all other `audit-outputs/` files.
- **Tooling note:** No installs, builds, servers, VPS access, Docker operations, git writes, or network-changing commands were run. The only git command was a read-only `git status --porcelain` inside `papyr-reference/`.

---

## 1. Owner decisions applied (appended, history preserved)

Prior decision history was not rewritten. Two new decisions were appended after DEC-185 and before the Open decisions section:

### DEC-186 — PDF-to-JPG page selection preserves duplicates and requested order

- Status: Accepted.
- Content: repeated and overlapping page selections are preserved as independent outputs in user-entered order, matching DEC-077/DEC-078 Split semantics; outputs, ZIP, manifest, and names must disambiguate duplicates; range syntax/validation per DEC-038; preview shows duplicated membership and effective sequence.

### DEC-187 — JPG-to-PDF officially accepts JPG, JPEG, PNG, and WebP at launch

- Status: Accepted.
- Content: JPG/JPEG, PNG, and WebP accepted at launch; user-facing name remains "JPG to PDF"; validation by actual bytes and DEC-093 safety controls; DEC-088 threat blocking applies; copy/FAQ/legal disclosures state actual formats.

### Open decisions section (stale content replaced, not decision history)

The former section claimed 11 discovery-era topics "remain unresolved" (user segments, MVP tool set, processing boundaries, storage, limits, privacy/advertising, brand, SEO, infrastructure, analytics, Guinevere disposition). All of those are resolved by DEC-001 through DEC-187. The section now states that and lists only genuinely unresolved or research-gated details, each with governing decisions and canonical homes in the two specs (UX spec §21; arch spec §25.3). Nothing new was invented: every listed item exists in the specs or the decision log, and each remains research-gated under DEC-054 through DEC-057 and DEC-060.

## 2. Cross-review corrections applied

### H-1 (High): Architecture non-goal Redis/Telegram contradiction

- **Location:** arch spec §1.3 (non-goals bullet).
- **Before:** "Guinevere or OpenClaw runtime, agents, BullMQ, PostgreSQL/Drizzle, Telegram reporting bots, or decision-engine infrastructure (DEC-016)."
- **After:** "Guinevere/OpenClaw runtime and agents, BullMQ, PostgreSQL/Drizzle, Guinevere's Telegram reporting bots, and persona or decision-engine infrastructure (DEC-016). Queue Redis remains governed by DEC-019 (§8), and Telegram operational incident alerts by DEC-180 (§20)."
- Effect: the exclusion now names Guinevere's reporting bots specifically, includes persona infrastructure, and explicitly preserves queue Redis (DEC-019) and Telegram operational alerts (DEC-180), matching §2.3, §7.2, §8.1, and §20.3.

### M-1 (Medium): Superseded DEC-063 citation removed

- **Location:** arch spec §6.1 (VPS authorization statement).
- **Before:** "(DEC-063, DEC-172, DEC-160)".
- **After:** "(DEC-172, DEC-160)".
- Note: DEC-066 was deliberately not added. It is the decision that superseded the benchmark-related entries (including DEC-063), but it is not contextually relevant to a VPS-access authorization statement; DEC-172 ("This decision does not authorize current VPS access or configuration changes") and DEC-160 are the governing citations. DEC-063 now appears only in §26.2's historical-supersession note, which is correct.

### M-2 (Medium): gpt5.6-sol provider documentation gate added

- **Location:** UX spec §21.21 (new item) and arch spec §25.3.21 (new item, cross-referencing UX).
- Content (matches DEC-051 consequences verbatim scope): base URL, authentication, request/response schema, structured-output support, tool-use capabilities, rate limits, cost, context limits, retry behavior, data retention, and availability must be documented before technical design finalization.
- Also added to the decision log's Open decisions section (item 3) and to arch Appendix A row 25 (DEC-051).

### M-3 (Medium): PDF-to-JPG range semantics resolved per DEC-186

- **Location:** UX spec §12.5.4 (Ready-state step), §12.5.8 (done card), §12.5 output naming, §20.4.5 (acceptance criterion), and arch spec §11.6 (new bullet).
- The "same corrected order/overlap semantics as Split where they apply (DEC-038)" hedge is replaced by explicit duplicate-preserving, order-preserving semantics (DEC-186) with syntax/validation per DEC-038, and unambiguous output/ZIP/manifest/naming. Arch §11.6 now states the mechanism obligation (disambiguation and order in outputs, ZIP contents, individual downloads, manifest) so the two specs no longer diverge by omission.

### M-4 (Medium): Progress vocabulary reconciled

- Canonical stages (DEC-033): preparing, uploading, queued, processing, finalizing, ready.
- **UX spec §13.1:** the state table now uses Preparing (was Loading) and adds Finalizing; the "Loading card" rows in §12.3 and §12.5 flows were renamed to "Preparing card". A mapping note states that Idle, Ready (configuration), Ready (done), and Error are UI states framing the lifecycle (Ready/Ready-done both map to the lifecycle's ready stage), and that arch §13.2 uses the same vocabulary.
- **Arch spec §13.2:** now states it is the shared canonical vocabulary with UX §13.1, which defines the user-facing state set including Idle/Ready/Error framing states.
- Error, Idle, and configuration states are preserved in both.

### L-1 (Low): Defect count fixed

- **Location:** UX spec §4 (audit list).
- "14 defect items D1-D13" → "13 defect items D1-D13" (matches the audit's 13 items and the spec's own D1-D13 references).

### L-2 (Low): pre-benchmark wording removed from both specs

- **UX §21.1:** now "Conservative defaults documented as design and safety choices, adjusted from production observations rather than benchmark-proven, and the procedure for raising them are technical-design responsibilities (DEC-066)."
- **Arch §14.2:** now "Conservative design and safety defaults, adjusted from production observations rather than benchmark-proven, and the procedure for safely raising limits are documented during technical design (DEC-034, DEC-066)."
- **Arch §25.3.2:** now "as conservative design and safety defaults with a documented raising procedure, adjusted from production observations rather than benchmark-proven (DEC-034, DEC-066)."
- Residual "pre-benchmark" occurrence: none in either spec. The only remaining occurrence in the repository is `papyr-rebuild-decisions.md` line 437 inside DEC-034's accepted-decision text. That is decision history and was intentionally not rewritten (append-only rule); DEC-066 already declares benchmark references in the log to be historical context overridden where inconsistent.

### L-3 (Low): Missing accepted-requirement fragments added

- **UX §15.3 (Support):** contact submissions follow documented retention rules with redaction-safe error handling (DEC-046); legally required operator/contact information remains provided where applicable (DEC-110).
- **UX §18.2 (Safe rejection):** false-positive handling and support escalation never require users to email or upload the rejected document through the contact form or any other channel (DEC-088).
- **UX §17 (analytics/privacy boundaries, item 11):** regional monitoring and launch communication distinguish US, LATAM, and Europe sufficiently to identify material failures without prohibited profiling (DEC-104).
- **Arch §20.1:** regional monitoring statement added (DEC-104).
- **Arch §23.2 (prohibited-data register):** submitted contact-form content in error states is redaction-safe; submissions minimized, retained under documented rules, deleted per policy (DEC-046, DEC-050).
- **Arch §23.3 (retention summary):** new row "Contact and result-problem submissions | Per documented retention rules (DEC-046, DEC-117, DEC-120)".
- **Arch §24.1 (launch gate):** legally required operator or contact information remains provided where applicable (DEC-110).

### L-4 (Low): Architecture duplication of UX behavior reduced

- **Arch §10.4:** now names UX §12.0/§15.2/§17.5 as the canonical statement of user-visible disclosure behavior and retains only the architectural obligations (Privacy content accuracy, preserved legal-notice requirement).
- **Arch §13.2:** states the shared canonical vocabulary with UX §13.1 (mechanism obligations remain: percentages only from measurable units, distinct messages).
- **Arch §13.4:** names UX §13.3-13.4 as canonical for user-visible refresh/reset behavior; the section states the mechanism contract.
- **Arch §15.3:** names UX §13.2 as canonical for user-visible download behavior; the section states delivery mechanism obligations.

### L-5 (Low): JPG-to-PDF accepted formats recorded per DEC-187

- **UX §12.4** step 1 (tool name retained), step 2 (dropzone accepts JPG/JPEG, PNG, WebP; DEC-187), §20.4.4 (acceptance criterion), §21.18 (FAQ copy must state actual accepted formats).
- **Arch §11.5:** new bullet (officially accepts JPG/JPEG, PNG, WebP; name remains "JPG to PDF"; DEC-093 validation; DEC-088 blocking).
- **Arch Appendix A row 11:** DEC-187 added.

### L-6 (Low): Newsletter deferral correctly categorized

- **UX §21.20:** retitled "Newsletter deferral (confirmed, not unresolved)" and the §21 intro now notes item 20 records a confirmed deferral with future work.

## 3. Baseline and cross-reference updates

- Both specs and the arch self-review now state the decision baseline as DEC-001 through DEC-187 (UX header/§1/§4; arch header table/§26.2).
- Arch Appendix A decision map updated for new citations: row 11 (DEC-186, DEC-187), row 20 (DEC-104), row 23 (DEC-046, DEC-050), row 24 (DEC-110), row 25 (DEC-051).
- Arch §26.5 gained a one-line correction-pass record pointing to this report.

## 4. Verification performed

1. **Placeholder scan:** grep for TODO/TBD/FIXME/XXX/PLACEHOLDER/lorem across all three files. Only hit is the arch §26.1 self-review sentence that states no such tokens exist; no actual placeholders found.
2. **pre-benchmark scan:** zero occurrences in either spec after edits (see L-2 residual note for the decision log).
3. **Consistency greps:**
   - "Telegram reporting bots" appears only as "Guinevere's Telegram reporting bots" in the fixed §1.3 non-goal, alongside the explicit DEC-180 preservation. No contradictory wording remains.
   - "Guinevere" references: §1.3 (fixed) and §3.2 (monorepo exclusion, correct). UX "OpenClaw-related content" reference in §10.6 is a historical-claims note, consistent with removal.
   - No stale "DEC-001 through DEC-185" / "to DEC-185" baseline statements remain; the only match is Appendix A row 1's "DEC-183 to DEC-185" decision-range citation, which is intentional.
   - "DEC-063" in arch appears only in the §26.2 supersession-history note.
   - "14 defect items" gone; "Loading card" gone from UX (renamed Preparing).
3. **List continuity:** UX §21 items 1-21 continuous; arch §25.3 items 1-21 continuous. Markdown structure (ATX headings, ordered lists, tables, `- **Field:**` decision blocks) manually checked per the architecture spec's own §26.5 convention.
4. **LSP diagnostics:** attempted `lsp_diagnostics` on all three files. No Markdown language server is configured in this environment ("No LSP server configured for extension: .md"); no diagnostics could be produced. This is recorded as a limitation, not a pass.
5. **Markdown lint scripts:** verified there is no root `package.json` or bun configuration exposing `lint:md:fix` / `lint:md` (directory listing). `bun run lint:md:fix` was therefore not runnable; no tooling was installed. Structural/manual checks were performed instead, as instructed.
6. **papyr-reference unchanged:** `git -C papyr-reference status --porcelain` returned empty output with exit 0. No command or write touched that directory.

## 5. Limitations

- No authoritative markdownlint pass (no repo tooling) and no Markdown LSP diagnostics (no configured server). Verification is structural/manual plus the greps above.
- The appended DEC-186/DEC-187 entries and the Open decisions rewrite were authored to match the log's established format, but no automated linter validated them.
- The cross-review's optional suggestion to annotate DEC-019 as narrowing DEC-016's Redis sentence in the log was not executed: the task limited log changes to appending DEC-186/DEC-187 and updating the Open decisions section, and AGENTS.md forbids rewriting prior decision history. The H-1 wording fix in the architecture spec resolves the reader-facing contradiction; the log annotation remains an optional owner follow-up.

## 6. Uncertainties and unresolved questions

- DEC-016 vs DEC-019: the log still contains DEC-016's blanket Redis exclusion without an explicit supersession annotation; resolution relies on log ordering and on the corrected arch §1.3 wording. Recommended owner follow-up: a short append-only annotation to DEC-019.
- The decision log's DEC-034 still says "Conservative pre-benchmark defaults". Kept as history; DEC-066 governs. Confirm the owner is satisfied with that treatment (recommend no rewrite, per append-only policy).
- UX §21 items 1-19 and arch §25.3 items 1-20 remain genuinely open and are unchanged in substance; only wording/numbering was touched. Item counts and cross-references between the two lists and the new Open decisions section should be re-checked if any future decision removes one of them.
- The newsletter deferral (UX §21.20) and the new gpt5.6-sol item (UX §21.21) both live under the "Unresolved items requiring later research" heading; the intro now flags item 20 as a confirmed deferral. If the owner prefers a separate "Confirmed deferrals" subsection, that is a one-line structural change not yet made.
- A repo-level `lint:md` run would be the authoritative lint pass once tooling exists.

## 7. Verification statement

- `papyr-reference/` was only read (git status, empty) and remains unchanged.
- Only the three assigned documents were modified: the decision log, the Product and UX Design Specification, and the Technical Architecture Specification.
- `AGENTS.md` and all other `audit-outputs/` files were not modified.
- This report is the primary deliverable; a chat-only summary is insufficient.
