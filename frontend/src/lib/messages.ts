import type { Locale } from "./i18n";

export const messages = {
  en: {
    siteName: "Papyr",
    nav: {
      home: "Home",
      tools: "Tools",
      basic: "Basic",
      conversion: "Conversion",
      menu: "Menu",
      menuClose: "Close menu",
      cta: "Get started",
    },
    states: {
      queued: "Waiting in queue",
      preparing: "Preparing your file",
      processing: "Processing your file",
      done: "Done",
      error: "Something went wrong",
      download: "Download",
    },
    uploader: {
      browse: "Browse files",
      drop: "Drop your files here or",
    },
    reset: {
      processAnother: "Process another file",
    },
    languages: { en: "English", es: "Español", id: "Bahasa Indonesia" },
    home: {
      description: "Papyr PDF tools.",
      hero: "PDF tools, free and simple",
      heroSub: "Compress, merge, split, and convert PDFs. No account needed.",
      toolsHeading: "Tools",
      tools: {
        compress: "Compress PDF",
        merge: "Merge PDF",
        split: "Split PDF",
        jpgToPdf: "JPG to PDF",
        pdfToJpg: "PDF to JPG",
      },
      privacy: "Your files stay yours",
      privacyDesc:
        "No account required. Files processed in your browser never leave your device. Server-processed files are deleted within one hour of upload.",
      howItWorks: "How it works",
      howItWorksSteps: ["Choose a tool", "Upload your file", "Get your result"],
      faq: "Frequently asked questions",
      faqItems: [
        {
          question: "Is Papyr free?",
          answer: "Yes, all five tools are free to use.",
        },
        {
          question: "Do I need an account?",
          answer: "No account is required to use any tool.",
        },
        {
          question: "How long are my files kept?",
          answer:
            "Server-processed files are automatically deleted within one hour of upload. Files processed in your browser never leave your device.",
        },
      ],
    },
    pages: {
      privacy: {
        title: "Privacy",
        description:
          "This page is an informational shell that provides general information about privacy on Papyr. The complete privacy content will be published in a later phase.",
      },
      terms: {
        title: "Terms of Service",
        description:
          "This page is an informational shell that provides general information about the terms that govern Papyr. The complete terms content will be published in a later phase.",
      },
      cookiesAdvertising: {
        title: "Cookies & Advertising",
        description:
          "This page is an informational shell that provides general information about cookies and advertising on Papyr. The complete cookies and advertising content will be published in a later phase.",
      },
      contact: {
        title: "Contact",
        description:
          "This page is an informational shell that provides general information about how to contact Papyr. Contact functionality will be published in a later phase.",
      },
      status: {
        title: "Status",
        description:
          "This page is an informational shell that provides general information about the availability of Papyr services. Status monitoring will be published in a later phase.",
      },
      roadmap: {
        title: "Roadmap",
        description:
          "This page is an informational shell that provides general information about the Papyr roadmap. The complete roadmap content will be published in a later phase.",
      },
      blog: {
        title: "Blog",
        description:
          "This page is an informational shell that provides general information about the Papyr blog. Blog articles will be published in a later phase.",
      },
    },
    footer: {
      tools: "Tools",
      support: "Support",
      copyright: "Papyr. Free PDF tools.",
      privacy: "Privacy",
      terms: "Terms of Service",
      cookiesAdvertising: "Cookies & Advertising",
      contact: "Contact",
      status: "Status",
      roadmap: "Roadmap",
      blog: "Blog",
    },
    a11y: {
      skipToContent: "Skip to main content",
      languageSwitcher: "Language",
      navToggle: "Open navigation",
      navClose: "Close navigation",
    },
    metadata: {
      title: "Papyr — PDF tools",
      description: "Papyr provides PDF tools to merge, split, compress, and convert PDF documents.",
    },
    notFound: {
      title: "Page not found",
      description: "The page you are looking for does not exist.",
    },
    tools: {
      compress: {
        title: "Compress PDF",
        description: "Reduce the file size of your PDF while keeping quality. Processed on our servers and deleted within one hour.",
        errors: {
          fileTooLarge: "File exceeds the maximum size limit.",
          uploadFailed: "Upload failed, please try again.",
        },
        actions: {
          compress: "Compress",
          uploading: "Uploading...",
        },
        status: {
          submitting: "Submitting...",
        },
      },
      merge: {
        title: "Merge PDF",
        description: "Combine multiple PDFs into one document.",
        errors: { uploadFailed: "Upload failed" },
        actions: { merge: "Merge PDFs" },
        status: { submitting: "Merging..." },
      },
      split: {
        title: "Split PDF",
        description: "Extract pages from a PDF document.",
        errors: { splittingFailed: "Error while splitting", uploadFailed: "Upload failed" },
        actions: { start: "Start Splitting", uploading: "Uploading..." },
        status: { processing: "Processing" },
      },
    },
  },
  es: {
    siteName: "Papyr",
    nav: {
      home: "Inicio",
      tools: "Herramientas",
      basic: "Básicas",
      conversion: "Conversión",
      menu: "Menú",
      menuClose: "Cerrar menú",
      cta: "Comenzar",
    },
    states: {
      queued: "En cola",
      preparing: "Preparando tu archivo",
      processing: "Procesando tu archivo",
      done: "Listo",
      error: "Algo salió mal",
      download: "Descargar",
    },
    uploader: {
      browse: "Elegir archivos",
      drop: "Arrastra tus archivos aquí o",
    },
    reset: {
      processAnother: "Procesar otro archivo",
    },
    languages: { en: "English", es: "Español", id: "Bahasa Indonesia" },
    home: {
      description: "Herramientas PDF de Papyr.",
      hero: "Herramientas PDF, gratis y simples",
      heroSub: "Comprime, combina, divide y convierte PDFs. Sin necesidad de cuenta.",
      toolsHeading: "Herramientas",
      tools: {
        compress: "Comprimir PDF",
        merge: "Combinar PDF",
        split: "Dividir PDF",
        jpgToPdf: "JPG a PDF",
        pdfToJpg: "PDF a JPG",
      },
      privacy: "Tus archivos son tuyos",
      privacyDesc:
        "No se requiere cuenta. Los archivos procesados en tu navegador nunca salen de tu dispositivo. Los archivos procesados en el servidor se eliminan en un plazo máximo de una hora tras la subida.",
      howItWorks: "Cómo funciona",
      howItWorksSteps: ["Elige una herramienta", "Sube tu archivo", "Obtén tu resultado"],
      faq: "Preguntas frecuentes",
      faqItems: [
        {
          question: "¿Papyr es gratis?",
          answer: "Sí, las cinco herramientas son gratuitas.",
        },
        {
          question: "¿Necesito una cuenta?",
          answer: "No se necesita cuenta para usar ninguna herramienta.",
        },
        {
          question: "¿Cuánto tiempo se guardan mis archivos?",
          answer:
            "Los archivos procesados en el servidor se eliminan automáticamente en un plazo máximo de una hora tras la subida. Los archivos procesados en tu navegador nunca salen de tu dispositivo.",
        },
      ],
    },
    pages: {
      privacy: {
        title: "Privacidad",
        description:
          "Esta página es un marco informativo que ofrece información general sobre la privacidad en Papyr. El contenido completo de privacidad se publicará en una fase posterior.",
      },
      terms: {
        title: "Términos de servicio",
        description:
          "Esta página es un marco informativo que ofrece información general sobre los términos que rigen Papyr. El contenido completo de los términos se publicará en una fase posterior.",
      },
      cookiesAdvertising: {
        title: "Cookies y publicidad",
        description:
          "Esta página es un marco informativo que ofrece información general sobre las cookies y la publicidad en Papyr. El contenido completo sobre cookies y publicidad se publicará en una fase posterior.",
      },
      contact: {
        title: "Contacto",
        description:
          "Esta página es un marco informativo que ofrece información general sobre cómo contactar con Papyr. La funcionalidad de contacto se publicará en una fase posterior.",
      },
      status: {
        title: "Estado",
        description:
          "Esta página es un marco informativo que ofrece información general sobre la disponibilidad de los servicios de Papyr. La supervisión de estado se publicará en una fase posterior.",
      },
      roadmap: {
        title: "Hoja de ruta",
        description:
          "Esta página es un marco informativo que ofrece información general sobre la hoja de ruta de Papyr. El contenido completo de la hoja de ruta se publicará en una fase posterior.",
      },
      blog: {
        title: "Blog",
        description:
          "Esta página es un marco informativo que ofrece información general sobre el blog de Papyr. Los artículos del blog se publicarán en una fase posterior.",
      },
    },
    footer: {
      tools: "Herramientas",
      support: "Soporte",
      copyright: "Papyr. Herramientas PDF gratuitas.",
      privacy: "Privacidad",
      terms: "Términos de servicio",
      cookiesAdvertising: "Cookies y publicidad",
      contact: "Contacto",
      status: "Estado",
      roadmap: "Hoja de ruta",
      blog: "Blog Papyr",
    },
    a11y: {
      skipToContent: "Saltar al contenido principal",
      languageSwitcher: "Idioma",
      navToggle: "Abrir navegación",
      navClose: "Cerrar navegación",
    },
    metadata: {
      title: "Papyr — Herramientas PDF",
      description:
        "Papyr ofrece herramientas PDF para combinar, dividir, comprimir y convertir documentos PDF.",
    },
    notFound: {
      title: "Página no encontrada",
      description: "La página que buscas no existe.",
    },
    tools: {
      compress: {
        title: "Comprimir PDF",
        description: "Reduce el tamaño de tu PDF manteniendo la calidad. Se procesa en nuestros servidores y se elimina en una hora.",
        errors: {
          fileTooLarge: "El archivo supera el límite de tamaño máximo.",
          uploadFailed: "Error al subir, inténtalo de nuevo.",
        },
        actions: {
          compress: "Comprimir",
          uploading: "Subiendo...",
        },
        status: {
          submitting: "Enviando...",
        },
      },
    },
  },
  id: {
    siteName: "Papyr",
    nav: {
      home: "Beranda",
      tools: "Alat",
      basic: "Dasar",
      conversion: "Konversi",
      menu: "Menu navigasi",
      menuClose: "Tutup menu",
      cta: "Mulai",
    },
    states: {
      queued: "Menunggu dalam antrean",
      preparing: "Menyiapkan file Anda",
      processing: "Memproses file Anda",
      done: "Selesai",
      error: "Terjadi kesalahan",
      download: "Unduh",
    },
    uploader: {
      browse: "Pilih file",
      drop: "Seret file Anda ke sini atau",
    },
    reset: {
      processAnother: "Proses file lain",
    },
    languages: { en: "English", es: "Español", id: "Bahasa Indonesia" },
    home: {
      description: "Alat PDF Papyr.",
      hero: "Alat PDF, gratis dan sederhana",
      heroSub: "Kompres, gabung, pisah, dan konversi PDF. Tanpa perlu akun.",
      toolsHeading: "Alat",
      tools: {
        compress: "Kompres PDF",
        merge: "Gabung PDF",
        split: "Pisah PDF",
        jpgToPdf: "JPG ke PDF",
        pdfToJpg: "PDF ke JPG",
      },
      privacy: "File Anda tetap milik Anda",
      privacyDesc:
        "Tidak perlu akun. File yang diproses di browser tidak pernah meninggalkan perangkat Anda. File yang diproses di server dihapus dalam waktu satu jam setelah diunggah.",
      howItWorks: "Cara kerja",
      howItWorksSteps: ["Pilih alat", "Unggah file Anda", "Dapatkan hasil"],
      faq: "Pertanyaan umum",
      faqItems: [
        {
          question: "Apakah Papyr gratis?",
          answer: "Ya, kelima alat tersedia gratis.",
        },
        {
          question: "Apakah saya perlu akun?",
          answer: "Tidak perlu akun untuk menggunakan alat apa pun.",
        },
        {
          question: "Berapa lama file saya disimpan?",
          answer:
            "File yang diproses di server otomatis dihapus dalam waktu satu jam setelah diunggah. File yang diproses di browser tidak pernah meninggalkan perangkat Anda.",
        },
      ],
    },
    pages: {
      privacy: {
        title: "Privasi",
        description:
          "Halaman ini adalah kerangka informasi yang memberikan informasi umum tentang privasi di Papyr. Konten privasi lengkap akan diterbitkan pada fase berikutnya.",
      },
      terms: {
        title: "Ketentuan Layanan",
        description:
          "Halaman ini adalah kerangka informasi yang memberikan informasi umum tentang ketentuan yang mengatur Papyr. Konten ketentuan lengkap akan diterbitkan pada fase berikutnya.",
      },
      cookiesAdvertising: {
        title: "Cookie dan Iklan",
        description:
          "Halaman ini adalah kerangka informasi yang memberikan informasi umum tentang cookie dan iklan di Papyr. Konten lengkap tentang cookie dan iklan akan diterbitkan pada fase berikutnya.",
      },
      contact: {
        title: "Kontak",
        description:
          "Halaman ini adalah kerangka informasi yang memberikan informasi umum tentang cara menghubungi Papyr. Fungsionalitas kontak akan diterbitkan pada fase berikutnya.",
      },
      status: {
        title: "Status",
        description:
          "Halaman ini adalah kerangka informasi yang memberikan informasi umum tentang ketersediaan layanan Papyr. Pemantauan status akan diterbitkan pada fase berikutnya.",
      },
      roadmap: {
        title: "Peta Jalan",
        description:
          "Halaman ini adalah kerangka informasi yang memberikan informasi umum tentang peta jalan Papyr. Konten peta jalan lengkap akan diterbitkan pada fase berikutnya.",
      },
      blog: {
        title: "Blog",
        description:
          "Halaman ini adalah kerangka informasi yang memberikan informasi umum tentang blog Papyr. Artikel blog akan diterbitkan pada fase berikutnya.",
      },
    },
    footer: {
      tools: "Alat",
      support: "Dukungan",
      copyright: "Papyr. Alat PDF gratis.",
      privacy: "Privasi",
      terms: "Ketentuan Layanan",
      cookiesAdvertising: "Cookie dan Iklan",
      contact: "Kontak",
      status: "Status layanan",
      roadmap: "Peta Jalan",
      blog: "Blog Papyr",
    },
    a11y: {
      skipToContent: "Lewati ke konten utama",
      languageSwitcher: "Bahasa",
      navToggle: "Buka navigasi",
      navClose: "Tutup navigasi",
    },
    metadata: {
      title: "Papyr — Alat PDF",
      description:
        "Papyr menyediakan alat PDF untuk menggabungkan, memisahkan, mengompres, dan mengonversi dokumen PDF.",
    },
    notFound: {
      title: "Halaman tidak ditemukan",
      description: "Halaman yang Anda cari tidak ada.",
    },
    tools: {
      compress: {
        title: "Kompres PDF",
        description: "Kurangi ukuran PDF Anda dengan tetap menjaga kualitas. Diproses di server kami dan dihapus dalam satu jam.",
        errors: {
          fileTooLarge: "File melebihi batas ukuran maksimum.",
          uploadFailed: "Gagal mengunggah, silakan coba lagi.",
        },
        actions: {
          compress: "Kompres",
          uploading: "Mengunggah...",
        },
        status: {
          submitting: "Mengirim...",
        },
      },
    },
  },
} as const;

export type Messages = (typeof messages)[Locale];

export function getMessages(locale: Locale): Messages {
  return messages[locale];
}
