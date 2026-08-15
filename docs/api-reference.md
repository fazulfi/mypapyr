# Papyr Public API reference

This is the machine-readable and human-readable contract for the Papyr
backend. Every shape here is grounded in the backend source under
`backend/app/` — the schemas in `schemas/job.py`, the error envelope in
`errors.py`, the closed failure vocabulary in
`routers/capabilities.py`, the state machine in `tasks/state_machine.py`,
and the four router modules (`capabilities`, `status`, `download`,
`compress`). Field names are **snake_case** unless the endpoint payload is
modeled with `alias_generator=to_camel` (the capabilities contract); the
concrete shapes below state which is which.

The **capabilities endpoint is the machine-readable source of truth**: every
limit, every tool, and every failure code the client may legitimately rely on
is enumerated under `GET /api/v1/capabilities`. Implement a client against
that payload, not against this document's examples.

- [Hosts & request path](#hosts--request-path)
- [Correlation & caching headers](#correlation--caching-headers)
- [Error envelope](#error-envelope)
- [Failure code table (19)](#failure-code-table-19)
- [State machine](#state-machine)
- [Endpoints](#endpoints)

## Hosts & request path

The browser issues **same-origin** `/api/v1/*` requests. In this branch the
client talks to the FastAPI service directly at its published origin; a
build-time Next.js rewrite and the frontend→backend origin variable
(`NEXT_PUBLIC_API_BASE_URL`) land with the production networking task. The
target path traverses Cloudflare DNS/TLS → nginx → FastAPI on the internal
service DNS `api:3000` (`deploy/runbook-vps.md`; `deploy/docker-compose.yml`).

```text
Browser ── /api/v1/* (same-origin) ──> Next.js rewrite (next.config.ts)
        ── https://api.mypapyr.com/api/v1/* ──> Cloudflare (DNS, TLS)
        ── nginx (default_server → 444; valid vhost → proxy) ──> FastAPI (:3000)
```

The API service publishes no host port (`expose: "3000"` only); TLS is
terminated by nginx, and the nginx vhost must drop unknown Hosts (fail-closed
`default_server → 444`).

## Correlation & caching headers

- **`X-Request-ID`** — every response carries this correlation header
  (`backend/app/middleware.py`). A valid inbound `X-Request-ID` (≤64 chars)
  is propagated; otherwise a fresh UUID4 is issued. Errors embed the same id
  in the envelope body (`request_id`) and echo it in the header
  (`errors.py:217-233`), so a failed request can be traced to log lines.
  `X-Request-ID` is also in the cross-origin `Allow-Headers` allowlist
  (`backend/app/security/middleware.py:34`).
- **`Cache-Control`**:
  - `GET /api/v1/capabilities` → `public, max-age=3600` (the contract changes
    only on deploy; one hour cache safe, `routers/capabilities.py:82`).
  - `GET .../status` and `GET .../download/{output}` → `no-store` (per-task
    timing/progress metadata and signed grants must never be replayed by a
    shared proxy; `status.py:115`, `download.py:156`).

## Error envelope

Every error response has a stable shape built by
`errors.build_error_envelope` (`errors.py:177-193`). `messageKey` is the
stable localization key; `message` is a short human default; `details` (when
present) carries sanitized field locations **only** — never `msg`, `input`,
filenames, payloads, or credentials (`errors.py:196-214`).

```json
{
  "error": {
    "code": "bad_request",
    "category": "validation",
    "message": "Bad request",
    "messageKey": "error.badRequest",
    "retryable": false
  },
  "request_id": "8f2b9c1a-...-uuid4"
}
```

The `category` vocabulary is closed (`errors.py:46-55`):
`validation`, `auth`, `threat`, `system`, `rate_limit`, `not_found`,
`engine`.

The deterministic status→code table (`errors.py:69-140`) used by the
auth/validation/threat handlers:

| HTTP | code | category | messageKey | retryable |
| ---- | ---- | ---- | ---- | ---- |
| 400 | `bad_request` | validation | `error.badRequest` | false |
| 401 | `unauthorized` | auth | `error.unauthorized` | false |
| 403 | `forbidden` | auth | `error.forbidden` | false |
| 404 | `not_found` | not_found | `error.notFound` | false |
| 405 | `method_not_allowed` | validation | `error.methodNotAllowed` | false |
| 409 | `conflict` | validation | `error.conflict` | false |
| 413 | `payload_too_large` | validation | `error.payloadTooLarge` | false |
| 415 | `unsupported_media_type` | validation | `error.unsupportedMediaType` | false |
| 422 | `unprocessable_entity` | validation | `error.unprocessableEntity` | false |
| 429 | `rate_limited` | rate_limit | `error.rateLimited` | **true** |
| 5xx (unknown) | `internal_error` | system | `error.internalError` | false |

Unknown 4xx statuses normalize to `client_error`/validation; everything else
unknown normalizes to `internal_error`/system (`errors.py:151-174`). The
submission routers (e.g. `compress.py`) raise `HTTPException` with only a
`messageKey` detail — never rendered directly (validation normalization) —
and map store/queue failures to the fail-closed 503/409 generic envelope.

**Scanner/threat gate** is specified but the concrete scanner remains behind the defined protocol seam on this branch. The classification matrix is implemented: blocking verdicts (when a scanner is present) map to `MALICIOUS`/`ACTIVE_CONTENT` → 403, `INDETERMINATE` → 500, `SCANNER_UNAVAILABLE`/`SANITIZATION_UNAVAILABLE` → 429. Admission currently enforces validation, sanitization, and the fail-closed classification matrix.

## Failure code table (19)

`GET /api/v1/capabilities` advertises the **closed** 19-code failure
vocabulary (`routers/capabilities.py:106-191`, `FailureCode`). Each entry is
`{code, messageKey, retryable}`. Codes are **stable forever**; retryability
and localization are resolved from the single metadata table. Four codes are
**retryable** (marked ●) — all map to `error.rateLimited`:

| # | code | messageKey | retryable |
| --- | ---- | ---- | ---- |
| 1 | `empty` | `error.badRequest` | no |
| 2 | `type_mismatch` | `error.unsupportedMediaType` | no |
| 3 | `size_exceeded` | `error.payloadTooLarge` | no |
| 4 | `corrupt` | `error.badRequest` | no |
| 5 | `resource_exceeded` | `error.invalidRequest` | no |
| 6 | `too_many_files` | `error.invalidRequest` | no |
| 7 | `total_too_large` | `error.payloadTooLarge` | no |
| 8 | `too_many_pages` | `error.invalidRequest` | no |
| 9 | `too_many_pixels` | `error.invalidRequest` | no |
| 10 | `too_many_outputs` | `error.invalidRequest` | no |
| 11 | `estimated_memory_exceeded` | `error.invalidRequest` | no |
| 12 | `zip_too_large` | `error.payloadTooLarge` | no |
| 13 | `result_too_large` | `error.payloadTooLarge` | no |
| 14 | `queue_full` | `error.rateLimited` | **● yes** |
| 15 | `max_wait_exceeded` | `error.rateLimited` | **● yes** |
| 16 | `too_many_concurrent` | `error.rateLimited` | **● yes** |
| 17 | `rate_limited` | `error.rateLimited` | **● yes** |
| 18 | `not_found` | `error.notFound` | no |
| 19 | `expired` | `error.notFound` | no |

Queue admission codes (14–16) are carried by the typed `QueueError` and
mapped deterministically via `failure_code_for_queue_error`
(`capabilities.py:220-231`); unknown queue errors fail closed rather than
misclassify. `not_found`/`expired` both resolve to the non-revealing 404
(see status/download below).

## State machine

`backend/app/tasks/state_machine.py` defines the closed active vocabulary and
deterministic transition table:

```text
JobState = {queued, processing, done, failed, cancelled}

Events:   worker_claimed | result_uploaded | engine_error | timeout
          | safety_shutdown | user_cancelled | deadline_reached

Transitions (guarded pairs return None — never invented):
  queued     --worker_claimed-->          processing
  queued     --user_cancelled-->          cancelled
  processing --result_uploaded-->        done
  processing --engine_error-->           failed
  processing --timeout-->                failed
  processing --safety_shutdown-->        failed
  done       --deadline_reached-->       EXPIRED (LifecycleOutcome)
  failed     --deadline_reached-->       EXPIRED (LifecycleOutcome)
```

- `expired` is **not a state** — it is a `LifecycleOutcome` driven by the
  absolute retention deadline. `done`/`failed` yield it on
  `DEADLINE_REACHED`; `cancelled` is fully terminal
  (`state_machine.py:50-84`).
- Expired records are no longer queryable; status returns the same stable 404
  as an unknown id, non-revealing.
- `cancellable` is `true` only in `queued` (user cancellation is only
  expressible from queued; `job.py:136-137`, `status.py:86`).
- `result` present ⟺ `state == done`; `error` present ⟺ `state == failed`
  (enforced both by the store and the `TaskStatus` model validator,
  `job.py:126-137`).

### `TaskStatus` JSON shape (`schemas/job.py:102-137`) — snake_case

`GET /api/v1/tools/{tool}/tasks/{task_id}/status` returns:

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool": "compress-pdf",
  "state": "processing",
  "created_at": "2026-08-13T10:00:00Z",
  "accepted_at": "2026-08-13T10:00:00Z",
  "updated_at": "2026-08-13T10:00:05Z",
  "expires_at": "2026-08-13T11:00:00Z",
  "progress": {"unit": "bytes_uploaded", "value": 51200, "total": 102400},
  "result": null,
  "error": null,
  "queued_at": "2026-08-13T10:00:00Z",
  "started_at": "2026-08-13T10:00:05Z",
  "completed_at": null,
  "cancellable": false
}
```

- `progress.unit` ∈ `{bytes_uploaded, pages_processed, engine_progress}`
  (measureable only; `total` `null` = indeterminate; `job.py:30-40`).
- `result` (only when `done`) `{output_count, total_bytes}` — metadata only,
  never file names, signed URLs, or keys (`job.py:43-53`).
- `error` (only when `failed`) `{code, category, retryable, message_key}` —
  safe category only (`job.py:56-69`).
- The body is **snake_case**, and `Cache-Control: no-store`.

## Endpoints

### `GET /health`

Liveness. Always `200` (application is running).

```json
{"status": "ok"}
```

`backend/app/main.py:86-88`, `backend/Dockerfile.production` healthcheck
probes this path.

### `GET /health/ready`

Readiness. `200` only when all three checks pass; otherwise `503`.

```json
{
  "status": "ready",
  "checks": {
    "foundation": "ok",
    "redis": "ok",
    "scanner": "ok"
  },
  "deferred": ["worker"]
}
```

- `foundation`: `ok` | `missing_required_config` — whether the five required
  env vars load (`config.py`).
- `redis`: `ok` | `unavailable` — task-store ping.
- `scanner`: `ok` | `unavailable` — ClamAV verdict must be `CLEAN`.
- `deferred` always lists `["worker"]` (never probed here).
- `backend/app/health.py:61-74,181-201`.

### `GET /api/v1/capabilities`

The machine-readable contract. **camelCase** payload
(`alias_generator=to_camel`), `Cache-Control: public, max-age=3600`. Versioned
(`version: 1`). Source of truth for every tool limit, the global limits, and
the failure-code table above.

```json
{
  "version": 1,
  "tools": {
    "compress-pdf": {
      "maxFiles": 1, "maxFileBytes": 104857600, "maxTotalBytes": 104857600,
      "maxPages": 1000, "maxOutputs": 1,
      "maxPixelsPerImage": null, "maxPixelsPerPage": null, "maxTotalPixels": null,
      "maxEstimatedMemoryBytes": 1610612736, "maxExecutionSeconds": 180,
      "maxZipBytes": null, "maxResultBytes": 536870912
    }
  },
  "global": {
    "retentionSeconds": 3600,
    "maxWaitSeconds": 900,
    "maxQueueLength": 2000,
    "maxConcurrentPerOrigin": 4,
    "defaultTimeoutSeconds": 180
  },
  "failureCodes": [
    {"code": "empty", "messageKey": "error.badRequest", "retryable": false}
  ]
}
```

- `tools[slug]` keys are the closed tool ids: `compress-pdf`, `merge-pdf`,
  `split-pdf`, `jpg-to-pdf`, `pdf-to-jpg` (`capabilities.py:96-103`).
- Per-tool ceilings (MB/GB are **MiB/GiB**, decimal for pixel caps). Defaults
  differ per tool — e.g. merge allows 20 files/100 MiB each/200 MiB total,
  1000 pages; split allows 100 outputs and a 200 MiB zip; jpg-to-pdf 50 files
  of 20 MiB and `maxPixelsPerImage=20000000`; pdf-to-jpg 200 pages/200
  outputs, `maxPixelsPerPage=16000000`, max-exec 300 s
  (`capabilities.py:305-378`).
- `global` axes are derived from runtime Settings when mounted, so the
  advertised contract always equals enforcement
  (`capabilities.py:406-423`).

### `POST /api/v1/tools/{tool}/tasks` — admission (multipart upload)

`tool` ∈ `{compress-pdf, merge-pdf, split-pdf, jpg-to-pdf, pdf-to-jpg}`.

- Server runs, in order: **validation** → **security sanitize** → **R2 upload (sanitized bytes)** → **enqueue** → **admission response** (see `compress.py:88-160`). A concrete threat scanner behind the classification seam is a later phase; admission currently enforces validation, sanitization, and the fail-closed classification matrix.

- Success returns **`202 Accepted`**:

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "queued",
  "expires_at": "2026-08-13T11:00:00Z"
}
```

(`schemas/job.py:88-99`; `task_id` is opaque high-entropy; admission always
reports `queued`.)

Failures: 400 on validation/sanitization rejection, 403/429/500 from the
scanner threat gate, 409/503 on enqueue store failures (fail-closed generic
envelope) — all in the stable error shape with the closed failure code in the
`error.code`.

### `GET /api/v1/tools/{tool}/tasks/{task_id}/status`

Returns the `TaskStatus` shape above. **`200`** with `Cache-Control: no-store`.
Unknown id, a task whose record names a different `tool`, or an expired task
all return **`404`** (non-revealing, identical). Store failure → generic
`500`. Status reads never extend retention (`status.py:90-116`).

### `GET /api/v1/tools/{tool}/tasks/{task_id}/download/{output}`

Signed download grant for one output of a **done** task. `output` is a
zero-based integer (`ge=0`). Returns **`200`**:

```json
{
  "url": "https://<r2-endpoint>/.../tmp/2026-08-13/abc123...pdf?...sig...",
  "expires_at": "2026-08-13T11:00:00Z"
}
```

(`routers/download.py:60-72,108-157`.)

- `url` is a presigned GET URL valid for **`min(remaining artifact lifetime, 300 s)`**
  (`utils/r2.py:57-58,284-305`); it can never outlive the artifact, and a
  URL whose remaining lifetime is under 1 s is treated as expired.
- `expires_at` is the authoritative artifact expiry, unchanged by any refresh.
- **Every denial returns the same `404`**: unknown task, expired task, wrong
  `tool`, task not `done`/no result, out-of-range `output`, or
  already-expired artifact (`download.py:138-155`). Pre-signed URL is granted
  only when `record.tool == tool`, `state == done`, and `0 ≤ output < len(objects)`
  (`authorize_download`, `download.py:108-123`).
- `Cache-Control: no-store`. R2 credential/transport failure → generic `500`.

**Download flow contract**: admission returns `task_id` → poll `status` until
`state == "done"` (with `result.outputCount`) → request
`download/{output}` for `0..outputCount-1` → fetch the presigned `url` within
300 s and before `expires_at`.
