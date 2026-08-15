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
   * Render immediately on page load (owner decision 2026-08-15) instead
   * of waiting for a tool result phase. The script still loads lazily
   * once the slot enters the viewport.
   */
  immediate?: boolean;
  /** Which Adsterra unit to render (defaults to the 300x250 box). */
  unit?: AdUnitId;
  /** Accessible label for the slot (localized copy from messages.ads.label). */
  label?: string;
}

/**
 * Adsterra ad slot (reserved dimensions, lazy client-side injection).
 *
 * - SSR renders only the reserved placeholder so no layout shift occurs.
 * - The Adsterra snippet (atOptions + invoke.js) is injected into the
 *   slot div — invoke.js renders the iframe at the script's position —
 *   and only after the placeholder becomes visible in the viewport.
 * - The injected nodes are removed on unmount.
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
  // Resolve the accessible label once at mount: explicit prop wins, else the
  // <html lang> from the hydration document, else the neutral fallback.
  const resolvedLabel = label ?? FALLBACK_LABEL;
  const [enabled] = useState<boolean>(() => isAdEnabled());
  const selected: AdUnit = unit !== undefined ? AD_UNITS[unit] : AD_UNITS["box-300x250"];
  const allowed =
    shouldRenderAd(pageSlug) &&
    (immediate || phase === undefined || isAfterPrimaryExperience(phase));

  // Initialize visible to true when IntersectionObserver is unavailable
  // (jsdom, older browsers, SSR before hydration). This avoids a
  // synchronous setState inside the effect body which would violate
  // react-hooks/set-state-in-effect.
  const [visible, setVisible] = useState<boolean>(
    () => typeof window !== "undefined" && typeof IntersectionObserver === "undefined",
  );

  useEffect(() => {
    if (!enabled || !allowed || visible) return;
    const node = slotRef.current;
    if (node === null) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: "200px" },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [enabled, allowed, visible]);

  useEffect(() => {
    if (!enabled || !allowed || !visible) return;

    const slotNode = slotRef.current;
    if (slotNode === null) return;
    const containerId = `atContainer-${selected.key}`;
    if (slotNode.querySelector(`[id="${containerId}"]`) !== null) return;

    // Official Adsterra multi-placement pattern (root cause fix 2026-08-15):
    // invoke.js consumes a SINGLE global window.atOptions and deletes it
    // after the first placement (`m1(window.atOptions, Qt), delete
    // window.atOptions`), so a second invoke.js on the same page renders
    // nothing. The supported way to place multiple units on one page is the
    // atAsyncOptions queue: each slot pushes its own config
    // {key, format:'js', async:true, container:<id>}, renders a <div> with
    // that container id, and loads its own invoke.js. Verified against live
    // working multi-slot Adsterra sites (format 'js' + container div).
    const win = window as Window & {
      atAsyncOptions?: Array<Record<string, unknown>>;
    };
    if (!Array.isArray(win.atAsyncOptions)) win.atAsyncOptions = [];
    win.atAsyncOptions.push({
      key: selected.key,
      format: "js",
      async: true,
      container: containerId,
      params: {},
    });

    const container = document.createElement("div");
    container.id = containerId;
    slotNode.appendChild(container);

    const invokeScript = document.createElement("script");
    invokeScript.type = "text/javascript";
    invokeScript.async = true;
    invokeScript.src = `${ADSTERRA_HOST}/${selected.key}/invoke.js`;
    document.head.appendChild(invokeScript);

    return () => {
      slotNode.innerHTML = "";
    };
  }, [enabled, allowed, visible, selected]);

  if (!enabled || !allowed) return null;

  return (
    <div
      ref={slotRef}
      data-testid="papyr-ad-slot"
      aria-label={resolvedLabel ?? FALLBACK_LABEL}
      style={{
        width: selected.width,
        height: selected.height,
        margin: "0 auto",
      }}
    />
  );
}
