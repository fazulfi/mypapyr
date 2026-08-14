"use client";

import { use } from "react";

import { isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export default function SplitPdfPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = use(params);
  const validLocale = isLocale(locale) ? (locale as Locale) : "en";
  const messages = getMessages(validLocale);

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <main className="container mx-auto p-4">
        <h1>{messages.tools.split.title}</h1>
        <p>{messages.tools.split.description}</p>
      </main>
    </div>
  );
}
