import { test, expect } from "@playwright/test";

const LOCALES = [
  {
    locale: "en",
    title: "Split PDF",
    label: "Page ranges (optional)",
    split: "Split PDF",
    defaultNote: "No ranges entered: one output per source page",
    outputOne: "Output 1: pages 1-3",
    outputTwo: "Output 2: page 5",
    reversedError: "must ascend",
  },
  {
    locale: "es",
    title: "Dividir PDF",
    label: "Intervalos de páginas (opcional)",
    split: "Dividir PDF",
    defaultNote: "Sin intervalos: se genera una salida por cada página",
    outputOne: "Salida 1: páginas 1-3",
    outputTwo: "Salida 2: página 5",
    reversedError: "debe ser ascendente",
  },
  {
    locale: "id",
    title: "Pisah PDF",
    label: "Rentang halaman (opsional)",
    split: "Pisah PDF",
    defaultNote: "Tanpa rentang: satu output untuk setiap halaman",
    outputOne: "Output 1: halaman 1-3",
    outputTwo: "Output 2: halaman 5",
    reversedError: "harus menaik",
  },
] as const;

const PDF_BYTES = Buffer.from(
  "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n" +
    "2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n" +
    "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n" +
    "xref\n0 4\n0000000000 65535 f \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF",
);

const slug: Record<(typeof LOCALES)[number]["locale"], string> = {
  en: "split-pdf",
  es: "dividir-pdf",
  id: "pisahkan-pdf",
};

test.describe("Split PDF tool page", () => {
  for (const { locale, title, label, split } of LOCALES) {
    test(`/${locale}/${slug[locale]} renders localized heading, ranges input, and split action`, async ({
      page,
    }) => {
      await page.goto(`/${locale}/${slug[locale]}`);
      await expect(page.locator("h1")).toContainText(title);
      await expect(page.getByTestId("dropzone")).toBeVisible();
      await expect(page.getByLabel(label)).toBeVisible();
      const splitButton = page.getByRole("button", { name: split });
      await expect(splitButton).toBeVisible();
      await expect(splitButton).toBeDisabled();
    });
  }

  test("split-pdf returns 200 for all three locales", async ({ page }) => {
    for (const { locale } of LOCALES) {
      const response = await page.goto(`/${locale}/${slug[locale]}`);
      expect(response?.status(), `expected 200 for /${locale}/${slug[locale]}`).toBe(200);
    }
  });

  test("split-pdf sets html lang per locale", async ({ page }) => {
    for (const { locale } of LOCALES) {
      await page.goto(`/${locale}/${slug[locale]}`);
      await expect(page.locator("html")).toHaveAttribute("lang", locale);
    }
  });

  test("ranges input exposes help text and omits a placeholder-only instruction", async ({
    page,
  }) => {
    await page.goto("/en/split-pdf");
    const input = page.getByLabel("Page ranges (optional)");
    await expect(input).toBeVisible();
    await expect(input).not.toHaveAttribute("placeholder");
    await expect(input).toHaveAttribute("aria-describedby", /split-ranges-help/);
    await expect(page.getByText("Example: 1-3,5,8-10")).toBeVisible();
  });

  test("shows the default one-output-per-page note when ranges are empty", async ({ page }) => {
    await page.goto("/en/split-pdf");
    await expect(page.getByText("No ranges entered: one output per source page")).toBeVisible();
  });

  for (const { locale, outputOne, outputTwo, defaultNote } of LOCALES) {
    test(`/${locale} live preview reflects valid ordered ranges`, async ({ page }) => {
      await page.goto(`/${locale}/${slug[locale]}`);
      const input = page.locator("#split-ranges");
      await expect(page.getByText(defaultNote)).toBeVisible();
      await input.fill("1-3,5");
      await expect(page.getByText(outputOne)).toBeVisible();
      await expect(page.getByText(outputTwo)).toBeVisible();
      await expect(page.getByText(defaultNote)).toBeHidden();
    });
  }

  for (const { locale, reversedError, split } of LOCALES) {
    test(`/${locale} reversed range shows localized error and blocks submission`, async ({
      page,
    }) => {
      await page.goto(`/${locale}/${slug[locale]}`);
      await page.setInputFiles('input[type="file"]', {
        name: "test.pdf",
        mimeType: "application/pdf",
        buffer: PDF_BYTES,
      });
      const splitButton = page.getByRole("button", { name: split });
      await expect(splitButton).toBeEnabled();
      await page.locator("#split-ranges").fill("5-2");
      await expect(page.getByText(reversedError)).toBeVisible();
      await expect(splitButton).toBeDisabled();
    });
  }

  test("split-pdf has no horizontal overflow at 375px width", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/en/split-pdf");
    await expect(page.locator("h1")).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("split-pdf has no horizontal overflow at 1280px width", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/en/split-pdf");
    await expect(page.locator("h1")).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test("split-pdf produces no runtime JS errors across locales", async ({ page }) => {
    const jsErrors: string[] = [];
    page.on("pageerror", (error) => {
      if (error.message.includes("favicon")) return;
      jsErrors.push(error.message);
    });
    for (const { locale } of LOCALES) {
      await page.goto(`/${locale}/${slug[locale]}`);
      await expect(page.locator("h1")).toBeVisible();
    }
    expect(jsErrors).toEqual([]);
  });
});
