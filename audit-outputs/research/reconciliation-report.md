# Papyr Rebuild: Cross-Domain Reconciliation Report (X2)

| Field | Value |
|---|---|
| Document ID | X2 (plan deliverable, `audit-outputs/research/reconciliation-report.md`) |
| Version | 1.0 |
| Date | 2026-07-31 |
| Canonical language | English (DEC-184) |
| Author role | Sisyphus-Junior (executor subagent; Wave 4 reconciliation per plan §10) |
| Status | Complete for owner review; gates research into owner decisions and implementation planning |
| Governing plan | `audit-outputs/research-program-plan.md` (§6.6 deliverable X2; §10 reconciliation; §11 program-wide assertions; §14 owner-review handoff) |
| Governing decisions | DEC-001 through DEC-188; primary gates DEC-054, DEC-055, DEC-056, DEC-057, DEC-060, DEC-066, DEC-183, DEC-184, DEC-188 |
| Inputs read in full | `AGENTS.md`; `papyr-rebuild-decisions.md` (DEC-001–188 plus Open decisions, 2230 lines); both approved specifications (`2026-07-31-papyr-product-ux-design.md`, 728 lines; `2026-07-31-papyr-technical-architecture.md`, 1188 lines); `audit-outputs/research/research-brief-verification.md`; `audit-outputs/research/source-and-decision-index.md`; and primary briefs A1–A6, B1–B5, C1–C6, D1–D5, E1–E3 (all 25 read; conflict-carrying briefs read in full) |
| Primary deliverable | this file |

---

## 1. Purpose

This report is the final cross-domain reconciliation of the 25 primary research briefs (Tracks A–E) against the accepted decision baseline (DEC-001–188) and both approved design specifications. Its task is to classify every material research finding into:

- **(A) Compatible recommendations** — consistent with the accepted decisions and both specs; safe to carry into later implementation planning once category-B decisions are made.
- **(B) Genuine conflicts** — material contradictions or choice points between accepted decisions, brief recommendations, or the specs that require an explicit owner decision (DEC-183, DEC-057).
- **(C) Deferred non-blocking questions and defaults** — conservative defaults, implementation-time re-checks, and minor confirmations that do not block planning.
- **(D) Source and contract blockers** — documentation, contract text, or operational data that is owner-supplied or access-gated and must be obtained before technical design can finalize.

It also collapses the ~50 brief-level owner prompts (verification report §5.4 item 3) into the smallest possible set of high-level material owner questions, and states what may proceed into implementation planning once the owner resolves the blockers. It does **not** create an implementation plan (DEC-060, DEC-185).

Nothing in this report is an accepted product decision. It is a reconciliation input; owner approval per DEC-057 and the gates of DEC-060 and DEC-188 remain binding.

## 2. Method and evidence base

1. Read `AGENTS.md` (governing rules) first.
2. Read the full decision log (DEC-001–188 and Open decisions).
3. Read both approved specifications in full.
4. Read the two navigation aids: `research-brief-verification.md` (PPR-VER-001, 25/25 PASS, 0 blocking defects, 2 minor observations, 3 open items) and `source-and-decision-index.md` (X1, including the K1–K18 conflict register and M1–M23 missing-source register).
5. Read the primary briefs, with full reads of the conflict-carrying briefs: A1, A2 (to §8), A6, B1, B3, B4, C1, C2, C3, C4, D1, D5, E1. The remaining briefs (A3–A5, B2, B5, C5, C6, D2–D4, E2, E3) were read through their X1 per-track entries and the verification report, which the verifier produced from full reads of all 25 files.
6. Classified each recommendation against the decision baseline and the spec sections it serves, using the K/M registers from X1 as the cross-check.
7. Verified `papyr-reference/` remains unchanged (Section 11).

Precedence applied throughout (plan §5; arch §1.4): decisions > specs > audit/research evidence > legacy reference. Briefs are recommendations, never decisions (DEC-054, DEC-057).

### 2.1 Verification status of inputs

- **25/25 briefs PASS** verification (PPR-VER-001): template coverage 25/25, primary sources with dates 25/25, ≥2 alternatives 25/25, recommendation-as-nondecision labeling 25/25, owner prompts 25/25, placeholder scan clean in all primary briefs, **DEC-066 compliance confirmed** (every "benchmark" mention is a prohibition statement, a non-goal, an acceptance-criteria framing, or a design-choice note; no benchmark program, corpus, matrix, or quality-score program exists).
- **X1 index** records 18 conflict/tension markers (K1–K18) and 23 missing/stale/unavailable source items (M1–M23). This report reconciles each K marker to a category and carries the M register into the source/contract blocker section.
- **DEC-066 is preserved by this report**: no benchmark work is introduced, recommended, or implied anywhere below; all numeric values discussed are documented design/safety choices subject to DEC-066's adjustment-from-observations rule.

## 3. Classification summary

| Category | Count | Description |
|---|---|---|
| A. Compatible recommendations (safe to carry) | 18 | Engine matrix non-AGPL elements, routing model, queue design, R2 lifecycle, hardening posture, observability, backups, analytics schema, support design, testing program, blog pipeline architecture (contingent), topics pipeline criteria |
| B. Genuine conflicts requiring owner decision | 7 | Licensing fork (K3); VPS memory envelope (K2); EEA/UK/CH ad consent (K9); `gpt5.6-sol` identity/access path (K10); paper-policy interpretation (K1, K17); browser-path sanitization (K11); legacy URL traffic dispositions (K12) |
| C. Deferred non-blocking questions and defaults | 12 | Conservative limit values and raising procedure, queue caps, scanner fail-closed confirmation sub-items, monitoring/backup defaults, UI baseline confirmations (UX §21.11–19), analytics/support micro-choices, implementation-time re-checks (M6–M11, M14–M20, M22–M23) |
| D. Source and contract blockers | 5 | `gpt5.6-sol` provider documentation (M2); Adsterra publisher terms/ad-unit code (M1); VPS host-state verification (M13); legacy traffic data (M4, M5); AGPL commercial pricing (M3) |

The mapping of each K marker to a category:

| K | Tension | Category | Disposition |
|---|---|---|---|
| K1 | DEC-083 vs DEC-085 paper-policy mechanism | B (question 5) | Owner confirms edge-country-only reading |
| K2 | Worker + ClamAV budget exceeds ~8 GB envelope | B (question 2) | Owner decides reconciliation trade |
| K3 | Ghostscript AGPL vs permissive engines per tool | B (question 1) | Single largest cross-track dependency |
| K4 | Maintained-scanner requirement vs limited PDF coverage | B (question 6) | Owner confirms scanner + honest-limits rule |
| K5 | caniuse vs BCD Safari wasm GC | C | Source conflict; routing does not depend on it |
| K6 | Google docs cite obsolete RFC 5988 | C | Brief uses RFC 8288; recorded, not blocking |
| K7 | MDN `display:none` vs `opacity:0` hidden input | C | Brief follows `opacity:0`; documented choice |
| K8 | Legacy "no tracking / PATUH" claims vs accepted model | C | D2 re-scopes copy; history not rewritten |
| K9 | EEA/UK/CH consent vs DEC-022 no-consent | B (question 3) | Triggers DEC-022 consequence clause |
| K10 | `gpt5.6-sol` vendor-neutral wording vs public record | B (question 4) | Owner confirms access path; docs are D |
| K11 | Browser-path active-content sanitization scope | B (question 6) | Server-route recommendation needs owner confirmation |
| K12 | 410 Gone vs DEC-114 traffic test for deferred URLs | B (question 7) | Owner traffic knowledge required |
| K13 | Legacy BetterStack "pending" vs DEC-119 Vercel status | C | Provider selection is deployment-time; C |
| K14 | 16-MP/200-page browser ceiling mirrored as server default | C | Documented conservatism; first telemetry adjustment candidate |
| K15 | "Compress server-default" read as "no local path" | C | Consistent reading across A2/B1; owner confirmation only if a local path is ever considered |
| K16 | Legacy SLA response targets vs DEC-050 no-promise rule | C | Not carried into copy; owner commitment only if desired |
| K17 | CLDR Letter countries beyond US/CA | B (question 5) | Keep two-country rule or extend via new decision |
| K18 | Plan §8 (12 sections) vs Track task (16 sections) template count | C | Internal process inconsistency; all content present |

---

## 4. Category A — Compatible recommendations (safe to carry into implementation planning)

These findings are consistent with the accepted decisions and both specifications, involve no material conflict, and may be carried as design inputs into later implementation planning (still subject to DEC-057 approval of the resulting design).

| # | Recommendation | Evidence (brief §) | Decision/spec basis | Notes |
|---|---|---|---|---|
| A-1 | **Permissive-first engine matrix structure** with a documented AGPL exception only where no permissive alternative meets behavior; pin current versions, monthly dependency review, hardened containers for every engine, no malware-free claims | A1 §7, §8; A1 §5.4 | DEC-059, DEC-056, DEC-179, DEC-169, DEC-171, DEC-090 | The matrix structure itself is compatible; the Ghostscript fork is B (question 1). Version pinning satisfies the CVE currency requirements |
| A-2 | **Merge/Split server fallback: pikepdf (qpdf)** for structure-preserving merge/split with its native sanitization API implementing DEC-090 categories; pypdf as permissive fallback | A3 §7; A4 §7 | DEC-079, DEC-090, DEC-091, DEC-064; arch §25.3.2, §11.3–11.4 | Implements the approved sanitization requirement directly; browser happy path uses pdf-lib with disclosed limitations (A-3) |
| A-3 | **Browser-first Merge/Split via pdf-lib for the unencrypted happy path** within DEC-015 limits, with encryption/corruption/active-content jobs routed to the server path | A3 §7; A4 §7; B1 §7.1 | DEC-011, DEC-015, DEC-030, DEC-065; UX §12.2–12.3 | pdf-lib is unmaintained (M-carry: A1 §9 item 4); design-time dep review and fallback plan required. The active-content routing question is B (question 6) |
| A-4 | **JPG to PDF hybrid: browser pdf-lib + server img2pdf (LGPL-3.0) + Pillow (HPND)** for lossless JPEG/PNG embed, WebP decode, EXIF auto-orientation, per-image Letter/A4 sizing | A5 §7 | DEC-011, DEC-041, DEC-082, DEC-083/085/089, DEC-084, DEC-093, DEC-187; arch §11.5, §25.3.7 | Paper-policy interface consumed from B3; the region rule confirmation is B (question 5); WebP metadata loss is best-effort per DEC-084 |
| A-5 | **PDF to JPG: pypdfium2 (server) + pdf.js (browser)** — the only fully permissive pairing meeting rendering, white compositing (DEC-081), encryption support, and the 16-MP ceiling; white fill implemented explicitly in both paths | A6 §7 | DEC-039, DEC-081, DEC-092, DEC-186, DEC-015; arch §11.6, §25.3.6 | PyMuPDF/Ghostscript remain AGPL-dependent alternatives (B question 1); output profile starting point is a documented design choice (C) |
| A-6 | **Layered browser routing (B1 Alternative B):** device-class caps + file-characteristic evaluation (decoded dimensions, geometry, encryption, corruption, estimated peak memory) + capability feature detection; ordinary `input[type=file]` baseline always works; at most one server transition per job (DEC-065); fail-closed classes never upload; no `navigator.deviceMemory` | B1 §7 | DEC-011, DEC-015, DEC-030, DEC-031, DEC-065, DEC-165; arch §10, §14.1; UX §16.3 | Directly implements the "measured capabilities and explicit rules" requirement |
| A-7 | **Minimal custom queue over Redis Streams consumer groups** with AOF `appendfsync everysec`, `noeviction`, TTL-bounded minimal metadata, per-origin fairness classes, Lua-atomic queued→cancelled transition, `XAUTOCLAIM` stale-claim reclaim | C1 §7 | DEC-019, DEC-035, DEC-137, DEC-174, DEC-162; arch §8–9 | Values are defaults (C); framework-vs-custom preference is a deferred confirmation (C) |
| A-8 | **Active deletion as primary R2 timer + lifecycle rule (1-day) as safety net**, `tmp/<date>/<uuid><ext>` key scheme, signed URLs capped at `min(remaining, 300 s)`, cleanup telemetry counts/timing only | C3 §7 | DEC-013, DEC-067, DEC-070, DEC-075, DEC-166, DEC-170; arch §12 | 1-vs-2-day safety-net age is a default (C) |
| A-9 | **Layered hardening posture:** per-service hardened profiles (non-root, read-only root, tmpfs, `cap_drop ALL`, `no-new-privileges`, pids/ulimits, bounded egress, healthchecks); multi-zone Nginx limits keyed on real Cloudflare IP; scanner as one layer with honest limits | C4 §7 | DEC-169, DEC-171, DEC-162, DEC-088, DEC-020; arch §6.2, §7, §17 | ClamAV budget and fail-closed posture are B (question 2) and B (question 6) |
| A-10 | **Netdata + multi-region external uptime + Vercel-hosted automated status + Telegram alerts** with noise-resistant health logic and content-free alerts | C5 §7 | DEC-182, DEC-119, DEC-161, DEC-180, DEC-116; arch §20 | Provider selection and account creation are deployment-time owner actions (C) |
| A-11 | **restic to S3-compatible destination; isolated monthly restore verification**; ephemeral processing state excluded from backups; DR distinct from release rollback | C6 §7 | DEC-173, DEC-181, DEC-178; arch §18.4 | Retention window/drill host are defaults (C) |
| A-12 | **Threat classification and fail-closed matrix** (anything not classifiable as safe fails closed); DEC-088 blocking precedes DEC-090 sanitization; prohibited-data register enforced by the D3 leakage-test suite | D5 §6.1, §6.6 | DEC-088, DEC-090, DEC-065, DEC-036; arch §17, §23 | The matrix is compatible; scanner selection confirmation is B (question 6) |
| A-13 | **Analytics boundary schema:** Vercel Web Analytics baseline + privacy-reviewed custom events + `beforeSend` redaction + opt-out; allowed/prohibited field lists; closed-set sanitized failure categories; leakage-test suite in CI | D3 §7 | DEC-025, DEC-126, DEC-024; UX §17; arch §22.3 | ePrivacy consent interaction depends on the D1 decision (B question 3) |
| A-14 | **Contact/support: Cloudflare-native delivery** (Worker/function validating Turnstile + honeypot + rate limit, Email Routing to owner inbox); minimal data model; 30-day retention default; redaction-safe errors; no unsupportable response-time promises | D4 §7 | DEC-046, DEC-050, DEC-117, DEC-120, DEC-110; UX §15.3; arch §23.2 | Email Sending beta vs free-path `email()` handler is an implementation-time confirmation (C) |
| A-15 | **Legal copy baseline:** EN disclosure inventory + qualified legal review before launch + controlled ES/ID localization; re-scope of legacy "no tracking"/"PATUH" claims; three pages in three locales with version history | D2 §6–7 | DEC-045, DEC-168, DEC-022, DEC-110; UX §15.2, §21.10 | Cannot finalize before the ad-consent decision (B question 3); joint-controllership etc. are legal-review scope (C) |
| A-16 | **WCAG 2.2 AA four-layer program:** axe-core in CI (target-size rule enabled) + manual keyboard passes + representative AT passes (NVDA/JAWS/VoiceOver/TalkBack) + documented exceptions register; no certification claims | B2 §7 | DEC-062; UX §16; arch §22.1–22.2, §22.4 | AT combination list and external-review timing are deferred (C) |
| A-17 | **UI-baseline verification methods:** contrast re-verification method, `@theme inline` emission check, rendered-visual-verification standard; the four owner prompts (D3, U3, U5/D12, Merge edge case) are recorded as design/copy-pass confirmations, not material decisions | B5 §6–7 | DEC-143; UX §21.11–19, §10.6 | Rendered pass deferred to implementation (phase prohibition); UI prompts are C, not elevated here per the no-UI-micro-decision rule |
| A-18 | **Blog pipeline architecture (contingent):** scheduled content-bot workflow producing gate-passing PRs that auto-merge through the normal build path; `@next/mdx` with strict frontmatter schema and component allowlist; kill-switch and pause thresholds; secrets only in Actions environments | E2 §7 | DEC-048, DEC-049, DEC-053, DEC-124, DEC-096, DEC-097; UX §15.6; arch §25.3.21 | Design finalization is **blocked** on the E1 provider documentation (D-1); architecture shape is compatible |
| A-19 | **Launch-topic criteria and cadence rules** (at most one coordinated trilingual set per day, UTC boundary, skip-over-weaken, DEC-113 dates, no future dates; 9 selection criteria incl. owner-supplied demand evidence); the five candidate topics are a proposal, not a decision | E3 §7 | DEC-052, DEC-053, DEC-121, DEC-124, DEC-113; UX §19.8, §21.5 | Topic selection is a proposal for owner approval (C); demand data is owner-supplied (D) |

## 5. Category B — Genuine conflicts requiring explicit owner decisions

These are material decision points where accepted decisions, brief recommendations, or specs do not determine a unique outcome, and where the owner must choose. Each maps to a collapsed owner question in Section 8. The briefs escalated these rather than resolving them (DEC-183), and this report preserves that status.

### B-1. Ghostscript licensing and the Compress engine (K3) — Owner question 1

- **Where documented:** A1 §5.4, §7, §9 (items 1, 2, 9); A2 §7; D5 §4.3/§8; X1 K3.
- **The conflict:** A1/A2 recommend Ghostscript `pdfwrite` for Compress as the strongest capability match (documented Distiller-parameter downsampling/re-encoding for the premium-screen profile, DEC-014). Ghostscript is AGPL-3.0-or-later or Artifex-commercial; AGPL §13 network-use obligations apply to the combined SaaS work unless a commercial license is obtained (A1 §5.4, citing Artifex and the Ricoh/Artifex dual-licensing text). A5 and A6 avoid the AGPL fork entirely by recommending fully permissive engines (img2pdf/Pillow; pypdfium2/pdf.js). The whole matrix's coherence depends on one owner decision (X1 K3: "single largest cross-track owner dependency").
- **Evidence gaps:** Artifex commercial pricing is not public; industry commentary (~$25k/yr) is secondary and unverified (M3). PyMuPDF AGPL-3.0-only vs or-later is unresolved in issue #4504 (A1 §9 item 2). Legacy invocation lacks `-dSAFER` (confirmed gap, A1 §5.2; must be corrected under any path).
- **What the owner decides:** (a) commercial Artifex licenses; (b) permissive-only Compress pipeline (pikepdf structural optimization + Pillow downsampling/re-encode + pikepdf sanitization — the A2 §7 fallback, which still produces an always-new artifact and honest reporting under DEC-080); or (c) releasing the processing-service code under AGPL. A secondary sub-choice (also part of question 1): whether to carry pdf-lib (unmaintained, Snyk INACTIVE) in the browser bundle with a design-time security review and fallback plan, or handle merge/split server-side entirely (A1 §9 item 9c).
- **Impact if unresolved:** Compress engine selection (arch §25.3.1, UX §21.1 item 2) and the browser merge/split dependency posture cannot be finalized. Everything else in Track A can proceed.

### B-2. VPS memory envelope: workers vs ClamAV (K2) — Owner question 2

- **Where documented:** C1 §7/§9 (2 workers × 2 GiB, API, Redis 384 MB, Nginx); C4 §7/§9 (ClamAV official recommendation 3–4 GiB RAM, "may get by with less"); C2 §9 (explicitly recorded per DEC-183); X1 K2.
- **The conflict:** Summed at upper bounds, 4 GiB workers + ClamAV 3–4 GiB + API/Redis/Nginx/system/Netdata exceed the ~8 GB / 4-core VPS envelope (legacy evidence: `papyr-reference/deploy/docker-compose.yml:17-24`, `runbook-vps.md:5.1`; current host state unverifiable, M13). C2's per-tool `maxEstimatedMemoryBytes` (0.75–1.5 GiB) fit a 2 GiB worker with margin but not a reduced one.
- **What the owner decides:** the reconciliation trade — (a) tune clamd to a deliberately smaller documented budget (reduced `MaxThreads`/scan-size limits, accepting the documented limitation); (b) reduce the worker bound (e.g., 1.5 GiB) and lower the estimated-memory gates; (c) reduce concurrency below 2 jobs; (d) authorize a bounded capacity trade (e.g., accept swap pressure) or an approved VPS upgrade (DEC-098 requires owner approval for vertical upgrades and DEC-095 for new spending). Also confirm fail-closed scanner posture (B-6 sub-item).
- **Impact if unresolved:** C1 worker bounds, C2 limit table, and C4 scanner budget cannot be locked; capacity/security architecture for the processing path stays open.

### B-3. EEA/UK/CH advertising consent conflict (K9, K8) — Owner question 3

- **Where documented:** D1 §4.2–4.3, §5–6, §8; D5 §6.7; DEC-022 (`papyr-rebuild-decisions.md:279-290`); X1 K8, K9.
- **The conflict:** DEC-022 accepts loading non-intrusive ads in all launch regions without prior consent, and explicitly records that this is not evidence of GDPR/UK GDPR/FADP/ePrivacy/PECR compliance and that "if prior consent is legally or contractually required, Papyr must either implement compliant consent controls, serve demonstrably non-tracking contextual advertisements, or suppress advertisements in the affected regions." D1's public-evidence review (provider Privacy/Cookies policies, EDPB Guidelines 05/2020, ICO PECR, ePrivacy Art. 5(3), industry CMP environment) concludes that EEA/UK/CH ePrivacy-style consent obligations are not satisfied by Adsterra's own GDPR statements, and that Adsterra's publisher terms are not public. D5 records that this *reinforces* (does not contradict) the DEC-022 risk record — the decision baseline is not rewritten.
- **Related:** K8 — legacy legal documents claim "Cookie Policy: Tidak diperlukan", "cookie consent banner TIDAK diperlukan", "Status: PATUH (Compliant)" (`26_Papyr_Legal_Pages_v1.0.md:90,299,320,639-649`), which conflict with the accepted analytics/advertising model and are re-scoped by D2, not resolved here.
- **What the owner decides:** (a) keep DEC-022 as-is (accepted risk); (b) prior consent via a CMP for EEA/UK/CH (and optionally California) — contradicts the no-prior-consent preference, so it requires an explicit superseding decision; or (c) regional suppression (C2) or demonstrably non-tracking contextual ads (C1, unverified against the provider) — aligned with DEC-104's "suppress affected behavior while preserving product access." D1 recommends B or C2. The owner must also supply the Adsterra publisher terms and the exact ad-unit code for `mypapyr.com` (D-2) so the consent question can be verified rather than inferred.
- **Impact if unresolved:** D2 legal copy cannot finalize (it must be self-consistent with the D1 outcome); D3's analytics consent interaction and the Cookies/Advertising page stay open; ad integration and UX §21.9/arch §25.3.12 stay gated. This is the largest legal-risk item.

### B-4. `gpt5.6-sol` identity and access path (K10) — Owner question 4 (shared with D-1)

- **Where documented:** E1 §5.1, §9.2; DEC-051 (`papyr-rebuild-decisions.md:633-643`); X1 K10, M2.
- **The conflict:** DEC-051/plan wording records that the identifier "does not imply a specific vendor"; the public record as of 2026-07-31 identifies `gpt5.6-sol` with OpenAI's GPT-5.6 Sol family (released 2026-07-09; P1–P3 primary sources, S2 OpenRouter secondary). E1 reconciles: a "custom provider" can be an owner-managed access path (OpenAI platform account, an OpenAI-compatible gateway/reseller, Azure/Bedrock hosting, or a self-hosted deployment) serving the same public model family. The two are not contradictory, but the owner must confirm which access path the "custom provider" uses, including the exact identifier string the provider expects.
- **What the owner decides:** the access-path confirmation (part of question 4) and, via D-1, supplies the 14-field provider documentation (base URL, auth, schemas, structured outputs, tool use, rate limits, billed cost, context, retry, retention, availability/SLA, compliance policy, exact identifier).
- **Impact if unresolved:** Technical design of the provider integration (UX §21.21, arch §25.3.21) and consequently the E2 blog pipeline are blocked. No other track depends on this.

### B-5. Regional paper-policy interpretation (K1, K17) — Owner question 5

- **Where documented:** B3 §5.1, §7.1, §9 (items 1, 2); DEC-083 (`:1017-1027`), DEC-085 (`:1042-1052`), DEC-089 (`:1084-1094`); X1 K1, K17.
- **The conflict:** DEC-083 says the applicable locale is derived from the active Papyr locale plus a documented regional rule; DEC-085 (later, more specific) selects the trusted edge country code; DEC-089 completes the A4 fallback. B3 reads DEC-085/089 as operative (edge-country-only: `US`/`CA` → Letter, everything else or missing → A4; locale never decides paper) and requests owner confirmation of that reading. Separately, CLDR records de facto Letter usage in 12 additional countries (Mexico, Philippines, Chile, Colombia, Costa Rica, El Salvador, Guatemala, Nicaragua, Panama, Venezuela, Belize, Puerto Rico), while DEC-085 limits Letter to US and Canada; extending Letter requires a new explicit decision.
- **What the owner decides:** (a) confirm the edge-country-only rule as the accepted interpretation (recommended); (b) keep the two-country Letter rule (recommended, CLDR nuance documented as a known limitation) or extend Letter via a new decision.
- **Impact if unresolved:** UX §21.3 and arch §25.3.7 paper-policy mapping (consumed by A5 and the browser JPG-to-PDF path) stay interpretation-gated. Non-material if the recommended readings are accepted; the residual risk is small.

### B-6. Browser-path sanitization and scanner confirmation (K11, K4) — Owner question 6

- **Where documented:** A4 §5.1/§9.1; D5 §6.2 item 5; C4 §7/§9; DEC-090 (`:1096-1107`), DEC-093 (`:1133-1143`); X1 K11, K4.
- **The conflict (K11):** DEC-090's sanitization text targets "PDF-producing server outputs" (arch §17.3), while DEC-093 requires equivalent browser and server safety outcomes. pdf-lib browser page copies can carry page-level active content into Merge/Split outputs; the browser path has no sanitization pass. A4 recommends routing active-content-bearing files to the server sanitization path; D5 confirms A6 (rasterization) is unaffected. The owner/design must confirm that routing-to-server is the accepted browser-path safety mechanism (with the routing signal: detect active content in the browser, then route).
- **The sub-conflict (K4):** DEC-171 requires a maintained general malware scanner as a defense layer; ClamAV's PDF-detection coverage is documented as limited. The briefs resolve this only by the honest-limits rule (no malware-free claims). The owner confirms the scanner choice (ClamAV candidate) and the fail-closed posture on scanner outage (C4 §7 prompt 1: fail-closed recommended; a narrowly-scoped fail-open would contradict DEC-169's layering).
- **What the owner decides:** (a) browser-path safety = route active-content-bearing Merge/Split files to the server sanitization path (recommended) vs a separate browser sanitization pass; (b) confirm ClamAV (or an equally maintained scanner) and fail-closed admission on scanner unavailability; (c) Trivy gate CRITICAL-only vs include HIGH (C4 §9).
- **Impact if unresolved:** The Merge/Split browser/server safety-equivalence requirement (DEC-093) and the scanner layer (arch §25.3.8) stay open.

### B-7. Legacy URL dispositions vs DEC-114 traffic test (K12) — Owner question 7

- **Where documented:** B4 §6, §9 (items 1, 9); DEC-114 (`:1374-1384`), DEC-127; X1 K12, M4, M5.
- **The conflict:** B4 recommends 410 Gone for the eight deferred tool URLs (`/rotate`, `/protect`, `/unlock`, `/watermark`, `/sign`, `/pdf-to-word`, `/ocr`, `/pdf-to-excel`); DEC-114 says legacy pages still receiving meaningful traffic should be retained and updated. No traffic data is available in read-only research (M4), so DEC-114's traffic test cannot be applied; the disposition table therefore assumes the sitemap-bounded inventory (16 indexable URLs, M5).
- **What the owner decides:** using their traffic knowledge, whether any deferred tool URL deserves a redirect to a relevant live page instead of 410; the slug table confirmation and the locale-less entry redirect status (302/307 vs 301) are recommended defaults that remain within SEO design (UX §21.4) — these are recorded as deferred (C), not elevated here.
- **Impact if unresolved:** The redirect map (arch §25.3.15, UX §21.4) cannot finalize; migration hygiene and D2's legal pages target consistency stay gated.

---

## 6. Category C — Deferred non-blocking questions and defaults

These carry documented conservative defaults, are adjustable from production telemetry per DEC-066, or are minor confirmations that do not block planning. They are recorded so the owner can confirm them in one pass without micro-detail questions.

| # | Item | Default / recommendation | Evidence | Notes |
|---|---|---|---|---|
| C-1 | Per-tool server limit values | C2 §7.1 table (e.g., 100 MB/1000 pages Compress; 20 files/200 MB/1000 pages Merge; 100 outputs Split; 50 files/100 MP/20 MP per image JPG-to-PDF; 200 pages/16 MP PDF-to-JPG) | C2 §7, §7.5 | Conservative design/safety defaults; raising procedure documented; owner approval only for *material* raises (DEC-057) |
| C-2 | Queue caps and worker count | 2 workers × 1 job, 2 GiB, 180 s default; queue 2000/15 min; 4 per origin; Redis 384 MB `noeviction`; AOF everysec | C1 §7 | Maintained-framework-vs-custom preference left to owner as a non-blocking confirmation |
| C-3 | R2 lifecycle safety-net age | 1 day (effective removal ~1–2 days with R2's documented lag) vs 2 days for extra margin | C3 §7 | Owner can pick without blocking planning |
| C-4 | Nginx rate-zone values | Admission 10 r/m burst 5 (legacy value); status 60 r/m burst 30; health unrate-limited; `limit_req_status 429` | C4 §7 | 10 r/m is not a daily quota; adjustable from telemetry |
| C-5 | Monitoring provider and thresholds | Netdata + multi-region external uptime + Vercel status; provider accounts are deployment-time owner actions; free-tier limits unconfirmed (M14) | C5 §9, §5.2 | Accounts require owner action at deployment, not planning |
| C-6 | Backup retention window and drill host | restic; retention/restore-target values are design choices; isolated monthly restore | C6 §7, §9 | Non-blocking defaults |
| C-7 | Analytics micro-choices | Opt-out presentation (footer vs Privacy page), regional vs global opt-out, provider retention figure (M23) | D3 §8 | Dependent on the D1 outcome for consent gating; otherwise defaulted |
| C-8 | Support defaults | 30-day contact/result-report retention default; response-time statement = no public commitment (DEC-050); dedicated security address optional | D4 §8 | Owner confirmation optional; defaults are decision-compliant |
| C-9 | UI-baseline owner prompts (UX §21.13–16) | D3 navbar width (1440 vs 1200 convention), U3 duplicate CTA intent, U5 homepage entrance animations (+D12 dropdown transition), Merge error-state auto-clear | B5 §6–7; UX §10.6, §21 | Explicitly **not** elevated to material owner questions (task constraint); confirmed in the copy/design pass |
| C-10 | Blog topic selection and cadence details | Five candidate topics (E3 §7) are a proposal; 9 selection criteria; daily trilingual set; UTC boundary | E3 §7, §9 | Demand data is owner-supplied (D-4); topics remain proposals |
| C-11 | Implementation-time re-checks (M6–M11, M16–M20, M22–M23) | Pin Redis version; confirm trusted-edge header config (M9); pin next-i18next (M10); confirm Email Sending beta vs `email()` handler (M16); pdf.js legacy floor vs pinned version (M18); WebAIM survey freshness (M19); WCAG 2.2 2024-12-12 revision (M20); Vercel analytics retention (M23); vendor tool-coverage claims unverified (B2) | X1 §8 | DEC-056 requires rechecking at implementation; none blocks planning |
| C-12 | Process-level notes | caniuse vs BCD (K5); RFC 5988 vs 8288 (K6); MDN hidden-input technique (K7); legacy compliance claims re-scoping (K8); legacy SLA targets not carried (K16); template-count discrepancy (K18); 16-MP ceiling mirrored as server default (K14); Compress server-only reading (K15) | X1 §7 | Recorded, not blocking; each has a documented disposition |

## 7. Category D — Source and contract blockers

These are owner-supplied or access-gated inputs required before technical design can finalize. They are gaps in the *source base*, not failures of the briefs (DEC-056 compliance: all gaps were recorded, none fabricated).

| # | Blocker | Required input | Governed by | Blocks |
|---|---|---|---|---|
| D-1 | `gpt5.6-sol` private provider documentation (M2) | 14 contract fields: exact identifier string, base URL, auth scheme, request/response schema, structured-output support, tool use, rate limits at the owner's tier, billed cost, effective context, retry behavior, data-retention commitment, availability/SLA, compliance/safety policy | DEC-051; UX §21.21; arch §25.3.21; E1 §8–9 | E2 pipeline technical design; provider adapter, retry, and cost-ceiling design. **Only true hard blocker on a design path** |
| D-2 | Adsterra publisher terms + ad-unit code (M1) | Current publisher Terms and Conditions (not public; `/terms-conditions/` redirects to homepage), the exact banner/native ad-unit code for `mypapyr.com`, the unit's cookies/identifiers/recipients, and any EEA/UK-specific provider requirements | DEC-022, DEC-045; D1 §4.5/§8; UX §21.9; arch §25.3.12 | Consent decision verification (B-3), D2 Cookies/Advertising copy, ad integration design |
| D-3 | Current VPS host state (M13) | Verification of the ~8 GB / 4-core / 4.5 GB swap assumption before first deployment | DEC-172, DEC-160; C1/C2/C4 §9 | Capacity/architecture finalization (feeds B-2); re-verify before deployment |
| D-4 | Legacy traffic and demand data (M4, M5) | Owner's traffic knowledge for DEC-114's "meaningful traffic" test on deferred URLs; Search Console/keyword demand evidence for blog topics | DEC-114, DEC-127; B4 §9.1; E3 §9.1 | Legacy URL dispositions (B-7); blog topic demand validation |
| D-5 | AGPL/commercial engine pricing (M3) | Artifex commercial pricing (not public; ~$25k/yr industry figure is secondary and unverified) | A1 §9.1 | Informs the B-1 licensing decision (does not block it) |

Also recorded: the browser routing signal set (estimated peak memory, active-content detection in the browser) and the `estimatedPeak` formula are design-time deliverables, not source gaps (C2 §9, B1 §5).

## 8. Collapsed high-level material owner questions

All ~50 brief-level prompts reduce to the following **seven** high-level decisions. They are ordered by materiality (cost, legal risk, licensing, capacity/security architecture, provider contract). Each maps to the category-B analysis above and to the decisions/spec sections that would be amended or confirmed.

**Q1 — Licensing: Compress engine and AGPL compliance (B-1).** Choose the compliance path for AGPL engines (Ghostscript/MuPDF/PyMuPDF): (a) commercial Artifex licenses, (b) permissive-only matrix (Compress via pikepdf + Pillow pipeline; A5/A6 pairings already permissive), or (c) AGPL-released processing service. Include the secondary confirmation on carrying pdf-lib (unmaintained) in the browser bundle with a fallback plan. (DEC-059, DEC-056, DEC-095; arch §25.3.1; A1/A2.)

**Q2 — Capacity/security architecture: VPS memory envelope (B-2).** Decide how the ~8 GB host reconciles 2 GiB workers + ClamAV's documented 3–4 GiB + API/Redis/Nginx: tune clamd to a smaller documented budget, reduce worker bounds, reduce concurrency, or authorize a bounded capacity/VPS-upgrade trade. (DEC-098, DEC-095, DEC-169, DEC-171; C1/C2/C4.)

**Q3 — Legal risk: advertising consent in EEA/UK/CH (B-3).** Keep DEC-022 as-is (accepted risk), introduce prior consent via CMP, or suppress/non-track ads in consent-required regions (plus California characterization under legal review). (DEC-022 consequence clause, DEC-104; D1/D2/D3.)

**Q4 — Provider contract: `gpt5.6-sol` (B-4 + D-1).** Confirm the access path (OpenAI platform / compatible gateway / Azure or Bedrock / self-hosted) and supply the 14-field provider documentation. (DEC-051; UX §21.21; arch §25.3.21; E1.)

**Q5 — Regional paper policy (B-5).** Confirm the edge-country-only rule as the operative interpretation and keep Letter limited to US/CA (recommended) or extend to the 12 CLDR de-facto Letter countries. (DEC-083/085/089; B3.)

**Q6 — Security architecture: browser-path sanitization and scanner (B-6).** Confirm that active-content-bearing Merge/Split files route to the server sanitization path (vs a browser sanitization pass), and confirm the maintained scanner (ClamAV candidate) with fail-closed admission. (DEC-090/093/171, DEC-169; A4/D5/C4.)

**Q7 — SEO/URL migration: deferred-tool dispositions (B-7).** Using the owner's traffic knowledge, confirm 410 Gone for the eight deferred tool URLs or targeted redirects where traffic exists; the slug table and entry-redirect status are recommended defaults under SEO design. (DEC-114/127; B4.)

All other brief-level prompts are category-C defaults or category-D inputs and do not require a separate material decision.

## 9. Required explicit analyses

### 9.1 Ghostscript licensing / Compress engine

Analyzed at B-1. Summary: Ghostscript `pdfwrite` is the strongest capability match for the premium-screen profile (A2 §5.1, §7) and the legacy engine (`papyr-reference/backend/services/compress_service.py:72-86`, which lacks `-dSAFER` — a confirmed gap to correct). AGPL-3.0-or-later / Artifex-commercial dual licensing (A1 §5.4) makes SaaS use the decisive cost question: AGPL §13 network-use obligations on the combined work unless commercially licensed. Pricing is unverified (M3/D-5). The permissive fallback (pikepdf structural optimization + Pillow image downsampling/re-encode + pikepdf sanitization) meets DEC-080 (always-new artifact) and DEC-090 (sanitization) but delivers materially less size reduction for image-heavy PDFs — a documented capability trade, not a benchmark claim (DEC-066). Outcome: one owner decision (Q1) gates arch §25.3.1 and UX §21.1 item 2 only.

### 9.2 VPS memory vs workers / ClamAV

Analyzed at B-2. Summary: legacy host basis 8 GB / 4 vCPU / 4.5 GB swap (`papyr-reference/deploy/docker-compose.yml:17-24`, `runbook-vps.md:5.1`; unverifiable without access, M13). C1's 2 × 2 GiB workers + API + Redis (384 MB) + Nginx + C4's ClamAV 3–4 GiB exceed the envelope at upper bounds (X1 K2). C2's estimated-memory gate fits a 2 GiB worker with margin but is coupled to the worker bound. DEC-066 means no measurement exists and none may be created; the reconciliation must be a documented budget decision (Q2) plus the DEC-098 vertical-upgrade gate if capacity proves insufficient. ClamAV's own docs allow "may get by with less" with documented limitations (C4 §5.2), so a tuned budget is viable without changing the fail-closed posture.

### 9.3 EEA/UK/CH ad consent conflict

Analyzed at B-3. Summary: DEC-022 (`:279-290`) accepts no-consent loading in all launch regions as a recorded compliance risk, with an explicit consequence clause requiring consent controls, non-tracking contextual ads, or regional suppression if prior consent is legally/contractually required. D1's provider review (Adsterra Privacy/Cookies policies effective 29.06.2026/Jan 2023, onboarding guide, `/terms-conditions/` redirect; EDPB 05/2020, ICO PECR, ePrivacy Art. 5(3), Google CMP environment) finds EEA/UK/CH consent obligations not satisfied by the provider's GDPR statements and the binding terms unreadable (D-2). D5 §6.7 records the finding as reinforcing, not contradicting, DEC-022. Owner decision Q3 is required before D2 copy, D3 consent gating, and UX §21.9/arch §25.3.12 finalize.

### 9.4 `gpt5.6-sol` custom provider contract

Analyzed at B-4 and D-1. Summary: public record (P1–P3, accessed 2026-07-31) identifies the identifier with OpenAI GPT-5.6 Sol (released 2026-07-09, $5/$30 per 1M, 1M context, `max`/`ultra` reasoning, Programmatic Tool Calling, ZDR compatibility). DEC-051's vendor-neutral wording and the public record are reconcilable via an owner-managed access path; E1's known/unknown matrix (14 fields) separates verified public facts from owner-supplied gaps. The owner's confirmation (Q4) plus the documentation supply (D-1) is the **only true hard blocker on a design path** (UX §21.21, arch §25.3.21, E2). No provider access, account creation, or API call was performed during research (E1 §12).

### 9.5 Regional paper policy

Analyzed at B-5. Summary: DEC-083 (locale-derived), DEC-085 (edge-country mechanism), DEC-089 (A4 fallback) form a three-decision chain whose operative reading is the edge-country-only rule (`US`/`CA` → Letter; all else/absent → A4; locale never decides paper; value ephemeral, never a profile). CLDR records de facto Letter in 12 additional countries; the accepted two-country rule is the default with the nuance documented (K17). Owner confirmation Q5 resolves UX §21.3 and arch §25.3.7; the implementation detail (trusted-header configuration, M9) is a category-C re-check.

### 9.6 Source gaps that block planning

- **Hard blocker:** `gpt5.6-sol` provider docs (D-1) — blocks the blog pipeline design path (E2), nothing else.
- **Contract verification inputs:** Adsterra publisher terms + ad-unit code (D-2) — required to verify the Q3 consent decision and finalize D2 copy.
- **Operational data:** VPS host state (D-3) and legacy traffic/demand data (D-4) — required to finalize the memory envelope (Q2) and URL dispositions (Q7); both are deployment- or owner-side inputs, not research gaps.
- **Pricing data:** AGPL commercial pricing (D-5) — informs Q1 but does not block it.
- **Non-blocking gaps:** M6–M11, M14–M23 are implementation-time re-checks (category C-11) and do not block planning.

## 10. What may proceed into implementation planning after the owner resolves the blockers

Once the owner answers Q1–Q7 (and the D-1/D-2 inputs are supplied), the following design areas are unblocked and may proceed into implementation planning. This is a statement of readiness, not an implementation plan (DEC-060, DEC-185):

1. **Frontend and UX:** tool flows (UX §12), shared states and download behavior (§13), advertising placement (UX §14; subject to Q3), legal surfaces (D2; subject to Q3), status/roadmap (UX §15.4–15.5), responsive and WCAG 2.2 AA program (B2/B5; §16, §20), analytics schema (D3; subject to Q3), error/recovery behavior (§18).
2. **Routing and capability contract:** B1 layered routing; C2 per-tool server limits table and the machine-readable contract (arch §14); DEC-165 contract shape and failure-code set (C2 §7.4); browser/server limit separation.
3. **Backend architecture:** C1 queue/worker/Redis design; C3 R2 lifecycle and one-hour enforcement; C4 per-service hardening profiles and Nginx zones; D5 threat-classification and fail-closed matrix; task state machine and session recovery (arch §13); signed downloads (arch §15). The memory-envelope and scanner decisions (Q2, Q6) are the only capacity inputs pending.
4. **SEO and content migration:** B4 slug table and redirect map (subject to Q7); hreflang/canonical/sitemap rules; B3 paper-policy function (subject to Q5); ID slug mapping.
5. **Monitoring and operations:** C5 monitoring/status/Telegram design; C6 backup and monthly restore verification; DEC-176 secrets procedure; CI core gate and manual deployment/rollback (arch §19).
6. **Blog automation:** E2 pipeline architecture (after D-1/E1 contract); E3 topic criteria and cadence rules; topic selection remains an owner approval.
7. **Engine matrix:** A3–A6 pairings as recommended; A2 Compress path (after Q1); pdf-lib carry decision (part of Q1).
8. **Testing and acceptance:** functional acceptance criteria from all 25 briefs, mapped to the core gate (DEC-177); privacy leakage tests (D3), security fixtures (D5), WCAG checks (B2), migration hygiene tests (B4).

Nothing above is authorized for implementation until the owner approves the resulting design and implementation plan (DEC-057, DEC-060, DEC-188).

## 11. `papyr-reference/` unchanged — evidence

- Command (read-only): `git -C papyr-reference status --porcelain` — **empty output, exit 0** (verified 2026-07-31 for this report).
- HEAD: `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` — `981c59a docs(fase2): mark STEP-F2-063 complete`.
- This matches the HEAD recorded by PPR-VER-001 and by every brief's own before/after verification. No tracked or untracked change exists. No file under `papyr-reference/` was read-write; all references in this report cite legacy paths as evidence only (DEC-001, DEC-059, DEC-099).

## 12. Files not modified by this reconciliation

- `papyr-rebuild-decisions.md` — not edited (append-only log; no new decision created).
- Both approved specifications — not edited.
- All 25 research briefs, X1, and all evidence files — not edited.
- `AGENTS.md` — not edited.
- `papyr-reference/` — not touched (Section 11).
- The only file created by this task is this report.

## 13. Placeholder verification

- Method: after writing, `grep -iE 'TODO|TBD|FIXME|XXX|lorem ipsum|placeholder|WIP'` over `audit-outputs/research/reconciliation-report.md`.
- Result: **0 placeholder tokens**. No TODO, TBD, FIXME, XXX, "lorem ipsum", or WIP token appears in this file. The word "placeholder" occurs only in self-verification prose (Section 2.1 and this section) describing the scans performed, never as a leftover token. All open items are named decisions (Q1–Q7), named defaults (C-1…C-12), or named blockers (D-1…D-5), consistent with the spec convention (arch §26.1) of recording unresolved items as named choices rather than tokens.
- Verification command and output are recorded in the execution trail of this task; the report was re-scanned after the final edit.

## 14. DEC-066 preservation statement

- No benchmark program, corpus, matrix, comparative quality/performance study, quality-score program, VPS benchmark workload, or benchmark report is introduced, recommended, or implied by this report.
- All numeric values referenced (C2 limits, C1 queue caps, C3 lifecycle age, B1 routing caps, A2/A6 profile starting points) are explicitly conservative design/safety choices adjustable from production observability (DEC-066).
- No acceptance criterion in any brief or in this report depends on benchmark evidence; all are functional/operational verification criteria.

## 15. Prohibitions-compliance statement

- No decision log, specification, brief, evidence file, or `AGENTS.md` content was modified; no new decision was created (all recommendations remain subject to DEC-057).
- No implementation, scaffolding, installs, builds, services, VPS/SSH access, deployment, account creation, provider authentication, or remote mutation was performed (plan §4.1; DEC-060, DEC-160, DEC-172).
- `papyr-reference/` remains unchanged (Section 11).
- No web research was performed beyond the sources already recorded in the briefs; no citation was re-fetched because no contradiction required resolution.
- Conflicts K1–K18 and gaps M1–M23 are surfaced, not resolved (DEC-183). Category-B items are presented to the owner as decisions, not silently decided.
- This file is the primary deliverable; a chat-only summary is insufficient.
