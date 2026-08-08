import { test, expect } from "@playwright/test";

const LOCALES = [
  { locale: "en", title: "JPG to PDF", convert: "Convert to PDF", uploading: "Uploading..." },
  { locale: "es", title: "JPG a PDF", convert: "Convertir a PDF", uploading: "Subiendo..." },
  { locale: "id", title: "JPG ke PDF", convert: "Konversi ke PDF", uploading: "Mengunggah..." },
] as const;

test.describe("JPG to PDF tool page", () => {
  for (const { locale, title, convert } of LOCALES) {
    test(`/${locale}/jpg-to-pdf renders localized heading, dropzone, and convert action`, async ({
      page,
    }) => {
      await page.goto(`/${locale}/jpg-to-pdf`);
      await expect(page.locator("h1")).toContainText(title);
      await expect(page.getByTestId("dropzone")).toBeVisible();
      const convertButton = page.getByRole("button", { name: convert });
      await expect(convertButton).toBeVisible();
      await expect(convertButton).toBeDisabled();
    });
  }

  test("jpg-to-pdf returns 200 for all three locales", async ({ page }) => {
    for (const { locale } of LOCALES) {
      const response = await page.goto(`/${locale}/jpg-to-pdf`);
      expect(response?.status(), `expected 200 for /${locale}/jpg-to-pdf`).toBe(200);
    }
  });

  test("jpg-to-pdf sets html lang per locale", async ({ page }) => {
    for (const { locale } of LOCALES) {
      await page.goto(`/${locale}/jpg-to-pdf`);
      await expect(page.locator("html")).toHaveAttribute("lang", locale);
    }
  });

  test("jpg-to-pdf exposes paper policy and metadata disclosure copy", async ({ page }) => {
    await page.goto("/en/jpg-to-pdf");
    await expect(
      page.getByText("Page size and orientation are chosen automatically"),
    ).toBeVisible();
    await expect(page.getByText("Image metadata (EXIF)")).toBeVisible();
  });

  test("jpg-to-pdf file input accepts only image/jpeg", async ({ page }) => {
    await page.goto("/en/jpg-to-pdf");
    const input = page.locator('input[type="file"]');
    await expect(input).toHaveAttribute("accept", "image/jpeg");
  });

  test("jpg-to-pdf has no horizontal overflow at 375px width", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/en/jpg-to-pdf");
    await expect(page.locator("h1")).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("jpg-to-pdf has no horizontal overflow at 1280px width", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/en/jpg-to-pdf");
    await expect(page.locator("h1")).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("jpg-to-pdf produces no runtime JS errors across locales", async ({ page }) => {
    const jsErrors: string[] = [];
    page.on("pageerror", (error) => {
      if (error.message.includes("favicon")) return;
      jsErrors.push(error.message);
    });
    for (const { locale } of LOCALES) {
      await page.goto(`/${locale}/jpg-to-pdf`);
      await expect(page.locator("h1")).toBeVisible();
    }
    expect(jsErrors).toEqual([]);
  });
});
