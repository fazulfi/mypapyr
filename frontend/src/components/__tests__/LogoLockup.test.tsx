import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { locales } from "../../lib/i18n";
import { LogoLockup } from "../LogoLockup";

describe("SH-04 LogoLockup", () => {
  it("renders an accessible link with aria-label Papyr", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    expect(markup).toContain('aria-label="Papyr"');
    expect(markup).toContain("Papyr");
  });

  it("defaults to href='/' when no locale or explicit href is provided", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    expect(markup).toContain('href="/"');
  });

  it("generates a locale-aware href when locale is provided", () => {
    const markup = renderToStaticMarkup(<LogoLockup locale="es" />);
    expect(markup).toContain('href="/es"');
  });

  it("generates the correct href for every supported locale", () => {
    for (const locale of locales) {
      const markup = renderToStaticMarkup(<LogoLockup locale={locale} />);
      expect(markup).toContain(`href="/${locale}"`);
    }
  });

  it("honors an explicit href override even when locale is provided", () => {
    const markup = renderToStaticMarkup(<LogoLockup href="/custom" locale="id" />);
    expect(markup).toContain('href="/custom"');
    expect(markup).not.toContain('href="/id"');
  });

  it("renders the navbar size variant by default (28×28 mark, 17px text)", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    // Navbar mark: h-7 w-7 (1.75rem = 28px)
    expect(markup).toMatch(/class="[^"]*\bh-7\b[^"]*"/);
    expect(markup).toMatch(/class="[^"]*\bw-7\b[^"]*"/);
    // Navbar text: text-[17px]
    expect(markup).toContain("text-[17px]");
    // Tracking
    expect(markup).toContain("tracking-tight");
  });

  it("renders the footer size variant when size='footer' (24×24 mark, 15px text)", () => {
    const markup = renderToStaticMarkup(<LogoLockup size="footer" />);
    // Footer mark: h-6 w-6 (1.5rem = 24px)
    expect(markup).toMatch(/class="[^"]*\bh-6\b[^"]*"/);
    expect(markup).toMatch(/class="[^"]*\bw-6\b[^"]*"/);
    // Footer text: text-[15px]
    expect(markup).toContain("text-[15px]");
    // Footer uses rounded-[5px]
    expect(markup).toContain("rounded-[5px]");
  });

  it("renders the navbar size variant explicitly", () => {
    const markup = renderToStaticMarkup(<LogoLockup size="navbar" />);
    expect(markup).toMatch(/class="[^"]*\bh-7\b[^"]*"/);
    expect(markup).toMatch(/class="[^"]*\bw-7\b[^"]*"/);
    expect(markup).toContain("text-[17px]");
  });

  it("uses the canonical --color-navy token for the mark background", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    // The mark div uses bg-navy via tailwind class
    expect(markup).toContain("bg-navy");
  });

  it("renders the document FileIcon SVG with white stroke", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    // SVG with core document path and polyline
    expect(markup).toContain("M14.5 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V7.5L14.5 2z");
    expect(markup).toContain('stroke="white"');
    expect(markup).toContain("viewBox=");
  });

  it("renders the brand name Papyr in navy color", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    expect(markup).toContain("text-navy");
    expect(markup).toContain("Papyr");
  });

  it("renders as a Next.js Link when no explicit href with locale", () => {
    // Next.js Link renders as <a> in static markup
    const markup = renderToStaticMarkup(<LogoLockup locale="en" />);
    expect(markup).toContain('href="/en"');
    expect(markup).toContain('aria-label="Papyr"');
  });

  it("includes the link wrapper as a direct anchor element", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    expect(markup).toMatch(/^<a\b/);
  });

  it("applies rounded-md for navbar size mark", () => {
    const markup = renderToStaticMarkup(<LogoLockup size="navbar" />);
    expect(markup).toContain("rounded-md");
    expect(markup).not.toContain("rounded-[5px]");
  });

  it("applies rounded-[5px] for footer size mark", () => {
    const markup = renderToStaticMarkup(<LogoLockup size="footer" />);
    expect(markup).toContain("rounded-[5px]");
    expect(markup).not.toContain("rounded-md");
  });

  it("applies font-semibold to the brand name text", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    expect(markup).toContain("font-semibold");
  });

  it("keeps the mark and text horizontally aligned with flex gap-2", () => {
    const markup = renderToStaticMarkup(<LogoLockup />);
    expect(markup).toContain("flex");
    expect(markup).toContain("items-center");
    expect(markup).toContain("gap-2");
  });
});
