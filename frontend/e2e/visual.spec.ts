import { expect, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const viewports = [375, 768, 1280, 1440] as const;
const routes = [
  "/en",
  "/en/compress-pdf",
  "/en/merge-pdf",
  "/en/split-pdf",
  "/en/jpg-to-pdf",
  "/en/pdf-to-jpg",
  "/en/privacy",
  "/en/nonexistent",
] as const;

const visualOutput = join(process.cwd(), "test-results", "visual");

function screenshotName(route: string, width: number): string {
  const routeName = route.replace(/^\//, "").replace(/\//g, "-") || "home";
  return join(visualOutput, `${routeName}-${width}.png`);
}

function wcagContrastRatio(l1: number, l2: number): number {
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function relativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r / 255, g / 255, b / 255].map((channel) =>
    channel <= 0.03928 ? channel / 12.92 : Math.pow((channel + 0.055) / 1.055, 2.4),
  );
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function parseRgb(rgb: string): [number, number, number] {
  const match = rgb.match(/[\d.]+/g);
  if (!match || match.length < 3) return [0, 0, 0];
  return [Number(match[0]), Number(match[1]), Number(match[2])];
}

function hexLuminance(hex: string): number {
  const value = hex.replace("#", "");
  return relativeLuminance(
    Number.parseInt(value.slice(0, 2), 16),
    Number.parseInt(value.slice(2, 4), 16),
    Number.parseInt(value.slice(4, 6), 16),
  );
}

test.beforeEach(async ({ page }) => {
  await page.route("**/highperformanceformat.com/**", (route) => route.abort());
  await page.addInitScript(() => {
    const shifts: number[] = [];
    Object.defineProperty(window, "__papyrLayoutShifts", { value: shifts, writable: false });
    if ("PerformanceObserver" in window) {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const layoutEntry = entry as PerformanceEntry & {
            hadRecentInput?: boolean;
            value?: number;
          };
          if (!layoutEntry.hadRecentInput && typeof layoutEntry.value === "number") {
            shifts.push(layoutEntry.value);
          }
        }
      }).observe({ type: "layout-shift", buffered: true });
    }
  });
});

test.describe("VL-03 rendered visual verification", () => {
  for (const route of routes) {
    for (const width of viewports) {
      test(`${route} at ${width}px`, async ({ page }) => {
        await page.setViewportSize({ width, height: 900 });
        const response = await page.goto(route, { waitUntil: "domcontentloaded" });
        if (route.endsWith("nonexistent")) {
          expect(response?.status()).toBe(404);
        } else {
          const accent = page.locator('[class~="bg-accent"]').first();
          await expect(accent).toBeAttached();
          await expect(accent).toHaveCSS("background-color", "rgb(37, 99, 235)");
        }
        await expect(page.locator("main#main-content")).toBeVisible();

        mkdirSync(visualOutput, { recursive: true });
        await page.screenshot({ fullPage: true, path: screenshotName(route, width) });
      });
    }
  }

  test("documented token combinations meet WCAG AA", async () => {
    const combinations = [
      ["foreground on bg", "#171717", "#f9fafb"],
      ["navy on bg", "#1e3a5f", "#f9fafb"],
      ["accent on white", "#2563eb", "#ffffff"],
      ["SkipLink white on accent", "#ffffff", "#2563eb"],
    ] as const;

    for (const [label, foreground, background] of combinations) {
      const ratio = wcagContrastRatio(hexLuminance(foreground), hexLuminance(background));
      expect(ratio, `${label} contrast ${ratio.toFixed(2)}:1`).toBeGreaterThanOrEqual(4.5);
    }
  });

  test("computed SkipLink contrast meets WCAG AA", async ({ page }) => {
    await page.goto("/en", { waitUntil: "domcontentloaded" });
    await page.keyboard.press("Tab");
    const focused = page.locator(":focus");
    await expect(focused).toHaveAttribute("href", "#main-content");
    const colors = await focused.evaluate((element) => {
      const style = getComputedStyle(element);
      return { background: style.backgroundColor, foreground: style.color };
    });
    const background = parseRgb(colors.background);
    const foreground = parseRgb(colors.foreground);
    const ratio = wcagContrastRatio(
      relativeLuminance(...background),
      relativeLuminance(...foreground),
    );
    expect(ratio, `SkipLink contrast ${ratio.toFixed(2)}:1`).toBeGreaterThanOrEqual(4.5);
  });

  test("home hero and ad region remain layout-stable on load", async ({ page }) => {
    await page.goto("/en", { waitUntil: "networkidle" });
    await page.waitForTimeout(1000);
    const result = await page.evaluate(() => {
      const root = document.documentElement;
      const shifts =
        (window as Window & { __papyrLayoutShifts?: number[] }).__papyrLayoutShifts ?? [];
      return { cls: shifts.reduce((total, value) => total + value, 0), width: root.clientWidth };
    });
    expect(result.width).toBeGreaterThan(0);
    expect(result.cls, `home CLS was ${result.cls.toFixed(3)}`).toBeLessThan(0.1);
  });
});
