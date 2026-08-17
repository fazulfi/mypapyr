// @vitest-environment jsdom
// PT-01: Unit coverage for the analytics send pipeline: hook pre-binding,
// trackEvent/trackPageView, opt-out, and the SSR guard.

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  errorCategoryFor,
  isOptedOut,
  redactPayload,
  trackEvent,
  trackPageView,
  useAnalytics,
} from "../analytics";

type VaSink = ReturnType<typeof vi.fn>;

function mockVa(): VaSink {
  return (window as Window & { va?: VaSink }).va as VaSink;
}

function setCleanNavigator(): void {
  vi.stubGlobal("navigator", {});
}

describe("lib/analytics useAnalytics", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { va: vi.fn() });
    setCleanNavigator();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("pre-binds locale and tool into every event", () => {
    const { trackEvent: track } = useAnalytics("en", "compress-pdf");
    track("task_started", { page: "/compress" });

    expect(mockVa()).toHaveBeenCalledTimes(1);
    const call = mockVa().mock.calls[0] as [string, Record<string, unknown>];
    expect(call[0]).toBe("event");
    expect(call[1]).toEqual({
      name: "task_started",
      locale: "en",
      tool: "compress-pdf",
      page: "/compress",
    });
  });

  it("pre-binds locale when no tool is given", () => {
    const { trackEvent: track } = useAnalytics("es");
    track("task_started", { page: "/split" });

    const call = mockVa().mock.calls[0] as [string, Record<string, unknown>];
    expect(call[1]).toEqual({
      name: "task_started",
      locale: "es",
      page: "/split",
    });
  });

  it("event data overrides pre-bound context for the same key", () => {
    const { trackEvent: track } = useAnalytics("en", "merge-pdf");
    track("task_started", { locale: "id", page: "/merge" });

    const call = mockVa().mock.calls[0] as [string, Record<string, unknown>];
    expect(call[1]).toMatchObject({ locale: "id", tool: "merge-pdf" });
  });

  it("exposes a trackPageView that fires the pageview event", () => {
    const { trackPageView: pageView } = useAnalytics("en", "split-pdf");
    pageView();

    expect(mockVa()).toHaveBeenCalledTimes(1);
    expect(mockVa().mock.calls[0]).toEqual(["event", { name: "pageview" }]);
  });

  it("does not call va when opted out (doNotTrack)", () => {
    vi.stubGlobal("navigator", { doNotTrack: "1" });
    const { trackEvent: track, trackPageView: pageView } = useAnalytics("en", "merge-pdf");
    track("task_started", { page: "/merge" });
    pageView();
    expect(mockVa()).not.toHaveBeenCalled();
  });
});

describe("lib/analytics trackEvent + trackPageView", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { va: vi.fn() });
    setCleanNavigator();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("trackEvent sends name + redacted payload through window.va", () => {
    trackEvent("task_completed", {
      page: "/compress",
      locale: "en",
      tool: "compress-pdf",
      filename: "tax.pdf",
    });

    expect(mockVa()).toHaveBeenCalledTimes(1);
    const call = mockVa().mock.calls[0] as [string, Record<string, unknown>];
    expect(call[0]).toBe("event");
    expect(call[1]).toEqual({
      name: "task_completed",
      page: "/compress",
      locale: "en",
      tool: "compress-pdf",
    });
    expect(call[1]).not.toHaveProperty("filename");
  });

  it("trackPageView fires the pageview event", () => {
    trackPageView();
    expect(mockVa()).toHaveBeenCalledTimes(1);
    expect(mockVa().mock.calls[0]).toEqual(["event", { name: "pageview" }]);
  });

  it("is a no-op when window.va is absent", () => {
    vi.stubGlobal("window", {});
    expect(() => trackEvent("task_started", { page: "/compress" })).not.toThrow();
    expect(() => trackPageView()).not.toThrow();
  });
});

describe("lib/analytics SSR guard", () => {
  let originalWindow: typeof globalThis.window;

  beforeEach(() => {
    originalWindow = globalThis.window;
    // Simulate a server environment by hiding `window` on the global object.
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: undefined,
    });
  });

  afterEach(() => {
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: originalWindow,
    });
    vi.unstubAllGlobals();
  });

  it("trackEvent is a no-op when window is undefined", () => {
    const sink = vi.fn();
    // Even if a stray global va existed, it must not be called.
    (globalThis as Record<string, unknown>).va = sink;
    expect(() => trackEvent("task_started", { page: "/compress" })).not.toThrow();
    expect(sink).not.toHaveBeenCalled();
  });

  it("trackPageView is a no-op when window is undefined", () => {
    const sink = vi.fn();
    (globalThis as Record<string, unknown>).va = sink;
    expect(() => trackPageView()).not.toThrow();
    expect(sink).not.toHaveBeenCalled();
  });
});

describe("lib/analytics errorCategoryFor", () => {
  it.each([
    ["invalid file uploaded", "invalid-file"],
    ["limit exceeded for upload", "limit-exceeded"],
    ["service unavailable", "server-unavailable"],
    ["task expired", "expired"],
    ["request cancelled", "cancelled"],
    ["file is encrypted", "encrypted"],
    ["source blocked", "blocked"],
  ])("maps %s to %s", (message, expected) => {
    expect(errorCategoryFor(message)).toBe(expected);
  });

  it("maps an unknown string to internal", () => {
    expect(errorCategoryFor("something unexpected")).toBe("internal");
  });

  it("maps null/undefined to internal", () => {
    expect(errorCategoryFor(null)).toBe("internal");
    expect(errorCategoryFor(undefined)).toBe("internal");
  });

  it("maps a numeric error to internal", () => {
    expect(errorCategoryFor(500)).toBe("internal");
  });

  it("recurses into object errors preferring category", () => {
    expect(errorCategoryFor({ category: "limit-exceeded" })).toBe("limit-exceeded");
    expect(errorCategoryFor({ code: "invalid-file" })).toBe("invalid-file");
    expect(errorCategoryFor({ message: "file is encrypted" })).toBe("encrypted");
  });
});

describe("lib/analytics redactPayload edge cases", () => {
  it("redacts a filename value inside an allowed field", () => {
    const result = redactPayload({ page: "/compress", referrer: "tax-return.pdf" });
    expect(result.referrer).toBe("[redacted]");
  });

  it("recurses into arrays and nested objects", () => {
    const result = redactPayload(
      {
        page: "/merge",
        webVitals: [{ name: "LCP", value: 120 }],
        referrer: { password: "hunter2", kept: "yes" },
      },
      ["page", "webVitals", "referrer"],
    );
    expect(result.webVitals).toEqual([{ name: "LCP", value: 120 }]);
    expect(result.referrer).toEqual({ kept: "yes" });
  });

  it("drops keys not in the allowed list", () => {
    const result = redactPayload(
      { page: "/split", filename: "a.pdf", password: "x", payload: "skipped" },
      ["page"],
    );
    expect(result).toEqual({ page: "/split" });
  });
});

describe("lib/analytics isOptedOut", () => {
  it("returns true when globalPrivacyControl is active", () => {
    vi.stubGlobal("navigator", { globalPrivacyControl: true });
    expect(isOptedOut()).toBe(true);
  });

  it("returns true when the app-level opt-out flag is set", () => {
    vi.stubGlobal("navigator", {});
    (window as Window & { _papyrAnalyticsOptOut?: unknown })._papyrAnalyticsOptOut = true;
    expect(isOptedOut()).toBe(true);
  });

  it("returns false when no opt-out signal is present", () => {
    vi.stubGlobal("navigator", {});
    delete (window as Window & { _papyrAnalyticsOptOut?: unknown })._papyrAnalyticsOptOut;
    expect(isOptedOut()).toBe(false);
  });
});
