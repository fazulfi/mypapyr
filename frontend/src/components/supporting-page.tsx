import { notFound } from "next/navigation";

import { isLocale } from "@/lib/i18n";
import { getMessages, type Messages } from "@/lib/messages";

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
  return getMessages(locale).pages[key];
}

export function SupportingPageContent({ copy }: { copy: SupportingPageCopy }): React.ReactElement {
  return (
    <>
      <h1>{copy.title}</h1>
      <p>{copy.description}</p>
    </>
  );
}
