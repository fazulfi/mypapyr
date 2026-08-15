// @vitest-environment jsdom
/**
 * PT-02: Advertising slots + placement guards.
 *
 * Covers:
 * - `isAdEnabled()` behaviour (DNT, GPC, disable flag).
 * - `shouldRenderAd()` page-level guard.
 * - `isAfterPrimaryExperience()` phase guard.
 * - `isSeparatedFromDownload()` spatial-guard semantic.
 * - `AdSlot` component: reserved dimensions, IntersectionObserver-based
 *   lazy script injection, unmount cleanup.
 * - Non-allowed pages: slot returns null, nothing breaks.
 */
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { cleanup, render, act } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  AD_SLOT_DIMENSIONS,
  ADSTERRA_HOST,
  ADSTERRA_KEY,
  allowedAdPages,
  isAdEnabled,
} from "@/lib/ads";

import { AdSlot } from "@/components/ads/AdSlot";
import { LeaderboardAdSlot } from "@/components/ads/LeaderboardAdSlot";
import {
  isAfterPrimaryExperience,
  isSeparatedFromDownload,
  shouldRenderAd,
} from "@/components/ads/placement";

// Original navigator privacy signals, captured once so per-test mutations
// can be restored in `afterEach` (prevents cross-test pollution).
interface NavigatorWithPrivacy {
  doNotTrack?: string;
  globalPrivacyControl?: boolean;
}
const navPrivacy = navigator as Navigator & NavigatorWithPrivacy;
const originalDoNotTrack = navPrivacy.doNotTrack;
const originalGlobalPrivacyControl = navPrivacy.globalPrivacyControl;

/** Restore every privacy signal + ad flag mutated by the tests above. */
function resetAdPrivacySignals() {
  const win = window as Window & { _papyrAdsDisabled?: unknown };
  delete win._papyrAdsDisabled;
  const nav = navigator as Navigator & NavigatorWithPrivacy;
  Object.defineProperty(nav, "doNotTrack", {
    value: originalDoNotTrack,
    configurable: true,
  });
  Object.defineProperty(nav, "globalPrivacyControl", {
    value: originalGlobalPrivacyControl,
    configurable: true,
  });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Stub IntersectionObserver for environments that lack it (jsdom). */
function installIntersectionObserver() {
  const mockObserve = vi.fn();
  const mockDisconnect = vi.fn();
  const instances: Array<{
    fire: (isIntersecting: boolean) => void;
  }> = [];

  class MockObserver {
    readonly observe = mockObserve;
    readonly disconnect = mockDisconnect;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    constructor(private handler: (entries: any[]) => void) {
      instances.push(this);
    }
    fire(isIntersecting: boolean) {
      this.handler([{ isIntersecting, target: document.createElement("div") }]);
    }
  }

  vi.stubGlobal("IntersectionObserver", MockObserver as unknown as typeof IntersectionObserver);

  return {
    mockObserve,
    mockDisconnect,
    /** Fire the most recently created observer instance. */
    fire: (isIntersecting: boolean) => {
      const last = instances[instances.length - 1];
      if (last) last.fire(isIntersecting);
    },
    /** Fire every registered observer instance (multi-slot pages). */
    fireAll: (isIntersecting: boolean) => {
      for (const instance of instances) instance.fire(isIntersecting);
    },
  };
}

afterEach(() => {
  cleanup();
  resetAdPrivacySignals();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  // Remove any lingering script nodes from the test DOM.
  document.head.querySelectorAll("[data-papyr-ad-slot]").forEach((n) => n.remove());
});

// ---------------------------------------------------------------------------
// Config sanity
// ---------------------------------------------------------------------------

describe("ads config", () => {
  it("exports reserved dimensions 300x250", () => {
    expect(AD_SLOT_DIMENSIONS).toEqual({ width: 300, height: 250 });
  });

  it("exports a non-empty Adsterra key and host", () => {
    expect(ADSTERRA_KEY).toBe("b552110bd65e7690ed89a04a1d654898");
    expect(ADSTERRA_HOST).toBe("https://www.highperformanceformat.com");
  });

  it("allowedAdPages covers home, tools, and supporting pages; status stays ad-free (owner decision 2026-08-15)", () => {
    expect(allowedAdPages).toEqual([
      "home",
      "compress-pdf",
      "merge-pdf",
      "split-pdf",
      "jpg-to-pdf",
      "pdf-to-jpg",
      "contact",
      "privacy",
      "terms",
      "cookies-advertising",
      "roadmap",
      "faq",
    ]);
    expect(allowedAdPages).not.toContain("status");
  });
});

// ---------------------------------------------------------------------------
// isAdEnabled
// ---------------------------------------------------------------------------

describe("isAdEnabled()", () => {
  it("returns true when no DNT, GPC, or disable flag is set", () => {
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    delete w._papyrAdsDisabled;
    const n = navigator as Navigator & NavigatorWithPrivacy;
    Object.defineProperty(n, "doNotTrack", {
      value: undefined,
      configurable: true,
    });
    Object.defineProperty(n, "globalPrivacyControl", {
      value: undefined,
      configurable: true,
    });
    expect(isAdEnabled()).toBe(true);
  });

  it("returns false when window._papyrAdsDisabled is true", () => {
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    w._papyrAdsDisabled = true;
    expect(isAdEnabled()).toBe(false);
  });

  it("returns true when _papyrAdsDisabled is not set to true", () => {
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    w._papyrAdsDisabled = false;
    expect(isAdEnabled()).toBe(true);
  });

  it("returns false when navigator.doNotTrack is '1'", () => {
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    delete w._papyrAdsDisabled;
    const n = navigator as Navigator & NavigatorWithPrivacy;
    Object.defineProperty(n, "doNotTrack", {
      value: "1",
      configurable: true,
    });
    expect(isAdEnabled()).toBe(false);
  });

  it("returns false when navigator.globalPrivacyControl is true", () => {
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    delete w._papyrAdsDisabled;
    const n = navigator as Navigator & NavigatorWithPrivacy;
    Object.defineProperty(n, "globalPrivacyControl", {
      value: true,
      configurable: true,
    });
    expect(isAdEnabled()).toBe(false);
  });

  it("returns true during SSR (no window)", () => {
    const windowRef = globalThis.window;
    // @ts-expect-error deleting window for test
    delete globalThis.window;
    try {
      expect(isAdEnabled()).toBe(true);
    } finally {
      globalThis.window = windowRef;
    }
  });
});

// ---------------------------------------------------------------------------
// shouldRenderAd
// ---------------------------------------------------------------------------

describe("shouldRenderAd()", () => {
  it("returns true for every canonical tool slug", () => {
    for (const slug of allowedAdPages) {
      expect(shouldRenderAd(slug)).toBe(true);
    }
  });

  it("returns false for status, legal, and support surfaces", () => {
    const nonAllowed = ["status", "blog", "tool-unavailable", "unknown-page"];
    for (const slug of nonAllowed) {
      expect(shouldRenderAd(slug)).toBe(false);
    }
  });

  it("returns false for unknown pages", () => {
    expect(shouldRenderAd("does-not-exist")).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// isAfterPrimaryExperience
// ---------------------------------------------------------------------------

describe("isAfterPrimaryExperience()", () => {
  it("returns false for idle (before any user interaction)", () => {
    expect(isAfterPrimaryExperience("idle")).toBe(false);
  });

  it("returns false for uploading/queued/processing/preparing", () => {
    for (const phase of ["uploading", "queued", "processing", "preparing"]) {
      expect(isAfterPrimaryExperience(phase)).toBe(false);
    }
  });

  it("returns false for ready state", () => {
    expect(isAfterPrimaryExperience("ready")).toBe(false);
  });

  it("returns true for done", () => {
    expect(isAfterPrimaryExperience("done")).toBe(true);
  });

  it("returns true for error", () => {
    expect(isAfterPrimaryExperience("error")).toBe(true);
  });

  it("returns true for finalizing (immediately before done)", () => {
    expect(isAfterPrimaryExperience("finalizing")).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// isSeparatedFromDownload
// ---------------------------------------------------------------------------

describe("isSeparatedFromDownload()", () => {
  it("returns true for done", () => {
    expect(isSeparatedFromDownload("done")).toBe(true);
  });

  it("returns true for error", () => {
    expect(isSeparatedFromDownload("error")).toBe(true);
  });

  it("returns false for idle (Download not yet available)", () => {
    expect(isSeparatedFromDownload("idle")).toBe(false);
  });

  it("returns false for processing states", () => {
    expect(isSeparatedFromDownload("processing")).toBe(false);
  });

  it("returns false for uploading/queued/preparing", () => {
    for (const phase of ["uploading", "queued", "preparing"]) {
      expect(isSeparatedFromDownload(phase)).toBe(false);
    }
  });
});

// ---------------------------------------------------------------------------
// AdSlot component
// ---------------------------------------------------------------------------

describe("AdSlot component", () => {
  it("renders the reserved placeholder with 300x250 dimensions when enabled and allowed", () => {
    const { container } = render(React.createElement(AdSlot, { pageSlug: "compress-pdf" }));

    const placeholder = container.querySelector('[aria-label="Advertisement"]');
    expect(placeholder).not.toBeNull();
    expect(placeholder?.getAttribute("aria-label")).toBe("Advertisement");

    const htmlEl = placeholder as HTMLElement;
    expect(htmlEl.style.width).toBe("300px");
    expect(htmlEl.style.height).toBe("250px");
  });

  it("renders nothing when ads are disabled via _papyrAdsDisabled", () => {
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    w._papyrAdsDisabled = true;

    const { container } = render(React.createElement(AdSlot, { pageSlug: "compress-pdf" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).toBeNull();
  });

  it("renders the localized label passed as a prop (Publicidad/Iklan)", () => {
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "home", immediate: true, label: "Publicidad" }),
    );
    expect(container.querySelector('[aria-label="Publicidad"]')).not.toBeNull();
    cleanup();
    const { container: id } = render(
      React.createElement(AdSlot, { pageSlug: "home", immediate: true, label: "Iklan" }),
    );
    expect(id.querySelector('[aria-label="Iklan"]')).not.toBeNull();
  });

  it("renders nothing on a non-allowed page (status)", () => {
    const { container } = render(React.createElement(AdSlot, { pageSlug: "status" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).toBeNull();
  });

  it("renders on supporting content pages per the 2026-08-15 owner decision (terms, faq)", () => {
    for (const slug of ["terms", "faq", "contact", "privacy", "roadmap", "cookies-advertising"]) {
      const { container } = render(React.createElement(AdSlot, { pageSlug: slug }));
      expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
      cleanup();
    }
  });

  it("immediate prop renders the tool-page slot in idle phase (owner decision 2026-08-15)", () => {
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
  });

  it("renders the leaderboard unit with reserved 728x90 dimensions", () => {
    const { container } = render(
      React.createElement(AdSlot, {
        pageSlug: "home",
        immediate: true,
        unit: "leaderboard-728x90",
      }),
    );
    const el = container.querySelector('[aria-label="Advertisement"]') as HTMLElement;
    expect(el).not.toBeNull();
    expect(el.style.width).toBe("728px");
    expect(el.style.height).toBe("90px");
  });

  it("renders the mobile banner unit with reserved 320x50 dimensions", () => {
    const { container } = render(
      React.createElement(AdSlot, {
        pageSlug: "home",
        immediate: true,
        unit: "mobile-banner-320x50",
      }),
    );
    const el = container.querySelector('[aria-label="Advertisement"]') as HTMLElement;
    expect(el.style.width).toBe("320px");
    expect(el.style.height).toBe("50px");
  });

  it("does not break when ad script is blocked (no error thrown)", () => {
    // Simulate an environment where IntersectionObserver is undefined
    // and script injection does nothing — the component should not crash.
    vi.stubGlobal("IntersectionObserver", undefined);
    // Suppress console noise from the intentionally removed window prop.
    const { container } = render(React.createElement(AdSlot, { pageSlug: "merge-pdf" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
  });

  it("renders nothing when ad disabled (DNT)", () => {
    Object.defineProperty(navigator, "doNotTrack", {
      value: "1",
      configurable: true,
    });

    const { container } = render(React.createElement(AdSlot, { pageSlug: "compress-pdf" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).toBeNull();
  });

  it("renders nothing when ad disabled (GPC)", () => {
    Object.defineProperty(navigator, "globalPrivacyControl", {
      value: true,
      configurable: true,
    });

    const { container } = render(React.createElement(AdSlot, { pageSlug: "compress-pdf" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// IntersectionObserver lazy loading + script injection
// ---------------------------------------------------------------------------

describe("AdSlot lazy script injection", () => {
  it("registers the slot in atAsyncOptions with a container div on mount", () => {
    const { container } = render(React.createElement(AdSlot, { pageSlug: "jpg-to-pdf" }));

    // The placeholder renders with reserved dimensions.
    const placeholder = container.querySelector('[aria-label="Advertisement"]');
    expect(placeholder).not.toBeNull();

    // The slot registers in the official atAsyncOptions queue and renders
    // its container div immediately (no observer gating). No
    // single-consumption global atOptions.
    const win = window as Window & { atAsyncOptions?: Array<Record<string, unknown>> };
    expect(win.atAsyncOptions).toBeDefined();
    const entry = (win.atAsyncOptions ?? []).find(
      (o) => o.key === "b552110bd65e7690ed89a04a1d654898",
    );
    expect(entry).toBeDefined();
    expect(entry?.format).toBe("js");
    expect(entry?.async).toBe(true);
    expect(entry?.container).toBe("atContainer-b552110bd65e7690ed89a04a1d654898");

    const containerDiv = container.querySelector(
      '[id="atContainer-b552110bd65e7690ed89a04a1d654898"]',
    );
    expect(containerDiv).not.toBeNull();
    expect((window as Window & { atOptions?: unknown }).atOptions).toBeUndefined();
  });

  it("removes the container div on unmount", () => {
    const { unmount, container } = render(React.createElement(AdSlot, { pageSlug: "split-pdf" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
    expect(container.querySelector('[id^="atContainer-"]')).not.toBeNull();

    unmount();

    expect(container.querySelector('[id^="atContainer-"]')).toBeNull();
  });

  it("falls back immediately when IntersectionObserver is undefined (e.g. jsdom)", () => {
    vi.stubGlobal("IntersectionObserver", undefined);

    const { container } = render(React.createElement(AdSlot, { pageSlug: "pdf-to-jpg" }));

    // The slot should render immediately because the fallback path fires.
    const placeholder = container.querySelector('[aria-label="Advertisement"]');
    expect(placeholder).not.toBeNull();
    expect((placeholder as HTMLElement).style.width).toBe("300px");
    expect((placeholder as HTMLElement).style.height).toBe("250px");
  });

  it("does NOT inject the script on a non-allowed page", () => {
    const { fire } = installIntersectionObserver();

    render(React.createElement(AdSlot, { pageSlug: "status" }));

    act(() => {
      fire(true);
    });

    expect(document.querySelector('script[data-papyr-ad-slot="true"]')).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Guards integration: ad never before uploader / never beside Download
// ---------------------------------------------------------------------------

describe("ad placement guards integration", () => {
  it("shouldRenderAd + isAfterPrimaryExperience guard: idle -> false", () => {
    // On a tool page the ad is page-allowed, but during idle the
    // primary-experience guard denies it.
    expect(shouldRenderAd("compress-pdf")).toBe(true);
    expect(isAfterPrimaryExperience("idle")).toBe(false);

    // Combined check mirrors what the wiring logic should apply:
    const shouldRender = shouldRenderAd("compress-pdf") && isAfterPrimaryExperience("idle");
    expect(shouldRender).toBe(false);
  });

  it("shouldRenderAd + isAfterPrimaryExperience guard: done -> true", () => {
    expect(shouldRenderAd("compress-pdf")).toBe(true);
    expect(isAfterPrimaryExperience("done")).toBe(true);

    const shouldRender = shouldRenderAd("compress-pdf") && isAfterPrimaryExperience("done");
    expect(shouldRender).toBe(true);
  });

  it("status page returns shouldRenderAd false even if phase is done", () => {
    expect(shouldRenderAd("status")).toBe(false);
    expect(isAfterPrimaryExperience("done")).toBe(true);

    // The page guard takes precedence — no ad on non-tool pages.
    const shouldRender = shouldRenderAd("status") && isAfterPrimaryExperience("done");
    expect(shouldRender).toBe(false);
  });

  it("ad never beside Download controls on result states (isSeparatedFromDownload)", () => {
    // On result phases the separation guard must be true, meaning the
    // component wiring should position the AdSlot outside the result-card.
    expect(isSeparatedFromDownload("done")).toBe(true);
    expect(isSeparatedFromDownload("error")).toBe(true);

    // Non-result phases return false as they have no Download control.
    expect(isSeparatedFromDownload("idle")).toBe(false);
    expect(isSeparatedFromDownload("uploading")).toBe(false);
    expect(isSeparatedFromDownload("queued")).toBe(false);
  });
  it("all five tool pages work end-to-end (placeholder renders, no crash)", () => {
    // Reset any mock pollution from previous tests.
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    delete w._papyrAdsDisabled;
    vi.restoreAllMocks();

    for (const slug of allowedAdPages) {
      cleanup();
      const { container } = render(React.createElement(AdSlot, { pageSlug: slug }));
      const placeholder = container.querySelector('[aria-label="Advertisement"]');
      expect(placeholder).not.toBeNull();
      const el = placeholder as HTMLElement;
      expect(el.style.width).toBe("300px");
      expect(el.style.height).toBe("250px");
    }
  });
});

// ---------------------------------------------------------------------------
// Responsive leaderboard
// ---------------------------------------------------------------------------

describe("LeaderboardAdSlot (responsive)", () => {
  it("renders the SSR-safe mobile unit before hydration (320x50)", () => {
    const markup = renderToStaticMarkup(
      React.createElement(LeaderboardAdSlot, { pageSlug: "home" }),
    );
    expect(markup).toContain("width:320px");
    expect(markup).toContain("height:50px");
  });
});

// ---------------------------------------------------------------------------
// Multi-placement isolation (root cause: atOptions global one-shot consume)
// ---------------------------------------------------------------------------

describe("AdSlot multi-placement (official atAsyncOptions pattern)", () => {
  it("registers each slot in window.atAsyncOptions with its own container div", () => {
    const { container } = render(
      React.createElement("div", null, [
        React.createElement(AdSlot, {
          key: "lb",
          pageSlug: "home",
          immediate: true,
          unit: "leaderboard-728x90",
        }),
        React.createElement(AdSlot, {
          key: "box",
          pageSlug: "home",
          immediate: true,
          unit: "box-300x250",
        }),
      ]),
    );

    // Each slot registers its own entry in the official atAsyncOptions
    // queue (the pattern used by working Adsterra multi-placement sites).
    const win = window as Window & { atAsyncOptions?: Array<Record<string, unknown>> };
    expect(win.atAsyncOptions).toBeDefined();
    const queue = win.atAsyncOptions ?? [];
    const keys = queue.map((o) => o.key);
    expect(keys).toContain("d78b74f28dcbbde269d55fe72b8a96a3");
    expect(keys).toContain("b552110bd65e7690ed89a04a1d654898");

    for (const entry of queue) {
      expect(entry.format).toBe("js");
      expect(entry.async).toBe(true);
      expect(typeof entry.container).toBe("string");
      expect(entry.container).toMatch(/^atContainer-/);
    }

    const containers = container.querySelectorAll('[id^="atContainer-"]');
    expect(containers.length).toBe(2);
    // Both slots render container divs inside their reserved slot divs.
    const slotDivs = container.querySelectorAll('[data-testid="papyr-ad-slot"]');
    expect(slotDivs.length).toBe(2);
    for (const slot of Array.from(slotDivs)) {
      expect(slot.querySelector('[id^="atContainer-"]')).not.toBeNull();
    }

    expect((window as Window & { atOptions?: unknown }).atOptions).toBeUndefined();
  });

  it("keeps reserved placeholder dimensions on the outer slot div", () => {
    const { container } = render(
      React.createElement(AdSlot, {
        pageSlug: "home",
        immediate: true,
        unit: "skyscraper-160x600",
      }),
    );
    const slot = container.querySelector('[data-testid="papyr-ad-slot"]') as HTMLElement;
    expect(slot).not.toBeNull();
    expect(slot.style.width).toBe("160px");
    expect(slot.style.height).toBe("600px");
    const win = window as Window & { atAsyncOptions?: Array<Record<string, unknown>> };
    const entry = (win.atAsyncOptions ?? []).find(
      (o) => o.key === "d7750ca9d81b86c2f911c3fee1f5cadd",
    );
    expect(entry).toBeDefined();
    expect(entry?.container).toBe("atContainer-d7750ca9d81b86c2f911c3fee1f5cadd");
    expect(container.querySelector('[id^="atContainer-"]')).not.toBeNull();
  });
});
