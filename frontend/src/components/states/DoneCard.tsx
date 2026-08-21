"use client";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export interface DoneCardProps {
  locale: Locale;
  onDownload: () => void;
  onReset: () => void;
  originalBytes?: number;
  compressedBytes?: number;
  fileName?: string;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 KB";
  const mb = bytes / (1024 * 1024);
  if (mb >= 1) return `${mb.toFixed(1)} MB`;
  return `${Math.round(bytes / 1024)} KB`;
}

function formatPercent(original: number, compressed: number): number {
  if (original === 0) return 0;
  if (compressed >= original) return 0;
  const saved = original - compressed;
  return Math.round((saved / original) * 100);
}

function CheckIcon(): React.ReactElement {
  return (
    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="white"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function DownloadIcon(): React.ReactElement {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

function RefreshIcon(): React.ReactElement {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="23 4 23 10 17 10" />
      <polyline points="1 20 1 14 7 14" />
      <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
    </svg>
  );
}

function ArrowRightIcon(): React.ReactElement {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#CBD5E1"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

export function DoneCard({
  locale,
  onDownload,
  onReset,
  originalBytes,
  compressedBytes,
  fileName,
}: DoneCardProps): React.ReactElement {
  const copy = getMessages(locale);
  const hasResult = originalBytes !== undefined && compressedBytes !== undefined;
  const saved = hasResult ? formatPercent(originalBytes, compressedBytes) : 0;

  return (
    <div className="rounded-2xl border border-accent/20 bg-white p-6 shadow-[0_4px_20px_rgba(37,99,235,0.06)]">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-500">
          <CheckIcon />
        </div>
        <div>
          <p className="text-base font-semibold text-navy">
            {hasResult ? copy.states.complete : copy.states.done}
          </p>
          {fileName !== undefined && <p className="text-xs text-slate-500">{fileName}</p>}
        </div>
      </div>

      {hasResult && (
        <div className="mb-5 rounded-xl bg-slate-50 px-4 py-5">
          <div className="flex items-center justify-between">
            <div className="text-center">
              <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-700">
                {copy.states.before}
              </p>
              <p className="text-2xl font-semibold tracking-tight text-slate-500">
                {formatFileSize(originalBytes)}
              </p>
            </div>
            <div className="flex flex-col items-center gap-1">
              <span className="rounded-full bg-accent/10 px-3 py-1 text-sm font-bold text-blue-800">
                &minus;{saved}%
              </span>
              <ArrowRightIcon />
            </div>
            <div className="text-center">
              <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-blue-800">
                {copy.states.after}
              </p>
              <p className="text-2xl font-semibold tracking-tight text-navy">
                {formatFileSize(compressedBytes)}
              </p>
            </div>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={onDownload}
        className="mb-2.5 flex w-full items-center justify-center gap-2 rounded-xl bg-accent px-5 py-4 text-base font-semibold text-white shadow-[0_2px_12px_rgba(37,99,235,0.25)] transition-colors hover:bg-accent/90"
      >
        <DownloadIcon />
        {hasResult ? copy.states.downloadCta : copy.states.download}
      </button>
      <button
        type="button"
        onClick={onReset}
        className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-transparent px-5 py-3 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-50"
      >
        <RefreshIcon />
        {copy.reset.processAnother}
      </button>
    </div>
  );
}
