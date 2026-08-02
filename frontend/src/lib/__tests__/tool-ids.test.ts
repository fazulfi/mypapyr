import { describe, expect, it } from "vitest";

import { TOOL_IDS, isToolId, type ToolId } from "../tool-ids";

// SH-04 review fix: tool ids were duplicated in catalog.ts and
// product-status.ts and could drift. tool-ids.ts is the single authoritative
// source; catalog and product-status both derive from it, so the ids stay in
// lockstep without circular imports (tool-ids imports nothing).

describe("TOOL_IDS (single authoritative tool-id source)", () => {
  it("exposes exactly the five canonical tool ids in owner-approved order", () => {
    expect(TOOL_IDS).toEqual([
      "compress-pdf",
      "merge-pdf",
      "split-pdf",
      "jpg-to-pdf",
      "pdf-to-jpg",
    ]);
  });

  it("is frozen so consumers cannot mutate the canonical set", () => {
    expect(Object.isFrozen(TOOL_IDS)).toBe(true);
    const mutable = TOOL_IDS as unknown as string[];
    expect(() => {
      mutable.push("rotate");
    }).toThrow();
  });

  it("isToolId accepts every canonical id", () => {
    for (const id of TOOL_IDS) {
      expect(isToolId(id)).toBe(true);
    }
  });

  it("isToolId rejects aliases, deferred ids, and malformed values", () => {
    expect(isToolId("image-to-pdf")).toBe(false);
    expect(isToolId("pdf-to-image")).toBe(false);
    expect(isToolId("rotate")).toBe(false);
    expect(isToolId("pdf-to-word")).toBe(false);
    expect(isToolId("ocr")).toBe(false);
    expect(isToolId("")).toBe(false);
    expect(isToolId("compress")).toBe(false);
    expect(isToolId("Compress PDF")).toBe(false);
    expect(isToolId(undefined as unknown as string)).toBe(false);
  });

  it("isToolId narrows unknown values to the canonical ToolId type", () => {
    const candidate: unknown = "compress-pdf";
    if (isToolId(candidate)) {
      const narrowed: ToolId = candidate;
      expect(narrowed).toBe("compress-pdf");
    } else {
      expect.unreachable("compress-pdf must be a canonical ToolId");
    }
  });
});
