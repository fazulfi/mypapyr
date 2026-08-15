import type { Locale } from "./i18n";
import type { LegacyToolId, ToolId } from "./tool-ids";

export type CatalogToolId = ToolId | LegacyToolId;
// Canonical SH-04 catalog, grounded in the owner-approved R-15 slug table
// (read-only at f4b792c) and canonical product UX §8.2/§12 EN identities.
// Copy flag: no canonical Spanish display-label string exists; ES labels are
// the display forms matching the owner-approved Spanish slugs verbatim.
// Descriptions are the product spec §4 Purpose lines verbatim; icons are
// Lucide-compatible stroke identifiers per Brand Guidelines §8.4/§8.5.
export type ToolLocalizedLabels = Record<Locale, string>;

export type ToolIconName =
  | "archive"
  | "files"
  | "scissors"
  | "file-image"
  | "image"
  | "rotate"
  | "lock"
  | "unlock"
  | "watermark"
  | "sign"
  | "file-text"
  | "scan"
  | "table";

export interface CatalogTool {
  id: CatalogToolId;
  hrefs: ToolLocalizedLabels;
  shortLabel: ToolLocalizedLabels;
  fullLabel: ToolLocalizedLabels;
  localizedLabels: ToolLocalizedLabels;
  description: string;
  icon: ToolIconName;
  /** True for deferred legacy tools served a localized 410 (DEC-194). */
  legacy?: boolean;
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

// T3/DEC-194: the eight deferred legacy tools are catalogued so navigation and
// link surfaces can render them, but every entry is flagged `legacy: true` and
// links to the localized 410 route; they are never part of the active catalog.
export const legacyCatalog: readonly CatalogTool[] = [
  {
    id: "rotate",
    hrefs: {
      en: "/en/tool-unavailable?tool=rotate",
      es: "/es/tool-unavailable?tool=rotate",
      id: "/id/tool-unavailable?tool=rotate",
    },
    shortLabel: { en: "Rotate PDF", es: "Rotar PDF", id: "Putar PDF" },
    fullLabel: { en: "Rotate PDF", es: "Rotar PDF", id: "Putar PDF" },
    localizedLabels: { en: "Rotate PDF", es: "Rotar PDF", id: "Putar PDF" },
    description: "Rotate PDF pages to the orientation you need.",
    icon: "rotate",
    legacy: true,
  },
  {
    id: "protect",
    hrefs: {
      en: "/en/tool-unavailable?tool=protect",
      es: "/es/tool-unavailable?tool=protect",
      id: "/id/tool-unavailable?tool=protect",
    },
    shortLabel: { en: "Protect PDF", es: "Proteger PDF", id: "Proteksi PDF" },
    fullLabel: { en: "Protect PDF", es: "Proteger PDF", id: "Proteksi PDF" },
    localizedLabels: { en: "Protect PDF", es: "Proteger PDF", id: "Proteksi PDF" },
    description: "Protect a PDF with a strong password.",
    icon: "lock",
    legacy: true,
  },
  {
    id: "unlock",
    hrefs: {
      en: "/en/tool-unavailable?tool=unlock",
      es: "/es/tool-unavailable?tool=unlock",
      id: "/id/tool-unavailable?tool=unlock",
    },
    shortLabel: { en: "Unlock PDF", es: "Desbloquear PDF", id: "Hapus Password" },
    fullLabel: { en: "Unlock PDF", es: "Desbloquear PDF", id: "Hapus Password" },
    localizedLabels: { en: "Unlock PDF", es: "Desbloquear PDF", id: "Hapus Password" },
    description: "Remove password protection from a PDF you own.",
    icon: "unlock",
    legacy: true,
  },
  {
    id: "watermark",
    hrefs: {
      en: "/en/tool-unavailable?tool=watermark",
      es: "/es/tool-unavailable?tool=watermark",
      id: "/id/tool-unavailable?tool=watermark",
    },
    shortLabel: { en: "Watermark", es: "Marca de agua", id: "Watermark" },
    fullLabel: { en: "Watermark PDF", es: "Marca de agua PDF", id: "Tambah Watermark" },
    localizedLabels: { en: "Watermark PDF", es: "Marca de agua PDF", id: "Tambah Watermark" },
    description: "Add a text or image watermark to each page of a PDF.",
    icon: "watermark",
    legacy: true,
  },
  {
    id: "sign",
    hrefs: {
      en: "/en/tool-unavailable?tool=sign",
      es: "/es/tool-unavailable?tool=sign",
      id: "/id/tool-unavailable?tool=sign",
    },
    shortLabel: { en: "Sign PDF", es: "Firmar PDF", id: "Tanda Tangan" },
    fullLabel: { en: "Sign PDF", es: "Firmar PDF", id: "Tanda Tangan PDF" },
    localizedLabels: { en: "Sign PDF", es: "Firmar PDF", id: "Tanda Tangan PDF" },
    description: "Add your digital signature to a PDF directly in your browser.",
    icon: "sign",
    legacy: true,
  },
  {
    id: "pdf-to-word",
    hrefs: {
      en: "/en/tool-unavailable?tool=pdf-to-word",
      es: "/es/tool-unavailable?tool=pdf-to-word",
      id: "/id/tool-unavailable?tool=pdf-to-word",
    },
    shortLabel: { en: "PDF to Word", es: "PDF a Word", id: "PDF ke Word" },
    fullLabel: { en: "PDF to Word", es: "PDF a Word", id: "PDF ke Word" },
    localizedLabels: { en: "PDF to Word", es: "PDF a Word", id: "PDF ke Word" },
    description: "Convert a PDF into an editable Word (.docx) document.",
    icon: "file-text",
    legacy: true,
  },
  {
    id: "ocr",
    hrefs: {
      en: "/en/tool-unavailable?tool=ocr",
      es: "/es/tool-unavailable?tool=ocr",
      id: "/id/tool-unavailable?tool=ocr",
    },
    shortLabel: { en: "OCR PDF", es: "OCR PDF", id: "OCR PDF" },
    fullLabel: { en: "OCR PDF", es: "OCR PDF", id: "OCR PDF" },
    localizedLabels: { en: "OCR PDF", es: "OCR PDF", id: "OCR PDF" },
    description: "Turn scanned PDFs into searchable, selectable text.",
    icon: "scan",
    legacy: true,
  },
  {
    id: "pdf-to-excel",
    hrefs: {
      en: "/en/tool-unavailable?tool=pdf-to-excel",
      es: "/es/tool-unavailable?tool=pdf-to-excel",
      id: "/id/tool-unavailable?tool=pdf-to-excel",
    },
    shortLabel: { en: "PDF to Excel", es: "PDF a Excel", id: "PDF ke Excel" },
    fullLabel: { en: "PDF to Excel", es: "PDF a Excel", id: "PDF ke Excel" },
    localizedLabels: { en: "PDF to Excel", es: "PDF a Excel", id: "PDF ke Excel" },
    description: "Extract tables from a PDF into a spreadsheet (.xlsx).",
    icon: "table",
    legacy: true,
  },
];

export function getLegacyTools(): readonly CatalogTool[] {
  return legacyCatalog;
}

export function getAllTools(): readonly CatalogTool[] {
  return toolCatalog;
}

export function getToolById(id: string): CatalogTool | undefined {
  return toolCatalog.find((tool) => tool.id === id);
}

export function getToolHrefs(id: string): ToolLocalizedLabels | undefined {
  return getToolById(id)?.hrefs;
}
