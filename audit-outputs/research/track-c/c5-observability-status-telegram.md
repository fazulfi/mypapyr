# C5 — Observability, Status, and Telegram Research Brief

| Field | Value |
|---|---|
| Brief ID | C5 |
| Path | `audit-outputs/research/track-c/c5-observability-status-telegram.md` |
| Track | C — Infrastructure and operations |
| Title | Observability, status, and Telegram research |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent, Track C Wave 1) |
| Status | Complete (draft for owner review under DEC-057) |
| Governing decisions | DEC-097, DEC-104, DEC-116, DEC-119, DEC-161, DEC-180, DEC-182; supporting: DEC-024, DEC-025, DEC-066, DEC-167, DEC-175 |
| Spec sections served | Technical Architecture Specification §16, §20, §24, §25.3 items 10, 11, 19; Product and UX Design Specification §13, §15.4, §17, §21.8, §20.6 |

**Files read for this brief**

- `<workspace-root>\AGENTS.md`
- `<workspace-root>\papyr-rebuild-decisions.md` (in full; DEC-097, DEC-104, DEC-116, DEC-119, DEC-161, DEC-180, DEC-182 govern this brief)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (in full; §16, §20, §23, §24, §25.3)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (in full; §13.3, §15.4, §17, §20.6, §21.8)
- `<workspace-root>\audit-outputs\research-program-plan.md` (§7.3, §8)
- `<workspace-root>\audit-outputs\spec-cross-review.md`
- Legacy (read-only): `papyr-reference/docs/runbook-vps.md` (§10, §11), `papyr-reference/backend/main.py` (`/health`), `papyr-reference/deploy/nginx/conf.d/production.conf` (health location), `papyr-reference/backend/utils/config.py`
- Evidence file (primary evidence deliverable): `audit-outputs/research/track-c/evidence/c5-evidence-observability.md`

---

## 2. Scope

This brief resolves the monitoring, public status, and alerting design:

- **Monitoring coverage** (DEC-182): Netdata for VPS/service resource health plus independent external uptime checks; coverage of API, queue, workers, Redis, processing engines, storage integration, cleanup health, and relevant public endpoints — without collecting document contents.
- **Noise-resistant health signals for the public status experience** (DEC-116, DEC-119, DEC-161): the simple public status page hosted on Vercel, updated automatically from approved health signals, distinguishing observable availability from guarantees. Architecture §25.3 item 11.
- **Alert thresholds and deduplication for Telegram** (DEC-180): actionable, deduplicated, severity-aware alerts with no sensitive payloads; delivery failure visible in monitoring. Architecture §25.3 item 10.
- **Regional distinction** (DEC-104): monitoring and launch communication distinguish the US, LATAM, and Europe sufficiently to identify material failures per region, without prohibited profiling or document collection.
- **Operational overrides and pause/disable controls for AI-assisted automation** (DEC-097): owner accountability, auditable outputs, fail-safe behavior, secret protection, and pause controls. Architecture §25.3 item 19.

The user-visible status page copy/layout (plain EN/ES/ID, no sensitive infrastructure details) is owned by the UX spec §15.4; this brief sets the signal-derivation contract the page consumes.

## 3. Non-goals

- **Netdata alert-rule file syntax and exact thresholds for every metric**: this brief sets representative conservative thresholds and the deduplication contract; exact rules are design/implementation output refined from production telemetry (DEC-066).
- **Analytics event schema** (product analytics per DEC-025): D3 owns the analytics/privacy boundary; this brief's signals are operational, not product-analytics.
- **Telegram bot mechanics beyond the alert contract** (account creation, bot registration): no account/bot is created during research; only the documented Bot API contract is described.
- **Backup scheduling/monitoring**: C6 owns backup cadence; this brief only notes that backup failures must alert.
- **The public status page visual design and copy**: UX spec §15.4.
- **A second notification channel**: explicitly not required at launch (DEC-180).

## 4. Research questions

Restated from plan §7.3 (C5):

1. What monitoring coverage satisfies DEC-182 (Netdata + external uptime) for API, queue, workers, Redis, engines, storage integration, cleanup health, and public endpoints, without document content?
2. How are noise-resistant health signals derived and combined so the Vercel-hosted public status page (DEC-119) updates automatically (DEC-161) and stays useful when the backend VPS is unavailable?
3. What alert thresholds, severity levels, and deduplication rules are appropriate for Telegram alerts (DEC-180), including handling of Telegram delivery failure?
4. How does monitoring distinguish the US, LATAM, and Europe sufficiently for material-failure identification without prohibited profiling (DEC-104)?
5. What operational overrides and pause/disable controls satisfy DEC-097 (owner accountability with AI-assisted automation)?

## 5. Evidence

### 5.1 Legacy baseline evidence (read-only, `papyr-reference/`)

| Path and line | What it evidences |
|---|---|
| `docs/runbook-vps.md:23-25` | Legacy monitoring endpoints: Netdata at `https://<vps-ip>:19999` (or SSH tunnel), Netdata Cloud claimed, Telegram `<telegram-bot>` → chat ID `<telegram-chat-id>`. |
| `docs/runbook-vps.md:10.1-10.2` | Netdata local via SSH tunnel; Netdata Cloud claim procedure. |
| `docs/runbook-vps.md:10.3` | Legacy Telegram alerts: `alarm-notify.sh test`; health.d rules `papyr_security.conf` — CPU anomaly >50% non-Papyr process, outbound >100 Mbps, disk >85%. |
| `docs/runbook-vps.md:10.4` | BetterStack Uptime **pending** (awaiting signup); planned monitors: `mypapyr.com` HEAD 3 min, `api.mypapyr.com/health` GET 3 min, `/test/connectivity` GET 5 min. |
| `docs/runbook-vps.md:11` | Legacy compliance cadence: AIDE daily, chkrootkit/rkhunter weekly, Lynis monthly, OpenSCAP quarterly. |
| `docs/runbook-vps.md:8.3` | Incident handling: massive 5xx → compose ps, logs, restart, memory check. |
| `backend/main.py:112-120` | `/health` returns `status/version/timestamp` — the API health-check surface. |
| `deploy/nginx/conf.d/production.conf:98-104` | Nginx `/health` location: unrate-limited, `access_log off` — public health endpoint pattern. |
| `docs/runbook-vps.md:12` | Provider 2FA/account matrix — context for DEC-097 owner accountability. |

### 5.2 Primary web sources (official documentation; access date 2026-07-31)

Current authoritative documentation for Netdata, external uptime/status-page providers (BetterStack, UptimeRobot, Cloudflare Health Checks), and the Telegram Bot API is collected in the evidence file `evidence/c5-evidence-observability.md` (research primary evidence deliverable, access date 2026-07-31). Verified facts applied in this brief:

- **Netdata** (`https://learn.netdata.cloud/docs/netdata-agent/installation/docker`): official `netdata/netdata` image with `stable` tag; the container requires `pid: host`, `network_mode: host`, `cap_add SYS_PTRACE,SYS_ADMIN`, `security_opt apparmor:unconfined`, and host mounts (`/proc`, `/sys`, `/var/run/docker.sock`, `/var/log`, `/etc/passwd`, `/etc/group`, `/`, read-only) for full host/container monitoring — i.e., the monitoring container intentionally runs with elevated visibility; a Docker **socket proxy** is the documented way to reduce socket exposure; `DISABLE_TELEMETRY=1` opts out of anonymous telemetry; health check polls `http://localhost:19999/api/v1/info`; out-of-box collectors cover system, Docker containers, Nginx, Redis, and go.d modules (incl. web-server access-log tailing). Netdata Cloud requires an owner account claim at deployment (not performed during research).
- **Uptime/status providers:** BetterStack (`https://betterstack.com/docs/uptime/getting-started-with-status-pages/` and `/docs/uptime/api/`) provides hosted status pages and a status-pages/monitors API v2 (`uptime.betterstack.com/api/v2`) that supports programmatic status derivation; UptimeRobot (`https://uptimerobot.com/status-page/`, `/api/`, `/pricing/`) provides free public status pages and a monitors API; Cloudflare Health Checks (`https://developers.cloudflare.com/health-checks/`) probe origins from multiple locations. Free-tier monitor counts, check intervals, and regional probe coverage are confirmed at signup (owner action); the legacy runbook lists BetterStack as pending.
- **Telegram Bot API** (`https://core.telegram.org/bots/faq`, `https://core.telegram.org/bots/api`): **official rate limits — "In a single chat, avoid sending more than one message per second" (short bursts allowed, then 429), groups capped at 20 messages/minute, bulk broadcast at most ~30 messages/second (free tier)**; 429 responses carry `retry_after`; `sendMessage` text length limit 4096 characters; bots cannot initiate conversations (the owner starts the bot and the chat_id is registered); token compromise is handled via @BotFather.

## 6. Alternatives

### Monitoring and status

**Alternative A1 — Netdata (VPS/services) + external uptime monitors (multi-region) feeding a Vercel-hosted automated status page (recommended).**
- Netdata covers internal resource/service health (DEC-182); external monitors from ≥2 regions cover outside-in availability of `mypapyr.com` and `api.mypapyr.com/health` and survive a VPS outage (DEC-119). The public status page on Vercel consumes a compact health-status feed (edge function calling the monitors' status API and/or the API `/health` and per-tool readiness endpoint) with noise-resistant logic: N consecutive failures across ≥2 regions over a window before marking a component degraded/down; single-region flaps do not flip public status. Status wording distinguishes "observable availability" from per-engine guarantees (DEC-161); general per-tool availability may be exposed without infrastructure details (DEC-167).
- Trade-offs: two monitoring surfaces to maintain (internal + external); monitor-provider free-tier limits may constrain check intervals; status must not depend on the failing VPS to render (it reads the provider's status API, not the VPS) (DEC-119).

**Alternative A2 — Netdata alone; status page renders only VPS-sourced health data.**
- Rejected: the status page would depend on the failing VPS to render, violating DEC-119.

**Alternative A3 — A full commercial status-page product (e.g., BetterStack status page hosted) instead of a Vercel page.**
- Viable and the legacy plan (runbook §10.4, BetterStack pending). Trade-offs: faster time-to-value, built-in incident history and public page, no custom Vercel rendering; but adds an account/provider dependency and its own free-tier limits, and the owner explicitly approved Vercel hosting (DEC-119). Recommendation: keep the public page on Vercel (DEC-119) and use the monitor provider's checks/API as the signal source; the provider's own hosted page may be used as an internal/redundant view but the canonical public surface is Vercel.

### Alerting and Telegram

**Alternative B1 — Netdata notification integration + a small dedicated alert relay for non-Netdata signals (recommended).**
- Netdata alerts route to Telegram through its notification integration for resource/service alerts. A small relay (own code, inside the operational service) handles application-derived alerts that Netdata cannot express: queue depth/backlog, cleanup lag, per-tool readiness changes, scanner DB staleness, backup failures, Telegram delivery failure. Both paths share the deduplication and severity contract.
- Trade-offs: two alert producers to keep consistent; mitigated by one shared contract (severity levels, dedup keys, retention of "alert open" state) and one delivery module.

**Alternative B2 — All alerts through the relay; Netdata dashboards only, no Netdata notifications.**
- Rejected: loses Netdata's tuned resource anomaly detection (DEC-182 baseline) and adds custom reimplementation of OS-level alerting.

### Telegram alert contract (both alternatives)

- **Severity levels:** `info` (no notification default; recorded), `warning` (delayed/actionable soon), `critical` (immediate). Initial representative thresholds (conservative design choices, DEC-066): critical — service down, queue backlog > cap, cleanup failure streak, scanner down/stale, backup failure, OOM events, worker crash loop; warning — resource pressure (CPU/mem/disk per legacy baselines), queue wait > 50% of max, retry-rate spike, per-tool readiness degraded.
- **Deduplication:** each alert type has a dedup key (e.g., `svc:api:down`); while an alert is **open**, only state transitions (open → resolved, or severity escalation) generate a new message; repeat notifications are suppressed with a documented re-notify interval (e.g., every 30–60 min for unresolved critical); resolution messages close the key. Alert state is retained (Redis-sanitized metrics store or a small state file) so restarts do not re-spam.
- **Payload rules (DEC-180):** no user files, filenames, passwords, signed URLs, object keys, or sensitive payloads; safe service/category names only. Telegram delivery failure increments a delivery-failure metric and a `warning` alert (no second channel required at launch, DEC-180); bot token follows DEC-176.

### Regional monitoring (DEC-104)

- External monitors are configured per region where the provider supports it (e.g., probes from US/EU regions; LATAM coverage via provider availability); status components are per-region ("API: Americas", "API: Europe") rather than a single global component; launch communication uses the same regional labels. No per-user profiling: regional bucketing is at the monitor/edge level only, consistent with DEC-104 and DEC-085 (coarse edge country codes are ephemeral).

### Operational overrides and pause controls (DEC-097)

- A documented **operational override** mechanism: an owner-only, audited switch (protected VPS environment config, not repository data) that can (1) pause server-job admission, (2) pause automated status derivation and fall back to a manually declared "maintenance" state, (3) disable the alert relay, and (4) disable AI-assisted automation actions. Every override action writes an auditable log entry (who/what/when via the owner account) and is reversible. Automation never holds production credentials beyond the protected env config (DEC-176) and never performs high-risk actions (deploy, rollback, destructive cleanup outside policy, secret rotation, firewall changes) without explicit owner authorization (DEC-097, DEC-160).

## 7. Recommendation

**Recommendation (not an accepted decision):** adopt **A1 (Netdata + multi-region external uptime + Vercel status page with noise-resistant logic) + B1 (Netdata notifications + dedicated relay for application alerts)**, with the Telegram alert contract, regional component model, and DEC-097 override/pause controls described above.

Concrete signal composition for the public status components (user-relevant, EN/ES/ID copy per UX §15.4):

| Component | Signals | Noise-resistance rule |
|---|---|---|
| Website (tool pages) | External uptime of `mypapyr.com` from ≥2 regions | degraded on ≥2 failed checks within a window; down after N consecutive windows |
| API (admission/status) | External uptime of `api.mypapyr.com/health` from ≥2 regions + API `/health` | degraded/down as above; API `/health` never the sole signal for "down" (Vercel independence, DEC-119) |
| Server processing (queue/workers) | Netdata service health + queue backlog + per-tool readiness (DEC-167) | degraded when backlog > cap or any tool readiness false; wording per DEC-161 ("processing may be slower", never a completion guarantee) |
| Storage (R2 integration) | Application R2 connectivity check + cleanup lag | degraded on failed connectivity or cleanup failure streak |

Monitoring coverage list (DEC-182): API process (request rate, 5xx, latency), queue (depth, wait, exec time, failures, retries, stuck claims — C1), workers (count, per-job memory, OOM, timeouts), Redis (memory, persistence, eviction attempts, latency), processing engines (per-tool readiness, crash loops), storage integration (R2 connectivity, cleanup lag, lifecycle-rule-present), public endpoints (external uptime), host (CPU/mem/disk/network, legacy baselines), backups (C6 success/failure). No document contents, filenames, passwords, signed URLs, or object keys in any metric, log, or alert (DEC-025, DEC-175, DEC-180).

**Owner decision prompts:** (1) monitor-provider selection for external checks (BetterStack [legacy pending], UptimeRobot, or Cloudflare Health Checks) given free-tier limits and regional coverage — the evidence file compares them; (2) whether the canonical public status page is Vercel-rendered with the provider's API as signal source (recommended) or the provider's hosted page (alternative); (3) acceptance of the representative alert thresholds as launch defaults subject to telemetry adjustment (DEC-066).

## 8. Measurable acceptance criteria

1. Monitoring covers API, queue, workers, Redis, processing engines, storage integration, cleanup health, and public endpoints (DEC-182); a coverage checklist test asserts each required metric source exists.
2. No metric, log, or alert contains document contents, filenames, passwords, signed URLs, or object keys; a data-leakage guard test asserts this (DEC-025, DEC-175, DEC-180).
3. The public status page renders from non-VPS data sources; a failure-injection test (backend endpoints unavailable) asserts the page still renders and shows the API component degraded/down rather than failing to load (DEC-119).
4. Status derivation is noise-resistant: transient single-region flaps do not change public status; only sustained multi-region failures do; verified by replaying recorded check histories in a test (DEC-161).
5. Telegram alerts: each alert type is deduplicated by key; a duplicate event while the alert is open does not re-notify; resolution closes the key; verified by a contract test against the relay (DEC-180).
6. Telegram delivery failure increments a metric and raises a `warning` alert (no second channel required) (DEC-180).
7. Regional components exist for the US, LATAM, and Europe and can identify a material failure in one region without profiling users (DEC-104).
8. Override and pause controls exist, are owner-only, auditable, reversible, and disable admission/status-derivation/alert-relay/automation as documented (DEC-097); an audit-log test asserts each override records an entry.
9. Alert payloads contain no sensitive data; a message-inspection test asserts the safe category set only (DEC-180).
10. Backup failures (C6) raise a Telegram alert within the contract (DEC-181).

## 9. Assumptions, uncertainties, and unresolved questions

- **Assumption:** Netdata remains the internal monitoring choice with its existing legacy deployment patterns (runbook §10.1-10.3); the official Docker deployment requires elevated privileges (`pid: host`, host network, `SYS_PTRACE`/`SYS_ADMIN`) and a Netdata Cloud account claim at deployment time (not performed during research); the Docker socket exposure should use the documented socket-proxy pattern.
- **Uncertainty:** monitor-provider free-tier check intervals and regional probe coverage at launch; the evidence file records current published limits; final provider selection is an owner decision.
- **Uncertainty:** Telegram Bot API rate limits and current message constraints (verified in the evidence file with access date); the relay must honor `429 retry_after` and the per-chat limits.
- **Unresolved:** external monitor provider selection (owner prompt above).
- **Unresolved:** whether a manually declared "maintenance" public-status state is acceptable alongside the fully automatic derivation (DEC-161 mandates automatic derivation; a maintenance override is an exception under DEC-097 and should be owner-confirmed).

## 10. Dependencies and cross-track interfaces

- **C1:** supplies queue metrics (depth, wait, exec, failures, retries, stuck) and Redis health.
- **C3:** supplies cleanup lag and lifecycle-rule-present telemetry.
- **C4:** supplies scanner health (DB age, failures) and rate-limit/OOM signals.
- **C6:** supplies backup success/failure signals.
- **D3:** product analytics boundary stays separate from operational monitoring (DEC-025); no cross-contamination of event schemas.
- **D5:** security telemetry feeds the same alert contract without sensitive payloads (DEC-088).
- **X1/X2:** recommendation and owner prompts feed the index and reconciliation report.

## 11. Source-date log and evidence-completeness notes

- Decisions and specifications read 2026-07-31; legacy files read 2026-07-31.
- Web evidence (Netdata, uptime providers, Telegram Bot API) was researched directly (read-only official docs) and persisted in `evidence/c5-evidence-observability.md` with per-source URLs and access date 2026-07-31. This brief's §5.2 summarizes it; exact versions, limits, and API details in the evidence file prevail, and any disagreement must be surfaced (DEC-183).
- Evidence-completeness: Netdata edition/features, provider free-tier and regional limits, and Telegram Bot API rate limits are the material items recorded in the evidence file.

## 12. Prohibitions-compliance statement

No prohibited action was taken: no installs, builds, containers, server starts, VPS/SSH access, deployment, provider authentication, account creation (including Netdata Cloud, BetterStack/UptimeRobot, or Telegram bot registration), remote mutation, or benchmark program (DEC-066, DEC-060, DEC-160, DEC-172). No source, spec, decision, or existing audit-output file was modified. All writes were confined to `audit-outputs/research/track-c/`. `papyr-reference/` was verified unchanged via read-only `git -C papyr-reference status --porcelain` (empty, exit 0) before and after this brief.
