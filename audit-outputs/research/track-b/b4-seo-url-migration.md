# B4 - SEO, Slugs, and Legacy URL Migration

## 1. Header

- **Brief ID**: B4
- **Path**: `<workspace-root>\audit-outputs\research\track-b\b4-seo-url-migration.md`
- **Track**: B - Frontend, capability, and SEO research
- **Title**: SEO, slugs, and legacy URL migration research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (executor subagent, Track B)
- **Status**: Draft (complete for owner review under DEC-057; findings are recommendations, not accepted decisions)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (deliverable B4 at §6.2; Track B questions §7.2; brief template §8; verification §11)
- **Governing decisions**: DEC-023, DEC-047, DEC-099, DEC-114, DEC-122, DEC-127 (primary); supporting DEC-026, DEC-044, DEC-048, DEC-121, DEC-124, DEC-140, DEC-153, DEC-184, DEC-188, DEC-054 through DEC-060, DEC-066
- **Spec sections served**: Product and UX Design Specification §8.2 (lines 131-157), §19 (SEO and content migration constraints, lines 612-623), §21.4 (line 702), §20.1 item 7 (line 637); Technical Architecture Specification §4.2 (lines 213-219), §6.4 (line 320), §25.3.15-16 (lines 1075-1076)
- **Files read**:
  - `<workspace-root>\AGENTS.md`
  - `<workspace-root>\audit-outputs\research-program-plan.md`
  - `<workspace-root>\papyr-rebuild-decisions.md` (DEC-001 through DEC-188, Open decisions)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (§8, §19, §20, §21)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (§4, §6, §11, §25.3)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-b4-web.md` (Google Search Central, RFC, sitemaps.org evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-decisions.md` (decision-log extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-specs.md` (spec extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-legacy-frontend.md` (§1 route inventory, §4 sitemap, §5 robots, §7 next.config, §12 URL evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-ui-audits.md` (§9.3 SEO findings)
  - Legacy (read-only): `papyr-reference/frontend/src/app/sitemap.ts`, `robots.ts`, `next.config.ts`, `layout.tsx`, all `src/app/*/layout.tsx` metadata files (per `_evidence-legacy-frontend.md` §1, §4, §5, §7)
- **Template note**: The plan §8 lists 12 numbered sections. The header sub-fields above are expanded as their own labeled fields; combined with the 12 numbered sections this satisfies both the plan's template and the 16-section instruction for Track B briefs (header sub-fields counted individually), following the Track A A1 precedent.

---

## 2. Scope

This brief resolves the SEO, localized-slug, and legacy URL migration research for the rebuild. It covers:

- **Localized slugs for EN/ES/ID** for the five tools and the essential supporting surfaces, selected during SEO design (UX §21.4), under the locale-prefix rule (DEC-023) and the translated-Indonesian-slug rule (DEC-122).
- **The complete legacy URL inventory** with an explicit retain/update, redirect, noindex, or removal disposition for every URL (DEC-127), reconciled with the retention policy (DEC-114) and the archive policy (DEC-099).
- **The legacy URL redirect map** and its mechanics (301 versus 302, chains, retention, monitoring), following Google's documented site-move process and Bing guidance.
- **hreflang, canonical, sitemap, and locale-less redirect requirements** (DEC-023, DEC-047), with the primary-source rules for each.

The user problem served: existing search visibility and useful legacy intent are assets to preserve (DEC-114), while the domain must serve only the rebuilt product after relaunch (DEC-099) with no soft 404s, no redirect chains, no duplicate indexing, and no lost equity (DEC-127, UX §20.1 item 7).

The current approved Papyr behavior this brief must support: every localized route carries an explicit locale prefix including English (DEC-023); English does not use unprefixed tool routes as canonical URLs (DEC-023); Indonesian URLs use translated, search-appropriate slugs under `/id/` (DEC-122); locale-less entry redirects once by supported browser language with a persistent manual override (DEC-047); the complete legacy sitemap and indexable URL inventory is audited before relaunch with explicit dispositions (DEC-127); the domain serves only the rebuilt product after relaunch (DEC-099); the relaunch is direct activation without a campaign but with a coordinated activation checklist covering deployment, redirects, and indexing (DEC-140); tool-page SEO content is concise and intent-aligned with a supporting blog (DEC-044).

## 3. Non-goals

- No launch blog topic selection or post-launch topic pipeline: owned by Track E3 (DEC-052, DEC-053, DEC-121, DEC-124). This brief covers the blog URL structures (`<locale>/blog`, `<locale>/blog/<slug>`) and blog SEO constraints (DEC-044, UX §19 item 8) only.
- No analytics event-schema design: owned by Track D3 (DEC-025).
- No Adsterra interaction with SEO: owned by Track D1 (DEC-005, DEC-018).
- No copywriting of metadata titles or descriptions: the specs require per-locale metadata (UX §19 item 1, §11.1 item 4); the copy itself is a UX/content task. This brief fixes the URL, slug, and tag structures the copy must fill.
- No implementation of redirects, middleware, or sitemap generation: design input only, per DEC-060.
- No benchmark program or comparative SEO study (DEC-066).

## 4. Research questions

Restated from plan §7.2 (B4):

1. What are the recommended EN/ES/ID slugs for the five tools and the essential supporting pages, given DEC-023 (locale prefixes) and DEC-122 (translated Indonesian slugs)?
2. What is the complete legacy URL inventory, and what explicit disposition (retain/update, redirect, noindex, or removal) does each URL receive per DEC-127, DEC-114, and DEC-099?
3. What are the redirect-map mechanics (status codes, chains, retention period, monitoring) per the primary-source guidance?
4. What are the hreflang, canonical, sitemap, and locale-less redirect requirements (DEC-023, DEC-047), and which standards/values do they mandate?
5. How does the migration avoid soft 404s, redirect chains, duplicate indexing, and unpredictable crawler behavior (UX §20.1 item 7; DEC-047)?
6. What are the interfaces to B3 (locale facts) and the implementation-time verification?

## 5. Evidence

### 5.1 Approved decisions

Source: `<workspace-root>\papyr-rebuild-decisions.md` (verbatim in `_evidence-decisions.md` §2, with line ranges).

| Decision | Source lines | SEO/URL content (exact text) |
|---|---|---|
| DEC-023 | 292-302 | "Use an explicit locale prefix for every localized route, including English and Spanish"; "English does not use unprefixed tool routes as canonical URLs"; localized tool slugs, metadata, structured data, internal links, sitemaps, canonicals, and hreflang generated consistently per locale; requests without a locale require a documented redirect or locale-selection policy that avoids redirect loops and SEO duplication; "Legacy unprefixed URLs require a deliberate redirect map to preserve useful backlinks and search equity where applicable." |
| DEC-047 | 584-594 | Locale-less entry redirects once according to supported browser-language preferences; persistent manual language switcher takes precedence; unsupported languages fall back to English; "Search crawlers, shared URLs, locale-prefixed routes, and canonical/hreflang behavior must not be redirected unpredictably"; "Redirect status, caching, and middleware behavior require SEO testing to avoid loops, duplicate indexing, or incorrect geo-language assumptions." |
| DEC-099 | 1205-1215 | After relaunch the existing domain serves only the rebuilt product; the legacy application is preserved as source/history and is not exposed through a public legacy subdomain; "Important legacy URLs require intentional redirects or replacement responses under the localized URL strategy." |
| DEC-114 | 1374-1384 | Legacy public pages or articles still receiving meaningful traffic are retained and updated rather than discarded; each retained page audited for factual accuracy, product alignment, language, search intent, duplication, and policy consistency; retention does not permit stale instructions, unavailable features, obsolete claims, or duplicate pages; URL, localization, canonical, and redirect treatment defined during SEO design, especially for legacy Indonesian pages; pages without continuing value may be redirected or retired through an explicit content-mapping decision. |
| DEC-122 | 1463-1472 | Indonesian tool and content URLs use translated, search-appropriate slugs under `/id/` rather than reusing English slugs by default; slugs use natural, stable terminology selected during SEO design; legacy Indonesian URLs require an explicit mapping to retained localized URLs, with redirects where paths change; EN and ES retain their own localized slug policies; all locale alternates remain connected through hreflang and canonicals. |
| DEC-127 | 1517-1526 | Audit the full legacy sitemap and indexable URL inventory before relaunch, not only pages known to receive traffic; every legacy public URL receives an explicit retain/update, redirect, noindex, or removal disposition; the audit reconciles locale mappings, canonicals, hreflang, sitemap inclusion, internal links, and DEC-114; removal avoids unnecessary soft 404s and redirect chains; retained pages meet current content and policy standards. |

Supporting: DEC-026 (legacy documents labeled as historical/archive), DEC-044 (tool-page SEO + blog), DEC-140 (direct activation with a coordinated activation checklist covering deployment, redirects, and indexing), DEC-153 (processing and results stay on one page; no redirect to a result URL), DEC-121/DEC-124 (trilingual blog content with cross-locale metadata, hreflang, canonicals, and update tracking).

### 5.2 Specification requirements

Source: `_evidence-specs.md` §2.8 (UX §19 in full), §2.6 (UX §8.2, §9), §3.2 (arch §4.2), §3.10 (arch §6.4, §11.1), §4.1-4.2 (open-item register).

- UX §8.2 route table (lines 135-150): the fixed EN slugs are `/en/compress-pdf`, `/en/merge-pdf`, `/en/split-pdf`, `/en/jpg-to-pdf`, `/en/pdf-to-jpg`, `/en/privacy`, `/en/terms`, `/en/cookies-advertising`, `/en/contact`; the spec leaves the ES and ID slug values open (shown as `<slug>` tokens) for selection during SEO design (UX §21.4). Supporting surfaces: `<locale>/status`, `<locale>/roadmap`, `<locale>/blog`, `<locale>/blog/<slug>`.
- UX §8.2 notes (lines 154-156): exact slugs selected during SEO design (Section 19); ID uses translated slugs (DEC-122); locale-less entry per DEC-047; legacy unprefixed URLs require a deliberate redirect map (DEC-023, DEC-099, DEC-127); tool pages stay available during backend outages with no redirect to the status page (DEC-163).
- UX §19 items 1-10 (lines 614-623): locale-prefixed routes with consistent per-locale slugs, metadata, structured data, internal links, sitemaps, canonicals, hreflang (item 1); locale-less entry without unpredictable crawler behavior (item 2); complete legacy URL inventory with explicit dispositions (item 3); legacy archive with intentional redirects (item 4); Indonesian preservation and coverage reconciliation (item 5); tool-page transactional intent (item 6); no competitor pages (item 7); blog SEO with 15 launch articles and daily cadence (item 8); no launch campaign, coordinated activation checklist (item 9); no public counters (item 10).
- UX §20.1 item 7 (line 637): "Full legacy URL inventory has explicit dispositions with no soft 404s or redirect chains (DEC-127)."
- UX §11.1 item 4 (line 293): metadata uses locale-aware defaults with `metadataBase https://mypapyr.com`; the legacy Indonesian-only default title is replaced by localized international copy (DEC-003).
- Arch §4.2 (lines 213-219): locale-prefixed routes with a deliberate redirect map for legacy unprefixed routes (DEC-023); Indonesian translated slugs under `/id/` (DEC-122); locale-less entry once with manual override (DEC-047); "Locale resolution must avoid redirect loops, unpredictable crawler behavior, and SEO duplication"; "Canonical URLs, hreflang, sitemaps, and internal links are generated consistently per locale."
- Arch §6.4 (line 320): the rebuild API uses `/api/v1`; "Legacy routes require an explicit migration or retirement disposition and must not remain accidentally active (DEC-164)."

### 5.3 Legacy URL inventory (evidence)

Source: `_evidence-legacy-frontend.md` §1, §4, §5, §7, §12.

**The complete legacy sitemap and indexable URL inventory** (16 URLs, from `frontend/src/app/sitemap.ts:21-47`; also covered by `seo-analytics.test.ts:47-64`):

| # | Legacy URL | Content | Priority/change frequency (legacy) |
|---|---|---|---|
| 1 | `https://mypapyr.com/` | Homepage (Indonesian) | 1 / weekly |
| 2 | `/compress` | Compress PDF (launch tool) | 0.8 / monthly |
| 3 | `/merge` | Merge PDF (launch tool) | 0.8 / monthly |
| 4 | `/split` | Split PDF (launch tool) | 0.8 / monthly |
| 5 | `/image-to-pdf` | JPG to PDF (launch tool) | 0.8 / monthly |
| 6 | `/pdf-to-image` | PDF to JPG (launch tool) | 0.8 / monthly |
| 7 | `/rotate` | Rotate PDF (deferred, DEC-094) | 0.8 / monthly |
| 8 | `/protect` | Protect PDF (deferred) | 0.8 / monthly |
| 9 | `/unlock` | Unlock PDF (deferred) | 0.8 / monthly |
| 10 | `/watermark` | Watermark PDF (deferred) | 0.8 / monthly |
| 11 | `/sign` | Sign PDF (deferred) | 0.8 / monthly |
| 12 | `/pdf-to-word` | PDF to Word (deferred) | 0.8 / monthly |
| 13 | `/ocr` | OCR (deferred) | 0.8 / monthly |
| 14 | `/pdf-to-excel` | PDF to Excel (deferred) | 0.8 / monthly |
| 15 | `/faq` | FAQ (Indonesian) | 0.5 / monthly |
| 16 | `/privacy` | Privacy (Indonesian) | 0.3 / yearly |

Additional inventory facts from the evidence:

- The legacy `next.config.ts` (7 lines, quoted in full in `_evidence-legacy-frontend.md` §7) has **no redirects, rewrites, or headers**; there is no legacy redirect logic to port. The URL migration must be designed fresh.
- The legacy `robots.ts` is a single catch-all (`allow: '/'`) with `sitemap: https://mypapyr.com/sitemap.xml` (evidence §4-5).
- Metadata evidence per route (evidence §1): all tool pages are client components with Indonesian titles/descriptions and per-tool OG images; only 7 of 15 routes set an `openGraph.url`; `/privacy` has no OG block; metadata quirks are documented there.
- Footer dead links `Syarat` (`#`) and `Kontak` (`#`) with no `/terms` or `/contact` routes (evidence §9.3; defect D1); `/faq` and `/privacy` are the only non-tool content pages; there is **no legacy blog**, no `/terms`, no `/contact`, no `/status`, no `/roadmap`.
- Domains: `mypapyr.com` (frontend), `www.mypapyr.com` (in the backend CORS allowlist only), `api.mypapyr.com` (backend API, nginx, Cloudflare-proxied). The frontend has no `www` redirect evidence; Google guidance requires verifying all variants (evidence §5.4 below).
- Legacy API routes (evidence §12.5): `/api/compress`, `/api/image-to-pdf`, `/api/pdf-to-image`, `/api/protect`, `/api/unlock`, `/api/watermark`, `/api/pdf-to-word`, `/api/ocr`, `/api/pdf-to-excel`, `/api/status/{task_id}`; the rebuild API is `/api/v1` (DEC-164) and these legacy API paths need a retirement disposition per arch §6.4 (they are not indexable public pages, but they must not remain accidentally active).

### 5.4 Primary web sources: Google Search Central, sitemaps.org, IETF

Source: `_evidence-b4-web.md` (all URLs accessed 2026-07-31; page "Last updated" stamps recorded in the evidence source inventory).

- **URL structure options** (S1, "Managing Multi-Regional and Multilingual Sites", updated 2025-12-10): four documented options; subdirectories with gTLD (`example.com/de/`) are presented as easy and low-maintenance; URL parameters are "Not recommended"; "Google recommends using different URLs for each language version of a page rather than using cookies or browser settings"; use `hreflang` when URLs differ per language; "Do not automatically redirect users between language versions" (i.e., the pages must remain directly reachable); localized words in URLs are fine with UTF-8 encoding; when the same content exists in the same language at multiple URLs, pick a preferred version with `rel="canonical"` plus `hreflang`.
- **hreflang** (S2, "Tell Google about localized versions of your page"): three equivalent methods (HTML `<link rel="alternate" hreflang>` in `<head>`, HTTP `Link` headers, sitemap `xhtml:link` children); each version lists itself and all others (self-referencing); sets must be bidirectional ("If two pages don't both point to each other, the tags will be ignored"); language code is ISO 639-1 with optional ISO 3166-1 Alpha 2 region; "Other codes such as `es-419` are NOT supported"; `x-default` is the reserved fallback; alternate URLs must be fully qualified (`https://...`); localized pages are duplicates only if the main content is untranslated.
- **Canonicalization** (S3 updated 2026-07-10; S4): canonical selection signals are a "hint, not a rule"; influence ranking: redirects > `rel="canonical"` link annotations > sitemap inclusion; use absolute URLs; self-referential canonicals are recommended ("Do include a `rel='canonical'` link on the canonical page itself"); `rel="canonical"` annotations with `hreflang`, `lang`, `media`, or `type` attributes are ignored for canonicalization; with hreflang, specify a canonical page in the same language or the best substitute; "Prefer URLs in `hreflang` clusters"; RFC 6596 (April 2012) defines the canonical link relation; the Link header form is defined by RFC 8288 (October 2017, obsoletes RFC 5988; Google's docs still cite RFC 5988, a documented drift in evidence §9.3).
- **Redirects and site moves** (S6 updated 2026-04-14; S7 updated 2026-06-17): permanent redirects (301, 308) are followed and used as canonical signals; temporary redirects (302, 303, 307) are followed but not used as canonical signals; the documented migration process includes "Prepare a URL mapping from current URLs to corresponding new format", server-side permanent redirects, and Search Console verification of all variants of both old and new sites; "Avoid chaining redirects... we advise redirecting to the final destination directly. If this is not possible, keep the number of redirects in the chain low, ideally no more than 3 and fewer than 5"; keep redirects "for as long as possible, generally at least 1 year"; update internal links, self-referencing canonicals, and hreflang annotations to new URLs; submit the new sitemap and remove the old one; deleted or merged content returns HTTP 404 or 410; "Don't worry about link credit. `301` and other permanent redirects don't cause a loss in PageRank."
- **noindex and robots.txt** (S8 updated 2025-12-10; S9): `noindex` via `<meta name="robots">` or `X-Robots-Tag`; "Specifying the `noindex` rule in the robots.txt file is not supported by Google"; the page must not be blocked by robots.txt or the crawler never sees the `noindex` rule; robots.txt "is not a mechanism for keeping a web page out of Google".
- **Sitemaps** (S12, sitemaps.org protocol 0.9, page last updated 2016-11-21; S11 updated 2026-07-08): max 50,000 URLs and 50 MB per sitemap; `<loc>` less than 2,048 characters beginning with the protocol; `<lastmod>` "must be set to the date the linked page was last modified, not when the sitemap is generated"; "Google ignores `<priority>` and `<changefreq>` values"; fully qualified absolute URLs; sitemap hreflang annotations per S2; submission via Search Console or the `Sitemap:` directive in robots.txt.
- **Bing Webmaster Guidelines** (S15): use 301 redirects for permanent changes; 302 only for short-term changes (less than 2 days); use redirects instead of canonical tags for URL moves; sitemaps list only canonical URLs and remove deleted or redirected URLs promptly; use NOINDEX when a URL should not appear; return 404 for removed content; "Preserve URL Stability Over Time. Avoid unnecessary URL changes."
- **Google dead URLs observed** (evidence §9.1): the old `.../crawling-indexing/international/multi-regional-multilingual-sites` and `localized-versions` URLs return 404; current URLs are under `/search/docs/specialty/international/`. Any older Papyr materials referencing the old URLs should be updated.

## 6. Alternatives

### Slug strategy

**Alternative A - Fully localized slugs per locale (recommended)**

- **What it is**: every locale has its own natural slugs (EN `compress-pdf`, ES `comprimir-pdf`, ID `kompres-pdf`, and so on), connected by hreflang and per-locale canonicals.
- **Trade-offs**: matches DEC-122 (translated ID slugs), DEC-023 (consistent per-locale slugs/metadata), and Google's "Use your audience's language" URL guidance (S5, evidence §5.4); search-fit for ES and ID markets (DEC-104 regions, DEC-003). Cost: three slug tables to maintain and test; hreflang/canonical correctness becomes a launch gate (DEC-023).
- **Risks**: slug drift between locales; mitigated by one canonical catalog feeding slugs (arch §11.1 line 508) and by tests.
- **Verdict**: required by the accepted decisions; not really optional.

**Alternative B - English-only slugs under each locale prefix**

- **What it is**: `/es/compress-pdf`, `/id/compress-pdf`.
- **Trade-offs**: simpler; but contradicts DEC-122's translated-slug requirement for Indonesian, weakens ES/ID search intent, and keeps the legacy English-derived naming that the Indonesian market already avoided (`image-to-pdf` slug with Indonesian content).
- **Verdict**: rejected.

**Alternative C - Numeric or ID-based URLs**

- **What it is**: `/en/tool/5`.
- **Trade-offs**: violates Google's "use readable words rather than long ID numbers" guidance (S5) and harms user comprehension.
- **Verdict**: rejected.

### Legacy redirect strategy

**Alternative A - Direct mapping of legacy Indonesian URLs to their `/id/` counterparts, plus 301 (recommended)**

- **What it is**: every legacy URL whose content was Indonesian maps to the corresponding new `/id/<slug>` page (e.g., `/compress` -> `/id/kompres-pdf`), served as a permanent 301/308 redirect, with the ID pages hreflang-connected to their EN and ES alternates. The legacy root `/` maps to the locale-less entry behavior (DEC-047) since it is the site root.
- **Trade-offs**: preserves the Indonesian search equity deterministically (the legacy content was 100% Indonesian, evidence §5.3); keeps one direct hop per URL (no chains); the ID pages are first-class launch pages (DEC-118), so the redirect targets are live and complete. Cost: the ID slug set must be finalized before the map is written.
- **Risks**: a non-Indonesian visitor clicking an old link lands on the ID page rather than a detected locale; acceptable because the historical content was Indonesian, and the ID page's hreflang set lets users switch (DEC-149).
- **Verdict**: recommended.

**Alternative B - Route all legacy URLs through locale detection (Accept-Language)**

- **What it is**: every legacy unprefixed URL runs the DEC-047 detection redirect instead of a fixed target.
- **Trade-offs**: arguably better per-visitor language matching; but DEC-047's consequences demand crawler-safe, non-unpredictable behavior, and Google treats detection redirects as non-deterministic ("Do not automatically redirect users between language versions"; S1), making a permanent redirect target a moving canonical problem. It also loses the direct mapping DEC-127 expects ("an explicit mapping to retained localized URLs").
- **Risks**: redirect loops, duplicated crawling, unpredictable canonical/hreflang behavior, the exact failures DEC-047 and DEC-023 forbid.
- **Verdict**: rejected for tool URLs; retained only for the site root and other genuinely locale-agnostic entry points.

**Alternative C - Keep legacy URLs live alongside the rebuild**

- **What it is**: serve the old Indonesian pages at their old paths after relaunch.
- **Trade-offs**: violates DEC-099 (domain serves only the rebuilt product), DEC-023 (English does not use unprefixed canonical URLs; every localized route carries a locale prefix), and DEC-114 (no duplicate pages competing with canonical EN/ES content).
- **Verdict**: rejected.

### Redirect status for locale-less entry

- **301 versus 302 for DEC-047 detection**: Google documents that temporary redirects (302/303/307) are followed but not used as canonical signals, while permanent redirects are canonical signals (evidence §5.4). For locale-detection entry, a permanent 301 would pin crawlers to one target, which conflicts with "Search crawlers... must not be redirected unpredictably" (DEC-047). Recommendation: use a temporary redirect (302/307) for the locale-less entry redirect so crawlers do not treat the detection target as the canonical, and use permanent 301/308 only for the legacy URL map. This is a recommendation to confirm in SEO testing per DEC-047's consequence.

### Disposition for deferred legacy tools

- The eight deferred tool URLs (`/rotate`, `/protect`, `/unlock`, `/watermark`, `/sign`, `/pdf-to-word`, `/ocr`, `/pdf-to-excel`) are not launch scope (DEC-094: return gradually after launch). Options:
  1. **301 to the closest launched surface**: preserves some equity; risk of misleading users when the target does not perform the same function (e.g., `/watermark` has no launch counterpart).
  2. **410 Gone (or 404)**: honest, matches Google's guidance for removed content (S7: "return HTTP 404 or 410 for URLs not moved"); the map is updated when each tool relaunches under DEC-094. 410 is preferred over 404 because the resource is intentionally gone, not missing.
  3. **A "returns later" page with noindex**: violates DEC-114's no-stale-content and the no-coming-soon navigation rule (UX §8.3); fragile.
- Recommendation: **410 Gone** for the eight deferred tools at relaunch, with the redirect map updated per tool when each relaunches (DEC-094), and each disposition recorded in the URL-inventory table. The owner should confirm whether any deferred URL is currently attracting meaningful traffic (DEC-114) that would justify a different treatment.

## 7. Recommendation

Recommendation only, not an accepted decision (DEC-054, DEC-057): adopt **localized slugs (Alternative A)**, the **direct legacy-to-`/id/` redirect map with 301** (Alternative A), **302/307 for the locale-less entry redirect**, and the **410 disposition for deferred tools**, per the following tables. The exact slugs remain subject to SEO design and owner approval (UX §21.4); the values below are the recommended selection.

### 7.1 Recommended slug table (EN fixed by the spec; ES/ID recommended)

| Surface | EN (UX §8.2, fixed) | ES (recommended) | ID (recommended) |
|---|---|---|---|
| Homepage | `/en/` | `/es/` | `/id/` |
| Compress PDF | `/en/compress-pdf` | `/es/comprimir-pdf` | `/id/kompres-pdf` |
| Merge PDF | `/en/merge-pdf` | `/es/combinar-pdf` | `/id/gabungkan-pdf` |
| Split PDF | `/en/split-pdf` | `/es/dividir-pdf` | `/id/pisahkan-pdf` |
| JPG to PDF | `/en/jpg-to-pdf` | `/es/jpg-a-pdf` | `/id/gambar-ke-pdf` |
| PDF to JPG | `/en/pdf-to-jpg` | `/es/pdf-a-jpg` | `/id/pdf-ke-gambar` |
| Privacy | `/en/privacy` | `/es/privacidad` | `/id/privasi` |
| Terms | `/en/terms` | `/es/terminos` | `/id/ketentuan` |
| Cookies/Advertising | `/en/cookies-advertising` | `/es/cookies-publicidad` | `/id/cookie-iklan` |
| Contact/Support | `/en/contact` | `/es/contacto` | `/id/kontak` |
| Status | `/en/status` | `/es/estado` | `/id/status` |
| Roadmap | `/en/roadmap` | `/es/hoja-de-ruta` | `/id/roadmap` |
| Blog index | `/en/blog` | `/es/blog` | `/id/blog` |
| Blog article | `/en/blog/<slug>` | `/es/blog/<slug>` | `/id/blog/<slug>` |

Slug notes: ID slugs follow the legacy Indonesian tool names (the rebuild keeps the English product name "JPG to PDF" per DEC-187 while the ID slug uses the natural Indonesian "gambar-ke-pdf", matching the legacy content language); all slugs use lowercase ASCII with hyphens per Google's URL guidance (S5); no `es-419` or other non-ISO values anywhere (S2).

### 7.2 Legacy URL disposition table (recommended)

| Legacy URL | Disposition | Target | Status |
|---|---|---|---|
| `/` (root) | Locale-less entry redirect (DEC-047) | Detection with manual override; not a fixed canonical target | 302/307 |
| `/compress` | Redirect | `/id/kompres-pdf` | 301 |
| `/merge` | Redirect | `/id/gabungkan-pdf` | 301 |
| `/split` | Redirect | `/id/pisahkan-pdf` | 301 |
| `/image-to-pdf` | Redirect | `/id/gambar-ke-pdf` | 301 |
| `/pdf-to-image` | Redirect | `/id/pdf-ke-gambar` | 301 |
| `/faq` | Retain/update | New `/id/faq` page (content updated and policy-checked per DEC-114) | live |
| `/privacy` | Retain/update | `/id/privasi` (re-scoped copy per DEC-045, DEC-168, UX §21.17) | live |
| `/rotate` | Removal | 410 Gone; map updated when the tool relaunches (DEC-094) | 410 |
| `/protect` | Removal | 410 Gone | 410 |
| `/unlock` | Removal | 410 Gone | 410 |
| `/watermark` | Removal | 410 Gone | 410 |
| `/sign` | Removal | 410 Gone | 410 |
| `/pdf-to-word` | Removal | 410 Gone | 410 |
| `/ocr` | Removal | 410 Gone | 410 |
| `/pdf-to-excel` | Removal | 410 Gone | 410 |
| Legacy API paths (`/api/*`, `/api/status/{id}`) | Retirement | Superseded by `/api/v1` (DEC-164); must not remain accidentally active (arch §6.4) | n/a (non-indexable) |

Every entry records its disposition in the URL-inventory table that the implementation plan must carry forward, per DEC-127 ("Every legacy public URL must receive an explicit retain/update, redirect, noindex, or removal disposition").

### 7.3 hreflang, canonical, sitemap, and locale-less rules

1. **hreflang**: per page, a bidirectional set listing every locale alternate including itself, in `<head>` (or sitemap `xhtml:link`, or HTTP `Link` headers; one method is sufficient, S2). Values are ISO 639-1 language with optional ISO 3166-1 Alpha 2 region; no `es-419` (S2). Fully qualified absolute URLs only. `x-default` points to the EN version (the unsupported-language fallback, DEC-047).
2. **Canonical**: every page carries a self-referencing `rel="canonical"` with an absolute URL (S4); the canonical is always the locale-prefixed page in the same language (never an unprefixed EN route, DEC-023); hreflang-cluster URLs are preferred as canonicals (S4). Blog and tool pages generate canonicals from the same canonical catalog (arch §11.1 line 508).
3. **Sitemap**: one sitemap covering the live locale-prefixed URLs with per-URL hreflang alternates (S2 method 3), fully qualified, `<lastmod>` reflecting real page modification dates (S12/S11), no redirecting or removed legacy URLs (S15); the sitemap is replaced at relaunch (old sitemap removed, new sitemap submitted, S7). Size limits (50,000 URLs / 50 MB) are far above the launch inventory.
4. **robots.txt**: catch-all allow plus the `Sitemap:` line (legacy precedent retained); `noindex` is never expressed in robots.txt (S8); any page needing removal uses `noindex` meta/X-Robots-Tag or true 404/410.
5. **Locale-less entry**: one redirect per DEC-047 using a temporary status (302/307) so crawlers do not pin a canonical to the detection target; manual override remembered with minimal non-sensitive storage; unsupported languages fall back to EN; no redirect loops (DEC-047). The site root participates in this path; all other URLs are canonicalized to locale-prefixed forms.
6. **Metadata**: per-locale title, description, OG, and Twitter metadata with `metadataBase https://mypapyr.com` (UX §11.1 item 4), generated from the canonical catalog; structured data consistent per locale (DEC-023).
7. **Migration hygiene**: no soft 404s, no chains beyond 3 (ideally none: each legacy URL redirects directly to its final target), redirects kept at least one year, internal links and sitemaps updated, both site variants verified in Search Console (S7, UX §20.1 item 7). The `www.mypapyr.com` variant exists in the legacy CORS allowlist; canonicalization of `www` vs non-`www` must be verified during implementation (S7 variant guidance).
8. **Blog**: `<locale>/blog` and `<locale>/blog/<slug>` structures; 15 launch articles (five topics x three locales) with cross-locale hreflang, canonicals, internal links, and update tracking (DEC-121); truthful publication and update dates (DEC-113).

## 8. Measurable acceptance criteria

Functional verification criteria, with no benchmark wording (DEC-066):

1. **Complete disposition table**: every legacy URL from the §5.3 inventory appears in the implementation's URL-inventory table with exactly one of retain/update, redirect, noindex, or removal (DEC-127).
2. **No soft 404s**: a functional test walks the legacy URL list and asserts each returns 301/308 (redirect), 200 (retained), or 404/410 (removed), never a 200 page that is not the intended content (UX §20.1 item 7).
3. **No redirect chains**: each legacy redirect targets a final live URL directly; a test asserts zero chains (S7).
4. **Slug correctness**: the live routes match the approved slug table; EN slugs match the spec's fixed values (UX §8.2); ID slugs are translated and search-appropriate (DEC-122).
5. **hreflang integrity**: a test walks every localized page and asserts the hreflang set is bidirectional, includes self, uses only ISO 639-1 + ISO 3166-1 Alpha 2 values (no `es-419`), uses fully qualified URLs, and includes `x-default` on the entry set (S2).
6. **Canonical integrity**: every page emits a self-referencing absolute canonical in the same language as the page; no page canonicalizes to an unprefixed URL (DEC-023, S4).
7. **Sitemap hygiene**: the sitemap contains only live locale-prefixed canonical URLs with correct `<lastmod>` and hreflang alternates; it contains no legacy or redirecting URLs (S12, S15).
8. **Locale-less entry**: the entry redirect is temporary (302/307), single-hop, loop-free, honors the manual override, and falls back to EN (DEC-047); crawler behavior is verified in SEO testing per DEC-047's consequence.
9. **No accidental legacy surfaces**: the legacy API paths are not reachable under the rebuild (DEC-164, arch §6.4); the legacy app is not served on any public subdomain (DEC-099).
10. **Retention**: redirects remain in place for at least one year after relaunch with monitoring of indexing transfer (S7); the coordinated activation checklist covers deployment, redirects, and indexing (DEC-140).
11. **No benchmarks**: the migration plan contains no comparative quality/performance study, corpus, matrix, or score program (DEC-066).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Legacy traffic data unavailable in research**: the decision log records that legacy pages "still receive meaningful traffic" (DEC-114) should be retained, but no traffic data was available to this read-only research (no analytics access, no production access, DEC-160/172). The disposition table assumes the legacy inventory per the sitemap; the owner's traffic knowledge should confirm whether any deferred tool URL deserves a redirect instead of 410 (DEC-114).
2. **Search Console verification is a launch-time action**: verifying both properties and submitting the Change of Address (S7) happens at implementation/relaunch, not research; recorded as a checklist item.
3. **`www` variant canonicalization**: the legacy backend allowlist includes `www.mypapyr.com`; no frontend `www` redirect evidence exists; the final `www` vs non-`www` canonical decision is an implementation detail to verify (S7 variant guidance).
4. **Google doc drift**: Google's canonical docs still cite RFC 5988 for the Link header, obsoleted by RFC 8288 (evidence §9.3); the brief cites RFC 8288 as current and records the drift.
5. **Old Google international URLs are dead**: any older Papyr materials referencing `.../crawling-indexing/international/...` should be updated to `/search/docs/specialty/international/` (evidence §9.1).
6. **Slug recommendations are not decisions**: UX §21.4 defers exact slug selection to SEO design; the §7.1 table is the recommended selection, and the owner (or SEO design) may adjust wording while keeping the structure (DEC-023, DEC-122).
7. **No indexable legacy blog exists**: the legacy inventory has no blog, terms, contact, status, or roadmap URLs; those surfaces are new, so no legacy equity transfer applies to them.
8. **Robots and OG metadata quirks**: the legacy per-tool OG images and metadata are Indonesian-only; the rebuild generates per-locale metadata from the catalog (UX §11.1 item 4); the old static `/og/*.png` assets are legacy content under DEC-114/DEC-026 handling.
9. **Material owner questions**: (a) confirmation of the §7.1 slug selection (or the owner's preferred wording); (b) the deferred-tool disposition: 410 Gone (recommended) versus targeted redirects for any URL the owner knows still attracts traffic; (c) acceptance of the 302/307 temporary status for the locale-less entry redirect versus a permanent 301 to EN.
10. **hreflang `x-default` target**: the EN version is the recommended `x-default` (unsupported languages fall back to EN, DEC-047); confirm this choice.

## 10. Dependencies and cross-track interfaces

- **B3 (i18n, locale, paper policy)**: supplies the locale set (en/es/id), the language-tag facts (RFC 5646; no `es-419` in hreflang), and the `<html lang>` per-page requirement; B4 supplies the route structure B3's locale detection must serve.
- **B1 (browser routing)**: no interaction with routing; results stay on one page with no redirect (DEC-153), so the URL migration never affects the tool flow.
- **B2 (accessibility)**: per-locale `<html lang>` is an accessibility requirement (SC 3.1.1) and a launch gate (DEC-118); the language switcher behavior (DEC-149) interacts with the locale-less entry override.
- **D2 (legal and privacy copy)**: the new `/id/privasi`, `/es/privacidad`, `/en/privacy`, terms, and cookies pages (DEC-045) must exist before the redirect map targets them; the legacy `/privacy` URL maps to the re-scoped ID privacy page (UX §21.17).
- **Track E (blog)**: blog URL structures and hreflang/canonical rules apply to the 15 launch articles (DEC-121, DEC-124); E3 owns the topics.
- **Arch §22.2 (E2E tests)**: the migration hygiene checks in §8 (dispositions, chains, hreflang, canonical, sitemap) become part of the EN/ES/ID end-to-end verification (arch line 941).
- **X1/X2 (index/reconciliation)**: this brief contributes the slug table, the disposition table, the 302-vs-301 entry decision, and the owner questions in §9.9 to the reconciliation decision prompts (plan §14).

## 11. Source-date log and evidence-completeness notes

- All web sources accessed 2026-07-31; page "Last updated" stamps recorded in `_evidence-b4-web.md` (S1/S3/S5/S6/S7/S8/S10/S11 stamps captured; S2/S4/S9 footers not captured and stated as such; sitemaps.org protocol page dated 2016-11-21; RFC 6596 April 2012; RFC 8288 October 2017).
- Legacy evidence read 2026-07-31; all paths under `papyr-reference/`; line references cited in §5.3.
- Completeness notes: (a) the legacy inventory is bounded by the legacy sitemap and route listing (16 indexable URLs plus the API paths); a full server-log or Search Console crawl beyond that was not possible in read-only research (no production access, DEC-160/172), so the inventory is the documented baseline and any additional legacy URLs the owner is aware of should be added to the table; (b) Bing guidance is cited for alignment only; Google Search Central is the primary reference; (c) no benchmark or test-run evidence was created (DEC-066).
- Uncertainties from §9 are not resolved in this brief; they are recorded for the owner and for reconciliation (X2).

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066).
- No installs, builds, server starts, VPS/SSH access, deployment, DNS changes, account creation (including Search Console), browser execution, or authenticated/mutating remote actions were performed (plan §4.1).
- No product code, scaffolding, or infrastructure was created or modified; no decision log or specification was edited; no evidence file, audit file, or `papyr-reference/` file was modified.
- `papyr-reference/` was read-only; verified unchanged via `git -C papyr-reference status --porcelain` (empty output, exit 0) before and after this task.
- No ranking, traffic, or performance claims are made; all SEO statements cite the primary sources in §5.4 and remain subject to normal search-engine behavior.
- Findings in this brief are recommendations, not accepted decisions (DEC-054, DEC-057).
