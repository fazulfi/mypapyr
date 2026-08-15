"use client";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

/**
 * PrivacyNotice — reusable privacy notice for tool pages (ported from
 * papyr-reference/frontend/src/components/PrivacyNotice.tsx). Shows a shield
 * icon plus localized copy contextual to the tool's processing model.
 * Always visible regardless of tool state.
 */

function ShieldIcon() {
  return (
    <svg
      width={14}
      height={14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

export type ProcessingModel = "server" | "client" | "hybrid";

export function PrivacyNotice({ locale, model }: { locale: Locale; model: ProcessingModel }) {
  const copy = getMessages(locale);
  return (
    <div className="mt-6 flex items-start rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-xs text-slate-500">
      <span className="mt-0.5 mr-2 shrink-0 text-slate-400">
        <ShieldIcon />
      </span>
      <p>{copy.privacyNotice.model[model]}</p>
    </div>
  );
}
