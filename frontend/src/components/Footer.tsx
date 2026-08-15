import Link from "next/link";

import { getAllTools, getLegacyTools } from "../lib/catalog";
import type { Locale } from "../lib/i18n";
import { getMessages } from "../lib/messages";
import { LogoLockup } from "./LogoLockup";

interface FooterSupportLink {
  route: string;
  messageKey: "privacy" | "terms" | "cookiesAdvertising" | "contact" | "status" | "roadmap";
}

const SUPPORT_LINKS: readonly FooterSupportLink[] = [
  { route: "privacy", messageKey: "privacy" },
  { route: "terms", messageKey: "terms" },
  { route: "cookies-advertising", messageKey: "cookiesAdvertising" },
  { route: "contact", messageKey: "contact" },
  { route: "status", messageKey: "status" },
  { route: "roadmap", messageKey: "roadmap" },
];

const basicToolIds = ["compress-pdf", "merge-pdf", "split-pdf"] as const;
const securityToolIds = ["protect", "unlock"] as const;
const enhancementToolIds = ["watermark", "sign"] as const;
const convertToolIds = ["jpg-to-pdf", "pdf-to-jpg"] as const;

interface FooterCategory {
  labelKey: "basic" | "security" | "enhancement" | "conversion";
  toolIds: readonly string[];
}

const FOOTER_CATEGORIES: readonly FooterCategory[] = [
  { labelKey: "basic", toolIds: basicToolIds },
  { labelKey: "security", toolIds: securityToolIds },
  { labelKey: "enhancement", toolIds: enhancementToolIds },
  { labelKey: "conversion", toolIds: convertToolIds },
];

interface FooterProps {
  locale: Locale;
}

export function Footer({ locale }: FooterProps): React.ReactElement {
  const copy = getMessages(locale);
  const footerCopy = copy.footer;
  const currentYear = new Date().getFullYear();
  const allTools = [...getAllTools(), ...getLegacyTools()];

  return (
    <footer className="border-t border-slate-200 bg-bg">
      <div className="mx-auto grid max-w-[1200px] gap-10 px-6 py-12 md:grid-cols-[auto_1fr_1fr]">
        <div className="md:col-span-1">
          <LogoLockup size="footer" locale={locale} />
        </div>

        <nav aria-label={footerCopy.tools}>
          <h2 className="mb-4 text-sm font-semibold text-navy">{footerCopy.tools}</h2>
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
            {FOOTER_CATEGORIES.map((category) => (
              <div key={category.labelKey}>
                <h3 className="mb-3 text-sm font-semibold text-slate-900">
                  {copy.nav[category.labelKey]}
                </h3>
                <ul className="space-y-2">
                  {category.toolIds.map((id) => {
                    const tool = allTools.find((entry) => entry.id === id);
                    if (!tool) return null;
                    return (
                      <li key={tool.id}>
                        <Link
                          href={tool.hrefs[locale]}
                          className="text-sm text-slate-600 transition-colors hover:text-accent"
                        >
                          {tool.shortLabel[locale]}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </div>
        </nav>

        <nav aria-label={footerCopy.support}>
          <h2 className="mb-4 text-sm font-semibold text-navy">{footerCopy.support}</h2>
          <ul className="space-y-2">
            {SUPPORT_LINKS.map((link) => (
              <li key={link.route}>
                <Link
                  href={`/${locale}/${link.route}`}
                  className="text-sm text-slate-500 transition-colors hover:text-navy"
                >
                  {footerCopy[link.messageKey]}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      <div className="border-t border-slate-200">
        <div className="mx-auto max-w-[1200px] px-6 py-6">
          <p className="text-[13px] text-slate-500">
            &copy; {currentYear} {footerCopy.copyright}
          </p>
        </div>
      </div>
    </footer>
  );
}
