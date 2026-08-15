// papyr — privacy-reviewed analytics schema (PT-01)
// ===================================================
// Allowed and prohibited field definitions for the analytics pipeline.
//
// STRICT CONTRACT: this module must not contain any prohibited-field key in
// any exported shape. `PROHIBITED_FIELD_NAMES` is exported as an array (whose
// enumerable keys are numeric indices), and the fast lookup table is private —
// so no prohibited name ever appears as an object key in an exported shape.
// Consumers guard against leakage via `isProhibitedFieldName`.
//
// Reviewed against DEC-025, DEC-042, DEC-174, DEC-175, DEC-117.

/** Fields permitted in analytics events. */
export const ALLOWED_FIELDS = Object.freeze([
  "page",
  "locale",
  "referrer",
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "tool",
  "mode",
  "coarseSizeBand",
  "funnel",
  "timing",
  "errorCategory",
  "outcome",
  "webVitals",
  "adPresent",
] as const);

export type AllowedField = (typeof ALLOWED_FIELDS)[number];

/**
 * Field names that are **prohibited** from analytics payloads (DEC-025,
 * DEC-042, DEC-174, DEC-117). If a payload contains one of these keys the
 * redaction layer strips it; if an allowed key's value matches one of these
 * names (e.g. a filename slipped into `referrer`), the value is coerced to a
 * sanitized stub.
 *
 * Exported as an array so the module itself never exposes a prohibited name as
 * an object key in any exported shape.
 */
export const PROHIBITED_FIELD_NAMES = Object.freeze([
  "filename",
  "file",
  "fileName",
  "objectKey",
  "key",
  "signedUrl",
  "url",
  "password",
  "pass",
  "content",
  "text",
  "preview",
  "error",
  "message",
  "stack",
  "fingerprint",
  "deviceId",
  "body",
  "raw",
  "data",
] as const);

// Private static lookup — never exported, so prohibited names never surface as
// object keys in an exported shape.
const PROHIBITED_LOOKUP: Record<string, true> = Object.fromEntries(
  PROHIBITED_FIELD_NAMES.map((name) => [name.toLowerCase(), true]),
);

/**
 * Returns `true` when `key` names a prohibited field (case-insensitive).
 * Used by the redaction layer to strip document-sensitive fields before any
 * event leaves the browser.
 */
export function isProhibitedFieldName(key: string): boolean {
  return PROHIBITED_LOOKUP[key.toLowerCase()] === true;
}

// ---------------------------------------------------------------------------
// Coarse size bands — never exact byte counts, only the band identifier
// ---------------------------------------------------------------------------

export type CoarseSizeBand = "small" | "medium" | "large";

const ONE_MIB = 1048576;
const TEN_MIB = 10485760;

/**
 * Map an exact byte count to a coarse band identifier. Only the band string
 * may be sent to analytics — never the raw byte count.
 *
 *   <= 1 MiB           → "small"
 *   > 1 MiB, <= 10 MiB → "medium"
 *   > 10 MiB           → "large"
 *
 * Non-positive inputs (e.g. an absent size reported as -1) are treated as
 * "small" rather than rejected.
 */
export function bandSize(bytes: number): CoarseSizeBand {
  if (bytes <= 0) return "small";
  if (bytes <= ONE_MIB) return "small";
  if (bytes <= TEN_MIB) return "medium";
  return "large";
}

// ---------------------------------------------------------------------------
// Closed enums
// ---------------------------------------------------------------------------

/** Sanitised failure categories — never the raw error string (DEC-025). */
export type ErrorCategory =
  | "invalid-file"
  | "limit-exceeded"
  | "server-unavailable"
  | "expired"
  | "cancelled"
  | "internal"
  | "encrypted"
  | "blocked";

/** Funnel stage labels. */
export type FunnelStage = "upload" | "queued" | "processing" | "done" | "error";

/** Outcome of a completed server or client operation. */
export type Outcome = "success" | "failure" | "cancelled" | "expired";

/** The processing path that handled the job. */
export type ProcessingMode = "server" | "browser";

/** Canonical tool identifier, aligned with src/lib/tool-ids.ts. */
export type ToolId = "compress-pdf" | "merge-pdf" | "split-pdf" | "jpg-to-pdf" | "pdf-to-jpg";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Returns `true` when `key` is one of the allowed event field names
 * (case-sensitive, exact match against `ALLOWED_FIELDS`).
 */
export function isAllowedField(key: string): key is AllowedField {
  return (ALLOWED_FIELDS as readonly string[]).includes(key);
}
