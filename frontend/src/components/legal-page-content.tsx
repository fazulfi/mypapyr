import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import type { SupportingPageCopy } from "@/components/supporting-page";

import { AdSlot } from "@/components/ads/AdSlot";
import { LegalVersionFooter } from "@/components/legal-version-footer";

export type LegalSectionsKey = "privacy" | "terms" | "cookiesAdvertising";

export function LegalPageContent({
  copy,
  locale,
  sectionsKey,
}: {
  copy: SupportingPageCopy;
  locale: Locale;
  sectionsKey: LegalSectionsKey;
}): React.ReactElement {
  const sections = getMessages(locale).legal.sections[sectionsKey];
  return (
    <article className="mx-auto max-w-3xl">
      <h1>{copy.title}</h1>
      <p>{copy.description}</p>
      {sectionsKey === "privacy" ? (
        <p className="mt-2 text-sm text-foreground/60">
          {getMessages(locale).privacyPage.lastUpdated}
        </p>
      ) : null}
      {sections.map((section) => (
        <section key={section.heading} className="mt-8">
          <h2>{section.heading}</h2>
          {section.paragraphs.map((paragraph, index) => (
            <p key={index} className="mt-2">
              {paragraph.includes("privacy@mypapyr.com") ? (
                <>
                  {paragraph.split("privacy@mypapyr.com")[0]}
                  <a href="mailto:privacy@mypapyr.com">privacy@mypapyr.com</a>
                  {paragraph.split("privacy@mypapyr.com")[1]}
                </>
              ) : (
                paragraph
              )}
            </p>
          ))}
        </section>
      ))}
      <LegalVersionFooter locale={locale} />
      <div className="mt-10 max-w-full overflow-hidden" aria-label={copy.adLabel}>
        <AdSlot pageSlug={sectionsKey} immediate unit="banner-468x60" label={copy.adLabel} />
      </div>
    </article>
  );
}
