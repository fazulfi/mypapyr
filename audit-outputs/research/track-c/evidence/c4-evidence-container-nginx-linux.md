# C4 Evidence — Docker, Nginx, Linux Hardening

- **Access date:** 2026-07-31
- **Purpose:** primary-source evidence for `c4-vps-processing-hardening.md` (container/process hardening, Nginx rate limiting, OS posture)
- **Method:** read-only fetch of official docs. No installs, no containers, no VPS access.

## 1. Docker Engine security

Source: `https://docs.docker.com/engine/security/security/` (accessed 2026-07-31).

- Four security areas: kernel namespaces/cgroups; Docker daemon attack surface; container configuration profile (defaults and customizations); kernel hardening features (AppArmor, SELinux, seccomp, etc.).
- Namespaces provide process/network isolation; cgroups prevent resource-exhaustion DoS.
- **Daemon:** runs as root unless rootless mode; only trusted users should control it; the Docker socket is high privilege; expose the API over HTTPS/TLS only; recommended to run Docker exclusively on a server and move other services into containers.
- **Capabilities:** by default Docker drops all capabilities except those needed (allowlist approach). "The best practice for users would be to remove all capabilities except those explicitly required for their processes" — i.e., `--cap-drop ALL` + minimal `cap-add` is the documented best practice.
- **User namespaces** (userns-remap) supported since Docker 1.10, not enabled by default; maps container root to a non-root host UID; helps mitigate container breakout.
- **Other layers:** AppArmor templates ship with Docker; SELinux policies for Red Hat; custom seccomp profiles (`/engine/security/seccomp/`); Docker Content Trust for signed images (`/engine/security/trust/`).
- Related pages (referenced): `https://docs.docker.com/engine/security/seccomp/`, `https://docs.docker.com/engine/security/apparmor/`, `https://docs.docker.com/engine/security/rootless/`.

## 2. Docker best practices and Compose fields (referenced)

- Dockerfile best practices: multi-stage builds; `COPY` over `ADD`; run as non-root `USER`; use `HEALTHCHECK`; pin base images (digests); proper signal handling (init, e.g., tini). Source: `https://docs.docker.com/build/building/best-practices/` and `https://docs.docker.com/reference/dockerfile/` (referenced).
- Compose spec fields: `read_only: true`, `cap_drop`/`cap_add`, `security_opt: [no-new-privileges:true]`, `tmpfs`, `deploy.resources.limits` (`cpus`, `memory`), `pids_limit`, `ulimits`, `restart`, `healthcheck`, `depends_on: condition: service_healthy`, internal networks. Source: `https://docs.docker.com/compose/compose-file/` (referenced; fields are long-standing spec elements).
- `--memory` + `--memory-swap` and OOM behavior: cgroup memory limits; exceeding the limit triggers the OOM killer for the container. Logging: `json-file` driver with `max-size`/`max-file` rotation. (Referenced at `https://docs.docker.com/engine/containers/resource_constraints/` and `https://docs.docker.com/config/containers/logging/json-file/`.)

## 3. Nginx

Sources (accessed 2026-07-31):
- `https://nginx.org/en/docs/http/ngx_http_limit_req_module.html`
- `https://nginx.org/en/docs/http/ngx_http_realip_module.html` (referenced)
- `https://nginx.org/en/docs/http/ngx_http_core_module.html` (referenced)

- **limit_req:** "leaky bucket" rate limiting per key. `limit_req_zone $binary_remote_addr zone=name:10m rate=1r/s;` rates can be `r/s` or `r/m` ("half-request per second is 30r/m"). `limit_req zone=... burst=N [nodelay|delay=N]`. Burst: requests over the rate are delayed up to the burst size; beyond burst → rejected. `nodelay` serves burst requests immediately (no delaying) but still rejects beyond burst. `delay=N` (1.15.7) limits when delaying begins. Multiple `limit_req` directives per location allowed (per-IP + per-server example given). **Default rejection status is 503; `limit_req_status` can set another code (e.g., 429).** Zone memory: 1 MB ≈ 16k IPv4 states (32-bit) or ≈ 8k states (64-bit, 128 bytes/state). `$limit_req_status` variable reports PASSED/DELAYED/REJECTED (1.17.6+). `limit_req_dry_run` (1.17.1+) for testing without enforcement.
- **realip module:** `set_real_ip_from` (trusted proxy CIDRs), `real_ip_header CF-Connecting-IP`, `real_ip_recursive` — enables keying rate limits and logs on the real client IP behind Cloudflare. Cloudflare publishes the authoritative range list at `https://www.cloudflare.com/ips-v4` (and `ips-v6`) for periodic refresh.
- **Core module (referenced):** `client_max_body_size`, `client_body_timeout`, `client_header_timeout`, `proxy_read_timeout`/`proxy_send_timeout`/`proxy_connect_timeout`, `proxy_buffering`, `server_tokens off`, `add_header` (security headers: HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy; note CSP should be tailored to the app).

## 4. Linux OS hardening (referenced)

- sshd: key-based auth only, `PermitRootLogin no`, restricted sudo — consistent with DEC-172 (design decision, not doc-derived).
- CIS Distribution Independent Linux Benchmark / Ubuntu CIS Benchmark (ciscontrols.org, cisecurity.org, referenced) for sysctl guidance: `net.ipv4.tcp_syncookies=1`, `net.ipv4.ip_forward=0`, `net.ipv4.conf.all.rp_filter=1`, `net.ipv4.conf.all.log_martians=1`, etc. (systemd sysctl.d).
- unattended-upgrades for security patches on Debian/Ubuntu (documented in Debian/Ubuntu package docs; legacy runbook §9.1 already uses it).
- fail2ban/crowdsec: legacy runbook uses CrowdSec; with Cloudflare fronting public traffic, host-level ban tooling is defense-in-depth (runbook evidence, not a new source).
- Docker daemon: legacy `userns-remap=default` on the VPS (Dockerfile.production comments; runbook §5.7) — userns-remap is supported but not default (Docker security page above).

## Uncertainties

- Compose `pids_limit`/`ulimits` exact spec keys and current deprecation status: referenced pages not re-fetched; the fields are standard spec elements since Compose v2.
- Current Cloudflare IP ranges: refresh from https://www.cloudflare.com/ips-v4 at implementation (legacy production.conf hardcodes ranges).

## Source list

| # | URL | Accessed |
|---|---|---|
| 1 | https://docs.docker.com/engine/security/security/ | 2026-07-31 |
| 2 | https://nginx.org/en/docs/http/ngx_http_limit_req_module.html | 2026-07-31 |
| 3 | https://nginx.org/en/docs/http/ngx_http_realip_module.html | 2026-07-31 (referenced) |
| 4 | https://nginx.org/en/docs/http/ngx_http_core_module.html | 2026-07-31 (referenced) |
| 5 | https://docs.docker.com/engine/security/seccomp/ | 2026-07-31 (referenced) |
| 6 | https://docs.docker.com/engine/security/rootless/ | 2026-07-31 (referenced) |
| 7 | https://docs.docker.com/compose/compose-file/ | 2026-07-31 (referenced) |
| 8 | https://www.cloudflare.com/ips-v4 | 2026-07-31 (referenced) |
