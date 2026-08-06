"use client";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export interface DoneCardProps {
  locale: Locale;
  onDownload: () => void;
  onReset: () => void;
}

export function DoneCard({ locale, onDownload, onReset }: DoneCardProps): React.ReactElement {
  const copy = getMessages(locale);
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6">
      <p className="mb-4 text-sm font-medium text-slate-700">{copy.states.done}</p>
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onDownload}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-accent/90"
        >
          {copy.states.download}
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
        >
          {copy.reset.processAnother}
        </button>
      </div>
    </div>
  );
}
