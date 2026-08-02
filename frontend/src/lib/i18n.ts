export const locales = ["en", "es", "id"] as const;

export const defaultLocale = "en";

export type Locale = (typeof locales)[number];

export const LOCALE_COOKIE = "papyr_locale";

// R-15 §4–§6 legacy locale-less paths: reserved for the URL-disposition task,
// never locale-prefixed here (five tool 301s, eight deferred 410s, /faq, /privacy).
export const LEGACY_ROUTING_PATHS: ReadonlySet<string> = new Set([
  "/compress",
  "/merge",
  "/split",
  "/image-to-pdf",
  "/pdf-to-image",
  "/rotate",
  "/protect",
  "/unlock",
  "/watermark",
  "/sign",
  "/pdf-to-word",
  "/ocr",
  "/pdf-to-excel",
  "/faq",
  "/privacy",
]);

export function isLocale(value: string): value is Locale {
  return (locales as readonly string[]).includes(value);
}

interface AcceptLanguageEntry {
  tag: string;
  q: number;
}

export function parseAcceptLanguage(header: string | null | undefined): string[] {
  if (!header || header.trim() === "") {
    return [];
  }
  const entries: AcceptLanguageEntry[] = [];
  for (const part of header.split(",")) {
    const segments = part.split(";");
    const tag = segments[0]?.trim().toLowerCase();
    if (!tag || tag === "*") {
      continue;
    }
    let q = 1;
    for (const segment of segments.slice(1)) {
      const [key, value] = segment.trim().toLowerCase().split("=");
      if (key === "q" && value !== undefined) {
        const parsed = Number.parseFloat(value);
        if (Number.isFinite(parsed)) {
          q = parsed;
        }
      }
    }
    if (q > 0) {
      entries.push({ tag: tag.split("-")[0], q });
    }
  }
  return entries.sort((a, b) => b.q - a.q).map((entry) => entry.tag);
}

// R-15 §8 order: persisted valid preference, then Accept-Language, then EN.
export function resolveLocale(
  preference: string | null | undefined,
  acceptLanguage: string | null | undefined,
): Locale {
  if (preference !== undefined && preference !== null && isLocale(preference)) {
    return preference;
  }
  for (const tag of parseAcceptLanguage(acceptLanguage)) {
    if (isLocale(tag)) {
      return tag;
    }
  }
  return defaultLocale;
}

// Two-letter ISO-639-1-shaped prefixes that are not supported locales (e.g. /fr)
// are locale-like: they are stripped so the request resolves under EN without loops.
const LOCALE_LIKE_PREFIX = /^[A-Za-z]{2}$/;

export function getLocaleRedirectPath(pathname: string, locale: Locale): string | null {
  const segments = pathname.split("/").filter((segment) => segment.length > 0);
  const first = segments[0];
  if (first !== undefined && isLocale(first)) {
    return null;
  }
  if (first !== undefined && LOCALE_LIKE_PREFIX.test(first)) {
    const rest = segments.slice(1).join("/");
    return rest === "" ? `/${locale}` : `/${locale}/${rest}`;
  }
  return pathname === "/" ? `/${locale}` : `/${locale}${pathname}`;
}
