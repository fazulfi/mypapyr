# A6 — PDF to JPG Research Brief

## 1. Header

- **Brief ID**: A6
- **Path**: `<workspace-root>\audit-outputs\research\track-a\a6-pdf-to-jpg.md`
- **Track**: A — Tool and engine research
- **Title**: PDF to JPG research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (Track A executor subagent)
- **Status**: Draft (complete for owner review; no accepted product decision)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (A6; §7.1; §8)
- **Governing decisions**: DEC-011 (hybrid), DEC-015 (browser limits: 200 pages desktop / 50 mobile, sequential rendering, 16-MP per-page ceiling), DEC-030/DEC-065 (server fallback), DEC-036/DEC-064 (encrypted input), DEC-037 (ZIP + individual downloads), DEC-039 (automatic high-quality profile), DEC-042 (naming), DEC-054-060, DEC-066, DEC-081 (white compositing), DEC-088 (threat blocking), DEC-092 (untrusted-input rendering), DEC-168 (disclosure), DEC-179, DEC-186 (duplicate-preserving, order-preserving page selection)
- **Engine/license evidence**: cited from `a1-shared-engine-licenses.md`
- **Files read**: all files listed in A1 §1, plus tool-specific: `papyr-reference/backend/routers/pdf_to_image.py` (full), `papyr-reference/backend/services/pdf_to_image_service.py` (full), `papyr-reference/backend/tests/test_pdf_to_image.py` (full), `papyr-reference/frontend/src/components/PageRangeInput.tsx` (full), audit `ui-five-tools-audit.md` §3.5 and §4, pypdfium2 PyPI/docs and PyMuPDF Page docs (2026-07-31)

## 2. Scope

PDF to JPG converts selected PDF pages to high-quality JPG images with one automatic output profile and **no settings** (DEC-039). Approved Papyr behavior:

- One automatic high-quality profile; no Standard/High/Maximum/DPI/JPEG-quality controls (DEC-039); text and line art crisp for normal high-quality screen use within the 16-MP per-page safety ceiling for browser processing (DEC-015/039); the UI never implies conversion can create missing detail from low-resolution sources (DEC-039).
- **Transparency**: pages composited onto white before JPEG encoding, deterministically, in both browser and server paths (DEC-081).
- **Page selection**: duplicate-preserving and order-preserving, matching Split semantics — repeated/overlapping selections produce independent outputs in the user-entered order; range syntax and validation per DEC-038; preview shows duplicated membership and effective sequence (DEC-186, DEC-077/078); output names, ZIP contents, individual downloads, and manifest disambiguate duplicates (DEC-186/037/078).
- Browser-capable with server fallback (DEC-011/015/030/065); sequential page rendering; 16-MP ceiling.
- Encrypted input: password requested only when required (DEC-036/064).
- Untrusted-input rendering: source PDFs inspected for parser and infrastructure safety; rendering with isolation, least privilege, bounded resources, current patched dependencies; active content not represented in raster output but no execution/following of external references (DEC-092); threat-classified inputs blocked (DEC-088).
- Multi-file results: ZIP auto-download + individual downloads (DEC-037); single-page jobs download directly; the legacy `file_type` PNG-vs-ZIP model is replaced (UX §12.5).
- Output naming: source-derived with localized suffixes; duplicates disambiguated (DEC-042, DEC-186); legacy `page.png`/`pages.zip` defaults replaced.
- Server results: one-hour retention, signed URLs, per-tool limits (DEC-013/034/070/170).

## 3. Non-goals

- No JPEG-quality, DPI, or profile controls (DEC-039).
- No benchmark program or comparative quality study (DEC-066) — the output profile is a design choice validated by functional verification and production observation (UX §21.1 item 2; arch §11.6).
- No PNG output path (the rebuild outputs JPG; DEC-037/UX §12.5).
- No OCR or text extraction.
- No AGPL compliance decision here (A1 §9).

## 4. Research questions

1. Which engines satisfy server rendering with white compositing, and which satisfy browser rendering within the 16-MP ceiling?
2. Licenses and obligations (cite A1).
3. Current versions and documentation (A1).
4. Representative failure modes and resource profiles (pixel expansion, memory, sequential rendering), qualitatively.
5. Legacy behavior retained/corrected/superseded, with citations (150 DPI PNG, sort/dedupe semantics).
6. At least two viable alternatives with trade-offs; recommendation.
7. Measurable acceptance criteria (functional).
8. Cross-track interfaces (B1, C2, C4, D5).

## 5. Evidence

### 5.1 Engine capability evidence (primary sources, 2026-07-31)

- **PyMuPDF 1.28.0 (AGPL-3.0/commercial)** — legacy server engine (`pdf_to_image_service.py:14, 135-172`): `page.get_pixmap(matrix=zoom)` with `zoom = dpi/72`; **documented white compositing**: with `alpha=False` (default) the pixmap samples are pre-cleared with 0xFF, "resulting in white where the page has nothing to show" (PyMuPDF `Page` docs — primary evidence for DEC-081). Pixmap memory = width × height × channels (RGB ~3 B/px, 25% more with alpha) — the 16-MP ceiling maps to ~48 MB per page RGB pixmap before JPEG encode. Supports encrypted PDFs with password. AGPL fork (A1 §9).
- **pypdfium2 5.12.1 (Apache-2.0/BSD-3-Clause; PDFium BSD)** — rendering via `page.render(scale=...)` with **documented white background fill** example (`FPDFBitmap_Create` + `FPDFBitmap_FillRect(..., 0xFFFFFFFF)` — pypdfium2 README), scale→DPI formula (`scale = dpi/72`), `bitmap.to_pil()` for JPEG encode; encrypted PDFs supported; permissive licensing; fast rendering (project claims). Strong candidate if the owner wants to avoid AGPL.
- **Ghostscript 10.07.1 (AGPL/commercial)** — raster devices (`-sDEVICE=jpeg`, `-r`, `-dJPEGQ`, `-dQFactor`, `-dFirstPage/-dLastPage`); white paper background by default for the jpeg device; same AGPL fork and CVE/sandbox posture as A2; historically the "industry standard" rasterizer (legacy feasibility claim).
- **poppler 26.07.0 (pdftoppm, GPLv2/GPLv3)** — `pdftoppm -jpeg -r <dpi>`; white paper background by default; monthly releases with malformed-document crash fixes (A1 §5.3). GPL: server use without distribution is fine; conveying in the Docker image triggers source/relink obligations for that component.
- **pdf.js (pdfjs-dist 6.2.108, Apache-2.0)** — browser rendering to canvas: one canvas per page (no tiling — pdf.js FAQ and Apryse guide); `getDocument({password})` supports encrypted PDFs; canvas-size caps to avoid downscale; memory profile = width × height × 4 B/canvas (FAQ); the 16-MP iOS Safari canvas ceiling (A1 §5.1) bounds browser rendering; JPEG encode via `canvas.toBlob('image/jpeg', quality)` after white fill (fill must be implemented explicitly — pdf.js does not guarantee a white canvas by default; DEC-081 requires the explicit white fill in the render loop).

### 5.2 Legacy evidence (read-only)

| Legacy fact | Location | Disposition |
|---|---|---|
| Server engine PyMuPDF at 150 DPI, PNG output | `pdf_to_image_service.py:23, 112-184` | **Superseded** — automatic JPG profile (DEC-039); 150 DPI PNG was a preset, not an accepted requirement (DEC-059) |
| `parse_page_range` sorts and dedupes (set) | `pdf_to_image_service.py:54, 109` | **Superseded** by DEC-186 (duplicate-preserving, order-preserving) |
| ZIP naming `page_1.png`, `page_2.png` (1-indexed) | `pdf_to_image_service.py:210-213` | Superseded naming; DEC-042/186 require source-derived names with duplicate disambiguation |
| Response `file_type` (`"png"` or `"zip"`); single PNG for 1 page | `routers/pdf_to_image.py:174-179, 205-209` | **Superseded** by ZIP + individual downloads model (DEC-037, UX §12.5) |
| Encrypted PDFs rejected with 400 | `routers/pdf_to_image.py:88-97` | **Superseded** by password flow (DEC-036/064) |
| Validation order (empty/MIME/ext/magic/size/encrypted) | `routers/pdf_to_image.py:40-104` | Retain as base; extend per DEC-092/093 structure checks + C4 scanning |
| Page range format "1-3,5"; errors for 0, out-of-bounds, bad tokens | `pdf_to_image_service.py:26-109`; tests `test_pdf_to_image.py:423-495` | Retain syntax/validation per DEC-038; change semantics to order-preserving/duplicate-preserving (DEC-186) |
| Legacy tests assert PNG/ZIP outputs and dedupe-friendly behavior | `tests/test_pdf_to_image.py:281-495` | Legacy fixtures are reference evidence; rebuild fixtures assert DEC-186/037/081 semantics |
| 60 s rasterize timeout; 150 DPI constant | `pdf_to_image_service.py:20, 23` | Retain timeout concept; profile becomes design choice (DEC-039) |
| Frontend: server-only page with PageRangeInput; done card "n halaman · ZIP/PNG"; download via anchor | audit §3.5 (`pdf-to-image/page.tsx:384-416, 494-505`) | Corrected per UX §12.5 (browser-capable, JPG, ZIP+individual) |
| Legacy two-step flow "Membaca dokumen PDF..." | `pdf-to-image/page.tsx:455-462` | Retain (UX §12.5) |

### 5.3 Legacy behavior: retained / corrected / superseded

- **Retained**: two-step reading flow; range-input UX; server rendering concept; timeout discipline; validation order; signed-URL delivery.
- **Corrected**: output format (PNG→JPG, DEC-039); white compositing made explicit and deterministic (DEC-081); page-selection semantics (DEC-186); ZIP+individual delivery (DEC-037); encrypted-input password flow (DEC-064); browser-capable path (DEC-011/015); accessible preview (duplicated membership visible — DEC-186).
- **Superseded**: 150 DPI PNG preset; `file_type png|zip`; `page_1.png` naming; server-only processing; blanket encrypted rejection.

## 6. Alternatives

1. **Server: pypdfium2; browser: pdf.js (recommended shape).** Both permissive (Apache-2.0/BSD-3), both with documented white-compositing approaches (pypdfium2 `FillRect` 0xFFFFFFFF; pdf.js explicit white fill before JPEG encode), both support encrypted PDFs, both handle the 16-MP ceiling (browser canvas cap; server render at bounded scale). Trades: pypdfium2 requires JPEG encode glue (to PIL/quality); pdf.js needs the white-fill step implemented deliberately; server renders at a scale chosen to keep ≤16 MP or document downscaling (DEC-015 ceiling; profile design per DEC-039).
2. **Server: PyMuPDF (legacy engine).** Trades: mature, documented white background (alpha=False), fast; AGPL/commercial fork and no first-class sanitization concern (rasterization inherently excludes active content — DEC-092); fewer glue steps. Viable under the owner's AGPL decision.
3. **Server: Ghostscript jpeg device.** Trades: battle-tested rasterizer with explicit JPEG quality controls; AGPL fork; CVE history → hardened isolation; sequential page bounds via `-dFirstPage/-dLastPage`. Viable under the AGPL decision with C4 hardening.
4. **Server: poppler pdftoppm.** Trades: GPL (conveyance obligations in the image); simple CLI; JPEG/DPI controls; white paper default. Viable if GPL conveyance is acceptable and AGPL is not.

All four satisfy DEC-055. Privacy/security: every option renders untrusted PDFs in isolation with bounded resources (DEC-092/169); the source PDF is never executed and external references are never followed (DEC-092); threat-classified files are blocked before engines (DEC-088).

## 7. Recommendation

**Recommendation (not an accepted decision — DEC-054/057):** adopt **pypdfium2 for the server path and pdf.js for the browser path** — the only fully permissive pairing that meets rendering, white compositing (documented fill), encryption support, and the 16-MP ceiling without an AGPL/GPL licensing fork. Implement the DEC-081 white fill explicitly in both paths (server: `FPDFBitmap_FillRect` white; browser: white fill before `canvas.toBlob('image/jpeg')`), the DEC-039 profile as a design choice (starting point: ~150-200 DPI capped at 16 MP per page, JPEG quality around the "high" family, validated by functional fixtures), and the DEC-186 selection semantics (one output per user-entered selection in order). PyMuPDF remains the legacy-engine fallback if the owner accepts its AGPL terms. Server JPEG encode glue uses Pillow (HPND) for quality control.

## 8. Measurable acceptance criteria

1. Page selection `1,1,3-4` on a 4-page PDF produces 4 outputs in exactly that order — the duplicate page 1 appears twice, each uniquely named in the ZIP, individual-download listing, and manifest (DEC-186, DEC-078).
2. Range syntax and validation per DEC-038 (charset, start>end, out-of-bounds incl. 0, malformed tokens → localized errors); CTA disabled until valid; preview shows duplicated membership (DEC-186).
3. Output is JPEG (not PNG); single-page jobs download one JPG directly; multi-page jobs auto-download a ZIP with every file individually downloadable (DEC-037).
4. A transparent-region fixture renders with **white**, not black, in both browser and server paths (DEC-081) — functional visual fixture.
5. A text-and-line-art fixture stays crisp at normal screen use within the 16-MP ceiling; the profile never exceeds 16 MP per page in the browser path (DEC-015/039).
6. A low-resolution source produces an output with an honest UI (no implication that detail was created) (DEC-039).
7. Encrypted input: password requested only when needed; wrong-password vs corrupt-file errors distinct (DEC-036/064).
8. Threat-classified input is blocked with a safe rejection before rendering (DEC-088); rendering runs non-root with bounded CPU/memory/time/disk and restricted network (DEC-092/169).
9. Browser jobs within DEC-015 limits (200/50 pages) process sequentially; over-limit/unsafe jobs transition to the server path with truthful stage labels (DEC-015/030/065).
10. Output naming is source-derived with localized suffixes and duplicate disambiguation (DEC-042/186).
11. Server results obey the one-hour retention clock, signed URLs, expiry UI, and the machine-readable limits contract (DEC-013/067/070/170/165).
12. No fabricated progress or quality claims (DEC-033).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Exact output profile** (scale/DPI, JPEG quality, downscaling threshold) is a design choice validated by functional testing and production observation (DEC-039, DEC-066; UX §21.1 item 2); starting values above are recommendations from documented engine parameters (A2-style, not benchmarks).
2. **White compositing determinism**: pypdfium2 documents the fill API but exact blend behavior for transparency groups should be fixture-verified (DEC-081 allows documented appearance limitations).
3. **pdf.js white canvas**: pdf.js does not guarantee a white canvas by default; the render loop must fill explicitly — an implementation detail this brief records as required (DEC-081).
4. **Server scale vs 16-MP ceiling**: the ceiling is a browser-processing safety limit (DEC-015); the server profile may render above it only if the design documents why (DEC-015's ceiling text is browser-specific; C2 owns server limits).
5. **Active-content semantics**: rasterization inherently excludes active content from output, but malformed input can still target parsers (DEC-092); sanitization *reporting* (DEC-091) is not required for this tool (arch §11.6), while threat blocking (DEC-088) applies — confirmed reading.
6. Owner questions: (a) AGPL acceptance for the PyMuPDF alternative; (b) confirmation of the profile starting point (150-200 DPI, ≤16 MP, "high" JPEG) before design finalization.

## 10. Dependencies and cross-track interfaces

- **A1**: license/version evidence (pypdfium2 Apache/BSD, pdf.js Apache-2.0, PyMuPDF AGPL, Ghostscript AGPL, poppler GPL).
- **B1**: browser routing (page counts 200/50, 16-MP ceiling, sequential rendering, canvas memory) (DEC-015/030/065).
- **C2**: per-tool server limits (pages, per-page megapixels, output expansion, ZIP size) (DEC-034).
- **C4**: rendering isolation, resource bounds, malware scanning, dependency patching (DEC-092/169/171).
- **D5**: threat blocking (DEC-088) and the untrusted-input register (DEC-092).
- **X2**: surfaces the PDF-to-JPG engine approval and the profile-confirmation item.

## 11. Source-date log and evidence-completeness notes

- Sources: pypdfium2 PyPI/README, PyMuPDF Page docs, Ghostscript releases/CVE index, poppler releases, pdf.js FAQ/releases, MDN createImageBitmap, pqina iOS canvas limit — all accessed 2026-07-31 (A1 §5.1). Legacy files read 2026-07-31 with citations above.
- Completeness: backend pdf_to_image router/service and test suite read in full; frontend `pdf-to-image/page.tsx` verified via audit §3.5 line-level extraction; no runtime validation performed (prohibited); profile and compositing behavior are design-and-fixture items.

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative report, or quality-score program (DEC-066).
- No installs, builds, servers, VPS access, deployment, account creation, or authenticated remote actions (plan §4.1).
- `papyr-reference/` read-only; `git -C papyr-reference status --porcelain` empty with exit 0 before and after.
- No claim of malware-free output, universal sanitization, or guaranteed rendering fidelity (DEC-081, DEC-092, DEC-171).
- Recommendation only; owner approval required (DEC-057).
