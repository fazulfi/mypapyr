import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export function LegalVersionFooter({ locale }: { locale: Locale }): React.ReactElement {
  const { version, effectiveDate, footerLabel } = getMessages(locale).legal;
  return (
    <footer className="mt-10 border-t border-foreground/10 pt-4 text-sm text-foreground/60">
      Version {version} — {footerLabel} {effectiveDate}
    </footer>
  );
}
