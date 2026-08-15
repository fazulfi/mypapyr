"use client";

import { useEffect, useState } from "react";

import { AD_UNITS, type AdUnit } from "@/lib/ads";

import { AdSlot } from "./AdSlot";

/**
 * Responsive leaderboard: desktop 728x90, mobile 320x50 (owner decision
 * 2026-08-15). The mobile unit reserves SSR space so small viewports never
 * overflow horizontally; after hydration the matching unit for the viewport
 * is chosen via matchMedia and re-evaluated on breakpoint changes.
 */
export function LeaderboardAdSlot({ pageSlug }: { pageSlug: string }): React.ReactElement {
  const [unit, setUnit] = useState<AdUnit>(AD_UNITS["mobile-banner-320x50"]);

  useEffect(() => {
    if (typeof window.matchMedia !== "function") return;
    const query = window.matchMedia("(min-width: 768px)");
    const apply = () => {
      setUnit(query.matches ? AD_UNITS["leaderboard-728x90"] : AD_UNITS["mobile-banner-320x50"]);
    };
    apply();
    query.addEventListener("change", apply);
    return () => query.removeEventListener("change", apply);
  }, []);

  return <AdSlot pageSlug={pageSlug} immediate unit={unit.id} />;
}
