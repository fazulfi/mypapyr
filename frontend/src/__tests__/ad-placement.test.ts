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

  it("allowedAdPages matches the five canonical tool slugs", () => {
    expect(allowedAdPages).toEqual([
      "compress-pdf",
      "merge-pdf",
      "split-pdf",
      "jpg-to-pdf",
      "pdf-to-jpg",
    ]);
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
    const nonAllowed = ["status", "terms", "privacy", "faq", "contact", "blog", "roadmap"];
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

  it("renders nothing on a non-allowed page (status)", () => {
    const { container } = render(React.createElement(AdSlot, { pageSlug: "status" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).toBeNull();
  });

  it("renders nothing on a legal page (terms)", () => {
    const { container } = render(React.createElement(AdSlot, { pageSlug: "terms" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).toBeNull();
  });

  it("renders nothing on a support page (faq)", () => {
    const { container } = render(React.createElement(AdSlot, { pageSlug: "faq" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).toBeNull();
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
  it("appends the script node only after IntersectionObserver fires isIntersecting", () => {
    const { fire } = installIntersectionObserver();

    const { container } = render(React.createElement(AdSlot, { pageSlug: "jpg-to-pdf" }));

    // Before observer fires: no script injected.
    expect(document.querySelector(`script#papyr-adsterra-script`)).toBeNull();

    const placeholder = container.querySelector('[aria-label="Advertisement"]');
    expect(placeholder).not.toBeNull();

    // Fire the observer callback — the slot is now visible.
    act(() => {
      fire(true);
    });

    // After observer fires: script is injected.
    const script = document.getElementById("papyr-adsterra-script") as HTMLScriptElement | null;
    expect(script).not.toBeNull();
    expect(script?.src).toBe(
      `https://www.highperformanceformat.com/b552110bd65e7690ed89a04a1d654898/invoke.js`,
    );
    expect(script?.async).toBe(true);
    expect(script?.dataset.papyrAdSlot).toBe("true");
    // The owner-approved unit code defines the global atOptions config
    // (key, iframe format, 300x250 dimensions) before invoke.js loads.
    const atOptions = document.head.querySelector(
      'script[data-papyr-atoptions="true"]',
    ) as HTMLScriptElement | null;
    expect(atOptions).not.toBeNull();
    expect(atOptions?.textContent).toContain("'key'");
    expect(atOptions?.textContent).toContain("b552110bd65e7690ed89a04a1d654898");
    expect(atOptions?.textContent).toContain("'format': 'iframe'");
    expect(atOptions?.textContent).toContain("'height': 250");
    expect(atOptions?.textContent).toContain("'width': 300");
  });

  it("removes the script node on unmount", () => {
    const { fire } = installIntersectionObserver();

    const { unmount, container } = render(React.createElement(AdSlot, { pageSlug: "split-pdf" }));
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();

    // Fire observer to trigger injection.
    act(() => {
      fire(true);
    });

    expect(document.getElementById("papyr-adsterra-script")).not.toBeNull();

    unmount();

    expect(document.getElementById("papyr-adsterra-script")).toBeNull();
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

    expect(document.getElementById("papyr-adsterra-script")).toBeNull();
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
