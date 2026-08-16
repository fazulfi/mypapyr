import { describe, expect, it } from "vitest";

import sitemap, { BASE_URL } from "../sitemap";
import robots from "../robots";
import { toolCatalog } from "../../lib/catalog";
import { LEGACY_ROUTING_PATHS } from "../../lib/i18n";

describe("T8 sitemap", () => {
  it("uses the canonical production base URL", () => {
    expect(BASE_URL).toBe("https://budgezen.com");
    for (const entry of sitemap()) {
      expect(entry.url.startsWith(BASE_URL)).toBe(true);
    }
  });

  it("contains exactly 17 URLs", () => {
    const entries = sitemap();
    expect(entries).toHaveLength(17);
  });

  it("leads with the homepage at priority 1", () => {
    const entries = sitemap();
    expect(entries[0].url).toBe(`${BASE_URL}`);
    expect(entries[0].priority).toBe(1);
  });

  it("includes the tool-unavailable base page", () => {
    const urls = sitemap().map((entry) => entry.url);
    expect(urls).toContain(`${BASE_URL}/tool-unavailable`);
  });

  it("includes all five active tool EN slugs", () => {
    const urls = sitemap().map((entry) => entry.url);
    for (const tool of toolCatalog) {
      expect(urls).toContain(`${BASE_URL}${tool.hrefs.en}`);
    }
  });

  it("includes the 8 deferred legacy tool URLs as tool-unavailable pages", () => {
    const urls = sitemap().map((entry) => entry.url);
    const legacyIds = [
      "rotate",
      "protect",
      "unlock",
      "watermark",
      "sign",
      "pdf-to-word",
      "ocr",
      "pdf-to-excel",
    ];
    expect(legacyIds).toHaveLength(8);
    for (const id of legacyIds) {
      expect(urls).toContain(`${BASE_URL}/tool-unavailable?tool=${id}`);
    }
  });

  it("includes /faq and /privacy entries", () => {
    const urls = sitemap().map((entry) => entry.url);
    expect(urls).toContain(`${BASE_URL}/faq`);
    expect(urls).toContain(`${BASE_URL}/privacy`);
  });

  it("does not include legacy locale-less tool routes directly (410-excluded per DEC-194)", () => {
    const urls = sitemap().map((entry) => entry.url);
    for (const path of LEGACY_ROUTING_PATHS) {
      // /faq and /privacy are the only non-tool legacy paths that are canonical
      if (path === "/faq" || path === "/privacy") {
        continue;
      }
      expect(urls).not.toContain(`${BASE_URL}${path}`);
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
