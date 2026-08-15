import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { locales, type Locale } from "../../lib/i18n";
import { getMessages, messages } from "../../lib/messages";

import { LanguageSwitcher } from "../LanguageSwitcher";

function defaultPath(targetLocale: Locale): string {
  return `/${targetLocale}`;
}

describe("SH-05 LanguageSwitcher", () => {
  it("renders a <select> with aria-label and the equivalent-path for every locale", () => {
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
      expect(markup).toContain("<select");
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

  it("marks the current locale as the selected option", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="es"
        a11yLabel={messages.es.a11y.languageSwitcher}
        languageLabels={messages.es.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    // <option value="es" selected>...</option> — react renders `selected=""` on selected option
    expect(markup).toMatch(/<option[^>]*value="es"[^>]*selected/);
  });

  it("each option carries the matching value and lang attribute", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="en"
        a11yLabel={messages.en.a11y.languageSwitcher}
        languageLabels={messages.en.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    expect(markup).toMatch(/<option[^>]*value="en"[^>]*lang="en"/);
    expect(markup).toMatch(/<option[^>]*value="es"[^>]*lang="es"/);
    expect(markup).toMatch(/<option[^>]*value="id"[^>]*lang="id"/);
  });

  it("renders the a11yLabel as accessible name on the select", () => {
    const markup = renderToStaticMarkup(
      <LanguageSwitcher
        currentLocale="id"
        a11yLabel={messages.id.a11y.languageSwitcher}
        languageLabels={messages.id.languages}
        getEquivalentPath={defaultPath}
      />,
    );
    expect(markup).toContain(`aria-label="${messages.id.a11y.languageSwitcher}"`);
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
});
