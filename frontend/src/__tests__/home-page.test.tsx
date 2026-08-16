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
  it("renders exactly one hero h1 carrying both localized hero lines for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup.match(/<h1/g)).toHaveLength(1);
      expect(markup).toContain(copy.home.heroLine1);
      expect(markup).toContain(copy.home.heroLine2);
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
      expect(markup).toContain(copy.home.privacyEyebrow);
      expect(markup).toContain(copy.home.privacy);
      for (const card of copy.home.privacyCards) {
        expect(markup).toContain(card.title);
        expect(markup).toContain(escapeText(card.desc));
      }
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
    // The claim scan covers the hero, sub, CTA, trust badges, and tool cards.
    // The privacy-card "never read/analyze/store" line is the REFERENCE parity
    // copy mandated by the plan dossier (§1.3) and lives in messages.home.privacyCards,
    // so it is deliberately excluded here and asserted verbatim by the T4 privacy test.
    const claimPattern =
      /\bno tracking\b|\bno-tracking\b|\btracking\b|\binstant\b|\bfastest\b|fully private|client-only|client only|no personal data/i;
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      const heroAndTools = [
        copy.home.heroPill,
        copy.home.heroLine1,
        copy.home.heroLine2,
        copy.home.heroSub,
        copy.nav.cta,
        ...copy.home.trustBadges,
        copy.home.toolsEyebrow,
        copy.home.toolsHeading,
        ...getAllTools().map((tool) => tool.description),
      ].join(" ");
      expect(heroAndTools).not.toMatch(claimPattern);
      expect(textContent(markup)).not.toMatch(
        /\bno tracking\b|\bno-tracking\b|\binstant\b|\bfastest\b|fully private|client-only|client only|no personal data/i,
      );
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

describe("T3 rich homepage copy keys", () => {
  it("defines the localized hero pill copy for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      expect(copy.home.heroPill.trim()).not.toBe("");
    }
  });

  it("defines both split hero lines for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      expect(copy.home.heroLine1.trim()).not.toBe("");
      expect(copy.home.heroLine2.trim()).not.toBe("");
    }
  });

  it("defines all three trust badges for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      expect(copy.home.trustBadges).toHaveLength(3);
      for (const badge of copy.home.trustBadges) {
        expect(badge.trim()).not.toBe("");
      }
    }
  });

  it("defines the tools eyebrow and card CTA for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      expect(copy.home.toolsEyebrow.trim()).not.toBe("");
      expect(copy.home.cardCta.trim()).not.toBe("");
    }
  });

  it("defines the privacy eyebrow and all three privacy cards for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      expect(copy.home.privacyEyebrow.trim()).not.toBe("");
      expect(copy.home.privacyCards).toHaveLength(3);
      for (const card of copy.home.privacyCards) {
        expect(card.title.trim()).not.toBe("");
        expect(card.desc.trim()).not.toBe("");
      }
    }
  });
});

describe("T4 rich homepage restore (hero pill, trust badges, card footer, privacy cards)", () => {
  it("renders the hero pill badge with the localized pill copy and accent styling", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup).toContain(copy.home.heroPill);
      expect(markup).toContain("rounded-full border border-accent/30 bg-accent/10");
    }
  });

  it("renders the two-line hero with the accent heroLine2 span for every locale", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      const h1 = markup.match(/<h1[^>]*>[\s\S]*?<\/h1>/)?.[0] ?? "";
      expect(h1).toContain(copy.home.heroLine1);
      expect(h1).toContain("<br/>");
      expect(h1).toContain(`<span class="text-accent">${copy.home.heroLine2}</span>`);
    }
  });

  it("renders all three trust badges with their localized copy", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      const positions = copy.home.trustBadges.map((badge) => markup.indexOf(escapeText(badge)));
      for (const position of positions) {
        expect(position).toBeGreaterThan(-1);
      }
      for (let i = 1; i < positions.length; i++) {
        expect(positions[i]).toBeGreaterThan(positions[i - 1]);
      }
    }
  });

  it("renders the tools section eyebrow above the tool grid", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      const eyebrow = markup.indexOf(copy.home.toolsEyebrow);
      // Compare against the h2 opener itself so a heading string that is a
      // substring of the eyebrow never self-matches (e.g. en "Tools" vs "All tools").
      const toolsHeadingTag = `<h2 class="text-[32px] font-semibold tracking-tight text-navy">`;
      const headingPosition = markup.indexOf(toolsHeadingTag);
      expect(eyebrow).toBeGreaterThan(-1);
      expect(headingPosition).toBeGreaterThan(-1);
      expect(eyebrow).toBeLessThan(headingPosition);
    }
  });

  it("renders a footer row with the card CTA and arrow icon on every tool card", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      const cards = markup.split(/<\/a>/g).filter((chunk) => chunk.includes("data-tool-id="));
      expect(cards).toHaveLength(getAllTools().length);
      for (const card of cards) {
        expect(card).toContain(copy.home.cardCta);
        expect(card).toContain("<line");
        expect(card).toContain("<polyline");
      }
    }
  });

  it("renders the three privacy cards with icon chips and localized titles and descriptions", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = await renderHome(locale);
      expect(markup).toContain("bg-accent/15");
      for (const card of copy.home.privacyCards) {
        expect(markup).toContain(card.title);
        expect(markup).toContain(escapeText(card.desc));
      }
      // Expectation: the privacy cards render with shield/clock/lock icon SVG paths.
      expect(markup).toContain('d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"');
      expect(markup).toContain('<circle cx="12" cy="12" r="10">');
      expect(markup).toContain('<rect x="3" y="11" width="18" height="11" rx="2" ry="2">');
    }
  });
  it("renders ad slots after the hero and after the FAQ (owner decision 2026-08-15)", async () => {
    for (const locale of locales) {
      const markup = await renderHome(locale);
      const adCount = (markup.match(/aria-label="(?:Advertisement|Publicidad|Iklan)"/g) ?? [])
        .length;
      expect(adCount).toBeGreaterThanOrEqual(2);
      const faqIdx = markup.indexOf("Frequently");
      const label = locale === "es" ? "Publicidad" : locale === "id" ? "Iklan" : "Advertisement";
      const lastAdIdx = markup.lastIndexOf(`aria-label="${label}"`);
      expect(lastAdIdx).toBeGreaterThan(faqIdx);
    }
  });
});
describe("SSR ad slot markers: reserved placeholders, client-only scripts", () => {
  it("emits leaderboard + box slot markers with a width:320px placeholder and defers third-party scripts to the client", async () => {
    const markup = await renderHome("en");
    const slotTags = [
      ...markup.matchAll(/<div\b[^>]*\bdata-testid="papyr-ad-slot"\b[^>]*>/g),
    ].map((match) => match[0]);
    expect(slotTags.length).toBeGreaterThanOrEqual(2);
    expect(slotTags.some((tag) => /width:320px/.test(tag))).toBe(true);
    // Third-party ad scripts must stay client-only: never present in SSR markup.
    expect(markup).not.toContain("highperformanceformat.com");
  });
});
