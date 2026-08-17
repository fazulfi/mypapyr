"use client";

/**
 * PT-01 privacy gate for Vercel Analytics and Speed Insights.
 *
 * Gates all automatic pageview, web-vital, and custom events behind the
 * existing DNT / GPC / `_papyrAnalyticsOptOut` opt-out check (ADR-01).
 * When the visitor has expressed an opt-out preference, the `beforeSend`
 * callback returns `null` / `false` — dropping the event before it reaches
 * `va.vercel-scripts.com`.
 *
 * Rendered from the server-side layout; the opt-out check runs client-side
 * at event-send time, so late-setting of the app flag is honoured.
 */
import type { ComponentProps } from "react";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";

import { isOptedOut } from "@/lib/analytics";

/**
 * `BeforeSendEvent` is not exported by @vercel/analytics or
 * @vercel/speed-insights (it is declared locally in each entry point), so the
 * event/return types are derived from the components' own `beforeSend` prop
 * types instead of importing a possibly-missing named type.
 */
type AnalyticsBeforeSend = NonNullable<ComponentProps<typeof Analytics>["beforeSend"]>;
type SpeedBeforeSend = NonNullable<ComponentProps<typeof SpeedInsights>["beforeSend"]>;

/**
 * `beforeSend` for `<Analytics />`. Returns `null` to cancel the event when
 * the visitor has expressed an opt-out preference.
 */
export function analyticsBeforeSend(
  event: Parameters<AnalyticsBeforeSend>[0],
): ReturnType<AnalyticsBeforeSend> {
  return isOptedOut() ? null : event;
}

/**
 * `beforeSend` for `<SpeedInsights />`. Returns `false` to cancel the event
 * when the visitor has expressed an opt-out preference.
 */
export function speedInsightsBeforeSend(
  event: Parameters<SpeedBeforeSend>[0],
): ReturnType<SpeedBeforeSend> {
  return isOptedOut() ? false : event;
}

/** Privacy-gated analytics + speed insights pair for the root layout. */
export function PrivacyAnalytics(): React.ReactNode {
  return (
    <>
      <Analytics beforeSend={analyticsBeforeSend} />
      <SpeedInsights beforeSend={speedInsightsBeforeSend} />
    </>
  );
}
