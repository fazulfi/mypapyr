# C5 Evidence — Netdata, External Uptime/Status Providers, Telegram Bot API

- **Access date:** 2026-07-31
- **Purpose:** primary-source evidence for `c5-observability-status-telegram.md` (monitoring, status signals, Telegram alerting)
- **Method:** read-only fetch of official documentation. No accounts created, no bots, no live API calls.

## 1. Netdata

Source: `https://learn.netdata.cloud/docs/netdata-agent/installation/docker` (accessed 2026-07-31; page "Last updated on Jul 23, 2026"). Related pages referenced: `https://learn.netdata.cloud/docs/netdata-agent/` and alerts/notifications docs.

- Official image `netdata/netdata`; tags `stable` (recommended), `edge`, `latest` (may be nightly), `vX.Y.Z` etc.
- Docker deployment requires **elevated privileges and mounts** for full host monitoring: `pid: host`, `network_mode: host`, `cap_add: SYS_PTRACE, SYS_ADMIN`, `security_opt: apparmor:unconfined`, mounts of `/`, `/proc`, `/sys`, `/etc/passwd`, `/etc/group`, `/var/log`, `/var/run/docker.sock` (ro), `/run/dbus`; persistent volumes for `/etc/netdata` (config), `/var/lib/netdata` (dbengine data), `/var/cache/netdata`.
- **Docker socket security:** docs recommend a Docker **socket proxy** (HAProxy/CetusGuard) restricting access to the `/containers` endpoint (read-only) instead of mounting the socket directly. Rootless Docker limits collection (some plugins unavailable).
- Health check: container polls `http://localhost:19999/api/v1/info` by default (`NETDATA_HEALTHCHECK_TARGET`); `cli` mode uses `netdatacli ping`.
- Telemetry opt-out: `DISABLE_TELEMETRY=1` / `DO_NOT_TRACK=1`.
- Out-of-box collectors include system (CPU/mem/disk/net), Docker containers, Nginx, Redis, and go.d.plugin modules (docker, weblog for access-log tailing, systemd units); custom app charts are addable. Data retention via dbengine (Netdata parents/streaming for longer retention, referenced).
- Alerts: agent-side health/alarm configuration with WARNING/CRITICAL thresholds and ML/anomaly detection (Netdata AI, referenced); notifications integrate via Netdata Cloud and notification integrations.
- **Netdata Cloud:** requires an account and a claim step (`netdata-claim.sh`; legacy runbook §10.2). Not performed during research — it is a deployment-time owner action.

## 2. External uptime / status page providers

### BetterStack (Uptime + Status Pages)

Sources: `https://betterstack.com/docs/uptime/getting-started-with-status-pages/` and `https://betterstack.com/docs/uptime/api/` (accessed 2026-07-31).

- Status page = a dedicated page informing users about outages and scheduled maintenance.
- Public status pages hosted by BetterStack; monitors (HTTP/ping etc.) drive status; incidents/maintenance handling; multi-region/global checks (exact probe-region coverage verified at signup — account creation not performed).
- API v2 (`https://uptime.betterstack.com/api/v2/status-pages`, monitors API) allows programmatic creation/updating of status pages and monitors → supports automated status derivation (DEC-161) from an external system.
- Legacy note: `papyr-reference/docs/runbook-vps.md:10.4` lists BetterStack Uptime as pending with planned monitors.

### UptimeRobot

Sources: `https://uptimerobot.com/status-page/`, `https://uptimerobot.com/api/`, `https://uptimerobot.com/pricing/` (accessed 2026-07-31).

- Free tier: monitors and basic public status pages; status page customization limited on free plans; alert contacts/integrations limited.
- REST API for monitor management; monitors can be HTTP/HEAD/ping etc.
- Free-tier check interval and region coverage details verified at signup (not performed).

### Cloudflare Health Checks

Source: `https://developers.cloudflare.com/health-checks/` (accessed 2026-07-31, referenced).

- Cloudflare-side health checks of origins from multiple locations; notifications via webhooks/email; useful for origin health, but a public status page still needs a rendering surface (Vercel per DEC-119) and multi-provider independence is stronger with a dedicated status provider.

## 3. Telegram Bot API

Sources: `https://core.telegram.org/bots/faq` (accessed 2026-07-31) and `https://core.telegram.org/bots/api` (referenced).

- **Rate limits (official FAQ, "My bot is hitting limits, how do I avoid this?"):**
  - "In a single chat, avoid sending more than one message per second. We may allow short bursts that go over this limit, but eventually you'll begin receiving 429 errors."
  - "In a group, bots are not able to send more than 20 messages per minute."
  - "For bulk notifications, bots are not able to broadcast more than about 30 messages per second" (free; paid broadcasts exist but require Stars and are irrelevant here).
- 429 responses: the API returns a `retry_after` field; the relay must honor it with backoff (documented in the Bot API `sendMessage` docs, referenced).
- `sendMessage` parameters: `chat_id`, `text`, `parse_mode` (`HTML`/`MarkdownV2`), `disable_web_page_preview`, `disable_notification`, `reply_parameters`. Message length limit **4096 characters** for text messages (Bot API reference).
- Delivery detection: `sendMessage` returns an error on failure (e.g., chat not found, bot blocked); webhook/long-polling only matter for receiving updates, which Papyr does not need for outbound alerts.
- Bots cannot initiate conversations: the owner must start the bot and send an initial message so the chat_id is known (documented bot behavior).
- Bot token format `<bot_id>:<auth_hash>`; token compromise → revoke via @BotFather (referenced). Token handling per DEC-176 (protected VPS env, never in client code).
- Legacy: `<telegram-bot>` → chat ID `<telegram-chat-id>` (runbook §10.3).

## Uncertainties

- Current Netdata stable version number and Netdata Cloud free-plan limits: verify at signup/deployment (account creation is a deployment-time owner action, not performed in research).
- BetterStack/UptimeRobot free-tier monitor counts, check intervals, and probe regions: verify at signup; the C5 brief treats provider selection as an owner decision.
- Telegram message-length and rate-limit values may change; the evidence above is current as of the access date.

## Source list

| # | URL | Accessed |
|---|---|---|
| 1 | https://learn.netdata.cloud/docs/netdata-agent/installation/docker | 2026-07-31 |
| 2 | https://betterstack.com/docs/uptime/getting-started-with-status-pages/ | 2026-07-31 |
| 3 | https://betterstack.com/docs/uptime/api/ | 2026-07-31 |
| 4 | https://uptimerobot.com/status-page/ | 2026-07-31 |
| 5 | https://uptimerobot.com/api/ | 2026-07-31 |
| 6 | https://uptimerobot.com/pricing/ | 2026-07-31 |
| 7 | https://developers.cloudflare.com/health-checks/ | 2026-07-31 (referenced) |
| 8 | https://core.telegram.org/bots/faq | 2026-07-31 |
| 9 | https://core.telegram.org/bots/api | 2026-07-31 (referenced) |
