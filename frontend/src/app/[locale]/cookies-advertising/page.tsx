import {
  resolveSupportingPageCopy,
  SupportingPageContent,
  type SupportingPageProps,
} from "@/components/supporting-page";

export default async function CookiesAdvertisingPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const copy = await resolveSupportingPageCopy(params, "cookiesAdvertising");
  return <SupportingPageContent copy={copy} pageSlug="cookies-advertising" />;
}
