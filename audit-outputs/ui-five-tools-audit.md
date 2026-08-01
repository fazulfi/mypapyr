# UI/UX Audit — Five Approved Launch Tools (Papyr Reference)

- **Date**: 2026-07-31
- **Auditor**: subagent (codebase search / UX audit), delegated by Sisyphus
- **Scope**: Read-only, page-by-page UX audit of Compress (Kompres PDF), Merge (Gabungkan PDF), Split (Pisahkan PDF), Image-to-PDF (Gambar ke PDF), PDF-to-Image (PDF ke Gambar) in `papyr-reference/` (read-only legacy baseline).
- **Method**: Static source inspection only. No browser, no build, no runtime execution. All line references are to files under `<workspace-root>\papyr-reference\frontend\src\` unless stated otherwise.
- **Baseline principle**: Existing UI/UX is the owner-approved baseline; this audit documents it exactly, then lists deviations and preserve/correct recommendations for the rebuild. No redesign proposed.

---

## 1. Inspected Sources (complete list)

| # | File | Purpose |
|---|------|---------|
| 1 | `frontend/src/app/compress/page.tsx` (138 lines) | Compress page (server-processed via PDFUploader) |
| 2 | `frontend/src/app/merge/page.tsx` (687 lines) | Merge page (client-side, dnd-kit sortable list) |
| 3 | `frontend/src/app/split/page.tsx` (569 lines) | Split page (client-side, PageRangeInput) |
| 4 | `frontend/src/app/image-to-pdf/page.tsx` (767 lines) | Image-to-PDF page (hybrid client/server, sortable grid) |
| 5 | `frontend/src/app/pdf-to-image/page.tsx` (579 lines) | PDF-to-Image page (server-only, PageRangeInput) |
| 6 | `frontend/src/components/PDFUploader.tsx` (537 lines) | Shared upload/progress/result component (used by Compress) |
| 7 | `frontend/src/components/PageRangeInput.tsx` (164 lines) | Shared page-range parser/input (used by Split, PDF-to-Image) |
| 8 | `frontend/src/components/PrivacyNotice.tsx` (44 lines) | Shared privacy notice (all 5 tools) |
| 9 | `frontend/src/components/OtherTools.tsx` (69 lines) | Shared cross-tool link grid (all 5 tools) |
| 10 | `frontend/src/lib/pdfUtils.ts` (255 lines) | Client-side PDF logic: mergePDFs, splitPDF, getPDFPageCount, imagesToPDF, downloadPDF, rotate helpers |
| 11 | `frontend/src/lib/format.ts` (21 lines) | formatFileSize, formatPercent |
| 12 | `frontend/src/lib/config.ts` (39 lines) | apiUrl, siteUrl, limits (20MB, retention 60 min, allowed MIME types) |
| 13 | `frontend/src/lib/analytics.ts` (69 lines) | trackTaskStarted/Completed/Failed, device category |
| 14 | `frontend/src/app/globals.css` (45 lines) | Tokens (navy #1e3a5f, accent #2563eb, bg #f9fafb), animate-shimmer, animate-fade-up |
| 15 | `frontend/src/app/layout.tsx` (59 lines) | Root layout: lang="id", DM Sans, Navbar/main/Footer, Vercel Analytics + SpeedInsights |
| 16 | `frontend/src/app/{compress,merge,split,image-to-pdf,pdf-to-image}/layout.tsx` | Per-tool metadata (title/description/OG + /og/*.png) |
| 17 | `frontend/src/lib/__tests__/pdfUtils.test.ts` (191 lines) | Unit tests: getPDFPageCount, mergePDFs, splitPDF, rotatePDFAllPages, imagesToPDF |
| 18 | `frontend/e2e/smoke.spec.ts` (32 lines) | All 13 tool pages return HTTP 200 |
| 19 | `frontend/e2e/client-tools.spec.ts` (204 lines) | E2E: Merge (2 tests), Split (2 tests), Rotate, Sign |
| 20 | `frontend/e2e/helpers.ts` (34 lines) | Fixtures + upload helpers (no data-testid; selectors use visible Indonesian copy) |
| 21 | `backend/routers/compress.py` (221 lines) | POST /api/compress?quality=ebook (screen|ebook|printer), signed URL 1h, response {download_url, original_size, compressed_size, saved_percent} |
| 22 | `backend/routers/pdf_to_image.py` (251 lines) | POST /api/pdf-to-image (file + pages), response {download_url, file_type: png|zip, page_count}, signed URL 1h |
| 23 | `backend/routers/image_to_pdf.py` (233 lines) | POST /api/image-to-pdf (multi-file), response {download_url, image_count, pdf_size}, signed URL 1h |
| 24 | `frontend/src/__tests__/` (glob) | No tests exist for compress/merge/split/image-to-pdf/pdf-to-image pages |
| 25 | `frontend/src/components/__tests__/` (glob) | Only `PasswordInput.test.ts`; no tests for PDFUploader, PageRangeInput, PrivacyNotice, OtherTools |

Verification: `papyr-reference/` was only read, never modified. No commands were run inside `papyr-reference/`.

---

## 2. Shared Design System Baseline (from globals.css + root layout + shared components)

- **Tokens** (`globals.css:3-10`): `--color-navy: #1e3a5f`, `--color-accent: #2563eb`, `--color-bg: #f9fafb`. Font: DM Sans (`app/layout.tsx:9-14`), `<html lang="id">` (`app/layout.tsx:49`).
- **Animations** (`globals.css:19-44`): `animate-shimmer` (1.4s infinite gradient sweep) used for indeterminate processing bars; `animate-fade-up` (0.3s, translateY(10px)) used for every state-transition card. All state cards animate in — consistent across all five tools.
- **Page shell**: `mx-auto w-full max-w-xl px-4 py-8 sm:py-12` (identical on all five pages).
- **Tool header pattern** (identical structure on all five pages):
  1. 64px rounded-2xl accent icon tile (`h-16 w-16 rounded-2xl bg-accent/10 text-accent`),
  2. `h1` `text-3xl font-bold tracking-tight text-navy md:text-4xl`,
  3. one-line subtitle `text-base text-slate-500`,
  4. context paragraph `mt-2 text-sm text-slate-400 max-w-md` with a real-world use case (WhatsApp, KTP, lamaran kerja, media sosial).
- **Feature badges**: 3-card grid `grid-cols-1 gap-4 md:grid-cols-3`, each `rounded-2xl bg-white p-5 border border-slate-100 shadow-sm`, icon + `h3 text-sm font-semibold text-navy`.
- **Dropzone pattern** (identical classes everywhere): `rounded-2xl border-2 border-dashed bg-white px-5 py-14 text-center transition-all`, `border-slate-300 hover:border-accent/50`, drag-over → `border-accent bg-accent/5`; 56px accent icon tile; `text-base font-semibold tracking-tight text-navy` CTA line; `text-xs text-slate-400` constraints line; hidden `<input type="file">`; the dropzone is a `<div role="button" tabIndex={0}>` with Enter/Space keydown handlers (e.g., `merge/page.tsx:561-566`).
- **Processing card**: `rounded-2xl border border-slate-200 bg-white p-6` with status line, 6px shimmer bar (`h-1.5 rounded-full bg-slate-100` + `animate-shimmer`), optional footnote.
- **Done card**: `rounded-2xl border border-accent/20 bg-white p-6 shadow-[0_4px_20px_rgba(37,99,235,0.06)]`; 40px emerald-500 circle with white check; title + metadata line; full-width accent download CTA (`rounded-xl bg-accent px-5 py-4 text-base font-semibold text-white shadow-[0_2px_12px_rgba(37,99,235,0.25)] hover:bg-accent/90`); secondary outline reset CTA (`rounded-xl border border-slate-200 bg-transparent px-5 py-3 text-sm font-medium text-slate-500 hover:bg-slate-50`).
- **Error card**: `rounded-2xl border border-rose-200 bg-rose-50/50 p-6`; rose alert icon + "Terjadi Kesalahan" header; message; full-width accent "Coba Lagi" button.
- **PrivacyNotice**: always visible on all five pages, `mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-500 border border-slate-100`, shield icon + one of three model strings (`PrivacyNotice.tsx:28-33`).
- **OtherTools**: `mt-16 border-t border-slate-200` section, h2 "Alat lainnya" (uppercase tracking-widest accent), 2-column link grid of the other 12 tools (`OtherTools.tsx:25-66`).
- **Metadata**: each tool has its own `layout.tsx` with title/description/OG + per-tool OG image (`/og/compress.png`, `/og/merge.png`, `/og/split.png`, `/og/image-to-pdf.png`, `/og/pdf-to-image.png`). All Indonesian.
- **Analytics**: `trackTaskStarted(tool)` on action, `trackTaskCompleted`/`trackTaskFailed(tool, reason)` on outcome, for merge/split/image-to-pdf/pdf-to-image; PDFUploader tracks for compress incl. `invalid_file` and `rate_limit` reasons (`PDFUploader.tsx:272, 329`).

---

## 3. Per-Tool Audit

### 3.1 Compress — Kompres PDF (`app/compress/page.tsx`)

**Processing model**: Server (FastAPI `POST {apiUrl}/api/compress?quality=ebook`, `PDFUploader.tsx:303`; backend `routers/compress.py:104-109`). Ghostscript compression, result stored in R2 with 1-hour signed URL (`compress.py:155-159`).

**Page structure / component flow**:
- `Header` (`compress/page.tsx:96-108`): H1 "Kompres PDF" (:100-102), subtitle "Perkecil ukuran PDF tanpa mengurangi kualitas." (:103), context "Cocok untuk kirim dokumen lewat WhatsApp, email kantor, atau upload ke portal pemerintah yang ada batas ukuran file." (:104-107).
- `PDFUploader` (:111-114): `endpoint={config.apiUrl + '/api/compress'}`, `onStateChange` lifts `UploadState` ('idle'|'uploading'|'processing'|'done'|'error', `PDFUploader.tsx:17`) to page state. `onUploadComplete`/`onReset` props are unused on this page.
- `PrivacyNotice model="server"` (:117).
- Feature badges only while `uploaderState === 'idle'` (:120-134).
- `OtherTools currentTool="/compress"` rendered **always visible**, outside any state conditional (:135) — this is the ONLY one of the five tools where OtherTools stays on screen during processing/done.

**Configuration**: No user-facing configuration. `quality=ebook` is hardcoded in `PDFUploader.tsx:303` even though the backend supports `screen|ebook|printer` (`compress.py:109`). No compression-level selector exists in the UI.

**Upload & validation UX** (`PDFUploader.tsx`):
- Dropzone copy: "Seret PDF ke sini / atau klik untuk upload" (:383-387); constraints "Maks 20MB · Hanya file PDF · Dihapus dalam 1 jam" (:388-390). Note: this is the only tool whose dropzone mentions auto-deletion; also the only one saying "upload" vs "memilih".
- Validation (:207-221): MIME type must be in `accept` list ('application/pdf' default), non-empty, <= `maxSizeMB` (default 20). Message style: "Tipe file tidak valid. Hanya file PDF yang diterima." / "File kosong." / "Ukuran file terlalu besar. Maksimal 20MB." — differs from the other four tools' validation wording ("bukan file PDF", "terlalu besar (maks 20MB)", "kosong").
- Upload starts automatically on file select — no submit button (unique among the five tools; all others require an explicit CTA).
- Upload progress: XHR `upload` progress events → determinate bar "Mengunggah... {progress}%" (:251-256, 411-419); on transfer end switches to indeterminate "Sedang mengompres..." (:297-301, 439) with footnote "Mengoptimalkan gambar dan stream..." (:443-445). 120s timeout (:304).
- **Auto-retry**: first failure (5xx, network, timeout) triggers silent 1s-delayed retry with label "Mencoba ulang..." (:223-241, 412); only the second failure surfaces the error card. 429 → immediate error "Terlalu banyak permintaan. Coba lagi dalam 1 menit." (:269-272). 4xx validation → immediate error, no retry (:273-282). Retry delay uses bare `setTimeout` not cleared on unmount/reset (:229-232) — minor robustness note.
- Error card (:517-534): "Coba Lagi" calls `resetState` → back to idle dropzone (file is discarded, not kept).

**Result UX** (richest of the five tools, `PDFUploader.tsx:450-515`):
- "Kompresi selesai!" + original filename (:461-462).
- Before/After panel on `bg-slate-50` (:467-492): "SEBELUM" (slate, size) — accent pill "−X%" — "SESUDAH" (navy, size), arrow icon between. `saved%` = `formatPercent(original, compressed)` (`format.ts:15-21`; returns 0 if compressed >= original, so "−0%" pill is possible).
- Download = `<a href={download_url} download>` (server URL; force-download per `compress.py:156-159`) labeled "Unduh PDF yang Dikompres".
- Reset = "Kompres file lain".

**Responsive**: Full-width buttons; badges 1-col → 3-col at md; shell max-w-xl; nothing tool-specific.

**A11y semantics**: dropzone `role="button"` + Enter/Space (:356-371); no `aria-live`/`role="status"` on progress or result; progress bar has no `role="progressbar"`/`aria-valuenow`; error card has no `role="alert"`.

**Analytics**: `trackTaskStarted('compress')` once per attempt (:309, not on retry), `trackTaskCompleted` on success (:264), `trackTaskFailed` with reasons `server_error` (:237), `rate_limit` (:272), `invalid_file` (:329).

### 3.2 Merge — Gabungkan PDF (`app/merge/page.tsx`)

**Processing model**: Client-only (pdf-lib `mergePDFs`, `pdfUtils.ts:209-233`). Nothing leaves the device.

**State machine**: `'idle' | 'processing' | 'done' | 'error'` (:35). Files persist across error → "Coba Lagi" (returns to idle, list kept, :543-552).

**Page structure / component flow**:
- Header (:471-483): H1 "Gabungkan PDF" (:475-477), subtitle "Gabungkan beberapa file PDF menjadi satu." (:478), context "Satukan scan KTP, ijazah, dan dokumen lainnya jadi satu file untuk keperluan lamaran kerja atau pendaftaran online." (:479-482).
- Done card (:486-518): "PDF berhasil digabungkan!" + summary "{n} file · {size}" (:493-496); "Unduh PDF Gabungan" (:500-507); "Gabungkan file lain" (:509-516).
- Processing card (:521-533): "Sedang menggabungkan {n} file..." + shimmer + "Proses berjalan di browser — file tidak dikirim ke server." (:529-531).
- Error card (:536-554): "Terjadi Kesalahan" + message + "Coba Lagi".
- Upload zone + sortable file list rendered in `idle | error` (:557-681).
- Feature badges only when `files.length === 0` (:663-676): "Proses di browser / Tanpa upload server / Privasi terjaga" (:334-338).
- OtherTools inside the `idle | error` wrapper (:679) — hidden during processing/done.
- `PrivacyNotice model="client"` (:684) — always visible.

**File management**:
- Multi-select + drag-drop; `accept=".pdf" multiple` (:577-589); dropzone copy switches after first file: "Seret beberapa PDF ke sini\natau klik untuk memilih" → "Tambah file lagi" (:593-597; the `\n` in the JS string renders collapsed in HTML).
- Constraints: "Maks 20MB per file · Hanya file PDF" (:598-600).
- Per-file validation (:368-400): non-PDF → `"<name>" bukan file PDF.`; >20MB → `"<name>" terlalu besar (maks 20MB).`; 0 bytes → `"<name>" kosong.`. Multiple errors joined into one message.
- Sortable list (`dnd-kit`, :615-632): `PointerSensor` (5px activation distance) + `KeyboardSensor` with `sortableKeyboardCoordinates` (:357-360); `verticalListSortingStrategy`; each row (`SortableFileItem`, :266-330) = drag-handle button (no aria-label, :294-301) + accent order badge (index+1, :304-306) + file icon + truncated name/size + remove button `aria-label="Hapus <name>"` (:320-327).
- Summary line "{n} file dipilih · {size}" + "Seret untuk mengubah urutan" hint when >= 2 files (:606-613).
- Empty state: "Belum ada file. Upload minimal 2 PDF." (:657-661).
- CTA "Gabungkan PDF" disabled until >= 2 files, with helper "Upload minimal 2 file PDF untuk menggabungkan." (:635-652). Disabled style: `bg-slate-200 text-slate-400 cursor-not-allowed`.

**Result UX**: Programmatic download via `downloadPDF(mergedData, 'merged.pdf')` (:451-455, `pdfUtils.ts:240-254` creates blob + temp `<a>`). **Filename is hardcoded English `merged.pdf`** — inconsistent with Indonesian copy and with split's generated filename.

**Responsive**: rows stack full-width; badges 1→3 cols; no other tool-specific behavior.

**A11y**: dropzone role=button OK; remove buttons labeled; drag handles unlabeled (SR announces bare "button"); dnd-kit has no `announcements`/`screenReaderInstructions` config, so keyboard reorder feedback is not announced; no aria-live on status changes; h1 → h3 jump in badges (no h2).

### 3.3 Split — Pisahkan PDF (`app/split/page.tsx`)

**Processing model**: Client-only (`getPDFPageCount` + `splitPDF`, `pdfUtils.ts:153-201`).

**State machine**: `'idle' | 'loading' | 'ready' | 'processing' | 'done' | 'error'` (:14) — the two-step flow (read page count → configure range) is unique to Split and PDF-to-Image.

**Page structure / component flow**:
- Header (:359-371): H1 "Pisahkan PDF" (:363-365), subtitle "Ambil halaman tertentu dari dokumen PDF." (:366), context "Ambil halaman yang kamu butuhkan dari laporan, skripsi, atau e-book tanpa perlu download ulang seluruh file." (:367-370). Note: uses informal "kamu" — the only tool header doing so.
- **Loading card** (:445-452): "Membaca dokumen PDF..." + shimmer (no footnote).
- **Ready state** (:455-503): file info row (file icon, truncated name, "{n} halaman · {size}", remove `aria-label="Hapus file"` :468-476) → PageRangeInput in bordered card (:479-481) → "Pisahkan PDF" button disabled unless `canSplit` (:484-495) → helper "Masukkan halaman yang ingin dipilih." only when input is empty (:497-501).
- Processing card (:409-421): "Sedang memisahkan {n} halaman..." + shimmer + client-side footnote (:417-419).
- Done card (:374-406): "PDF berhasil dipisahkan!" + "{n} halaman · {size}" (:381-384); "Unduh PDF" (:388-395); "Pisahkan file lain" (:397-404).
- Error card (:424-442): "Coba Lagi" returns to `ready` if a file with known page count is still present, else `idle` (:434).
- Idle state (:506-563): dropzone (copy "Seret PDF ke sini atau klik untuk memilih" :541-543; constraints "Maks 20MB · Hanya file PDF" :544) → badges ("Proses di browser / Tanpa upload server / Privasi terjaga" :221-225) → OtherTools (:561). **No empty-state text** (unlike merge/image-to-pdf).
- `PrivacyNotice model="client"` (:566).

**Configuration UX (PageRangeInput, shared with PDF-to-Image)**:
- Label "Halaman yang diambil" with `htmlFor="page-range"` (:109-111); input placeholder "Contoh: 1-3, 5, 7-10" (:117); helper "Masukkan nomor halaman atau rentang (1-3, 5, 7)" (:124-126).
- Parser (`PageRangeInput.tsx:19-89`): charset whitelist `[\d\s,\-]` → "Gunakan angka, tanda hubung, dan koma saja."; range `start-end` with start>end → "Rentang tidak valid: angka awal harus lebih kecil dari angka akhir."; out-of-bounds (incl. 0) → "Halaman X melebihi total halaman dokumen (N)."; bad token → `"<part>" bukan nomor halaman yang valid.`; output sorted, deduped.
- Error styling: rose border + focus ring (:118-122); error text below input (:129).
- Live preview (no error + >=1 page): "Halaman yang dipilih: 1, 3, 5 (3 halaman)" in accent (:132-136).
- Quick-select chips: "Halaman Pertama" / "Halaman Terakhir" / "Semua Halaman" (:139-161).
- `onChange(pages, raw)` via `useEffect` (:98-100); page stores `rangeError = raw.trim() !== '' && pages.length === 0` (`split/page.tsx:288-294`) so a partially-typed range keeps the button disabled.
- **A11y gap**: input has label + helper, but error text and live preview are plain `<p>` with no `aria-live`/`aria-invalid`/`aria-describedby` wiring.

**Result UX**: Programmatic download; filename derived from range — e.g. `1-3, 5` → `split_1-3_5.pdf` (:320-328); fallback `split_pages.pdf`.

**Analytics**: `trackTaskStarted('split')` / `trackTaskCompleted('split')` / `trackTaskFailed('split', 'server_error')` (:305, 311, 316) — note the failure reason string is `'server_error'` even though processing is client-side.

### 3.4 Image-to-PDF — Gambar ke PDF (`app/image-to-pdf/page.tsx`)

**Processing model**: **Hybrid** with a hardcoded 3MB total-size threshold (:43 `CLIENT_THRESHOLD_BYTES`): <= 3MB → client-side `imagesToPDF` (pdf-lib, `pdfUtils.ts:103-146`; WebP converted via OffscreenCanvas `webpToPng` :82-92); > 3MB → server `POST /api/image-to-pdf` (FormData multi-file, :497-519). The threshold is disclosed only in the processing footnote, not in the UI beforehand.

**State machine**: `'idle' | 'processing' | 'done' | 'error'` (:36) — no loading/ready step; validation happens synchronously per file on add.

**Page structure / component flow**:
- Header (:557-569): H1 "Gambar ke PDF" (:561-563), subtitle "Ubah foto atau gambar menjadi file PDF." (:564), context "Jadikan foto KTP, bukti transfer, atau hasil scan jadi PDF rapi untuk dikirim lewat email atau di-upload ke formulir online." (:565-568).
- Done card (:572-605): "PDF berhasil dibuat!" + "{n} gambar" with size **only for client-side results** (`resultData ? formatFileSize(...) : ''`, :580-583; the server response's `pdf_size` field is ignored — backend `image_to_pdf.py:191-195` returns it, frontend drops it). Download "Unduh PDF"; reset "Buat PDF lain".
- Processing card (:608-622): "Membuat PDF dari {n} gambar..." + shimmer + conditional footnote: browser note if <=3MB, "Mengirim ke server untuk diproses..." if >3MB (:616-620).
- Error card (:625-643): "Coba Lagi" → idle; images are kept.
- Upload zone + grid rendered in `idle | error` (:646-761).
- Feature badges when `images.length === 0` (:742-756): "Proses instan / Tanpa upload server / Privasi terjaga" (:351-355) — "Proses instan" is a slight overstatement for the server path, and "Tanpa upload server" only holds under 3MB.
- OtherTools inside the wrapper (:759). `PrivacyNotice model="hybrid"` (:764) — the only hybrid notice.

**File management**:
- Dropzone: `accept="image/jpeg,image/png,image/webp" multiple` (:666-678); copy "Seret gambar ke sini\natau klik untuk memilih" → "Tambah gambar lagi" (:682-686); constraints "Maks 20MB per file · JPG, PNG, WEBP" (:687-689).
- Three-layer validation (:392-445): (1) MIME type OR extension fallback (`.jpg/.jpeg/.png/.webp`) → "bukan format yang didukung. Hanya JPG, PNG, dan WEBP."; (2) size <= 20MB, non-empty; (3) **magic-bytes check** (JPEG FF D8 FF / PNG signature / RIFF…WEBP, :46-51, 415-424) → "bukan file gambar yang valid." — strongest validation of the five tools; catches renamed fakes.
- Thumbnail grid (`rectSortingStrategy`, :709): `grid-cols-2 gap-3 sm:grid-cols-3` (:710); card = 4:3 thumbnail (`<img alt={file.name}>` :312) + order badge + remove button + drag handle.
- Summary "{n} gambar dipilih · {size}" + reorder hint (:695-701).
- Empty state: "Belum ada gambar. Pilih minimal 1 gambar." (:735-739).
- CTA "Buat PDF" — **always enabled** (no `disabled` prop, :724-730); it is only rendered when >=1 image exists, so it is functionally safe but lacks the disabled affordance pattern the other tools use.
- Object URL hygiene: preview URLs created on add (:429), revoked on remove (:447-453) and reset (:537-550) — correct.

**Result UX**: client path → programmatic `downloadPDF(data, 'images.pdf')` (:529-531); server path → `window.open(resultUrl, '_blank')` (:533) — **popup-blocker risk and no `download` attribute/filename control**; download URL is a 1-hour signed R2 URL. Filename `images.pdf` in both paths.

**A11y gaps (worst of the five)**: remove button and drag handle are `opacity-0` revealed only on `group-hover` (:320-337) — invisible on touch devices and for keyboard users; a focused-but-not-hovered control stays invisible (no `focus-visible` fallback). Drag handle has no aria-label. No live-region announcements.

### 3.5 PDF-to-Image — PDF ke Gambar (`app/pdf-to-image/page.tsx`)

**Processing model**: Server-only (FastAPI `POST /api/pdf-to-image` with `file` + raw `pages` string, :310-317; backend `pdf_to_image.py:107-122`). Output: single PNG for 1 page, ZIP for multiple (`package_output`, backend :166-179); response `{download_url, file_type, page_count}` (:205-209).

**State machine**: `'idle' | 'loading' | 'ready' | 'processing' | 'done' | 'error'` (:14) — same two-step flow as Split.

**Page structure / component flow**:
- Header (:367-381): H1 "PDF ke Gambar" (:371-373), subtitle "Ubah halaman PDF menjadi gambar PNG berkualitas tinggi." (:374-376), context "Konversi slide presentasi, sertifikat, atau halaman dokumen jadi gambar untuk di-share di media sosial atau grup WhatsApp." (:377-380) — mixes English "di-share".
- Loading card (:455-462): "Membaca dokumen PDF..." (identical to Split).
- Ready state (:465-513): file info row + remove `aria-label="Hapus file"` (:468-486) → PageRangeInput card (:489-491) → "Ubah ke Gambar" button disabled unless `canConvert` (:494-505) → helper "Masukkan halaman yang ingin diubah ke gambar." when input empty (:507-511).
- Processing card (:419-431): "Mengubah {n} halaman menjadi gambar..." + shimmer + "File dikirim ke server untuk diproses — otomatis dihapus setelah 1 jam." (:427-429).
- Done card (:384-416): "Gambar berhasil dibuat!" + "{n} halaman · ZIP/PNG" (:391-394); download is an `<a href={download_url} download>` whose label switches "Unduh ZIP"/"Unduh Gambar" (:398-405); reset "Ubah file lain" (:407-414).
- Error card (:434-452): "Coba Lagi" → `ready` if file + page count known, else `idle` (:444).
- Idle (:516-573): dropzone "Seret PDF ke sini atau klik untuk memilih" / "Maks 20MB · Hanya file PDF" → badges → OtherTools. No empty-state text (same as Split).
- `PrivacyNotice model="server"` (:576).

**Feature badges** (:226-230) — the only tool whose badges describe the server reality: "Konversi cepat / Auto-hapus 1 jam / Privasi terjaga".

**Result UX**: server filename (`page.png` / `pages.zip`, backend :174-179) via anchor download — no programmatic filename generation. `file_type` drives both the metadata line and the CTA label. The `pages` raw string is sent as typed (e.g. "1-3, 5"); page count comes from the server response (`page_count`), not the local preview count.

**A11y**: same gaps as Split (no live regions on PageRangeInput; no progressbar role; drag N/A here — single file only).

---

## 4. Cross-Tool Consistency Matrix

| Dimension | Compress | Merge | Split | Image-to-PDF | PDF-to-Image |
|---|---|---|---|---|---|
| Processing model | Server | Client | Client | Hybrid (<=3MB client) | Server |
| PrivacyNotice model | server (:117) | client (:684) | client (:566) | hybrid (:764) | server (:576) |
| State machine | idle/uploading/processing/done/error | idle/processing/done/error | idle/loading/ready/processing/done/error | idle/processing/done/error | idle/loading/ready/processing/done/error |
| Page shell + header pattern | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dropzone pattern (classes, drag state, role=button, Enter/Space) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dropzone constraints copy | "Maks 20MB · Hanya file PDF · Dihapus dalam 1 jam" | "Maks 20MB per file · Hanya file PDF" | "Maks 20MB · Hanya file PDF" | "Maks 20MB per file · JPG, PNG, WEBP" | "Maks 20MB · Hanya file PDF" |
| Explicit action CTA | None (auto-upload) | "Gabungkan PDF" (disabled <2) | "Pisahkan PDF" (disabled w/o range) | "Buat PDF" (always enabled) | "Ubah ke Gambar" (disabled w/o range) |
| Processing indicator | Determinate % → shimmer | Shimmer | Shimmer | Shimmer | Shimmer |
| Processing footnote | "Mengoptimalkan gambar dan stream..." | "Proses berjalan di browser..." | "Proses berjalan di browser..." | conditional browser/server | "otomatis dihapus setelah 1 jam" |
| Done card layout | ✓ (+ before/after panel) | ✓ | ✓ | ✓ | ✓ |
| Result metadata | before/after + −% | n file · size | n halaman · size | n gambar (+size client only) | n halaman · ZIP/PNG |
| Download mechanism | `<a download>` | programmatic button | programmatic button | button (client) / `window.open` (server) | `<a download>` |
| Download filename | `compressed_<name>` (server) | `merged.pdf` (hardcoded EN) | `split_<range>.pdf` (generated) | `images.pdf` | `page.png` / `pages.zip` |
| Reset CTA | "Kompres file lain" | "Gabungkan file lain" | "Pisahkan file lain" | "Buat PDF lain" | "Ubah file lain" |
| Error → "Coba Lagi" behavior | reset to idle (file dropped) | idle (files kept) | ready if parsed else idle | idle (images kept) | ready if parsed else idle |
| Empty-state text | n/a (auto-flow) | "Belum ada file. Upload minimal 2 PDF." | none | "Belum ada gambar. Pilih minimal 1 gambar." | none |
| Feature badges visible when | uploader idle | files.length === 0 | idle | images.length === 0 | idle |
| Feature badge copy | Proses instan / Aman & privat / Kualitas terjaga | Proses di browser / Tanpa upload server / Privasi terjaga | Proses di browser / Tanpa upload server / Privasi terjaga | Proses instan / Tanpa upload server / Privasi terjaga | Konversi cepat / Auto-hapus 1 jam / Privasi terjaga |
| OtherTools visibility | **always** (:135) | idle/error only (:679) | idle only (:561) | idle/error only (:759) | idle only (:571) |
| Validation depth | MIME + size + empty | type + size + empty | type + size + empty | MIME/ext + size + empty + **magic bytes** | type + size + empty |
| Per-file validation message style | "Tipe file tidak valid. Hanya file PDF yang diterima." | `"<name>" bukan file PDF.` | `"<name>" bukan file PDF.` | `"<name>" bukan format yang didukung...` | `"<name>" bukan file PDF.` |
| Analytics (start/complete/fail) | ✓ (incl. rate_limit, invalid_file) | ✓ | ✓ | ✓ | ✓ |
| Retry behavior | silent auto-retry 1s (server errors) | none | none | none | none |
| aria-live / role=status / progressbar semantics | none | none | none | none | none |
| Heading structure | h1 → h3 badges (no h2) | h1 → h3 badges | h1 → h3 badges | h1 → h3 badges | h1 → h3 badges |

✓ = matches the shared pattern described in §2.

---

## 5. Preserve (Confirmed Baseline — keep in rebuild)

1. **Page shell + header anatomy** — max-w-xl container, icon tile, H1, subtitle, context paragraph with an Indonesia-specific use case. Consistent across all five and the strongest part of the design.
2. **State-card language** — done (accent border + emerald check), processing (shimmer), error (rose) cards with `animate-fade-up`; identical classes.
3. **Dropzone interaction contract** — dashed border, drag-over highlight, `role="button"` + tabIndex + Enter/Space, hidden input, 20MB constraint line.
4. **PrivacyNotice always visible** with accurate per-model copy (server/client/hybrid) — including pdf-to-image's "Auto-hapus 1 jam" promise which matches backend retention (signed URL 3600s, `config.ts:31-33`).
5. **PageRangeInput UX** — labeled input, placeholder example, inline parse errors, live selected-pages preview, quick-select chips (First/Last/All). Parser errors are specific and localized (out-of-bounds, start>end, bad token).
6. **Merge/image-to-pdf sortable lists** — pointer + keyboard sensors with 5px activation distance, order badges, per-item remove with aria-label.
7. **image-to-pdf magic-bytes validation** — best-in-class file validation; worth extending to the PDF tools (PDF header `%PDF` check) in the rebuild.
8. **Compress before/after size panel** with saved-percentage pill — the clearest result feedback; good template for other result cards.
9. **Analytics discipline** — task_started/completed/failed with tool names and failure reasons, device category.
10. **Per-tool metadata layouts** with localized titles and per-tool OG images.
11. **Client-side privacy framing in processing footnotes** — accurate and reassuring ("file tidak dikirim ke server").

## 6. Correct (Deviations / Fixes for the Rebuild)

1. **OtherTools visibility inconsistency** (compress always visible; merge/image-to-pdf in idle|error; split/pdf-to-image only idle). Recommend one rule for all five — either always visible (compress) or hidden during processing/done only. Splitting the difference hides navigation exactly when users finish a task and might want the next one.
2. **Download filename inconsistency** — `merged.pdf` is hardcoded English; split generates `split_<range>.pdf`; image-to-pdf always `images.pdf`. Standardize: derive a name from the source file(s), e.g. `merged_<first>.pdf`, `gambar_ke_pdf.pdf`, or per-tool Indonesian defaults.
3. **image-to-pdf server path uses `window.open`** — popup blockers can silently kill the download. Prefer an `<a download href>` like compress/pdf-to-image, or a hidden anchor click. Also: server returns `pdf_size` but the done card omits size for server results — display it for parity with the client path.
4. **Auto-retry in PDFUploader** — keep, but clear the `setTimeout` on unmount/reset and consider capping attempts; also surface "Mencoba ulang..." state honestly (it currently shows during 'uploading' with 0% bar).
5. **Hardcoded `quality=ebook`** — either expose screen/ebook/printer as a real configuration step (backend already supports it) or remove the query param from the URL and let the backend default; document the decision.
6. **Hover-only controls in image-to-pdf grid** — remove button + drag handle are `opacity-0 group-hover:opacity-100` with no `focus-visible` fallback; invisible on touch/keyboard. Make them always visible (at reduced opacity) or `focus-visible:opacity-100`.
7. **Accessibility semantics** — add to all five: `role="status"`/`aria-live="polite"` on processing and done transitions, `role="alert"` on error cards, `role="progressbar"` + `aria-valuenow` on the determinate upload bar, `aria-invalid`/`aria-describedby` wiring in PageRangeInput (error + live preview), and `aria-label` on drag handles ("Ubah urutan <name>"). Consider dnd-kit `announcements` for keyboard reorder feedback.
8. **Heading hierarchy** — feature-badge cards use `h3` directly under `h1` (no h2). Either demote badges to plain text with `font-semibold` or insert a visually-hidden h2.
9. **Dropzone copy drift** — "Maks 20MB" vs "Maks 20MB per file"; "atau klik untuk upload" vs "atau klik untuk memilih"; compress mentions "Dihapus dalam 1 jam" on the dropzone while pdf-to-image only says it in the processing footnote. Align constraint-line grammar and per-tool claims.
10. **Validation message style drift** — compress's PDFUploader uses "Tipe file tidak valid..." while merge/split/pdf-to-image use `"<name>" bukan file PDF.`. Use one template that includes the filename (and, ideally, the offending MIME type).
11. **Empty-state copy missing** on split and pdf-to-image (merge and image-to-pdf have it). Add "Belum ada file. Upload PDF untuk memulai." equivalents.
12. **Disabled-CTA consistency** — image-to-pdf's "Buat PDF" never shows the disabled state (button simply doesn't render without images). Use the same disabled style + helper-text pattern as the other tools for consistency.
13. **`'server_error'` failure reason on client-side tools** (split/merge/image-to-pdf client path) — mislabeled; use a distinct reason like `'processing_error'` or `'client_error'`.
14. **Informal "kamu" only in split header** (and "di-share" in pdf-to-image) — pick one tone register (recommend keeping the neutral register used by compress/merge/image-to-pdf).
15. **formatPercent floors at 0** — a result that got larger shows "−0%"; consider showing "0%" or hiding the pill when `compressed >= original`.
16. **Hybrid threshold disclosure** — image-to-pdf's 3MB client/server split is invisible until processing starts; state it under the dropzone ("<=3MB diproses di browser, lebih besar dikirim ke server") or in the badges.

---

## 7. Test Coverage Status (evidence for rebuild planning)

- **Frontend unit**: `lib/__tests__/pdfUtils.test.ts` covers `getPDFPageCount`, `mergePDFs` (incl. <2 files), `splitPDF` (incl. empty/out-of-range/page 0), `imagesToPDF` (PNG, empty, unsupported). **No frontend unit tests for**: PDFUploader, PageRangeInput, PrivacyNotice, OtherTools, or any of the five pages (verified via glob of `src/__tests__/` and `src/components/__tests__/` — only PasswordInput.test.ts exists there).
- **E2E**: `smoke.spec.ts` asserts all 13 tool routes return 200. `client-tools.spec.ts` covers Merge (2 tests: happy path + disabled-until-2-files) and Split (2 tests: range extraction + out-of-range rejection) — **no e2e for Compress, Image-to-PDF, or PDF-to-Image** (server-dependent).
- **Backend**: `tests/test_api_compress.py`, `tests/test_api_pdf_to_image.py`, `tests/test_api_image_to_pdf.py`, plus `test_compress.py`, `test_pdf_to_image.py`, `test_pdf_validator.py`, `test_full_flow.py` exist (not inspected in depth — out of UX scope).
- Rebuild implication: the launch tools' interactive states (drag/drop, disabled CTA, range errors, retry) are currently protected only by e2e for merge/split; the other three need equivalent coverage.

## 8. Uncertainties & Unresolved Questions

1. **Visual rendering unverified** — static source audit only; no browser run. Actual spacing, contrast, and font rendering were not confirmed (e.g., `text-accent/80` on "Sesudah" label, `bg-slate-50` panel contrast).
2. **`package_output` internals not read** — ZIP-vs-PNG decision confirmed only via router comments and response `file_type` (`pdf_to_image.py:166-179`); the service function itself (`services/pdf_to_image_service.py`) was not inspected.
3. **R2 cleanup mechanics not read** — `utils/cleanup.py` and `utils/r2.py` were not inspected; the "auto-hapus 1 jam" claim rests on `generate_signed_url(expiry_seconds=3600)` + `config.ts` retention constant.
4. **Backend image-to-pdf `pdf_size`** is returned but unused by the frontend — intent unknown (was it meant to mirror compress's before/after panel?).
5. **dnd-kit keyboard experience** — KeyboardSensor is configured, but without `announcements` the live-region feedback cannot be verified statically; needs a screen-reader pass in the rebuild.
6. **Compress quality preset** — no evidence in the repo of a product decision to lock `ebook`; flag for owner confirmation before the rebuild copies it.
7. **Merge error path when adding files fails while state === 'error'** — `addFiles` sets state to idle only when `errors.length === 0`; if a valid file is added alongside an invalid one, state stays 'error' until "Coba Lagi" is clicked (the file IS added though). Confirm desired behavior (auto-clear error when valid files are added).
8. **`formatFileSize(0)` returns "0 KB"** — theoretical edge (0-byte results are blocked at validation); harmless but noted.

## 9. Chat-Only Summary Is Insufficient

Per AGENTS.md, this file is the primary deliverable. The parent agent must read it before using these findings.
