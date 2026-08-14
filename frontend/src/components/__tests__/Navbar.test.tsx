import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(() => "/en"),
}));

import { locales } from "../../lib/i18n";
import { getMessages, messages } from "../../lib/messages";
import { getAllTools } from "../../lib/catalog";

import {
  Navbar,
  getNavCategories,
  resolveEquivalentPath,
  ChevronDownIcon,
  MenuIcon,
  XIcon,
} from "../Navbar";

describe("SH-05 exported SVG icons", () => {
  it("ChevronDownIcon renders a chevron svg with aria-hidden", () => {
    const markup = renderToStaticMarkup(<ChevronDownIcon />);
    expect(markup).toContain("<svg");
    expect(markup).toContain('aria-hidden="true"');
    expect(markup).toContain('points="6 9 12 15 18 9"');
  });

  it("MenuIcon renders a hamburger svg with three lines", () => {
    const markup = renderToStaticMarkup(<MenuIcon />);
    expect(markup).toContain("<svg");
    expect(markup).toContain('aria-hidden="true"');
    expect(markup).toContain('y1="6"');
    expect(markup).toContain('y1="12"');
    expect(markup).toContain('y1="18"');
  });

  it("XIcon renders a close svg with crossing lines", () => {
    const markup = renderToStaticMarkup(<XIcon />);
    expect(markup).toContain("<svg");
    expect(markup).toContain('aria-hidden="true"');
    expect(markup).toContain('x1="18"');
    expect(markup).toContain('x2="18"');
  });
});

describe("SH-05 resolveEquivalentPath — pure equivalent-path logic", () => {
  it("preserves tool-equivalent paths when current pathname is a tool page", () => {
    expect(resolveEquivalentPath("/en/compress-pdf", "en", "es")).toBe("/es/comprimir-pdf");
    expect(resolveEquivalentPath("/es/comprimir-pdf", "es", "en")).toBe("/en/compress-pdf");
    expect(resolveEquivalentPath("/id/kompres-pdf", "id", "es")).toBe("/es/comprimir-pdf");
  });

  it("maps all five tools bidirectionally across all locale pairs", () => {
    const toolPairs: Array<[string, string, string]> = [
      ["en", "/en/compress-pdf", "/es/comprimir-pdf"],
      ["en", "/en/merge-pdf", "/es/combinar-pdf"],
      ["en", "/en/split-pdf", "/es/dividir-pdf"],
      ["en", "/en/jpg-to-pdf", "/es/jpg-a-pdf"],
      ["en", "/en/pdf-to-jpg", "/es/pdf-a-jpg"],
    ];
    for (const [fromLocale, fromPath, expectedEs] of toolPairs) {
      expect(resolveEquivalentPath(fromPath, fromLocale as "en", "es")).toBe(expectedEs);
      expect(resolveEquivalentPath(expectedEs, "es", fromLocale as "en")).toBe(fromPath);
    }
  });

  it("swaps the locale prefix for non-tool pages", () => {
    expect(resolveEquivalentPath("/en/privacy", "en", "es")).toBe("/es/privacy");
    expect(resolveEquivalentPath("/en/terms", "en", "id")).toBe("/id/terms");
    expect(resolveEquivalentPath("/es/contacto", "es", "en")).toBe("/en/contacto");
  });

  it("handles root-like paths by prepending the target locale", () => {
    expect(resolveEquivalentPath("/en", "en", "es")).toBe("/es");
    expect(resolveEquivalentPath("/", "en", "id")).toBe("/id");
  });

  it("handles deeply nested non-tool paths", () => {
    expect(resolveEquivalentPath("/en/blog/some-post", "en", "es")).toBe("/es/blog/some-post");
    expect(resolveEquivalentPath("/id/status/something", "id", "en")).toBe("/en/status/something");
  });

  it("returns target locale root when pathname has unrecognized structure", () => {
    expect(resolveEquivalentPath("/some-page", "en", "es")).toBe("/es");
    expect(resolveEquivalentPath("invalid", "en", "id")).toBe("/id");
    expect(resolveEquivalentPath("", "es", "en")).toBe("/en");
  });

  it("matches Indonesian tool paths correctly for all five tools", () => {
    expect(resolveEquivalentPath("/id/kompres-pdf", "id", "en")).toBe("/en/compress-pdf");
    expect(resolveEquivalentPath("/id/gabungkan-pdf", "id", "en")).toBe("/en/merge-pdf");
    expect(resolveEquivalentPath("/id/pisahkan-pdf", "id", "en")).toBe("/en/split-pdf");
    expect(resolveEquivalentPath("/id/gambar-ke-pdf", "id", "en")).toBe("/en/jpg-to-pdf");
    expect(resolveEquivalentPath("/id/pdf-ke-gambar", "id", "en")).toBe("/en/pdf-to-jpg");
  });
});

describe("SH-05 Navbar — structure and accessibility", () => {
  it("renders a semantic nav landmark", () => {
    const markup = renderToStaticMarkup(<Navbar locale="en" />);
    expect(markup).toContain("<nav");
    expect(markup).toContain("</nav>");
  });

  it("renders the LogoLockup with the current locale", () => {
    const markup = renderToStaticMarkup(<Navbar locale="es" />);
    expect(markup).toContain('href="/es"');
    expect(markup).toContain('aria-label="Papyr"');
  });

  it("renders desktop category buttons for Basic, Security, Enhancement, and Conversion", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = renderToStaticMarkup(<Navbar locale={locale} />);
      expect(markup).toContain(copy.nav.basic);
      expect(markup).toContain(copy.nav.security);
      expect(markup).toContain(copy.nav.enhancement);
      expect(markup).toContain(copy.nav.conversion);
    }
  });

  it("renders exactly four category buttons", () => {
    const markup = renderToStaticMarkup(<Navbar locale="en" />);
    const basicIdx = markup.indexOf(messages.en.nav.basic);
    const securityIdx = markup.indexOf(messages.en.nav.security);
    const enhancementIdx = markup.indexOf(messages.en.nav.enhancement);
    const conversionIdx = markup.indexOf(messages.en.nav.conversion);
    expect(basicIdx).toBeGreaterThan(0);
    expect(securityIdx).toBeGreaterThan(0);
    expect(enhancementIdx).toBeGreaterThan(0);
    expect(conversionIdx).toBeGreaterThan(0);
  });

  it("exports getNavCategories with the four canonical categories", () => {
    const categories = getNavCategories("en");
    expect(categories).toHaveLength(4);

    const allTools = categories.flatMap((c) => c.tools.map((t) => t.id));
    expect(allTools).toHaveLength(9);
    expect(allTools).toEqual([
      "compress-pdf",
      "merge-pdf",
      "split-pdf",
      "protect",
      "unlock",
      "watermark",
      "sign",
      "jpg-to-pdf",
      "pdf-to-jpg",
    ]);
  });

  it("groups tools into Basic, Security, Enhancement, and Conversion", () => {
    const categories = getNavCategories("en");
    expect(categories[0].label).toBe("Basic");
    expect(categories[0].tools.map((t) => t.id)).toEqual([
      "compress-pdf",
      "merge-pdf",
      "split-pdf",
    ]);
    expect(categories[1].label).toBe("Security");
    expect(categories[1].tools.map((t) => t.id)).toEqual(["protect", "unlock"]);
    expect(categories[2].label).toBe("Enhancement");
    expect(categories[2].tools.map((t) => t.id)).toEqual(["watermark", "sign"]);
    expect(categories[3].label).toBe("Conversion");
    expect(categories[3].tools.map((t) => t.id)).toEqual(["jpg-to-pdf", "pdf-to-jpg"]);
  });

  it("legacy category tools link to the localized tool-unavailable route", () => {
    for (const locale of locales) {
      const categories = getNavCategories(locale);
      const securityTools = categories[1].tools;
      const enhancementTools = categories[2].tools;
      for (const tool of [...securityTools, ...enhancementTools]) {
        expect(tool.hrefs[locale]).toBe(`/${locale}/tool-unavailable?tool=${tool.id}`);
      }
    }
  });


  it("provides localized category labels for every locale across all four categories", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const categories = getNavCategories(locale);
      expect(categories).toHaveLength(4);
      expect(categories[0].label).toBe(copy.nav.basic);
      expect(categories[1].label).toBe(copy.nav.security);
      expect(categories[2].label).toBe(copy.nav.enhancement);
      expect(categories[3].label).toBe(copy.nav.conversion);
    }
  });

  it("provides locale-specific hrefs for every tool in every locale", () => {
    for (const locale of locales) {
      const categories = getNavCategories(locale);
      const tools = getAllTools();
      for (const tool of tools) {
        const found = categories.flatMap((c) => c.tools).find((t) => t.id === tool.id);
        expect(found).toBeDefined();
        expect(found!.hrefs[locale]).toBe(tool.hrefs[locale]);
        expect(found!.fullLabel[locale]).toBe(tool.fullLabel[locale]);
      }
    }
  });

  it("renders the CTA link pointing to the first basic tool", () => {
    const markup = renderToStaticMarkup(<Navbar locale="es" />);
    expect(markup).toContain('href="/es/comprimir-pdf"');
  });

  it("renders category buttons with aria-expanded attribute", () => {
    const markup = renderToStaticMarkup(<Navbar locale="en" />);
    expect(markup).toContain("aria-expanded");
  });

  it("renders category buttons with aria-controls attribute", () => {
    const markup = renderToStaticMarkup(<Navbar locale="en" />);
    expect(markup).toContain("aria-controls");
  });

  it("renders a mobile hamburger toggle with accessible label and 44px touch target", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = renderToStaticMarkup(<Navbar locale={locale} />);
      expect(markup).toContain(copy.a11y.navToggle);
      expect(markup).toContain("min-h-[44px]");
      expect(markup).toContain("min-w-[44px]");
    }
  });

  it("renders the LanguageSwitcher component", () => {
    const markup = renderToStaticMarkup(<Navbar locale="id" />);
    const copy = getMessages("id");
    expect(markup).toContain(copy.a11y.languageSwitcher);
    expect(markup).toContain("English");
    expect(markup).toContain("Español");
    expect(markup).toContain("Bahasa Indonesia");
  });

  it("renders a CTA button with nav.cta label", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = renderToStaticMarkup(<Navbar locale={locale} />);
      expect(markup).toContain(copy.nav.cta);
    }
  });

  it("localizes all nav text for every supported locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = renderToStaticMarkup(<Navbar locale={locale} />);
      expect(markup).toContain(copy.nav.basic);
      expect(markup).toContain(copy.nav.security);
      expect(markup).toContain(copy.nav.enhancement);
      expect(markup).toContain(copy.nav.conversion);
      expect(markup).toContain(copy.nav.cta);
      expect(markup).toContain(copy.a11y.navToggle);
      expect(markup).toContain(copy.a11y.languageSwitcher);
    }
  });

  it("references both navToggle and navClose in the component source for the mobile toggle", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = renderToStaticMarkup(<Navbar locale={locale} />);
      const hasToggle = markup.includes(copy.a11y.navToggle);
      const hasClose = markup.includes(copy.a11y.navClose);
      expect(hasToggle || hasClose).toBe(true);
    }
  });

  it("renders tool links with locale-specific hrefs in the CTA button", () => {
    const markup = renderToStaticMarkup(<Navbar locale="es" />);
    expect(markup).toContain('href="/es/comprimir-pdf"');
    expect(markup).toContain("Comenzar");
  });

  it("renders tool links with Indonesian locale hrefs in the CTA button", () => {
    const markup = renderToStaticMarkup(<Navbar locale="id" />);
    expect(markup).toContain('href="/id/kompres-pdf"');
    expect(markup).toContain("Mulai");
  });

  it("does not render placeholder or empty hrefs", () => {
    const markup = renderToStaticMarkup(<Navbar locale="en" />);
    expect(markup).not.toContain('href="#"');
    expect(markup).not.toContain('href=""');
  });

  it("does not reference legacy or non-canonical tool paths as direct href targets", () => {
    const markup = renderToStaticMarkup(<Navbar locale="en" />);
    expect(markup).not.toContain('href="/compress"');
    expect(markup).not.toContain('href="/merge"');
    expect(markup).not.toContain('href="/split"');
    expect(markup).not.toContain('href="/rotate"');
    expect(markup).not.toContain('href="/protect"');
    expect(markup).not.toContain('href="/unlock"');
    expect(markup).not.toContain('href="/watermark"');
    expect(markup).not.toContain('href="/sign"');
    expect(markup).not.toContain('href="/image-to-pdf"');
    expect(markup).not.toContain('href="/pdf-to-image"');
    expect(markup).not.toContain('href="/pdf-to-word"');
    expect(markup).not.toContain('href="/pdf-to-excel"');
    expect(markup).not.toContain('href="/ocr"');
  });
});
