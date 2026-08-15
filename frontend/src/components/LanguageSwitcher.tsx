import type { Locale } from "../lib/i18n";
import { locales } from "../lib/i18n";

interface LanguageSwitcherProps {
  currentLocale: Locale;
  a11yLabel: string;
  languageLabels: Record<Locale, string>;
  getEquivalentPath: (targetLocale: Locale) => string;
}

/**
 * Language selector rendered as a native <select> so it is keyboard- and
 * screen-reader-friendly by default. Changing the option navigates to the
 * equivalent path in the chosen locale (preserves tool route + subpath).
 */
export function LanguageSwitcher({
  currentLocale,
  a11yLabel,
  languageLabels,
  getEquivalentPath,
}: LanguageSwitcherProps): React.ReactElement {
  return (
    <label className="inline-flex items-center gap-1">
      <span className="sr-only">{a11yLabel}</span>
      <select
        aria-label={a11yLabel}
        value={currentLocale}
        onChange={(event) => {
          const target = event.target.value as Locale;
          if (target !== currentLocale) {
            window.location.href = getEquivalentPath(target);
          }
        }}
        className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-700 transition-colors hover:border-slate-300 focus:border-navy focus:outline-none focus:ring-1 focus:ring-navy"
      >
        {locales.map((locale) => (
          <option key={locale} value={locale} lang={locale}>
            {languageLabels[locale]}
          </option>
        ))}
      </select>
    </label>
  );
}
