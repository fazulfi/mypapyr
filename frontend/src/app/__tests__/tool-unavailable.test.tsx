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
}));

import { notFound } from "next/navigation";

import ToolUnavailablePage, { generateMetadata } from "../[locale]/tool-unavailable/page";
import { getLegacyTools } from "../../lib/catalog";
import { locales } from "../../lib/i18n";
import { getMessages } from "../../lib/messages";

function render410(locale: string, tool: string): Promise<string> {
  return ToolUnavailablePage({
    params: Promise.resolve({ locale }),
    searchParams: Promise.resolve({ tool }),
  }).then((tree) => renderToStaticMarkup(tree));
}

describe("T3 localized 410 tool-unavailable page (DEC-194)", () => {
  it("renders for every legacy tool in every locale with the tool name and a home back link", async () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      for (const tool of getLegacyTools()) {
        const markup = await render410(locale, tool.id);
        expect(markup).toContain(tool.localizedLabels[locale]);
        expect(markup).toContain(copy.notFound.title);
        expect(markup).toContain(copy.notFound.description);
        expect(markup).toContain(`href="/${locale}"`);
        expect(markup).toContain(copy.nav.home);
      }
    }
  });

  it("declares noindex and no canonical on the non-indexable 410 surface", async () => {
    for (const locale of locales) {
      const metadata = await generateMetadata({
        params: Promise.resolve({ locale }),
        searchParams: Promise.resolve({ tool: "rotate" }),
      });
      const robots = metadata.robots;
      expect(robots).not.toBeUndefined();
      expect(robots).not.toBeNull();
      if (typeof robots === "string") {
        throw new Error("robots must be an object for the 410 surface");
      }
      expect(robots?.index).toBe(false);
      expect(metadata.alternates?.canonical).toBeUndefined();
    }
  });

  it("rejects unknown legacy tool ids via notFound", async () => {
    await expect(render410("en", "compress-pdf")).rejects.toThrow("NEXT_NOT_FOUND");
    await expect(render410("en", "not-a-tool")).rejects.toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });

  it("rejects unsupported locales via notFound", async () => {
    await expect(render410("fr", "rotate")).rejects.toThrow("NEXT_NOT_FOUND");
  });
});
