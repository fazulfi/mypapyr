# Track B — Legacy Frontend Evidence: Browser Routing, SEO/URL Migration, UI Baseline

Source repository: `<workspace-root>\papyr-reference` (READ-ONLY legacy Papyr clone; not modified by this exploration).
Evidence standard: every finding cites source path + line range; exact strings are quoted verbatim. Uncertainties are explicitly marked.

Generated: 2026-07-31. All line numbers refer to the current state of `papyr-reference/`.

---

## 1. Route Inventory

All tool routes are static-path App Router routes. Every tool page is a **client component** (`'use client'` as first line). Every tool route (except `/privacy`) has a `layout.tsx` that exports static `Metadata` and returns `children` unchanged (trivial pass-throughs: `return children;`).

The root layout (`src/app/layout.tsx`) applies `title.template: '%s | Papyr'` and `title.default: 'Papyr — Alat PDF Gratis untuk Indonesia'` (Section 2).

### 1.1 Table

| Route | page.tsx client/server | Metadata owner | `title` (exact) | `description` (exact) | openGraph (exact non-null fields) | twitter / url / icons |
|---|---|---|---|---|---|---|
| `/` (home) | `src/app/page.tsx` — **server** (no `'use client'`; exports `TOOLS` L360) | `src/app/layout.tsx:16-41` | default `Papyr — Alat PDF Gratis untuk Indonesia` (L18); template `%s \| Papyr` (L19) | `Kompres, gabungkan, pisahkan, dan konversi PDF dengan mudah. Gratis, tanpa akun, dan menjaga privasi. Dibuat untuk pengguna Indonesia.` (L21-22) | `type: 'website'`, `locale: 'id_ID'`, `siteName: 'Papyr'`, title (L28), description (L29-30), `url: 'https://mypapyr.com'` (L31), `images: ['/og/papyr.png']` (L32) | twitter `summary_large_image` + `/og/papyr.png` (L34-40) |
| `/compress` | `src/app/compress/page.tsx` — **client** (L1) | `src/app/compress/layout.tsx:3-14` | `Kompres PDF Online Gratis` (L4) | `Perkecil ukuran file PDF tanpa mengurangi kualitas. Cocok untuk kirim dokumen lewat WhatsApp, email kantor, atau upload ke portal pemerintah.` (L5-6) | `title: 'Kompres PDF Online Gratis - Papyr'` (L8), description (L9-10), `type: 'website'` (L11), `images: ['/og/compress.png']` (L12) | no twitter; no url; no icons |
| `/merge` | `src/app/merge/page.tsx` — **client** (L1) | `src/app/merge/layout.tsx:3-14` | `Gabungkan PDF Online Gratis` (L4) | `Gabungkan beberapa file PDF menjadi satu dokumen. Satukan scan KTP, ijazah, dan dokumen lainnya untuk lamaran kerja atau pendaftaran online.` (L5-6) | `title: 'Gabungkan PDF Online Gratis - Papyr'` (L8), description (L9-10), `type: 'website'` (L11), `images: ['/og/merge.png']` (L12) | no twitter; no url; no icons |
| `/split` | `src/app/split/page.tsx` — **client** (L1) | `src/app/split/layout.tsx:3-14` | `Pisahkan PDF Online Gratis` (L4) | `Ambil halaman tertentu dari dokumen PDF. Pisahkan halaman dari laporan, skripsi, atau e-book tanpa perlu download ulang seluruh file.` (L5-6) | `title: 'Pisahkan PDF Online Gratis - Papyr'` (L8), description (L9-10), `type: 'website'` (L11), `images: ['/og/split.png']` (L12) | no twitter; no url; no icons |
| `/rotate` | `src/app/rotate/page.tsx` — **client** (L1) | `src/app/rotate/layout.tsx:3-14` | `Putar PDF — Rotate Halaman PDF Online Gratis` (L4) | `Putar halaman PDF sesuai kebutuhan. Perbaiki orientasi dokumen scan, foto, atau halaman yang terbalik. Gratis, tanpa akun, langsung di browser.` (L5-6) | `title: 'Putar PDF Online Gratis - Papyr'` (L8), description (L9-10), `type: 'website'` (L11), `images: ['/og/rotate.png']` (L12) | no twitter; no url; no icons |
| `/image-to-pdf` | `src/app/image-to-pdf/page.tsx` — **client** (L1) | `src/app/image-to-pdf/layout.tsx:3-14` | `Ubah Gambar ke PDF Online Gratis` (L4) | `Ubah foto atau gambar menjadi file PDF. Jadikan foto KTP, bukti transfer, atau hasil scan jadi PDF rapi untuk dikirim lewat email.` (L5-6) | `title: 'Ubah Gambar ke PDF Online Gratis - Papyr'` (L8), description (L9-10), `type: 'website'` (L11), `images: ['/og/image-to-pdf.png']` (L12) | no twitter; no url; no icons |
| `/pdf-to-image` | `src/app/pdf-to-image/page.tsx` — **client** (L1) | `src/app/pdf-to-image/layout.tsx:3-14` | `Ubah PDF ke Gambar Online Gratis` (L4) | `Ubah halaman PDF menjadi gambar PNG berkualitas tinggi. Konversi slide presentasi atau sertifikat jadi gambar untuk di-share di media sosial.` (L5-6) | `title: 'Ubah PDF ke Gambar Online Gratis - Papyr'` (L8), description (L9-10), `type: 'website'` (L11), `images: ['/og/pdf-to-image.png']` (L12) | no twitter; no url; no icons |
| `/protect` | `src/app/protect/page.tsx` — **client** (L1) | `src/app/protect/layout.tsx:3-13` | `Proteksi PDF dengan Password - Papyr` (L4) | `Lindungi file PDF Anda dengan password AES-256. Gratis, cepat, tanpa login. File dihapus otomatis dalam 60 menit.` (L5-6) | `title: 'Proteksi PDF dengan Password - Papyr'` (L8), `description: 'Lindungi file PDF Anda dengan password AES-256. Gratis, cepat, tanpa login.'` (L9), `url: 'https://mypapyr.com/protect'` (L10), `images: ['/og/protect.png']` (L11) | no twitter; no icons |
| `/unlock` | `src/app/unlock/page.tsx` — **client** (L1) | `src/app/unlock/layout.tsx:3-13` | `Hapus Password PDF - Papyr` (L4) | `Buka kunci PDF yang terproteksi password. Masukkan password, download PDF tanpa proteksi. Gratis dan privasi terjaga.` (L5-6) | `title: 'Hapus Password PDF - Papyr'` (L8), `description: 'Buka kunci PDF yang terproteksi password. Gratis dan privasi terjaga.'` (L9), `url: 'https://mypapyr.com/unlock'` (L10), `images: ['/og/unlock.png']` (L11) | no twitter; no icons |
| `/watermark` | `src/app/watermark/page.tsx` — **client** (L1) | `src/app/watermark/layout.tsx:3-14` | `Tambah Watermark PDF - Papyr` (L4) | `Tambahkan watermark teks atau gambar ke semua halaman PDF. Preview sebelum apply. Gratis, tanpa login.` (L5-6) | `title: 'Tambah Watermark PDF - Papyr'` (L8), description (L9-10), `url: 'https://mypapyr.com/watermark'` (L11), `images: ['/og/watermark.png']` (L12) | no twitter; no icons |
| `/sign` | `src/app/sign/page.tsx` — **client** (L1) | `src/app/sign/layout.tsx:3-14` | `Tanda Tangani PDF Online - Papyr` (L4) | `Tanda tangani PDF langsung dari browser. Gambar, upload, atau ketik tanda tangan. 100% privasi — file tidak diupload.` (L5-6) | `title: 'Tanda Tangani PDF Online - Papyr'` (L8), description (L9-10), `url: 'https://mypapyr.com/sign'` (L11), `images: ['/og/sign.png']` (L12) | no twitter; no icons |
| `/pdf-to-word` | `src/app/pdf-to-word/page.tsx` — **client** (L1) | `src/app/pdf-to-word/layout.tsx:3-14` | `Konversi PDF ke Word (DOCX) - Papyr` (L4) | `Ubah file PDF menjadi dokumen Word (.docx) dengan cepat dan akurat. 100% gratis, tanpa registrasi.` (L5-6) | `title: 'Konversi PDF ke Word (DOCX) - Papyr'` (L8), description (L9-10), `url: 'https://mypapyr.com/pdf-to-word'` (L11), `images: ['/og/pdf-to-word.png']` (L12) | no twitter; no icons |
| `/ocr` | `src/app/ocr/page.tsx` — **client** (L1) | `src/app/ocr/layout.tsx:3-14` | `OCR PDF — Jadikan PDF Scan Bisa Dicari - Papyr` (L4) | `Jadikan file PDF gambar atau scan memiliki text layer yang bisa dicari dan diseleksi. Hasil tetap dalam format PDF. Gratis, tanpa registrasi.` (L5-6) | `title: 'OCR PDF — Jadikan PDF Scan Bisa Dicari - Papyr'` (L8), description (L9-10), `url: 'https://mypapyr.com/ocr'` (L11), `images: ['/og/ocr.png']` (L12) | no twitter; no icons |
| `/pdf-to-excel` | `src/app/pdf-to-excel/page.tsx` — **client** (L1) | `src/app/pdf-to-excel/layout.tsx:3-14` | `Konversi PDF ke Excel (XLSX) - Papyr` (L4) | `Ekstrak tabel dari file PDF dan konversi ke format Excel (.xlsx). 100% gratis, tanpa registrasi.` (L5-6) | `title: 'Konversi PDF ke Excel (XLSX) - Papyr'` (L8), description (L9-10), `url: 'https://mypapyr.com/pdf-to-excel'` (L11), `images: ['/og/pdf-to-excel.png']` (L12) | no twitter; no icons |
| `/faq` | `src/app/faq/page.tsx` — **client** (L1, accordion state) | `src/app/faq/layout.tsx:3-14` | `FAQ — Pertanyaan Umum` (L4) | `Jawaban untuk pertanyaan yang sering ditanyakan tentang Papyr — alat PDF gratis untuk Indonesia. Keamanan file, batas upload, format yang didukung.` (L5-6) | `title: 'FAQ Papyr — Pertanyaan Umum'` (L8), description (L9-10), `type: 'website'` (L11), `images: ['/og/papyr.png']` (L12) | no twitter; no url; no icons |
| `/privacy` | `src/app/privacy/page.tsx` — **server** (no `'use client'`); page itself exports metadata | `src/app/privacy/page.tsx:3-7` | `Kebijakan Privasi` (L4) | `Kebijakan privasi Papyr — alat PDF gratis untuk Indonesia. File dihapus otomatis dalam 1 jam.` (L5-6) | **none** (no openGraph / twitter / url / icons) | no twitter; no icons |
### 1.2 Metadata file paths + line refs (complete list of `export const metadata` occurrences)

- `frontend/src/app/layout.tsx:16` (root)
- `frontend/src/app/compress/layout.tsx:3`, `frontend/src/app/merge/layout.tsx:3`, `frontend/src/app/split/layout.tsx:3`, `frontend/src/app/rotate/layout.tsx:3`, `frontend/src/app/image-to-pdf/layout.tsx:3`, `frontend/src/app/pdf-to-image/layout.tsx:3`, `frontend/src/app/protect/layout.tsx:3`, `frontend/src/app/unlock/layout.tsx:3`, `frontend/src/app/watermark/layout.tsx:3`, `frontend/src/app/sign/layout.tsx:3`, `frontend/src/app/pdf-to-word/layout.tsx:3`, `frontend/src/app/ocr/layout.tsx:3`, `frontend/src/app/pdf-to-excel/layout.tsx:3`, `frontend/src/app/faq/layout.tsx:3`
- `frontend/src/app/privacy/page.tsx:3` (metadata lives in the page; `/privacy` has no layout.tsx — directory listing contains only `page.tsx`)

No route uses `generateMetadata` or dynamic metadata. No route defines `icons` in metadata. `favicon.ico` exists at `frontend/src/app/favicon.ico` (auto-discovery; no `icons` key anywhere).

### 1.3 Metadata quirks (uncertainty flags)

- Only 7 of 15 routes set an `openGraph.url`: `/ocr`, `/pdf-to-excel`, `/pdf-to-word`, `/protect`, `/unlock`, `/sign`, `/watermark`. The other 8 tool routes + FAQ rely on root `metadataBase` (`https://mypapyr.com`, layout.tsx:23). `/privacy` has no OG block at all.
- OG title format is inconsistent: 8 tools use `"<Name> - Papyr"` (hyphen); the rest reuse the page title verbatim. Root og:title has no suffix.
- Some descriptions are duplicated verbatim between `description` and `openGraph.description` (e.g. `/ocr` L6 vs L10); others are shortened in OG (e.g. `/compress`, `/merge`).

---

## 2. Root Layout (`frontend/src/app/layout.tsx`, 59 lines)

### 2.1 Font loading (L9-14, verbatim)

```ts
const dmSans = DM_Sans({
  variable: '--font-dm-sans',
  subsets: ['latin'],
  display: 'swap',
  preload: true,
});
```

`DM_Sans` imported from `next/font/google` (L2). `preload: true` and `display: 'swap'` were applied in STEP-F2-050 (`frontend/LIGHTHOUSE.md:121-124`).

### 2.2 Full metadata export (L16-41, verbatim)

```ts
export const metadata: Metadata = {
  title: {
    default: 'Papyr — Alat PDF Gratis untuk Indonesia',
    template: '%s | Papyr',
  },
  description:
    'Kompres, gabungkan, pisahkan, dan konversi PDF dengan mudah. Gratis, tanpa akun, dan menjaga privasi. Dibuat untuk pengguna Indonesia.',
  metadataBase: new URL('https://mypapyr.com'),
  openGraph: {
    type: 'website',
    locale: 'id_ID',
    siteName: 'Papyr',
    title: 'Papyr — Alat PDF Gratis untuk Indonesia',
    description:
      'Kompres, gabungkan, pisahkan, dan konversi PDF dengan mudah. Gratis, tanpa akun, dan menjaga privasi.',
    url: 'https://mypapyr.com',
    images: ['/og/papyr.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Papyr — Alat PDF Gratis untuk Indonesia',
    description:
      'Kompres, gabungkan, pisahkan, dan konversi PDF. Gratis, tanpa akun, auto-hapus 1 jam.',
    images: ['/og/papyr.png'],
  },
};
```
### 2.3 html lang, theme setup, providers (L43-59 render body, verbatim)

```tsx
<html lang="id" className={`${dmSans.variable} h-full antialiased`}>
  <body className="flex min-h-full flex-col font-sans">
    <Navbar />
    <main className="flex-1">{children}</main>
    <Footer />
    <Analytics />
    <SpeedInsights />
  </body>
</html>
```

- `lang="id"` on `<html>` (L49).
- No dark-mode toggle, no theme script, no CSS-variable inline `<style>` in the layout. **Discrepancy flag:** `LIGHTHOUSE.md:102-105` claims a "theme inline script" is already inlined in the layout; the current `layout.tsx` source contains no inline script (uncertainty — doc/code drift).
- Providers: `Analytics` from `@vercel/analytics/next` (L3, L54) and `SpeedInsights` from `@vercel/speed-insights/next` (L4, L55). No other Provider wrappers, no context providers, no `suppressHydrationWarning`.
- `./globals.css` imported at L7. Navbar (L51) and Footer (L53) wrap `<main>` (L52).

---

## 3. `frontend/src/app/globals.css` (45 lines)

- Tailwind v4 import: `@import 'tailwindcss';` (L1).
- **`@theme inline`** (not plain `@theme`) at L3-10, verbatim:

```css
@theme inline {
  --color-navy: #1e3a5f;
  --color-accent: #2563eb;
  --color-bg: #f9fafb;
  --color-background: #ffffff;
  --color-foreground: #171717;
  --font-sans: 'DM Sans', system-ui, sans-serif;
}
```

- Token summary: `navy #1e3a5f` (L4), `accent #2563eb` (L5), `bg #f9fafb` (L6), `background #ffffff` (L7), `foreground #171717` (L8), font stack `'DM Sans', system-ui, sans-serif` (L9). No other colors in @theme; the design additionally uses Tailwind palette classes inline (slate-*, rose-*, emerald-*, amber-*, green-*, red-*).
- `body` rules (L12-16): `background: var(--color-bg); color: var(--color-foreground); font-family: var(--font-sans);`
- Keyframes:
  - `shimmer` (L19-26): `background-position: -200% 0` → `200% 0`.
  - `fade-up` (L28-37): `from { opacity: 0; transform: translateY(10px); }` → `to { opacity: 1; transform: translateY(0); }`.
- Custom utilities (Tailwind v4 `@utility`, L39-45):
  - `animate-shimmer` → `animation: shimmer 1.4s ease-in-out infinite;` (L39-41)
  - `animate-fade-up` → `animation: fade-up 0.3s ease forwards;` (L43-45)
- No `@layer` blocks, no `prefers-color-scheme` media query, no dark scheme tokens, no `.dark` variant.

---

## 4. `frontend/src/app/sitemap.ts` (48 lines) — every URL verbatim

`BASE_URL = 'https://mypapyr.com'` (L3). `SITEMAP_TOOLS` (L5-19, verbatim): `/compress`, `/merge`, `/split`, `/rotate`, `/image-to-pdf`, `/pdf-to-image`, `/protect`, `/unlock`, `/watermark`, `/sign`, `/pdf-to-word`, `/ocr`, `/pdf-to-excel` (13 entries, `as const`).

Full emitted URL set (16 URLs), from L21-47:

| # | URL | changeFrequency | priority | line refs |
|---|---|---|---|---|
| 1 | `https://mypapyr.com` | `'weekly'` | `1` | L24-27 |
| 2-14 | `https://mypapyr.com/<tool>` — 13 tool URLs in SITEMAP_TOOLS order | `'monthly'` | `0.8` | L29-34 (map; `lastModified: new Date()` each) |
| 15 | `https://mypapyr.com/faq` | `'monthly'` | `0.5` | L35-40 |
| 16 | `https://mypapyr.com/privacy` | `'yearly'` | `0.3` | L41-46 |

Notes:
- Every entry sets `lastModified: new Date()` (runtime date, not fixed).
- `/faq` is NOT in `SITEMAP_TOOLS`; appended separately (L35-40).
- Order confirmed by `frontend/src/__tests__/seo-analytics.test.ts:47-64` ("returns 16 sitemap URLs: home, 13 tools, faq, privacy"; entries.at(-2)=faq, entries.at(-1)=privacy).

---

## 5. `frontend/src/app/robots.ts` (11 lines) — verbatim

```ts
import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
    },
    sitemap: 'https://mypapyr.com/sitemap.xml',
  };
}
```

- Single catch-all rule: `userAgent: '*'`, `allow: '/'` (L5-8). No `disallow` entries.
- Sitemap URL: `https://mypapyr.com/sitemap.xml` (L9).
---

## 6. OG image generators

### 6.1 `frontend/src/app/opengraph-image.tsx` (128 lines)

- `alt = 'Papyr — Alat PDF Gratis untuk Indonesia'` (L3).
- `size = { width: 1200, height: 630 }` (L5-8); `contentType = 'image/png'` (L10).
- Rendered via `next/og` `ImageResponse` (L1, L13). **Static brand image — NOT per-tool dynamic.** Content: gradient `linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)` (L16), logo tile + "Papyr" wordmark (L27-73), tagline `Alat PDF gratis untuk Indonesia` (L85), 4 feature pills `['Kompres', 'Gabungkan', 'Pisahkan', 'Konversi']` (L96), bottom line `mypapyr.com · Gratis · Tanpa akun · Auto-hapus 1 jam` (L121).
- Note: root metadata `images` explicitly reference static `/og/papyr.png` (layout.tsx L32, L39); route layouts reference static `/og/<tool>.png`. The dynamic `opengraph-image.tsx` is auto-discovered by Next.js but may be shadowed by the explicit metadata `images` (behavior not verified by a build — uncertainty).

### 6.2 `frontend/src/app/twitter-image.tsx` (128 lines)

- Byte-for-byte identical to `opengraph-image.tsx` (same alt, 1200x630, `image/png`, same gradient/content, same bottom line). Source L1-128.

### 6.3 Static OG assets (`frontend/public/og/`, 14 files)

`compress.png`, `image-to-pdf.png`, `merge.png`, `ocr.png`, `papyr.png`, `pdf-to-excel.png`, `pdf-to-image.png`, `pdf-to-word.png`, `protect.png`, `rotate.png`, `sign.png`, `split.png`, `unlock.png`, `watermark.png` — one per tool + brand `papyr.png`. No `faq.png`/`privacy.png`; those routes reference `/og/papyr.png`.

---

## 7. `frontend/next.config.ts` (7 lines) — verbatim, complete file

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
```

- **No `redirects`, no `rewrites`, no `headers`, no `images` config, no experimental options, no `output` setting.** All routing behavior is default App Router; the legacy frontend has no redirect/rewrite logic to port — URL migration strategy must be designed fresh for the rebuild.

---

## 8. `frontend/package.json` (52 lines)

### 8.1 scripts (L5-22, verbatim)

```json
"dev": "next dev",
"build": "next build",
"start": "next start",
"lint": "eslint",
"test": "vitest run",
"test:watch": "vitest",
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui",
"test:e2e:headed": "playwright test --headed",
"test:e2e:report": "playwright show-report",
"e2e:fixtures": "tsx e2e/fixtures/generate-fixtures.ts",
"format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css}\" \"e2e/**/*.ts\"",
"format:check": "prettier --check \"src/**/*.{ts,tsx,js,jsx,json,css}\" \"e2e/**/*.ts\"",
"analyze": "next experimental-analyze -o",
"analyze:ui": "next experimental-analyze",
"lhci": "lhci autorun"
```

### 8.2 dependencies (L23-34)

| Package | Version |
|---|---|
| `@dnd-kit/core` | `^6.3.1` |
| `@dnd-kit/sortable` | `^10.0.0` |
| `@dnd-kit/utilities` | `^3.2.2` |
| `@vercel/analytics` | `^2.0.1` |
| `@vercel/speed-insights` | `^2.0.0` |
| `next` | **`16.2.4`** (exact) |
| `pdf-lib` | `^1.17.1` |
| `pdfjs-dist` | `^5.7.284` |
| `react` | **`19.2.4`** (exact) |
| `react-dom` | **`19.2.4`** (exact) |

### 8.3 devDependencies (L35-51)

`@lhci/cli ^0.15.1`, `@playwright/test ^1.60.0`, `@tailwindcss/postcss ^4`, `@types/node ^20`, `@types/react ^19`, `@types/react-dom ^19`, `@vitest/coverage-v8 ^3.2.4`, `eslint ^9`, `eslint-config-next 16.2.4`, `eslint-config-prettier ^10.1.8`, `prettier ^3.8.3`, `tailwindcss ^4`, `tsx ^4.22.1`, `typescript ^5`, `vitest ^3.2.1`.

Related config: `tsconfig.json` alias `"@/*": ["./src/*"]` (L21-23); `postcss.config.mjs` = only `@tailwindcss/postcss`; `eslint.config.mjs` = `eslint-config-next/core-web-vitals` + `typescript` + `prettier`; `.prettierrc` = semi, singleQuote, tabWidth 2, trailingComma all, printWidth 100, endOfLine lf.
---

## 9. Navbar / Footer / OtherTools — links, aria, alt, lang state

### 9.1 `frontend/src/components/Navbar.tsx` (265 lines) — `'use client'` (L1)

- **NAV_CATEGORIES** exported (L83-117): 4 categories / 13 tools (order asserted by `navbar.test.ts:10-13`).
  - Alat Dasar (L85-92): `/compress` Kompres, `/merge` Gabungkan, `/split` Pisahkan, `/rotate` Putar
  - Keamanan (L94-99): `/protect` Proteksi, `/unlock` Hapus Password
  - Enhancement (L101-106): `/watermark` Watermark, `/sign` Tanda Tangan
  - Konversi (L108-116): `/image-to-pdf` Gambar ke PDF, `/pdf-to-image` PDF ke Gambar, `/pdf-to-word` PDF ke Word, `/pdf-to-excel` PDF ke Excel, `/ocr` OCR
- Logo link: `href="/"` (L148-160), text "Papyr" (L159).
- Desktop category triggers are `<button>`s (L168-181) with mouseenter+click toggling `openCategory`; closes on outside mousedown (L128-136) and on pathname change (L139-142).
- Desktop dropdown item links `<Link href={tool.href}>` (L186-197); active styling when `pathname === tool.href` (L190-193).
- Desktop CTA `href="/compress"` text `Coba Gratis` (L207-212); mobile CTA same href/text (L216-222).
- Mobile hamburger `<button aria-label={mobileOpen ? 'Tutup menu' : 'Buka menu'}>` (L223-229).
- Mobile menu uses native `<details>/<summary>` accordion per category (L238-259); item links L244-255.
- Icons: `FileIcon` (L9-25), `MenuIcon` (L27-44), `XIcon` (L46-62), `ChevronDownIcon` (L64-79) — inline SVG, no aria-hidden set (decorative; rely on adjacent text).
- **No `lang`/locale state in Navbar.**

### 9.2 `frontend/src/components/Footer.tsx` (229 lines) — `'use client'` (L1)

- **LanguageSwitcher** (L64-116): trigger `<button>` with GlobeIcon, text `🇮🇩 Indonesia` + chevron (L80-87). Dropdown (L89-113): active row `🇮🇩 Indonesia` + check icon (L91-105, not a link/button); `🇬🇧 English` row + `<span>Segera hadir</span>` badge (L106-111) — **decorative/disabled; no switching logic.** Closes on outside mousedown (L68-76).
- **FOOTER_TOOL_CATEGORIES** exported (L120-154) — same 4 categories / 13 tools as navbar (identical hrefs/labels; asserted by `footer.test.ts`).
- **FOOTER_LINKS** (L158-163): `{ href: '/privacy', label: 'Privasi' }`, `{ href: '/faq', label: 'FAQ' }`, `{ href: '#', label: 'Syarat' }`, `{ href: '#', label: 'Kontak' }` — **two dead links (`#`) for Terms and Contact; no `/terms` or `/contact` route exists.**
- Logo link `href="/"` (L201-206); copyright `© 2026` (L207).
- Footer tool grid links L182-187; bottom links L212-220.

### 9.3 `frontend/src/components/OtherTools.tsx` (69 lines) — server component (no `'use client'`)

- **ALL_TOOLS** (L25-39), 13 entries: `/compress` Kompres PDF, `/merge` Gabungkan PDF, `/split` Pisahkan PDF, `/rotate` Putar PDF, `/image-to-pdf` Gambar ke PDF, `/pdf-to-image` PDF ke Gambar, `/protect` Proteksi PDF, `/unlock` Hapus Password PDF, `/watermark` Tambah Watermark PDF, `/sign` Tanda Tangani PDF, `/pdf-to-word` PDF ke Word, `/pdf-to-excel` PDF ke Excel, `/ocr` OCR PDF.
- Props `{ currentTool: string }` (L43-45); filters current tool (L48); grid `Alat lainnya` (L51-66). No aria attributes; icons are inline SVG without text alternative.

### 9.4 Landing page (`frontend/src/app/page.tsx`, server)

- **TOOLS** exported (L360-452), 13 entries `{id, href, icon, name, desc}`. Hrefs: `/compress`, `/merge`, `/split`, `/image-to-pdf`, `/pdf-to-image`, `/rotate`, `/protect`, `/unlock`, `/watermark`, `/sign`, `/pdf-to-word`, `/ocr`, `/pdf-to-excel`. Asymmetric ids: `img-to-pdf` → `/image-to-pdf`, `pdf-to-img` → `/pdf-to-image` (asserted `landing-page.test.ts:101-114`).
- Hero CTA `href="/compress"` "Mulai gratis" (L510-515). Tool cards `<Link href={tool.href}>` (L547-562) with "Gunakan alat" affordance (L559-561).
- PRIVACY_ITEMS (L456-472): "Transfer aman", "Dihapus dalam 1 jam", "Tanpa penyimpanan". TRUST_BADGES (L476-480): "Tanpa akun", "Auto-hapus 1 jam", "Bisa di HP".
---

## 10. E2E coverage & Lighthouse

### 10.1 Playwright

- `frontend/playwright.config.ts` (39 lines): `testDir: './e2e'`, `baseURL: 'http://localhost:3000'`, projects **chromium / firefox / mobile-chrome (Pixel 5)** (L19-32), webServer `npm run dev` at localhost:3000 (L33-38), retries 2 in CI, trace/video on-first-retry.
- `frontend/e2e/smoke.spec.ts` (32 lines):
  - `TOOL_PATHS` (L3-17): all 13 tool routes.
  - Test "homepage loads successfully" (L20-24): goto `/`, title matches `/Papyr/`, first `h1,h2` visible.
  - Test "all 13 tool pages are accessible" (L26-31): each tool path returns HTTP 200.
- `frontend/e2e/client-tools.spec.ts` (204 lines) — 8 tests over 4 client-side tools (merge, split, rotate, sign):
  - **Merge** (L15-48): merge 2 PDFs → download event with `.pdf` filename; success `PDF berhasil digabungkan!`; button `Unduh PDF Gabungan`; negative: merge button disabled until ≥2 files; helper `Upload minimal 2 file PDF untuk menggabungkan.`
  - **Split** (L50-88): custom range `1-2` → download; negative: range `99-100` → `/melebihi total halaman dokumen/` and button disabled.
  - **Rotate** (L90-136): `Putar Semua 90°` then `/Putar \d+ halaman/`, success `PDF berhasil diputar!`, download; single-page 180° variant.
  - **Sign** (L138-203): draw→place→sign flow via canvas `aria-label="Area menggambar tanda tangan"`; buttons `Draw`, `Gunakan Tanda Tangan`, `Lanjut Tempatkan Signature`, `Tanda Tangani PDF`; success `/PDF Ditandatangani/`; negative: continue disabled with no placements.
  - Spec header (L10-13): **"There are no data-testid attributes on these pages"** — selectors rely on real Indonesian copy.
- `frontend/e2e/helpers.ts` (34 lines): `uploadPDF` (first `input[type="file"]`), `waitForDownloadButton` (L18-24, regex `Unduh PDF Gabungan|Unduh PDF|Download Ulang|Download`), `verifyToolPageLoads` (L29-33).
- `frontend/e2e/fixtures/generate-fixtures.ts` (48 lines): generates 3-page `sample.pdf` (595x842 pt, Helvetica) and 1-page `single-page.pdf` via pdf-lib.
- `frontend/e2e/COVERAGE.md` (110 lines): **18 frontend Vitest files / 530 tests, all pass** (L21); backend **208 pytest tests** (L34); e2e **10 unique tests** (2 smoke + 8 client-side) × 3 browsers = 30 invocations (L47, L56-58); CI = 5 jobs (frontend-lint, frontend-test, frontend-build, backend-lint, backend-test), **no e2e job in CI by design** (L61-72); server-side E2E (STEP-F2-043) and hybrid/navigation E2E (STEP-F2-044) **skipped by user request** (L96-107).

### 10.2 Lighthouse

- `frontend/lighthouserc.js` (35 lines): collect URLs `/`, `/compress`, `/merge`, `/protect`, `/pdf-to-word` (L14-20); `numberOfRuns: 3` (L23); assertions (L26-31): performance `['warn', { minScore: 0.9 }]`, accessibility `['error', { minScore: 0.95 }]`, seo `['error', { minScore: 0.95 }]`, best-practices `['warn', { minScore: 0.9 }]`; upload `temporary-public-storage` (L33).
- `frontend/LIGHTHOUSE.md` (142 lines): thresholds table (L34-44) mirrors config; `/pdf-to-word` chosen as representative async page (L46-49). **No actual Lighthouse scores recorded** — full runs intentionally deferred to CI/non-laptop (L5-10, L140-142). Bundle snapshot 2026-05-17 (L63-80): total client chunks ~1.76 MB uncompressed; top chunks `042pvwmmlu8~n.js` ~424 KB (PDF.js worker), `0-gdq1_osscot.js` ~416 KB (PDF rendering core). STEP-F2-050 audit (L110-130): pdfjs-dist already lazy (`await import('pdfjs-dist')` in `components/PDFPageViewer.tsx` L93 and `components/WatermarkPreview.tsx` L37); pdf-lib named-import only; @dnd-kit code-split per route; one raw `<img>` left at `app/image-to-pdf/page.tsx:312` (blob URL); DM_Sans display/preload applied.
---

## 11. i18n artifacts

### 11.1 In code (frontend/src)

- **`<html lang="id">`** — `frontend/src/app/layout.tsx:49`.
- **openGraph `locale: 'id_ID'`** — `frontend/src/app/layout.tsx:26`.
- **Footer `LanguageSwitcher`** — `frontend/src/components/Footer.tsx:64-116`. Visual-only: `🇮🇩 Indonesia` active (L85, L92); `🇬🇧 English` with badge `Segera hadir` (L107-110). **No switching behavior, no router integration, no stored preference.**
- **OCR language option** (NOT a UI-locale feature — it is the OCR engine language): `type OcrLanguage = 'ind' | 'eng' | 'ind+eng'` (`frontend/src/app/ocr/page.tsx:14`); labels via `getLanguageLabel` (`page.tsx:197-206` and `logic.ts:14-23`): `'Bahasa Indonesia'`, `'English'`, `'Indonesia + English'`; `LANGUAGE_OPTIONS: OcrLanguage[] = ['ind', 'eng', 'ind+eng']` (`page.tsx:208`, `logic.ts:9`).
- **No `next-intl`, no i18n config, no middleware**: `frontend/package.json` has no i18n dependency; repo-wide grep for `next-intl|i18n|useTranslations|IntlProvider|locale` matched only `frontend/src/app/layout.tsx:26` (locale id_ID), `frontend/package-lock.json`, and planning docs/stepprompts. No `frontend/src/middleware.*` file exists (glob: no files).
- **Hardcoded-language pattern**: all UI copy is hardcoded Bahasa Indonesia inline (no string-table/translation module). Examples: `MESSAGES` in `frontend/src/components/PrivacyNotice.tsx:28-33`; validation strings in `lib/pdfUtils.ts` (e.g. `'Pilih minimal 1 halaman untuk diputar.'` L23). The only English UI strings are the OCR labels `'English'`/`'Indonesia + English'` (`ocr/page.tsx:202-204`) and the footer `English` row (Footer.tsx:107).

### 11.2 In docs (design intent)

- `docs/19_Papyr_UIUX_Spec_v1.0.md`: L109 `HTML lang="id" pada root element`; L112 `Language switcher di footer (Indonesia aktif, English "Segera hadir")`; L331-333 dropdown `bottom-full` + `English: Disabled dengan badge "Segera hadir"`; L702 `Language switcher: Indonesia (aktif), English (segera hadir)`; L931 `Language switcher | <button> trigger`; L941 `HTML lang | lang="id"`; L1287 `lang="id", locale id_ID`. (Spec line numbers are as-is in the current file; re-verify if the doc is re-read.)

---

## 12. Legacy URL / domain evidence

### 12.1 Canonical domains

| Domain | Where found | Role |
|---|---|---|
| `mypapyr.com` | root metadata (layout.tsx:23,31); sitemap.ts:3; robots.ts:9; README L8/93/154/167/339; CHANGELOG L100/147/162/492/502; docs | Production frontend domain (Hostinger DNS → Vercel) |
| `www.mypapyr.com` | `deploy/.env.production.example:20` (`ALLOWED_ORIGINS=https://mypapyr.com,https://www.mypapyr.com`); stepprompts L2186, L3104 | Backend CORS allowlist includes www variant |
| `api.mypapyr.com` | nginx production.conf L29/46/49-50; README L21/42/154/165; CHANGELOG L13/61/101; stepprompts passim | Backend API (Linode VPS Jakarta, Cloudflare-proxied, Let's Encrypt origin cert) |
| `frontend-ten-omega-35.vercel.app` | README L164; CHANGELOG L498 | Legacy Vercel URL (pre-custom-domain) |
| `localhost:3000` / `localhost:8000` | `lib/config.ts:13,16` (defaults); playwright baseURL; README L224/235/247 | Local dev defaults |

### 12.2 nginx

- `deploy/nginx/conf.d/default.conf` (7 lines): catch-all server, `listen 80 default_server`, `server_name _;`, `return 444;`.
- `deploy/nginx/conf.d/production.conf` (149 lines): `server_name api.mypapyr.com` on port 80 (L27-41, HTTP→HTTPS 301) and 443 (L43-148). Rate limits `papyr_api:10m rate=30r/m` (L6), `papyr_burst:10m rate=2r/s` (L7). Bad-bot UA map (L10-16), blocked-path map (L19-25), Cloudflare real-IP (L59-75), `client_max_body_size 25M` (L85), security headers (L90-95). Locations: `/health` (L98-104), `/test/connectivity` (L107-112), `/api/` (L115-133, rate-limited, proxy `http://backend:8000`, 300s timeouts, `proxy_buffering off`), `/status/` (L136-143, used by `useAsyncTask`), catch-all `return 444` (L146-148). **No frontend static serving / no frontend server_name — the frontend is Vercel-hosted.**
### 12.3 env files

- `.env.example` (41 lines): frontend keys `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` (L5; **unused in frontend/src — legacy leftover, uncertainty**), `NEXT_PUBLIC_SITE_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` (L4-10); backend keys R2 (L17-21), `CORS_ORIGINS` (L24), `MAX_UPLOAD_SIZE_MB=20` (L27), `FILE_RETENTION_MINUTES=60` (L28), `RATE_LIMIT_PER_MINUTE=10` (L29), Supabase standby (L32-33), `SENTRY_DSN` (L36), `HOSTINGER_API_TOKEN` (L41).
- `deploy/.env.production.example` (29 lines): `R2_BUCKET_NAME=papyr-files` (L17), `ALLOWED_ORIGINS=https://mypapyr.com,https://www.mypapyr.com` (L20), `RATE_LIMIT_PER_MINUTE=10` (L23), `MAX_UPLOAD_SIZE_MB=20` (L24), `FILE_RETENTION_MINUTES=60` (L25), `ENVIRONMENT=production` (L28).
- Frontend runtime config `frontend/src/lib/config.ts`: `apiUrl: clean(process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000')` (L13), `siteUrl: clean(process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000')` (L16), Supabase standby (L19-20); `limits` (L24-38): maxUploadBytes 20MB, maxUploadMB 20, fileRetentionMinutes 60, allowedPdfMimeTypes `['application/pdf']`, allowedImageMimeTypes `['image/jpeg','image/png','image/webp']`. No `.env.local` committed (glob: none).

### 12.4 CI workflows

- `.github/workflows/ci.yml` (139 lines): 5 jobs on push/PR to `main`+`develop`; frontend-build env `NEXT_PUBLIC_API_URL: https://api.example.com`, `NEXT_PUBLIC_SITE_URL: https://mypapyr.com` (L84-85); Node 20, python 3.11, `ruff==0.7.4` pinned (L102). No frontend deploy step (Vercel handles it).
- `.github/workflows/deploy-vps.yml` (210 lines): builds/pushes `ghcr.io/fazulfi/papyr-backend:latest` / `:sha` (L98-99) to VPS `/opt/papyr/production` via SSH; compose services `backend nginx` (L158); smoke polls `http://localhost/health` through nginx (L174); rollback on failure (L186-196). Repo: `fazulfi/papyr` (README L214, CHANGELOG L492).

### 12.5 API endpoints used by the frontend (URL-migration input)

| Tool | API call | Source |
|---|---|---|
| compress | `POST ${config.apiUrl}/api/compress` via PDFUploader `endpoint`; `?quality=ebook` appended at PDFUploader.tsx:303 | `app/compress/page.tsx:112` |
| image-to-pdf | `POST ${config.apiUrl}/api/image-to-pdf` (server fallback >3MB) | `app/image-to-pdf/page.tsx:503` |
| pdf-to-image | `POST ${config.apiUrl}/api/pdf-to-image` | `app/pdf-to-image/page.tsx:314` |
| protect | `POST ${config.apiUrl}/api/protect` (XHR) | `app/protect/page.tsx:261` |
| unlock | `POST ${config.apiUrl}/api/unlock` (XHR) | `app/unlock/page.tsx:244` |
| watermark | `POST ${config.apiUrl}/api/watermark` (XHR) | `app/watermark/page.tsx:310` |
| pdf-to-word | async: `useAsyncTask(`${config.apiUrl}/api/pdf-to-word`, { statusBaseUrl: `${config.apiUrl}/api` })`; direct fetch fallback | `app/pdf-to-word/page.tsx:202-203, 294` |
| ocr | async: `useAsyncTask(`${config.apiUrl}/api/ocr`, ...)`; direct fetch fallback | `app/ocr/page.tsx:245-246, 337` |
| pdf-to-excel | async: `useAsyncTask(`${config.apiUrl}/api/pdf-to-excel`, ...)`; direct fetch fallback | `app/pdf-to-excel/page.tsx:212-213, 308` |
| merge / split / rotate / sign | no API — client-side pdf-lib | imports of `lib/pdfUtils.ts` |
---

## 13. Accessibility-relevant component evidence

### 13.1 PDFUploader (`frontend/src/components/PDFUploader.tsx`, 537 lines, `'use client'`)

- Upload zone: `<div role="button" tabIndex={0}>` (L356-358) with onKeyDown Enter/Space → file picker (L360-362); drag/drop handlers (L363-368). Hidden `<input type="file" accept=".pdf" className="hidden">` (L373-378). **No aria-label on the input; the wrapper div has `role="button"` but no explicit accessible name** (visible copy `Seret PDF ke sini / atau klik untuk upload`, L383-387, gives an implicit label).
- Validation messages (L207-221): `'Tipe file tidak valid. Hanya file PDF yang diterima.'`, `'File kosong.'`, `` `Ukuran file terlalu besar. Maksimal ${maxSizeMB}MB.` ``.
- State branches: idle (L352-394), uploading (L396-422, progress `Mengunggah... ${progress}%`), processing (L424-448, `Sedang mengompres...` shimmer), done (L450-515: before/after sizes + saved % + `<a href={result.download_url} download>` L495-502 + reset button L505-512), error (L517-533: `Terjadi Kesalahan` + message + `Coba Lagi`).
- Retry: first failure auto-retries after 1s (L226-232); second shows error (L233-238). 429 → `'Terlalu banyak permintaan. Coba lagi dalam 1 menit.'` (L270). 4xx → `body.detail || 'File terlalu besar untuk diproses.'` (L277). XHR timeout 120000ms (L304).

### 13.2 PasswordInput (`frontend/src/components/PasswordInput.tsx`, 184 lines, `'use client'`)

- Exported pure helpers: `calculatePasswordStrength` (L16-23, score 0-4: length≥8, uppercase, digit, special), `getPasswordStrengthLevel` (L25-29: ≥3 strong, 2 medium, else weak).
- Inputs: `aria-label="Password"` (L133), `aria-label="Konfirmasi password"` (L162); visible `<label>` elements also present (L121, L150).
- Show/hide toggles: `aria-label={showPassword ? 'Sembunyikan password' : 'Tampilkan password'}` (L135-142); confirm variant (L164-175).
- Strength indicator `<div aria-label="Password strength indicator">` (L72) + text `Kekuatan password: Kuat/Sedang/Lemah` (L90).
- Error text: `Minimal 4 karakter` (L146 — **hardcoded; note prop `minLength = 4` default L102 but the message is not interpolated**), `Password tidak cocok` (L178).
- Invalid styling: `border-rose-400 focus:ring-rose-200` (L130, L159).

### 13.3 PageRangeInput (`frontend/src/components/PageRangeInput.tsx`, 164 lines, `'use client'`)

- Proper label pairing: `<label htmlFor="page-range">Halaman yang diambil</label>` + `<input id="page-range" type="text">` (L109-123); placeholder `Contoh: 1-3, 5, 7-10` (L117).
- Error surfaced as `<p className="mt-2 text-xs font-medium text-rose-500">{result.error}</p>` (L129) — **plain text node; no `role="alert"`/`aria-live`**. Error strings (L27-88): `'Gunakan angka, tanda hubung, dan koma saja.'`, `` `Rentang tidak valid: "${part}".` ``, `'Rentang tidak valid: angka awal harus lebih kecil dari angka akhir.'`, `` `Halaman ${n} melebihi total halaman dokumen (${totalPages}).` ``, `` `"${part}" bukan nomor halaman yang valid.` ``.
- Live preview `<p>`: `Halaman yang dipilih: 1, 2 (2 halaman)` (L132-136). Quick-select buttons (L140-160): `Halaman Pertama`, `Halaman Terakhir`, `Semua Halaman`.

### 13.4 useAsyncTask (`frontend/src/hooks/useAsyncTask.ts`, 204 lines)

- Polling hook: submit → poll `${normalizedStatusBaseUrl}/status/${taskId}` every `pollingIntervalMs` (default 3000, L32) until `timeoutMs` (default 180000, L32).
- User-facing error strings (Indonesian): timeout `'Konversi timeout setelah 3 menit. Coba lagi dengan file lebih kecil.'` (L71); failed `data.error || 'Konversi gagal.'` (L103); poll failure `'Gagal memeriksa status konversi.'` (L120); submit failure `err.message || 'Gagal mengirim file.'` (L178); missing task_id `'Server tidak mengembalikan task_id.'` (L154).
- No DOM/a11y surface; statuses `idle | submitting | queued | processing | done | failed | timeout` (L12).

### 13.5 PrivacyNotice (`frontend/src/components/PrivacyNotice.tsx`, 44 lines, `'use client'`)

- Static `<div>` with shield SVG + `<p>{MESSAGES[model]}</p>` (L37-42). **No aria-live, no role, no link** to the privacy page. `MESSAGES` (L28-33): server → `'File kamu otomatis dihapus setelah 1 jam. Kami tidak pernah menyimpan dokumenmu.'`; client → `'File tidak pernah meninggalkan perangkatmu. Semua proses berjalan di browser.'`; hybrid → `'File kecil diproses di browser. File besar dikirim ke server dan otomatis dihapus dalam 1 jam.'`.
### 13.6 Supporting components (brief)

- **PDFPageViewer** (`components/PDFPageViewer.tsx`, 220 lines): canvas `aria-label={`Preview halaman ${currentPage} PDF`}` (L186); prev/next `<button>`s with disabled logic (L198-216, text `Sebelumnya`/`Berikutnya`); error `'Gagal menampilkan halaman PDF. Pastikan file PDF valid.'` (L148); exports `clampPage` (L39-42).
- **SignaturePad** (`components/SignaturePad.tsx`, 487 lines): canvas `aria-label="Area menggambar tanda tangan"` + `role="img"` (L460-461); toolbar buttons with aria-labels (`Warna Hitam`/`Warna Biru` L366, `Ketebalan 2px` L388, `Undo goresan terakhir` L417, `Hapus semua goresan` L429) + `aria-pressed` (L367, L389); save disabled when blank (L479); hint `Tanda tangan di sini...` (L446).
- **SignaturePlacementOverlay** (`components/SignaturePlacementOverlay.tsx`, 385 lines): container `aria-label={`Overlay penempatan tanda tangan halaman ${currentPage}`}` (L255); placement box `role="button" tabIndex={0}` + `aria-label={`Signature ${index + 1} di halaman ${currentPage}`}` (L286-288); **keyboard support: ArrowLeft/Right/Up/Down move placement by 0.01** (L301-330); resize handles `aria-label={`Ubah ukuran dari sudut ${corner}`}` (L357).
- **SignatureType** (`components/SignatureType.tsx`, 214 lines): labeled text input inside `<label>` (L112-121), font `<select>` (L124-140), color swatches with aria-label + aria-pressed (L146-159); error `'Gagal membuat preview tanda tangan. Coba lagi.'` (L88).
- **SignatureUpload** (`components/SignatureUpload.tsx`, 264 lines): hidden input `aria-hidden="true"` (L163-170); upload zone `role="button" tabIndex={0}` + `aria-label="Upload gambar tanda tangan (PNG atau JPG, maks 1MB)"` (L174-179); error `'Gagal memproses gambar. Silakan coba lagi.'` (L135).
- **WatermarkConfig** (`components/WatermarkConfig.tsx`, 208 lines): labeled controls via `<label>` wrappers; color input `aria-label="Warna watermark"` (L124); slider rows label-wrap pattern (L43-63).
- **WatermarkPreview** (`components/WatermarkPreview.tsx`, 255 lines): canvas `aria-label="Preview halaman pertama PDF"` (L214); overlay `<svg aria-hidden="true">` (L218); error `'Preview PDF gagal dibuat. Pastikan file PDF tidak rusak.'` (L149).
- **FAQ accordion** (`app/faq/page.tsx`): toggle is `<button onClick={onToggle}>` (L105-111) — **no `aria-expanded`, no `aria-controls`** (a11y gap).
- **Sign page upload** (`app/sign/page.tsx:358-391`): `role="button" tabIndex={0}` + `aria-label="Upload PDF untuk ditandatangani"` (L370-372); hidden input `aria-hidden="true"` (L383).
- **Merge/image-to-pdf upload zones** (`app/merge/page.tsx:560-575`, `app/image-to-pdf/page.tsx:649-665`): `role="button" tabIndex={0}` with Enter/Space keydown, **no aria-label** (implicit from visible copy).

### 13.7 Cross-cutting a11y patterns

- **Buttons vs links**: navigation/CTAs use `next/link`; in-flow actions (upload, convert, reset, toggle) use `<button type="button">`. Download in PDFUploader done-state is `<a href={download_url} download>` (PDFUploader.tsx:495-502); client-side tool downloads are `<button>`s triggering `downloadPDF()` programmatic `<a>` (pdfUtils.ts:240-254).
- **Input labels**: `PageRangeInput` is the only component using explicit `htmlFor`/`id` pairing (L109-114). Others use wrapping `<label>` (PasswordInput, SignatureType, WatermarkConfig) or `aria-label` (PasswordInput inputs).
- **Error message pattern**: red `<p>` text (rose-500) with **no `role="alert"`/`aria-live` anywhere**; error panels are rose-200/rose-50 divs with heading `Terjadi Kesalahan`.
- **Focus handling**: upload zones are `tabIndex={0}` + Enter/Space; placement overlay supports arrow-key nudge; dropdowns close on outside mousedown (Navbar L128-136, Footer L68-76) but have **no Escape-key close, no focus trap**; mobile menu uses native `<details>`.
- **Alt texts**: `<img>` alts are file-name or descriptive (`alt={item.file.name}` image-to-pdf:312; `alt="Preview tanda tangan"` SignaturePlacementOverlay:335, SignatureType:175, SignatureUpload:209; `alt="Preview gambar watermark"` WatermarkPreview:242).

---

## Uncertainties & open questions

1. `LIGHTHOUSE.md:102-105` claims a "theme inline script" is inlined in the layout; the actual `layout.tsx` (L43-58) contains no inline script — doc/code drift possible.
2. `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` in `.env.example:5` is not referenced anywhere in `frontend/src` (legacy leftover, likely unused).
3. `opengraph-image.tsx`/`twitter-image.tsx` are auto-discovered by Next.js, but all metadata `images` explicitly point at static `/og/*.png`; whether the dynamic ImageResponse files actually serve meta images was not verified by a build (read-only inspection).
4. Only 7 of 15 routes pin `openGraph.url`; the rest rely on `metadataBase`. Rendered `og:url` values not verified at build/runtime.
5. `Footer` `Syarat`/`Kontak` links are `href="#"` placeholders; no `/terms` or `/contact` route exists.
6. `docs/19_Papyr_UIUX_Spec_v1.0.md` line numbers cited as-is from the current file; re-verify if re-read.
7. OCR "language" strings (`English`, `Indonesia + English`) are OCR-engine options, not UI-locale strings — out of scope for i18n migration decisions.

## Verification

- Output file exists and is non-empty (this file).
- `git -C <workspace-root>\papyr-reference status --porcelain` returned empty before and after the exploration (verified 2026-07-31).
- No commands modified `papyr-reference/`; all reads were read-only.
