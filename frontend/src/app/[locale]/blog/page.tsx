import {
  resolveSupportingPageCopy,
  SupportingPageContent,
  type SupportingPageProps,
} from "@/components/supporting-page";

export default async function BlogPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const copy = await resolveSupportingPageCopy(params, "blog");
  return <SupportingPageContent copy={copy} pageSlug="blog" adLabel={copy.adLabel} />;
}
