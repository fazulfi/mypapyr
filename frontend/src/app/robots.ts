import type { MetadataRoute } from "next";

import { SEO_BASE_URL } from "../lib/seo/alternates";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${SEO_BASE_URL}/sitemap.xml`,
  };
}
