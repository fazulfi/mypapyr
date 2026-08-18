import type { Metadata } from "next";

import { locales, type Locale } from "../i18n";

/**
 * SEO-03 / P8-E — single source of truth for the canonical SEO origin and the
 * per-route canonical/hreflang shape. All three SEO surfaces (root layout
 * metadata, `sitemap.ts`, `robots.ts`) import `SEO_BASE_URL` from here so the
 * canonical host cannot drift between the `<head>`, `sitemap.xml`, and
 * `robots.txt`.
 *
 * Host decision: `https://budgezen.com` is the confirmed primary production
 * and canonical origin. `mypapyr.com` remains a legacy domain; edge redirect
 * coverage is an external deployment concern and must be verified independently.
 */
export const SEO_BASE_URL = "https://budgezen.com";

/** Absolute, locale-prefixed URL for a subpath ("" → locale root). */
export function absoluteHref(locale: Locale, subpath: string): string {
  return subpath === "" ? `${SEO_BASE_URL}/${locale}` : `${SEO_BASE_URL}/${locale}${subpath}`;
}

/** Per-locale path map for a supporting route rendered at `/{locale}/{slug}`. */
export function supportingPaths(slug: string): Record<Locale, string> {
  return Object.fromEntries(locales.map((l) => [l, `/${l}/${slug}`])) as Record<Locale, string>;
}

export interface AlternateLinks {
  canonical: string;
  languages: Record<Locale | "x-default", string>;
}

/**
 * Computes the absolute self-referencing canonical and bidirectional hreflang
 * (en/es/id + x-default → EN) for one route from its per-locale path map. The
 * map must contain full locale-prefixed paths (e.g. tool `hrefs` or the output
 * of `supportingPaths`); the helper never guesses a path, keeping output
 * deterministic and static-safe (no `generateMetadata` pathname reads).
 */
export function alternateLinks(locale: Locale, paths: Record<Locale, string>): AlternateLinks {
  const canonical = `${SEO_BASE_URL}${paths[locale]}`;
  return {
    canonical,
    languages: {
      en: `${SEO_BASE_URL}${paths.en}`,
      es: `${SEO_BASE_URL}${paths.es}`,
      id: `${SEO_BASE_URL}${paths.id}`,
      "x-default": `${SEO_BASE_URL}${paths.en}`,
    },
  };
}

/** Convenience: `alternateLinks` for a supporting route `/{locale}/{slug}`. */
export function supportingAlternates(locale: Locale, slug: string): AlternateLinks {
  return alternateLinks(locale, supportingPaths(slug));
}

/** Supporting-route `Metadata` built from resolved title/description + alternates. */
export function supportingPageMetadata(
  locale: Locale,
  slug: string,
  title: string,
  description: string,
): Metadata {
  return {
    title,
    description,
    alternates: supportingAlternates(locale, slug),
  };
}
