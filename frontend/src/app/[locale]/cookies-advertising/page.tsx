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
  const copy = await resolveSupportingPageCopy(params, "cookiesAdvertising");
  return supportingPageMetadata(locale, "cookies-advertising", copy.title, copy.description);
}

export default async function CookiesAdvertisingPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const copy = await resolveSupportingPageCopy(params, "cookiesAdvertising");
  return (
    <SupportingPageContent copy={copy} pageSlug="cookies-advertising" adLabel={copy.adLabel} />
  );
}
