import { test, expect } from "@playwright/test";

/**
 * SH-09 dedicated E2E spec: not-found shell, SkipLink focus contrast, and favicon.
 *
 * Contrast verification uses WCAG 2.1 relative-luminance formula computed from
 * getComputedStyle values in the browser, not source-only inspection.
 */

function wcagContrastRatio(l1: number, l2: number): number {
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function relativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r / 255, g / 255, b / 255].map((c) =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4),
  );
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function parseRgb(rgb: string): [number, number, number] {
  const match = rgb.match(/[\d.]+/g);
  if (!match || match.length < 3) {
    return [0, 0, 0];
  }
  return [Number(match[0]), Number(match[1]), Number(match[2])];
}

// ── SkipLink focus contrast ───────────────────────────────────────────

test.describe("SkipLink focus contrast", () => {
  test("focused SkipLink text-on-background contrast meets WCAG AA (≥4.5:1)", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    // Tab to the SkipLink
    await page.keyboard.press("Tab");
    const focused = page.locator(":focus");
    await expect(focused).toHaveAttribute("href", "#main-content");

    // Read computed colors
    const bgStr = await focused.evaluate((el) => window.getComputedStyle(el).backgroundColor);
    const textStr = await focused.evaluate((el) => window.getComputedStyle(el).color);

    const [bR, bG, bB] = parseRgb(bgStr);
    const [tR, tG, tB] = parseRgb(textStr);

    const bgLuminance = relativeLuminance(bR, bG, bB);
    const textLuminance = relativeLuminance(tR, tG, tB);
    const ratio = wcagContrastRatio(bgLuminance, textLuminance);

    expect(
      ratio,
      `SkipLink focus contrast ${ratio.toFixed(2)}:1 did not meet 4.5:1 (bg=${bgStr}, text=${textStr})`,
    ).toBeGreaterThanOrEqual(4.5);
  });

  test("focused SkipLink uses accent background token (#2563eb or equivalent) in all locales", async ({
    page,
  }) => {
    for (const locale of ["en", "es", "id"]) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");

      // Focus the SkipLink
      await page.keyboard.press("Tab");
      const focused = page.locator(":focus");
      await expect(focused).toHaveAttribute("href", "#main-content");

      const bgStr = await focused.evaluate((el) => window.getComputedStyle(el).backgroundColor);
      // The accent should dominate — check it's a blue (#2563eb is rgb(37,99,235))
      const [r, , b] = parseRgb(bgStr);
      expect(b, `${locale}: expected blue-dominant background, got ${bgStr}`).toBeGreaterThan(r);
    }
  });
});

// ── not-found shell ───────────────────────────────────────────────────

test.describe("Root not-found (404) shell", () => {
  test("/nonexistent returns 404 status", async ({ page }) => {
    const response = await page.goto("/nonexistent");
    expect(response?.status()).toBe(404);
  });

  test("/en/nonexistent returns 404 status", async ({ page }) => {
    const response = await page.goto("/en/nonexistent");
    expect(response?.status()).toBe(404);
  });

  test("root 404 has html lang attribute set to resolved locale", async ({ page }) => {
    const response = await page.goto("/nonexistent");
    expect(response?.status()).toBe(404);

    // Root not-found should resolve locale and set lang
    const lang = await page.locator("html").getAttribute("lang");
    expect(["en", "es", "id"]).toContain(lang);
  });

  test("root 404 contains exactly one SkipLink", async ({ page }) => {
    const response = await page.goto("/nonexistent");
    expect(response?.status()).toBe(404);

    const skipLinks = page.locator('a[href="#main-content"]');
    await expect(skipLinks).toHaveCount(1);
  });

  test("root 404 contains exactly one main#main-content with tabIndex=-1", async ({ page }) => {
    const response = await page.goto("/nonexistent");
    expect(response?.status()).toBe(404);

    const main = page.locator("main#main-content");
    await expect(main).toHaveCount(1);
    await expect(main).toHaveAttribute("tabindex", "-1");
  });

  test("root 404 renders localized notFound.title heading", async ({ page }) => {
    // Pre-set the locale cookie so we know which locale the 404 resolves to
    await page.context().addCookies([
      {
        name: "papyr_locale",
        value: "es",
        domain: "localhost",
        path: "/",
        httpOnly: false,
        secure: false,
        sameSite: "Lax" as const,
      },
    ]);
    const response = await page.goto("/nonexistent");
    expect(response?.status()).toBe(404);

    // Spanish notFound.title is "Página no encontrada"
    await expect(page.locator("h1")).toContainText("Página no encontrada");
  });

  test("root 404 renders localized notFound.description", async ({ page }) => {
    await page.context().addCookies([
      {
        name: "papyr_locale",
        value: "id",
        domain: "localhost",
        path: "/",
        httpOnly: false,
        secure: false,
        sameSite: "Lax" as const,
      },
    ]);
    const response = await page.goto("/nonexistent");
    expect(response?.status()).toBe(404);

    // Indonesian notFound.description
    await expect(page.locator("p")).toContainText("tidak ada");
  });

  test("root 404 loads the canonical theme and layout styles", async ({ page }) => {
    const response = await page.goto("/nonexistent", { waitUntil: "domcontentloaded" });
    expect(response?.status()).toBe(404);

    const styles = await page.locator("body").evaluate((body) => {
      const computed = window.getComputedStyle(body);
      return {
        backgroundColor: computed.backgroundColor,
        color: computed.color,
        display: computed.display,
        fontFamily: computed.fontFamily,
        margin: computed.margin,
        minHeight: computed.minHeight,
        viewportHeight: window.innerHeight,
      };
    });

    expect(styles.backgroundColor).toBe("rgb(249, 250, 251)");
    expect(styles.color).toBe("rgb(23, 23, 23)");
    expect(styles.display).toBe("flex");
    expect(styles.fontFamily.toLowerCase()).toContain("dm sans");
    expect(styles.margin).toBe("0px");
    expect(Number.parseFloat(styles.minHeight)).toBeGreaterThanOrEqual(styles.viewportHeight);
  });
});

// ── Favicon ───────────────────────────────────────────────────────────

test.describe("favicon", () => {
  test("GET /favicon.ico returns 200", async ({ request }) => {
    const response = await request.get("/favicon.ico");
    expect(response.status()).toBe(200);
  });

  test("favicon.ico Content-Type is an image type", async ({ request }) => {
    const response = await request.get("/favicon.ico");
    expect(response.status()).toBe(200);
    const contentType = response.headers()["content-type"];
    expect(contentType).toMatch(/^image\//);
  });

  test("favicon exists in all three locale home pages' <head>", async ({ page }) => {
    for (const locale of ["en", "es", "id"]) {
      await page.goto(`/${locale}`);
      await page.waitForLoadState("networkidle");

      const faviconLink = page.locator('link[rel="icon"]');
      await expect(faviconLink).toHaveAttribute("href", "/favicon.ico");
    }
  });
});
