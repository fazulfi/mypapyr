# Integration inventory

This public inventory lists the external services and dependencies the repository integrates with, without credentials or private operational identifiers. A listed integration is not evidence that production wiring is complete; the "Repository status" column records what the source tree proves.

| Integration | Purpose | Repository status |
| --- | --- | --- |
| GitHub | Source hosting, pull requests, and CI | Active for this repository |
| Vercel | Frontend hosting, status surface, Analytics, Speed Insights | Implemented in repository: privacy-gated `<Analytics/>`/`<SpeedInsights/>` in the root layout |
| Cloudflare | DNS, TLS, edge proxying, and coarse abuse controls | Configuration contract documented |
| Cloudflare R2 | Temporary object storage for server-processed documents | Implemented in repository: client, signed downloads, cleanup, and lifecycle template |
| Cloudflare Email Sending | Best-effort async delivery of contact submissions | Implemented in repository: REST client, payload contract, counts-only metrics; delivery gated on dashboard onboarding plus `CF_EMAIL_API_TOKEN` |
| Cloudflare Turnstile | Bot gate on the contact form | Implemented in repository: client render (opt-in site key) + server `siteverify` (soft gate, opt-in secret) |
| VPS and Nginx | API, Redis, and bounded worker hosting | Public-safe templates only |
| Redis | Durable queue and minimal task-state store | Implemented in repository: Streams queue, task store, and one-worker processing |
| Ghostscript | Compress PDF engine, invoked as an official unmodified subprocess | Implemented in branch: pinned 10.07.1 build in the worker image; pending merge/deployment |
| ClamAV (clamd) | Threat scanning of uploads | Implemented in repository: scanner gate wired via `CLAMD_HOST`/`CLAMD_PORT`/`SCANNER_ENABLED` |
| AI gateway | Planned model gateway for explicitly specified server features | Environment contract only |
| Sentry | Planned sanitized application error reporting | Environment contract only |
| Telegram | Planned operational incident alerts | Environment contract only |
| S3-compatible backup storage | Planned encrypted operational backups | Environment contract only |
| Adsterra | Native advertising units, frontend-only | Implemented in repository: reserved-dimension slots, lazy client injection, placement guards, house-promo fallback |

## Integration rules

- Secrets are provisioned outside the repository.
- Public templates use placeholders only.
- User document contents, filenames, passwords, signed URLs, and extracted text must not be sent to analytics, error monitoring, alerting, or advertising services.
- Temporary object storage must use opaque keys and deterministic expiry.
- CI never authenticates to or mutates production integrations.
- Value-level configuration is verified during a separately authorized release procedure.

## Ghostscript

The compression workflow uses the official, unmodified Ghostscript distribution, implemented in the feature branch. Papyr invokes it as a separate hardened server-side subprocess with pinned versions (10.07.1, checksum-verified at image build) and bounded execution. The project does not fork, modify, vendor, or link Ghostscript source into its application code.

## Redis

The repository implements Redis as the durable queue and minimal task-state store. A `jobs` stream with a `workers` consumer group carries only minimal task metadata — never document bodies, passwords, signed URLs, or extracted text — and each worker instance processes one in-flight job with automatic recovery of stale claims. The queue is bounded at 2,000 entries with a 900-second oldest-wait ceiling, and adaptive fair-use controls keyed by SHA-256 origin fingerprints enforce per-origin concurrency and frequency limits with allow, delay, challenge, and reject levels, failing closed when Redis is unavailable. Every task record carries a TTL within the one-hour retention target, and the approved operating contract pins a bounded-memory `noeviction` configuration.

## Cloudflare R2

The repository implements temporary object storage for server-processed documents. Objects are stored under opaque, non-identifying keys in a dated prefix, and uploads mirror the artifact deadline with an 8,192-byte ASCII metadata limit. Download grants are presigned URLs capped at 300 seconds or the remaining artifact lifetime, whichever is shorter, and never extend beyond the one-hour retention target. A cleanup coordinator actively removes source, intermediate, and result objects at their hard 3,600-second deadline before deleting task records, with counts-and-timing telemetry only. R2 lifecycle expiration is day-granular, so its one-day-minimum template on the temporary and multipart prefixes is an independent safety net, not an extension of or substitute for application-driven cleanup.

## ClamAV (clamd)

The API and worker images reach a ClamAV daemon for the upload threat gate. `CLAMD_HOST` (default `localhost`, overridden to the `clamd` service DNS in compose) and `CLAMD_PORT` (default `3310`) wire the client; `SCANNER_ENABLED=false` is the explicit opt-out when no scanner is deployed. Blocking verdicts map to stable statuses: `MALICIOUS`/`ACTIVE_CONTENT` → 403, `INDETERMINATE` → 500, scanner unavailable → 429 (fail-closed).

## Advertising (Adsterra, frontend-only)

The repository implements a single Adsterra unit per page with reserved dimensions to prevent layout shift (`frontend/src/components/ads/AdSlot.tsx`). Six owner-approved zones are hardcoded in `frontend/src/lib/ads.ts` as public client-side keys: 300x250 box, 728x90 leaderboard, 320x50 mobile banner, 468x60 banner, 160x600 skyscraper, and 160x300 half-page. The slot is injected lazily on the client inside the slot div (zone `atOptions` config followed by `invoke.js`), never beside the Download control, and gated by `allowedAdPages`: the homepage, all five tool pages, and the contact, privacy, terms, cookies-advertising, roadmap, and faq supporting pages. The status and blog pages stay ad-free. When the provider iframe errors or no-fills within 5 seconds, the reserved slot renders a localized first-party house promo (internal link, no analytics, no external requests) — provider ads are never claimed to be fixed. Ad delivery is disabled under the browser's Do Not Track header, Global Privacy Control, or the `_papyrAdsDisabled` flag (`isAdEnabled`, `frontend/src/lib/ads.ts:131-153`). Ad presence is tracked only through the privacy-reviewed analytics schema; user documents, filenames, and passwords are never sent to the advertising provider.

## Cloudflare Email Sending

Contact submissions are delivered by the Cloudflare Email Sending REST API (PT-03). The backend POSTs to `https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send` with `Authorization: Bearer <CF_EMAIL_API_TOKEN>` and a JSON body shaped `{to, from: {address, name}, reply_to: {address, name}, subject, text, html}` (`backend/app/services/contact_service.py:217-226`; `backend/app/routers/support.py:201-222`). The account id falls back to `R2_ACCOUNT_ID` when `CF_EMAIL_ACCOUNT_ID` is unset.

Delivery is best-effort and asynchronous: the endpoint returns `202` before the provider call runs in a FastAPI background task, and provider failures increment a counts-only `delivery_failures` metric (never content, never a client error). Real outbound mail requires:

- a valid `CF_EMAIL_API_TOKEN` (without it the task counts a failure — the API never fails fast on it);
- dashboard onboarding: a verified sending domain (matching `CONTACT_FROM_DOMAIN`) and a token granted the Email Sending permission.

Provider errors surface only as an exception class name in server logs. Non-2xx responses raise through `httpx.raise_for_status()`, so the standard HTTP error vocabulary applies: 401/403 (missing or insufficient token permission), 404 (unknown account id or unverified route), and 429 (rate limit). Papyr's privacy contract applies before the payload is built: message and email are PII by nature and allowed in the email payload, but never logged and never included in API envelopes.

## Cloudflare Turnstile

The contact form uses Turnstile as a client-side render plus server-side `siteverify` pair (PT-03). On the client, the widget script is injected only when `NEXT_PUBLIC_TURNSTILE_SITE_KEY` is set, and the widget renders explicitly into a reserved container; without a token the client blocks submission with a localized message (`frontend/src/components/support/ContactForm.tsx:75-150,202-206`). On the server, `TURNSTILE_SITE_SECRET` opts the endpoint into `POST https://challenges.cloudflare.com/turnstile/v0/siteverify` with `{secret, response, remoteip}` (`backend/app/routers/support.py:225-254`).

Turnstile is a **soft gate**: a missing token or failed verification increments `metrics.turnstile_rejections` but the submission is still accepted and delivered — the API never rejects on Turnstile. Tokens are single-use and valid for roughly 300 seconds, which bounds the form lifetime between widget render and submit. Client-side block and server-side count together mean a misconfigured key degrades to counting, never to blocking legitimate contact.

## Vercel Analytics and Speed Insights

The root layout renders privacy-gated `<Analytics />` and `<SpeedInsights />` from `@vercel/analytics/next` and `@vercel/speed-insights/next` (`frontend/src/components/PrivacyAnalytics.tsx`). Both pass a `beforeSend` callback that returns `null` (Analytics) or `false` (Speed Insights) when `isOptedOut()` is true, dropping the event before it reaches Vercel's collector. The opt-out check honors the browser's Do Not Track header, Global Privacy Control, and the app-level `_papyrAnalyticsOptOut` flag, and runs at event-send time so late opt-out is honored.

Custom events go through the closed-field redaction pipeline (`frontend/src/lib/analytics.ts`): `trackEvent` redacts payloads to the allowed schema, coerces values that look like document filenames to a stub, maps raw error strings to a closed `errorCategory` enum, and is a no-op under SSR or when no `window.va` sink exists. Document content, filenames, passwords, signed URLs, and extracted text are never sent (PT-01, DEC-025/DEC-117/DEC-174/DEC-175).
