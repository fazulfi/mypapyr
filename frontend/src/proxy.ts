import { NextResponse, type NextRequest } from "next/server";

import { LOCALE_COOKIE, getLocaleRedirectPath, isLocale, resolveLocale } from "./lib/i18n";
import { SEO_BASE_URL } from "./lib/seo/alternates";
import { getMessages } from "./lib/messages";
import { deferredToolId, localizedToolLabel, redirectTargetFor } from "./lib/seo-redirects";
import { resolveRouteAlias } from "./lib/route-aliases";

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|opengraph-image|twitter-image|.*\\..*).*)",
  ],
};

export const CANONICAL_ORIGIN = "https://budgezen.com";
export const TRUSTED_LEGACY_HOSTS = new Set(["mypapyr.com", "www.mypapyr.com"]);

function requestHost(request: NextRequest): string {
  const forwardedHost = request.headers.get("x-forwarded-host");
  if (forwardedHost !== null) {
    return forwardedHost.trim().toLowerCase();
  }
  return request.nextUrl.hostname.toLowerCase();
}

export function isSafeRedirectPath(path: string): boolean {
  return (
    path.startsWith("/") && !path.startsWith("//") && !path.includes("\\") && !/[\r\n]/.test(path)
  );
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function buildGoneResponse(request: NextRequest, toolId: string): NextResponse {
  const locale = resolveLocale(
    request.cookies.get(LOCALE_COOKIE)?.value,
    request.headers.get("accept-language"),
  );
  const copy = getMessages(locale);
  const toolLabel = localizedToolLabel(locale, toolId);
  const home = `/${locale}`;
  const title = escapeHtml(copy.gone.title);
  const html = [
    "<!doctype html>",
    `<html lang="${locale}">`,
    "<head>",
    '<meta charset="utf-8">',
    `<title>${title}</title>`,
    '<meta name="robots" content="noindex, nofollow">',
    "</head>",
    "<body>",
    '<main id="main-content" tabindex="-1">',
    `<h1>${title}</h1>`,
    `<p>${escapeHtml(toolLabel)} ${escapeHtml(copy.gone.description)}</p>`,
    `<a href="${home}">${escapeHtml(copy.nav.home)}</a>`,
    "</main>",
    "</body>",
    "</html>",
  ].join("");
  return new NextResponse(html, {
    status: 410,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export function proxy(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;
  const host = requestHost(request);
  if (TRUSTED_LEGACY_HOSTS.has(host)) {
    const canonicalUrl = new URL(CANONICAL_ORIGIN);
    canonicalUrl.pathname = pathname;
    canonicalUrl.search = request.nextUrl.search;
    return NextResponse.redirect(canonicalUrl, 308);
  }

  const locale = resolveLocale(
    request.cookies.get(LOCALE_COOKIE)?.value,
    request.headers.get("accept-language"),
  );

  const activeTarget = redirectTargetFor(pathname, locale);
  if (activeTarget !== null) {
    const url = new URL(activeTarget, SEO_BASE_URL);
    url.search = request.nextUrl.search;
    return NextResponse.redirect(url, 301);
  }

  const toolId = deferredToolId(pathname);
  if (toolId !== null) {
    return buildGoneResponse(request, toolId);
  }

  // The redirect Location is shaped from the raw pathname; refuse pathnames
  // that could turn it into a scheme-relative or header-injectable URL.
  if (!isSafeRedirectPath(pathname)) {
    return NextResponse.next();
  }

  const firstSegment = pathname.split("/")[1];
  if (firstSegment !== undefined && isLocale(firstSegment)) {
    // Canonical localized URL stays in the browser; rewrite translated slugs
    // (ES/ID) internally to the EN-slug route directory that renders them.
    const aliased = resolveRouteAlias(pathname);
    if (aliased !== null && aliased !== pathname) {
      const rewritten = request.nextUrl.clone();
      rewritten.pathname = aliased;
      return NextResponse.rewrite(rewritten);
    }
    return NextResponse.next();
  }

  const targetPath = getLocaleRedirectPath(pathname, locale);
  if (targetPath === null) {
    return NextResponse.next();
  }

  const url = request.nextUrl.clone();
  url.pathname = targetPath;

  const response = NextResponse.redirect(url, 307);
  response.cookies.set(LOCALE_COOKIE, locale, {
    path: "/",
    sameSite: "lax",
    secure: true,
    maxAge: 60 * 60 * 24 * 365,
  });
  return response;
}

export default proxy;
