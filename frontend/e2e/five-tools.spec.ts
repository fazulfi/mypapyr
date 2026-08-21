import { expect, test, type Page } from "@playwright/test";

import {
  fileForTool,
  interceptServerToolFlow,
  minimalPdf,
  minimalJpg,
  submitToolFlow,
  toolFixtures,
  type Locale,
  type ToolFixture,
} from "./helpers";

const locales: Locale[] = ["en", "es", "id"];
const tools = Object.values(toolFixtures);
const toolCases = tools.flatMap((tool) => locales.map((locale) => ({ tool, locale })));

async function blockAds(page: Page): Promise<void> {
  await page.route("**/highperformanceformat.com/**", (route) => route.abort());
  await page.route("**/*invoke.js", (route) => route.abort());
}

async function clearTaskToken(page: Page, tool: ToolFixture): Promise<void> {
  await page.evaluate((toolId) => sessionStorage.removeItem(`papyr:task:${toolId}`), tool.id);
}

async function waitForDone(page: Page): Promise<void> {
  await expect(page.getByRole("button", { name: /Download|Descargar|Unduh/ })).toBeVisible({
    timeout: 15000,
  });
  await expect(
    page.getByRole("button", { name: /Process another|Procesar otro|Proses file/ }),
  ).toBeVisible();
}

async function assertNoRuntimeErrors(page: Page, action: () => Promise<void>): Promise<void> {
  const errors: Error[] = [];
  const onError = (error: Error): void => {
    errors.push(error);
  };
  page.on("pageerror", onError);
  try {
    await action();
    expect(errors).toEqual([]);
  } finally {
    page.off("pageerror", onError);
  }
}

function filesFor(tool: ToolFixture): Array<{ name: string; mimeType: string; buffer: Buffer }> {
  return tool.id === "merge-pdf"
    ? [fileForTool(tool, 0), fileForTool(tool, 1)]
    : [fileForTool(tool)];
}

test.describe("Phase 10 VL-01 five-tool trilingual E2E gate", () => {
  test.beforeEach(async ({ page }) => {
    await blockAds(page);
  });

  for (const { tool, locale } of toolCases) {
    test(`${tool.id} ${locale}: happy path, download, reset, recovery, and layout`, async ({
      page,
    }) => {
      await assertNoRuntimeErrors(page, async () => {
        await clearTaskToken(page, tool);
        const controller = await interceptServerToolFlow(page, tool);
        await page.goto(tool.hrefs[locale]);
        await expect(page.locator("html")).toHaveAttribute("lang", locale);
        await expect(page.locator("h1")).toBeVisible();
        await expect(page.getByTestId("dropzone")).toBeVisible();

        await submitToolFlow(page, tool, locale, filesFor(tool));
        await expect(page.getByRole("status")).toBeVisible();
        controller.setState("processing");
        await expect(page.getByRole("status")).toBeVisible();
        controller.setState("done");
        await waitForDone(page);

        const download = page.getByRole("button", { name: /Download|Descargar|Unduh/ });
        await expect(download).toBeEnabled();
        await expect(
          page.getByRole("button", { name: /Process another|Procesar otro|Proses file/ }),
        ).toBeVisible();

        if (tool.id === "split-pdf") {
          const downloadResponse = page.waitForResponse(
            (response) =>
              response.url().includes("/download/0") && response.request().method() === "GET",
          );
          await download.click();
          await downloadResponse;
        } else {
          const navigation = page.waitForEvent("framenavigated");
          await download.click();
          await navigation;
          await expect(page).toHaveURL("https://example.com/dl");
        }

        await expect(page.getByTestId("dropzone")).toHaveCount(0);
        await expect(
          page.getByRole("button", { name: /Process another|Procesar otro|Proses file/ }),
        ).toBeVisible();
        await expect(
          page.evaluate((toolId) => sessionStorage.getItem(`papyr:task:${toolId}`), tool.id),
        ).resolves.toBeNull();

        await page
          .getByRole("button", { name: /Process another|Procesar otro|Proses file/ })
          .click();
        await expect(page.getByTestId("dropzone")).toBeVisible();
        await expect(page.getByTestId("file-count")).toHaveCount(0);
        await expect(
          page.getByRole("button", { name: tool.submitText[locale], exact: true }),
        ).toBeDisabled();

        await page.evaluate(() => {
          const root = document.documentElement;
          if (root.scrollWidth > root.clientWidth) throw new Error("horizontal overflow");
        });
      });
    });

    test(`${tool.id} ${locale}: retryable error and queued cancellation contract`, async ({
      page,
    }) => {
      await clearTaskToken(page, tool);
      const controller = await interceptServerToolFlow(page, tool, {
        states: ["queued"],
        autoAdvance: false,
        error: { category: "processing", message_key: "states.error", retryable: true },
      });
      await page.goto(tool.hrefs[locale]);
      await submitToolFlow(page, tool, locale, filesFor(tool));
      await expect(page.getByRole("status")).toBeVisible();
      await expect(page.getByRole("button", { name: /Cancel|Cancelar|Batalkan/ })).toHaveCount(0);
      controller.setState("failed");
      await expect(page.locator('[role="alert"][data-retryable="true"]')).toBeVisible({
        timeout: 10000,
      });
      await expect(
        page.getByRole("button", { name: /Try Again|Intentar de nuevo|Coba Lagi/ }),
      ).toBeVisible();
    });
  }

  test("OtherTools links transition through the five canonical routes", async ({ page }) => {
    await page.goto(toolFixtures["compress-pdf"].hrefs.en);
    const chain: ToolFixture[] = [
      toolFixtures["merge-pdf"],
      toolFixtures["split-pdf"],
      toolFixtures["jpg-to-pdf"],
      toolFixtures["pdf-to-jpg"],
    ];
    for (const tool of chain) {
      await page.locator(`a[href="${tool.hrefs.en}"]`).click();
      await expect(page).toHaveURL(tool.hrefs.en);
      await expect(page.locator("h1")).toBeVisible();
    }
  });

  test("mobile and desktop target widths have no document overflow", async ({ page }) => {
    for (const width of [375, 1280]) {
      await page.setViewportSize({ width, height: 800 });
      for (const tool of tools) {
        await page.goto(tool.hrefs.en);
        const overflow = await page.evaluate(
          () => document.documentElement.scrollWidth <= document.documentElement.clientWidth,
        );
        expect(overflow, `${tool.id} overflows at ${width}px`).toBe(true);
      }
    }
  });

  test("shared fixtures are valid for both accepted MIME families", async () => {
    expect(minimalPdf.subarray(0, 5).toString()).toBe("%PDF-");
    expect(minimalJpg.subarray(0, 2).toString("hex")).toBe("ffd8");
  });
});
