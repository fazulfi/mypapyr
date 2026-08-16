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
import { Analytics, type BeforeSendEvent as AnalyticsBeforeSendEvent } from "@vercel/analytics/next";
import { SpeedInsights, type BeforeSendEvent as SpeedBeforeSendEvent } from "@vercel/speed-insights/next";

import { isOptedOut } from "@/lib/analytics";

/**
 * `beforeSend` for `<Analytics />`. Returns `null` to cancel the event when
 * the visitor has expressed an opt-out preference.
 */
export function analyticsBeforeSend(
  event: AnalyticsBeforeSendEvent,
): AnalyticsBeforeSendEvent | null {
  return isOptedOut() ? null : event;
}

/**
 * `beforeSend` for `<SpeedInsights />`. Returns `false` to cancel the event
 * when the visitor has expressed an opt-out preference.
 */
export function speedInsightsBeforeSend(
  event: SpeedBeforeSendEvent,
): SpeedBeforeSendEvent | false {
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