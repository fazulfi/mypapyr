"use client";

import { useMemo, useState } from "react";
import { use } from "react";

import type { Locale } from "@/lib/i18n";
import { defaultLocale, isLocale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { ToolPageHeader } from "@/components/ToolPageHeader";
import { PrivacyNotice } from "@/components/PrivacyNotice";
import { AdSlot } from "@/components/ads/AdSlot";
import { LeaderboardAdSlot } from "@/components/ads/LeaderboardAdSlot";
import OtherTools from "@/components/OtherTools";
import { ResultProblemReport } from "@/components/support/ResultProblemReport";
import { Dropzone } from "@/components/uploader/Dropzone";
import { PreparingCard } from "@/components/states/PreparingCard";
import { QueuedCard } from "@/components/states/QueuedCard";
import { ProcessingCard } from "@/components/states/ProcessingCard";
import { DoneCard } from "@/components/states/DoneCard";
import { ErrorCard } from "@/components/states/ErrorCard";
import type { ToolState } from "@/lib/toolState";
import { useTaskPolling } from "@/hooks/useTaskPolling";
import { downloadTaskResult } from "@/lib/taskDownloads";
import { parseRangeSpec } from "@/lib/splitRanges";

const MAX_SIZE_BYTES = 104857600; // 100 MiB

function formatTemplate(template: string, params: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) =>
    key in params ? String(params[key]) : match,
  );
}

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

export function SplitPdfTool({ locale }: { locale: Locale }) {
  const copy = getMessages(locale);
  const [files, setFiles] = useState<File[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [uploadPhase, setUploadPhase] = useState<"idle" | "uploading" | "error">("idle");
  const [rangeText, setRangeText] = useState("");
  const [serverRejected, setServerRejected] = useState(false);

  const { status } = useTaskPolling({
    toolId: "split-pdf",
    taskId: taskId ?? "",
    enabled: taskId !== null,
  });

  const rangeSpec = useMemo(() => parseRangeSpec(rangeText), [rangeText]);
  const rangeError = rangeSpec.ok ? null : rangeSpec.error;
  const previewRanges = rangeSpec.ok ? rangeSpec.ranges : [];
  const rangeErrorMessage = rangeError === null ? null : copy.tools.split.ranges.errors[rangeError];

  async function handleSubmit(selected: File[]): Promise<void> {
    if (selected.length === 0 || !rangeSpec.ok) return;
    setUploadPhase("uploading");
    setServerRejected(false);
    try {
      const form = new FormData();
      for (const file of selected) form.append("file", file);
      if (rangeSpec.canonical !== "") form.append("ranges", rangeSpec.canonical);
      const response = await fetch("/api/v1/tools/split-pdf/tasks", {
        method: "POST",
        body: form,
      });
      if (response.status === 400) {
        let messageKey = "";
        try {
          const body = (await response.json()) as { detail?: { messageKey?: string } };
          messageKey = body?.detail?.messageKey ?? "";
        } catch {
          messageKey = "";
        }
        if (messageKey === "error.badRequest") {
          setServerRejected(true);
          setUploadPhase("idle");
          return;
        }
        throw new Error("Upload failed: " + response.status);
      }
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
    setRangeText("");
    setServerRejected(false);
  }

  async function handleDownload(): Promise<void> {
    if (taskId === null || status === null) return;
    await downloadTaskResult({
      toolId: "split-pdf",
      taskId,
      outputCount: status.outputCount ?? 0,
      entryName: (index) => "split-" + (index + 1) + ".pdf",
      zipFilename: "split-pdf.zip",
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
          <ToolPageHeader locale={locale} toolId="split-pdf" />
          <PrivacyNotice locale={locale} model="client" />
          <LeaderboardAdSlot pageSlug="split-pdf" />
          <Dropzone
            files={files}
            onChange={setFiles}
            accept={["application/pdf"]}
            maxFiles={1}
            maxSizeBytes={MAX_SIZE_BYTES}
            disabled={phase === "uploading"}
            locale={locale}
          />
          <div className="mt-6">
            <label htmlFor="split-ranges" className="block text-sm font-semibold text-slate-700">
              {copy.tools.split.ranges.label}
            </label>
            <p id="split-ranges-help" className="mt-1 text-sm text-slate-600">
              {copy.tools.split.ranges.help}
            </p>
            <input
              id="split-ranges"
              name="ranges"
              type="text"
              autoComplete="off"
              spellCheck={false}
              value={rangeText}
              onChange={(event) => {
                setRangeText(event.target.value);
                setServerRejected(false);
              }}
              disabled={phase === "uploading"}
              aria-invalid={rangeError !== null || undefined}
              aria-describedby={
                rangeError === null ? "split-ranges-help" : "split-ranges-help split-ranges-error"
              }
              className="mt-2 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 disabled:cursor-not-allowed disabled:opacity-50"
            />
            {rangeErrorMessage !== null && (
              <p
                id="split-ranges-error"
                role="alert"
                className="mt-2 text-sm font-medium text-red-700"
              >
                {rangeErrorMessage}
              </p>
            )}
          </div>
          {serverRejected && (
            <div role="alert" className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4">
              <p className="text-sm font-medium text-red-800">
                {copy.tools.split.ranges.errors.serverRejected}
              </p>
            </div>
          )}
          {rangeError === null && (
            <section
              aria-live="polite"
              className="mt-4 rounded-lg border border-slate-200 bg-white p-4"
            >
              <h2 className="text-sm font-semibold text-slate-700">
                {copy.tools.split.ranges.previewHeading}
              </h2>
              {previewRanges.length > 0 ? (
                <ol className="mt-2 space-y-1">
                  {previewRanges.map((range, index) => (
                    <li key={`output-${index}`} className="text-sm text-slate-600">
                      {formatTemplate(
                        range.start === range.end
                          ? copy.tools.split.ranges.previewItemSingle
                          : copy.tools.split.ranges.previewItemRange,
                        {
                          index: index + 1,
                          pages:
                            range.start === range.end
                              ? String(range.start)
                              : `${range.start}-${range.end}`,
                        },
                      )}
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="mt-2 text-sm text-slate-600">{copy.tools.split.ranges.defaultNote}</p>
              )}
            </section>
          )}
          <button
            type="button"
            onClick={() => void handleSubmit(files)}
            disabled={files.length === 0 || phase === "uploading" || rangeError !== null}
            className="mt-4 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {phase === "uploading"
              ? copy.tools.split.actions.uploading
              : copy.tools.split.actions.split}
          </button>
          <OtherTools currentTool="split-pdf" locale={locale} />
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
        <ToolPageHeader locale={locale} toolId="split-pdf" />
        <PrivacyNotice locale={locale} model="client" />
        {card}
        <AdSlot pageSlug="split-pdf" phase={phase} />
        <OtherTools currentTool="split-pdf" locale={locale} />
        <ResultProblemReport locale={locale} page="/split-pdf" localeContext={locale} />
        <AdSlot pageSlug="split-pdf" immediate unit="skyscraper-160x600" />
      </div>
    </main>
  );
}

export default function SplitPdfPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale: rawLocale } = use(params);
  const locale: Locale = isLocale(rawLocale) ? rawLocale : defaultLocale;
  return <SplitPdfTool locale={locale} />;
}
