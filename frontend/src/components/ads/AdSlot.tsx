"use client";

import { useEffect, useRef, useState } from "react";

import {
  AD_SLOT_DIMENSIONS,
  ADSTERRA_HOST,
  ADSTERRA_KEY,
  isAdEnabled,
} from "@/lib/ads";

import { shouldRenderAd } from "./placement";

interface AdSlotProps {
  /** Route slug of the page rendering the slot (e.g. "compress-pdf"). */
  pageSlug: string;
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
 */
export function AdSlot({ pageSlug }: AdSlotProps): React.ReactElement | null {
  const slotRef = useRef<HTMLDivElement | null>(null);
  const [enabled] = useState<boolean>(() => isAdEnabled());
  const allowed = shouldRenderAd(pageSlug);

  // The guard starts false: on non-allowed pages the slot never renders.
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!enabled || !allowed) return;
    const node = slotRef.current;
    if (node === null) return;

    // jsdom (and older browsers) lack IntersectionObserver; in that case
    // treat the slot as visible immediately so nothing silently breaks.
    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }

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
  }, [enabled, allowed]);

  useEffect(() => {
    if (!enabled || !allowed || !visible) return;

    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.type = "text/javascript";
    script.async = true;
    script.dataset.papyrAdSlot = "true";
    script.src = `${ADSTERRA_HOST}/lib/${ADSTERRA_KEY}.js`;
    document.head.appendChild(script);

    return () => {
      const existing = document.getElementById(SCRIPT_ID);
      if (existing !== null && existing.parentNode !== null) {
        existing.parentNode.removeChild(existing);
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