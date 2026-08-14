"use client";

import type { ReactNode } from "react";

import type { Locale } from "@/lib/i18n";
import type { Messages } from "@/lib/messages";
import { getMessages } from "@/lib/messages";
import type { ToolId } from "@/lib/tool-ids";

/**
 * ToolPageHeader — shared tool page chrome (ported from the REFERENCE tool
 * pages, e.g. papyr-reference/frontend/src/app/compress/page.tsx): icon chip
 * + h1 + description + a row of three feature badge pills. All copy is
 * localized via messages.ts; the tool icon is the catalog icon at 19px
 * strokeWidth 1.8 inside the accent chip.
 */

// Maps tool-page ids to their `tools.*` message key (catalog id vs copy key).
const TOOLS_KEY: Record<ToolId, keyof Messages["tools"]> = {
  "compress-pdf": "compress",
  "merge-pdf": "merge",
  "split-pdf": "split",
  "jpg-to-pdf": "jpgToPdf",
  "pdf-to-jpg": "pdfToJpg",
};

const TOOL_ICONS: Record<ToolId, ReactNode> = {
  "compress-pdf": (
    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="2" y="3" width="20" height="5" rx="1" />
      <path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
      <path d="M10 12h4" />
    </svg>
  ),
  "merge-pdf": (
    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
      <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
    </svg>
  ),
  "split-pdf": (
    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="6" cy="6" r="3" />
      <path d="M8.12 8.12 12 12" />
      <path d="M20 4 8.12 15.88" />
      <circle cx="6" cy="18" r="3" />
      <path d="M14.8 14.8 20 20" />
    </svg>
  ),
  "jpg-to-pdf": (
    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
      <path d="M14 2v4a2 2 0 0 0 2 2h4" />
      <circle cx="10" cy="12" r="2" />
      <path d="m20 17-1.296-1.296a2.41 2.41 0 0 0-3.408 0L9 22" />
    </svg>
  ),
  "pdf-to-jpg": (
    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
      <circle cx="9" cy="9" r="2" />
      <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
    </svg>
  ),
};

function CheckIcon() {
  return (
    <svg
      width={14}
      height={14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg
      width={14}
      height={14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg
      width={14}
      height={14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

const FEATURE_ICONS: readonly ReactNode[] = [
  <CheckIcon key="check" />,
  <ClockIcon key="clock" />,
  <ShieldIcon key="shield" />,
];

export function ToolPageHeader({ locale, toolId }: { locale: Locale; toolId: ToolId }) {
  const copy = getMessages(locale);
  const tool = copy.tools[TOOLS_KEY[toolId]];
  const features = copy.toolPages[toolId].features;

  return (
    <div className="mb-8 flex flex-col items-center text-center">
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10 text-accent">
        {TOOL_ICONS[toolId]}
      </div>
      <h1 className="mb-2 text-3xl font-bold text-navy">{tool.title}</h1>
      <p className="text-base text-slate-500">{tool.description}</p>
      <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
        {features.map((feature, index) => (
          <span
            key={feature}
            className="inline-flex items-center gap-1.5 rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent"
          >
            {FEATURE_ICONS[index]}
            {feature}
          </span>
        ))}
      </div>
    </div>
  );
}
