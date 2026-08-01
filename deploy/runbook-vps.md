# Papyr VPS Runbook — Outline (Phase 0 / FD-03)
#
# This is an OUTLINE only. Each section is a placeholder for the operational
# steps that will be written up in a later wave once we know the real VPS
# host, deploy user, and image registry. Do NOT record any real host, IP,
# domain, or credential here.

## 0. Scope
- Phase 0 foundation scaffolding only.
- Deploys the 4-service skeleton from `deploy/docker-compose.yml`
  (nginx, api, redis, workers). A scanner service is intentionally
  deferred to SEC-03 — see `audit-outputs/phase-0/phase-0-execution-dag.md`.

## 1. Operator identity (DEC-172)
- All on-host actions are performed by a dedicated non-root operator.
- The operator is added to the `docker` group (or equivalent) so they can
  run `docker compose` without `sudo`. The root account is not used for
  routine deploy operations.
- SSH to the VPS uses key-based auth only; password auth is disabled.

## 2. Prerequisites
- [ ] VPS provisioned (real host / IP captured out-of-band, not in this file).
- [ ] DNS A/AAAA records pointed at the VPS (real FQDN captured out-of-band).
- [ ] Firewall allows 80/443 inbound; SSH restricted to operator IPs.
- [ ] Docker Engine + Compose plugin installed at the OS level.
- [ ] Operator account present, in the `docker` group, passwordless sudo
      disabled for deploy actions.

## 3. Files to place on the VPS
- [ ] `/opt/papyr/deploy/docker-compose.yml` — copy from repo.
- [ ] `/opt/papyr/deploy/nginx/conf.d/production.conf` — copy from repo.
- [ ] `/opt/papyr/deploy/.env.production` — provisioned out-of-band, mode 0600,
      owned by the operator (DEC-176). NEVER copied from
      `.env.production.example`.
- [ ] Image pull secret (if using a private registry) — provisioned out-of-band.

## 4. First-boot sequence (placeholder)
- [ ] Pull images: `docker compose -f /opt/papyr/deploy/docker-compose.yml pull`.
- [ ] Validate config: `docker compose -f ... config` (human review).
- [ ] Bring up the app profile: `docker compose --profile app up -d`.
- [ ] Bring up the edge profile: `docker compose --profile edge up -d`.
- [ ] Tail logs: `docker compose -f ... logs -f --tail=200`.

## 5. Day-2 operations (placeholder)
- [ ] Rolling restart: `docker compose --profile app up -d --no-deps api`.
- [ ] Inspect Redis: `docker compose exec redis redis-cli ping`.
- [ ] Reload nginx config: `docker compose exec nginx nginx -s reload`.
- [ ] Rotate `.env.production`: out-of-band, then restart affected services.

## 6. Incident triage (placeholder)
- [ ] Capture `docker compose ps` and `docker compose logs --since 1h`.
- [ ] Capture `df -h`, `free -m`, `uptime` on the host.
- [ ] Escalate to on-call with the captured bundle; do not paste secrets.

## 7. Out of scope (deferred)
- TLS termination and cert provisioning (SEC-03 alongside the scanner service).
- Backup schedule for the Redis volume.
- Observability stack (metrics, traces, alerting).
- CI/CD wiring from this repo to the VPS.