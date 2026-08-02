import { describe, expect, it } from "vitest";

import { locales, type Locale } from "../i18n";
import { productStatus } from "../product-status";
import { TOOL_IDS } from "../tool-ids";
import { getAllTools, getToolById, getToolHrefs, toolCatalog, type CatalogTool } from "../catalog";

// SH-04 contract, grounded in read-only canonical sources at f4b792c (R-15 slug
// table; product UX §8.2/§12 EN identities; legacy ALL_TOOLS §9.3 ID labels).
// Copy flag: no canonical Spanish display-label string exists; ES labels are the
// display forms matching the owner-approved Spanish slugs verbatim.

const EN_LABELS = ["Compress PDF", "Merge PDF", "Split PDF", "JPG to PDF", "PDF to JPG"] as const;

const ES_LABELS = [
  "Comprimir PDF",
  "Combinar PDF",
  "Dividir PDF",
  "JPG a PDF",
  "PDF a JPG",
] as const;

const ID_LABELS = [
  "Kompres PDF",
  "Gabungkan PDF",
  "Pisahkan PDF",
  "Gambar ke PDF",
  "PDF ke Gambar",
] as const;

const EN_HREFS = [
  "/en/compress-pdf",
  "/en/merge-pdf",
  "/en/split-pdf",
  "/en/jpg-to-pdf",
  "/en/pdf-to-jpg",
] as const;

const ES_HREFS = [
  "/es/comprimir-pdf",
  "/es/combinar-pdf",
  "/es/dividir-pdf",
  "/es/jpg-a-pdf",
  "/es/pdf-a-jpg",
] as const;

const ID_HREFS = [
  "/id/kompres-pdf",
  "/id/gabungkan-pdf",
  "/id/pisahkan-pdf",
  "/id/gambar-ke-pdf",
  "/id/pdf-ke-gambar",
] as const;

describe("toolCatalog (canonical, exactly five tools)", () => {
  it("exports exactly the five canonical tools with the five required fields", () => {
    expect(toolCatalog).toHaveLength(5);

    for (const tool of toolCatalog) {
      expect(typeof tool.id).toBe("string");
      expect(tool.hrefs).toEqual(
        expect.objectContaining({
          en: expect.any(String),
          es: expect.any(String),
          id: expect.any(String),
        }),
      );
      expect(tool.shortLabel).toEqual(
        expect.objectContaining({
          en: expect.any(String),
          es: expect.any(String),
          id: expect.any(String),
        }),
      );
      expect(tool.fullLabel).toEqual(
        expect.objectContaining({
          en: expect.any(String),
          es: expect.any(String),
          id: expect.any(String),
        }),
      );
      expect(tool.localizedLabels).toEqual(
        expect.objectContaining({
          en: expect.any(String),
          es: expect.any(String),
          id: expect.any(String),
        }),
      );
    }
  });

  it("preserves the canonical English tool identities in order", () => {
    expect(toolCatalog.map((t) => t.id)).toEqual([...TOOL_IDS]);
    expect(toolCatalog.map((t) => t.fullLabel.en)).toEqual([...EN_LABELS]);
  });

  it("provides localised labels grounded in canonical sources per locale", () => {
    expect(toolCatalog.map((t) => t.localizedLabels.es)).toEqual([...ES_LABELS]);
    expect(toolCatalog.map((t) => t.localizedLabels.id)).toEqual([...ID_LABELS]);
    expect(toolCatalog.map((t) => t.localizedLabels.en)).toEqual([...EN_LABELS]);
  });

  it("exposes the owner-approved EN route for each tool", () => {
    const resolved = toolCatalog.map((t) => t.hrefs.en);
    expect(resolved).toEqual([...EN_HREFS]);
  });

  it("exposes the owner-approved ES route for each tool", () => {
    const resolved = toolCatalog.map((t) => t.hrefs.es);
    expect(resolved).toEqual([...ES_HREFS]);
  });

  it("exposes the owner-approved ID route for each tool", () => {
    const resolved = toolCatalog.map((t) => t.hrefs.id);
    expect(resolved).toEqual([...ID_HREFS]);
  });
});

describe("catalog helper APIs", () => {
  it("getAllTools returns the canonical ordered tools", () => {
    expect(getAllTools()).toEqual(toolCatalog);
  });

  it("getToolById resolves a canonical tool by id", () => {
    const compress = getToolById("compress-pdf");
    expect(compress?.id).toBe("compress-pdf");
    expect(compress?.hrefs.en).toBe("/en/compress-pdf");
    expect(compress?.fullLabel.en).toBe("Compress PDF");
    expect(getToolById("not-a-tool")).toBeUndefined();
  });

  it("getToolHrefs returns the unique per-locale hrefs for a tool", () => {
    expect(getToolHrefs("merge-pdf")).toEqual({
      en: "/en/merge-pdf",
      es: "/es/combinar-pdf",
      id: "/id/gabungkan-pdf",
    });
    expect(getToolHrefs("unknown")).toBeUndefined();
  });
});

describe("route uniqueness", () => {
  it("all 15 hrefs across locales are unique", () => {
    const allHrefs = toolCatalog.flatMap((t) => [t.hrefs.en, t.hrefs.es, t.hrefs.id]);
    expect(allHrefs).toHaveLength(15);
    expect(new Set(allHrefs).size).toBe(15);
  });

  it("excludes aliases and deferred tools from the canonical catalog", () => {
    const ids = toolCatalog.map((t) => t.id);
    expect(ids).not.toContain("image-to-pdf");
    expect(ids).not.toContain("pdf-to-image");
    expect(ids).not.toContain("rotate");
    expect(ids).not.toContain("pdf-to-word");
  });
});

// SH-04 review fixes: catalog duplicated the canonical Locale type and the
// tool ids. Canonical product UX §8.4 (Brand Guidelines icon table) and the
// product spec §4 Purpose lines require a description and an icon per tool.

const CANONICAL_DESCRIPTIONS = {
  "compress-pdf":
    "Reduce PDF file size while preserving crisp on-screen quality, using one automatic high-quality profile.",
  "merge-pdf":
    "Combine multiple PDFs into one file in the user's chosen order, with controls at the file level.",
  "split-pdf":
    "Extract selected pages as separate PDFs using custom page ranges or one PDF per page.",
  "jpg-to-pdf": "Convert images into a single PDF with automatic, safe fitting.",
  "pdf-to-jpg": "Convert PDF pages to high-quality JPG images with one automatic output profile.",
} as const;

// Lucide-compatible stroke icon identifiers per Brand Guidelines §8.4/§8.5:
// Compress = archive box, Merge = joined documents, Split = scissors,
// JPG to PDF = image into file, PDF to JPG = file to image.
const CANONICAL_ICONS = {
  "compress-pdf": "archive",
  "merge-pdf": "files",
  "split-pdf": "scissors",
  "jpg-to-pdf": "file-image",
  "pdf-to-jpg": "image",
} as const;

describe("canonical description and icon (UX §8.4 / product spec §4)", () => {
  it("carries a non-empty canonical description for every tool", () => {
    for (const tool of toolCatalog) {
      expect(tool.description).toBeTruthy();
      expect(tool.description.length).toBeGreaterThan(0);
    }
  });

  it("carries a non-empty canonical icon identifier for every tool", () => {
    for (const tool of toolCatalog) {
      expect(tool.icon).toBeTruthy();
      expect(tool.icon.length).toBeGreaterThan(0);
    }
  });

  it("descriptions match the canonical product-spec Purpose lines verbatim", () => {
    const byId = new Map(toolCatalog.map((t) => [t.id, t.description]));
    for (const id of TOOL_IDS) {
      expect(byId.get(id)).toBe(CANONICAL_DESCRIPTIONS[id]);
    }
  });

  it("icons match the canonical Brand-Guidelines §8.4 identifiers verbatim", () => {
    const byId = new Map(toolCatalog.map((t) => [t.id, t.icon]));
    for (const id of TOOL_IDS) {
      expect(byId.get(id)).toBe(CANONICAL_ICONS[id]);
    }
  });

  it("descriptions and icons are unique across the five tools", () => {
    expect(new Set(toolCatalog.map((t) => t.description)).size).toBe(toolCatalog.length);
    expect(new Set(toolCatalog.map((t) => t.icon)).size).toBe(toolCatalog.length);
  });
});

describe("single authoritative identity (SH-04 review fixes)", () => {
  it("catalog ids are exactly the canonical TOOL_IDS tuple in order", () => {
    expect(toolCatalog.map((t) => t.id)).toEqual([...TOOL_IDS]);
  });

  it("catalog ids match product-status plannedTools (no duplicated id list)", () => {
    expect(toolCatalog.map((t) => t.id)).toEqual([...productStatus.plannedTools]);
  });

  it("catalog label records are keyed exactly by the canonical i18n locales", () => {
    for (const tool of toolCatalog) {
      expect(Object.keys(tool.hrefs).sort()).toEqual([...locales].sort());
      expect(Object.keys(tool.shortLabel).sort()).toEqual([...locales].sort());
      expect(Object.keys(tool.fullLabel).sort()).toEqual([...locales].sort());
      expect(Object.keys(tool.localizedLabels).sort()).toEqual([...locales].sort());
    }
  });

  it("catalog href records satisfy the canonical i18n Locale key type", () => {
    const first: CatalogTool = toolCatalog[0];
    const hrefs: Record<Locale, string> = first.hrefs;
    expect(hrefs.en).toBe("/en/compress-pdf");
  });
});
