# D3 — Analytics and Privacy Boundaries

| Field | Value |
|---|---|
| Brief ID | PPR-RB-D3 |
| Path | `audit-outputs\research\track-d\d3-analytics-privacy.md` |
| Track | D (monetization, legal, privacy, support, and security requirements) |
| Title | Analytics and privacy boundaries |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete (recommendation; no approved decision) |
| Governing decisions | DEC-025, DEC-126, DEC-024, DEC-042, DEC-036, DEC-117, DEC-050, DEC-020, DEC-175 |
| Spec sections served | Product/UX spec §17, §20.6; Technical Architecture spec §4.5, §22.3, §23 |
| Files read (local) | `papyr-rebuild-decisions.md` (DEC-025, DEC-126, DEC-024, DEC-042, DEC-036, DEC-117, DEC-050, DEC-020, DEC-054–057, DEC-066, DEC-104); `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` §17, §20.6; `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` §4.5, §22.2-22.3, §23; `papyr-reference/frontend/src/lib/analytics.ts`; `papyr-reference/docs/18_Papyr_Analytics_Event_Taxonomy_v1.0.md`; `papyr-reference/backend/utils/logging_config.py` |

---

## 1. Scope

**Decision area.** The allowed and prohibited fields for Papyr's product analytics, the event-schema privacy review, data-retention policy, regional activation controls, and the automated leakage tests required by DEC-025 and the architecture spec §22.3.

**User problem.** Papyr needs enough instrumentation to improve reliability, SEO conversion, tool completion, and advertising performance without recording documents or sensitive interactions. Users entrust files to the service on the strength of the privacy promise; analytics must never undermine it.

**Current approved behavior.** Detailed product events, funnels, attribution, performance, and sanitized error analytics are collected; session replay on document-tool workflows, fingerprinting data, and document-sensitive information are prohibited (DEC-025). Usage totals stay private, deferred to a future admin dashboard that is not launch scope (DEC-126). Event schemas require privacy review, a data-retention policy, regional activation controls, and automated tests or audits guarding against sensitive-field leakage (DEC-025; Arch §22.3).

**What this brief produces.** A concrete allowed-field and prohibited-field schema boundary, the activation/retention/opt-out design requirements, the leakage-test requirements, and the provider evidence for the recommended analytics stack.

## 2. Non-goals

- No analytics provider account creation or authenticated access.
- No session replay, heatmapping, or fingerprinting tool evaluation (prohibited outright by DEC-025).
- No public counters or admin dashboard (DEC-126).
- No benchmark program; analytics acceptance is verified by functional leakage tests and privacy review, not by comparative analytics-quality studies (DEC-066).

## 3. Research questions (restated from plan §7.4, D3)

1. What fields are allowed in analytics events, and what fields are prohibited, per DEC-025 and UX §17?
2. What retention, regional activation, and consent/opt-out behavior must analytics honor (DEC-025, DEC-022)?
3. What must the event-schema privacy review cover?
4. What must automated leakage tests verify, and how do they map to the architecture spec's testing layers?
5. Which analytics provider best fits the approved boundaries (primary-source evidence), and what are the alternatives?

## 4. Evidence

### 4.1 Local authoritative requirements

| Source | Location | Requirement |
|---|---|---|
| DEC-025 | `papyr-rebuild-decisions.md:316-327` | Allowed: acquisition source, page and locale, tool selection, processing mode, coarse input bands, funnel stages, timings, sanitized failure categories, download completion, Web Vitals, advertising performance where permitted. Prohibited: file contents, previews, rendered document text, file names, object keys, signed URLs, passwords, full error payloads containing user data, stable device fingerprints. No session replay on uploader/editor/processing/result workflows; masking alone insufficient. Schema privacy review, data-retention policy, regional activation controls, automated leakage guards. Does not override consent/opt-out obligations (DEC-022) |
| DEC-126 | `papyr-rebuild-decisions.md:1506-1515` | No public counters; metrics follow DEC-025; no filenames, contents, passwords, object keys, signed URLs, or prohibited identifiers even in the future admin dashboard |
| DEC-042 | `papyr-rebuild-decisions.md:524-534` | Original and generated file names never sent to analytics, monitoring, logs, or error reporting |
| DEC-036 | `papyr-rebuild-decisions.md:452-462` | Passwords never in analytics |
| DEC-024 | `papyr-rebuild-decisions.md:304-314` | 90-day metrics: job success/failure, processing/queue latency, uptime, Core Web Vitals, organic entrances, tool usage distribution, completed downloads; distinguish browser-local from server jobs without collecting document contents; numeric targets defined before implementation planning |
| DEC-050 | `papyr-rebuild-decisions.md:622-631` | Support analytics use aggregate categories and resolution timing, never copying private message contents into general product analytics |
| DEC-020 | `papyr-rebuild-decisions.md:253-265` | Fair-use controls avoid retaining document contents and minimize personal-data collection |
| DEC-175 | `papyr-rebuild-decisions.md:2054-2063` | Operational logs retained 30 days, content-excluded |
| UX §17 | `2026-07-31-papyr-product-ux-design.md:584-596` | User-visible analytics/privacy boundaries incl. privacy copy re-scope |
| Arch §22.2-22.3 | `2026-07-31-papyr-technical-architecture.md:937-951` | Security checks include data-leakage guards on logs, analytics, and task records; automated tests assert passwords, filenames, signed URLs, object keys, and document contents never reach logs, analytics, persisted task records, or backups |

### 4.2 Legacy analytics evidence (baseline)

- `papyr-reference/frontend/src/lib/analytics.ts:1-69` — legacy Vercel Analytics events `task_started`/`task_completed`/`task_failed` with `tool`, `tool_name`, `device_category`, and a `error.slice(0, 200)` field on failure. The raw error string field is a leakage risk under the accepted model (error payloads may contain user data) and must be replaced by sanitized failure categories.
- `papyr-reference/docs/18_Papyr_Analytics_Event_Taxonomy_v1.0.md` — legacy taxonomy (size buckets small/medium/large, device categories, planned file/navigation/monetization events). Historical baseline; planned `file_*` events (upload start/completed/failed with `file_size_bytes`, `file_type`) exceed the allowed coarse-band scope unless redefined as coarse bands only; `utm_source` and `is_returning` fields (planned `homepage_viewed`) are permitted only if they do not constitute a stable identifier or fingerprint.
- `papyr-reference/backend/utils/logging_config.py:36-43,68-117` — legacy structured backend logs use `input_size_bucket` (small/medium/large) rather than exact bytes; this coarse-band pattern is the approved precedent for analytics and backend events.

### 4.3 Provider primary sources (accessed 2026-07-31)

| Source | URL | Version/date | Evidence |
|---|---|---|---|
| Vercel Web Analytics — Privacy and Compliance | https://vercel.com/docs/analytics/privacy-policy | Last updated 2026-06-26 | No third-party cookies; end users identified by a hash of the incoming request; visitor-session data discarded after 24 hours; aggregated data; data-point list (URL, dynamic path, referrer, filtered query params, geolocation at country/state/city granularity, device OS/browser/type, script version) |
| Vercel Web Analytics — Redacting Sensitive Data | https://vercel.com/docs/analytics/redacting-sensitive-data | Last updated 2026-06-26 | `beforeSend` hook to drop/modify events, remove query params, and implement opt-out via a `localStorage` flag |
| Cloudflare Web Analytics — overview and data pages | https://developers.cloudflare.com/analytics/web-analytics/ | Accessed 2026-07-31 | Privacy-first web analytics alternative; no cookies, no cross-session identifiers; Core Web Vitals; dimensions |

### 4.4 Consent and regional context (supporting)

- ICO PECR guide (https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/what-are-pecr/) and ePrivacy Directive 2002/58/EC Article 5(3): storage or access to terminal-equipment information requires consent unless strictly necessary. Analytics identifiers that write to terminal equipment therefore engage consent questions in EEA/UK/CH; Vercel Web Analytics' no-third-party-cookie, hash-based design reduces but does not by itself eliminate the question of what is stored/accessed on the device. DEC-025 states analytics do not override consent/opt-out obligations.
- EDPB Guidelines 05/2020 on consent (https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en) — consent-validity standards if a consent path is adopted.

## 5. Alternatives

### Alternative A — Vercel Web Analytics for page-level + custom events (recommended baseline)

- **Description.** Keep the platform-native Vercel Web Analytics for page views, Web Vitals, referrer, and coarse geolocation, extended with privacy-reviewed custom events via `track()` and hardened with `beforeSend` redaction and an opt-out flag.
- **Trade-offs.** Zero additional provider; the provider's docs describe no third-party cookies, 24-hour session discard, and hashed identification (Section 4.3). Custom events still send to Vercel, so the schema must be enforced client-side and at the intake boundary; geolocation data point records city-level granularity, which must be disclosed (DEC-085).
- **Cost/operational impact.** Included in Vercel; minimal.
- **Privacy/security implications.** The leakage controls are contractual/client-side; Vercel documents a redaction hook, and the schema review plus automated leakage tests in Section 6 enforce the boundary.
- **Risk.** Provider data-point list includes URL and query params, so redaction of document-sensitive routes must be configured; city-level geolocation is disclosed.

### Alternative B — Cloudflare Web Analytics (or another cookieless provider) instead of / in addition to Vercel

- **Description.** Replace or supplement Vercel Web Analytics with Cloudflare Web Analytics, whose docs describe no cookies and no cross-session identifiers.
- **Trade-offs.** Privacy-lighter page analytics; Cloudflare Web Analytics historically does not provide the same custom-event funnel plumbing as Vercel's `track()` for the DEC-024 funnel metrics, so custom events would still need a sanctioned path; running two providers duplicates instrumentation.
- **Cost/operational impact.** Free tier; extra script and data inventory.
- **Privacy/security implications.** Fewer identifiers; but every analytics provider still receives page-level data and must be disclosed and assessed.
- **Risk.** Tool-completion funnels (DEC-024) may not be measurable with this provider alone.

### Alternative C — No analytics provider; backend operational metrics only

- **Description.** Drop product analytics entirely; keep only sanitized backend logs (30-day, content-excluded) and Netdata-style operational metrics.
- **Trade-offs.** Maximum privacy; but DEC-024 requires measurement of organic entrances, tool usage distribution, and completed downloads, which are web-analytics signals; this alternative cannot satisfy the approved 90-day criteria.
- **Cost/operational impact.** None.
- **Privacy/security implications.** Lowest data surface.
- **Risk.** Conflicts with DEC-024 and DEC-025's explicit choice of detailed product analytics; listed for completeness.

**Comparison summary:** A satisfies DEC-024/DEC-025 with the least new surface, provided the schema, redaction, and leakage tests in Section 6 are enforced. B is a valid privacy-lighter variant for page analytics but does not alone cover custom funnels. C conflicts with accepted decisions.

## 6. Recommendation (recommendation only, not an accepted decision)

1. **Adopt Alternative A** as the analytics baseline: Vercel Web Analytics page/Web Vitals/referrer data plus privacy-reviewed custom events, hardened by `beforeSend` redaction and an opt-out mechanism, with the schema below.
2. **Adopt the allowed/prohibited field schema** (Section 6.1) as the single source of truth for event definitions, and make it the review checklist for every new event.
3. **Replace the legacy raw error-string field** (`analytics.ts:66`, `error.slice(0, 200)`) with a closed-set sanitized failure category; full error payloads containing user data are prohibited (DEC-025).
4. **Coarse input bands, never exact bytes** for input size (legacy precedent `logging_config.py:36-43`); exact sizes remain operational-log-only if content-free.
5. **Define retention and regional activation** (Section 6.2) and implement the automated leakage-test suite (Section 6.3) as part of the security checks in Arch §22.2.
6. **Record an opt-out and consent stance** consistent with the D1/D2 decisions: analytics do not override consent/opt-out obligations (DEC-025); if the D1 decision adopts a CMP, analytics identifiers follow the same consent gate in EEA/UK/CH.

### 6.1 Allowed and prohibited field schema

**Allowed (top-level schema):**

| Field group | Allowed fields | Constraint |
|---|---|---|
| Identity of visit | Page path, locale, referrer (source), acquisition source (UTM where present) | No user identifier; no hashed ID treated as a stable fingerprint; URL redacted via `beforeSend` for document-sensitive routes |
| Tool and flow | Tool slug (five launch tools), processing mode (client/server/fallback), funnel stage, outcome (started/completed/failed), retry count (sanitized) | Tool slugs from the approved catalog; no other tool names at launch |
| Input characteristics | Coarse band only: small/medium/large (size), page-count band, image-count band, output-count band | Bands defined per tool (C2 limits); never exact bytes or exact counts where they can re-identify a file |
| Timing | Duration bands or ms timings for processing stages | Timings on the task, not on document content |
| Failure | Sanitized failure category from a closed enum (validation, unsupported, password-wrong, rate-limited, server-error, timeout, security-blocked) | No raw error text, no exception payloads, no scanner/engine internals (DEC-169, DEC-171, DEC-088) |
| Outcome | Download completed, expiry reached, auto-download blocked | No signed URLs, no object keys, no filenames |
| Performance | Web Vitals fields as provided by the analytics SDK | No document content |
| Advertising (where permitted) | Ad-impression/click presence as provided by the ad provider, only if it stays within the schema and the consent outcome from D1 | No ad clickstream combined with document-sensitive fields |
| Operational (backend) | Task state, queue depth bands, duration bands, error categories, cleanup counts | Mirrors DEC-174 minimal metadata; 30-day log retention (DEC-175) |

**Prohibited (from analytics, monitoring, logs, and error reporting):** file contents, previews, rendered document text, file names (original or generated), object keys, signed URLs, PDF passwords, full error payloads containing user data, stable device fingerprints, session-replay/heatmap/session-recording data on uploader/editor/processing/result workflows, precise document metadata (EXIF fields are preserved in user-owned outputs per DEC-084 but never sent to analytics), and any field that would let a file be reconstructed or re-identified.

**Boundary rule:** any new event or field must pass the privacy review (Section 6.2 item 1) before it may be added; no ad-hoc instrumentation.

### 6.2 Retention, activation, consent, and opt-out

1. **Event-schema privacy review**: every event definition reviewed against this schema and the prohibited-data register (Arch §23.2) before enabling, recorded in the analytics schema document.
2. **Retention**: analytics retention per DEC-025 "data-retention policy" — set a documented retention window consistent with the provider's capabilities (Vercel documents session discard at 24 hours for visitor sessions; dashboard retention per the provider plan) and review it at launch; the policy is recorded in D2's Privacy inventory.
3. **Regional activation**: analytics identifiers follow the consent outcome from D1 in EEA/UK/CH if a CMP is adopted; otherwise activation is global with the opt-out below. Regional monitoring (DEC-104) distinguishes US, LATAM, and Europe in aggregate without profiling individuals.
4. **Opt-out**: a documented user opt-out (e.g., `beforeSend` nulling with a persistent flag per Vercel's documented pattern, or the consent gate) that users can reach from the Privacy/Cookies pages; the mechanism is disclosed in D2 copy.
5. **No public counters**: usage totals remain private (DEC-126).

### 6.3 Automated leakage-test requirements (Arch §22.3)

The following must be automated in CI and asserted in functional tests:

1. **Prohibited-string guards**: event payloads sent through the analytics boundary must not contain filenames, object keys, signed-URL fragments, passwords, or document-content samples; tests inject decoy sensitive values through the full tool flows and assert they never appear in emitted analytics events or backend logs.
2. **Raw-error ban**: `task_failed`-style events only ever carry the closed sanitized category set; tests assert the raw error string is never an event field (replaces `analytics.ts:66`).
3. **Coarse-band enforcement**: input-size fields serialize only band values; tests assert no exact byte field reaches the analytics schema.
4. **Log/analytics/task-record cross-check**: per Arch §22.3, tests assert passwords, filenames, signed URLs, object keys, and document contents never reach logs, analytics, persisted task records, or backups.
5. **Redaction-function unit tests**: `beforeSend` redaction drops/rewrites the configured sensitive routes and query parameters; unit tests cover the documented examples.
6. **Schema-validation gate**: events failing schema validation are rejected in test (and, where feasible, in production instrumentation), so the allowed/prohibited boundary is executable, not just documented.
7. **Regional-behavior tests**: if consent or suppression is selected, tests verify analytics identifiers activate only per policy in EEA/UK/CH-representative requests.

## 7. Measurable acceptance criteria (no benchmark wording)

1. All analytics events conform to the Section 6.1 schema; the schema is machine-readable and enforced by validation in the test suite.
2. The leakage-test suite passes: decoy filenames/passwords/object keys/signed URLs/content samples never appear in emitted events, logs, task records, or backups (Arch §22.3).
3. The legacy `error.slice(0, 200)` raw-error field is absent; failures emit only sanitized categories.
4. Input sizes are emitted only as coarse bands.
5. A documented analytics-retention policy, regional-activation rule, and user opt-out exist and are disclosed on the Privacy/Cookies pages (interface to D2).
6. No session replay, heatmap, or fingerprinting tool is present on any document-tool workflow (DEC-025), verified by dependency and DOM checks.
7. No public usage counter is displayed (DEC-126).
8. Privacy review is recorded for every enabled event before launch, with the review evidence retained in the analytics schema document.

## 8. Assumptions, uncertainties, and unresolved questions

- **Assumption:** Vercel Web Analytics remains the frontend analytics host at launch; if the provider materially changes its data practices, DEC-056 requires re-verification.
- **Uncertainty:** Whether the hash-based visitor identification or the city-level geolocation data point engages ePrivacy consent in EEA/UK/CH; this depends on the D1 consent decision and the qualified legal review (D2).
- **Uncertainty:** Vercel dashboard retention for custom events is provider-plan dependent; the exact retention figure is recorded at implementation time and disclosed.
- **Unresolved (owner):** Analytics opt-out presentation (footer link vs Privacy-page-only) and whether the opt-out must be regional-only or global; consent gating of analytics if D1 selects a CMP.
- **Unresolved (legal review):** Whether analytics identifiers count as personal data for GDPR/CCPA purposes and what the legal-basis statement in the Privacy page should be.

## 9. Dependencies and cross-track interfaces

- **D1 (Adsterra):** Ad-performance analytics fields depend on the D1 decision and must never couple ad identifiers with document-sensitive events.
- **D2 (legal copy):** The analytics disclosure section of Privacy/Cookies copy is generated from this schema and retention/opt-out design.
- **D4 (contact/support):** Support analytics use aggregate categories only (DEC-050); result-problem-report fields follow DEC-117 (never filenames, contents, passwords, signed URLs, object keys).
- **C5 (observability):** Backend event/log sanitization is shared; Netdata/Telegram alerts must not contain document-sensitive fields (DEC-180, DEC-175).
- **C2 (limits):** Coarse input bands reference the per-tool limit table.
- **X2 (reconciliation):** Owner prompts: opt-out presentation, analytics consent gating if CMP adopted.

## 10. Source-date log and evidence-completeness notes

| Source | Accessed | Notes |
|---|---|---|
| Vercel Analytics Privacy and Compliance | 2026-07-31 | Last updated 2026-06-26 |
| Vercel Analytics Redacting Sensitive Data | 2026-07-31 | Last updated 2026-06-26 |
| Cloudflare Web Analytics docs | 2026-07-31 | Alternative provider evidence |
| ICO PECR / EDPB consent guidance | 2026-07-31 | Consent context |
| Legacy analytics.ts / taxonomy / logging_config | 2026-07-31 | Baseline only |

Evidence-completeness: provider documentation and local decision requirements are covered. Exact provider retention figures and legal-basis conclusions are deferred to implementation-time verification and the D2 legal review, recorded as uncertainties rather than hidden.

## 11. Prohibitions-compliance statement

- No analytics provider account was created, no authenticated API call was made, and no analytics script was executed.
- No source, specification, decision-log, or existing `audit-outputs/` file was modified. The only file created is this brief.
- `papyr-reference/` was only read and remains unchanged.
- No benchmark program, corpus, or comparative analytics study was created (DEC-066).
- Findings are recommendations requiring owner approval (DEC-054, DEC-057).
