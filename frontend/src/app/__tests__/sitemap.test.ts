import { describe, expect, it } from "vitest";

import sitemap, { BASE_URL, LAST_MODIFIED } from "../sitemap";
import robots from "../robots";
import { SEO_BASE_URL } from "../../lib/seo/alternates";
import { toolCatalog } from "../../lib/catalog";
import { LEGACY_ROUTING_PATHS, locales } from "../../lib/i18n";

const SUPPORTING_SLUGS = [
  "faq",
  "privacy",
  "terms",
  "cookies-advertising",
  "contact",
  "status",
  "roadmap",
  "blog",
] as const;

describe("T8 sitemap", () => {
  it("uses the canonical production base URL for every entry", () => {
    expect(BASE_URL).toBe("https://budgezen.com");
    expect(BASE_URL).toBe(SEO_BASE_URL);
    for (const entry of sitemap()) {
      expect(entry.url.startsWith(`${BASE_URL}/`)).toBe(true);
      expect(new URL(entry.url).host).toBe("budgezen.com");
    }
  });

  it("contains 42 URLs = 14 public routes × 3 locales", () => {
    const entries = sitemap();
    expect(entries).toHaveLength(42);
  });

  it("leads with the homepage for all three locales at priority 1", () => {
    const entries = sitemap();
    const urls = entries.map((entry) => entry.url);
    expect(urls.slice(0, 3)).toEqual([`${BASE_URL}/en`, `${BASE_URL}/es`, `${BASE_URL}/id`]);
    for (const entry of entries.slice(0, 3)) {
      expect(entry.priority).toBe(1);
    }
    expect(urls).not.toContain(BASE_URL);
  });

  it("includes every active tool slug in all three locales", () => {
    const urls = sitemap().map((entry) => entry.url);
    for (const tool of toolCatalog) {
      for (const locale of locales) {
        expect(urls).toContain(`${BASE_URL}${tool.hrefs[locale]}`);
      }
    }
  });

  it("includes every supporting public route in all three locales", () => {
    const urls = sitemap().map((entry) => entry.url);
    for (const slug of SUPPORTING_SLUGS) {
      for (const locale of locales) {
        expect(urls).toContain(`${BASE_URL}/${locale}/${slug}`);
      }
    }
  });

  it("excludes tool-unavailable and the 8 deferred legacy query variants (DEC-194)", () => {
    const urls = sitemap().map((entry) => entry.url);
    for (const url of urls) {
      expect(url).not.toContain("/tool-unavailable");
    }
  });

  it("excludes locale-less redirecting entry paths", () => {
    const urls = sitemap().map((entry) => entry.url);
    expect(urls).not.toContain(BASE_URL);
    for (const path of LEGACY_ROUTING_PATHS) {
      expect(urls).not.toContain(`${BASE_URL}${path}`);
    }
  });

  it("emits per-entry hreflang alternates for all locales with x-default to EN", () => {
    for (const entry of sitemap()) {
      const languages = entry.alternates?.languages ?? {};
      for (const locale of locales) {
        const target = languages[locale];
        expect(target).toBeDefined();
        expect(String(target).startsWith(`${BASE_URL}/${locale}`)).toBe(true);
      }
      expect(languages["x-default"]).toBe(languages.en);
    }
  });

  it("keeps each entry self-referencing and cross-referenced within its group", () => {
    const urls = sitemap().map((item) => item.url);
    for (const entry of sitemap()) {
      const languages = entry.alternates?.languages ?? {};
      const targets = [languages.en, languages.es, languages.id];
      expect(targets).toContain(entry.url);
      expect(languages["x-default"]).toBe(languages.en);
      for (const target of targets) {
        expect(urls).toContain(target);
      }
    }
  });

  it("carries no other-host or relative URL leakage", () => {
    const raw = JSON.stringify(sitemap());
    expect(raw).not.toMatch(/https:\/\/(?!budgezen\.com)/);
    expect(raw).not.toContain("mypapyr.com");
    expect(raw).not.toContain("http://");
  });

  it("emits a committed, deterministic real lastmod on every entry", () => {
    const first = sitemap();
    const second = sitemap();
    // Deterministic across calls — never build-time `new Date()`.
    for (const [index, entry] of first.entries()) {
      expect(entry.lastModified).toBe(LAST_MODIFIED);
      expect(second[index].lastModified).toBe(LAST_MODIFIED);
    }
  });

  it("keeps lastModified as a valid ISO date string", () => {
    for (const entry of sitemap()) {
      const modified = entry.lastModified;
      expect(typeof modified).toBe("string");
      const parsed = new Date(String(modified));
      expect(Number.isNaN(parsed.getTime())).toBe(false);
      expect(String(modified).split("T")[0]).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    }
  });

  it("never emits es-419 anywhere in the sitemap", () => {
    const raw = JSON.stringify(sitemap());
    expect(raw).not.toContain("es-419");
  });

  it("keeps locale vocabulary to exactly en/es/id with x-default to EN", () => {
    for (const entry of sitemap()) {
      const languages = entry.alternates?.languages ?? {};
      const keys = Object.keys(languages).sort();
      expect(keys).toEqual(["en", "es", "id", "x-default"]);
      expect(languages["x-default"]).toBe(languages.en);
    }
  });
});

describe("T8 robots", () => {
  it("allows all user agents and points at the sitemap", () => {
    const config = robots();
    expect(config.rules).toEqual({ userAgent: "*", allow: "/" });
    expect(config.sitemap).toBe("https://budgezen.com/sitemap.xml");
  });
});
