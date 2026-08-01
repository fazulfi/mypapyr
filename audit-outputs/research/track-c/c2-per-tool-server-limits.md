# C2 — Per-Tool Server Limits Research Brief

## 1. Header

- **Brief ID**: C2
- **Path**: `<workspace-root>\audit-outputs\research\track-c\c2-per-tool-server-limits.md`
- **Track**: C — Infrastructure and operations
- **Title**: Per-tool server safety/design limits
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (executor subagent, Track C Wave 2 follow-up)
- **Status**: Complete (draft for owner review under DEC-057; no accepted product decision)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (§6.3 deliverable C2, Wave 2; §7.3 Track C questions; §8 brief template; §11 verification assertions)
- **Governing decisions**: DEC-034 (per-tool server limits), DEC-035 (bounded queueing), DEC-066 (limits are design/safety choices, not benchmark results), DEC-070 (one-hour absolute deadline from upload receipt), DEC-165 (machine-readable capability and limits contract); supporting: DEC-013, DEC-015, DEC-020, DEC-024, DEC-036, DEC-037, DEC-038, DEC-054 to DEC-060, DEC-064, DEC-067, DEC-073, DEC-076, DEC-077, DEC-078, DEC-088, DEC-090, DEC-093, DEC-137, DEC-167, DEC-169, DEC-174, DEC-186, DEC-187, DEC-188
- **Spec sections served**: Technical Architecture Specification §9, §10.2, §11, §13, §14, §25.3 item 2 (and items 3, 4, 9 interfaces); Product and UX Design Specification §12, §13, §21.1
- **Template note**: The plan §8 lists 12 numbered sections. Following the A1 precedent (A1 §1 "Template note"), the header sub-fields above are expanded as their own labeled fields; combined with the 12 numbered sections this satisfies both the plan's template and the "16-section" instruction in the C2 task (header sub-fields counted individually).

**Files read (complete list)**

- `<workspace-root>\AGENTS.md`
- `<workspace-root>\papyr-rebuild-decisions.md` (in full; DEC-034, DEC-035, DEC-066, DEC-070, DEC-165 govern this brief)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (in full; §9, §10.2, §11, §13, §14, §25.3)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (in full; §12, §13, §21)
- `<workspace-root>\audit-outputs\research-program-plan.md` (§6.3, §7.3, §8, §10, §11)
- Track A briefs (all six, in full): `audit-outputs/research/track-a/a1-shared-engine-licenses.md`, `a2-compress-pdf.md`, `a3-merge-pdf.md`, `a4-split-pdf.md`, `a5-jpg-to-pdf.md`, `a6-pdf-to-jpg.md`
- Track C briefs: `audit-outputs/research/track-c/c1-queue-workers-redis.md` (in full), `c3-r2-lifecycle.md` (in full), `c4-vps-processing-hardening.md` (in full), `c5-observability-status-telegram.md` (relevant sections), `c6-backups-restores.md` (relevant sections)
- Track B evidence (browser-capability context): `audit-outputs/research/track-b/_evidence-b1-web.md` (in full)
- Legacy (read-only): `papyr-reference/backend/utils/config.py`, `backend/utils/pdf_validator.py`, `backend/routers/compress.py`, `backend/services/compress_service.py`, `backend/routers/image_to_pdf.py`, `backend/routers/pdf_to_image.py`, `backend/services/pdf_to_image_service.py`, `backend/services/async_task.py`, `deploy/docker-compose.yml`, `frontend/src/lib/config.ts`

---

## 2. Scope

This brief resolves the **server-side input and processing limits for each of the five MVP tools** — Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG — as conservative design and safety defaults, per DEC-034 and DEC-066. It is the Wave 2 follow-up that consumes the Track A tool briefs (A2-A6) for per-tool engine resource and output-expansion characteristics and the C1 queue/worker brief for worker bounds and queue caps.

The user problem served: each operation has a different CPU, memory, disk, rendering, archive-output, and worst-case complexity profile, so a single universal file-size/page-count ceiling would be either unsafe for expensive tools or unnecessarily restrictive for simpler ones (DEC-034). The limits must be (a) independent per tool, (b) conservative design/safety choices explicitly documented as adjustable from production observations rather than benchmark-proven (DEC-066), (c) consistent with the bounded queue (DEC-035) and the absolute one-hour server-retention deadline (DEC-070), and (d) exposed consistently to the UI and API as a machine-readable capability and limits contract (DEC-165) with machine-readable validation failures (DEC-034).

Current approved Papyr behavior this brief supports:

- Compress PDF is server-default (DEC-014, DEC-015); Merge, Split, JPG to PDF, and PDF to JPG are browser-first with automatic server fallback (DEC-011, DEC-030, DEC-065) under the DEC-015 browser limits.
- Server-side jobs run in bounded worker processes (C1: 2 worker replicas x 1 job, 2 GiB memory limit each, 180 s default per-job timeout with per-tool overrides defined in this brief) inside hardened containers (C4/DEC-169).
- Server-side source, intermediate, and result objects are deleted no later than one hour after upload receipt (DEC-013, DEC-070); jobs that cannot reasonably finish before expiry are not admitted or fail clearly (DEC-070); no deadline-prediction admission control is built (DEC-073).
- Valid jobs remain queued during normal capacity pressure, bounded by hard queue caps (DEC-035; C1: 2000 queued jobs, 15-minute maximum wait, 4 concurrent queued+processing jobs per origin).
- The versioned backend API is the canonical source for server capabilities and limits; the frontend reads the contract rather than maintaining a hardcoded copy, with conservative fallback if unavailable (DEC-165).
- Threat-classified files are blocked, never processed (DEC-088); validation inspects structure and decoded-resource risk, not extension/MIME alone (DEC-169, DEC-093).

## 3. Non-goals

- **No benchmark program or capacity measurement.** No value in this brief is a benchmark result; none was run (DEC-066). Values are conservative documented design/safety defaults.
- **No browser-limit design.** Browser capability detection and routing thresholds are Track B1's deliverable (DEC-015, DEC-030, DEC-065; arch §25.3 item 17). This brief references the accepted DEC-015 browser limits only as the conservative reference floor and keeps server limits clearly distinct in the contract (DEC-165).
- **No worker count / memory / timeout sizing.** Those are C1's conclusions; this brief consumes them and only sets per-tool limits and per-tool timeout overrides that must fit the C1 bounds.
- **No queue-cap, Redis, or fair-scheduling parameters.** C1 (DEC-035, DEC-137). This brief enforces consistency with them at admission.
- **No R2 lifecycle mechanics or result-expiry mechanics.** C3. This brief only sets result-size/ZIP-size operational bounds that C3's storage and signed-download sizing consume.
- **No Nginx rate-limit values, scanner selection, or container hardening details.** C4. This brief supplies the per-tool ceilings that drive Nginx `client_max_body_size`, tmpfs/scan size ceilings, and timeouts (C4 §10 interface).
- **No monitoring/alert thresholds.** C5. This brief states which limit-triggered telemetry must exist.
- **No decision on engine selection, sanitization mechanics, or the AGPL compliance path.** Track A briefs and the owner decision surfaced in A1 §9.
- **No changing of any value in any other brief, the decision log, the specs, or `papyr-reference/`.**

## 4. Research questions

Restated from plan §7.3 (C2) and DEC-034:

1. What independent server-side limits (bytes, pages, pixel counts, output counts, estimated memory, expected output size) are appropriate conservative design/safety defaults for each of the five tools, given each tool's documented engine resource profile from A2-A6 and the C1 worker bounds?
2. How are the limits kept consistent with the bounded queue (DEC-035), the one-hour absolute deadline (DEC-070), fair scheduling and per-origin concurrency (DEC-137, DEC-020), and the no-deadline-prediction rule (DEC-073)?
3. What exact fields should the machine-readable capability and limits contract expose per tool, how are browser limits kept distinct from server limits (DEC-165), and what machine-readable failure codes does the API return for limit violations (DEC-034)?
4. What documented procedure safely raises a limit from production observations rather than benchmarks (DEC-066, DEC-034)?
5. What measurable, non-benchmark acceptance criteria verify the limits and the contract (DEC-066)?

## 5. Evidence

### 5.1 Consumed findings (Track A and Track C briefs, all dated 2026-07-31)

| Source brief | Evidence this brief consumes |
|---|---|
| A1 §5.3 | Documented engine characteristics: Ghostscript `pdfwrite` re-interprets and re-encodes (processing time roughly proportional to page/image count; memory can spike on large embedded images; output can be larger than input for already-optimized files); pikepdf/qpdf are structure-preserving (memory approximately inputs + outputs); MuPDF/PyMuPDF pixmap memory = width x height x channels; pdf.js renders one canvas per page (no tiling); Pillow requires current versions (CVE-2026-59199 fixed in 12.3.0) and `MAX_IMAGE_PIXELS` resource limits; WebP is not a PDF native codec (must be decoded/re-encoded). |
| A2 §5.1, §5.2 | Compress: Ghostscript pdfwrite profile work is CPU-heavy (image downsampling/re-encoding); legacy invocation timeout 30 s (`compress_service.py:40`), no `-dSAFER` (gap to correct); output may exceed input (DEC-080 honesty). |
| A3 §5.1, §5.2 | Merge: pikepdf structure-preserving merge with sanitization and encryption support; legacy had no backend merge endpoint (browser-only); all-or-nothing semantics (DEC-076). |
| A4 §5.1, §5.2 | Split: pikepdf page selection; legacy range parser sorted+deduped (superseded by DEC-077/078 order-preserving, overlap-independent outputs); per-page mode subject to output-count and archive-size safety limits (DEC-038). |
| A5 §5.1, §5.2 | JPG to PDF: JPEG/PNG direct-embed is near-lossless and low-expansion; WebP must be decoded and re-encoded (output expansion risk); decode expansion dominates resource use (DEC-093); per-image fitting to Letter/A4 (DEC-041/082/083/085/089); accepted formats JPG/JPEG/PNG/WebP (DEC-187); metadata preservation incl. EXIF (DEC-084). |
| A6 §5.1, §5.2 | PDF to JPG: pixmap memory = width x height x channels (16 MP RGB = ~48 MB); sequential rendering bounds peak memory (DEC-015); server profile ~150-200 DPI capped at 16 MP per page as a design starting point; JPEG encode via Pillow; legacy rasterize timeout 60 s (`pdf_to_image_service.py:20`); duplicate-preserving, order-preserving selection (DEC-186). |
| C1 §5.1, §7 | Legacy VPS resource basis ~8 GB / 4 cores / 4.5 GB swap (`docker-compose.yml:17-24`, `runbook-vps.md:5.1`); legacy upload cap 20 MB (`config.py:101-103`); worker recommendation 2 replicas x 1 job, 2 GiB per worker, 1.5 CPU each; default per-job timeout 180 s with per-tool overrides defined in C2; queue caps 2000 queued / 15 min max wait / 4 per-origin concurrent; per-origin fairness classes; `noeviction` Redis with 384 MB cap. |
| C3 §7 | Result objects bounded in size feed R2 storage and signed-URL download sizing; expiry is authoritative from upload receipt; `expires_at` exposed on status. |
| C4 §6, §7 | Nginx `client_max_body_size` set per C2's largest per-tool upload + headroom; scan size ceilings and tmpfs caps derive from C2; ClamAV memory budget must be reconciled with the C1 worker envelope (see §9). |
| C5 §8 | Limit-triggered rejections and limit-adjacent failures are monitoring signals (rejection rates, timeout rates, OOM). |
| B1 evidence §2 | Browser ceilings (Chromium isolate ~4 GB, macOS Safari ~7-15 GB process kill, iOS ~1-3 GB) are the *browser* context; server limits are separate per DEC-165. |

### 5.2 Legacy baseline evidence (read-only, `papyr-reference/`)

| Path and line | What it evidences |
|---|---|
| `backend/utils/config.py:101-103` | Legacy universal `MAX_UPLOAD_SIZE_MB=20`, `FILE_RETENTION_MINUTES=60`, `RATE_LIMIT_PER_MINUTE=10` — the single-ceiling pattern DEC-034 supersedes. |
| `backend/utils/pdf_validator.py:34-141` | Shared PDF validation order (empty, MIME, extension, `%PDF` magic, size, page count, encrypted) — the baseline DEC-093/169 extend with decoded-resource checks. |
| `backend/routers/compress.py:36-101` | Compress validation; encrypted PDFs rejected with 400 (superseded by password flow, DEC-036/064); per-route `@limiter.limit` (per-process counters, superseded by DEC-020/C1). |
| `backend/services/compress_service.py:39-40, 89-94` | `GS_TIMEOUT_SECONDS = 30`; subprocess timeout handling — legacy per-tool timeout precedent for C2's per-tool overrides. |
| `backend/routers/image_to_pdf.py:28-36, 83-90` | Accepted image MIME/extension set (jpeg/png/webp) and the single 20 MB ceiling applied per file — the per-image byte cap DEC-034 replaces per tool. |
| `backend/routers/pdf_to_image.py:40-104` | PDF validation for PDF-to-image; 20 MB ceiling; encrypted rejected (superseded). |
| `backend/services/pdf_to_image_service.py:19-23, 154-165` | `RASTERIZE_TIMEOUT_SECONDS = 60`, `DEFAULT_DPI = 150`, `zoom = dpi / 72` — legacy rasterize timeout and profile starting points. |
| `backend/services/async_task.py:46-48, 116-186` | Legacy in-memory task store (TTL 2 h) and `asyncio.wait_for(timeout=120)` per-task timeout — the pattern C1 replaces; per-task timeout precedent. |
| `deploy/docker-compose.yml:17-24` | Legacy budget comment ("8GB RAM, 4 cores total → leave 4GB + 0.5 core for system + Nginx") and backend `cpus 3.5` / `memory 4G` limits — the envelope C2 limits must fit once split across API/Redis/workers/scanner. |
| `frontend/src/lib/config.ts:24-38` | Legacy frontend-mirrored `maxUploadBytes: 20MB`, `fileRetentionMinutes: 60` — the duplication DEC-165 removes. |

### 5.3 Documented engine/resource characteristics and derived unit math (no measurements)

The following are standard documented relationships and unit arithmetic (DEC-056 primary evidence in A1-A6), not measured capacities:

- **Pixmap memory** = width x height x channels (A6 §5.1). RGB at 3 B/px: a 16-MP page = ~48 MB; an A4 page at 150 DPI (~1240 x 1754 = 2.2 MP) = ~6.5 MB; at 200 DPI (~3.9 MP) = ~12 MB; at 300 DPI (~8.7 MP) = ~26 MB. A 100-MP decoded total in RGB = ~300 MB before engine buffers.
- **PDF-to-JPG output expansion** is the dominant cost: one JPEG per selected page; JPEG size is content-dependent (documented, not measured here); a ZIP of 200 outputs is bounded by a ZIP-size cap in this brief.
- **JPG-to-PDF expansion**: JPEG/PNG direct embed adds only container overhead (img2pdf, A5 §5.1); WebP must be decoded and re-encoded (PNG Paeth or JPEG), which can expand output (A5 §5.1, A1 §5.3); decode expansion is the resource risk, so per-image and total pixel caps bound it (DEC-093).
- **Compress expansion**: `pdfwrite` may produce output larger than input on already-optimized files (A1 §5.3, A2 §5.1) — the result-size axis is therefore an operational safety net, not a rejection prediction, and the UI reports honestly (DEC-080).
- **Merge/Split memory** is approximately inputs plus outputs for structure-preserving engines (A3/A4 §5.1), so total input bytes and page count bound it.
- **Time proportionality**: pdfwrite work scales with page/image count; rasterization scales with selected pages at bounded DPI (A1 §5.3, A6 §5.1). Sequential rendering keeps PDF-to-JPG peak memory at one page at a time (DEC-015, A6 §5.1).

## 6. Alternatives

### 6.1 Policy approach for the limit surface

**Policy A — Single generous per-file cap plus page count (minimal contract).**
- What it is: one byte cap per tool (e.g., 100 MB) plus a page cap; few axes; a small contract.
- Trade-offs: simplest to implement and explain; but a 100 MB image-heavy PDF (or a 100-MP image set) can drive decoded memory and engine work far beyond the worker bound *before* any limit trips, converting resource-exhaustion risk into worker OOM kills and timeouts. It does not satisfy DEC-034's combined-axes language ("limits may combine total bytes, per-file bytes, file count, page count, pixel count, page geometry, estimated memory, and expected output size") or DEC-169's decoded-resource-risk validation as cleanly. Cost/operational impact: fewer validation checks, but more incident-driven tuning. Privacy/security: weaker defense against decompression-bomb-style inputs (DEC-093).
- Status: feasible and viable as a fallback, not recommended.

**Policy B — Multi-axis per-tool caps with an estimated-memory gate (recommended).**
- What it is: per-tool byte/page/pixel/output/ZIP/memory axes as in §7, with admission computing a conservative `estimatedPeak` from decoded-resource risk (file bytes, page count, decoded pixel totals, output count) and rejecting when it exceeds the tool's `maxEstimatedMemoryBytes` — before the engine runs.
- Trade-offs: a larger, versioned contract and a documented estimate formula; but it directly implements DEC-034's axis list, DEC-093's decode-expansion limits, and DEC-169's resource-exhaustion prevention, and it keeps every admitted job inside the C1 worker bound (2 GiB) with margin. Cost/operational impact: modest validation code and one documented formula, verified by functional fixtures; fewer production incidents. Privacy/security: resource bombs are rejected structurally without executing engines (DEC-088/093).
- Status: recommended (DEC-055 satisfied: at least two viable approaches compared).

### 6.2 Enforcement-layer alternatives (same policy, different placement)

- **Enforcement at Nginx + API admission + worker runtime (recommended):** Nginx `client_max_body_size` set to the largest per-tool upload plus headroom as a coarse first gate (C4 §6); API admission authoritative per DEC-165 (structure, decoded-resource risk, all per-tool axes, fair-use/queue checks); worker runtime enforces the container memory/time/disk bounds as the final backstop (C1/C4). Trade-off: three places to keep consistent — mitigated by the contract as the single source of truth and drift tests.
- **Enforcement only in the API:** simpler, but leaves the origin exposed to oversized request bodies before application code runs (C4 §6 rejects this for the legacy precedent).
- **Enforcement only in worker runtime:** admissions accept jobs the workers cannot complete (violates DEC-070's "jobs that cannot finish must not be admitted" and wastes upload/storage). Rejected.

## 7. Recommendation

**Recommendation (not an accepted decision — DEC-054, DEC-057):** adopt **Policy B (multi-axis per-tool caps with an estimated-memory gate) with layered enforcement (Nginx coarse gate + API admission authoritative + worker runtime backstop)** and the conservative per-tool defaults below. Every value is a documented design/safety default, adjustable from production observations per DEC-066; **none is a benchmark result — no benchmark was run**.

### 7.1 Conservative per-tool server-limit defaults (server processing path)

| Axis | Compress PDF | Merge PDF | Split PDF | JPG to PDF | PDF to JPG |
|---|---|---|---|---|---|
| `maxFiles` | 1 | 20 | 1 | 50 | 1 |
| `maxFileBytes` | 100 MB | 100 MB | 100 MB | 20 MB | 100 MB |
| `maxTotalBytes` | 100 MB | 200 MB | 100 MB | 200 MB | 100 MB |
| `maxPages` (source) | 1000 | 1000 | 1000 | n/a | 200 |
| `maxOutputs` | 1 | 1 | 100 | 1 | 200 |
| `maxPixelsPerImage` / `maxPixelsPerPage` | n/a | n/a | n/a | 20 MP | 16 MP |
| `maxTotalPixels` | n/a | n/a | n/a | 100 MP | n/a |
| `maxEstimatedMemoryBytes` | 1.5 GiB | 1.5 GiB | 1.25 GiB | 1.5 GiB | 0.75 GiB |
| `maxExecutionSeconds` (per-tool timeout override of the C1 180 s default) | 180 | 180 | 180 | 180 | 300 |
| `maxZipBytes` | n/a (single) | n/a (single) | 200 MB | n/a (single) | 256 MB |
| `maxResultBytes` (operational safety cap) | 512 MB | 512 MB | 512 MB | 512 MB | 512 MB |
| Accepted MIME (server validation) | `application/pdf` | `application/pdf` | `application/pdf` | `image/jpeg`, `image/png`, `image/webp` | `application/pdf` |
| Accepted extensions | `.pdf` | `.pdf` | `.pdf` | `.jpg`, `.jpeg`, `.png`, `.webp` | `.pdf` |

Rationale per tool (documented characteristics, not measurements):

- **Compress PDF** (server-default, DEC-015): 1000 pages is a conservative ceiling for CPU-heavy `pdfwrite` re-encoding (A2 §5.1); the 1.5 GiB estimated-memory gate protects against image-bomb PDFs (pdfwrite memory can spike on large embedded images, A1 §5.3); 180 s extends the legacy 30 s Ghostscript timeout (`compress_service.py:40`) to cover heavier inputs. The 512 MB `maxResultBytes` is an operational cap only — `pdfwrite` can legitimately produce a larger output (DEC-080), which is reported honestly, not rejected; the cap merely bounds R2/bandwidth in pathological cases.
- **Merge PDF** (browser-first with server fallback, DEC-011/030/065): file-level controls (DEC-040), all-or-nothing (DEC-076), structure-preserving pikepdf memory ≈ inputs + outputs (A3 §5.1): 20 files / 200 MB total / 1000 pages conservatively bound that memory within 1.5 GiB.
- **Split PDF** (browser-first with server fallback): single input; range mode up to 1000 source pages with at most 100 entered ranges (= 100 outputs); per-page mode is capped by the output cap (documents over 100 pages in per-page mode are rejected with a clear code — a documented safety limit per DEC-038); ZIP cap 200 MB bounds the archive; overlap and order semantics (DEC-077/078) do not change the caps, they only multiply outputs, which `maxOutputs` bounds.
- **JPG to PDF** (browser-first with server fallback): 50 images and 100 MP total match the accepted DEC-015 desktop browser caps as a deliberately conservative server default; 20 MB per image and 20 MP per image bound decode expansion (DEC-093) — encoded size is a poor predictor of decode cost; WebP re-encode expansion is documented (A5 §5.1). EXIF/metadata preservation (DEC-084) is unaffected by the caps.
- **PDF to JPG** (browser-capable with server fallback): 200 source pages and 200 outputs align with the accepted DEC-015 desktop page cap as a conservative server default — the server's initial advantage is reliability and profile control, not larger page counts; 16 MP per page keeps each sequential pixmap ≤ ~48 MB (A6 §5.1) and matches the DEC-015 ceiling; 300 s timeout override covers 200 sequential renders (legacy rasterize timeout was 60 s, `pdf_to_image_service.py:20`); ZIP cap 256 MB bounds 200 JPG outputs.

Global contract fields (not per tool): `retentionSeconds: 3600` (DEC-070), `maxWaitSeconds: 900` and `maxQueueLength: 2000` and `maxConcurrentPerOrigin: 4` (C1, DEC-035/137/020), `defaultTimeoutSeconds: 180` (C1).

### 7.2 Admission, queue, and deadline consistency (DEC-035, DEC-070, DEC-073)

- Every server job must be able to finish before its authoritative `expires_at` (upload receipt + 1 h, DEC-070). Admission enforces the hard caps so that `maxWaitSeconds` (15 min) + `maxExecutionSeconds` (per tool) leaves a practical download window. No completion-time prediction is computed or presented (DEC-073).
- Queue caps from C1 are enforced at admission: queue length, maximum wait, per-origin concurrency. A job that waits past `maxWaitSeconds` fails with a clear, retryable, machine-readable code rather than silently extending its window (DEC-035, DEC-070).
- Fair-use cost weighting (DEC-020, C1) may use the same per-tool axes (input size and complexity, output count) as cost signals; enforcement levels (allow / delay / challenge / reject) remain as C1 §7 defines.

### 7.3 Machine-readable capability and limits contract shape (DEC-165)

Exact fields worth exposing. Recommended shape (versioned endpoint, e.g., `GET /api/v1/capabilities`):

```json
{
  "schemaVersion": 1,
  "contractVersion": "1.0.0",
  "generatedAt": "2026-07-31T00:00:00Z",
  "cacheMaxAgeSeconds": 300,
  "global": {
    "retentionSeconds": 3600,
    "maxWaitSeconds": 900,
    "maxQueueLength": 2000,
    "maxConcurrentPerOrigin": 4,
    "defaultTimeoutSeconds": 180
  },
  "tools": {
    "compress-pdf": {
      "processingPath": "server",          // server-default (DEC-015)
      "browserFirst": false,
      "ready": true,                       // per-tool readiness (DEC-167)
      "limits": {
        "maxFiles": 1,
        "maxFileBytes": 104857600,
        "maxTotalBytes": 104857600,
        "maxPages": 1000,
        "maxOutputs": 1,
        "maxEstimatedMemoryBytes": 1610612736,
        "maxExecutionSeconds": 180,
        "maxResultBytes": 536870912,
        "acceptedMimeTypes": ["application/pdf"],
        "acceptedExtensions": [".pdf"]
      }
    },
    "merge-pdf": { /* processingPath hybrid, browserFirst true; 20/100MB/200MB/1000 pages/1 output/1.5GiB/180s/512MB */ },
    "split-pdf": { /* processingPath hybrid, browserFirst true; 1/100MB/100MB/1000 pages/100 outputs/1.25GiB/180s/200MB zip/512MB */ },
    "jpg-to-pdf": { /* processingPath hybrid, browserFirst true; 50/20MB/200MB/20MP per image/100MP total/1.5GiB/180s/512MB; image MIME set */ },
    "pdf-to-jpg": { /* processingPath hybrid, browserFirst true; 1/100MB/100MB/200 pages/200 outputs/16MP per page/0.75GiB/300s/256MB zip/512MB */ }
  }
}
```

Contract requirements (DEC-165): cacheable safely (`cacheMaxAgeSeconds` with the frontend using conservative fallback values if unavailable); versioned (`contractVersion` bump on any change, with CI asserting backend validation matches the published contract — no silent drift); localized at the presentation layer (the contract carries machine keys, the frontend maps keys to localized copy); browser-specific safety limits are **not** in this server contract — they remain frontend capability logic and are surfaced separately so the two never merge (DEC-165). `processingPath`/`browserFirst` let the frontend render correct routing copy without hardcoding.

### 7.4 Machine-readable failure codes (DEC-034)

Recommended code set, each with a safe localized message key, an HTTP status, and an optional `limit` payload giving the violated axis and value:

| Code | Meaning | HTTP |
|---|---|---|
| `file_empty` | Zero-byte file | 400 |
| `unsupported_mime_type` / `unsupported_extension` | Extension/MIME outside accepted set | 415 / 400 |
| `invalid_magic_bytes` | Byte signature mismatch | 400 |
| `file_too_large` | Single file over `maxFileBytes` | 413 |
| `total_bytes_exceeded` | Input set over `maxTotalBytes` | 413 |
| `file_count_exceeded` | Over `maxFiles` | 422 |
| `page_count_exceeded` | Source over `maxPages` | 422 |
| `pixel_count_exceeded` | Per-image/page or total over pixel caps | 422 |
| `output_count_exceeded` | Selection produces over `maxOutputs` (Split per-page, ranges; PDF to JPG selections) | 422 |
| `estimated_memory_exceeded` | Computed `estimatedPeak` over `maxEstimatedMemoryBytes` (resource-bomb gate) | 422 |
| `zip_size_exceeded` | ZIP assembly over `maxZipBytes` | 422 |
| `corrupt_file` | Structurally invalid input | 422 |
| `encrypted_requires_password` | Password needed to proceed (with which-file scope for Merge, DEC-074) | 400 |
| `incorrect_password` | Wrong credentials — distinct from corrupt per DEC-036 | 401 |
| `permission_restricted` | Credentials valid but document permissions deny the operation (DEC-064) | 403 |
| `threat_blocked` | Threat-classified file blocked (DEC-088; safe category only, no exploit detail) | 403 |
| `engine_unavailable` | Tool's engine not ready (per-tool readiness, DEC-167) | 503 |
| `queue_full` | Queue-length cap reached; retryable with `Retry-After` (DEC-035) | 503 |
| `wait_limit_exceeded` | Job failed after `maxWaitSeconds`; retryable | 409 |
| `rate_limited` | Fair-use challenge; `Retry-After` (DEC-020) | 429 |
| `task_not_found` / `expired` | Unknown or expired task (DEC-067) | 404 |
| `processing_timeout` | Exceeded `maxExecutionSeconds`; safe category | 500 |
| `processing_failed` | Generic engine failure; safe category | 500 |

Response shape: `{ "error": { "code": "page_count_exceeded", "messageKey": "limit.page_count_exceeded", "tool": "compress-pdf", "limit": { "axis": "maxPages", "value": 1000 } } }`. Rejections never include filenames, passwords, signed URLs, object keys, document contents, or scanner/engine internals (DEC-025, DEC-036, DEC-042, DEC-088, DEC-169).

### 7.5 Raising procedure (documented, DEC-066/DEC-034)

Limits are conservative defaults. The documented raising procedure:

1. **Observe** production telemetry (C5): limit-triggered rejection rates per code, timeout rates, worker OOM/memory peaks, queue wait, engine failure categories, and coarse input-band distributions (DEC-024) — no document contents (DEC-025).
2. **Confirm headroom**: worker memory/time/disk bounds (C1) and the VPS memory envelope (C1/C4) have demonstrable margin; ClamAV and Redis budgets are reconciled; no OOM or timeout spikes near the ceiling.
3. **Propose** the new value with the documented rationale (what observation justifies it); **material raises require owner approval** (DEC-057).
4. **Change and verify**: bump `contractVersion`, update backend validation, and assert in CI that the published contract matches validation (drift test) and that over-limit fixtures still reject with correct codes.
5. **Re-observe** after deployment (DEC-160 gate); roll back the value if failures rise. An automated raise is never implied; every change is reviewed and reversible.

## 8. Measurable acceptance criteria

Functional and operational verification criteria (no benchmark wording per DEC-066):

1. `GET /api/v1/capabilities` returns the versioned contract for all five tools with the §7.3 fields; a schema test and a drift test assert the contract matches backend validation config exactly.
2. For each tool and each limit axis, an over-limit fixture is rejected before any engine work with the correct machine-readable code, the correct HTTP status, and a localized safe message (DEC-034).
3. The estimated-memory gate rejects a decoded-resource-bomb fixture (e.g., a PDF whose embedded image pixel sum or an image set whose decoded total exceeds the cap) with `estimated_memory_exceeded` before the engine runs (DEC-093, DEC-169).
4. A Compress job whose output exceeds the input (already-optimized source) completes with honest zero/negative-savings reporting (DEC-080); the 512 MB `maxResultBytes` cap only triggers in pathological cases and fails with a safe code.
5. Split per-page mode on a document over 100 pages, and PDF-to-JPG page selection producing over 200 outputs, reject with `output_count_exceeded` (DEC-038, DEC-186).
6. Threat-classified inputs are blocked with `threat_blocked` before engines (DEC-088); encrypted inputs return `encrypted_requires_password`/`incorrect_password`/`permission_restricted` as appropriate, distinct from `corrupt_file` (DEC-036, DEC-064).
7. The contract is cacheable with the declared TTL; when the contract endpoint is unavailable, the frontend renders conservative fallback values and backend validation remains authoritative (spoofed client values are rejected) (DEC-165).
8. Browser-specific limits never appear in the server contract; server limits never appear in browser capability logic (DEC-165) — asserted by a test on the two surfaces.
9. Admission honors queue caps and per-origin concurrency from C1 (queue length, max wait, per-origin 4) and never admits a job that cannot finish before its authoritative `expires_at`; no completion-time guarantee is presented (DEC-035, DEC-070, DEC-073).
10. Result/ZIP size caps bound R2 objects (C3 interface); over-cap jobs fail with a safe code and all artifacts are deleted by the absolute deadline (DEC-070, DEC-166).
11. Per-tool readiness (DEC-167) gates admission: jobs are not accepted for a tool whose engine is unavailable (`engine_unavailable`).
12. The raising procedure is documented (runbook/design), and a limit change requires a contract-version bump plus CI drift-test passage; the procedure contains no automated, unreviewed raise (DEC-066, DEC-057).
13. No text in the limits documentation claims measured or benchmark-proven capacity (DEC-066).

## 9. Assumptions, uncertainties, and unresolved questions

- **Assumption:** the VPS remains an ~8 GB / 4-core host with ~4.5 GB swap (legacy evidence, C1 §9); the current host state is unverifiable without access (DEC-172, DEC-160) and the budget must be re-verified before first deployment.
- **Uncertainty (surfaced, not silently resolved — DEC-183):** the memory envelope. C1 recommends 2 workers x 2 GiB (4 GiB) plus API, Redis (384 MB cap), and Nginx; C4 requires ClamAV, whose official documentation recommends 3-4 GiB ("may get by with less"). Summed with the system/Netdata share, the 8 GB envelope is exceeded if all budgets are at their upper bounds. The per-tool `maxEstimatedMemoryBytes` values above fit a 2 GiB worker with margin, but the worker bound itself, the ClamAV budget, and concurrency must be reconciled in design (C1 ↔ C4 ↔ C2 interface); a reduced worker bound (e.g., 1.5 GiB) would require lowering the estimated-memory gates.
- **Uncertainty:** the `estimatedPeak` formula (multipliers over file bytes, page count, decoded pixel totals, output count) must be documented as conservative design constants and validated with functional fixtures; the exact formula is design work, not fixed here.
- **Uncertainty:** per-page JPEG sizes and ZIP growth are content-dependent and unmeasured (DEC-066); the 200/256 MB ZIP caps are conservative defaults to be adjusted from production distribution data.
- **Uncertainty:** server PDF-to-JPG matching the DEC-015 desktop page cap (200) is deliberately conservative; raising it is a candidate first adjustment once telemetry shows headroom.
- **Unresolved (owner prompts):** (1) Policy B vs Policy A; (2) confirmation of the §7.1 default values as launch-safe; (3) the memory-envelope reconciliation decision (worker bound vs ClamAV budget vs concurrency); (4) acceptance of the raising procedure, including owner approval for material raises; (5) whether Split per-page mode's 100-page cap (= `maxOutputs`) is the preferred conservative limit.

## 10. Dependencies and cross-track interfaces

- **A2-A6**: engine resource profiles and output-expansion characteristics (this brief's §7.1 table derives from them).
- **B1**: browser capability detection stays separate; routing thresholds use the server contract for the fallback path (DEC-015/030/065, DEC-165).
- **C1**: worker bounds (2 GiB, 180 s default), queue caps (2000/15 min/4 per origin), fair-use classes — this brief's limits must fit and are enforced at admission; per-tool timeouts are the "per-tool overrides" C1 defers to C2.
- **C3**: `maxResultBytes`/`maxZipBytes` bound R2 object sizes and signed-URL download sizing; `retentionSeconds` mirrors the absolute deadline.
- **C4**: per-tool ceilings drive Nginx `client_max_body_size` (largest upload + headroom), tmpfs/scan size ceilings, and timeouts; the ClamAV memory budget participates in the envelope reconciliation (§9).
- **C5**: limit-triggered rejection rates, timeout rates, and OOM signals are monitoring inputs; limit adjustments use the same telemetry.
- **D5**: `threat_blocked` and fail-closed classes align with the D5 register (DEC-088); validation codes are safe general categories.
- **X1/X2**: this brief's recommendation, default table, contract shape, failure codes, and owner prompts feed the source/decision index and the reconciliation report.

## 11. Source-date log and evidence-completeness notes

- All decisions, specifications, Track A briefs, Track C briefs, and legacy files were read on 2026-07-31; legacy citations above use `papyr-reference/` paths with line references.
- Web evidence was not re-fetched for this brief: engine characteristics are cited from the Track A briefs (A1-A6), each of which records primary-source URLs and the access date 2026-07-31 in its own §5 and §11; worker/queue values are cited from C1, which records its evidence files (`evidence/c1-evidence-*.md`, access date 2026-07-31).
- Completeness notes: (a) this brief intentionally performs no new web research — its evidence is the consumed Track A/C findings plus the legacy files listed in §1; (b) no value here is measured; all limits are documented design/safety defaults per DEC-066; (c) the memory-envelope tension between C1, C4, and this brief is recorded in §9 for the design reconciliation rather than resolved here (DEC-183); (d) the exact `estimatedPeak` formula and the per-page JPEG/ZIP distribution data are recorded as design-and-telemetry items, not invented here.
- Uncertainties from §9 are not resolved in this brief; they are recorded for the owner and for reconciliation (X2).

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066).
- No installs, builds, container or server starts, VPS/SSH access, deployment, provider authentication, account creation, or authenticated/mutating remote actions were performed (plan §4.1).
- No product code, scaffolding, or infrastructure was created or modified; no decision log, specification, or existing audit-output file was edited. All writes were confined to `audit-outputs/research/track-c/` (this file only).
- `papyr-reference/` was read-only; verified unchanged via read-only `git -C papyr-reference status --porcelain` (empty output, exit 0) before and after this task.
- No value in this brief is presented as a measured capacity or a benchmark result; all limits are conservative design and safety defaults adjustable from production observations (DEC-066).
- Findings in this brief are recommendations, not accepted decisions (DEC-054, DEC-057); owner approval is required before any limit set becomes part of approved design and implementation planning.
