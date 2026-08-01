# C4 — VPS Processing Hardening Research Brief

| Field | Value |
|---|---|
| Brief ID | C4 |
| Path | `audit-outputs/research/track-c/c4-vps-processing-hardening.md` |
| Track | C — Infrastructure and operations |
| Title | VPS processing hardening and malware scanning research |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent, Track C Wave 1) |
| Status | Complete (draft for owner review under DEC-057) |
| Governing decisions | DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171; supporting: DEC-020, DEC-035, DEC-066, DEC-160, DEC-162, DEC-172, DEC-179 |
| Spec sections served | Technical Architecture Specification §6.2, §7, §17, §21, §25.3 items 8, 9; Product and UX Design Specification §18, §21.7 (interface only) |

**Files read for this brief**

- `<workspace-root>\AGENTS.md`
- `<workspace-root>\papyr-rebuild-decisions.md` (in full; DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171 govern this brief)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (in full; §6.2, §7, §17, §21, §25.3)
- `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (in full; §18)
- `<workspace-root>\audit-outputs\research-program-plan.md` (§7.3, §8)
- `<workspace-root>\audit-outputs\spec-cross-review.md`
- Legacy (read-only): `papyr-reference/deploy/docker-compose.yml`, `papyr-reference/backend/Dockerfile.production`, `papyr-reference/deploy/nginx/conf.d/production.conf`, `papyr-reference/deploy/nginx/conf.d/default.conf`, `papyr-reference/backend/utils/pdf_validator.py`, `papyr-reference/backend/utils/config.py`, `papyr-reference/backend/main.py`, `papyr-reference/docs/runbook-vps.md`, `papyr-reference/.github/workflows/deploy-vps.yml`
- Evidence files (primary evidence deliverables): `audit-outputs/research/track-c/evidence/c4-evidence-container-nginx-linux.md`, `audit-outputs/research/track-c/evidence/c4-evidence-scanner.md`

---

## 2. Scope

This brief resolves the VPS processing hardening design for untrusted PDF and image inputs:

- **Balanced input validation and hardened container isolation** (DEC-169): non-root execution, least privilege, bounded CPU/memory/time/disk, restricted network, hardened filesystem/capabilities, maintained engines. Docker is one defense layer, not the sole boundary.
- **Malware scanning** (DEC-171): scanner selection, update channel, resource profile, safe-failure behavior, and monitoring hooks. Architecture §25.3 item 8.
- **Nginx rate-limit values and fair-use thresholds** (DEC-020, DEC-035): the Nginx layer complementing application fair-use controls. Architecture §25.3 item 9.
- **Relationship to sanitization and threat blocking** (DEC-088, DEC-090, DEC-092, DEC-093): the defense-layer order, where each control sits, and what fails closed. Detailed threat classification is D5's scope; this brief fixes the processing-boundary requirements D5 constrains.
- **Maintenance cadence** (DEC-179): dependency/base-image/signature update obligations relevant to hardening.

The current approved behavior: all server-side inputs are treated as untrusted; validation inspects actual file structure and decoded-resource risk rather than extension/MIME alone; threat-classified files are blocked (DEC-088); PDF-producing outputs are sanitized of active content (DEC-090); PDF-to-JPG inputs are inspected for parser safety (DEC-092); image inputs are validated and decoded in isolation (DEC-093); a maintained general malware scanner is one security signal (DEC-171).

## 3. Non-goals

- **Per-tool server limits** (C2): the numeric input ceilings (bytes, pages, pixels) that bound "resource risk" are C2; this brief sets the *enforcement boundaries* they plug into.
- **Threat-classification policy details** (what exactly is "a threat"): D5 (security, threat, and privacy requirements) owns the classification register and fail-closed classes.
- **Sanitization engine mechanics** (how active content is stripped): Track A tool briefs and the engine research (A1–A6).
- **Redis/worker sizing** (C1): C1 sets worker bounds and queue caps; this brief hardens the container/process layer around them.
- **OS-level compliance scanning** (CIS/OpenSCAP/Lynis schedules): recorded as legacy cadence in the runbook; referenced here only as supporting evidence.
- **A benchmark program or VPS capacity testing**: explicitly prohibited (DEC-066, DEC-063).

## 4. Research questions

Restated from plan §7.3 (C4):

1. What container and process hardening satisfies DEC-169 (non-root, least privilege, bounded CPU/memory/time/disk, restricted network, hardened filesystem/capabilities) for the API, Redis, worker, and Nginx services on one Docker Compose stack (DEC-162)?
2. Which maintained malware scanner should be selected (DEC-171), through which update channel, with what resource profile, and — critically — what is the safe-failure behavior when the scanner is unavailable or its signatures are stale?
3. What Nginx rate-limit values and fair-use thresholds implement DEC-020/DEC-035 at the proxy layer, keyed on real client IP behind Cloudflare, without being the sole control?
4. How do validation, scanning, sanitization, threat blocking, and container isolation compose into the defense layers of arch §17.1, and which failure classes fail closed (DEC-088, DEC-090, DEC-092, DEC-093)?
5. What maintenance obligations follow (DEC-179) for base images, native engines, packages, and scanner signatures?

## 5. Evidence

### 5.1 Legacy baseline evidence (read-only, `papyr-reference/`)

| Path and line | What it evidences |
|---|---|
| `backend/Dockerfile.production:103-134` | Non-root `appuser` (UID/GID 1001), `tini` PID 1, healthcheck, multi-stage build with pinned `python:3.11.9-slim-bookworm` base (digest-pinned per comments), `TMPDIR=/opt/papyr/temp` for the exec-enabled temp path. |
| `backend/Dockerfile.production:24-47` | Builder isolation; pip upgrade for CVE fixes in the build toolchain. |
| `backend/Dockerfile.production:74-101` | Runtime native deps (ghostscript, poppler-utils, tesseract, LibreOffice) — the footprint the five-tool rebuild trims (DEC-010) and keeps patched (DEC-179). |
| `deploy/docker-compose.yml:17-36` | Legacy hardening: `read_only: true`, `security_opt: no-new-privileges`, `cap_drop: [ALL]` with a small `cap_add` set, CPU/memory limits (backend `cpus 3.5`, `memory 4G`), reservations. |
| `deploy/docker-compose.yml:39-50` | tmpfs writable areas with size bounds (`/tmp` 512 M exec, `/home/appuser/.cache` 128 M) and a read-only env file mount. |
| `deploy/docker-compose.yml:52-66` | Env via `env_file` (mode-600 file), internal `expose` only (no published backend port), custom bridge network. |
| `deploy/docker-compose.yml:68-81` | Healthcheck on `/health`; `json-file` log driver with `max-size 10m`, `max-file 3`. |
| `deploy/docker-compose.yml:82-128` | Nginx service: 0.5 CPU / 256 M limit, `cap_add NET_BIND_SERVICE`, only 80/443 published. |
| `deploy/nginx/conf.d/production.conf:6-25` | Legacy rate zones: `papyr_api` 30 r/m and `papyr_burst` 2 r/s; bad-bot UA map; blocked-path map (env/git/wp-admin/traversal). |
| `deploy/nginx/conf.d/production.conf:57-75` | `set_real_ip_from` for all Cloudflare ranges, `real_ip_header CF-Connecting-IP` — real-IP keying precedent. |
| `deploy/nginx/conf.d/production.conf:84-95` | `client_max_body_size 25M` (20 M upload + headroom), `client_body_timeout 60s`, security headers, `server_tokens off`. |
| `deploy/nginx/conf.d/production.conf:98-143` | Health endpoint unrate-limited; `/api/` limited (`burst=10 nodelay` + `burst=5`); `/status/` limited `burst=20 nodelay`; `return 444` catch-all. |
| `backend/utils/pdf_validator.py` | Legacy validation order: empty, MIME, extension, magic bytes (`%PDF`), size, page count, encrypted — the baseline DEC-093/DEC-169 extend. |
| `backend/utils/config.py:101-103` | `MAX_UPLOAD_SIZE_MB=20`, `RATE_LIMIT_PER_MINUTE=10` (application-level rate limit). |
| `backend/main.py:33-84` | `slowapi` application limiter and 429 handler (in-process; superseded by Redis-shared counters per DEC-020, see C1). |
| `.github/workflows/deploy-vps.yml:58-71` | Trivy scan gate (CRITICAL severity, `ignore-unfixed: true`) in the CI/deploy pipeline — the DEC-177 core-gate security scan precedent. |
| `docs/runbook-vps.md:10.3` | Legacy Netdata alert rules (CPU anomaly, outbound spike, disk >85%) — legacy monitoring baseline for C5. |
| `docs/runbook-vps.md:11` | Legacy compliance cadence: AIDE daily, chkrootkit/rkhunter weekly, Lynis monthly, OpenSCAP quarterly, CrowdSec. |

### 5.2 Primary web sources (official documentation; access date 2026-07-31)

Current authoritative documentation for Docker container hardening, Nginx rate limiting/proxy hardening, Linux OS hardening, and the malware scanner is collected in the evidence files `evidence/c4-evidence-container-nginx-linux.md` and `evidence/c4-evidence-scanner.md` (research primary evidence deliverables, access date 2026-07-31). Verified facts applied in this brief:

- **Docker security** (`https://docs.docker.com/engine/security/security/`): namespaces + cgroups for isolation and resource DoS protection; the daemon is high-privilege (rootless mode exists); **"the best practice for users would be to remove all capabilities except those explicitly required"** (i.e., `--cap-drop ALL` + minimal `cap-add`); userns-remap is supported but not default; AppArmor/SELinux profiles and custom seccomp profiles are additional layers; Docker Content Trust for signed images. Compose fields for `read_only`, tmpfs, `cap_drop/cap_add`, `security_opt: no-new-privileges`, `pids_limit`, `ulimits`, resource limits, healthchecks, and `depends_on: condition: service_healthy` are standard spec elements.
- **Nginx** (`https://nginx.org/en/docs/http/ngx_http_limit_req_module.html`): `limit_req` is a leaky bucket; `burst` + `nodelay`/`delay` semantics; rates in `r/s` or `r/m` (30r/m = 0.5 r/s); multiple zones per location supported; **default rejection status is 503 and `limit_req_status` can set 429**; zone memory ≈ 1 MB per ~8k states (64-bit, 128 bytes/state); `$limit_req_status` (PASSED/DELAYED/REJECTED) and `limit_req_dry_run` exist for validation. `realip` module (`set_real_ip_from` + `real_ip_header CF-Connecting-IP`) keys limits/logs on the real client IP; Cloudflare publishes the authoritative ranges at `https://www.cloudflare.com/ips-v4`.
- **Linux hardening:** sshd key-only/no-root-login posture is governed by DEC-172; CIS benchmarks guide sysctl hardening; unattended-upgrades is the Debian/Ubuntu security-patch mechanism (legacy runbook §9.1).
- **ClamAV** (`https://docs.clamav.net/`): GPLv2, Cisco-maintained, supports PDF among many formats, archive-bomb protection, signed signature DBs, hourly `freshclam` updates; **minimum recommended RAM is 3 GiB+ (docs: "we recommend at 3-4 GiB of RAM, but you may get by with less if you're willing to accept some limitations")**; `clamd.conf` knobs (`LocalSocket`, `User`, `ScanOnAccess`, resource/size limits in `clamd.conf.sample`) and exit-code semantics (0 clean / 1 found / 2 error) support fail-closed logic; official container image `clamav/clamav`. ClamAV is explicitly not a full endpoint-security suite and cannot guarantee unpacking every format variant.
- **Trivy** (`https://aquasecurity.github.io/trivy/`): CI container-image scanning with exit-code gating — the legacy deploy-gate precedent.

## 6. Alternatives

### Malware scanner selection

**Alternative A1 — ClamAV (clamd daemon + freshclam) as a sidecar service in the Compose stack (recommended).**
- Maintained open-source (GPLv2), the de-facto standard for server-side scanning; official container image; signature updates via `freshclam` on a documented cadence; on-demand scanning fits the "scan once at admission" model.
- Trade-offs: **memory footprint is the binding constraint on a small VPS — the official documentation recommends 3 GiB+ RAM (3–4 GiB) for clamd with the standard signature DB**, and states "you may get by with less if you're willing to accept some limitations". On an 8 GB VPS this must be a deliberate, tuned budget (a smaller clamd with reduced concurrency/size limits, plus a documented limitation), not an unplanned allocation. Signature-DB update latency and stale-DB risk need `freshclam` health + staleness alerting; PDF-specific detection limits are documented by the project. Fits the defense-in-depth framing of DEC-171 and the "scanner failure, update health, resource consumption, and safe rejection behavior are operationally monitored" requirement.
- Safe-failure: **fail closed** — if `clamd` is unavailable or signatures are stale beyond a documented threshold, new jobs are rejected with a safe "service temporarily unavailable" category (never processed unscanned), an operational alert fires (C5), and a runbook procedure restores scanning. Rationale: DEC-088 requires blocking infrastructure threats; a degraded scanner is treated as an availability incident on the processing path, not a permission to skip the layer. (Fail-open would contradict DEC-169's layered model; the availability cost is bounded because admission pauses only while the scanner is down.)
- Cost/operational impact: one additional container, ~hundreds of MB RAM within the C1 budget, daily signature updates, monthly signature/DB maintenance in the DEC-179 cadence.

**Alternative A2 — Vendor/managed scanning API (e.g., a cloud scanning service).**
- Trade-offs: no in-house update channel or resource footprint, but introduces a new provider dependency, egress/uploads of user documents to a third party (privacy/DPA implications and DEC-012/DEC-025 exposure), per-file cost, and a hard external dependency at admission time (fails closed on provider outage). Rejected for MVP because the document bytes would be sent to an additional processor, conflicting with the "temporary, least-surface" model and DEC-095's cost boundary.

**Alternative A3 — No dedicated scanner (rely on validation + sanitization + isolation).**
- Rejected: DEC-171 explicitly requires a maintained general malware scanner as a separate layer.

### Container/process isolation

**Alternative B1 — Evolve the legacy hardening baseline into explicit per-service profiles (recommended).**
- Extend the legacy compose (`read_only`, caps, no-new-privileges, tmpfs, limits, healthchecks) into explicit profiles for api/redis/workers/nginx with: non-root USER in every image; `cap_drop: ALL` + minimal `cap_add`; `read_only: true` + bounded `tmpfs` for each writable area; `security_opt: no-new-privileges`; seccomp default (custom only where an engine requires syscalls, documented); `pids_limit`; `ulimits`; CPU/memory limits per C1 sizing; **no network from workers except the internal bridge and the R2 S3 endpoint** (egress allowlist; workers must not reach arbitrary external hosts, arch §7.3); internal-only networks with no published Redis/worker ports (DEC-162); `json-file` log rotation with size caps; digest-pinned base images with quarterly refresh (DEC-179).
- Trade-offs: moderate configuration work; preserves the proven legacy posture while making each layer explicit and auditable.

**Alternative B2 — Rootless Docker / user-namespace remap as the primary isolation boundary.**
- The legacy VPS already ran `userns-remap=default` (Dockerfile.production comments; runbook §5.7). Trade-offs: added host UID mapping complexity (already documented as a legacy pain point) and image/volume portability friction; valuable as defense-in-depth but not a replacement for the per-container hardening of B1. Recommendation: retain the legacy userns-remap compatibility requirement (arch §7.3) and document it, while B1 remains the primary posture.

### Nginx rate limiting and fair-use

**Alternative C1 — Multi-zone Nginx rate limiting keyed on real client IP (recommended), complementing application controls.**
- Keep the legacy pattern (`set_real_ip_from` Cloudflare ranges + `CF-Connecting-IP`, `limit_req_zone`) with **updated** Cloudflare IP ranges, and separate zones for admission (`/api/v1/...` upload/limit endpoints), status polling, and public health. Proposed conservative values (design choices, adjustable from telemetry, DEC-066): admission zone `rate=10r/m` per IP with `burst=5` (upload admissions are far below this for ordinary users; aligns with the legacy `RATE_LIMIT_PER_MINUTE=10`); status-poll zone `rate=60r/m` per IP with `burst=30 nodelay` (legacy client polls every 3 s ≈ 20 r/m); health endpoint unrate-limited but path-restricted. Nginx rejects with 429 before the application; the application's Redis-shared fair-use controls (C1) are authoritative for adaptive decisions (delay/challenge/reject), because Nginx alone cannot enforce per-origin concurrency or cost-weighted policy across API processes (DEC-020).
- Trade-offs: Nginx gives coarse, cheap, per-IP protection; the adaptive policy must live in the application. Fine.

**Alternative C2 — Application-only fair-use controls, no Nginx rate zones.**
- Rejected: leaves the origin exposed to trivial connection/upload floods before the application runs; the legacy precedent and arch §6.2 require Nginx zones as a first layer.

## 7. Recommendation

**Recommendation (not an accepted decision):** adopt **A1 (ClamAV sidecar, fail-closed) + B1 (explicit per-service hardened profiles) + C1 (multi-zone Nginx limits keyed on real IP)** as the C4 package:

- **Defense layers** (arch §17.1), each with a fail-closed default: (1) Cloudflare + Nginx filtering (bot/path/size/rate); (2) application file validation (structure + decoded-resource risk, DEC-093/DEC-169); (3) ClamAV scan at admission — **fail closed** on scanner unavailable or stale signatures; (4) active-content sanitization for PDF-producing outputs (DEC-090); (5) bounded resource controls (C1/C2 ceilings enforced by container limits, timeouts, tmpfs/disk caps, pids/ulimits); (6) hardened container isolation (B1). Threat-classified files are blocked (DEC-088) and never reach engines beyond minimum isolated inspection; scan/sanitize/validation failures never leak exploit details to users (safe general categories only, DEC-169/DEC-171).
- **Per-service profiles** (summarized; full table belongs in design): api (non-root, read-only + tmpfs, caps drop-all, no-new-privileges, memory cap per C1, no published ports), redis (internal only, persistent volume, memory cap, no public exposure per DEC-162), workers (non-root, read-only + bounded tmpfs workspace per-job cap, caps drop-all, seccomp default with documented exceptions, memory/CPU per C1, **egress restricted to R2 S3 endpoint and internal bridge**, `pids_limit`), nginx (only 80/443 published, `NET_BIND_SERVICE`, caps drop-all otherwise). Healthchecks on every service (DEC-162).
- **Nginx values** (conservative design defaults, DEC-066): `client_max_body_size` set per C2's largest per-tool upload + headroom; admission zone 10 r/m burst 5 (with `limit_req_status 429` so Nginx rejects at the same status the application uses — the module's default is 503); status zone 60 r/m burst 30 nodelay; health unrate-limited; updated Cloudflare `set_real_ip_from` ranges (refreshed from `https://www.cloudflare.com/ips-v4`); security headers + `server_tokens off` retained; `return 444` catch-all retained.
- **Scanner operations**: `freshclam` on the hourly documented cadence with staleness alerting (a DB older than the documented threshold raises an operational alert, and admission pauses if the threshold is crossed); scan at admission with a size/time-bounded config (per-input scan size ceiling aligned to C2); **a deliberate, documented clamd memory budget within the C1 envelope (tuned `MaxScanSize`/`MaxFileSize`/`MaxThreads`/`StreamMaxLength`, acknowledging the official 3–4 GiB recommendation and the "may get by with less" allowance)**; scanner metrics (scan duration, hits, failures, DB age) exported to C5; monthly signature/policy review inside the DEC-179 cadence; quarterly base-image refresh with digest pinning.
- **Maintenance** (DEC-179): monthly dependency review; prompt critical fixes; Trivy scan retained as the CI core-gate security stage (legacy gate precedent), extended to HIGH with a documented backlog if the evidence supports it.

**Owner decision prompts:** (1) fail-closed admission on scanner outage (recommended) vs a narrowly-scoped temporary fail-open mode during incidents — the latter contradicts DEC-169's layering and is **not** recommended; (2) whether Nginx admission zone 10 r/m (legacy value) is acceptable as the launch default given DEC-020's "no rigid daily quota for ordinary users" (note: per-minute rate limits at this scale do not constitute a daily quota, but the value is a design choice); (3) ClamAV resource budget within the C1 memory envelope.

## 8. Measurable acceptance criteria

1. Every service runs as a non-root user; a test asserts no container process runs as UID 0 (DEC-169).
2. Worker containers have no outbound network path except the internal bridge and the R2 endpoint; a network-isolation test asserts arbitrary egress is blocked (DEC-169, DEC-162).
3. Worker root filesystems are read-only with bounded tmpfs; a test asserts writes outside tmpfs fail (DEC-169).
4. Capabilities are dropped to the documented minimal set; `no-new-privileges` is set; a test asserts the effective capability set (DEC-169).
5. CPU, memory, pids, ulimit, and disk bounds are declared in executable Compose config and enforced; a bounded-resource test asserts a worker exceeding its memory cap is OOM-killed rather than degrading the API (C1/C4 boundary).
6. ClamAV: a benign sample passes; a **scanner-signature test fixture** (documented EICAR-class artifact, not a live malware payload) is rejected with a safe category; a **disabled-scan mode** test asserts jobs are rejected (fail closed) with a safe "temporarily unavailable" category (DEC-171).
7. ClamAV signature staleness beyond the documented threshold produces an operational alert and admission pause; DB age is exported as a metric (DEC-171, DEC-182).
8. Nginx: requests over the admission zone limit receive 429; real-client-IP keying works through the Cloudflare proxy configuration (a spoofed `CF-Connecting-IP` from a non-Cloudflare source is not trusted); health endpoint remains unrate-limited (DEC-020, DEC-035, arch §6.2).
9. Threat-classified files are blocked before reaching document engines; the rejection message exposes only a safe general category (DEC-088, DEC-169).
10. Sanitization of detected active content is verified on PDF-producing outputs with documented coverage limits; no claim of perfect sanitization appears anywhere (DEC-090, DEC-171).
11. Base images are digest-pinned; quarterly refresh and the monthly dependency review are represented in the operating cadence (DEC-179).

## 9. Assumptions, uncertainties, and unresolved questions

- **Assumption:** the VPS runs Docker Engine with Compose (legacy `deploy/docker-compose.yml`) and retains `userns-remap=default` compatibility requirements; current host state is unverifiable without access (DEC-172, DEC-160).
- **Uncertainty:** ClamAV's exact memory footprint and scan latency on the VPS; the official recommendation is 3–4 GiB RAM for clamd with the standard signature DB ("you may get by with less"), so the C1 memory envelope must reserve a deliberate scanner budget and the limitation must be documented; values above are conservative bounds pending production observation (DEC-066).
- **Uncertainty:** ClamAV PDF-specific detection coverage; documented by the project as limited — the scanner is one layer, never a guarantee (DEC-171).
- **Unresolved:** whether the CI Trivy gate should be raised from CRITICAL-only to include HIGH (legacy chose CRITICAL with a tracked HIGH backlog; changing it affects deploy friction — owner decision).
- **Unresolved:** whether host-level CrowdSec (legacy) remains alongside Cloudflare + Nginx filtering; legacy runbook treats it as active (runbook §4, §11); retained unless the owner removes it.

## 10. Dependencies and cross-track interfaces

- **C1:** worker memory/CPU/time bounds (this brief hardens and enforces C1's sizes); queue caps bound the rate at which scanning must complete.
- **C2:** per-tool input limits drive `client_max_body_size`, scan size ceilings, tmpfs caps, and timeouts.
- **C5:** scanner health (DB age, scan failures), rate-limit violations, OOM events, and per-service health are monitoring signals.
- **D5:** threat classification register and fail-closed classes; this brief's scanner/validation boundary constrains D5's processing-path requirements.
- **A1–A6:** engine entrypoints run inside the hardened worker profile; sanitization mechanics feed outputs (DEC-090).
- **X1/X2:** recommendation and owner prompts feed the index and reconciliation report.

## 11. Source-date log and evidence-completeness notes

- Decisions and specifications read 2026-07-31; legacy files read 2026-07-31.
- Web evidence (Docker, Nginx, Linux hardening, scanner) was researched directly (read-only official docs) and persisted in `evidence/c4-evidence-container-nginx-linux.md` and `evidence/c4-evidence-scanner.md` with per-source URLs and access date 2026-07-31. This brief's §5.2 summarizes them; exact versions, rule syntax, and figures in the evidence files prevail, and any disagreement must be surfaced (DEC-183).
- Evidence-completeness: ClamAV current version/signature cadence, current Cloudflare IP ranges requirement (Nginx `set_real_ip_from`), Docker seccomp/AppArmor current guidance, and Nginx `nodelay` semantics are the material items recorded in the evidence files.

## 12. Prohibitions-compliance statement

No prohibited action was taken: no installs, builds, containers, server starts, VPS/SSH access, deployment, provider authentication, account creation, remote mutation, malware execution, or benchmark program (DEC-066, DEC-060, DEC-160, DEC-172). No source, spec, decision, or existing audit-output file was modified. All writes were confined to `audit-outputs/research/track-c/`. `papyr-reference/` was verified unchanged via read-only `git -C papyr-reference status --porcelain` (empty, exit 0) before and after this brief.
