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
  AD_UNITS,
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

  it("exports the supplied Adsterra box key and host", () => {
    expect(ADSTERRA_KEY).toBe("14278ade858b889df3f9a48a85098165");
    expect(ADSTERRA_HOST).toBe("https://www.highperformanceformat.com");
  });
  it("registers every supplied zone with its reserved dimensions", () => {
    expect(AD_UNITS).toMatchObject({
      "banner-468x60": { key: "c4481f08be3b70c7319918d35aa4fcb2", width: 468, height: 60 },
      "box-300x250": { key: "14278ade858b889df3f9a48a85098165", width: 300, height: 250 },
      "half-page-160x300": { key: "da5cac1e0adafcc3bf2523ac944d6806", width: 160, height: 300 },
      "leaderboard-728x90": { key: "ed81f188de7abab7b8a0d9913a927205", width: 728, height: 90 },
      "mobile-banner-320x50": { key: "e2dfaa4221ee4a3dca911358c1b8db05", width: 320, height: 50 },
      "skyscraper-160x600": { key: "f08af336b34c0f385d0f7c7963b901c7", width: 160, height: 600 },
    });
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
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );

    const placeholder = container.querySelector('[aria-label="Advertisement"]');
    expect(placeholder).not.toBeNull();
    expect(placeholder?.getAttribute("aria-label")).toBe("Advertisement");

    const htmlEl = placeholder as HTMLElement;
    expect(htmlEl.style.width).toBe("300px");
    expect(htmlEl.style.height).toBe("250px");
  });

  it("keeps a reserved slot but disables scripts via _papyrAdsDisabled", () => {
    const w = window as Window & { _papyrAdsDisabled?: unknown };
    w._papyrAdsDisabled = true;

    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
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
      const { container } = render(
        React.createElement(AdSlot, { pageSlug: slug, immediate: true }),
      );
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
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "merge-pdf", immediate: true }),
    );
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
  });

  it("keeps a reserved slot while DNT disables ad scripts", () => {
    Object.defineProperty(navigator, "doNotTrack", {
      value: "1",
      configurable: true,
    });

    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
  });

  it("keeps a reserved slot while GPC disables ad scripts", () => {
    Object.defineProperty(navigator, "globalPrivacyControl", {
      value: true,
      configurable: true,
    });

    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    expect(container.querySelector('[aria-label="Advertisement"]')).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
  });
  it("keeps the reserved slot while privacy signals block ad scripts", () => {
    Object.defineProperty(navigator, "doNotTrack", { value: "1", configurable: true });
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    const slot = container.querySelector('[data-testid="papyr-ad-slot"]') as HTMLElement | null;
    expect(slot).not.toBeNull();
    expect(slot?.style.width).toBe("300px");
    expect(slot?.querySelector("script")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// IntersectionObserver lazy loading + script injection
// ---------------------------------------------------------------------------

describe("AdSlot lazy script injection", () => {
  it("injects atOptions + invoke.js inside the slot div on mount (P6 verified)", () => {
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "jpg-to-pdf", immediate: true }),
    );

    const placeholder = container.querySelector('[aria-label="Advertisement"]');
    expect(placeholder).not.toBeNull();

    const slot = container.querySelector('[data-testid="papyr-ad-slot"]') as HTMLElement;
    const atOptions = slot.querySelector('script[data-papyr-atoptions="true"]');
    expect(atOptions).not.toBeNull();
    expect(atOptions?.textContent).toContain("'format': 'iframe'");
    expect(atOptions?.textContent).toContain("14278ade858b889df3f9a48a85098165");

    const invoke = slot.querySelector(
      'script[data-papyr-ad-slot="true"]',
    ) as HTMLScriptElement | null;
    expect(invoke).not.toBeNull();
    expect(invoke?.src).toBe(
      "https://www.highperformanceformat.com/14278ade858b889df3f9a48a85098165/invoke.js",
    );
    expect(invoke?.async).toBe(false);
  });

  it("removes injected scripts on unmount", () => {
    const { unmount, container } = render(
      React.createElement(AdSlot, { pageSlug: "split-pdf", immediate: true }),
    );
    expect(container.querySelector('script[data-papyr-ad-slot="true"]')).not.toBeNull();

    unmount();

    expect(container.querySelector('script[data-papyr-ad-slot="true"]')).toBeNull();
  });

  it("falls back immediately when IntersectionObserver is undefined (e.g. jsdom)", () => {
    vi.stubGlobal("IntersectionObserver", undefined);

    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "pdf-to-jpg", immediate: true }),
    );

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
      const { container } = render(
        React.createElement(AdSlot, { pageSlug: slug, immediate: true }),
      );
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

describe("AdSlot per-slot P6 embed (proven pattern)", () => {
  it("injects the verified atOptions+invoke embed into each slot independently", () => {
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

    const slotDivs = container.querySelectorAll('[data-testid="papyr-ad-slot"]');
    expect(slotDivs.length).toBe(2);

    const firstInvoke = slotDivs[0]?.querySelector('script[data-papyr-ad-slot="true"]');
    expect(firstInvoke).not.toBeNull();
    expect(slotDivs[1]?.querySelector('script[data-papyr-ad-slot="true"]')).toBeNull();
    firstInvoke?.dispatchEvent(new Event("load"));

    const scripts = container.querySelectorAll("script[data-papyr-ad-slot='true']");
    expect(scripts.length).toBe(2);
    const srcs = Array.from(scripts).map((s) => (s as HTMLScriptElement).src);
    expect(srcs.some((src) => src.includes("ed81f188de7abab7b8a0d9913a927205"))).toBe(true);
    expect(srcs.some((src) => src.includes("14278ade858b889df3f9a48a85098165"))).toBe(true);

    // Each slot carries its own atOptions with its own zone key.
    const options = container.querySelectorAll("script[data-papyr-atoptions='true']");
    expect(options.length).toBe(2);
    expect(options[0]?.textContent).toContain("ed81f188de7abab7b8a0d9913a927205");
    expect(options[1]?.textContent).toContain("14278ade858b889df3f9a48a85098165");
  });
  it("waits for the first invoke script before appending the next global atOptions pair", () => {
    const { container } = render(
      React.createElement("div", null, [
        React.createElement(AdSlot, {
          key: "first",
          pageSlug: "home",
          immediate: true,
          unit: "leaderboard-728x90",
        }),
        React.createElement(AdSlot, {
          key: "second",
          pageSlug: "home",
          immediate: true,
          unit: "box-300x250",
        }),
      ]),
    );

    const slots = container.querySelectorAll('[data-testid="papyr-ad-slot"]');
    const firstInvoke = slots[0]?.querySelector('script[data-papyr-ad-slot="true"]');
    expect(firstInvoke).not.toBeNull();
    expect(slots[1]?.querySelector('script[data-papyr-ad-slot="true"]')).toBeNull();

    firstInvoke?.dispatchEvent(new Event("load"));

    expect(slots[1]?.querySelector('script[data-papyr-ad-slot="true"]')).not.toBeNull();
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
    expect(slot.style.width).toBe("160px");
    expect(slot.style.height).toBe("600px");
    expect(slot.querySelector('script[data-papyr-atoptions="true"]')).not.toBeNull();
    expect(slot.querySelector('script[data-papyr-ad-slot="true"]')).not.toBeNull();
  });

  it("removes injected scripts on unmount", () => {
    const { unmount, container } = render(
      React.createElement(AdSlot, { pageSlug: "split-pdf", immediate: true }),
    );
    expect(container.querySelector('script[data-papyr-ad-slot="true"]')).not.toBeNull();

    unmount();

    expect(container.querySelector('script[data-papyr-ad-slot="true"]')).toBeNull();
  });
});
