import Link from "next/link";

import { toolCatalog } from "../lib/catalog";
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

interface FooterProps {
  locale: Locale;
}

export function Footer({ locale }: FooterProps): React.ReactElement {
  const footerCopy = getMessages(locale).footer;
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-slate-200 bg-bg">
      <div className="mx-auto grid max-w-[1200px] gap-10 px-6 py-12 md:grid-cols-[auto_1fr_1fr]">
        <div className="md:col-span-1">
          <LogoLockup size="footer" locale={locale} />
        </div>

        <nav aria-label={footerCopy.tools}>
          <h2 className="mb-4 text-sm font-semibold text-navy">{footerCopy.tools}</h2>
          <ul className="space-y-2">
            {toolCatalog.map((tool) => (
              <li key={tool.id}>
                <Link
                  href={tool.hrefs[locale]}
                  className="text-sm text-slate-500 transition-colors hover:text-navy"
                >
                  {tool.shortLabel[locale]}
                </Link>
              </li>
            ))}
          </ul>
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
