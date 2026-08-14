import Link from "next/link";

import type { Locale } from "../lib/i18n";
import { getMessages } from "../lib/messages";
import { getAllTools, getLegacyTools } from "../lib/catalog";

/* ── Inline SVG Icon ── */

function ArrowRightIcon() {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

/* ── Component ── */

interface OtherToolsProps {
  currentTool: string;
  /** Optional for parity with the reference signature; defaults to English. */
  locale?: Locale;
}

export default function OtherTools({ currentTool, locale = "en" }: OtherToolsProps) {
  const copy = getMessages(locale);
  const allTools = [...getAllTools(), ...getLegacyTools()];
  const siblingTools = allTools.filter((t) => t.id !== currentTool);

  return (
    <div className="mt-16 w-full border-t border-slate-200 pb-8 pt-8">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-widest text-accent">
        {copy.otherTools.title}
      </h2>
      <div className="grid grid-cols-2 gap-3">
        {siblingTools.map((tool) => (
          <Link
            key={tool.id}
            href={tool.hrefs[locale]}
            className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-navy transition-colors hover:border-accent/50 hover:text-accent"
          >
            {tool.fullLabel[locale]}
            <ArrowRightIcon />
          </Link>
        ))}
      </div>
    </div>
  );
}