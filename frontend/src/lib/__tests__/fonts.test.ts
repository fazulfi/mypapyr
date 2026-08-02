import { describe, it, expect, vi, beforeEach } from "vitest";
import { DM_Sans } from "next/font/google";

vi.mock("next/font/google", () => ({
  DM_Sans: vi.fn(() => ({
    className: "dm-sans-class",
    style: { fontFamily: "var(--font-dm-sans)" },
    variable: "--font-dm-sans",
  })),
}));

describe("Sh-02 DM Sans font foundation", () => {
  beforeEach(() => {
    (DM_Sans as ReturnType<typeof vi.fn>).mockClear();
  });

  it("configures the DM Sans google font through next/font", async () => {
    await import("../fonts");
    const call = (DM_Sans as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(call).toBeDefined();
    const config = call[0] as Record<string, unknown>;
    expect(config.subsets).toContain("latin");
    expect(config.weight).toContain("400");
    expect(config.variable).toBe("--font-dm-sans");
    expect(config.display).toBe("swap");
  });

  it("exports a reusable font with a variable custom property", async () => {
    const { fontSans } = await import("../fonts");
    expect(fontSans).toBeDefined();
    expect((fontSans as { variable?: string }).variable).toBe("--font-dm-sans");
  });
});
