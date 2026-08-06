"use client";

import { use, useState } from "react";
import { useTranslations } from "next-intl";
import Dropzone from "@/components/uploader/Dropzone";
import { QueuedCard, PreparingCard, ProcessingCard, DoneCard, ErrorCard } from "@/components/states";
import { useTaskPolling } from "@/hooks/useTaskPolling";
import { isLocale, Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export default function MergePdfPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = use(params);
  const [files, setFiles] = useState<File[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const isLocaleValid = isLocale(locale);
  const messages = isLocaleValid ? getMessages(locale as Locale) : getMessages("en");
  
  const { status, refresh, stop } = useTaskPolling({
    toolId: "merge-pdf",
    taskId: taskId ?? undefined,
    enabled: !!taskId,
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

    if (files.length > 20) {
      setError(messages.tools.merge.errors.tooManyFiles);
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

      const data = await response.json();
      setTaskId(data.taskId);
    } catch (err) {
      setError(messages.tools.merge.errors.uploadFailed);
      setTaskId(null);
    }
  };

  const handleDownload = async () => {
    if (!status || !status.outputCount || status.outputCount === 0) return;

    try {
      const response = await fetch(
        `/api/v1/tools/merge-pdf/tasks/${taskId}/download/0`
      );
      if (!response.ok) throw new Error("Download grant failed");

      const grant = await response.json();
      window.location.href = grant.url;
    } catch (err) {
      setError(messages.tools.merge.errors.downloadFailed);
    }
  };

  const handleReset = () => {
    stop();
    setFiles([]);
    setTaskId(null);
    setError(null);
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        {messages.tools.merge.title}
      </h1>
      <p className="text-gray-600 mb-8">
        {messages.tools.merge.description}
      </p>

      {!taskId ? (
        <>
          <Dropzone
            files={files}
            onChange={handleFileChange}
            accept={"application/pdf"}
            multiple
            maxFiles={20}
            locale={locale as Locale}
          />

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <button
            onClick={handleMergeClick}
            disabled={files.length < 2}
            className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg disabled:opacity-50 hover:bg-blue-700"
          >
            {messages.tools.merge.actions.merge}
          </button>
        </>
      ) : (
        <div className="max-w-md mx-auto">
          {status?.state === "queued" && <QueuedCard locale={locale as Locale} />}
          {status?.state === "processing" && <ProcessingCard locale={locale as Locale} />}
          {status?.state === "done" && (
            <DoneCard
              locale={locale as Locale}
              onDownload={handleDownload}
              onReset={handleReset}
            />
          )}
          {status?.state === "failed" && (
            <ErrorCard
              locale={locale as Locale}
              messageKey={status.errorCategory}
              retryable={false}
              onReset={handleReset}
            />
          )}
        </div>
      )}
    </main>
  );
}
