import { test, expect } from "@playwright/test";

const LOCALES = [
  { locale: "en", title: "PDF to JPG", convert: "Convert to JPG", uploading: "Uploading..." },
  { locale: "es", title: "PDF a JPG", convert: "Convertir a JPG", uploading: "Subiendo..." },
  { locale: "id", title: "PDF ke JPG", convert: "Konversi ke JPG", uploading: "Mengunggah..." },
] as const;

test.describe("PDF to JPG tool page", () => {
  for (const { locale, title, convert } of LOCALES) {
    test(`/${locale}/pdf-to-jpg renders localized heading, dropzone, and convert action`, async ({
      page,
    }) => {
      await page.goto(`/${locale}/pdf-to-jpg`);
      await expect(page.locator("h1")).toContainText(title);
      await expect(page.getByTestId("dropzone")).toBeVisible();
      const convertButton = page.getByRole("button", { name: convert });
      await expect(convertButton).toBeVisible();
      await expect(convertButton).toBeDisabled();
    });
  }

  test("pdf-to-jpg returns 200 for all three locales", async ({ page }) => {
    for (const { locale } of LOCALES) {
      const response = await page.goto(`/${locale}/pdf-to-jpg`);
      expect(response?.status(), `expected 200 for /${locale}/pdf-to-jpg`).toBe(200);
    }
  });

  test("pdf-to-jpg sets html lang per locale", async ({ page }) => {
    for (const { locale } of LOCALES) {
      await page.goto(`/${locale}/pdf-to-jpg`);
      await expect(page.locator("html")).toHaveAttribute("lang", locale);
    }
  });

  test("pdf-to-jpg exposes quality profile and resolution disclosure copy", async ({ page }) => {
    await page.goto("/en/pdf-to-jpg");
    await expect(page.getByText("Every page is rendered at one high-quality")).toBeVisible();
    await expect(page.getByText("Conversion cannot add detail that is missing")).toBeVisible();
  });

  test("pdf-to-jpg file input accepts only application/pdf", async ({ page }) => {
    await page.goto("/en/pdf-to-jpg");
    const input = page.locator('input[type="file"]');
    await expect(input).toHaveAttribute("accept", "application/pdf");
  });

  test("pdf-to-jpg has no horizontal overflow at 375px width", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/en/pdf-to-jpg");
    await expect(page.locator("h1")).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("pdf-to-jpg has no horizontal overflow at 1280px width", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/en/pdf-to-jpg");
    await expect(page.locator("h1")).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("pdf-to-jpg produces no runtime JS errors across locales", async ({ page }) => {
    const jsErrors: string[] = [];
    page.on("pageerror", (error) => {
      if (error.message.includes("favicon")) return;
      jsErrors.push(error.message);
    });
    for (const { locale } of LOCALES) {
      await page.goto(`/${locale}/pdf-to-jpg`);
      await expect(page.locator("h1")).toBeVisible();
    }
    expect(jsErrors).toEqual([]);
  });
});
