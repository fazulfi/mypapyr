# FD-03 Execution Record — DEPLOY workspace scaffold (Phase 0)

This file is the **primary deliverable** for FD-03. A chat-only summary is
insufficient per AGENTS.md.

- **Date:** 2026-08-01
- **Atomic unit:** FD-03 (DEPLOY workspace scaffold)
- **Phase:** 0 — Foundation
- **Workdir:** `<workspace-root>`
- **TDD posture:** manual RED → GREEN (platform TDD skill id unavailable on
  this workstation). Docker is absent; the regression test is a pyyaml
  structural check (`python -c "import yaml; ..."`).

## 1. Skills loaded + why

| Skill | Why |
| --- | --- |
| `context-grooming` | Multi-step atomic work; need lean, recoverable record. |
| `ocs-delegation-gate` | All non-trivial work delegated with verification. FD-03 is small enough to execute inline, but the gate rules still apply to every delegation prompt. |
| `ocs-markdown-autofix` | The deliverable file (`fd-03-execution-record.md`) is a markdown plan/record file that lives under `audit-outputs/`. |
| `ocs-runtime-validation` | Per AGENTS.md, runtime evidence is required before claiming completion. The pyyaml structural check is the runtime evidence in lieu of `docker compose config`. |
| `git-master` | Every git probe is prefixed `GIT_MASTER=1`; read-only probes only. |

No delegation was actually launched for FD-03 — the work fits a single
inline pass with strict RED/GREEN evidence. The delegation gate is still
honored by keeping every step verifiable and persisted.

## 2. Pre-flight legacy invariant evidence

Commands run **before any file under `deploy/` was created**:

```
$ GIT_MASTER=1 git -C papyr-reference status --porcelain
(empty)
exit: 0

$ GIT_MASTER=1 git -C papyr-reference rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
exit: 0
```

Interpretation: `papyr-reference/` is clean and pinned at the canonical
HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`. Work is authorized to
proceed.

Local tool inventory snapshot:

```
$ command -v docker
docker: NOT FOUND  (and `docker --version` → command not found)

$ python -c "import yaml; print(yaml.__version__)"
6.0.3
```

## 3. Docker-absent fallback rationale

`docker compose config` is the canonical regression test for a compose
file. It cannot run on this workstation (binary absent). The substituted
regression test is a pyyaml structural check:

- Parse `deploy/docker-compose.yml` with `yaml.safe_load`.
- Assert `sorted(d['services'].keys()) == ['api','nginx','redis','workers']`.
- Assert `'scanner' not in d['services']` (scanner service deferred to SEC-03).
- Assert `len(d['services']) == 4`.

This is intentionally weaker than `docker compose config` — it does not
validate the Compose schema or env interpolation. It only catches the
shape errors that matter for FD-03 (parseability + the service-name
invariant). Stronger validation moves to the deploy wave when Docker is
available.

## 4. RED evidence (before any deliverable file exists)

Exact command:

```
python -c "import yaml,sys; p='<workspace-root>/deploy/docker-compose.yml'; d=yaml.safe_load(open(p)); expected=sorted(['api','nginx','redis','workers']); got=sorted(d['services'].keys()); assert got==expected, f'services mismatch: got {got} expected {expected}'; print('SERVICES_OK', got)"
```

Exact output:

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import yaml,sys; p='<workspace-root>/deploy/docker-compose.yml'; d=yaml.safe_load(open(p)); expected=sorted(['api','nginx','redis','workers']); got=sorted(d['services'].keys()); assert got==expected, f'services mismatch: got {got} expected {expected}'; print('SERVICES_OK', got)
                                                                                            ~~~~^^^
FileNotFoundError: [Errno 2] No such file or directory: '<workspace-root>/deploy/docker-compose.yml'
exit: 1
```

Interpretation: the regression test correctly fails because the file
under test is absent. RED captured.

## 5. GREEN evidence (after files written)

Command A — sorted services + name + volumes:

```
$ python -c "import yaml; d=yaml.safe_load(open('<workspace-root>/deploy/docker-compose.yml')); expected=sorted(['api','nginx','redis','workers']); got=sorted(d['services'].keys()); assert got==expected, 'services mismatch: got %s expected %s' % (got, expected); print('SERVICES_OK', got); print('NAME_OK', d.get('name')); print('VOLUMES_OK', sorted(d['volumes'].keys()))"
SERVICES_OK ['api', 'nginx', 'redis', 'workers']
NAME_OK papyr
VOLUMES_OK ['redis-data']
exit: 0
```

Command B — negative assertion: scanner must NOT be present, count must be 4:

```
$ python -c "import yaml; d=yaml.safe_load(open('<workspace-root>/deploy/docker-compose.yml')); assert 'scanner' not in d['services'], 'scanner service must be deferred to SEC-03'; assert len(d['services']) == 4, 'service count must be 4, got %d' % len(d['services']); print('SCANNER_DEFERRED_OK count=', len(d['services'])); print('SERVICE_LIST=', sorted(d['services'].keys()))"
SCANNER_DEFERRED_OK count= 4
SERVICE_LIST= ['api', 'nginx', 'redis', 'workers']
exit: 0
```

Interpretation: the regression test now passes with exactly the four
required services, and the scanner service is correctly absent.

## 6. .gitignore negation verification (env template tracked-eligible)

```
$ GIT_MASTER=1 git -C <workspace-root> check-ignore deploy/.env.production.example
exit: 1   ← path is NOT ignored → tracked-eligible

$ GIT_MASTER=1 git -C <workspace-root> check-ignore -v deploy/.env.production.example
.gitignore:7:!.env.*.example	deploy/.env.production.example
```

Interpretation: `git check-ignore` (no `-v`) exits 1, which means the
path is **not** ignored — i.e. tracked-eligible. The `-v` form prints
the negation line that whitelists it (`.gitignore:7: !.env.*.example`),
which matches what was added in PR-01 per the AGENTS.md context note.

Sanity check against an actually-ignored file (defense-in-depth):

```
$ GIT_MASTER=1 git -C <workspace-root> check-ignore -v .env.papyr
.gitignore:9:/.env.papyr	.env.papyr
exit: 0   ← actually-ignored path correctly returns exit 0
```

## 7. Files created (path → bytes → exact content)

### 7.1 `<workspace-root>\deploy\docker-compose.yml` — 1.9 KB (1922 bytes)

```yaml
# Papyr deploy — docker-compose skeleton (Phase 0 / FD-03).
#
# This is a SKELETON only. It defines the four services that compose the
# Phase 0 deploy unit (nginx, api, redis, workers). Image tags, network
# bindings, secret references, volumes, and a real `docker compose config`
# pass happen in a later wave (see FD-03 ownership in
# audit-outputs/phase-0/phase-0-execution-dag.md).
#
# Constraints honored:
#   - Exactly 4 services. A scanner service is intentionally deferred to
#     SEC-03 and MUST NOT be added here.
#   - No real image digests, no real registry hosts, no real domains.
#   - No real secrets; env values come from .env.production.example only.
#
# Local validation: Docker is absent on this workstation, so the regression
# test is a pyyaml structural check:
#   python -c "import yaml; d=yaml.safe_load(open('deploy/docker-compose.yml')); \
#     assert sorted(d['services'].keys())==['api','nginx','redis','workers']"

name: papyr

services:
  nginx:
    image: nginx:__SET_ME__
    profiles: ["edge"]
    depends_on:
      - api
    ports:
      - "127.0.0.1:__SET_ME__:80"   # placeholder host bind; real bind in deploy wave
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    restart: unless-stopped

  api:
    image: papyr-api:__SET_ME__
    profiles: ["app"]
    env_file:
      - .env.production.example    # template only; real .env.production is provided at VPS via DEC-176
    depends_on:
      - redis
    expose:
      - "3000"
    restart: unless-stopped

  workers:
    image: papyr-workers:__SET_ME__
    profiles: ["app"]
    env_file:
      - .env.production.example
    depends_on:
      - redis
      - api
    restart: unless-stopped

  redis:
    image: redis:__SET_ME__
    profiles: ["app"]
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
    driver: local
```

### 7.2 `<workspace-root>\deploy\nginx\conf.d\production.conf` — 1.5 KB (1508 bytes)

```nginx
# Papyr nginx production server-block skeleton (Phase 0 / FD-03).
#
# SKELETON ONLY. No real domain, no real TLS certs, no real upstreams.
# All placeholders use __SET_ME__ so an unintended publish cannot leak a value.

upstream papyr_api_upstream {
    # Placeholder upstream name. The api service is exposed on its compose
    # network at the service name `api` on port 3000 (see docker-compose.yml).
    server api:3000;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;

    # PLACEHOLDER domain. Replace with the real FQDN during the deploy wave.
    server_name __SET_ME__;

    # Phase 0 skeleton: no TLS block. TLS termination lands with SEC-03
    # alongside the scanner service; do not add ssl_certificate / ssl_certificate_key
    # values here.

    # Static assets / cache-friendly paths
    location /static/ {
        alias /var/www/papyr/static/;
        access_log off;
        expires 30d;
    }

    # Application reverse proxy
    location / {
        proxy_pass http://papyr_api_upstream;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection        "";
        proxy_read_timeout 60s;
    }

    # Health endpoint placeholder for the upstream
    location = /healthz {
        proxy_pass http://papyr_api_upstream/healthz;
        access_log off;
    }
}
```

### 7.3 `<workspace-root>\deploy\.env.production.example` — 1.6 KB (1639 bytes)

```dotenv
# Papyr production environment — NON-SECRET TEMPLATE ONLY (Phase 0 / FD-03).
#
# This file is intentionally safe to commit. Every value below is either
# empty or a clearly-marked placeholder such as `__SET_ME__` or `changeme`.
#
# DO NOT put any of the following here:
#   - real database connection strings
#   - real API keys, tokens, OAuth client secrets
#   - real hostnames, IP addresses, or domain names
#   - real TLS cert paths or private key material
#
# Operational rules (see DEC-176):
#   - On the VPS this file ships as a template only; the real `.env.production`
#     is provisioned separately and installed mode 0600 owned by the
#     non-root operator (DEC-172). This template is NEVER deployed as-is.
#
# Git tracking: this file is matched by `.gitignore` rule `!.env.*.example`,
# so it is tracked-eligible while real `.env*` files remain ignored.

# --- Application runtime --------------------------------------------------
APP_ENV=production
API_PORT=3000
LOG_LEVEL=info

# --- Public-facing URLs ---------------------------------------------------
# Placeholder origin(s). Replace with the real CORS allowlist at deploy time.
CORS_ALLOWED_ORIGINS=__SET_ME__

# --- Internal service wiring ---------------------------------------------
# Placeholder Redis URL — service name `redis` matches docker-compose.yml.
REDIS_URL=redis://redis:6379/0

# Placeholder database URL — replace with the real managed-DB URL during the deploy wave.
DATABASE_URL=changeme

# --- Upstream AI provider base URL ---------------------------------------
# Placeholder AI base URL. Set to the real provider endpoint at deploy time.
PAPYR_AI_BASE_URL=__SET_ME__
```

### 7.4 `<workspace-root>\deploy\runbook-vps.md` — 2.9 KB (2912 bytes)

```markdown
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
```

Byte sizes reported by `ls -la` (Windows-via-bash view):

| Path | Bytes |
| --- | --- |
| `deploy/.env.production.example` | 1.6K (~1639) |
| `deploy/docker-compose.yml`      | 1.9K (~1922) |
| `deploy/nginx/conf.d/production.conf` | 1.5K (~1508) |
| `deploy/runbook-vps.md`          | 2.9K (~2912) |

## 8. Scope-discipline statement

What FD-03 did:

- Created four skeleton files under `deploy/`.
- Validated compose shape with a pyyaml structural check (Docker is absent).
- Re-verified the `papyr-reference/` invariant before and after work.
- Recorded every command and its result in this file.

What FD-03 deliberately did NOT do:

- Did NOT start Docker, did NOT run any container.
- Did NOT fake a `docker compose config` PASS.
- Did NOT modify anything under `papyr-reference/` (HEAD pinned at
  `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` before and after).
- Did NOT read or print any value from `<workspace-root>\.env.papyr`.
- Did NOT add a scanner service or any 5th service to `docker-compose.yml`.
- Did NOT create Dockerfiles, real TLS certs, or any process.
- Did NOT touch `frontend/` or `backend/`.
- Did NOT run any git mutation (`add`, `commit`, `push`, `init`,
  `remote`). Only read-only probes (`status`, `rev-parse`,
  `check-ignore`) prefixed `GIT_MASTER=1`.
- Did NOT install dependencies, run migrations, start dev servers, or
  alter infrastructure.

## 9. Post-work legacy invariant re-check

```
$ GIT_MASTER=1 git -C papyr-reference status --porcelain
(empty)
porcelain-exit: 0

$ GIT_MASTER=1 git -C papyr-reference rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
HEAD-exit: 0
```

Interpretation: `papyr-reference/` is unchanged. The invariant holds.

## 10. Source-of-truth references

- **FD-03 ownership:** `audit-outputs/phase-0/phase-0-execution-dag.md`
  (FD-03 deploy section). This record cites the DAG node by path.
- **Architecture context:** `audit-outputs/foundation-architecture-audit.md`
  — the deploy surface is referenced there; FD-03 scaffolds only the
  shape, not the implementation choices that the architecture audit
  tracks.
- **Decision log:**
  - `papyr-rebuild-decisions.md` — DEC-172 (non-root operator on the
    VPS), DEC-176 (env file mode 0600 on the VPS). The runbook outline
    references both by ID; it does not implement them.
- **Constraints:** `AGENTS.md` — read-only `papyr-reference/`, no
  commits, mandatory `audit-outputs/` persistence.

## 11. Uncertainties + unresolved questions

- **No `docker compose config` validation.** The pyyaml check is a
  structural substitute; it does not validate Compose schema or env
  interpolation. Stronger validation will need a host with Docker.
  Resolution: defer to the deploy wave when the runner has Docker.
- **Image tags are placeholders (`nginx:__SET_ME__`, etc.).** No real
  registry, digest, or tag has been chosen in Phase 0. Resolution:
  image policy is a separate decision (not FD-03).
- **TLS is intentionally absent from `production.conf`.** TLS termination
  lands in SEC-03 alongside the scanner service. Resolution: do NOT add
  a TLS block until SEC-03 is scheduled.
- **`deploy/` is untracked in the root repo right now.** The AGENTS.md
  context says root repo is initialized, files untracked, commits deferred
  to a later Wave. FD-03 did not run `git add`; staging is the commit
  wave's responsibility.
- **`.env.production.example` is placeholder-only by design.** If any
  future agent reads it and assumes the values are real, they will fail.
  Resolution: the header comment explicitly forbids that use.
- **No unit test under `deploy/`** because the regression test lives
  inline in the record (pyyaml one-liner). If the project later adds
  a `tests/` directory, the pyyaml check should be promoted to a real
  test file. Resolution: deferred.
- **`docker --version` returned `command not found`** under bash on this
  Windows host. That is sufficient evidence of absence for the fallback
  rationale; no Windows-Process probe was performed.

## 12. Acceptance summary

| Acceptance criterion | Status |
| --- | --- |
| `deploy/docker-compose.yml` parses with pyyaml | PASS (SERVICES_OK) |
| `sorted(d['services'].keys()) == ['api','nginx','redis','workers']` | PASS |
| `.env.production.example` contains only placeholder values | PASS (all values `__SET_ME__`, `changeme`, `production`, `info`, or `redis://redis:6379/0` — the last is the compose-network placeholder, not a real connection string) |
| All four files exist with expected content | PASS (4 files, byte sizes recorded) |
| Legacy invariant unchanged (porcelain empty, HEAD 981c59a...) | PASS (verified pre and post) |
| `papyr-reference/` not modified | PASS (read-only) |
| No real secret / IP / domain-cert anywhere | PASS (verified by review of written content) |
| `.env.production.example` tracked-eligible | PASS (`check-ignore` exit 1; `.gitignore:7:!.env.*.example`) |
| Docker not started, no fake `docker compose` PASS | PASS (`docker` command absent; only pyyaml ran) |