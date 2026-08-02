import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { colors, supportColors, spacing, fontFamily } from "../design-tokens";

const globalsCss = readFileSync(resolve(process.cwd(), "src/app/globals.css"), "utf8");

describe("SH-02 design tokens", () => {
  it("defines the canonical f4b792c Papyr color palette", () => {
    expect(colors).toEqual({
      navy: "#1e3a5f",
      accent: "#2563eb",
      bg: "#f9fafb",
      foreground: "#171717",
    });
  });

  it("documents the required slate / emerald / rose support scale (UX 10.1)", () => {
    expect(supportColors).toEqual({
      "slate-100": "oklch(96.8% 0.007 247.896)",
      "slate-200": "oklch(92.9% 0.013 255.508)",
      "slate-300": "oklch(86.9% 0.022 252.894)",
      "slate-400": "oklch(70.4% 0.04 256.788)",
      "slate-500": "oklch(55.4% 0.046 257.417)",
      "emerald-500": "oklch(69.6% 0.17 162.48)",
      "rose-50": "oklch(96.9% 0.015 12.422)",
      "rose-200": "oklch(89.2% 0.058 10.001)",
      "rose-500": "oklch(64.5% 0.246 16.439)",
    });
  });

  it("defines a consistent spacing scale on a 4px base", () => {
    expect(spacing).toEqual({
      xs: "0.25rem",
      sm: "0.5rem",
      md: "0.75rem",
      lg: "1rem",
      xl: "1.5rem",
      "2xl": "2rem",
      "3xl": "3rem",
    });
  });

  it("wires the DM Sans font variable with the canonical fallback stack", () => {
    expect(fontFamily.sans).toBe('var(--font-dm-sans), "DM Sans", system-ui, sans-serif');
    expect(fontFamily.mono).toContain("monospace");
  });

  it("emits a non-inline @theme block in globals.css (D5)", () => {
    expect(globalsCss).toMatch(/@theme\s*\{/);
    expect(globalsCss).not.toContain("@theme inline");
  });

  it("emits the canonical color tokens inside @theme in globals.css", () => {
    const themeBlock = globalsCss.match(/@theme\s*\{([\s\S]*?)\}/)?.[1] ?? "";
    for (const [key, value] of Object.entries(colors)) {
      expect(themeBlock).toContain(`--color-${key}: ${value};`);
    }
  });

  it("emits the wired font token inside @theme in globals.css (D4)", () => {
    const themeBlock = globalsCss.match(/@theme\s*\{([\s\S]*?)\}/)?.[1] ?? "";
    expect(themeBlock).toContain(
      '--font-sans: var(--font-dm-sans), "DM Sans", system-ui, sans-serif;',
    );
  });

  it("removes the dead --color-background token (D4)", () => {
    expect(globalsCss).not.toContain("--color-background");
  });

  it("does not contain the warm beige/orange palette", () => {
    for (const legacy of ["#f7f3ec", "#1a1815", "#c97b2d", "#efe7d8", "#d9cfbc"]) {
      expect(globalsCss).not.toContain(legacy);
    }
  });

  it("applies the canonical bg and foreground to the body without silent fallback (D5)", () => {
    expect(globalsCss).toMatch(/body\s*\{[\s\S]*var\(--color-bg\)/);
    expect(globalsCss).toMatch(/body\s*\{[\s\S]*var\(--color-foreground\)/);
    expect(globalsCss).toMatch(/html\s*\{[\s\S]*var\(--color-bg\)/);
    expect(globalsCss).toMatch(/html\s*\{[\s\S]*var\(--color-foreground\)/);
  });

  it("keeps the DM Sans family on the body via the wired token", () => {
    expect(globalsCss).toMatch(/body\s*\{[\s\S]*var\(--font-sans\)/);
  });

  it("preserves accessible base styles", () => {
    expect(globalsCss).toMatch(/@media\s*\(prefers-reduced-motion:\s*reduce\)/);
    expect(globalsCss).toMatch(/:focus-visible/);
    expect(globalsCss).toContain("box-sizing: border-box");
    expect(globalsCss).toContain("scrollbar-gutter");
  });

  it("keeps the module and globals.css token values in lockstep", () => {
    const themeBlock = globalsCss.match(/@theme\s*\{([\s\S]*?)\}/)?.[1] ?? "";
    for (const [key, value] of Object.entries(colors)) {
      expect(themeBlock).toContain(`--color-${key}: ${value};`);
    }
  });
});
