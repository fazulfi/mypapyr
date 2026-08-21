import { AxeBuilder } from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import axeConfig from "../../axe-config";

const routes = [
  "/en",
  "/es",
  "/id",
  "/en/compress-pdf",
  "/en/merge-pdf",
  "/en/split-pdf",
  "/en/jpg-to-pdf",
  "/en/pdf-to-jpg",
  "/en/privacy",
  "/en/blog",
  "/en/blog/compress-pdf-guide",
  "/en/nonexistent",
  "/en/tool-unavailable?tool=compress-pdf",
] as const;

test.describe.configure({ mode: "parallel" });

test.beforeEach(async ({ page }) => {
  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = request.url();
    if (
      url.includes("highperformanceformat.com") ||
      url.includes("doubleclick.net") ||
      url.includes("googlesyndication.com") ||
      url.includes("adsterra.com") ||
      request.resourceType() === "iframe"
    ) {
      await route.abort();
      return;
    }
    await route.continue();
  });
});

function formatViolations(
  violations: readonly { id: string; help: string; nodes: readonly { target: unknown }[] }[],
): string {
  return violations
    .map(
      (violation) =>
        `${violation.id}: ${violation.help}\\n${violation.nodes
          .map((node) => `  - ${String(node.target)}`)
          .join("\\n")}`,
    )
    .join("\\n");
}

test.describe("WCAG 2.2 AA automated accessibility scans", () => {
  for (const route of routes) {
    test(`has no axe violations: ${route}`, async ({ page }) => {
      await page.goto(route);
      await page.waitForLoadState("networkidle");
      await expect(page.locator("h1").first()).toBeVisible();

      const results = await new AxeBuilder({ page })
        .withTags(axeConfig.runOnly.values)
        .options({ rules: axeConfig.rules })
        .analyze();
      expect(results.violations, formatViolations(results.violations)).toHaveLength(0);
    });
  }
});

test.describe("Keyboard accessibility", () => {
  test("SkipLink is the first tab stop and moves focus to main content", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    await page.keyboard.press("Tab");
    await expect(page.locator(":focus")).toHaveAttribute("href", "#main-content");
    await page.keyboard.press("Enter");
    await expect(page.locator("#main-content")).toBeFocused();
  });

  test("homepage navigation can be tabbed without a focus trap", async ({ page }) => {
    await page.goto("/en");
    await page.waitForLoadState("networkidle");

    const seen = new Set<string>();
    for (let index = 0; index < 80; index += 1) {
      await page.keyboard.press("Tab");
      const focus = await page.locator(":focus").evaluate((element) => ({
        tag: element.tagName,
        id: element.id,
        text: element.textContent?.trim().slice(0, 80) ?? "",
      }));
      expect(focus.tag).toMatch(/^(A|BUTTON|INPUT|SELECT|TEXTAREA|SUMMARY)$/);
      seen.add(`${focus.tag}:${focus.id}:${focus.text}`);
      if (index > 8 && (await page.locator(":focus").count()) === 0) {
        break;
      }
    }
    expect(seen.size).toBeGreaterThan(8);
  });
});
