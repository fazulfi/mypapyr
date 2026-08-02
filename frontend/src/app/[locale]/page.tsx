import { notFound } from "next/navigation";

import { getAllTools, getToolById, type ToolIconName } from "@/lib/catalog";
import { isLocale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

interface LocaleHomePageProps {
  params: Promise<{ locale: string }>;
}

const TOOL_ICONS: Record<ToolIconName, React.ReactElement> = {
  archive: (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="2" y="3" width="20" height="5" rx="1" />
      <path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
      <path d="M10 12h4" />
    </svg>
  ),
  files: (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
      <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
    </svg>
  ),
  scissors: (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
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
  "file-image": (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
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
  image: (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
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

function ToolIcon({ name }: { name: ToolIconName }): React.ReactElement {
  return TOOL_ICONS[name];
}

function ArrowRightIcon(): React.ReactElement {
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
      aria-hidden="true"
    >
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

function ChevronIcon({ className }: { className?: string }): React.ReactElement {
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
      aria-hidden="true"
      className={className}
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

// DEC-148: every launch tool card shares one identical class list so no tool
// receives a featured treatment. Matches the legacy card baseline
// (papyr-reference/frontend/src/app/page.tsx:550) with the canonical navy/blue
// tokens from frontend/src/lib/design-tokens.ts.
const TOOL_CARD_CLASS =
  "group flex flex-col gap-3 rounded-[10px] border border-slate-200 bg-white p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04)] transition-all hover:-translate-y-0.5 hover:border-accent/60 hover:shadow-[0_4px_20px_rgba(37,99,235,0.1)]";

export default async function LocaleHomePage({
  params,
}: LocaleHomePageProps): Promise<React.ReactElement> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = getMessages(locale);
  const compressHref = getToolById("compress-pdf")?.hrefs[locale] ?? `/${locale}`;

  return (
    <>
      <section className="mx-auto max-w-[1200px] px-6 pb-20 pt-24 text-center">
        <h1 className="mx-auto mb-5 max-w-[18ch] text-balance text-[clamp(40px,6vw,72px)] font-semibold leading-[1.08] tracking-[-2px] text-navy">
          {copy.home.hero}
        </h1>
        <p className="mx-auto mb-10 max-w-[520px] text-lg leading-relaxed text-slate-500">
          {copy.home.heroSub}
        </p>
        <a
          href={compressHref}
          className="inline-flex items-center gap-2 rounded-[10px] bg-navy px-8 py-3.5 text-base font-semibold tracking-tight text-white shadow-md transition-all hover:-translate-y-0.5 hover:shadow-lg"
        >
          {copy.nav.cta}
          <ArrowRightIcon />
        </a>
      </section>

      <div className="mx-auto max-w-[1200px] border-t border-slate-200" />

      <section className="mx-auto max-w-[1200px] px-6 py-20">
        <h2 className="mb-12 text-[32px] font-semibold tracking-tight text-navy">
          {copy.home.toolsHeading}
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {getAllTools().map((tool) => (
            <a
              key={tool.id}
              href={tool.hrefs[locale]}
              data-tool-id={tool.id}
              className={TOOL_CARD_CLASS}
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-[10px] bg-slate-100 text-slate-500 transition-colors group-hover:bg-accent/15 group-hover:text-accent">
                <ToolIcon name={tool.icon} />
              </span>
              <span className="text-[15px] font-semibold text-navy">
                {tool.localizedLabels[locale]}
              </span>
              <span className="text-[13.5px] leading-snug text-slate-500">{tool.description}</span>
            </a>
          ))}
        </div>
      </section>

      <section className="border-y border-slate-200 bg-slate-100">
        <div className="mx-auto max-w-[1200px] px-6 py-[72px]">
          <h2 className="mb-4 text-center text-[28px] font-semibold tracking-tight text-navy">
            {copy.home.privacy}
          </h2>
          <p className="mx-auto max-w-[720px] text-center text-base leading-relaxed text-slate-500">
            {copy.home.privacyDesc}
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-[1200px] px-6 py-20">
        <h2 className="mb-12 text-center text-[28px] font-semibold tracking-tight text-navy">
          {copy.home.howItWorks}
        </h2>
        <ol className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {copy.home.howItWorksSteps.map((step, index) => (
            <li
              key={step}
              className="flex flex-col items-center gap-3 rounded-[10px] border border-slate-200 bg-white p-6 text-center"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-accent/15 text-sm font-semibold text-accent">
                {index + 1}
              </span>
              <span className="text-[15px] font-semibold text-navy">{step}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="mx-auto max-w-[760px] px-6 pb-24">
        <h2 className="mb-8 text-center text-[28px] font-semibold tracking-tight text-navy">
          {copy.home.faq}
        </h2>
        <div className="flex flex-col gap-3">
          {copy.home.faqItems.map((item) => (
            <details
              key={item.question}
              className="group rounded-[10px] border border-slate-200 bg-white px-5 py-4"
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-[15px] font-semibold text-navy marker:content-none">
                {item.question}
                <ChevronIcon className="shrink-0 text-slate-400 transition-transform group-open:rotate-180" />
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-slate-500">{item.answer}</p>
            </details>
          ))}
        </div>
      </section>
    </>
  );
}
