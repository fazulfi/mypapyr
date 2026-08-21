"use client";

import { use, useState } from "react";

import { isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { AdSlot } from "@/components/ads/AdSlot";

/* ── Inline SVG Icons ── */

function ChevronDownIcon({ open }: { open: boolean }) {
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
      className={`shrink-0 text-slate-600 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

function HelpCircleIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-accent"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

/* ── Accordion Item ── */

function AccordionItem({
  question,
  answer,
  isOpen,
  onToggle,
}: {
  question: string;
  answer: string;
  isOpen: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white transition-shadow hover:shadow-sm">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <span className="text-[15px] font-semibold text-navy">{question}</span>
        <ChevronDownIcon open={isOpen} />
      </button>
      <div
        className={`grid transition-all duration-200 ease-in-out ${
          isOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          <p className="px-5 pb-4 text-[15px] leading-relaxed text-slate-600">{answer}</p>
        </div>
      </div>
    </div>
  );
}

/* ── Internal FAQ component (accepts locale directly for testability) ── */

export function FAQContent({ locale }: { locale: string }): React.ReactElement {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const validLocale = isLocale(locale) ? (locale as Locale) : "en";
  const copy = getMessages(validLocale);

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-12 sm:py-16">
      {/* Header */}
      <div className="flex items-center gap-3">
        <HelpCircleIcon />
        <h1 className="text-2xl font-bold text-navy sm:text-3xl">{copy.faqPage.title}</h1>
      </div>
      <p className="mt-3 text-[15px] text-slate-500">{copy.faqPage.subtitle}</p>

      {/* Accordion */}
      <div className="mt-8 space-y-3">
        {copy.faqPage.items.map((item, index) => (
          <AccordionItem
            key={index}
            question={item.q}
            answer={item.a}
            isOpen={openIndex === index}
            onToggle={() => setOpenIndex(openIndex === index ? null : index)}
          />
        ))}
      </div>

      {/* CTA */}
      <div className="mt-10 rounded-xl bg-slate-50 p-6 text-center">
        <p className="text-[15px] text-slate-600">{copy.faqPage.cta}</p>
        <a
          href={`mailto:${copy.faqPage.ctaEmail}`}
          className="mt-2 inline-block text-[15px] font-medium text-accent underline underline-offset-2 hover:text-navy"
        >
          {copy.faqPage.ctaEmail}
        </a>
      </div>
      <div
        className="mt-10 flex max-w-full flex-col items-center gap-6 overflow-hidden"
        aria-label="Advertisement"
      >
        <AdSlot pageSlug="faq" immediate unit="banner-468x60" label={copy.ads.label} />
      </div>
    </div>
  );
}

/* ── FAQ Page (client component for Next.js route) ── */

export default function FAQPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}): React.ReactElement {
  const { locale } = use(params);
  return <FAQContent locale={locale} />;
}
