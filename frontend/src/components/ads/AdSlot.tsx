"use client";

import { useEffect, useRef, useState } from "react";

import { ADSTERRA_HOST, AD_UNITS, isAdEnabled, type AdUnit, type AdUnitId } from "@/lib/ads";

import { isAfterPrimaryExperience, shouldRenderAd } from "./placement";

interface AdSlotProps {
  /** Route slug of the page rendering the slot (e.g. "compress-pdf"). */
  pageSlug: string;
  /**
   * Current tool interaction phase. When provided AND `immediate` is not
   * set, the slot only renders after the primary tool experience
   * completes (done/error/finalizing), per the original FR/DEC-151
   * placement. Pages using `immediate` render the placeholder right away.
   */
  phase?: string;
  /**
   * Render immediately on page load (owner decision 2026-08-15).
   */
  immediate?: boolean;
  /** Which Adsterra unit to render (defaults to the 300x250 box). */
  unit?: AdUnitId;
  /** Accessible label for the slot (localized copy from messages.ads.label). */
  label?: string;
}

/**
 * Adsterra ad slot (reserved dimensions, client-side injection).
 *
 * - SSR renders only the reserved placeholder so no layout shift occurs.
 * - The owner-approved unit code is injected client-side: the zone's
 *   `atOptions` (format 'iframe', reserved width/height) followed by its
 *   invoke.js, both appended inside the slot div because invoke.js renders
 *   the ad at the script's own position. This exact pattern was verified
 *   displaying ads in production on 2026-08-15 (release 5fe86e6, single
 *   300x250 slot).
 * - Injected nodes are removed on unmount.
 * - Never renders on non-allowed pages or when ads are disabled (DNT/GPC).
 */
const FALLBACK_LABEL = "Advertisement";

export function AdSlot({
  pageSlug,
  phase,
  immediate = false,
  unit,
  label,
}: AdSlotProps): React.ReactElement | null {
  const slotRef = useRef<HTMLDivElement | null>(null);
  const resolvedLabel = label ?? FALLBACK_LABEL;
  const [enabled] = useState<boolean>(() => isAdEnabled());
  const selected: AdUnit = unit !== undefined ? AD_UNITS[unit] : AD_UNITS["box-300x250"];
  const allowed =
    shouldRenderAd(pageSlug) &&
    (immediate || phase === undefined || isAfterPrimaryExperience(phase));

  // The owner-approved embed renders immediately on the client; no
  // IntersectionObserver gating (it left slots unhydrated on some
  // browsers). Reserved dimensions prevent layout shift. The injected
  // script nodes are the dedup marker — no extra state, because a setState
  // re-render would run this effect's cleanup and wipe the slot.
  useEffect(() => {
    if (!enabled || !allowed) return;

    const slotNode = slotRef.current;
    if (slotNode === null) return;
    if (slotNode.querySelector("script[data-papyr-ad-slot='true']") !== null) return;

    // Owner-approved unit code (PT-02): atOptions defines the zone config,
    // invoke.js renders the iframe at the script's own position — both must
    // live inside the slot div, never in <head> (the iframe would land
    // invisible in the head).
    const atOptionsScript = document.createElement("script");
    atOptionsScript.dataset.papyrAtoptions = "true";
    atOptionsScript.text =
      "atOptions = {'key': '" +
      selected.key +
      "','format': 'iframe','height': " +
      selected.height +
      ",'width': " +
      selected.width +
      ",'params': {}};";

    const invokeScript = document.createElement("script");
    invokeScript.dataset.papyrAdSlot = "true";
    invokeScript.dataset.papyrUnit = selected.id;
    invokeScript.type = "text/javascript";
    invokeScript.async = true;
    invokeScript.src = `${ADSTERRA_HOST}/${selected.key}/invoke.js`;

    slotNode.appendChild(atOptionsScript);
    slotNode.appendChild(invokeScript);

    return () => {
      slotNode.innerHTML = "";
    };
  }, [enabled, allowed, selected]);

  if (!enabled || !allowed) return null;

  return (
    <div
      ref={slotRef}
      data-testid="papyr-ad-slot"
      aria-label={resolvedLabel}
      style={{
        width: selected.width,
        height: selected.height,
        margin: "0 auto",
      }}
    />
  );
}
