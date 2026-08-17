# P6 Completion Report — Enterprise Scope

- **Date**: 2026-08-17
- **Branch**: `feat/full-p6-enterprise-completion` @ `cf56039`
- **PR**: [fazulfi/mypapyr#46](https://github.com/fazulfi/mypapyr/pull/46) — CI 19/19 green (run 32002627224)
- **Deployed release**: `p6-complete-1786951216` on faiz-prod (82.25.62.204), active 2026-08-17.

## Scope delivered

| Workstream | Scope | Status |
| --- | --- | --- |
| WS-1 | Privacy: DNT/GPC opt-out gates Vercel Analytics + Speed Insights before any event leaves the browser (ADR-01) | ✅ |
| WS-2 | PT-04: encrypted-PDF password handling wired end-to-end into Merge — client detection (`isEncryptedPdf`, first 4 KiB), per-file `PasswordInput`, per-index `password_<i>` multipart fields, backend sanitizer password stage with distinct `error.wrongPassword` envelope; passwords never persisted/logged (DEC-174) | ✅ |
| WS-3 | Ads: one reserved-dimension unit per page (ADR-03), explicit phase/immediate guard (G12), house-promo fallback (ADR-04), `e2e/ad-behavior.spec.ts` (presence/absence/DNT-GPC/fallback), a11y E2E isolated from third-party ad network | ✅ |
| WS-4 | Contact (PT-03): accurate trilingual copy (contact + cookies-and-advertising), env-var contract for Cloudflare Email Sending/Turnstile/scanner, `POST /api/v1/support/contact` documented in api-reference, integrations.md reconciled (Adsterra reality, ClamAV, CF Email, Turnstile, Vercel Analytics) | ✅ |
| WS-5 | SEO (ADR-06, canonical = budgezen.com): hreflang alternates + canonical in `generateMetadata`, per-locale sitemap (42 URLs), robots aligned, tests | ✅ |
| WS-6 | Docs reconciliation: roadmap self-contradiction removed, README legend + claims, product/architecture specs, AGENTS.md facts (9 routers, proxy.ts, 19 CI jobs), test counts, ADR-03/05 claims alignment | ✅ |
| WS-7 | Typecheck hardening (ADR-09): fixed 5 pre-existing `tsc --noEmit` errors (incl. @vercel/speed-insights `BeforeSendEvent` import), new `frontend-typecheck` CI job, `typecheck` npm script | ✅ |
| BLOCKED-B | Backend security audit re-run with command evidence; fixed 2 gate-blockers (FakeR2 mypy overrides, /ID flake), verified product code security-sound + fail-closed | ✅ |
| BLOCKED-D | Deployment topology resolved: mypapyr.com = VPS (systemd Next.js :3017), api.mypapyr.com = VPS (docker api :3016), budgezen.com = Vercel; deployment executed against the VPS target | ✅ |

## Evidence and gate results

- Backend: 1360 passed / 44 opt-in skips; coverage 89.38% (gate 80%); ruff check + format clean; mypy strict clean — verified locally and in isolated VPS containers at the CI pins.
- Frontend: 780 tests / 52 files; coverage stmts 91.27% / branches 86.15% / funcs 91.71% / lines 93.10%; lint, format, typecheck, production build clean; Playwright E2E green (including the new ad-behavior spec and the ad-isolated a11y spec).
- CI: all 19 jobs green on PR #46 — Backend trio, Frontend five, Security (Trivy, gitleaks), Supply chain (dependency review, npm audit, pip-audit), QA (pins, compose, hadolint, markdownlint, image build+non-root smoke, shellcheck, yamllint).
- gitleaks full-history: clean (after allowlisting the retired `frontend/public/adtest.html` diagnostic page and renaming a test fixture variable).
- markdownlint: clean on all tracked docs.

## Deployment and verification

- Backend activated via `docker compose up -d --pull never` with new digest images (`papyr-api` `db08adf2…`, `papyr-workers` `0d39493b…`); redis + clamd untouched; all containers healthy.
- Frontend activated via symlink + systemd unit `WorkingDirectory` update (unit file hardcodes the release path — not symlink-resolved); process cwd verified; BUILD_ID `di0s7rcjmp_ln79MZXoFZ`.
- `nginx -t` passes (warnings are pre-existing shared-host vhost overlap).
- Public verification (Cloudflare): `/` → 307 → `/en`; `/en` `/es` `/id` → 200; `api.mypapyr.com/health` + `/health/ready` + `/api/v1/capabilities` → 200; hreflang `en/es/id/x-default` → budgezen.com; canonical → budgezen.com/en; sitemap 42 URLs; ad-slot marker present on `/en` and `/en/privacy`; contact copy accurate.
- Rollback target recorded in `/opt/mypapyr/production/rollback/p6-complete-1786951216-rollback.md` (previous release `ads13-1786819926`, previous API/workers digests, previous manifest) and in the repo evidence.

## Known limitations and manual actions

1. **Cloudflare Email Sending credentials are not provisioned in production** (owner out-of-band action). Contact submissions are validated, accepted (202), and delivery failures are counted only. Provision `CF_EMAIL_API_TOKEN` + verify `CF_EMAIL_ACCOUNT_ID` in `/opt/mypapyr/production/.env` to enable delivery.
2. **`TURNSTILE_SITE_SECRET` / `NEXT_PUBLIC_TURNSTILE_SITE_KEY` are not provisioned** — the challenge is silently skipped (soft gate). Provision both to enable the anti-bot challenge.
3. **Contact rate limiting is in-memory (3/60 s per process)** — documented acceptable for the current single-process API; migrate to a Redis counter (pattern from `fair_use.py`) before horizontal scaling.
4. **Adsterra env vars (`ADSTERRA_PUBLISHER_ID`/`PLACEMENT_IDS`/`API_KEY`) are a dead contract** — zone keys are hardcoded in `frontend/src/lib/ads.ts` (public client-side constants by design).
5. **budgezen.com remains on Vercel** serving the previously deployed build; this release was deployed to the VPS (mypapyr.com + api.mypapyr.com). Promoting this build to budgezen.com is a separate Vercel alias action.
6. **No alerting yet** (Sentry/Telegram) — monitor probes exist (`ops-runbook.md`); provisioning is a separate task.
7. **R2 lifecycle policy** on the live bucket is a separately authorized operator action (`deploy/r2-lifecycle.json`).
