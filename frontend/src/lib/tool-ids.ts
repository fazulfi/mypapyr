// Single authoritative source of the five canonical tool ids, shared by
// catalog.ts and product-status.ts. Imported by both; imports nothing itself,
// so no circular dependency is possible. Grounded in the owner-approved R-15
// slug table and the canonical product UX §8.2/§12 EN identities.
export const TOOL_IDS = Object.freeze([
  "compress-pdf",
  "merge-pdf",
  "split-pdf",
  "jpg-to-pdf",
  "pdf-to-jpg",
] as const);

// The eight deferred legacy tool ids (DEC-194): they are catalogued for the
// localized 410 disposition but are never part of the active five-tool set.
// Kept disjoint from TOOL_IDS; imports nothing itself like TOOL_IDS.
export const LEGACY_TOOL_IDS = Object.freeze([
  "rotate",
  "protect",
  "unlock",
  "watermark",
  "sign",
  "pdf-to-word",
  "ocr",
  "pdf-to-excel",
] as const);

export type LegacyToolId = (typeof LEGACY_TOOL_IDS)[number];

export function isLegacyToolId(value: unknown): value is LegacyToolId {
  return typeof value === "string" && (LEGACY_TOOL_IDS as readonly string[]).includes(value);
}

export type ToolId = (typeof TOOL_IDS)[number];

export function isToolId(value: unknown): value is ToolId {
  return typeof value === "string" && (TOOL_IDS as readonly string[]).includes(value);
}
