// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";

import { getMessages, messages } from "@/lib/messages";
import { locales } from "@/lib/i18n";
import { LegalVersionFooter } from "@/components/legal-version-footer";
import { LegalPageContent } from "@/components/legal-page-content";

describe("legal version footer (DEC-045)", () => {
  it("renders the full hard-coded localized footer label for every locale", () => {
    const expectedLabels = {
      en: "Effective date",
      es: "Fecha de entrada en vigor",
      id: "Tanggal berlaku",
    } as const;

    for (const locale of locales) {
      render(<LegalVersionFooter locale={locale} />);
      expect(screen.getByText(`Version 1.0 — ${expectedLabels[locale]} 2026-08-20`)).toBeDefined();
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
    const claims = {
      en: {
        retention: "Cloudflare R2",
        browser: "Merge PDF, Split PDF",
        analytics: "anonymous, aggregated page views without cookies",
        optOut: "Do Not Track and Global Privacy Control",
        expiry: "expire within 5 minutes",
      },
      es: {
        retention: "Cloudflare R2",
        browser: "Unir PDF y Dividir PDF",
        analytics: "visitas anónimas y agregadas sin cookies",
        optOut: "Do Not Track y Global Privacy Control",
        expiry: "caducan en un plazo de 5 minutos",
      },
      id: {
        retention: "Cloudflare R2",
        browser: "Gabung PDF, Pisah PDF",
        analytics: "kunjungan halaman secara anonim dan agregat tanpa cookie",
        optOut: "Do Not Track serta Global Privacy Control",
        expiry: "kedaluwarsa dalam 5 menit",
      },
    } as const;

    for (const locale of locales) {
      const legal = messages[locale].legal;
      const copy = claims[locale];
      const privacy = legal.sections.privacy.flatMap((section) => section.paragraphs).join(" ");
      const cookies = legal.sections.cookiesAdvertising
        .flatMap((section) => section.paragraphs)
        .join(" ");
      expect(privacy).toContain(copy.retention);
      expect(privacy).toContain(copy.browser);
      expect(privacy).toContain(copy.analytics);
      expect(privacy).toContain("privacy@mypapyr.com");
      expect(privacy).toContain(copy.expiry);
      expect(cookies).toContain(copy.optOut);
      expect(getMessages(locale).privacyPage.lastUpdated.length).toBeGreaterThan(0);
    }
  });

  it("keeps security expiry and advertising opt-out claims in every locale", () => {
    const expected = {
      en: { expiry: "expire within 5 minutes", optOut: "Do Not Track and Global Privacy Control" },
      es: {
        expiry: "caducan en un plazo de 5 minutos",
        optOut: "Do Not Track y Global Privacy Control",
      },
      id: {
        expiry: "kedaluwarsa dalam 5 menit",
        optOut: "Do Not Track serta Global Privacy Control",
      },
    } as const;

    for (const locale of locales) {
      const legal = messages[locale].legal;
      const security = legal.sections.privacy
        .find((section) => section.heading === messages[locale].legal.sections.privacy[2].heading)
        ?.paragraphs.join(" ");
      const advertising = legal.sections.cookiesAdvertising[1].paragraphs.join(" ");
      expect(security).toContain(expected[locale].expiry);
      expect(advertising).toContain(expected[locale].optOut);
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
