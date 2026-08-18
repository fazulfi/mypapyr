import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { isLocale } from "@/lib/i18n";
import { supportingPageMetadata } from "@/lib/seo/alternates";
import {
  resolveSupportingPageCopy,
  SupportingPageContent,
  type SupportingPageProps,
} from "@/components/supporting-page";

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
  const copy = await resolveSupportingPageCopy(params, "terms");
  return <SupportingPageContent copy={copy} pageSlug="terms" adLabel={copy.adLabel} />;
}
