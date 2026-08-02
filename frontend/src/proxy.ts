import { NextResponse, type NextRequest } from "next/server";

import {
  LEGACY_ROUTING_PATHS,
  LOCALE_COOKIE,
  getLocaleRedirectPath,
  isLocale,
  resolveLocale,
} from "./lib/i18n";

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\..*).*)"],
};

export function isSafeRedirectPath(path: string): boolean {
  return (
    path.startsWith("/") && !path.startsWith("//") && !path.includes("\\") && !/[\r\n]/.test(path)
  );
}

export function proxy(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;

  if (LEGACY_ROUTING_PATHS.has(pathname)) {
    return NextResponse.next();
  }

  // The redirect Location is shaped from the raw pathname; refuse pathnames
  // that could turn it into a scheme-relative or header-injectable URL.
  if (!isSafeRedirectPath(pathname)) {
    return NextResponse.next();
  }

  const firstSegment = pathname.split("/")[1];
  if (firstSegment !== undefined && isLocale(firstSegment)) {
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
