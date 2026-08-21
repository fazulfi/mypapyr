# Release checklist

Gate checklist for shipping a Papyr release. CI is never the deployment mechanism; every release passes these gates and is activated by an operator on the VPS (or by a Vercel alias move for the frontend when served from Vercel).

## 1. Branch and review

- [ ] Work is on a feature branch off `main`, never committed directly to `main`.
- [ ] Commits are atomic and grouped by concern (git history reads cleanly; each commit is independently revertible).
- [ ] `git diff origin/main...HEAD` reviewed; no unrelated files, no secrets, no `.env`/`.vercel`/key material.
- [ ] Pull request opened with: summary, scope, ADR references, test evidence, deploy + rollback plan, security/privacy impact, linked artifacts.

## 2. Local gates (must all exit 0)

Backend (from `backend/`):

- [ ] `python -m pytest -q`
- [ ] `python -m pytest --cov=app --cov-fail-under=80`
- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `python -m mypy app tests --strict --no-incremental`

Frontend (from `frontend/`):

- [ ] `npm ci`
- [ ] `npm run test:coverage`
- [ ] `npm run lint`
- [ ] `npm run format:check`
- [ ] `npm run typecheck`
- [ ] `npm run build`

Repo guard (root):

- [ ] `bash scripts/check-ci.sh`

## 3. CI gates (must all pass on the PR)

- [ ] Backend: Pytest + coverage, Ruff, Strict mypy.
- [ ] Frontend: Lint + Format, TypeScript typecheck, Vitest + Coverage, Next.js production build, Playwright E2E.
- [ ] Security: Trivy (critical/high), gitleaks full-history.
- [ ] Supply chain: dependency review, npm audit, pip-audit.
- [ ] QA: action-pin truth, compose structural, hadolint, markdownlint, production API image build + non-root smoke, shellcheck, yamllint.
- [ ] Operations guards: monitoring scope (OP-01), Telegram relay scope (OP-03), backup scope (OP-04).
- [ ] All 25 CI jobs pass on the PR (24 on pushes to main, where the PR-only dependency review is skipped; 7 status checks required by branch protection).

### 3.1 P7 operations verification (when the release carries the P7 operations scope)

Record results in the completion report alongside the CI evidence. These steps are owner-gated; a skipped step stays explicit with a written reason.

- [ ] Netdata: `deploy/monitoring/netdata-compose.yml` renders with `docker compose config --quiet`, stays internal-only (no published host ports), and `scripts/check-monitoring.sh` exits 0.
- [ ] Derived status: `frontend/src/lib/status.ts` derives availability from consecutive failures across at least two regions; the localized status page renders unavailable and unknown states without a VPS health fetch. The live multi-region snapshot producer is not wired until the owner approves the monitoring provider and thresholds (owner gate).
- [ ] Telegram relay: `scripts/check-telegram-relay.sh` exits 0; a dry-run (`--dry-run`) sends nothing and exits 0. If the bot token and chat id are unprovisioned, the relay stays skipped and the skip is recorded as an owner-gated pending action.
- [ ] Backup: `scripts/check-backup.sh` exits 0; daily restic (`deploy/backup/restic-backup.sh`) runs against a scratch repository with the allowlist scope manifest, and the monthly isolated restore drill (`deploy/backup/restore-drill.md`) is executed on a scratch repository until a live repository exists.
- [ ] Environment provisioning: every new variable in `deploy/.env.production.example` has a real value in the production env file (`PAPYR_ENV_FILE`), approved by the owner; no empty or `__SET_ME__` value ships to the VPS.
- [ ] Non-root runtime: the production API image runs with a non-root user, read-only root filesystem, and dropped capabilities (the CI `qa-production-api` job is the gate; a local smoke is optional extra evidence).
- [ ] PR/CI gates: the P7 PR is open with all 25 CI jobs green and an owner-approved merge; nothing deploys until the owner clears the gates and the release build in Section 4 passes.

## 4. Release build (VPS)

- [ ] Pull the release commit into `/opt/mypapyr/ci/mypapyr` (or equivalent staging clone) and reset to the exact commit.
- [ ] Build the frontend with production env (`NEXT_PUBLIC_API_BASE_URL=https://api.mypapyr.com`); record the `BUILD_ID` (current: `HHzujraVbxQa5Q0LcI4dZ`).
- [ ] Build `papyr-api` (`Dockerfile.production`, context `backend/`) and `papyr-workers` (`Dockerfile.worker`, context = repo root) locally; record digests.
- [ ] Stage the release directory under `/opt/mypapyr/releases/<name>`; `chown -R mypapyr:mypapyr`.
- [ ] Write `deploy/image-manifest.env` with digest-form image references + `PAPYR_ENV_FILE=/opt/mypapyr/production/.env`.
- [ ] Validate: `docker compose ... config --quiet` exits 0.
- [ ] Record the rollback point (previous frontend release dir + BUILD_ID, previous image digests, previous manifest) before activation.

## 5. Activation

Backend:

- [ ] `docker compose -p papyr-app --project-directory <rel>/deploy --env-file <rel>/deploy/image-manifest.env -f docker-compose.yml -f /opt/mypapyr/production/compose.override.yml --profile app --profile queue up -d --pull never` exits 0.
- [ ] All `papyr-app-*` containers healthy; `curl localhost:3016/health` → 200.

Frontend (VPS-hosted):

- [ ] Update `WorkingDirectory` in `/etc/systemd/system/mypapyr-web.service` to the new release (it is hardcoded, not symlink-resolved).
- [ ] `systemctl daemon-reload && systemctl restart mypapyr-web`.
- [ ] `systemctl is-active mypapyr-web` → active; `curl localhost:3017/` → 307, `/en` → 200.
- [ ] Verify served `BUILD_ID` matches the release (read the process cwd).

Frontend (Vercel-hosted, when applicable):

- [ ] Alias the verified production deployment to the custom domain; record pre/post deployment URLs and BUILD_IDs.

## 6. Post-deploy verification

- [ ] `nginx -t` (read-only) passes before any reload; never reload nginx broadly on the shared host.
- [ ] Public verification via Cloudflare: `GET https://mypapyr.com/` → 307; `/en` `/es` `/id` → 200; `https://api.mypapyr.com/health`, `/health/ready`, `/api/v1/capabilities` → 200.
- [ ] Content markers for the release (e.g. sitemap URL count, hreflang/canonical, contact copy) verified live.
- [ ] Ad-slot verification (all-pages policy): exactly one reserved-dimension ad marker present on `/en` (homepage), on a tool page after the result phase, and on supporting pages including `/en/status` and `/en/blog`; no slot beside the Download control.
- [ ] Rollback target recorded in `/opt/mypapyr/production/rollback/<release>-rollback.md` and in the repo evidence.

## 7. Post-release

- [ ] Completion report written (evidence, gates, deployment, verification, rollback target, known limitations, manual actions) naming both releases (backend `p6-complete-*`, frontend `p6-ads-all-*`) and the BUILD_ID.
- [ ] Documentation reconciled: README capability table, roadmap, AGENTS.md facts, integrations, environment-variables, api-reference.
