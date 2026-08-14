"use client";

import { use } from "react";

import type { Locale } from "@/lib/i18n";
import { isLocale, defaultLocale } from "@/lib/i18n";
import { ToolPageHeader } from "@/components/ToolPageHeader";
import { PrivacyNotice } from "@/components/PrivacyNotice";
import OtherTools from "@/components/OtherTools";
import { Dropzone } from "@/components/uploader/Dropzone";
import { useState } from "react";

export function SplitPdfTool({ locale }: { locale: Locale }) {
  const [files, setFiles] = useState<File[]>([]);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-3xl">
        <ToolPageHeader locale={locale} toolId="split-pdf" />
        <PrivacyNotice locale={locale} model="client" />
        <Dropzone
          files={files}
          onChange={setFiles}
          accept={["application/pdf"]}
          maxFiles={1}
          locale={locale}
        />
        <OtherTools currentTool="split-pdf" locale={locale} />
      </div>
    </main>
  );
}

export default function SplitPdfPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = use(params);
  const validLocale: Locale = isLocale(locale) ? locale : defaultLocale;
  return <SplitPdfTool locale={validLocale} />;
}
