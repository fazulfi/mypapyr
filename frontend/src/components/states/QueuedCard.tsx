"use client";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export interface QueuedCardProps {
  locale: Locale;
}

export function QueuedCard({ locale }: QueuedCardProps): React.ReactElement {
  const copy = getMessages(locale);
  return (
    <div role="status" className="rounded-xl border border-slate-200 bg-white p-6">
      <div data-testid="skeleton" className="mb-3 h-3 w-24 animate-pulse rounded bg-slate-200" />
      <p className="text-sm font-medium text-slate-700">{copy.states.queued}</p>
    </div>
  );
}
