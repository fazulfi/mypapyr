# A3 — Merge PDF Research Brief

## 1. Header

- **Brief ID**: A3
- **Path**: `<workspace-root>\audit-outputs\research\track-a\a3-merge-pdf.md`
- **Track**: A — Tool and engine research
- **Title**: Merge PDF research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (Track A executor subagent)
- **Status**: Draft (complete for owner review; no accepted product decision)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (A3; §7.1; §8)
- **Governing decisions**: DEC-011 (browser-first), DEC-015 (browser limits), DEC-030/DEC-065 (auto server fallback), DEC-036/DEC-064/DEC-074 (passwords per file), DEC-040 (file-level controls), DEC-042 (naming), DEC-076 (all-or-nothing), DEC-079 (safe feature preservation), DEC-088/090/091 (threat blocking + sanitization), DEC-054-060, DEC-066, DEC-179, DEC-188
- **Engine/license evidence**: cited from `a1-shared-engine-licenses.md`
- **Files read**: all files listed in A1 §1, plus tool-specific: `papyr-reference/frontend/src/app/merge/page.tsx` (behavior cited via `audit-outputs/ui-five-tools-audit.md` §3.2 and §4 with line references), `papyr-reference/frontend/src/lib/pdfUtils.ts` (full), `papyr-reference/backend/tests/test_pdf_to_image.py` (not merge-specific; cross-check for page-selection semantics), pypdf merging docs and pikepdf sanitization docs (2026-07-31)

## 2. Scope

Merge PDF combines multiple PDFs into one file in the user's chosen order, with file-level controls only (reorder via drag-and-drop with keyboard alternatives, remove files; no cross-document page editor in the MVP — DEC-040). Approved Papyr behavior:

- Browser-first processing with automatic server fallback for corrupt/encrypted-unsupported/unsafe jobs (DEC-011, DEC-030, DEC-065) within DEC-015 browser limits (100 MB/500 pages desktop; 50 MB/200 pages mobile; 25 MB/100 pages iOS).
- Per-file validation; all-or-nothing semantics — no partial output presented if any source fails to open/authenticate/validate/process (DEC-076); UI identifies the affected source safely and keeps other valid sources in memory.
- Each encrypted input gets its own password requested and validated independently; credentials memory-only, never reused (DEC-064, DEC-074, DEC-036).
- Preserve bookmarks, form fields, annotations, links, metadata, page geometry, and other supported document features to the greatest extent the selected engine can do *safely*; unsupported or transformed features disclosed truthfully; no universal lossless claim (DEC-079).
- Sanitize detected active content from the output and disclose general categories removed (DEC-090, DEC-091).
- CTA enabled only with two or more valid files; page order within each source preserved (DEC-040).
- Output naming source-derived with a safe localized suffix (DEC-042); legacy hardcoded English `merged.pdf` (`merge/page.tsx:451-455` per audit §3.2; spec UX §12.2) is replaced.
- Server results: one-hour retention, signed URLs, ZIP+individual applies to multi-file results (Split/PDF-to-JPG); Merge produces a single PDF so the single-download path applies (DEC-037 scoped to multi-file tools).

## 3. Non-goals

- No page-level editor, cross-document rearrangement/removal, or per-page composition in the MVP (DEC-040).
- No benchmark program or comparative quality study (DEC-066).
- No guarantee of lossless feature preservation — DEC-079 requires truthful limits, not promises.
- No preservation of active content (JavaScript, attachments, launch actions) — those are sanitized, not preserved (DEC-090).
- No decision on the AGPL compliance path (A1 §9).

## 4. Research questions

1. Which engine(s) best satisfy browser-first merging plus the DEC-079 safe-feature-preservation and DEC-090 sanitization requirements?
2. Licenses and obligations (cite A1).
3. Current versions and documentation (A1).
4. Representative failure modes and resource profiles for multi-file merges, qualitatively (DEC-066).
5. Legacy behavior retained/corrected/superseded, with citations.
6. At least two viable alternatives with trade-offs; recommendation.
7. Measurable acceptance criteria (functional).
8. Cross-track interfaces (B1, C2, C4, D5).

## 5. Evidence

### 5.1 Engine capability evidence (primary sources, 2026-07-31)

- **pdf-lib 1.17.1 (MIT; unmaintained since 2021)** — browser merge via `copyPages` + `addPage` (legacy `pdfUtils.ts:209-233`). Capabilities: copies page content streams and page-level objects (incl. annotations that live on pages); supports creating forms and adding attachments, setting document metadata. **Limitations** (primary README): cannot read/manipulate encrypted documents (`EncryptedPDFError`; `ignoreEncryption` does not decrypt); cannot extract/rewrite plain text; no HTML/CSS; and for merging it does not merge document-level structures across inputs — outlines/bookmarks, document-level metadata, named destinations, and AcroForm fields of the sources are not carried into a fresh `PDFDocument.create()` result (feature-set evidence: fresh doc + copyPages; the README's feature list contains no merge-outlines/merge-forms capability). This directly bounds DEC-079 in the browser path: page content and geometry yes; cross-document bookmarks/forms/document metadata no (truthful disclosure required).
- **pikepdf 10.11.0 / qpdf 12.3.2 (MPL-2.0 / Apache-2.0)** — structure-preserving page selection/merge (`pikepdf` page copy across `Pdf` objects; qpdf `--pages`); encryption/password handling; attachment ops; **explicit sanitization API**: `remove_javascript()`, `remove_attachments()`, `remove_external_access()`, `remove_thumbnails()`, `Sanitizer` — directly implements DEC-090's categories (JavaScript, embedded attachments, external actions, launch actions via /OpenAction//AA). Page geometry and content streams are preserved at object level; forms/outlines/annotations/links are carried if copied deliberately (copying pages preserves page-associated annotations/links; document-level structures need explicit handling — deterministic conflict rules for duplicate form names, outlines, metadata are design work, and DEC-079 asks that they be documented, not benchmarked).
- **pypdf 6.14.2 (BSD-3-Clause)** — `PdfWriter.append/merge`; imports outlines; page geometry preserved; **documented limitation**: when merging forms, some form fields with identical names prevent access to data (pypdf merging docs). Encrypted inputs need decryption first (`crypto` extra). Known DoS CVEs fixed in current versions (A1 §5.3). No sanitization API.
- **PyMuPDF 1.28.0 (AGPL-3.0/commercial)** — `insert_pdf` concatenation; bookmarks via `get_toc`/`set_toc` (manual, per Artifex merge guide); fast; AGPL licensing fork; no built-in sanitization API (MuPDF's `mutool clean` has sanitize options, but PyMuPDF does not wrap them as a first-class API — treat as a gap to verify or as an additional MuPDF-toolchain step).
- **pdfcpu v0.13.0 (Apache-2.0)** — merge/split; attachments; PDF 1.7 ceiling; Go-based (different runtime).

### 5.2 Legacy evidence (read-only)

| Legacy fact | Location | Disposition |
|---|---|---|
| Merge is browser-only via pdf-lib `mergePDFs` (>=2 files, `copyPages`) | `frontend/src/lib/pdfUtils.ts:209-233` | Retained as the browser happy path; document-feature caveats must be disclosed (DEC-079) |
| `ignoreEncryption: true` on load — silently loads undecrypted doc and "may fail or have unexpected results" | `pdfUtils.ts:221` | **Corrected**: encrypted inputs must route to server with a password flow (DEC-064/074), not silently attempted locally |
| Drag-and-drop reorder (dnd-kit Pointer+Keyboard sensors, 5 px) + remove + order badges + "{n} files · size" summary | `merge/page.tsx` per audit §3.2 (`:357-360, 266-330, 606-613`) | Retain (DEC-040); add keyboard announcements and drag-handle aria-labels (audit §6 item 7) |
| CTA disabled until >=2 valid files with helper | `merge/page.tsx:635-652` | Retain |
| Per-file validation messages (`"<name>" bukan file PDF.` etc.) | `merge/page.tsx:368-400` | Retain with unified template (audit §6 item 10) |
| Hardcoded English `merged.pdf` filename | `merge/page.tsx:451-455` (audit §3.2); spec UX §12.2 | **Superseded** by DEC-042 naming |
| State machine idle/processing/done/error; files persist across error → "Coba Lagi" | audit §3.2 | Retain; add error-state edge case owner confirmation (audit §8.7; UX §21.16) |
| No backend merge endpoint exists (client-only in legacy) | `docs/11_Papyr_API_Spec_v1.0.md:78` | Rebuild adds the server fallback path (DEC-030/065) |

### 5.3 Legacy behavior: retained / corrected / superseded

- **Retained**: browser-first merge; file-level reorder/remove; >=2-file CTA gate; page-order-per-source; dnd-kit interaction contract.
- **Corrected**: encrypted-input handling (server routing + per-file passwords — DEC-064/074); drag-handle/keyboard accessibility; unified validation copy; error-state auto-clear decision surfaced to owner (audit §8.7).
- **Superseded**: hardcoded `merged.pdf`; silent `ignoreEncryption` merge; any implication that all document features survive (DEC-079 disclosure); preservation of active content (DEC-090).

## 6. Alternatives

1. **pdf-lib browser-first + pikepdf server fallback (recommended shape).** Browser happy path is the accepted DEC-011 model and preserves page content/geometry/order; the server fallback uses pikepdf (structure-preserving, permissive MPL-2.0, sanitization API, password support). Trades: two code paths to keep behaviorally consistent (browser vs server result parity is an acceptance criterion); pdf-lib's unmaintained status and limited feature merge require truthful DEC-079 disclosure on the browser path; server path carries the sanitization pass (DEC-090) and C4 hardening.
2. **Server-only merge with pypdf (BSD-3-Clause).** Trades: single engine, outline import on merge; but form-name conflicts documented; no sanitization API; encrypted inputs need pre-decrypt; contradicts DEC-011's browser-first preference (would need an owner decision to override).
3. **Server-only merge with PyMuPDF (AGPL/commercial).** Trades: fast, mature; manual bookmark handling; AGPL fork; no first-class sanitization API. Only viable if AGPL terms are accepted.
4. **qpdf `--pages` / pdfcpu as the server engine.** Trades: qpdf content-preserving and permissive (Apache-2.0); attachment ops; no sanitization for JS/actions beyond attachment removal (needs a pikepdf-style object walk); pdfcpu PDF 1.7 ceiling and Go runtime. Viable but pikepdf bundles the sanitization API, which these lack.

All four satisfy "at least two viable alternatives" (DEC-055). Privacy/security: server merge receives multiple untrusted files; every engine runs in hardened isolation; passwords memory-only (DEC-036/074); output sanitized (DEC-090) and never claimed malware-free (DEC-171).

## 7. Recommendation

**Recommendation (not an accepted decision — DEC-054/057):** keep **pdf-lib for the browser happy path** (unencrypted, within DEC-015 limits) and adopt **pikepdf (qpdf) for the server fallback** — merging with explicit, deterministic conflict handling for duplicate form names/destinations/outlines/metadata (documented per DEC-079), plus a **pikepdf sanitization pass** implementing DEC-090 (JavaScript, launch actions, embedded attachments, external actions) with category-level reporting for DEC-091. Browser and server outputs must pass the same functional acceptance checks (order, page count, geometry, sanitization, disclosure). If the owner prefers a single engine, pypdf (BSD) is the permissive fallback with its documented form-merge limitation; PyMuPDF requires the AGPL decision from A1 §9. Any merge result discloses the truthful feature-preservation scope (DEC-079) — no lossless promise.

## 8. Measurable acceptance criteria

1. Merging N valid PDFs produces one PDF containing every source page in the user's selected order, with page order within each source preserved (DEC-040).
2. The CTA is disabled until two or more valid files are selected; helper text shows (legacy pattern retained).
3. A job with one invalid/corrupt/unreadable source fails with a safe error identifying the source; **no partial output is produced or presented** (DEC-076); valid sources remain in memory for correction/retry.
4. Encrypted inputs: each locked source is identified and its password requested/validated independently; wrong password on one file does not process the job; credentials never logged/persisted (DEC-036/064/074).
5. Feature preservation: a fixture with bookmarks, form fields, annotations, links, and metadata is merged and the result verified against the *selected engine's documented* preservation scope; any unsupported/transformed feature is disclosed truthfully (DEC-079).
6. Sanitization: a fixture with JavaScript, an embedded attachment, and a launch action produces output without those elements, and the UI reports the general categories removed (DEC-090/091).
7. Threat-classified input is blocked, not sanitized and returned (DEC-088).
8. Browser routing: jobs within DEC-015 limits process locally; jobs over limits, encrypted, corrupt, or unsafe route to the server with truthful transition messaging (DEC-030/065); no retry loops or duplicate outputs (DEC-065).
9. Output naming is source-derived with a safe localized suffix (DEC-042); never the hardcoded `merged.pdf`.
10. Server results obey the one-hour retention clock, signed-URL download, and expiry UI (DEC-013/067/070/170); limits come from the machine-readable contract (DEC-165).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Browser-path feature scope is engine-bounded**: pdf-lib will not merge document-level outlines/forms/metadata. Whether the browser path must match server-path feature preservation, or disclose the difference, is a design decision this brief recommends resolving in favor of truthful disclosure + server fallback for feature-critical jobs (B1 routing input).
2. **Conflict handling** (duplicate form names, destinations, outlines, metadata) has no off-the-shelf canonical behavior across engines; DEC-079 requires documenting deterministic rules — design work, validated by fixtures.
3. **pdf-lib unmaintained**: acceptable for an MVP happy path only if its transitive dependency set is reviewed and a migration path exists (A1 §9.4).
4. **Sanitization coverage** is per-engine and must be verified; pikepdf's API covers the DEC-090 categories but "detected" semantics (what counts as detection) need fixture-based definition.
5. Owner questions: (a) acceptable to carry two merge implementations (browser + server) for parity, or prefer server-only; (b) whether the browser path should hide/limit feature-preservation expectations in copy (DEC-079 honesty) — wording to be finalized in the copy pass.

## 10. Dependencies and cross-track interfaces

- **A1**: license/version/security evidence (pikepdf MPL-2.0, pdf-lib MIT/unmaintained, qpdf Apache-2.0).
- **B1**: routing thresholds for encrypted/complex/corrupt files to the server path (DEC-015/030/065); pdf-lib encryption limitation is a routing input.
- **C2**: per-tool merge server limits (file count, per-file bytes, total pages, estimated memory) (DEC-034).
- **C4**: sanitization and hardening for the server merge path (DEC-090, DEC-169, DEC-171).
- **D5**: threat blocking precedes sanitization (DEC-088); sanitization categories feed the DEC-091 message and the D5 register.
- **X2**: surfaces the merge-engine approval item and the browser/server parity decision.

## 11. Source-date log and evidence-completeness notes

- Sources: pikepdf docs/PyPI, qpdf docs, pypdf merging docs, pdf-lib npm/README — all accessed 2026-07-31 (A1 §5.1). Legacy files read 2026-07-31 (audit §3.2 line refs and `pdfUtils.ts` cited above).
- Completeness: `merge/page.tsx` (687 lines) was verified through the audit's line-level extraction and targeted reads; no runtime validation was performed (prohibited). Engine feature behavior is documented from primary sources; fixture verification is an implementation-time acceptance activity.

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative report, or quality-score program (DEC-066).
- No installs, builds, servers, VPS access, deployment, account creation, or authenticated remote actions (plan §4.1).
- `papyr-reference/` read-only; `git -C papyr-reference status --porcelain` empty with exit 0 before and after.
- No claim of malware-free output, universal sanitization, or guaranteed lossless preservation (DEC-079, DEC-090, DEC-171).
- Recommendation only; owner approval required (DEC-057).
