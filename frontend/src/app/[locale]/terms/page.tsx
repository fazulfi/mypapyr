import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { isLocale, type Locale } from "@/lib/i18n";
import { supportingPageMetadata } from "@/lib/seo/alternates";
import { resolveSupportingPageCopy, type SupportingPageProps } from "@/components/supporting-page";
import { LegalPageContent } from "@/components/legal-page-content";

export async function generateMetadata({ params }: SupportingPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = await resolveSupportingPageCopy(params, "terms");
  return supportingPageMetadata(locale, "terms", copy.title, copy.description);
}

export default async function TermsPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = await resolveSupportingPageCopy(params, "terms");
  return <LegalPageContent copy={copy} locale={locale as Locale} sectionsKey="terms" />;
}
