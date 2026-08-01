# D1 — Adsterra Terms, Scripts, and Consent Review

| Field | Value |
|---|---|
| Brief ID | PPR-RB-D1 |
| Path | `audit-outputs\research\track-d\d1-adsterra.md` |
| Track | D (monetization, legal, privacy, support, and security requirements) |
| Title | Adsterra terms, scripts, and consent review |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete (recommendation; no approved decision) |
| Governing decisions | DEC-005, DEC-018, DEC-022, DEC-102, DEC-129, DEC-130, DEC-131, DEC-135, DEC-136, DEC-151 |
| Spec sections served | Product/UX spec §14, §15.2, §21.9; Technical Architecture spec §4.5, §25.3.12 |
| Files read (local) | `papyr-rebuild-decisions.md` (DEC-005, DEC-018, DEC-022, DEC-102, DEC-129–131, DEC-135–136, DEC-151, DEC-054–060, DEC-066, DEC-104, DEC-183, DEC-188); `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` §14, §15.2, §21.9; `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` §4.5, §25.3.12; `papyr-reference/frontend/src/components/Footer.tsx`; `papyr-reference/frontend/src/app/privacy/page.tsx`; `papyr-reference/frontend/src/app/faq/page.tsx`; `papyr-reference/docs/26_Papyr_Legal_Pages_v1.0.md`; `papyr-reference/docs/12_Papyr_Security_Policy_v1.0.md`; `audit-outputs/ui-docs-code-reconciliation.md` |

---

## 1. Scope

**Decision area.** Whether and how Papyr monetizes through Adsterra banner and native advertising at launch, under the accepted decisions DEC-005 (Adsterra monetization), DEC-018 (banner/native only), and DEC-022 (load without prior consent in all launch regions, recorded as an accepted compliance risk).

**User problem.** Papyr's tools are free and advertising-funded. Advertising must not obstruct task completion, and the advertising technology must be understood well enough to make a lawful, honest disclosure decision before launch.

**Current approved behavior.** Adsterra banner and native advertising only (DEC-018); ads load without prior consent in all launch regions (DEC-022, accepted risk); tool-page ads appear only after the primary tool experience (DEC-151); result-page ads are separated from Download controls (DEC-131); blog, legal, support, and status pages may carry the same light policy (DEC-129, DEC-130); UX outranks advertising (DEC-102); if Adsterra is not viable, Papyr operates without ads (DEC-135, DEC-136).

**What this brief produces.** A review of Adsterra's published publisher-facing terms and policies as accessible without an account, the documented behavior of Adsterra ad formats and scripts, cookies and identifiers, data recipients, regional behavior, consent requirements, and the compliance options. It does not create an account, run any script, or claim compliance.

## 2. Non-goals

- No Adsterra account creation, sign-up, script execution, ad placement, or dashboard access.
- No legal compliance certification; no statement that the DEC-022 accepted risk is removed.
- No revenue, CPM, fill-rate, or traffic-quality evaluation of Adsterra (DEC-066: no comparative benchmark; revenue assumptions deferred per DEC-005).
- No alternative ad-network selection (DEC-135 prohibits an automatic fallback monetization model).
- No consent-management-platform (CMP) implementation; this brief only scopes the options.

## 3. Research questions (restated from plan §7.4, D1)

1. What do Adsterra's current publisher-facing terms and policies say, and which obligations bind Papyr independently of Adsterra's marketing claims?
2. Which ad formats are eligible under DEC-018, and what does Adsterra document about their behavior?
3. What cookies, identifiers, and data do Adsterra's scripts introduce on publisher pages, and who are the data recipients?
4. What regional behavior and consent requirements apply, including under EU/UK/Swiss ePrivacy-style law and Adsterra's own policy environment?
5. What are the compliance options (consent controls, non-tracking contextual ads, regional suppression) and their trade-offs?
6. What must Papyr's Privacy/Terms/Cookies copy disclose about advertising (interface to D2), and what analytics boundaries apply (interface to D3)?

## 4. Evidence

### 4.1 Primary provider sources (accessed 2026-07-31)

| Source | URL | Version / date | What it evidences |
|---|---|---|---|
| Adsterra Privacy Policy | https://adsterra.com/privacy-policy/ | Effective 29.06.2026 | Processing entities, data categories, third-party transfers, GDPR/California rights statements |
| Adsterra Privacy Policy (managed link) | https://adsterra.com/privacy-policy-managed/ | Effective 29.06.2026 | Same instrument reached from the Cookies Policy footer |
| Adsterra Cookies Policy | https://adsterra.com/cookies/ | Last updated January 2023 | Cookie categories on adsterra.com, marketing cookies, pixel tracking, RTB/SSP context |
| Adsterra publisher onboarding guide | https://adsterra.com/blog/set-up-publishers-dashboard/ | Article dated 26 June 2026 | Publisher registration flow, no minimum traffic claim, format list, payout terms, eCPM model |
| Adsterra homepage format descriptions | https://adsterra.com/ | Accessed 2026-07-31 | Current format catalog and marketing claims (popunder, social bar, in-page push, interstitial, native banners, banners, smartlink) |
| Adsterra Terms & Conditions URL | https://adsterra.com/terms-conditions/ | Accessed 2026-07-31 | Redirects to the marketing homepage; the publisher agreement text is not published at a stable public URL |

### 4.2 Provider-policy findings

**Entities and jurisdiction.** Adsterra's Privacy Policy states the service is operated by AD MARKET LIMITED, a Cyprus company (registration HE 361574, Limassol), and ADMEDIA LLC FZ, a United Arab Emirates company, together "Adsterra". The policy claims commitment to applicable data protection law "including the GDPR".

**Publisher-facing obligations visible without an account.**

- Registration requires accepting the publisher Terms and Conditions at sign-up ("mind to put a tick to accept our Terms and Conditions"), per the official onboarding guide. The terms text itself is not available at a stable public URL; `/terms-conditions/` redirects to the homepage (verified 2026-07-31).
- The onboarding guide states: no minimum traffic requirements for publishers; approved sites receive ad codes ("scripts") to copy onto the site; domains must be approved; the "BOOST CPM" toggle and ad-unit format are selected per site.
- Payout terms documented in the guide: minimum withdrawal $5 (Paxum), $25 (PayPal), $1,000 (wire); NET15 (payments biweekly); local bank transfers from $50 in 40+ currencies.
- The guide advertises an anti-adblock capability ("monetizing 100% of your traffic") and a "3-level security system" as provider claims.

**Scripts, cookies, and identifiers (as documented).**

- Adsterra serves advertising through publisher ad codes (scripts) placed on publisher sites; the Cookies Policy documents that advertising delivery uses cookies, pixel tracking tags, and, for the adsterra.com platform itself, "marketing" cookies that "track visitors across websites" to "display ads that are relevant and engaging" (categories table, "Marketing"; "Pixel tracking" section). Adsterra states it sells ad impressions via real-time bidding (RTB) as an SSP (homepage FAQ and format pages).
- The Cookies Policy states pixel tags record that a user visited a particular webpage "along with additional non-personally identifiable information", that these tags support measurement of campaign effectiveness, and that cookie files "can be used to ensure proper display of advertising materials". Adsterra states it does "not collect the online user's personally identifiable information through our pixel tracking tags" (a provider claim; whether data is personal data under GDPR is a legal question this brief does not resolve).
- The Privacy Policy lists Technical Data (IP address, browser, OS, time zone and location setting, usage and clickstream) among data collected, states data may be transferred to third parties (business partners, subcontractors, advertising networks, analytics providers), and states it relies on GDPR legal bases including consent, contract, legitimate interests, and legal obligation depending on the activity.
- The Cookies Policy discloses that its own platform uses third-party marketing cookies on the doubleclick.net, google.com, facebook.net, tiktok.com, bing.com, yandex.com, linkedin.com domains and similar, i.e., cross-site advertising identifiers are part of the documented Adsterra advertising environment. This is evidence of the ecosystem Adsterra participates in; it is not a binding statement of exactly which identifiers each Papyr ad unit will set on Papyr pages.

**Eligible formats under DEC-018.** Of Adsterra's current catalog (popunder, social bar, in-page push, interstitial, native banners, display banners, smartlink), only **banner** (static display banners, listed sizes 160x300, 160x600, 300x250, 320x50, 468x60, 728x90) and **native banners** fall within DEC-018's "non-intrusive banner and native" allowlist. Popunders, interstitials, social bars, and in-page push are explicitly excluded by DEC-018. Smartlink is a link-based format and is not a banner/native placement; its use is outside the approved formats.

**Regional behavior and consent.** Adsterra markets the platform globally (248 geos) and does not, in the pages reviewed, publish a region-specific consent gate that publishers may rely on; the reviewed pages do not state that a publisher's end-user consent obligations are satisfied by Adsterra. The Cookies Policy's "necessary" category includes a `CookieConsent` cookie for adsterra.com itself, indicating the provider operates its own consent tooling for its platform. The provider's GDPR-compliance claims describe Adsterra's own processing; they do not transfer an end-user consent basis to the publisher for cookies or identifiers set on publisher pages.

### 4.3 Regulatory and industry context (supporting, not provider-binding)

| Source | URL | Role |
|---|---|---|
| EDPB Guidelines 05/2020 on consent (Regulation 2016/679) | https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en | Primary regulatory guidance on consent validity for cookies/ad tech (accessed 2026-07-31) |
| ICO guide to PECR — "What are PECR?" | https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/what-are-pecr/ | PECR applies to cookies/similar technologies; uses UK GDPR consent standard (accessed 2026-07-31) |
| ePrivacy Directive 2002/58/EC | https://eur-lex.europa.eu/eli/dir/2002/58/oj | Storage/access to terminal equipment requires consent (Article 5(3)) |
| Google AdSense/Ad Manager EU user consent policy (CMP requirement) | https://support.google.com/adsense/answer/7670013 and https://support.google.com/admanager/answer/7673898 | Industry environment: major ad platforms require TCF-compliant consent signals for EEA/UK traffic (supporting evidence of the ad-industry consent regime, not an Adsterra term) |

These are cited as context: they evidence the legal and industry environment in which ad networks operate. They are not Adsterra's binding terms and do not by themselves prove what Adsterra requires.

### 4.4 Legacy evidence (baseline only, not a requirement)

- `papyr-reference/frontend/src/components/Footer.tsx:158-163` — legacy footer links include "Syarat" and "Kontak" pointing to `#` dead links; no ads, no Adsterra references anywhere in the clone (grep for "adsterra" across `papyr-reference/` returned no matches).
- `papyr-reference/docs/26_Papyr_Legal_Pages_v1.0.md:90,299,320` — legacy legal doc claims "Cookie Policy: Tidak diperlukan (tidak menggunakan cookie)" and "cookie consent banner/popup TIDAK diperlukan"; these claims conflict with the accepted advertising model and are re-scoped in D2.
- `papyr-reference/frontend/src/app/privacy/page.tsx:47,73` and `faq/page.tsx:61` — legacy "tidak ada tracking" / "tidak mengumpulkan data pribadi apapun" claims requiring re-scoping (see D2).
- `papyr-reference/docs/12_Papyr_Security_Policy_v1.0.md:2.1-2.4` — legacy zero-tracking posture; historical only.

### 4.5 What could not be verified without an account

The current publisher Terms and Conditions text, the exact script behavior of the specific banner/native ad units issued for `mypapyr.com`, the exact cookies/identifiers those units set on Papyr pages, Adsterra's advertiser-side targeting data, and any region-specific Adsterra policy for EEA/UK traffic. These require either the owner's Adsterra account or a direct request to Adsterra; neither is authorized in this research phase. The terms-conditions URL redirect confirms the text is not public.

## 5. Alternatives

### Alternative A — Continue with DEC-022 as-is: load banner/native ads in all regions without prior consent

- **Description.** Implement Adsterra banner/native codes globally; no CMP; disclose advertising in Privacy/Terms/Cookies copy; rely on the accepted-risk record.
- **Trade-offs.** Lowest friction and fastest task flow (DEC-008, DEC-102). Legal exposure persists for EEA/UK/CH traffic where ePrivacy/UK PECR consent for storage/access of cookies and identifiers is broadly required, and for US state privacy laws where applicable. The provider's GDPR-compliance statements do not remove the publisher's own obligations (Section 4.2). Adsterra policy conformance also cannot be confirmed because the terms text is not public.
- **Cost/operational impact.** No CMP cost; modest integration (two scripts); continued accepted-risk posture.
- **Privacy/security implications.** Third-party scripts on Papyr pages; cross-site advertising identifiers may be set; ad script failures must not block status, legal, or support content (DEC-130).
- **Risk.** Matches the recorded DEC-022 risk; the brief does not treat this as compliance evidence.

### Alternative B — Prior consent via a CMP for EEA/UK/CH (and optionally California), ads without consent elsewhere

- **Description.** Region-gate advertising consent. Load a consent banner/CMP for users in EEA/UK/CH; obtain consent before ad scripts set marketing cookies/identifiers; keep ads consent-free in other regions.
- **Trade-offs.** Better aligns with ePrivacy/UK PECR consent requirements and the industry TCF-CMP environment; adds first-visit friction that the owner explicitly rejected for launch (DEC-022 rationale), adds CMP tooling (a third-party script itself), and requires geo-detection (already available as trusted edge country per DEC-085). Consent state storage itself is personal-data handling that the Privacy page must disclose.
- **Cost/operational impact.** CMP provider selection and subscription (or self-built minimal banner); consent-state storage and audit; ongoing policy maintenance.
- **Privacy/security implications.** Consent state is personal data; must be minimized, disclosed, and deletable. The CMP is another third-party script on legal/support pages unless confined to ad-bearing pages.
- **Risk.** Lower legal risk in EEA/UK/CH; contradicts the owner's no-prior-consent preference and therefore requires an explicit superseding decision (DEC-022 consequence clause).

### Alternative C — Serve demonstrably non-tracking contextual ads or suppress ads in consent-required regions

- **Description.** Two variants: (C1) use ad placements/categories that do not set tracking cookies or identifiers (contextual-only) and disclose them as such; (C2) suppress Adsterra entirely in regions where consent is required, continuing to serve ads only where no prior consent is needed.
- **Trade-offs.** C1 preserves revenue surface but depends on Adsterra offering a demonstrably non-tracking delivery mode, which the reviewed public documentation does not confirm; verification requires provider confirmation. C2 is the most conservative: revenue lost in the suppressed regions, product and trust surfaces unaffected; aligns with DEC-104's "suppress affected behavior while preserving product access where feasible".
- **Cost/operational impact.** Geo-suppression logic (edge country signal per DEC-085 pattern); no CMP cost. C1 additionally requires a provider assurance process.
- **Privacy/security implications.** Strongest privacy posture; no advertising identifiers where suppressed.
- **Risk.** C1 risk depends on provider verification; C2 removes the regional legal risk but not the US state or global legal review requirement.

### Comparison summary

| Criterion | A (no consent, as-is) | B (CMP prior consent) | C (non-tracking / suppression) |
|---|---|---|---|
| Legal-risk reduction (EEA/UK/CH) | None (accepted risk) | High (consent-based) | High (C2) / Medium (C1, unverified) |
| First-visit friction | None | High | None (C2) |
| Revenue impact | None | Low | High (C2) / Low (C1) |
| Additional third-party scripts | Ad only | Ad + CMP | Ad only (C1) / none in suppressed regions (C2) |
| Alignment with owner preference (DEC-022) | Full | Contradicts | Contradicts launch preference (C2) |
| Implementation complexity | Low | Medium | Low–Medium |

## 6. Recommendation (recommendation only, not an accepted decision)

1. **Preserve DEC-022 as the standing launch preference**, but treat the review results as the trigger for an explicit owner decision before launch: the public evidence indicates that EEA/UK/CH ePrivacy-style consent obligations and the ad-industry consent environment (Section 4.3) are not satisfied by the provider's own GDPR statements, and the exact Adsterra publisher terms remain unreadable without an account. This is precisely the situation DEC-022's consequence clause contemplates ("If prior consent is legally or contractually required, Papyr must either implement compliant consent controls, serve demonstrably non-tracking contextual advertisements, or suppress advertisements in the affected regions").
2. **Require the owner to supply, from their Adsterra account, the current publisher Terms and Conditions and the exact ad-unit code for mypapyr.com** before design finalization (owner-supplied gap, mirroring the E1 documentation-contract pattern), so the actual cookies, identifiers, data recipients, and contract obligations can be verified rather than inferred.
3. **Recommend Alternative B or C2 for EEA/UK/CH at launch**, with C2 (regional suppression) as the simplest risk-removing default and B as the revenue-preserving option if the owner accepts the added friction. This is a recommendation, not a decision; the owner's explicit choice is required (DEC-057).
4. **Restrict integration to banner and native units only**, enforce the DEC-018 exclude-list (no popunder, social bar, in-page push, interstitial, anti-adblock messaging, smartlink), reserve stable dimensions, and load scripts asynchronously/lazily with status, legal, and support surfaces never depending on Adsterra scripts (DEC-130).
5. **Re-scope Papyr's own copy**: Privacy, Terms, and Cookies/Advertising pages must describe advertising truthfully, name the provider, state what is disclosed about advertising identifiers, and avoid any compliance claim (D2 owns the copy inventory).

## 7. Measurable acceptance criteria (no benchmark wording)

1. The Adsterra integration uses only banner and native formats; automated checks assert the DEC-018 exclude-list is absent from the page (no popunder/social-bar/in-page-push/interstitial/smartlink/anti-adblock code present) — functional verification, not a performance comparison.
2. Ad slots reserve stable dimensions; a layout-stability check (Core Web Vitals CLS) verifies no ad-induced layout shift on representative pages, per DEC-018, DEC-151, DEC-131.
3. Status, legal, and support pages render and function fully when ad scripts are blocked or fail (DEC-130), verified by a script-blocked functional test.
4. Result pages keep advertising spatially separate from primary and fallback Download controls; no ad imitates a download button, result card, progress state, warning, or system action (DEC-131), verified by automated DOM/semantic checks.
5. The documented inventory of Adsterra cookies/identifiers expected on Papyr pages is recorded from the owner-supplied account evidence, and the Privacy/Cookies disclosure is consistent with that inventory (interface to D2).
6. If consent or suppression is selected, regional behavior is verified with test requests from EEA/UK/CH-representative locations: ads load only per the selected policy, and the geo signal uses the trusted edge country code with the DEC-089 fallback rules.
7. No Adsterra account was created and no ad script was executed during research (prohibitions-compliance, Section 12).

## 8. Assumptions, uncertainties, and unresolved questions

- **Uncertainty (material):** The current Adsterra publisher Terms and Conditions are not publicly accessible (URL redirects to homepage). All conclusions about the contract rest on the onboarding guide and policies; the binding agreement text is an owner-supplied gap.
- **Uncertainty:** The exact cookies and identifiers set by the specific banner/native units for mypapyr.com are unverified; only Adsterra's general Cookies/Pixel-tracking disclosures are available.
- **Uncertainty:** Adsterra's statement that it does not collect personally identifiable information through pixel tags is a provider claim that does not resolve whether the data constitutes personal data under GDPR/ePrivacy for the publisher.
- **Assumption:** Adsterra's published documents remain current at launch; DEC-056 requires rechecking when provider terms materially change.
- **Unresolved (owner):** Which option (A, B, C1, C2) applies at launch; whether the owner accepts a CMP; whether Adsterra can confirm a non-tracking delivery mode (C1).
- **Unresolved (legal):** Whether EEA/UK/CH ePrivacy consent is required for the specific ad units; whether US state privacy laws (CCPA/CPRA opt-out) impose obligations; the qualified legal review in D2 is the owner action that addresses this.
- **Unresolved (provider):** Adsterra's own requirements for EEA/UK publishers (e.g., consent-signal expectations) are not stated in the public pages reviewed.

## 9. Dependencies and cross-track interfaces

- **D2 (legal/privacy copy):** Advertising disclosure inventory; re-scoping of legacy "no tracking" claims; qualified legal review scope. D1 findings feed D2's advertising-behavior disclosure.
- **D3 (analytics/privacy):** Advertising-performance analytics "where permitted" (DEC-025) must not include document-sensitive fields; ad-related events stay within the DEC-025 schema.
- **B1/B4 (frontend):** Ad script loading strategy and ad-slot placement interface to layout stability and Core Web Vitals requirements.
- **C4/C5 (hardening/observability):** Ad scripts are third-party content; malware scanning and network restrictions on the VPS do not apply to the client-side ad scripts, but the scripts must not touch the processing API; observability must not record ad clickstream as document-sensitive telemetry.
- **X2 (reconciliation):** D1's owner decision prompt (consent vs suppression vs as-is) feeds the reconciliation report and the DEC-022 owner review.

## 10. Source-date log and evidence-completeness notes

| Source | Accessed | Notes |
|---|---|---|
| Adsterra Privacy Policy | 2026-07-31 | Effective 29.06.2026 |
| Adsterra Cookies Policy | 2026-07-31 | Last updated January 2023 (older than Privacy Policy; version gap noted) |
| Adsterra publisher onboarding guide | 2026-07-31 | Article dated 26 June 2026 |
| Adsterra homepage and format pages | 2026-07-31 | Marketing claims marked as such |
| Adsterra /terms-conditions/ | 2026-07-31 | Redirects to homepage; terms text not public |
| EDPB Guidelines 05/2020 | 2026-07-31 | Regulatory context |
| ICO PECR guide | 2026-07-31 | Regulatory context; ICO notes the guide is under review following the Data (Use and Access) Act |
| Google EU user consent policy | 2026-07-31 | Supporting industry context only |

Evidence-completeness: provider-policy and regulatory-context evidence is complete for a pre-approval review; contract-text and unit-level script evidence is intentionally incomplete and is recorded as an owner-supplied gap rather than hidden.

## 11. Prohibitions-compliance statement

- No Adsterra account was created, no sign-up or authentication was performed, and no advertising script was executed or placed.
- No web-search, fetch, or read action modified any remote resource.
- `papyr-reference/` was only read; it remains unchanged.
- No source, specification, decision-log, or existing `audit-outputs/` file was modified. The only file created is this brief.
- No benchmark program, corpus, or comparative performance study was created (DEC-066).
- This brief does not claim legal compliance or assert that the DEC-022 accepted risk is removed; findings are recommendations requiring owner approval (DEC-054, DEC-057).
