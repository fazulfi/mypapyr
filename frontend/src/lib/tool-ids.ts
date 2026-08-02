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

export type ToolId = (typeof TOOL_IDS)[number];

export function isToolId(value: unknown): value is ToolId {
  return typeof value === "string" && (TOOL_IDS as readonly string[]).includes(value);
}
