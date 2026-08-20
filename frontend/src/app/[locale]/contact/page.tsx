import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { isLocale } from "@/lib/i18n";
import { supportingPageMetadata } from "@/lib/seo/alternates";
import { resolveSupportingPageCopy, type SupportingPageProps } from "@/components/supporting-page";
import { ContactForm } from "@/components/support/ContactForm";
import { AdSlot } from "@/components/ads/AdSlot";

export async function generateMetadata({ params }: SupportingPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = await resolveSupportingPageCopy(params, "contact");
  return supportingPageMetadata(locale, "contact", copy.title, copy.description);
}

/**
 * PT-03 Contact page.
 *
 * Server component wrapper: resolves the localized title/description through
 * the shared `resolveSupportingPageCopy` contract (unsupported locales reject
 * via `notFound`), then renders the client-side categorized `ContactForm`.
 */
export default async function ContactPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const { locale } = await params;
  const copy = await resolveSupportingPageCopy(params, "contact");

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-12 sm:py-16">
      <h1 className="text-2xl font-bold text-navy sm:text-3xl">{copy.title}</h1>
      <p className="mt-3 text-[15px] text-slate-500">{copy.description}</p>
      <div className="mt-8">
        <ContactForm locale={locale} context={{ page: "/contact", locale }} />
      </div>
      <div
        className="mt-10 flex max-w-full flex-col items-center gap-6 overflow-hidden"
        aria-label={copy.adLabel}
      >
        <AdSlot pageSlug="contact" immediate unit="banner-468x60" label={copy.adLabel} />
      </div>
    </div>
  );
}
