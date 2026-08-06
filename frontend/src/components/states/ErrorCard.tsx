"use client";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export interface ErrorCardProps {
  locale: Locale;
  messageKey: string | null;
  retryable: boolean;
  onReset: () => void;
}

function resolveMessage(copy: ReturnType<typeof getMessages>, messageKey: string | null): string {
  if (messageKey === null) {
    return copy.states.error;
  }
  let value: unknown = copy;
  for (const part of messageKey.split(".")) {
    if (value === null || typeof value !== "object") {
      return copy.states.error;
    }
    value = (value as Record<string, unknown>)[part];
  }
  return typeof value === "string" ? value : copy.states.error;
}

export function ErrorCard({
  locale,
  messageKey,
  retryable,
  onReset,
}: ErrorCardProps): React.ReactElement {
  const copy = getMessages(locale);
  const message = resolveMessage(copy, messageKey);
  return (
    <div
      role="alert"
      data-retryable={retryable}
      className="rounded-xl border border-red-200 bg-red-50 p-6"
    >
      <p className="mb-4 text-sm font-medium text-red-800">{message}</p>
      <button
        type="button"
        onClick={onReset}
        className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
      >
        {copy.reset.processAnother}
      </button>
    </div>
  );
}
