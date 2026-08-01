# A2 — Compress PDF Research Brief

## 1. Header

- **Brief ID**: A2
- **Path**: `<workspace-root>\audit-outputs\research\track-a\a2-compress-pdf.md`
- **Track**: A — Tool and engine research
- **Title**: Compress PDF research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (Track A executor subagent)
- **Status**: Draft (complete for owner review; no accepted product decision)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (A2 deliverable; Track A questions §7.1; template §8)
- **Governing decisions**: DEC-014 (automatic premium-screen mode), DEC-015 (server-default), DEC-030/DEC-065 (fallback), DEC-034 (server limits), DEC-036/DEC-064 (encrypted input), DEC-042 (naming), DEC-054-060, DEC-066 (no benchmarks), DEC-080 (always-new artifact, honest reporting), DEC-083/085/089 (paper policy — not compress-applicable), DEC-088/090/091 (threat blocking + sanitization), DEC-168 (processing disclosure), DEC-179 (maintenance), DEC-188
- **Engine/license evidence**: cited from `a1-shared-engine-licenses.md` (§5, §7) per plan §6.1
- **Files read**: all files listed in A1 §1, plus tool-specific: `papyr-reference/backend/routers/compress.py`, `papyr-reference/backend/services/compress_service.py`, `papyr-reference/frontend/src/components/PDFUploader.tsx` (lines 200-329), `papyr-reference/frontend/src/app/compress/page.tsx`, `papyr-reference/frontend/src/lib/format.ts`, `papyr-reference/frontend/src/lib/config.ts`, and the Ghostscript pdfwrite documentation (accessed 2026-07-31)

## 2. Scope

The feature area is server-side PDF compression behind one automatic, high-end "premium screen" mode with **no quality presets, DPI, or target-size controls** (DEC-014). The user problem: reduce PDF file size while preserving crisp on-screen quality, without requiring the user to understand compression trade-offs. Approved Papyr behavior:

- Server-side processing by default (DEC-014, DEC-015); no browser path in the MVP (a later browser path, if any, must follow DEC-030/DEC-065).
- One automatic profile; the legacy hardcoded `quality=ebook` query param is removed (UX §12.1, citing `PDFUploader.tsx:303`).
- Always generate a new processed artifact even when no reduction is achieved; report actual input size, output size, and real change honestly, including zero savings or a larger output (DEC-080); never fabricate a percentage, never substitute the original (DEC-080).
- Preserve searchable/selectable text, links, page geometry, and legibility whenever the source format permits (DEC-014).
- Detect encrypted input and request a password only when required; distinct wrong-password vs corrupt-file errors (DEC-036, DEC-064).
- Sanitize detected active content (JavaScript, launch actions, embedded attachments, external actions) from the output and disclose general categories removed (DEC-090, DEC-091).
- Source-derived output naming with a safe localized suffix (DEC-042); legacy `compressed_<name>` is the baseline (UX §12.1).
- Server results: one-hour maximum retention (DEC-013/DEC-070), short-lived signed URLs (DEC-170), per-tool server limits (DEC-034), status/expiry UI (DEC-067), processing disclosure on the Privacy page with truthful workflow labels (DEC-168).

## 3. Non-goals

- No benchmark program or comparative quality study (DEC-066) — profile thresholds are design choices validated by functional testing and production observation (UX §21.1 item 2).
- No user-facing quality controls, presets, target-size, or DPI selectors (DEC-014).
- No browser-side compression engine selection (server-default is fixed for the MVP; DEC-015).
- No paper-policy, i18n-locale, or metadata-preservation work specific to this tool (not compress-applicable; see A5 for JPG-to-PDF metadata).
- No decision on the AGPL compliance path — that is an owner decision surfaced here and in A1 §9.

## 4. Research questions

1. Which engine best satisfies the automatic premium-screen compression profile under DEC-059's first-principles requirement?
2. What is the license of each candidate and the obligations for SaaS/server-side delivery (cite A1)?
3. What are the current versions and official documentation (A1)?
4. What are representative failure modes and resource profiles for realistic inputs, qualitatively (DEC-066)?
5. Which legacy behavior is retained, corrected, or superseded (with file:line citations)?
6. What are at least two viable alternatives with trade-offs, and which is recommended?
7. What are the measurable acceptance criteria (functional, not comparative)?
8. What are the cross-track interfaces (B1, C2, C4, D5)?

## 5. Evidence

### 5.1 Engine capability evidence (primary sources, accessed 2026-07-31)

- **Ghostscript 10.07.1 (AGPL-3.0-or-later / commercial)** — `pdfwrite` device performs the required premium-profile work: image downsampling and re-encoding via Distiller parameters (`-dColorImageResolution`, `-dDownsampleColorImages`, `-dColorImageFilter=/DCTEncode`, `-dDetectDuplicateImages`, `-dCompressFonts`, `-dSubsetFonts`, `-dCompatibilityLevel`), with documented preset tables (/screen 72 dpi, /ebook 150 dpi QFactor≈0.76, /printer 300 dpi, /prepress; defaults and QFactors per note in VectorDevices doc). **Critical documented characteristic**: pdfwrite produces a *new* PDF that "should look the same" but whose internals differ; comments are not preserved and bookmarks/hyperlinks are "normally not present in the output"; the device attempts to preserve some non-marking information but does not guarantee it. This means Ghostscript-based compression is inherently a re-interpretation and must be treated as such for DEC-014's "preserve links/page geometry when the source permits" requirement (functional verification needed). Security: ~25 CVEs 2023-2026 (A1 §5.1); sandbox (SAFER) is default in current versions but the PostScript surface is large; untrusted input must run in hardened containers (Artifex blog; Safran doc; A1 §9.8). Legacy invocation (`compress_service.py:72-86`) **omits `-dSAFER`** — a confirmed gap to correct.
- **pikepdf 10.11.0 / qpdf 12.3.2 (MPL-2.0 / Apache-2.0)** — lossless structural compression: object streams, cross-reference streams, stream recompression (`compress_streams`), font/stream compression, attachment removal, sanitization API (A1 §5.3). Does not re-encode images → cannot deliver the premium-screen image downsampling requirement on its own. Permissive licensing avoids the AGPL fork.
- **PyMuPDF 1.28.0 (AGPL-3.0/commercial)** — lossless save-time optimization: `doc.save(..., garbage=4, deflate=True, clean=True)` recompresses streams; also `doc.tobytes(..., deflate)`. No image re-encoding (image pixels are kept or optionally rewritten via pixmap). Could perform white/other compositing for images if re-encoded, but that is A5/A6 territory.
- **pypdf 6.14.2 (BSD-3-Clause)** — content-stream compression (`compress_content_streams`), xref/object streams; no image re-encoding; known DoS CVE history (A1 §5.3). Not a size-reduction engine for image-heavy PDFs.
- **pdfcpu v0.13.0 (Apache-2.0)** — `optimize` command; structural; no image re-encoding.

All sources and dates: A1 §5.1 and §5.3.

### 5.2 Legacy evidence (read-only)

| Legacy fact | Location | Disposition |
|---|---|---|
| Ghostscript is the compression engine | `papyr-reference/backend/services/compress_service.py:4-5, 72-86`; `docs/11_Papyr_API_Spec_v1.0.md:74, 210` | Retained as candidate (engine is appropriate); invocation needs modernization |
| Presets `screen` / `ebook` / `printer`, default `ebook` | `compress_service.py:33-37`; `routers/compress.py:109` | **Superseded** — one automatic premium-screen profile (DEC-014) |
| Frontend hardcodes `?quality=ebook` | `frontend/src/components/PDFUploader.tsx:303` | **Removed** (UX §12.1) |
| Ghostscript flags: `-dCompatibilityLevel=1.4 -dPDFSETTINGS=... -dDetectDuplicateImages=true -dCompressFonts=true -dSubsetFonts=true`; **no `-dSAFER`** | `compress_service.py:72-86` | Baseline; rebuild adds current sandbox options (`--safe`/`-dSAFER` per current docs), no presets, and a custom premium profile |
| 30 s Ghostscript timeout | `compress_service.py:40, 89-94, 103-111` | Retain as conservative bound; feed C2 |
| Encrypted PDFs rejected with 400 (legacy policy: "tidak dapat diproses") | `routers/compress.py:84-101` | **Superseded** — DEC-036/DEC-064 require password request when needed |
| Validation order (empty/MIME/ext/magic/size/encrypted) | `routers/compress.py:36-101`; `utils/pdf_validator.py:34-141` | Retain, extended by DEC-093-style structure checks for this tool's PDFs and C4 scanning |
| Output name `compressed_<filename>` | `routers/compress.py:156` | Baseline for DEC-042 naming |
| `saved_percent = round((1-compressed/original)*100)` | `routers/compress.py:161-166` | Keep honest; DEC-080 requires truthful "no savings/larger output" UI; legacy UI floors at 0 ("−0%") — `frontend/src/lib/format.ts:15-21`, audit §6 item 15 | 
| Auto-upload on selection; XHR progress; 1 s auto-retry (uncleared timeout); 120 s client timeout | `PDFUploader.tsx:207-311` | Retain pattern; fix uncleared retry timer and honest "retrying" label (UX §12.1 baseline corrections) |
| R2 upload + 1-hour signed URL + force-download | `routers/compress.py:147-159`; `utils/r2.py` (per arch spec Appendix B) | Retain (DEC-013/170) |
| Legacy docs claim Ghostscript/PyMuPDF "industry-standard" (feasibility) and license "AGPL/Apache/MIT" (feasibility §410) | `docs/09_Papyr_Feasibility_Study_v1.0.md:101, 410` | Historical context; the AGPL fork is surfaced in A1 §9 and §7 of this brief |

### 5.3 Legacy behavior: retained / corrected / superseded (summary)

- **Retained**: server-side Ghostscript-class compression; R2 + signed-URL delivery; honest before/after reporting (with the "−0%" bug corrected); auto-upload start; validation order; per-tool rate limit and limits concept (DEC-020/034).
- **Corrected**: add current Ghostscript sandbox flags and hardened invocation (DEC-169); honest UI when output is not smaller (replace "−0%" floor); clear retry timer on unmount/reset; unified validation/constraint copy and heading semantics (audit §6 items 1, 9-10, 15; UX §12.0/12.1); password flow instead of blanket rejection (DEC-036/064).
- **Superseded**: quality presets and the hardcoded `ebook` param (DEC-014); any "always reduce size" assumption (DEC-080); legacy "−0%" pill (DEC-080); pre-processing disclosure block in favor of Privacy-page disclosure (DEC-168).

## 6. Alternatives

1. **Ghostscript pdfwrite with a custom premium-screen profile (retained engine, modernized).** Trades: strongest documented image-downsampling/re-encoding capability and industry track record; but (a) re-interprets the document (feature-fidelity risk for links/annotations/forms — functional verification required per DEC-014), (b) AGPL-3.0/commercial licensing fork for SaaS (A1 §5.4) — owner decision, (c) historical CVE load → hardened isolation mandatory (DEC-169), (d) output may be larger on already-optimized inputs (documented; handled by DEC-080 honesty). Cost: zero OSS; commercial license cost if chosen.
2. **Permissive lossless optimization (pikepdf/qpdf or PyMuPDF-save or pypdf):** recompress streams and structure, no image re-encoding. Trades: fully permissive licenses (pikepdf MPL-2.0/qpdf Apache-2.0) or AGPL (PyMuPDF); lower fidelity risk (structure-preserving); but typical savings are much smaller for image-heavy PDFs — cannot deliver "premium screen" image downsampling alone. Privacy/security: pikepdf sanitization API implements DEC-090 directly; PyMuPDF/pypdf need a sanitization pass.
3. **Hybrid pipeline (recommended shape):** Ghostscript premium profile as primary; if the owner chooses not to license AGPL engines, a permissive pipeline (pikepdf structural optimization + optional Pillow-based image downsampling re-encode) is the fallback. Trades: more glue code; permissive license clarity; still needs a sanitization pass (pikepdf provides it).
4. **Browser-side "compression"** — not feasible for real compression: pdf-lib cannot re-encode images and is unmaintained; no browser engine re-encodes PDF image streams (A1 §5.3). Records why the server-default stays (DEC-015) — one feasible path only.

Privacy/security implications (all): PDFs are untrusted input (DEC-088/092/093); every engine runs in hardened containers with bounded resources; no engine output is claimed malware-free (DEC-171); Ghostscript specifically must run with sandbox options and no network.

## 7. Recommendation

**Recommendation (not an accepted decision — DEC-054/057):** keep **Ghostscript `pdfwrite`** as the primary Compress engine with a **custom premium-screen profile** (starting points grounded in the documented distiller parameters rather than benchmarks: color/gray resolution 150 dpi, bicubic downsampling above a 1.5 threshold, DCT re-encode with a QFactor around the ebook family, `-dDetectDuplicateImages=true`, font embedding/subsetting, `-dCompatibilityLevel=1.7`), invoked with current sandbox options (`-dSAFER` per current Ghostscript docs), a bounded timeout, and hardened container isolation — **conditional on the owner's AGPL/commercial licensing decision** (A1 §9). If the owner declines AGPL terms, adopt the permissive pipeline: **pikepdf** structural optimization (MPL-2.0) + Pillow-based image downsampling with JPEG re-encode (HPND) + pikepdf sanitization (DEC-090). Either way: always-new artifact, honest size reporting (DEC-080), password flow (DEC-036/064), per-tool limits (DEC-034), and the premium-screen profile thresholds set during technical design and validated by functional testing (UX §21.1 item 2), not by benchmarks (DEC-066).

## 8. Measurable acceptance criteria

Functional verification criteria (no benchmark wording per DEC-066):

1. Selecting a valid PDF starts a server job automatically (no configuration step); the UI truthfully labels uploading/queued/processing/ready stages (DEC-033, DEC-168).
2. The output is a **newly generated PDF artifact** (byte-different from the source is expected; never a passthrough of the original) (DEC-080).
3. The result UI reports actual input size, output size, and real change — including explicit "no savings" and "output larger" wording; no fabricated percentage (DEC-080).
4. Page count and page geometry are preserved; searchable/selectable text remains selectable for a text-based fixture (DEC-014).
5. Links survive for a link-bearing source **where the selected engine preserves them**; the UI states the truthful limitation where the engine does not (DEC-079-style honesty applied to compress; DEC-014 "whenever the source format permits").
6. A fixture with active content (JavaScript, embedded attachment, launch action) produces output without that content, and the UI discloses the general categories removed (DEC-090/091).
7. Encrypted-input fixture: password requested only when needed; correct password processes; wrong password returns a distinct error (DEC-036/064).
8. Threat-classified fixture is blocked with a safe rejection (DEC-088) and files never reach the engine beyond minimum inspection (C4 integration).
9. Ghostscript (if selected) runs with sandbox options, non-root, bounded CPU/memory/time/disk, restricted network (DEC-169); 30 s timeouts produce clear errors (legacy `compress_service.py:103-111` baseline).
10. Output naming follows DEC-042 (`compressed_<source>` family with safe localized suffix).
11. Server-result expiry is enforced and displayed per DEC-067/070; download uses short-lived signed URLs (DEC-170).
12. The capability/limits contract exposes Compress-specific server limits and the frontend renders them (DEC-165).

## 9. Assumptions, uncertainties, and unresolved questions

1. **AGPL vs commercial vs permissive** for Ghostscript (and PyMuPDF if used anywhere in the matrix) is the primary open owner question (A1 §9).
2. **Premium-profile exact thresholds** (resolution, downsampling threshold, QFactor, font handling) are deliberately not fixed here: they are design choices validated by functional testing (UX §21.1 item 2; DEC-066). Starting values above are recommendations from documented engine parameters.
3. **Feature preservation through pdfwrite** (links/annotations/forms) is engine-version-dependent; the brief records the documented limitation and requires functional fixtures, not a guarantee (DEC-014, DEC-079-style honesty).
4. **Output can grow**: documented engine characteristic; the product must not treat growth as failure (DEC-080).
5. **Sanitization coverage** is not universal; category detection and removal must be verified per engine and disclosed honestly (DEC-090/091).
6. Owner question: is the "premium screen" profile to prioritize text documents, scanned/photographic PDFs, or both equally — the profile trade-off differs (downsampling is the lever for scans; font/stream work dominates text PDFs).

## 10. Dependencies and cross-track interfaces

- **A1** supplies the license/version/security evidence cited throughout.
- **B1**: server-default means no browser capability routing for Compress; still needs the Privacy-page disclosure and truthful stage labels (DEC-168).
- **C2**: compress-specific server limits (bytes, pages, est. memory, timeout) depend on the selected engine's documented profile and production observation (DEC-034, DEC-066).
- **C4**: Ghostscript sandbox flags, container hardening, malware scanning, and update channel (DEC-169, DEC-171, DEC-179).
- **D5**: threat blocking (DEC-088) precedes sanitization (DEC-090/091); sanitization categories feed the D5 register and the DEC-091 UI message.
- **X2**: surfaces the AGPL owner-decision prompt and the premium-profile confirmation to the reconciliation report (plan §14).

## 11. Source-date log and evidence-completeness notes

- Web sources: Ghostscript releases (2026-07-31), VectorDevices doc gs10.05.1 (2026-07-31), Artifex licensing/hardening blog (2026-07-31), Ghostscript CVE index (2026-07-31), A1 §5.1 for all versions/licenses.
- Legacy sources read 2026-07-31 with line citations above.
- Completeness: engine behavior is documented from primary docs; no runtime validation was performed (prohibited); per-tool limits and failure profiles are recorded qualitatively for C2 and must be validated during implementation by normal functional testing.

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative report, or quality-score program was created or run (DEC-066).
- No installs, builds, servers, VPS access, deployment, account creation, or authenticated remote actions (plan §4.1).
- `papyr-reference/` read-only; `git -C papyr-reference status --porcelain` empty with exit 0 before and after.
- No claim of malware-free output, universal sanitization, or guaranteed preservation is made (DEC-090, DEC-171).
- Recommendation only; owner approval required (DEC-057).
