# B1 - Browser Capability Detection and Routing Thresholds

## 1. Header

- **Brief ID**: B1
- **Path**: `<workspace-root>\audit-outputs\research\track-b\b1-browser-capability-routing.md`
- **Track**: B - Frontend, capability, and SEO research
- **Title**: Browser capability detection and routing thresholds
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (executor subagent, Track B)
- **Status**: Draft (complete for owner review under DEC-057; findings are recommendations, not accepted decisions)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (deliverable B1 at §6.2; Track B questions §7.2; brief template §8; verification §11)
- **Governing decisions**: DEC-011, DEC-015, DEC-030, DEC-031, DEC-065 (primary); supporting DEC-032, DEC-036, DEC-054 through DEC-060, DEC-064, DEC-066, DEC-083, DEC-085, DEC-089, DEC-090, DEC-092, DEC-093, DEC-165, DEC-188
- **Spec sections served**: Technical Architecture Specification §10 (Browser/Server Routing, lines 462-496), §4.3 (lines 221-227), §14.1 (lines 666-673), §22.4 (lines 953-958), §25.3.17 (line 1077); Product and UX Design Specification §16.3 (lines 578-582), §18 (lines 598-610), §21.1 (line 699)
- **Files read**:
  - `<workspace-root>\AGENTS.md`
  - `<workspace-root>\audit-outputs\research-program-plan.md`
  - `<workspace-root>\papyr-rebuild-decisions.md` (DEC-001 through DEC-188, Open decisions)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (§16, §18, §21)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (§10, §14, §22, §25.3)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-b1-web.md` (web/primary-source evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-decisions.md` (decision-log extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-specs.md` (spec extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-legacy-frontend.md` (legacy frontend evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-ui-audits.md` (UI audit evidence)
  - Legacy (read-only): `papyr-reference/frontend/src/lib/config.ts`, `frontend/src/components/PDFUploader.tsx`, `frontend/src/app/image-to-pdf/page.tsx` (per `_evidence-legacy-frontend.md` and arch spec §11.5 citations)
- **Template note**: The plan §8 lists 12 numbered sections. The header sub-fields above are expanded as their own labeled fields; combined with the 12 numbered sections this satisfies both the plan's template and the 16-section instruction for Track B briefs (header sub-fields counted individually), following the Track A A1 precedent.

---

## 2. Scope

This brief resolves the browser capability detection and routing-threshold research for the hybrid browser-first processing model. It covers:

- **Capability signals**: which client-side signals (memory, decoded dimensions, page geometry, encryption, corruption, relevant APIs) determine local feasibility, per DEC-011 ("Routing must be based on measured capabilities and explicit rules rather than hidden arbitrary behavior", source lines 133-144) and DEC-015.
- **Conservative routing thresholds per tool**: the device-aware browser-first caps of DEC-015 (lines 185-200) and how they map to the five tools.
- **Browser support matrix and progressive enhancement**: how DEC-031 (lines 391-401) and the documented enhancement patterns affect routing and fallback.
- **Automatic server fallback**: the single-transition fallback of DEC-030 and DEC-065 and which failure classes fail closed.

The user problem served: a task-oriented visitor with an arbitrary supported browser should get reliable local processing whenever the job fits the device's documented capabilities, and an automatic, visible, single transition to temporary server processing otherwise, without crashes, retry loops, or misleading claims about where the file is handled (DEC-030, DEC-065).

The current approved Papyr behavior this brief must support: hybrid model preferring local browser processing (DEC-011); conservative device-aware limits of 100 MB / 500 pages desktop, 50 MB / 200 pages capable mobile, 25 MB / 100 pages iPhone and iPad, PDF-to-JPG 200 pages desktop and 50 pages mobile with a 16-megapixel per-page ceiling, JPG-to-PDF 50 images / 100 megapixels desktop and 40 megapixels mobile, Compress server-default (DEC-015); automatic fallback for corrupt, encrypted, unsupported, or unsafe files (DEC-030); fallback after safe browser failure without a second confirmation (DEC-065); local results kept only for the active tab session (DEC-032); passwords requested only when encryption is detected (DEC-036, DEC-064).

## 3. Non-goals

- No benchmark program, corpus, comparative performance study, or quality-score evaluation of browsers, engines, or devices (DEC-066). All resource statements are documented engineering facts or conservative design/safety choices.
- No per-tool server limits (bytes, pages, pixels, estimated memory on the server): owned by Track C2 (DEC-034, plan §6.3).
- No engine or library selection for the tools: owned by Track A2-A6. This brief consumes their documented memory and canvas characteristics.
- No browser-support test matrix implementation: the arch spec §22.4 (lines 953-958) and the UX spec §16.3 define the testing obligations; this brief supplies the routing facts those tests must verify.
- No frontend implementation, installs, builds, or browser execution (plan §4.1).
- No decision on whether a browser-local job must show a manual paper or margin control (DEC-041 prohibits controls; paper policy is Track B3).

## 4. Research questions

Restated from plan §7.2 (B1):

1. Which capability signals determine whether a job is feasible locally, and how is each signal measured without relying on hidden or unavailable data (DEC-011, DEC-015)?
2. What conservative routing thresholds apply per tool and per device class, given the DEC-015 caps and the documented browser memory ceilings?
3. How do the DEC-031 browser support matrix and progressive enhancement shape the baseline path and the enhanced path for each capability?
4. Which failure classes transition automatically to server processing, and which fail closed, per DEC-030 and DEC-065?
5. What are the interfaces to the tool briefs (A2-A6) and the server-limits brief (C2), and where do browser limits end and server limits begin (DEC-165)?
6. How is the resulting routing behavior verified without a benchmark program (DEC-066)?

## 5. Evidence

### 5.1 Approved behavior and routing gates (decision log)

Source: `<workspace-root>\papyr-rebuild-decisions.md` (verbatim quotes and line ranges in `_evidence-decisions.md` §2).

| Decision | Source lines | Routing relevance (exact text) |
|---|---|---|
| DEC-011 | 133-144 | Hybrid browser-first; "Routing must be based on measured capabilities and explicit rules rather than hidden arbitrary behavior"; Merge/Split/JPG-to-PDF browser-first candidates; Compress and demanding PDF-to-JPG may need server or fallback; exact limits left open pending research. |
| DEC-015 | 185-200 | Conservative device-aware limits: desktop 100 MB / 500 pages; capable non-iOS mobile 50 MB / 200 pages; iPhone/iPad 25 MB / 100 pages; PDF-to-JPG 200 pages desktop / 50 pages mobile, sequential rendering, 16-megapixel per-page ceiling; JPG-to-PDF 50 images / 100 MP desktop, 40 MP mobile; Compress server-default. "Routing must also evaluate decoded image dimensions, page geometry, encryption, file corruption, estimated peak memory, and browser capabilities rather than relying only on file size." Product safety limits, not browser hard limits; raiseable only after telemetry and real-device testing. |
| DEC-030 | 378-389 | Automatic server fallback for corrupt, encrypted, unsupported, or unsafe-for-browser files; transition visible; passwords never logged; server fallback subject to limits, abuse controls, queue capacity, security validation, one-hour deletion; clear failure if server cannot recover. |
| DEC-031 | 391-401 | Support latest two major versions of Chrome, Edge, Firefox, Safari on desktop, current Safari on iOS/iPadOS, Chrome on Android; progressive enhancement and ordinary file-input/download fallbacks required where Chromium-specific file APIs are unavailable; unsupported browsers get a clear compatibility message or server path. |
| DEC-065 | 799-809 | After safe browser failure, automatically transition the same job to server processing without a second confirmation, only for classified recoverable failures; no retry loops, duplicate jobs, duplicate downloads, or repeated uploads; security-policy failures, unsupported content, invalid passwords, user cancellation, retention violations, and unsafe conditions fail closed. |

Supporting: DEC-032 (local results only for the active tab session), DEC-036/DEC-064 (passwords requested only when encryption detected, memory-only handling), DEC-090/DEC-092 (sanitization and untrusted-input rendering), DEC-093 (byte-level image validation), DEC-165 (browser-specific safety limits remain frontend capability logic, clearly distinguished from server limits; arch §14.1 line 673), DEC-066 (no benchmark program).

### 5.2 Specification requirements

Source: `audit-outputs/research/track-b/_evidence-specs.md` §3.5 (arch §10), §3.3 (arch §4.3), §3.8 (arch §14.1, §22.4), §2.2 (UX §16.3), §2.4 (UX §18).

- Arch §10.2 (lines 470-479): the DEC-015 limits verbatim, plus "Routing must also evaluate decoded image dimensions, page geometry, encryption, file corruption, estimated peak memory, and browser capabilities rather than relying only on file size (DEC-015). These are product safety limits, not browser hard limits."
- Arch §10.3 (lines 481-488): fallback classes per DEC-030 and DEC-065, including the fail-closed list.
- Arch §10.4 (lines 490-492): disclosure obligations; workflow states label uploading, queued, and server processing truthfully.
- Arch §10.5 (lines 494-496): backend-outage behavior; tool pages stay accessible, browser-capable operations continue locally, no redirect to status page.
- Arch §4.3 (lines 221-227): client components perform browser processing, upload, polling, and result presentation; browser processing runs within DEC-015 limits; "The frontend owns browser-specific capability logic and limits, which must be clearly distinguished from server limits in the capability contract (DEC-165)".
- Arch §22.4 (lines 953-958): supported matrix per DEC-031; automated tests where feasible plus representative real-device testing, especially iOS; unsupported browsers receive a clear compatibility message or server path; progressive enhancement and ordinary file-input/download fallbacks where Chromium-specific APIs are unavailable.
- UX §16.3 (lines 578-582): mirrors the arch matrix statement.
- UX §18 items 4 and 5 (lines 603-604): routing transparency and retry semantics; fallback transitions visible, no indefinite retry loops.

### 5.3 Web and primary-source evidence

Source: `audit-outputs/research/track-b/_evidence-b1-web.md` (all sources accessed 2026-07-31). Section references below are to that evidence file.

**Browser memory ceilings (evidence §2, §5):**

- Chrome/V8: hard per-isolate heap cap of ~4 GB (v8-isolate.h `maximum_heap_size_in_bytes`; V8 blog "One small step for Chrome, one giant heap for V8", `https://v8.dev/blog/heap-size-limit`; chromium-dev thread `https://groups.google.com/a/chromium.org/g/chromium-dev/c/IKZvzuBP9QE`); renderer process capped near ~16 GiB; wasm memory cap 4 GiB; "Even on 64-bit OS, we impose deliberate 2GB limits in each renderer process" (engineer quotes in the thread). GC pauses scale with heap size; "all script execution is paused" during collections (developer.chrome.com/docs/devtools/memory-problems).
- Safari/WebKit: macOS WebContent kill thresholds ~7 GB (RAM <= 16 GB) or ~15 GB (RAM > 16 GB) plus 1 GB per tab (WebKit changeset 295192); iOS Safari subject to OS Jetsam per-process limits with the warning at 80% of the critical threshold (WebKit PR #28244); observed iOS ceilings 1-3 GB per tab (supporting: Apple Developer Forums thread 761666, EmulatorJS issue #1220).
- Firefox: no fixed per-tab cap; memory-pressure-driven tab unloading (firefox-source-docs.mozilla.org/browser/tabunloader/); >1 GB private bytes marks a content process deprecated (bug 1305091); 2025 runaway reports of 1-4 GB processes (bug 1986440).
- Cross-browser measurement: no programmatic GC in JS (MDN memory management); `performance.measureUserAgentSpecificMemory()` is Chromium-only and implementation-defined, explicitly "results cannot be compared across browsers" (web.dev, "Monitor your web page's total memory usage").

**Detectability of memory (evidence §7):**

- `navigator.deviceMemory` is Chromium-only (Chrome 63; Firefox `false`, Safari `false` in BCD), secure-context only, and deliberately coarse: rounded to the nearest power of two and clamped (2, 4, 8, 16, 32 GiB) to curtail fingerprinting (MDN; W3C Device Memory API Working Draft, 30 March 2026, `https://www.w3.org/TR/device-memory/`). Conclusion recorded in the evidence: memory quantity cannot be detected reliably cross-browser; memory pressure can only be inferred from side effects.

**Capability support matrices (evidence §1):**

- Universally available in the DEC-031 matrix: Web Workers (96.93% usage), IndexedDB (96.68%), File API (96.68%), WebGL 1 (96.92%), Pointer Events (95.04%), ResizeObserver (94.30%), CSS custom properties (95.83%), native `<dialog>` (96.09%), WebAssembly MVP (95.13%; stable since 2017: Chrome 57, Firefox 52, Safari 11, Edge 16).
- Tiered: OffscreenCanvas full 2D+WebGL from Chrome 69 / Firefox 105 / Safari 17 (93.33% + 0.50% partial; Safari 16.2 partial = 2D only), WebGL 2 from Chrome 56 / Firefox 51 / Safari 15 (94.67%), SharedArrayBuffer/wasm threads require cross-origin isolation (COOP/COEP) in practice (caniuse notes; 94.10% threads), wasm GC Chrome 119 / Firefox 120 / Safari 18.2 per BCD (caniuse stale for Safari, conflict recorded in evidence §9.1).
- File System Access API is not tracked by caniuse and is not Baseline: handle APIs Chrome 86 / Firefox 111 / Safari 15.2; `showOpenFilePicker` is Chromium-only (Firefox/Safari `false` in BCD); `FileSystemWritableFileStream` in Safari only from 26; OPFS Chrome 86 / Firefox 111 / Safari 15.2 (evidence §1.2-1.3). The caniuse `filesystem` key is the legacy, unmaintained FileWriter API and must not be used for routing decisions.

**Client-side PDF libraries (evidence §4):**

- pdf-lib 1.17.1 (npm, published 2021-11-06): pure JavaScript, no WebAssembly; custom font embedding requires the separate `@pdf-lib/fontkit` module.
- jsPDF 4.2.1 (npm, published 2026-03-17): pure JavaScript (`fflate` compression), no WebAssembly.
- pdf.js pdfjs-dist 6.2.108 (npm, 2026-07-28); documented memory controls in `src/display/api.js`: `rangeChunkSize` default 65536 bytes, `maxImageSize` (default -1, i.e. no limit), `canvasMaxAreaInBytes`, `useWasm` default true; FAQ documents the canvas math: a letter page at 96 DPI is 816x1056 px and needs 3.4 MB per page at 1x, 14 MB at 2x (2x2 = 4 factor for HiDPI), "multiply that by e.g., 2x2 = 4 if it's a HiDPI display"; "Our recommendation is to create and render only visible pages." Base64 conversion "uses more memory"; "delivering raw PDF data as typed array in first place" is recommended. The modern build assumes native support for latest JS features and may depend on OffscreenCanvas/ImageDecoder/WebAssembly; a `legacy` build exists (floor roughly Chrome 125 / Firefox ESR / Safari 18 per the wiki FAQ).

**Progressive enhancement and graceful degradation (evidence §6):**

- MDN glossary definitions; the canonical detect-then-dynamically-import pattern from web.dev ("Building for modern browsers and progressively enhancing like it's 2003", `https://web.dev/articles/progressively-enhance-your-pwa`): "I only load the file when the API is actually supported... I never make the user pay the download cost for a feature that their browser doesn't support."
- MDN feature detection: member checks, element-property checks, `CSS.supports`/`@supports`, `matchMedia`; "don't confuse feature detection with browser sniffing... this is a terrible practice".
- The W3C Device Memory API spec embeds the fallback decision pattern in its normative example: "The web application should consider how to handle browsers that do not support the API: either by enabling by default, or disabling by default."

### 5.4 Legacy baseline evidence (read-only, `papyr-reference/`)

Source: `audit-outputs/research/track-b/_evidence-legacy-frontend.md` (§12.5, §13.1, §7).

- Legacy client-side tools (merge, split, rotate, sign) used pdf-lib via `lib/pdfUtils.ts` with no API call (`_evidence-legacy-frontend.md` §12.5); PDF previews and PDF-to-JPG rendering used pdfjs-dist (`PDFPageViewer.tsx` lazy `await import('pdfjs-dist')`).
- Legacy upload config: `frontend/src/lib/config.ts:24-38` set `maxUploadBytes` 20 MB, `fileRetentionMinutes` 60, allowed PDF MIME `application/pdf`, allowed images `image/jpeg`, `image/png`, `image/webp` (evidence §12.3).
- Legacy image-to-pdf hybrid threshold: 3 MB, `frontend/src/app/image-to-pdf/page.tsx:43` (cited by arch spec §11.5 line 553; the rebuild replaces it with DEC-015 limits and capability-based routing).
- Legacy had no capability detection: upload zones are `role="button"` + `tabIndex={0}` + hidden `input[type=file]` (evidence §13.1, PDFUploader.tsx:356-378), i.e., the ordinary file-input pattern that satisfies DEC-031's fallback requirement.
- Legacy PDFUploader error/retry precedent: first failure auto-retries after 1 s, second shows error (PDFUploader.tsx:226-238); 429 response surfaces "Terlalu banyak permintaan" (line 270).

## 6. Alternatives

### Alternative A - File-size and page-count-only thresholds (legacy-style)

- **What it is**: route decisions keyed only on total input bytes and page count, as the legacy 20 MB / 3 MB hybrid thresholds did.
- **Trade-offs**: simplest to implement and explain; ignores decoded image dimensions, page geometry, encryption, corruption, and estimated peak memory, all of which DEC-015 explicitly requires routing to evaluate. A small compressed PDF can expand massively in memory (DEC-015 rationale: "PDF memory use can greatly exceed compressed file size"); a 20 MB PDF with 4k-per-page images can exceed the ~4 GB V8 isolate on desktop and far exceed the 1-3 GB iOS ceiling.
- **Risks**: iOS tab reloads and OOM crashes on files that pass a byte-count check; incorrect local/server disclosure. Privacy impact: more jobs misrouted to server than necessary. Cost/operational impact: unnecessary server load.
- **Verdict**: fails the approved routing-signal requirement; used only as the baseline contrast.

### Alternative B - Layered routing: device-class caps + file-characteristic evaluation + capability feature detection (recommended)

- **What it is**: three layers evaluated in a single deterministic routing decision per job:
  1. Device-class caps from DEC-015 (desktop / capable non-iOS mobile / iPhone+iPad), applied to total input bytes, page counts, image counts, and megapixel ceilings.
  2. File-characteristic evaluation: decoded image dimensions and pixel counts (from file bytes, per DEC-093), page geometry, encryption detection (PDF trailer `/Encrypt`), corruption detection (parse result), and estimated peak memory from the documented engine characteristics (canvas math, decoded-image expansion).
  3. Capability feature detection: probe OffscreenCanvas (2D and WebGL), Web Workers, IndexedDB, WebAssembly, canvas area limits; keep the ordinary `input[type=file]` baseline path working in every supported browser per DEC-031; dynamically load enhanced modules only when the probes pass (web.dev pattern, evidence §6.4).
  After a safe, classified browser failure, the same job transitions once to server processing (DEC-065); fail-closed classes never upload (DEC-065).
- **Trade-offs**: more upfront design and unit-test surface than Alternative A; requires a routing decision module that is pure and testable; the device-class tier still relies on coarse platform signals (touch capability, iOS platform hints) because precise memory is not measurable cross-browser (evidence §7).
- **Risks**: low-RAM desktop and iPadOS Safari variance under the desktop caps; managed via conservative caps, sequential rendering for PDF-to-JPG, and the DEC-065 single-transition fallback, then telemetry-based adjustments per DEC-015.
- **Cost/operational impact**: moderate; the routing logic is frontend capability logic clearly separated from the server capability contract (DEC-165, arch §14.1 line 673).
- **Privacy/security**: keeps more jobs on-device (privacy-positive), never calls `navigator.geolocation` (DEC-085), never reads device memory into analytics (DEC-025 prohibits fingerprinting; `deviceMemory` is deliberately excluded), and respects the fail-closed security classes (DEC-065).

### Alternative C - Dynamic limits driven by `navigator.deviceMemory`

- **What it is**: scale caps continuously from the reported device memory.
- **Trade-offs**: only Chromium reports it (evidence §7.2), so Firefox/Safari would need a fixed fallback anyway; values are coarse powers of two designed to prevent fingerprinting, not precise budgeting; and the API's own spec embeds a "enable or disable by default" pattern rather than continuous scaling.
- **Risks**: inconsistent limits across the DEC-031 matrix; a privacy-negative signal added to analytics risk.
- **Verdict**: rejected. The DEC-015 class caps already encode device-aware conservatism without a non-portable API.

### Alternative D - Always-server processing (no local path)

- **What it is**: drop browser processing entirely.
- **Trade-offs**: simplest reliability story; violates DEC-011 (browser-first hybrid), raises VPS cost and latency, and weakens the on-device privacy promise that the accepted model and legacy copy rely on.
- **Verdict**: rejected; not a viable reading of the approved decisions.

## 7. Recommendation

Recommendation only, not an accepted decision (DEC-054, DEC-057): adopt **Alternative B** with the following routing table and rules.

### 7.1 Per-tool routing table

| Tool | Primary path | Browser-first caps (DEC-015) | Additional routing signals evaluated | Fallback behavior |
|---|---|---|---|---|
| Compress PDF | Server-default (DEC-015) | None at launch; no local path | n/a (server by default per DEC-015, DEC-014) | Server failure returns a clear actionable failure (DEC-030) |
| Merge PDF | Browser-first | Desktop 100 MB / 500 pages; capable mobile 50 MB / 200 pages; iPhone/iPad 25 MB / 100 pages | Encryption (per-file password flow, DEC-064/DEC-074, or server route), corruption, estimated peak memory from per-page rendering cost, active-content detection (sanitization on server per DEC-090) | Recoverable decode failure transitions once to server (DEC-065); invalid passwords, security-policy failures fail closed |
| Split PDF | Browser-first | Same as Merge | Encryption, corruption, page-count parse, overlapping/order semantics need no extra routing | Same as Merge |
| JPG to PDF | Browser-first | 50 images / 100 MP desktop; 40 MP capable mobile; iPhone/iPad within the 25 MB / 100-page class caps | Per-image byte validation and decoded dimensions/pixel count/frame count/EXIF orientation per DEC-093 and DEC-187 (JPG/JPEG, PNG, WebP); estimated decode expansion | Invalid or threat-classified images blocked (DEC-088, DEC-093); safe decode failures fall back once (DEC-065) |
| PDF to JPG | Browser-first | 200 pages desktop / 50 pages mobile; 16-megapixel per-page ceiling; sequential page rendering (DEC-015) | Encryption, corruption, page geometry, canvas area (canvasMaxAreaInBytes / maxImageSize limits per evidence §4.3), white-compositing requirement (DEC-081) | Same as Merge; rendering must never execute active content (DEC-092) |

### 7.2 Routing rules

1. **Signals, not size alone**: every job evaluates decoded image dimensions, page geometry, encryption, corruption, estimated peak memory, and browser capabilities in addition to byte size (DEC-015 consequence; arch §10.2 line 479).
2. **No `navigator.deviceMemory`**: no routing decision depends on it (evidence §7); the DEC-015 class caps are the memory-aware layer.
3. **Device class**: coarse, privacy-safe classification (desktop / capable non-iOS mobile / iPhone+iPad) per DEC-015 tiers; capability probes (touch/pointer, platform hints, canvas limits) inform it; this is not browser sniffing, which MDN and the W3C documentation discourage, and it must be implemented as feature detection plus documented class caps.
4. **Baseline path**: the ordinary `input[type=file]` upload and download path works in every supported browser (DEC-031); the File System Access API is not required (Chromium-only per evidence §1.2-1.3) and legacy precedent already uses plain file inputs (evidence §5.4).
5. **Enhanced path**: OffscreenCanvas/WebAssembly-backed rendering modules load dynamically only when the relevant probes pass (evidence §6.4); otherwise the job uses the baseline path or routes to server.
6. **Single transition**: fallback to server happens at most once per job, only for classified recoverable failures; no retry loops, duplicate jobs, or repeated uploads (DEC-065). Security-policy failures, unsupported content, invalid passwords, user cancellation, retention violations, and unsafe conditions fail closed (DEC-065).
7. **Transparency**: the local/server state and the transition reason stay visible in status messaging (DEC-030, DEC-065; arch §10.4; UX §18 item 4); workflow states label uploading, queued, and server processing truthfully (DEC-168).
8. **Unsupported browsers**: a clear compatibility message or the server-processing path, never silent failure (DEC-031).
9. **Contract separation**: browser-specific safety limits remain frontend capability logic, clearly distinguished from server limits in the machine-readable capability contract (DEC-165, arch §14.1 line 673).
10. **Adjustment procedure**: caps are conservative design/safety choices; they change only through the documented raising procedure after anonymous reliability telemetry and representative real-device testing, never from a benchmark program (DEC-015, DEC-066).

## 8. Measurable acceptance criteria

Functional and operational verification criteria, with no benchmark wording (DEC-066):

1. **Deterministic routing function**: a pure, unit-tested function `route(tool, deviceClass, fileSignals, capabilities)` returns `local | server | blocked` for every combination, and every branch is traceable to DEC-015's listed signals (bytes, decoded dimensions, page geometry, encryption, corruption, estimated peak memory, browser capabilities).
2. **No non-portable signals**: the routing code contains no reference to `navigator.deviceMemory`, no geolocation call (DEC-085), and no fingerprinting collection (DEC-025).
3. **Caps enforced**: the DEC-015 limits hold per class in tests (100/50/25 MB; 500/200/100 pages; 200/50 PDF-to-JPG pages; 16 MP per page; 50/40 MP JPG-to-PDF; 50 images).
4. **Encryption and corruption**: encrypted input triggers the password flow or a server route; corrupt input routes to server once or fails clearly when the server cannot recover (DEC-030, DEC-036, DEC-064); wrong-password errors are distinct from corrupt-file errors (DEC-036).
5. **Single-transition property**: a test proves that a simulated recoverable failure produces exactly one server transition and never a retry loop, duplicate job, or duplicate download (DEC-065).
6. **Fail-closed classes**: security-policy failures, unsupported content, invalid passwords, user cancellation, retention violations, and unsafe conditions never upload (DEC-065).
7. **Baseline path**: the file-input path completes a local job in each supported browser class of the DEC-031 matrix; enhanced modules are absent from the bundle for browsers that fail their probes (evidence §6.4 pattern).
8. **Transparency**: UI state distinguishes local from server processing and shows the transition reason (arch §10.4; UX §18 item 4), and the Privacy page accurately describes browser processing, automatic server fallback, and one-hour retention (DEC-168).
9. **Unsupported-browser path**: browsers outside the matrix receive the compatibility message or the server path (DEC-031).
10. **Contract boundary**: browser limits and server limits are expressed in distinct, labeled fields of the capability contract (DEC-165).
11. **Backend-outage behavior**: browser-capable operations still work and server-dependent jobs show temporary unavailability without redirecting to the status page (DEC-163; arch §10.5).
12. **No benchmarks**: the routing design contains no comparative quality/performance study, corpus, matrix, or score program (DEC-066).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Low-RAM desktops**: the desktop caps (100 MB / 500 pages) can still be large relative to a 4-8 GB Windows laptop alongside the OS and other tabs; the V8 isolate is capped near 4 GB but a multi-hundred-MB PDF plus worker copies plus canvases approaches it. The conservative caps plus the single-transition fallback absorb this, and telemetry will confirm (DEC-015).
2. **iPadOS Safari**: the evidence distinguishes iPhone/iPad at 25 MB / 100 pages (DEC-015), but practical iPadOS Jetsam behavior is less documented than iOS; treat iPadOS with the iPhone/iPad class caps until real-device testing (DEC-031).
3. **caniuse vs BCD conflict on Safari wasm GC**: caniuse reports not supported, BCD reports Safari 18.2 (evidence §9.1). The brief uses BCD for Safari 18.2+ but notes caniuse's global-usage figure is depressed by stale data. Routing does not depend on wasm GC.
4. **Chromium issue 41133247** is sign-in gated; only the title was verifiable (evidence §9.9). The Google Groups thread remains the authoritative quote source.
5. **Firefox has no fixed per-tab cap**; memory-pressure unloading and 2025 runaway reports (bug 1986440) mean large local jobs on Firefox should remain conservative (evidence §2.3).
6. **pdf.js legacy build floor**: the FAQ documents roughly Chrome 125 / Firefox ESR / Safari 18 for the legacy build (evidence §3.2); the rebuild's supported matrix is newer (DEC-031), so the modern build is usable, but this must be re-confirmed at implementation against the pinned pdf.js version.
7. **pdf-lib is unmaintained** (2021-era); the merge/split browser path inherits this. Design-time security review and a fallback plan are required (also flagged in Track A A1 §9).
8. **Routing-signal accuracy**: page count and encryption are read from PDF structure; corruption is a parse result. These are documented capabilities of pdf.js/pdf-lib, not measured here (DEC-066); functional fixtures verify them at implementation.
9. **Material owner questions**: (a) whether the desktop caps may be lowered initially for safer real-device behavior, or kept at DEC-015's values with telemetry; (b) whether iPadOS should share the iPhone/iPad tier (recommended) or the mobile tier; (c) confirmation that Compress remains server-only at launch with no local path (DEC-015 states server-default; this brief reads it as no local Compress path).
10. **Adjustment data**: caps may be raised only after anonymous reliability telemetry and representative real-device testing demonstrate acceptable failure rates (DEC-015); the telemetry design belongs to Track D3/D5 boundaries, not this brief.

## 10. Dependencies and cross-track interfaces

- **A2-A6 (tool research)**: consume the engine memory/canvas characteristics this brief relies on (pdf-lib pure JS, pdf.js canvas math and `maxImageSize`/`canvasMaxAreaInBytes`, 16-MP ceiling, white compositing) and cite them (plan §6.2, §7.1; A1 §10).
- **C2 (per-tool server limits, Wave 2)**: the browser caps are the local side; C2 defines server-side limits and the capability contract fields (DEC-034, DEC-165). This brief's routing rules end where server validation begins.
- **C4/D5 (hardening and threat handling)**: the fail-closed routing classes (DEC-065) feed the threat classification register; JPG-to-PDF byte validation and decode isolation come from DEC-093 (Track A5 and D5).
- **B2 (accessibility)**: routing transparency, status announcements, and error/fallback messaging must be accessible (DEC-062); the browser routing states feed B2's progress/status coverage.
- **B3 (i18n/paper policy)**: the browser-side JPG-to-PDF path must display the selected paper standard before conversion (DEC-083, DEC-085); the routing decision must not hide that disclosure.
- **B4 (SEO/URL)**: fallback and processing states have no URL impact (results stay on one page, DEC-153); no routing interaction with locale-less redirects is introduced.
- **Arch §22.4 / UX §16.3**: the routing facts in this brief define what the browser/device test matrix must verify at implementation.
- **X1/X2 (index/reconciliation)**: this brief contributes the routing threshold table and the owner questions in §9.9 to the decision-prompt list (plan §14).

## 11. Source-date log and evidence-completeness notes

- All web sources accessed 2026-07-31; versions and page dates recorded inline in `_evidence-b1-web.md` (V8 heap-size-limit 2017-02-09; v8-isolate.h HEAD; WebKit changeset 295192 2022-06-02; WebKit PR #28244 2024-05-07; W3C Device Memory API Working Draft 2026-03-30; pdfjs-dist 6.2.108 published 2026-07-28; pdf-lib 1.17.1 published 2021-11-06; jsPDF 4.2.1 published 2026-03-17; caniuse data reflecting Chrome 153 / Firefox 155 / Safari 26.x era).
- Legacy evidence read 2026-07-31; all paths under `papyr-reference/`; line references cited in §5.4.
- Completeness notes: (a) the primary evidence file `_evidence-b1-web.md` is the authoritative source for every web claim in this brief; secondary items are explicitly marked there (e.g., Stack Overflow max-memory thread, Apple Developer Forums, EmulatorJS issue, Lapcat blog) and were not promoted to primary here; (b) `performance.measureUserAgentSpecificMemory()` is Chromium-only and explicitly non-comparable across browsers, so no cross-browser memory measurement exists (evidence §2.4.1); (c) no benchmark or test-run evidence was created (DEC-066).
- Uncertainties from §9 are not resolved in this brief; they are recorded for the owner and for reconciliation (X2).

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066).
- No installs, builds, server starts, VPS/SSH access, deployment, account creation, browser execution, or authenticated/mutating remote actions were performed (plan §4.1).
- No product code, scaffolding, or infrastructure was created or modified; no decision log or specification was edited; no evidence file, audit file, or `papyr-reference/` file was modified.
- `papyr-reference/` was read-only; verified unchanged via `git -C papyr-reference status --porcelain` (empty output, exit 0) before and after this task.
- No claim is made that any browser or device is "safe" beyond the documented engineering facts; all limits remain conservative design/safety choices (DEC-015, DEC-066).
- Findings in this brief are recommendations, not accepted decisions (DEC-054, DEC-057).
