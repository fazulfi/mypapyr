// papyr — analytics send pipeline (PT-01)
// ========================================
// SSR-guarded, opt-out-aware wrapper around Vercel Analytics (`window.va`).
// Never sends raw error strings — maps them to a closed `errorCategory` enum.
//
// Reviewed against DEC-025, DEC-042, DEC-174, DEC-175, DEC-117.
// Consumed by PT-03 (contact form / result-problem report) via the locked
// `redactPayload` / `trackEvent` signatures.

import {
  ALLOWED_FIELDS,
  bandSize,
  isAllowedField,
  isProhibitedFieldName,
  type AllowedField,
  type CoarseSizeBand,
  type ErrorCategory,
  type FunnelStage,
  type Outcome,
  type ProcessingMode,
  type ToolId,
} from "./analytics-schema";

export {
  ALLOWED_FIELDS,
  bandSize,
  isAllowedField,
  isProhibitedFieldName,
  type AllowedField,
  type CoarseSizeBand,
  type ErrorCategory,
  type FunnelStage,
  type Outcome,
  type ProcessingMode,
  type ToolId,
};

/** Vercel Analytics event sink (injected by @vercel/analytics). */
type VaSink = (type: "event", payload: Record<string, unknown>) => void;

/** Shape of the global analytics object exposed on `window`. */
type VaWindow = Window & { va?: VaSink };

type AnalyticsEventData = Record<string, unknown>;

const SANITIZED_STUB = "[redacted]";

/** Suffixes that identify a string value as a document filename. */
const FILENAME_HINTS = [".pdf", ".jpg", ".jpeg", ".png", ".webp"];

/** Baseline context pre-bound by `useAnalytics`. */
interface AnalyticsContext {
  locale: string;
  tool?: ToolId;
}

/**
 * Returns `true` when a string value looks like a document filename. The
 * redaction layer uses this to coerce document-sensitive values that slipped
 * into an allowed field (e.g. a filename in `referrer`) to a sanitized stub.
 */
function looksLikeFilename(value: string): boolean {
  const lower = value.toLowerCase();
  return FILENAME_HINTS.some((hint) => lower.includes(hint));
}

/**
 * Recursively sanitize a single value. Strings matching a prohibited name or
 * a filename hint are coerced to a stub; object keys matching a prohibited
 * name are dropped.
 */
function redactValue(value: unknown): unknown {
  if (typeof value === "string") {
    if (isProhibitedFieldName(value) || looksLikeFilename(value)) {
      return SANITIZED_STUB;
    }
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((item) => redactValue(item));
  }
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const [key, nestedValue] of Object.entries(record)) {
      if (isProhibitedFieldName(key)) continue;
      out[key] = redactValue(nestedValue);
    }
    return out;
  }
  return value;
}

/**
 * Returns a new object containing only the allowed keys, recursing into
 * nested objects. Values that match a prohibited field name — or look like a
 * document filename — are coerced to a sanitized stub. The original object is
 * never mutated. Locked signature: consumed by PT-03.
 */
export function redactPayload<T extends AnalyticsEventData>(
  data: T,
  allowedKeys: readonly AllowedField[] = ALLOWED_FIELDS,
): Record<string, unknown> {
  const allowed = new Set<string>(allowedKeys);
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(data)) {
    if (!allowed.has(key)) continue;
    out[key] = redactValue(value);
  }
  return out;
}

/**
 * Returns `true` when the visitor has expressed a do-not-track or
 * global-privacy-control preference, or when the app-level opt-out flag is
 * set. Only meaningful in a browser context; safe when `window` or `navigator`
 * is unavailable.
 */
export function isOptedOut(): boolean {
  if (typeof window === "undefined") return false;
  const nav = typeof navigator === "undefined" ? undefined : navigator;
  if (nav) {
    const dnt = (nav as Navigator & { doNotTrack?: string }).doNotTrack;
    if (dnt === "1") return true;
    const gpc = (nav as Navigator & { globalPrivacyControl?: boolean }).globalPrivacyControl;
    if (gpc === true) return true;
  }
  if ((window as Window & { _papyrAnalyticsOptOut?: unknown })._papyrAnalyticsOptOut === true) {
    return true;
  }
  return false;
}

/**
 * Map a raw error to a closed `errorCategory`. Raw error strings/messages are
 * NEVER sent — only the category (DEC-025, DEC-117).
 */
export function errorCategoryFor(value: unknown): ErrorCategory {
  if (value === undefined || value === null) return "internal";
  if (typeof value === "string") {
    const text = value.toLowerCase();
    if (text.includes("invalid")) return "invalid-file";
    if (text.includes("limit")) return "limit-exceeded";
    if (text.includes("unavailable")) return "server-unavailable";
    if (text.includes("expired")) return "expired";
    if (text.includes("cancel")) return "cancelled";
    if (text.includes("encrypt")) return "encrypted";
    if (text.includes("block")) return "blocked";
    return "internal";
  }
  if (typeof value === "object" && value !== null) {
    const record = value as { code?: unknown; category?: unknown; message?: unknown };
    return errorCategoryFor(record.category ?? record.code ?? record.message);
  }
  return "internal";
}

/**
 * Send a named analytics event with a privacy-redacted payload.
 * SSR-safe: on the server this is a no-op. Honors the opt-out flag.
 * Never sends raw error strings — any `error`/`message` key is replaced by a
 * closed `errorCategory`. Locked signature: consumed by PT-03.
 */
export function trackEvent(name: string, data: AnalyticsEventData = {}): void {
  if (typeof window === "undefined") return;
  if (isOptedOut()) return;

  const sink = (window as VaWindow).va;
  if (typeof sink !== "function") return;

  const redacted = redactPayload(data);
  if ("error" in data || "message" in data) {
    const rawError = data.error ?? data.message;
    redacted.errorCategory = errorCategoryFor(rawError);
  }
  sink("event", { name, ...redacted });
}

/** Send a privacy-redacted pageview event. */
export function trackPageView(): void {
  if (typeof window === "undefined") return;
  if (isOptedOut()) return;
  const sink = (window as VaWindow).va;
  if (typeof sink !== "function") return;
  sink("event", { name: "pageview" });
}

/**
 * Analytics helper for client components. Pre-binds the locale (and optional
 * tool) context into every event so call sites never repeat them.
 *
 * The bound `trackEvent` merges context into each event and redacts the final
 * payload, so context values pass through the same privacy gate as event data.
 */
export function useAnalytics(
  locale: string,
  toolId?: ToolId,
): { trackEvent: typeof trackEvent; trackPageView: typeof trackPageView } {
  const context: AnalyticsContext = { locale, ...(toolId ? { tool: toolId } : {}) };

  const boundTrackEvent: typeof trackEvent = (name: string, data: AnalyticsEventData = {}) => {
    trackEvent(name, { ...context, ...data });
  };

  return { trackEvent: boundTrackEvent, trackPageView };
}