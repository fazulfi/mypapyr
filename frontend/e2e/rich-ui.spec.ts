import { test, expect } from "@playwright/test";

test.describe("Homepage rich UI", () => {
  test("hero pill badge renders with free/no-account/auto-delete text", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    // Pill badge: inline-flex rounded-full border accent chip above the H1.
    const pill = page.locator("section .inline-flex.rounded-full");
    await expect(pill.first()).toBeVisible();
    await expect(pill.first()).toContainText(/free|account|delete|auto/i);
  });

  test("trust badges section renders three badges", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    // Trust badges: flex wrap row with 3 items below the hero CTA.
    const hero = page.locator("section").first();
    const badgeRow = hero.locator(".flex.flex-wrap.items-center.justify-center.gap-6");
    await expect(badgeRow).toBeVisible();
    const badges = badgeRow.locator("div").filter({ has: page.locator("svg") });
    await expect(badges).toHaveCount(3);
  });

  test("tool cards render with name, description, and footer CTA", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const cards = page.locator("a[data-tool-id]");
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(5);

    // Each card has name, description, and CTA footer
    const firstCard = cards.first();
    await expect(firstCard).toContainText(/compress pdf|merge pdf|split pdf|jpg to pdf|pdf to jpg/i);
    await expect(firstCard.locator(".mt-auto")).toBeVisible();
  });

  test("privacy cards section renders three cards", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    // Privacy section: bg-slate-100 band with grid of 3 cards (icon chip + title + desc)
    const privacySection = page.locator("section.bg-slate-100");
    await expect(privacySection).toBeVisible();
    const cards = privacySection.locator("h3");
    await expect(cards).toHaveCount(3);
  });

  test("FAQ accordion renders three items that expand on click", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const faqDetails = page.locator("details");
    await expect(faqDetails).toHaveCount(3);

    // Click first question – should open
    const firstSummary = faqDetails.first().locator("summary");
    await firstSummary.click();
    await expect(faqDetails.first()).toHaveAttribute("open");
  });
});

test.describe("Navigation categories", () => {
  test("desktop nav shows four category buttons", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    // Desktop category buttons (Basic, Security, Enhancement, Conversion)
    const nav = page.locator("nav").first();
    const desktopCategories = nav.locator(".hidden.md\\:flex button");
    const count = await desktopCategories.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });

  test("each category dropdown opens on click showing tool links", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const nav = page.locator("nav").first();
    const firstCategoryBtn = nav.locator(".hidden.md\\:flex button").first();
    await firstCategoryBtn.click();

    // The dropdown (absolute panel at top-full) appears with tool links
    const dropdown = nav.locator(".absolute.left-0.top-full").first();
    await expect(dropdown).toBeVisible();
    const links = dropdown.locator("a");
    await expect(links.first()).toHaveAttribute("href", /\/en\//);
  });

  test("mobile hamburger opens and closes nav accordion", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const nav = page.locator("nav").first();
    const hamburger = nav.locator("button[aria-label]").last();
    await expect(hamburger).toBeVisible();

    // Open
    await hamburger.click();
    const mobileMenu = nav.locator(".md\\:hidden.border-t");
    await expect(mobileMenu).toBeVisible();

    // Close
    await hamburger.click();
    await expect(mobileMenu).not.toBeVisible();
  });
});

test.describe("Footer columns", () => {
  test("footer has four tool category columns", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const footer = page.locator("footer");
    const categoryHeadings = footer.locator("h3");
    const count = await categoryHeadings.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });

  test("footer has a support column with privacy, terms, contact, status, roadmap", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const footer = page.locator("footer");
    const supportNav = footer.locator("nav").last();
    await expect(supportNav).toBeVisible();
    const links = supportNav.locator("a");
    const linkCount = await links.count();
    expect(linkCount).toBeGreaterThanOrEqual(5);

    // Key support routes must be present
    const hrefs = await links.evaluateAll((els) =>
      els.map((el) => (el as HTMLAnchorElement).getAttribute("href")),
    );
    for (const route of ["/en/privacy", "/en/terms", "/en/contact", "/en/status", "/en/roadmap"]) {
      expect(hrefs.some((href) => href === route)).toBe(true);
    }
  });

  test("footer renders dynamic copyright year", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const currentYear = new Date().getFullYear().toString();
    await expect(page.locator("footer")).toContainText(currentYear);
  });
});

test.describe("OtherTools rail on tool pages", () => {
  test("tool page renders OtherTools section with tool links", async ({ page }) => {
    await page.goto("/en/compress-pdf");
    await page.waitForLoadState("networkidle");

    // OtherTools: section with uppercase heading and 2-col grid of links
    const otherTools = page.locator("main .mt-16.w-full.border-t").last();
    await expect(otherTools).toBeVisible();
    const heading = otherTools.locator("h2");
    await expect(heading).toBeVisible();

    // Has at least one other tool link
    const links = otherTools.locator("a");
    const count = await links.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test("OtherTools links point to different tools, not the current page", async ({ page }) => {
    await page.goto("/en/compress-pdf");
    await page.waitForLoadState("networkidle");

    const links = page.locator("main .mt-16.w-full.border-t a");
    const hrefs = await links.evaluateAll((els) => els.map((el) => (el as HTMLAnchorElement).href));
    for (const href of hrefs) {
      expect(href).not.toContain("compress-pdf");
    }
  });

  test("OtherTools section exists on split-pdf page", async ({ page }) => {
    await page.goto("/en/split-pdf");
    await page.waitForLoadState("networkidle");

    const otherTools = page.locator("main .mt-16.w-full.border-t");
    await expect(otherTools).toBeVisible();
  });
});
