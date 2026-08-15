import { notFound } from "next/navigation";

import { isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { AdSlot } from "@/components/ads/AdSlot";

export default async function PrivacyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<React.ReactElement> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }

  const copy = getMessages(locale as Locale);

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-12 sm:py-16">
      <h1 className="text-2xl font-bold text-navy sm:text-3xl">{copy.pages.privacy.title}</h1>
      <p className="mt-2 text-sm text-slate-400">{copy.privacyPage.lastUpdated}</p>

      <div className="mt-8 space-y-8 text-[15px] leading-relaxed text-slate-600">
        {/* Intro */}

        <section>
          <p>{copy.privacyPage.sections.intro}</p>
        </section>
        {/* What we collect */}
        <section>
          <h2 className="text-lg font-semibold text-navy">
            {copy.privacyPage.sections.whatWeCollect.title}
          </h2>
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {copy.privacyPage.sections.whatWeCollect.items.map((item, i) => (
              <li key={i} dangerouslySetInnerHTML={{ __html: item }} />
            ))}
          </ul>
        </section>

        {/* What we DON'T collect */}
        <section>
          <h2 className="text-lg font-semibold text-navy">
            {copy.privacyPage.sections.whatWeDontCollect.title}
          </h2>
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {copy.privacyPage.sections.whatWeDontCollect.items.map((item, i) => (
              <li key={i} dangerouslySetInnerHTML={{ __html: item }} />
            ))}
          </ul>
        </section>

        {/* How long files are kept */}
        <section>
          <h2 className="text-lg font-semibold text-navy">
            {copy.privacyPage.sections.howLong.title}
          </h2>
          {copy.privacyPage.sections.howLong.paragraphs.map((para, i) => (
            <p
              key={i}
              className={i > 0 ? "mt-2" : "mt-3"}
              dangerouslySetInnerHTML={{ __html: para }}
            />
          ))}
        </section>

        {/* Analytics */}
        <section>
          <h2 className="text-lg font-semibold text-navy">
            {copy.privacyPage.sections.analytics.title}
          </h2>
          {copy.privacyPage.sections.analytics.paragraphs.map((para, i) => (
            <p key={i} className="mt-3" dangerouslySetInnerHTML={{ __html: para }} />
          ))}
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {copy.privacyPage.sections.analytics.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>

        {/* Security */}
        <section>
          <h2 className="text-lg font-semibold text-navy">
            {copy.privacyPage.sections.security.title}
          </h2>
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {copy.privacyPage.sections.security.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>

        {/* Contact */}
        <section>
          <h2 className="text-lg font-semibold text-navy">
            {copy.privacyPage.sections.contact.title}
          </h2>
          {copy.privacyPage.sections.contact.paragraphs.map((para, i) => {
            const email = copy.privacyPage.sections.contact.email;
            return (
              <p key={i} className="mt-3">
                {para.includes("{email}") ? (
                  <>
                    {para.split("{email}")[0]}
                    <a
                      href={`mailto:${email}`}
                      className="font-medium text-accent underline underline-offset-2 hover:text-navy"
                    >
                      {email}
                    </a>
                    {para.split("{email}")[1]}
                  </>
                ) : (
                  para
                )}
              </p>
            );
          })}
        </section>
      </div>
      <div className="mt-10 max-w-full overflow-hidden" aria-label="Advertisement">
        <AdSlot pageSlug="privacy" immediate unit="banner-468x60" />
      </div>
    </div>
  );
}
