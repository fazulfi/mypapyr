import { describe, expect, it } from "vitest";
import { NextRequest } from "next/server";

import {
  ACTIVE_ALIAS_REDIRECTS,
  DEFERRED_GONE_PATHS,
  redirectTargetFor,
} from "../lib/seo-redirects";
import { LOCALE_COOKIE } from "../lib/i18n";
import { config, isSafeRedirectPath, proxy } from "../proxy";

function makeRequest(
  pathname: string,
  headers?: Record<string, string>,
  origin = "http://localhost",
): NextRequest {
  return new NextRequest(`${origin}${pathname}`, { headers });
}

function redirectTargetForForTest(alias: string): string {
  const target = redirectTargetFor(alias);
  if (target === null) throw new Error(`Missing target for ${alias}`);
  return target;
}

function headerValue(response: Response, name: string): string | null {
  return response.headers.get(name);
}

describe("canonical host proxy", () => {
  it("redirects the trusted legacy host to budgezen.com with path and query", () => {
    const response = proxy(
      makeRequest("/en/compress-pdf?utm_source=legacy", undefined, "https://mypapyr.com"),
    );
    expect(response.status).toBe(308);
    expect(headerValue(response, "location")).toBe(
      "https://budgezen.com/en/compress-pdf?utm_source=legacy",
    );
  });

  it.each(["mypapyr.com", "www.mypapyr.com"])(
    "redirects trusted legacy forwarded host %s even when NextRequest URL uses an internal host",
    (legacyHost) => {
      const response = proxy(
        makeRequest(
          "/en/compress-pdf?utm_source=legacy",
          { host: legacyHost },
          "https://internal.vercel.app",
        ),
      );
      expect(response.status).toBe(308);
      expect(headerValue(response, "location")).toBe(
        "https://budgezen.com/en/compress-pdf?utm_source=legacy",
      );
    },
  );

  it("uses the canonical Host header before the forwarded host", () => {
    const response = proxy(
      makeRequest(
        "/en",
        { host: "www.mypapyr.com", "x-forwarded-host": "attacker.example" },
        "https://internal.vercel.app",
      ),
    );
    expect(response.status).toBe(308);
    expect(headerValue(response, "location")).toBe("https://budgezen.com/en");
  });

  it.each([
    { host: "attacker.example", forwarded: "mypapyr.com.evil.example" },
    { host: "attacker.example", forwarded: "https://mypapyr.com" },
    { host: "attacker.example", forwarded: "mypapyr.com, attacker.example" },
  ])("does not trust malformed or ambiguous forwarded hosts", ({ host, forwarded }) => {
    const response = proxy(
      makeRequest("/en", { host, "x-forwarded-host": forwarded }, "https://internal.vercel.app"),
    );
    expect(response.status).not.toBe(308);
    expect(headerValue(response, "location")).toBeNull();
  });

  it("passes the canonical host through without a host redirect", () => {
    const response = proxy(makeRequest("/en", undefined, "https://budgezen.com"));
    expect(response.status).not.toBe(308);
    expect(headerValue(response, "location")).toBeNull();
  });

  it.each(["http://localhost", "https://preview.example.vercel.app", "https://attacker.example"])(
    "does not redirect untrusted host %s",
    (origin) => {
      const response = proxy(makeRequest("/en", undefined, origin));
      expect(response.status).not.toBe(308);
      expect(headerValue(response, "location")).toBeNull();
    },
  );

  it("does not loop when the legacy host is already the redirect target", () => {
    const response = proxy(makeRequest("/en", undefined, "https://budgezen.com"));
    expect(headerValue(response, "location")).toBeNull();
  });
});

describe("SH-01 locale proxy", () => {
  it("redirects the locale-less root with 307 to the default locale", () => {
    const response = proxy(makeRequest("/"));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe("http://localhost/en");
  });

  it("persists the resolved locale in a minimal cookie on the redirect", () => {
    const response = proxy(makeRequest("/"));
    expect(response.cookies.get(LOCALE_COOKIE)?.value).toBe("en");
  });

  it("marks the locale cookie Secure so it only travels over HTTPS", () => {
    const response = proxy(makeRequest("/"));
    expect(headerValue(response, "set-cookie")).toContain("Secure");
  });

  it("honors a persisted cookie preference over the accept-language header", () => {
    const response = proxy(
      makeRequest("/", {
        cookie: `${LOCALE_COOKIE}=id`,
        "accept-language": "es;q=0.9, en;q=0.5",
      }),
    );
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe("http://localhost/id");
  });

  it("uses accept-language q-values when no preference is persisted", () => {
    const response = proxy(makeRequest("/", { "accept-language": "en;q=0.4, es;q=0.9" }));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe("http://localhost/es");
  });

  it("falls back to the default locale for unsupported languages", () => {
    const response = proxy(makeRequest("/", { "accept-language": "fr;q=0.9" }));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe("http://localhost/en");
  });

  it("passes already-localized paths through without redirecting", () => {
    for (const path of ["/en", "/es/compress-pdf", "/id/kompres-pdf"]) {
      const response = proxy(makeRequest(path));
      expect(headerValue(response, "location")).toBeNull();
    }
  });

  it("strips unsupported two-letter locale-like prefixes to the resolved locale", () => {
    const bare = proxy(makeRequest("/fr"));
    expect(bare.status).toBe(307);
    expect(headerValue(bare, "location")).toBe("http://localhost/en");

    const nested = proxy(makeRequest("/fr/foo"));
    expect(nested.status).toBe(307);
    expect(headerValue(nested, "location")).toBe("http://localhost/en/foo");
  });

  it("strips locale-like prefixes after resolving the persisted preference", () => {
    const response = proxy(makeRequest("/fr/foo", { cookie: `${LOCALE_COOKIE}=id` }));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe("http://localhost/id/foo");
  });

  it("preserves query strings when stripping a locale-like prefix", () => {
    const response = proxy(makeRequest("/fr/foo?utm_source=test"));
    expect(headerValue(response, "location")).toBe("http://localhost/en/foo?utm_source=test");
  });

  it("prefixes locale-less application paths while keeping the slug", () => {
    const response = proxy(makeRequest("/compress-pdf"));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe("http://localhost/en/compress-pdf");
  });

  it("preserves query strings on the redirect", () => {
    const response = proxy(makeRequest("/?utm_source=test"));
    expect(headerValue(response, "location")).toBe("http://localhost/en?utm_source=test");
  });

  it.each(["/faq", "/privacy"])("redirects %s to the default locale", (path) => {
    const response = proxy(makeRequest(`${path}?utm_source=test`));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe(`http://localhost/en${path}?utm_source=test`);
  });

  it.each(["/faq", "/privacy"])("redirects %s using the locale cookie", (path) => {
    const response = proxy(makeRequest(path, { cookie: `${LOCALE_COOKIE}=es` }));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe(`http://localhost/es${path}`);
  });

  it.each(["/faq", "/privacy"])("redirects %s using Accept-Language", (path) => {
    const response = proxy(makeRequest(path, { "accept-language": "id" }));
    expect(response.status).toBe(307);
    expect(headerValue(response, "location")).toBe(`http://localhost/id${path}`);
  });

  it("passes a scheme-relative pathname through without shaping a redirect", () => {
    const response = proxy(makeRequest("//evil.com"));
    expect(headerValue(response, "location")).toBeNull();
  });

  it("never emits raw control characters in a redirect location", () => {
    const response = proxy(makeRequest("/%0d%0aSet-Cookie:evil=1"));
    const location = headerValue(response, "location");
    expect(location).not.toBeNull();
    expect(location).not.toMatch(/[\r\n]/);
  });
});

describe("SH-01 proxy redirect-path guard", () => {
  it("accepts strictly relative application paths", () => {
    for (const path of ["/", "/en", "/en/foo", "/compress-pdf", "/es/compress-pdf"]) {
      expect(isSafeRedirectPath(path)).toBe(true);
    }
  });

  it("rejects scheme-relative, backslash, scheme, and control-character paths", () => {
    for (const path of [
      "//evil.com",
      "\\evil.com",
      "/\\evil.com",
      "http://evil.com",
      "https://evil.com",
      "evil.com",
      "/en\r\nSet-Cookie:evil=1",
    ]) {
      expect(isSafeRedirectPath(path)).toBe(false);
    }
  });
});

describe("SH-01 proxy matcher", () => {
  const pattern = `^${config.matcher[0]}$`;
  const matches = (path: string) => new RegExp(pattern).test(path);

  it("is a static constant array", () => {
    expect(Array.isArray(config.matcher)).toBe(true);
    expect(typeof config.matcher[0]).toBe("string");
  });

  it("excludes api, next internals, favicon, sitemap, robots and public files", () => {
    for (const path of [
      "/api/v1/status",
      "/_next/static/chunks/main.js",
      "/_next/image?url=%2Flogo.png",
      "/favicon.ico",
      "/sitemap.xml",
      "/robots.txt",
      "/images/logo.svg",
      "/docs/file.pdf",
    ]) {
      expect(matches(path)).toBe(false);
    }
  });

  it("matches locale-less and localized application paths", () => {
    for (const path of ["/", "/en", "/es/compress-pdf", "/fr", "/compress-pdf"]) {
      expect(matches(path)).toBe(true);
    }
  });
});

describe("SEO-02 active tool alias 301s", () => {
  it.each(Object.entries(ACTIVE_ALIAS_REDIRECTS))(
    "redirects %s with a direct one-hop 301 to the resolved English target",
    (alias) => {
      const response = proxy(makeRequest(alias));
      expect(response.status).toBe(301);
      expect(headerValue(response, "location")).toBe(
        `https://budgezen.com${redirectTargetForForTest(alias)}`,
      );
    },
  );

  it.each([
    ["es", "es", "/es/comprimir-pdf"],
    ["id", "id", "/id/kompres-pdf"],
  ])("resolves %s aliases using the locale cookie", (locale, cookie, target) => {
    const response = proxy(makeRequest("/compress", { cookie: `${LOCALE_COOKIE}=${cookie}` }));
    expect(headerValue(response, "location")).toBe(`https://budgezen.com${target}`);
    expect(response.cookies.get(LOCALE_COOKIE)).toBeUndefined();
  });

  it("resolves an Indonesian alias from Accept-Language", () => {
    const response = proxy(makeRequest("/pdf-to-image", { "accept-language": "id" }));
    expect(headerValue(response, "location")).toBe("https://budgezen.com/id/pdf-ke-gambar");
  });

  it("uses a trusted canonical origin for alias redirects", () => {
    const response = proxy(makeRequest("/compress", undefined, "https://attacker.example"));
    expect(headerValue(response, "location")).toBe("https://budgezen.com/en/compress-pdf");
  });

  it("resolves the 301 target without any further legacy redirecting", () => {
    for (const target of Object.values(ACTIVE_ALIAS_REDIRECTS)) {
      const response = proxy(makeRequest(target));
      expect(headerValue(response, "location")).toBeNull();
      expect(response.status).not.toBe(301);
      expect(response.status).not.toBe(410);
    }
  });

  it("preserves query strings on the active alias 301", () => {
    const response = proxy(makeRequest("/compress?utm_source=seo&page=2"));
    expect(response.status).toBe(301);
    expect(headerValue(response, "location")).toBe(
      "https://budgezen.com/en/compress-pdf?utm_source=seo&page=2",
    );
  });
});

describe("SEO-02 deferred tool 410 handling", () => {
  it("returns an intentional localized 410 with no-store for every deferred path", () => {
    for (const path of DEFERRED_GONE_PATHS) {
      const response = proxy(makeRequest(path));
      expect(response.status).toBe(410);
      expect(headerValue(response, "cache-control")).toContain("no-store");
      expect(headerValue(response, "cache-control")).toContain("no-cache");
      expect(headerValue(response, "content-type")).toContain("text/html");
    }
  });

  it("renders the localized 410 body with an accessible document and a home link", async () => {
    const response = proxy(makeRequest("/rotate"));
    const body = await response.text();
    expect(body).toContain('lang="en"');
    expect(body).toContain('<main id="main-content"');
    expect(body).toContain("<h1");
    expect(body).toContain("Rotate PDF");
    expect(body).toContain("This tool is no longer available.");
    expect(body).not.toContain("The page you are looking for does not exist.");
    expect(body).toContain('name="robots" content="noindex, nofollow"');
    expect(body).toContain('href="/en"');
  });

  it("localizes the 410 body from a resolved locale preference", async () => {
    const response = proxy(
      makeRequest("/rotate", {
        cookie: `${LOCALE_COOKIE}=es`,
        "accept-language": "en;q=0.9",
      }),
    );
    expect(response.status).toBe(410);
    const body = await response.text();
    expect(body).toContain('lang="es"');
    expect(body).toContain("Esta herramienta ya no está disponible.");
    expect(body).toContain("Rotar PDF");
  });
});

describe("SEO-02 edge-case matrix", () => {
  it("redirects only to closed internal paths, never a user-controlled destination", () => {
    for (const path of ["//evil.com", "/\\evil.com", "/compress?next=https://evil.com"]) {
      const response = proxy(makeRequest(path));
      const location = headerValue(response, "location");
      if (location !== null) {
        const url = new URL(location);
        expect(url.origin).toBe("https://budgezen.com");
        expect(url.pathname).toMatch(/^\/(en|es|id)\//);
      }
    }
    expect(headerValue(proxy(makeRequest("//evil.com")), "location")).toBeNull();
    expect(headerValue(proxy(makeRequest("/\\evil.com")), "location")).toBeNull();
  });

  it("does not redirect active aliases that are already inside a locale segment", () => {
    for (const path of ["/en/compress", "/es/merge", "/id/split"]) {
      const response = proxy(makeRequest(path));
      expect(headerValue(response, "location")).toBeNull();
    }
  });

  it("serves a single-hop 410 without rewriting to an indexable route", () => {
    for (const path of DEFERRED_GONE_PATHS) {
      const response = proxy(makeRequest(path));
      expect(response.status).toBe(410);
      expect(headerValue(response, "location")).toBeNull();
    }
  });
});
