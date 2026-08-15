"use client";

import { useEffect, useRef, useState } from "react";

import { AD_SLOT_DIMENSIONS, ADSTERRA_HOST, ADSTERRA_KEY, isAdEnabled } from "@/lib/ads";

import { isAfterPrimaryExperience, shouldRenderAd } from "./placement";

interface AdSlotProps {
  /** Route slug of the page rendering the slot (e.g. "compress-pdf"). */
  pageSlug: string;
  /**
   * Current tool interaction phase. When provided, the slot only renders
   * after the primary tool experience (done/error/finalizing). Omit to
   * always render (suitable for non-tool surfaces if needed, though ads
   * are page-gated by `allowedAdPages`).
   */
  phase?: string;
}

const SCRIPT_ID = "papyr-adsterra-script";
const PLACEHOLDER_ID = "papyr-adsterra-slot";

/**
 * Adsterra native ad unit (300x250).
 *
 * - SSR renders only the reserved placeholder so no layout shift occurs.
 * - The Adsterra script is injected lazily, on the client, only after the
 *   placeholder becomes visible in the viewport (IntersectionObserver).
 * - The injected script node is removed on unmount.
 * - Never renders on non-allowed pages or when ads are disabled.
 * - When `phase` is provided, the slot waits for the primary tool
 *   experience to complete before rendering.
 */
export function AdSlot({ pageSlug, phase }: AdSlotProps): React.ReactElement | null {
  const slotRef = useRef<HTMLDivElement | null>(null);
  const [enabled] = useState<boolean>(() => isAdEnabled());
  const allowed =
    shouldRenderAd(pageSlug) && (phase === undefined || isAfterPrimaryExperience(phase));

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

    // Owner-approved PT-02 unit code: define the global `atOptions`
    // configuration, then load the zone's invoke.js. Without `atOptions`
    // the script cannot render the 300x250 unit.
    const existing = document.getElementById(SCRIPT_ID);
    if (existing !== null) return;

    const atOptionsScript = document.createElement("script");
    atOptionsScript.dataset.papyrAtoptions = "true";
    atOptionsScript.text =
      "atOptions = {'key': '" +
      ADSTERRA_KEY +
      "','format': 'iframe','height': " +
      AD_SLOT_DIMENSIONS.height +
      ",'width': " +
      AD_SLOT_DIMENSIONS.width +
      ",'params': {}};";
    const invokeScript = document.createElement("script");
    invokeScript.id = SCRIPT_ID;
    invokeScript.type = "text/javascript";
    invokeScript.async = true;
    invokeScript.src = `${ADSTERRA_HOST}/${ADSTERRA_KEY}/invoke.js`;
    invokeScript.dataset.papyrAdSlot = "true";

    document.head.appendChild(atOptionsScript);
    document.head.appendChild(invokeScript);

    return () => {
      const atOptionsNode = document.head.querySelector('script[data-papyr-atoptions="true"]');
      if (atOptionsNode !== null && atOptionsNode.parentNode !== null) {
        atOptionsNode.parentNode.removeChild(atOptionsNode);
      }
      const existingInvoke = document.getElementById(SCRIPT_ID);
      if (existingInvoke !== null && existingInvoke.parentNode !== null) {
        existingInvoke.parentNode.removeChild(existingInvoke);
      }
    };
  }, [enabled, allowed, visible]);

  if (!enabled || !allowed) return null;

  return (
    <div
      ref={slotRef}
      id={PLACEHOLDER_ID}
      aria-label="Advertisement"
      style={{
        width: AD_SLOT_DIMENSIONS.width,
        height: AD_SLOT_DIMENSIONS.height,
      }}
    />
  );
}
