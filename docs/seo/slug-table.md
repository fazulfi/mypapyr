# SEO — Authoritative Slug Table

- **Owner**: SEO-01 (P8-A), frontend route governance
- **Status**: In branch, tracked (source of truth: `frontend/src/lib/catalog.ts` `hrefs`,
  `frontend/src/lib/i18n.ts`, `frontend/src/app/sitemap.ts` `_SUPPORTING_ROUTE_SLUGS`); no P8 commit, PR,
  release, or deployment exists.
- **Guard**: `scripts/check-seo-inventory.sh` cross-checks this table against the legacy inventory
  and the code singletons below, so the table cannot drift from the running app.

This table is the single authoritative mapping of every indexable public route to its per-locale
slug and canonical URL for Papyr. It is **not** an implementation module — the code singletons in
§4 remain the runtime source of truth; this document records them and the rules that keep the
canonical set stable. There is intentionally **no second slug table** anywhere in the tree; the
`LEGACY_*` sets in `frontend/src/lib/i18n.ts` are a separate, disjoint legacy disposition set (see
`docs/seo/legacy-url-inventory.md`), never a conflicting copy of this table.

## 1. Canonical host

The canonical base is `https://budgezen.com` (via `SEO_BASE_URL`, imported by
`sitemap.ts`, `robots.ts`, and `[locale]/layout.tsx` metadata). The owner has confirmed
`budgezen.com` as the primary production and canonical frontend host. `mypapyr.com` is
legacy/redirect-only; redirect completeness remains an external edge concern and is not inferred
from this source table.

## 2. Locale set

Papyr serves three locales. There is no `es-419`; `x-default` points at EN.

| Locale | ISO code | Notes |
| --- | --- | --- |
| English | `en` | default; `x-default` target |
| Spanish | `es` | |
| Indonesian | `id` | |

## 3. Tool slugs (5 tools × 3 locales = 15 URL paths)

Source of truth: `frontend/src/lib/catalog.ts` `toolCatalog[].hrefs`, keyed by the canonical EN
slug in `frontend/src/lib/tool-ids.ts` `TOOL_IDS`. Machine-parse key: each row is
`| tool | <EN slug> | <en> | <es> | <id> |`.

| Type | EN slug | `/en/...` | `/es/...` | `/id/...` |
| --- | --- | --- | --- | --- |
| tool | compress-pdf | /en/compress-pdf | /es/comprimir-pdf | /id/kompres-pdf |
| tool | merge-pdf | /en/merge-pdf | /es/combinar-pdf | /id/gabungkan-pdf |
| tool | split-pdf | /en/split-pdf | /es/dividir-pdf | /id/pisahkan-pdf |
| tool | jpg-to-pdf | /en/jpg-to-pdf | /es/jpg-a-pdf | /id/gambar-ke-pdf |
| tool | pdf-to-jpg | /en/pdf-to-jpg | /es/pdf-a-jpg | /id/pdf-ke-gambar |

## 4. Supporting slugs (8 supporting × 3 locales = 24 URL paths)

Source of truth: shared slugs listed in `frontend/src/app/sitemap.ts` `_SUPPORTING_ROUTE_SLUGS` and
rendered under every locale (`/{locale}/{slug}`). Machine-parse key: `| supporting | <slug> |`.

| Type | Slug | Locale forms |
| --- | --- | --- |
| supporting | faq | /{locale}/faq |
| supporting | privacy | /{locale}/privacy |
| supporting | terms | /{locale}/terms |
| supporting | cookies-advertising | /{locale}/cookies-advertising |
| supporting | contact | /{locale}/contact |
| supporting | status | /{locale}/status |
| supporting | roadmap | /{locale}/roadmap |
| supporting | blog | /{locale}/blog |

## 5. Home route

| Type | Form |
| --- | --- |
| home | /{locale} (EN default `/en`) |

## 6. Count invariant

**42 indexable URLs** = 15 tool paths (5 tools × 3 locales) + 24 supporting paths (8 supporting ×
3 locales) + 3 home paths (3 locales). This invariant is asserted by `frontend/src/app/sitemap.ts`
and `frontend/src/app/__tests__/sitemap.test.ts` and must not regress.

## 7. Non-indexable surfaces (excluded)

The following are **not** in this slug table and must never appear in the sitemap, canonical, or
hreflang sets (DEC-194):

- `tool-unavailable` shell and all `/{locale}/tool-unavailable?tool=<legacy id>` variants.
- All 15 legacy locale-less paths — they are governed by the legacy disposition inventory
  (`docs/seo/legacy-url-inventory.md`), not this table.
