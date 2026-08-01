# Evidence B3 — i18n, Locale, and Paper-Standard Policy (Web/Primary Sources)

- **Deliverable**: Track B, B3 — web/primary-source evidence for i18n, locale, and paper-standard policy
- **Access date for ALL sources below**: **2026-07-31** (unless a page states its own modification date, which is recorded per source)
- **Method**: read-only, anonymous web access. No authenticated calls, no installs, no browser execution. Large pages were fetched once and their relevant sections extracted (raw tool-output files retained under the local OpenCode tool-output cache for line-level re-verification).
- **Source hierarchy**: Primary sources (ISO, IETF, W3C, Unicode/CLDR, vendor official docs, library source code) are cited first. Wikipedia and similar encyclopedic pages are explicitly marked **[SECONDARY]** with the primary citations they rely on noted.
- **Verification evidence** (required): file exists; non-empty; §1 contains a paper-size country mapping table with sources; §4 contains the BCP 47 / CLDR / Intl section with URLs; §6 contains the `@page` / print section; no placeholder tokens (no TODO/TBD/lorem-ipsum tokens anywhere).

---

## 1. Paper size standards and country usage

### 1.1 ISO 216 (A4 = 210 × 297 mm) — PRIMARY sources

**Source: ISO official standard page**
- URL: https://www.iso.org/standard/36631.html
- Page title: "ISO 216:2007 — Writing paper and certain classes of printed matter — Trimmed sizes — A and B series, and indication of machine direction"
- Version/date: Edition 2, published 2007-09. Page states: "This publication was last reviewed and confirmed in 2021. Therefore this version remains current." Lifecycle shows stage 90.20 "International Standard under systematic review" reopened 2026-07-15 (i.e., under review as of access date). Previous withdrawn edition: ISO 216:1975. TC: ISO/TC 6 "Paper, board and pulps"; ICS 85.080.10 "Office paper".
- Abstract (verbatim): "ISO 216:2007 specifies the trimmed sizes of writing paper and certain classes of printed matter. It applies to trimmed sizes of paper for administrative, commercial and technical use, and also to certain classes of printed matter, such as forms, catalogues, etc. It does not necessarily apply to newspapers, published books, posters or other special items which may be the subject of separate International Standards. ISO 216:2007 also specifies the method for the indication of the machine direction for trimmed sheets."
- **Important gap noted**: the public iso.org page does **not** publish the dimension table (paywalled/OBP). The 210 × 297 mm value is corroborated by the sources below.

**Source: CEN adoption record (EN ISO 216:2007), iTeh standards catalogue**
- URL: https://standards.iteh.ai/catalog/standards/cen/1627f460-418a-49c5-ad08-968cac6736d4/en-iso-216-2007
- Page title: "EN ISO 216:2007 — Paper Sizes A and B Series…"
- Date: catalog entry dated 2007-09-15. States: "EN ISO 216:2007 (ISO 216:2007) defines the system of trimmed sizes… the metric A series (main series) and B series (subsidiary)… **Most used: A4 (210 × 297 mm)**."

**Source: MDN `size` descriptor (dimensions as implemented by CSS/browsers)** — see §6 for full citation. A4 = 210mm × 297mm, letter = 8.5in × 11in.

**Source: pdf-lib source code (points-based A4 constant)** — see §6. `PageSizes.A4 = [595.28, 841.89]` pt (= 210 × 297 mm at 72 dpi), `PageSizes.Letter = [612.0, 792.0]` pt (= 8.5 × 11 in).

**[SECONDARY] Source: Wikipedia "Paper size"** (dimension table and adoption history)
- URL: https://en.wikipedia.org/wiki/Paper_size (revision oldid=1362341472; accessed 2026-07-31)
- Table row: A4 = 210 × 297 mm; A0 = 841 × 1189 mm; aspect ratio √2.
- Adoption claims: DIN 476 (1922) → ISO 216 (1975); "By 1977, A4 was the standard letter format in 88 of 148 countries. Today the standard has been adopted by all countries in the world except the United States and Canada. In Mexico, Costa Rica, Colombia, Venezuela, Chile, and the Philippines, the US letter format is still in common use, despite their official adoption of the ISO standard."
- Primary citation it relies on for the country map: the CLDR "Territory Information" dataset (see 1.3), cited in the article's map caption as "Common Locale Data Repository in 2017".

### 1.2 US Letter (8.5 × 11 in = 215.9 × 279.4 mm) — ANSI/ASME Y14.1

**[SECONDARY] Source: Wikipedia "Letter (paper size)"**
- URL: https://en.wikipedia.org/wiki/Letter_(paper_size) (revision oldid=1365157894, last edited 2026-07-20)
- States: "**Letter** (officially **ANSI A**) is a paper size standard defined in **ANSI/ASME Y14.1** by the American National Standards Institute… It measures 8.5 by 11 inches (215.9 by 279.4 mm) and is similar in use to the A4 paper standard at 210 mm × 297 mm… used by most other countries, defined in ISO 216…"
- Primary citations it relies on:
  - **CLDR "Territory Information"** (Unicode): "US Letter is the primary paper size used in Belize, Canada, Chile, Colombia, Costa Rica, El Salvador, Guatemala, Mexico, Nicaragua, Panama, Philippines, Puerto Rico, United States, Venezuela" — cited version: CLDR 45, 2024-04-16.
  - American Forest & Paper Association (AF&PA), "Why is the standard paper size in the U.S. 8½″ x 11″?" (archived) — origin of 8.5 × 11.
  - Reagan-era adoption for US federal forms (early 1980s); Government Letter was previously 8 × 10.5 in.
- Note: the actual ANSI/ASME Y14.1 document (current: "Decimal Inch Drawing Sheet Size and Format", ANSI/ASME Y14.1-2020 era) is a paywalled standard; I did not fetch the ANSI webstore page. The identification of ANSI/ASME Y14.1 as the governing standard comes from the encyclopedic source above; flag as **[SECONDARY]** for the standard number.

### 1.3 Country → paper-size mapping (PRIMARY dataset: Unicode CLDR Territory Information)

**Source: CLDR "Territory Information" (supplemental data chart)**
- URL: https://www.unicode.org/cldr/charts/latest/supplemental/territory_information.html
- Publisher: Unicode Consortium / CLDR. The `latest` URL resolves to the current CLDR release at access time; Wikipedia's citation of the same dataset was to "CLDR 45, 2024-04-16". (TR35/LDML spec version at access: 48.2, dated 2026-03-03 — see §4.2.)
- Columns used: Measurement system (metric / US) and Paper Size (A4 / US-Letter), plus preferred calendar.

Verified rows (extracted from the fetched page; each row lists **Measurement system** and **Paper size**):

| Country (CLDR territory) | Meas. system | Paper size | Verified from row |
|---|---|---|---|
| United States | US | US-Letter | yes |
| Canada | metric | US-Letter | yes |
| Belize | US | US-Letter | yes |
| Chile | metric | US-Letter | yes |
| Colombia | metric | US-Letter | yes |
| Costa Rica | metric | US-Letter | yes |
| El Salvador | metric | US-Letter | yes |
| Guatemala | metric | US-Letter | yes |
| Mexico | metric | US-Letter | yes |
| Nicaragua | metric | US-Letter | yes |
| Panama | metric | US-Letter | yes |
| Puerto Rico | US | US-Letter | yes |
| Philippines | metric | US-Letter | yes |
| Venezuela | metric | US-Letter | yes |
| Indonesia | metric | A4 | yes |
| Spain | metric | A4 | yes |
| Japan | metric | A4 | yes |
| Argentina | metric | A4 | yes |
| Bolivia | metric | A4 | yes |
| Brazil | metric | A4 | yes |
| Cuba | metric | A4 | yes |
| Dominican Republic | metric | A4 | yes |
| Ecuador | metric | A4 | yes |
| Honduras | metric | A4 | yes |
| Paraguay | metric | A4 | yes |
| Peru | metric | A4 | yes |
| Uruguay | metric | A4 | yes |
| (sampled for completeness) Afghanistan, Australia, Austria, Belgium, Germany, UK, India, Vietnam, Thailand, Cambodia, China — all metric / A4 | metric | A4 | yes |

**Interpretation / conflicts to document (B3-relevant):**
- **Mexico**: CLDR lists the measurement system as `metric` but paper size as `US-Letter`. This is the "metric country, Letter paper" conflict. Wikipedia's adoption list says Mexico officially adopted ISO 216 (1965) yet "the US letter format is still in common use".
- **Philippines**: CLDR lists `metric` measurement system with `US-Letter` paper size — the ambiguity flagged in the research brief. Wikipedia lists the Philippines among "US letter format still in common use, despite official adoption of the ISO standard" and the Letter article groups it with Letter-primary countries.
- **Chile/Colombia/Venezuela**: CLDR says US-Letter; Wikipedia says these countries officially adopted ISO 216 but Letter remains common. So: official standard = ISO 216 lineage; de facto office paper = Letter (per CLDR data).
- **Canada**: CLDR says `metric` measurement system but `US-Letter` paper (matches Wikipedia: ISO 216 "adopted by all countries except the United States and Canada" — i.e., Canada is officially non-ISO for paper even though metric).
- **Indonesia and Spain**: both `metric` + `A4` in CLDR (see §2 and §3).

### 1.4 F4 / Folio (transitional size relevant to Indonesia and Southeast Asia)

**[SECONDARY] Source: Wikipedia "Paper size", §Transitional paper sizes → F4 (from article wikitext, section anchor "Paper size F4")**
- URL: https://en.wikipedia.org/wiki/Paper_size#F4
- Verbatim: "A non-standard **F4** paper size is common in Southeast Asia. It is a transitional size with the shorter side of ISO A4 (210 mm…) and the longer side of British *Foolscap* (13 in…). ISO A4 is exactly 90% the height of F4. This size is sometimes also known as (metric) 'foolscap' or 'folio'." Table gives F4 = 210 × 330 mm.
- Related secondary citation in the same article: Canadian standard CAN2-200.2-M79 "Common Image Area for Paper Sizes P4 and A4" documented a 210 × 280 mm size (withdrawn 2012) — cited via scc.ca (Standards Council of Canada) — this shows the P4/A4 transition is a known topic in standards history.

---

## 2. Indonesia: office paper size and national standards body (BSN)

### 2.1 National standard adopting ISO 216: SNI ISO 216:2010 (PRIMARY — BSN catalog)

**Source: BSN "Pesta Online" (portal pemesanan SNI — Badan Standardisasi Nasional official SNI catalog)**
- Listing URL: https://pesta.bsn.go.id/produk/by_ics/10?ics_no=85&key= (ICS 85 — TEKNOLOGI KERTAS)
- Detail URL: https://pesta.bsn.go.id/produk/detail/8160-sniiso2162010
- Catalog entry (verbatim fields): **"SNI ISO 216:2010 — Kertas dan karton — Kertas tulis dan beberapa jenis barang cetakan-Ukuran siap pakai-Seri A dan B, dan indikasi arah mesin"**; Language: **Dwi-Bahasa** (bilingual); No ICS: **85.060**; Status: **Berlaku** (in force); price Rp 45.000.
- Interpretation: Indonesia's national standard **SNI ISO 216:2010** is the Indonesian adoption of ISO 216 (A and B series trimmed sizes, with machine-direction indication), i.e., Indonesia's official paper size standard is the ISO 216 system (A4 = 210 × 297 mm). The related raw-paper standard SNI ISO 217:2010 / SNI ISO 217:2013 (ISO 217, IDT) also appears in the same BSN catalog page.
- Caveat: the BSN catalog page does not restate the millimeter dimensions; dimensions come from ISO 216 itself (§1.1) and CLDR (Indonesia = A4, §1.3).

### 2.2 Common Indonesian office sizes (A4, F4/Folio, kuarto)

- **A4**: CLDR territory data lists Indonesia as `metric` + `A4` (PRIMARY, §1.3). ISO 216 adoption per SNI ISO 216:2010 (§2.1).
- **F4/Folio**: **[SECONDARY]** Wikipedia F4 section (§1.4) documents F4 = 210 × 330 mm as common in Southeast Asia, including the "folio" name. Indonesian-language industry sources found in search (marked secondary, commercial): dinastindopratama.com ("Standard ukuran kertas internasional, kertas di Indonesia", 2020) lists Indonesian market sizes: "A4: 21 × 29.7 cm; A5: 14.8 × 21 cm; **F4/Folio: 21.5 × 33 cm**; Q4/Kuarto: 21.6 × 27.9 cm (ANSI Letter-equivalent); A3: 29.7 × 42 cm". These commercial sources are **not primary**; they corroborate that A4 is the office standard and F4/Folio is a widely sold local size.
- Indonesian Wikipedia "Ukuran kertas" (id.wikipedia.org/wiki/Ukuran_kertas) is **[SECONDARY]** and likewise presents ISO 216 A-series as the international/office standard, with R and F sizes "muncul sesuai permintaan pasar" (appear per market demand).

---

## 3. Spain: A4 (ISO 216) usage — UNE adoption (PRIMARY-ish)

**Source: AENOR store catalog (Asociación Española de Normalización — the Spanish standards body's official catalog)**
- URL: https://tienda.aenor.com/p/norma-une-en-iso-216-2008-n0040991
- Page title: **"UNE-EN ISO 216:2008"**
- Catalog fields (verbatim): "**Papel de escritura y ciertos tipos de impresos. Formatos acabados. Series A y B, e indicador de dirección máquina. (ISO 216:2007)**"; "Fecha edición: 2008-04-30 — **En Vigor**"; "Idiomas disponibles: Español, Inglés"; "ICS: 85.080.10 — Papel para oficina"; "CTN: CTN 57 — Celulosa y papel"; "Anulaciones: Anula a UNE-EN ISO 216:2002"; "**Equivalencia Internacional: Idéntica ISO 216:2007, Idéntica EN ISO 216:2007**".
- Interpretation: the Spanish national standard **UNE-EN ISO 216:2008** is identical to ISO 216:2007 and is currently in force ("En Vigor"), i.e., A4 is the Spanish national paper format standard.
- Corroborating **[SECONDARY]**: Spanish Wikipedia "ISO 216" (es.wikipedia.org/wiki/ISO_216, updated 2025-12-21): "La norma ISO 216 equivale a la norma española UNE-EN-ISO 216"; CLDR territory data lists Spain = metric + A4 (PRIMARY, §1.3).

---

## 4. Locale → region mapping standards

### 4.1 BCP 47 / RFC 5646 — how language tags encode region (PRIMARY)

**Source: RFC 5646 "Tags for Identifying Languages" (BCP 47)**
- URL: https://www.rfc-editor.org/rfc/rfc5646.html (also datatracker.ietf.org/doc/html/rfc5646)
- Date: September 2009; Status: Best Current Practice 47 (with RFC 4647); Obsoletes RFC 4646/3066/1766.
- Key normative facts (verbatim from the RFC):
  - ABNF: `Language-Tag = langtag / privateuse / grandfathered`; `langtag = language ["-" script] ["-" region] *("-" variant) *("-" extension) ["-" privateuse]`; `region = 2ALPHA ; ISO 3166-1 code / 3DIGIT ; UN M.49 code`.
  - Region subtags (Section 2.2.4): "used to indicate linguistic variations associated with or appropriate to a specific country, territory, or region… Two-letter region subtags were defined according to the assignments found in ISO 3166-1… In addition, the codes that are 'exceptionally reserved' … with the exception of 'UK', which is an exact synonym for the assigned code 'GB'."
  - Examples the RFC itself uses: `en-US` (American English), `es-419`-style region usage described via "Spanish content tailored to be useful throughout Latin America", `en-CA`, `fr-CA`, `zh-Hant-CN`, `sr-Latn-RS`.
  - Case conventions (Section 2.1.1): ISO 639 lowercase language, ISO 15924 title-case script, ISO 3166-1 uppercase region — so canonical forms `en-US`, `en-GB`, `es-ES`, `id-ID` follow the RECOMMENDED formatting (formatting is not semantically meaningful; tags are case-insensitive).
  - Canonicalization (Section 4.5) and the IANA Language Subtag Registry (Section 3) govern valid subtags.
- Derived mapping for this project: `en-US` = English (language `en` from ISO 639-1) + region `US` (ISO 3166-1 alpha-2); `en-GB` = English + Great Britain; `es-ES` = Spanish + Spain; `id-ID` = Indonesian + Indonesia. The region subtag is the mechanism by which a locale string carries country information.

**Source: RFC 9110 §12.5.4 (see §5.1)** also defines `language-range` by reference to RFC 4647 §2.1.

### 4.2 CLDR / UTS #35 (LDML) — what data exists for `id` (PRIMARY)

**Source: Unicode Technical Standard #35, "Unicode Locale Data Markup Language (LDML)"**
- URL: https://unicode.org/reports/tr35/
- Version/date: **48.2**, dated **2026-03-03**; status: approved Unicode Technical Standard (stable).
- Key facts:
  - Defines Unicode locale identifiers built on BCP 47: `unicode_language_id = language (script)? (region)? (variant)*`; region subtag = alpha{2} (ISO 3166-1) or digit{3} (UN M.49) — with validity data in `common/validity/region.xml`.
  - "For example, 'en-US' (American English), 'en_GB' (British English), 'es-419' (Latin American Spanish), and 'uz-Cyrl' (Uzbek in Cyrillic) are all valid Unicode language identifiers."
  - Documents locale inheritance, likely subtags, language matching, number formatting (Part 3), date/time formatting (Part 4), plural rules, and MessageFormat (Part 9) — the data model behind `Intl`.

**Source: CLDR Locale Data Summary for Indonesian [id]**
- URL: https://unicode.org/cldr/charts/latest/summary/id.html (latest-release chart; release-era data, LDML 48.x at access)
- Verified data present for `id` (Indonesian):
  - Numbering systems: default = `latn`, native = `latn`.
  - Date formats (Gregorian, native column): full `EEEE, dd MMMM y`; long `d MMMM y`; medium `d MMM y`; short `dd/MM/yy`. Time formats: full `HH.mm.ss zzzz`; long `HH.mm.ss z`; medium `HH.mm.ss`; short `HH.mm` (24-hour clock).
  - Yes/no (posix): `yes:y / ya:y`, `no:n / tidak:t`.
  - Standard number patterns: `standard-decimal #,##0.###`; `standard-currency ¤#,##0.00`; `standard-percent #,##0%`; `standard-scientific #E0`.
  - Caveat on separator symbols: the chart's plural-rule examples render decimal with comma ("1,5 hari") while the standard pattern string shows `#,##0.###`; MDN's runtime example (`new Intl.NumberFormat(["ban", "id"]).format(123456.789)` → `"123.456,789"`, see §4.4) confirms the runtime Indonesian convention: `.` thousands group, `,` decimal separator.
  - `id` has full locale coverage in CLDR (the summary lists characters, parse leniency, display names, ellipsis, quotation marks, etc.) — i.e., Indonesian is a fully supported CLDR locale.
- Related CLDR primary source for plural behavior of `id` and `es`: §7.1.

### 4.3 MDN Intl API — Intl.Locale (PRIMARY reference)

**Source: MDN "Intl.Locale"**
- URL: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Locale
- Page modified: 2025-07-22. Baseline: widely available (since Sept 2020).
- Key facts: `Intl.Locale` "represents a Unicode locale identifier"; properties include `language`, `script`, **`region`** ("Returns the region of the world (usually a country) associated with the locale"), `variants`, plus extension-derived `calendar`, `hourCycle`, `numberingSystem`, etc. Methods: `maximize()` / `minimize()` (likely-subtags), `toString()`, `getWeekInfo()`, `getTimeZones()`, `getTextInfo()`.
- **How to derive region/country from a locale string** (per this reference): construct `new Intl.Locale("es-ES")` and read `.region` → `"ES"`; if the tag has no region, `maximize()` fills the most likely region from CLDR data (e.g., `new Intl.Locale("es").maximize()` → region `ES`). Same mechanism applies for `en-US` → `US`, `en-GB` → `GB`, `id-ID` → `ID`. Region subtags are BCP 47/ISO 3166-1 (§4.1).

**Source: MDN "Intl.NumberFormat"**
- URL: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat (fetched via reader; content verified)
- Key facts: formats numbers per locale and options; `locales` argument may be a list with fallbacks. Relevant runtime example (verbatim): `new Intl.NumberFormat(["ban", "id"]).format(123456.789)` → `"123.456,789"` — i.e., Indonesian number formatting (period thousands group, comma decimal separator). Spec: ECMAScript® 2027 Internationalization API Specification (# numberformat-objects).

**Source: MDN "Intl.DateTimeFormat"** — not fetched in full; the Intl.Locale and Intl.NumberFormat pages plus the ECMA-402 spec (cited there) cover the API shape. Gap noted: exact DateTimeFormat page content not re-verified on access date; the URL is https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat (same reference family). CLDR id date/time patterns (§4.2) are the data this API consumes.

### 4.4 "Trusted edge country" — coarse country classification by CDN/edge (PRIMARY vendor docs)

**Source: Cloudflare docs, "Cloudflare HTTP headers"**
- URL: https://developers.cloudflare.com/fundamentals/reference/http-request-headers/ (canonical: .../fundamentals/reference/http-headers/)
- Page last updated: 2026-05-05.
- Verbatim: "**CF-IPCountry** — The `CF-IPCountry` header contains a **two-character country code** of the originating visitor's country. Besides the **ISO-3166-1 alpha-2 codes**, Cloudflare uses the following special country codes: `XX` — Used for clients without country code data; `T1` — Used for clients using the Tor network." It is added via the "**Add visitor location headers** Managed Transform" (i.e., opt-in at the edge, not an unconditional header in the current documented model).
- Design implication: the edge terminates the connection and maps the client IP to a **country-level code**; the origin receives a coarse country identifier without needing raw IP geolocation.

**Source: Vercel docs, "Request headers"**
- URL: https://vercel.com/docs/headers/request-headers (page last_updated 2025-12-13)
- Verbatim: "`x-vercel-ip-country` — A two-character ISO 3166-1 country code for the country associated with the location of the requester's public IP address." Also documented: `x-vercel-ip-continent` (two-character ISO 3166-1 continent code: AF/AN/AS/EU/NA/OC/SA), `x-vercel-ip-country-region` (ISO 3166-2 first-level region), and finer-grained `x-vercel-ip-city`, `-latitude`, `-longitude`, `-postal-code`, `-timezone`.
- Design implication: the coarse, privacy-lean signals are country/continent; Vercel *can* expose city/lat/long but those are finer IP-derived data, not precise GPS geolocation.

**Context source (W3C) on IP-based language detection**: W3C "Setting language preferences in a browser" (full citation in §5.2) notes: "Sometimes a server may determine which language to send to you in a way that doesn't rely on the Accept-Language information. For example, Google tends to use IP information to determine the language you will receive." — i.e., coarse IP-derived country signals are an established (non-invasive, header-less) content-negotiation input.

**Synthesis for B3**: "Trusted edge country" = the country (ISO 3166-1 alpha-2) the edge/CDN attributes to the client's IP, delivered as a small integer/2-letter code in a request header or request property (Cloudflare `CF-IPCountry`; Vercel `x-vercel-ip-country` + `x-vercel-ip-continent`). It is coarse by design: country or continent granularity, not precise geolocation; it is an approximation (VPNs, shared IPs, missing data `XX`/`T1`), and it is derived at the network edge where the client's IP is actually visible, so the application never handles raw IP if it only consumes the country code.

---

## 5. Non-invasive locale fallback standards

### 5.1 RFC 9110 §12.5.4 — Accept-Language (PRIMARY)

**Source: RFC 9110 "HTTP Semantics" (IETF, June 2022), Section 12.5.4**
- URL: https://www.rfc-editor.org/rfc/rfc9110.html#section-12.5.4 (full text verified from https://www.rfc-editor.org/rfc/rfc9110.txt, lines 5615–5666 of the fetched copy)
- Verbatim key text:
  - "The 'Accept-Language' header field can be used by user agents to indicate the set of natural languages that are preferred in the response. Language tags are defined in Section 8.5.1. `Accept-Language = #( language-range [ weight ] )` … Each language-range can be given an associated quality value… For example, `Accept-Language: da, en-gb;q=0.8, en;q=0.7` would mean: 'I prefer Danish, but will accept British English and other types of English'."
  - "some recipients treat the order in which language tags are listed as an indication of descending priority… However, this behavior cannot be relied upon. For consistency and to maximize interoperability, many user agents assign each language tag a unique quality value while also listing them in order of decreasing quality." Matching schemes are defined in RFC 4647 ("Basic Filtering" = the HTTP/1.1 scheme from RFC 2616 §14.4).
  - Privacy: "It might be contrary to the privacy expectations of the user to send an Accept-Language header field with the complete linguistic preferences of the user in every request (Section 17.13)."
  - User control: "user agents need to allow user control over the linguistic preference… A user agent that does not provide such control to the user MUST NOT send an Accept-Language header field."
  - RFC 4647 (BCP 47 "Matching of Language Tags", https://www.rfc-editor.org/rfc/rfc4647.html) is the companion spec for language-range syntax and matching; not re-fetched on access date, cited here via RFC 9110.
- Practical browser behavior is documented by W3C (§5.2) and Next.js (§7.3): browsers send the user's ordered language preferences; selecting a language+region adds both the regional tag and the bare language tag (e.g., `es-419, es`).

### 5.2 W3C i18n guidance (PRIMARY)

**Source: W3C Internationalization — "Setting language preferences in a browser"**
- URL: https://www.w3.org/International/questions/qa-lang-priorities
- Publisher: W3C Internationalization (i18n) Activity. (No explicit version; living W3C FAQ page.)
- Key facts:
  - Browsers send language preferences in the **Accept-Language** header; servers use **HTTP content negotiation**; "If none of the languages you request are available, the server should be set up to return a default language choice."
  - Values must conform to **BCP 47**; "It is typically a two- or three-letter language code (eg. `fr` for French), followed by optional subcodes representing such things as country (eg. `fr-CA`…). Regions can include larger areas than countries. If you set Spanish for Latin America, you are likely to set `es-419`."
  - qvalue example: `Accept-Language: da, en-gb;q=0.8, en;q=0.7`.
  - Best practice: list the bare language after a language+region pair (e.g., `fr-CH` followed by `fr`) because literal HTTP/1.1 matching cannot match `fr-CH` against a document labeled `fr` (Apache adds an implicit parent with very low quality; quoting the Apache docs).
  - IP-based detection note (used in §4.4).
  - Edge/Chrome/Firefox/Safari behaviors: Edge auto-adds vanilla tag; Chrome adds it; Firefox requires manual addition; Safari sends only the top item; mobile browsers derive preferences from OS language.

**Related W3C i18n resources (cited by the above page, not re-fetched):**
- Language tags overview: https://www.w3.org/International/articles/language-tags/
- Server setup techniques: https://www.w3.org/International/techniques/server-setup

---

## 6. Browser print behavior and paper size

### 6.1 CSS paged media — `@page` and the `size` descriptor (PRIMARY)

**Source: MDN "@page CSS at-rule"**
- URL: https://developer.mozilla.org/en-US/docs/Web/CSS/@page
- Page modified: 2026-04-20. Baseline 2024 (cross-browser since Dec 2024).
- Key facts: `@page` "modifies different aspects of printed pages… page's dimensions, orientation, and margins". The `size` descriptor "Specifies the target size and orientation of the page box's containing block. In the general case, where one page box is rendered onto one page sheet, it also indicates the size of the destination page sheet." Named pages via `page` property; pseudo-classes `:first/:left/:right/:blank`; margin at-rules (`@top-right` etc.). Spec: CSS Paged Media Module Level 3 (drafts.csswg.org/css-page-3/).

**Source: MDN "size CSS at-rule descriptor"**
- URL: https://developer.mozilla.org/en-US/docs/Web/CSS/@page/size
- Page modified: 2026-04-20. Baseline 2024.
- Key facts:
  - `auto`: "The user agent decides the size of the page. **In most cases, the dimensions and orientation of the target sheet are used**." → i.e., when `size` is not set, the printer's/default paper size governs.
  - `A4`: "This matches the standard, ISO dimensions: **210mm x 297mm**. (most frequently used dimensions for personal printing.)"
  - `letter`: "equivalent to the dimensions of letter paper in North America i.e., **8.5in x 11in**"; `legal` 8.5in × 14in; `ledger` 11in × 17in; `A3/A5/B4/B5/JIS-B4/JIS-B5` also listed.
  - Syntax examples: `size: A4 portrait;`, `size: 4in 6in;`, `@media print { @page { size: 50mm 150mm; } }`.

### 6.2 `window.print()` (PRIMARY)

**Source: MDN "Window: print() method"**
- URL: https://developer.mozilla.org/en-US/docs/Web/API/Window/print
- Page modified: 2025-11-07. Baseline: widely available (June 2023).
- Verbatim: "Opens the print dialog to print the current document. If the document is still loading… finish loading before opening the print dialog. This method will block while the print dialog is open." Spec: HTML Standard (§ printing).

### 6.3 Client-side PDF generation — explicit page size

**Source: pdf-lib source code and README (official repo, Hopding/pdf-lib)**
- Repo: https://github.com/Hopding/pdf-lib ; docs site https://pdf-lib.js.org
- Pinned commit (master at access): **93dd36e85aa659a3bca09867d2d8fac172501fbe**
- Page sizes constant (source file `src/api/sizes.ts`): `A4: [595.28, 841.89]`, `Letter: [612.0, 792.0]`, `Legal: [612.0, 1008.0]`, plus full A/B/C/RA/SRA series, `Executive`, `Folio`, `Tabloid` (points). Permalink-style reference: https://github.com/Hopding/pdf-lib/blob/93dd36e85aa659a3bca09867d2d8fac172501fbe/src/api/sizes.ts
- Usage (README "Create Document"): `const page = pdfDoc.addPage()` (default size) or `pdfDoc.addPage([550, 750])` / `addPage(PageSizes.A4)` — page dimensions are specified explicitly in PDF points when creating client-side PDFs; the PDF's MediaBox then carries the chosen size, independent of the user's printer default.

**Source: jsPDF source code and README (official repo, parallax/jsPDF)**
- Repo: https://github.com/parallax/jsPDF ; docs https://artskydj.github.io/jsPDF/docs/
- Pinned commit (master at access): **a3930ce03a585a26b2c76d12a0f413ce96f6d1a3**
- README (verbatim): "// Default export is a4 paper, portrait, using millimeters for units" — and constructor options `orientation`, `unit`, `format`.
- Source `src/jspdf.js` (pageFormats map, lines 271–311 of the fetched copy): `a4: [595.28, 841.89]`, `letter: [612, 792]`, `government-letter: [576, 756]`, `legal: [612, 1008]`, `junior-legal: [576, 360]`, `ledger: [1224, 792]`, `tabloid: [792, 1224]`, `dl`, and a0–a10/b0–b10/c0–c10 series. Default: `format = format || "a4"` (line 323). Permalink-style reference: https://github.com/parallax/jsPDF/blob/a3930ce03a585a26b2c76d12a0f413ce96f6d1a3/src/jspdf.js (lines 271–323)
- `jsPDFOptions.format` type is `string | number[]` (custom sizes allowed as number arrays) — from `types/index.d.ts` (`constructor(options?: jsPDFOptions)`; `format?: string | number[]`).

**B3 synthesis for print/PDF paper policy**: CSS `@page { size: ... }` lets a web print layout declare A4/letter explicitly; if omitted, the UA uses the target sheet (user's printer default). Client-side PDF libraries fix the page size at generation time in PDF points (pdf-lib `PageSizes.A4`/`Letter`; jsPDF `format: 'a4'`/`'letter'` or raw point/mm arrays). Therefore the application can implement a paper policy keyed on locale/region: pick A4 for `id-ID`/`es-ES` users and Letter for US/CA/PH/MX-style Letter regions, by either setting `@page { size: A4 }` for print CSS or passing the corresponding constant/format to the PDF library.

---

## 7. Language/culture datasets for UI translation

### 7.1 CLDR plural rules for Indonesian (`id`) and Spanish (`es`) (PRIMARY)

**Source: CLDR "Language Plural Rules" supplemental chart**
- URL: https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html
- Publisher: Unicode Consortium / CLDR; `latest` release at access; machine-readable rules defined in UTS #35 Part 3 ("Language Plural Rules", https://unicode.org/reports/tr35/tr35-numbers.html#Language_Plural_Rules).
- **Indonesian [id]**: cardinal category **`other` only** — the chart marks it "no plural differences" (examples: "15 hari", "1,5 hari"); ordinal: `other`. (Legacy code `in` is shown aliased to `id`.)
- **Spanish [es]**: cardinal categories **`one`** (`n = 1`), **`many`** (millions-style: `e = 0 and i != 0 and i % 1000000 = 0 and v = 0 or e != 0..5`), and **`other`**; ordinal: `other`.
- Implication: Indonesian UI messages need no plural-form selection (single form); Spanish messages need at least one/other (and should handle `many` for 1,000,000+).

### 7.2 ICU MessageFormat (PRIMARY)

**Source: ICU User Guide, "Formatting Messages"**
- URL: https://unicode-org.github.io/icu/userguide/format_parse/messages/
- Key facts: ICU `MessageFormat` uses pattern strings with `{placeholders}`; `plural` arguments select sub-messages using the plural rules "for the specified language"; `select` arguments use fixed keywords; `choice` is discouraged; quoting/escaping rules (ASCII apostrophe); recommended to write full sentences inside plural/select sub-messages, with `select` outermost; skeletons (`::`) recommended over locale-specific patterns; a successor MessageFormat 2.0 is in development (working group + draft spec linked from the page).
- Related primary links on the page: CLDR plural-rules spec (cldr.unicode.org/index/cldr-spec/plural-rules), UTS #35 Part 3.

### 7.3 i18n library options in the Next.js ecosystem (PRIMARY docs)

**next-intl**
- URL: https://next-intl.dev/docs (docs nav shows v3/v4 version selector)
- Verbatim: "`next-intl` is an internationalization toolkit for Next.js that helps you: 1. Render localized translations 2. Format dates, numbers, and more 3. Handle internationalized routing". Supports App Router and Pages Router setups.

**next-i18next (v16)**
- URL (README, master at access): https://github.com/i18next/next-i18next (raw README fetched: https://raw.githubusercontent.com/i18next/next-i18next/master/README.md)
- Verbatim: "next-i18next v16 is a thin layer on top of i18next and react-i18next that handles the Next.js-specific wiring — middleware, server/client split, resource hydration". Supports App Router, Pages Router, mixed setups; language detection order: "Detects language from cookie > Accept-Language header > fallback"; `fallbackLng` required config; `resourceLoader` recommended for serverless (Vercel).
- Note: README fetched from `master` (moving ref); no commit SHA pinned for next-i18next.

**Next.js built-in i18n**
- App Router guide: https://nextjs.org/docs/app/building-your-application/routing/internationalization — docs version **16.2.12**, lastUpdated **2025-12-09**. Recommends selecting locale from the incoming **Accept-Language** header using `@formatjs/intl-localematcher` + `negotiator` (example included), then routing by sub-path (`/en-US/products`) or domain, with `app/[lang]` and JSON dictionaries; `generateStaticParams` for static generation. Lists ecosystem resources: next-intl, next-international, next-i18n-router, paraglide-next, lingui, tolgee, next-intlayer, gt-next.
- Pages Router guide (built-in i18n config since v10): https://nextjs.org/docs/pages/building-your-application/routing/internationalization — docs version **16.2.12**, lastUpdated **2026-03-03**. `next.config.js` `i18n: { locales, defaultLocale, domains }`; automatic locale detection from Accept-Language; `localeDetection: false` to disable; `NEXT_LOCALE` cookie takes priority over Accept-Language; sub-path vs domain strategies; UTS-35/Unicode locale identifiers ("Locales are UTS Locale Identifiers… `en-US`… `nl`"); limits: 100 locales, 100 domain items. This page also confirms the "built-in" option is intended to complement libraries (react-intl, react-i18next, lingui, next-intl, next-translate, etc.).
- Caveat: the Pages Router built-in i18n does **not** integrate with `output: 'export'` (static export) per the page.

---

## 8. Indonesian government/consumer expectations on language

**Source: Undang-Undang Nomor 24 Tahun 2009 (UU 24/2009), "Bendera, Bahasa, dan Lambang Negara, serta Lagu Kebangsaan"** — official text
- Primary URL (official regulation database, PDF): https://peraturan.bpk.go.id/Download/27970/UU%20Nomor%2024%20Tahun%202009.pdf (peraturan.bpk.go.id — Badan Pemeriksa Keuangan's official legislation database; the authoritative online copy of the statute).
- Secondary quoting the operative provision (pasal.id summary of UU 24/2009): "Pasal 29… (1) Bahasa INDONESIA wajib digunakan dalam informasi tentang produk barang atau jasa produksi dalam negeri atau luar negeri yang beredar di INDONESIA." (Indonesian must be used in information about goods/service products, domestic or foreign, circulating in Indonesia.)
- Relevance framing (research-only): this is a consumer-information statute about product/service information circulated in Indonesia; it is **not** a web-content or app-localization regulation, and the Indonesian Ministry of Communication rules cited in the brief concern content regulation, not language. It is cited here only because it is the genuine authoritative anchor for the expectation that consumer-facing product/service information in Indonesia be available in Indonesian — an expectation that a localized consumer web app aligns with. Treat as supporting context, not a technical requirement.
- Also note (PRIMARY, Unicode): Indonesian is a fully covered CLDR locale (§4.2) and is a standard locale in `Intl` (MDN example uses `id` as a fallback locale; §4.3), which is the ecosystem-level evidence of expected Indonesian-language localization support.

---

## 9. Gaps, uncertainties, and flags

1. **ISO 216 dimension table not public on iso.org** — the official page (paywalled) does not display the mm table; dimensions corroborated via CEN EN ISO 216:2007 record (iTeh), MDN, Wikipedia (secondary), and library constants. If a strictly-PRIMARY dimension statement is needed, the ISO OBP preview (https://www.iso.org/obp/ui/en/) or purchase of ISO 216:2007 is required (not done; read-only).
2. **ANSI/ASME Y14.1 standard number** — attributed via Wikipedia (secondary); the ANSI/ASME webstore page was not fetched (paywalled). For a hard citation, fetch https://webstore.ansi.org/ (ASME Y14.1) in a later pass.
3. **Country mapping source granularity** — CLDR "latest" charts URL is unversioned; Wikipedia cited CLDR 45 (2024-04-16). At access, TR35/LDML is 48.2 (2026-03-03). If a pinned CLDR version is required for audit reproducibility, fetch https://www.unicode.org/cldr/charts/45/supplemental/territory_information.html (versioned).
4. **Mexico / Philippines / Venezuela / Chile / Colombia / Costa Rica / El Salvador / Guatemala / Nicaragua / Panama / Belize** — CLDR says US-Letter de facto while ISO 216 is the official lineage; a locale→paper policy must therefore prefer the CLDR de facto value, not the nominal standard, for these countries.
5. **F4/Folio (210 × 330 mm)** — documented by Wikipedia (secondary) and Indonesian commercial sources (secondary); no BSN/ISO primary statement found for F4. Treat as market convention, not a standard.
6. **Vercel privacy nuance** — Vercel documents fine-grained headers (city, lat/long, postal code). "Coarse" is a design choice (country/continent), not a platform guarantee; Cloudflare's CF-IPCountry is opt-in via Managed Transform per the current docs.
7. **next-i18next README** — fetched from `master` (moving ref), no SHA pinned; v16 features described may shift.
8. **MDN Intl.DateTimeFormat** — not fetched in full on access date (only Intl.Locale and Intl.NumberFormat were). API shape identical family per ECMA-402; CLDR id data in §4.2 covers the patterns.
9. **RULE NOTE**: This is research evidence only; no implementation decisions are made here.

---

## 10. Source register (all accessed 2026-07-31)

| # | Source | URL | Type | Version/date noted on page |
|---|---|---|---|---|
| 1 | ISO 216:2007 standard page | https://www.iso.org/standard/36631.html | Primary (ISO) | Ed. 2, 2007-09; confirmed 2021; review stage 90.20 opened 2026-07-15 |
| 2 | EN ISO 216:2007 (CEN, via iTeh) | https://standards.iteh.ai/catalog/standards/cen/1627f460-418a-49c5-ad08-968cac6736d4/en-iso-216-2007 | Primary (CEN catalog) | 2007-09-15 |
| 3 | Wikipedia: Paper size | https://en.wikipedia.org/wiki/Paper_size | Secondary | rev oldid=1362341472 |
| 4 | Wikipedia: Letter (paper size) | https://en.wikipedia.org/wiki/Letter_(paper_size) | Secondary | rev oldid=1365157894, 2026-07-20 |
| 5 | CLDR Territory Information | https://www.unicode.org/cldr/charts/latest/supplemental/territory_information.html | Primary (Unicode) | latest release (CLDR 45 cited by Wikipedia for same data, 2024-04-16) |
| 6 | BSN SNI catalog — SNI ISO 216:2010 | https://pesta.bsn.go.id/produk/detail/8160-sniiso2162010 ; listing https://pesta.bsn.go.id/produk/by_ics/10?ics_no=85&key= | Primary (BSN) | SNI ISO 216:2010, Berlaku |
| 7 | AENOR — UNE-EN ISO 216:2008 | https://tienda.aenor.com/p/norma-une-en-iso-216-2008-n0040991 | Primary (UNE catalog) | 2008-04-30, En Vigor |
| 8 | RFC 5646 (BCP 47) | https://www.rfc-editor.org/rfc/rfc5646.html | Primary (IETF) | Sept 2009 |
| 9 | RFC 9110 §12.5.4 Accept-Language | https://www.rfc-editor.org/rfc/rfc9110.html#section-12.5.4 | Primary (IETF) | June 2022 |
| 10 | W3C qa-lang-priorities | https://www.w3.org/International/questions/qa-lang-priorities | Primary (W3C) | living page |
| 11 | UTS #35 LDML | https://unicode.org/reports/tr35/ | Primary (Unicode) | 48.2, 2026-03-03 |
| 12 | CLDR id summary | https://unicode.org/cldr/charts/latest/summary/id.html | Primary (Unicode) | latest release |
| 13 | CLDR Language Plural Rules | https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html | Primary (Unicode) | latest release |
| 14 | MDN Intl.Locale | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Locale | Primary (MDN) | modified 2025-07-22 |
| 15 | MDN Intl.NumberFormat | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat | Primary (MDN) | (fetched via reader; spec ECMAScript 2027 Intl) |
| 16 | Cloudflare HTTP headers | https://developers.cloudflare.com/fundamentals/reference/http-request-headers/ | Primary (vendor docs) | updated 2026-05-05 |
| 17 | Vercel Request headers | https://vercel.com/docs/headers/request-headers | Primary (vendor docs) | last_updated 2025-12-13 |
| 18 | MDN @page | https://developer.mozilla.org/en-US/docs/Web/CSS/@page | Primary (MDN) | modified 2026-04-20 |
| 19 | MDN size descriptor | https://developer.mozilla.org/en-US/docs/Web/CSS/@page/size | Primary (MDN) | modified 2026-04-20 |
| 20 | MDN window.print() | https://developer.mozilla.org/en-US/docs/Web/API/Window/print | Primary (MDN) | modified 2025-11-07 |
| 21 | pdf-lib README + src/api/sizes.ts | https://github.com/Hopding/pdf-lib | Primary (repo) | SHA 93dd36e85aa659a3bca09867d2d8fac172501fbe |
| 22 | jsPDF README + src/jspdf.js + types | https://github.com/parallax/jsPDF | Primary (repo) | SHA a3930ce03a585a26b2c76d12a0f413ce96f6d1a3 |
| 23 | ICU MessageFormat user guide | https://unicode-org.github.io/icu/userguide/format_parse/messages/ | Primary (ICU/Unicode) | current ICU user guide (ICU 78 download era) |
| 24 | next-intl docs | https://next-intl.dev/docs | Primary (library docs) | v3/v4 selector |
| 25 | next-i18next README | https://github.com/i18next/next-i18next | Primary (library repo) | master (v16) |
| 26 | Next.js App Router i18n | https://nextjs.org/docs/app/building-your-application/routing/internationalization | Primary (vendor docs) | docs v16.2.12; lastUpdated 2025-12-09 |
| 27 | Next.js Pages Router i18n | https://nextjs.org/docs/pages/building-your-application/routing/internationalization | Primary (vendor docs) | docs v16.2.12; lastUpdated 2026-03-03 |
| 28 | UU 24/2009 (official PDF) | https://peraturan.bpk.go.id/Download/27970/UU%20Nomor%2024%20Tahun%202009.pdf | Primary (legislation DB) | UU No. 24 Tahun 2009 |
| 29 | pasal.id UU 24/2009 summary (Pasal 29 quote) | https://pasal.id/peraturan/uu/uu-no-24-tahun-2009 | Secondary | — |
| 30 | es.wikipedia ISO 216 (UNE equivalence) | https://es.wikipedia.org/wiki/ISO_216 | Secondary | updated 2025-12-21 |
| 31 | id.wikipedia Ukuran kertas | https://id.wikipedia.org/wiki/Ukuran_kertas | Secondary | — |
| 32 | dinastindopratama.com (Indonesian paper sizes) | https://www.dinastindopratama.com/standard-ukuran-kertas-internasional-iso-kertas-di-indonesia-dan-kertas-di-dunia.html/ | Secondary (commercial) | 2020-09-30 |

---

*End of evidence file. Prepared 2026-07-31. All web access read-only and anonymous. `papyr-reference/` untouched.*
