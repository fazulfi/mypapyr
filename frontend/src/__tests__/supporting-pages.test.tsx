vi.mock("@vercel/analytics/next", () => ({
  Analytics: () => null,
}));
vi.mock("@vercel/speed-insights/next", () => ({
  SpeedInsights: () => null,
}));
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/font/google", () => ({
  DM_Sans: vi.fn(() => ({
    className: "dm-sans-class",
    style: { fontFamily: "var(--font-dm-sans)" },
    variable: "--font-dm-sans",
  })),
}));

vi.mock("next/navigation", () => ({
  notFound: vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
  usePathname: vi.fn(() => "/en"),
}));

import { notFound } from "next/navigation";

import { resolveSupportingPageCopy } from "../components/supporting-page";
import LocaleLayout from "../app/[locale]/layout";
import BlogPage from "../app/[locale]/blog/page";
import ContactPage from "../app/[locale]/contact/page";
import CookiesAdvertisingPage from "../app/[locale]/cookies-advertising/page";
import RoadmapPage from "../app/[locale]/roadmap/page";
import StatusPage from "../app/[locale]/status/page";
import TermsPage from "../app/[locale]/terms/page";

import { locales } from "../lib/i18n";
import { getMessages, messages } from "../lib/messages";

function escapeText(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

const supportingPages = [
  { route: "terms", key: "terms", Component: TermsPage },
  { route: "cookies-advertising", key: "cookiesAdvertising", Component: CookiesAdvertisingPage },
  { route: "contact", key: "contact", Component: ContactPage },
  { route: "status", key: "status", Component: StatusPage },
  { route: "roadmap", key: "roadmap", Component: RoadmapPage },
  { route: "blog", key: "blog", Component: BlogPage },
] as const;

type PageEntry = (typeof supportingPages)[number];

const pageKeys = supportingPages.map((entry) => entry.key);

async function renderPage(Component: PageEntry["Component"], locale: string): Promise<string> {
  const tree = await Component({ params: Promise.resolve({ locale }) });
  return renderToStaticMarkup(tree);
}

describe("SH-08 supporting surface shells", () => {
  it("resolves every supporting surface under every locale with a shell heading", async () => {
    for (const { Component, key } of supportingPages) {
      for (const locale of locales) {
        const markup = await renderPage(Component, locale);
        const title = getMessages(locale).pages[key].title;
        // renderToStaticMarkup escapes HTML entities, so match the escaped version.
        const escapedTitle = title
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");
        // Contact is a rich page and renders the title inside a classed h1;
        // assert the heading text is present in the first h1 rather than
        // relying on the byte-exact shell markup.
        const h1 = markup.match(/<h1[^>]*>([^<]*)<\/h1>/);
        expect(h1).not.toBeNull();
        expect(h1![1]).toContain(escapedTitle);
      }
    }
  });

  it("renders exactly one h1 per shell page in every locale", async () => {
    for (const { Component } of supportingPages) {
      for (const locale of locales) {
        const markup = await renderPage(Component, locale);
        expect(markup.match(/<h1/g)).toHaveLength(1);
      }
    }
  });

  it("renders the localized factual scope statement", async () => {
    for (const { Component, key } of supportingPages) {
      for (const locale of locales) {
        const markup = await renderPage(Component, locale);
        expect(markup).toContain(getMessages(locale).pages[key].description);
      }
    }
  });

  it("renders no nested main element inside the shell pages", async () => {
    for (const { Component } of supportingPages) {
      for (const locale of locales) {
        const markup = await renderPage(Component, locale);
        expect(markup).not.toContain("<main");
      }
    }
  });

  it("renders no placeholder hash links", async () => {
    for (const { Component } of supportingPages) {
      for (const locale of locales) {
        const markup = await renderPage(Component, locale);
        expect(markup).not.toMatch(/href="#"/);
        expect(markup).not.toContain('href="#');
      }
    }
  });

  it("sits inside the shared main wrapper with exactly one main when composed with the layout", async () => {
    for (const { Component } of supportingPages) {
      for (const locale of locales) {
        const pageElement = await Component({ params: Promise.resolve({ locale }) });
        const shell = await LocaleLayout({
          children: pageElement,
          params: Promise.resolve({ locale }),
        });
        const markup = renderToStaticMarkup(shell);
        expect(markup.match(/<main/g)).toHaveLength(1);
        expect(markup).toContain('id="main-content"');
      }
    }
  });

  it("composes the locale-aware Navbar before main and Footer after main for every surface", async () => {
    for (const { Component } of supportingPages) {
      for (const locale of locales) {
        const copy = getMessages(locale);
        const pageElement = await Component({ params: Promise.resolve({ locale }) });
        const shell = await LocaleLayout({
          children: pageElement,
          params: Promise.resolve({ locale }),
        });
        const markup = renderToStaticMarkup(shell);
        const nav = markup.indexOf("<nav");
        const main = markup.indexOf("<main");
        const mainClose = markup.indexOf("</main>");
        const footer = markup.lastIndexOf("<footer");
        expect(nav).toBeGreaterThan(-1);
        expect(nav).toBeLessThan(main);
        expect(footer).toBeGreaterThan(mainClose);
        expect(markup).toContain(copy.a11y.languageSwitcher);
        expect(markup).toContain(copy.footer.copyright);
      }
    }
  });

  it("rejects unsupported locales via notFound for every surface", async () => {
    for (const { Component } of supportingPages) {
      await expect(renderPage(Component, "fr")).rejects.toThrow("NEXT_NOT_FOUND");
      expect(notFound).toHaveBeenCalled();
    }
  });
});

describe("SH-08 shared supporting-page contract", () => {
  it("renders every route (except contact, status) with the shared heading and copy", async () => {
    for (const { Component, key } of supportingPages) {
      if (key === "contact" || key === "status") continue; // rich/custom pages
      for (const locale of locales) {
        const copy = getMessages(locale).pages[key];
        const pageMarkup = await renderPage(Component, locale);
        expect(pageMarkup).toContain(escapeText(copy.title));
        expect(pageMarkup).toContain(escapeText(copy.description));
      }
    }
  });

  it("renders an ad banner on ad-carrying supporting pages (owner decision 2026-08-15)", async () => {
    for (const { Component, key } of supportingPages) {
      if (!["privacy", "terms", "cookies-advertising", "roadmap"].includes(key)) continue;
      const pageMarkup = await renderPage(Component, "en");
      expect(pageMarkup).toContain('aria-label="Advertisement"');
    }
  });

  it("resolves localized copy through the shared contract helper for every key and locale", async () => {
    for (const key of pageKeys) {
      for (const locale of locales) {
        const copy = await resolveSupportingPageCopy(Promise.resolve({ locale }), key);
        const page = getMessages(locale).pages[key];
        expect(copy.title).toBe(page.title);
        expect(copy.description).toBe(page.description);
        expect(copy.adLabel).toBe(getMessages(locale).ads.label);
      }
    }
  });

  it("rejects unsupported locales through the shared contract helper", async () => {
    await expect(
      resolveSupportingPageCopy(Promise.resolve({ locale: "fr" }), "privacy"),
    ).rejects.toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });
});

describe("SH-08 page-shell message resources", () => {
  it("defines title and description copy for all seven surfaces in every locale", () => {
    for (const locale of locales) {
      for (const key of pageKeys) {
        const copy = messages[locale].pages[key];
        expect(copy.title.trim()).not.toBe("");
        expect(copy.description.trim()).not.toBe("");
      }
    }
  });

  it("localizes the shell headings per locale", () => {
    // English, Spanish, and Indonesian all use the loanword "Blog"; Indonesian
    // additionally shares the English "Status".
    const sharedHeadings = new Set(["blog"]);
    const sharedIdHeadings = new Set(["status", "blog"]);
    for (const key of pageKeys) {
      const en = messages.en.pages[key].title;
      const es = messages.es.pages[key].title;
      const id = messages.id.pages[key].title;
      if (!sharedHeadings.has(key)) {
        expect(es).not.toBe(en);
      }
      if (!sharedIdHeadings.has(key)) {
        expect(id).not.toBe(en);
      }
    }
  });

  it("localizes the scope statements per locale", () => {
    for (const key of pageKeys) {
      const en = messages.en.pages[key].description;
      expect(messages.es.pages[key].description).not.toBe(en);
      expect(messages.id.pages[key].description).not.toBe(en);
    }
  });

  it("keeps legal and supporting scope statements free of shell wording", () => {
    for (const key of ["terms", "status", "roadmap", "blog"] as const) {
      expect(messages.en.pages[key].description).not.toContain("informational shell");
      expect(messages.en.pages[key].description).not.toContain("later phase");
      expect(messages.es.pages[key].description).not.toContain("marco informativo");
      expect(messages.es.pages[key].description).not.toContain("fase posterior");
      expect(messages.id.pages[key].description).not.toContain("kerangka informasi");
      expect(messages.id.pages[key].description).not.toContain("fase berikutnya");
    }
  });

  it("describes shipped pages with accurate scope statements", () => {
    for (const key of ["terms", "contact", "cookiesAdvertising"] as const) {
      expect(messages.en.pages[key].description).not.toContain("informational shell");
      expect(messages.en.pages[key].description).not.toContain("later phase");
    }
    expect(messages.en.pages.contact.description).toContain("contact form");
    expect(messages.en.pages.cookiesAdvertising.description).toContain("Do Not Track");
  });

  it("keeps page copy free of TODO, TBD, placeholder, and lorem markers", () => {
    const markerPattern = /todo|tbd|placeholder|lorem/i;
    for (const locale of locales) {
      for (const key of pageKeys) {
        expect(messages[locale].pages[key].title).not.toMatch(markerPattern);
        expect(messages[locale].pages[key].description).not.toMatch(markerPattern);
      }
    }
  });

  it("keeps page copy free of unproven speed, free, and security claims", () => {
    // Word boundaries avoid false positives such as "aman" inside Indonesian "Halaman".
    const claimPattern =
      /\b(free|fast|instant|secure|gratis|rápido|rapido|instante|seguro|cepat|instan|aman)\b/i;
    for (const locale of locales) {
      for (const key of pageKeys) {
        expect(messages[locale].pages[key].title).not.toMatch(claimPattern);
        expect(messages[locale].pages[key].description).not.toMatch(claimPattern);
      }
    }
  });
});
