# D4 — Contact and Support Mechanisms

| Field | Value |
|---|---|
| Brief ID | PPR-RB-D4 |
| Path | `audit-outputs\research\track-d\d4-contact-support.md` |
| Track | D (monetization, legal, privacy, support, and security requirements) |
| Title | Contact and support mechanisms |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete (recommendation; no approved decision) |
| Governing decisions | DEC-046, DEC-050, DEC-117, DEC-120, DEC-110, DEC-062, DEC-036, DEC-088 |
| Spec sections served | Product/UX spec §15.3, §18 item 11, §21.7; Technical Architecture spec §25.3.14, §23.2 |
| Files read (local) | `papyr-rebuild-decisions.md` (DEC-046, DEC-050, DEC-117, DEC-120, DEC-110, DEC-062, DEC-036, DEC-088, DEC-054–057, DEC-066, DEC-118); `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` §15.3, §18, §21.7; `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` §23.2, §25.3.14; `papyr-reference/frontend/src/components/Footer.tsx`; `papyr-reference/frontend/src/app/faq/page.tsx`; `papyr-reference/docs/08_Papyr_SLA_v1.0.md` §5; `papyr-reference/docs/26_Papyr_Legal_Pages_v1.0.md` §2.13 |

---

## 1. Scope

**Decision area.** The contact and support mechanisms at launch: a public support email plus a simple categorized contact form (DEC-046), routed to one owner-managed inbox (DEC-050), plus the separate result-problem report flow (DEC-117) with an optional reply email (DEC-120). This brief compares feasible minimal contact delivery and anti-spam options that do not require account creation during this research phase, and specifies data retention, redaction-safe error handling, delivery monitoring, and locale-matched confirmations.

**User problem.** Users need a way to report processing failures, privacy requests, security concerns, accessibility issues, advertising concerns, and general feedback without accounts, without uploading documents, and without getting spammed or ghosted.

**Current approved behavior.** Support email + categorized contact form at launch; no accounts, no live chat (DEC-046); submissions route to one owner-managed inbox (DEC-050); form minimizes personal data, includes anti-spam/abuse protection, never requests document uploads/contents/passwords (DEC-046); result-problem reports never upload documents and may carry an optional reply email used only for that matter (DEC-117, DEC-120); the site avoids promising unsupportable response times (DEC-050); legally required operator/contact information is provided (DEC-110); WCAG 2.2 AA applies to contact/support interfaces (DEC-062).

**What this brief produces.** A comparison of minimal contact-delivery options (email, form-to-inbox mechanisms), an anti-spam comparison, and the retention, error-handling, monitoring, and localization requirements. No account is created for any provider.

## 2. Non-goals

- No provider account creation, sign-up, or authenticated API access during research.
- No implementation of forms or email pipelines (research-phase prohibition).
- No live-chat, helpdesk, ticketing-system, or AI-support-agent selection (DEC-046, DEC-050).
- No newsletter integration (DEC-109, DEC-120).
- No promises of specific response times in public copy (DEC-050).

## 3. Research questions (restated from plan §7.4, D4)

1. What is the minimal data model for the contact form and the result-problem report, and what is prohibited from both?
2. What feasible minimal contact-delivery options exist without account creation, and what are their trade-offs?
3. What anti-spam and abuse-protection options fit the no-account, minimal-friction product (interface to Cloudflare edge)?
4. What retention, redaction-safe error handling, delivery monitoring, and owner-inbox routing are required?
5. How do locale-matched confirmations and accessibility apply to these surfaces?

## 4. Evidence

### 4.1 Local authoritative requirements

| Source | Location | Requirement |
|---|---|---|
| DEC-046 | `papyr-rebuild-decisions.md:572-582` | Support email + categorized contact form; no accounts, no live chat; minimize personal data; anti-spam/abuse protection; never request document uploads/contents/passwords; categories: processing failure, billing/advertising concern, privacy/data request, accessibility, security, general feedback; delivery monitoring, retention rules, redaction-safe error handling, expected response statement; shared queue across locales with locale-matched confirmations/copy |
| DEC-050 | `papyr-rebuild-decisions.md:622-631` | One owner-managed inbox; runbook defines routing, priority, templates, escalation for privacy/security reports, spam handling, owner-unavailable continuity; no unsupportable response-time promises; support analytics aggregate-only |
| DEC-117 | `papyr-rebuild-decisions.md:1408-1417` | Result-problem reports: short categorized report, no document upload/attachment; fields limited to tool, processing path, sanitized error/result category, browser context, user description; never filenames, contents, passwords, signed URLs, object keys; optional, spam-protected; distinguishes product feedback from urgent security/privacy support |
| DEC-120 | `papyr-rebuild-decisions.md:1441-1450` | Optional reply email; used only for the submitted matter, never auto-added to a newsletter; minimal retention, access controls, deletion policy, privacy disclosure, safe operational routing; never request document attachments |
| DEC-110 | `papyr-rebuild-decisions.md:1330-1340` | Legally required operator/contact information provided where applicable |
| DEC-062 | `papyr-rebuild-decisions.md:764-774` | WCAG 2.2 AA for contact/support interfaces |
| DEC-088 | `papyr-rebuild-decisions.md:1072-1082` | False-positive handling and support escalation never require users to email or upload the rejected document through the contact form |
| Arch §23.2 | `2026-07-31-papyr-technical-architecture.md:992-993` | Submitted contact-form content never in error states; submissions minimized, retained under documented rules, deleted per policy; reports carry only tool, path, sanitized category, browser context, optional email |

### 4.2 Legacy evidence (baseline)

- `papyr-reference/frontend/src/components/Footer.tsx:158-163` — footer "Kontak" and "Syarat" links are `#` dead links; no contact page exists in the legacy clone.
- `papyr-reference/frontend/src/app/faq/page.tsx:84-87` — legacy FAQ routes support solely to `privacy@mypapyr.com` with "secepat mungkin" ("as soon as possible") response language.
- `papyr-reference/docs/08_Papyr_SLA_v1.0.md` §5 (lines 316-339) — legacy support model: no formal support team; best-effort email/GitHub-issues channels; legacy targets include bug-report response < 72 hours and P0 incident response < 1 hour (lines 279-286, 658-659). These committed targets are not sustainable commitments for public copy under DEC-050.
- `papyr-reference/docs/26_Papyr_Legal_Pages_v1.0.md:342-350` — legacy privacy contact: `privacy@mypapyr.com`, GitHub Issues, owner identity.

### 4.3 Provider primary sources (accessed 2026-07-31)

| Source | URL | Evidence |
|---|---|---|
| Cloudflare Email Routing | https://developers.cloudflare.com/email-routing/ | Inbound email routing to custom addresses (support@/contact@), forwarding to verified external addresses, and Workers `email()` handlers for auto-reply and forwarding; available on the Free plan; part of the approved Cloudflare topology (DEC-017) |
| Cloudflare Email Sending (beta) | https://developers.cloudflare.com/email-service/ (Email Sending) | Outbound transactional email from Workers via the `EMAIL` binding or REST API/SMTP; available on the Workers Paid plan; deliverability management |
| Cloudflare Turnstile | https://developers.cloudflare.com/turnstile/ | Smart CAPTCHA alternative; managed/non-interactive/invisible widgets; WCAG 2.2 AA compliant; server-side Siteverify validation mandatory; tokens expire in 300 seconds and are single-use; works without routing traffic through Cloudflare; free tier available |
| Cloudflare Turnstile — Get started | https://developers.cloudflare.com/turnstile/get-started/ | Sitekey/secret-key model; hostname restriction; key rotation; separate dev/staging/prod widgets |

### 4.4 Anti-spam options (feasible without account creation in this phase)

| Option | Source | Trade-offs |
|---|---|---|
| Cloudflare Turnstile | Section 4.3 | Non-intrusive, WCAG 2.2 AA; adds a third-party script on the contact surface; requires sitekey/secret configuration (owner/agent action at implementation time, not research); the widget itself is not a full spam filter — combined with rate limiting and content heuristics |
| Cloudflare edge bot/rate filtering (WAF-style, already in topology) | Arch §5.4, legacy `production.conf` rate zones | API-side rate limiting on form submission endpoint (legacy precedent 10 req/min per IP); no extra script; does not distinguish humans from bots on its own |
| Honeypot field + time-trap | Common practice (OWASP unvalidated-spam-forms mitigation) | No third-party dependency; must be hidden accessibly (never `display:none` traps for assistive tech without an accessible alternative; use off-screen positioning); easy for sophisticated bots alone |
| Manual moderation by the owner-inbox operator | DEC-050 runbook | Last-resort filtering of spam that passes technical controls; cheap, requires operator time |

Recommendation context: Turnstile + submission rate limiting + honeypot is a layered no-account anti-spam stack that fits the product's minimal-friction and accessibility requirements; final values (rate thresholds) are C4's fair-use territory.

## 5. Alternatives

### Alternative A — Cloudflare-native delivery: form → Workers → Email Routing to owner inbox

- **Description.** The contact form posts to a Vercel server action/API route or directly to a Cloudflare Worker; the Worker validates (Turnstile token, honeypot, rate limit), formats a minimal message, and delivers to the owner inbox via Email Routing/forwarding (or Email Sending on the Workers Paid plan). Confirmations are sent from the same pipeline.
- **Trade-offs.** Uses the already-approved Cloudflare topology (DEC-017); inbound Email Routing is free; no new paid third party for the MVP path; requires Cloudflare account configuration by the owner (account exists in the approved topology, but configuration is an implementation-phase action). Auto-reply via Workers `email()` handler is documented for the free path.
- **Cost/operational impact.** Cloudflare free tier for routing; Workers usage within existing limits; no new vendor.
- **Privacy/security implications.** Data passes through Cloudflare (already an approved provider); message content is minimal by design; no document data; retention controlled by the owner-inbox operator.
- **Risk.** Configuration complexity is in the Worker code and Cloudflare account settings; delivery monitoring must cover the Worker and the inbox.

### Alternative B — Serverless form-to-email service (e.g., a third-party form backend)

- **Description.** Use a form-backend SaaS that converts form POSTs into emails (representative services: Formspree, FormSubmit, Basin, Web3Forms). These require account creation and credentials (owner action), typically include hosted anti-spam, and deliver to the owner inbox.
- **Trade-offs.** Fastest to integrate and lowest code; adds a new third-party processor outside the approved topology, requiring a DPA assessment and disclosure (D2), a new secret, and dependence on a free-tier service whose limits and deliverability are outside Papyr's control.
- **Cost/operational impact.** Free tiers exist with limits; paid tiers add cost.
- **Privacy/security implications.** A new processor receives contact data; terms and retention vary by provider and must be reviewed at selection time; forms may route through the vendor's CDN.
- **Risk.** Vendor stability and data-retention uncertainty; conflicts with the minimal-provider posture.

### Alternative C — Direct email links plus a published support inbox (no form backend)

- **Description.** Publish `support@mypapyr.com` (and privacy/security addresses) as `mailto:` links and a mail-client-based submission path, without a server-side form.
- **Trade-offs.** Zero delivery infrastructure; but loses structured categorization, anti-spam control, delivery confirmation, and the DEC-117 result-problem-report flow (which is a form). Accessibility is fine, but structured reports are degraded.
- **Cost/operational impact.** Lowest; relies on the owner's mail provider.
- **Privacy/security implications.** Minimal new data surfaces; user's own mail client handles content.
- **Risk.** Cannot satisfy DEC-046's categorized contact form or DEC-117's result-local report; listed only as a partial channel that should exist anyway (the public email address is part of DEC-046).

**Comparison summary:** A best fits the approved topology and decisions with controlled privacy surface; B is fastest but adds a processor; C satisfies only the email half of DEC-046. Recommendation: A, with the public email address maintained alongside (DEC-046 requires both).

## 6. Recommendation (recommendation only, not an accepted decision)

1. **Adopt Alternative A** for form delivery: a minimal form submission path using the Cloudflare edge (Worker or Vercel server function) validated by Turnstile, honeypot, and submission rate limiting, delivering to the owner-managed inbox via Cloudflare Email Routing; keep the public support email address as a first-class channel (DEC-046).
2. **Adopt the layered anti-spam stack**: Cloudflare Turnstile (managed widget) + honeypot/timing trap + per-IP submission rate limit, with thresholds documented as fair-use defaults (interface to C4). Rejection is graceful and never resurfaces submitted content.
3. **Adopt the minimal data model** in Section 6.1 for both the contact form and the result-problem report.
4. **Adopt the retention, redaction-safe error handling, delivery monitoring, and owner-inbox routing requirements** in Sections 6.2-6.4.
5. **Never request or accept document uploads/attachments** in either flow (DEC-046, DEC-117, DEC-088, DEC-120); the form UI and copy make this explicit.

### 6.1 Minimal data model

**Contact form fields:** category (required, closed enum: processing failure, billing/advertising concern, privacy/data request, accessibility, security, general feedback per DEC-046); message (required, length-limited); optional reply email (validated format); optional browser/tool context (auto-filled, sanitized: page path and locale only, never filenames or document data). No name, no phone, no file attachment, no document identifier.

**Result-problem report fields:** tool (from the flow), processing path (client/server/fallback), sanitized error/result category (closed enum from the failure taxonomy), browser context (sanitized), user description (length-limited), optional reply email (DEC-120). Never filenames, document contents, passwords, signed URLs, or object keys (DEC-117).

**Prohibited in both:** document uploads/attachments, document contents, filenames, PDF passwords, signed URLs, object keys, and any content that could identify the user's file (DEC-046, DEC-117, DEC-120).

### 6.2 Retention and access

1. Submissions are retained under a documented policy set by the owner (recommended default: message data retained until the matter is resolved plus a short documented period, then deleted; the owner may adopt a fixed window such as 30 days consistent with the operational-log window; the exact figure is an owner decision recorded in the runbook and Privacy copy).
2. The optional email is used only for the submitted matter and never merged into a marketing list (DEC-120).
3. Access to the inbox and any stored submissions is restricted to the owner and delegated operators documented in the runbook (DEC-050); deletion is supported and documented.
4. Support analytics record only aggregate category counts and resolution timing, never message contents (DEC-050).

### 6.3 Redaction-safe error handling

1. Form/report submission errors are displayed as safe localized messages (e.g., validation category, rate-limit retry, temporary failure) and never re-render the submitted message back into error payloads, logs, or telemetry (Arch §23.2).
2. Error logging excludes submitted content; only the failure category and timestamp are logged (DEC-175 content-exclusion applies).
3. A failed submission preserves the user's typed content in the browser session (same-tab, sessionStorage-free or in-memory form state) only for retry, never in analytics.

### 6.4 Delivery monitoring and owner-inbox routing

1. Delivery monitoring covers the submission pipeline (Worker/function invocation success, Email Routing delivery, and an outbound confirmation) so silent failures are detectable; monitoring uses counts and status only, never message content (DEC-175, DEC-182 pattern).
2. The runbook defines: inbox routing and priority categories, reusable response templates per category, escalation for privacy/security reports (treated as high priority with a documented path), spam handling, and owner-unavailable continuity (DEC-050).
3. Automated confirmations are locale-matched to the submission locale (EN/ES/ID) and state an honest expectation (e.g., "we aim to reply within N business days" only if the owner commits to it; otherwise "as soon as possible" with no fabricated SLA — DEC-050 forbids unsupportable promises; legacy SLA targets at `08_Papyr_SLA_v1.0.md:279-286` are not carried into public copy without owner commitment).
4. Security and privacy reports are clearly distinguished from product feedback in the form categories and routed accordingly (DEC-046, DEC-117).

## 7. Measurable acceptance criteria (no benchmark wording)

1. Contact form and result-problem report exist in EN, ES, and ID (DEC-118), with locale-matched confirmations and copy (DEC-046).
2. Neither flow accepts file uploads/attachments; automated tests assert the submission API rejects multipart document fields (DEC-046, DEC-117).
3. Anti-spam controls are present and verifiable: Turnstile token validation is server-side (per Turnstile security requirements), honeypot is implemented accessibly, and the submission endpoint is rate-limited; tests assert unvalidated tokens are rejected.
4. Submission errors never resurface submitted content in any response, log, or analytics event (Arch §23.2), verified by the D3-style leakage tests extended to the form path.
5. Delivery monitoring exists and alerts on pipeline failure without including message content.
6. Optional reply email is validated, used only for the matter, and never added to a newsletter list (DEC-120).
7. WCAG 2.2 AA checks pass on the contact/support surfaces, including accessible error announcements and the accessible honeypot pattern (DEC-062).
8. Public copy makes no unsupported response-time promise; the expected-response statement matches the runbook (DEC-050).
9. Footer contact links resolve (replacing `Footer.tsx:161-162` dead links), and the support email is published (DEC-046).

## 8. Assumptions, uncertainties, and unresolved questions

- **Assumption:** The owner already has a Cloudflare account in the approved topology (DEC-017) and can create the Email Routing/Turnstile configuration at implementation time; no account was created during research.
- **Uncertainty:** Cloudflare Email Sending is a beta feature on the Workers Paid plan; the free-path confirmation may use the Workers `email()` auto-reply handler instead. The exact delivery path is confirmed at implementation time from current Cloudflare docs (DEC-056).
- **Unresolved (owner):** Retention window for submissions; response-time statement (commit to a target or use best-effort language); whether privacy/security reports get a dedicated address (e.g., security@mypapyr.com) in addition to the general inbox.
- **Unresolved (provider):** Third-party form-backend terms were not evaluated in depth because the recommendation stays within the Cloudflare topology; if the owner prefers Alternative B, a provider selection and DPA review becomes a follow-up.

## 9. Dependencies and cross-track interfaces

- **D2 (legal copy):** Contact/retention/opt-in disclosures on Privacy and Terms pages; privacy-request channel matches D4's routing.
- **D3 (analytics):** Support analytics aggregate-only; form leakage tests share the D3 leakage-test suite.
- **C4 (hardening):** Rate-limit thresholds and submission-endpoint abuse controls; Worker/function isolation.
- **C5 (observability):** Delivery monitoring and alerting; alerts must not contain message content (DEC-180 pattern).
- **B5 (verification):** WCAG 2.2 AA checks on contact/support surfaces.
- **X2 (reconciliation):** Owner prompts: retention window, response-time statement, privacy/security address split.

## 10. Source-date log and evidence-completeness notes

| Source | Accessed | Notes |
|---|---|---|
| Cloudflare Email Routing docs | 2026-07-31 | Free-plan inbound routing; Workers handler documented |
| Cloudflare Email Service overview | 2026-07-31 | Email Sending beta noted (Workers Paid plan) |
| Cloudflare Turnstile docs + Get started | 2026-07-31 | WCAG 2.2 AA, Siteverify mandate, 300s token expiry |
| ICO PECR / EDPB guidance (context) | 2026-07-31 | Contact-form data as personal data context for retention/access rules |
| Legacy FAQ/SLA/legal docs | 2026-07-31 | Baseline only |

Evidence-completeness: delivery options, anti-spam options, and requirements are covered from primary provider docs and accepted decisions. Exact retention figures and response-time statements are owner decisions recorded as open items.

## 11. Prohibitions-compliance statement

- No provider account was created, no sign-up or authenticated API call was performed, and no form or email pipeline was implemented or tested.
- No source, specification, decision-log, or existing `audit-outputs/` file was modified. The only file created is this brief.
- `papyr-reference/` was only read and remains unchanged.
- No benchmark program, corpus, or comparative study was created (DEC-066).
- Findings are recommendations requiring owner approval (DEC-054, DEC-057).
