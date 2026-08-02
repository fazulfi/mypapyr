import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { locales } from "../../lib/i18n";
import { getMessages } from "../../lib/messages";
import { SkipLink } from "../SkipLink";

describe("SH-03 SkipLink", () => {
  it("renders an anchor to the main content target by default", () => {
    const markup = renderToStaticMarkup(<SkipLink label="Skip to main content" />);
    expect(markup).toContain('href="#main-content"');
    expect(markup).toContain("Skip to main content");
  });

  it("honors an explicit target", () => {
    const markup = renderToStaticMarkup(<SkipLink href="#app" label="Skip" />);
    expect(markup).toContain('href="#app"');
  });

  it("is visually hidden until focused so it leads the tab order", () => {
    const markup = renderToStaticMarkup(<SkipLink label="Skip" />);
    expect(markup).toMatch(/class="[^"]*\bsr-only\b[^"]*"/);
    expect(markup).toContain("focus:not-sr-only");
  });

  it("uses the canonical --color-bg token for the focused text color", () => {
    const markup = renderToStaticMarkup(<SkipLink label="Skip to main content" />);
    expect(markup).toContain("var(--color-bg)");
    expect(markup).not.toContain("var(--color-background)");
  });

  it("renders the localized label for every supported locale", () => {
    for (const locale of locales) {
      const label = getMessages(locale).a11y.skipToContent;
      const markup = renderToStaticMarkup(<SkipLink label={label} />);
      expect(markup).toContain(label);
    }
  });
});
