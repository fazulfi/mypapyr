import { describe, it, expect } from "vitest";
import nextConfig from "../../../next.config";

describe("frontend configuration", () => {
  it("next.config.ts exists and exports a config object", () => {
    expect(nextConfig).toBeDefined();
    const t = typeof nextConfig;
    expect(t === "object" || t === "function").toBe(true);
  });
});

describe("frontend API proxy contract", () => {
  it("rewrites /api/v1/:path* to the configured backend origin", async () => {
    const rewrites = await nextConfig.rewrites?.();
    const api = Array.isArray(rewrites)
      ? rewrites.find((r) => r.source === "/api/v1/:path*")
      : rewrites?.afterFiles?.find((r) => r.source === "/api/v1/:path*");

    expect(api).toBeDefined();
    expect(api?.destination).toMatch(/^https:\/\/api\.mypapyr\.com\/api\/v1\/:path\*$/);
  });
});
