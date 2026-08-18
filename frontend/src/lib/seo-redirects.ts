import type { Locale } from "./i18n";
import { getLegacyTools } from "./catalog";

// SEO-02 redirect map. The SH-01 legacy inventory is partitioned into three
// disjoint dispositions (DEC-023, DEC-042, DEC-047, DEC-194):
//   1. five active tool aliases  -> direct one-hop 301 to the localized EN route
//   2. eight deferred legacy tools -> intentional localized 410 Gone (DEC-194)
//   3. /faq and /privacy -> conservative pass-through (reserved for locale routing)
// Every target below is a hard-coded closed internal path; the proxy never
// redirects to a user-supplied destination.
export const ACTIVE_ALIAS_REDIRECTS: Readonly<Record<string, string>> = {
  "/compress": "/en/compress-pdf",
  "/merge": "/en/merge-pdf",
  "/split": "/en/split-pdf",
  "/image-to-pdf": "/en/jpg-to-pdf",
  "/pdf-to-image": "/en/pdf-to-jpg",
};

export const DEFERRED_GONE_PATHS: ReadonlySet<string> = new Set([
  "/rotate",
  "/protect",
  "/unlock",
  "/watermark",
  "/sign",
  "/pdf-to-word",
  "/ocr",
  "/pdf-to-excel",
]);

export const DEFERRED_TOOL_IDS: Readonly<Record<string, string>> = {
  "/rotate": "rotate",
  "/protect": "protect",
  "/unlock": "unlock",
  "/watermark": "watermark",
  "/sign": "sign",
  "/pdf-to-word": "pdf-to-word",
  "/ocr": "ocr",
  "/pdf-to-excel": "pdf-to-excel",
};

export const CONSERVATIVE_PATHS: ReadonlySet<string> = new Set(["/faq", "/privacy"]);

export function redirectTargetFor(pathname: string): string | null {
  return ACTIVE_ALIAS_REDIRECTS[pathname] ?? null;
}

export function deferredToolId(pathname: string): string | null {
  return DEFERRED_TOOL_IDS[pathname] ?? null;
}

export function isConservativePassThrough(pathname: string): boolean {
  return CONSERVATIVE_PATHS.has(pathname);
}

export function localizedToolLabel(locale: Locale, toolId: string): string {
  const entry = getLegacyTools().find((tool) => tool.id === toolId);
  return entry?.localizedLabels[locale] ?? toolId;
}
