/**
 * Adsterra ad slot configuration.
 *
 * Single-source of truth for ad dimensions, publisher keys, and the
 * enable/disable guard.  The allowed page list is grounded in the
 * canonical TOOL_IDS (see lib/tool-ids.ts).
 */

/** Reserved dimensions used to prevent layout shift. */
export const AD_SLOT_DIMENSIONS = Object.freeze({ width: 300, height: 250 });

/** Adsterra native zone key (300x250). */
export const ADSTERRA_KEY = "b552110bd65e7690ed89a04a1d654898";

/** Adsterra script host. */
export const ADSTERRA_HOST = "https://www.highperformanceformat.com";

/**
 * Canonical list of page slugs where ads may be rendered: the five tool
 * pages plus the homepage (owner decision 2026-08-15). Ads are NEVER
 * rendered on status, legal, support, or other non-tool pages.
 */
export const allowedAdPages: readonly string[] = Object.freeze([
  "home",
  "compress-pdf",
  "merge-pdf",
  "split-pdf",
  "jpg-to-pdf",
  "pdf-to-jpg",
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
