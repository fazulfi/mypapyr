import { test, expect } from "@playwright/test";

test.describe("Locale Routing", () => {
  test("GET / returns single-hop 307 redirect to resolved locale", async ({ request }) => {
    const response = await request.get("/", { maxRedirects: 0 });
    expect(response.status()).toBe(307);
    const location = response.headers()["location"];
    expect(location).toMatch(/^\/en$/);
    expect(response.headers()["set-cookie"]).toBeDefined();
  });

  test("GET /en returns 200 with html lang=en", async ({ page }) => {
    const response = await page.goto("/en");
    expect(response?.status()).toBe(200);
    await expect(page.locator("html")).toHaveAttribute("lang", "en");
  });

  test("GET /es returns 200 with html lang=es", async ({ page }) => {
    const response = await page.goto("/es");
    expect(response?.status()).toBe(200);
    await expect(page.locator("html")).toHaveAttribute("lang", "es");
  });

  test("GET /id returns 200 with html lang=id", async ({ page }) => {
    const response = await page.goto("/id");
    expect(response?.status()).toBe(200);
    await expect(page.locator("html")).toHaveAttribute("lang", "id");
  });

  test("locale home page renders localized SH-07 hero copy", async ({ page }) => {
    await page.goto("/en");
    await expect(page.locator("h1")).toContainText("PDF tools thatjust work.");

    await page.goto("/es");
    await expect(page.locator("h1")).toContainText("Herramientas PDF quesimplemente funcionan.");

    await page.goto("/id");
    await expect(page.locator("h1")).toContainText("Alat PDF yanglangsung bekerja.");
  });

  test("papyr_locale cookie preference redirects / to preferred locale", async ({ browser }) => {
    const context = await browser.newContext();
    await context.addCookies([
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
    const page = await context.newPage();
    const response = await page.goto("/");
    expect(response?.status()).toBe(200);
    expect(new URL(page.url()).pathname).toBe("/es");
    await context.close();
  });

  test("Accept-Language header resolves locale (es)", async ({ request }) => {
    const response = await request.get("/", {
      maxRedirects: 0,
      headers: { "Accept-Language": "es,en;q=0.9" },
    });
    expect(response.status()).toBe(307);
    expect(response.headers()["location"]).toBe("/es");
  });

  test("Accept-Language header resolves locale (id)", async ({ request }) => {
    const response = await request.get("/", {
      maxRedirects: 0,
      headers: { "Accept-Language": "id,en;q=0.9" },
    });
    expect(response.status()).toBe(307);
    expect(response.headers()["location"]).toBe("/id");
  });

  test("cookie preference overrides Accept-Language", async ({ request }) => {
    // First get the cookie from a redirect that prefers "id"
    const cookieResponse = await request.get("/", {
      maxRedirects: 0,
      headers: { "Accept-Language": "id,en;q=0.9" },
    });
    expect(cookieResponse.status()).toBe(307);
    expect(cookieResponse.headers()["location"]).toBe("/id");

    // Now send the cookie + an Accept-Language that prefers "es":
    // cookie "id" must win over Accept-Language "es"
    const setCookie = cookieResponse.headers()["set-cookie"];
    expect(setCookie).toBeDefined();
    const cookieResponse2 = await request.get("/", {
      maxRedirects: 0,
      headers: {
        Cookie: setCookie,
        "Accept-Language": "es,en;q=0.9",
      },
    });
    expect(cookieResponse2.status()).toBe(307);
    expect(cookieResponse2.headers()["location"]).toBe("/id");
  });

  test("unsupported locale-like prefix /fr strips to default locale /en (307)", async ({
    request,
  }) => {
    const response = await request.get("/fr", { maxRedirects: 0 });
    expect(response.status()).toBe(307);
    expect(response.headers()["location"]).toBe("/en");
  });

  test("unsupported locale-like prefix /fr/some-page strips to /en/some-page (307)", async ({
    request,
  }) => {
    const response = await request.get("/fr/some-page", { maxRedirects: 0 });
    expect(response.status()).toBe(307);
    expect(response.headers()["location"]).toBe("/en/some-page");
  });

  test("unsupported locale resists infinite redirect loops", async ({ browser }) => {
    const context = await browser.newContext({
      extraHTTPHeaders: { "Accept-Language": "fr,en;q=0.9" },
    });
    const page = await context.newPage();
    await page.goto("/");
    // "fr" is not a supported locale; should fall back to en, not loop
    expect(new URL(page.url()).pathname).toBe("/en");
    await context.close();
  });

  test("locale redirect sets secure cookie on first visit", async ({ page }) => {
    const response = await page.goto("/");
    expect(response?.status()).toBe(200);
    const cookies = await page.context().cookies();
    const localeCookie = cookies.find((c) => c.name === "papyr_locale");
    expect(localeCookie).toBeDefined();
    expect(localeCookie!.path).toBe("/");
    expect(localeCookie!.sameSite).toBe("Lax");
    expect(localeCookie!.httpOnly).toBe(false);
  });
});
