import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  notFound: vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
}));

import { notFound } from "next/navigation";

import PrivacyPage from "../[locale]/privacy/page";
import { locales } from "../../lib/i18n";
import { getMessages } from "../../lib/messages";

async function renderPrivacy(locale: string): Promise<string> {
  const tree = await PrivacyPage({ params: Promise.resolve({ locale }) });
  return renderToStaticMarkup(tree);
}

// Removes HTML tags so we can scan visible copy.
function textContent(markup: string): string {
  return markup
    .replace(/<[^>]+>/g, " ")
    .replace(/&#x27;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

describe("T8 full privacy page", () => {
  it("renders exactly one h1 with the localized title for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderPrivacy(locale);
      expect(markup.match(/<h1/g)).toHaveLength(1);
      expect(markup).toContain(getMessages(locale).pages.privacy.title);
    }
  });

  it("renders exactly seven sections with localized headings for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderPrivacy(locale);
      const sectionCount = (markup.match(/<section/g) ?? []).length;
      expect(sectionCount).toBe(7);
      const copy = getMessages(locale).privacyPage.sections;
      const headings = [
        copy.whatWeCollect.title,
        copy.whatWeDontCollect.title,
        copy.howLong.title,
        copy.analytics.title,
        copy.security.title,
        copy.contact.title,
      ];
      for (const heading of headings) {
        expect(markup).toContain(heading);
      }
    }
  });

  it("renders the intro paragraph for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderPrivacy(locale);
      expect(textContent(markup)).toContain(
        textContent(getMessages(locale).privacyPage.sections.intro),
      );
    }
  });

  it("renders the last-updated line for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderPrivacy(locale);
      expect(markup).toContain(getMessages(locale).privacyPage.lastUpdated);
    }
  });

  it("renders the localized contact email as a mailto link for every locale", async () => {
    for (const locale of locales) {
      const markup = await renderPrivacy(locale);
      const email = getMessages(locale).privacyPage.sections.contact.email;
      expect(markup).toContain(`href="mailto:${email}"`);
    }
  });

  it("renders list items for collect, don't-collect, analytics, and security sections", async () => {
    for (const locale of locales) {
      const markup = await renderPrivacy(locale);
      const copy = getMessages(locale).privacyPage.sections;
      const liCount = (markup.match(/<li/g) ?? []).length;
      const expected =
        copy.whatWeCollect.items.length +
        copy.whatWeDontCollect.items.length +
        copy.analytics.items.length +
        copy.security.items.length;
      expect(liCount).toBe(expected);
    }
  });

  it("rejects unsupported locales via notFound", async () => {
    await expect(renderPrivacy("fr")).rejects.toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });
});
