import type { Metadata } from "next";
import type { ReactNode } from "react";
import { notFound } from "next/navigation";

import { getToolById } from "@/lib/catalog";
import { isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { alternateLinks } from "@/lib/seo/alternates";

interface ToolLayoutProps {
  children?: ReactNode;
  params: Promise<{ locale: string }>;
}

export async function generateMetadata({ params }: ToolLayoutProps): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const tool = getToolById("jpg-to-pdf");
  if (tool === undefined) {
    return {};
  }
  const copy = getMessages(locale as Locale);
  return {
    title: copy.tools.jpgToPdf.title,
    description: copy.tools.jpgToPdf.description,
    alternates: alternateLinks(locale as Locale, tool.hrefs),
  };
}

export default function JpgToPdfLayout({ children }: ToolLayoutProps): ReactNode {
  return children;
}
