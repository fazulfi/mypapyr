# Evidence File B4 — SEO, Slugs, and Legacy URL Migration (Web/Primary Sources)

- **Deliverable**: Track B, deliverable B4 (SEO, slugs, and legacy URL migration) — web/primary-source evidence.
- **Date of research / access date for all URLs below**: **2026-07-31** (UTC+7, Asia/Bangkok). Every cited page was fetched on this date.
- **Author**: Librarian subagent (read-only, anonymous, no accounts, no authentication).
- **Method**: Direct fetches of primary sources (developers.google.com/search, sitemaps.org, rfc-editor.org, bing.com/webmasters). No installs, builds, servers, or browser execution were performed. `papyr-reference/` was not touched.
- **Evidence standard**: Primary sources first. Secondary (SEO-blog) sources are explicitly marked SECONDARY and are not relied on for core guidance.
- **Page-version convention**: Each section lists the official page title, URL, access date, and the page footer's "Last updated" stamp when captured by the fetch. Where the footer stamp was not captured (long pages truncated before the footer), this is stated explicitly rather than guessed.

---

## 0. Source inventory (fetched 2026-07-31)

| # | Source (title) | URL | Page "Last updated" |
|---|---|---|---|
| S1 | Managing Multi-Regional and Multilingual Sites (Google Search Central) | https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites | 2025-12-10 UTC |
| S2 | Tell Google about localized versions of your page (Google Search Central) | https://developers.google.com/search/docs/specialty/international/localized-versions | footer stamp not captured in fetch (content fetched in full) |
| S3 | What is URL canonicalization (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/canonicalization | 2026-07-10 UTC |
| S4 | How to specify a canonical URL with rel="canonical" and other methods (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls | footer stamp not captured in fetch (content fetched in full) |
| S5 | URL structure best practices for Google Search (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/url-structure | 2025-12-10 UTC |
| S6 | Redirects and Google Search (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/301-redirects | 2026-04-14 UTC |
| S7 | How to move a site — site moves with URL changes (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes | 2026-06-17 UTC |
| S8 | Block Search indexing with noindex (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/block-indexing | 2025-12-10 UTC |
| S9 | Robots meta tag, data-nosnippet, and X-Robots-Tag specifications (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag | footer stamp not captured in fetch (content fetched in full) |
| S10 | Introduction to robots.txt (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/robots/intro | 2025-12-10 UTC |
| S11 | Build and submit a sitemap (Google Search Central) | https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap | 2026-07-08 UTC |
| S12 | Sitemaps XML format (sitemaps.org protocol) | https://www.sitemaps.org/protocol.html | "Last Updated: Monday, November 21, 2016" (protocol namespace 0.9) |
| S13 | RFC 6596 — The Canonical Link Relation | https://www.rfc-editor.org/rfc/rfc6596 | April 2012 (IETF Informational) |
| S14 | RFC 8288 — Web Linking | https://www.rfc-editor.org/info/rfc8288 | October 2017 (IETF Proposed Standard; obsoletes RFC 5988) |
| S15 | Bing Webmaster Guidelines | https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a | no explicit "last updated" stamp on page; page content reflects a 2025–2026 refresh (references Copilot and grounding experiences) |

**Navigation note**: The older Google URLs `.../crawling-indexing/international/multi-regional-multilingual-sites` and `.../crawling-indexing/international/localized-versions` returned HTTP 404 on 2026-07-31. Google has moved these documents to `/search/docs/specialty/international/` (S1, S2). Any reference in older Papyr materials to the old URLs should be updated.

---

## 1. Multi-regional and multilingual URL structure options (R1)

**Primary source**: S1 — "Managing Multi-Regional and Multilingual Sites", https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites (accessed 2026-07-31; last updated 2025-12-10 UTC).

### 1.1 Documented URL-structure options with pros/cons

The page's "Using locale-specific URLs" table documents exactly four options and marks URL parameters as **Not recommended**:

1. **Country-specific domain (ccTLD)** — e.g. `example.de`
   - Pros: clear geotargeting; server location irrelevant; easy separation of sites.
   - Cons: expensive (can have limited availability); requires more infrastructure; strict ccTLD requirements (sometimes); can only target a single country.
2. **Subdomains with gTLD** — e.g. `de.example.com`
   - Pros: easy to set up; allows different server locations; easy separation of sites.
   - Cons: users might not recognize geotargeting from the URL alone (is "de" the language or country?).
3. **Subdirectories with gTLD** — e.g. `example.com/de/`
   - Pros: easy to set up; low maintenance (same host).
   - Cons: users might not recognize geotargeting from the URL alone; single server location; separation of sites harder.
4. **URL parameters** — e.g. `site.com?loc=de` — **Not recommended.** Cons: URL-based segmentation difficult; users might not recognize geotargeting from the URL alone.

**Accuracy guard**: The current Google page does NOT rank subdirectories as "the" recommended option; it presents subdirectories as a practical, easy-to-set-up, low-maintenance option within the table. The URL-structure page (S5, §5.2 below) separately lists both `example.de` and `example.com/de/` as "Recommended" examples for multi-regional sites. Papyr's decision log should reflect this nuance (no single documented "Google recommends subdirectories over everything" statement in the current docs).

### 1.2 Locale-detection signals Google documents

- ccTLDs are "a strong signal to both users and search engines that your site is explicitly intended for a certain country"; some countries restrict ccTLD registration.
- `hreflang` statements (tags, headers, or sitemaps).
- Server location (IP address) — "not a definitive signal".
- Other signals: local addresses/phone numbers, local language and currency, links from local sites, Business Profile.
- Google treats some vanity ccTLDs (.tv, .me, plus a listed set: .ad .ai .as .bz .cc .cd .co .dj .fm .io .la .me .ms .nu .sc .sr .su .tv .tk .ws) as gTLDs.
- Google **ignores** locational `meta` tags (e.g. `geo.position`, `distribution`) and geotargeting HTML attributes.
- Google does **not** vary crawler source location to find locale variations; site owners must explicitly tell Google about variations.

### 1.3 Language/URL guidance relevant to slugs

- "Google recommends using different URLs for each language version of a page rather than using cookies or browser settings to adjust the content language on the page."
- If different URLs are used per language, use `hreflang` annotations.
- Do not automatically redirect users between language versions.
- It is fine to use localized words in the URL or an IDN, but use UTF-8 encoding and escape URLs properly when linking.
- If the same content exists in the same language at multiple URLs (e.g. `example.de/` and `example.com/de/`), pick a preferred version and use `rel="canonical"` plus `hreflang`.

---

## 2. hreflang — localized versions of a page (R2)

**Primary source**: S2 — "Tell Google about localized versions of your page", https://developers.google.com/search/docs/specialty/international/localized-versions (accessed 2026-07-31; footer "Last updated" stamp not captured in fetch — content was fetched in full via two independent readers).

### 2.1 Three implementation methods (equivalent per Google)

1. **HTML `<link>` tags** in the `<head>`: `<link rel="alternate" hreflang="lang_code" href="url_of_page" />` — one link per variant **including itself**; the set of links is identical on every version of the page. Must be in a well-formed `<head>`; do not combine with other attributes such as `media` in a single link tag.
2. **HTTP headers**: `Link: <url1>; rel="alternate"; hreflang="lang_code_1", <url2>; rel="alternate"; hreflang="lang_code_2", ...` — useful for non-HTML files (e.g. PDFs); URLs must be wrapped in `< >`; every version returns the identical header, listing every version including itself.
3. **Sitemap**: XML sitemap with `<xhtml:link rel="alternate" hreflang="..." href="..."/>` children under each `<url>`; requires `xmlns:xhtml="http://www.w3.org/1999/xhtml"`; each `<url>` lists every variant **including itself**; child elements do not count toward the sitemap URL limit; sitemap location rules still apply.

"The three methods are equivalent from Google's perspective." Using all three at once gives no Search benefit.

### 2.2 Required attributes / value syntax

- `lang_code`: a supported language/region code, or the reserved `x-default`.
- Format: one code, or two codes separated by a dash — language code in **ISO 639-1** format, optional region code in **ISO 3166-1 Alpha 2** format. Examples: `en-US`, `de-be`, `zh-Hans-US`.
- Only ISO 639-1 and ISO 3166-1 Alpha 2 values are supported; other codes such as `es-419` are NOT supported.
- "You can't specify the country code by itself. The first code stands for the language and Google doesn't automatically derive the language from a country code." (`be` is Belarusian, not Belgium — use `de-be`, `nl-be`, `fr-be`.)
- Script variations: derived from country (e.g. `zh-TW` → Traditional), or explicit ISO 15924 (`zh-Hant`, `zh-Hans`).
- `x-default`: reserved value for the fallback page when no other language/region matches the user's browser setting; designed for language-selector pages; no language code is attached to it.

### 2.3 Bidirectional and self-referencing requirements

- "Each language version must list itself **as well as** all other language versions." (self-referencing)
- "If two pages don't both point to each other, the tags will be ignored." (bidirectional)
- Alternate URLs must be fully-qualified, including transport method: `https://example.com/foo`, NOT `//example.com/foo` or `/foo`.
- Alternate URLs do not need to be in the same domain.
- For same-language multi-region variants (`en-ie`, `en-ca`, `en-au`), provide a generic `en` catchall page (may be one of the specific pages).
- If a full bidirectional set is hard to maintain, omit some languages on some pages — Google processes the pairs that do point to each other; always link newly expanded language pages bidirectionally to the dominant/originating language.

### 2.4 Common errors (documented "Troubleshooting" section)

- **Missing return links**: page X links to Y, so Y must link back to X; otherwise annotations may be ignored.
- **Incorrect language codes**: must be ISO 639-1 language (+ optional ISO 3166-1 Alpha 2 region); region alone is invalid.
- **Incorrect region codes**: use officially assigned ISO 3166-1 Alpha 2 codes; reserved/unofficial codes such as `EU`, `UN`, `UK` have no effect on Google Search.

### 2.5 Relationship to canonicalization

- S2: "Localized versions of a page are only considered duplicates if the main content of the page remains untranslated."
- S4 (canonical page): if using `hreflang` elements, specify a canonical page **in the same language**, or the best possible substitute language.
- S4: URLs inside `hreflang` clusters are preferred as canonicals (see §3.4).

### 2.6 Spec references used by Google

- Google's own article (S2) is the operative reference for its `hreflang` implementation; Google cites ISO 639-1 / ISO 3166-1 Alpha 2 / ISO 15924 for code values.
- The HTTP `Link` header serialization that Google documents is defined by the IETF Web Linking specification: **RFC 8288** (S14, https://www.rfc-editor.org/info/rfc8288, October 2017, obsoletes RFC 5988). RFC 8288 §3.4.1 defines the `hreflang` link-param ("a hint indicating what the language of the result of dereferencing the link should be"; ABNF value is `Language-Tag`).
- The sitemap `xhtml:link` hreflang extension is **not** defined by the sitemaps.org protocol document (S12); it is a Google-documented extension using the XHTML namespace, as specified in S2. Google's sitemap documentation (S11) links to S2 for localized versions.

---

## 3. Canonicalization (R3)

**Primary sources**: S3 — "What is URL canonicalization", https://developers.google.com/search/docs/crawling-indexing/canonicalization (accessed 2026-07-31; last updated 2026-07-10 UTC); S4 — "How to specify a canonical URL with rel='canonical' and other methods", https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (accessed 2026-07-31; footer stamp not captured); S13 — RFC 6596.

### 3.1 Definition and canonical selection

- S3: Canonicalization is "the process of selecting the representative –canonical– URL of a piece of content"; Google clusters near-identical pages and chooses the most complete/useful page as canonical. Canonical preference signals are a "hint, not a rule."
- Sources of duplicate content named by Google: region variants, device variants, protocol variants (HTTP/HTTPS), site functions (sort/filter), accidental variants.
- Different language versions are duplicates only when the primary content is in the same language (only template/boilerplate translated).

### 3.2 rel=canonical rules (S4)

- Methods ranked by influence: **redirects** (strong) > **`rel="canonical"` link annotations** (strong) > **sitemap inclusion** (weak). Methods can stack.
- Google supports `rel="canonical"` link annotations "as described in RFC 6596" (S13).
- **Absolute URLs**: "Use absolute paths rather than relative paths with the `rel="canonical"` link element." Good: `https://www.example.com/dresses/green/green-dress.html`; bad: `/dresses/green/green-dress.html`.
- **Self-referencing**: "Do include a `rel="canonical"` link on the canonical page itself (also known as a self-referential canonical)."
- **Cross-domain canonicals for syndication**: RFC 6596 §3 (S13) states the canonical target "MAY ... Exist on a different hostname or domain." RFC 6596 Appendix A lists Google's cross-domain support ("Google, canonical link relation HTML and HTTP header support, within the same domain and across domains") citing Google's "Handling legitimate cross-domain rel=canonical" post (2009). Google's current docs page (S4) also says "Alternate URLs do not need to be in the same domain" for hreflang annotations.
- **Don'ts** (S4): don't use robots.txt for canonicalization (Google may still index disallowed URLs without content); don't use the URL removal tool for canonicalization; don't specify different canonicals via different techniques; don't use URL fragments as canonical (Google generally doesn't support fragments).
- **Lowercase/hyphen normalization**: Google's URL-structure guidance (S5, §5.2) covers case sensitivity and hyphens-vs-underscores; the canonical doc does not itself mandate lowercase.
- **rel="canonical" with hreflang/lang/media/type attributes is ignored for canonicalization** (S4): "rel='canonical' annotations with hreflang, lang, media, and type attributes are not used for canonicalization."
- HTTP header method: `Link: <https://www.example.com/downloads/white-paper.pdf>; rel="canonical"` — Google cites RFC 5988 for the header form; RFC 5988 is now obsolete and replaced by RFC 8288 (S14). Use absolute URLs in the header too. Supported for web search results; useful for PDFs/Word docs.
- Google recommends choosing one method (link element OR header), not both simultaneously.
- Don't use `noindex` to express canonical preference within a single site (completely blocks the page).

### 3.3 Canonical ↔ hreflang relationship

- S4: If using `hreflang`, specify a canonical page in the same language, or the best possible substitute language.
- S4 "Prefer URLs in `hreflang` clusters": for canonicalization, Google prefers URLs that are part of reciprocal `hreflang` clusters. Example: `de-de` and `de-ch` that point to each other are preferred over `/de-at/` that is not in the cluster.
- S2: localized pages are duplicates only if main content is untranslated — meaning translated pages should use hreflang, not canonical.

### 3.4 Other canonicalization signals

- HTTPS preferred over HTTP as canonical, except when: invalid SSL certificate, insecure dependencies, HTTPS redirects to HTTP, or `rel="canonical"` points to HTTP. Avoid bad TLS certs/HTTPS-to-HTTP redirects; don't put HTTP versions in sitemaps or hreflang annotations.
- Sitemap inclusion: all pages listed in a sitemap are *suggested* as canonicals; sitemap is a weak signal.
- Redirects: permanent redirects are the strongest signal for canonicals; use redirects when deprecating duplicate pages.

---

## 4. Redirects and URL migration (R4)

**Primary sources**: S6 — "Redirects and Google Search", https://developers.google.com/search/docs/crawling-indexing/301-redirects (accessed 2026-07-31; last updated 2026-04-14 UTC); S7 — "How to move a site" (site moves with URL changes), https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes (accessed 2026-07-31; last updated 2026-06-17 UTC); S15 — Bing Webmaster Guidelines (accessed 2026-07-31).

### 4.1 301 vs 302 (S6)

- **Permanent redirects** (301, 308, instant meta refresh, JS `location`): Googlebot follows; the indexing pipeline uses the redirect as a signal that the target should be canonical; "Show the new redirect target in search results."
- **Temporary redirects** (302, 303, 307, delayed meta refresh): Googlebot follows but the redirect is not used as a canonical signal; "Show the source page in search results."
- Server-side redirects are most reliably interpreted; use server-side permanent redirects whenever possible; JavaScript redirects only as last resort (rendering may fail); crypto redirects (link-only "we moved") are not reliable.
- Recommended: `301` and `308`.

### 4.2 Site moves with URL changes (S7) — the documented migration process

Overview steps:
1. General best practices for site moves.
2. Prepare the new site and test thoroughly.
3. **Prepare a URL mapping** from current URLs to corresponding new format.
4. Start the site move by configuring server redirects from old URLs to new ones.
5. Monitor traffic on both old and new URLs.

**Search Console verification of both properties** (S7): "If you haven't already, verify both the old and new sites in Search Console. Be sure to verify all variants of both the old and new sites" (e.g. `www` and non-`www`, HTTP and HTTPS variants, for both old and new). Also submit a Change of Address in Search Console for the old site.

**301 not 302**: "We recommend server side permanent redirects from the old URLs to the new URLs"; "we recommend that you use HTTP permanent redirects if possible, such as `301` and `308`." (S7)

**Avoid redirect chains**: "Avoid chaining redirects. While Googlebot can follow up to 10 hops in a 'chain' of multiple redirects (for example, Page 1 > Page 2 > Page 3), we advise redirecting to the final destination directly. If this is not possible, keep the number of redirects in the chain low, ideally no more than 3 and fewer than 5." (S7)

**Update internal links and sitemaps** (S7):
- Update annotations: each new URL should have a self-referencing `rel="canonical"` link tag; update `rel-alternate-hreflang` annotations to new URLs.
- Update internal links from old URLs to new URLs using the mapping.
- Save for the final move: a sitemap file containing the new URLs, and a list of sites linking to the old URLs.
- After the move: submit the new sitemap in Search Console; remove the old sitemap; keep redirects "for as long as possible, generally at least 1 year."

**Monitoring indexation during migration** (S7):
- Use Search Console Sitemaps report: new-URL sitemap starts at zero indexed pages; old-URL sitemap count drops to zero over time. Warnings about redirecting URLs in the old sitemap are expected/normal.
- Index Coverage report shows drop on old site, increase on new site; check regularly for unexpected crawl errors.
- Search queries report shows impressions/clicks shifting to new URLs.
- Server access/error logs: check Googlebot crawling and unexpected HTTP errors.

**How long old URLs remain crawlable / visible** (S6, S7):
- "To consider a site move complete, Googlebot will have to visit every URL on your old and new site at least once." The move happens per-URL.
- "As a general rule, a medium-sized website can take a few weeks for most pages to move in our index; larger sites can take longer."
- S6 "Alternate versions of a URL": after a redirect, Google tracks both source and target; the old URL becomes an "alternate name" of the canonical and "may appear in search results when a user's query hints that they might trust the old URL more." After a domain move, Google may "continue to occasionally show the old URLs in the results, even though the new URLs are already indexed ... as users get used to the new domain name, the alternate names will fade away."
- Keep redirects ≥ 1 year so Google transfers all signals; consider keeping them indefinitely for users, but update your own links to the new URLs.

**Deleted/merged content**: return HTTP `404` or `410` for URLs not moved (S7).

**Common migration mistakes** (S7 troubleshooting): `noindex`/robots.txt blocks left in place; incorrect redirects to wrong/nonexistent URLs; other crawl errors; insufficient server capacity (Google crawls the new site more heavily after migration); not updating sitemaps.

### 4.3 Bing Webmaster Guidelines on redirects and URL structure (S15)

- "Use 301 redirects for permanent URL changes; Use 302 redirects only for very short-term changes (less than 2 days); Use redirects instead of canonical tags" for URL moves.
- Sitemaps "should: List only canonical URLs; Reflect current site structure; Remove deleted or redirected URLs promptly; Include freshness signals (such as lastmod) where applicable."
- "robots.txt controls crawl access, not indexing. Use NOINDEX when a URL should NOT appear in Bing search, Copilot experiences, or grounding API results."
- Removed content: "Return a 404 status code; Use Bing's Content Removal tools when appropriate; Update deleted or changed URLs via IndexNow."
- "Preserve URL Stability Over Time. Avoid unnecessary URL changes. When changes are required: Use proper redirects; Preserve meaning and intent."
- Bing also documents IndexNow for fast notification of URL adds/updates/removals.
- **Dated-info note**: The Bing guidelines page is currently framed around Bing + Copilot/grounding and is best read as the 2026 iteration; no explicit "last updated" stamp was visible on the fetched page (accessed 2026-07-31).

---

## 5. Slug / URL best practices (R5)

**Primary source**: S5 — "URL structure best practices for Google Search", https://developers.google.com/search/docs/crawling-indexing/url-structure (accessed 2026-07-31; last updated 2025-12-10 UTC).

### 5.1 Crawlability requirements

- Follow **IETF STD 66** (RFC 3986, URI syntax); reserved characters must be percent-encoded.
- Don't use URL fragments to change content (Google generally doesn't support fragments).
- Use common parameter encoding (`=` for key-value, `&` to add parameters).
- Case sensitivity: "Google Search's URL handling is case sensitive (for example, Google treats both `/APPLE` and `/apple` as distinct URLs with their own content). If upper and lower case text in a URL is treated the same by your web server, convert all text to the same case so it's easier for Google to determine that URLs reference the same page."

### 5.2 Readability best practices (the "slug" guidance)

- **Use descriptive URLs**: "use readable words rather than long ID numbers" (e.g. `wiki/Aviation` not `index.php?topic=42&area=3a5ebc...`).
- **Use your audience's language** in the URL (with transliteration as applicable).
- **Use percent encoding as necessary** when linking (non-ASCII characters percent-encoded).
- **Use hyphens, not underscores**: "we recommend using hyphens (`-`) instead of underscores (`_`) to separate words in your URLs, as it helps users and search engines better identify concepts in the URL." Historical reason: underscores are commonly used for concepts kept together (e.g. `format_date`).
- **Use as few parameters as you can**: "Whenever possible, shorten URLs by trimming unnecessary parameters (meaning, parameters that don't change the content)."
- Keep URLs concise/simple: "we recommend creating a simple URL structure"; overly complex URLs with many parameters cause crawl waste (additive filtering, irrelevant parameters, session IDs, calendars).
- **Multi-regional sites**: "consider using a URL structure that makes it easy to geotarget your site." Recommended examples given: country-specific domain `https://example.de`; country-specific subdirectory with gTLD `https://example.com/de/`. Reference made to S1's locale-specific URL table.
- Related: S1 recommends different URLs per language (rather than cookie/browser-based switching) and says localized words/IDNs in URLs are fine with UTF-8 encoding.

### 5.3 Localized URLs in multi-regional sites (R5 second half)

- S1: "Use different URLs for different language versions"; if you do, use `hreflang` so Search links to the correct language version.
- S2: fully-qualified alternate URLs; each variant lists itself and all others; `x-default` fallback; language/region codes as in §2.2.
- There is no Google statement that slugs must be translated; localized words are permitted (S1, S5). What Google *requires* is explicit locale annotation via hreflang/sitemaps when URLs differ per language/region (S1).

---

## 6. noindex and robots.txt (R6)

**Primary sources**: S8 — "Block Search indexing with noindex", https://developers.google.com/search/docs/crawling-indexing/block-indexing (accessed 2026-07-31; last updated 2025-12-10 UTC); S9 — "Robots meta tag, data-nosnippet, and X-Robots-Tag specifications", https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag (accessed 2026-07-31; footer stamp not captured); S10 — "Introduction to robots.txt", https://developers.google.com/search/docs/crawling-indexing/robots/intro (accessed 2026-07-31; last updated 2025-12-10 UTC).

### 6.1 noindex implementation (S8, S9)

- Two equivalent implementation methods:
  1. `<meta name="robots" content="noindex">` in the `<head>` (also `googlebot` for Google-only: `<meta name="googlebot" content="noindex">`).
  2. `X-Robots-Tag: noindex` HTTP response header — required for non-HTML resources (PDFs, video, images).
- "Specifying the `noindex` rule in the robots.txt file is not supported by Google." (S8)
- Critical requirement (S8): "the page or resource **must not** be blocked by a robots.txt file, and it has to be otherwise accessible to the crawler. If the page is blocked by a robots.txt file ... the crawler will never see the `noindex` rule, and the page can still appear in search results."
- Google may take months to recrawl after adding `noindex`; use URL Inspection to request recrawl. For fast removal, use the removals documentation (S8, S9 rule table: "To remove information from Google, follow our step-by-step guide" → `/search/docs/crawling-indexing/remove-information`).
- Valid rules per S9 include: `all`, `noindex`, `nofollow`, `none` (= noindex+nofollow), `nosnippet`, `indexifembedded`, `max-snippet`, `max-image-preview`, `max-video-preview`, `notranslate`, `noimageindex`, `unavailable_after`. Multiple rules combine with commas or multiple tags; in conflicts "the more restrictive rule applies." (`noarchive`/`nocache`/`nositelinkssearchbox` are listed as historical/unused by Google.)

### 6.2 noindex vs removal

- S8: `noindex` is for pages you control and can keep accessible; it prevents indexing but takes time to be recrawled.
- S8: "If you need to remove a page of your site quickly from Google's search results, see our documentation about removals" (https://developers.google.com/search/docs/crawling-indexing/remove-information — not fetched in this pass; cited from S8's link).

### 6.3 robots.txt (S10)

- Purpose: "A robots.txt file tells search engine crawlers which URLs the crawler can access on your site. This is used mainly to avoid overloading your site with requests; **it is not a mechanism for keeping a web page out of Google**."
- Allowed directives per Google's intro page: `User-agent`, `Allow`, `Disallow`, plus the `Sitemap:` directive (the Sitemap directive is documented on S11 and S12; S10 links to Google's robots.txt spec pages, including "How Google interprets the robots.txt specification" at https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec — not fetched in this pass).
- Disallowed URLs can still be indexed: "A page that's disallowed in robots.txt can still be indexed if linked to from other sites" — the URL and anchor text can appear in results without a description. To prevent indexing, use `noindex` or password protection.
- robots.txt rules are not supported by all engines and cannot enforce behavior; don't use robots.txt for sensitive content.
- To block media files from appearing in Google results, robots.txt can be used for images/video/audio (unlike HTML pages).

---

## 7. Sitemaps (R7)

**Primary sources**: S12 — sitemaps.org protocol, https://www.sitemaps.org/protocol.html (accessed 2026-07-31; page "Last Updated: Monday, November 21, 2016" — protocol namespace 0.9, current version); S11 — "Build and submit a sitemap", https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (accessed 2026-07-31; last updated 2026-07-08 UTC).

### 7.1 Protocol version and limits

- Current protocol namespace: `http://www.sitemaps.org/schemas/sitemap/0.9` (S12).
- Limits (S12, S11): a single sitemap may contain **no more than 50,000 URLs** and be **no larger than 50MB (52,428,800 bytes)** uncompressed; gzip compression allowed (uncompressed size limit applies). Sitemap index files: max 50,000 sitemaps and 50MB.
- `<loc>` value must begin with the protocol (e.g. `http`) and be **less than 2,048 characters** (S12).
- Required structure: `<urlset>` root with namespace, `<url>` per entry, `<loc>` child per URL (S12). Other tags optional (`lastmod`, `changefreq`, `priority`).
- Sitemap file location: a sitemap can only include URLs that are descendants of its directory on the same host/protocol; root placement strongly recommended (S12, S11).
- Entity escaping required for XML values (S12); file must be UTF-8 (S12, S11).

### 7.2 lastmod guidance

- S12: `<lastmod>` "should be in W3C Datetime format" and "must be set to the date the linked page was last modified, not when the sitemap is generated."
- S11: "Google uses the `<lastmod>` value if it's consistently and verifiably (for example by comparing to the last modification of the page) accurate. The `<lastmod>` value should reflect the date and time of the last significant update to the page" (main content, structured data, links = significant; copyright-date change = not significant).
- S11: "Google ignores `<priority>` and `<changefreq>` values."
- S11: use fully-qualified absolute URLs in sitemaps; Google crawls URLs exactly as listed.

### 7.3 hreflang annotations inside sitemaps

- S2 (hreflang doc, §2.1 method 3): XML sitemap with `xmlns:xhtml="http://www.w3.org/1999/xhtml"` and `<xhtml:link rel="alternate" hreflang="lang" href="url"/>` children; one `<url>` per variant; each entry lists every variant including itself; child elements don't count toward the URL limit; the sitemap directory-location rules apply.
- S11 confirms the XML sitemap format "can be used to supply additional data about ... the localized versions of your pages," linking to S2.

### 7.4 Submission

- Search Console Sitemaps report; Search Console API; or `Sitemap: https://example.com/my_sitemap.xml` line in robots.txt (multiple sitemap lines allowed, no limit) (S11). S12 also documents HTTP ping submission for engines that support it.

---

## 8. Domain/URL inventory migration practice (R8)

**Primary source**: S7 — "How to move a site" (https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes, accessed 2026-07-31; last updated 2026-06-17 UTC). Supporting: S6 (alternate names), S11 (sitemaps), S15 (Bing).

### 8.1 Google's documented "prepare URL mapping" step

- "It's important to map your old site's URLs to the URLs for the new site." (S7)
- **Determine your old URLs** (S7): start with important URLs (from sitemaps, server logs/analytics, Search Console "Links to your site"); use the CMS to list all content URLs; check server logs for recently visited URLs; **include images, videos, JS, and CSS** in the inventory.
- **Create a mapping of old to new URLs**: decide where each old URL should redirect; store in a database or as URL-rewriting rules (S7).
- **Update URL details on the new site** (S7):
  1. Update annotations: self-referencing `rel="canonical"` on each new URL; update `hreflang` annotations to new URLs.
  2. Update internal links from old URLs to new URLs using the mapping.
  3. Save: a sitemap file of the new URLs and a list of external sites linking to old URLs.
- **Plan the redirect strategy** (S7): server-side permanent redirects (301/308) from old to new per the mapping; small/medium sites: move all URLs simultaneously; large sites: move in sections; avoid redirect chains (≤3 ideally, <5, max 10 hops) — §4.2.
- "Don't worry about link credit. `301` and other permanent redirects don't cause a loss in PageRank." (S7)
- Keep redirects ≥ 1 year; update internal/external/ad/profile links promptly; monitor with Search Console Sitemaps report + Index Coverage + queries (§4.2).

### 8.2 Standard practice: map every legacy URL before launch

- S7 documents the mapping as a required pre-launch step for URL-changing moves: "3. Prepare a URL mapping from the current URLs to their corresponding new format" is a numbered overview step, and "Prepare URL mapping" is a full section ("Once you have the listing of old URLs, decide where each one should redirect to").
- For wildcard-able domain moves a per-URL list may be unnecessary, but for path changes Google instructs building the full mapping; deleted/merged content must return 404/410 (S7).
- S7 troubleshooting: "Incorrect redirects — Check your redirects from the old site to the new one. We frequently see people redirecting to the wrong (non-existent) URLs on the new site." — i.e., a complete, accurate redirect map is the documented norm.
- Bing (S15) aligns: sitemaps should list only canonical URLs and remove deleted/redirected URLs promptly; use 301s for moves; preserve URL stability.

---

## 9. Conflicts, dated information, and gaps

1. **Old Google international URLs are dead**: `.../crawling-indexing/international/multi-regional-multilingual-sites` and `.../crawling-indexing/international/localized-versions` returned 404 on 2026-07-31; current URLs are under `/search/docs/specialty/international/` (S1, S2).
2. **"Google recommends subdirectories" nuance**: The current multi-regional doc (S1) presents ccTLD/subdomain/subdirectory as options with pros/cons and does not single out one as universally recommended; it marks URL parameters as "Not recommended." Subdirectories are documented as easy to set up and low-maintenance. The URL-structure page (S5) lists both `example.de` and `example.com/de/` as recommended examples. Avoid overstating Google's position in Papyr decisions.
3. **RFC reference drift**: Google's canonical docs cite RFC 5988 for the Link header (S4); RFC 5988 is obsolete and replaced by RFC 8288 (S14, October 2017). The HTML `rel="canonical"` reference, RFC 6596 (S13, April 2012), is still current.
4. **Sitemaps protocol date**: sitemaps.org protocol page last updated 2016-11-21; namespace 0.9 remains the current version (S12). No newer protocol version exists as of access date.
5. **Bing guidelines framing**: S15 is the current Bing Webmaster Guidelines page, rewritten around Bing + Copilot/grounding; it contains the URL/redirect/noindex guidance summarized in §4.3 and §6. No visible last-updated stamp (accessed 2026-07-31).
6. **Footer stamps not captured** (stated, not guessed): S2, S4, S9 — content was retrieved in full via two independent readers; the pages' "Last updated" footers fell outside the captured window. S1/S3/S5/S6/S7/S8/S10/S11 stamps were captured and are listed above.
7. **No secondary (SEO-blog) sources were used for core guidance** in this evidence file. The only non-search-engine references are the IETF RFCs (primary standards).

---

## 10. Verification evidence

- Output file exists and is non-empty: `<workspace-root>\audit-outputs\research\track-b\_evidence-b4-web.md` (created 2026-07-31).
- Sections present: URL structure (R1, R5), hreflang (R2), canonical (R3), redirects/URL migration (R4, R8), noindex + robots.txt (R6), sitemaps (R7) — each with URLs and access date 2026-07-31.
- No placeholder tokens (no TODO/FIXME/TBD/lorem text) in this file.
- `papyr-reference/` was not modified; no installs, builds, servers, or browser execution were performed.
