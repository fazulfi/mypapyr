// @vitest-environment node
/**
 * OP-02 status page rendering tests.
 *
 * The page is a server component that renders derived availability from
 * safe, approved snapshot inputs. These tests lock:
 * - localized shell heading/scope statement + exactly-one ad slot + exactly
 *   one h1 and no anchor links (SH-08 contracts apply to the enriched page);
 * - the branch-default rendering (empty safe input) stays unknown and never
 *   fetches the VPS or any API endpoint;
 * - operational / degraded / down fixtures render their localized labels,
 *   per-region rows, observation timestamp, and derivation policy.
 */
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  notFound: vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
}));

import { notFound } from "next/navigation";

import type { SupportingPageCopy } from "@/components/supporting-page";
import { locales, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { type StatusSnapshot } from "@/lib/status";
import StatusPage, { StatusContent } from "@/app/[locale]/status/page";

function copyFor(locale: Locale): SupportingPageCopy {
  const messages = getMessages(locale);
  return { ...messages.pages.status, adLabel: messages.ads.label };
}

function window(
  regionIds: readonly string[],
  failing: Record<string, number> = {},
  rounds = 4,
  start = 1_000_000_000,
): StatusSnapshot[] {
  return Array.from({ length: rounds }, (_, i) => ({
    observedAt: start + i * 3_600_000,
    regions: regionIds.map((region) => ({
      region,
      reachable: i < rounds - (failing[region] ?? 0),
    })),
  }));
}

async function renderPage(locale: string): Promise<string> {
  const tree = await StatusPage({ params: Promise.resolve({ locale }) });
  return renderToStaticMarkup(tree);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("OP-02 status page: localized shell contracts", () => {
  it("renders one h1, the localized scope statement, and no anchors in every locale", async () => {
    for (const locale of locales) {
      const markup = await renderPage(locale);
      const copy = getMessages(locale).pages.status;

      expect(markup.match(/<h1/g)).toHaveLength(1);
      expect(markup).toContain(copy.title);
      expect(markup).toContain(copy.description);
      expect(markup).not.toMatch(/<a\b/);
      expect(markup).not.toContain('href="#');
    }
  });

  it("renders exactly one reserved banner-468x60 slot in every locale", async () => {
    for (const locale of locales) {
      const markup = await renderPage(locale);
      expect(markup.match(/data-testid="papyr-ad-slot"/g)).toHaveLength(1);
      expect(markup).toContain("width:468px");
      expect(markup).toContain("height:60px");
      expect(markup).toContain(`aria-label="${getMessages(locale).ads.label}"`);
    }
  });

  it("rejects unsupported locales via notFound", async () => {
    await expect(renderPage("fr")).rejects.toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });
});

describe("OP-02 status page: branch-default safe input", () => {
  it("renders the explicit unknown state without fetching the VPS or any endpoint", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(null, { status: 200 }));

    const markup = await renderPage("en");

    expect(fetchSpy).not.toHaveBeenCalled();
    expect(markup).toContain("Status unknown");
    expect(markup).toContain("Monitoring signals are being configured");
    expect(markup).not.toContain("/api/v1");
    expect(markup).not.toContain("health");
  });

  it("words availability as observations rather than guarantees", async () => {
    for (const locale of locales) {
      const markup = await renderPage(locale);
      const copy = getMessages(locale);
      expect(markup).toContain(copy.statusPage.observedDisclaimer);
      expect(markup).toContain(copy.pages.status.description);
    }
  });
});

describe("OP-02 status page: derived state rendering", () => {
  it("renders operational state, region rows, observation time, and the policy", () => {
    const locale = "en" as const;
    const markup = renderToStaticMarkup(
      StatusContent({
        locale,
        copy: copyFor(locale),
        snapshots: window(["fra", "sin"]),
      }),
    );

    expect(markup).toContain("Operational");
    expect(markup).toContain("fra");
    expect(markup).toContain("sin");
    expect(markup).toContain("Last observed");
    expect(markup).toContain('dateTime="1970-01-12T16:46:40.000Z"');
    expect(markup).toContain("3 failed observations");
  });

  it("renders the down state when two regions sustain the failure threshold", () => {
    const locale = "en" as const;
    const markup = renderToStaticMarkup(
      StatusContent({
        locale,
        copy: copyFor(locale),
        snapshots: window(["fra", "sin"], { fra: 3, sin: 3 }),
      }),
    );

    expect(markup).toContain("Service disruption");
    expect(markup).toContain("Multiple regions are reporting sustained failures");
    const downLabels = markup.match(/>Down( \(\d+\))?</g) ?? [];
    expect(downLabels.length).toBeGreaterThanOrEqual(2);
  });

  it("renders the degraded state when a single region crosses the threshold", () => {
    const locale = "en" as const;
    const markup = renderToStaticMarkup(
      StatusContent({
        locale,
        copy: copyFor(locale),
        snapshots: window(["fra", "sin"], { fra: 3 }),
      }),
    );

    expect(markup).toContain("Degraded");
    expect(markup).toContain("fra");
    expect(markup).toContain("sin");
  });

  it("keeps exactly one ad slot while rendering a derived state", () => {
    const locale = "en" as const;
    const markup = renderToStaticMarkup(
      StatusContent({
        locale,
        copy: copyFor(locale),
        snapshots: window(["fra", "sin"], { fra: 3, sin: 3 }),
      }),
    );

    expect(markup.match(/data-testid="papyr-ad-slot"/g)).toHaveLength(1);
  });
});
