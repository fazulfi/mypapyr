import { expect, test, type Page } from "@playwright/test";

/**
 * PT-02 advertising behavior, end-to-end.
 *
 * Asserts the first-party ad-slot contract on the rendered app:
 * - allowed pages show exactly one reserved slot when ads are enabled
 *   (one ad per page, commit 8d9fc04);
 * - tool pages defer their slot until the primary experience completes
 *   (FR/DEC-151) and show it afterwards;
 * - the status page stays ad-free (DEC-130);
 * - DNT/GPC opt-out blocks ad delivery (privacy gate);
 * - the house-promo fallback appears when the provider script is blocked.
 *
 * The reserved slot div is the test subject:
 * `div[data-testid="papyr-ad-slot"]` with a localized aria-label
 * ("Advertisement"/"Publicidad"/"Iklan"). We never assert on third-party
 * network calls (they may be blocked in CI); the fallback test instead
 * deliberately aborts the provider request to force the first-party
 * fallback deterministically.
 */

const AD_SLOT = 'div[data-testid="papyr-ad-slot"]';
const PROVIDER_SCRIPT = 'script[data-papyr-ad-slot="true"]';
const FALLBACK = '[data-papyr-fallback="true"]';

/** Localized reserved-slot aria-labels (messages.ads.label). */
const AD_LABEL: Record<string, string> = {
  en: "Advertisement",
  es: "Publicidad",
  id: "Iklan",
};

const PDF_BYTES = Buffer.from(
  "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n" +
    "2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n" +
    "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n" +
    "xref\n0 4\n0000000000 65535 f \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF",
);

/** Mocks the compress-pdf admission/polling/download APIs with a done task. */
async function mockCompressTaskFlow(page: Page): Promise<void> {
  await page.route("**/api/v1/tools/compress-pdf/tasks", (route) =>
    route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({ task_id: "task-e2e-ads", expires_at: "2026-01-01T00:00:00Z" }),
    }),
  );
  await page.route("**/api/v1/tools/compress-pdf/tasks/*/status", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-e2e-ads",
        tool: "compress-pdf",
        state: "done",
        expires_at: "2026-01-01T00:00:00Z",
        result: { output_count: 1, total_bytes: 2048 },
      }),
    }),
  );
  await page.route("**/api/v1/tools/compress-pdf/tasks/*/download/0", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ url: "https://example.test/out.pdf" }),
    }),
  );
}

async function submitCompress(page: Page): Promise<void> {
  await page.setInputFiles('input[type="file"]', {
    name: "test.pdf",
    mimeType: "application/pdf",
    buffer: PDF_BYTES,
  });
  await page.getByRole("button", { name: "Compress" }).click();
}

test.describe("ad behavior", () => {
  test("allowed pages render exactly one reserved ad slot when ads are enabled", async ({
    page,
  }) => {
    for (const locale of ["en", "es", "id"]) {
      await page.goto(`/${locale}`);
      await expect(page.locator(AD_SLOT)).toHaveCount(1);
      await expect(page.locator(AD_SLOT)).toBeVisible();
      await expect(page.locator(AD_SLOT)).toHaveAttribute("aria-label", AD_LABEL[locale]);
    }
  });

  test("/en/privacy renders the reserved ad slot when ads are enabled", async ({ page }) => {
    await page.goto("/en/privacy");
    await expect(page.locator(AD_SLOT)).toHaveCount(1);
    await expect(page.locator(AD_SLOT)).toBeVisible();
    await expect(page.locator(AD_SLOT)).toHaveAttribute("aria-label", "Advertisement");
  });

  test("a tool page defers its slot until the primary experience completes (FR/DEC-151)", async ({
    page,
  }) => {
    await page.goto("/en/compress-pdf");
    // Idle: the phase gate keeps the slot away from the uploader.
    await expect(page.locator(AD_SLOT)).toHaveCount(0);

    await mockCompressTaskFlow(page);
    await submitCompress(page);
    await expect(page.locator(AD_SLOT)).toBeVisible({ timeout: 20000 });
    await expect(page.locator(AD_SLOT)).toHaveCount(1);
  });

  test("status stays ad-free across locales (DEC-130)", async ({ page }) => {
    for (const locale of ["en", "es", "id"]) {
      await page.goto(`/${locale}/status`);
      await expect(page.locator(AD_SLOT)).toHaveCount(0);
      await expect(page.getByLabel(AD_LABEL[locale])).toHaveCount(0);
    }
  });

  test("privacy gate blocks ad delivery on a tool page when DNT/GPC opt out", async ({
    browser,
  }) => {
    const context = await browser.newContext();
    await context.addInitScript(() => {
      Object.defineProperty(navigator, "doNotTrack", { value: "1", configurable: true });
      Object.defineProperty(navigator, "globalPrivacyControl", { value: true, configurable: true });
    });
    const page = await context.newPage();

    try {
      await mockCompressTaskFlow(page);
      await page.goto("/en/compress-pdf");
      expect(await page.evaluate(() => navigator.doNotTrack)).toBe("1");
      expect(
        await page.evaluate(
          () => (navigator as Navigator & { globalPrivacyControl?: boolean }).globalPrivacyControl,
        ),
      ).toBe(true);

      // Idle: phase gate (no slot regardless of privacy state).
      await expect(page.locator(AD_SLOT)).toHaveCount(0);

      // Done phase: the reserved slot stays (442e941) but no provider
      // script, iframe, or fallback may ever appear inside it.
      await submitCompress(page);
      await expect(page.locator(AD_SLOT)).toBeVisible({ timeout: 20000 });
      await expect(page.locator(AD_SLOT).locator(PROVIDER_SCRIPT)).toHaveCount(0);
      await expect(page.locator(AD_SLOT).locator("iframe")).toHaveCount(0);
      await expect(page.locator(FALLBACK)).toHaveCount(0);
    } finally {
      await context.close();
    }
  });

  test("house-promo fallback appears when the provider script is blocked", async ({ page }) => {
    await page.route("**/invoke.js", (route) => route.abort());
    await page.goto("/en");

    await expect(page.locator(FALLBACK)).toBeVisible({ timeout: 15000 });
    await expect(page.locator(FALLBACK).first()).toHaveAttribute("href", "/en");
    await expect(page.locator(FALLBACK).first()).toContainText("Free PDF tools");
    await expect(page.locator(AD_SLOT)).toHaveCount(1);
  });
});
