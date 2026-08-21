"use client";

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";

import type { Locale } from "../lib/i18n";
import { locales } from "../lib/i18n";
import { getAllTools, getLegacyTools, type CatalogTool } from "../lib/catalog";
import { getMessages } from "../lib/messages";
import { LogoLockup } from "./LogoLockup";
import { LanguageSwitcher } from "./LanguageSwitcher";

const basicToolIds = ["compress-pdf", "merge-pdf", "split-pdf"] as const;
const securityToolIds = ["protect", "unlock"] as const;
const enhancementToolIds = ["watermark", "sign"] as const;
const convertToolIds = ["jpg-to-pdf", "pdf-to-jpg"] as const;

export interface NavCategory {
  label: string;
  tools: readonly CatalogTool[];
}

export function getNavCategories(locale: Locale): NavCategory[] {
  const allTools = [...getAllTools(), ...getLegacyTools()];
  const copy = getMessages(locale);
  const basicTools: CatalogTool[] = [];
  const securityTools: CatalogTool[] = [];
  const enhancementTools: CatalogTool[] = [];
  const convertTools: CatalogTool[] = [];
  for (const tool of allTools) {
    if ((basicToolIds as readonly string[]).includes(tool.id)) {
      basicTools.push(tool);
    } else if ((securityToolIds as readonly string[]).includes(tool.id)) {
      securityTools.push(tool);
    } else if ((enhancementToolIds as readonly string[]).includes(tool.id)) {
      enhancementTools.push(tool);
    } else if ((convertToolIds as readonly string[]).includes(tool.id)) {
      convertTools.push(tool);
    }
  }
  return [
    { label: copy.nav.basic, tools: basicTools },
    { label: copy.nav.security, tools: securityTools },
    { label: copy.nav.enhancement, tools: enhancementTools },
    { label: copy.nav.conversion, tools: convertTools },
  ];
}

export function resolveEquivalentPath(
  pathname: string,
  currentLocale: Locale,
  targetLocale: Locale,
): string {
  const allTools = getAllTools();

  const currentTool = allTools.find((tool) => pathname.includes(tool.hrefs[currentLocale]));
  if (currentTool) {
    return currentTool.hrefs[targetLocale];
  }

  const segments = pathname.split("/").filter(Boolean);
  if (segments.length > 0 && (locales as readonly string[]).includes(segments[0])) {
    segments[0] = targetLocale;
    return `/${segments.join("/")}`;
  }

  return `/${targetLocale}`;
}

export function ChevronDownIcon() {
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
      aria-hidden="true"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

export function MenuIcon() {
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
      aria-hidden="true"
    >
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  );
}

export function XIcon() {
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
      aria-hidden="true"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

const CHEVRON_DOWN_SVG = (
  <svg
    width="13"
    height="13"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <polyline points="6 9 12 15 18 9" />
  </svg>
);

const MENU_SVG = (
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
    <line x1="3" y1="6" x2="21" y2="6" />
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="3" y1="18" x2="21" y2="18" />
  </svg>
);

const X_SVG = (
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
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

interface NavbarProps {
  locale: Locale;
}

export function Navbar({ locale }: NavbarProps): React.ReactElement {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openCategory, setOpenCategory] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const copy = getMessages(locale);
  const categories = getNavCategories(locale);
  const firstCategoryTools = categories[0]?.tools ?? [];

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpenCategory(null);
      }
    }

    function handleEscape(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setOpenCategory(null);
        setMobileOpen(false);
      }
    }

    function handlePopState() {
      setOpenCategory(null);
      setMobileOpen(false);
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    window.addEventListener("popstate", handlePopState);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-bg/92 backdrop-blur-md">
      <div className="mx-auto flex h-[52px] max-w-[1440px] items-center gap-4 px-4 sm:px-6">
        <LogoLockup size="navbar" locale={locale} />

        <div
          ref={dropdownRef}
          className="hidden min-w-0 flex-1 items-center justify-center gap-1 md:flex"
        >
          {categories.map((category) => {
            const isOpen = openCategory === category.label;
            const btnId = `nav-category-${category.label.toLowerCase().replace(/\s+/g, "-")}`;
            const ddId = `nav-dropdown-${category.label.toLowerCase().replace(/\s+/g, "-")}`;
            return (
              <div key={category.label} className="relative">
                <button
                  id={btnId}
                  onMouseEnter={() => setOpenCategory(category.label)}
                  onClick={() => setOpenCategory(isOpen ? null : category.label)}
                  aria-expanded={isOpen}
                  aria-controls={ddId}
                  className={`flex items-center gap-1 whitespace-nowrap rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors lg:px-3 lg:text-sm ${
                    isOpen
                      ? "bg-slate-100 text-slate-900"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`}
                >
                  {category.label}
                  <span className={`transition-transform ${isOpen ? "rotate-180" : ""}`}>
                    {CHEVRON_DOWN_SVG}
                  </span>
                </button>

                {isOpen && (
                  <div
                    id={ddId}
                    className="absolute left-0 top-full z-50 mt-1 w-56 rounded-lg border border-slate-200 bg-white py-2 shadow-lg"
                  >
                    {category.tools.map((tool) => (
                      <a
                        key={tool.id}
                        href={tool.hrefs[locale]}
                        className={`block px-4 py-2 text-sm transition-colors hover:bg-slate-100 ${
                          pathname.includes(tool.hrefs[locale])
                            ? "bg-accent/10 text-blue-800 font-medium"
                            : "text-slate-600"
                        }`}
                        onClick={() => setOpenCategory(null)}
                      >
                        {tool.fullLabel[locale]}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="hidden shrink-0 items-center gap-3 md:flex">
          <LanguageSwitcher
            currentLocale={locale}
            a11yLabel={copy.a11y.languageSwitcher}
            languageLabels={copy.languages}
            getEquivalentPath={(targetLocale) =>
              resolveEquivalentPath(pathname, locale, targetLocale)
            }
          />
          <a
            href={firstCategoryTools[0]?.hrefs[locale] ?? `/${locale}`}
            className="shrink-0 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            {copy.nav.cta}
          </a>
        </div>

        <div className="flex items-center gap-3 md:hidden">
          <a
            href={firstCategoryTools[0]?.hrefs[locale] ?? `/${locale}`}
            className="flex min-h-[44px] items-center rounded-lg bg-accent px-3.5 py-1.5 text-[13px] font-semibold text-white"
            onClick={() => setMobileOpen(false)}
          >
            {copy.nav.cta}
          </a>
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="flex min-h-[44px] min-w-[44px] items-center justify-center text-slate-600"
            aria-label={mobileOpen ? copy.a11y.navClose : copy.a11y.navToggle}
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? X_SVG : MENU_SVG}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="border-t border-slate-200 bg-white px-4 py-4 md:hidden sm:px-6">
          <div className="flex flex-col gap-3">
            {categories.map((category) => (
              <details key={category.label} className="group">
                <summary className="flex min-h-[44px] cursor-pointer items-center justify-between rounded-lg bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-900 marker:content-none">
                  {category.label}
                  <span className="transition-transform group-open:rotate-180">
                    {CHEVRON_DOWN_SVG}
                  </span>
                </summary>
                <div className="mt-2 flex flex-col gap-1 pl-4">
                  {category.tools.map((tool) => (
                    <a
                      key={tool.id}
                      href={tool.hrefs[locale]}
                      onClick={() => setMobileOpen(false)}
                      className={`flex min-h-[44px] items-center rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
                        pathname.includes(tool.hrefs[locale])
                          ? "bg-accent/10 text-blue-800"
                          : "text-slate-600 hover:bg-slate-50"
                      }`}
                    >
                      {tool.fullLabel[locale]}
                    </a>
                  ))}
                </div>
              </details>
            ))}
            <div className="pt-2">
              <LanguageSwitcher
                currentLocale={locale}
                a11yLabel={copy.a11y.languageSwitcher}
                languageLabels={copy.languages}
                getEquivalentPath={(targetLocale) =>
                  resolveEquivalentPath(pathname, locale, targetLocale)
                }
              />
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
