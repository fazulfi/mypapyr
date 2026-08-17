// @vitest-environment jsdom
// PT-01 (ADR-01): the Vercel Analytics / Speed Insights `beforeSend` gates
// must cancel automatic pageview / web-vital events when the visitor has
// expressed a DNT, GPC, or app-flag opt-out preference.

import { afterEach, describe, expect, it, vi } from "vitest";

import { analyticsBeforeSend, speedInsightsBeforeSend } from "@/components/PrivacyAnalytics";

function setCleanNavigator(): void {
  vi.stubGlobal("navigator", {});
}

function clearOptOutFlag(): void {
  delete (window as Window & { _papyrAnalyticsOptOut?: unknown })._papyrAnalyticsOptOut;
}

afterEach(() => {
  vi.unstubAllGlobals();
  clearOptOutFlag();
});

const analyticsEvent = { type: "pageview" as const, url: "/en/compress-pdf" };
const speedEvent = { type: "vital" as const, url: "/en/compress-pdf", route: "/en/compress-pdf" };

describe("PrivacyAnalytics beforeSend gates", () => {
  it("analyticsBeforeSend cancels the pageview when doNotTrack is 1", () => {
    vi.stubGlobal("navigator", { doNotTrack: "1" });
    expect(analyticsBeforeSend(analyticsEvent)).toBeNull();
  });

  it("analyticsBeforeSend cancels the pageview when globalPrivacyControl is true", () => {
    vi.stubGlobal("navigator", { globalPrivacyControl: true });
    expect(analyticsBeforeSend(analyticsEvent)).toBeNull();
  });

  it("analyticsBeforeSend cancels the pageview when the app opt-out flag is set", () => {
    setCleanNavigator();
    (window as Window & { _papyrAnalyticsOptOut?: unknown })._papyrAnalyticsOptOut = true;
    expect(analyticsBeforeSend(analyticsEvent)).toBeNull();
  });

  it("analyticsBeforeSend passes the event through when not opted out", () => {
    setCleanNavigator();
    expect(analyticsBeforeSend(analyticsEvent)).toBe(analyticsEvent);
  });

  it("speedInsightsBeforeSend cancels the vital when doNotTrack is 1", () => {
    vi.stubGlobal("navigator", { doNotTrack: "1" });
    expect(speedInsightsBeforeSend(speedEvent)).toBe(false);
  });

  it("speedInsightsBeforeSend cancels the vital when globalPrivacyControl is true", () => {
    vi.stubGlobal("navigator", { globalPrivacyControl: true });
    expect(speedInsightsBeforeSend(speedEvent)).toBe(false);
  });

  it("speedInsightsBeforeSend cancels the vital when the app opt-out flag is set", () => {
    setCleanNavigator();
    (window as Window & { _papyrAnalyticsOptOut?: unknown })._papyrAnalyticsOptOut = true;
    expect(speedInsightsBeforeSend(speedEvent)).toBe(false);
  });

  it("speedInsightsBeforeSend passes the event through when not opted out", () => {
    setCleanNavigator();
    expect(speedInsightsBeforeSend(speedEvent)).toBe(speedEvent);
  });
});
