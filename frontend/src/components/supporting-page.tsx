import { notFound } from "next/navigation";

import { isLocale } from "@/lib/i18n";
import { getMessages, type Messages } from "@/lib/messages";

import { AdSlot } from "@/components/ads/AdSlot";

// SH-08 shared supporting-page contract: the seven supporting routes keep their
// own page modules so canonical URLs and per-page ownership stay explicit; this
// module owns the locale validation and heading/scope-statement render they share.

export interface SupportingPageProps {
  params: Promise<{ locale: string }>;
}

export type SupportingPageKey = keyof Messages["pages"];

export interface SupportingPageCopy {
  title: string;
  description: string;
  /** Localized ad-slot label (messages.ads.label), resolved server-side. */
  adLabel: string;
}

// Resolves typed copy for a supporting route key; unsupported locales reject
// via next/navigation notFound(), matching the per-route page behavior.
export async function resolveSupportingPageCopy(
  params: SupportingPageProps["params"],
  key: SupportingPageKey,
): Promise<SupportingPageCopy> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const messages = getMessages(locale);
  return { ...messages.pages[key], adLabel: messages.ads.label };
}

export function SupportingPageContent({
  copy,
  pageSlug,
  adLabel,
}: {
  copy: SupportingPageCopy;
  pageSlug?: string;
  adLabel?: string;
}): React.ReactElement {
  return (
    <>
      <h1>{copy.title}</h1>
      <p>{copy.description}</p>
      {pageSlug !== undefined ? (
        <div className="mt-8 max-w-full overflow-hidden" aria-label={adLabel ?? "Advertisement"}>
          <AdSlot pageSlug={pageSlug} immediate unit="banner-468x60" label={adLabel} />
        </div>
      ) : null}
    </>
  );
}
