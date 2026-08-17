# Papyr alert contract — Telegram incident relay (OP-03)

**Scope.** OP-03 is the operator incident paging path: a privacy-safe Telegram
relay (`deploy/monitoring/telegram-relay.py`) that consumes the OP-01
health-signal vocabulary (and the fixed backend monitor report JSON,
`backend/app/ops/monitor.py`) and sends a Telegram message only for
**critical** signals. It is the incident path named in
`deploy/monitoring/health-signals.md`: `warn -> warning` is review-only and
never paged; `fail -> critical` triggers this relay.

**Authority.** The backend monitor schema and the OP-01 health-signal contract
are NOT modified here. This contract names, bounds, and owns the relay's
message payload, cadence, retry, and permanent-failure behaviour only.

## Delivery seam

The relay is standalone (standard library only) and runs from a cron/systemd
timer or the monitoring host. Delivery options:

- **Telegram Bot API** (default): `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
  come from the environment only — never from arguments or committed files.
- **`--sender-script PATH`**: an external command receives the message text on
  stdin and exits `0` (accepted), `2` (permanent failure), or any other code
  (transient, retryable). This is the offline-safe test seam and an operator
  substitution point.
- **`--dry-run`**: prints the message and updates alert state; never sends and
  never requires credentials.

Exit codes are stable: `0` success (or dry-run), `1` transient failure after
retries, `2` configuration/input error, `3` permanent-failure marker present
or just written.

## Message payload

The relay transmits, per critical check: the check **name**, the **status**
(`fail`), the ISO **generated_at** of the report, and the closed detail fields
from the allowlist below. Counts from the report `summary` (ok/warn/fail) may
accompany. Everything else in the report is ignored.

<!-- ALERT-PAYLOAD-ALLOWLIST-START -->
status, status_code, error_class, count, pending, oldest_idle_ms, group_exists, worker_probe, age_seconds, reason, region, consecutive_failures, state
<!-- ALERT-PAYLOAD-ALLOWLIST-END -->

The allowlist above is the closed field vocabulary shared with the OP-01
signal contract. It is additive-only; removing or renaming an entry is a
contract change. Non-scalar values (nested maps, lists, bytes) are dropped,
never rendered.

## Alert behaviour

- **Alert** on a critical (`fail`) transition.
- **Reminder (repeat)** after `--cooldown` seconds (default 3600 s) while the
  check stays critical.
- **Deduplicated** within the cooldown window; per-check alert state persists
  to `--state` (JSON) so restarts cannot double-page.
- **Recovery** message when a previously-critical check leaves critical.
- **Retry**: transient failures (network, HTTP 429/5xx, sender-script
  non-2/non-0 exit) are retried up to `--max-attempts` (default 3) with
  `--retry-delay` seconds between attempts (default 5 s). A message is marked
  sent only after confirmed delivery, so a transient failure re-alerts on the
  next run.
- **Permanent failure**: HTTP 400/401/403/404/410 (bad token, bad chat id,
  bot blocked) or a sender-script exit `2` writes a permanent-failure marker
  (default `<state>.permanent-failure`) and stops paging. A marker present at
  startup fails closed with exit `3` and sends nothing until the operator
  clears the marker after fixing the channel.

## Privacy boundary

Alerts carry operational aggregates only (DEC-175, DEC-182). A message never
carries, and the relay source must never emit:

<!-- ALERT-PRIVACY-REJECTED-TERMS-START -->
filename, document name, document content, extracted text, object key, signed url, password, token, payload, document metadata
<!-- ALERT-PRIVACY-REJECTED-TERMS-END -->

In concrete terms:

- **No filenames or document terms.** Uploaded file names, extracted text, and
  content-derived values never reach a message.
- **No object keys or signed URLs.** R2 object keys and download grants never
  reach a message.
- **No credentials.** The bot token and chat id come from the environment and
  are never logged, printed, or committed; only the HTTP status class is
  surfaced.
- **No payload fields.** Queue/upload payload bodies and request contents are
  never transmitted.
- **Exception classes, not messages.** Check details carry exception class
  names, status codes, counts, and booleans only.

## Operational posture

- The relay never sends in `--dry-run`; credentials are required only for a
  live send and fail closed (exit `2`) when absent.
- State and marker files are operator-owned paths on the monitoring host —
  never committed, never world-writable by the relay itself beyond the
  invoking user's permissions.
- Provisioning the bot token/chat id is an owner-gated, out-of-band action
  (R-12/G-4), consistent with `docs/integrations.md` ("environment contract
  only") and `docs/ops-runbook.md` ("Alert wiring (placeholders)").
- Guard: `scripts/check-telegram-relay.sh` asserts the relay's structural
  contract offline (stdlib-only, allowlist equality with this document, no
  committed secrets, no placeholders, marker/cooldown/retry behaviour
  present). Runtime `docker compose`/cron wiring belongs on the deployment
  host.
