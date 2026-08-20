import { describe, expect, it } from "vitest";

import { LEGACY_ROUTING_PATHS } from "../i18n";
import {
  ACTIVE_ALIAS_REDIRECTS,
  CONSERVATIVE_PATHS,
  DEFERRED_GONE_PATHS,
  DEFERRED_TOOL_IDS,
  deferredToolId,
  isConservativePassThrough,
  redirectTargetFor,
} from "../seo-redirects";

describe("SEO-02 redirect map inventory", () => {
  it("maps exactly the five active tool aliases to direct localized EN targets", () => {
    expect(ACTIVE_ALIAS_REDIRECTS).toEqual({
      "/compress": "/en/compress-pdf",
      "/merge": "/en/merge-pdf",
      "/split": "/en/split-pdf",
      "/image-to-pdf": "/en/jpg-to-pdf",
      "/pdf-to-image": "/en/pdf-to-jpg",
    });
  });

  it("flags exactly the eight deferred legacy tools as 410", () => {
    expect([...DEFERRED_GONE_PATHS]).toEqual([
      "/rotate",
      "/protect",
      "/unlock",
      "/watermark",
      "/sign",
      "/pdf-to-word",
      "/ocr",
      "/pdf-to-excel",
    ]);
    expect(DEFERRED_TOOL_IDS).toEqual({
      "/rotate": "rotate",
      "/protect": "protect",
      "/unlock": "unlock",
      "/watermark": "watermark",
      "/sign": "sign",
      "/pdf-to-word": "pdf-to-word",
      "/ocr": "ocr",
      "/pdf-to-excel": "pdf-to-excel",
    });
  });

  it("keeps /faq and /privacy conservative (pass-through, not redirected)", () => {
    expect([...CONSERVATIVE_PATHS]).toEqual(["/faq", "/privacy"]);
  });

  it("partitions the full SH-01 inventory exactly, without overlap or gaps", () => {
    const partitioned = new Set([
      ...Object.keys(ACTIVE_ALIAS_REDIRECTS),
      ...DEFERRED_GONE_PATHS,
      ...CONSERVATIVE_PATHS,
    ]);
    expect(partitioned.size).toBe(LEGACY_ROUTING_PATHS.size);
    for (const path of LEGACY_ROUTING_PATHS) {
      expect(partitioned.has(path)).toBe(true);
    }
  });

  it("never points an active alias at a retired or locale-less target", () => {
    for (const target of Object.values(ACTIVE_ALIAS_REDIRECTS)) {
      expect(target).toMatch(/^\/(en|es|id)\//);
      for (const retired of DEFERRED_GONE_PATHS) {
        expect(target).not.toBe(retired);
      }
      expect(target).not.toBe("/faq");
      expect(target).not.toBe("/privacy");
    }
  });
});

describe("SEO-02 redirectTargetFor", () => {
  it("resolves every active tool alias to its closed internal EN target", () => {
    for (const [alias, target] of Object.entries(ACTIVE_ALIAS_REDIRECTS)) {
      expect(redirectTargetFor(alias)).toBe(target);
    }
  });

  it("returns null for deferred, conservative, localized, and root paths", () => {
    for (const path of [
      ...DEFERRED_GONE_PATHS,
      "/faq",
      "/privacy",
      "/",
      "/compress-pdf",
      "/en/compress-pdf",
      "/es/compress-pdf",
      "/en/rotate",
      "/fr/foo",
    ]) {
      expect(redirectTargetFor(path)).toBeNull();
    }
  });
});

describe("SEO-02 deferredToolId and conservative pass-through", () => {
  it("resolves every deferred path to its tool id", () => {
    for (const [path, id] of Object.entries(DEFERRED_TOOL_IDS)) {
      expect(deferredToolId(path)).toBe(id);
    }
  });

  it("returns null for non-deferred paths", () => {
    for (const path of [
      "/compress",
      "/faq",
      "/privacy",
      "/",
      "/compress-pdf",
      "/en/rotate",
      "/fr/rotate",
    ]) {
      expect(deferredToolId(path)).toBeNull();
    }
  });

  it("passes through only /faq and /privacy", () => {
    expect(isConservativePassThrough("/faq")).toBe(true);
    expect(isConservativePassThrough("/privacy")).toBe(true);
    for (const path of [
      "/compress",
      "/rotate",
      "/faq/x",
      "/privacy/x",
      "/compress-pdf",
      "/",
      "/en/faq",
    ]) {
      expect(isConservativePassThrough(path)).toBe(false);
    }
  });
});
