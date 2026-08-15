"use client";

import { useEffect, useState } from "react";
import { use } from "react";

import { ToolPageHeader } from "@/components/ToolPageHeader";
import { PrivacyNotice } from "@/components/PrivacyNotice";
import { AdSlot } from "@/components/ads/AdSlot";
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
import { downloadTaskResult } from "@/lib/taskDownloads";

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

export function PdfToJpgTool({ locale }: { locale: Locale }) {
  const copy = getMessages(locale);
  const [files, setFiles] = useState<File[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [uploadPhase, setUploadPhase] = useState<"idle" | "uploading" | "error">("idle");

  const { status } = useTaskPolling({
    toolId: "pdf-to-jpg",
    taskId: taskId ?? "",
    enabled: taskId !== null,
  });

  async function handleSubmit(selected: File[]): Promise<void> {
    if (selected.length === 0) return;
    setUploadPhase("uploading");
    try {
      const form = new FormData();
      for (const file of selected) form.append("file", file);
      const response = await fetch("/api/v1/tools/pdf-to-jpg/tasks", {
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
    setUploadPhase("idle");
  }

  async function handleDownload(): Promise<void> {
    if (taskId === null || status === null) return;
    await downloadTaskResult({
      toolId: "pdf-to-jpg",
      taskId,
      outputCount: status.outputCount ?? 0,
      entryName: (index) => "page-" + (index + 1) + ".jpg",
      zipFilename: "pdf-to-jpg.zip",
    });
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
          <ToolPageHeader locale={locale} toolId="pdf-to-jpg" />
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
              ? copy.tools.pdfToJpg.actions.uploading
              : copy.tools.pdfToJpg.actions.convert}
          </button>

          <div className="mt-6 space-y-1">
            <p className="text-xs text-slate-600">{copy.tools.pdfToJpg.qualityNote}</p>
            <p className="text-xs text-slate-500">{copy.tools.pdfToJpg.resolutionNote}</p>
          </div>
          <OtherTools currentTool="pdf-to-jpg" locale={locale} />
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
      card = (
        <DoneCard locale={locale} onDownload={() => void handleDownload()} onReset={handleReset} />
      );
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
        <ToolPageHeader locale={locale} toolId="pdf-to-jpg" />
        <PrivacyNotice locale={locale} model="server" />
        <AdSlot pageSlug="pdf-to-jpg" phase={phase} />
        {card}
        <OtherTools currentTool="pdf-to-jpg" locale={locale} />
      </div>
    </main>
  );
}

export default function PdfToJpgPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale: rawLocale } = use(params);
  const locale: Locale = isLocale(rawLocale) ? rawLocale : defaultLocale;
  return <PdfToJpgTool locale={locale} />;
}