import { test, expect } from "@playwright/test";

test.describe("SkipLink accessibility", () => {
  test("SkipLink is the first tab stop in the page", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    // First Tab should focus the SkipLink
    await page.keyboard.press("Tab");
    const focused = page.locator(":focus");
    await expect(focused).toHaveAttribute("href", "#main-content");
  });

  test("Enter on SkipLink transfers focus to main#main-content", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    // Tab to SkipLink
    await page.keyboard.press("Tab");
    await expect(page.locator(":focus")).toHaveAttribute("href", "#main-content");

    // Press Enter to activate the skip link
    await page.keyboard.press("Enter");

    // main#main-content should now be focused (has tabIndex=-1, so focusable)
    await expect(page.locator("#main-content")).toBeFocused();
  });

  test("SkipLink renders with localized label per locale", async ({ page }) => {
    for (const { locale, label } of [
      { locale: "en", label: "Skip to main content" },
      { locale: "es", label: "Saltar al contenido principal" },
      { locale: "id", label: "Lewati ke konten utama" },
    ]) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");

      // The SkipLink exists in the DOM with the localized label
      const skipLink = page.locator(`a[href="#main-content"]`);
      await expect(skipLink).toBeAttached();
      await expect(skipLink).toContainText(label);
    }
  });

  test("main#main-content exists and is focusable on every locale", async ({ page }) => {
    for (const locale of ["en", "es", "id"]) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");

      const main = page.locator("main#main-content");
      await expect(main).toBeAttached();
      await expect(main).toHaveAttribute("tabindex", "-1");
    }
  });
});

test.describe("JavaScript errors", () => {
  test("no runtime JS errors on any locale home page (excluding favicon)", async ({ page }) => {
    const jsErrors: string[] = [];
    page.on("pageerror", (error) => {
      if (error.message.includes("favicon")) {
        return;
      }
      jsErrors.push(error.message);
    });

    for (const locale of ["en", "es", "id"]) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");
    }

    expect(jsErrors).toEqual([]);
  });
});

test.describe("Horizontal overflow", () => {
  test("no horizontal overflow at 375px viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("no horizontal overflow at 1280px viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("no horizontal overflow on support pages at 375px", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    const supportRoutes = [
      "/en/privacy",
      "/en/terms",
      "/en/cookies-advertising",
      "/en/contact",
      "/en/status",
      "/en/roadmap",
      "/en/blog",
    ];

    for (const route of supportRoutes) {
      // Deterministic readiness instead of networkidle: the Footer's next/link
      // RSC prefetch keeps the network busy indefinitely on short pages
      // (legitimate product behavior — prefetch stays enabled). Wait on rendered
      // content (h1 visible) and then assert the real overflow condition.
      await page.goto(route, { waitUntil: "domcontentloaded" });
      await expect(page.locator("h1")).toBeVisible();

      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
      expect(scrollWidth, `overflow on ${route}`).toBeLessThanOrEqual(clientWidth);
    }
  });
});
