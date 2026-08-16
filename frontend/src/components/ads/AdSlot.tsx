"use client";

import { useEffect, useRef, useState } from "react";

import { ADSTERRA_HOST, AD_UNITS, isAdEnabled, type AdUnit, type AdUnitId } from "@/lib/ads";

import {
  FALLBACK_TIMEOUT_MS,
  isSlotFilled,
  resolveClientLocale,
  showHouseFallback,
} from "./fallback";
import { isAfterPrimaryExperience, shouldRenderAd } from "./placement";

interface AdLoadEntry {
  slotNode: HTMLDivElement;
  selected: AdUnit;
  cancelled: boolean;
  atOptionsScript?: HTMLScriptElement;
  invokeScript?: HTMLScriptElement;
  finish?: () => void;
  /** Set by `pumpAdLoadQueue` right after this entry's scripts are appended. */
  onInjected?: () => void;
}

const adLoadQueue: AdLoadEntry[] = [];
let activeAdLoad: AdLoadEntry | null = null;

function pumpAdLoadQueue(): void {
  if (activeAdLoad !== null) return;

  const entry = adLoadQueue.shift();
  if (entry === undefined) return;
  if (entry.cancelled) {
    pumpAdLoadQueue();
    return;
  }

  activeAdLoad = entry;
  const atOptionsScript = document.createElement("script");
  atOptionsScript.dataset.papyrAtoptions = "true";
  atOptionsScript.setAttribute("data-cfasync", "false");
  atOptionsScript.text =
    "atOptions = {'key': '" +
    entry.selected.key +
    "','format': 'iframe','height': " +
    entry.selected.height +
    ",'width': " +
    entry.selected.width +
    ",'params': {}};";

  const invokeScript = document.createElement("script");
  invokeScript.dataset.papyrAdSlot = "true";
  invokeScript.dataset.papyrUnit = entry.selected.id;
  invokeScript.setAttribute("data-cfasync", "false");
  invokeScript.type = "text/javascript";
  invokeScript.async = false;
  invokeScript.src = `${ADSTERRA_HOST}/${entry.selected.key}/invoke.js`;

  const finish = () => {
    if (activeAdLoad !== entry) return;
    invokeScript.removeEventListener("load", finish);
    invokeScript.removeEventListener("error", finish);
    activeAdLoad = null;
    entry.finish = undefined;
    pumpAdLoadQueue();
  };

  entry.atOptionsScript = atOptionsScript;
  entry.invokeScript = invokeScript;
  entry.finish = finish;
  invokeScript.addEventListener("load", finish);
  invokeScript.addEventListener("error", finish);
  entry.slotNode.appendChild(atOptionsScript);
  entry.slotNode.appendChild(invokeScript);
  entry.onInjected?.();
}

function enqueueAdLoad(slotNode: HTMLDivElement, selected: AdUnit): AdLoadEntry {
  const entry: AdLoadEntry = { slotNode, selected, cancelled: false };
  adLoadQueue.push(entry);
  pumpAdLoadQueue();
  return entry;
}

function cancelAdLoad(entry: AdLoadEntry): void {
  entry.cancelled = true;
  const queuedIndex = adLoadQueue.indexOf(entry);
  if (queuedIndex >= 0) adLoadQueue.splice(queuedIndex, 1);
  entry.atOptionsScript?.remove();
  entry.invokeScript?.remove();
  if (activeAdLoad === entry) entry.finish?.();
}

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
 * Adsterra ad slot (reserved dimensions, client-side injection) with a
 * first-party house-promo fallback (PT-02).
 *
 * - SSR renders only the reserved placeholder so no layout shift occurs.
 * - The owner-approved unit code (PT-02) is injected client-side: the
 *   zone's `atOptions` config (format 'iframe', reserved width/height)
 *   followed by its invoke.js, both appended INSIDE the slot div. This is
 *   the exact pattern that displayed ads in production (release 5fe86e6,
 *   2026-08-15 18:42 WIB screenshot) — the only configuration ever proven
 *   to render.
 * - If the invoke script errors, or no provider iframe appears within
 *   `FALLBACK_TIMEOUT_MS` of injection, the reserved slot shows a
 *   localized, clearly labeled Papyr promotion (internal link only — no
 *   analytics, no external requests, no document metadata). A MutationObserver
 *   watches for the provider iframe; an iframe cancels the fallback.
 *   Provider ads are never claimed to be fixed — this is a transparent
 *   first-party fallback when the provider fails or no-fills.
 * - Injected nodes, the observer, and the timeout are cleaned up on unmount.
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

  useEffect(() => {
    if (!enabled || !allowed) return;

    const slotNode = slotRef.current;
    if (slotNode === null) return;
    if (slotNode.querySelector("script[data-papyr-ad-slot='true']") !== null) return;

    const entry = enqueueAdLoad(slotNode, selected);
    const locale = resolveClientLocale();
    let settled = false;
    let disposed = false;
    let fallbackTimer: number | null = null;
    let observer: MutationObserver | null = null;
    let onInvokeError: (() => void) | null = null;

    const showFallback = (): void => {
      if (settled || disposed) return;
      if (isSlotFilled(slotNode)) {
        settled = true;
        if (fallbackTimer !== null) window.clearTimeout(fallbackTimer);
        observer?.disconnect();
        return;
      }
      settled = true;
      if (fallbackTimer !== null) window.clearTimeout(fallbackTimer);
      observer?.disconnect();
      cancelAdLoad(entry);
      slotNode.innerHTML = "";
      showHouseFallback(slotNode, locale, selected);
    };

    if (typeof MutationObserver === "function") {
      observer = new MutationObserver(() => {
        if (settled || disposed) return;
        if (isSlotFilled(slotNode)) {
          settled = true;
          if (fallbackTimer !== null) window.clearTimeout(fallbackTimer);
          observer?.disconnect();
        }
      });
      observer.observe(slotNode, { childList: true, subtree: true });
    }

    entry.onInjected = () => {
      if (settled || disposed) return;
      onInvokeError = () => {
        showFallback();
      };
      entry.invokeScript?.addEventListener("error", onInvokeError);
      fallbackTimer = window.setTimeout(showFallback, FALLBACK_TIMEOUT_MS);
    };
    // The queue injects the first entry synchronously; cover both paths.
    if (entry.invokeScript !== undefined) entry.onInjected();

    return () => {
      disposed = true;
      if (fallbackTimer !== null) window.clearTimeout(fallbackTimer);
      observer?.disconnect();
      if (onInvokeError !== null) entry.invokeScript?.removeEventListener("error", onInvokeError);
      cancelAdLoad(entry);
      slotNode.innerHTML = "";
    };
  }, [enabled, allowed, selected]);

  if (!allowed) return null;
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
