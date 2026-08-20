import type { Locale } from "@/lib/i18n";

export type BlogTopic = "compress-pdf" | "merge-pdf" | "split-pdf" | "jpg-to-pdf" | "pdf-to-jpg";

export interface BlogArticleEntry {
  topic: BlogTopic;
  date: string;
  slugs: Record<Locale, string>;
  titles: Record<Locale, string>;
  descriptions: Record<Locale, string>;
}

export const BLOG_ARTICLES: readonly BlogArticleEntry[] = [
  {
    topic: "compress-pdf",
    date: "2026-08-20",
    slugs: { en: "compress-pdf-guide", es: "guia-comprimir-pdf", id: "panduan-kompres-pdf" },
    titles: {
      en: "How to Compress a PDF: A Complete Guide",
      es: "Cómo comprimir un PDF: guía completa",
      id: "Cara Mengompres PDF: Panduan Lengkap",
    },
    descriptions: {
      en: "Learn how to compress PDF files online without losing quality, using Papyr's free compress tool.",
      es: "Aprende a comprimir archivos PDF en línea sin perder calidad con la herramienta gratuita de Papyr.",
      id: "Pelajari cara mengompres file PDF secara online tanpa kehilangan kualitas, menggunakan alat kompres Papyr yang gratis.",
    },
  },
  {
    topic: "merge-pdf",
    date: "2026-08-20",
    slugs: { en: "merge-pdf-guide", es: "guia-combinar-pdf", id: "panduan-gabungkan-pdf" },
    titles: {
      en: "How to Merge PDFs: Combine Multiple Files Into One",
      es: "Cómo combinar PDFs: une varios archivos en uno",
      id: "Cara Menggabungkan PDF: Satukan Beberapa File Menjadi Satu",
    },
    descriptions: {
      en: "Combine multiple PDF files into one document in your browser — no upload needed — with Papyr's free merge tool.",
      es: "Une varios archivos PDF en un solo documento en tu navegador, sin subir nada, con la herramienta gratuita de Papyr.",
      id: "Satukan beberapa file PDF menjadi satu dokumen di browser Anda — tanpa perlu upload — dengan alat gabung Papyr yang gratis.",
    },
  },
  {
    topic: "split-pdf",
    date: "2026-08-20",
    slugs: { en: "split-pdf-guide", es: "guia-dividir-pdf", id: "panduan-pisahkan-pdf" },
    titles: {
      en: "How to Split a PDF: Extract Pages You Need",
      es: "Cómo dividir un PDF: extrae las páginas que necesitas",
      id: "Cara Memisahkan PDF: Ekstrak Halaman yang Anda Butuhkan",
    },
    descriptions: {
      en: "Extract selected pages or custom ranges from a PDF entirely in your browser with Papyr's free split tool.",
      es: "Extrae páginas seleccionadas o intervalos personalizados de un PDF, todo en tu navegador, con la herramienta gratuita de Papyr.",
      id: "Ekstrak halaman tertentu atau rentang kustom dari PDF sepenuhnya di browser Anda dengan alat pisah Papyr yang gratis.",
    },
  },
  {
    topic: "jpg-to-pdf",
    date: "2026-08-20",
    slugs: { en: "jpg-to-pdf-guide", es: "guia-jpg-a-pdf", id: "panduan-gambar-ke-pdf" },
    titles: {
      en: "How to Convert JPG to PDF: Images to a Single Document",
      es: "Cómo convertir JPG a PDF: imágenes en un solo documento",
      id: "Cara Mengubah JPG ke PDF: Gambar Menjadi Satu Dokumen",
    },
    descriptions: {
      en: "Turn one or more JPG images into a single PDF with automatic page fitting, using Papyr's free converter.",
      es: "Convierte una o varias imágenes JPG en un solo PDF con ajuste automático de página, usando el convertidor gratuito de Papyr.",
      id: "Ubah satu atau lebih gambar JPG menjadi satu PDF dengan penyesuaian halaman otomatis, menggunakan konverter Papyr yang gratis.",
    },
  },
  {
    topic: "pdf-to-jpg",
    date: "2026-08-20",
    slugs: { en: "pdf-to-jpg-guide", es: "guia-pdf-a-jpg", id: "panduan-pdf-ke-gambar" },
    titles: {
      en: "How to Convert PDF to JPG: Pages to High-Quality Images",
      es: "Cómo convertir PDF a JPG: páginas a imágenes de alta calidad",
      id: "Cara Mengubah PDF ke JPG: Halaman Menjadi Gambar Berkualitas Tinggi",
    },
    descriptions: {
      en: "Convert every page of your PDF into a high-quality JPG image with Papyr's free converter.",
      es: "Convierte cada página de tu PDF en una imagen JPG de alta calidad con el convertidor gratuito de Papyr.",
      id: "Ubah setiap halaman PDF Anda menjadi gambar JPG berkualitas tinggi dengan konverter Papyr yang gratis.",
    },
  },
];
