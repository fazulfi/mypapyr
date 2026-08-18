import { NextResponse, type NextRequest } from "next/server";

import { LOCALE_COOKIE, getLocaleRedirectPath, isLocale, resolveLocale } from "./lib/i18n";
import { getMessages } from "./lib/messages";
import {
  deferredToolId,
  isConservativePassThrough,
  localizedToolLabel,
  redirectTargetFor,
} from "./lib/seo-redirects";
import { resolveRouteAlias } from "./lib/route-aliases";

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|opengraph-image|twitter-image|.*\\..*).*)",
  ],
};

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
  const title = escapeHtml(copy.notFound.title);
  const html = [
    "<!doctype html>",
    `<html lang="${locale}">`,
    "<head>",
    '<meta charset="utf-8">',
    `<title>${title}</title>`,
    "</head>",
    "<body>",
    `<h1>${title}</h1>`,
    `<p>${escapeHtml(toolLabel)} ${escapeHtml(copy.notFound.description)}</p>`,
    `<a href="${home}">${escapeHtml(copy.nav.home)}</a>`,
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

  const activeTarget = redirectTargetFor(pathname);
  if (activeTarget !== null) {
    const url = request.nextUrl.clone();
    url.pathname = activeTarget;
    return NextResponse.redirect(url, 301);
  }

  const toolId = deferredToolId(pathname);
  if (toolId !== null) {
    return buildGoneResponse(request, toolId);
  }

  if (isConservativePassThrough(pathname)) {
    return NextResponse.next();
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

  const locale = resolveLocale(
    request.cookies.get(LOCALE_COOKIE)?.value,
    request.headers.get("accept-language"),
  );

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
