# B3 - i18n, Locale, and Paper-Standard Policy

## 1. Header

- **Brief ID**: B3
- **Path**: `<workspace-root>\audit-outputs\research\track-b\b3-i18n-locale-paper-policy.md`
- **Track**: B - Frontend, capability, and SEO research
- **Title**: i18n, locale, and paper-standard policy research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (executor subagent, Track B)
- **Status**: Draft (complete for owner review under DEC-057; findings are recommendations, not accepted decisions)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (deliverable B3 at §6.2; Track B questions §7.2; brief template §8; verification §11)
- **Governing decisions**: DEC-083, DEC-085, DEC-089 (primary paper policy); supporting DEC-004, DEC-023, DEC-041, DEC-047, DEC-082, DEC-084, DEC-103, DEC-115, DEC-118, DEC-122, DEC-184, DEC-187, DEC-188, DEC-054 through DEC-060, DEC-066
- **Spec sections served**: Product and UX Design Specification §8.2 (lines 131-157), §9 (lines 171-181), §12.4 (lines 415-435), §20.4 item 4 (line 667), §21.3 (line 701), §21.6 (line 704); Technical Architecture Specification §4.2 (lines 213-219), §5.3 (lines 260-270), §11.5 (lines 544-553), §25.3.7 (line 1067)
- **Files read**:
  - `<workspace-root>\AGENTS.md`
  - `<workspace-root>\audit-outputs\research-program-plan.md`
  - `<workspace-root>\papyr-rebuild-decisions.md` (DEC-001 through DEC-188, Open decisions)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (§8, §9, §12, §16, §20, §21)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (§4, §5, §11, §25.3)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-b3-web.md` (paper standards, CLDR, BCP 47, print and PDF library evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-decisions.md` (decision-log extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-specs.md` (spec extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-legacy-frontend.md` (§11 i18n artifacts, §12 URL evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-ui-audits.md` (§9.2 i18n findings)
  - Legacy (read-only): `papyr-reference/frontend/src/app/layout.tsx`, `frontend/src/components/Footer.tsx` (per `_evidence-legacy-frontend.md` §2, §11)
- **Template note**: The plan §8 lists 12 numbered sections. The header sub-fields above are expanded as their own labeled fields; combined with the 12 numbered sections this satisfies both the plan's template and the 16-section instruction for Track B briefs (header sub-fields counted individually), following the Track A A1 precedent.

---

## 2. Scope

This brief resolves the i18n, locale, and paper-standard policy research for the rebuild. It covers:

- **Locale strategy**: the EN/ES/ID first-class launch locales (DEC-004, DEC-115, DEC-118), locale-prefixed routing (DEC-023), and locale-less entry detection (DEC-047).
- **Paper-standard policy**: how the trusted edge country code and the active locale map to Letter or A4 for JPG-to-PDF (DEC-083, DEC-085, DEC-089), including the non-invasive fallback when EN spans US and non-US markets (UX §21.3) and when no trusted country signal is available (DEC-089).
- **Locale-aware formatting and copy resilience**: number and date conventions per locale from CLDR, plural rules, and the copy-length resilience requirement (UX §16.1 item 6).
- **Indonesian coverage at relaunch**: reconciled with the one-month schedule and the complete-over-deadline policy (DEC-115, DEC-118, DEC-103).

The user problem served: a user in the US, Latin America, or Europe, or in Indonesia, should get a fully localized experience with a paper standard that matches their regional document expectations, without settings, geolocation prompts, or language-only guessing (DEC-041, DEC-085).

The current approved Papyr behavior this brief must support: JPG-to-PDF uses Letter-family geometry for US and Canada and A4-family otherwise, derived from the trusted edge country code with A4 as the deterministic fallback (DEC-083, DEC-085, DEC-089); the selected standard is visible before processing with no manual control (DEC-041); the tool officially accepts JPG/JPEG, PNG, and WebP at launch (DEC-187); all five tools launch completely in EN, ES, and ID (DEC-027, DEC-118); every localized route carries an explicit locale prefix (DEC-023); Indonesian tool and content URLs use translated slugs (DEC-122); locale-less entry redirects once by supported browser language with a persistent manual override (DEC-047).

## 3. Non-goals

- No tool-slug selection or legacy URL redirect map: owned by B4 (UX §21.4, arch §25.3.15-16). B3 supplies the locale facts B4's slug work depends on.
- No translation-management system or translation pipeline design: blog localization belongs to Track E (DEC-048, DEC-049); UI copy localization is a UX §9 design responsibility. This brief records the locale data (CLDR, plural rules, formats) that any pipeline must respect.
- No manual paper-size, orientation, DPI, or margin controls: prohibited by DEC-041.
- No precise browser geolocation: prohibited by DEC-085.
- No change to the accepted paper policy: DEC-083/085/089 are authoritative; this brief documents the evidence behind them and the residual rule details (UX §21.3), it does not replace the decisions.
- No implementation, installs, builds, or servers (plan §4.1).

## 4. Research questions

Restated from plan §7.2 (B3):

1. How does the active locale and the trusted edge country code map to Letter or A4 for JPG-to-PDF (DEC-083, DEC-085, DEC-089)?
2. What is the non-invasive fallback when EN spans US and non-US markets (UX §21.3), and what happens when no trusted edge country is available (DEC-089)?
3. What is the evidence basis for the Letter/A4 country mapping, and where does the accepted policy differ from de facto usage (CLDR)?
4. What is the Indonesian coverage extent at relaunch, reconciled with DEC-115, DEC-118, and DEC-103?
5. Which locale data (number formats, dates, plural rules) must the UI respect, per CLDR and the Intl APIs?
6. What are the interfaces to A5 (JPG-to-PDF engine) and B4 (slugs, routes, hreflang)?

## 5. Evidence

### 5.1 Approved paper-policy decisions

Source: `<workspace-root>\papyr-rebuild-decisions.md` (verbatim in `_evidence-decisions.md` §2, with line ranges).

| Decision | Source lines | Paper-policy content (exact text) |
|---|---|---|
| DEC-083 | 1017-1027 | JPG to PDF "automatically uses Letter-family page geometry for US and Canada locale contexts and A4-family geometry for other launch markets, with per-image portrait or landscape orientation"; the applicable locale must be derived "deterministically from the active Papyr locale and an explicitly documented regional rule; browser geolocation permission is not required"; "Because English spans both US and non-US markets and Spanish spans multiple regions, research/design must define a non-invasive fallback that does not pretend language alone always identifies paper preference"; the selected standard is visible before processing; no manual control. |
| DEC-085 | 1042-1052 | "Use the coarse country code supplied by the trusted Vercel or Cloudflare request edge to select Letter for US and Canada and A4 for other countries, without requesting precise browser geolocation"; the code must define trusted headers, behavior when headers are absent or spoofable outside the trusted edge, and a deterministic A4 fallback; country code use is "ephemeral for page-policy selection and must not become a persistent location profile"; privacy and analytics documentation must disclose broader country-level processing. |
| DEC-089 | 1084-1094 | "If no trusted edge country code is available for JPG to PDF paper selection, use A4 as the deterministic default"; "US and Canada use Letter only when the trusted country signal is available; missing, invalid, or untrusted signals fall back to A4"; no precise geolocation request or persistent country profile; the selected standard remains visible before conversion. |

Note on the relationship between DEC-083 and DEC-085: DEC-083 says the applicable locale is derived from the active Papyr locale plus a documented regional rule; DEC-085 later refines the mechanism to the trusted edge country code, and DEC-089 completes the fallback rule. The specs (UX §12.4 item 5 line 427; arch §5.3 lines 260-270; arch §11.5 line 548) consistently state: Letter for US/CA, A4 elsewhere, from the trusted edge country code, A4 fallback. This brief treats the edge-country mechanism as the operative rule (the later, more specific decision), and records the residual interpretation question in §9.

### 5.2 Paper standards and country mapping

Source: `_evidence-b3-web.md` §1-§3 (all sources accessed 2026-07-31).

- **ISO 216** (A4 = 210 x 297 mm): official ISO page `https://www.iso.org/standard/36631.html` (Edition 2, 2007-09, confirmed 2021, under systematic review as of access). The public page does not publish the dimension table (paywalled); the value is corroborated by CEN's EN ISO 216:2007 catalog record (`https://standards.iteh.ai/.../en-iso-216-2007`, "Most used: A4 (210 x 297 mm)"), MDN `@page/size` (A4 = 210 mm x 297 mm; letter = 8.5 in x 11 in), and the PDF library constants.
- **US Letter** (8.5 x 11 in = 215.9 x 279.4 mm): ANSI/ASME Y14.1 per the encyclopedic source (secondary for the standard number; the ANSI webstore is paywalled and was not fetched); the dimension is corroborated by the MDN and library sources.
- **CLDR Territory Information** (primary Unicode dataset, `https://www.unicode.org/cldr/charts/latest/supplemental/territory_information.html`): verified rows for paper size and measurement system:

| Country (CLDR territory) | Measurement system | Paper size |
|---|---|---|
| United States | US | US-Letter |
| Canada | metric | US-Letter |
| Belize, Puerto Rico | US | US-Letter |
| Chile, Colombia, Costa Rica, El Salvador, Guatemala, Mexico, Nicaragua, Panama, Philippines, Venezuela | metric | US-Letter |
| Indonesia, Spain, Japan, Argentina, Brazil, Germany, UK, Australia, and the sampled metric set | metric | A4 |

- **Interpretation recorded in the evidence**: Mexico, the Philippines, Chile, Colombia, Venezuela, Costa Rica, and neighbors are CLDR-de-facto Letter countries even though ISO 216 is the nominal official lineage; Canada is officially non-ISO for paper (metric system, Letter paper); Indonesia and Spain are metric + A4.
- **Indonesia**: national standard SNI ISO 216:2010 (BSN catalog `https://pesta.bsn.go.id/produk/detail/8160-sniiso2162010`, status "Berlaku" = in force) adopts ISO 216; CLDR lists Indonesia as metric + A4; F4/Folio (210 x 330 mm) is a widely sold local size documented only by secondary sources (Wikipedia, commercial catalogs), not a standard.
- **Spain**: national standard UNE-EN ISO 216:2008 (AENOR catalog, "En Vigor", "Idéntica ISO 216:2007"); CLDR lists Spain as metric + A4.

### 5.3 Locale and region standards

Source: `_evidence-b3-web.md` §4-§5.

- **RFC 5646 (BCP 47)**: language tags encode region via the region subtag (`en-US`, `es-ES`, `id-ID`; region = ISO 3166-1 alpha-2 or UN M.49). Canonical case conventions: lowercase language, title-case script, uppercase region.
- **RFC 9110 §12.5.4 (Accept-Language)**: user agents indicate preferred natural languages with q-values; matching per RFC 4647; "user agents need to allow user control over the linguistic preference"; sending the full linguistic preference in every request has privacy implications (Section 17.13).
- **W3C i18n (qa-lang-priorities)**: browsers send ordered preferences; best practice is listing the bare language after a language+region pair; unsupported languages should receive a default-language response; IP-based country inference is an established, non-invasive input (e.g., Google).
- **CLDR / UTS #35 (LDML) 48.2 (2026-03-03)**: defines Unicode locale identifiers on BCP 47; `Intl.Locale.region` extracts the region (e.g., `new Intl.Locale("es-ES").region` = "ES"; `maximize()` fills the most likely region, e.g., `en` -> region US).
- **Trusted edge country (vendor docs)**: Cloudflare `CF-IPCountry` (two-character ISO 3166-1 alpha-2; special codes `XX` for no data, `T1` for Tor; added via the "Add visitor location headers" Managed Transform, i.e., opt-in) at `https://developers.cloudflare.com/fundamentals/reference/http-request-headers/` (updated 2026-05-05); Vercel `x-vercel-ip-country` plus `x-vercel-ip-continent` (country/continent granularity; finer headers exist but are a design choice, not a platform guarantee) at `https://vercel.com/docs/headers/request-headers` (last updated 2025-12-13). Both are coarse by design: country or continent, not precise geolocation, and approximations under VPNs, shared IPs, or missing data.
- **Locale data for `id`** (CLDR summary `https://unicode.org/cldr/charts/latest/summary/id.html`): default numbering system `latn`; decimal separator comma, thousands group dot (runtime example `new Intl.NumberFormat(["ban","id"]).format(123456.789)` -> "123.456,789"); date patterns `dd/MM/yy` short and `d MMM y` medium; 24-hour clock; yes/no `ya`/`tidak`. Indonesian has full CLDR coverage.
- **Plural rules** (`language_plural_rules.html`): Indonesian cardinal = `other` only (no plural-form selection needed); Spanish cardinal = `one`/`many`/`other` (one for n=1; many for millions-style values); both ordinals `other`.
- **ICU MessageFormat** (`https://unicode-org.github.io/icu/userguide/format_parse/messages/`): `plural` arguments select sub-messages using the language's plural rules; write full sentences in sub-messages; skeletons preferred.
- **i18n ecosystem** (primary docs): next-intl (v3/v4), next-i18next v16 (detection order cookie > Accept-Language > fallback; `fallbackLng` required), and Next.js App Router internationalization (16.2.12 docs; locale from Accept-Language with `@formatjs/intl-localematcher` + `negotiator`; sub-path or domain routing; `app/[lang]`; `generateStaticParams`). Pages Router built-in i18n does not integrate with `output: 'export'`.

### 5.4 Print and PDF page-size mechanics

Source: `_evidence-b3-web.md` §6.

- CSS `@page { size: A4 }` or `size: letter` (MDN, Baseline 2024) declares the page box explicitly; with `size: auto` (the default), "the dimensions and orientation of the target sheet are used", i.e., the user's printer default governs. Applies to print CSS for any result-view surface.
- `window.print()` (MDN, Baseline June 2023) opens the print dialog; it blocks while the dialog is open.
- Client-side PDF libraries fix page size at generation time in PDF points: pdf-lib `src/api/sizes.ts` (pinned SHA 93dd36e85aa659a3bca09867d2d8fac172501fbe): `A4: [595.28, 841.89]`, `Letter: [612.0, 792.0]`; jsPDF `src/jspdf.js` (pinned SHA a3930ce03a585a26b2c76d12a0f413ce96f6d1a3, lines 271-323): `format` defaults to "a4"; `letter: [612, 792]`; custom sizes as number arrays. The PDF's MediaBox carries the chosen size independent of the user's printer default.

### 5.5 Indonesian language expectations

Source: `_evidence-b3-web.md` §8.

- UU Nomor 24 Tahun 2009 (official statute PDF at `https://peraturan.bpk.go.id/Download/27970/...`), Pasal 29: "Bahasa INDONESIA wajib digunakan dalam informasi tentang produk barang atau jasa produksi dalam negeri atau luar negeri yang beredar di INDONESIA" (Indonesian must be used in information about goods/service products circulating in Indonesia). Framing recorded in the evidence: this is a consumer-information statute, not a web-content localization regulation; it supports the expectation that consumer-facing product/service information in Indonesia be available in Indonesian, as supporting context only.
- Indonesian is a fully covered CLDR locale and a standard `Intl` locale (evidence §5.3).

### 5.6 Legacy i18n baseline (evidence)

Source: `_evidence-legacy-frontend.md` §11 and §12; `_evidence-ui-audits.md` §9.2.

- Legacy is 100% Indonesian, hardcoded inline: `<html lang="id">` (`frontend/src/app/layout.tsx:49`), openGraph `locale: 'id_ID'` (line 26), root default title "Papyr - Alat PDF Gratis untuk Indonesia" (line 18). No i18n library, no middleware, no translation module, no stored preference (evidence §11.1).
- Footer language switcher (`Footer.tsx:64-116`): `id_ID` active, English row is an inert div with a "Segera hadir" badge, no switching logic (D9; owner question U4).
- Legacy output filename defects: merge hardcodes `merged.pdf` (English); split generates `split_<range>.pdf`; image-to-pdf always `images.pdf` (`_evidence-ui-audits.md` §9.2); DEC-042 requires safe localized suffixes.
- Legacy copy register inconsistency: split header uses informal "kamu"; pdf-to-image mixes "di-share"; the rebuild uses one neutral register per locale (UX §9 item 7, line 179; audit §6 item 14).
- Legacy URL evidence: canonical domain mypapyr.com; the legacy app is Indonesian-only, so all legacy unprefixed URLs carry Indonesian content (evidence §12).

## 6. Alternatives

### Alternative A - Edge-country-only paper selection with A4 fallback (recommended)

- **What it is**: the paper standard is a deterministic function of the trusted edge country code only: `US`, `CA` -> Letter; every other or missing value -> A4. The active locale plays no independent role. The country code is ephemeral (used for the page-policy decision, never stored as a profile), read only from the trusted edge headers (Cloudflare `CF-IPCountry` or Vercel `x-vercel-ip-country`), with untrusted or spoofed values (e.g., user-supplied headers outside the trusted edge, `XX`, `T1`, invalid codes) treated as absent.
- **Trade-offs**: matches DEC-085/DEC-089 exactly ("Edge-derived country context is more accurate than language alone", DEC-085 rationale); resolves UX §21.3 cleanly: when EN spans US and non-US markets, the language tag never decides paper, the edge country does, and the deterministic fallback is A4 (DEC-089). Cost: the language switcher cannot influence paper choice, so a US-resident Spanish reader always gets Letter and a German English reader always gets A4; the evidence supports this as correct regional behavior (CLDR §5.2).
- **Risks**: VPN/shared-IP misassignment (the vendor docs record `XX`/`T1` and approximation); mitigated by A4 fallback (the broadly dominant international standard, DEC-089 rationale) and by the visible-before-processing disclosure.
- **Cost/operational impact**: negligible; one pure function plus header trust rules.
- **Privacy/security**: no geolocation prompt, no persistent profile, no analytics of the country value beyond the accepted disclosures (DEC-085 consequences; arch §5.3).

### Alternative B - Locale-priority mapping (active locale -> paper via the locale's region)

- **What it is**: derive paper from the active locale string (e.g., `en-US` -> Letter, `en-GB` -> A4, `es-ES` -> A4, `es-MX` -> Letter, `id-ID` -> A4).
- **Trade-offs**: conceptually simple, but the product's locale tags are `en`, `es`, `id` (no region, per the route scheme UX §8.2), so `en` and `es` cannot distinguish markets at all; `Intl.Locale.maximize()` would guess a region from the language (e.g., `en` -> US), which is exactly the "pretend language alone identifies paper preference" behavior DEC-083's consequence forbids; and the user's manually selected language is a language choice, not a region statement.
- **Risks**: systematic misassignment for non-US English speakers and Latin American Spanish speakers, the two largest launch populations (DEC-104 regions).
- **Verdict**: rejected as the primary mechanism; retained only as an explicitly documented non-goal.

### Alternative C - Browser geolocation API

- **What it is**: ask the browser for precise location to pick the paper size.
- **Trade-offs**: most "accurate" per device, but DEC-085 explicitly rejects it ("without requesting precise browser geolocation") and it adds a permission prompt that violates the no-settings, no-friction flow (DEC-041, DEC-008).
- **Verdict**: rejected; prohibited by decision.

## 7. Recommendation

Recommendation only, not an accepted decision (DEC-054, DEC-057): adopt **Alternative A** with the following rule table and supporting rules.

### 7.1 Paper-standard rule

| Trusted edge country code (ISO 3166-1 alpha-2) | Paper standard | Basis |
|---|---|---|
| `US`, `CA` | Letter-family | DEC-083, DEC-085 |
| Any other valid code | A4-family | DEC-083, DEC-085 ("A4 for other countries") |
| Absent header, `XX` (no data), `T1` (Tor), invalid or non-ISO code, or value arriving outside the trusted edge | A4 (deterministic default) | DEC-089 |

### 7.2 Supporting rules

1. **Trust boundary**: the country code is accepted only from the trusted Vercel or Cloudflare request edge headers after the platform's own filtering; user-supplied or proxy-injected values outside the trusted edge are treated as absent (DEC-085 consequence; arch §5.3 line 266). Cloudflare `CF-IPCountry` is delivered via the opt-in "Add visitor location headers" Managed Transform, and Vercel delivers `x-vercel-ip-country`; the implementation must confirm which one is active and test the spoof-rejection behavior.
2. **Ephemerality**: the value is used for the page-policy decision only, never stored as a persistent location profile (DEC-085; arch §5.3 line 267).
3. **Visibility**: the selected standard is shown before conversion on the JPG-to-PDF tool in all three locales (DEC-083, DEC-085, DEC-089; UX §12.4 item 5), with the user-visible summary wording finalized in the copy pass (UX §21.3).
4. **Locale is not a paper signal**: the active locale (`en`, `es`, `id`) never decides Letter versus A4 by itself; this is the documented resolution of UX §21.3's "when EN spans US and non-US markets" case. A future revision may add CLDR-based Letter handling for the additional de facto Letter countries (evidence §5.2) only through a new explicit owner decision; the accepted decisions limit Letter to US and Canada (DEC-085).
5. **Print and PDF generation**: for any print CSS surface, use `@page { size: ... }` with the policy-selected size or accept the UA default (`auto` uses the target sheet); for client-side PDF generation, pass the policy-selected constant (pdf-lib `PageSizes.A4`/`Letter`; jsPDF `format: 'a4'`/`'letter'`) so the MediaBox carries the intended size (evidence §5.4).
6. **Locale-aware formatting**: UI formatting uses `Intl` with the active locale for numbers and dates per CLDR (Indonesian decimal comma/thousands dot, `dd/MM/yy` short dates, 24-hour clock, `id`/`es` plural rules via ICU-style messages; evidence §5.3). Indonesian UI messages need no plural-form selection (cardinal `other` only); Spanish needs at least one/other.
7. **Copy resilience**: EN/ES/ID copy must not break layouts at any breakpoint (UX §16.1 item 6); one neutral register per locale (UX §9 item 7).
8. **Output names**: safe localized suffixes per DEC-042 replace the legacy `merged.pdf`/`images.pdf` hardcodes (evidence §5.6).
9. **Indonesian coverage at relaunch**: all five tools plus the essential supporting surfaces are complete in ID before launch: tool instructions, errors, processing disclosures, results, metadata, navigation, legal/support pages, status, roadmap, blog index and the five launch topics, and core accessibility text (DEC-118 consequences; DEC-121 for the blog). The schedule trade-off is governed by the complete-over-deadline policy (DEC-103); if ID completeness cannot be met in the one-month target, the launch delays rather than cutting ID scope.
10. **Document language**: `<html lang>` and metadata are locale-aware per page (replacing the hardcoded `lang="id"` at `frontend/src/app/layout.tsx:49`; UX §9 item 9), with hreflang/canonical/sitemap implications owned by B4 (DEC-023).

## 8. Measurable acceptance criteria

Functional verification criteria, with no benchmark wording (DEC-066):

1. **Deterministic paper function**: a pure, unit-tested function maps (trusted edge country code) to Letter or A4 per §7.1, with the A4 fallback covering absent, `XX`, `T1`, invalid, and untrusted values.
2. **Spoof rejection**: a test proves that a forged country header delivered outside the trusted edge is treated as absent (A4), not honored.
3. **Visibility**: the JPG-to-PDF UI displays the selected standard before processing in EN, ES, and ID (DEC-083, DEC-085, DEC-089).
4. **No settings, no geolocation**: no manual paper control exists (DEC-041) and no geolocation permission is requested (DEC-085).
5. **Ephemerality**: the country value is not persisted in any cookie, localStorage, server record, analytics event beyond the accepted scope, or backup (DEC-085; DEC-025).
6. **Print/PDF size**: generated PDFs carry the policy-selected MediaBox (A4 595.28 x 841.89 pt or Letter 612 x 792 pt per the library constants); print CSS uses the corresponding `@page` size (evidence §5.4).
7. **Locale formatting**: numbers and dates render per CLDR for `id` (comma decimal, dot thousands, `dd/MM/yy`) and per `es`/`en` conventions; plural handling works for Spanish `one`/`many`/`other` and Indonesian single-form messages (evidence §5.3).
8. **Localized output names**: downloaded results use safe localized suffixes per DEC-042; the legacy English hardcodes are gone (evidence §5.6).
9. **ID launch completeness**: the ID surface is complete across tools, legal, support, status, roadmap, blog, and core accessibility text before launch (DEC-118); any schedule shortfall triggers the DEC-103 complete-over-deadline policy rather than a partial ID launch.
10. **Locale routing**: every localized route carries its locale prefix (DEC-023), and locale-less entry redirects once with manual override precedence (DEC-047), with the SEO behavior verified per B4.
11. **No benchmarks**: the paper-policy design contains no comparative quality/performance study, corpus, matrix, or score program (DEC-066).

## 9. Assumptions, uncertainties, and unresolved questions

1. **DEC-083 vs DEC-085 interpretation**: DEC-083 mentions deriving the applicable locale from the active Papyr locale plus a documented regional rule; DEC-085 (later) selects the trusted edge country mechanism. This brief reads DEC-085/089 as the operative rule and documents that reading; the owner should confirm that the edge-country-only rule is the accepted interpretation (residual of UX §21.3).
2. **De facto Letter countries beyond US/CA**: CLDR records Letter as the de facto paper size in Chile, Colombia, Costa Rica, El Salvador, Guatemala, Mexico, Nicaragua, Panama, Philippines, Venezuela, Belize, and Puerto Rico (evidence §5.2), while DEC-085 limits Letter to US and Canada. Owner question: keep the accepted two-country rule (recommended, with the CLDR nuance documented as a known limitation) or extend Letter to the additional CLDR-Letter countries via a new decision.
3. **F4/Folio (210 x 330 mm)**: common in Southeast Asia including Indonesia but documented only by secondary sources; not a standard. Owner question: out of scope at launch (recommended; the accepted policy is A4/Letter only).
4. **ISO 216 dimension table not public**: the official ISO page is paywalled; dimensions are corroborated by CEN, MDN, and library constants (evidence §5.2). For a strictly primary statement, the ISO OBP preview or purchased standard would be needed; not required for this brief.
5. **ANSI/ASME Y14.1 attribution** is via the encyclopedic source (secondary for the standard number); the ANSI webstore page was not fetched (paywalled).
6. **Edge header availability**: `CF-IPCountry` is opt-in via a Managed Transform and Vercel's headers are platform-managed; the exact trusted-header configuration is an implementation detail to confirm at design time (evidence §5.3).
7. **CLDR chart version**: the `latest` charts URL is unversioned (Wikipedia cited CLDR 45); TR35/LDML is 48.2 as of access. Versioned charts (e.g., `charts/45/`) can pin the dataset if audit reproducibility requires it.
8. **next-i18next README** was fetched from a moving ref (no SHA pinned); v16 details may shift (evidence §5.3).
9. **UU 24/2009 framing**: cited as supporting consumer-information context only, not as a technical localization regulation (evidence §5.5); no compliance claim is made.
10. **Material owner questions**: (a) the DEC-083/085 interpretation in item 1; (b) the Letter-country extension in item 2; (c) confirmation that ID coverage per §7.2 item 9 is the accepted relaunch inventory, accepting DEC-103's delay-over-cut policy if the schedule slips.

## 10. Dependencies and cross-track interfaces

- **A5 (JPG to PDF)**: consumes the paper-policy function output for MediaBox selection and must display the selected standard before conversion (DEC-083, DEC-085); the accepted formats JPG/JPEG/PNG/WebP (DEC-187) do not change the paper policy.
- **B1 (browser routing)**: the browser-local JPG-to-PDF path applies the same paper policy; the routing decision must not hide the paper disclosure.
- **B4 (SEO, slugs, routes)**: locale-prefixed routes, translated ID slugs (DEC-122), locale-less entry detection (DEC-047), and hreflang/canonical/sitemap per locale (DEC-023) are B4's domain; B3 supplies the locale set (en/es/id), the language-tag facts (RFC 5646: `es-419` is not a valid hreflang value; ISO 639-1 + ISO 3166-1 alpha-2 only), and the requirement that locale-aware `<html lang>` be per page.
- **B2 (accessibility)**: localized labels, errors, and announcements are launch-gate items (DEC-118); the language switcher is keyboard- and screen-reader-accessible (DEC-149; D9 fix).
- **D2 (legal and privacy copy)**: privacy and analytics documentation must disclose any country-level processing performed by hosting or analytics providers (DEC-085 consequence); metadata-preservation disclosure for JPG-to-PDF (DEC-084) is D2 copy territory.
- **Track E (blog)**: the five launch topics and daily cadence are localized EN/ES/ID (DEC-121, DEC-124); the paper policy has no blog interface, but the locale data here (CLDR, plural rules) informs blog localization.
- **X1/X2 (index/reconciliation)**: this brief contributes the paper rule table, the DEC-083/085 interpretation item, the Letter-country extension question, and the ID coverage inventory to the reconciliation decision prompts (plan §14).

## 11. Source-date log and evidence-completeness notes

- All web sources accessed 2026-07-31; versions and dates recorded inline in `_evidence-b3-web.md` (ISO 216:2007 edition 2; EN ISO 216:2007; SNI ISO 216:2010; UNE-EN ISO 216:2008; RFC 5646 2009-09; RFC 9110 2022-06; UTS #35 LDML 48.2 2026-03-03; Cloudflare docs updated 2026-05-05; Vercel docs last updated 2025-12-13; MDN `@page`/`size` modified 2026-04-20; pdf-lib SHA 93dd36e85aa659a3bca09867d2d8fac172501fbe; jsPDF SHA a3930ce03a585a26b2c76d12a0f413ce96f6d1a3; Next.js docs 16.2.12).
- Legacy evidence read 2026-07-31; all paths under `papyr-reference/`; line references cited in §5.6.
- Completeness notes: (a) the CLDR country table is a verified sample of the territory-information dataset, not a full-world enumeration; the full dataset is the primary reference; (b) Wikipedia is used only where the evidence file marks it secondary, with the primary citations it relies on (CLDR, AF&PA) noted; (c) no benchmark or test-run evidence was created (DEC-066).
- Uncertainties from §9 are not resolved in this brief; they are recorded for the owner and for reconciliation (X2).

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066).
- No installs, builds, server starts, VPS/SSH access, deployment, account creation, geolocation requests, browser execution, or authenticated/mutating remote actions were performed (plan §4.1).
- No product code, scaffolding, or infrastructure was created or modified; no decision log or specification was edited; no evidence file, audit file, or `papyr-reference/` file was modified.
- `papyr-reference/` was read-only; verified unchanged via `git -C papyr-reference status --porcelain` (empty output, exit 0) before and after this task.
- No claim is made that UU 24/2009 or any other source imposes a technical localization requirement; the statute is cited as supporting context only.
- Findings in this brief are recommendations, not accepted decisions (DEC-054, DEC-057).
