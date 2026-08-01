# A5 — JPG to PDF Research Brief

## 1. Header

- **Brief ID**: A5
- **Path**: `<workspace-root>\audit-outputs\research\track-a\a5-jpg-to-pdf.md`
- **Track**: A — Tool and engine research
- **Title**: JPG to PDF research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (Track A executor subagent)
- **Status**: Draft (complete for owner review; no accepted product decision)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (A5; §7.1; §8)
- **Governing decisions**: DEC-011 (hybrid browser-first), DEC-015 (browser limits: 50 images/100 MP desktop, 40 MP mobile), DEC-041 (automatic fitting), DEC-042 (naming), DEC-054-060, DEC-066, DEC-082 (per-image page size/orientation), DEC-083/DEC-085/DEC-089 (Letter/A4 paper policy via edge country, A4 fallback), DEC-084 (metadata preservation incl. EXIF GPS — accepted risk), DEC-088 (threat blocking), DEC-093 (byte-level validation and decode isolation), DEC-168 (processing disclosure), DEC-179, DEC-186 (n/a), DEC-187 (accepts JPG/JPEG, PNG, WebP at launch)
- **Engine/license evidence**: cited from `a1-shared-engine-licenses.md`
- **Files read**: all files listed in A1 §1, plus tool-specific: `papyr-reference/backend/routers/image_to_pdf.py` (full), `papyr-reference/frontend/src/lib/pdfUtils.ts` (imagesToPDF/webpToPng, full), `papyr-reference/frontend/src/app/image-to-pdf/page.tsx` (lines 1-120, 480-559), audit `ui-five-tools-audit.md` §3.4 and §4, img2pdf manpage and PyMuPDF image docs (2026-07-31)

## 2. Scope

JPG to PDF converts images into a single PDF with automatic, safe fitting and **no settings** (DEC-041). Approved Papyr behavior:

- Officially accepts JPG/JPEG, PNG, and WebP at launch; tool name remains "JPG to PDF" (DEC-187).
- Inputs validated by actual bytes (magic bytes and structure), dimensions, pixel count, frame count where applicable, orientation data, decode expansion, and resource limits — not extension alone (DEC-093); threat-classified files blocked (DEC-088); ordinary invalid images get safe localized errors.
- Automatic fitting per image: standard page size + portrait/landscape chosen per image; preserve aspect ratio, no cropping, respect EXIF orientation; deterministic page-size and margin rules (DEC-041, DEC-082).
- Paper policy: Letter-family for US/Canada from the trusted edge country code; A4-family elsewhere; A4 deterministic fallback; selected standard visible before processing; interfaces with B3 for the locale/region rule (DEC-083/085/089).
- Image order user-adjustable before conversion (DEC-041).
- Source metadata preserved to the greatest extent supported by the transformations, including EXIF GPS/timestamps/device info (DEC-084, accepted risk); interface and Privacy docs disclose that metadata may remain.
- Hybrid, browser-first: small jobs local, larger jobs server (DEC-011); legacy hardcoded 3 MB threshold replaced by DEC-015 limits and capability routing (arch §11.5).
- Output naming source-derived + localized (DEC-042); legacy `images.pdf` replaced.
- Server results via signed URLs (DEC-170); one-hour retention; per-tool limits (DEC-034).

## 3. Non-goals

- No manual A4/Letter, orientation, DPI, or margin controls (DEC-041).
- No renaming or re-branding the tool despite PNG/WebP support (DEC-187).
- No metadata-stripping option (future feature — DEC-084).
- No benchmark program (DEC-066).
- No image editing/cropping/compression controls.
- No AGPL compliance decision here (A1 §9).

## 4. Research questions

1. Which engines satisfy hybrid browser-first conversion with WebP acceptance, EXIF orientation, per-image fitting, and DEC-084 metadata preservation?
2. Licenses and obligations (cite A1).
3. Current versions and documentation (A1).
4. Representative failure modes and resource profiles for image sets, qualitatively.
5. Legacy behavior retained/corrected/superseded, with citations.
6. At least two viable alternatives with trade-offs; recommendation.
7. Measurable acceptance criteria (functional).
8. Cross-track interfaces (B1, C2, C4, D5 — plus B3 for paper policy).

## 5. Evidence

### 5.1 Engine capability evidence (primary sources, 2026-07-31)

- **pdf-lib 1.17.1 (MIT; unmaintained)** — browser path (legacy `pdfUtils.ts:103-146`): `embedPng`/`embedJpg` embed the original image streams (original JPEG/PNG bytes are stored in the PDF, so embedded-stream metadata survives); **WebP is not embeddable** — must be decoded first (legacy `webpToPng` uses `createImageBitmap`, whose default `imageOrientation: 'from-image'` applies EXIF orientation — MDN), then embedded as PNG. No EXIF-orientation application for direct JPEG/PNG embeds (dimensions taken from stream headers) — the legacy browser path does **not** apply EXIF orientation for JPEG/PNG inputs (DEC-041/082 require respecting EXIF orientation → corrected). Page geometry: legacy creates a page sized to image pixels (1 px = 1 pt) with no margins — superseded by DEC-041/082 standard-page fitting.
- **img2pdf 0.6.3 (LGPL-3.0)** — lossless container conversion: JPEG/JPEG2000/non-interlaced-PNG embedded **directly** (container overhead ~500-700 B; source metadata survives by construction); other formats (incl. WebP) stored via PNG Paeth re-encode (metadata best-effort only); `--rotation auto` (default) applies EXIF Orientation; `--auto-orient` swaps page dimensions to image orientation; `--pagesize`/`--border` support Letter/A4 and margins. Fits DEC-041/082 (per-image pagesize + auto-orient) and DEC-084 (direct-embed preservation for JPEG/PNG). Does not set PDF-document-level metadata (author/title) itself.
- **Pillow 12.3.0 (HPND)** — decode/encode JPG/PNG/WebP; `ImageOps.exif_transpose`; `Image.save(..., exif=...)`; PDF writing with `save_all`/`append_images`; resource limits via `Image.MAX_IMAGE_PIXELS`; CVE-2026-59199 (fixed 12.3.0) demonstrates decode/transform risk with current-version mandate. WebP decoded → must re-encode for PDF (metadata best-effort per DEC-084).
- **PyMuPDF 1.28.0 (AGPL/commercial)** — `insert_image` accepts filename/stream/pixmap; MuPDF decodes JPEG/PNG/WebP etc.; JPEG/PNG embedded natively, other formats (incl. WebP) may be stored uncompressed unless `deflate=True` (docs) — large outputs for WebP unless re-encoded; legacy server path uses it (`image_to_pdf.py:125-162`); document-level metadata settable. AGPL fork (A1 §9).
- **Browser createImageBitmap** — default EXIF orientation handling (MDN `imageOrientation: 'from-image'`); used for WebP decode; canvas size limits constrain large images on mobile (16 MP iOS Safari ceiling — A1 §5.1).

### 5.2 Legacy evidence (read-only)

| Legacy fact | Location | Disposition |
|---|---|---|
| Accepted MIME/ext: image/jpeg, image/png, image/webp; .jpg/.jpeg/.png/.webp | `frontend/src/app/image-to-pdf/page.tsx:40-41`; `backend/routers/image_to_pdf.py:28-29` | Retain (DEC-187 formalizes it) |
| Magic-byte validation (JPEG FF D8 FF, PNG signature, RIFF....WEBP) — strongest of the five tools | `image-to-pdf/page.tsx:45-72`; `routers/image_to_pdf.py:33-36, 72-81` | Retain as the base of DEC-093 validation; extend with dimensions/pixel-count/decode-expansion checks |
| Hybrid 3 MB threshold | `image-to-pdf/page.tsx:43` | **Superseded** by DEC-015 limits and capability routing (arch §11.5) |
| Client conversion: embedJpg/embedPng; WebP→canvas→PNG; page sized to pixels | `frontend/src/lib/pdfUtils.ts:103-146` (webpToPng `:82-92`) | Corrected: standard-page fitting + EXIF orientation + margins (DEC-041/082); retain WebP decode pattern |
| Server conversion: PyMuPDF; page sized to image `rect`; `insert_image`; output `images.pdf` | `routers/image_to_pdf.py:125-162, 171-178` | Corrected: standard pages, per-image orientation; naming via DEC-042 |
| Server response `pdf_size` returned but dropped by frontend done card | `routers/image_to_pdf.py:191-195`; audit §3.4/§6 item 3 | Corrected: show size for both paths (UX §12.4) |
| Server path download via `window.open` (popup-blocker risk) | `image-to-pdf/page.tsx:533` | Corrected: anchor/signed-URL download (UX §12.4) |
| Hover-only remove/drag controls in thumbnail grid | audit §3.4/§6 item 6 | Corrected (always-visible/focus-visible) |
| FAQ says "Papyr mendukung file PDF, JPG, dan PNG" (missing WebP) | `ui-docs-code-reconciliation.md` §8.9 (faq/page.tsx:81) | Corrected by copy governance (DEC-187 formats) |
| Legacy privacy/FAQ claims "tidak ada tracking" | reconciliation §8.8 | Re-scoped per DEC-022/025/045 (UX §21.17) |

### 5.3 Legacy behavior: retained / corrected / superseded

- **Retained**: accepted formats; magic-byte validation approach; sortable thumbnail grid; hybrid model concept; per-image-one-page model (rebuilt on standard pages).
- **Corrected**: page sizing (pixel-sized → standard paper + margins, DEC-041/082); EXIF orientation (applied, DEC-041); WebP storage (re-encode to JPEG/PNG to avoid uncompressed PDF streams); server `pdf_size` display; `window.open` download; thumbnail controls visibility; FAQ/privacy copy.
- **Superseded**: 3 MB hardcoded threshold (DEC-015/034); `images.pdf` naming (DEC-042); dropzone "20MB per file" copy (unified constraints per audit §6 item 9).

## 6. Alternatives

1. **Hybrid: browser pdf-lib + server img2pdf/Pillow (recommended shape).** Browser: pdf-lib with WebP→PNG decode (createImageBitmap, EXIF-aware) for small jobs. Server: **img2pdf** for JPEG/PNG (lossless direct embed, EXIF orientation auto, Letter/A4 pagesize, borders) + **Pillow** for WebP decode→PNG pre-processing and any decode-isolation needs, with PDF-document metadata set by a thin wrapper (pdf-lib or PyMuPDF-free path via img2pdf's metadata hooks if available — verify at design). Trades: permissive licenses (LGPL-3.0/HPND/MIT); lossless JPEG/PNG embedding best preserves DEC-084; WebP is re-encoded (metadata best-effort — honest disclosure per DEC-084); two server components to integrate.
2. **Server-only PyMuPDF.** Trades: single engine; AGPL/commercial fork; WebP handled but uncompressed unless re-encoded/deflated (output-size risk); page-level and doc-level metadata settable; no first-class sanitization needed (images only). Viable if AGPL terms accepted.
3. **Server-only Pillow.** Trades: single permissive engine; full control of decode (resource limits), EXIF transpose, re-encode, PDF save (multi-page via save_all); but re-encodes everything (JPEG/PNG lossy path unless careful — quality/file-size trade-off; metadata preservation weaker than direct embed), and PDF output fidelity is basic.
4. **Server-only img2pdf.** Trades: best lossless/EXIF behavior for JPEG/PNG; WebP needs a pre-decode step (Pillow) anyway; no document metadata API of its own. Recommend pairing with a metadata layer regardless.

Privacy/security: all image decoders are untrusted-input surfaces (DEC-093); Pillow decode limits (`MAX_IMAGE_PIXELS`), byte-level validation, isolated decode boundary, and C4 malware scanning apply; EXIF fields are preserved but never executed/logged/trusted (DEC-084/DEC-093).

## 7. Recommendation

**Recommendation (not an accepted decision — DEC-054/057):** implement the **hybrid path**: browser pdf-lib for small jobs (WebP→PNG decode with EXIF-aware `createImageBitmap`; JPEG/PNG embedded directly) and a **server path combining img2pdf (LGPL-3.0) for lossless JPEG/PNG embedding with EXIF auto-orientation and per-image Letter/A4 pagesize + margins, plus Pillow (HPND) for WebP decode and resource-limited validation**, with a thin PDF-document-metadata layer for the DEC-084 disclosure surface. This maximizes permissive licensing, EXIF/metadata preservation (DEC-084), and the DEC-041/082 fitting contract while keeping the DEC-187 format surface. PyMuPDF remains a viable single-engine alternative only under the owner's AGPL decision (A1 §9). The paper-policy mapping (Letter/A4) is implemented as an interface consumed from B3 (DEC-083/085/089).

## 8. Measurable acceptance criteria

1. JPG/JPEG, PNG, and WebP inputs are all accepted and converted to one PDF; the tool name and copy say "JPG to PDF" (DEC-187).
2. A renamed-fake fixture (e.g., .jpg text file, .png containing non-PNG bytes) is rejected by byte-level validation with a safe localized error (DEC-093).
3. Decode-expansion limits (pixel count, dimensions, frame count) reject oversized/decompression-bomb inputs before decode; threat-classified files are blocked (DEC-088/093).
4. Each image maps to a standard page (Letter for US/CA, A4 elsewhere, A4 fallback) with portrait/landscape per image and safe margins; aspect ratio preserved; no cropping (DEC-041/082).
5. A fixture with EXIF Orientation 6/8 renders upright (DEC-041).
6. Mixed portrait/landscape sets produce a PDF with per-image page orientation (DEC-082).
7. The selected paper standard is visible before processing (DEC-083/085).
8. Metadata disclosure: the interface and Privacy page state that source metadata (incl. EXIF GPS) may remain; a JPEG with EXIF GPS embedded via the lossless path retains the GPS data in the output stream (DEC-084) — best-effort verification for re-encoded formats is disclosed, not guaranteed.
9. Order is user-adjustable and preserved in the output (DEC-041).
10. Browser jobs within DEC-015 limits run locally; larger jobs route to the server with truthful stage labels (DEC-011/015/168).
11. Output naming is source-derived and localized (DEC-042); server results use signed URLs and the one-hour retention clock (DEC-170/013/067).
12. No fabricated progress/quality claims (DEC-033, DEC-080-style honesty applied to conversion results).

## 9. Assumptions, uncertainties, and unresolved questions

1. **WebP metadata through re-encode**: EXIF/XMP in WebP is re-encoded to PNG (or JPEG) by Pillow/canvas; full preservation is not guaranteed — DEC-084's "best effort, not byte-for-byte fidelity" applies; verify per-format behavior with fixtures.
2. **Paper-policy region rule** for EN/ES markets where language alone does not identify Letter vs A4 is B3's deliverable (DEC-083/085/089, UX §21.3); this brief assumes the interface consumes it.
3. **img2pdf document metadata** capabilities (title/author at PDF Info level) need verification at design time; pdf-lib can set document metadata on the client path, and a small metadata layer can be added server-side.
4. **Browser EXIF orientation** for direct JPEG/PNG embeds: pdf-lib does not transpose pixels; the recommended design applies orientation during decode (createImageBitmap) or reads EXIF and adjusts page dimensions/rotation — exact approach is design work with fixture verification (DEC-041).
5. Owner questions: (a) AGPL acceptance for PyMuPDF as a possible single-engine option; (b) confirmation that re-encoded formats (WebP) may lose some metadata (accepted risk boundary of DEC-084).

## 10. Dependencies and cross-track interfaces

- **A1**: license/version evidence (img2pdf LGPL-3.0, Pillow HPND, pdf-lib MIT/unmaintained, PyMuPDF AGPL).
- **B1**: browser routing thresholds (image count, total megapixels per DEC-015; canvas limits for WebP decode).
- **B3**: Letter/A4 paper-policy mapping (DEC-083/085/089; UX §21.3) — this brief implements the interface.
- **C2**: per-tool server limits (image count, per-file bytes, total megapixels, output PDF size) (DEC-034).
- **C4**: decode isolation, resource limits, malware scanning (DEC-093, DEC-169, DEC-171).
- **D5**: threat blocking before decode (DEC-088); metadata-preservation register (DEC-084) feeds the D5 prohibited-data review.
- **X2**: surfaces the JPG-to-PDF engine approval and the WebP metadata-acceptance item.

## 11. Source-date log and evidence-completeness notes

- Sources: img2pdf PyPI + Debian manpage, Pillow release notes + NVD CVE-2026-59199, PyMuPDF image docs, MDN createImageBitmap, pdf-association WebP discussion — all accessed 2026-07-31 (A1 §5.1). Legacy files read 2026-07-31 with citations above.
- Completeness: `image-to-pdf/page.tsx` (767 lines) verified via full read of the header/validation/processing sections and audit §3.4; no runtime validation performed (prohibited); EXIF/metadata behaviors are documented as design-and-fixture items.

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative report, or quality-score program (DEC-066).
- No installs, builds, servers, VPS access, deployment, account creation, or authenticated remote actions (plan §4.1).
- `papyr-reference/` read-only; `git -C papyr-reference status --porcelain` empty with exit 0 before and after.
- No claim of malware-free output, universal sanitization, or guaranteed metadata preservation (DEC-084, DEC-090, DEC-171).
- Recommendation only; owner approval required (DEC-057).
