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
  const copy = await resolveSupportingPageCopy(params, "status");
  return supportingPageMetadata(locale, "status", copy.title, copy.description);
}

export default async function StatusPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const copy = await resolveSupportingPageCopy(params, "status");
  return <SupportingPageContent copy={copy} pageSlug="status" adLabel={copy.adLabel} />;
}
