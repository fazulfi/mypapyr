# Papyr Rebuild: Structured Research Execution Plan

| Field | Value |
|---|---|
| Document ID | PPR-RP-001 |
| Title | Papyr Rebuild Structured Research Execution Plan |
| Version | 1.0 |
| Date | 2026-07-31 |
| Canonical language | English (DEC-184) |
| Status | Approved for execution by the owner ("continue"); research briefs are not yet created |
| Governing decisions | DEC-054 through DEC-060, DEC-066, DEC-188 (see Section 3) |
| Governing rules | `<workspace-root>\AGENTS.md` (Papyr Rebuild Orchestrator Rules) |
| Plan author | Sisyphus-Junior (executor subagent), persisting the prior Plan Agent's accepted program structure |
| Primary deliverable | this file |
| Output root | `<workspace-root>\audit-outputs\research\` |

---

## 1. Purpose

This plan turns the owner-approved specifications (DEC-188) and the accepted parallel-track research program into a durable, executable plan. It defines bounded tracks, exact deliverable paths, the mandatory brief template, source priority, delegation contracts, dependencies, waves, stopping conditions, verification assertions, and the owner-review handoff.

The owner approved both written specifications and said to continue (DEC-188). A prior Plan Agent designed this program but could not persist it because it ran in read-only mode. This file is the durable primary artifact required by AGENTS.md.

## 2. Scope

This plan governs the research phase only.

### 2.1 What the research phase produces

- 25 structured research briefs under `audit-outputs\research\` (Tracks A through E).
- One `source-and-decision-index.md`.
- One `reconciliation-report.md`.
- The owner-review handoff that follows.

### 2.2 What the research phase does not produce

- No product code, scaffolding, or implementation.
- No benchmark program, corpus, matrix, comparative quality or performance report.
- No installs, builds, server starts, VPS/SSH access, deployment, or account creation.
- No modifications to `papyr-reference/`, the decision log, the specifications, or any existing `audit-outputs/` file.
- No commits. The workspace root `<workspace-root>` is not currently a git repository, and no commits are part of this phase (Section 13).

## 3. Governing gates

The following accepted decisions are hard gates for every research brief and for this program as a whole:

| Decision | Gate applied here |
|---|---|
| DEC-054 | Every brief requires deep, evidence-based research with stated alternatives, trade-offs, risks, cost and operational impact, privacy and security implications, and measurable acceptance criteria. Findings are recommendations, not accepted decisions. |
| DEC-055 | Every brief uses the structured template in Section 8. At least two viable approaches are compared unless evidence shows only one is feasible. Briefs link to their governing decisions. |
| DEC-056 | Primary sources are prioritized: current official documentation, standards, source code, licenses, security advisories, and contractual or legal terms. Secondary sources only support, never solely justify. Sources carry URLs or identifiers, dates, and versions. |
| DEC-057 | Owner approval is required for every researched feature to move into design and implementation planning. No brief result auto-authorizes implementation. |
| DEC-058 | Research runs in parallel domain tracks with bounded scope, named deliverables, dependencies, evidence standards, and a synthesis checkpoint. A shared source and decision index prevents duplication. |
| DEC-059 | All five tools are re-researched from first principles. Legacy code is reference evidence, not an automatically accepted requirement. |
| DEC-060 | Rebuild coding stays blocked until briefs are complete, cross-domain findings are reconciled, design is approved, and an implementation plan is reviewed. |
| DEC-066 | No formal or informal benchmark program. No corpora, matrices, comparative performance studies, quality-score programs, VPS benchmark workloads, or benchmark reports. Limits are conservative design or safety choices adjusted from production observations. |
| DEC-188 | The two specifications govern the structured research briefs and cross-domain reconciliation. Implementation planning remains blocked until research and reconciliation are completed and reviewed. |

DEC-183 is also in force for conflict handling: material contradictions discovered during research are surfaced to the owner, never silently resolved.

## 4. Prohibitions and permitted actions

### 4.1 Explicitly prohibited during research

- Formal or informal benchmark programs, corpora, benchmark matrices, comparative quality or performance reports, quality-score programs, or VPS benchmark workloads (DEC-066).
- Implementation: no product code, scaffolding, feature code, or infrastructure modification (DEC-060).
- Installs, dependency installation, builds, container builds, or server starts of any kind.
- VPS/SSH access, configuration, or account creation on any host (DEC-172, DEC-160).
- Deployment, DNS or provider changes, or production operations (DEC-160).
- Account creation at any provider, including Adsterra, analytics, monitoring, or email services.
- Modifying `papyr-reference/` in any way (read-only reference per AGENTS.md and DEC-001).
- Modifying `papyr-rebuild-decisions.md`, the two specifications, or any existing `audit-outputs/` file.
- Authenticated or mutating remote actions: no API calls with credentials, no account access, no writes to any remote service.
- Fabricating sources, authors, test results, citations, or product claims (DEC-048).
- Silently resolving conflicts between findings or between findings and the specifications (DEC-183).

### 4.2 Permitted during research

- Read-only inspection of `papyr-reference/`, the decision log, the specifications, and existing `audit-outputs/` files.
- Read-only web search and fetch of public primary documentation: official library, engine, and provider documentation; license texts; standards bodies; security advisories; Adsterra publisher terms; and authoritative legal and regulatory summaries (DEC-056).
- Read-only `git status` inside `papyr-reference/` for cleanliness verification.
- Writing only the assigned deliverable files under `audit-outputs\research\`.

## 5. Source priority

When evidence conflicts, the following precedence applies, consistent with the architecture specification Section 1.4:

1. `<workspace-root>\papyr-rebuild-decisions.md`: authoritative record of accepted decisions.
2. `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` and `...\2026-07-31-papyr-technical-architecture.md`: canonical design documents derived from the decision baseline (DEC-185, DEC-188).
3. `audit-outputs\` files: durable evidence supporting design, not standalone requirements.
4. `papyr-reference\`: read-only legacy clone, evidence of the current baseline only (DEC-001, DEC-059).
5. Historical legacy documents in `papyr-reference\docs\`: non-canonical historical material (DEC-026).

External evidence within a brief must rank primary sources first per DEC-056: official documentation and source code above community material, license and advisory texts above summaries, and current versions above stale ones. Every external source records its URL or identifier and its access date.

## 6. Deliverables map

All research deliverables live under `audit-outputs\research\`. The plan itself lives at `audit-outputs\research-program-plan.md`.

### 6.1 Track A: tool and engine research (shared evidence first)

| # | Deliverable path | Title | Primary open items served |
|---|---|---|---|
| A1 | `audit-outputs\research\track-a\a1-shared-engine-licenses.md` | Shared engine and license evidence | Arch §25.3.1; DEC-059, DEC-056 |
| A2 | `audit-outputs\research\track-a\a2-compress-pdf.md` | Compress PDF research brief | UX §21.1-2; Arch §25.3.1, §25.3.6 |
| A3 | `audit-outputs\research\track-a\a3-merge-pdf.md` | Merge PDF research brief | UX §21.1; Arch §25.3.2; DEC-079 |
| A4 | `audit-outputs\research\track-a\a4-split-pdf.md` | Split PDF research brief | UX §21.1; Arch §25.3.2 |
| A5 | `audit-outputs\research\track-a\a5-jpg-to-pdf.md` | JPG to PDF research brief | UX §21.1; Arch §25.3.2, §25.3.7 |
| A6 | `audit-outputs\research\track-a\a6-pdf-to-jpg.md` | PDF to JPG research brief | UX §21.1-2; Arch §25.3.2, §25.3.6 |

A1 must complete before A2 through A6 can finalize their engine and library recommendations. A2 through A6 may run in parallel with each other after A1 delivers its evidence table.

### 6.2 Track B: frontend, capability, and SEO research

| # | Deliverable path | Title | Primary open items served |
|---|---|---|---|
| B1 | `audit-outputs\research\track-b\b1-browser-capability-routing.md` | Browser capability detection and routing thresholds | Arch §25.3.17; UX §21.1; DEC-015, DEC-030, DEC-065 |
| B2 | `audit-outputs\research\track-b\b2-accessibility.md` | Accessibility and WCAG 2.2 AA research brief | UX §21.11-12; DEC-062 |
| B3 | `audit-outputs\research\track-b\b3-i18n-locale-paper-policy.md` | i18n, locale, and paper-standard policy research | UX §21.3, §21.6; Arch §25.3.7; DEC-083, DEC-085, DEC-089 |
| B4 | `audit-outputs\research\track-b\b4-seo-url-migration.md` | SEO, slugs, and legacy URL migration research | UX §21.4; Arch §25.3.15-16; DEC-023, DEC-122, DEC-127, DEC-114, DEC-099 |
| B5 | `audit-outputs\research\track-b\b5-ui-baseline-verification.md` | UI-baseline verification checklist | UX §21.11-19 owner-confirmation and verification items; D3, U3, U5, D12, U1 |

B5 is a checklist-and-scope deliverable: it packages the owner-confirmation items (navbar width intent D3, duplicate CTA intent U3, homepage entrance animations U5 and D12, Merge error-state edge case), the contrast re-verification method (UX §21.12), the `@theme inline` token emission verification (UX §21.19), and the rendered visual verification standard (UX §21.11). Because running a browser against the legacy site requires a build or server start, which this phase prohibits, B5 defines the checklist, evidence standard, and owner decision prompts now and defers the actual rendered pass to implementation-time verification. It does not execute the pass.

### 6.3 Track C: infrastructure and operations research

| # | Deliverable path | Title | Primary open items served |
|---|---|---|---|
| C1 | `audit-outputs\research\track-c\c1-queue-workers-redis.md` | Queue, workers, and Redis research | Arch §25.3.3-5; DEC-019, DEC-020, DEC-035, DEC-137, DEC-174 |
| C2 | `audit-outputs\research\track-c\c2-per-tool-server-limits.md` | Per-tool server limits (follow-up wave) | UX §21.1; Arch §25.3.2; DEC-034, DEC-066 |
| C3 | `audit-outputs\research\track-c\c3-r2-lifecycle.md` | R2 lifecycle and retention enforcement | DEC-013, DEC-067, DEC-070, DEC-075, DEC-166 |
| C4 | `audit-outputs\research\track-c\c4-vps-processing-hardening.md` | VPS processing hardening and malware scanning | Arch §25.3.8-9; DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171 |
| C5 | `audit-outputs\research\track-c\c5-observability-status-telegram.md` | Observability, status, and Telegram research | Arch §25.3.10-11, §25.3.19; DEC-116, DEC-119, DEC-161, DEC-180, DEC-182, DEC-097, DEC-104 |
| C6 | `audit-outputs\research\track-c\c6-backups-restores.md` | Backups and restore verification research | Arch §25.3.20; DEC-173, DEC-181, DEC-178 |

C1, C3, C4, C5, and C6 run in Wave 1. C2 is the Wave 2 follow-up: it depends on the tool briefs (A2 through A6) for per-tool memory, output-expansion, and failure profiles, and on C1 for worker bounds and queue caps. C2 must not be started until A2 through A6 and C1 have produced their findings.

### 6.4 Track D: monetization, legal, privacy, support, and security requirements

| # | Deliverable path | Title | Primary open items served |
|---|---|---|---|
| D1 | `audit-outputs\research\track-d\d1-adsterra.md` | Adsterra terms, scripts, and consent review | UX §21.9; Arch §25.3.12; DEC-005, DEC-018, DEC-022 |
| D2 | `audit-outputs\research\track-d\d2-legal-privacy-copy.md` | Legal and privacy copy requirements | UX §21.10, §21.17; Arch §25.3.13; DEC-045, DEC-168, DEC-084, DEC-085, DEC-110 |
| D3 | `audit-outputs\research\track-d\d3-analytics-privacy.md` | Analytics and privacy boundaries | DEC-025, DEC-126; UX §17 |
| D4 | `audit-outputs\research\track-d\d4-contact-support.md` | Contact and support mechanisms | UX §21.7; Arch §25.3.14; DEC-046, DEC-050, DEC-117, DEC-120 |
| D5 | `audit-outputs\research\track-d\d5-security-threat-privacy.md` | Security, threat, and privacy requirements | DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171, DEC-036, DEC-064; UX §18 |

D2 produces the disclosure inventory and copy requirements for Privacy, Terms, and Cookies/Advertising, and scopes the qualified legal review that remains an owner action before launch (DEC-045). D2 does not provide legal advice and must not claim compliance (DEC-022). D1 reviews Adsterra's published publisher terms, script behavior as documented, and regional legal context from authoritative public sources; it must not access or create an Adsterra account and must not claim that its findings remove the DEC-022 accepted risk.

### 6.5 Track E: blog automation research

| # | Deliverable path | Title | Primary open items served |
|---|---|---|---|
| E1 | `audit-outputs\research\track-e\e1-gpt5-6-sol-contract.md` | `gpt5.6-sol` provider contract documentation | UX §21.21; Arch §25.3.21; DEC-051 |
| E2 | `audit-outputs\research\track-e\e2-automated-mdx-blog-pipeline.md` | Automated MDX blog pipeline research | DEC-048, DEC-049; UX §15.6 |
| E3 | `audit-outputs\research\track-e\e3-launch-postlaunch-topics.md` | Launch and post-launch localized topics | UX §21.5; DEC-052, DEC-053, DEC-121, DEC-124, DEC-113 |

E1 documents everything about the `gpt5.6-sol` provider that is discoverable from public sources and then produces an explicit documentation contract listing each item from DEC-051 (base URL, authentication, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, availability) with the exact gaps that only the owner can supply. No agent may authenticate to the provider or access it. The brief stops at the documentation contract; the owner supplies the private documentation before technical design finalization.

### 6.6 Cross-cutting deliverables

| # | Deliverable path | Title | When produced |
|---|---|---|---|
| X1 | `audit-outputs\research\source-and-decision-index.md` | Source and decision index | Maintained throughout, finalized in Wave 3 |
| X2 | `audit-outputs\research\reconciliation-report.md` | Cross-domain reconciliation report | Wave 4 |

X1 maps every research brief to its governing decisions, spec sections, primary sources, and dependent briefs, so that cross-track duplication is visible (DEC-058). X2 reconciles the 25 briefs: it lists confirmed findings, cross-track interfaces, material conflicts escalated to the owner, and the owner decision prompts that gate design and implementation planning (DEC-057, DEC-060, DEC-188).

## 7. Track definitions and research questions

Each brief answers the questions below plus its tool- or domain-specific questions. Questions are derived from the two specifications' unresolved-items lists and the governing decisions, not invented.

### 7.1 Track A questions (all six briefs)

- Which engine, library, or approach best satisfies the tool's approved behavior under DEC-059's first-principles requirement?
- What is the license of each candidate, and what are the obligations, including for server-side use, redistribution, and SaaS delivery? (A1 owns the consolidated license evidence; A2-A6 cite it.)
- What is the current official documentation and latest stable version for each candidate, with access dates?
- What are the representative failure modes and resource profiles (memory, time, disk, output expansion) for realistic inputs, described qualitatively and by documented engine characteristics, not by benchmark runs?
- Which legacy behavior is retained, which is corrected, and which is superseded, with file and line citations into `papyr-reference/`?
- What are at least two viable alternatives with trade-offs, and which is recommended?
- What are the measurable acceptance criteria for the tool's behavior under DEC-066 (functional verification, not comparison)?
- What are the cross-track interfaces: to B1 (browser capability), C2 (server limits), C4 (hardening and sanitization), D5 (threat handling)?

Tool-specific focus:

- A2 Compress: premium-screen profile thresholds (downsampling, re-encoding, quality floor) as design choices validated by functional testing (DEC-014, DEC-066); always-new-artifact and honest size reporting (DEC-080); server-default processing (DEC-015).
- A3 Merge: document-feature preservation to the safe extent supported (DEC-079); active-content sanitization (DEC-090, DEC-091); per-file passwords (DEC-074); all-or-nothing failure (DEC-076); browser-first with server fallback.
- A4 Split: range syntax and validation (DEC-038); overlap as independent outputs (DEC-077); user-entered order (DEC-078); ZIP plus individual downloads (DEC-037).
- A5 JPG to PDF: accepted formats JPG/JPEG, PNG, WebP (DEC-187); byte-level validation and decode isolation (DEC-093); automatic per-image fitting (DEC-041, DEC-082); paper policy interfaces with B3 (DEC-083, DEC-085, DEC-089); metadata preservation and disclosure (DEC-084).
- A6 PDF to JPG: automatic output profile (DEC-039); white compositing (DEC-081); 16-megapixel ceiling (DEC-015); duplicate-preserving order-preserving page selection (DEC-186); untrusted-input rendering (DEC-092).

### 7.2 Track B questions

- B1: What capability signals (memory, dimensions, encryption, corruption, APIs) determine local feasibility? What are the conservative routing thresholds for each tool per DEC-015, DEC-030, and DEC-065? How do the browser support matrix (DEC-031) and progressive enhancement affect routing? Interfaces to A2-A6 and C2.
- B2: What does WCAG 2.2 Level AA acceptance coverage require for upload, ordering, progress, error, result, and download interactions (DEC-062)? What automated tools and manual keyboard and assistive-technology methods are standard? Interfaces to B5 and to the design specs' Section 16.
- B3: How does the active locale and the trusted edge country code map to Letter or A4 (DEC-083, DEC-085, DEC-089)? What is the non-invasive fallback when EN spans US and non-US markets? What is the Indonesian coverage extent at relaunch reconciled with DEC-115, DEC-118, and DEC-103? Interfaces to A5 and B4.
- B4: What are the EN/ES/ID tool slugs and the legacy URL redirect map (DEC-023, DEC-122)? What is the complete legacy URL inventory with retain/update, redirect, noindex, or removal dispositions (DEC-127, DEC-114, DEC-099)? What are the hreflang, canonical, sitemap, and locale-less redirect requirements (DEC-023, DEC-047)?
- B5: Assemble the owner-confirmation prompts (D3, U3, U5/D12, Merge error-state edge case) and the verification methods for contrast (UX §21.12), `@theme inline` emission (UX §21.19), and rendered visual checks (UX §21.11). Define the evidence standard and record that the rendered pass executes during implementation, not research.

### 7.3 Track C questions

- C1: Queue and worker design (DEC-019): worker count, per-worker memory and time bounds, queue-depth safety caps (DEC-035). Fair-scheduling classes, concurrency bounds, and starvation prevention (DEC-137). Redis persistence mode, eviction policy, and recovery (DEC-174). Fair-use controls consistent across API processes (DEC-020). Interfaces to C2 and C4.
- C2 (Wave 2): Per-tool server limits (bytes, pages, pixel counts, output counts, estimated memory) as conservative design and safety defaults with a documented raising procedure (DEC-034, DEC-066). Consumes A2-A6 and C1 findings. Produces a per-tool limit table and a machine-readable-contract shape recommendation for DEC-165.
- C3: R2 object model, key hygiene, active deletion by absolute deadline, lifecycle-rule safety net, and cleanup observability (DEC-013, DEC-067, DEC-070, DEC-075, DEC-166). Interfaces to C2 (limits) and C5 (cleanup telemetry).
- C4: Validation and hardening (DEC-169): non-root execution, bounded CPU/memory/time/disk, restricted network, hardened filesystem. Malware scanner selection, update channel, and safe-failure behavior (DEC-171). Sanitization and threat blocking (DEC-088, DEC-090, DEC-092, DEC-093). Nginx rate-limit values and fair-use thresholds (DEC-020, DEC-035).
- C5: Monitoring coverage (DEC-182), noise-resistant health signals for the public status experience (DEC-116, DEC-119, DEC-161), alert thresholds and deduplication for Telegram (DEC-180), regional monitoring (DEC-104), and operational overrides and pause controls for AI-assisted automation (DEC-097).
- C6: Backup scope, schedule, retention, encryption, restore-target configuration (DEC-173), monthly isolated restore verification (DEC-181), and the relationship between restore and rollback (DEC-178).

### 7.4 Track D questions

- D1: Current Adsterra publisher terms, eligible formats, script behavior as documented, cookies and identifiers, data recipients, regional behavior, and consent requirements (DEC-005, DEC-018, DEC-022). Presents the evidence and the compliance options (consent controls, non-tracking contextual ads, or regional suppression) without claiming compliance.
- D2: Disclosure inventory for Privacy, Terms, and Cookies/Advertising in EN/ES/ID (DEC-045, DEC-168): processing paths, server fallback, R2, providers, analytics boundaries, advertising behavior, controls, retention, metadata preservation (DEC-084, DEC-085). Re-scoped copy requirements replacing legacy "no tracking" claims (UX §21.17). Scopes the qualified legal review as an owner action.
- D3: Analytics event scope and schema boundaries (DEC-025): allowed fields, prohibited fields, retention, regional activation, leakage guards, and the prohibition on session replay and fingerprinting. Defines what event-schema privacy review and automated leakage tests must cover.
- D4: Contact form and result-problem report mechanics (DEC-046, DEC-050, DEC-117, DEC-120): minimal data, anti-spam, delivery monitoring, retention, redaction-safe errors, owner-managed inbox routing, and locale-matched confirmations. Interfaces to D5.
- D5: Threat classification, blocking, sanitization, password handling, and the prohibited-data register as applied to research findings (DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171, DEC-036, DEC-064). Confirms which failure classes fail closed and which route to server fallback.

### 7.5 Track E questions

- E1: The full DEC-051 documentation contract for `gpt5.6-sol`: base URL, authentication, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, availability. Publicly discoverable items are documented with sources; remaining items are listed as owner-supplied gaps. No provider access.
- E2: The automated MDX blog pipeline (DEC-048, DEC-049): generation, localization, blocking quality gates that fail closed, validation, scheduling, audit logs, pause and kill-switch controls, rollback, and repository-based publication through the normal build path. No publication and no repository writes during research.
- E3: The five launch topics and the post-launch topic pipeline (DEC-052, DEC-053, DEC-121, DEC-124): topic selection criteria that avoid tool-page cannibalization, localization and search-intent requirements per locale, cadence rules, and date-display requirements (DEC-113).

## 8. Required brief template

Every brief must follow this template. A brief that misses a section is incomplete and fails verification.

1. Header: brief ID and path, track, title, date, author role, status (draft, complete, superseded), and the exact files read.
2. Scope: the feature or decision area, the user problem, and the current approved Papyr behavior.
3. Non-goals: what this brief explicitly does not cover.
4. Research questions: the questions from Section 7 that apply, restated as answerable questions.
5. Evidence: primary sources with URLs or identifiers, access dates, versions, and legacy file and line citations into `papyr-reference/`. Secondary sources are marked as supporting only.
6. Alternatives: at least two viable approaches with trade-offs, risks, cost and operational impact, and privacy and security implications (DEC-055).
7. Recommendation: explicitly labeled as a recommendation, not an accepted decision (DEC-054, DEC-057).
8. Measurable acceptance criteria: functional, security, accessibility, or operational criteria verifiable without a benchmark program (DEC-066).
9. Assumptions, uncertainties, and unresolved questions.
10. Dependencies and cross-track interfaces.
11. Source-date log and evidence-completeness notes.
12. Prohibitions-compliance statement: confirmation that no prohibited action was taken and that `papyr-reference/` remains unchanged.

## 9. Delegation contract

### 9.1 Delegation categories

- Research collection agents (explore for repository evidence, librarian for web and primary-source evidence) gather per-brief evidence. They run in parallel background tasks within a track.
- A synthesis pass (metis or oracle style agent) produces X1 and X2 from the completed briefs.
- The orchestrator (Sisyphus) enforces this plan, verifies deliverables, and escalates conflicts to the owner.

### 9.2 Delegation prompt requirements

Every delegation prompt must state:

- The exact output file path under `audit-outputs\research\`, which is the primary deliverable.
- That a chat-only summary is insufficient.
- The required evidence: source file paths and line references for repository material, URLs or identifiers and access dates for web material, findings, uncertainties, and unresolved questions.
- The required skills loaded by the agent and why they apply.
- That `papyr-reference/` must remain unchanged.
- The verification evidence the agent must produce before reporting completion.
- The prohibitions in Section 4.1.

### 9.3 Skills

- Orchestrator load: `ocs-delegation-gate`, `context-grooming`, `ocs-markdown-autofix`.
- Research agents load skills relevant to their domain (for example Cloudflare and Workers skills for Track C, advertising and legal research skills for Track D where available). The `ocs-markdown-autofix` conventions apply to every brief.
- No skill is loaded that implies implementation, benchmarking, deployment, or VPS access.

## 10. Dependencies and parallel waves

The program follows the prior Plan Agent's wave structure: plan and scaffold, five parallel domain tracks, per-tool server-limits follow-up, source and decision index, reconciliation, final verification, owner review.

| Wave | Name | Work | Exit condition |
|---|---|---|---|
| 0 | Plan and scaffold | This plan file, the `audit-outputs\research\` tree, and the deliverable map. | Plan exists; directory tree exists; briefs not yet created. |
| 1 | Five parallel domain tracks | A1 through A6 (A1 gates A2-A6 engine citations), B1-B5, C1, C3, C4, C5, C6, D1-D5, E1-E3. 24 briefs in parallel background tasks. | Every Wave 1 brief exists and passes per-brief verification. |
| 2 | Per-tool server-limits follow-up | C2, consuming A2-A6 and C1 findings. | C2 exists and passes verification. |
| 3 | Source and decision index | X1 finalized from all 25 briefs. | X1 exists and maps every brief to decisions, spec sections, and sources. |
| 4 | Reconciliation | X2 written. Material conflicts escalate to the owner; nothing is silently resolved. | X2 exists with confirmed findings, interfaces, and owner decision prompts. |
| 5 | Final verification | Full assertion run in Section 11. | All assertions pass. |
| 6 | Owner review | Owner reviews X2 and the briefs, approves or redirects each researched feature per DEC-057. | Owner disposition recorded; design and implementation planning may begin only after approval (DEC-060, DEC-188). |

Wave dependencies:

- A1 precedes A2-A6 completion (engine and license evidence is cited by the tool briefs).
- C2 precedes nothing and follows A2-A6 and C1.
- B1, B4, and B5 consume tool findings from Track A where routing, slugs, and UI verification depend on them; they may start in Wave 1 but must reconcile in Wave 4.
- D1 and D2 findings feed X2 and the owner consent decision under DEC-022.
- E1 and E2 are independent of Tracks A-D except for content topics in E3.

## 11. Verification assertions

A brief is not complete until its assertions pass. These are per-brief and program-wide checks.

Per-brief assertions:

1. The file exists at its exact path in Section 6 and is non-empty.
2. All template sections in Section 8 are present and substantive.
3. At least two viable approaches are compared, or the brief records why only one is feasible (DEC-055).
4. Primary sources are cited with URLs or identifiers and access dates (DEC-056).
5. Legacy evidence cites `papyr-reference/` paths with file and line references.
6. The recommendation is explicitly labeled as a recommendation (DEC-054, DEC-057).
7. Acceptance criteria are measurable and contain no benchmark wording (DEC-066).
8. No TODO, TBD, FIXME, or placeholder tokens remain.
9. The prohibitions-compliance statement is present and accurate (Section 4.1).
10. `git -C papyr-reference status --porcelain` returns empty output with exit 0 before and after the brief.

Program-wide assertions:

1. All 25 briefs, X1, and X2 exist.
2. Every unresolved item in UX spec Section 21 and arch spec Section 25.3 is mapped to at least one brief in X1, or explicitly recorded as deferred (for example the post-launch tool-restoration sequence under DEC-094).
3. No deliverable contains a benchmark program, corpus, comparative report, or quality-score program (DEC-066).
4. No deliverable contains implementation, deployment, VPS, or account-creation instructions that were executed.
5. Cross-track conflicts listed in X2 are either resolved with cited evidence or escalated to the owner (DEC-183).
6. `papyr-reference/` remains unchanged (empty porcelain, exit 0).
7. Markdown structural conventions are manually verified; `bun run lint:md:fix` and `lint:md` are noted as unavailable because the workspace has no root package.json exposing them, and no tooling is installed (Section 12).

## 12. Markdown tooling note

The `ocs-markdown-autofix` workflow (`bun run lint:md:fix` and `bun run lint:md`) cannot be executed here: `<workspace-root>` has no root `package.json` or bun configuration exposing those scripts. No markdown tooling is installed, per the execution boundaries. Every brief therefore records manual verification: ATX headings, ordered-list continuity, well-formed tables, and no placeholder text. This limitation is reported, not hidden.

## 13. Repository status record

- `<workspace-root>` is not currently a git repository. No commits, branches, or pushes are part of this phase.
- `papyr-reference/` is a separate read-only legacy clone. A read-only `git status --porcelain` returned empty output with exit 0 at plan creation (2026-07-31), and the same check runs at every verification boundary.
- The rebuild repository itself is not yet created, consistent with the coding gate in DEC-060.

## 14. Owner-review handoff

Wave 6 delivers to the owner:

1. `audit-outputs\research\reconciliation-report.md` as the entry point, with confirmed findings, cross-track interfaces, and conflicts.
2. The 25 briefs for per-feature review under DEC-057.
3. The `source-and-decision-index.md` for traceability.
4. A decision-prompt list that includes: the Compress engine and profile selection, per-tool server limits, worker and queue bounds, Redis persistence mode, malware scanner, paper-policy mapping, tool slugs and legacy URL dispositions, Adsterra consent disposition, legal-review scope, contact and support mechanics, monitoring and alert thresholds, backup configuration, `gpt5.6-sol` documentation gaps for owner supply, and the B5 owner-confirmation items (navbar width, CTA intent, entrance animations, Merge error-state edge case).

Findings are recommendations. Owner approval of each researched feature is required before it enters approved design and implementation planning (DEC-057). Coding remains blocked until research is complete, findings are reconciled, the resulting design is approved, and an implementation plan is reviewed (DEC-060, DEC-188).

## 15. Verification statement for this plan

- Required inputs were read in full: `AGENTS.md`, `papyr-rebuild-decisions.md` (DEC-001 through DEC-188 plus the Open decisions section), both approved specifications, `audit-outputs\spec-cross-review.md`, and `audit-outputs\spec-corrections-report.md`.
- DEC-054 through DEC-060, DEC-066, and DEC-188 are incorporated as governing gates in Section 3.
- Tracks A through E, the index, and the reconciliation report are defined with exact paths in Section 6.
- `audit-outputs\research\` was created with track subdirectories. No research briefs were created.
- The only files created by this task are this plan and the `audit-outputs\research\` directory tree.
- `papyr-reference/` was verified unchanged via read-only `git status --porcelain` (empty, exit 0).
- No installs, builds, servers, VPS access, deployment, account creation, or git writes were performed.
- This file is the primary deliverable; a chat-only summary is insufficient.
