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
  const copy = await resolveSupportingPageCopy(params, "blog");
  return supportingPageMetadata(locale, "blog", copy.title, copy.description);
}

export default async function BlogPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const copy = await resolveSupportingPageCopy(params, "blog");
  return <SupportingPageContent copy={copy} pageSlug="blog" adLabel={copy.adLabel} />;
}
