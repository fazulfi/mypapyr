import type { Locale } from "./i18n";
import type { ToolId } from "./tool-ids";

// Canonical SH-04 catalog, grounded in the owner-approved R-15 slug table
// (read-only at f4b792c) and canonical product UX §8.2/§12 EN identities.
// Copy flag: no canonical Spanish display-label string exists; ES labels are
// the display forms matching the owner-approved Spanish slugs verbatim.
// Descriptions are the product spec §4 Purpose lines verbatim; icons are
// Lucide-compatible stroke identifiers per Brand Guidelines §8.4/§8.5.
export type ToolLocalizedLabels = Record<Locale, string>;

export type ToolIconName = "archive" | "files" | "scissors" | "file-image" | "image";

export interface CatalogTool {
  id: ToolId;
  hrefs: ToolLocalizedLabels;
  shortLabel: ToolLocalizedLabels;
  fullLabel: ToolLocalizedLabels;
  localizedLabels: ToolLocalizedLabels;
  description: string;
  icon: ToolIconName;
}

export const toolCatalog: readonly CatalogTool[] = [
  {
    id: "compress-pdf",
    hrefs: { en: "/en/compress-pdf", es: "/es/comprimir-pdf", id: "/id/kompres-pdf" },
    shortLabel: { en: "Compress PDF", es: "Comprimir PDF", id: "Kompres PDF" },
    fullLabel: { en: "Compress PDF", es: "Comprimir PDF", id: "Kompres PDF" },
    localizedLabels: { en: "Compress PDF", es: "Comprimir PDF", id: "Kompres PDF" },
    description:
      "Reduce PDF file size while preserving crisp on-screen quality, using one automatic high-quality profile.",
    icon: "archive",
  },
  {
    id: "merge-pdf",
    hrefs: { en: "/en/merge-pdf", es: "/es/combinar-pdf", id: "/id/gabungkan-pdf" },
    shortLabel: { en: "Merge PDF", es: "Combinar PDF", id: "Gabungkan PDF" },
    fullLabel: { en: "Merge PDF", es: "Combinar PDF", id: "Gabungkan PDF" },
    localizedLabels: { en: "Merge PDF", es: "Combinar PDF", id: "Gabungkan PDF" },
    description:
      "Combine multiple PDFs into one file in the user's chosen order, with controls at the file level.",
    icon: "files",
  },
  {
    id: "split-pdf",
    hrefs: { en: "/en/split-pdf", es: "/es/dividir-pdf", id: "/id/pisahkan-pdf" },
    shortLabel: { en: "Split PDF", es: "Dividir PDF", id: "Pisahkan PDF" },
    fullLabel: { en: "Split PDF", es: "Dividir PDF", id: "Pisahkan PDF" },
    localizedLabels: { en: "Split PDF", es: "Dividir PDF", id: "Pisahkan PDF" },
    description:
      "Extract selected pages as separate PDFs using custom page ranges or one PDF per page.",
    icon: "scissors",
  },
  {
    id: "jpg-to-pdf",
    hrefs: { en: "/en/jpg-to-pdf", es: "/es/jpg-a-pdf", id: "/id/gambar-ke-pdf" },
    shortLabel: { en: "JPG to PDF", es: "JPG a PDF", id: "Gambar ke PDF" },
    fullLabel: { en: "JPG to PDF", es: "JPG a PDF", id: "Gambar ke PDF" },
    localizedLabels: { en: "JPG to PDF", es: "JPG a PDF", id: "Gambar ke PDF" },
    description: "Convert images into a single PDF with automatic, safe fitting.",
    icon: "file-image",
  },
  {
    id: "pdf-to-jpg",
    hrefs: { en: "/en/pdf-to-jpg", es: "/es/pdf-a-jpg", id: "/id/pdf-ke-gambar" },
    shortLabel: { en: "PDF to JPG", es: "PDF a JPG", id: "PDF ke Gambar" },
    fullLabel: { en: "PDF to JPG", es: "PDF a JPG", id: "PDF ke Gambar" },
    localizedLabels: { en: "PDF to JPG", es: "PDF a JPG", id: "PDF ke Gambar" },
    description: "Convert PDF pages to high-quality JPG images with one automatic output profile.",
    icon: "image",
  },
];

export function getAllTools(): readonly CatalogTool[] {
  return toolCatalog;
}

export function getToolById(id: string): CatalogTool | undefined {
  return toolCatalog.find((tool) => tool.id === id);
}

export function getToolHrefs(id: string): ToolLocalizedLabels | undefined {
  return getToolById(id)?.hrefs;
}
