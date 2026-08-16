import type { MetadataRoute } from "next";

import { toolCatalog } from "../lib/catalog";

export const BASE_URL = "https://budgezen.com";

// Deferred legacy tool slugs: they no longer exist as live routes in the
// five-tool launch and are served by the URL-disposition layer as an
// intentional localized 410 Gone. Per DEC-194 they are excluded from the
// sitemap; the user's faq/privacy entry points (locale-less /faq, /privacy)
// remain the canonical legacy paths.
const ACTIVE_TOOL_EN_SLUGS = toolCatalog.map((tool) => tool.hrefs.en);

const LEGACY_TOOL_IDS = [
  "rotate",
  "protect",
  "unlock",
  "watermark",
  "sign",
  "pdf-to-word",
  "ocr",
  "pdf-to-excel",
] as const;

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  return [
    {
      url: BASE_URL,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 1,
    },
    ...ACTIVE_TOOL_EN_SLUGS.map((slug) => ({
      url: `${BASE_URL}${slug}`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.8,
    })),
    {
      url: `${BASE_URL}/tool-unavailable`,
      lastModified: now,
      changeFrequency: "yearly",
      priority: 0.1,
    },
    ...LEGACY_TOOL_IDS.map((id) => ({
      url: `${BASE_URL}/tool-unavailable?tool=${id}`,
      lastModified: now,
      changeFrequency: "yearly" as const,
      priority: 0.1,
    })),
    {
      url: `${BASE_URL}/faq`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.5,
    },
    {
      url: `${BASE_URL}/privacy`,
      lastModified: now,
      changeFrequency: "yearly",
      priority: 0.3,
    },
  ];
}
