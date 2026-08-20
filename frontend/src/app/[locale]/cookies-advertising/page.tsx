import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { isLocale } from "@/lib/i18n";
import { supportingPageMetadata } from "@/lib/seo/alternates";
import { resolveSupportingPageCopy, type SupportingPageProps } from "@/components/supporting-page";
import { LegalPageContent } from "@/components/legal-page-content";

export async function generateMetadata({ params }: SupportingPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = await resolveSupportingPageCopy(params, "cookiesAdvertising");
  return supportingPageMetadata(locale, "cookies-advertising", copy.title, copy.description);
}

export default async function CookiesAdvertisingPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = await resolveSupportingPageCopy(params, "cookiesAdvertising");
  return <LegalPageContent copy={copy} locale={locale} sectionsKey="cookiesAdvertising" />;
}
