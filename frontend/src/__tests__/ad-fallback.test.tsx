// @vitest-environment jsdom
/**
 * PT-02 house-promo fallback: when the Adsterra invoke script errors or no
 * provider iframe appears within the timeout, the reserved slot shows a
 * localized, clearly labeled first-party Papyr promotion; when an iframe
 * appears, no fallback is shown.
 *
 * Covers:
 * - localized fallback copy (EN/ES/ID) under messages.ads.fallback
 * - invoke-script error -> immediate fallback
 * - no iframe within FALLBACK_TIMEOUT_MS -> fallback
 * - provider iframe appearing -> no fallback
 * - queue: a queued slot starts its own timeout at injection, not on mount
 * - unmount cleanup (timeout/observer/scripts)
 * - privacy gating: DNT/GPC/_papyrAdsDisabled keep the reserved slot only
 * - non-allowed page: nothing renders, no fallback
 * - SSR: one reserved slot, zero fallback content
 * - fallback is a first-party internal anchor (no external requests)
 * - locale resolution (pathname, then cookie)
 */
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { act, cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AD_UNITS } from "@/lib/ads";
import { AdSlot } from "@/components/ads/AdSlot";
import {
  FALLBACK_TIMEOUT_MS,
  isSlotFilled,
  localeFromPathname,
  resolveClientLocale,
  showHouseFallback,
} from "@/components/ads/fallback";
import { locales, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

interface NavigatorWithPrivacy {
  doNotTrack?: string;
  globalPrivacyControl?: boolean;
}

const navPrivacy = navigator as Navigator & NavigatorWithPrivacy;
const originalDoNotTrack = navPrivacy.doNotTrack;
const originalGlobalPrivacyControl = navPrivacy.globalPrivacyControl;

function resetAdPrivacySignals(): void {
  const win = window as Window & { _papyrAdsDisabled?: unknown };
  delete win._papyrAdsDisabled;
  const nav = navigator as Navigator & NavigatorWithPrivacy;
  Object.defineProperty(nav, "doNotTrack", { value: originalDoNotTrack, configurable: true });
  Object.defineProperty(nav, "globalPrivacyControl", {
    value: originalGlobalPrivacyControl,
    configurable: true,
  });
}

function clearLocaleCookie(): void {
  document.cookie = "papyr_locale=; Max-Age=0; path=/";
}

function getInvokeScript(container: HTMLElement): HTMLScriptElement | null {
  return container.querySelector('script[data-papyr-ad-slot="true"]');
}

function getFallback(container: HTMLElement): HTMLAnchorElement | null {
  return container.querySelector('[data-papyr-fallback="true"]');
}

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  resetAdPrivacySignals();
  clearLocaleCookie();
  document.head.querySelectorAll("[data-papyr-ad-slot]").forEach((node) => node.remove());
});

// ---------------------------------------------------------------------------
// Localized fallback copy
// ---------------------------------------------------------------------------

describe("messages.ads.fallback localized copy", () => {
  it("defines eyebrow/title/body/cta for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale).ads.fallback;
      expect(copy.eyebrow.length).toBeGreaterThan(0);
      expect(copy.title.length).toBeGreaterThan(0);
      expect(copy.body.length).toBeGreaterThan(0);
      expect(copy.cta.length).toBeGreaterThan(0);
    }
  });

  it("carries distinct localized titles", () => {
    expect(getMessages("en").ads.fallback.title).toBe("Free PDF tools");
    expect(getMessages("es").ads.fallback.title).toBe("Herramientas PDF gratis");
    expect(getMessages("id").ads.fallback.title).toBe("Alat PDF gratis");
  });
});

// ---------------------------------------------------------------------------
// Locale resolution
// ---------------------------------------------------------------------------

describe("fallback locale resolution", () => {
  it("extracts the locale from a locale-prefixed pathname", () => {
    expect(localeFromPathname("/es/comprimir-pdf")).toBe("es");
    expect(localeFromPathname("/id/kompres-pdf")).toBe("id");
    expect(localeFromPathname("/en/compress-pdf")).toBe("en");
  });

  it("returns null for non-locale pathnames", () => {
    expect(localeFromPathname("/")).toBeNull();
    expect(localeFromPathname("/compress")).toBeNull();
    expect(localeFromPathname("/fr/foo")).toBeNull();
  });

  it("falls back to the papyr_locale cookie when the path has no locale", () => {
    document.cookie = "papyr_locale=es; path=/";
    expect(resolveClientLocale()).toBe("es");
  });

  it("defaults to en when neither path nor cookie carry a locale", () => {
    expect(resolveClientLocale()).toBe("en");
  });

  it("detects an iframe as slot fill", () => {
    const div = document.createElement("div");
    expect(isSlotFilled(div)).toBe(false);
    div.appendChild(document.createElement("iframe"));
    expect(isSlotFilled(div)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// showHouseFallback unit behavior
// ---------------------------------------------------------------------------

describe("showHouseFallback", () => {
  it("renders a localized internal anchor without external content", () => {
    const div = document.createElement("div");
    showHouseFallback(div, "es", AD_UNITS["box-300x250"]);

    const anchor = div.querySelector('[data-papyr-fallback="true"]');
    expect(anchor).not.toBeNull();
    expect(anchor?.textContent).toContain("Herramientas PDF gratis");
    expect(anchor?.textContent).toContain("Explorar herramientas");
    expect((anchor as HTMLAnchorElement).getAttribute("href")).toBe("/es");
    expect(div.querySelector("script")).toBeNull();
    expect(div.querySelector("img")).toBeNull();
    expect(div.querySelector("iframe")).toBeNull();
    expect(div.innerHTML).not.toContain("http");
  });

  it("uses a compact single-row layout for short units", () => {
    const div = document.createElement("div");
    showHouseFallback(div, "en", AD_UNITS["mobile-banner-320x50"]);
    expect(div.querySelector('[data-papyr-fallback="true"]')?.textContent).toContain(
      "Free PDF tools",
    );
    expect(div.querySelector('[data-papyr-fallback="true"]')).not.toBeNull();
  });

  it("is idempotent: a second call does not duplicate the promo", () => {
    const div = document.createElement("div");
    showHouseFallback(div, "en", AD_UNITS["box-300x250"]);
    showHouseFallback(div, "en", AD_UNITS["box-300x250"]);
    expect(div.querySelectorAll('[data-papyr-fallback="true"]')).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// AdSlot fallback behavior (fake timers)
// ---------------------------------------------------------------------------

describe("AdSlot house-promo fallback", () => {
  it("shows a localized fallback immediately when the invoke script errors", () => {
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "home", immediate: true }),
    );

    const invoke = getInvokeScript(container);
    expect(invoke).not.toBeNull();
    act(() => {
      invoke?.dispatchEvent(new Event("error"));
    });

    const fallback = getFallback(container);
    expect(fallback).not.toBeNull();
    expect(fallback?.textContent).toContain("Free PDF tools");
    expect(fallback?.textContent).toContain("Explore tools");
    expect(fallback?.getAttribute("href")).toBe("/en");
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelectorAll('[data-testid="papyr-ad-slot"]')).toHaveLength(1);
  });

  it("shows a fallback when no iframe appears within the timeout", () => {
    vi.useFakeTimers();
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "home", immediate: true }),
    );

    expect(getFallback(container)).toBeNull();
    act(() => {
      vi.advanceTimersByTime(FALLBACK_TIMEOUT_MS - 1);
    });
    expect(getFallback(container)).toBeNull();
    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(getFallback(container)).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
  });

  it("keeps the reserved slot ad-only when an iframe appears (no fallback)", async () => {
    vi.useFakeTimers();
    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "home", immediate: true }),
    );

    const slot = container.querySelector('[data-testid="papyr-ad-slot"]');
    await act(async () => {
      slot?.appendChild(document.createElement("iframe"));
    });
    act(() => {
      vi.advanceTimersByTime(FALLBACK_TIMEOUT_MS * 2);
    });

    expect(getFallback(container)).toBeNull();
    expect(slot?.querySelector("iframe")).not.toBeNull();
  });

  it("starts a queued slot's timeout when it is injected, not on mount", () => {
    vi.useFakeTimers();
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
    expect(slots[1]?.querySelector('script[data-papyr-ad-slot="true"]')).toBeNull();

    act(() => {
      firstInvoke?.dispatchEvent(new Event("error"));
    });

    // First slot fell back; the second was just injected, so its own 5s
    // window has not elapsed yet.
    expect(getFallback(slots[0] as HTMLElement)).not.toBeNull();
    expect(slots[1]?.querySelector('script[data-papyr-ad-slot="true"]')).not.toBeNull();
    expect(getFallback(slots[1] as HTMLElement)).toBeNull();

    act(() => {
      vi.advanceTimersByTime(FALLBACK_TIMEOUT_MS);
    });
    expect(getFallback(slots[1] as HTMLElement)).not.toBeNull();
    expect(container.querySelectorAll('[data-papyr-fallback="true"]')).toHaveLength(2);
  });

  it("cleans up timeout, observer, and scripts on unmount", () => {
    vi.useFakeTimers();
    const { unmount, container } = render(
      React.createElement(AdSlot, { pageSlug: "home", immediate: true }),
    );
    expect(getInvokeScript(container)).not.toBeNull();

    unmount();
    act(() => {
      vi.advanceTimersByTime(FALLBACK_TIMEOUT_MS * 2);
    });

    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector('[data-papyr-fallback="true"]')).toBeNull();
    expect(document.body.querySelector('[data-papyr-fallback="true"]')).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Privacy gating: reserved slot only, no script, no fallback
// ---------------------------------------------------------------------------

describe("AdSlot fallback privacy gating", () => {
  it("keeps a reserved slot without fallback when DNT is enabled", () => {
    vi.useFakeTimers();
    Object.defineProperty(navigator, "doNotTrack", { value: "1", configurable: true });

    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    act(() => {
      vi.advanceTimersByTime(FALLBACK_TIMEOUT_MS * 2);
    });

    expect(container.querySelector('[data-testid="papyr-ad-slot"]')).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(getFallback(container)).toBeNull();
  });

  it("keeps a reserved slot without fallback when GPC is enabled", () => {
    vi.useFakeTimers();
    Object.defineProperty(navigator, "globalPrivacyControl", { value: true, configurable: true });

    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    act(() => {
      vi.advanceTimersByTime(FALLBACK_TIMEOUT_MS * 2);
    });

    expect(container.querySelector('[data-testid="papyr-ad-slot"]')).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(getFallback(container)).toBeNull();
  });

  it("keeps a reserved slot without fallback when _papyrAdsDisabled is true", () => {
    vi.useFakeTimers();
    (window as Window & { _papyrAdsDisabled?: unknown })._papyrAdsDisabled = true;

    const { container } = render(
      React.createElement(AdSlot, { pageSlug: "compress-pdf", immediate: true }),
    );
    act(() => {
      vi.advanceTimersByTime(FALLBACK_TIMEOUT_MS * 2);
    });

    expect(container.querySelector('[data-testid="papyr-ad-slot"]')).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(getFallback(container)).toBeNull();
  });

  it("renders nothing (and never a fallback) on a non-allowed page", () => {
    const { container } = render(React.createElement(AdSlot, { pageSlug: "unknown-page" }));
    expect(container.querySelector('[data-testid="papyr-ad-slot"]')).toBeNull();
    expect(getFallback(container)).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// SSR: reserved placeholder only
// ---------------------------------------------------------------------------

describe("AdSlot SSR fallback surface", () => {
  it("emits one reserved slot and zero fallback content", () => {
    const markup = renderToStaticMarkup(
      React.createElement(AdSlot, { pageSlug: "home", immediate: true }),
    );
    expect((markup.match(/data-testid="papyr-ad-slot"/g) ?? []).length).toBe(1);
    expect(markup).toContain('style="width:300px;height:250px;margin:0 auto"');
    expect(markup).not.toContain("papyr-fallback");
    expect(markup).not.toContain("From Papyr");
    expect(markup).not.toContain("highperformanceformat.com");
  });

  it("falls back through AdSlot for every locale copy without breaking the slot", () => {
    for (const locale of locales as readonly Locale[]) {
      cleanup();
      const { container } = render(
        React.createElement(AdSlot, {
          pageSlug: "home",
          immediate: true,
          label: getMessages(locale).ads.label,
        }),
      );
      expect(container.querySelector('[data-testid="papyr-ad-slot"]')).not.toBeNull();
    }
  });
});
