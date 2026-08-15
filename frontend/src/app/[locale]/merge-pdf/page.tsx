"use client";

import { use, useState } from "react";

import type { Locale } from "@/lib/i18n";
import { isLocale, defaultLocale } from "@/lib/i18n";
import { AdSlot } from "@/components/ads/AdSlot";
import { ToolPageHeader } from "@/components/ToolPageHeader";
import { PrivacyNotice } from "@/components/PrivacyNotice";
import OtherTools from "@/components/OtherTools";
import { getMessages } from "@/lib/messages";
import { Dropzone } from "@/components/uploader/Dropzone";
import { QueuedCard } from "@/components/states/QueuedCard";
import { PreparingCard as _PreparingCard } from "@/components/states/PreparingCard";
import { ProcessingCard } from "@/components/states/ProcessingCard";
import { DoneCard } from "@/components/states/DoneCard";
import { ErrorCard } from "@/components/states/ErrorCard";
import { useTaskPolling } from "@/hooks/useTaskPolling";

export function MergePdfTool({ locale }: { locale: Locale }) {
  const messages = getMessages(locale);
  const [files, setFiles] = useState<File[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    status,
    refresh: _refresh,
    stop,
  } = useTaskPolling({
    toolId: "merge-pdf",
    taskId: taskId ?? "",
    enabled: taskId !== null,
  });

  const handleFileChange = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setError(null);
    setTaskId(null);
  };

  const handleMergeClick = async () => {
    if (files.length < 2) {
      setError(messages.tools.merge.errors.needAtLeastTwo);
      return;
    }

    setError(null);
    setTaskId(null);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("/api/v1/tools/merge-pdf/tasks", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = (await response.json()) as { task_id: string };
      setTaskId(data.task_id);
    } catch {
      setError(messages.tools.merge.errors.uploadFailed);
    }
  };

  const handleDownload = async () => {
    if (!status || !status.outputCount || status.outputCount === 0) return;

    try {
      const response = await fetch(`/api/v1/tools/merge-pdf/tasks/${taskId}/download/0`);
      if (!response.ok) throw new Error("Download grant failed");

      const grant = (await response.json()) as { url: string };
      window.location.href = grant.url;
    } catch {
      setError(messages.tools.merge.errors.downloadFailed);
    }
  };

  const handleReset = () => {
    stop();
    setFiles([]);
    setTaskId(null);
    setError(null);
  };

  const mergePhase =
    taskId === null
      ? "idle"
      : status?.state === "failed"
        ? "error"
        : status?.state === "done"
          ? "done"
          : "processing";

  return (
    <main className="container mx-auto px-4 py-8">
      <ToolPageHeader locale={locale} toolId="merge-pdf" />
      <PrivacyNotice locale={locale} model="client" />

      {!taskId ? (
        <>
          <Dropzone
            files={files}
            onChange={handleFileChange}
            accept={["application/pdf"]}
            maxFiles={20}
            locale={locale}
          />

          {error && (
            <div className="mt-4 rounded border border-red-200 bg-red-50 p-4">
              <p className="text-red-800" role="alert">
                {error}
              </p>
            </div>
          )}

          <button
            onClick={() => void handleMergeClick()}
            disabled={files.length < 2}
            className="mt-6 rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {messages.tools.merge.actions.merge}
          </button>
        </>
      ) : (
        <div className="mx-auto max-w-md">
          {status?.state === "queued" && <QueuedCard locale={locale} />}
          {status?.state === "processing" && <ProcessingCard locale={locale} />}
          {status?.state === "done" && (
            <DoneCard locale={locale} onDownload={handleDownload} onReset={handleReset} />
          )}
          {status?.state === "failed" && (
            <ErrorCard
              locale={locale}
              messageKey={status.errorCategory}
              retryable={false}
              onReset={handleReset}
            />
          )}
        </div>
      )}
      <AdSlot pageSlug="merge-pdf" phase={mergePhase} />
      <OtherTools currentTool="merge-pdf" locale={locale} />
    </main>
  );
}

export default function MergePdfPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = use(params);
  const validLocale: Locale = isLocale(locale) ? locale : defaultLocale;
  return <MergePdfTool locale={validLocale} />;
}
