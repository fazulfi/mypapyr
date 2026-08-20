import { readFile } from "node:fs/promises";
import path from "node:path";

import { BLOG_ARTICLES, type BlogArticleEntry } from "../../content/blog/manifest";
import { locales, type Locale } from "./i18n";
import { alternateLinks, SEO_BASE_URL } from "./seo/alternates";
import { toolCatalog } from "./catalog";

export const BLOG_AUTHOR = "Papyr Team" as const;
export type BlogTopic = BlogArticleEntry["topic"];

export interface BlogArticle {
  entry: BlogArticleEntry;
  locale: Locale;
  slug: string;
  title: string;
  description: string;
  date: string;
  author: typeof BLOG_AUTHOR;
  href: string;
  toolHref: string;
}

const FILE_PATTERN = /^[a-z0-9-]+\/(en|es|id)\.mdx$/;

export function getBlogEntries(): readonly BlogArticleEntry[] {
  return BLOG_ARTICLES;
}
export function getArticleByTopic(topic: BlogTopic): BlogArticleEntry | undefined {
  return BLOG_ARTICLES.find((entry) => entry.topic === topic);
}
export function blogPaths(entry: BlogArticleEntry): Record<Locale, string> {
  return Object.fromEntries(
    locales.map((locale) => [locale, `/${locale}/blog/${entry.slugs[locale]}`]),
  ) as Record<Locale, string>;
}
export function blogAlternates(locale: Locale, entry: BlogArticleEntry) {
  return alternateLinks(locale, blogPaths(entry));
}
export function toolHrefFor(topic: BlogTopic, locale: Locale): string {
  const tool = toolCatalog.find((candidate) => candidate.id === topic);
  if (!tool) throw new Error(`blog: unknown topic ${topic}`);
  return tool.hrefs[locale];
}
export function getArticle(locale: Locale, slug: string): BlogArticle | undefined {
  if (!locales.includes(locale)) return undefined;
  const entry = BLOG_ARTICLES.find((candidate) => candidate.slugs[locale] === slug);
  if (!entry) return undefined;
  return {
    entry,
    locale,
    slug,
    title: entry.titles[locale],
    description: entry.descriptions[locale],
    date: entry.date,
    author: BLOG_AUTHOR,
    href: `${SEO_BASE_URL}${blogPaths(entry)[locale]}`,
    toolHref: toolHrefFor(entry.topic, locale),
  };
}
export function getArticlesByLocale(locale: Locale): BlogArticle[] {
  return BLOG_ARTICLES.map((entry) => getArticle(locale, entry.slugs[locale])).filter(
    (article): article is BlogArticle => article !== undefined,
  );
}
export function contentFilePath(entry: BlogArticleEntry, locale: Locale): string {
  const file = `${entry.topic}/${locale}.mdx`;
  if (!FILE_PATTERN.test(file)) throw new Error(`blog: unsafe content path ${file}`);
  return path.join(process.cwd(), "content", "blog", file);
}
export async function getArticleSource(locale: Locale, slug: string): Promise<string> {
  const article = getArticle(locale, slug);
  if (!article) throw new Error(`blog: no article for ${locale}/${slug}`);
  return readFile(contentFilePath(article.entry, locale), "utf8");
}
export function countWords(mdx: string): number {
  const body = mdx
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`[^`]*`/g, " ")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]*)\]\(([^)]*)\)/g, "$1 $2")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/[*_>~-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return body.length === 0 ? 0 : body.split(" ").length;
}
export async function validateBlogContent(): Promise<string[]> {
  const violations: string[] = [];
  const slugsPerLocale: Record<Locale, Set<string>> = {
    en: new Set(),
    es: new Set(),
    id: new Set(),
  };
  for (const entry of BLOG_ARTICLES)
    for (const locale of locales) {
      const slug = entry.slugs[locale];
      if (slugsPerLocale[locale].has(slug)) violations.push(`duplicate-slug ${locale}/${slug}`);
      slugsPerLocale[locale].add(slug);
      const file = `${entry.topic}/${locale}.mdx`;
      if (!FILE_PATTERN.test(file)) violations.push(`file-pattern ${file}`);
      let source: string;
      try {
        source = await readFile(contentFilePath(entry, locale), "utf8");
      } catch {
        violations.push(`file-missing ${file}`);
        continue;
      }
      const words = countWords(source);
      if (words < 400 || words > 800) violations.push(`word-count ${file} (${words})`);
      const toolHref = toolHrefFor(entry.topic, locale);
      if (!source.includes(toolHref)) violations.push(`missing-tool-link ${file} (${toolHref})`);
    }
  return violations;
}
