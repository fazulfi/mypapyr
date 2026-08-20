# SEO — Legacy URL Inventory & Disposition

- **Owner**: SEO-01 (P8-A), URL disposition governance
- **Status**: In branch, tracked (source of truth: `frontend/src/lib/i18n.ts`
  `LEGACY_ROUTING_PATHS` union); no P8 commit, PR, release, or deployment exists.
- **Guard**: `scripts/check-seo-inventory.sh` verifies every row below has exactly one disposition,
  that disposition maps to a real mechanism, and that the 15-path set exactly equals the app's
  `LEGACY_ROUTING_PATHS` (no drift, no duplicates).

This inventory records the disposition of every **legacy locale-less path** that the Papyr app must
handle (DEC-127, DEC-194). The full set is the 15 paths reserved in
`frontend/src/lib/i18n.ts:12-26` (`LEGACY_ROUTING_PATHS`). Every path has exactly one disposition
(301 / 410 / 307), each disposition maps to one of the three mechanisms defined in §4, and no path
is left to the generic handler (which would soft-404).

## 1. Disposition key

| Disposition | Meaning | Mechanism |
| --- | --- | --- |
| 301 | Permanent redirect, single-hop, locale-prefixed canonical target; does not set the locale cookie | `MECH_301` (§4.1) |
| 410 | Permanent Gone, localized + accessible body; non-indexable | `MECH_410` (§4.2) |
| 307 | Temporary redirect honoring cookie → Accept-Language → EN (DEC-047) | `MECH_307` (§4.3) |

## 2. The 15 legacy paths

Machine-parse key: each row is `| <legacy path> | <disposition> | <target / mechanism> |`.

| Legacy path | Disposition | Target / mechanism | Notes |
| --- | --- | --- | --- |
| /compress | 301 | /{locale}/compress-pdf | single-hop to localized canonical |
| /merge | 301 | /{locale}/merge-pdf | single-hop to localized canonical |
| /split | 301 | /{locale}/split-pdf | single-hop to localized canonical |
| /image-to-pdf | 301 | /{locale}/jpg-to-pdf | single-hop to localized canonical |
| /pdf-to-image | 301 | /{locale}/pdf-to-jpg | single-hop to localized canonical |
| /rotate | 410 | MECH_410 | retired tool; localized 410 Gone |
| /protect | 410 | MECH_410 | retired tool; localized 410 Gone |
| /unlock | 410 | MECH_410 | retired tool; localized 410 Gone |
| /watermark | 410 | MECH_410 | retired tool; localized 410 Gone |
| /sign | 410 | MECH_410 | retired tool; localized 410 Gone |
| /pdf-to-word | 410 | MECH_410 | retired tool; localized 410 Gone |
| /ocr | 410 | MECH_410 | retired tool; localized 410 Gone |
| /pdf-to-excel | 410 | MECH_410 | retired tool; localized 410 Gone |
| /faq | 307 | /{locale}/faq | locale-less supporting (DEC-047) |
| /privacy | 307 | /{locale}/privacy | locale-less supporting (DEC-047) |

**Counts: 5 × 301, 8 × 410, 2 × 307 = 15** (preserved exactly; corrections require documented
owner evidence per R-25 — **NOT_VERIFIED**, none on record, so the 410-default disposition stands).

## 3. Ordering guarantees

- 301 targets are always locale-prefixed (`/compress` → `/{locale}/compress-pdf`), so the redirect
  resolves in **one hop** and never re-enters the legacy dispatcher (`getLocaleRedirectPath` returns
  `null` for already-localized paths).
- No legacy path resolves to another legacy path (no chains).
- 410 bodies are returned directly; they never consult the redirect builder.
- The 8 deferred tools carry **no per-URL 301 exception** in the absence of owner traffic data
  (R-25 / DEC-114 hard gate).

## 4. Mechanisms

### 4.1 MECH_301 — direct permanent redirect (SEO-02)

`/compress|/merge|/split|/image-to-pdf|/pdf-to-image` → `301` to `/{resolvedLocale}/<canonical EN
slug>`, resolved via cookie → Accept-Language → EN. Does **not** set the `papyr_locale` cookie on a
301 (a permanent, cacheable redirect must not bake a per-user preference). Implemented in
`frontend/src/proxy.ts` (Next.js 16 proxy-file convention).

### 4.2 MECH_410 — localized gone (SEO-02, DEC-194)

`/rotate|/protect|/unlock|/watermark|/sign|/pdf-to-word|/ocr|/pdf-to-excel` → a real `410 Gone`
with a localized, accessible HTML body (`<html lang={locale}>`, single `main#main-content`, one
Home link, WCAG-AA contrast, distinct `gone` copy — never `notFound` copy). Non-indexable. Owned by
the proxy layer.

### 4.3 MECH_307 — locale-less supporting (DEC-047)

`/faq|/privacy` → `307` to `/{locale}/faq` / `/{locale}/privacy`, honoring cookie → Accept-Language →
EN. Temporary because the resolved locale is visitor-dependent.

## 5. Cross-checks performed by the guard

The guard (`scripts/check-seo-inventory.sh`) verifies:

1. **Exactly 15 legacy paths** exist in this inventory (5×301 + 8×410 + 2×307).
2. Every disposition is one of `301|410|307` and maps to a defined mechanism.
3. No duplicate legacy path and no conflicting disposition.
4. The 15 paths **exactly equal** the app's `LEGACY_ROUTING_PATHS` union in `frontend/src/lib/i18n.ts`
   (no missing, no extra, no drift).
5. The 5 301 targets resolve to canonical EN slugs that exist in `docs/seo/slug-table.md` §3
   (targets are present; a target absent from the slug table = unmapped mechanism = fail).
6. The 8 410 paths are exactly the deferred tool slugs (from `frontend/src/lib/catalog.ts`
   `LEGACY_TOOL_IDS`), and the 2 307 paths are exactly `/faq` and `/privacy`.

Any lapse exits non-zero (fail-closed), so SEO-01 cannot silently drift from code.
