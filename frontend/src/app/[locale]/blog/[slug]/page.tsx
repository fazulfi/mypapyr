import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ReactElement } from "react";
import { MDXRemote } from "next-mdx-remote/rsc";

import { AdSlot } from "@/components/ads/AdSlot";
import {
  BLOG_AUTHOR,
  blogAlternates,
  getArticle,
  getArticlesByLocale,
  getArticleSource,
} from "@/lib/blog";
import { isLocale, locales } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

export const dynamicParams = false;

export function generateStaticParams(): { locale: string; slug: string }[] {
  return locales.flatMap((locale) =>
    getArticlesByLocale(locale).map((article) => ({ locale, slug: article.slug })),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale: rawLocale, slug } = await params;
  if (!isLocale(rawLocale)) notFound();
  const article = getArticle(rawLocale, slug);
  if (!article) notFound();
  return {
    title: article.title,
    description: article.description,
    alternates: blogAlternates(rawLocale, article.entry),
  };
}

export default async function BlogArticlePage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<ReactElement> {
  const { locale: rawLocale, slug } = await params;
  if (!isLocale(rawLocale)) notFound();
  const article = getArticle(rawLocale, slug);
  if (!article) notFound();
  const source = await getArticleSource(rawLocale, slug);
  const adLabel = getMessages(rawLocale).ads.label;
  return (
    <article className="mx-auto max-w-3xl">
      <header className="mb-6">
        <h1>{article.title}</h1>
        <p className="mt-2 text-sm text-foreground/60">
          <time dateTime={article.date}>{article.date}</time> · {BLOG_AUTHOR}
        </p>
      </header>
      <div className="prose prose-neutral max-w-none">
        <MDXRemote source={source} />
      </div>
      <div className="mt-8 max-w-full overflow-hidden" aria-label={adLabel}>
        <AdSlot pageSlug="blog" immediate unit="banner-468x60" label={adLabel} />
      </div>
    </article>
  );
}
