"use client";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export interface ProcessingCardProps {
  locale: Locale;
  fileName?: string;
  fileSizeBytes?: number;
  progressPercent?: number;
}

function FileIcon(): React.ReactElement {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14.5 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 KB";
  const mb = bytes / (1024 * 1024);
  if (mb >= 1) return `${mb.toFixed(1)} MB`;
  return `${Math.round(bytes / 1024)} KB`;
}

export function ProcessingCard({
  locale,
  fileName,
  fileSizeBytes,
  progressPercent,
}: ProcessingCardProps): React.ReactElement {
  const copy = getMessages(locale);
  return (
    <div role="status" className="rounded-2xl border border-slate-200 bg-white p-6">
      {(fileName !== undefined || fileSizeBytes !== undefined) && (
        <div className="mb-7 flex items-center gap-3.5">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-slate-500">
            <FileIcon />
          </div>
          <div>
            {fileName !== undefined && (
              <p className="text-sm font-semibold text-navy">{fileName}</p>
            )}
            {fileSizeBytes !== undefined && (
              <p className="text-xs text-slate-400">{formatFileSize(fileSizeBytes)}</p>
            )}
          </div>
        </div>
      )}
      <p className="mb-2.5 text-sm font-medium text-slate-500">
        {copy.states.processing}
        {progressPercent !== undefined ? ` ${progressPercent}%` : ""}
      </p>
      <div className="relative h-1.5 overflow-hidden rounded-full bg-slate-100">
        <div className="absolute inset-0 animate-shimmer rounded-full bg-gradient-to-r from-transparent via-accent to-transparent bg-[length:200%_100%]" />
      </div>
      <p className="mt-2.5 text-center text-xs text-slate-400">{copy.states.processingHint}</p>
    </div>
  );
}
