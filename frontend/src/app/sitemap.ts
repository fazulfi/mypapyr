import type { MetadataRoute } from "next";

import { toolCatalog } from "../lib/catalog";
import { locales, type Locale } from "../lib/i18n";

export const BASE_URL = "https://budgezen.com";

// PT01-G8 / WS-5 (SEO-03): every canonical public route is emitted for all
// three locales as an absolute budgezen.com URL, each with per-entry hreflang
// alternates (en/es/id + x-default → EN) so the XML carries localized variant
// discovery alongside the metadata alternate links. Excluded per DEC-194:
// deferred legacy tool slugs (localized 410 Gone) and the tool-unavailable
// shell are not indexable and never appear here. Locale-less entry paths
// (/faq, /privacy, /) are reserved for 307 locale routing, so listing them
// would point crawlers at redirects rather than final URLs.
type SupportingRouteSlug =
  "faq" | "privacy" | "terms" | "cookies-advertising" | "contact" | "status" | "roadmap" | "blog";

const _SUPPORTING_ROUTE_SLUGS: readonly SupportingRouteSlug[] = [
  "faq",
  "privacy",
  "terms",
  "cookies-advertising",
  "contact",
  "status",
  "roadmap",
  "blog",
] as const satisfies readonly SupportingRouteSlug[];

interface SitemapGroup {
  changeFrequency: MetadataRoute.Sitemap[number]["changeFrequency"];
  priority: number;
  paths: Record<Locale, string>;
}

function group(
  changeFrequency: SitemapGroup["changeFrequency"],
  priority: number,
  paths: Record<Locale, string>,
): SitemapGroup {
  return { changeFrequency, priority, paths };
}

function supportingGroup(
  slug: SupportingRouteSlug,
  changeFrequency: SitemapGroup["changeFrequency"],
  priority: number,
): SitemapGroup {
  return group(
    changeFrequency,
    priority,
    Object.fromEntries(locales.map((locale) => [locale, `/${locale}/${slug}`])) as Record<
      Locale,
      string
    >,
  );
}

// changeFrequency/priority mirror the pre-WS-5 EN-only sitemap semantics for
// shared routes (home 1.0/weekly, tools 0.8/monthly, faq 0.5/monthly,
// privacy 0.3/yearly) with sensible defaults for the routes added by WS-5.
const SITEMAP_GROUPS: readonly SitemapGroup[] = [
  group(
    "weekly",
    1,
    Object.fromEntries(locales.map((locale) => [locale, `/${locale}`])) as Record<Locale, string>,
  ),
  ...toolCatalog.map((tool) => group("monthly", 0.8, tool.hrefs)),
  supportingGroup("faq", "monthly", 0.5),
  supportingGroup("privacy", "yearly", 0.3),
  supportingGroup("terms", "yearly", 0.3),
  supportingGroup("cookies-advertising", "yearly", 0.3),
  supportingGroup("contact", "yearly", 0.3),
  supportingGroup("status", "monthly", 0.3),
  supportingGroup("roadmap", "monthly", 0.3),
  supportingGroup("blog", "weekly", 0.5),
];

function buildEntry(
  groupEntry: SitemapGroup,
  locale: Locale,
  now: Date,
): MetadataRoute.Sitemap[number] {
  const u = (target: Locale): string => `${BASE_URL}${groupEntry.paths[target]}`;
  return {
    url: u(locale),
    lastModified: now,
    changeFrequency: groupEntry.changeFrequency,
    priority: groupEntry.priority,
    alternates: {
      languages: {
        en: u("en"),
        es: u("es"),
        id: u("id"),
        "x-default": u("en"),
      },
    },
  };
}

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  return SITEMAP_GROUPS.flatMap((entry) => locales.map((locale) => buildEntry(entry, locale, now)));
}
