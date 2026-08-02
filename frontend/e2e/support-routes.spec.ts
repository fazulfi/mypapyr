import { test, expect } from "@playwright/test";

test.describe("Localized support routes", () => {
  test("/en/privacy renders localized heading", async ({ page }) => {
    await page.goto("/en/privacy");
    await expect(page.locator("h1")).toContainText("Privacy");
  });

  test("/es/privacy renders localized heading", async ({ page }) => {
    await page.goto("/es/privacy");
    await expect(page.locator("h1")).toContainText("Privacidad");
  });

  test("/id/privacy renders localized heading", async ({ page }) => {
    await page.goto("/id/privacy");
    await expect(page.locator("h1")).toContainText("Privasi");
  });

  test("/en/terms renders localized heading", async ({ page }) => {
    await page.goto("/en/terms");
    await expect(page.locator("h1")).toContainText("Terms of Service");
  });

  test("/es/terms renders localized heading", async ({ page }) => {
    await page.goto("/es/terms");
    await expect(page.locator("h1")).toContainText("Términos de servicio");
  });

  test("/id/terms renders localized heading", async ({ page }) => {
    await page.goto("/id/terms");
    await expect(page.locator("h1")).toContainText("Ketentuan Layanan");
  });

  test("/en/cookies-advertising renders localized heading", async ({ page }) => {
    await page.goto("/en/cookies-advertising");
    await expect(page.locator("h1")).toContainText("Cookies & Advertising");
  });

  test("/en/contact renders localized heading", async ({ page }) => {
    await page.goto("/en/contact");
    await expect(page.locator("h1")).toContainText("Contact");
  });

  test("/en/status renders localized heading", async ({ page }) => {
    await page.goto("/en/status");
    await expect(page.locator("h1")).toContainText("Status");
  });

  test("/id/status renders localized heading", async ({ page }) => {
    await page.goto("/id/status");
    await expect(page.locator("h1")).toContainText("Status");
  });

  test("/en/roadmap renders localized heading", async ({ page }) => {
    await page.goto("/en/roadmap");
    await expect(page.locator("h1")).toContainText("Roadmap");
  });

  test("/id/blog renders localized heading", async ({ page }) => {
    await page.goto("/id/blog");
    await expect(page.locator("h1")).toContainText("Blog");
  });

  test("/en/blog renders localized heading", async ({ page }) => {
    await page.goto("/en/blog");
    await expect(page.locator("h1")).toContainText("Blog");
  });

  test("unsupported locale-like prefix /fr/status strips to /en/status (307)", async ({
    request,
  }) => {
    const response = await request.get("/fr/status", { maxRedirects: 0 });
    expect(response.status()).toBe(307);
    expect(response.headers()["location"]).toBe("/en/status");
  });

  test("support routes return 200 status", async ({ page }) => {
    const routes = [
      "/en/privacy",
      "/en/terms",
      "/en/cookies-advertising",
      "/en/contact",
      "/en/status",
      "/en/roadmap",
      "/en/blog",
      "/es/privacy",
      "/id/privacy",
    ];
    for (const route of routes) {
      const response = await page.goto(route);
      expect(response?.status(), `expected 200 for ${route}`).toBe(200);
    }
  });
});
