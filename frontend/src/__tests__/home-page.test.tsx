import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
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

import LocaleLayout from "../app/[locale]/layout";
import LocaleHomePage from "../app/[locale]/page";
import { getAllTools, getToolById } from "../lib/catalog";
import { locales } from "../lib/i18n";
import { getMessages } from "../lib/messages";

async function renderHome(locale: string): Promise<string> {
  const tree = await LocaleHomePage({ params: Promise.resolve({ locale }) });
  return renderToStaticMarkup(tree);
}

async function renderComposedHome(locale: string): Promise<string> {
  const pageElement = await LocaleHomePage({ params: Promise.resolve({ locale }) });
  const shell = await LocaleLayout({
    children: pageElement,
    params: Promise.resolve({ locale }),
  });
  return renderToStaticMarkup(shell);
}

// SH-07 legacy-catalog hygiene: the thirteen-tool legacy catalog and its
// un-scope-corrected "no tracking" claims must never surface on the homepage
// (DEC-150; UX §11.4; audit-outputs/ui-docs-code-reconciliation.md §8.8).
const LEGACY_TOOL_ROUTES = [
  "/rotate",
  "/protect",
  "/unlock",
  "/watermark",
  "/sign",
  "/pdf-to-word",
  "/ocr",
  "/pdf-to-excel",
  "/image-to-pdf",
  "/pdf-to-image",
] as const;

const LEGACY_TOOL_LABELS = [
  "Rotate",
  "Protect",
  "Unlock",
  "Watermark",
  "Sign",
  "PDF to Word",
  "OCR",
  "PDF to Excel",
  "Putar PDF",
  "Proteksi PDF",
  "Hapus Password",
  "Tambah Watermark",
  "Tanda Tangan",
  "PDF ke Word",
  "PDF ke Excel",
] as const;

function toolCardTags(markup: string): string[] {
  return [...markup.matchAll(/<a\b[^>]*\bdata-tool-id="[^"]+"[^>]*>/g)].map((match) => match[0]);
}

function attribute(tag: string, name: string): string | undefined {
  return tag.match(new RegExp(`\\b${name}="([^"]*)"`))?.[1];
}

// renderToStaticMarkup escapes apostrophes as &#x27;; escape the expected copy
// so visible-text assertions survive HTML serialization.
function escapeText(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/'/g, "&#x27;");
}

// Reduces serialized markup to its visible text so claim scans ignore class
// names and attribute values (e.g. Tailwind tracking-* utilities).
function textContent(markup: string): string {
  return markup
    .replace(/<[^>]+>/g, "")
    .replace(/&#x27;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

describe("SH-07 localized homepage hero", () => {
  it("renders exactly one hero h1 carrying the localized hero copy for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup.match(/<h1/g)).toHaveLength(1);
      expect(markup).toContain(copy.home.hero);
    }
  });

  it("renders the localized hero sub copy for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup).toContain(copy.home.heroSub);
    }
  });

  it("points the primary CTA at the locale Compress PDF route with the canonical CTA label", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const compressHref = getToolById("compress-pdf")?.hrefs[locale];
      expect(compressHref).toBeDefined();
      const markup = await renderHome(locale);
      expect(markup).toContain(`href="${compressHref}"`);
      expect(markup).toContain(copy.nav.cta);
    }
  });

  it("renders no nested main landmark inside the home page itself", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      expect(markup).not.toContain("<main");
    }
  });

  it("composes with the layout into exactly one main landmark for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderComposedHome(locale);
      expect(markup.match(/<main/g)).toHaveLength(1);
      expect(markup).toContain('id="main-content"');
    }
  });

  it("keeps the skip-link target on the single main landmark when composed", async () => {
    for (const locale of locales) {
      const markup = await renderComposedHome(locale);
      expect(markup.match(/<main/g)).toHaveLength(1);
      expect(markup).toMatch(/<main id="main-content"[^>]*tabindex="-1"[^>]*>/);
    }
  });

  it("composes the locale-aware Navbar before main and Footer after main", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderComposedHome(locale);
      const nav = markup.indexOf("<nav");
      const main = markup.indexOf("<main");
      const mainClose = markup.indexOf("</main>");
      const footer = markup.indexOf("<footer");
      expect(nav).toBeGreaterThan(-1);
      expect(nav).toBeLessThan(main);
      expect(footer).toBeGreaterThan(mainClose);
      expect(markup).toContain(copy.a11y.languageSwitcher);
      expect(markup).toContain(copy.footer.copyright);
    }
  });

  it("rejects unsupported locales via notFound", async () => {
    await expect(renderHome("fr")).rejects.toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });
});

describe("SH-07 five-tool directory", () => {
  it("renders exactly five catalog-derived tool cards for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      const cards = markup.match(/data-tool-id="/g) ?? [];
      expect(cards).toHaveLength(getAllTools().length);
      expect(cards).toHaveLength(5);
    }
  });

  it("renders every catalog tool with locale-aware href, label, and canonical description", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      for (const tool of getAllTools()) {
        expect(markup).toContain(`data-tool-id="${tool.id}"`);
        expect(markup).toContain(`href="${tool.hrefs[locale]}"`);
        expect(markup).toContain(tool.localizedLabels[locale]);
        expect(markup).toContain(escapeText(tool.description));
      }
    }
  });

  it("renders every tool card as a real locale-prefixed link (keyboard focusable)", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      const cardTags = toolCardTags(markup);
      expect(cardTags).toHaveLength(5);
      for (const tag of cardTags) {
        const href = attribute(tag, "href");
        expect(href).toBeDefined();
        expect(href).toMatch(new RegExp(`^/${locale}/`));
        expect(href).not.toMatch(/#|javascript:|^\/$/);
      }
    }
  });

  it("gives every card equal visual weight with an identical class list", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      const classes = toolCardTags(markup).map((tag) => attribute(tag, "class"));
      expect(classes).toHaveLength(5);
      expect(classes.every((className) => className === classes[0])).toBe(true);
      expect(classes[0]).toBeTruthy();
    }
  });

  it("lays the tool grid out responsively across breakpoints", async () => {
    const markup = await renderHome("en");
    expect(markup).toContain("grid");
    expect(markup).toContain("grid-cols-1");
    expect(markup).toContain("sm:grid-cols-2");
    expect(markup).toContain("lg:grid-cols-3");
  });
});

describe("SH-07 privacy, how-it-works, and FAQ sections", () => {
  it("renders the truthful localized privacy section for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup).toContain(copy.home.privacy);
      expect(markup).toContain(copy.home.privacyDesc);
    }
  });

  it("renders the localized how-it-works section with all steps in order", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup).toContain(copy.home.howItWorks);
      const positions = copy.home.howItWorksSteps.map((step) => markup.indexOf(step));
      for (const position of positions) {
        expect(position).toBeGreaterThan(-1);
      }
      for (let i = 1; i < positions.length; i++) {
        expect(positions[i]).toBeGreaterThan(positions[i - 1]);
      }
    }
  });

  it("renders the FAQ as details/summary with every canonical item", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup).toContain(copy.home.faq);
      expect(markup.match(/<details/g)).toHaveLength(copy.home.faqItems.length);
      expect(markup.match(/<summary/g)).toHaveLength(copy.home.faqItems.length);
      for (const item of copy.home.faqItems) {
        expect(markup).toContain(item.question);
        expect(markup).toContain(item.answer);
      }
    }
  });
});

describe("SH-07 copy and claim hygiene", () => {
  it("carries no legacy 13-tool routes or labels", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      for (const route of LEGACY_TOOL_ROUTES) {
        expect(markup).not.toContain(route);
      }
      for (const label of LEGACY_TOOL_LABELS) {
        expect(markup).not.toContain(label);
      }
    }
  });

  it("carries no unproven speed, tracking, or absolute-privacy claims", async () => {
    const claimPattern =
      /\bno tracking\b|\bno-tracking\b|\btracking\b|\binstant\b|\bfastest\b|fully private|client-only|client only|no personal data|never (read|analyze|store)/i;
    for (const locale of locales) {
      const markup = await renderHome(locale);
      expect(textContent(markup)).not.toMatch(claimPattern);
    }
  });

  it("renders no placeholder, hash, or empty links", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      expect(markup).not.toMatch(/href="#/);
      expect(markup).not.toMatch(/href=""/);
      expect(markup).not.toMatch(/lorem|TODO|TBD|placeholder|change me/i);
    }
  });
});

describe("SH-07 accessibility foundations", () => {
  it("keeps global focus-visible and reduced-motion styles effective", () => {
    const css = readFileSync(fileURLToPath(new URL("../app/globals.css", import.meta.url)), "utf8");
    expect(css).toContain(":focus-visible");
    expect(css).toContain("prefers-reduced-motion");
  });
});
