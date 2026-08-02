import type { Locale } from "../lib/i18n";
import { locales } from "../lib/i18n";

interface LanguageSwitcherProps {
  currentLocale: Locale;
  a11yLabel: string;
  languageLabels: Record<Locale, string>;
  getEquivalentPath: (targetLocale: Locale) => string;
}

export function LanguageSwitcher({
  currentLocale,
  a11yLabel,
  languageLabels,
  getEquivalentPath,
}: LanguageSwitcherProps): React.ReactElement {
  return (
    <fieldset aria-label={a11yLabel}>
      <legend className="sr-only">{a11yLabel}</legend>
      <div className="flex items-center gap-1">
        {locales.map((locale) => (
          <a
            key={locale}
            href={getEquivalentPath(locale)}
            aria-current={locale === currentLocale ? "page" : undefined}
            lang={locale}
            hrefLang={locale}
            className={
              locale === currentLocale
                ? "rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-navy"
                : "rounded-md px-2 py-1 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
            }
          >
            {languageLabels[locale]}
          </a>
        ))}
      </div>
    </fieldset>
  );
}
