import { test, expect } from "@playwright/test";

// Touch-target helper: asserts an element's bounding box is at least 44px in
// both dimensions (WCAG 2.5.8 / Apple HIG minimum for mobile).
async function expectTouchTargetAtLeast44px(locator: import("@playwright/test").Locator) {
  const box = await locator.boundingBox();
  expect(box, "element must have a bounding box").not.toBeNull();
  expect(box!.width, "touch target width must be >= 44px").toBeGreaterThanOrEqual(44);
  expect(box!.height, "touch target height must be >= 44px").toBeGreaterThanOrEqual(44);
}

test.describe("Mobile nav (Pixel 7)", () => {
  // All mobile-nav tests need a mobile viewport to see the hamburger
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
  });

  test("hamburger opens the mobile nav accordion", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const nav = page.locator("nav").first();
    const hamburger = nav.locator("button[aria-label]").last();
    await expect(hamburger).toBeVisible();

    // Before open: mobile menu hidden
    const mobileMenu = nav.locator(".md\\:hidden.border-t");
    await expect(mobileMenu).not.toBeVisible();

    await hamburger.click();
    await expect(mobileMenu).toBeVisible();

    // Category accordions visible inside the menu
    const categorySummaries = mobileMenu.locator("summary");
    await expect(categorySummaries.first()).toBeVisible();
  });

  test("hamburger closes the mobile nav accordion", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const nav = page.locator("nav").first();
    const hamburger = nav.locator("button[aria-label]").last();
    const mobileMenu = nav.locator(".md\\:hidden.border-t");

    await hamburger.click();
    await expect(mobileMenu).toBeVisible();

    await hamburger.click();
    await expect(mobileMenu).not.toBeVisible();
  });

  test("category accordion expands to reveal tool links on tap", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const nav = page.locator("nav").first();
    const hamburger = nav.locator("button[aria-label]").last();
    await hamburger.click();

    const mobileMenu = nav.locator(".md\\:hidden.border-t");
    const firstSummary = mobileMenu.locator("summary").first();
    await firstSummary.click();

    // The details element it belongs to becomes open
    const details = mobileMenu.locator("details").first();
    await expect(details).toHaveAttribute("open");
    const links = details.locator("a");
    await expect(links.first()).toBeVisible();
  });

  test("nav hamburger and CTA meet 44px touch targets", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const nav = page.locator("nav").first();
    const hamburger = nav.locator("button[aria-label]").last();
    await expectTouchTargetAtLeast44px(hamburger);

    // Find the mobile CTA (the one in the md:hidden group) by its classes
    const mobileCta = nav.locator("a.flex.min-h-\\[44px\\]");
    if ((await mobileCta.count()) > 0) {
      await expectTouchTargetAtLeast44px(mobileCta.first());
    }
  });

  test("mobile menu items meet 44px touch targets", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const nav = page.locator("nav").first();
    const hamburger = nav.locator("button[aria-label]").last();
    await hamburger.click();

    const mobileMenu = nav.locator(".md\\:hidden.border-t");
    const firstSummary = mobileMenu.locator("summary").first();
    await firstSummary.click();

    const firstLink = mobileMenu.locator("details").first().locator("a").first();
    await expectTouchTargetAtLeast44px(firstLink);
  });
});

test.describe("Tool page mobile (Pixel 7)", () => {
  test("tool page uploader renders on mobile", async ({ page }) => {
    await page.goto("/en/compress-pdf");
    await page.waitForLoadState("networkidle");

    // The dropzone / uploader must be present and visible on mobile
    const uploader = page.locator('[data-testid="dropzone"], input[type="file"]');
    await expect(uploader.first()).toBeVisible();
  });

  test("tool page uploader is wide enough for comfortable tapping (>= 320px)", async ({ page }) => {
    await page.goto("/en/compress-pdf");
    await page.waitForLoadState("networkidle");

    const uploader = page.locator('[data-testid="dropzone"], input[type="file"]');
    const box = await uploader.first().boundingBox();
    expect(box, "uploader must have a bounding box").not.toBeNull();
    expect(box!.width, "uploader should span most of the 375px viewport").toBeGreaterThanOrEqual(320);
  });

  test("no horizontal overflow on tool page at 375px", async ({ page }) => {
    await page.goto("/en/compress-pdf");
    await page.waitForLoadState("networkidle");

    const overflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(overflow).toBe(false);
  });

  test("no horizontal overflow on homepage at 375px", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const overflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(overflow).toBe(false);
  });
});
