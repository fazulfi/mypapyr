import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { getArticlesByLocale, BLOG_AUTHOR } from "@/lib/blog";
import { isLocale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { supportingPageMetadata } from "@/lib/seo/alternates";
import type { SupportingPageProps } from "@/components/supporting-page";

export async function generateMetadata({ params }: SupportingPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const copy = getMessages(locale).pages.blog;
  return supportingPageMetadata(locale, "blog", copy.title, copy.description);
}

export default async function BlogListingPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const articles = getArticlesByLocale(locale);
  const copy = getMessages(locale).pages.blog;
  return (
    <div className="mx-auto max-w-3xl">
      <h1>{copy.title}</h1>
      <p>{copy.description}</p>
      <ul className="mt-8 space-y-6">
        {articles.map((article) => (
          <li key={article.slug}>
            <Link
              href={`/${locale}/blog/${article.slug}`}
              className="text-xl font-semibold text-accent"
            >
              {article.title}
            </Link>
            <p className="mt-1 text-sm text-foreground/60">
              <time dateTime={article.date}>{article.date}</time> · {BLOG_AUTHOR}
            </p>
            <p className="mt-1">{article.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
