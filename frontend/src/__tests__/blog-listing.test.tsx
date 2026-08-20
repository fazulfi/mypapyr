// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import BlogListingPage from "@/app/[locale]/blog/page";
import { BLOG_AUTHOR } from "@/lib/blog";
import { locales } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

describe("P9 blog listing", () => {
  it("renders the real listing: 5 articles with title, date, author, and banner ad slot", async () => {
    for (const locale of locales) {
      const element = await BlogListingPage({ params: Promise.resolve({ locale }) });
      const { unmount } = render(element);
      expect(screen.getByRole("heading", { level: 1 }).textContent).toBe(
        getMessages(locale).pages.blog.title,
      );
      const links = screen
        .getAllByRole("link")
        .filter((link) => (link as HTMLAnchorElement).href.includes(`/${locale}/blog/`));
      expect(links).toHaveLength(5);
      expect(document.body.textContent?.split(BLOG_AUTHOR).length).toBe(6);
      expect(screen.getAllByRole("time")).toHaveLength(5);
      expect(screen.getAllByLabelText(getMessages(locale).ads.label)).toHaveLength(2);
      unmount();
    }
  });
});
