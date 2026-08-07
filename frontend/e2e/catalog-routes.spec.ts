import { test, expect } from "@playwright/test";

import { toolCatalog } from "../src/lib/catalog";

interface CatalogRoute {
  locale: "en" | "es" | "id";
  url: string;
  title: string;
  toolId: string;
}

const ROUTES: CatalogRoute[] = toolCatalog.flatMap((tool) =>
  (["en", "es", "id"] as const).map((locale) => ({
    locale,
    url: tool.hrefs[locale],
    title: tool.localizedLabels[locale],
    toolId: tool.id,
  })),
);

test.describe("Catalog route coverage - all five tools across EN/ES/ID", () => {
  test("exactly fifteen catalog routes are covered (5 tools x 3 locales)", () => {
    expect(ROUTES).toHaveLength(15);
    expect(new Set(ROUTES.map((route) => route.url)).size).toBe(15);
  });

  for (const route of ROUTES) {
    // Verify route resolves (200), renders localized content, preserves canonical URL
    test(`${route.url} returns 200`, async ({ page }) => {
      const response = await page.goto(route.url);
      expect(response?.status(), `expected 200 for ${route.url}`).toBe(200);

      // Verify localization: correct html lang attribute
      await expect(page.locator("html")).toHaveAttribute("lang", route.locale);

      // Verify essential elements render
      await expect(page.locator("h1")).toBeVisible();
      await expect(page.getByTestId("dropzone")).toBeVisible();
    });

    test(`${route.url} preserves translated slug in browser address bar`, async ({ page }) => {
      await page.goto(route.url);
      const landed = new URL(page.url()).pathname;
      expect(landed, `translated slug must stay canonical for ${route.url}`).toBe(route.url);
    });
  }

  test("canonical localized URL is preserved in the browser (no redirect for translated slugs)", async ({
    page,
  }) => {
    for (const route of ROUTES) {
      await page.goto(route.url);
      const landed = new URL(page.url()).pathname;
      expect(landed, `translated slug must stay canonical for ${route.url}`).toBe(route.url);
    }
  });

  test("catalog routes produce no runtime JS errors", async ({ page }) => {
    const jsErrors: string[] = [];
    page.on("pageerror", (error) => {
      if (error.message.includes("favicon")) return;
      jsErrors.push(error.message);
    });
    for (const route of ROUTES) {
      await page.goto(route.url);
      await expect(page.locator("h1")).toBeVisible();
    }
    expect(jsErrors).toEqual([]);
  });

  test("catalog routes have no horizontal overflow at 375px width", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    for (const route of ROUTES) {
      await page.goto(route.url);
      await expect(page.locator("h1")).toBeVisible();
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
      expect(scrollWidth, `overflow on ${route.url}`).toBeLessThanOrEqual(clientWidth);
    }
  });
});
