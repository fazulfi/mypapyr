// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { getMessages } from "@/lib/messages";

import { SplitPdfTool } from "@/app/[locale]/split-pdf/page";

afterEach(() => {
  cleanup();
});

describe("SplitPdfTool localized rendering", () => {
  it("renders the localized title and description for each locale", () => {
    for (const locale of ["en", "es", "id"] as const) {
      const copy = getMessages(locale);
      const { unmount } = render(<SplitPdfTool locale={locale} />);
      expect(screen.getByRole("heading", { level: 1, name: copy.tools.split.title })).toBeTruthy();
      expect(screen.getByText(copy.tools.split.description)).toBeTruthy();
      unmount();
    }
  });
});
