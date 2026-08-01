# Product and UX Spec Revision: DEC-189 through DEC-196 and Cross-Domain Reconciliation

- **Date:** 2026-07-31
- **Author:** Sisyphus-Junior (executor subagent), applying owner decisions DEC-189 through DEC-196 and the completed cross-domain reconciliation
- **Deliverable:** this file (primary audit deliverable, per AGENTS.md mandatory delegated-output persistence); a chat-only summary is insufficient
- **File changed (only this one):**
  1. `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (canonical Product and UX Design Specification; 728 lines before, 732 lines after)
- **Files verified unchanged:** `papyr-reference/` (read-only git status; see Section 7), `AGENTS.md`, `papyr-rebuild-decisions.md`, `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`, and all other `audit-outputs/` files.
- **Tooling note:** No installs, builds, servers, VPS access, Docker operations, git writes, or network-changing commands were run. The only git command was a read-only `git status --porcelain` inside `papyr-reference/`.

---

## 1. Inputs read in full

| # | Input | Role |
|---|---|---|
| 1 | `AGENTS.md` | Governing orchestrator rules (read first, per task) |
| 2 | `papyr-rebuild-decisions.md` | Full decision log; DEC-189 through DEC-196 read in full (lines 2232-2330); DEC-001-188 context read for baseline and cross-references |
| 3 | `audit-outputs/research/reconciliation-report.md` | X2 cross-domain reconciliation (complete, 299 lines) |
| 4 | `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` | The assigned spec to revise (read in full, 728 lines) |
| 5 | `audit-outputs/spec-cross-review.md` | Prior cross-review (H-1, M-1..M-4, L-1..L-6), previously applied |
| 6 | `audit-outputs/spec-corrections-report.md` | Prior corrections pass (DEC-186/187 and cross-review fixes), for revision-state continuity |

No web research was performed. No decision log, architecture spec, AGENTS.md, or legacy reference was edited.

## 2. Decisions incorporated and where

All seven reconciliation owner questions (X2 §8, Q1-Q7) were resolved by DEC-189 through DEC-196. Each accepted decision was applied to the UX spec only where the user experience is affected (DEC-189) or where the decision states product-facing behavior.

### 2.1 Decision baseline update

- **Header field** (line 7): "DEC-001 through DEC-187" to "DEC-001 through DEC-196"; added a `- **Revision:**` line naming DEC-189-196 and X2.
- **§1 Status**: baseline sentence updated to DEC-196; added the revision sentence citing the completed reconciliation (`audit-outputs/research/reconciliation-report.md`, X2) and the non-normative status of research findings (DEC-054, DEC-057).
- **§4 Sources and precedence item 1**: baseline updated to DEC-196.
- **§4 item 3**: added the reconciliation report to the audit-deliverables list.
- **§4**: added the precedence caveat "Research findings, recommendations, and defaults recorded in the audit deliverables are design inputs, not decisions; only accepted decisions are normative (DEC-054, DEC-057)."

### 2.2 DEC-189 (one active worker) — user-facing queue consequences only

- **§13.1 State model, Queued row**: states the initial backend runs one active worker, so valid jobs may wait in the bounded fair queue and wait language reflects that reality (DEC-189).
- **§13.5 Honest progress**: bounded queuing is an expected state rather than an error under the one-worker initial posture (DEC-189).
- **§21.1**: raising worker concurrency requires later capacity evidence and explicit approval (DEC-189).

Queue/worker internals, memory budgets, and scaling mechanics remain in the Technical Architecture Specification's domain and were not restated here.

### 2.3 DEC-190 (no-prior-consent advertising risk reaffirmed) — no compliance claims

- **§14.8 Consent**: now states the owner reaffirmed the accepted risk after review of the research findings (DEC-022, DEC-190); explicitly names GDPR, UK GDPR, Swiss FADP, ePrivacy, PECR, and US state law as non-covered; prohibits compliance claims without qualified review (DEC-190); retains the binding override if prior consent is later determined mandatory.
- **§14.9 UX priority**: critical product functionality and legal, support, and status content remain available when ad scripts are blocked or disabled (DEC-190).
- **§15.2 Legal pages**: consent-risk disclosure now cites (DEC-022, DEC-190, DEC-045).
- **§20.6.1**: no-prior-consent position remains the owner-reaffirmed accepted risk with no compliance claims (DEC-190).
- **§21.9**: the gating decision is reaffirmed (DEC-190); provider terms, scripts, cookies, identifiers, and recipients still require pre-launch review, and a later legal/provider-policy determination remains binding.

### 2.4 DEC-191 (US/CA Letter, else A4)

- **§12.4 JPG to PDF, step 5 (automatic fitting policy)**: rewritten to the DEC-191 rule: Letter only when the trusted coarse edge country code is US or CA; every other, missing, or invalid code selects A4; the active content locale never independently selects paper size.
- **§20.4.4**: acceptance criterion updated to the same rule.
- **§21.3**: item narrowed (number preserved): the regional rule itself is resolved (DEC-191); only the user-visible summary wording remains for the copy pass. The former open questions (missing edge country, EN spanning US and non-US markets) are resolved by DEC-191's locale-never-decides clause.

### 2.5 DEC-192 (active-content Merge/Split routed to server sanitization)

- **§12.2 Merge PDF, processing model**: browser inspection detecting PDF JavaScript, embedded attachments, launch actions, or other active content routes the job to the temporary server path for sanitization; no separate browser sanitization engine; fail-closed when the malware-scanner or sanitization path is unavailable; ordinary safe files still use the browser path within DEC-015 limits.
- **§12.2 Merge PDF, document features**: active-content-bearing inputs route to the server sanitization path rather than browser page copying; no malware-free guarantee.
- **§12.3 Split PDF, processing model**: same routing and fail-closed rule.
- **§12.3 Split PDF, active content**: routing to the server sanitization path; no malware-free guarantee.
- **§18.3 Sanitization notice**: Merge/Split active-content inputs route to server sanitization and fail closed when the path is unavailable; no malware-free guarantee.
- **§20.3.12**: acceptance criterion updated (DEC-090, DEC-091, DEC-192).

### 2.6 DEC-193 and DEC-196 (gateway identity and authentication) — facts, no secrets

- **§15.6 Blog**: the workflow calls the owner's OpenAI-compatible gateway at `https://router.budgezen.com/v1` with exact JSON model identifier `mypapyr` (never the public `gpt5.6-sol` name) and `Authorization: Bearer <API_KEY>`; gateway accessed only from server-side or protected automation environments; credentials never enter client code, repository content, logs, generated articles, or analytics; no internal spending guard at launch, with reliability controls mandatory and separate (bounded timeout, finite retries with backoff, idempotency where supported, one bounded publication workflow, repeated-failure pause, kill switch).
- **§21.21**: item rewritten (number preserved) as "Gateway capability documentation": identity and authentication resolved (DEC-193, DEC-196); remaining documentation items are request/response schema deviations, structured-output behavior, tool-use behavior, effective context, data retention, availability, and safety or compliance policies; provider integration stays isolated behind an interface (DEC-051, DEC-193).

No API key, token, credential value, or secret is present in the spec. Only the base URL, identifier string, and header scheme are stated, matching the task constraint "gateway/model/auth facts without secrets."

### 2.7 DEC-194 (localized 410 Gone default for deferred legacy tool URLs)

- **§7 Launch scope item 8**: URL inventory disposition default now cites DEC-194.
- **§8.2 note 3**: deferred legacy tool URLs return an intentional localized 410 Gone by default, with targeted redirects only on credible traffic or intent evidence (DEC-194).
- **§19.3 Legacy URL inventory**: full DEC-194 rule: 410 default, targeted redirect only on credible evidence, 410 experience explains unavailability and links to live tools, sitemap/navigation/canonical/internal links exclude 410 URLs.
- **§19.4 Legacy archive**: important legacy URLs receive intentional redirects or replacement responses, with the localized 410 default for deferred tool URLs (DEC-099, DEC-194).
- **§20.1.7**: acceptance criterion updated (DEC-127, DEC-194).
- **§21.4**: item narrowed (number preserved): deferred tool URLs default to localized 410 (DEC-194); the five-tool slug table and remaining non-tool dispositions stay in SEO design.

### 2.8 DEC-195 (unmodified Ghostscript as separate Compress executable, license gate)

- **§12.1 Compress PDF, processing model**: Ghostscript as official unmodified open-source executable in a separate server-side subprocess, not modified/linked/embedded into proprietary code; authoritative distribution, version-pinned, hardened, `-dSAFER`; AGPL/copyright notices preserved and unmodified source made available; no claim that subprocess use eliminates every licensing obligation; focused license review before launch with a fallback to a permissive engine path or commercial license if the owner does not accept required disclosure.
- **§20.4.1**: Compress acceptance criterion extended with the Ghostscript production model and the license-gate-before-launch rule (DEC-195).
- **§21.2**: item narrowed (number preserved): the engine selection is resolved (DEC-195, license review pending); only the internal profile thresholds remain for technical design.

### 2.9 Cross-domain reconciliation citation (X2)

- Cited in the header revision field, §1 Status, §4 precedence item 3, and §22.4 (reconciliation gates complete; compatible findings are design inputs; owner-side contract and operational inputs remain; the X2 readiness statement does not authorize implementation, DEC-057).

## 3. Section numbering stability

- All section headings (1 through 22, including subsections) are unchanged from the pre-revision document; no section was added or removed. Verified by heading listing: `## 1. Status` through `## 22. Relationship to the Technical Architecture Specification`, with all subsections (4.1, 8.1-8.5, 10.1-10.7, 11.1-11.4, 12.0-12.5, 13.1-13.5, 15.1-15.6, 16.1-16.3, 20.1-20.8) intact.
- §21 items remain numbered 1 through 21, continuous. Resolved items (2, 3, 4, 9, 21) were narrowed to their still-open residuals rather than deleted; the §21 intro records this policy.
- §13.1 state table: all 9 state rows plus the header and separator rows intact; only the Queued row changed.
- §20 lists: all numbered items in §20.1 (1-8), §20.3 (1-13), §20.4 (1-5), §20.6 (1-5) retain their numbers.

## 4. Preservation checks

- **DEC-066 (no benchmark program):** no benchmark language was introduced anywhere; profile thresholds remain "validated through normal functional testing, without a benchmark program" (§21.2), and "adjusted from production observations rather than benchmark-proven" wording is retained (§21.1).
- **DEC-143 (binding visual baseline):** §10 (existing visual baseline), token table, typography, §10.6 D1-D13 defects, and §20.2 visual-continuity criteria were not modified.
- **DEC-022 vs DEC-190:** DEC-190 is a reaffirmation of DEC-022, not a supersession; §14.8 cites both and preserves the risk framing and the binding override clause.
- **DEC-083/085/089 vs DEC-191:** DEC-191 resolves the DEC-083 ambiguity. §12.4 step 5 now states the DEC-191 rule directly and cites (DEC-083, DEC-085, DEC-191); the obsolete "Letter-family for other markets ... A4 fallback" phrasing was replaced. DEC-085/DEC-089 remain the operative mechanism/fallback in the decision log; the spec now states the resolved product rule.
- **DEC-051 (provider documentation) vs DEC-193/196:** §21.21 preserves the documentation obligation for the remaining capability fields while recording the resolved identity/auth items; §15.6 cites DEC-193/196 for the gateway facts and keeps DEC-048/DEC-053 for the reliability controls.
- **No undecided category-A recommendations added as normative requirements:** the reconciliation's category-A/B items were only incorporated where an accepted decision (DEC-189-196) made them normative; category-C defaults and category-D inputs remain recorded as unresolved or as owner-side inputs, not requirements. The §4 precedence caveat states this explicitly.
- **Unresolved capability details and implementation gate preserved:** §21 items 1, 5-8, 10-19 remain unresolved as before; §1 and §3.1 keep the non-implementation status; §22.4 keeps the implementation-planning gate.

## 5. Verification performed

1. **Changed-file path:** `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` confirmed present, 732 lines (was 728).
2. **Baseline grep:** `grep -n "DEC-187|DEC-188|DEC-189|DEC-190|DEC-191|DEC-192|DEC-193|DEC-194|DEC-195|DEC-196"` — every DEC-189-196 decision is cited; the only remaining DEC-187 citations are the intentional JPG-to-PDF format references (§12.4 steps 1-2, §21.18) and the DEC-187 acceptance criterion in §20.4.4. No stale "DEC-001 through DEC-187" or "through DEC-185" statements remain (grep returned no match). No "three audit deliverables" phrasing remains.
3. **Placeholder scan:** `grep -niE 'TODO|TBD|FIXME|XXX|lorem ipsum|placeholder|WIP'` — two hits, both pre-existing self-descriptive prose: §11.3 "No `#` placeholders" (stating footer dead links are replaced) and §12.3 "placeholder example" (describing the legacy PageRangeInput). No TODO/TBD/FIXME/XXX/lorem/WIP tokens. `<slug>` and `<locale>` in §8.2 remain deliberate route-pattern notation, not placeholders.
4. **Headings/tables/lists:** ATX heading scan above; §13.1 table row count verified (9 rows); §21 items 1-21 continuous; §20 lists continuous.
5. **Markdown lint scripts:** verified unavailable. `<workspace-root>` has no root `package.json` and no `bun.lockb` (directory listing), so `bun run lint:md:fix` / `lint:md` (OCS markdown-autofix skill) could not be executed. Manual structural verification (headings, ordered-list numbering, table well-formedness, placeholder scan) was applied instead; this limitation is recorded here and matches the pre-existing note in the architecture spec's §26.5 and the prior corrections report.
6. **LSP diagnostics:** attempted `lsp_diagnostics` on the spec; no Markdown language server is configured in this environment ("No LSP server configured for extension: .md"). Recorded as a limitation, not a pass.
7. **`papyr-reference/` unchanged:** read-only `git -C papyr-reference status --porcelain` returned empty output with exit 0; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`, matching the HEAD recorded by the reconciliation report (X2 §11) and the earlier correction pass. No tracked or untracked change exists; no command or write touched that directory.

## 6. Exact edit log (35 edits, all applied successfully)

| # | Location | Before (abridged) | After (abridged) | Decision |
|---|---|---|---|---|
| 1 | Header line 7-8 | `- **Decision baseline:** DEC-001 through DEC-187 ...` | `- **Decision baseline:** DEC-001 through DEC-196 ...` plus `- **Revision:** 2026-07-31 (incorporates DEC-189 through DEC-196 and the completed cross-domain reconciliation, X2)` | baseline update |
| 2 | §1 | "consolidates ... DEC-001 through DEC-187 ... the three audit deliverables" | "... DEC-196 ... the audit deliverables ..." + revision sentence citing X2 and non-normative research status | baseline + X2 |
| 3 | §4 item 1 | "(DEC-001 through DEC-187)" | "(DEC-001 through DEC-196)" | baseline |
| 4 | §4 item 3 | three bullets | added reconciliation report bullet (X2) | X2 citation |
| 5 | §4 after item 4 | — | precedence caveat: research findings are design inputs, only accepted decisions normative (DEC-054, DEC-057) | non-normative rule |
| 6 | §7 item 8 | "...every URL (DEC-127)." | "...every URL (DEC-127); deferred legacy tool URLs return an intentional localized 410 Gone by default (DEC-194)." | DEC-194 |
| 7 | §8.2 note 3 | "...redirect map under the SEO design (DEC-023, DEC-099, DEC-127)." | + 410-default sentence (DEC-194) | DEC-194 |
| 8 | §12.1 Processing model | "Server-side by default (DEC-014, DEC-015). If a browser processing path..." | + Ghostscript separate-process, `-dSAFER`, notices/source, license-gate sentence, permissive/commercial fallback (DEC-195) | DEC-195 |
| 9 | §12.2 Processing model | "Browser-first (DEC-011). Corrupt, encrypted-unsupported, or unsafe jobs..." | + active-content detection routes to server sanitization, no browser sanitization engine, fail-closed (DEC-192) | DEC-192 |
| 10 | §12.2 Document features | "Active content is sanitized from the output (DEC-090) with category-level disclosure (DEC-091)." | + server-routing and no-malware-free-guarantee (DEC-192) | DEC-192 |
| 11 | §12.3 Processing model | "Browser-first (DEC-011) with automatic server fallback for unsafe jobs (DEC-030, DEC-065)." | + active-content routing, no browser sanitization engine, fail-closed (DEC-192) | DEC-192 |
| 12 | §12.3 Active content | "Sanitized from outputs with category-level disclosure (DEC-090, DEC-091)." | + server routing, no malware-free guarantee (DEC-192) | DEC-192 |
| 13 | §12.4 step 5 | "Letter-family geometry is used for US and Canada; A4-family for other markets ... (DEC-083, DEC-085, DEC-089)." | "Letter is selected only when the trusted coarse edge country code is the United States or Canada; every other country, missing code, or invalid code selects A4, and the active content locale never independently selects paper size (DEC-191)." | DEC-191 |
| 14 | §13.1 Queued row | "...(DEC-033, DEC-035)" | + one-worker wait reality (DEC-189) | DEC-189 |
| 15 | §13.5 | "...updated from real queue state (DEC-033)." | + "under the one-worker initial posture, bounded queuing is an expected state rather than an error (DEC-189)" | DEC-189 |
| 16 | §14.8 Consent | "(DEC-022), not evidence of GDPR, UK GDPR, Swiss, ePrivacy, or US state compliance..." | + owner reaffirmation (DEC-190); names GDPR, UK GDPR, Swiss FADP, ePrivacy, PECR, US state law; no-compliance-claim clause; override clause | DEC-190 |
| 17 | §14.9 | "...rather than degrading the product (DEC-135, DEC-136)." | + critical functionality/content availability when ad scripts blocked (DEC-190) | DEC-190 |
| 18 | §15.2 | "(DEC-022, DEC-045)" | "(DEC-022, DEC-190, DEC-045)" | DEC-190 |
| 19 | §15.6 Blog | "...uses the owner's `gpt5.6-sol` provider (DEC-051) with blocking quality gates..." | + gateway URL, `mypapyr` identifier, Bearer auth, server-side-only access, no-secrets rule, no spending guard, reliability controls (DEC-193, DEC-196) | DEC-193/196 |
| 20 | §18.3 | "(DEC-091). Sanitization is distinguished..." | + Merge/Split server routing, fail-closed, no malware-free guarantee (DEC-192) | DEC-192 |
| 21 | §19.3 | "(DEC-127). Legacy pages that still attract..." | + 410 default, targeted-redirect evidence rule, 410 experience, exclusion of 410 URLs from sitemap/nav/canonical/internal links (DEC-194) | DEC-194 |
| 22 | §19.4 | "...replacement responses (DEC-099)." | "...replacement responses, with the localized 410 default for deferred tool URLs (DEC-099, DEC-194)." | DEC-194 |
| 23 | §20.1.7 | "...no soft 404s or redirect chains (DEC-127)." | + localized 410 default, targeted redirects on evidence (DEC-194) | DEC-194 |
| 24 | §20.3.12 | "...(DEC-090, DEC-091)." | + Merge/Split server routing and fail-closed (DEC-192) | DEC-192 |
| 25 | §20.4.1 | "...fabricates a percentage (DEC-014, DEC-080)." | + Ghostscript production model and license-gate-before-launch (DEC-195) | DEC-195 |
| 26 | §20.4.4 | "Letter for US/CA and A4 elsewhere with A4 fallback ... (DEC-041, DEC-082, DEC-083, DEC-085, DEC-089, DEC-084)" | "Letter only for trusted US/CA edge country codes and A4 for every other, missing, or invalid code, with the locale never deciding paper size ... (DEC-041, DEC-082, DEC-191, DEC-084)" | DEC-191 |
| 27 | §20.6.1 | "...verified absent (DEC-018)." | + no-prior-consent position remains owner-reaffirmed accepted risk, no compliance claims (DEC-190) | DEC-190 |
| 28 | §21 intro | "Item 20 records a confirmed deferral..." | + "Items whose underlying questions were resolved by DEC-189 through DEC-196 are narrowed to their still-open residuals rather than deleted, preserving numbering." | narrowing policy |
| 29 | §21.1 | "...technical-design responsibilities (DEC-066)." | + one worker at relaunch; raising concurrency requires capacity evidence and approval (DEC-189) | DEC-189 |
| 30 | §21.2 | "The 'premium screen quality' profile's internal thresholds..." | + "The engine selection is resolved: the official unmodified Ghostscript executable as a separate server-side subprocess, subject to a focused license review before public launch (DEC-195)." | DEC-195 |
| 31 | §21.3 | "Paper-standard regional rule details. How the active locale maps to Letter/A4..." | "Paper-standard regional rule wording. The regional rule itself is resolved: Letter only for trusted US/CA edge country codes ... (DEC-191). What remains is only the user-visible summary wording, finalized in the copy pass (DEC-191)." | DEC-191 |
| 32 | §21.4 | "...redirect map, selected during SEO design (DEC-023, DEC-122, DEC-127)." | + 410 default and evidence rule (DEC-194); slug table and remaining non-tool dispositions stay in SEO design | DEC-194 |
| 33 | §21.9 | "...including whether prior consent is required (DEC-022, DEC-045)." | + gating reaffirmed (DEC-190); provider review remains; later binding determination overrides | DEC-190 |
| 34 | §21.21 | "`gpt5.6-sol` provider documentation ... base URL, authentication, request/response schema..." | "Gateway capability documentation ... identity and authentication resolved (DEC-193, DEC-196) ... remaining documentation items are the exact request and response schema deviations, structured-output behavior, tool-use behavior, effective context, data retention, availability, and applicable safety or compliance policies (DEC-193, DEC-196)." | DEC-193/196 |
| 35 | §22.4 | "...completion of the required research and reconciliation gates (DEC-185, DEC-060)." | + reconciliation complete (X2); findings are inputs; owner-side inputs remain; readiness statement does not authorize implementation (DEC-057) | X2 citation |

## 7. Prohibitions-compliance and verification statement

- Only the assigned spec was modified. The decision log (append-only), the architecture spec, `AGENTS.md`, research briefs, and all other files were not edited.
- `papyr-reference/` was only read (git status, porcelain output empty, exit 0); it remains unchanged at HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`.
- No undecided category-A reconciliation recommendations were promoted to normative requirements.
- No product code, installs, builds, servers, VPS, deploy, or git write operations were performed.
- No API keys, tokens, or secret values appear in the spec or in this file; the only gateway facts recorded are the base URL, the `mypapyr` identifier, and the `Authorization: Bearer <API_KEY>` scheme.
- This file is the primary deliverable of this task; a chat-only summary is insufficient.
