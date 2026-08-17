"use client";

import { useEffect, useState } from "react";
import { use } from "react";

import type { Locale } from "@/lib/i18n";
import { defaultLocale, isLocale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { ToolPageHeader } from "@/components/ToolPageHeader";
import { PrivacyNotice } from "@/components/PrivacyNotice";
import { AdSlot } from "@/components/ads/AdSlot";
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
import PasswordInput, {
  type LockedFileInfo,
  type PasswordErrorKind,
} from "@/components/PasswordInput";
import { isEncryptedPdf } from "@/lib/pdf-encryption";
import { buildPasswordFields, fileId, reconcilePasswordValues } from "@/lib/mergePasswordFields";

const MAX_FILES = 20;
const MIN_FILES = 2;
const MAX_SIZE_BYTES = 104857600; // 100 MiB per file

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

export function MergePdfTool({ locale }: { locale: Locale }) {
  const copy = getMessages(locale);
  const [files, setFiles] = useState<File[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [uploadPhase, setUploadPhase] = useState<"idle" | "uploading" | "error">("idle");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  // Memory-only encrypted-PDF detection and passwords (PT-04): the ids are
  // derived from file metadata, and the values live only in React state —
  // never localStorage/sessionStorage/URL/analytics. Removed files drop out
  // via reconcilePasswordValues; reset clears both maps.
  const [encryptedIds, setEncryptedIds] = useState<Set<string>>(new Set());
  const [passwordValues, setPasswordValues] = useState<Map<string, string>>(new Map());
  const [passwordError, setPasswordError] = useState<PasswordErrorKind | null>(null);

  const { status } = useTaskPolling({
    toolId: "merge-pdf",
    taskId: taskId ?? "",
    enabled: taskId !== null,
  });

  // Fetch download grant when task completes successfully (only once)
  useEffect(() => {
    if (taskId === null || status === null || status.state !== "done") return;
    if (downloadUrl !== null) return;
    let cancelled = false;
    void fetch("/api/v1/tools/merge-pdf/tasks/" + taskId + "/download/0")
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

  async function handleFilesChange(next: File[]): Promise<void> {
    setFiles(next);
    setPasswordError(null);
    const nextIds = new Set<string>(encryptedIds);
    const pending: Promise<void>[] = [];
    for (const file of next) {
      const id = fileId(file);
      if (nextIds.has(id)) continue;
      pending.push(
        isEncryptedPdf(file).then((encrypted) => {
          if (encrypted) nextIds.add(id);
        }),
      );
    }
    await Promise.all(pending);
    setEncryptedIds(nextIds);
    setPasswordValues(reconcilePasswordValues(next, nextIds, passwordValues));
  }

  async function handleSubmit(selected: File[]): Promise<void> {
    if (selected.length < MIN_FILES) return;
    setPasswordError(null);
    const built = buildPasswordFields(selected, encryptedIds, passwordValues);
    if (!built.ok) {
      setPasswordError("unsupported");
      return;
    }
    setUploadPhase("uploading");
    try {
      const form = new FormData();
      for (const file of selected) form.append("files", file);
      for (const [field, value] of Object.entries(built.fields)) form.append(field, value);
      const response = await fetch("/api/v1/tools/merge-pdf/tasks", {
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
    setEncryptedIds(new Set());
    setPasswordValues(new Map());
    setPasswordError(null);
  }

  function handleDownload(): void {
    if (downloadUrl !== null) window.location.href = downloadUrl;
  }

  const canSubmit = files.length >= MIN_FILES;

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
          <ToolPageHeader locale={locale} toolId="merge-pdf" />
          <PrivacyNotice locale={locale} model="client" />
          <Dropzone
            files={files}
            onChange={(next) => void handleFilesChange(next)}
            accept={["application/pdf"]}
            maxFiles={MAX_FILES}
            maxSizeBytes={MAX_SIZE_BYTES}
            disabled={phase === "uploading"}
            locale={locale}
          />

          <ul className="mt-4 space-y-1">
            {files
              .filter((file) => encryptedIds.has(fileId(file)))
              .map((file) => {
                const info: LockedFileInfo = {
                  id: fileId(file),
                  name: file.name,
                  type: file.type,
                  size: file.size,
                  isEncrypted: true,
                };
                const id = fileId(file);
                return (
                  <li key={id}>
                    <PasswordInput
                      file={info}
                      locale={locale}
                      errorType={passwordError ?? undefined}
                      memoryUsage={{
                        value: passwordValues.get(id) ?? "",
                        onChange: (pw) => {
                          setPasswordError(null);
                          setPasswordValues((prev) => {
                            const nextMap = new Map(prev);
                            nextMap.set(id, pw);
                            return nextMap;
                          });
                        },
                      }}
                    />
                  </li>
                );
              })}
          </ul>

          <button
            type="button"
            onClick={() => void handleSubmit(files)}
            disabled={!canSubmit || phase === "uploading"}
            className="mt-4 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {phase === "uploading"
              ? copy.tools.merge.actions.uploading
              : copy.tools.merge.actions.merge}
          </button>
          <OtherTools currentTool="merge-pdf" locale={locale} />
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
        <ToolPageHeader locale={locale} toolId="merge-pdf" />
        <PrivacyNotice locale={locale} model="client" />
        {card}
        <AdSlot pageSlug="merge-pdf" phase={phase} label={copy.ads.label} />
        <OtherTools currentTool="merge-pdf" locale={locale} />
        <ResultProblemReport locale={locale} page="/merge-pdf" localeContext={locale} />
      </div>
    </main>
  );
}

export default function MergePdfPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale: rawLocale } = use(params);
  const locale: Locale = isLocale(rawLocale) ? rawLocale : defaultLocale;
  return <MergePdfTool locale={locale} />;
}
