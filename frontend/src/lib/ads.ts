// papyr — Adsterra ad unit registry (owner-approved 2026-08-15).
// ===============================================================
// Single source of truth for every ad unit: zone key, reserved
// dimensions, responsive pairing, and the pages each unit may render on.
//
// Owner decisions applied (2026-08-15):
// - Homepage + all five tool pages + supporting content pages may carry ads.
// - Tool pages show ads immediately (idle), not only after results.
// - The 300x250 result-area placement from FR/DEC-151 is retained in
//   addition to the new placements; nothing may obstruct or imitate
//   primary controls (uploader, download, forms).
//
// Privacy: ad scripts load client-side only, lazily; disabled under
// DNT/GPC via isAdEnabled().

/** Adsterra script host. */
export const ADSTERRA_HOST = "https://www.highperformanceformat.com";

/** One Adsterra zone with its reserved dimensions. */
export interface AdUnit {
  /** Stable identifier used by pages and tests. */
  id: AdUnitId;
  /** Adsterra zone key. */
  key: string;
  /** Reserved width in px (anti layout shift). */
  width: number;
  /** Reserved height in px. */
  height: number;
}

export type AdUnitId =
  | "box-300x250"
  | "leaderboard-728x90"
  | "mobile-banner-320x50"
  | "banner-468x60"
  | "skyscraper-160x600"
  | "half-page-160x300";

/** All owner-approved Adsterra zones. */
export const AD_UNITS: Record<AdUnitId, AdUnit> = Object.freeze({
  "box-300x250": {
    id: "box-300x250",
    key: "b552110bd65e7690ed89a04a1d654898",
    width: 300,
    height: 250,
  },
  "leaderboard-728x90": {
    id: "leaderboard-728x90",
    key: "d78b74f28dcbbde269d55fe72b8a96a3",
    width: 728,
    height: 90,
  },
  "mobile-banner-320x50": {
    id: "mobile-banner-320x50",
    key: "ee018a59ef764e1441c33552349209a0",
    width: 320,
    height: 50,
  },
  "banner-468x60": {
    id: "banner-468x60",
    key: "5b954d1bc5abe2a0e4c8d13431e61d9c",
    width: 468,
    height: 60,
  },
  "skyscraper-160x600": {
    id: "skyscraper-160x600",
    key: "d7750ca9d81b86c2f911c3fee1f5cadd",
    width: 160,
    height: 600,
  },
  "half-page-160x300": {
    id: "half-page-160x300",
    key: "fefb15efab5ec11aa8457b17b09775bf",
    width: 160,
    height: 300,
  },
} satisfies Record<AdUnitId, AdUnit>);

/**
 * Responsive leaderboard pairing: desktop 728x90, mobile 320x50. Pages
 * render whichever fits the viewport (matchMedia, client-side only).
 */
export function pickLeaderboardUnit(): AdUnit {
  if (typeof window !== "undefined" && typeof window.matchMedia === "function") {
    return window.matchMedia("(min-width: 768px)").matches
      ? AD_UNITS["leaderboard-728x90"]
      : AD_UNITS["mobile-banner-320x50"];
  }
  // SSR default: the desktop unit reserves space in server HTML.
  return AD_UNITS["leaderboard-728x90"];
}

/**
 * Backwards-compatible exports (existing pages/tests use these).
 */
export const ADSTERRA_KEY = AD_UNITS["box-300x250"].key;
export const AD_SLOT_DIMENSIONS = Object.freeze({
  width: AD_UNITS["box-300x250"].width,
  height: AD_UNITS["box-300x250"].height,
});

/**
 * Pages where ads may render (owner decision 2026-08-15): the homepage,
 * all five tool pages, and supporting content pages (contact, privacy,
 * terms, cookies-advertising, roadmap, faq). The status page stays ad-free
 * so incident information remains immediately readable (DEC-130).
 */
export const allowedAdPages: readonly string[] = Object.freeze([
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

/**
 * Returns `true` when advertisement is allowed on the current client.
 *
 * Ad delivery is disabled when any of the following apply:
 * - `window._papyrAdsDisabled` is explicitly set to `true`
 * - The browser's Do Not Track header is enabled (`"1"`)
 * - The browser's Global Privacy Control signal is active
 *
 * During server-side rendering (no `window`) the function assumes
 * the default enabled state so that the reserved placeholder can be
 * emitted and layout shift prevented.
 */
export function isAdEnabled(): boolean {
  if (typeof window === "undefined") return true;

  try {
    const win = window as Window & { _papyrAdsDisabled?: unknown };
    if (win._papyrAdsDisabled === true) return false;
  } catch {
    // Cross-origin window access may throw; treat as enabled.
  }

  try {
    const nav = navigator as Navigator & {
      doNotTrack?: string;
      globalPrivacyControl?: boolean;
    };
    if (nav.doNotTrack === "1") return false;
    if (nav.globalPrivacyControl === true) return false;
  } catch {
    // navigator access is safe in modern environments, but belt-and-suspenders.
  }

  return true;
}
