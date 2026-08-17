# Papyr health-signal contract (OP-01)

**Scope.** OP-01 defines the closed, privacy-safe health-signal vocabulary for
Papyr operations (arch §25.3; DEC-182) and the internal-only Netdata coverage
that feeds it (`netdata-compose.yml`). OP-02 and OP-03 consume these signals.

**Authority.** The fixed backend monitor schema (`backend/app/ops/monitor.py`)
remains the source of truth for the eight in-VPS checks; this contract names,
bounds, and owns each signal without modifying that schema. The ninth signal,
`public_endpoints`, is the OP-02 consumer contract; its live multi-region
probes are owner-gated under R-12/G-4 and are implemented elsewhere.

## Signal vocabulary

The vocabulary is closed and additive-only. Removing or renaming a signal is a
contract change. Each signal carries only count, boolean, enum, duration,
status-code and exception-class fields — never document content.

<!-- HEALTH-SIGNAL-VOCABULARY-START -->
| Signal | Surface | Owner | Freshness | Severity mapping | Source | Closed data fields |
| --- | --- | --- | --- | --- | --- | --- |
| `api_ready` | API readiness | api | <=60s | ok->info; warn->warning; fail->critical | monitor check_api_ready | status, status_code, error_class |
| `queue_backlog` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_backlog | count |
| `queue_pel` | queue | queue | <=60s | ok->info; warn->warning; fail->critical | monitor check_queue_pel | pending, oldest_idle_ms, group_exists |
| `worker_health` | workers | worker | <=60s | ok->info; warn->warning; fail->critical | monitor check_worker_health | group_exists, pending, oldest_idle_ms, worker_probe |
| `redis` | Redis | redis | <=60s | ok->info; warn->warning; fail->critical | monitor check_redis | status, error_class |
| `clamd` | engines | engine | <=60s | ok->info; warn->warning; fail->critical | monitor check_clamd | status, error_class |
| `r2_ops` | storage integration | storage | <=300s | ok->info; warn->warning; fail->critical | monitor check_r2_ops | status, error_class |
| `cleanup_freshness` | cleanup health | cleanup | <=3600s | ok->info; warn->warning; fail->critical | monitor check_cleanup_freshness | age_seconds, reason |
| `public_endpoints` | public endpoints | status | <=300s | ok->info; degraded->warning; down->critical | OP-02 multi-region snapshot | region, consecutive_failures, state |
<!-- HEALTH-SIGNAL-VOCABULARY-END -->

## Surface mapping

| OP-01 surface | Signals | Notes |
| --- | --- | --- |
| API readiness | `api_ready` | GET /health/ready answers 200 with status ready. |
| Queue | `queue_backlog`, `queue_pel` | Stream XLEN and pending-entry idle age under the R-07 cap. |
| Workers | `worker_health` | Consumer-group existence, PEL staleness, worker /health probe. |
| Redis | `redis` | PING plus the docker compose memory-watermark probe. |
| Engines | `clamd` | Scanner daemon TCP PING/PONG on 3310; engine subprocess availability aggregates into `worker_health` (the worker /health probe reflects in-process engine readiness). |
| Storage integration | `r2_ops` | Read-only bounded R2 list probe (MaxKeys=1, prefix tmp/); never mutates. |
| Cleanup health | `cleanup_freshness` | ops:cleanup marker last outcome ok and last success recent. |
| Public endpoints | `public_endpoints` | OP-02 derived state from multi-region observations. Live snapshot production is owner-gated under R-12/G-4. |

## Freshness

- `<=60s` checks run from the Netdata agent and the backend monitor watch loop
  (60 s interval); staleness beyond the bound is a `fail`/`critical`.
- `<=300s` covers the read-only R2 probe and any external observation window.
- `<=3600s` is the cleanup freshness ceiling (3600 s = cleanup max age).
- A signal whose last observation exceeds its freshness is treated as absent
  (`fail`/`critical`), never as healthy-stale.

## Severity mapping

- `ok -> info` — healthy; no action.
- `warn -> warning` — degraded: a bounded condition (backlog near the warn
  threshold, cleanup aging); review, no paging.
- `fail -> critical` — failed: a monitored surface is down or stale; incident
  path (OP-03) and public status derivation (OP-02) trigger.
- The `public_endpoints` signal maps its derived states `degraded` and `down`
  instead of `warn`/`fail` because derivation is deliberately noise-resistant.

## Owners

| Owner | Responsibility |
| --- | --- |
| `api` | Control-plane readiness contract. |
| `queue` | Streams backlog and pending-entry thresholds. |
| `worker` | Consumer-group health and engine subprocess availability. |
| `redis` | Foundation liveness and R-09 memory watermark. |
| `engine` | Scanner daemon and engine runtime availability. |
| `storage` | R2 object-lifecycle integration availability. |
| `cleanup` | Expired-task cleanup freshness. |
| `status` | Public-endpoint derivation consumed by OP-02. |

## Privacy boundary

Monitoring collects aggregate operational signals only (DEC-175, DEC-182).
The health vocabulary and the Netdata agent never derive a signal from, and
never carry:

<!-- PRIVACY-REJECTED-TERMS-START -->
filename, document name, document content, extracted text, object key, signed url, password, token, payload, document metadata
<!-- PRIVACY-REJECTED-TERMS-END -->

In concrete terms:

- **No filenames or document terms.** Uploaded file names, document names,
  extracted text, and content-derived values are never signals.
- **No object keys.** Opaque R2 object keys (`tmp/<date>/<32hex>.<ext>`) and
  their components never appear; `r2_ops` reports availability only.
- **No signed URLs.** Download grants and presigned URLs are never signals.
- **No passwords.** Encrypted-PDF passphrases and any credential material are
  never signals (PT-04 memory-only contract).
- **No payload fields.** Upload/queue payload bodies and request contents are
  never signals.
- **No document metadata.** Page counts, sizes, and other precise document
  characteristics are excluded; only task-count and backlog aggregates are
  observables.
- **Exception classes, not messages.** Check details carry exception class
  names, status codes, counts, and booleans only (DEC-175).

## Operational posture

- Netdata runs internal-only: no published port, no docker socket mount, no
  env_file (the app env carries R2 credentials and must never reach the
  monitoring plane), neutral `NETDATA_HOSTNAME`, digest-pinned immutable image,
  and no Netdata Cloud or provider claim. Guard: `scripts/check-monitoring.sh`.
- The Netdata service intentionally retains default container capabilities:
  the official image transitions to the `netdata` user via an internal
  privilege drop and its go.d/system collectors require the default set.
  Everything else mirrors the hardened app posture (read-only rootfs,
  no-new-privileges, tmpfs, resource bounds, bounded json-file logging).
- Container liveness is the agent's own supervisor's job (`restart:
  unless-stopped`); the agent's output charts are the monitored object, so no
  container healthcheck is declared.
- Owner-gated, out of branch scope: provider/threshold approvals, the
  `monitoring` profile activation on the VPS, and operator UI access via SSH
  tunnel (R-12/G-4). No host, credential, or secret is committed here.
