"use client";

import { useEffect, useState } from "react";
import { use } from "react";

import { ToolPageHeader } from "@/components/ToolPageHeader";
import { AdSlot } from "@/components/ads/AdSlot";
import { PrivacyNotice } from "@/components/PrivacyNotice";
import OtherTools from "@/components/OtherTools";
import type { Locale } from "@/lib/i18n";
import { defaultLocale, isLocale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { Dropzone } from "@/components/uploader/Dropzone";
import { PreparingCard } from "@/components/states/PreparingCard";
import { QueuedCard } from "@/components/states/QueuedCard";
import { ProcessingCard } from "@/components/states/ProcessingCard";
import { DoneCard } from "@/components/states/DoneCard";
import { ErrorCard } from "@/components/states/ErrorCard";
import type { ToolState } from "@/lib/toolState";
import { useTaskPolling } from "@/hooks/useTaskPolling";

const MAX_SIZE_BYTES = 104857600; // 100 MiB

function derivePhase(
  status: ReturnType<typeof useTaskPolling>["status"],
  hasTaskId: boolean,
): ToolState {
  if (!hasTaskId || status === null) return "queued";
  if (status.state === "queued") return "queued";
  if (status.state === "processing") return "processing";
  if (status.state === "done") return "done";
  return "error";
}

export function CompressPdfTool({ locale }: { locale: Locale }) {
  const copy = getMessages(locale);
  const [files, setFiles] = useState<File[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [uploadPhase, setUploadPhase] = useState<"idle" | "uploading" | "error">("idle");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const { status } = useTaskPolling({
    toolId: "compress-pdf",
    taskId: taskId ?? "",
    enabled: taskId !== null,
  });

  // Fetch download grant when task completes successfully (only once)
  useEffect(() => {
    if (taskId === null || status === null || status.state !== "done") return;
    if (downloadUrl !== null) return;
    let cancelled = false;
    void fetch("/api/v1/tools/compress-pdf/tasks/" + taskId + "/download/0")
      .then(async (response) => {
        if (!response.ok) return;
        const grant = (await response.json()) as { url: string };
        if (!cancelled) setDownloadUrl(grant.url);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [taskId, status, downloadUrl]);

  async function handleSubmit(selected: File[]): Promise<void> {
    if (selected.length === 0) return;
    setUploadPhase("uploading");
    try {
      const form = new FormData();
      for (const file of selected) form.append("file", file);
      const response = await fetch("/api/v1/tools/compress-pdf/tasks", {
        method: "POST",
        body: form,
      });
      if (!response.ok) throw new Error("Upload failed: " + response.status);
      const body = (await response.json()) as { task_id: string };
      setTaskId(body.task_id);
      setUploadPhase("idle");
    } catch {
      setUploadPhase("error");
    }
  }

  function handleReset(): void {
    setFiles([]);
    setTaskId(null);
    setDownloadUrl(null);
    setUploadPhase("idle");
  }

  function handleDownload(): void {
    if (downloadUrl !== null) window.location.href = downloadUrl;
  }

  const phase: ToolState =
    taskId === null
      ? uploadPhase === "uploading"
        ? "uploading"
        : uploadPhase === "error"
          ? "error"
          : "idle"
      : derivePhase(status, true);

  // Idle / ready / uploading phase: show dropzone + submit button
  if (phase === "idle" || phase === "ready" || phase === "uploading") {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-3xl">
          <ToolPageHeader locale={locale} toolId="compress-pdf" />
          <PrivacyNotice locale={locale} model="server" />
          <Dropzone
            files={files}
            onChange={setFiles}
            accept={["application/pdf"]}
            maxFiles={1}
            maxSizeBytes={MAX_SIZE_BYTES}
            disabled={phase === "uploading"}
            locale={locale}
          />
          <button
            type="button"
            onClick={() => void handleSubmit(files)}
            disabled={files.length === 0 || phase === "uploading"}
            className="mt-4 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {phase === "uploading"
              ? copy.tools.compress.actions.uploading
              : copy.tools.compress.actions.compress}
          </button>
          <OtherTools currentTool="compress-pdf" locale={locale} />
        </div>
      </main>
    );
  }

  // Card for queued/processing/done/error phases
  let card: React.ReactNode;
  switch (phase) {
    case "preparing":
      card = <PreparingCard locale={locale} />;
      break;
    case "queued":
      card = <QueuedCard locale={locale} />;
      break;
    case "processing":
    case "finalizing":
      card = <ProcessingCard locale={locale} />;
      break;
    case "done":
      card = <DoneCard locale={locale} onDownload={handleDownload} onReset={handleReset} />;
      break;
    case "error":
      card = (
        <ErrorCard
          locale={locale}
          messageKey={status?.messageKey ?? null}
          retryable={status?.retryable ?? false}
          onReset={handleReset}
        />
      );
      break;
    default:
      card = null;
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-3xl">
        <ToolPageHeader locale={locale} toolId="compress-pdf" />
        <PrivacyNotice locale={locale} model="server" />
        <OtherTools currentTool="compress-pdf" locale={locale} />
        <AdSlot pageSlug="compress-pdf" phase={phase} />
        {card}
      </div>
    </main>
  );
}

export default function CompressPdfPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale: rawLocale } = use(params);
  const locale: Locale = isLocale(rawLocale) ? rawLocale : defaultLocale;
  return <CompressPdfTool locale={locale} />;
}
