import type { Locale } from "./i18n";
import { toolCatalog } from "./catalog";

export function canonicalSlug(href: string): string {
  return href.split("/").filter(Boolean).pop() ?? "";
}

// Maps `${locale}/${translatedSlug}` → canonical EN slug. Built once from the
// catalog: EN slugs already match the app-router directories, so aliases exist
// only for non-EN locales whose translated slug differs from the EN slug.
const ALIASES: ReadonlyMap<string, string> = (() => {
  const map = new Map<string, string>();
  for (const tool of toolCatalog) {
    const enSlug = canonicalSlug(tool.hrefs.en);
    for (const locale of ["es" as Locale, "id" as Locale]) {
      const slug = canonicalSlug(tool.hrefs[locale]);
      if (slug !== enSlug) {
        map.set(`${locale}/${slug}`, enSlug);
      }
    }
  }
  return map;
})();

export function resolveRouteAlias(pathname: string): string | null {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length < 2) return null;
  const [locale, ...rest] = segments;
  const enSlug = ALIASES.get(`${locale}/${rest[0]}`);
  if (enSlug === undefined) return null;
  return `/${locale}/${enSlug}` + (rest.length > 1 ? `/${rest.slice(1).join("/")}` : "");
}
