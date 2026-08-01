# Papyr UI/UX & Brand Documentation vs. Frontend Implementation — Reconciliation Audit

- **Date**: 2026-07-31
- **Auditor**: subagent (codebase search specialist), delegated by Sisyphus
- **Scope**: Claim-by-claim reconciliation of `docs/19_Papyr_UIUX_Spec_v1.0.md` and `docs/32_Papyr_Brand_Guidelines_v1.0.md` against the current frontend implementation in `papyr-reference/`, read-only. Actual code is the authority. No spec writing, no implementation.
- **Primary deliverable**: this file, `audit-outputs/ui-docs-code-reconciliation.md`.
- **Method**: Static source inspection only. Read/Glob/Grep for evidence. No browser, no build, no runtime, no git operations. `papyr-reference/` was only read, never modified.
- **Tool deviation note**: The subagent toolset exposed no Write/Edit tool, so this deliverable file was created with bash heredoc writes (the only file-write shell use; no other shell operations were performed). All other investigation used Read/Glob/Grep per the delegation constraints.
- **Line citations**: `Doc19 L<line>` / `Doc19 §<section>` refer to `papyr-reference/docs/19_Papyr_UIUX_Spec_v1.0.md`; `Doc32 §<section>` refers to `papyr-reference/docs/32_Papyr_Brand_Guidelines_v1.0.md`. Code paths are relative to `papyr-reference/` (e.g., `frontend/src/app/page.tsx:497`).
- **Related artifact**: `audit-outputs/ui-five-tools-audit.md` (2026-07-31) contains a complementary page-by-page UX audit of the five launch tools. This reconciliation focuses on documentation claims vs. code, not on UX quality.

---

## 1. Executive Summary

1. **Design token layer is highly accurate.** Every color token, font setting, spacing token, radius, shadow, and animation keyframe documented in both docs matches `globals.css` and the components exactly. This is the strongest, safest material for the future canonical spec.
2. **Component specifications are largely accurate.** PDFUploader, PageRangeInput, PrivacyNotice, accordion, sortable merge/image items, rotate grid, and the done/error/processing state cards match their documented classes nearly to the pixel.
3. **Catalog and navigation claims are the most stale.** Both docs describe a 6-tool Papyr with 6 flat navbar links; the code implements **13 tools**, a **4-category dropdown navbar**, a **1440px navbar container** (docs say 1200px), a footer **tools directory section**, a **13-card landing grid** (doc says 6), and an **OtherTools grid of 12 cards** (doc says 5).
4. **Seven tools and several components are entirely missing from both docs**: Protect, Unlock, Watermark, Sign, PDF-to-Word, PDF-to-Excel, OCR, plus PasswordInput, the signature suite (SignaturePad/Upload/Type/PlacementOverlay), the watermark suite (WatermarkConfig/Preview), and PDFPageViewer.
5. **The docs' own improvement recommendations remain unimplemented** (dark mode, skip link, aria-live, progressbar roles, reduced motion, undo, batch download, etc.), so Doc19 §10 and the a11y recommendations read as an unchanged roadmap, not as stale claims.
6. **Historical-only content is concentrated in market/language claims**: Indonesia-first positioning, Indonesian-only copy rules, and the OpenClaw-managed Twitter/X presence (Doc32 §11, §13). These are superseded by rebuild decisions DEC-002/003/004/016/021/028 and have no code counterpart for the social media claims.
7. **Several internal self-inconsistencies** exist in Doc19 (e.g., §3.3 says PDFUploader serves PDF-to-Image, but only Compress uses it; §5.4 lists Syarat/Kontak footer links that are dead `href="#"` with no routes; §8.2's upload-zone keyboard pattern does not hold for the Rotate page, which the doc itself documents).

---

## 2. Files Inspected (Evidence Base)

### Docs under reconciliation
| File | Lines | Role |
|---|---|---|
| `papyr-reference/docs/19_Papyr_UIUX_Spec_v1.0.md` | 1305 | UI/UX spec (Jun 2025, Draft-to-Approved) |
| `papyr-reference/docs/32_Papyr_Brand_Guidelines_v1.0.md` | 978 | Brand guidelines (2026-06-03, Approved) |
| `papyr-reference/CHANGELOG.md` | 553 | Code-state dating context (2.0.0, 2026-05-20 VPS migration) |
| `papyr-rebuild-decisions.md` | 621+ | Accepted rebuild decisions (DEC-001…049) used for supersession context |

### Frontend implementation (all under `papyr-reference/frontend/`)
| File | Purpose in verification |
|---|---|
| `src/app/globals.css` (45) | Tokens, keyframes, animate-shimmer/fade-up utilities |
| `src/app/layout.tsx` (59) | DM Sans, lang="id", antialiased, Navbar/main/Footer, Vercel Analytics + SpeedInsights |
| `src/app/page.tsx` (596) | Landing: hero, tools grid (13 cards), privacy section, all 13 tool icons |
| `src/components/Navbar.tsx` (265) | Category dropdowns, 1440px container, logo, CTAs, mobile accordion |
| `src/components/Footer.tsx` (229) | Tools directory (4 categories), bottom bar, LanguageSwitcher, dead links |
| `src/components/PDFUploader.tsx` (537) | Compress-only uploader: states, XHR progress, auto-retry, quality=ebook |
| `src/components/PageRangeInput.tsx` (164) | Range parser + quick selects |
| `src/components/PrivacyNotice.tsx` (44) | Three model messages |
| `src/components/OtherTools.tsx` (69) | 13-tool cross-nav grid |
| `src/app/compress/page.tsx` (138), `merge/page.tsx` (687), `split/page.tsx` (569), `image-to-pdf/page.tsx` (767), `pdf-to-image/page.tsx` (579), `rotate/page.tsx` (629) | The six Doc19-covered tool pages |
| `src/app/faq/page.tsx` (164), `src/app/privacy/page.tsx` (105) | Content pages |
| `src/app/protect/page.tsx` (552), `unlock/page.tsx`, `watermark/page.tsx`, `sign/page.tsx`, `ocr/page.tsx`, `pdf-to-word/page.tsx`, `pdf-to-excel/page.tsx` | The seven undocumented tools (headers/patterns verified; sign success variant at `sign/page.tsx:606`) |
| `src/app/{13 tools}/layout.tsx` + `sitemap.ts` + `robots.ts` + `opengraph-image.tsx` + `twitter-image.tsx` | SEO/metadata layer |
| `src/lib/config.ts` (39), `src/lib/pdfUtils.ts` (255), `src/lib/analytics.ts` (69) | Limits, client-side PDF logic, analytics events |
| `package.json` (52) | deps: dnd-kit, pdf-lib, pdfjs-dist, Tailwind v4, no icon library |
| `backend/routers/compress.py`, `backend/services/compress_service.py`, `backend/services/pdf_to_image_service.py`, `backend/Dockerfile` | Ghostscript + PyMuPDF claims |

### Greps performed
`role="button"` (10 pages + PDFUploader; **not** rotate), `aria-label` (13 matches), `PrivacyNotice model=` (13 tools: server 6 / client 4 / hybrid 2), `title:|description:` in all tool layouts, `skip|aria-live|progressbar|focus-visible|prefers-reduced-motion` (one focus-visible in SignaturePlacementOverlay only), `OpenClaw|twitter.com` (none in frontend), `PyMuPDF|fitz` (backend), `ghostscript|quality` (backend), `import PDFUploader` (only compress).

---

## 3. Claim-by-Claim — `docs/19_Papyr_UIUX_Spec_v1.0.md`

Verdict classes: **Accurate/current** (matches code today), **Stale** (was true, implementation changed), **Contradicted** (code disagrees), **Missing** (implementation exists, doc never covers it), **Historical-only** (describes a superseded state).

### 3.1 Accurate / current

| Doc claim | Code evidence |
|---|---|
| §1.1 L69-72 mobile-first: `max-w-xl` tool container, `px-4`, `sm:`/`md:` breakpoints | `frontend/src/app/compress/page.tsx:94` (identically `merge:469`, `split:357`, `image-to-pdf:555`, `pdf-to-image:365`, `rotate:398`); `px-4` throughout |
| §1.2 L78-82 PrivacyNotice 3 variants + shield icon | `frontend/src/components/PrivacyNotice.tsx:26-33` (messages verbatim), `:9-24` (shield); badges "Auto-hapus 1 jam"/"Tanpa akun" `frontend/src/app/page.tsx:477-480`; privacy section 3 pillars `page.tsx:456-472` |
| §1.3 L88-92 `animate-fade-up` 0.3s, shimmer, real-time upload %, states idle→uploading→processing→done | `globals.css:39-44`; `PDFUploader.tsx:251-256` (XHR progress), `:412` ("Mengunggah... X%") |
| §1.4 L98-102 aria-labels, semantic HTML, navy contrast claim | `Navbar.tsx:226`; `merge/page.tsx:324`; `layout.tsx:50-53`; navy `#1e3a5f` `globals.css:4` (ratio plausible but not re-measured — see Uncertainties) |
| §1.5 L108-113 `lang="id"`, all-Indonesian copy, WhatsApp/portal examples, footer language switcher, OG locale `id_ID` | `layout.tsx:49`, `:26`; `compress/page.tsx:105-107`; `Footer.tsx:64-116` |
| §1.6 L119-123 one-task-per-page, upload zone focal, linear flow, OtherTools below | All tool pages; `OtherTools` imported at the bottom of every tool page |
| §2.1 L131-152 typography: DM Sans via next/font, `--font-dm-sans`, fallback, `antialiased`, latin subset; type scale (hero clamp, tool H1 30/36px, content H1 24/30px) | `layout.tsx:9-14,49`; `globals.css:9`; `page.tsx:497` (`text-[clamp(40px,6vw,72px)] font-semibold leading-[1.08] tracking-[-2px] text-navy`); `compress/page.tsx:100` (`text-3xl ... md:text-4xl font-bold tracking-tight text-navy`); `faq/page.tsx:133`, `privacy/page.tsx:12` (`text-2xl ... sm:text-3xl`) |
| §2.2 L156-198 palette: five hex tokens; slate roles; semantic rose/emerald; accent tints 5/10/15/20/30/50/60 | `globals.css:4-8` (all five exact); `PDFUploader.tsx:454,517-524`; `page.tsx:550,582`; `PDFUploader.tsx:369-371` |
| §2.3 L202-223 spacing scale | Spot-verified: `px-4` tool pages, `py-14` upload zones (`PDFUploader.tsx:369`), `mb-8` tool headers (`compress:96`), `mt-16` OtherTools (`OtherTools.tsx:51`), `gap-1.5` pill (`page.tsx:490`), `py-8 sm:py-12` tool pages |
| §2.4 L227-234 radii | `Navbar.tsx:156` (`rounded-md` logo), `page.tsx:550` (`rounded-[10px]` tool card), upload `rounded-2xl` (`PDFUploader.tsx:369`), pills `rounded-full`, inputs `rounded-xl` |
| §2.5 L238-246 shadows incl. three custom accent shadows | `page.tsx:550` (`0_1px_3px_rgba(0,0,0,0.04)` + hover `0_4px_20px_rgba(37,99,235,0.1)`); `PDFUploader.tsx:454` (`0_4px_20px_rgba(37,99,235,0.06)`), `:498` (`0_2px_12px_rgba(37,99,235,0.25)`) |
| §2.6 L250-259 animations | `globals.css:19-44` (shimmer 1.4s ease-in-out infinite; fade-up 0.3s ease forwards); accordion `duration-200` `faq/page.tsx:113`; `hover:-translate-y-0.5` `page.tsx:512` |
| §2.7 L263-272 iconography: inline SVG, no library, stroke 1.6–2.0 standard / 1.7–1.8 tool icons, tool header 21px, upload 26px, currentColor | `package.json:23-34` (no icon dependency); tool icons `strokeWidth="1.8"` `page.tsx:121`; header icons 21px `compress:14`; upload 26px `PDFUploader.tsx:33` |
| §3.1 L286-309 navbar basics: sticky top-0 z-50, h-[52px], bg-bg/92 blur, border-b slate-200, logo h-7 w-7 + text-[17px], CTA "Coba Gratis", mobile mini CTA px-3.5 py-1.5 text-[13px], hamburger aria-label, auto-close on route change | `Navbar.tsx:145-146,156-160,207-229` |
| §3.2 L311-333 footer: bg-bg, border-t, bottom bar 1200px px-6 py-10, link text-[13px] font-medium slate-500, copyright text-[13px] slate-300; LanguageSwitcher bottom-full, Indonesia active + check, English disabled + "Segera hadir" | `Footer.tsx:169,198-220`; `Footer.tsx:89-112` |
| §3.3 L335-374 PDFUploader props, state machine, drag visual, client validation, XHR progress, 120s timeout, auto-retry 1s | `PDFUploader.tsx:19-27,164-172,207-241,248-305,352-371` |
| §3.4 L376-408 PageRangeInput (props, classes, quick selects, validation) | `PageRangeInput.tsx:7-10,106-163` — label, input, focus `border-accent ring-1 ring-accent/20`, error `border-rose-400`, helper, accent preview, rose error msg, three quick selects, validation rules (digits/hyphens/commas/spaces; start <= end; bounds; live preview) |
| §3.5 L410-435 PrivacyNotice classes + three messages | `PrivacyNotice.tsx:28-43` — verbatim match |
| §3.7 L463-485 upload zone pattern | `PDFUploader.tsx:369-371`; identical on merge/split/image-to-pdf/pdf-to-image pages |
| §3.8 L487-503 feature badge card | `compress/page.tsx:122-133`, `merge/page.tsx:665-675` (`rounded-2xl bg-white p-5 border-slate-100 shadow-sm`, grid-cols-1 md:grid-cols-3 gap-4) |
| §3.9 L505-522 sortable merge item | `merge/page.tsx:286-329` — all classes verified incl. grip handle, order badge `h-6 w-6 rounded-md bg-accent/10 text-xs font-bold text-accent`, remove `rounded-lg p-1.5 text-slate-300 hover:bg-rose-50 hover:text-rose-500`, dragging `border-accent shadow-lg` z-50 |
| §3.10 L524-540 sortable image item | `image-to-pdf/page.tsx:302-346` — `aspect-[4/3]`, order badge `bg-accent text-white`, hover-reveal remove/drag overlays, file info px-2.5 py-2 |
| §3.11 L542-558 accordion | `faq/page.tsx:104-120` — grid-rows 0fr to 1fr + opacity, duration-200, px-5 py-4 trigger, px-5 pb-4 answer |
| §3.12 L560-576 rotate page grid | `rotate/page.tsx:509-543` — grid-cols-3 sm:grid-cols-4 gap-3, border-2 cells, rotated `border-accent/40 bg-accent/5`, hover `hover:border-accent/60`, thumbnail h-16 w-12 with rotate transform, hover badge |
| §4.1 L580-598 page shell | `layout.tsx:50-53` (`body flex min-h-full flex-col font-sans`, `main flex-1`) |
| §4.2 L600-607 container widths (landing 1200, content 672) | `page.tsx:488`; `faq/page.tsx:129`; `privacy/page.tsx:11` (navbar width contradicted — §3.3) |
| §4.3 L609-657 grid systems | `page.tsx:545` (1/2/3), `:579` (1/3), badges `md:grid-cols-3`, `OtherTools.tsx:55` (grid-cols-2), `image-to-pdf:710` (2/3), `rotate:509` (3/4) |
| §4.4 L659-669 padding system | `page.tsx:488,535,569`; `compress:94`; `faq:129`; `Footer.tsx:198` |
| §5.3 L692-697 tool navigation (no breadcrumbs, OtherTools, deep links) | All tool pages |
| §6.1 L721-751 server flow (validation, uploading %, shimmer processing, done, reset; timeout; auto-retry) | `PDFUploader.tsx:207-311` — accurate **for Compress**; "berlaku untuk PDF-to-Image" is stale (see §3.2) |
| §6.2 L753-780 client flow (Merge, Split, Rotate, Image-to-PDF < 3MB) | `image-to-pdf/page.tsx:43` (`CLIENT_THRESHOLD_BYTES = 3MB`), `:489-519`; `pdfUtils.ts:170-233` (split/merge in browser) |
| §6.3 L782-793 dnd-kit sensors/strategies | `package.json:24-26`; `merge/page.tsx:357-360` (PointerSensor distance 5 + KeyboardSensor), `:620` (verticalListSortingStrategy); `image-to-pdf/page.tsx:709` (rectSortingStrategy); dragging visual `merge:290` |
| §6.4 L795-813 error visuals (rose-50/50, rose-200, alert circle, "Terjadi Kesalahan", "Coba Lagi") | `PDFUploader.tsx:517-533`; `merge:536-554`; `split:424-442` (rotate deviates — §3.3) |
| §6.5 L815-830 loading texts (all eight) | "Mengunggah... X%" `PDFUploader:412`; "Sedang mengompres..." `:439`; "Sedang menggabungkan X file..." `merge:524`; "Sedang memisahkan X halaman..." `split:412`; "Membuat PDF dari X gambar..." `image-to-pdf:611`; "Mengubah X halaman menjadi gambar..." `pdf-to-image:422`; "Memutar halaman PDF..." `rotate:569`; "Membaca dokumen PDF..." `split:447` |
| §6.6 L832-844 done state (accent/20 border, accent shadow, emerald check, full-width accent download, outline reset) | `PDFUploader.tsx:450-515`; `merge:486-517`; `split:374-405`; compress before/after + savings badge `PDFUploader:467-492` |
| §7.1-7.4 breakpoints, adaptations, touch targets, mobile specifics | Standard Tailwind breakpoints throughout; nav links `px-4 py-2.5` `Navbar:248`; buttons `py-4`/`py-3`; quick selects `px-3 py-1.5` `PageRangeInput:143`; accordion trigger `px-5 py-4` `faq:107`; "Seret PDF ke sini atau klik untuk upload" `PDFUploader:383-387`; mobile CTA `Navbar:218` |
| §8.2 keyboard nav (upload zone tabIndex + Enter/Space) | `PDFUploader.tsx:357-362`; `merge:561-566`; `split:509-514`; `image-to-pdf:650-655`; `pdf-to-image:519-524`; `protect:354`, `unlock:334`, `sign:370`, `ocr:417`, `pdf-to-word:372`, `pdf-to-excel:388` — **exception: rotate** (see §3.3) |
| §8.3 screen reader labels, lang, metadata titles | "Buka menu"/"Tutup menu" `Navbar:226`; "Hapus {filename}" `merge:324`, `image-to-pdf:324`; "Hapus file" `split:472`, `pdf-to-image:482`, `rotate:480`; `lang="id"` `layout:49`; per-tool metadata in all 13 `layout.tsx` files (e.g., `compress/layout.tsx:4`) |
| §9.1 L970-1015 landing hero (pill with dot, H1 "Alat PDF yang langsung bekerja.", navy CTA "Mulai gratis", trust badges) | `page.tsx:488-528` — classes and copy verified verbatim (tool card count contradicted — §3.3) |
| §9.2 L1027-1065 tool page pattern (header: 64px tile, H1, description, context; always-visible PrivacyNotice; idle-only badges; OtherTools) | `compress:94-135`; same structure on merge/split/image-to-pdf/pdf-to-image |
| §9.3 L1067-1073 Compress (server model, before/after, badges "Proses instan/Aman & privat/Kualitas terjaga") | `compress:111-135`; `PDFUploader:467-492` |
| §9.4 L1075-1083 Merge (multi-file, dnd reorder, disabled until >= 2, client model, badges, changing upload text) | `merge:557-601` ("Tambah file lagi" at `:596`), `:635-646`, `:684` |
| §9.5 L1085-1093 Split (loading to ready, PageRangeInput, client model) | `split:444-503`, `:566` |
| §9.6 L1095-1105 Image-to-PDF (accepts jpeg/png/webp, thumbnails, magic-byte validation, hybrid < 3MB, hybrid model) | `image-to-pdf:40-72` (magic bytes), `:669` (accept), `:43` (3MB), `:764` (hybrid) |
| §9.7 L1107-1115 PDF-to-Image (server PyMuPDF, PNG/ZIP, signed URL, server model, badges) | `pdf-to-image/page.tsx:314-327,398-404`; `backend/services/pdf_to_image_service.py:14,135-156` (fitz 150 DPI); `:576` (server model) |
| §9.8 L1117-1128 Rotate (horizontal header, pill badges, visual grid, click = +90 deg, global buttons, navy process button, emerald done state, client model) | `rotate/page.tsx:400-411,414-424,487-506,509-543,551,576,622` |
| §9.9 L1130-1157 FAQ (header, 8 items, single-open, grid animation, CTA card + email) | `faq/page.tsx:47-88` (8 items), `:126-149` (single-open), `:153-161` (email `privacy@mypapyr.com`) |
| §9.10 L1159-1186 Privacy (container, prose classes, H2, lists, links) | `privacy/page.tsx:11-101` — all classes verified |
| §11 L1275-1287 mapping table (Ghostscript, dnd-kit, pdf-lib, hybrid 3MB, PyMuPDF) | `backend/routers/compress.py:109-140` (Ghostscript, quality presets); `backend/services/compress_service.py:43-137`; `merge/page.tsx` dnd-kit; `pdfUtils.ts:170-233` pdf-lib; `backend/services/pdf_to_image_service.py:118-156` PyMuPDF |

### 3.2 Stale

| Doc claim | Why stale | Code evidence |
|---|---|---|
| §3.3 L337 "PDFUploader ... untuk tool yang memerlukan server-side processing (Compress, PDF-to-Image)" | Only Compress uses PDFUploader; PDF-to-Image implements its own upload + `fetch` flow with no percent progress | Grep `import PDFUploader` → single hit `frontend/src/app/compress/page.tsx:4`; `pdf-to-image/page.tsx:302-336` |
| §6.1 L725 "Berlaku untuk: Compress, PDF-to-Image" | The server-side flow taxonomy now also applies to Protect, Unlock, OCR, PDF-to-Word, PDF-to-Excel (server PrivacyNotice models), which the doc never lists | `PrivacyNotice model=` grep: server on compress, pdf-to-image, protect, unlock, ocr, pdf-to-word, pdf-to-excel |
| §3.1 L306 + §5.1 L678 "Desktop: 6 link tool horizontal" | Navbar now has 4 category dropdowns over 13 tools; no flat tool link row exists | `Navbar.tsx:83-117` (NAV_CATEGORIES), `:163-204` (desktop dropdowns) |
| §5.5 L705-718 sitemap table (9 routes) | Seven routes are missing; also no /terms or /contact despite footer links | `sitemap.ts:5-19` (13 tools), `:35-46` (faq, privacy); `Footer.tsx:161-162` |
| §9.1 L995 "6 tool cards (1/2/3 cols)" | Landing renders 13 cards | `page.tsx:360-452` (TOOLS array, 13 entries), `:545-564` (grid) |
| §3.6 L459 "Menampilkan 5 tool (semua kecuali yang aktif)" | OtherTools renders 12 cards (13 minus active) | `OtherTools.tsx:25-39` (13 entries), `:48` (filter) |
| §11 L1282 "Image to PDF ... server fallback" threshold | Still 3MB — accurate, but the hybrid disclosure copy in code ("Mengirim ke server untuk diproses...") is a pattern the doc never specifies | `image-to-pdf/page.tsx:616-620` |

### 3.3 Contradicted

| Doc claim | Code reality | Code evidence |
|---|---|---|
| §3.1 L292 / §4.2 L605 / §5.1: Navbar container `max-w-[1200px]` | Navbar container is `max-w-[1440px]` | `Navbar.tsx:146` |
| §3.1 L306, §5.1 L678: desktop shows "semua 6 link tool" + CTA | Desktop shows 4 category buttons with hover/click dropdowns (13 tool links); no inline tool links | `Navbar.tsx:163-204` |
| §6.1 L738-740 "Progress bar real-time (0-100%)" for server-side tools generally | Only Compress (XHR) has percent upload; PDF-to-Image and the other server tools use `fetch` without upload progress | `PDFUploader.tsx:251-256` vs `pdf-to-image/page.tsx:314-327` |
| §6.4 L797-803 "Visual Konsisten" error state | Rotate error state deviates: rose-600 solid button, rose-800 heading, no `animate-fade-up`, rounded-xl; Sign success uses a `text-green-700` variant outside the documented emerald card | `rotate/page.tsx:602-618`; `sign/page.tsx:606` |
| §8.2 L925 upload zone keyboard pattern (`tabIndex={0}`, `onKeyDown`) | Rotate upload zone has neither role, tabIndex, nor keydown handler | `rotate/page.tsx:428-432` (only onClick/onDrop/onDragOver) — §9.8 documents this page, making the doc self-inconsistent |
| §2.6 L252 `animate-shimmer` 1.4s | Rotate processing uses an inline 1.2s shimmer variant, bypassing the token | `rotate/page.tsx:567` (`animate-[shimmer_1.2s_ease-in-out_infinite]`) |

### 3.4 Missing (implementation features the doc never covers)

1. **Seven tools and routes**: `/protect`, `/unlock`, `/watermark`, `/sign`, `/pdf-to-word`, `/pdf-to-excel`, `/ocr` — with pages, layouts, metadata, analytics tracking, PrivacyNotice models (server for protect/unlock/ocr/pdf-to-word/pdf-to-excel; hybrid for watermark; client for sign), and sitemap entries (`Navbar.tsx:96-115`, `sitemap.ts:12-18`, `analytics.ts:9-23`).
2. **Components**: `PasswordInput.tsx`, `SignaturePad.tsx`, `SignatureUpload.tsx`, `SignatureType.tsx`, `SignaturePlacementOverlay.tsx` (uses `focus-visible:ring-2` — the only custom focus ring in the app), `WatermarkConfig.tsx`, `WatermarkPreview.tsx`, `PDFPageViewer.tsx` — none specified in Doc19.
3. **Footer tools directory**: 4-category "Alat" section with 13 links (`Footer.tsx:171-194`) — no spec in Doc19 §3.2/§5.4.
4. **Navbar category architecture** (hover + click dropdowns, mobile `<details>` accordion, outside-click close) — `Navbar.tsx:127-142,163-262`.
5. **Analytics layer**: `@vercel/analytics` custom events task_started/completed/failed + device_category (`analytics.ts:5-69`, `layout.tsx:54-55`) — Doc19 only cross-references PPR-AET-001.
6. **SEO infrastructure**: `sitemap.ts`, `robots.ts`, `opengraph-image.tsx`, `twitter-image.tsx`, per-tool metadata (13 layout files) — Doc19 §8.3 mentions metadata titles but no SEO spec.
7. **Compress quality parameter**: backend supports `screen|ebook|printer` (`backend/routers/compress.py:109`); frontend hardcodes `?quality=ebook` (`PDFUploader.tsx:303`) — undocumented in Doc19 (relevant to DEC-014's automatic-mode decision).
8. **Server-disclosure copy**: "File dikirim ke server untuk diproses — otomatis dihapus setelah 1 jam" (`pdf-to-image/page.tsx:428`) and "Mengirim ke server untuk diproses..." (`image-to-pdf/page.tsx:619`) — a transparency pattern the doc never specifies (relevant to DEC-011/030).
9. **Dead footer links**: "Syarat" and "Kontak" are `href="#"` with no routes (`Footer.tsx:161-162`; glob for terms/contact/about/blog → none). Doc19 §5.4 lists them as functional navigation.
10. **Loading-state third variant**: Rotate loading uses an `animate-spin` border spinner (`rotate/page.tsx:456`), outside Doc19 §6.5's determinate/indeterminate taxonomy.
11. **Sign/watermark interaction states** (canvas drawing, signature type switching, placement overlay drag) — entirely new interaction patterns.

### 3.5 Historical-only

| Doc content | Status |
|---|---|
| L3/L1304 tagline "Tool PDF gratis, cepat, dan aman untuk Indonesia" | Accurate vs code today (metadata/footer), but superseded by DEC-003/004 (international markets; English + Spanish launch). Historical positioning. |
| L26-27, L1295-1296 document metadata (Jun 2025, Draft, approval 2025-06-03) | Historical record; predates the 2026-05-20 v2.0.0 codebase state (CHANGELOG:3) and Doc32 (2026-06-03). |
| §1.1 L66 "realitas pengguna Indonesia yang mayoritas ... mobile" | Market rationale superseded by DEC-003; no code counterpart to retain. |
| §1.5 L104-113 "Indonesia-First" principle | Code is still 100% Indonesian, so the *description* is accurate; the *principle* is superseded by DEC-003/004. |

### 3.6 Doc-internal inconsistencies (not code issues)

- §3.3 vs §9.7: PDFUploader claimed for PDF-to-Image; the page has its own flow (see §3.2).
- §5.4 (footer links: Privasi, FAQ, Syarat, Kontak) vs §5.5 (no /terms, /contact routes) — the doc lists links it never routes; code made them `href="#"`.
- §8.2 (upload zone keyboard pattern) vs §9.8 (Rotate page, which lacks it) — self-inconsistency; code follows §9.8's "different page" spirit but not §8.2's general pattern.
- Document ID: header says `PPR-UX-001` (Doc19 L23) while Doc32 §13 references it as `PPR-UIUX-001` (L959).

---

## 4. Claim-by-Claim — `docs/32_Papyr_Brand_Guidelines_v1.0.md`

### 4.1 Accurate / current

| Doc claim | Code evidence |
|---|---|
| §2.1 L84-93 Brand name Papyr, mypapyr.com | `layout.tsx:23` (metadataBase `https://mypapyr.com`); retained per DEC-021 |
| §3.1 L144-172 logo construction: 28x28 tile, rounded-md, navy, white stroke SVG file icon (viewBox 24, strokeWidth 2), wordmark 17px semibold tracking-tight navy | `Navbar.tsx:156-159` (tile `h-7 w-7 rounded-md bg-navy`; FileIcon `strokeWidth="2"` white at `:11-25`; wordmark `text-[17px] font-semibold tracking-tight text-navy`) |
| §4.1 L228-236 five primary tokens | `globals.css:4-8` — exact hex match for all five |
| §4.2 L238-248 supporting palette (slate-500/200/100, accent/10/15/30/60) | `page.tsx:552,582`; `PDFUploader.tsx:478`; `page.tsx:490`; hover borders `page.tsx:550` |
| §5 L290-354 typography (DM Sans variable via Google Fonts, --font-dm-sans, latin; type scale incl. hero clamp, 32px H2, 28px H3, xs uppercase widest section label, 15px titles, 13.5px desc, 13px small, 12px badge; leading/tracking rules; antialiased) | `layout.tsx:9-14,49`; `page.tsx:497,537-542,556-557`; `Footer.tsx:207,216`; `page.tsx:492` |
| §6.1 L360-367 container class and page background (#F9FAFB) | `page.tsx:488`; `globals.css:12-13` (navbar exception — §4.3) |
| §6.2 L369-377 vertical spacing (navbar 52px; tools py-20; privacy py-[72px]; footer py-10) | `Navbar.tsx:146`; `page.tsx:535,569`; `Footer.tsx:198` |
| §6.3 L379-390 component spacing (card p-6; grid gap-4; privacy gap-8; primary px-8 py-3.5; icon h-10 w-10) | `page.tsx:550,545,579,512,552` |
| §6.4 L392-400 grid pattern `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4` | `page.tsx:545` — verbatim |
| §7.1 L418-437 card default + hover (incl. both custom shadows) | `page.tsx:550` — verbatim |
| §7.2 L441-452 primary button | `page.tsx:512` — verbatim (hero CTA; tool-page action buttons differ — §4.2/4.3) |
| §7.3 L473-487 pill badge incl. dot indicator | `page.tsx:490-494` |
| §7.4 L493-509 icon containers | `page.tsx:552` — verbatim |
| §7.5 L511-529 navbar (sticky, border, bg-bg/92, backdrop-blur-md, 52px) | `Navbar.tsx:145-146` (container width differs — §4.3) |
| §7.6 L531-539 footer (border-t, bg-bg, py-10) | `Footer.tsx:169,198` (plus undocumented tools section) |
| §8.1-8.3 L556-596 iconography (Lucide-style stroke, round caps/joins, inline SVG, currentColor, template) | All icons in code are inline SVGs matching the template; `package.json` has no icon dependency |
| §8.2 L567-574 sizes: tool icon 19x19 stroke 1.8; UI small 15x15/2; menu 20x20/2; logo file icon 14-15/2 | `page.tsx:113-223` (19/1.8), `:23-38` (15/2), `Navbar.tsx:28-44` (20/2), `Navbar.tsx:11-25` (15/2), `Footer.tsx:8-24` (13/2) |
| §9 L623-723 animation principles (150-300ms, hover lift `-translate-y-0.5`, shadow transitions, shimmer/fade-up keyframes, transition classes, antialiased, "no scale hover", "no bounce", "CLS 0") | `globals.css:19-44`; `page.tsx:512,550`; code complies with the don'ts |
| §10.1-10.6 L727-816 copy voice (Bahasa Indonesia, "kamu", short CTAs, error message style) | Verified across all pages; error examples match `PDFUploader.tsx:210-216` ("Tipe file tidak valid...", "Ukuran file terlalu besar. Maksimal 20MB."); CTA patterns "Mulai gratis"/"Coba Gratis"/"Gunakan alat"/"Upload file"/"Unduh ..." all present |
| §12 L864-950 do's and don'ts | Consistent with implementation |

### 4.2 Stale

| Doc claim | Why stale | Code evidence |
|---|---|---|
| §4.3 L254-258 semantic colors "Green (to be defined) / Red (to be defined) / Amber (to be defined)" + note "gunakan Tailwind default (green-600, red-600, amber-600)" | The codebase has standardized since: emerald-500 success circles, rose-50/rose-200/rose-500 error cards, no amber warning UI exists | `PDFUploader.tsx:454,517-524`; `merge:489,537`; `rotate:576,603` |
| §4.4 L270 "Primary button bg #1E3A5F (navy) — CTA utama" | True for the hero CTA only; every tool-page primary action button (merge, split, convert, download) is accent blue | `page.tsx:512` (navy) vs `merge:639-643`, `split:488-492`, `PDFUploader:498`, `pdf-to-image:401` (accent) |
| §7.2 L457-467 "Secondary Button ... px-5 py-2" | No secondary CTA in the app uses px-5 py-2; navbar CTA is `px-4 py-2` (`Navbar.tsx:209`), mobile `px-3.5 py-1.5 text-[13px]` (`Navbar.tsx:218`) |
| §8.4 L600-610 icon table (6 tools) | Seven more tools have icons in code; descriptions partially mismatched: Compress described as "Archive/box dengan panah ke bawah" but the actual glyph is corner arrows (compress/expand); PDF-to-Image described as "dokumen dengan panah ke gambar" but the actual glyph is a document with text lines | `page.tsx:113-129` (compress), `:188-205` (pdf-to-image), `:225-356` (the 7 undocumented icons) |
| §3.2 L179 "Icon only — mobile navbar collapsed" | Mobile navbar keeps the full icon+wordmark logo | `Navbar.tsx:148-160` (rendered unconditionally) |

### 4.3 Contradicted

| Doc claim | Code reality | Code evidence |
|---|---|---|
| §6.1 L364 "Konten tidak pernah lebih lebar dari ini [1200px]" | Navbar container is 1440px | `Navbar.tsx:146` |
| §7.2 secondary button spec (px-5 py-2, rounded-lg, shadow-sm) | The navbar CTA (the only secondary CTA) is px-4 py-2 | `Navbar.tsx:209` |
| §3.1 logo radius `rounded-md` (6px) as the single construction rule | Footer logo tile uses `rounded-[5px]` | `Footer.tsx:202` |

### 4.4 Missing (no brand guidance exists)

1. Icons/colors for the seven undocumented tools (`page.tsx:225-356`).
2. Official semantic color decisions (emerald success / rose error conventions now entrenched).
3. The 1440px navbar container and the footer tools-directory pattern.
4. Analytics disclosure patterns in processing copy (server-disclosure lines).
5. The new interaction surface: signature canvas, placement overlay (with its `focus-visible` ring), watermark config/preview, PDF page viewer.
6. A processing-feedback taxonomy that includes rotate's spinner variant and 1.2s shimmer.
7. Error-state variants outside the standard card (rotate's rose-600 button, sign's green-700 success text).

### 4.5 Historical-only

| Doc content | Status |
|---|---|
| §1.3 L77 "AI agent (OpenCode, Sisyphus, OpenClaw)" audience | OpenClaw removed per DEC-016 |
| §2.2 L95-108 tagline + "Variasi yang TIDAK diperbolehkan: Tagline dalam bahasa Inggris" | Positioning superseded by DEC-003/004 (English + Spanish launch) |
| §2.3 L110-117 brand values incl. "Indonesia-first ... server dekat Asia" | Superseded by DEC-003; legacy server was Linode Jakarta (`CHANGELOG.md:12`); DEC-017 retains VPS but regional claims need re-scoping |
| §10.1 L731 "Seluruh UI Papyr menggunakan Bahasa Indonesia" + `lang="id"` | True today (`layout.tsx:49`), but contradicts accepted DEC-004 (EN/ES launch) |
| §11 L820-861 social media (Twitter/X via OpenClaw account, bio "untuk Indonesia", content pillars) | No code counterpart (grep `OpenClaw|twitter.com` in frontend → zero matches); OpenClaw removed per DEC-016 |
| §13 L962 related docs incl. `PPR-CLAW-001` (OpenClaw System Specification) | Historical per DEC-016 |
| §4.3 note about "warna status belum didefinisikan" | Describes an earlier codebase state; emerald/rose are now de-facto standards |

---

## 5. Implementation Surface Absent from Both Docs (Combined Coverage Gaps)

1. Seven tools: Protect, Unlock, Watermark, Sign, PDF-to-Word, PDF-to-Excel, OCR (pages, layouts, metadata, sitemap, analytics names, privacy models).
2. Components: PasswordInput, SignaturePad, SignatureUpload, SignatureType, SignaturePlacementOverlay, WatermarkConfig, WatermarkPreview, PDFPageViewer.
3. Navbar category dropdown system (desktop hover/click + mobile `<details>` accordion).
4. Footer tools directory (4 categories, 13 links).
5. Dead-link problem: "Syarat"/"Kontak" (`Footer.tsx:161-162`) with no routes (glob: no terms/contact/about/blog dirs).
6. Vercel Analytics + SpeedInsights instrumentation and the custom event schema (`analytics.ts:5-69`; `layout.tsx:54-55`).
7. SEO layer: `sitemap.ts` (13 tools + faq + privacy), `robots.ts`, `opengraph-image.tsx`, `twitter-image.tsx`, 13 per-tool metadata blocks.
8. Compress quality: backend `screen|ebook|printer` (`compress.py:109`), frontend hardcoded `ebook` (`PDFUploader.tsx:303`).
9. Server-processing disclosure copy (`pdf-to-image/page.tsx:428`; `image-to-pdf/page.tsx:619`).
10. Rotate deviations (spinner loading, 1.2s shimmer, non-standard error state) and sign's green-700 success variant.
11. Two icon sets per tool (landing card icon vs tool-page header icon differ for merge, rotate, pdf-to-image, etc.) — undocumented in both docs.

---

## 6. Conflicts with Accepted Rebuild Decisions (Decision-Log Context)

| Decision | Relationship to the docs |
|---|---|
| DEC-002/003/004 (PDF tools; international; EN/ES) | Both docs' Indonesia-first positioning and Doc32's "no English tagline" rule are superseded. Code is still 100% Indonesian, so docs and code agree with each other while both conflict with the accepted direction. |
| DEC-016 (remove Guinevere/OpenClaw) | Doc32 §11 (OpenClaw-managed Twitter/X) and §13 (PPR-CLAW-001) are historical-only. |
| DEC-021 (retain Papyr name, mypapyr.com) | Consistent with both docs and code (`layout.tsx:23`). |
| DEC-028 (evolve visual identity, baseline) | The reconciliation confirms the documented tokens are pixel-accurate in code — a low-risk baseline to retain; the catalog/nav drift (§3.2/3.3) is exactly the "correct what is stale" work DEC-028 anticipates. |
| DEC-043 (homepage directory) | Docs describe the directory homepage accurately (hero, tool grid, privacy section, FAQ) except the tool count (6 vs 13). |
| DEC-014 (single automatic compress mode) | Code hardcodes `quality=ebook` (`PDFUploader.tsx:303`) while the backend exposes three presets; neither doc mentions quality. The canonical spec must codify the automatic mode and whether `ebook` is the intended profile. |
| DEC-023 (locale-prefixed routes) | Not yet implemented; docs are monolingual — future spec must define the EN/ES route and copy architecture from scratch. |
| DEC-045 (Privacy/Terms/Cookies pages) | Footer dead links ("Syarat"/"Kontak") must be resolved; Docs 19/32 give no terms/cookies guidance. |
| DEC-011/015/030 (processing disclosure) | Code already discloses server processing in copy; docs never specify the pattern — the canonical spec should formalize it. |
| DEC-025 (detailed analytics, no session replay) | Doc32's "tanpa tracking invasif" phrasing and the privacy page's "tidak ada tracking" statement (`privacy/page.tsx:47,73`) need re-scoping against the accepted analytics decision and DEC-022 risk. |

---

## 7. Recommendations for the Future Canonical Design Spec

(Recommendations only — no spec written.)

### 7.1 Retain as-is (verified pixel-accurate against code)

- All five color tokens and the slate/semantic/accent-tint usage tables (Doc19 §2.2; Doc32 §4.1-4.2).
- Typography: DM Sans, `--font-dm-sans`, fallback, antialiased, latin subsets, and the full type scale with tracking/leading rules (Doc19 §2.1; Doc32 §5).
- Spacing scale, radii, and shadow system incl. the three custom accent shadows (Doc19 §2.3-2.5; Doc32 §6.3, §7.1).
- Animation keyframes: shimmer 1.4s and fade-up 0.3s, transition conventions, hover lift (Doc19 §2.6; Doc32 §9) — with a note to standardize rotate's 1.2s inline variant.
- Iconography principles: inline SVG, Lucide-style stroke, round caps/joins, currentColor, size conventions (Doc19 §2.7; Doc32 §8.1-8.3).
- Component specs: upload zone, feature badge card, sortable file/image items, accordion, rotate page grid, PageRangeInput, PrivacyNotice (classes + three messages), done/error/processing cards, FAQ page, Privacy page (Doc19 §3.4-3.12, §6.4-6.6, §9.9-9.10).
- Touch-target table and mobile adaptations (Doc19 §7.3-7.4).
- Contrast table (Doc19 §8.4) — after one re-verification pass with a color-contrast tool.

### 7.2 Rewrite or extend

- **Catalog and routes**: 13 tools with per-tool privacy models (server: compress, pdf-to-image, protect, unlock, ocr, pdf-to-word, pdf-to-excel; client: merge, split, rotate, sign; hybrid: image-to-pdf, watermark), per-tool processing mode (browser/server/hybrid), and per-tool limits.
- **Navbar spec**: 4-category dropdown architecture, 1440px container, hover+click behavior, outside-click close, mobile `<details>` accordion, active states.
- **Footer spec**: tools directory section, bottom bar, language switcher, and a dead-link policy (resolve Syarat/Kontak).
- **Landing spec**: 13-card grid, hero, privacy pillars; keep the exact card classes.
- **OtherTools spec**: 12 cards, grid-cols-2, heading.
- **Server-flow taxonomy**: which tools use XHR-with-progress (compress only) vs fetch-without-progress, and the disclosure copy patterns.
- **Loading taxonomy**: add the spinner variant (rotate) or standardize on shimmer; document the 1.2s deviation decision.
- **Error/done consistency**: absorb rotate's and sign's variants into explicit specs (or standardize them).
- **Compress quality**: document the automatic-mode decision (DEC-014) and the ebook preset reality.
- **New component specs**: PasswordInput, signature suite, watermark suite, PDFPageViewer.
- **Analytics and SEO**: event schema, sitemap/robots/OG-image conventions, per-tool metadata patterns.
- **Accessibility roadmap** (still valid from Doc19 §8.5/§10.3): skip link, aria-live regions, `role="progressbar"`, focus-visible rings (only the sign overlay has one today), prefers-reduced-motion.
- **i18n**: EN/ES launch posture per DEC-004, locale-prefixed routes per DEC-023, copy-length resilience (current Indonesian context paragraphs are long for English/Spanish in some places).
- **Semantic colors**: officialize emerald success / rose error / amber (future) with exact tokens.
- **Button taxonomy**: two documented conventions — navy hero CTA and accent tool-page primary actions — with exact padding values (px-8 py-3.5; px-4 py-2 navbar; px-3.5 py-1.5 mobile).
- **Icon inventory**: single source of truth for all 13 tool icons, resolving the landing-card vs page-header icon drift.

### 7.3 Mark historical (do not carry forward)

- Indonesia-first principle and Indonesian-only copy rules (Doc19 §1.5; Doc32 §2.2-2.3, §10.1).
- OpenClaw-related content (Doc32 §1.3, §11, §13).
- "6 tools" counts anywhere (Doc19 §3.1/3.6/5.1/9.1).
- Universal 1200px rule (Doc32 §6.1) — replaced by the 1440px navbar + 1200px content convention.
- "Semantic colors to be defined" note (Doc32 §4.3) — replaced by emerald/rose/amber decisions.
- Secondary button px-5 py-2 spec (Doc32 §7.2) — replaced by actual values.
- Doc19's §5.5 sitemap — replaced by the 13-tool + legal-pages map.

---

## 8. Uncertainties & Unresolved Questions

1. **Historical code states**: Whether Doc19 (Jun 2025) and Doc32 (Jun 2026) matched the codebase at their authored dates cannot be verified without git history (git operations were out of scope).
2. **Contrast ratios** (Doc19 §8.4): hex values match code, but ratios were not re-measured (static inspection only; no browser tooling).
3. **Favicon**: `frontend/src/app/favicon.ico` is binary; the Doc32 logo rules could not be verified against it.
4. **OG images**: `opengraph-image.tsx` / `twitter-image.tsx` were noted but not inspected in detail (metadata references `/og/papyr.png`; the route handlers generate it at request time).
5. **Doc32 icon-table dating**: the table lists 6 tools while the current code has 13; whether the code at 2026-06-03 already had 13 is unknown (see #1).
6. **Backend surface for the 7 new tools**: only compress/pdf-to-image/image-to-pdf routers were verified; protect/unlock/watermark/sign/ocr/pdf-to-word/pdf-to-excel backend behavior was out of scope for this reconciliation.
7. **Document-ID cross-references** (Doc19 §11; Doc32 §13): the referenced PPR-* IDs were not verified against the actual `docs/` file headers; note the internal inconsistency `PPR-UX-001` vs `PPR-UIUX-001`.
8. **Privacy/analytics statements**: code claims ("tidak ada tracking", "tidak mengumpulkan data pribadi apapun" — `faq/page.tsx:61`, `privacy/page.tsx:47`) coexist with Vercel Analytics instrumentation; whether these statements remain accurate is a policy/legal question for the rebuild (DEC-022/025/045), not a code question.
9. **FAQ copy staleness inside the product**: FAQ says "Papyr mendukung file PDF, JPG, dan PNG" (`faq/page.tsx:81`) but Image-to-PDF accepts WEBP — an in-product content drift that the future spec's copy governance should catch.

---

## 9. Verification Statement

- `papyr-reference/` was only read; nothing was modified, formatted, installed, or executed there.
- This deliverable was created at `<workspace-root>\audit-outputs\ui-docs-code-reconciliation.md`.
- Headings: `# Papyr UI/UX & Brand Documentation vs. Frontend Implementation — Reconciliation Audit`; `## 1. Executive Summary`; `## 2. Files Inspected (Evidence Base)`; `## 3. Claim-by-Claim — docs/19_Papyr_UIUX_Spec_v1.0.md` (3.1 Accurate / current; 3.2 Stale; 3.3 Contradicted; 3.4 Missing; 3.5 Historical-only; 3.6 Doc-internal inconsistencies); `## 4. Claim-by-Claim — docs/32_Papyr_Brand_Guidelines_v1.0.md` (4.1-4.5); `## 5. Implementation Surface Absent from Both Docs`; `## 6. Conflicts with Accepted Rebuild Decisions`; `## 7. Recommendations for the Future Canonical Design Spec` (7.1 Retain; 7.2 Rewrite or extend; 7.3 Mark historical); `## 8. Uncertainties & Unresolved Questions`; `## 9. Verification Statement`.
- Chat-only summary: see companion response. This file is the primary deliverable.
