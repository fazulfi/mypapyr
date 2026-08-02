import { describe, expect, it } from "vitest";

import {
  LEGACY_ROUTING_PATHS,
  LOCALE_COOKIE,
  defaultLocale,
  getLocaleRedirectPath,
  isLocale,
  locales,
  parseAcceptLanguage,
  resolveLocale,
} from "../i18n";

describe("SH-01 i18n locale model", () => {
  it("exposes the canonical supported locale list with English default", () => {
    expect(locales).toEqual(["en", "es", "id"]);
    expect(defaultLocale).toBe("en");
  });

  it("exposes the persisted preference cookie name", () => {
    expect(LOCALE_COOKIE).toBe("papyr_locale");
  });

  it("validates supported locales and rejects everything else", () => {
    for (const locale of locales) {
      expect(isLocale(locale)).toBe(true);
    }
    expect(isLocale("fr")).toBe(false);
    expect(isLocale("EN")).toBe(false);
    expect(isLocale("en-US")).toBe(false);
    expect(isLocale("")).toBe(false);
  });
});

describe("SH-01 parseAcceptLanguage", () => {
  it("returns an empty list for missing or empty headers", () => {
    expect(parseAcceptLanguage(null)).toEqual([]);
    expect(parseAcceptLanguage(undefined)).toEqual([]);
    expect(parseAcceptLanguage("")).toEqual([]);
    expect(parseAcceptLanguage("   ")).toEqual([]);
  });

  it("ignores the wildcard language tag", () => {
    expect(parseAcceptLanguage("*")).toEqual([]);
    expect(parseAcceptLanguage("fr, *;q=0.5")).toEqual(["fr"]);
  });

  it("orders candidates by descending q-value", () => {
    expect(parseAcceptLanguage("en;q=0.4, es;q=0.9, id;q=0.7")).toEqual(["es", "id", "en"]);
  });

  it("keeps document order for equal q-values", () => {
    expect(parseAcceptLanguage("es, en, id")).toEqual(["es", "en", "id"]);
  });

  it("extracts the primary subtag and lowercases it", () => {
    expect(parseAcceptLanguage("EN-US, de-DE")).toEqual(["en", "de"]);
  });

  it("drops q=0 candidates as unacceptable", () => {
    expect(parseAcceptLanguage("es;q=0, en;q=0.8")).toEqual(["en"]);
  });

  it("defaults missing q-values to 1", () => {
    expect(parseAcceptLanguage("es;quality=0.2, en")).toEqual(["es", "en"]);
  });

  it("skips malformed entries without throwing", () => {
    expect(parseAcceptLanguage(";q=0.5, , en;q=0.8")).toEqual(["en"]);
  });
});

describe("SH-01 resolveLocale", () => {
  it("falls back to the default locale with no inputs", () => {
    expect(resolveLocale(null, null)).toBe("en");
    expect(resolveLocale(undefined, undefined)).toBe("en");
  });

  it("honors a persisted valid preference over the accept-language header", () => {
    expect(resolveLocale("id", "es;q=0.9, en;q=0.5")).toBe("id");
    expect(resolveLocale("en", "es;q=0.9, en;q=0.5")).toBe("en");
  });

  it("ignores an invalid persisted preference and uses the header", () => {
    expect(resolveLocale("fr", "es;q=0.9, en;q=0.5")).toBe("es");
  });

  it("picks the highest-q supported candidate from accept-language", () => {
    expect(resolveLocale(null, "fr;q=0.9, es;q=0.8, en;q=0.7")).toBe("es");
    expect(resolveLocale(null, "en;q=0.4, es;q=0.9")).toBe("es");
  });

  it("handles region-tagged accept-language entries", () => {
    expect(resolveLocale(null, "en-US")).toBe("en");
  });

  it("falls back to the default locale for unsupported languages", () => {
    expect(resolveLocale(null, "fr;q=0.9")).toBe("en");
    expect(resolveLocale(null, "de, fr")).toBe("en");
  });
});

describe("SH-01 getLocaleRedirectPath", () => {
  it("prefixes the bare root with the resolved locale", () => {
    expect(getLocaleRedirectPath("/", "en")).toBe("/en");
    expect(getLocaleRedirectPath("/", "es")).toBe("/es");
    expect(getLocaleRedirectPath("/", "id")).toBe("/id");
  });

  it("returns null for already-prefixed paths", () => {
    expect(getLocaleRedirectPath("/en", "en")).toBeNull();
    expect(getLocaleRedirectPath("/es/compress-pdf", "en")).toBeNull();
    expect(getLocaleRedirectPath("/id/kompres-pdf", "en")).toBeNull();
  });

  it("strips unsupported two-letter locale-like prefixes", () => {
    expect(getLocaleRedirectPath("/fr", "en")).toBe("/en");
    expect(getLocaleRedirectPath("/fr/foo", "en")).toBe("/en/foo");
    expect(getLocaleRedirectPath("/xy", "en")).toBe("/en");
    expect(getLocaleRedirectPath("/xy/deep", "en")).toBe("/en/deep");
  });

  it("prefixes locale-less application paths while keeping the slug", () => {
    expect(getLocaleRedirectPath("/compress-pdf", "en")).toBe("/en/compress-pdf");
    expect(getLocaleRedirectPath("/jpg-to-pdf", "id")).toBe("/id/jpg-to-pdf");
  });

  it("keeps non-locale-like unknown paths intact under the resolved locale", () => {
    expect(getLocaleRedirectPath("/foo", "en")).toBe("/en/foo");
    expect(getLocaleRedirectPath("/foo/bar", "id")).toBe("/id/foo/bar");
  });
});

describe("SH-01 legacy routing paths", () => {
  it("excludes every legacy tool, faq and privacy path from locale prefixing", () => {
    const expected = [
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
    ];
    expect([...LEGACY_ROUTING_PATHS]).toEqual(expected);
    expect(LEGACY_ROUTING_PATHS.has("/compress-pdf")).toBe(false);
  });
});
