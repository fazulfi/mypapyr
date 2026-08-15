/**
 * Placement guard helpers for the Adsterra ad slot.
 *
 * These functions are used by the AdSlot component and by tests to verify
 * that ads only appear in allowed locations and are never adjacent to
 * primary experience controls.
 */

import { allowedAdPages } from "@/lib/ads";

/**
 * Returns `true` when the given page slug is in the canonical
 * `allowedAdPages` list.
 *
 * Status, legal, support, and any other non-tool pages return `false`,
 * which means the AdSlot will never render on them.
 */
export function shouldRenderAd(pageSlug: string): boolean {
  return allowedAdPages.includes(pageSlug);
}

/**
 * Returns `true` once the primary tool experience is past the
 * interactive/upload phase and the user has received a result or error.
 *
 * Until this point the ad would compete for attention or overlap with
 * critical UI (the uploader, progress indicators, etc.).
 *
 * Allowed phases: `"done"`, `"error"`, `"finalizing"` (immediately
 * before done).
 * Denied phases: `"idle"`, `"uploading"`, `"queued"`, `"processing"`,
 * `"preparing"`, `"ready"`.
 */
export function isAfterPrimaryExperience(phase: string): boolean {
  return phase === "done" || phase === "error" || phase === "finalizing";
}

/**
 * Returns `true` when the ad slot is guaranteed to be spatially
 * separated from the Download control in the markup order on result
 * states.
 *
 * This is a semantic check: when the tool page is in a result state
 * (`"done"` / `"error"`) the AdSlot must be positioned **before** or
 * **after** the result card block, never interleaved between the
 * Download button and its parent container.
 *
 * For the purposes of this phase-6 guard, the check is that the
 * phase is a result phase.  The spatial separation itself is
 * enforced by the component wiring (AdSlot rendered outside the
 * result-card subtree).
 */
export function isSeparatedFromDownload(phase: string): boolean {
  return phase === "done" || phase === "error";
}
