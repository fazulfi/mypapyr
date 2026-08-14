import type { Locale } from "./i18n";

export const messages = {
  en: {
    siteName: "Papyr",
    nav: {
      home: "Home",
      tools: "Tools",
      basic: "Basic",
      conversion: "Conversion",
      security: "Security",
      enhancement: "Enhancement",
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
      heroPill: "Free · No account · Auto-delete",
      heroLine1: "PDF tools that",
      heroLine2: "just work.",
      hero: "PDF tools, free and simple",
      heroSub: "Compress, merge, split, and convert PDFs. No account needed.",
      toolsHeading: "Tools",
      trustBadges: ["No account", "Auto-delete in 1 hour", "Works on your phone"],
      toolsEyebrow: "All tools",
      cardCta: "Use tool",
      tools: {
        compress: "Compress PDF",
        merge: "Merge PDF",
        split: "Split PDF",
        jpgToPdf: "JPG to PDF",
        pdfToJpg: "PDF to JPG",
      },
      privacy: "Your files stay yours",
      privacyEyebrow: "Privacy first",
      privacyCards: [
        {
          title: "Secure transfer",
          desc: "Files are transmitted over HTTPS and processed securely.",
        },
        {
          title: "Deleted in 1 hour",
          desc: "Every uploaded file is permanently deleted within 60 minutes, no exceptions.",
        },
        {
          title: "No storage",
          desc: "We never read, analyze, or store your documents. Ever.",
        },
      ],
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
        description:
          "Reduce the file size of your PDF while keeping quality. Processed on our servers and deleted within one hour.",
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
        description: "Combine multiple PDFs into one document. All files stay in your browser.",
        errors: {
          fileTooLarge: "File too large (max 200MB combined)",
          needAtLeastTwo: "Select at least 2 files",
          uploadFailed: "Upload failed",
          downloadFailed: "Download failed",
        },
        actions: { merge: "Merge PDFs", uploading: "Merging..." },
        status: { submitting: "Merging..." },
      },
      split: {
        title: "Split PDF",
        description: "Extract pages from a PDF document.",
        ranges: {
          label: "Page ranges (optional)",
          help: "Example: 1-3,5,8-10 — separate entries with commas. Leave empty to create one PDF per page.",
          defaultNote:
            "No ranges entered: one output per source page. The exact page count is checked after upload.",
          previewHeading: "Output preview",
          previewItemSingle: "Output {index}: page {pages}",
          previewItemRange: "Output {index}: pages {pages}",
          errors: {
            malformed:
              "Invalid range format. Use page numbers and ranges like 1-3,5,8-10, separated by commas and without spaces inside a range.",
            reversed:
              "Each range must ascend: the second number cannot be smaller than the first (write 3-7, not 7-3).",
            zero: "Page numbers start at 1, so zero is not allowed.",
            tooManyOutputs:
              "Too many outputs: each entry creates one output and the maximum is 100.",
            tooLong: "The range text is too long: the maximum is 2000 characters.",
            serverRejected:
              "The server rejected these ranges. Every number must match a page that exists in your PDF, the total number of outputs is limited, and encrypted files cannot be split with custom ranges. Adjust the ranges and try again.",
          },
        },
        errors: {
          fileTooLarge: "File too large (max 100MB)",
          uploadFailed: "Upload failed",
          downloadFailed: "Download failed",
        },
        actions: { split: "Split PDF", uploading: "Uploading..." },
        status: { submitting: "Submitting..." },
      },
      jpgToPdf: {
        title: "JPG to PDF",
        description: "Convert your JPG images into a single PDF document.",
        paperNote: "Page size and orientation are chosen automatically to fit each image.",
        metadataNote:
          "Image metadata (EXIF), such as location and timestamps, may remain in the PDF.",
        errors: {
          fileTooLarge: "File too large (max 100MB)",
          uploadFailed: "Upload failed",
          downloadFailed: "Download failed",
        },
        actions: { convert: "Convert to PDF", uploading: "Uploading..." },
        status: { submitting: "Submitting..." },
      },

      pdfToJpg: {
        title: "PDF to JPG",
        description: "Convert your PDF pages into high-quality JPG images.",
        qualityNote: "Every page is rendered at one high-quality output profile.",
        resolutionNote: "Conversion cannot add detail that is missing from low-resolution pages.",
        errors: {
          fileTooLarge: "File too large (max 100MB per page)",
          uploadFailed: "Upload failed",
          downloadFailed: "Download failed",
        },
        actions: { convert: "Convert to JPG", uploading: "Uploading..." },
        status: { submitting: "Submitting..." },
      },
    },
    toolPages: {
      "compress-pdf": {
        features: ["Up to 80% smaller", "Fast processing", "Privacy-first"],
      },
      "merge-pdf": {
        features: ["Combine many files", "Order preserved", "Privacy-first"],
      },
      "split-pdf": {
        features: ["Custom ranges", "One page per file", "Privacy-first"],
      },
      "jpg-to-pdf": {
        features: ["Multi-image", "Auto-fit pages", "Privacy-first"],
      },
      "pdf-to-jpg": {
        features: ["High quality", "Page per image", "Privacy-first"],
      },
    },
    privacyNotice: {
      model: {
        server: "Your files are automatically deleted after 1 hour. We never store your documents.",
        client: "Your files never leave your device. Everything runs in your browser.",
        hybrid:
          "Small files are processed in your browser. Large files are sent to the server and deleted within 1 hour.",
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
      security: "Seguridad",
      enhancement: "Mejoras",
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
      heroPill: "Gratis · Sin cuenta · Auto-eliminación",
      heroLine1: "Herramientas PDF que",
      heroLine2: "funcionan al instante.",
      hero: "Herramientas PDF, gratis y simples",
      heroSub: "Comprime, combina, divide y convierte PDFs. Sin necesidad de cuenta.",
      toolsHeading: "Herramientas",
      trustBadges: ["Sin cuenta", "Auto-eliminación en 1 hora", "Funciona en tu móvil"],
      toolsEyebrow: "Todas las herramientas",
      cardCta: "Usar herramienta",
      tools: {
        compress: "Comprimir PDF",
        merge: "Combinar PDF",
        split: "Dividir PDF",
        jpgToPdf: "JPG a PDF",
        pdfToJpg: "PDF a JPG",
      },
      privacy: "Tus archivos son tuyos",
      privacyEyebrow: "Privacidad primero",
      privacyCards: [
        {
          title: "Transferencia segura",
          desc: "Los archivos se transmiten por HTTPS y se procesan de forma segura.",
        },
        {
          title: "Eliminados en 1 hora",
          desc: "Cada archivo subido se elimina permanentemente en un plazo de 60 minutos, sin excepciones.",
        },
        {
          title: "Sin almacenamiento",
          desc: "Nunca leemos, analizamos ni almacenamos tus documentos. Nunca.",
        },
      ],
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
        description:
          "Reduce el tamaño de tu PDF manteniendo la calidad. Se procesa en nuestros servidores y se elimina en una hora.",
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
      merge: {
        title: "Unir PDF",
        description:
          "Combina varios PDFs en un solo documento. Todos los archivos permanecen en tu navegador.",
        errors: {
          fileTooLarge: "Archivo demasiado grande (máx. 200MB combinados)",
          needAtLeastTwo: "Selecciona al menos 2 archivos",
          uploadFailed: "Error de subida",
          downloadFailed: "Error de descarga",
        },
        actions: { merge: "Unir PDF", uploading: "Subiendo..." },
        status: { submitting: "Enviando..." },
      },
      split: {
        title: "Dividir PDF",
        description: "Extrae páginas de tu PDF y crea un nuevo documento.",
        ranges: {
          label: "Intervalos de páginas (opcional)",
          help: "Ejemplo: 1-3,5,8-10 — separa las entradas con comas. Déjalo vacío para crear un PDF por página.",
          defaultNote:
            "Sin intervalos: se genera una salida por cada página de origen. El número exacto de páginas se comprueba después de subir el archivo.",
          previewHeading: "Vista previa de salidas",
          previewItemSingle: "Salida {index}: página {pages}",
          previewItemRange: "Salida {index}: páginas {pages}",
          errors: {
            malformed:
              "Formato de intervalos no válido. Usa números de página e intervalos como 1-3,5,8-10, separados por comas y sin espacios dentro de un intervalo.",
            reversed:
              "Cada intervalo debe ser ascendente: el segundo número no puede ser menor que el primero (escribe 3-7, no 7-3).",
            zero: "Los números de página empiezan en 1, por lo que el cero no está permitido.",
            tooManyOutputs: "Demasiadas salidas: cada entrada crea una salida y el máximo es 100.",
            tooLong: "El texto de intervalos es demasiado largo: el máximo es 2000 caracteres.",
            serverRejected:
              "El servidor rechazó estos intervalos. Cada número debe corresponder a una página existente de tu PDF, el número total de salidas está limitado y los archivos cifrados no pueden dividirse con intervalos personalizados. Ajusta los intervalos e inténtalo de nuevo.",
          },
        },

        errors: {
          fileTooLarge: "Archivo demasiado grande (máx. 100MB)",
          uploadFailed: "Error de subida",
          downloadFailed: "Error de descarga",
        },
        actions: { split: "Dividir PDF", uploading: "Subiendo..." },
        status: { submitting: "Enviando..." },
      },
      jpgToPdf: {
        title: "JPG a PDF",
        description: "Convierte tus imágenes JPG en un solo documento PDF.",
        paperNote:
          "El tamaño y la orientación de la página se eligen automáticamente para cada imagen.",
        metadataNote:
          "Los metadatos de la imagen (EXIF), como la ubicación y las marcas de tiempo, pueden permanecer en el PDF.",
        errors: {
          fileTooLarge: "Archivo demasiado grande (máx. 100MB)",
          uploadFailed: "Error de subida",
          downloadFailed: "Error de descarga",
        },
        actions: { convert: "Convertir a PDF", uploading: "Subiendo..." },

        status: { submitting: "Enviando..." },
      },
      pdfToJpg: {

        title: "PDF a JPG",
        description: "Convierte las páginas de tu PDF en imágenes JPG de alta calidad.",
        qualityNote: "Cada página se renderiza con un único perfil de salida de alta calidad.",
        resolutionNote:
          "La conversión no puede añadir detalle que falte en páginas de baja resolución.",
        errors: {
          fileTooLarge: "Archivo demasiado grande (máx. 16MP por página)",
          uploadFailed: "Error de subida",

          downloadFailed: "Error de descarga",
        },
        actions: { convert: "Convertir a JPG", uploading: "Subiendo..." },
        status: { submitting: "Enviando..." },
      },
    },
    toolPages: {
      "compress-pdf": {
        features: ["Hasta 80% más pequeño", "Procesamiento rápido", "Privacidad primero"],
      },
      "merge-pdf": {
        features: ["Combina muchos archivos", "Orden preservado", "Privacidad primero"],
      },
      "split-pdf": {
        features: ["Intervalos personalizados", "Una página por archivo", "Privacidad primero"],
      },
      "jpg-to-pdf": {
        features: ["Multi-imagen", "Ajuste automático de páginas", "Privacidad primero"],
      },
      "pdf-to-jpg": {
        features: ["Alta calidad", "Una imagen por página", "Privacidad primero"],
      },
    },
    privacyNotice: {
      model: {
        server: "Tus archivos se eliminan automáticamente después de 1 hora. Nunca guardamos tus documentos.",
        client: "Tus archivos nunca salen de tu dispositivo. Todo se procesa en tu navegador.",
        hybrid:
          "Los archivos pequeños se procesan en tu navegador. Los archivos grandes se envían al servidor y se eliminan en 1 hora.",
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
      security: "Keamanan",
      enhancement: "Enhancement",
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
      heroPill: "Gratis · Tanpa akun · Auto-hapus",
      heroLine1: "Alat PDF yang",
      heroLine2: "langsung bekerja.",
      hero: "Alat PDF, gratis dan sederhana",
      heroSub: "Kompres, gabung, pisah, dan konversi PDF. Tanpa perlu akun.",
      toolsHeading: "Alat",
      trustBadges: ["Tanpa akun", "Auto-hapus 1 jam", "Bisa di HP"],
      toolsEyebrow: "Semua alat",
      cardCta: "Gunakan alat",
      tools: {
        compress: "Kompres PDF",
        merge: "Gabung PDF",
        split: "Pisah PDF",
        jpgToPdf: "JPG ke PDF",
        pdfToJpg: "PDF ke JPG",
      },
      privacy: "File Anda tetap milik Anda",
      privacyEyebrow: "Privasi utama",
      privacyCards: [
        {
          title: "Transfer aman",
          desc: "File ditransmisikan melalui HTTPS dan diproses secara aman.",
        },
        {
          title: "Dihapus dalam 1 jam",
          desc: "Setiap file yang diunggah dihapus permanen dalam 60 menit, tanpa pengecualian.",
        },
        {
          title: "Tanpa penyimpanan",
          desc: "Kami tidak pernah membaca, menganalisis, atau menyimpan dokumenmu. Selamanya.",
        },
      ],
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
        description:
          "Kurangi ukuran PDF Anda dengan tetap menjaga kualitas. Diproses di server kami dan dihapus dalam satu jam.",
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
      merge: {
        title: "Gabung PDF",
        description:
          "Gabungkan beberapa PDF menjadi satu dokumen. Semua file tetap ada di browser Anda.",
        errors: {
          fileTooLarge: "File terlalu besar (maks. 200MB gabungan)",
          needAtLeastTwo: "Pilih minimal 2 file",
          uploadFailed: "Gagal mengunggah",
          downloadFailed: "Gagal mengunduh",
        },
        actions: { merge: "Gabung PDF", uploading: "Mengunggah..." },
        status: { submitting: "Mengirim..." },
      },
      split: {
        title: "Pisah PDF",
        description: "Ekstrak halaman dari PDF dan buat dokumen baru.",
        ranges: {
          label: "Rentang halaman (opsional)",
          help: "Contoh: 1-3,5,8-10 — pisahkan entri dengan koma. Biarkan kosong untuk membuat satu PDF per halaman.",
          defaultNote:
            "Tanpa rentang: satu output untuk setiap halaman sumber. Jumlah halaman yang pasti diperiksa setelah unggah.",
          previewHeading: "Pratinjau output",
          previewItemSingle: "Output {index}: halaman {pages}",
          previewItemRange: "Output {index}: halaman {pages}",
          errors: {
            malformed:
              "Format rentang tidak valid. Gunakan nomor halaman dan rentang seperti 1-3,5,8-10, dipisahkan dengan koma dan tanpa spasi di dalam rentang.",
            reversed:
              "Setiap rentang harus menaik: angka kedua tidak boleh lebih kecil dari angka pertama (tulis 3-7, bukan 7-3).",
            zero: "Nomor halaman dimulai dari 1, jadi nol tidak diperbolehkan.",
            tooManyOutputs:
              "Terlalu banyak output: setiap entri membuat satu output dan maksimumnya adalah 100.",
            tooLong: "Teks rentang terlalu panjang: maksimum 2000 karakter.",
            serverRejected:
              "Server menolak rentang ini. Setiap nomor harus sesuai dengan halaman yang ada di PDF Anda, jumlah total output dibatasi, dan file terenkripsi tidak dapat dipisahkan dengan rentang kustom. Sesuaikan rentang lalu coba lagi.",
          },
        },
        errors: {
          fileTooLarge: "File terlalu besar (maks. 100MB)",
          uploadFailed: "Gagal mengunggah",
          downloadFailed: "Gagal mengunduh",
        },
        actions: { split: "Pisah PDF", uploading: "Mengunggah..." },
        status: { submitting: "Mengirim..." },
      },
      jpgToPdf: {
        title: "JPG ke PDF",
        description: "Konversi gambar JPG Anda menjadi satu dokumen PDF.",
        paperNote:
          "Ukuran dan orientasi halaman dipilih secara otomatis agar sesuai dengan setiap gambar.",
        metadataNote:
          "Metadata gambar (EXIF), seperti lokasi dan stempel waktu, dapat tetap ada di PDF.",
        errors: {
          fileTooLarge: "File terlalu besar (maks. 100MB)",
          uploadFailed: "Gagal mengunggah",
          downloadFailed: "Gagal mengunduh",
        },
        actions: { convert: "Konversi ke PDF", uploading: "Mengunggah..." },
        status: { submitting: "Mengirim..." },
      },
      pdfToJpg: {
        title: "PDF ke JPG",
        description: "Konversi halaman PDF Anda menjadi gambar JPG berkualitas tinggi.",
        qualityNote: "Setiap halaman dirender dengan satu profil keluaran berkualitas tinggi.",
        resolutionNote:
          "Konversi tidak dapat menambahkan detail yang hilang dari halaman beresolusi rendah.",
        errors: {
          fileTooLarge: "File terlalu besar (maks. 16MP per halaman)",
          uploadFailed: "Gagal mengunggah",
          downloadFailed: "Gagal mengunduh",
        },
        actions: { convert: "Konversi ke JPG", uploading: "Mengunggah..." },
        status: { submitting: "Mengirim..." },
      },
    },
    toolPages: {
      "compress-pdf": {
        features: ["Hingga 80% lebih kecil", "Pemrosesan cepat", "Privasi utama"],
      },
      "merge-pdf": {
        features: ["Gabungkan banyak file", "Urutan terjaga", "Privasi utama"],
      },
      "split-pdf": {
        features: ["Rentang kustom", "Satu halaman per file", "Privasi utama"],
      },
      "jpg-to-pdf": {
        features: ["Multi-gambar", "Halaman menyesuaikan otomatis", "Privasi utama"],
      },
      "pdf-to-jpg": {
        features: ["Kualitas tinggi", "Satu gambar per halaman", "Privasi utama"],
      },
    },
    privacyNotice: {
      model: {
        server: "File kamu otomatis dihapus setelah 1 jam. Kami tidak pernah menyimpan dokumenmu.",
        client: "File tidak pernah meninggalkan perangkatmu. Semua proses berjalan di browser.",
        hybrid:
          "File kecil diproses di browser. File besar dikirim ke server dan otomatis dihapus dalam 1 jam.",
      },
    },
  },
} as const;

export type Messages = (typeof messages)[Locale];

export function getMessages(locale: Locale): Messages {
  return messages[locale];
}
