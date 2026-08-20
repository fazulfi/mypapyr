// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { getArticlesByLocale, BLOG_AUTHOR } from "@/lib/blog";
import { locales } from "@/lib/i18n";

describe("P9 blog listing", () => {
  it("lists all 5 articles per locale with title, date, and author", () => {
    for (const locale of locales) {
      const articles = getArticlesByLocale(locale);
      expect(articles).toHaveLength(5);
      for (const article of articles) {
        const rendered = render(
          <ul>
            {articles.map((a) => (
              <li key={a.slug}>
                <a href={`/${locale}/blog/${a.slug}`}>{a.title}</a>
                <time dateTime={a.date}>{a.date}</time>
                <span>{BLOG_AUTHOR}</span>
              </li>
            ))}
          </ul>,
        );
        expect(screen.getAllByText(article.title).length).toBeGreaterThanOrEqual(1);
        expect(screen.getAllByText(BLOG_AUTHOR).length).toBeGreaterThanOrEqual(1);
        rendered.unmount();
      }
    }
  });
});
