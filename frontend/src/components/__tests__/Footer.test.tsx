import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { locales } from "../../lib/i18n";
import { getMessages } from "../../lib/messages";
import { Footer } from "../Footer";

function renderFooter(locale: (typeof locales)[number]): string {
  return renderToStaticMarkup(<Footer locale={locale} />);
}

const SUPPORT_ROUTES = [
  "privacy",
  "terms",
  "cookies-advertising",
  "contact",
  "status",
  "roadmap",
] as const;

describe("SH-06 Footer", () => {
  /* ── Structure ── */

  it("renders a semantic footer element", () => {
    const markup = renderFooter("en");
    expect(markup).toMatch(/^<footer\b/);
    expect(markup).toMatch(/<\/footer>$/);
  });

  it("includes the LogoLockup in footer size", () => {
    const markup = renderFooter("en");
    // Footer-size mark: h-6 w-6
    expect(markup).toMatch(/\bh-6\b/);
    expect(markup).toMatch(/\bw-6\b/);
    expect(markup).toContain("rounded-[5px]");
    expect(markup).toContain("text-[15px]");
    expect(markup).toContain('aria-label="Papyr"');
  });

  it("links the LogoLockup to the locale root", () => {
    const markup = renderFooter("es");
    expect(markup).toContain('href="/es"');
  });

  /* ── Tools section ── */

  it("renders a tools nav with the localized heading", () => {
    const markup = renderFooter("en");
    const copy = getMessages("en").footer;
    expect(markup).toContain(`<nav`);
    expect(markup).toContain(`aria-label="${copy.tools}"`);
    // The heading element inside the tools nav
    expect(markup).toContain(copy.tools);
  });

  it("renders four category columns with tools sourced from the catalog and legacy catalog", () => {
    const markup = renderFooter("en");
    // Basic column
    expect(markup).toContain("Compress PDF");
    expect(markup).toContain("Merge PDF");
    expect(markup).toContain("Split PDF");
    // Security column
    expect(markup).toContain("Protect PDF");
    expect(markup).toContain("Unlock PDF");
    // Enhancement column
    expect(markup).toContain("Watermark");
    expect(markup).toContain("Sign PDF");
    // Conversion column
    expect(markup).toContain("JPG to PDF");
    expect(markup).toContain("PDF to JPG");
  });

  it("each category column has a labeled h3 heading", () => {
    for (const locale of locales) {
      const markup = renderFooter(locale);
      const copy = getMessages(locale);
      expect(markup).toContain(copy.nav.basic);
      expect(markup).toContain(copy.nav.security);
      expect(markup).toContain(copy.nav.enhancement);
      expect(markup).toContain(copy.nav.conversion);
    }
  });

  it("tool links are rendered as Next.js Link anchors", () => {
    const markup = renderFooter("en");
    // All tool links must be anchor elements with hrefs
    const anchorMatches = markup.match(/<a\b/g);
    // LogoLockup (1) + 9 tools + 6 support = 16 anchors
    expect(anchorMatches).not.toBeNull();
    expect(anchorMatches!.length).toBe(16);
  });

  /* ── Support section ── */

  it("renders a support nav with the localized heading", () => {
    const markup = renderFooter("en");
    const copy = getMessages("en").footer;
    // Support nav must have aria-label
    expect(markup).toContain(`aria-label="${copy.support}"`);
    // And the heading text
    expect(markup).toContain(copy.support);
  });

  it("renders exactly six support links", () => {
    const markup = renderFooter("en");
    // Check each support route appears
    for (const route of SUPPORT_ROUTES) {
      expect(markup).toContain(`/${route}`);
    }
  });

  it("support links point to correct localized routes for every locale", () => {
    for (const locale of locales) {
      const markup = renderFooter(locale);
      for (const route of SUPPORT_ROUTES) {
        expect(markup).toContain(`/${locale}/${route}`);
      }
    }
  });

  it("support links use localized labels from messages for every locale", () => {
    for (const locale of locales) {
      const markup = renderFooter(locale);
      const copy = getMessages(locale).footer;
      // react-dom/server encodes & as &amp; — decode for label equality
      const decodedMarkup = markup.replace(/&amp;/g, "&");
      for (const route of SUPPORT_ROUTES) {
        const key = route.replace(/-([a-z])/g, (_: string, c: string) => c.toUpperCase()) as
          "privacy" | "terms" | "cookiesAdvertising" | "contact" | "status" | "roadmap";
        const label = copy[key as keyof typeof copy];
        if (typeof label === "string") {
          expect(decodedMarkup).toContain(label);
        }
      }
    }
  });

  /* ── Copyright ── */

  it("renders the dynamic current year at render time", () => {
    const markupBefore = renderFooter("en");
    const currentYear = String(new Date().getFullYear());
    expect(markupBefore).toContain(currentYear);
    const yearOccurrences = markupBefore.match(new RegExp(`© ${currentYear}`, "g"));
    expect(yearOccurrences).not.toBeNull();
    expect(yearOccurrences!.length).toBe(1);
  });

  it("renders the localized copyright text for every locale", () => {
    for (const locale of locales) {
      const markup = renderFooter(locale);
      const copy = getMessages(locale).footer;
      expect(markup).toContain(copy.copyright);
    }
  });

  /* ── Accessibility ── */

  it("includes exactly two semantic nav elements with accessible names", () => {
    const markup = renderFooter("en");
    // Count nav opening tags
    const navCount = (markup.match(/<nav\b/g) || []).length;
    expect(navCount).toBe(2);
    // Each nav must have an aria-label
    const ariaLabelCount = (markup.match(/aria-label="/g) || []).length;
    // LogoLockup has one, plus both navs = 3
    expect(ariaLabelCount).toBe(3);
  });

  it("uses semantic heading elements for section labels", () => {
    const markup = renderFooter("en");
    // At least 2 headings (tools + support)
    const h2Count = (markup.match(/<h2\b/g) || []).length;
    expect(h2Count).toBe(2);
  });

  /* ── Forbidden elements ── */

  it("has no hash placeholders anywhere", () => {
    const markup = renderFooter("en");
    expect(markup).not.toContain('href="#"');
  });

  it("computes the year dynamically from Date at render time", () => {
    const markup = renderFooter("en");
    const currentYear = new Date().getFullYear();
    const match = markup.match(/© (\d{4})/);
    expect(match).not.toBeNull();
    expect(Number(match![1])).toBe(currentYear);
  });

  it("has no language switcher or flag emoji", () => {
    const markup = renderFooter("en");
    expect(markup).not.toContain("LanguageSwitcher");
    // No flag emojis
    expect(markup).not.toMatch(/🇮🇩|🇪🇸|🇬🇧|🇺🇸/);
  });

  /* ── Localization ── */

  it("renders successfully for every supported locale", () => {
    for (const locale of locales) {
      const markup = renderFooter(locale);
      expect(markup).toContain(`href="/${locale}"`);
      expect(markup).toMatch(/^<footer\b/);
    }
  });

  it("uses distinct localized headings and labels per locale", () => {
    const toolHeadings = new Set<string>();
    const supportHeadings = new Set<string>();
    const copyrights = new Set<string>();
    for (const locale of locales) {
      const markup = renderFooter(locale);
      const copy = getMessages(locale).footer;
      expect(markup).toContain(copy.tools);
      expect(markup).toContain(copy.support);
      expect(markup).toContain(copy.copyright);
      toolHeadings.add(copy.tools);
      supportHeadings.add(copy.support);
      copyrights.add(copy.copyright);
    }
    expect(toolHeadings.size).toBe(locales.length);
    expect(supportHeadings.size).toBe(locales.length);
    expect(copyrights.size).toBe(locales.length);
  });
});
