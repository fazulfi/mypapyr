# Track B — Deliverable B1: Browser Capability Detection and Routing Thresholds — Web Evidence File

- **Access date for all sources in this file**: 2026-07-31 (unless a source explicitly states otherwise).
- **Research date**: 2026-07-31 (all sources verified as reachable on this date).
- **Purpose**: Primary-source evidence for Papyr rebuild decisions about (a) which client-side capabilities a browser must have, (b) per-browser memory ceilings, and (c) detection + fallback routing patterns.
- **Method**: Read-only, anonymous fetches of caniuse.com data files, MDN browser-compat-data (BCD), W3C/WHATWG specs, vendor docs (V8, Chromium, WebKit, Firefox Source Docs, web.dev/developer.chrome.com), and official project repositories (mozilla/pdf.js, Hopding/pdf-lib, parallax/jsPDF, npm registry). No installs, no builds, no browser execution, no authenticated access.
- **Evidence standard**: Primary sources only. Secondary sources are explicitly marked "(supporting)". No numbers are fabricated; where a source does not state a number, that is said explicitly.
- **Machine-readable data used**:
  - caniuse feature data: `https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/<key>.json` (this is the data behind `https://caniuse.com`; the site's "Global usage" percentages come from `usage_perc_y` / `usage_perc_a` in these files). Latest versions present in the data: Chrome 153, Edge 150, Firefox 155, Safari 26.x/27/TP, iOS Safari 26.5 — indicating the data is current as of mid-2026.
  - MDN Browser Compat Data (BCD): `https://raw.githubusercontent.com/mdn/browser-compat-data/main/...` (the machine-readable source of the MDN browser-compat tables). Note: in many BCD files the iOS Safari column is `"mirror"` (i.e., inherits the desktop Safari value); explicit iOS numbers are taken from caniuse (`ios_saf`).
- **Status-code legend (caniuse)**: `y` = supported, `a` = partial, `n` = not supported, `x` = requires prefix, `d` = disabled by default (flag), `#n` = see feature note.

---

## 1. Capability support matrices (research question 1)

### 1.1 First-supporting-version table (caniuse data files, accessed 2026-07-31)

"First y" = earliest browser version where the feature is supported (`y`); "partial" = earliest version with partial support (`a`); "usage %" = `usage_perc_y` (global-usage share of browsers supporting the feature) with `usage_perc_a` (partial) where nonzero.

| Capability (caniuse key) | Chrome | Edge | Firefox | Safari (macOS) | iOS Safari | caniuse global usage |
|---|---|---|---|---|---|---|
| WebAssembly (`wasm`) | 57 | 16 | 52 | 11 | 11.0–11.2 | 95.13 % (0 % partial) |
| Wasm bulk memory (`wasm-bulk-memory`) | 75 | 79 | 79 | 15 | 15.0–15.1 | 94.08 % |
| Wasm GC (`wasm-gc`) | 119 | 119 | 120 | **not supported** (TP = n) | **not supported** (26.5 = n) | 73.47 % |
| Wasm threads/atomics (`wasm-threads`) | 74 | 79 | 79 | 14.1 | 14.5–14.8 | 94.10 % |
| SharedArrayBuffer (`sharedarraybuffer`) | 68 (91+ requires cross-origin isolation) | 79 | 79 (requires COOP/COEP) | 15.2–15.3 (requires isolation) | 15.2–15.3 (requires isolation) | 93.97 % |
| Web Workers (`webworkers`) | 4 | 12 | 3.5 | 4 | 5.0–5.1 | 96.93 % |
| IndexedDB (`indexeddb`) | 23 (11 partial, prefixed) | 79 (12 partial) | 10 (4 partial, prefixed) | 10 (7.1 partial) | 10.0–10.2 (8 partial) | 96.68 % y + 0.25 % a |
| File API (`fileapi`) | 38 (6 partial) | 79 (12 partial) | 28 (3.6 partial) | 10 (5.1 partial) | 10.0–10.2 (6.0–6.1 partial) | 96.68 % y + 0.25 % a |
| File System Access API (modern) | — see 1.3 (caniuse does not track it) | — | — | — | — | — |
| OffscreenCanvas (`offscreencanvas`) | 69 | 79 | 105 | 17.0 (16.2 partial, 2D only) | 17.0 (16.2 partial, 2D only) | 93.33 % y + 0.50 % a |
| WebGL 1 (`webgl`) | 8 | 12 | 4 | 5.1 | 8 | 96.92 % |
| WebGL 2 (`webgl2`) | 56 | 79 | 51 | 15 | 15.0–15.1 | 94.67 % |
| WebGPU (`webgpu`) | 113 (not Linux-by-default; see notes) | 113 | 141 partial, disabled by default (flag) | 26.0 partial (flag; macOS 26 Tahoe+ default) | 26.0 | 82.17 % y + 2.83 % a |
| ResizeObserver (`resizeobserver`) | 64 | 79 | 69 | 13.1 | 13.4–13.7 | 94.30 % |
| Pointer Events (`pointer`) | 55 | 12 | 59 | 13 | 13.2 (13.0–13.1 partial) | 95.04 % |
| CSS Custom Properties (`css-variables`) | 49 | 16 (15 partial) | 31 | 10 (9.1 partial) | 10.0–10.2 (9.3 partial) | 95.83 % |
| Native `<dialog>` (`dialog`) | 37 | 79 | 98 | 15.4 | 15.4 | 96.09 % |
| navigator.deviceMemory | not in caniuse (feature key `mdn-api_navigator_devicememory` returns HTTP 404; see section 7) | — | — | — | — | — |

Source for every row: caniuse feature JSON (title, `stats`, `usage_perc_y`, `usage_perc_a`, `notes_by_num`) at `https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/<key>.json`, mirrored at `https://caniuse.com/<key>`; accessed 2026-07-31. Key caniuse notes that change the meaning of the numbers:

- **SharedArrayBuffer** — note #1: "Has support, but was disabled across browsers in January 2018 due to Spectre & Meltdown vulnerabilities." Note #3: "Requires cross-origin isolation by having Cross-Origin-Embedder-Policy (COEP) and Cross-Origin-Opener-Policy (COOP) headers set."
- **WebGPU** — note #1: Firefox flag `dom.webgpu.enabled`; note #2: Safari "WebGPU" feature flag; note #5: Chrome 113 not enabled on Linux by default; note #6: Firefox only enabled by default on Windows; note #7: Safari partial = only enabled by default on macOS 26 Tahoe or later; note #8: Firefox also only default on Windows / macOS 26 Tahoe on Apple Silicon; note #9: Chrome Linux support depends on hardware/drivers.
- **OffscreenCanvas** — note #3: Safari partial = 2D contexts only, not WebGL.
- **Pointer Events** — note #5/#6: iOS 13.0–13.1 partial = `releasePointerCapture` bug and wrong `buttons` value on touch.
- **IndexedDB** — note #2: Safari 7.1–9.3 partial = "seriously buggy behavior"; note #3: Safari 14.1.1 bug.
- **File API** — spec status `ls` (living standard); partial rows reflect prefixed/partial early implementations.

### 1.2 First-supporting-version table (MDN browser-compat-data, accessed 2026-07-31)

Source: `https://raw.githubusercontent.com/mdn/browser-compat-data/main/...` (BCD = the data that renders MDN "Browser compatibility" tables). `-` means the column mirrors another browser in BCD or the entry is absent.

| Feature (BCD path) | Chrome | Edge | Firefox | Safari | iOS Safari (BCD) |
|---|---|---|---|---|---|
| WebAssembly JS API (`webassembly/api.json` → `webassembly.api`) | 57 | 16 | 52 | 11 | mirror |
| Wasm threads & atomics (`webassembly/threads-and-atomics.json`) | 74 | — | 79 | 15.2 | mirror |
| Wasm bulk memory (`webassembly/bulk-memory-operations.json`) | 75 | — | 78 | 15.1 | mirror |
| Wasm GC (`webassembly/garbage-collection.json`) | 119 | — | 120 | 18.2 | mirror |
| Wasm SIMD (`webassembly/fixed-width-SIMD.json`) | 91 | — | 89 | 16.4 | mirror |
| SharedArrayBuffer (`javascript/builtins/SharedArrayBuffer.json`) | 68 | — | 79 | 15.2 | mirror |
| Atomics (`javascript/builtins/Atomics.json`) | 68 | — | 78 | 15.2 | mirror |
| Worker constructor (`api/Worker.json`) | 2 | 12 | 3.5 | 4 | 5 |
| WorkerGlobalScope (`api/WorkerGlobalScope.json`) | 4 | 12 | 3.5 | 4 | 5 |
| IDBFactory (`api/IDBFactory.json`) | 24 (23–57 prefixed, removed) | 12 | 16 (10–16) | 8 | — |
| File (`api/File.json`) | 13 | 12 | 7 (3–7) | 4 | — |
| Blob (`api/Blob.json`) | 5 | 12 | 4 | 6 | — |
| FileSystemHandle (`api/FileSystemHandle.json`) | 86 | — | 111 | 15.2 | — |
| FileSystemFileHandle (`api/FileSystemFileHandle.json`) | 86 | — | 111 | 15.2 | — |
| FileSystemDirectoryHandle (`api/FileSystemDirectoryHandle.json`) | 86 | — | 111 | 15.2 | — |
| FileSystemWritableFileStream (`api/FileSystemWritableFileStream.json`) | 86 | — | 111 | **26** | — |
| Window.showOpenFilePicker (`api/Window.json`) | 86 | — | **false** | **false** | — |
| StorageManager.getDirectory = OPFS (`api/StorageManager.json`) | 86 | — | 111 | 15.2 | — |
| OffscreenCanvas (`api/OffscreenCanvas.json`) | 69 | — | 105 | 16.4 | — |
| WebGLRenderingContext (`api/WebGLRenderingContext.json`) | 9 | 12 | 4 | 5.1 | 8 |
| WebGL2RenderingContext (`api/WebGL2RenderingContext.json`) | 56 | — | 51 | 15 | — |
| GPU (`api/GPU.json`) | 144 full (113–144 partial) | — | 141 partial | 26 | — |
| GPUAdapter (`api/GPUAdapter.json`) | 144 full (113–144 partial) | — | 141 partial | 26 | — |
| ResizeObserver (`api/ResizeObserver.json`) | 64 | — | 69 | 13.1 | — |
| PointerEvent (`api/PointerEvent.json`) | 55 | 12 | 59 | 13 | — |
| CSS custom properties (`css/properties/custom-property.json`) | 49 | 15 | 31 | 9.1 | — |
| `<dialog>` (`html/elements/dialog.json`) | 37 | — | 98 | 15.4 | — |
| Navigator.deviceMemory (`api/Navigator.json`) | 63 | — | **false** | **false** | — |

BCD `status` fields observed: every feature above except `Window.showOpenFilePicker` (`experimental: true`) and `GPU`/`GPUAdapter` (standard track, Chrome partial-history) is on the standard track, non-deprecated, non-experimental.

### 1.3 File System Access API — detailed note

- caniuse **does not** track the modern File System Access API. The caniuse feature key `filesystem` is the **legacy "Filesystem & FileWriter API"** (`https://caniuse.com/filesystem`; spec `https://www.w3.org/TR/file-system-api/`), which is Chrome-only (first `y` Chrome 13, prefixed), unsupported in Firefox/Safari/iOS, at 78.08 % global usage, and whose own caniuse note says: "The File API: Directories and System specification is no longer being maintained and support may be dropped in future versions." It is **not** a synonym for File System Access API.
- The modern File System Access API support matrix must therefore be read from MDN BCD (1.2): handle-based APIs in Chrome 86+, Firefox 111+, Safari 15.2+; `showOpenFilePicker` is Chromium-only (Firefox/Safari = `false` in BCD); `FileSystemWritableFileStream` in Safari only from 26; OPFS (`navigator.storage.getDirectory()`) in Chrome 86, Firefox 111, Safari 15.2.
- Cross-check on the corresponding MDN pages: `https://developer.mozilla.org/en-US/docs/Web/API/File_System_Access_API` (accessed 2026-07-31) — "Limited availability" (not Baseline) for the File System Access API as a whole; per-interface tables per 1.2.

---

## 2. Browser tab memory limits and practical per-tab ceilings (research question 2)

### 2.1 Chrome / Chromium (64-bit)

1. **V8 heap hard limit** — V8 blog, "One small step for Chrome, one giant heap for V8", published 09 February 2017: `https://v8.dev/blog/heap-size-limit` (accessed 2026-07-31). Quotes: "V8 has a hard limit on its heap size. This serves as a safeguard against applications with memory leaks. When an application reaches this hard limit, V8 does a series of last resort garbage collections. If the garbage collections do not help to free memory V8 stops execution and reports an out-of-memory failure." Embedders can raise it via `set_max_old_generation_size_in_bytes` (ResourceConstraints API), but "garbage collection pauses may increase with larger heaps."
2. **Official per-process limits list (64-bit)** — chromium-dev mailing list thread "Maximum amount of consumable memory per tab", started 2017-11-15, replies through 2020-09-22: `https://groups.google.com/a/chromium.org/g/chromium-dev/c/IKZvzuBP9QE` (accessed 2026-07-31; full thread text read). Chromium engineer Alex Gough (Sep 22, 2020): "FWIW these are the current limits for 64bit … Renderer: Per-process (Job, Rlimit) ~ 16 GiB (less if less system memory); V8 Isolate 4GB (reservation); V8 code range 128 MiB; Wasm Memory 4 GiB kSpecMaxWasmMaximumMemoryPages; Wasm Code Size 2 GiB kMaxWasmCodeMemory; Single partition_alloc allocation INT_MAX; Per-slab allocation limit from allocator shims: 2 GiB." Other engineer quotes in the same thread: "Even on 64-bit OS, we impose deliberate 2GB limits in each renderer process -- V8, Blink memory allocator etc. Basically you can't lift those limits." (Yuta Kitamura, 2019-01-21); "It's just been an implicit 2 GB limit for so long … it also acts as a protection against runaway sites" (Daniel Bratell, 2019-01-24); the often-quoted "We limit to 4Gb because certain types of attacks rely on being able to allocate > 4Gb of memory" appears in the original question (quoting prior commentary) and is consistent with the 4 GB V8 isolate reservation.
3. **V8 source documentation** — `https://chromium.googlesource.com/v8/v8.git/+/HEAD/include/v8-isolate.h` (accessed 2026-07-31): `maximum_heap_size_in_bytes` is "The hard limit for the heap size. When the heap size approaches this limit, V8 will perform series of garbage collections and invoke the NearHeapLimitCallback. If the garbage collections do not help and the callback does not increase the limit, then V8 will crash with V8::FatalProcessOutOfMemory." Also: "with pointer compression enabled, total heap usage of isolates in a group cannot exceed 4 GB, not counting array buffers and other off-heap storage."
4. **Practical ceiling statement** — Stack Overflow "Max memory usage of a chrome process (tab)..." (2013, updated through ~2023) documents that V8 defaults to ~512 MB (32-bit) / ~1.4 GB (64-bit) old-space historically and that `--max_old_space_size` is capped at 4096 on 64-bit, and that modern Chrome renders `--max_old_space_size` ineffective for tabs: `https://stackoverflow.com/questions/17491022/max-memory-usage-of-a-chrome-process-tab-how-do-i-increase-it` (accessed 2026-07-31) — **(supporting, not primary; primary numbers are items 1–3)**.
5. Corroborating issue (title only, content sign-in gated): Chromium issue "Limit of 4 GB per tab in 64 bit Chrome?" `https://issues.chromium.org/41133247` (accessed 2026-07-31; page requires sign-in to read comments — cited for existence, not quoted).

**Bottom line (Chrome)**: the practical addressable JS heap in a 64-bit Chrome tab is ~4 GB (V8 isolate reservation; pointer-compressed heap ≤ 4 GB), with the whole renderer process capped near ~16 GiB and a 4 GiB wasm memory cap (2.4). Multi-hundred-MB working sets are therefore feasible on desktop but the practical ceiling is ~4 GB per isolate.

### 2.2 Safari / WebKit

1. **macOS foreground WebContent kill threshold** — WebKit Changeset 295192, "Enforce foreground WebContent memory limit on macOS" (bug 240397), timestamp Jun 2, 2022: `https://trac.webkit.org/changeset/295192/webkit` (accessed 2026-07-31). Message: "We removed the foreground memory limit for WebContent on macOS in r272046. … This patch adds a foreground memory limit of 8GB or 16GB depending on RAM size. This matches the limits set by other browsers for their content process." Code:
   ```cpp
   static size_t thresholdForMemoryKillOfActiveProcess(unsigned tabCount) {
     size_t baseThreshold = ramSize() > 16 * GB ? 15 * GB : 7 * GB;
     return baseThreshold + tabCount * GB;
   }
   ```
   i.e., macOS Safari kills an active WebContent process at ~7 GB (≤16 GB RAM machine) or ~15 GB (>16 GB RAM), plus 1 GB per tab.
2. **iOS memory limits (Jetsam)** — WebKit PR #28244 "Trigger GC when crossing warning threshold on iOS" (2024-05-07): `https://github.com/WebKit/WebKit/pull/28244` (accessed 2026-07-31). Quote: "On iOS where we have fairly strict memory limits, sometimes the mutator can get far ahead of the GC. We might wait until a PROC_LIMIT_CRITICAL event fires before a full GC occurs, at which point the process is already eligible to be killed by the OS. … let's also trigger a full GC … when a PROC_LIMIT_WARNING event fires (which is 80% of the critical threshold)." This is the official confirmation that iOS Safari's WebContent process is subject to OS (Jetsam) per-process memory limits and that the warning fires at 80 % of the critical kill threshold.
3. **Observed iOS ceilings (supporting)** — Apple Developer Forums thread 761666 (Oct 2024): `https://developer.apple.com/forums/thread/761666` (accessed 2026-07-31): Safari on iPhone 12 Pro allowed ≈1.5 GB (page reload above that), iPhone 15 Pro / 15 Pro Max consistently ≈3 GB before reload. Also EmulatorJS issue #1220 (iOS 17): WebContent killed by Jetsam `per-process-limit` typically 1.0–1.5 GB on modern iPhones: `https://github.com/EmulatorJS/EmulatorJS/issues/1220` (accessed 2026-07-31) — both are **(supporting)**, but they consistently place iOS practical ceilings around 1–3 GB per tab.
4. Lapcat Software blog (2026-01-22) — iOS 26.2 crash observations at ~100 MB (iPhone SE 3) / ~200 MB (iPad 8) and a 64 MB `runtime.sendMessage()` extension limit: `https://lapcatsoftware.com/articles/2026/1/7.html` (accessed 2026-07-31) — **(supporting, secondary)**.

### 2.3 Firefox

1. **No fixed per-tab heap cap; memory-pressure system** — Firefox Source Docs, "Tab Unloading": `https://firefox-source-docs.mozilla.org/browser/tabunloader/` (accessed 2026-07-31): "Tab Unloading is a feature that automatically unloads tabs to prevent Firefox from crashing due to insufficient memory when the system's available memory is low." Two parts: "memory pressure detector and tab unloader"; unload order is least-recently-used; disable via `browser.tabs.unloadOnLowMemory`. So Firefox's ceiling is system-memory-driven rather than a fixed per-tab cap.
2. **Deprecated-process heuristic (>1 GB private bytes)** — Firefox bug 1305091 "Stop using content processes when they are using 'too much' memory": `https://bugzilla.mozilla.org/show_bug.cgi?id=1305091` (accessed 2026-07-31): "on any system (32-bit/64-bit) >1G private bytes" marks a content process as deprecated (no new tabs assigned).
3. **Real-world runaway reports (supporting)** — Firefox bug 1986440 (2025): "Since Firefox 142.0, JS-heavy sites cause runaway content processes that hoard gigabytes of RAM … A single content process rapidly grows beyond 1–2 GB resident RAM, sometimes exceeding 3–4 GB" (improved in 143.x): `https://bugzilla.mozilla.org/show_bug.cgi?id=1986440` (accessed 2026-07-31).
4. Firefox Source Docs, "about:memory": `https://firefox-source-docs.mozilla.org/performance/memory/about_colon_memory.html` (accessed 2026-07-31) — per-process memory reporting; "resident" is the key metric.

### 2.4 Cross-browser measurement APIs

1. **web.dev, "Monitor your web page's total memory usage with performance.measureUserAgentSpecificMemory()"** (published 2020-04-13): `https://web.dev/articles/monitor-total-page-memory-usage` (accessed 2026-07-31). "Currently the API is supported only in Chromium-based browsers, starting in Chrome 89." "The result of the API is highly implementation dependent … results cannot be compared across browsers." The value "includes JavaScript and DOM memory of all iframes, related windows, and web workers in the current process."
2. **Chrome DevTools, "Fix memory problems"** (updated 2024-11-06): `https://developer.chrome.com/docs/devtools/memory-problems` (accessed 2026-07-31). Garbage collection: "the browser reclaims memory. The browser decides when this happens. During collections, all script execution is paused."
3. **MDN, "Memory management"**: `https://developer.mozilla.org/en-US/docs/Web/JavaScript/Memory_management` (accessed 2026-07-31): "It is also not possible to programmatically trigger garbage collection in JavaScript — and will likely never be within the core language"; "This configuration may not be available in browsers" (referring to engine memory flags).

---

## 3. PDF.js (research question 3)

### 3.1 Repository and current version

- Repo: `https://github.com/mozilla/pdf.js` (accessed 2026-07-31). README (fetched from `https://raw.githubusercontent.com/mozilla/pdf.js/master/README.md`, accessed 2026-07-31): "PDF.js is a Portable Document Format (PDF) viewer that is built with HTML5." "PDF.js is built into version 19+ of Firefox."
- Latest GitHub release (GitHub Releases API `https://api.github.com/repos/mozilla/pdf.js/releases/latest`, accessed 2026-07-31): **v6.1.200**, published **2026-06-27** (assets: `pdfjs-6.1.200-dist.zip`, `pdfjs-6.1.200-legacy-dist.zip`). Release notes include "[api-minor] Bump library version to 6.1" (PR #21499).
- Latest npm build (npm registry `https://registry.npmjs.org/pdfjs-dist/latest`, accessed 2026-07-31): **pdfjs-dist 6.2.108**, published **2026-07-28**; description "Generic build of Mozilla's PDF.js library."; `engines: node >=22.13.0 || >=24`.

### 3.2 Minimum supported browsers (documented)

- There is **no `SUPPORTED_BROWSERS` file** in the repo. Support is documented in the README and the wiki FAQ.
- README (master, accessed 2026-07-31): "Please note that the 'Modern browsers' version assumes native support for the latest JavaScript features"; two demo builds are published: Modern browsers `https://mozilla.github.io/pdf.js/web/viewer.html` and Older browsers `https://mozilla.github.io/pdf.js/legacy/web/viewer.html`. Build command `npx gulp generic` vs `npx gulp generic-legacy` ("If you need to support older browsers, run: npx gulp generic-legacy").
- Wiki FAQ "Which browsers/environments are supported?" (`https://raw.githubusercontent.com/wiki/mozilla/pdf.js/Frequently-Asked-Questions.md`, accessed 2026-07-31): "By default we produce a non-translated/non-polyfilled build, intended for *the latest* browsers. However, we also provide a translated/polyfilled build for older browsers in a separate bundle (with a `legacy` suffix). The objective is to support all HTML5 compliant browsers…"
  - **Modern build**: Firefox (Yes), Chrome (Yes) — latest versions implied.
  - **`legacy` build**: Firefox ESR+ (Yes); Chrome 125+ (Yes); Opera (Yes); Edge (Yes, "Only the Chromium-based version"); Safari 18+ ("Mostly … Some missing features/defects have been reported, but no problems in general"); Node.js 22+ ("Mostly … Limited").
  - So as of 2026-07-31, the documented floor for the legacy build is roughly Chrome 125 / Firefox ESR / Safari 18, and the modern build targets latest Firefox/Chrome.
- FAQ also documents: range-request behavior ("PDF.js may automatically start using HTTP Range Requests to fetch not-yet-loaded portions of a PDF … a document can be rendered without fully loading it", depending on server `Range` header support); base64 memory warning ("The base64 conversion operation uses more memory, so we recommend delivering raw PDF data as typed array in first place").

### 3.3 Documented memory behavior / limits for large PDFs

1. FAQ "I want to render all 100 pages in a document at a high resolution. Is it a good idea?" — "Not really… a letter page size is 816⨉1056px at 96DPI … so you will need a canvas that takes up 816⨉1056⨉4 = 3,446,784 bytes (don't forget to multiply that by e.g., 2⨉2 = 4 if it's a HiDPI display). This requires you to allocate 3.5Mb (or 14Mb) per page… The demo viewer creates, renders, and holds canvases only for visible pages to reduce the amount of used memory. Our recommendation is to create and render only visible pages."
2. `getDocument()` memory-related options, from the JSDoc in `src/display/api.js` (fetched `https://raw.githubusercontent.com/mozilla/pdf.js/master/src/display/api.js`, accessed 2026-07-31):
   - `rangeChunkSize` — "Specify maximum number of bytes fetched per range request. The default value is 65536 (= 2^16)." (JSDoc L129; default confirmed in code: `: 2 ** 16`).
   - `disableAutoFetch` (L199), `disableStream` (L196), `disableRange` — control chunked fetching of the PDF.
   - `maxImageSize` (L164) — "The maximum allowed image size in total pixels, i.e. width * height. Images above this value will not be rendered. Use -1 for no limit, which is also the default value."
   - `canvasMaxAreaInBytes` — "The integer value is used to know when an image must be resized (uses OffscreenCanvas in the worker)."
   - `isOffscreenCanvasSupported` / `isImageDecoderSupported` / `useWasm` (default `true`; "Attempt to use WebAssembly in order to improve e.g. image decoding performance") — the modern build is explicitly allowed to depend on OffscreenCanvas/ImageDecoder/WebAssembly.
   - Transfer note (L119–121 and L607–610): "NOTE: If TypedArrays are used they will generally be transferred to the worker-thread. This will help reduce main-thread memory usage, however it will take ownership of the TypedArrays."
3. No fixed numeric "max PDF size" is documented anywhere in the README/FAQ; the documented constraints are the per-canvas math above plus the chunked/range-fetching model.

---

## 4. Client-side PDF generation/manipulation libraries (research question 4)

### 4.1 pdf-lib

- Repo README: `https://raw.githubusercontent.com/Hopding/pdf-lib/master/README.md` and homepage `https://pdf-lib.js.org` (accessed 2026-07-31): "Create and modify PDF documents in any JavaScript environment." "Designed to work in any modern JavaScript runtime. Tested in Node, Browser, Deno, and React Native environments." UMD builds "have been compiled to ES5, so they should work in any modern browser".
- npm (`https://registry.npmjs.org/pdf-lib/latest`, accessed 2026-07-31): **1.17.1, published 2021-11-06** (84 versions total). Dependencies: `pako`, `tslib`, `@pdf-lib/upng`, `@pdf-lib/standard-fonts` — **pure JavaScript; no WebAssembly, no native addons, no polyfill requirement documented**.
- Font embedding requires the optional sister module `@pdf-lib/fontkit` (npm latest **1.1.1, published 2020-11-28**; description "An advanced font engine for Node and the browser"; dependency `pako` only — again pure JS). README: "You must add the `@pdf-lib/fontkit` module to your project and register it using `pdfDoc.registerFontkit(...)` before embedding custom fonts" — it is not included by default ("it increases bundle size").
- The README lists no WebAssembly anywhere; PDF operations (create/modify/forms/embed fonts) run on plain JS + TypedArrays.

### 4.2 jsPDF

- Repo README: `https://raw.githubusercontent.com/parallax/jsPDF/master/README.md` (accessed 2026-07-31): "A library to generate PDFs in JavaScript." Distribution: `jspdf.es.*.js` (ES2015 modules), `jspdf.node.*.js` (Node), `jspdf.umd.*.js`, and `polyfills*.js` — "Required polyfills for older browsers like Internet Explorer. The es variant simply imports all required polyfills from `core-js`, the umd variant is self-contained."
- Polyfill section: "jsPDF requires modern browser APIs in order to function. To use jsPDF in older browsers like Internet Explorer, polyfills are required. You can load all required polyfills as follows: `import "jspdf/dist/polyfills.es.js"`."
- npm (`https://registry.npmjs.org/jspdf/latest`, accessed 2026-07-31): **4.2.1, published 2026-03-17**. Dependencies: `fflate` (pure-JS compression), `fast-png`, `@babel/runtime` — **no WebAssembly**.
- Optional runtime dependencies: `html2canvas`, `canvg`, `dompurify` (loaded dynamically only for the `html()` method); README documents them as webpack `externals`.
- License header states copyright 2010–2025 James Hall / yWorks.

---

## 5. Why multi-hundred-MB files are problematic client-side (research question 5)

Primary mechanics, each with a source:

1. **Every byte of a loaded file occupies live heap/process memory.** A PDF opened client-side exists as an `ArrayBuffer`/`Uint8Array`; PDF.js additionally transfers typed arrays to its worker (see 3.3.2), and rendering produces canvas bitmaps at ~4 bytes/pixel × devicePixelRatio² (see 3.3.1). Memory is not "streamed to disk" by default in the JS model.
2. **V8 enforces a hard per-isolate heap cap (~4 GB) and OOMs when GC cannot reclaim** — V8 blog heap-size-limit (2.1.1), v8-isolate.h (2.1.3), chromium-dev thread (2.1.2). Worker threads are separate isolates with the same cap; `performance.measureUserAgentSpecificMemory()` counts workers (2.4.1).
3. **GC pauses scale with heap size** — V8 blog heap-size-limit: "some phases in the garbage collector have a linear dependency on the heap size. Garbage collection pauses may increase with larger heaps." (2.1.1); DevTools memory-problems: during collections "all script execution is paused" (2.4.2).
4. **Mobile OS kills are far below the desktop caps.** iOS Safari WebContent is Jetsam-killed at ~1–3 GB (2.2.2, 2.2.3); Android/iOS also reload the tab. This is why multi-hundred-MB in-memory documents crash or reload on phones long before any V8 limit is reached.
5. **Firefox has no fixed per-tab cap but unloads tabs under memory pressure** (2.3.1) and treats >1 GB private-bytes processes as unhealthy (2.3.2).
6. **There is no cross-browser way to observe or force memory state** — no programmatic GC in JS; `measureUserAgentSpecificMemory()` is Chromium-only and implementation-defined (2.4.1, 2.4.3).
7. V8 blog "4GB wasm memory" (2020, Chrome M83; `https://v8.dev/blog/4gb-wasm-memory`, accessed 2026-07-31) — for wasm-based processing the addressable memory cap is 4 GiB (wasm32) and memory growth beyond 2 GB requires opt-in (`emcc -s ALLOW_MEMORY_GROWTH -s MAXIMUM_MEMORY=4GB`); the post explicitly recommends "gracefully handle the case of a malloc() failure" and warns "2-4GB is a lot of memory … there just won't be enough free memory on many users' machines."
8. V8 blog "Trash talk: the Orinoco garbage collector" (2019-01-03; `https://v8.dev/blog/trash-talk`, accessed 2026-07-31) and "Orinoco: young generation garbage collection" (2017-11-29; `https://v8.dev/blog/orinoco-parallel-scavenger`, accessed 2026-07-31) — document that GC pauses are the main reason large live sets cause jank; Orinoco (parallel/concurrent/idle GC) reduces but does not remove pauses.

**Net**: practical client-side ceilings are ≈4 GB (Chrome/V8 isolate), ≈7–15 GB (macOS Safari process kill), ≈1–3 GB (iOS), memory-pressure-based (Firefox). A multi-hundred-MB document is *possible* on desktop but consumes a large fraction of the ceiling once PDF data + worker copies + canvas bitmaps + fonts/images are summed, and it is *not* viable on mobile — hence routing/limits are needed, not a single "everything works" path.

---

## 6. Progressive enhancement and graceful degradation standards (research question 6)

1. **MDN Glossary — Progressive enhancement** (`https://developer.mozilla.org/en-US/docs/Glossary/Progressive_Enhancement`, last modified Jul 18, 2025; accessed 2026-07-31): "**Progressive enhancement** is a design philosophy that provides a baseline of essential content and functionality to as many users as possible, while delivering the best possible experience only to users of the most modern browsers that can run all the required code." "Feature detection is generally used to determine whether browsers can handle more modern functionality, while polyfills are often used to add missing features with JavaScript."
2. **MDN Glossary — Graceful degradation** (`https://developer.mozilla.org/en-US/docs/Glossary/Graceful_degradation`, last modified Jul 11, 2025; accessed 2026-07-31): "**Graceful degradation** is a design philosophy that centers around trying to build a modern website/application that will work in the newest browsers, but falls back to an experience that while not as good still delivers essential content and functionality in older browsers." "Polyfills can be used to build in missing features with JavaScript, but acceptable alternatives to features like styling and layout should be provided where possible, for example by using the CSS cascade, or HTML fallback behavior."
3. **MDN — Implementing feature detection** (`https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Testing/Feature_detection`, accessed 2026-07-31): "The idea behind feature detection is that you can run a test to determine whether a feature is supported in the current browser, and then conditionally run code to provide an acceptable experience both in browsers that *do* support the feature, and browsers that *don't*." Documented patterns:
   - member check: `if ("geolocation" in navigator) { … } else { /* fallback */ }`;
   - element-property check: `!!document.createElement("canvas").getContext`;
   - CSS: `CSS.supports(...)` and the `@supports` at-rule (preferred for CSS features; supports `AND`/`OR`/`NOT`);
   - `window.matchMedia(...)` for media-query tests;
   - note: "some features are, however, known to be undetectable. In these cases, you'll need to use a different approach, such as using a polyfill"; and "don't confuse feature detection with **browser sniffing** … this is a terrible practice".
4. **web.dev — "Building for modern browsers and progressively enhancing like it's 2003"** (published June 29, 2020): `https://web.dev/articles/progressively-enhance-your-pwa` (accessed 2026-07-31). This is the canonical worked example of the **detect → dynamically import an enhanced module, else load a legacy module** routing pattern. For the File System Access API it loads different import/export modules:
   ```js
   const loadImportAndExport = () => {
     if ('chooseFileSystemEntries' in window) {
       Promise.all([import('./import_image.mjs'), import('./export_image.mjs')]);
     } else {
       Promise.all([import('./import_image_legacy.mjs'), import('./export_image_legacy.mjs')]);
     }
   };
   ```
   and the general pattern stated for every capability (share, clipboard, badges, wake lock, …): "I only load the file when the API is actually supported… I never make the user pay the download cost for a feature that their browser doesn't support." Closing: "By applying progressive enhancement when building my app, I make sure that everybody gets a good, solid baseline experience, but that people using browsers that support more Web platform APIs get an even better experience."
5. **W3C Wiki — "Graceful degradation versus progressive enhancement"** (`https://www.w3.org/wiki/Graceful_degradation_versus_progressive_enhancement`, accessed 2026-07-31): "Progressive enhancement … Starting with a baseline of usable functionality, then increasing the richness of the user experience step by step by testing for support for enhancements before applying them."
6. **W3C Device Memory API spec** (see section 7) even embeds the fallback decision pattern in its normative example: "The web application should consider how to handle browsers that do not support the API: either by enabling by default, or disabling by default."
7. Supporting/secondary history: A List Apart, "Understanding Progressive Enhancement" (2008-10-07, `https://alistapart.com/article/understandingprogressiveenhancement/`); Resilient Web Design ch.5 (Jeremy Keith, `https://resilientwebdesign.com/chapter5/`).

**Standard pattern distilled for routing decisions**: build a baseline path that works everywhere (no optional capability required); probe each optional capability via feature detection (`'x' in obj`, `createElement` checks, `CSS.supports`/`@supports`, `matchMedia`); route to the enhanced path only when the probe passes, loading enhanced code dynamically so non-supporting browsers never pay for it; keep a graceful fallback (message + alternative action) for every capability.

---

## 7. Detectability of available memory (research question 7)

1. **`navigator.deviceMemory` status** — MDN, "Navigator: deviceMemory property" (`https://developer.mozilla.org/en-US/docs/Web/API/Navigator/deviceMemory`, last modified Jan 26, 2026; accessed 2026-07-31): "Limited availability. This feature is not Baseline because it does not work in some of the most widely-used browsers." "The reported value is imprecise to curtail fingerprinting. It's approximated by rounding the actual memory to the nearest power of 2, then dividing that number by 1024. It is then clamped within lower and upper bounds…" (e.g. `2, 4, 8, 16, 32` GiB). Secure context only. Related header: `Sec-CH-Device-Memory`.
2. **BCD support** (`api/Navigator.json` → `Navigator.deviceMemory`, accessed 2026-07-31): Chrome 63; Firefox `false`; Safari `false` (Edge mirrors Chrome). i.e., **Chromium-only**.
3. **Spec status** — W3C "Device Memory API", **W3C Working Draft, 30 March 2026** (published by the Web Performance Working Group on the Recommendation track; NOT a Recommendation as of access date): `https://www.w3.org/TR/device-memory/` (accessed 2026-07-31). Editors: Barry Pollard (Google), Guohui Deng (Microsoft). The draft defines both the `Sec-CH-Device-Memory` client hint and `navigator.deviceMemory`, with an exact coarsening algorithm (round to nearest power of two; clamp to implementation-defined bounds). Privacy section: "To reduce fingerprinting risk, the reported value is rounded to a single significant bit, as opposed to reporting the exact value."
4. **caniuse**: no `deviceMemory` feature exists in caniuse (feature key `mdn-api_navigator_devicememory` returns 404).
5. **Why precise device memory is unavailable cross-browser**: (a) the only implementation is Chromium (BCD above); (b) the spec itself mandates coarse, clamped values specifically to prevent fingerprinting (W3C §5); (c) other engines have not shipped it. Therefore memory *quantity* cannot be detected reliably; memory *pressure* can only be inferred from side-effects (tab reloads on iOS, OOM crashes, `performance.measureUserAgentSpecificMemory()` in Chromium-only — 2.4.1).

---

## 8. WebAssembly browser support thresholds as of 2026-07-31 (research question 8)

- **Stable since** (caniuse `wasm` and BCD `webassembly.api`, accessed 2026-07-31):
  - Chrome **57** (2017) — caniuse first `y` = 57; BCD `added=57`.
  - Firefox **52** (2017) — caniuse first `y` = 52 with note #4 "Disabled for Firefox 52 ESR"; BCD `added=52`.
  - Safari **11** (2017) — caniuse first `y` = 11; BCD `added=11`; iOS Safari 11.0–11.2.
  - Edge **16** (2017, EdgeHTML) — caniuse first `y` = 16; BCD `added=16`; Chromium Edge 79+ inherits Chrome support.
- **Global usage**: caniuse `usage_perc_y = 95.13` %, `usage_perc_a = 0` % (accessed 2026-07-31). Note: caniuse's global usage reflects the share of global web users on browsers with support; the number does not appear on the raw JSON with a date, so it should be quoted as "as of 2026-07-31 data" only.
- **Feature-level support** (wasm beyond MVP): bulk memory Chrome 75+/FF 79+/Safari 15+ (94.08 %); threads/atomics Chrome 74+/FF 79+/Safari 14.1+ (94.10 %); SIMD Chrome 91+/FF 89+/Safari 16.4+ (BCD); GC Chrome 119+/FF 120+/Safari 18.2 (BCD) — see conflicts in section 9.
- **webassembly.org roadmap** (`https://webassembly.org/roadmap/`, accessed 2026-07-31): "In November 2017, WebAssembly CG members representing four browsers, Chrome, Edge, Firefox, and WebKit, reached consensus that the design of the initial (MVP) WebAssembly API and binary format is complete…" The page's support table is JS-rendered ("Loading table, please wait…"); the page points to the `wasm-feature-detect` library for runtime detection. For per-version numbers the caniuse/BCD tables in sections 1.1–1.2 are the primary source.
- **Conclusion**: Wasm is effectively ubiquitous for MVP (95 %+ global usage; all five requested browsers at stable versions well above the 2017 thresholds). Threads require cross-origin isolation in practice (SharedArrayBuffer gating, caniuse note #3), and GC support is the newest addition — unusable in current Safari per caniuse but present per BCD (see 9.1).

---

## 9. Conflicts, discrepancies, and outdated data observed

1. **Wasm GC in Safari** — caniuse `wasm-gc`: Safari/iOS Safari = not supported (`n`, TP = n; usage 73.47 %); MDN BCD `webassembly/garbage-collection.json`: Safari `added=18.2`. The two primary sources disagree. BCD's 18.2 matches WebKit's release timeline for wasm GC (Safari 18.2, Dec 2024); caniuse appears stale for Safari here. Flag for the team: treat Safari 18.2+ as supporting wasm GC (BCD), but note caniuse's global-usage % (73.47 %) is depressed by the caniuse data state.
2. **Wasm threads in Safari** — caniuse `wasm-threads`: Safari 14.1; BCD `threads-and-atomics`: Safari 15.2. Minor discrepancy; both are 2021-era releases.
3. **Wasm bulk memory in Firefox** — caniuse: 79; BCD: 78. Minor discrepancy.
4. **OffscreenCanvas in Safari** — caniuse: 17.0 full (16.2 partial 2D-only); BCD: 16.4. Minor discrepancy.
5. **Web Workers in Chrome** — caniuse `webworkers`: 4; BCD `Worker` constructor: 2. Both true at different granularity (Worker API vs constructor landing); irrelevant for routing (both ancient).
6. **IndexedDB in Chrome** — caniuse: 23 (11 partial prefixed); BCD: 24 with 23–57 prefixed then unprefixed. Consistent enough; prefixed era only matters for < 2015 browsers.
7. **caniuse `filesystem` is the legacy API, not File System Access API** — see 1.3. Do not use `https://caniuse.com/filesystem` to decide File System Access routing.
8. **caniuse global-usage percentages have no publish date in the data files** — they are the site's monthly-updated figures; quote with "accessed 2026-07-31" only.
9. **Chromium issue 41133247 and Google Groups thread**: the issue page is sign-in gated (only the title "Limit of 4 GB per tab in 64 bit Chrome?" was verifiable); the Google Groups thread was fully readable and is the authoritative quote source.
10. **Firefox**: no fixed per-tab ceiling is documented anywhere in Firefox Source Docs; memory behavior is pressure-driven (2.3). Bug 1986440 shows real-world >1–3 GB runaway processes in 2025.

---

## 10. Verification evidence

- Output file: `<workspace-root>\audit-outputs\research\track-b\_evidence-b1-web.md` — created 2026-07-31; non-empty; no placeholder tokens (all numbers above come from fetched sources listed inline).
- Every capability in research question 1 has a support table with source URLs and access dates (sections 1.1, 1.2, 1.3).
- Every section cites URL + access date; page-level version/date information is stated where the source exposes it (e.g., "last modified Jul 28, 2026" for MDN WebAssembly, "published 09 February 2017" for the V8 heap-size-limit post, "W3C Working Draft 30 March 2026" for Device Memory API, "v6.1.200 published 2026-06-27" for pdf.js, npm publish dates for pdf-lib/jspdf/pdfjs-dist).
- Primary-source inventory (all accessed 2026-07-31):
  - caniuse feature JSON files (17 features): `https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/<key>.json`
  - MDN BCD: `https://raw.githubusercontent.com/mdn/browser-compat-data/main/{webassembly,api,javascript/builtins,css/properties,html/elements}/...`
  - MDN pages: WebAssembly; Navigator.deviceMemory; Memory management; Glossary/Progressive_Enhancement; Glossary/Graceful_degradation; Learn_web_development/Extensions/Testing/Feature_detection
  - V8: `https://v8.dev/blog/heap-size-limit`; `https://v8.dev/blog/4gb-wasm-memory`; `https://v8.dev/blog/trash-talk`; `https://v8.dev/blog/orinoco-parallel-scavenger`; `https://chromium.googlesource.com/v8/v8.git/+/HEAD/include/v8-isolate.h`
  - Chromium: `https://groups.google.com/a/chromium.org/g/chromium-dev/c/IKZvzuBP9QE`; `https://issues.chromium.org/41133247` (title only)
  - WebKit: `https://trac.webkit.org/changeset/295192/webkit`; `https://github.com/WebKit/WebKit/pull/28244`
  - Mozilla/Firefox: `https://firefox-source-docs.mozilla.org/browser/tabunloader/`; `https://firefox-source-docs.mozilla.org/performance/memory/about_colon_memory.html`; `https://bugzilla.mozilla.org/show_bug.cgi?id=1305091`; `https://bugzilla.mozilla.org/show_bug.cgi?id=1986440`
  - web.dev / developer.chrome.com: `https://web.dev/articles/monitor-total-page-memory-usage`; `https://web.dev/articles/progressively-enhance-your-pwa`; `https://developer.chrome.com/docs/devtools/memory-problems`
  - W3C: `https://www.w3.org/TR/device-memory/`; `https://www.w3.org/wiki/Graceful_degradation_versus_progressive_enhancement`
  - Repos/packages: `https://github.com/mozilla/pdf.js` (README, wiki FAQ, `src/display/api.js`, Releases API), `https://registry.npmjs.org/{pdfjs-dist,pdf-lib,jspdf,@pdf-lib/fontkit}/latest`, `https://github.com/Hopding/pdf-lib` (README), `https://github.com/parallax/jsPDF` (README), `https://webassembly.org/roadmap/`
