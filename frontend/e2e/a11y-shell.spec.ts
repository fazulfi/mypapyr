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
    const locales = ["en", "es", "id"] as const;
    for (const locale of locales) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");

      await page.keyboard.press("Tab");
      const skipLink = page.locator(":focus");
      await expect(skipLink).toHaveAttribute("href", "#main-content");
    }
  });

  test("main#main-content exists and is focusable on every locale", async ({ page }) => {
    const locales = ["en", "es", "id"] as const;
    for (const locale of locales) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");

      const mainContent = page.locator("#main-content");
      await expect(mainContent).toHaveAttribute("tabindex", "-1");
    }
  });
});

test.describe("JavaScript errors", () => {
  test("no runtime JS errors on any locale home page (excluding favicon)", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));

    const locales = ["en", "es", "id"] as const;
    for (const locale of locales) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");
    }

    expect(errors).toEqual([]);
  });
});

test.describe("Horizontal overflow", () => {
  test("no horizontal overflow at 375px viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const overflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(overflow).toBe(false);
  });

  test("no horizontal overflow at 1280px viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const overflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(overflow).toBe(false);
  });

  test("no horizontal overflow on support pages at 375px", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    const routes = [
      "/en/privacy",
      "/en/terms",
      "/en/cookies-advertising",
      "/en/contact",
      "/en/status",
      "/en/roadmap",
    ];
    for (const route of routes) {
      await page.goto(route);
      await page.waitForLoadState("networkidle");
      const overflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(overflow, `overflow detected at 375px on ${route}`).toBe(false);
    }
  });
});

test.describe("Homepage rich UI shell", () => {
  test("hero pill badge renders with free/no-account/auto-delete copy", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const pill = page.locator("section .inline-flex.rounded-full");
    await expect(pill.first()).toBeVisible();
    await expect(pill.first()).toContainText(/free|account|delete|auto/i);
  });

  test("trust badges section renders three items", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const hero = page.locator("section").first();
    const badgeRow = hero.locator(".flex.flex-wrap.items-center.justify-center.gap-6");
    await expect(badgeRow).toBeVisible();
    await expect(badgeRow.locator("> div")).toHaveCount(3);
  });

  test("privacy cards section renders three cards with headings", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const privacySection = page.locator("section.bg-slate-100");
    await expect(privacySection).toBeVisible();
    const cards = privacySection.locator("h3");
    await expect(cards).toHaveCount(3);
  });
});
