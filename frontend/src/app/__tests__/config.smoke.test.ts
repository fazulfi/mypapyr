import { describe, it, expect } from "vitest";
import nextConfig from "../../../next.config";

describe("frontend configuration", () => {
  it("next.config.ts exists and exports a config object", () => {
    expect(nextConfig).toBeDefined();
    const t = typeof nextConfig;
    expect(t === "object" || t === "function").toBe(true);
  });
});

describe("frontend host redirect contract", () => {
  it("redirects only exact legacy hosts to the fixed canonical origin", async () => {
    const redirects = await nextConfig.redirects?.();
    expect(redirects).toBeDefined();
    expect(redirects).toHaveLength(2);

    for (const host of ["mypapyr.com", "www.mypapyr.com"]) {
      const redirect = redirects?.find((entry) =>
        entry.has?.some((condition) => condition.type === "host" && condition.value === host),
      );
      expect(redirect).toMatchObject({
        source: "/:path*",
        destination: "https://budgezen.com/:path*",
        permanent: true,
      });
    }

    const hosts = redirects?.flatMap((entry) =>
      entry.has
        ?.filter((condition) => condition.type === "host")
        .map((condition) => condition.value),
    );
    expect(hosts).not.toContain("budgezen.com");
    expect(hosts).not.toContain("localhost");
    expect(hosts).not.toContain("mypapyr.com.evil.example");
    expect(redirects?.every((entry) => entry.destination === "https://budgezen.com/:path*")).toBe(
      true,
    );
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
