import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { locales, type Locale } from "../../lib/i18n";
import { getMessages, messages } from "../../lib/messages";

import { LanguageSwitcher } from "../LanguageSwitcher";

function defaultPath(targetLocale: Locale): string {
  return `/${targetLocale}`;
}

describe("SH-05 LanguageSwitcher", () => {
  it("renders a fieldset with accessible label for every supported locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const markup = renderToStaticMarkup(
        <LanguageSwitcher
          currentLocale={locale}
          a11yLabel={copy.a11y.languageSwitcher}
          languageLabels={copy.languages}
          getEquivalentPath={defaultPath}
        />,
      );
      expect(markup).toContain(copy.a11y.languageSwitcher);
      expect(markup).toContain("fieldset");
    }
  });

  it("renders three locale options with native-language labels", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="en"
        a11yLabel={messages.en.a11y.languageSwitcher}
        languageLabels={messages.en.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    expect(markup).toContain("English");
    expect(markup).toContain("Español");
    expect(markup).toContain("Bahasa Indonesia");
  });

  it("marks the current locale as the selected/active option", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="es"
        a11yLabel={messages.es.a11y.languageSwitcher}
        languageLabels={messages.es.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    // The Spanish option should be marked as current/selected
    expect(markup).toContain("Español");
    // The aria-current or checked/selected attribute should be present
    const hasSelected =
      markup.includes("aria-current") ||
      markup.includes('selected=""') ||
      markup.includes("selected");
    expect(hasSelected).toBe(true);
  });

  it("renders each locale option as a navigable link to the computed equivalent path", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="en"
        a11yLabel={messages.en.a11y.languageSwitcher}
        languageLabels={messages.en.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    expect(markup).toContain('href="/en"');
    expect(markup).toContain('href="/es"');
    expect(markup).toContain('href="/id"');
  });

  it("preserves tool-equivalent paths when getEquivalentPath returns a tool route", () => {
    const toolPaths: Record<Locale, string> = {
      en: "/en/compress-pdf",
      es: "/es/comprimir-pdf",
      id: "/id/kompres-pdf",
    };
    function getPath(targetLocale: Locale): string {
      return toolPaths[targetLocale];
    }

    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="en"
        a11yLabel={messages.en.a11y.languageSwitcher}
        languageLabels={messages.en.languages}
        getEquivalentPath={getPath}
      />,
    );
    expect(markup).toContain('href="/en/compress-pdf"');
    expect(markup).toContain('href="/es/comprimir-pdf"');
    expect(markup).toContain('href="/id/kompres-pdf"');
  });

  it("renders the a11yLabel as an accessible legend or label", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="id"
        a11yLabel={messages.id.a11y.languageSwitcher}
        languageLabels={messages.id.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    expect(markup).toContain(messages.id.a11y.languageSwitcher);
  });

  it("renders every locale option even when currentLocale is non-English", () => {
    for (const locale of locales) {
      const markup = renderToStaticMarkup(
        <LanguageSwitcher
          currentLocale={locale}
          a11yLabel={getMessages(locale).a11y.languageSwitcher}
          languageLabels={getMessages(locale).languages}
          getEquivalentPath={defaultPath}
        />,
      );
      expect(markup).toContain("English");
      expect(markup).toContain("Español");
      expect(markup).toContain("Bahasa Indonesia");
    }
  });

  it("does not render placeholder or empty hrefs", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="en"
        a11yLabel={messages.en.a11y.languageSwitcher}
        languageLabels={messages.en.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    expect(markup).not.toContain('href="#"');
    expect(markup).not.toContain('href=""');
  });
});
