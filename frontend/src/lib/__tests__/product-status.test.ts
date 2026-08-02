import { describe, expect, it } from "vitest";

import { TOOL_IDS } from "../tool-ids";
import { productStatus } from "../product-status";

describe("productStatus", () => {
  it("separates available foundation capabilities from planned product workflows", () => {
    expect(productStatus.available).toEqual([
      "frontend-shell",
      "backend-health",
      "deployment-templates",
      "continuous-integration",
    ]);
    expect(productStatus.plannedTools).toEqual([
      "compress-pdf",
      "merge-pdf",
      "split-pdf",
      "jpg-to-pdf",
      "pdf-to-jpg",
    ]);
  });

  it("derives plannedTools from the canonical TOOL_IDS tuple (no duplicated id list)", () => {
    expect(productStatus.plannedTools).toEqual(TOOL_IDS);
  });
});
