import type { Locale } from "./i18n";

export const messages = {
  en: {
    ads: {
      label: "Advertisement",
      fallback: {
        eyebrow: "From Papyr",
        title: "Free PDF tools",
        body: "Compress, merge, split, and convert PDFs. No account needed.",
        cta: "Explore tools",
      },
    },
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
      downloadCta: "Download Compressed PDF",
      complete: "Compression complete!",
      before: "Before",
      after: "After",
      errorTitle: "Something went wrong",
      retry: "Try Again",
      processingHint: "Optimizing images and streams...",
      queuePosition: "Position in queue",
      queueProgress: "Preparing your file...",
    },
    uploader: {
      browse: "Browse files",
      drop: "Drop your files here or",
      browseCta: "click to upload",
      dropHint: "Max {size}MB · PDF only · Deleted in 1 hour",
    },
    reset: {
      processAnother: "Process another file",
    },
    password: {
      label: "Password",
      placeholder: "Enter password",
      forFile: "Password for {name}",
      errors: {
        wrongPassword: "Wrong password",
        corrupt: "Corrupt file",
        unsupported: "Unsupported file",
      },
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
          "How Papyr handles your data: temporary server processing with 1-hour deletion, no tracking cookies, no AI training, and browser-only processing for Merge and Split.",
      },
      terms: {
        title: "Terms of Service",
        description:
          "The terms that govern your use of the Papyr PDF tools: acceptable use, no warranty, and how to contact us.",
      },
      cookiesAdvertising: {
        title: "Cookies & Advertising",
        description:
          "How Papyr uses cookies and advertising: reserved-dimension ad slots on the homepage, the five tools, and selected supporting pages; no tracking cookies; and an opt-out that honors Do Not Track and Global Privacy Control.",
      },
      contact: {
        title: "Contact",
        description:
          "Send us a message through the contact form. Categorized submissions are delivered to the Papyr owner inbox by email; replies go to the address you provide, if any.",
      },
      status: {
        title: "Status",
        description:
          "General information about the availability of Papyr services and current service status.",
      },
      roadmap: {
        title: "Roadmap",
        description: "General information about the Papyr roadmap and product direction.",
      },
      blog: {
        title: "Blog",
        description:
          "Guides for every Papyr PDF tool: compress, merge, split, JPG to PDF, and PDF to JPG.",
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
    gone: {
      title: "Tool no longer available",
      description: "This tool is no longer available.",
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
    otherTools: {
      title: "Other tools",
    },
    contact: {
      formLabel: "Contact form",
      intro: "Send us a message. We usually reply within a few days.",
      reportProblem: "Report a problem with this result",
      reportIntro: "Tell us what went wrong. Please do not include file contents or passwords.",
      closeReport: "Close",
      categoryLabel: "Category",
      categories: {
        bug: "Bug or processing problem",
        suggestion: "Suggestion",
        question: "Question",
        privacy: "Privacy or data request",
        advertising: "Advertising concern",
        other: "Other",
      },
      messageLabel: "Message",
      messageRequired: "Message is required.",
      messageTooLong: "Message must be at most 2000 characters.",
      emailLabel: "Email (optional)",
      optional: "optional",
      emailHint: "Only used to reply about this submission. Never added to any list.",
      emailInvalid: "Please enter a valid email address.",
      emailTooLong: "Email must be at most 254 characters.",
      categoryInvalid: "Please choose a valid category.",
      submit: "Send message",
      submitting: "Sending...",
      confirmation: "Thank you! Your message has been received.",
      endpointUnavailable:
        "Our contact service is temporarily unavailable. Your message was not sent to the server; please try again later.",
      rateLimited: "You have sent too many messages. Please wait a few minutes and try again.",
      sendAnother: "Send another message",
      turnstileRequired: "Please complete the security check.",
    },
    faqPage: {
      title: "Frequently Asked Questions",
      subtitle: "Answers to frequently asked questions about Papyr.",
      cta: "Still have questions?",
      ctaEmail: "privacy@mypapyr.com",
      items: [
        {
          q: "Is my file safe?",
          a: "Yes, your file's safety is our priority. All transfers use HTTPS (encrypted). Files uploaded to the server are stored in Cloudflare R2 with restricted access and are automatically deleted within 1 hour. For browser-processed features (Merge PDF, Split PDF), your files never leave your device.",
        },
        {
          q: "How long are files stored on the server?",
          a: "Maximum 1 hour. After that, files are automatically deleted from our servers — no exceptions. Download links also expire after 1 hour. For browser-processed features, files are never uploaded to the server at all.",
        },
        {
          q: "Do I need to create an account?",
          a: "No. Papyr works immediately without registration, without login, without email. Open the website, pick a tool, done. We do not collect any personal data.",
        },
        {
          q: "What is the maximum file size?",
          a: "The current upload limit is 20 MB per file. For browser-processed features (Merge PDF, Split PDF), the limit is more flexible since no server upload is needed.",
        },
        {
          q: "Can I use it on my phone?",
          a: "Yes! Papyr is optimized for mobile. All features are accessible from your phone's browser without installing an app. Just open budgezen.com from Chrome, Safari, or any other browser.",
        },
        {
          q: "Is Papyr free?",
          a: "Yes, all Papyr basic features are free — compress PDF, merge PDF, split PDF, JPG to PDF, and PDF to JPG. No hidden fees for normal use.",
        },
        {
          q: "What file formats are supported?",
          a: "Papyr supports PDF, JPG, and PNG files. You can compress PDFs, merge multiple PDFs, split PDF pages, convert images (JPG/PNG) to PDF, and convert PDF pages to PNG images.",
        },
        {
          q: "How can I contact Papyr?",
          a: "You can contact us via email at privacy@mypapyr.com. We will respond as soon as possible.",
        },
      ],
    },
    legal: {
      version: "1.0",
      effectiveDate: "2026-08-20",
      footerLabel: "Effective date",
      sections: {
        privacy: [
          {
            heading: "What we collect",
            paragraphs: [
              "Files you upload for server-processed tools (Compress PDF, JPG to PDF, PDF to JPG) are stored temporarily in Cloudflare R2 only for processing and are automatically deleted within 1 hour. Files for browser-processed tools (Merge PDF, Split PDF) never leave your device.",
              "We use Vercel Analytics, a privacy-friendly service that reports anonymous, aggregated page views without cookies and without identifying individual users.",
            ],
          },
          {
            heading: "What we do NOT collect",
            paragraphs: [
              "We do not require an account, name, or email. We do not read, analyze, or use your documents for any purpose other than providing the tool you chose, and never for AI training.",
            ],
          },
          {
            heading: "Security",
            paragraphs: [
              "All transfers use HTTPS. Download links are signed and expire within 5 minutes. Our servers never log file contents, object keys, or signed URLs.",
            ],
          },
          {
            heading: "Contact",
            paragraphs: ["Questions about privacy? Email privacy@mypapyr.com."],
          },
        ],
        terms: [
          {
            heading: "Service",
            paragraphs: [
              "Papyr provides browser-based PDF utilities at budgezen.com with no account or payment required: compress, merge, split, JPG to PDF, and PDF to JPG.",
            ],
          },
          {
            heading: "Acceptable use",
            paragraphs: [
              "You may use the tools only with files you are authorized to process. Uploading malicious content or abusing the service is prohibited.",
            ],
          },
          {
            heading: "No warranty",
            paragraphs: [
              "The service is provided as-is without warranties of any kind. Papyr is not liable for indirect or consequential damages.",
            ],
          },
          {
            heading: "Contact",
            paragraphs: ["Questions about these terms? Email privacy@mypapyr.com."],
          },
        ],
        cookiesAdvertising: [
          {
            heading: "Cookies",
            paragraphs: [
              "Papyr does not use tracking cookies. A single functional cookie (papyr_locale) remembers your language choice.",
            ],
          },
          {
            heading: "Advertising",
            paragraphs: [
              "Reserved-dimension ad slots may appear on the homepage, the five tool pages, and selected supporting pages. Ad content is served by a third-party network; opting out is supported and honors Do Not Track and Global Privacy Control.",
            ],
          },
          { heading: "Contact", paragraphs: ["Advertising concerns? Email privacy@mypapyr.com."] },
        ],
      },
    },
    privacyPage: {
      lastUpdated: "Last updated: 20 August 2026",
      sections: {
        intro:
          "Papyr is a free PDF tool that puts your privacy first. We designed this service to touch your personal data as little as possible.",
        whatWeCollect: {
          title: "What we collect",
          items: [
            "<strong>Files you upload</strong> — PDF or image files you process through Papyr are stored temporarily on our servers only for processing purposes.",
            "<strong>Anonymous analytics data</strong> — we use privacy-friendly Vercel Analytics to understand which pages are most frequently visited. No tracking cookies.",
          ],
        },
        whatWeDontCollect: {
          title: "What we do NOT collect",
          items: [
            "Name, email, or other personal information",
            "Content of the documents you upload",
            "We <strong>do not</strong> use your files to train AI or for any other purpose",
            "No accounts, no login, no tracking",
          ],
        },
        howLong: {
          title: "How long files are kept",
          paragraphs: [
            "All files uploaded to our servers are <strong>automatically deleted within 1 hour</strong>. No exceptions — after 1 hour, your files are permanently gone from our systems.",
            "For browser-processed features (Merge PDF, Split PDF), your files never leave your device at all.",
          ],
        },
        analytics: {
          title: "Analytics",
          paragraphs: [
            "We use <strong>Vercel Analytics</strong> to understand website performance. Vercel Analytics is privacy-friendly:",
          ],
          items: [
            "No cookies used",
            "No individual user tracking",
            "Data collected anonymously and in aggregate",
          ],
        },
        security: {
          title: "Security",
          items: [
            "All file transfers use HTTPS (encrypted)",
            "Files stored in Cloudflare R2 with restricted access",
            "Download links use signed URLs that expire within 1 hour",
            "Our servers never log file contents",
          ],
        },
        contact: {
          title: "Contact",
          email: "privacy@mypapyr.com",
          paragraphs: ["Have a privacy question? Contact us at {email}."],
        },
      },
      statusPage: {
        observedDisclaimer:
          "This page reports observed availability, not a guarantee of future uptime.",
        state: {
          operational: "Operational",
          degraded: "Degraded",
          down: "Service disruption",
          unknown: "Status unknown",
        },
        stateBody: {
          operational:
            "All monitored regions reported success in the most recent observation window.",
          degraded:
            "One or more regions are reporting repeated failures. Some requests may be affected.",
          down: "Multiple regions are reporting sustained failures at the same time.",
          unknown:
            "Monitoring signals are being configured. There is not enough observed data to determine availability yet.",
        },
        regionsHeading: "Regions",
        regionState: {
          operational: "Operational",
          degraded: "Observed failures",
          down: "Down",
        },
        policyHeading: "How availability is derived",
        policyBody:
          "Availability is derived from consecutive failed observations. A region is marked down only after {failures} failed observations in a row, and the service is marked as disrupted only when {regions} regions fail together.",
        lastObservedLabel: "Last observed",
        neverObserved: "Never",
        insufficientNote: "Not enough observations yet to confirm availability.",
      },
    },
  },
  es: {
    ads: {
      label: "Publicidad",
      fallback: {
        eyebrow: "De Papyr",
        title: "Herramientas PDF gratis",
        body: "Comprime, combina, divide y convierte PDFs. Sin cuenta.",
        cta: "Explorar herramientas",
      },
    },
    siteName: "Papyr",
    nav: {
      home: "Inicio",
      tools: "Herramientas",
      basic: "Básicas",
      conversion: "Conversión",
      security: "Seguridad",
      enhancement: "Mejora",
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
      downloadCta: "Descargar PDF comprimido",
      complete: "¡Compresión completada!",
      before: "Antes",
      after: "Después",
      errorTitle: "Algo salió mal",
      retry: "Intentar de nuevo",
      processingHint: "Optimizando imágenes y flujos...",
      queuePosition: "Posición en la cola",
      queueProgress: "Preparando tu archivo...",
    },
    uploader: {
      browse: "Elegir archivos",
      drop: "Arrastra tus archivos aquí o",
      browseCta: "haz clic para subir",
      dropHint: "Máx. {size}MB · Solo PDF · Eliminados en 1 hora",
    },
    reset: {
      processAnother: "Procesar otro archivo",
    },
    password: {
      label: "Contrase\u00f1a",
      placeholder: "Ingresa la contrase\u00f1a",
      forFile: "Contrase\u00f1a para {name}",
      errors: {
        wrongPassword: "Contrase\u00f1a incorrecta",
        corrupt: "Archivo corrupto",
        unsupported: "Archivo no compatible",
      },
    },
    languages: { en: "English", es: "Español", id: "Bahasa Indonesia" },
    home: {
      description: "Herramientas PDF de Papyr.",
      heroPill: "Gratis · Sin cuenta · Borrado automático",
      heroLine1: "Herramientas PDF que",
      heroLine2: "simplemente funcionan.",
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
          "Cómo trata Papyr tus datos: procesamiento temporal en el servidor con eliminación en 1 hora, sin cookies de seguimiento, sin entrenamiento de IA y procesamiento en el navegador para Unir y Dividir.",
      },
      terms: {
        title: "Términos de servicio",
        description:
          "Los términos que rigen el uso de las herramientas PDF de Papyr: uso aceptable, ausencia de garantías y cómo contactarnos.",
      },
      cookiesAdvertising: {
        title: "Cookies y publicidad",
        description:
          "Cómo usa Papyr las cookies y la publicidad: espacios publicitarios con dimensiones reservadas en la página de inicio, las cinco herramientas y algunas páginas de soporte; sin cookies de seguimiento; y una opción de exclusión que respeta Do Not Track y Global Privacy Control.",
      },
      contact: {
        title: "Contacto",
        description:
          "Envíanos un mensaje a través del formulario de contacto. Las solicitudes categorizadas se entregan por correo electrónico a la bandeja de entrada del propietario de Papyr; las respuestas van a la dirección que proporciones, si la indicas.",
      },
      status: {
        title: "Estado",
        description:
          "Información general sobre la disponibilidad de los servicios de Papyr y el estado actual del servicio.",
      },
      roadmap: {
        title: "Hoja de ruta",
        description: "Información general sobre la hoja de ruta y la dirección del producto Papyr.",
      },
      blog: {
        title: "Blog",
        description:
          "Guías para todas las herramientas PDF de Papyr: comprimir, combinar, dividir, JPG a PDF y PDF a JPG.",
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
    gone: {
      title: "Herramienta no disponible",
      description: "Esta herramienta ya no está disponible.",
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
        server:
          "Tus archivos se eliminan automáticamente después de 1 hora. Nunca guardamos tus documentos.",
        client: "Tus archivos nunca salen de tu dispositivo. Todo se procesa en tu navegador.",
        hybrid:
          "Los archivos pequeños se procesan en tu navegador. Los archivos grandes se envían al servidor y se eliminan en 1 hora.",
      },
    },
    otherTools: {
      title: "Otras herramientas",
    },
    contact: {
      formLabel: "Formulario de contacto",
      intro: "Envíanos un mensaje. Normalmente respondemos en unos días.",
      reportProblem: "Informar de un problema con este resultado",
      reportIntro: "Cuéntanos qué salió mal. No incluyas contenido de archivos ni contraseñas.",
      closeReport: "Cerrar",
      categoryLabel: "Categoría",
      categories: {
        bug: "Error o problema de procesamiento",
        suggestion: "Sugerencia",
        question: "Pregunta",
        privacy: "Privacidad o solicitud de datos",
        advertising: "Preocupación sobre publicidad",
        other: "Otro",
      },
      messageLabel: "Mensaje",
      messageRequired: "El mensaje es obligatorio.",
      messageTooLong: "El mensaje debe tener como máximo 2000 caracteres.",
      emailLabel: "Correo electrónico (opcional)",
      optional: "opcional",
      emailHint: "Solo se usa para responder sobre este mensaje. Nunca se añade a ninguna lista.",
      emailInvalid: "Introduce una dirección de correo válida.",
      emailTooLong: "El correo debe tener como máximo 254 caracteres.",
      categoryInvalid: "Elige una categoría válida.",
      submit: "Enviar mensaje",
      submitting: "Enviando...",
      confirmation: "¡Gracias! Hemos recibido tu mensaje.",
      endpointUnavailable:
        "Nuestro servicio de contacto no está disponible temporalmente. Tu mensaje no se envió al servidor; inténtalo de nuevo más tarde.",
      rateLimited: "Has enviado demasiados mensajes. Espera unos minutos e inténtalo de nuevo.",
      sendAnother: "Enviar otro mensaje",
      turnstileRequired: "Completa la verificación de seguridad.",
    },
    faqPage: {
      title: "Preguntas frecuentes",
      subtitle: "Respuestas a las preguntas más frecuentes sobre Papyr.",
      cta: "¿Todavía tienes preguntas?",
      ctaEmail: "privacy@mypapyr.com",
      items: [
        {
          q: "¿Está seguro mi archivo?",
          a: "Sí, la seguridad de tus archivos es nuestra prioridad. Todas las transferencias usan HTTPS (cifrado). Los archivos subidos al servidor se almacenan en Cloudflare R2 con acceso restringido y se eliminan automáticamente en 1 hora. Para las funciones procesadas en el navegador (Unir PDF, Dividir PDF), tus archivos nunca salen de tu dispositivo.",
        },
        {
          q: "¿Cuánto tiempo se guardan los archivos en el servidor?",
          a: "Máximo 1 hora. Después de ese tiempo, los archivos se eliminan automáticamente de nuestros servidores, sin excepciones. Los enlaces de descarga también caducan después de 1 hora. Para las funciones procesadas en el navegador, los archivos nunca se suben al servidor.",
        },
        {
          q: "¿Necesito crear una cuenta?",
          a: "No. Papyr funciona de inmediato sin registro, sin inicio de sesión y sin correo electrónico. Abre el sitio web, elige una herramienta y listo. No recopilamos ningún dato personal.",
        },
        {
          q: "¿Cuál es el tamaño máximo de archivo?",
          a: "El límite de subida actual es de 20 MB por archivo. Para las funciones procesadas en el navegador (Unir PDF, Dividir PDF), el límite es más flexible porque no se necesita subir al servidor.",
        },
        {
          q: "¿Se puede usar en el móvil?",
          a: "¡Sí! Papyr está optimizado para móviles. Todas las funciones son accesibles desde el navegador del teléfono sin instalar ninguna aplicación. Solo abre budgezen.com desde Chrome, Safari o cualquier otro navegador.",
        },
        {
          q: "¿Papyr es gratis?",
          a: "Sí, todas las funciones básicas de Papyr son gratuitas: comprimir PDF, unir PDF, dividir PDF, JPG a PDF y PDF a JPG. Sin costes ocultos para el uso normal.",
        },
        {
          q: "¿Qué formatos de archivo se admiten?",
          a: "Papyr admite archivos PDF, JPG y PNG. Puedes comprimir PDF, unir varios PDF, dividir páginas de PDF, convertir imágenes (JPG/PNG) a PDF y convertir páginas de PDF a imágenes PNG.",
        },
        {
          q: "¿Cómo puedo contactar con Papyr?",
          a: "Puedes contactar con nosotros por correo electrónico en privacy@mypapyr.com. Responderemos lo antes posible.",
        },
      ],
    },
    legal: {
      version: "1.0",
      effectiveDate: "2026-08-20",
      footerLabel: "Fecha de entrada en vigor",
      sections: {
        privacy: [
          {
            heading: "Qué recopilamos",
            paragraphs: [
              "Los archivos que subes para las herramientas procesadas en el servidor (Comprimir PDF, JPG a PDF y PDF a JPG) se almacenan temporalmente en Cloudflare R2 solo para su procesamiento y se eliminan automáticamente en un plazo de 1 hora. Los archivos de las herramientas procesadas en el navegador (Unir PDF y Dividir PDF) nunca salen de tu dispositivo.",
              "Usamos Vercel Analytics, un servicio respetuoso con la privacidad que informa de visitas anónimas y agregadas sin cookies y sin identificar a usuarios individuales.",
            ],
          },
          {
            heading: "Qué NO recopilamos",
            paragraphs: [
              "No exigimos una cuenta, nombre ni correo electrónico. No leemos, analizamos ni usamos tus documentos para ningún fin distinto de ofrecer la herramienta que elegiste, y nunca para entrenar IA.",
            ],
          },
          {
            heading: "Seguridad",
            paragraphs: [
              "Todas las transferencias usan HTTPS. Los enlaces de descarga están firmados y caducan en un plazo de 5 minutos. Nuestros servidores nunca registran el contenido de los archivos, las claves de objetos ni las URL firmadas.",
            ],
          },
          {
            heading: "Contacto",
            paragraphs: ["¿Preguntas sobre privacidad? Escribe a privacy@mypapyr.com."],
          },
        ],
        terms: [
          {
            heading: "Servicio",
            paragraphs: [
              "Papyr ofrece herramientas PDF basadas en el navegador en budgezen.com sin cuenta ni pago: comprimir, unir, dividir, JPG a PDF y PDF a JPG.",
            ],
          },
          {
            heading: "Uso aceptable",
            paragraphs: [
              "Solo puedes usar las herramientas con archivos cuyo procesamiento estés autorizado a realizar. Está prohibido subir contenido malicioso o abusar del servicio.",
            ],
          },
          {
            heading: "Sin garantías",
            paragraphs: [
              "El servicio se proporciona tal cual, sin garantías de ningún tipo. Papyr no se hace responsable de daños indirectos o consecuentes.",
            ],
          },
          {
            heading: "Contacto",
            paragraphs: ["¿Preguntas sobre estos términos? Escribe a privacy@mypapyr.com."],
          },
        ],
        cookiesAdvertising: [
          {
            heading: "Cookies",
            paragraphs: [
              "Papyr no utiliza cookies de seguimiento. Una única cookie funcional (papyr_locale) recuerda tu elección de idioma.",
            ],
          },
          {
            heading: "Publicidad",
            paragraphs: [
              "Pueden aparecer espacios publicitarios de dimensiones reservadas en la página de inicio, las cinco herramientas y algunas páginas de soporte. El contenido publicitario lo sirve una red externa; se admite la exclusión y se respetan Do Not Track y Global Privacy Control.",
            ],
          },
          {
            heading: "Contacto",
            paragraphs: ["¿Dudas sobre publicidad? Escribe a privacy@mypapyr.com."],
          },
        ],
      },
    },
    privacyPage: {
      lastUpdated: "Última actualización: 20 de agosto de 2026",
      sections: {
        intro:
          "Papyr es una herramienta PDF gratuita que antepone tu privacidad. Diseñamos este servicio para tocar tus datos personales lo menos posible.",
        whatWeCollect: {
          title: "Qué recopilamos",
          items: [
            "<strong>Los archivos que subes</strong> — los archivos PDF o de imagen que procesas a través de Papyr se almacenan temporalmente en nuestros servidores únicamente para su procesamiento.",
            "<strong>Datos de análisis anónimos</strong> — usamos Vercel Analytics, respetuoso con la privacidad, para entender qué páginas se visitan con más frecuencia. Sin cookies de seguimiento.",
          ],
        },
        whatWeDontCollect: {
          title: "Qué NO recopilamos",
          items: [
            "Nombre, correo electrónico u otra información personal",
            "Contenido de los documentos que subes",
            "No <strong>usamos</strong> tus archivos para entrenar IA ni para ningún otro fin",
            "Sin cuentas, sin inicio de sesión, sin seguimiento",
          ],
        },
        howLong: {
          title: "Cuánto tiempo se guardan los archivos",
          paragraphs: [
            "Todos los archivos subidos a nuestros servidores se <strong>eliminan automáticamente en 1 hora</strong>. Sin excepciones: después de 1 hora, tus archivos desaparecen permanentemente de nuestros sistemas.",
            "Para las funciones procesadas en el navegador (Unir PDF, Dividir PDF), tus archivos nunca salen de tu dispositivo.",
          ],
        },
        analytics: {
          title: "Analítica",
          paragraphs: [
            "Usamos <strong>Vercel Analytics</strong> para entender el rendimiento del sitio web. Vercel Analytics respeta la privacidad:",
          ],
          items: [
            "No utiliza cookies",
            "No rastrea a usuarios individualmente",
            "Los datos se recopilan de forma anónima y agregada",
          ],
        },
        security: {
          title: "Seguridad",
          items: [
            "Todas las transferencias de archivos usan HTTPS (cifrado)",
            "Archivos almacenados en Cloudflare R2 con acceso restringido",
            "Los enlaces de descarga usan URL firmadas que caducan en 1 hora",
            "Nuestros servidores nunca registran el contenido de los archivos",
          ],
        },
        contact: {
          title: "Contacto",
          email: "privacy@mypapyr.com",
          paragraphs: ["¿Tienes una pregunta sobre privacidad? Contáctanos en {email}."],
        },
      },
      statusPage: {
        observedDisclaimer:
          "Esta página informa disponibilidad observada, no garantiza disponibilidad futura.",
        state: {
          operational: "Operativo",
          degraded: "Degradado",
          down: "Interrupción del servicio",
          unknown: "Estado desconocido",
        },
        stateBody: {
          operational:
            "Todas las regiones supervisadas informaron resultados correctos en la ventana de observación más reciente.",
          degraded:
            "Una o más regiones informan fallos repetidos. Algunas solicitudes pueden verse afectadas.",
          down: "Varias regiones informan fallos sostenidos al mismo tiempo.",
          unknown:
            "Las señales de supervisión se están configurando. Todavía no hay suficientes datos observados para determinar la disponibilidad.",
        },
        regionsHeading: "Regiones",
        regionState: {
          operational: "Operativo",
          degraded: "Fallos observados",
          down: "Caído",
        },
        policyHeading: "Cómo se determina la disponibilidad",
        policyBody:
          "La disponibilidad se determina a partir de observaciones fallidas consecutivas. Una región solo se marca como caída después de {failures} observaciones fallidas seguidas, y el servicio solo se marca como interrumpido cuando {regions} regiones fallan a la vez.",
        lastObservedLabel: "Última observación",
        neverObserved: "Nunca",
        insufficientNote:
          "Todavía no hay suficientes observaciones para confirmar la disponibilidad.",
      },
    },
  },
  id: {
    ads: {
      label: "Iklan",
      fallback: {
        eyebrow: "Dari Papyr",
        title: "Alat PDF gratis",
        body: "Kompres, gabung, pisah, dan konversi PDF. Tanpa akun.",
        cta: "Jelajahi alat",
      },
    },
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
      downloadCta: "Unduh PDF yang Dikompres",
      complete: "Kompresi selesai!",
      before: "Sebelum",
      after: "Sesudah",
      errorTitle: "Terjadi Kesalahan",
      retry: "Coba Lagi",
      processingHint: "Mengoptimalkan gambar dan stream...",
      queuePosition: "Posisi dalam antrean",
      queueProgress: "Menyiapkan file Anda...",
    },
    uploader: {
      browse: "Pilih file",
      drop: "Seret file Anda ke sini atau",
      browseCta: "klik untuk upload",
      dropHint: "Maks {size}MB · Hanya file PDF · Dihapus dalam 1 jam",
    },
    reset: {
      processAnother: "Proses file lain",
    },
    password: {
      label: "Kata sandi",
      placeholder: "Masukkan kata sandi",
      forFile: "Kata sandi untuk {name}",
      errors: {
        wrongPassword: "Kata sandi salah",
        corrupt: "File rusak",
        unsupported: "File tidak didukung",
      },
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
          "Cara Papyr menangani data Anda: pemrosesan sementara di server dengan penghapusan dalam 1 jam, tanpa cookie pelacakan, tanpa pelatihan AI, dan pemrosesan di browser untuk Gabung dan Pisah.",
      },
      terms: {
        title: "Ketentuan Layanan",
        description:
          "Ketentuan yang mengatur penggunaan alat PDF Papyr: penggunaan yang dapat diterima, tanpa jaminan, dan cara menghubungi kami.",
      },
      cookiesAdvertising: {
        title: "Cookie dan Iklan",
        description:
          "Bagaimana Papyr menggunakan cookie dan iklan: slot iklan dengan dimensi yang disediakan di beranda, lima alat, dan beberapa halaman pendukung; tanpa cookie pelacakan; dan opsi menolak yang menghormati Do Not Track dan Global Privacy Control.",
      },
      contact: {
        title: "Kontak",
        description:
          "Kirim pesan kepada kami melalui formulir kontak. Pengiriman yang dikategorikan dikirim lewat email ke kotak masuk pemilik Papyr; balasan dikirim ke alamat yang Anda berikan, jika ada.",
      },
      status: {
        title: "Status",
        description:
          "Informasi umum tentang ketersediaan layanan Papyr dan status layanan saat ini.",
      },
      roadmap: {
        title: "Peta Jalan",
        description: "Informasi umum tentang peta jalan dan arah produk Papyr.",
      },
      blog: {
        title: "Blog",
        description:
          "Panduan untuk setiap alat PDF Papyr: kompres, gabungkan, pisahkan, JPG ke PDF, dan PDF ke JPG.",
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
    gone: {
      title: "Alat tidak lagi tersedia",
      description: "Alat ini tidak lagi tersedia.",
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
    otherTools: {
      title: "Alat lainnya",
    },
    contact: {
      formLabel: "Formulir kontak",
      intro: "Kirim pesan kepada kami. Kami biasanya membalas dalam beberapa hari.",
      reportProblem: "Laporkan masalah dengan hasil ini",
      reportIntro: "Ceritakan apa yang salah. Jangan sertakan konten file atau kata sandi.",
      closeReport: "Tutup",
      categoryLabel: "Kategori",
      categories: {
        bug: "Bug atau masalah pemrosesan",
        suggestion: "Saran",
        question: "Pertanyaan",
        privacy: "Privasi atau permintaan data",
        advertising: "Masalah iklan",
        other: "Lainnya",
      },
      messageLabel: "Pesan",
      messageRequired: "Pesan wajib diisi.",
      messageTooLong: "Pesan maksimal 2000 karakter.",
      emailLabel: "Email (opsional)",
      optional: "opsional",
      emailHint:
        "Hanya dipakai untuk membalas pesan ini. Tidak pernah ditambahkan ke daftar apa pun.",
      emailInvalid: "Masukkan alamat email yang valid.",
      emailTooLong: "Email maksimal 254 karakter.",
      categoryInvalid: "Pilih kategori yang valid.",
      submit: "Kirim pesan",
      submitting: "Mengirim...",
      confirmation: "Terima kasih! Pesan Anda telah kami terima.",
      endpointUnavailable:
        "Layanan kontak kami sedang tidak tersedia. Pesan Anda tidak terkirim ke server; silakan coba lagi nanti.",
      rateLimited:
        "Anda terlalu banyak mengirim pesan. Silakan tunggu beberapa menit dan coba lagi.",
      sendAnother: "Kirim pesan lain",
      turnstileRequired: "Selesaikan pemeriksaan keamanan.",
    },
    faqPage: {
      title: "Pertanyaan Umum",
      subtitle: "Jawaban untuk pertanyaan yang sering ditanyakan tentang Papyr.",
      cta: "Masih punya pertanyaan?",
      ctaEmail: "privacy@mypapyr.com",
      items: [
        {
          q: "Apakah file saya aman?",
          a: "Ya, keamanan file-mu adalah prioritas kami. Semua transfer menggunakan HTTPS (terenkripsi). File yang di-upload ke server disimpan di Cloudflare R2 dengan akses terbatas, dan otomatis dihapus dalam 1 jam. Untuk fitur yang diproses di browser (Gabungkan PDF, Pisahkan PDF), file-mu tidak pernah meninggalkan perangkatmu.",
        },
        {
          q: "Berapa lama file disimpan di server?",
          a: "Maksimal 1 jam. Setelah itu, file dihapus otomatis dari server kami — tanpa pengecualian. Link download juga kedaluwarsa setelah 1 jam. Untuk fitur yang diproses di browser, file tidak pernah di-upload ke server sama sekali.",
        },
        {
          q: "Apakah perlu daftar akun?",
          a: "Tidak. Papyr bisa langsung dipakai tanpa daftar, tanpa login, tanpa email. Buka website, pilih alat, selesai. Kami tidak mengumpulkan data pribadi apapun.",
        },
        {
          q: "Berapa ukuran file maksimum?",
          a: "Saat ini batas upload adalah 20 MB per file. Untuk fitur yang diproses di browser (Gabungkan PDF, Pisahkan PDF), batasnya lebih fleksibel karena tidak perlu upload ke server.",
        },
        {
          q: "Bisa dipakai di HP?",
          a: "Ya! Papyr dioptimalkan untuk mobile. Semua fitur bisa diakses dari browser HP tanpa perlu install aplikasi. Cukup buka budgezen.com dari Chrome, Safari, atau browser lainnya.",
        },
        {
          q: "Apakah Papyr gratis?",
          a: "Ya, semua fitur dasar Papyr gratis — kompres PDF, gabungkan PDF, pisahkan PDF, gambar ke PDF, dan PDF ke gambar. Tidak ada biaya tersembunyi untuk penggunaan normal.",
        },
        {
          q: "Format file apa yang didukung?",
          a: "Papyr mendukung file PDF, JPG, dan PNG. Kamu bisa mengompres PDF, menggabungkan beberapa PDF, memisahkan halaman PDF, mengubah gambar (JPG/PNG) menjadi PDF, dan mengubah halaman PDF menjadi gambar PNG.",
        },
        {
          q: "Bagaimana cara menghubungi Papyr?",
          a: "Kamu bisa menghubungi kami melalui email di privacy@mypapyr.com. Kami akan merespons secepat mungkin.",
        },
      ],
    },
    legal: {
      version: "1.0",
      effectiveDate: "2026-08-20",
      footerLabel: "Tanggal berlaku",
      sections: {
        privacy: [
          {
            heading: "Apa yang kami kumpulkan",
            paragraphs: [
              "File yang Anda unggah untuk alat yang diproses di server (Kompres PDF, Gambar ke PDF, PDF ke Gambar) disimpan sementara di Cloudflare R2 hanya untuk pemrosesan dan otomatis dihapus dalam 1 jam. File untuk alat yang diproses di browser (Gabung PDF, Pisah PDF) tidak pernah meninggalkan perangkat Anda.",
              "Kami menggunakan Vercel Analytics, layanan yang ramah privasi untuk melaporkan kunjungan halaman secara anonim dan agregat tanpa cookie dan tanpa mengidentifikasi pengguna secara individual.",
            ],
          },
          {
            heading: "Apa yang TIDAK kami kumpulkan",
            paragraphs: [
              "Kami tidak memerlukan akun, nama, atau email. Kami tidak membaca, menganalisis, atau menggunakan dokumen Anda untuk tujuan selain menyediakan alat yang Anda pilih, dan tidak pernah untuk pelatihan AI.",
            ],
          },
          {
            heading: "Keamanan",
            paragraphs: [
              "Semua transfer menggunakan HTTPS. Link unduhan ditandatangani dan kedaluwarsa dalam 5 menit. Server kami tidak pernah mencatat isi file, kunci objek, atau signed URL.",
            ],
          },
          {
            heading: "Kontak",
            paragraphs: ["Ada pertanyaan tentang privasi? Email privacy@mypapyr.com."],
          },
        ],
        terms: [
          {
            heading: "Layanan",
            paragraphs: [
              "Papyr menyediakan alat PDF berbasis browser di budgezen.com tanpa akun atau biaya: kompres, gabung, pisah, gambar ke PDF, dan PDF ke gambar.",
            ],
          },
          {
            heading: "Penggunaan yang dapat diterima",
            paragraphs: [
              "Anda hanya boleh menggunakan alat dengan file yang Anda berwenang untuk proses. Mengunggah konten berbahaya atau menyalahgunakan layanan dilarang.",
            ],
          },
          {
            heading: "Tanpa jaminan",
            paragraphs: [
              "Layanan disediakan apa adanya tanpa jaminan apa pun. Papyr tidak bertanggung jawab atas kerugian tidak langsung atau konsekuensial.",
            ],
          },
          {
            heading: "Kontak",
            paragraphs: ["Ada pertanyaan tentang ketentuan ini? Email privacy@mypapyr.com."],
          },
        ],
        cookiesAdvertising: [
          {
            heading: "Cookie",
            paragraphs: [
              "Papyr tidak menggunakan cookie pelacakan. Satu cookie fungsional (papyr_locale) mengingat pilihan bahasa Anda.",
            ],
          },
          {
            heading: "Iklan",
            paragraphs: [
              "Slot iklan berdimensi khusus dapat muncul di beranda, lima halaman alat, dan halaman pendukung tertentu. Konten iklan disediakan jaringan pihak ketiga; opsi menolak didukung dan menghormati Do Not Track serta Global Privacy Control.",
            ],
          },
          {
            heading: "Kontak",
            paragraphs: ["Ada kekhawatiran tentang iklan? Email privacy@mypapyr.com."],
          },
        ],
      },
    },
    privacyPage: {
      lastUpdated: "Terakhir diperbarui: 20 Agustus 2026",
      sections: {
        intro:
          "Papyr adalah alat PDF gratis yang mengutamakan privasimu. Kami merancang layanan ini agar sesedikit mungkin menyentuh data pribadimu.",
        whatWeCollect: {
          title: "Apa yang kami kumpulkan",
          items: [
            "<strong>File yang kamu upload</strong> — file PDF atau gambar yang kamu proses melalui Papyr disimpan sementara di server kami hanya untuk keperluan pemrosesan.",
            "<strong>Data analytics anonim</strong> — kami menggunakan Vercel Analytics yang privacy-friendly untuk memahami halaman mana yang paling sering dikunjungi. Tidak ada cookie pelacakan.",
          ],
        },
        whatWeDontCollect: {
          title: "Apa yang TIDAK kami kumpulkan",
          items: [
            "Nama, email, atau informasi pribadi lainnya",
            "Isi/konten dokumen yang kamu upload",
            "Kami <strong>tidak</strong> menggunakan file-mu untuk melatih AI atau keperluan lain",
            "Tidak ada akun, tidak ada login, tidak ada tracking",
          ],
        },
        howLong: {
          title: "Berapa lama file disimpan",
          paragraphs: [
            "Semua file yang di-upload ke server kami <strong>dihapus otomatis dalam 1 jam</strong>. Tidak ada pengecualian — setelah 1 jam, file-mu hilang permanen dari sistem kami.",
            "Untuk fitur yang diproses di browser (Gabungkan PDF, Pisahkan PDF), file-mu tidak pernah meninggalkan perangkatmu sama sekali.",
          ],
        },
        analytics: {
          title: "Analytics",
          paragraphs: [
            "Kami menggunakan <strong>Vercel Analytics</strong> untuk memahami performa website. Vercel Analytics bersifat privacy-friendly:",
          ],
          items: [
            "Tidak menggunakan cookie",
            "Tidak melacak pengguna secara individual",
            "Data dikumpulkan secara anonim dan agregat",
          ],
        },
        security: {
          title: "Keamanan",
          items: [
            "Semua transfer file menggunakan HTTPS (terenkripsi)",
            "File disimpan di Cloudflare R2 dengan akses terbatas",
            "Link download menggunakan signed URL yang kedaluwarsa dalam 1 jam",
            "Server kami tidak pernah mencatat isi file dalam log",
          ],
        },
        contact: {
          title: "Kontak",
          email: "privacy@mypapyr.com",
          paragraphs: ["Punya pertanyaan tentang privasi? Hubungi kami di {email}."],
        },
      },
      statusPage: {
        observedDisclaimer:
          "Halaman ini melaporkan ketersediaan yang teramati, bukan jaminan ketersediaan di masa depan.",
        state: {
          operational: "Beroperasi normal",
          degraded: "Menurun",
          down: "Gangguan layanan",
          unknown: "Status tidak diketahui",
        },
        stateBody: {
          operational:
            "Semua wilayah yang dipantau melaporkan hasil sukses pada jendela observasi terbaru.",
          degraded:
            "Satu atau lebih wilayah melaporkan kegagalan berulang. Sebagian permintaan mungkin terdampak.",
          down: "Beberapa wilayah melaporkan kegagalan berkelanjutan pada waktu yang sama.",
          unknown:
            "Sinyal pemantauan sedang dikonfigurasi. Belum ada cukup data teramati untuk menentukan ketersediaan.",
        },
        regionsHeading: "Wilayah",
        regionState: {
          operational: "Beroperasi normal",
          degraded: "Kegagalan teramati",
          down: "Gangguan",
        },
        policyHeading: "Cara ketersediaan ditentukan",
        policyBody:
          "Ketersediaan ditentukan dari kegagalan observasi berurutan. Sebuah wilayah baru ditandai terganggu setelah {failures} kegagalan observasi berturut-turut, dan layanan baru ditandai terganggu ketika {regions} wilayah gagal bersamaan.",
        lastObservedLabel: "Terakhir diamati",
        neverObserved: "Tidak pernah",
        insufficientNote: "Belum cukup observasi untuk mengonfirmasi ketersediaan.",
      },
    },
  },
} as const;

export type Messages = (typeof messages)[Locale];

export function getMessages(locale: Locale): Messages {
  return messages[locale];
}
