/**
 * PT-03 Result-problem report.
 *
 * A compact inline trigger shown near result/download states. Opens the
 * categorized contact form in a collapsed view, prefilled with sanitized
 * page/locale context. Reuses the `ContactSubmission` model + validation
 * from `@/lib/support`, and keeps errors redaction-safe (submitted content
 * is never echoed back after a failed submit).
 */

"use client";

import { useState } from "react";

import { getMessages } from "@/lib/messages";
import { sanitizeContext } from "@/lib/support";

import { ContactForm } from "./ContactForm";

export interface ResultProblemReportProps {
  locale: string;
  /** Page context (e.g. current tool path); sanitized before use. */
  page?: string | null;
  /** Locale context override; sanitized before use. */
  localeContext?: string | null;
}

export function ResultProblemReport({
  locale,
  page = null,
  localeContext = null,
}: ResultProblemReportProps): React.ReactElement {
  const [open, setOpen] = useState(false);

  const copy = getMessages(locale as "en" | "es" | "id");
  const context = sanitizeContext(page, localeContext ?? locale);

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 underline-offset-2 transition-colors hover:text-slate-700 hover:underline"
        aria-expanded={false}
        aria-controls="result-problem-report"
      >
        <svg
          width={13}
          height={13}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M12 9v4" />
          <path d="M12 17h.01" />
          <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
        </svg>
        {copy.contact.reportProblem}
      </button>
    );
  }

  return (
    <div
      id="result-problem-report"
      className="mt-3 rounded-xl border border-slate-100 bg-slate-50/60 px-4 py-3"
    >
      <p className="mb-2 text-xs font-medium text-slate-500">{copy.contact.reportIntro}</p>
      <ContactForm
        locale={locale}
        collapsed
        context={{ page: context.page, locale: context.locale }}
        copy={copy.contact}
      />
      <button
        type="button"
        onClick={() => setOpen(false)}
        className="mt-3 text-xs font-medium text-slate-400 underline-offset-2 hover:text-slate-600 hover:underline"
      >
        {copy.contact.closeReport}
      </button>
    </div>
  );
}

export default ResultProblemReport;