# D2 — Legal and Privacy Copy Requirements (Privacy, Terms, Cookies/Advertising)

| Field | Value |
|---|---|
| Brief ID | PPR-RB-D2 |
| Path | `audit-outputs\research\track-d\d2-legal-privacy-copy.md` |
| Track | D (monetization, legal, privacy, support, and security requirements) |
| Title | Legal and privacy copy requirements |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete (recommendation; no approved decision) |
| Governing decisions | DEC-045, DEC-168, DEC-084, DEC-085, DEC-110, DEC-022, DEC-025, DEC-036, DEC-042, DEC-064, DEC-066, DEC-117, DEC-120, DEC-130, DEC-046, DEC-050 |
| Spec sections served | Product/UX spec §15.2, §17, §21.10, §21.17; Technical Architecture spec §4.5, §25.3.13, §23 |
| Files read (local) | `papyr-rebuild-decisions.md` (DEC-045, DEC-168, DEC-084, DEC-085, DEC-110, DEC-022, DEC-025, DEC-036, DEC-042, DEC-064, DEC-066, DEC-117, DEC-120, DEC-130, DEC-046, DEC-050, DEC-054–057, DEC-104, DEC-118, DEC-121, DEC-183, DEC-187, DEC-188); both specs (sections listed above); `papyr-reference/docs/26_Papyr_Legal_Pages_v1.0.md`; `papyr-reference/frontend/src/app/privacy/page.tsx`; `papyr-reference/frontend/src/app/faq/page.tsx`; `papyr-reference/frontend/src/components/PrivacyNotice.tsx`; `papyr-reference/frontend/src/components/Footer.tsx`; `papyr-reference/docs/12_Papyr_Security_Policy_v1.0.md`; `audit-outputs/ui-docs-code-reconciliation.md` §6, §8.8 |

---

## 1. Scope

**Decision area.** The disclosure inventory and copy requirements for the Privacy Policy, Terms of Use, and Cookies/Advertising pages in English, Spanish, and Indonesian at launch (DEC-045, DEC-118), including the re-scoping of legacy "no tracking"/"no personal data" claims against the accepted analytics and advertising model (UX §21.17), and the scope of the qualified legal review that remains an owner action before launch (DEC-045).

**User problem.** Papyr temporarily processes documents, uses detailed product analytics, third-party advertising, and serves US, LATAM, and EU regions without user accounts. Users and regulators need accurate, current disclosures of what happens to their files and data; legacy copy claiming the opposite is misleading and must be corrected.

**Current approved behavior.** Privacy, Terms, and Cookies/Advertising pages launch in EN/ES/ID (DEC-045); the Privacy page carries the full processing and retention disclosure instead of the uploader (DEC-168); copy discloses the accepted consent risk in practice without claiming compliance (DEC-022, DEC-045); pages expose effective dates and version history (DEC-045); legal, support, and status pages may carry light advertising under DEC-130.

**What this brief produces.** An inventory of disclosures required on each legal page, the copy-accuracy requirements and legacy corrections, the localization and versioning requirements, and the scope and qualification of the legal review as an owner action. It does not provide legal advice and does not claim compliance.

## 2. Non-goals

- No legal advice, no compliance opinion, no certification, and no claim that any jurisdiction's requirements are satisfied.
- No final legal copy drafting; this brief specifies what copy must cover and the process to qualify it.
- No implementation of consent tooling or ad suppression (D1 owns that decision surface).
- No translation production; this brief specifies translation governance requirements.

## 3. Research questions (restated from plan §7.4, D2)

1. What disclosures must Privacy, Terms, and Cookies/Advertising cover for the approved processing, retention, provider, analytics, and advertising model (DEC-045, DEC-168)?
2. Which legacy copy claims conflict with the approved model and require re-scoping (UX §21.17)?
3. What do EN/ES/ID localization, versioning, and effective-date requirements look like?
4. Which regional regulatory transparency obligations are relevant context for the disclosure inventory (GDPR, ePrivacy/PECR, Swiss FADP, CCPA/CPRA, Spanish LOPDGDD, Indonesian PDP Law)?
5. What is the scope and qualification of the legal review the owner must commission before launch?

## 4. Evidence

### 4.1 Local authoritative requirements (decision log and specs)

| Source | Location | Requirement |
|---|---|---|
| DEC-045 | `papyr-rebuild-decisions.md:560-570` | Launch Privacy, Terms, Cookies/Advertising in EN and ES (now EN/ES/ID per DEC-118); documents must describe local vs server processing, one-hour maximum retention, R2, infrastructure providers, analytics boundaries, advertising behavior, user controls, contact channels; controlled translation; disclose the accepted consent risk without claiming compliance; effective dates and version history; qualified legal review before launch |
| DEC-168 | `papyr-rebuild-decisions.md:1973-1983` | Privacy page must clearly and accurately explain browser processing, automatic server fallback, R2 storage, providers, absolute one-hour maximum retention; uploader carries no dedicated disclosure but provides an accessible path to Privacy |
| DEC-084 | `papyr-rebuild-decisions.md:1029-1040` | Accepted privacy risk: metadata (incl. EXIF GPS) may remain in results; the interface and privacy documentation must disclose that source metadata may remain; metadata never sent to analytics or general logs |
| DEC-085 | `papyr-rebuild-decisions.md:1042-1052` | Privacy and analytics documentation must accurately disclose any broader country-level processing already performed by hosting or analytics providers |
| DEC-022 | `papyr-rebuild-decisions.md:279-290` | Legal copy must disclose the accepted consent risk in practice; the product must not claim compliance without supporting evidence |
| DEC-025 | `papyr-rebuild-decisions.md:316-327` | Analytics scope; no session replay on document workflows, no fingerprinting, no document-sensitive information; analytics do not override consent/opt-out obligations |
| DEC-036/DEC-064 | `papyr-rebuild-decisions.md:452-462, 787-797` | Passwords: memory-only, shortest practical lifetime, never in logs/analytics/URLs/dashboards/queues/storage/backups/error payloads |
| DEC-042 | `papyr-rebuild-decisions.md:524-534` | Original and generated file names never sent to analytics, monitoring, logs, or error reporting |
| DEC-110 | `papyr-rebuild-decisions.md:1330-1340` | Legally required operator/contact information remains provided where applicable; brand-only presentation never conceals mandatory disclosures |
| DEC-187 | `papyr-rebuild-decisions.md:2185-2195` | Interface, constraint copy, FAQ copy governance, and legal/Privacy disclosures must state the actual JPG-to-PDF accepted formats (JPG/JPEG, PNG, WebP) without implying the tool is renamed |
| UX §17.7 | `2026-07-31-papyr-product-ux-design.md:592` | Privacy copy re-scoped: legacy "no tracking"/"no personal data at all" claims conflict with the accepted model and are corrected |
| UX §15.2 | `2026-07-31-papyr-product-ux-design.md:530-532` | Legal page content requirements including advertising behavior and controls |
| Arch §23 | `2026-07-31-papyr-technical-architecture.md:968-1006` | Data classification, prohibited-data register, retention summary that disclosures must match |

### 4.2 Legacy copy requiring correction (baseline evidence)

| Path | Line(s) | Legacy claim | Conflict |
|---|---|---|---|
| `papyr-reference/frontend/src/app/privacy/page.tsx` | 47 | "Tidak ada akun, tidak ada login, tidak ada tracking" | Conflicts with DEC-025 analytics and DEC-022 advertising |
| `papyr-reference/frontend/src/app/privacy/page.tsx` | 73 | "Tidak melacak pengguna secara individual" | Overbroad given the accepted analytics and advertising model |
| `papyr-reference/frontend/src/app/privacy/page.tsx` | 31-34 | "Vercel Analytics ... privacy-friendly ... Tidak ada cookie pelacakan" | Must be re-verified and re-worded against the accepted model and D3 findings |
| `papyr-reference/frontend/src/app/faq/page.tsx` | 61 | "Kami tidak mengumpulkan data pribadi apapun" | Conflicts with contact form (DEC-046), optional reply email (DEC-120), analytics and advertising |
| `papyr-reference/frontend/src/app/faq/page.tsx` | 81 | "Papyr mendukung file PDF, JPG, dan PNG" | Conflicts with DEC-187 (JPG/JPEG, PNG, WebP) |
| `papyr-reference/docs/26_Papyr_Legal_Pages_v1.0.md` | 90, 299, 320 | "Cookie Policy: Tidak diperlukan (tidak menggunakan cookie)"; "cookie consent banner/popup TIDAK diperlukan" | Conflicts with the advertising model; superseded by DEC-045/DEC-022 |
| `papyr-reference/docs/26_Papyr_Legal_Pages_v1.0.md` | 639-649, 709-723 | "Status: PATUH (Compliant)" for UU PDP and GDPR; "Tidak diperlukan: cookie consent banner" | Historical self-assessment; not reusable as launch copy; DEC-022 forbids compliance claims without evidence |
| `papyr-reference/docs/12_Papyr_Security_Policy_v1.0.md` | 2.1-2.4, 6.3 | Zero-cookie/zero-tracking posture | Historical; superseded by DEC-025/DEC-022 |
| `papyr-reference/docs/18_Papyr_Analytics_Event_Taxonomy_v1.0.md` | 1.3 | "No Cookies", "GDPR-compliant by default" | Historical; must be re-verified against D3 and the legal review |
| `papyr-reference/frontend/src/components/Footer.tsx` | 161-162 | Footer links "Syarat" and "Kontak" are `#` dead links | Terms and Contact pages must exist and be linked (DEC-045, DEC-046) |
| `audit-outputs/ui-docs-code-reconciliation.md` | §8.8 (item 8) | Records the privacy/analytics statement conflict and that it is a policy/legal question for the rebuild | Confirmatory audit evidence for re-scoping |

### 4.3 Regulatory transparency context (primary sources, accessed 2026-07-31)

| Regulation | Official source | Relevance to the disclosure inventory |
|---|---|---|
| GDPR (Regulation (EU) 2016/679) | https://eur-lex.europa.eu/eli/reg/2016/679/oj | Articles 5, 12-22 (transparency, rights), 13-14 (information to be provided), 26 (joint controllership with ad providers is a question the legal review must address) |
| ePrivacy Directive 2002/58/EC | https://eur-lex.europa.eu/eli/dir/2002/58/oj | Article 5(3): storage/access to terminal equipment requires consent where not strictly necessary |
| EDPB Guidelines 05/2020 on consent | https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en | Consent validity standards relevant if a CMP is adopted |
| UK PECR / ICO guidance | https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/what-are-pecr/ | Cookies/similar technologies need consent; UK GDPR consent standard; note ICO states the guidance is under review after the Data (Use and Access) Act |
| UK GDPR | https://www.legislation.gov.uk/eur/2016/679 | UK version of GDPR applicable alongside PECR |
| Swiss FADP (revised, in force 1 Sep 2023) | https://www.fedlex.admin.ch/eli/cc/2022/491/en | Swiss privacy obligations; Switzerland is a launch-region-relevant market |
| California CCPA/CPRA | California Civil Code §1798.100 et seq.; CPRA amendments; agency: https://cppa.ca.gov/ | Notice at or before collection, opt-out of sale/sharing, sensitive-data limits; relevant for US traffic |
| Spanish LOPDGDD (Organic Law 3/2018) | https://www.boe.es/eli/es/lo/2018/12/05/3/con | Spanish implementation relevant to ES-locale users; consent and cookie rules |
| Indonesian PDP Law (UU No. 27/2022) | https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022 | Indonesian data-protection law (fully effective October 2024); relevant to ID-locale users |

These sources define the transparency obligations the disclosure inventory is designed to satisfy; whether they are fully satisfied for Papyr is the qualified legal review's question, not this brief's conclusion.

## 5. Alternatives

### Alternative A — Disclosure inventory without legal review until after launch

- **Description.** Publish re-scoped Privacy/Terms/Cookies copy per the inventory below, defer the qualified legal review to a post-launch follow-up.
- **Trade-offs.** Faster to launch; risks that a mandatory disclosure is missing or mis-stated when the product already serves multiple regions (DEC-104 simultaneous launch), and that the DEC-022 accepted risk is not adequately contextualized.
- **Cost/operational impact.** No legal cost now; higher remediation cost and regulatory risk later.
- **Privacy/security implications.** Copy may not match actual behavior if analytics or ad scripts change post-launch.
- **Risk.** Conflicts with DEC-045's explicit requirement that legal review occur before public launch.

### Alternative B — Qualified legal review of the inventory and copy before launch (recommended)

- **Description.** Complete the disclosure inventory (Section 6), produce draft copy in EN, commission a qualified legal review before launch, then localize the reviewed EN base into ES/ID with controlled translation and synchronized updates.
- **Trade-offs.** Slower and more expensive; satisfies DEC-045's launch gate; catches jurisdiction-specific gaps (joint controllership with ad providers, ePrivacy consent, CCPA opt-out, FADP, PDP Law) before traffic arrives.
- **Cost/operational impact.** One-time legal cost; the review scope is bounded by the inventory in Section 7.
- **Privacy/security implications.** Review verifies that copy matches the prohibited-data register (Arch §23.2).
- **Risk.** Lower; this is the DEC-045-compliant path.

### Alternative C — Minimal placeholder legal pages at launch

- **Description.** Ship short placeholders and expand later.
- **Trade-offs.** Cheapest; directly contradicts DEC-045 (separate pages with full disclosure), DEC-168 (full processing/retention disclosure), and DEC-110 (mandatory operator/contact information). Not viable under the approved decisions.
- **Risk.** High; listed only for completeness.

**Comparison summary:** B is the only option consistent with DEC-045/DEC-168/DEC-110. A and C trade the legal-review and disclosure requirements for speed, which DEC-103 (completeness over deadline) does not permit.

## 6. Recommendation (recommendation only, not an accepted decision)

1. **Adopt Alternative B**: an EN baseline disclosure inventory (below), qualified legal review before launch, then controlled ES/ID localization of the reviewed base.
2. **Re-scope the legacy copy** per the correction table in Section 4.2 before launch; no "no tracking", "no cookie", "no personal data", or "compliant" claims remain without supporting evidence (DEC-022, UX §21.17).
3. **Publish the three pages in all three locales** with effective dates, version history, and a change log accessible from each page (DEC-045); link them from the footer, replacing the legacy `#` dead links (`Footer.tsx:161-162`).
4. **Make the legal pages self-consistent with D1's outcome**: the advertising section reflects the owner's D1 decision (as-is, consent, or suppression) and never asserts compliance (DEC-022).
5. **Provide legally required operator/contact information** (DEC-110) on the Privacy and Terms pages, including the owner's identity/address where applicable and a privacy-contact channel consistent with D4.
6. **Require the legal review to cover at minimum**: GDPR/UK GDPR transparency and rights, ePrivacy/PECR consent for advertising and analytics identifiers (given the D1 decision), Swiss FADP, CCPA/CPRA notice and opt-out, Spanish LOPDGDD, Indonesian PDP Law, and the joint-controllership or processor status of the ad provider and analytics provider.

## 7. Disclosure inventory (copy requirements)

### 7.1 Privacy Policy (EN/ES/ID)

1. **Controller/operator identity** and contact channel (DEC-110, DEC-046): operator name, jurisdiction of establishment, support/privacy email, data-protection contact.
2. **Processing paths** (DEC-168): browser-local processing, automatic server fallback (DEC-065), the fact that files may be uploaded if local processing fails.
3. **Retention** (DEC-013, DEC-067, DEC-070, DEC-166): absolute one-hour maximum from upload receipt; active deletion plus R2 lifecycle safety net; no extension by refresh or retry; results cannot be restored after expiry.
4. **Storage and providers** (DEC-168, DEC-085): R2 temporary storage, Vercel frontend/analytics, VPS processing provider, Cloudflare edge; country-level processing already performed by hosting/analytics providers disclosed accurately (DEC-085).
5. **Analytics boundaries** (DEC-025, D3): what event data is collected (acquisition source, page/locale, tool, processing mode, coarse input bands, funnel stages, timings, sanitized failure categories, download completion, Web Vitals, ad performance where permitted) and what is never collected (file contents, previews, rendered text, filenames, object keys, signed URLs, passwords, full error payloads, stable fingerprints); no session replay on document workflows.
6. **Advertising behavior** (DEC-022, D1): provider (Adsterra), formats, that identifiers may be set by third-party ad scripts, the regional consent/suppression status per the D1 owner decision, and an honest statement that Papyr does not claim compliance.
7. **User controls** (DEC-045): how users can decline/opt out where available (analytics opt-out per D3, ad-blocking effects per DEC-130 with the caveat that blocking ads is a browser-level choice, contact for privacy requests).
8. **Contact-form and result-problem-report handling** (DEC-046, DEC-117, DEC-120): what data is collected (category, optional email), retention, that documents are never requested or attached, and privacy-contact routing.
9. **Metadata disclosure** (DEC-084): JPG-to-PDF and other outputs may retain source metadata including EXIF GPS, timestamps, device/software info, author, creator, title; preservation is best-effort, not a removal promise.
10. **Passwords** (DEC-036, DEC-064): encrypted PDFs processed only when the user supplies the password; passwords held in memory briefly, never stored, logged, or sent to analytics.
11. **Children**: no account system and no directed-to-children service; no age-gating because no registration (consistent with legacy, re-worded without compliance claims).
12. **Rights and requests**: how to submit access/deletion/complaint requests; response expectations per the D4 support process; supervisory-authority complaint paths where applicable (stated as user-rights information, not a compliance claim).

### 7.2 Terms of Use (EN/ES/ID)

1. Acceptance, service description (five tools; processing can be browser-local or server-side), free-forever core commitment (DEC-132, DEC-133) with its boundaries (fair-use and safety controls apply).
2. Acceptable use: no illegal content, no abuse, no interference with infrastructure, no automated scraping that circumvents fair-use controls, no reverse engineering (re-derived from legacy §3.4 and DEC-020; re-scoped for international markets).
3. Prohibited misuse of the service and fair-use controls (DEC-020): adaptive anonymous controls may delay/reject/challenge abusive traffic without a fixed daily quota for ordinary users.
4. Document ownership and license: users retain rights to their files; Papyr's limited license is only to process per request (legacy §3.5.2, re-scoped).
5. As-is / as-available disclaimer with no malware-free or perfect-output claims (DEC-090, DEC-171, DEC-066).
6. Limitation of liability and governing law/jurisdiction: an owner decision; the legacy Indonesian-only governing-law clause (`26_Papyr_Legal_Pages_v1.0.md:553`) is not suitable for a US/LATAM/EU international product and requires the legal review.
7. Changes to terms, effective dates, version history.

### 7.3 Cookies/Advertising page (EN/ES/ID)

1. What the page covers: cookies and similar storage technologies used by the site's analytics and advertising, plus the distinction from browser-local processing (which uses no server-side storage).
2. Analytics identifiers: what Vercel Web Analytics records (per D3) and how it is configured (no third-party cookies; hashed request identification; 24-hour session discard per Vercel docs).
3. Advertising identifiers: Adsterra scripts and the documented cookie/pixel environment (D1 evidence), any region suppression/consent outcome from the D1 owner decision, and how users can control or block them.
4. Language preference storage (DEC-047): the minimal non-sensitive storage used to remember the manual language choice must be disclosed.
5. Session recovery (DEC-032, DEC-072): same-tab `sessionStorage` recovery tokens, session-only, not persistent.
6. Links to Privacy and Terms; effective date and version history.
7. If the D1 decision introduces a CMP, the page documents the consent record and withdrawal path instead of any no-consent statement.

### 7.4 Localization and versioning requirements

- EN is the canonical legal base (DEC-184 applies to specifications; for legal copy, the reviewed EN base is the master and ES/ID are controlled translations produced by the translation governance in DEC-004/DEC-118 context).
- ES/ID must not contradict product behavior or the EN base; synchronized updates with a change log (DEC-045).
- Effective dates and version history on every page; the FAQ and Privacy pages' legacy "Terakhir diperbarui" pattern is retained but now tracked per document.

## 8. Measurable acceptance criteria (no benchmark wording)

1. Three pages (Privacy, Terms, Cookies/Advertising) exist in EN, ES, and ID with effective dates and version history (DEC-045, DEC-118), verified by route and content checks.
2. No legacy "no tracking", "no cookie", "no personal data at all", or "compliant/PATUH" claim remains in any public page (UX §21.17 correction table verified by content audit).
3. Privacy page states the one-hour absolute maximum retention, R2, providers, browser/server paths, and automatic fallback (DEC-168), verified by content check against the actual processing model.
4. The advertising section of the legal pages is consistent with the owner's D1 decision and makes no compliance claim (DEC-022), verified by review checklist.
5. JPG-to-PDF format copy (tool pages, FAQ, Privacy) states JPG/JPEG, PNG, and WebP (DEC-187), and the metadata-preservation disclosure is present (DEC-084).
6. Footer links to Privacy, Terms, Cookies/Advertising, and Contact resolve to real routes (legacy dead links `Footer.tsx:161-162` removed), verified by link checks.
7. The qualified legal review is documented with scope, findings, and disposition before launch (DEC-045), recorded as an owner action item with evidence of completion.
8. Localized copy length does not break layouts at all breakpoints (UX §16.1 item 6), verified by the accessibility/reflow checks in B5.

## 9. Assumptions, uncertainties, and unresolved questions

- **Assumption:** Legal-page content will be drafted during design/copy implementation from this inventory, not during research; this brief scopes, it does not draft final copy.
- **Uncertainty:** Whether Papyr's relationship with Adsterra and the analytics provider makes Papyr a joint controller for advertising identifiers; this is a legal-review question and materially affects the copy (D1 evidence only establishes the ecosystem).
- **Uncertainty:** Whether EEA/UK/CH ePrivacy consent is required for the ad units; the copy reflects the D1 owner decision and must not pre-empt it.
- **Unresolved (owner):** Governing law and jurisdiction clause for Terms; operator legal-entity presentation (natural person vs company) for DEC-110 disclosures; whether the ID legal pages follow the same base or require PDP-specific additions.
- **Unresolved (legal review):** CCPA/CPRA sale/sharing characterization of advertising identifiers; Spanish LOPDGDD specifics; PDP Law controller obligations for the ID locale.
- **Unresolved (process):** Which qualified reviewer the owner engages and the review timeline relative to launch.

## 10. Dependencies and cross-track interfaces

- **D1 (Adsterra):** The legal pages' advertising disclosure depends on the D1 owner decision (consent/suppression/as-is). D2 must not finalize advertising copy before D1's decision prompt is answered.
- **D3 (analytics/privacy):** The analytics section of Privacy/Cookies copy depends on D3's field schema, retention, regional activation, and opt-out design.
- **D4 (contact/support):** Privacy-rights contact and support routing copy depends on D4's channel, retention, and error-handling design.
- **B4 (SEO/URLs):** Legal-page routes, slugs (EN/ES/ID), sitemap, and hreflang per DEC-023/DEC-122.
- **B5 (verification):** Contrast/rendered verification of legal pages (DEC-062 applies to legal pages).
- **X2 (reconciliation):** Owner prompts: legal-review engagement, governing-law choice, legal-entity presentation.

## 11. Source-date log and evidence-completeness notes

| Source | Accessed | Notes |
|---|---|---|
| EUR-Lex GDPR / ePrivacy | 2026-07-31 | Stable official instruments |
| EDPB Guidelines 05/2020 | 2026-07-31 | Regulatory guidance |
| ICO PECR guide | 2026-07-31 | ICO notes the guide is under review (Data (Use and Access) Act); current as of access |
| Swiss FADP (fedlex) | 2026-07-31 | In force 1 Sep 2023 |
| CCPA/CPRA (CPPA) | 2026-07-31 | Agency site and California statutes |
| Spanish LOPDGDD (BOE) | 2026-07-31 | Official gazette |
| Indonesian PDP Law (BPK) | 2026-07-31 | Official repository; in force Oct 2024 |
| Legacy legal/security/analytics docs | 2026-07-31 | Baseline only |

Evidence-completeness: the inventory is derived from accepted decisions and primary regulatory sources. The final legality of each disclosure requires the qualified review; that gap is deliberately retained as an owner action, not closed by this brief.

## 12. Prohibitions-compliance statement

- No legal advice was provided, no compliance certification was issued, and no claim that Papyr satisfies any regulation was made.
- No source, specification, decision-log, or existing `audit-outputs/` file was modified. The only file created is this brief.
- `papyr-reference/` was only read and remains unchanged.
- No benchmark program, corpus, or comparative study was created (DEC-066).
- Findings are recommendations requiring owner approval (DEC-054, DEC-057).
