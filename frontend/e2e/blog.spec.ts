import { expect, test } from "@playwright/test";

test("blog listing shows all articles and article pages are indexable", async ({ page }) => {
  await page.goto("/en/blog");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Blog");
  await expect(page.locator("main ul li")).toHaveCount(5);
  await page
    .getByRole("link", { name: /How to Compress a PDF/i })
    .first()
    .click();
  await expect(page).toHaveURL(/\/en\/blog\/compress-pdf-guide$/);
  await expect(page.getByRole("heading", { level: 1 }).last()).toContainText(
    "How to Compress a PDF",
  );
  const canonical = await page.locator('link[rel="canonical"]').getAttribute("href");
  expect(canonical).toContain("https://budgezen.com/en/blog/");
});
