import { cookies, headers } from "next/headers";

import "./globals.css";

import { SkipLink } from "@/components/SkipLink";
import { fontVariables } from "@/lib/fonts";
import { type Locale, resolveLocale } from "@/lib/i18n";
import { getMessages, type Messages } from "@/lib/messages";

interface NotFoundContentProps {
  locale: Locale;
  messages: Messages;
}

export function NotFoundContent({ locale, messages }: NotFoundContentProps): React.ReactElement {
  return (
    <html lang={locale} className={fontVariables}>
      <body className="flex min-h-dvh flex-col bg-[var(--color-bg)] font-sans text-[var(--color-foreground)] antialiased">
        <SkipLink label={messages.a11y.skipToContent} />
        <main
          id="main-content"
          tabIndex={-1}
          className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center"
        >
          <h1 className="mb-2 text-4xl font-bold tracking-tight">{messages.notFound.title}</h1>
          <p className="max-w-md text-lg">{messages.notFound.description}</p>
        </main>
      </body>
    </html>
  );
}

export default async function NotFound(): Promise<React.ReactElement> {
  const cookieStore = await cookies();
  const headersList = await headers();

  const localePreference = cookieStore.get("papyr_locale")?.value;
  const acceptLanguage = headersList.get("accept-language");
  const locale = resolveLocale(localePreference, acceptLanguage);
  const messages = getMessages(locale);

  return <NotFoundContent locale={locale} messages={messages} />;
}
