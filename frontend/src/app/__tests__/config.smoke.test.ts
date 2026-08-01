import { describe, it, expect } from "vitest";
import nextConfig from "../../../next.config";

describe("frontend configuration", () => {
  it("next.config.ts exists and exports a config object", () => {
    expect(nextConfig).toBeDefined();
    const t = typeof nextConfig;
    expect(t === "object" || t === "function").toBe(true);
  });
});
