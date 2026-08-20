import type { Metadata } from "next";
import type { ReactNode } from "react";
import { notFound } from "next/navigation";

import { isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { supportingAlternates } from "@/lib/seo/alternates";

interface FaqLayoutProps {
  children?: ReactNode;
  params: Promise<{ locale: string }>;
}

export async function generateMetadata({ params }: FaqLayoutProps): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = getMessages(locale as Locale);
  return {
    title: copy.faqPage.title,
    description: copy.faqPage.subtitle,
    alternates: supportingAlternates(locale as Locale, "faq"),
  };
}

export default function FaqLayout({ children }: FaqLayoutProps): ReactNode {
  return children;
}
