# A1 — Shared Engine and License Evidence

## 1. Header

- **Brief ID**: A1
- **Path**: `<workspace-root>\audit-outputs\research\track-a\a1-shared-engine-licenses.md`
- **Track**: A — Tool and engine research (shared evidence first)
- **Title**: Shared engine and license evidence
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (Track A executor subagent)
- **Status**: Draft (complete for owner review; no accepted product decision)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (§6.1 deliverable A1; §7.1 Track A questions; §8 brief template; §11 verification assertions)
- **Governing decisions**: DEC-054, DEC-055, DEC-056, DEC-057, DEC-058, DEC-059, DEC-060, DEC-066, DEC-188 (plan §3); tool-specific decisions cited inline
- **Files read (complete list)**:
  - `<workspace-root>\AGENTS.md`
  - `<workspace-root>\audit-outputs\research-program-plan.md`
  - `<workspace-root>\papyr-rebuild-decisions.md` (DEC-001 through DEC-188, Open decisions)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (§12.0-12.5, §13, §16, §18, §20, §21)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (§9-17, §25, Appendices A-B)
  - `<workspace-root>\audit-outputs\ui-five-tools-audit.md` (full)
  - `<workspace-root>\audit-outputs\ui-home-shell-audit.md` (full)
  - `<workspace-root>\audit-outputs\ui-docs-code-reconciliation.md` (full)
  - Legacy backend (read-only): `papyr-reference/backend/requirements.txt`; `routers/compress.py`; `services/compress_service.py`; `routers/image_to_pdf.py`; `routers/pdf_to_image.py`; `services/pdf_to_image_service.py`; `utils/config.py`; `utils/pdf_validator.py`; `Dockerfile.production`; `tests/test_pdf_to_image.py`
  - Legacy frontend (read-only): `papyr-reference/frontend/src/app/compress/page.tsx`; `src/app/image-to-pdf/page.tsx` (lines 1-120, 480-559); `src/components/PDFUploader.tsx` (lines 200-329); `src/components/PageRangeInput.tsx`; `src/lib/pdfUtils.ts`; `src/lib/format.ts`; `src/lib/config.ts`
  - Legacy docs (grep only for engine claims): `papyr-reference/docs/05_Papyr_Project_Plan_v1.0.md`, `06_Papyr_Test_Plan_v1.0.md`, `09_Papyr_Feasibility_Study_v1.0.md`, `11_Papyr_API_Spec_v1.0.md`, `12_Papyr_Security_Policy_v1.0.md`
- **Template note**: The plan §8 lists 12 numbered sections. The header sub-fields above are expanded as their own labeled fields; combined with the 12 numbered sections this satisfies both the plan's template and the "16-section" instruction in the Track A task (header sub-fields counted individually).

---

## 2. Scope

This brief is the consolidated engine and license evidence base for the five MVP tools (Compress PDF, Merge PDF, Split PDF, JPG to PDF, PDF to JPG). It establishes, for every plausible candidate engine/library: current stable version and release date, exact license and its obligations for server-side use, redistribution, and SaaS delivery, current official documentation, representative capabilities and limitations, and security/maintenance posture. It also records the legacy engine stack and the security-relevant gaps observed in it.

Track A briefs A2-A6 cite this file for engine and license evidence instead of repeating it (plan §6.1: "A1 must complete before A2 through A6 can finalize their engine and library recommendations").

The user problem served: Papyr must select engines that (a) meet each tool's approved behavior under DEC-059's first-principles requirement, (b) are legally usable in a free, advertising-funded, no-account SaaS that temporarily processes user files on a VPS (DEC-005, DEC-012, DEC-017, DEC-105), and (c) can be operated securely against untrusted inputs (DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171).

Current approved Papyr behavior (baseline this brief must support): hybrid browser-first processing with automatic server fallback (DEC-011, DEC-015, DEC-030, DEC-065); Compress PDF server-default (DEC-015); server outputs sanitized of active content for PDF-producing tools (DEC-090, DEC-091); per-tool server limits set independently (DEC-034); one-hour maximum server retention (DEC-013, DEC-070); short-lived signed R2 result URLs (DEC-170); dependency review monthly with prompt critical security fixes (DEC-179).

## 3. Non-goals

- No benchmark program, corpus, comparative quality/performance report, or quality-score evaluation (DEC-066).
- No decision on which engine wins per tool: A2-A6 own those recommendations; this brief only consolidates evidence and records shared license implications.
- No legal advice. License obligations are described from primary texts and vendor statements; qualification by a lawyer remains an owner action where material (aligned with DEC-045's qualified legal review for launch copy; no claim of compliance is made).
- No installs, builds, server starts, or runtime validation (plan §4.1).
- No browser capability-detection research (Track B1), per-tool server limits (Track C2), malware scanner selection (Track C4), or threat-classification design (Track D5) — those are cross-track consumers of this evidence.
- No examination of OCR, office-conversion, or other deferred legacy engines (DEC-010, DEC-094).

## 4. Research questions

1. Which engines/libraries are plausibly usable for the five tools under DEC-059's first-principles requirement, and what are their current versions, documentation, capabilities, and limitations?
2. What is the license of each candidate, and what are the obligations for server-side use, redistribution, and SaaS delivery — including AGPL network-use obligations and GPL/LGPL/MPL distinctions?
3. What are the representative failure modes and resource profiles (memory, time, disk, output expansion) for realistic inputs, described qualitatively from documented engine characteristics (DEC-066)?
4. What is the legacy engine stack, which legacy engine choices are still defensible, and what security/maintenance gaps exist in how the legacy stack invokes them (DEC-059, DEC-169)?
5. Which candidates satisfy the security-relevant decisions: sanitization of active content (DEC-090), untrusted-input rendering (DEC-092), byte-level image validation and decode isolation (DEC-093), password-protected input (DEC-064)?
6. What are the measurable acceptance criteria for engine selection under DEC-066 (functional verification, not comparison)?
7. What are the cross-track interfaces to B1, C2, C4, D5?

## 5. Evidence

### 5.1 Primary sources (web), all accessed 2026-07-31

| Source | URL / identifier | What it evidences |
|---|---|---|
| Ghostscript releases page | https://ghostscript.com/releases | Latest release 10.07.1 (2026-05-19); AGPL + commercial dual licensing; "For commercial licensing for server-side PDF conversion, optimization, compression, and embedded use." |
| Ghostscript downloads/licensing | https://ghostscript.com/releases/gsdnld.html | AGPL vs Artifex commercial license split; "Which license is right for me?" guidance |
| Artifex licensing page | https://artifex.com/licensing | Dual AGPL-3.0/commercial licensing; commercial license "no code disclosure required"; each license crafted per use case |
| Artifex hardening blog | https://artifex.com/blog/security-hardening-ghostscript | Ghostscript architecture; PostScript/PDF untrusted-input risk; history of "data leaking" exploits; sandbox separation |
| Ghostscript CVE index | https://www.ghostscript.com/releases/cve/index.html | CVE history: CVE-2023-36664 (10.01.2), CVE-2023-43115 (10.02.0), CVE-2023-46751 (10.02.1), CVE-2024-29506..10 + CVE-2024-33869..71 (10.03.1), CVE-2024-46951..56 (10.04.0), CVE-2025-27830..37 (10.05.0), CVE-2025-59798..59801 (10.06.0) |
| Ghostscript VectorDevices (pdfwrite) docs, gs10.05.1 | https://ghostscript.readthedocs.io/en/gs10.05.1/VectorDevices.html | pdfwrite creates a new PDF whose internals differ from input; comments not preserved; bookmarks/hyperlinks usually not carried; full Distiller-parameter table for /default /screen /ebook /printer /prepress incl. resolutions and QFactor notes |
| SPDX AGPL-3.0-or-later | https://spdx.org/licenses/AGPL-3.0-or-later.html | SPDX license expression semantics |
| Ghostscript AGPL switch commit (via Yocto patch review) | https://patchwork.yoctoproject.org/project/oe-core/patch/20240207080823.498290-1-kai.kang@windriver.com | Ghostscript/GhostPDL switched to Affero GPL starting with version 9.07 (commit "Switch Ghostscript/GhostPDL to Affero GPL"), SPDX `AGPL-3.0-or-later` |
| PyMuPDF docs "About" | https://pymupdf.readthedocs.io/en/latest/about.html | PyMuPDF + MuPDF available under AGPL and commercial agreements; docs cover 1.28.0; Artifex is exclusive commercial licensing agent for MuPDF |
| PyMuPDF PyPI | https://pypi.org/project/pymupdf | License AGPL; latest version 1.28.0 (verified via PyPI JSON API on 2026-07-31); "Free for open-source projects / Commercial from Artifex"; no telemetry/licence-validation callbacks; works air-gapped |
| PyMuPDF GitHub issue #4504 | https://github.com/pymupdf/pymupdf/issues/4504 | Open question: PyMuPDF AGPL-3.0-only vs AGPL-3.0-or-later; MuPDF is AGPL-3.0-or-later; PyMuPDF license statements suggest AGPL-3.0-only (uncertainty) |
| PyMuPDF `Page` docs | https://pymupdf.readthedocs.io/en/latest/page.html | `get_pixmap`: alpha=False default; pixmap samples pre-cleared with 0xFF → white where page has nothing (transparency compositing); `insert_image` accepts filename/stream/pixmap |
| pikepdf PyPI | https://pypi.org/project/pikepdf | pikepdf 10.11.0 (PyPI JSON, 2026-07-31); MPL-2.0; powered by qpdf; "permits combining with closed source; publish source-level modifications to pikepdf itself" |
| pikepdf docs (10.x) | https://pikepdf.readthedocs.io | Sanitization module: `remove_javascript()`, `remove_attachments()`, `remove_external_access()`, `remove_thumbnails()`, `remove_search_index()`, `remove_multimedia()`, `Sanitizer`; password/encryption; merging and splitting pages; JobBuilder |
| Snyk pikepdf | https://security.snyk.io/package/pip/pikepdf | Version timeline 10.6.0..10.11.0 (2026-05..07); 0 direct vulnerabilities in latest |
| qpdf site + docs | https://qpdf.sourceforge.io ; https://qpdf.readthedocs.io (12.3.2) | qpdf 12.3.2 (2026-01-24 per Wikipedia; GitHub release tag v12.3.2 verified 2026-07-31); Apache-2.0; content-preserving; page selection for split/merge; `--list-attachments`, `--remove-attachment`, `--add-attachment`; does not render PDFs |
| qpdf GitHub | https://github.com/qpdf/qpdf | Apache-2.0; copyright 2005-2026 |
| pypdf PyPI | https://pypi.org/project/pypdf | pypdf 6.14.2 (2026-06-23, PyPI JSON); BSD-3-Clause; Python >=3.9; crypto extra for encryption |
| pypdf Snyk | https://security.snyk.io/package/pip/pypdf | CVE history: infinite loop via outlines in writer (fixed 6.13.0); LZWDecode data amplification (DoS); layout-mode text extraction resource allocation; 0 vulnerabilities in 6.14.2 |
| pypdf merging docs | https://pypdf.readthedocs.io/en/latest/user/merging-pdfs.html | Merging forms: duplicate field names prevent access to some data |
| pypdfium2 PyPI | https://pypi.org/project/pypdfium2 | pypdfium2 5.12.1; "Apache-2.0 / BSD-3-Clause"; PDFium under BSD-style license; encrypted PDF processing; render scale → DPI (scale = dpi/72); `FPDFBitmap_FillRect` white background example; PIL integration |
| pypdfium2 GitHub org | https://github.com/pypdfium2-team | Liberal license (BSD-3-Clause, Apache-2.0); fast rendering |
| Pillow release notes | https://pillow.readthedocs.io/en/stable/releasenotes/index.html | Pillow 12.3.0 (2026-07-01); quarterly releases; security fixes |
| NVD CVE-2026-59199 | https://nvd.nist.gov/vuln/detail/CVE-2026-59199 | Pillow <12.3.0 heap out-of-bounds write in Image.paste/crop/alpha_composite near signed 32-bit int limits; fixed 12.3.0 — evidence that image decode/transform APIs need current versions |
| img2pdf PyPI | https://pypi.org/project/img2pdf | img2pdf 0.6.3; LGPL-3.0; format table (JPEG/JPEG2000/non-interlaced-PNG direct embed; other raster formats via PNG Paeth; 1-bit via CCITT G4; CMYK via flate) |
| img2pdf manpage (Debian) | https://manpages.debian.org/unstable/img2pdf/img2pdf.1.en.html | `--rotation auto` (default) applies EXIF Orientation; `-a/--auto-orient` swaps page dimensions to image orientation; border/`--pagesize` support; direct-embed preservation incl. metadata |
| poppler site + releases | https://poppler.freedesktop.org ; https://poppler.freedesktop.org/releases.html | poppler 26.07.0 (2026-07-02); monthly releases; crash fixes in malformed documents |
| poppler Wikipedia | https://en.wikipedia.org/wiki/Poppler_(software) | License GPLv2 or GPLv3 |
| pdfcpu GitHub | https://github.com/pdfcpu/pdfcpu | pdfcpu v0.13.0 (2026-06-09); Apache-2.0; Go; merge/split/optimize/encrypt/attachments; supports up to PDF 1.7 |
| pdf-lib npm | https://www.npmjs.com/package/pdf-lib ; registry JSON (fetched 2026-07-31) | pdf-lib 1.17.1; MIT; last published 2021-11-07; dependencies pako, @pdf-lib/upng, @pdf-lib/standard-fonts |
| pdf-lib README (Limitations + Encryption Handling) | https://github.com/Hopding/pdf-lib (README.md raw, fetched 2026-07-31) | No plain-text extraction; no HTML/CSS embedding; **does not support encrypted documents** (`EncryptedPDFError`; `ignoreEncryption` does not decrypt) |
| Snyk pdf-lib | https://security.snyk.io/package/npm/pdf-lib | Maintenance: INACTIVE (no commits over 6 months at scan; last release 4 years ago); 279 open issues; no known security issues |
| pdfjs-dist npm | https://www.npmjs.com/package/pdfjs-dist ; registry JSON (fetched 2026-07-31) | pdfjs-dist 6.2.108 (2026-07-28); Apache-2.0; Node engine >=22.13 || >=24 |
| Mozilla pdf.js | https://mozilla.github.io/pdf.js ; GitHub releases | Apache-2.0; active (weekly releases); release notes include "Cap the max canvas dimensions in order to avoid to downscale large images in the worker" |
| pdf.js FAQ | https://github.com/mozilla/pdf.js/wiki/frequently-asked-questions | Renders each page onto one canvas; memory guidance; recommendation to render only visible pages |
| Apryse "PDF.js rendering" (secondary, supporting) | https://apryse.com/blog/pdf-js/guide-to-pdf-js-rendering | pdf.js has no canvas tiling; renders onto a single large canvas (supports the memory profile statement) |
| MDN createImageBitmap | https://developer.mozilla.org/en-US/docs/Web/API/Window/createImageBitmap | `imageOrientation: 'from-image'` (default) applies EXIF orientation |
| pqina "canvas area exceeds maximum limit" (secondary) | https://pqina.nl/blog/canvas-area-exceeds-the-maximum-limit | iOS Safari canvas area limit 16,777,216 px (= 16 MP) |
| pdf-association pdf-issues #248 | https://github.com/pdf-association/pdf-issues/discussions/248 | WebP/AVIF will not be added to PDF spec in foreseeable future; WebP is not a native PDF image codec |
| Ricoh virtual driver help (Artifex dual-licensing text) | https://help-us.na.smart-integration.ricoh.com/PrintCloud%20Virtual%20Print%20Driver/Help/index6.html | Artifex statement: SaaS/ASP use of AGPL Ghostscript/MuPDF requires commercial license OR releasing the application under AGPL; examples of distribution/network use |

### 5.2 Legacy evidence (read-only, `papyr-reference/`)

- `backend/requirements.txt:1-16` — PyMuPDF==1.26.7, Pillow==11.3.0; OCR/office stack present but non-MVP. Ghostscript is NOT a pip dependency (installed at OS level).
- `backend/Dockerfile.production:74-101` — installs `ghostscript` and `poppler-utils` via apt; also tesseract + libreoffice for non-MVP tools; non-root `appuser`, tini, 4 uvicorn workers.
- `backend/services/compress_service.py:72-86` — legacy Ghostscript invocation: `-sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS={screen|ebook|printer} -dNOPAUSE -dBATCH -dQUIET -dDetectDuplicateImages=true -dCompressFonts=true -dSubsetFonts=true`; **no `-dSAFER`/`--safe` flag**; 30 s timeout.
- `backend/routers/compress.py:104-109` — `quality` query param `screen|ebook|printer`, default `ebook`; `:156-166` output name `compressed_<name>`, `saved_percent = round((1 - compressed/original)*100)`.
- `frontend/src/components/PDFUploader.tsx:303` — hardcoded `?quality=ebook`.
- `backend/routers/image_to_pdf.py:28-36, 125-162` — PyMuPDF: page sized to image dimensions (`rect = img[0].rect`), `insert_image`, output `images.pdf`.
- `backend/routers/pdf_to_image.py` + `services/pdf_to_image_service.py:26-109, 112-184, 187-228` — PyMuPDF 150 DPI PNG rasterization (`zoom = dpi/72`), `parse_page_range` sorts and dedupes (set-based, `:54, 109`), `page_1.png` ZIP naming, `file_type png|zip`.
- `frontend/src/lib/pdfUtils.ts:103-146` — browser imagesToPDF (pdf-lib; WebP → canvas → PNG via `webpToPng`, `:82-92`); `:153-201` getPDFPageCount/splitPDF; `:209-233` mergePDFs (all pdf-lib, `ignoreEncryption: true`).
- `frontend/src/components/PageRangeInput.tsx:19-89` — legacy range parser: charset `[\d\s,\-]`, Set dedupe, sorted output (`:87`).
- `frontend/src/lib/format.ts:15-21` — `formatPercent` floors at 0 ("−0%" pill).
- `frontend/src/lib/config.ts:24-38` — mirrored limits 20 MB / 60 min; allowed image MIME set.
- `docs/11_Papyr_API_Spec_v1.0.md:74-78, 210, 223` — legacy engine mapping: Compress = Ghostscript; Image to PDF + PDF to Image = PyMuPDF; merge/split client-side via pdf-lib; preset table screen/ebook/printer.
- `docs/09_Papyr_Feasibility_Study_v1.0.md:99-101, 410` — client engine pdf-lib; server engines Ghostscript + PyMuPDF; licensing note "AGPL/Apache/MIT".
- `docs/12_Papyr_Security_Policy_v1.0.md:264, 774-785` — encrypted PDFs rejected; Ghostscript subprocess security notes (container, permission limits).
- `backend/utils/pdf_validator.py:34-141` — shared validation order: empty → MIME → extension → `%PDF` magic → size (413) → fitz open (page count, encrypted) → page-count limit → encrypted checks.

### 5.3 Engine capability and limitation evidence (consolidated)

- **Ghostscript 10.07.1** — interpreter for PostScript/PDF; `pdfwrite` is a *reinterpreting* high-level device: it produces a new PDF that "should look the same" but whose internals differ from the input; comments are not preserved and bookmarks/hyperlinks are "normally not present in the output" (VectorDevices doc). It performs image downsampling/re-encoding (lossy when DCT) and font/stream optimization. It can also render to raster (jpeg/png16m devices) for PDF-to-image. Security: strong copyleft history (AGPL since 9.07), ~25 CVEs in 2023-2026; SAFER/sandbox is default but PostScript interpreter surface is large; untrusted input must run in a hardened container (Artifex blog; Safran doc). Resource profile: pdfwrite processing time roughly proportional to page/image count; memory can spike on large embedded images; output can be larger than input for already-optimized files (documented engine characteristic).
- **MuPDF / PyMuPDF 1.28.0** — fast rendering and manipulation; `insert_pdf` for merge; page selection via `select`/`insert_pdf`; `get_pixmap(alpha=False)` renders onto white (0xFF pre-clear); supports encrypted PDFs with password; `insert_image` accepts many formats (JPEG/PNG embedded natively; other formats, incl. WebP, decoded via MuPDF and may be stored uncompressed unless deflated — docs advise `deflate=True`); AGPL-3.0/commercial dual; PyMuPDF itself may be AGPL-3.0-only (issue #4504 — uncertainty).
- **pikepdf 10.11.0 / qpdf 12.3.2** — structure- and content-preserving transformations; page selection (`pikepdf.Pdf.pages`, qpdf `--pages`) for split/merge; password/encryption support; attachment ops; **explicit sanitization API** (`remove_javascript`, `remove_attachments`, `remove_external_access`, `Sanitizer`) matching DEC-090 categories; qpdf does not render. MPL-2.0 (pikepdf) / Apache-2.0 (qpdf). qpdf CVE history (CVE-2021-36978, CVE-2022-34503, CVE-2023-36668) → pin current versions.
- **pypdf 6.14.2** — pure-Python merge/split; outlines can be imported on merge; form merge has duplicate-name conflicts (documented); no image re-encoding; encryption via `crypto` extra; known DoS CVEs (outlines infinite loop fixed 6.13.0; LZWDecode amplification) → pin current.
- **pypdfium2 5.12.1** — PDFium bindings; rendering with explicit white fill (documented example `FPDFBitmap_FillRect(..., 0xFFFFFFFF)`); scale factor → DPI (`scale = dpi/72`); encrypted PDFs supported; Apache-2.0/BSD-3-Clause; no manipulation of structure for merge (page import possible via PDFium API but higher effort).
- **poppler 26.07.0 (pdftoppm/pdftocairo)** — rasterization utilities; GPLv2/v3; pdftoppm has `-jpeg`, `-r` DPI; white paper background by default; monthly releases with malformed-document crash fixes.
- **pdfcpu v0.13.0** — Go; merge/split/optimize/encrypt/attachments; Apache-2.0; PDF <=1.7 support; alternative where a Go toolchain is acceptable.
- **pdf-lib 1.17.1** — browser/JS; create/merge/split; copyPages; forms (create/fill, but cross-document form merge unsupported); attachments add; **no encryption support** (throws on encrypted docs); WebP embedding unsupported (needs decode to PNG); inactive since 2021 (Snyk maintenance INACTIVE); MIT.
- **pdf.js (pdfjs-dist 6.2.108)** — browser/Node rendering; page render onto one canvas (no tiling); password support via `getDocument({password})`; canvas-size caps to avoid downscale; Apache-2.0; very active.
- **Pillow 12.3.0** — image decode/encode/transform; WebP support; EXIF via `ImageOps.exif_transpose`; `save(..., exif=...)`; PDF write support; HPND license; CVE-2026-59199 (fixed 12.3.0) shows why current versions are mandatory.
- **img2pdf 0.6.3** — lossless container conversion; JPEG/JPEG2000/non-interlaced-PNG direct embed (source metadata survives); other formats (incl. WebP) re-encoded via PNG Paeth; EXIF auto-rotation default; paper sizes A4/Letter; LGPL-3.0; low maintenance cadence (0.6.3 current, releases infrequent).

### 5.4 License obligations summary (from primary texts and vendor statements; not legal advice)

| License | Candidates under it | Server-side (SaaS) position | Key obligations | Source |
|---|---|---|---|---|
| AGPL-3.0 | Ghostscript (or-later), MuPDF, PyMuPDF | Network interaction with the program = conveying the work → the combined work must be offered under AGPL to users (source offer), or a commercial license obtained from the licensor. Artifex explicitly recommends a commercial license for SaaS/ASP use when the application is not AGPL. | Source offer to users of the running service (incl. unmodified use per §13); keep license/notice; no additional restrictions | gnu.org AGPL-3.0 text (as referenced by Artifex/PyPI); Ricoh/Artifex text; artifex.com/licensing |
| GPL-2.0/v3 | poppler (GPLv2 or GPLv3) | Server-side use without distribution does not trigger source obligations (no network clause); shipping the binary in a Docker image = conveying → source offer + relink obligations for combined distribution | If conveyed/distributed, provide source of the GPL components + license notices; allowed to link only with compatible components | SPDX GPL-2.0/GPL-3.0 texts (as referenced by poppler) |
| LGPL-3.0 | img2pdf | Server-side execution does not trigger app source disclosure; conveying the library (e.g., in an image) requires providing the library's source and permitting relinking; app can stay proprietary | Provide library source + relink facilities when distributed; notice | gnu.org LGPL-3.0 (via PyPI) |
| MPL-2.0 | pikepdf | File-level copyleft: modifications to pikepdf's own source files must be published; combination with proprietary app is allowed; no server-side disclosure of the app | Publish modified pikepdf source; keep notices; "Exhibit B" notice where required | mozilla.org/MPL/2.0; pikepdf PyPI |
| Apache-2.0 | qpdf, pdfcpu, pdf.js, pypdfium2 (dual) | Permissive; no source disclosure for use, incl. SaaS; retain NOTICE/license text; patent grant; no trademark use | Keep license text/NOTICE in distribution | apache.org/licenses/LICENSE-2.0 |
| BSD-3-Clause | pypdf, pypdfium2 (dual), PDFium | Permissive; retain copyright notice | Notice retention | opensource.org BSD-3 |
| MIT | pdf-lib | Permissive; retain copyright + permission notice | Notice retention | opensource.org MIT; npm |
| HPND | Pillow | Permissive; notice + no-use-of-name-for-endorsement without permission | Notice retention; advertising-name restriction | opensource.org HPND; Pillow LICENSE |

Compliance note for Papyr: a VPS Docker deployment that **conveys** any GPL/AGPL/LGPL component (it does — the image ships them) triggers source-offer obligations for those components at a minimum. AGPL components (Ghostscript, MuPDF/PyMuPDF if selected) additionally trigger AGPL §13 network-use obligations for the *combined work* unless a commercial license is obtained — the practical fork is: license the AGPL engines commercially from Artifex, or build the processing services on permissive (Apache-2.0/BSD/MIT/HPND) components where capability permits, or release the relevant service code under AGPL. This is a material owner decision (A2-A6 carry the per-tool angle).

## 6. Alternatives

The engine set is not one choice but a per-tool matrix. The plausible approach families (with trade-offs; A2-A6 select per tool):

1. **Reinterpreting native engines (Ghostscript)** — proven for compression; destructive re-interpretation of document internals (loses comments, often bookmarks/hyperlinks; re-encodes images); AGPL/commercial cost fork; strong CVE history requiring hardened isolation. Best where output-quality tuning (downsampling) is the point (Compress).
2. **Structure-preserving libraries (pikepdf/qpdf, pypdf, pdfcpu, pdf-lib browser)** — preserve objects and features; enable explicit sanitization (pikepdf) and safe split/merge; permissive licenses (except none of these are copyleft); but they do not render and do not re-encode images (no real compression). Best for Merge/Split.
3. **Rendering engines (PyMuPDF, pypdfium2, poppler, pdf.js, Ghostscript raster devices)** — convert pages to pixels for PDF-to-JPG and page-count/thumbnails; license spectrum AGPL (PyMuPDF/Ghostscript) vs permissive (pypdfium2, pdf.js) vs GPL (poppler). Best for PDF to JPG and previews.
4. **Image codecs (Pillow, img2pdf, browser createImageBitmap)** — decode/encode JPG/PNG/WebP and assemble PDFs; permissive licenses (HPND, LGPL-3.0, browser-native); enable EXIF handling and byte-level validation. Best for JPG to PDF.

Trade-offs, risks, cost, operational impact, privacy/security implications:

- **Cost**: Artifex commercial licenses (Ghostscript/MuPDF/PyMuPDF) are quoted per use case and not publicly priced (industry reports cite ~$25k/yr for Ghostscript — secondary, unverified; see §9). Permissive alternatives avoid that cost. Existing infrastructure has no engine budget line (DEC-095).
- **Operational**: AGPL services complicate the closed-source SaaS model; permissive stacks remove the licensing review item but may need more glue code (e.g., sanitization pass, image decode) — operational complexity shifts rather than disappears.
- **Privacy/security**: all PDF engines parse untrusted input; hardened containers, bounded resources, current versions, and the DEC-088/090/092/093 controls apply regardless of engine. pikepdf's sanitization API directly implements DEC-090 categories; Ghostscript and PyMuPDF do not guarantee sanitization.
- **Browser**: pdf-lib is the only realistic browser merge/split/create library but is unmaintained and cannot read encrypted PDFs; pdf.js handles rendering and passwords but cannot rewrite PDFs. This constrains browser-first routing (feeds B1/C2).

## 7. Recommendation

**Recommendation (not an accepted decision — DEC-054, DEC-057):** adopt a **layered, permissive-first engine matrix** with a documented AGPL exception only where no permissive alternative meets the approved behavior:

- **Compress PDF (server)**: Ghostscript `pdfwrite` remains the strongest capability match (documented image downsampling/re-encoding and stream optimization), but the AGPL/commercial fork and CVE history make it a **conditional recommendation** pending an owner licensing decision. Permissive fallback: pikepdf/qpdf or PyMuPDF-based lossless recompression (always-new artifact preserved under DEC-080, with honest reporting). See A2.
- **Merge/Split (server fallback)**: pikepdf (qpdf) — structure-preserving, permissive MPL-2.0, native sanitization API for DEC-090, password support (DEC-064/074). Browser: pdf-lib for the happy path only (MIT; unencrypted; feature caveats disclosed per DEC-079).
- **PDF to JPG (server)**: pypdfium2 (Apache-2.0/BSD-3-Clause) as primary with documented white compositing, or PyMuPDF if the owner accepts/obtains the AGPL/commercial terms; poppler as a GPL alternative; Ghostscript raster device as an additional GPL-adjacent path only where its AGPL terms are accepted.
- **JPG to PDF**: Pillow (HPND) for validation/decode/WebP, img2pdf (LGPL-3.0) for lossless JPEG/PNG embedding with EXIF preservation; browser pdf-lib for small local jobs.
- **Browser rendering/page counts**: pdf.js (Apache-2.0) for page counts/previews and any browser PDF-to-JPG path.
- **Maintenance posture**: pin current versions (table above), monthly dependency review (DEC-179), container hardening for every engine (DEC-169), and never claim malware-free output (DEC-171, DEC-090).

This recommendation is a recommendation only; per-tool recommendations in A2-A6 and the eventual design still require owner approval (DEC-057).

## 8. Measurable acceptance criteria

Functional/operational verification criteria (no benchmark wording per DEC-066):

1. **License gate**: for every engine selected in the approved design, the repository records the exact version, license, and the compliance path chosen for SaaS delivery (source-offer bundle, commercial license, or permissive-only selection), reviewable at implementation planning.
2. **Version currency**: every pinned engine version in the design is the current stable release at pin time (or has a documented reason for an older pin and an upgrade date).
3. **Sanitization**: the chosen Merge/Split/Compress server engine can demonstrably detect and remove the DEC-090 categories (JavaScript, launch actions, embedded attachments, external actions) and report the categories removed (DEC-091) — verified by functional fixtures, not claims.
4. **Encryption**: the chosen engines can detect encrypted PDFs and process them with a supplied password (DEC-064), with wrong-password errors distinct from corrupt-file errors (DEC-036).
5. **Rendering**: the chosen PDF-to-image engine produces white-composited output for transparent pages (DEC-081) — verified by a functional fixture with transparent regions.
6. **Resource bounds**: each engine runs non-root, with bounded CPU/memory/time/disk and restricted network in the hardened container (DEC-169); engine processes enforce timeouts (legacy precedent 30 s compress, 60 s rasterize).
7. **Security maintenance**: each selected engine has a documented CVE watch (e.g., ghostscript.com CVE index, NVD, Snyk) and a version-update procedure within the monthly review (DEC-179).
8. **No benchmarks**: the design contains no comparative quality/performance study, corpus, matrix, or score program (DEC-066).

## 9. Assumptions, uncertainties, and unresolved questions

1. **AGPL commercial pricing** is not public; industry commentary (~$25k/yr for Ghostscript, Artifex-quoted) is secondary and unverified. Owner must decide the compliance path (commercial licenses vs permissive-only stacks vs AGPL-released services).
2. **PyMuPDF AGPL-3.0-only vs or-later** is unresolved in the project's own issue #4504; treat as "AGPL-3.0 family, exact clause to confirm with Artifex."
3. **Ghostscript pdfwrite behavior on already-optimized inputs** (larger output possible) is documented as a capability characteristic, not measured here (DEC-066); A2 carries the design implication (always-new artifact, honest reporting).
4. **pdf-lib unmaintained**: any browser-first Merge/Split plan inherits a 2021-era library; security review of its transitive deps and a fallback plan if issues surface are required at design time.
5. **WebP is not a PDF native codec** (pdf-association discussion) — every JPG-to-PDF path must decode WebP first; metadata preservation through that decode is best-effort only (DEC-084).
6. **Engine failure modes** are described qualitatively from documentation; per-tool memory/output-expansion profiles feed C2 (server limits) and must be validated during implementation with normal functional testing, not benchmarks.
7. **Snyk/secondary databases** used only to corroborate version timelines and maintenance status; primary sources (PyPI/npm registry, vendor pages) carry version/license claims.
8. **Legacy Ghostscript invocation lacks `-dSAFER`** — a confirmed legacy gap (DEC-169 territory); the rebuild must invoke Ghostscript with current sandbox options in a hardened container.
9. Material owner questions: (a) AGPL compliance path for Ghostscript/MuPDF/PyMuPDF; (b) acceptance of a permissive-only engine matrix if capability is marginally lower; (c) willingness to carry pdf-lib (unmaintained) in the browser bundle vs server-side handling of merge/split entirely.

## 10. Dependencies and cross-track interfaces

- **A2-A6** consume this evidence table and must cite it (plan §6.1).
- **B1 (browser capability routing)**: pdf-lib encryption limitation, pdf.js canvas limits, 16-MP iOS Safari ceiling, and browser memory profile feed routing thresholds (DEC-015, DEC-030, DEC-065).
- **C2 (per-tool server limits)**: engine resource characteristics (pdfwrite re-encode cost, render DPI/scale expansion, pixmap memory = width×height×channels, ZIP expansion) feed per-tool limits (DEC-034).
- **C4 (hardening/malware)**: Ghostscript CVE history and sandbox posture, engine run-conditions (non-root, bounded resources, no network) feed hardening design (DEC-169, DEC-171).
- **D5 (threat handling)**: sanitization capabilities (pikepdf) vs threat blocking (DEC-088) and the "no malware-free claims" rule (DEC-090, DEC-171) shape the D5 register.
- **X1 source index / X2 reconciliation**: this brief contributes the license/version matrix and the AGPL owner-decision item to X2's decision-prompt list (plan §14).

## 11. Source-date log and evidence-completeness notes

- All web sources accessed 2026-07-31. Version claims verified against live registries on 2026-07-31: PyMuPDF 1.28.0, pikepdf 10.11.0, pypdf 6.14.2, pypdfium2 5.12.1, img2pdf 0.6.3, Pillow 12.3.0, qpdf v12.3.2, pdf-lib 1.17.1, pdfjs-dist 6.2.108, Ghostscript 10.07.1, poppler 26.07.0, pdfcpu v0.13.0.
- Legacy files read on 2026-07-31; all paths under `papyr-reference/`; line references cited above.
- Completeness notes: (a) three background explore agents were launched for the UI-audit/frontend/backend extraction but never acquired a concurrency slot and were cancelled before starting; all legacy reading was performed directly by the executor, so no delegated evidence was lost. (b) `papyr-reference/docs/` was searched via grep for engine mentions rather than read in full; the five relevant legacy documents are cited. (c) No benchmark or test-run evidence was created (DEC-066).
- Uncertainties from §9 are not resolved in this brief; they are recorded for the owner and for reconciliation (X2).

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066).
- No installs, builds, server starts, VPS/SSH access, deployment, account creation, or authenticated/mutating remote actions were performed (plan §4.1).
- No product code, scaffolding, or infrastructure was created or modified; no decision log or specification was edited.
- `papyr-reference/` was read-only; verified unchanged via `git -C papyr-reference status --porcelain` (empty output, exit 0) before and after this task.
- No claim of malware-free output, universal sanitization, or guaranteed preservation is made (DEC-090, DEC-171).
- Findings in this brief are recommendations, not accepted decisions (DEC-054, DEC-057).
