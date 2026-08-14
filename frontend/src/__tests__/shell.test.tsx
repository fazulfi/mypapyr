vi.mock("@vercel/analytics/next", () => ({
  Analytics: vi.fn(() => null),
}));
vi.mock("@vercel/speed-insights/next", () => ({
  SpeedInsights: vi.fn(() => null),
}));
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";

import { renderToStaticMarkup } from "react-dom/server";
import { existsSync } from "node:fs";
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

import LocaleLayout, { generateMetadata, generateStaticParams } from "../app/[locale]/layout";
import { locales } from "../lib/i18n";
import { getMessages, messages } from "../lib/messages";

async function renderShell(locale: string): Promise<string> {
  const tree = await LocaleLayout({
    children: <p>shell content</p>,
    params: Promise.resolve({ locale }),
  });
  return renderToStaticMarkup(tree);
}

function asImageList(images: unknown): unknown[] {
  return Array.isArray(images) ? images : images === undefined ? [] : [images];
}

function firstImageUrl(images: unknown): string {
  const first = asImageList(images)[0];
  if (typeof first === "string") {
    return first;
  }
  if (first instanceof URL) {
    return first.href;
  }
  if (first !== null && typeof first === "object" && "url" in first) {
    return String(first.url);
  }
  return "";
}

function firstImageAlt(images: unknown): string {
  const first = asImageList(images)[0];
  if (
    first !== null &&
    typeof first === "object" &&
    !(first instanceof URL) &&
    "alt" in first &&
    typeof first.alt === "string"
  ) {
    return first.alt;
  }
  return "";
}

describe("SH-03 locale-aware root shell", () => {
  it("renders the html lang attribute for every supported locale", async () => {
    for (const locale of locales) {
      const markup = await renderShell(locale);
      expect(markup).toContain(`<html lang="${locale}"`);
    }
  });

  it("keeps the SH-02 font variable on the html element", async () => {
    const markup = await renderShell("en");
    expect(markup).toContain('class="--font-dm-sans"');
  });

  it("renders the skip link first in tab order, before main content", async () => {
    const markup = await renderShell("en");
    const bodyOpen = markup.indexOf("<body");
    const firstAnchor = markup.indexOf("<a", bodyOpen);
    const firstMain = markup.indexOf("<main", bodyOpen);
    expect(firstAnchor).toBeGreaterThan(bodyOpen);
    expect(firstAnchor).toBeLessThan(firstMain);
  });

  it("points the skip link at the main content target with the localized label", async () => {
    const markup = await renderShell("en");
    const mainIndex = markup.indexOf('id="main-content"');
    expect(mainIndex).toBeGreaterThan(0);
    expect(markup.slice(0, mainIndex)).toContain('href="#main-content"');
    expect(markup.slice(0, mainIndex)).toContain(messages.en.a11y.skipToContent);
  });

  it("renders the localized skip-link label for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderShell(locale);
      expect(markup).toContain(messages[locale].a11y.skipToContent);
    }
  });

  it("provides exactly one main wrapper carrying id main-content", async () => {
    const markup = await renderShell("en");
    expect(markup.match(/<main/g)).toHaveLength(1);
    expect(markup).toContain('id="main-content"');
  });

  it("builds a sticky-footer-ready flex shell on body and main", async () => {
    const markup = await renderShell("en");
    expect(markup).toContain('<body class="flex min-h-dvh flex-col">');
    expect(markup).toMatch(/<main id="main-content"[^>]*class="flex-1"[^>]*>/);
  });

  it("makes the main content landmark programmatically focusable", async () => {
    const markup = await renderShell("en");
    expect(markup).toMatch(/<main id="main-content"[^>]*tabindex="-1"[^>]*>/);
  });

  it("renders the page children inside the main wrapper", async () => {
    const markup = await renderShell("en");
    expect(markup).toContain("<p>shell content</p>");
  });

  it("rejects unsupported locales via notFound", async () => {
    await expect(renderShell("fr")).rejects.toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });

  it("lists every supported locale as a static route", () => {
    expect(generateStaticParams()).toEqual(locales.map((locale) => ({ locale })));
  });
});

describe("SH-03 per-locale metadata", () => {
  it("anchors metadata to the canonical production origin", async () => {
    for (const locale of locales) {
      const metadata = await generateMetadata({ params: Promise.resolve({ locale }) });
      expect(new URL(String(metadata.metadataBase)).origin).toBe("https://mypapyr.com");
    }
  });

  it("carries localized title and description for every locale", async () => {
    for (const locale of locales) {
      const metadata = await generateMetadata({ params: Promise.resolve({ locale }) });
      const copy = getMessages(locale);
      expect(metadata.title).toBe(copy.metadata.title);
      expect(metadata.description).toBe(copy.metadata.description);
    }
  });

  it("localizes the metadata copy across locales", async () => {
    const titles = new Set<string>();
    const descriptions = new Set<string>();
    for (const locale of locales) {
      const metadata = await generateMetadata({ params: Promise.resolve({ locale }) });
      titles.add(String(metadata.title));
      descriptions.add(String(metadata.description));
    }
    expect(titles.size).toBe(locales.length);
    expect(descriptions.size).toBe(locales.length);
  });

  it("mirrors the localized copy into OpenGraph and Twitter text fields", async () => {
    const metadata = await generateMetadata({ params: Promise.resolve({ locale: "es" }) });
    const copy = getMessages("es");
    expect(metadata.openGraph).toEqual(
      expect.objectContaining({
        type: "website",
        locale: "es_ES",
        siteName: copy.siteName,
        title: copy.metadata.title,
        description: copy.metadata.description,
      }),
    );
    expect(metadata.twitter).toEqual(
      expect.objectContaining({
        card: "summary_large_image",
        title: copy.metadata.title,
        description: copy.metadata.description,
      }),
    );
  });

  it("points OpenGraph and Twitter at real public hero assets for every locale", async () => {
    const heroAsset = fileURLToPath(new URL("../../public/papyr-hero-light.svg", import.meta.url));
    expect(existsSync(heroAsset)).toBe(true);
    for (const locale of locales) {
      const metadata = await generateMetadata({ params: Promise.resolve({ locale }) });
      const base = String(metadata.metadataBase);
      const ogUrl = firstImageUrl(metadata.openGraph?.images);
      const twitterUrl = firstImageUrl(metadata.twitter?.images);
      expect(ogUrl).not.toBe("");
      expect(twitterUrl).not.toBe("");
      expect(new URL(ogUrl, base).href).toBe("https://mypapyr.com/papyr-hero-light.svg");
      expect(new URL(twitterUrl, base).href).toBe("https://mypapyr.com/papyr-hero-light.svg");
    }
  });

  it("localizes the social image alt text per locale", async () => {
    const alts = new Set<string>();
    for (const locale of locales) {
      const metadata = await generateMetadata({ params: Promise.resolve({ locale }) });
      const ogAlt = firstImageAlt(metadata.openGraph?.images);
      const twitterAlt = firstImageAlt(metadata.twitter?.images);
      expect(ogAlt).not.toBe("");
      expect(twitterAlt).toBe(ogAlt);
      alts.add(ogAlt);
    }
    expect(alts.size).toBe(locales.length);
  });

  it("rejects unsupported locales via notFound", async () => {
    await expect(generateMetadata({ params: Promise.resolve({ locale: "de" }) })).rejects.toThrow(
      "NEXT_NOT_FOUND",
    );
    expect(notFound).toHaveBeenCalled();
  });

  it("keeps metadata copy free of unproven speed, privacy, and free claims", async () => {
    const claimPattern = /free|fast|instant|secure|private|privacy/i;
    for (const locale of locales) {
      const metadata = await generateMetadata({ params: Promise.resolve({ locale }) });
      expect(String(metadata.title)).not.toMatch(claimPattern);
      expect(String(metadata.description)).not.toMatch(claimPattern);
    }
  });
});

describe("SH-05/06 locale shell glue", () => {
  it("renders the Navbar landmark after the SkipLink and before the main landmark", async () => {
    const markup = await renderShell("en");
    const skipLink = markup.indexOf('href="#main-content"');
    const nav = markup.indexOf("<nav");
    const main = markup.indexOf("<main");
    expect(skipLink).toBeGreaterThan(-1);
    expect(nav).toBeGreaterThan(skipLink);
    expect(nav).toBeLessThan(main);
  });

  it("renders the Footer landmark after the main content", async () => {
    const markup = await renderShell("en");
    const mainClose = markup.indexOf("</main>");
    const footer = markup.indexOf("<footer");
    expect(mainClose).toBeGreaterThan(-1);
    expect(footer).toBeGreaterThan(mainClose);
  });

  it("renders locale-aware Navbar copy for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderShell(locale);
      expect(markup).toContain(messages[locale].nav.cta);
      expect(markup).toContain(messages[locale].a11y.languageSwitcher);
    }
  });

  it("renders locale-aware Footer copy for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderShell(locale);
      expect(markup).toContain(messages[locale].footer.copyright);
      expect(markup).toContain(messages[locale].footer.support);
    }
  });


  it("keeps exactly one main landmark with the shell chrome mounted", async () => {
    const markup = await renderShell("en");
    expect(markup.match(/<main/g)).toHaveLength(1);
    expect(markup).toContain('id="main-content"');
  });
});

describe("T8 analytics instrumentation", () => {
  it("mounts Vercel Analytics and Speed Insights when rendering the shell", async () => {
    const analyticsMock = vi.mocked(Analytics);
    const speedMock = vi.mocked(SpeedInsights);

    await renderShell("en");

    expect(analyticsMock).toHaveBeenCalled();
    expect(speedMock).toHaveBeenCalled();
  });
});
