// papyr — Adsterra ad unit registry (budgezen publisher zones).
// ================================================================
// Single source of truth for every ad unit: zone key, reserved
// dimensions, responsive pairing, and the pages each unit may render on.
//
// The zone keys are public client-side publisher identifiers supplied by
// the owner. They grant no access to Papyr systems or document data.
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
    key: "14278ade858b889df3f9a48a85098165",
    width: 300,
    height: 250,
  },
  "leaderboard-728x90": {
    id: "leaderboard-728x90",
    key: "ed81f188de7abab7b8a0d9913a927205",
    width: 728,
    height: 90,
  },
  "mobile-banner-320x50": {
    id: "mobile-banner-320x50",
    key: "e2dfaa4221ee4a3dca911358c1b8db05",
    width: 320,
    height: 50,
  },
  "banner-468x60": {
    id: "banner-468x60",
    key: "c4481f08be3b70c7319918d35aa4fcb2",
    width: 468,
    height: 60,
  },
  "skyscraper-160x600": {
    id: "skyscraper-160x600",
    key: "f08af336b34c0f385d0f7c7963b901c7",
    width: 160,
    height: 600,
  },
  "half-page-160x300": {
    id: "half-page-160x300",
    key: "da5cac1e0adafcc3bf2523ac944d6806",
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
 * Pages where ads may render (owner decision 2026-08-15, extended 2026-08-17):
 * the homepage, all five tool pages, and every supporting content page
 * (contact, privacy, terms, cookies-advertising, roadmap, faq, status, blog).
 * One reserved-dimension unit renders per page, centered, with the same
 * banner format on supporting pages so the layout stays symmetric.
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
  "status",
  "blog",
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
