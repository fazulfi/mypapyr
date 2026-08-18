import { describe, expect, it } from "vitest";

import {
  SEO_BASE_URL,
  absoluteHref,
  alternateLinks,
  supportingAlternates,
  supportingPaths,
  type AlternateLinks,
} from "../seo/alternates";
import { locales } from "../i18n";
import { toolCatalog } from "../catalog";

const CANONICAL_HOST = "https://budgezen.com";

describe("SEO-03 / P8-E seo-alternates helper", () => {
  it("anchors the single canonical SEO origin at budgezen.com", () => {
    expect(SEO_BASE_URL).toBe(CANONICAL_HOST);
  });

  it("builds absolute locale-prefixed hrefs via absoluteHref", () => {
    expect(absoluteHref("en", "")).toBe(`${CANONICAL_HOST}/en`);
    expect(absoluteHref("es", "/faq")).toBe(`${CANONICAL_HOST}/es/faq`);
    expect(absoluteHref("id", "/compress-pdf")).toBe(`${CANONICAL_HOST}/id/compress-pdf`);
  });

  it("builds supporting-route path maps as per-locale slugs", () => {
    const paths = supportingPaths("faq");
    expect(paths).toEqual({ en: "/en/faq", es: "/es/faq", id: "/id/faq" });
    for (const locale of locales) {
      expect(paths[locale].startsWith(`/${locale}/`)).toBe(true);
    }
  });

  it("emits a self-referencing canonical for every locale in a path map", () => {
    const paths = { en: "/en/compress-pdf", es: "/es/comprimir-pdf", id: "/id/kompres-pdf" };
    for (const locale of locales) {
      const links = alternateLinks(locale, paths);
      expect(links.canonical).toBe(`${CANONICAL_HOST}${paths[locale]}`);
    }
  });

  it("emits bidirectional hreflang for en/es/id with x-default to EN", () => {
    const links = alternateLinks("es", {
      en: "/en/compress-pdf",
      es: "/es/comprimir-pdf",
      id: "/id/kompres-pdf",
    });
    expect(links.languages.en).toBe(`${CANONICAL_HOST}/en/compress-pdf`);
    expect(links.languages.es).toBe(`${CANONICAL_HOST}/es/comprimir-pdf`);
    expect(links.languages.id).toBe(`${CANONICAL_HOST}/id/kompres-pdf`);
    expect(links.languages["x-default"]).toBe(links.languages.en);
  });

  it("never introduces es-419 or other-host leakage", () => {
    for (const tool of toolCatalog) {
      for (const locale of locales) {
        const links = alternateLinks(locale, tool.hrefs);
        const raw = JSON.stringify(links);
        expect(raw).not.toContain("es-419");
        expect(raw).not.toContain("mypapyr.com");
        expect(raw).not.toContain("http://");
        expect(raw).not.toMatch(/(?:https:\/\/)(?!budgezen\.com)/);
      }
    }
  });

  it("keeps every canonical inside its own language set (self-reference invariant)", () => {
    for (const tool of toolCatalog) {
      for (const locale of locales) {
        const links = alternateLinks(locale, tool.hrefs);
        expect(Object.values(links.languages)).toContain(links.canonical);
      }
    }
  });

  it("produces deterministic output for identical inputs", () => {
    const paths = supportingPaths("privacy");
    const a: AlternateLinks = alternateLinks("en", paths);
    const b = alternateLinks("en", paths);
    expect(a).toEqual(b);
  });

  it("supports the locale-root home variant", () => {
    const home = { en: "/en", es: "/es", id: "/id" };
    for (const locale of locales) {
      const links = alternateLinks(locale, home);
      expect(links.canonical).toBe(`${CANONICAL_HOST}${home[locale]}`);
      expect(links.languages["x-default"]).toBe(`${CANONICAL_HOST}/en`);
    }
  });

  it("exposes supportingAlternates as per-locale slug alternates", () => {
    const links = supportingAlternates("id", "faq");
    expect(links.canonical).toBe(`${CANONICAL_HOST}/id/faq`);
    expect(links.languages.en).toBe(`${CANONICAL_HOST}/en/faq`);
    expect(links.languages["x-default"]).toBe(`${CANONICAL_HOST}/en/faq`);
  });
});
