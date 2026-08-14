import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { getMessages, messages } from "../../lib/messages";
import { locales } from "../../lib/i18n";
import { getAllTools, getLegacyTools } from "../../lib/catalog";
import OtherTools from "../OtherTools";

describe("T7 OtherTools rail", () => {
  it("renders the localized title from messages for every locale", () => {
    for (const locale of locales) {
      const markup = renderToStaticMarkup(
        <OtherTools currentTool="compress-pdf" locale={locale} />,
      );
      const copy = getMessages(locale);
      expect(markup).toContain(copy.otherTools.title);
    }
  });

  it("localizes otherTools.title per locale", () => {
    expect(messages.es.otherTools.title).not.toBe(messages.en.otherTools.title);
    expect(messages.id.otherTools.title).not.toBe(messages.en.otherTools.title);
  });

  it("renders all sibling tools and excludes the current tool", () => {
    const markup = renderToStaticMarkup(<OtherTools currentTool="compress-pdf" locale="en" />);
    const allTools = [...getAllTools(), ...getLegacyTools()];
    const siblings = allTools.filter((t) => t.id !== "compress-pdf");
    expect(siblings).toHaveLength(allTools.length - 1);
    for (const tool of siblings) {
      expect(markup).toContain(tool.hrefs.en);
    }
    // The current tool must not appear as a link
    expect(markup).not.toContain("/en/compress-pdf");
  });

  it("renders one link per sibling tool", () => {
    const allTools = [...getAllTools(), ...getLegacyTools()];
    const markup = renderToStaticMarkup(<OtherTools currentTool="compress-pdf" locale="en" />);
    const anchorMatches = markup.match(/<a\b/g);
    expect(anchorMatches).not.toBeNull();
    expect(anchorMatches!.length).toBe(allTools.length - 1);
  });

  it("renders an arrow icon footer in each link", () => {
    const markup = renderToStaticMarkup(<OtherTools currentTool="merge-pdf" locale="en" />);
    const linkCount = (markup.match(/<a\b/g) || []).length;
    const arrowCount = (markup.match(/<svg\b/g) || []).length;
    expect(linkCount).toBeGreaterThan(0);
    expect(arrowCount).toBe(linkCount);
  });

  it("uses localized hrefs and labels for sibling tools per locale", () => {
    for (const locale of locales) {
      const markup = renderToStaticMarkup(<OtherTools currentTool="split-pdf" locale={locale} />);
      const allTools = [...getAllTools(), ...getLegacyTools()];
      const siblings = allTools.filter((t) => t.id !== "split-pdf");
      for (const tool of siblings) {
        expect(markup).toContain(tool.hrefs[locale]);
        expect(markup).toContain(tool.fullLabel[locale]);
      }
    }
  });
});
