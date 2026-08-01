# Spec Cross-Review: Product/UX vs Technical Architecture vs Decision Log vs Audits

- **Date:** 2026-07-31
- **Reviewer:** subagent (read-only cross-review), delegated by Sisyphus
- **Deliverable:** this file (primary deliverable, per AGENTS.md mandatory delegated-output persistence)
- **Method:** Read-only analysis (Read, Glob, Grep). No files under `papyr-reference/`, `docs/superpowers/specs/`, `papyr-rebuild-decisions.md`, `AGENTS.md`, or existing `audit-outputs/` files were modified. No installs, builds, servers, Docker, VPS, git, or network actions were performed.
- **Markdown tooling note:** `bun run lint:md:fix` / `lint:md` (OCS markdown-autofix skill) could not be executed — `<workspace-root>` has no root `package.json` or bun configuration exposing those scripts (verified by directory listing). Markdown conventions (ATX headings, ordered-list numbering, well-formed tables, no placeholder text) were enforced manually, mirroring the architecture spec's own §26.5 note.

---

## 1. Reviewed Files

| # | Path | Role |
|---|---|---|
| 1 | `<workspace-root>\AGENTS.md` | Governing orchestrator rules (read first) |
| 2 | `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` | Product and UX Design Specification (723 lines) |
| 3 | `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` | Technical Architecture Specification (1182 lines) |
| 4 | `<workspace-root>\papyr-rebuild-decisions.md` | Complete decision log, DEC-001 through DEC-185 + open decisions (2190 lines) |
| 5 | `<workspace-root>\audit-outputs\ui-home-shell-audit.md` | Shell/navbar/footer/homepage audit (210 lines) |
| 6 | `<workspace-root>\audit-outputs\ui-five-tools-audit.md` | Five-tool page audit (303 lines) |
| 7 | `<workspace-root>\audit-outputs\ui-docs-code-reconciliation.md` | Docs-vs-code reconciliation audit (341 lines) |

Spot-verification of legacy citations was performed against `papyr-reference/` (read-only):
`docs/runbook-vps.md:17,25,§7,§10.1-10.4`; `backend/services/async_task.py:47`; `backend/routers/status.py:4,14,17,28`; `backend/utils/config.py:101-102`; `backend/utils/r2.py:24`; `frontend/src/hooks/useAsyncTask.ts:6-7,32`; `deploy/nginx/conf.d/{production,default}.conf`; `deploy/docker-compose.yml`; `backend/Dockerfile.production`; `.github/workflows/{ci,deploy-vps}.yml`; `frontend/src/lib/{config,pdfUtils,format}.ts`. All exist and match the cited content.

## 2. Method

1. Read both specifications in full (UX 1-723; arch 1-1182).
2. Read the complete decision log (DEC-001 through DEC-185, plus the open-decisions tail).
3. Read all three persisted audits in full.
4. Cross-checked, item by item: (a) UX vs arch on every shared boundary (processing routing, retention timers, result delivery, limits, progress model, sessionStorage, advertising, status page, browser support, acceptance criteria); (b) both specs vs the decision baseline for missing, added, or mis-cited requirements; (c) both specs vs audits for citation accuracy (D1-D13, §6 items, §8 items, U1-U7, line references); (d) placeholder scan (TODO/TBD/FIXME/XXX/PLACEHOLDER/lorem); (e) heading/cross-reference and numbered-list consistency; (f) legacy file/line citation existence.
5. Findings were verified for exact evidence before recording. Nothing was corrected in place — per DEC-183, contradictions are surfaced for owner review, not silently resolved.

Severity rubric:

- **Blocker:** design direction conflicts with an accepted decision so that implementation would be wrong as written.
- **High:** concrete contradiction or omission that must be corrected before owner approval.
- **Medium:** ambiguity, boundary drift, or missing accepted requirement needing explicit resolution.
- **Low:** citation, wording, or categorization nit with no design impact.

## 3. Findings

### 3.1 High

**H-1 — Architecture non-goal lists Redis as excluded while the same document mandates a Redis queue.**
- Location: `2026-07-31-papyr-technical-architecture.md` §1.3, line 64: "Guinevere or OpenClaw runtime, agents, BullMQ, **Redis**, PostgreSQL/Drizzle, Telegram reporting bots, or decision-engine infrastructure (DEC-016)."
- Contradicts, in the same document: §8.1 line 371 ("Redis is the coordination store for server-side PDF jobs (DEC-019)"), §2.3 line 145 ("Redis (VPS): durable minimal task metadata queue (DEC-174)"), and §7.2 service inventory ("redis ... none" public exposure).
- Governing decisions: DEC-016 (log lines 202-212, line 209: "The rebuild will not include Guinevere agents, BullMQ, Redis, PostgreSQL/Drizzle, Telegram reporting...") versus DEC-019 (log lines 239-251, accepted later in sequence: "Use a Redis-backed task queue and dedicated workers..."). DEC-019 is the later, tool-specific decision and governs queue Redis; DEC-016's blanket Redis exclusion is implicitly narrowed but the log never annotates the supersession.
- The same bullet's "Telegram reporting bots" collides with §20.3 (Telegram incident alerts, DEC-180); the two are distinguishable (Guinevere reporting bot vs operational alert channel) but the non-goal wording does not say so.
- Proposed correction: change §1.3 line 64 to "Guinevere/OpenClaw runtime, agents, BullMQ, PostgreSQL/Drizzle, Guinevere's Telegram reporting bots, or decision-engine infrastructure (DEC-016); queue Redis is governed by DEC-019 (§8)". Optionally annotate the decision log that DEC-019 narrows DEC-016's Redis sentence.
- Why not blocker: the document body unambiguously resolves in favor of DEC-019, so implementation direction is not at risk; the non-goals wording would mislead an approving reader and must be fixed before approval.

### 3.2 Medium

**M-1 — Architecture cites the superseded DEC-063 as authority, contradicting its own self-review.**
- Location: `2026-07-31-papyr-technical-architecture.md` §6.1 line 286: "No current VPS access, account creation, or configuration change is authorized by this specification (DEC-063, DEC-172, DEC-160)."
- DEC-063 status is "Superseded and broadened by DEC-066" (log lines 776-785). The architecture spec's own §26.2 line 1097 states "The superseded benchmark-related entries (DEC-061, DEC-063) are treated as history; DEC-066 governs."
- Governing decisions: DEC-066, DEC-172 (line 2029: "This decision does not authorize current VPS access or configuration changes"), DEC-160 (line 1894).
- Proposed correction: cite `(DEC-066, DEC-172, DEC-160)` or drop DEC-063.

**M-2 — DEC-051's provider-documentation requirement has no home in either spec.**
- DEC-051 consequences (log lines 640-642) require: "Authentication, base URL, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, and availability must be documented before technical design is finalized."
- The UX spec §15.6 (lines 546-547) names the `gpt5.6-sol` provider and the blocking gates, but neither the UX §21 unresolved items (lines 695-714) nor the architecture §25.3 items (lines 1057-1076) record the DEC-051 documentation obligation.
- Proposed correction: add an item to UX §21 or arch §25.3: "gpt5.6-sol provider documentation (authentication, base URL, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, availability) before technical design finalization (DEC-051)."

**M-3 — UX spec extends Split's range order/overlap semantics to PDF-to-JPG page selection without a governing decision.**
- Location: `2026-07-31-papyr-product-ux-design.md` §12.5.4 line 448: "PageRangeInput for page selection with the same corrected order/overlap semantics as Split where they apply (DEC-038)."
- DEC-077 (overlapping ranges as independent outputs) and DEC-078 (preserve user-entered output order) are Split-specific by their titles and bodies (log lines 945-967). DEC-038 (log lines 476-486) governs range syntax/validation and is titled "range-based and per-page Split PDF modes". No accepted decision applies overlap-as-independent-outputs to PDF-to-JPG page selection; the legacy PDF-to-Image parser sorted and deduplicated ranges (five-tools audit §3.3, `PageRangeInput.tsx:19-89`).
- The hedge "where they apply" makes the requirement ambiguous: applying DEC-077 to PDF-to-JPG would duplicate rendered pages for overlapping ranges.
- Proposed correction: either remove the overlap/order extension for PDF-to-JPG (keep syntax/validation per DEC-038) or record an explicit owner-confirmed decision; the architecture spec §11.6 is silent on the point, so the two specs currently diverge by omission.

**M-4 — Shared progress-model vocabulary differs between the two specs.**
- UX §13.1 state table (lines 467-476) defines Idle / Loading / Ready / Uploading / Queued / Processing / Ready(done) / Error, with no "preparing" or "finalizing".
- Architecture §13.2 (lines 634-636) states the UI presents "preparing, uploading, queued, processing, finalizing, and ready" per DEC-033.
- DEC-033 (log line 419) lists "preparing, uploading, queued, processing, finalizing, and ready" as examples ("such as").
- Proposed correction: either add preparing/finalizing to the UX state set (or map them onto Loading/Processing), or scope arch §13.2 explicitly to the server-job lifecycle and state in UX §13.1 that the stage vocabulary is the canonical user-facing set.

### 3.3 Low

**L-1 — UX spec miscounts the home-shell audit defects.**
- Location: `2026-07-31-papyr-product-ux-design.md` §4 line 72: "(shell, navbar, footer, homepage; 14 defect items D1-D13)". D1 through D13 is 13 items (`audit-outputs/ui-home-shell-audit.md` §12, lines 153-167), and the UX spec itself elsewhere says D1-D13 (lines 260-274, 639).
- Proposed correction: "13 defect items D1-D13".

**L-2 — "Conservative pre-benchmark defaults" wording survives from DEC-034 despite DEC-066.**
- Locations: UX §21.1 line 695; arch §14.2 line 677; arch §25.3.2 line 1058.
- DEC-066 (log line 821) requires limits/defaults to be "conservative, documented as design choices or operational safeguards" and forbids presenting them as benchmark-proven. "Pre-benchmark" implies a future benchmark program that DEC-066 prohibits.
- Proposed correction: "conservative defaults (documented design choices subject to production-observation adjustment, DEC-066)".

**L-3 — Small accepted-requirement fragments from DEC-046, DEC-088, DEC-104, DEC-110 are absent from both specs.**
- DEC-046 (log line 581): contact-form submissions require "delivery monitoring, retention rules, redaction-safe error handling, and an expected response statement". Both specs cover delivery monitoring (UX §21.7; arch §25.3.14) and response-time honesty (UX §15.3), but not submission retention rules or redaction-safe error handling.
- DEC-088 (log line 1082): false-positive handling "must not require users to email or upload the rejected document through the contact form" — absent from both specs (UX §18.2 covers blocking/copy but not the support-escalation consequence).
- DEC-104 (log line 1272): "Monitoring and launch communication must distinguish regions sufficiently to identify material failures" — absent.
- DEC-110 (log line 1338): "Legally required operator or contact information must still be provided where applicable" — absent.
- Proposed correction: one line each in UX §15.3/§18.2 and arch §23/§24 respectively.

**L-4 — Architecture restates product-facing requirements that UX owns (DEC-185 duplication risk).**
- Locations: arch §10.4 (disclosure-on-Privacy-page, lines 490-494), §13.2 (progress model), §13.4 (sessionStorage), §15.3 (download behavior). All are currently consistent with UX §13, §17.5, §18 — no contradiction today, but DEC-185 (log line 2171: "Requirements must not be duplicated inconsistently") makes this a drift risk.
- Proposed correction: where the requirement is purely user-visible, arch should reference the UX section rather than restate it.

**L-5 — "JPG to PDF" retains PNG/WEBP acceptance without an explicit accepted decision.**
- Location: UX §12.4.2 line 424 ("Dropzone accepting JPG (and, per the legacy baseline, PNG and WEBP with magic-bytes validation...)").
- Grounded in the legacy baseline and audits (five-tools audit §3.4, §6; reconciliation §7.2), so not a contradiction; but DEC-010/DEC-041/DEC-093 consistently name the tool "JPG to PDF" without deciding non-JPG inputs. Flag for explicit owner confirmation or a recorded decision.

**L-6 — UX §21.20 lists a resolved deferral under "Unresolved items requiring later research".**
- Location: UX §21.20 line 714 ("Newsletter deferral is confirmed (DEC-107, DEC-109)..."). Content is accurate; the category label is not (it is resolved, with future work).
- Proposed correction: move to a "confirmed deferrals" note or retitle the item.

## 4. Verified-Clean Areas (no findings)

- **Source precedence:** UX §4 (lines 65-75) and arch §1.4 (lines 70-80) are internally coherent and mutually reconcilable via DEC-143 (binding visual/UX baseline) versus DEC-001/DEC-059 (architecture must be re-justified). No conflict.
- **DEC-183/184/185:** Both specs state their status (documentation only, no implementation authorization), canonical English, coordination/cross-referencing, and the surface-contradictions rule (UX lines 5, 14-20, 716-723; arch lines 5-13, 21-23, 80, 1080-1083). Compliant.
- **DEC-143 visual preservation:** Token table, typography, spacing/radius/shadow/motion, component character, D1-D13 corrections, and approved-change limits (UX §10, §20.2) match the home-shell and five-tools audits exactly (verified against `globals.css:3-10`, `page.tsx:486-593`, `Navbar.tsx:145-146`, `compress/page.tsx:94-135`). No invented tokens or visual claims.
- **Five-tool / EN-ES-ID scope:** Consistent everywhere; no EN/ES-only leak. Blog count 15 (five topics x 3 locales, DEC-121) consistent across UX §7.7, §19.8, §20.1.6. DEC-004/115/118 sequencing handled correctly (UX §7.2). Architecture §11, §24.1 trilingual.
- **No benchmark program:** DEC-066 honored in both specs (UX non-goal §3.5, §21.2; arch §1.3, §7.4, §9.2, §16.4, §22.1, §22.5, §25.1). Only loose end is the L-2 wording.
- **Topology:** Vercel/Cloudflare/VPS(Nginx+FastAPI+Docker)/R2 consistent between arch §2.1-2.3 and UX references (§7.5, §15.4, §15.2) and DEC-017. Status page on Vercel (DEC-119) consistent in both.
- **Queue/retention/security/deploy rules:** One-hour clock from upload receipt (DEC-070), no extension (DEC-067/075), active deletion + lifecycle safety net (DEC-166), queued-only cancellation (DEC-069), same-tab sessionStorage recovery (DEC-072), tab-close continues job (DEC-071), 30-day logs (DEC-175), minimal Redis metadata (DEC-174), signed-URL downloads (DEC-170), manual deployment gate (DEC-160), rollback (DEC-178) — consistent between UX §13, §18 and arch §8, §9.5, §12, §13, §15, §18, §19.
- **Processing boundaries:** Compress server-default; Merge/Split browser-first; JPG-to-PDF hybrid (3 MB threshold replaced by DEC-015/DEC-034 limits); PDF-to-JPG browser-capable with server fallback and 16-MP ceiling — identical in UX §12 and arch §10.2/§11. Browser limit numbers match DEC-015 exactly (100 MB/500 pp, 50 MB/200 pp, 25 MB/100 pp, PDF-to-JPG 200/50 pp, JPG-to-PDF 50 img/100 MP, 40 MP).
- **DEC-168 disclosure:** Both specs consistent (uploader carries no dedicated disclosure block; Privacy page holds it; truthful workflow-state labels remain).
- **Claims discipline:** No unsupported legal/compliance claims (UX §14.8 correctly frames the DEC-022 accepted risk and its limits; arch §4.5, §25.3.12); no certification claims (UX §16.3); no malware-free/perfect-sanitization/complete-isolation claims (arch §17.7). No implementation authorization language anywhere.
- **Placeholder scan:** No TODO/TBD/FIXME/XXX/PLACEHOLDER/lorem tokens in either spec. Arch §26.1's claim (line 1091) is accurate. `<slug>`/`<locale>` in UX §8.2 are deliberate route-pattern notation, not placeholders. Arch §26.5's claim that no root `package.json` exists is accurate.
- **Heading/link consistency:** All UX internal references (§10.3, §14, §16, §19, §20, §21, §22) resolve; all arch internal references (§7.3, §8, §9, §10.4, §12, §13, §14, §15, §17.7, §20, §24, §25) resolve. UX §21 (1-20) and arch §25.3 (1-20) numbered lists are continuous. Audit cross-references check out: D1-D13, five-tools §6 items 1-16, §8.1/8.2/8.7/8.9, U1/U2/U3/U5/U7, reconciliation §3.3/§3.4/§4.5/§6/§7.2/§7.3/§8.2/§8.8/§8.9 all match the audit files.
- **Legacy citations:** Every spot-checked file/line resolves to real content: `runbook-vps.md:17` (api.mypapyr.com), `:25` (<telegram-bot>), §7 (restic), §10.1-10.4 (Netdata + BetterStack pending); `async_task.py:47` (`_tasks: dict[str, TaskInfo]`), TTL 2h in `test_async_task.py`; `status.py` `/api/status/{task_id}` + 404 "Task not found"; `useAsyncTask.ts` 3000 ms / 180000 ms; `config.py` 20 MB / 60 min; `r2.py` 3600 s signed expiry; `PDFUploader.tsx:303` `quality=ebook`. No fabricated citations found.

## 5. Uncertainties and Unresolved Questions

1. **DEC-016 vs DEC-019 Redis:** the decision log does not explicitly annotate DEC-019 as superseding DEC-016's blanket Redis exclusion; resolution relies on log ordering (later, tool-specific decision governs). Recommend the owner confirm this reading in the log (append-only supersession note, per AGENTS.md).
2. **Markdown lint:** full markdownlint verification was impossible (no root package.json, confirmed). Manual structural checks passed; a repo-level `lint:md` run after tooling exists would be the authoritative lint pass.
3. **Unread legacy internals:** arch Appendix B claims about `Dockerfile.production` healthcheck and `production.conf` rate-zone details were verified for existence but not re-audited line-by-line; the existing audits corroborate the compress/cleanup/r2 specifics cited.
4. **M-3 (PDF-to-JPG range semantics)** is a product-behavior question only the owner can resolve; it is recorded as a contradiction-adjacent ambiguity, not silently resolved.

## 6. Final Recommendation

**Conditional pass (PASS with required corrections).**

No blocker findings. One high-severity internal contradiction (H-1, arch §1.3 vs §8) must be corrected before owner approval, and the medium items (M-1 to M-4) should be resolved or explicitly acknowledged — M-3 requires an owner decision. All low items are editorial. Per DEC-183, these contradictions are hereby surfaced rather than silently resolved; none changes the overall design direction, and both specifications are otherwise internally and mutually consistent, fully grounded in DEC-001-185 and the persisted audits, free of benchmark obligations, placeholders, unsupported claims, and implementation authorization.

Suggested owner actions:

1. Approve the wording correction for H-1 (and optionally the log supersession note for DEC-016/DEC-019).
2. Decide M-3 (whether PDF-to-JPG page selection follows Split's order/overlap semantics).
3. Acknowledge M-1, M-2, M-4 and the low items for inclusion in the next spec revision.

## 7. Verification Statement

- `papyr-reference/` was only read; nothing was modified, formatted, installed, or executed there. The legacy clone remains unchanged.
- Neither specification, the decision log, `AGENTS.md`, nor any existing `audit-outputs/` file was modified.
- This deliverable was created at `<workspace-root>\audit-outputs\spec-cross-review.md`.
- Chat-only summary is insufficient; this file is the primary deliverable.
