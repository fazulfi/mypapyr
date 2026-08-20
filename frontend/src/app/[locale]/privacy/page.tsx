import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { supportingPageMetadata } from "@/lib/seo/alternates";
import { LegalPageContent } from "@/components/legal-page-content";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = getMessages(locale as Locale);
  return supportingPageMetadata(
    locale as Locale,
    "privacy",
    copy.pages.privacy.title,
    copy.pages.privacy.description,
  );
}

export default async function PrivacyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<React.ReactElement> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }

  const copy = getMessages(locale as Locale);

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-12 sm:py-16">
      <LegalPageContent
        copy={{
          title: copy.pages.privacy.title,
          description: copy.pages.privacy.description,
          adLabel: copy.ads.label,
        }}
        locale={locale as Locale}
        sectionsKey="privacy"
      />
    </div>
  );
}
