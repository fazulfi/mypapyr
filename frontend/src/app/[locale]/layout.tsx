import type { Metadata } from "next";
import type { ReactNode } from "react";
import { notFound } from "next/navigation";

import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { PrivacyAnalytics } from "@/components/PrivacyAnalytics";
import { SkipLink } from "@/components/SkipLink";
import { fontVariables } from "@/lib/fonts";
import { isLocale, locales, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

import "../globals.css";

const METADATA_BASE_URL = "https://budgezen.com";

// PT01-G8 / WS-5 (SEO-03): absolute per-locale canonical/hreflang roots. Next
// resolves `alternates` against metadataBase, so these are fully qualified
// budgezen.com URLs; pages may narrow the root per-path via metadata merge (DEC-023).
const LOCALE_ROOTS = {
  en: `${METADATA_BASE_URL}/en`,
  es: `${METADATA_BASE_URL}/es`,
  id: `${METADATA_BASE_URL}/id`,
} as const satisfies Record<Locale, string>;

// Mirrored from canonical docs/assets/papyr-hero-light.svg (1200x400, 1.91:1).
const SOCIAL_IMAGE_URL = "/papyr-hero-light.svg";
const SOCIAL_IMAGE_WIDTH = 1200;
const SOCIAL_IMAGE_HEIGHT = 400;

const OG_LOCALES: Record<Locale, string> = {
  en: "en_US",
  es: "es_ES",
  id: "id_ID",
};

export function generateStaticParams(): { locale: string }[] {
  return locales.map((locale) => ({ locale }));
}

interface LocaleLayoutProps {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = getMessages(locale);
  return {
    metadataBase: new URL(METADATA_BASE_URL),
    title: copy.metadata.title,
    description: copy.metadata.description,
    icons: "/favicon.ico",
    alternates: {
      canonical: LOCALE_ROOTS[locale],
      languages: {
        ...LOCALE_ROOTS,
        "x-default": LOCALE_ROOTS.en,
      },
    },
    openGraph: {
      type: "website",
      locale: OG_LOCALES[locale],
      siteName: copy.siteName,
      title: copy.metadata.title,
      description: copy.metadata.description,
      images: [
        {
          url: SOCIAL_IMAGE_URL,
          width: SOCIAL_IMAGE_WIDTH,
          height: SOCIAL_IMAGE_HEIGHT,
          alt: copy.metadata.title,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: copy.metadata.title,
      description: copy.metadata.description,
      images: [
        {
          url: SOCIAL_IMAGE_URL,
          width: SOCIAL_IMAGE_WIDTH,
          height: SOCIAL_IMAGE_HEIGHT,
          alt: copy.metadata.title,
        },
      ],
    },
  };
}

export default async function LocaleLayout({
  children,
  params,
}: LocaleLayoutProps): Promise<ReactNode> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = getMessages(locale);
  return (
    <html lang={locale} className={fontVariables}>
      <body className="flex min-h-dvh flex-col">
        <SkipLink label={copy.a11y.skipToContent} />
        <Navbar locale={locale} />
        <main id="main-content" tabIndex={-1} className="flex-1">
          {children}
        </main>
        <Footer locale={locale} />
        <PrivacyAnalytics />
      </body>
    </html>
  );
}
