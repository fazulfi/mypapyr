# A4 — Split PDF Research Brief

## 1. Header

- **Brief ID**: A4
- **Path**: `<workspace-root>\audit-outputs\research\track-a\a4-split-pdf.md`
- **Track**: A — Tool and engine research
- **Title**: Split PDF research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (Track A executor subagent)
- **Status**: Draft (complete for owner review; no accepted product decision)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (A4; §7.1; §8)
- **Governing decisions**: DEC-011 (browser-first), DEC-015 (limits), DEC-030/DEC-065 (server fallback), DEC-036/DEC-064 (encrypted input), DEC-037 (ZIP + individual downloads), DEC-038 (range + per-page modes), DEC-042 (naming), DEC-054-060, DEC-066, DEC-077 (overlap = independent outputs), DEC-078 (user-entered order), DEC-088/090/091 (threat blocking + sanitization), DEC-179, DEC-188
- **Engine/license evidence**: cited from `a1-shared-engine-licenses.md`
- **Files read**: all files listed in A1 §1, plus tool-specific: `papyr-reference/frontend/src/components/PageRangeInput.tsx` (full), `papyr-reference/frontend/src/lib/pdfUtils.ts` (full), `papyr-reference/backend/services/pdf_to_image_service.py` (parse_page_range reference for legacy sort/dedupe), audit `ui-five-tools-audit.md` §3.3/§3.5 and §4

## 2. Scope

Split PDF extracts selected pages as separate PDFs. Two MVP modes (DEC-038): **custom page ranges** and **one PDF per page**. Approved Papyr behavior:

- Browser-first with automatic server fallback for corrupt/encrypted-unsupported/unsafe jobs (DEC-011, DEC-030, DEC-065) within DEC-015 limits.
- Range syntax and validation: clear syntax, start-after-end, out-of-bounds, malformed-token errors with actionable localized messages; live preview of effective outputs (DEC-038).
- **Overlap semantics (DEC-077)**: entered ranges may overlap; each range creates an independent output; duplicated page membership is visible in preview; never merged/deduplicated/silently rewritten; repeated identical ranges need unambiguous labels.
- **Order semantics (DEC-078)**: outputs, ZIP ordering, individual-download listing, naming sequence, and manifest follow the *user-entered* range order (e.g., `8-10,1-2` → `8-10` first). Per-page mode continues in natural page order.
- Multi-file results: auto-download a ZIP and keep each generated file individually downloadable (DEC-037); single-output jobs download directly.
- Output naming: deterministic, safe, ordered names derived from the source plus range/page identifiers (DEC-042); legacy `split_<range>.pdf` is the baseline (UX §12.3).
- Encrypted input: password requested only when required (DEC-036, DEC-064).
- Sanitize active content from outputs with category disclosure (DEC-090, DEC-091).
- Server results: one-hour retention, signed URLs, per-tool limits (DEC-034), machine-readable contract (DEC-165).

## 3. Non-goals

- No page-reordering, page-removal-in-place, or document editing beyond selection (DEC-038 scope).
- No benchmark program or comparative quality study (DEC-066).
- No "all pages" quick-select behavior change: the legacy quick-select chips (First/Last/All) are retained as UX baseline (audit §3.3).
- No preservation of active content — sanitized (DEC-090).
- No AGPL compliance decision here (A1 §9).

## 4. Research questions

1. Which engines satisfy browser-first page extraction plus server fallback with structure preservation and sanitization?
2. Licenses and obligations (cite A1).
3. Current versions and documentation (A1).
4. Representative failure modes and resource profiles for range/per-page splits, qualitatively.
5. Legacy behavior retained/corrected/superseded, with citations (esp. PageRangeInput sort+dedupe).
6. At least two viable alternatives with trade-offs; recommendation.
7. Measurable acceptance criteria (functional).
8. Cross-track interfaces (B1, C2, C4, D5).

## 5. Evidence

### 5.1 Engine capability evidence (primary sources, 2026-07-31)

- **pdf-lib 1.17.1 (MIT; unmaintained)** — browser extraction via `copyPages(source, indices)` + `addPage` into a fresh document (legacy `pdfUtils.ts:170-201`). Preserves page content and geometry; creates independent output per selection (per-mode loop over selections). No encryption support (README primary evidence) → encrypted inputs route to server (DEC-064). No sanitization — the browser path produces page copies that may carry page-level active content into the output; DEC-090's sanitization applies to *server* outputs ("PDF-producing server outputs" — arch §17.3), and the browser path must be addressed for equivalent safety outcomes (DEC-093's browser/server equivalence principle extended by C4 reconciliation).
- **pikepdf 10.11.0 / qpdf 12.3.2 (MPL-2.0 / Apache-2.0)** — page selection via `pikepdf.Pdf.pages` slicing or qpdf `--pages`; structure- and content-preserving (outlines/destinations behavior documented in qpdf page-selection docs — page selection may or may not carry document-level structures; deterministic handling is design work per DEC-079-style discipline); attachment ops; **sanitization API** (`remove_javascript`, `remove_attachments`, `remove_external_access`, `Sanitizer`) implements DEC-090 categories; password/encryption support. Recommended server engine shape.
- **pypdf 6.14.2 (BSD-3-Clause)** — `PdfWriter.append/merge` for extraction; outlines import; encrypted input needs decryption; no sanitization API; DoS CVE history fixed in current versions (A1 §5.3).
- **PyMuPDF 1.28.0 (AGPL/commercial)** — `select(pages)`/`insert_pdf`; fast; AGPL fork; no first-class sanitization API (A3 §5.1).
- **pdfcpu v0.13.0 (Apache-2.0)** — split/trim; PDF 1.7 ceiling.

### 5.2 Legacy evidence (read-only)

| Legacy fact | Location | Disposition |
|---|---|---|
| Range parser: charset `[\d\s,\-]`; Set-based **dedupe**; **sorted** output (`Array.from(pages).sort(...)`) | `frontend/src/components/PageRangeInput.tsx:27, 38, 87` | **Superseded** — preserve order (DEC-078) and permit overlap (DEC-077) |
| Two-step flow: dropzone → "Membaca dokumen PDF..." (loading card) → ready state with file info + range input | `split/page.tsx` per audit §3.3 (`:445-452`) | Retain (UX §12.3) |
| Live preview "Halaman yang dipilih: ..." + quick-select chips First/Last/All | `PageRangeInput.tsx:132-161` | Retain; preview must additionally show duplicated membership and effective output sequence (DEC-077/078) |
| Output filename `split_<range>.pdf` derived from raw input (e.g., `1-3, 5` → `split_1-3_5.pdf`), fallback `split_pages.pdf` | `split/page.tsx:320-328` (audit §3.3) | Baseline for DEC-042; extended to per-page mode and manifest |
| Browser-only split via pdf-lib `splitPDF` (single output per call; page list passed in) | `frontend/src/lib/pdfUtils.ts:170-201` | Retained as primitive; rebuild produces one output per *range entry* (not one merged selection), preserving order |
| Server `parse_page_range` (used by legacy PDF-to-Image, not legacy Split) also sorts+dedupes | `backend/services/pdf_to_image_service.py:54, 109` | Superseded by DEC-186/078 for page-selection tools generally |
| State machine idle/loading/ready/processing/done/error; error → "Coba Lagi" returns to ready when page count known | audit §3.3 | Retain |
| No empty-state copy on Split idle | audit §3.3/§6 item 11 | Corrected per UX §12.0 (add empty-state copy) |

### 5.3 Legacy behavior: retained / corrected / superseded

- **Retained**: two-step reading flow; range input UX (label, placeholder, inline errors, live preview, quick selects); single-file dropzone; `split_<range>.pdf` naming concept; browser-first processing.
- **Corrected**: empty-state copy; accessible error/preview wiring (aria-live/aria-invalid — audit §6 item 7); failure-reason analytics label `'server_error'` for client work (audit §6 item 13).
- **Superseded**: sort-and-deduplicate range semantics (DEC-077/078); any silent merging of overlapping ranges; single-selection output model replaced by one-output-per-range with ZIP + individual downloads (DEC-037/038).

## 6. Alternatives

1. **pdf-lib browser-first + pikepdf server fallback (recommended shape).** Browser loop executes one `copyPages` per user-entered range into separate fresh documents (order = user order; overlap = independent outputs trivially); server fallback uses pikepdf page selection + sanitization pass (DEC-090) + encryption support. Trades: two paths to keep in parity; browser path cannot sanitize (see §5.1 — resolve in C4 reconciliation and disclose); pdf-lib unmaintained (A1 §9.4).
2. **Server-only pikepdf/qpdf split.** Trades: single engine, structure preservation, sanitization, permissive licenses; but removes browser-first (DEC-011) unless the owner accepts a routing override — not recommended.
3. **Server-only pypdf or PyMuPDF.** Trades: pypdf permissive with no sanitization API and documented merge/decrypt limitations; PyMuPDF AGPL fork and no first-class sanitization. Viable only with extra glue or AGPL acceptance.
4. **pdfcpu (Go)** as server engine — Apache-2.0, split/trim; PDF 1.7 ceiling; different runtime; viable but adds toolchain diversity without a capability advantage over pikepdf.

Privacy/security: split outputs are derived from untrusted inputs; sanitization applies to PDF-producing server outputs (arch §17.3); browser outputs must meet equivalent safety outcomes (DEC-093 principle) — the recommended design routes active-content-bearing or unsafe files to the server sanitization path and discloses honestly (DEC-090/091).

## 7. Recommendation

**Recommendation (not an accepted decision — DEC-054/057):** implement **browser-first splitting with pdf-lib** where each user-entered range produces its own output document in user-entered order (overlap naturally independent — DEC-077; order naturally preserved — DEC-078), within DEC-015 limits, and route encrypted, corrupt, unsafe, or active-content-bearing files to a **pikepdf server fallback** that performs structure-preserving page extraction plus the DEC-090 sanitization pass with DEC-091 category disclosure. Server ZIP assembly and manifest follow user-entered order (DEC-037/078); per-page mode is natural page order (DEC-078). pypdf is the permissive fallback if pikepdf is rejected. This keeps DEC-011's browser-first model while making DEC-077/078/090/064 satisfiable.

## 8. Measurable acceptance criteria

1. Custom range `8-10,1-2` on a 10-page PDF produces exactly two outputs — `8-10` first, `1-2` second — in ZIP order, individual-download listing, naming sequence, and manifest (DEC-078).
2. Overlapping ranges (e.g., `1-3,2-4`) produce independent outputs with duplicated page membership visible in the preview before processing; the system never merges or dedupes (DEC-077).
3. Repeated identical ranges produce unambiguous output labels (DEC-077) — deterministic naming rule verifiable by fixture.
4. Per-page mode on an N-page PDF produces N outputs in natural page order, subject to output-count/archive-size safety limits (DEC-038).
5. Range validation: charset, start>end, out-of-bounds (incl. 0), and malformed tokens each yield a localized, actionable error; CTA disabled until valid (DEC-038).
6. Multi-output jobs auto-download a ZIP; every generated file remains individually downloadable; single-output jobs download directly (DEC-037).
7. Encrypted input: password requested only when required; correct password proceeds; wrong password errors distinctly (DEC-036/064).
8. Sanitization: server outputs of a fixture with JavaScript/attachment/launch action contain none of those, and the UI discloses the general categories removed (DEC-090/091).
9. Threat-classified inputs are blocked, not sanitized and returned (DEC-088).
10. Naming is source-derived + range/page identifiers (DEC-042); no legacy merged-selection behavior.
11. Server results: one-hour retention clock, signed URLs, expiry UI, per-tool limits from the machine-readable contract (DEC-013/067/070/170/165).
12. Browser routing: over-limit/encrypted/unsafe files transition to the server path with truthful messaging; no retry loops or duplicate outputs (DEC-030/065).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Browser-path sanitization**: pdf-lib page copies may carry page-level active content into outputs; DEC-090's text targets "PDF-producing server outputs," but the browser/server safety-equivalence principle (DEC-093; arch §17.2) requires a decision — recommended resolution: route active-content-bearing files to the server sanitization path and disclose honestly. This needs owner/design confirmation and a fixture for detection.
2. **Output-count ceilings** (per-page mode) are C2 inputs: conservative defaults (e.g., max outputs/archive size) are design choices documented as safety limits (DEC-034, DEC-066).
3. **Repeated identical range labeling**: how to disambiguate (`1-3`, `1-3 (2)`) is a naming-policy detail for the copy/naming design (DEC-042, DEC-077).
4. **Legacy manifest**: legacy Split had no ZIP/manifest (client-only single output); the manifest format is new design work (DEC-037).
5. Owner questions: (a) browser-path active-content routing approach above; (b) whether "All pages" quick-select should be retained as-is in the two-mode MVP (legacy chip) — recommended retain.

## 10. Dependencies and cross-track interfaces

- **A1**: license/version evidence (pdf-lib MIT/unmaintained; pikepdf MPL-2.0; qpdf Apache-2.0).
- **B1**: routing thresholds for encrypted/complex/corrupt/active-content files (DEC-015/030/065).
- **C2**: per-tool split limits — output count, per-file bytes, total pages, ZIP expansion, memory (DEC-034).
- **C4**: sanitization pass and hardening for the server path (DEC-090/169/171); browser/server safety-equivalence reconciliation.
- **D5**: threat blocking before sanitization (DEC-088); sanitization categories for DEC-091.
- **X2**: surfaces the split-engine approval and the browser-sanitization decision.

## 11. Source-date log and evidence-completeness notes

- Sources: pdf-lib npm/README, pikepdf docs, qpdf docs, pypdf docs — accessed 2026-07-31 (A1 §5.1). Legacy files read 2026-07-31 with citations above (PageRangeInput and pdfUtils read in full; split/page.tsx verified via audit §3.3 line-level extraction).
- Completeness: no runtime validation performed (prohibited); semantics (order/overlap) are specified by accepted decisions and verifiable by fixtures at implementation time.

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative report, or quality-score program (DEC-066).
- No installs, builds, servers, VPS access, deployment, account creation, or authenticated remote actions (plan §4.1).
- `papyr-reference/` read-only; `git -C papyr-reference status --porcelain` empty with exit 0 before and after.
- No claim of malware-free output, universal sanitization, or guaranteed preservation (DEC-090, DEC-171).
- Recommendation only; owner approval required (DEC-057).
