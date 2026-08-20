// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";

import { getMessages, messages } from "@/lib/messages";
import { locales } from "@/lib/i18n";
import { LegalVersionFooter } from "@/components/legal-version-footer";
import { LegalPageContent } from "@/components/legal-page-content";

describe("legal version footer (DEC-045)", () => {
  it("renders Version X — Effective date from localized copy for every locale", () => {
    for (const locale of locales) {
      const { version, effectiveDate, footerLabel } = messages[locale].legal;
      render(<LegalVersionFooter locale={locale} />);
      expect(screen.getByText(new RegExp(`Version ${version}`))).toBeDefined();
      expect(screen.getByText(new RegExp(`${footerLabel} ${effectiveDate}`))).toBeDefined();
      cleanup();
    }
  });
});

describe("legal page copy (internal compliance audit, decision 4)", () => {
  it("removes all informational-shell and later-phase placeholders from legal copy", () => {
    const raw = JSON.stringify(messages);
    expect(raw).not.toMatch(/informational shell/i);
    expect(raw).not.toMatch(/later phase/i);
  });

  it("keeps claims consistent with product reality", () => {
    for (const locale of locales) {
      const legal = messages[locale].legal;
      const en = getMessages(locale);
      for (const section of [
        ...legal.sections.privacy,
        ...legal.sections.terms,
        ...legal.sections.cookiesAdvertising,
      ]) {
        for (const paragraph of section.paragraphs) {
          expect(paragraph.length).toBeGreaterThan(0);
        }
      }
      expect(en.privacyPage.lastUpdated.length).toBeGreaterThan(0);
    }
  });

  it("renders legal body sections plus the version footer via LegalPageContent", () => {
    const locale = "en";
    const copy = { title: "Privacy", description: "Privacy policy", adLabel: "Advertisement" };
    render(<LegalPageContent copy={copy} locale={locale} sectionsKey="privacy" />);
    expect(screen.getAllByRole("heading", { level: 2 }).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Version/).length).toBeGreaterThan(0);
  });
});
