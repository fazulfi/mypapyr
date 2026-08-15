"use client";

import type { Locale } from "@/lib/i18n";
import { getMessages, type Messages } from "@/lib/messages";

export interface ErrorCardProps {
  locale: Locale;
  messageKey: string | null;
  retryable: boolean;
  onReset: () => void;
}

function resolveMessage(copy: Messages, messageKey: string | null): string {
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

function AlertIcon(): React.ReactElement {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

export function ErrorCard({
  locale,
  messageKey,
  retryable,
  onReset,
}: ErrorCardProps): React.ReactElement {
  const copy = getMessages(locale);
  const message = messageKey === null ? null : resolveMessage(copy, messageKey);
  const showMessage = message !== null && message !== copy.states.errorTitle;
  return (
    <div
      role="alert"
      data-retryable={retryable}
      className="rounded-2xl border border-rose-200 bg-rose-50/50 p-6"
    >
      <div className="mb-4 flex items-center gap-3 text-rose-500">
        <AlertIcon />
        <p className="text-sm font-semibold">{copy.states.errorTitle}</p>
      </div>
      {showMessage && <p className="mb-5 text-sm text-slate-600">{message}</p>}
      <button
        type="button"
        onClick={onReset}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-accent px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-accent/90"
      >
        {copy.states.retry}
      </button>
    </div>
  );
}
