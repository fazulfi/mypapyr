import { describe, expect, it } from "vitest";

import {
  BLOG_AUTHOR,
  blogAlternates,
  blogPaths,
  countWords,
  getArticle,
  getArticlesByLocale,
  getArticleSource,
  validateBlogContent,
} from "../blog";
import { BLOG_ARTICLES } from "../../../content/blog/manifest";
import { locales, type Locale } from "../i18n";
import { SEO_BASE_URL } from "../seo/alternates";
import { toolCatalog } from "../catalog";

const TOPICS = ["compress-pdf", "merge-pdf", "split-pdf", "jpg-to-pdf", "pdf-to-jpg"] as const;

describe("P9 blog manifest (decision 2)", () => {
  it("defines exactly 15 articles = 5 topics × 3 locales", () => {
    expect(BLOG_ARTICLES).toHaveLength(5);
    for (const entry of BLOG_ARTICLES) {
      expect(TOPICS).toContain(entry.topic);
      for (const locale of locales) {
        expect(entry.slugs[locale]).toBeTruthy();
        expect(entry.titles[locale]).toBeTruthy();
        expect(entry.descriptions[locale]).toBeTruthy();
      }
    }
  });

  it("keeps slugs unique per locale and titles unique per locale (no duplication)", () => {
    for (const locale of locales) {
      const slugs = BLOG_ARTICLES.map((entry) => entry.slugs[locale]);
      expect(new Set(slugs).size).toBe(slugs.length);
      const titles = BLOG_ARTICLES.map((entry) => entry.titles[locale]);
      expect(new Set(titles).size).toBe(titles.length);
    }
  });

  it("uses one topic per active tool with valid ISO publication dates", () => {
    const toolIds = new Set(toolCatalog.map((tool) => tool.id));
    for (const entry of BLOG_ARTICLES) {
      expect(toolIds.has(entry.topic)).toBe(true);
      expect(entry.date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(Number.isNaN(new Date(entry.date).getTime())).toBe(false);
    }
  });
});

describe("P9 blog readers", () => {
  it("returns 15 localized articles through getArticlesByLocale", () => {
    for (const locale of locales) {
      const articles = getArticlesByLocale(locale);
      expect(articles).toHaveLength(5);
      for (const article of articles) {
        expect(article.locale).toBe(locale);
        expect(article.author).toBe(BLOG_AUTHOR);
        expect(article.href).toBe(`${SEO_BASE_URL}${blogPaths(article.entry)[locale]}`);
      }
    }
  });

  it("resolves getArticle by locale+slug and returns undefined for unknown slugs", () => {
    const first = BLOG_ARTICLES[0];
    const found = getArticle("en", first.slugs.en);
    expect(found?.entry.topic).toBe(first.topic);
    expect(getArticle("en", "does-not-exist")).toBeUndefined();
    expect(getArticle("fr" as Locale, "x")).toBeUndefined();
  });

  it("builds hreflang alternates with x-default to EN on the canonical origin", () => {
    for (const entry of BLOG_ARTICLES) {
      const alternates = blogAlternates("en", entry);
      expect(alternates.canonical.startsWith(`${SEO_BASE_URL}/en/blog/`)).toBe(true);
      for (const locale of locales) {
        expect(alternates.languages[locale].startsWith(`${SEO_BASE_URL}/${locale}/blog/`)).toBe(
          true,
        );
      }
      expect(alternates.languages["x-default"]).toBe(alternates.languages.en);
    }
  });
});

describe("P9 content gates (SEDANG, decision 5)", () => {
  it("reads every article body from the content store", async () => {
    for (const entry of BLOG_ARTICLES) {
      for (const locale of locales) {
        const source = await getArticleSource(locale, entry.slugs[locale]);
        expect(source.trim().length).toBeGreaterThan(0);
      }
    }
  });

  it("counts words on markdown-stripped body text", () => {
    expect(countWords("one two three")).toBe(3);
    expect(countWords("# Heading\n\nA **bold** [link](https://budgezen.com) word.")).toBe(6);
    expect(countWords("```js\nconst x = 1;\n```\n\nplain")).toBe(1);
  });

  it("enforces 400–800 words per article for every locale", async () => {
    const violations = await validateBlogContent();
    const wordIssues = violations.filter((v) => v.startsWith("word-count"));
    expect(wordIssues).toEqual([]);
  });

  it("requires an internal link to the topic's localized tool page in every body", async () => {
    const violations = await validateBlogContent();
    const linkIssues = violations.filter((v) => v.startsWith("missing-tool-link"));
    expect(linkIssues).toEqual([]);
  });

  it("requires valid file layout and author field", async () => {
    const violations = await validateBlogContent();
    expect(violations.filter((v) => v.startsWith("file-"))).toEqual([]);
    expect(BLOG_AUTHOR).toBe("Papyr Team");
  });
});
