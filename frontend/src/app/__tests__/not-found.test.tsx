import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/font/google", () => ({
  DM_Sans: vi.fn(() => ({
    className: "dm-sans-class",
    style: { fontFamily: "var(--font-dm-sans)" },
    variable: "--font-dm-sans",
  })),
}));

import { NotFoundContent } from "../not-found";
import { locales } from "../../lib/i18n";
import { getMessages } from "../../lib/messages";

describe("SH-09 not-found shell", () => {
  it("renders html element with a valid lang attribute", () => {
    const messages = getMessages("en");
    const markup = renderToStaticMarkup(<NotFoundContent locale="en" messages={messages} />);
    expect(markup).toContain("<html");
    expect(markup).toContain('lang="en"');
  });

  it("renders html lang correctly for each supported locale", () => {
    for (const locale of locales) {
      const messages = getMessages(locale);
      const markup = renderToStaticMarkup(<NotFoundContent locale={locale} messages={messages} />);
      expect(markup).toContain(`lang="${locale}"`);
    }
  });

  it("renders exactly one main#main-content with tabIndex=-1", () => {
    const messages = getMessages("en");
    const markup = renderToStaticMarkup(<NotFoundContent locale="en" messages={messages} />);
    expect(markup).toContain('id="main-content"');
    expect(markup).toContain('tabindex="-1"');
    const mainCount = (markup.match(/id="main-content"/g) ?? []).length;
    expect(mainCount).toBe(1);
  });

  it("renders exactly one SkipLink to #main-content", () => {
    const messages = getMessages("en");
    const markup = renderToStaticMarkup(<NotFoundContent locale="en" messages={messages} />);
    const skipCount = (markup.match(/href="#main-content"/g) ?? []).length;
    expect(skipCount).toBe(1);
  });

  it("renders localized skip-to-content label", () => {
    for (const locale of locales) {
      const messages = getMessages(locale);
      const markup = renderToStaticMarkup(<NotFoundContent locale={locale} messages={messages} />);
      expect(markup).toContain(messages.a11y.skipToContent);
    }
  });

  it("renders localized notFound title", () => {
    for (const locale of locales) {
      const messages = getMessages(locale);
      const markup = renderToStaticMarkup(<NotFoundContent locale={locale} messages={messages} />);
      expect(markup).toContain(messages.notFound.title);
    }
  });

  it("renders localized notFound description", () => {
    for (const locale of locales) {
      const messages = getMessages(locale);
      const markup = renderToStaticMarkup(<NotFoundContent locale={locale} messages={messages} />);
      expect(markup).toContain(messages.notFound.description);
    }
  });
});
