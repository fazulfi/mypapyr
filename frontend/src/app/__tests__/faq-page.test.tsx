// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { FAQContent } from "../[locale]/faq/page";
import { locales } from "../../lib/i18n";
import { getMessages } from "../../lib/messages";

afterEach(() => {
  cleanup();
});

describe("T8 FAQ page", () => {
  it("renders the localized FAQ heading for every locale", () => {
    for (const locale of locales) {
      const { unmount } = render(<FAQContent locale={locale} />);
      expect(screen.getByRole("heading", { level: 1 })).toBeTruthy();
      expect(screen.getByText(getMessages(locale).faqPage.title)).toBeTruthy();
      unmount();
    }
  });

  it("renders all 8 FAQ items with their questions for every locale", () => {
    for (const locale of locales) {
      const { unmount } = render(<FAQContent locale={locale} />);
      const copy = getMessages(locale).faqPage;
      expect(copy.items).toHaveLength(8);
      for (const item of copy.items) {
        expect(screen.getByText(item.q)).toBeTruthy();
      }
      unmount();
    }
  });

  it("renders the mailto CTA for every locale", () => {
    for (const locale of locales) {
      const { unmount } = render(<FAQContent locale={locale} />);
      const copy = getMessages(locale).faqPage;
      const link = screen.getByRole("link");
      expect(link.getAttribute("href")).toBe(`mailto:${copy.ctaEmail}`);
      unmount();
    }
  });

  it("keeps all answers collapsed by default", () => {
    const { unmount } = render(<FAQContent locale="en" />);
    const copy = getMessages("en").faqPage;
    // Collapsed answers are opacity-0 and clipped via grid-rows-[0fr]
    for (const item of copy.items) {
      const answerElements = screen.getAllByText(item.a);
      for (const el of answerElements) {
        expect(el.closest(".grid")?.className).toContain("grid-rows-[0fr]");
      }
    }
    unmount();
  });

  it("expands exactly one item at a time when clicked", () => {
    const { unmount } = render(<FAQContent locale="en" />);
    const copy = getMessages("en").faqPage;

    // Click the first question
    fireEvent.click(screen.getByText(copy.items[0].q));
    expect(screen.getByText(copy.items[0].a).closest(".grid")?.className).toContain(
      "grid-rows-[1fr]",
    );

    // Click the second question — first should collapse, second should expand
    fireEvent.click(screen.getByText(copy.items[1].q));
    expect(screen.getByText(copy.items[0].a).closest(".grid")?.className).toContain(
      "grid-rows-[0fr]",
    );
    expect(screen.getByText(copy.items[1].a).closest(".grid")?.className).toContain(
      "grid-rows-[1fr]",
    );

    // Click the first question again — second should collapse
    fireEvent.click(screen.getByText(copy.items[0].q));
    expect(screen.getByText(copy.items[1].a).closest(".grid")?.className).toContain(
      "grid-rows-[0fr]",
    );

    unmount();
  });

  it("collapses the open item when clicked again (toggle-off)", () => {
    const { unmount } = render(<FAQContent locale="en" />);
    const copy = getMessages("en").faqPage;

    fireEvent.click(screen.getByText(copy.items[0].q));
    fireEvent.click(screen.getByText(copy.items[0].q));
    expect(screen.getByText(copy.items[0].a).closest(".grid")?.className).toContain(
      "grid-rows-[0fr]",
    );

    unmount();
  });
});
