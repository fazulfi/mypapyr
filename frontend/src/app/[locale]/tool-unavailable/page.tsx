import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { getLegacyTools } from "@/lib/catalog";
import { isLocale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

interface ToolUnavailablePageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ tool?: string | string[] }>;
}

export async function generateMetadata({
  params,
}: ToolUnavailablePageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    return {};
  }
  const copy = getMessages(locale);
  return { title: copy.notFound.title, description: copy.notFound.description };
}

export default async function ToolUnavailablePage({
  params,
  searchParams,
}: ToolUnavailablePageProps): Promise<React.ReactElement> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const { tool } = await searchParams;
  const raw = Array.isArray(tool) ? tool[0] : tool;
  if (raw === undefined || !getLegacyTools().some((entry) => entry.id === raw)) {
    notFound();
  }

  const copy = getMessages(locale);
  const toolCopy = getLegacyTools().find((entry) => entry.id === raw);
  const toolName = toolCopy?.localizedLabels[locale] ?? raw;
  const backHref = `/${locale}`;

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-[600px] flex-col items-center justify-center px-6 py-24 text-center">
      <h1 className="mb-3 text-4xl font-bold tracking-tight text-navy">{copy.notFound.title}</h1>
      <p className="mb-8 text-lg leading-relaxed text-slate-500">
        {toolName} {copy.notFound.description}
      </p>
      <a
        href={backHref}
        className="inline-flex items-center gap-2 rounded-[10px] bg-navy px-8 py-3.5 text-base font-semibold tracking-tight text-white shadow-md transition-all hover:-translate-y-0.5 hover:shadow-lg"
      >
        {copy.nav.home}
      </a>
    </div>
  );
}
