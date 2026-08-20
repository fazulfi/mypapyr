# Phase 8 SEO SLO and R-25 traffic baseline

- **Status:** Baseline captured on 2026-08-20. External indexing and path-level legacy traffic remain NOT_VERIFIED.
- **Scope:** Three user-approved SEO service-level objectives, their measurement contracts, and the R-25 traffic evidence available at baseline time.
- **Owner:** Repository maintainers own the document, guards, and measurement scripts. The account owner confirms external Google Search Console, Google Analytics, DNS, Cloudflare, and production results.

## 1. User-approved SEO SLOs

### SLO 1: Indexing within 30 days

> "Semua halaman indexable budgezen.com ter-index Google dalam ≤30 hari."

| Field | Record |
| --- | --- |
| Target | All indexable `budgezen.com` pages are indexed by Google within 30 days of publication or canonical availability. |
| Measurement source | Google Search Console Coverage and Performance reports. |
| Baseline as of 2026-08-20 | **NOT_VERIFIED.** The `budgezen.com/sitemap.xml` read succeeded with 57 pages (42 P8 routes + 15 P9 blog articles), based on the owner-provided screenshot read on 20 August 2026. Sitemap availability and count do not prove external indexing. |
| Cadence | Weekly during the first 30 days after release, then monthly. |
| Owner | Repository: maintainers verify the sitemap inventory and record evidence. Account owner: confirms GSC indexing and timing. |

### SLO 2: No soft-404 or unintended noindex

> "Nol soft-404 / noindex pada halaman yang seharusnya di-index."

| Field | Record |
| --- | --- |
| Target | Zero soft-404 responses and zero unintended `noindex` exclusions among pages designated as indexable. |
| Measurement source | Google Search Console Coverage exclusions, plus the repository SEO inventory and crawl audit. |
| Baseline as of 2026-08-20 | **NOT_VERIFIED.** Repository inventory records 57 intended indexable URLs (42 P8 routes + 15 P9 blog articles), but no owner-confirmed GSC exclusion export or external crawl audit result is recorded here. |
| Cadence | Weekly while the migration settles, then monthly. |
| Owner | Repository: maintainers run `scripts/check-seo-inventory.sh` and preserve crawl-audit results. Account owner: confirms GSC exclusions and any manual actions. |

### SLO 3: Valid legacy dispositions

> "Semua legacy path → status 301/308/410 valid tanpa loop."

| Field | Record |
| --- | --- |
| Target | Every legacy path returns a valid 301, 308, or 410 disposition, with no redirect loop. |
| Measurement source | `scripts/check-seo-inventory.sh` plus an external crawl audit of representative and complete legacy paths. |
| Baseline as of 2026-08-20 | **Repository baseline:** 15 documented locale-less paths, with 5 paths assigned 301, 8 assigned 410, and 2 assigned 307 for locale-dependent supporting routes. **NOT_VERIFIED externally:** no complete owner-confirmed crawl result is recorded in this document. |
| Cadence | Weekly through migration validation, then monthly and after redirect changes. |
| Owner | Repository: maintainers own the inventory and guard. Account owner: confirms DNS, Cloudflare edge behavior, production responses, and crawl-audit evidence. |

The SLOs are targets, not evidence that external indexing or production response behavior is complete. A sitemap success, repository test, or inventory check must not be reported as proof of Google indexing.

## 2. R-25 legacy-traffic baseline

### Measurement contract

- **Baseline window:** `2026-07-21..2026-08-20`.
- **Source:** Cloudflare GraphQL `httpRequests1dGroups`, zone-level daily totals.
- **Zones:** `mypapyr.com` (`f2391a4d9748564581e5085fa4a68aa4`) and `budgezen.com` (`e95c93a77bc1f8fe897f36a81776cc36`).
- **Fields shown:** requests, page views, and unique visitors. Values below are data from the supplied baseline, not claims about causation, indexing, or business impact.
- **Limitation:** Path-level legacy breakdown was not available through `httpRequests1dGroups` filter arguments. Follow-up should use `httpRequests1hGroups` or `httpRequestsAdaptiveGroups` with the `clientRequestPath` dimension, then cross-check against GSC and GA.

### `mypapyr.com` zone

Total requests for the baseline window were approximately **62,000**.

| Date | Requests | Page views | Uniques |
| --- | ---: | ---: | ---: |
| 2026-08-15 | 6,685 | 315 | 108 |
| 2026-08-16 | 5,278 | 156 | 124 |
| 2026-08-02 | 2,440 | 202 | 116 |
| 2026-08-14 | 1,553 | 217 | 98 |

These are the supplied high-volume daily points, not a complete daily table.

### `budgezen.com` zone

The supplied post-cutover daily data are:

| Date | Requests | Page views | Uniques |
| --- | ---: | ---: | ---: |
| 2026-08-16 | 3,264 | 219 | 135 |
| 2026-08-17 | 1,801 | 134 | 106 |
| 2026-08-18 | 1,808 | 174 | 148 |
| 2026-08-19 | 2,365 | 77 | 119 |
| 2026-08-20 | 1,047 | 32 | 65 |

These numbers are data only. They do not establish that legacy paths received traffic, that users were redirected successfully, or that Google indexed the pages.

### R-25 follow-up and NOT_VERIFIED items

- **NOT_VERIFIED:** Path-level traffic for each legacy URL. The supplied zone-level daily totals cannot identify traffic to `/compress`, `/merge`, `/split`, `/image-to-pdf`, `/pdf-to-image`, retired paths, or locale-less supporting paths.
- **NOT_VERIFIED:** Complete 301/308/410 response coverage and loop-free behavior in production. The repository inventory and guard are not a production crawl.
- **NOT_VERIFIED:** Google indexing, ranking, crawl timing, or search performance. The sitemap success with 57 pages is not indexing evidence.
- **Owner-confirmable:** The account owner can run the recommended Cloudflare path query, provide GSC and GA cross-checks, and confirm production edge responses. Repository maintainers can then update this baseline with dated evidence without changing DNS or Cloudflare configuration.

## 3. DNS and Cloudflare read-only verification

DNS and Cloudflare configuration were verified read-only through the API. No DNS, Cloudflare, or API mutation was performed, and no token or secret is recorded here.

| Host | Zone | Cutover address and behavior |
| --- | --- | --- |
| `mypapyr.com` and `www.mypapyr.com` | `f2391a4d9748564581e5085fa4a68aa4` | A record `82.25.62.204`, proxied, to VPS Nginx 308 behavior |
| `budgezen.com` | `e95c93a77bc1f8fe897f36a81776cc36` | A record `76.76.21.21`, proxied, to Vercel |

This read-only configuration check does not verify external indexing, complete redirect coverage, or the SLOs above.
