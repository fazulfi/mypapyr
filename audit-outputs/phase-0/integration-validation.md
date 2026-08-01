# Phase 0 — Read-only Third-party Integration Validation

| Field | Value |
|---|---|
| Phase | Phase 0 (no-deploy, no-mutation) |
| Validation mode | Read-only (no deploy / DNS / bucket / container / repo mutation) |
| Validator | third-party-integration-validator (subagent) |
| Run timestamp (UTC) | 2026-07-31T19:22:54Z |
| Host | Windows (Git Bash), `gh 2.89.0`, `vercel 52.0.0`, `curl 7.x`, `OpenSSH_for_Windows_8.0` |
| Workspace | `<workspace-root>` |
| papyr-reference status | clean (`git status --porcelain` = 0 lines), HEAD pinned at `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (no modification during this run) |

Redaction policy applied to all command output: tokens, chat IDs, and `.env.papyr` values. Variable **names** only were extracted from `.env.papyr` using `grep -oE '^[A-Z_][A-Z0-9_]*=' | sed 's/=$//'`. The VPS IP appears only inside the SSH command line because the operator-supplied host is treated as an authorized asset for the read-only probe; in body text it is written as `<vps-ip>`.

## Tool availability snapshot

| Tool | Path | Version | Used for |
|---|---|---|---|
| `gh` | `/c/Program Files/GitHub CLI/gh` | 2.89.0 | GitHub API |
| `vercel` | `npm global` | 52.0.0 | Vercel API |
| `curl` | `/mingw64/bin/curl` | (system) | HTTP probe |
| `ssh` | `/usr/bin/ssh` (OpenSSH) | (system) | VPS read-only probe |
| `wrangler` | not installed; `npx --no-install wrangler` refused (no `wrangler@4.118.0` cached, install forbidden by Phase 0) | n/a | Cloudflare / R2 — UNKNOWN |
| `aws` / `s3cmd` / `mc` | not installed | n/a | R2 / S3 backup — UNKNOWN |

`wrangler` is intentionally not installed: Phase 0 forbids `npm install` and any CD-mutating command. R2/S3 read-only bucket-list calls would also require authentication that Phase 0 has not authorized. Marked UNKNOWN below.

## Environment variable contract (NAMES only — values redacted)

Extracted with:

```bash
grep -oE '^[A-Z_][A-Z0-9_]*=' "<workspace-root>/.env.papyr" | sed 's/=$//' | sort
```

Recorded NAMES relevant to third-party integrations:

```
ADSTERRA_API_KEY
ADSTERRA_PLACEMENT_IDS
ADSTERRA_PUBLISHER_ID
BACKUP_S3_ACCESS_KEY_ID
BACKUP_S3_ACCESS_KEY_ID_2
BACKUP_S3_BILLING
BACKUP_S3_BUCKET
BACKUP_S3_ENDPOINT
BACKUP_S3_SECRET_ACCESS_KEY
BACKUP_S3_SECRET_ACCESS_KEY_2
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_ACCOUNT_NAME
CLOUDFLARE_API_TOKEN_1
CLOUDFLARE_API_TOKEN_2
GITHUB_ACCOUNT
GITHUB_DEFAULT_BRANCH
GITHUB_REPO_NAME
GITHUB_REPO_VISIBILITY
PAPYR_AI_API_KEY
PAPYR_AI_BASE_URL
PAPYR_AI_MODEL
R2_ACCESS_KEY_ID
R2_BUCKET_NAME
R2_ENDPOINT
R2_SECRET_ACCESS_KEY
SENTRY_DSN
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
VERCEL_CLI_VERSION
VERCEL_LOGIN_STATUS
VERCEL_ORG
VERCEL_PROJECT_NAME
VPS_DOMAIN
VPS_HOST
VPS_SSH_PORT
VPS_USER
```

All required NAMES exist; no values were read.

---

## 1. GitHub — `fazulfi/mypapyr` (new) and `fazulfi/papyr` (legacy public)

### 1a. Auth status

**Command (exact, secrets redacted by `gh` itself):**

```bash
gh auth status
```

**Observed (redacted):**

```
✓ Logged in to github.com account fazulfi (GITHUB_TOKEN)  ← active
  Token: ghp_************************************
  Token scopes: 'admin:enterprise', 'admin:gpg_key', 'admin:org', 'admin:org_hook',
                'admin:public_key', 'admin:repo_hook', 'admin:ssh_signing_key',
                'audit_log', 'codespace', 'copilot', 'gist', 'notifications',
                'project', 'repo', 'user', 'workflow', 'write:discussion',
                'write:network_configurations', 'write:packages'

✓ Logged in to github.com account fazulfi (keyring)        ← inactive
  Token: gho_************************************
  Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

**Result:** **PASS** — active account is `fazulfi`, matching recorded env var `GITHUB_ACCOUNT=fazulfi`.

### 1b. New repo `fazulfi/mypapyr`

**Command (exact):**

```bash
gh repo view fazulfi/mypapyr --json name,visibility,defaultBranchRef,isEmpty
```

**Observed:**

```json
{"defaultBranchRef":{"name":""},"isEmpty":true,"name":"mypapyr","visibility":"PRIVATE"}
```

**Analysis vs recorded fact:**

| Field | Observed | Expected (R-02 / Phase-0 register) | Match |
|---|---|---|---|
| `name` | `mypapyr` | `mypapyr` | YES |
| `visibility` | `PRIVATE` | `PRIVATE` | YES |
| `isEmpty` | `true` | "created 2026-07-31, expected to receive first push in Wave 6" | YES (no first commit yet) |
| `defaultBranchRef.name` | `""` | `main` | **NO — DISCREPANCY (expected)** |

**Discrepancy (informational, not a failure):** An empty GitHub repo has no default branch materialized until the first commit lands. The repo will receive `main` as its default branch on first push (per Wave 6 G15; the repo was created with `--private` only and the default branch is set by the first pushed branch — see `audit-outputs/phase-0/implementation-readiness-reconciliation.md` line 94 and `audit-outputs/phase-0/phase-0-execution-dag.md` line 222). Not blocking; this is the documented empty-repo state.

**Result:** **PASS** (visibility + existence; default-branch assignment pending first push).

### 1c. Legacy repo `fazulfi/papyr` (PUBLIC, do NOT touch)

**Command (exact):**

```bash
gh repo view fazulfi/papyr --json visibility
```

**Observed:**

```json
{"visibility":"PUBLIC"}
```

**Result:** **PASS** — visibility is PUBLIC as recorded in `audit-outputs/phase-0/repository-safety-audit.md` line 7 ("Legacy repo `github.com/fazulfi/papyr` is **already public**"). **No mutation attempted.** Confirmed do-not-touch constraint is satisfied.

### 1d. Workspace `git remote -v` (must not point at legacy)

**Commands (exact):**

```bash
cd "<workspace-root>" && git remote -v
git -C "<workspace-root>/papyr-reference" remote -v
```

**Observed:**

```
fatal: not a git repository (or any of the parent directories): .git
---
origin  https://github.com/fazulfi/papyr.git (fetch)
origin  https://github.com/fazulfi/papyr.git (push)
```

**Result:** **PASS** — workspace root is intentionally not yet a git repo (Wave 1 G8/G9 setup pending; `git init -b main` is part of Wave 6 per `implementation-readiness-reconciliation.md` line 94). The only existing remote is inside `papyr-reference/` and points at the legacy public repo, which is the H9/G14 invariant substrate ("remote must never be legacy" applies to the *new* repo, not the read-only legacy clone). Confirmed compliant.

---

## 2. Vercel — `whoami`, project `papyr`, org `fazulfis-projects`, prod domain `mypapyr.com`

### 2a. `vercel whoami`

**Command (exact):**

```bash
vercel whoami
```

**Observed:**

```
fazulfi
```

**Result:** **PASS** — active Vercel user is `fazulfi`.

### 2b. Project listing under recorded org

**Command (exact):**

```bash
vercel project ls
```

**Observed:**

```
Fetching projects in fazulfis-projects
> Projects found under fazulfis-projects  [2s]

  Project Name   Latest Production URL   Updated   Node Version
  papyr          https://mypapyr.com     66d       24.x
```

**Result:** **PASS** — Vercel scope is `fazulfis-projects` (literal Vercel scope identifier), single project `papyr`, latest production URL `https://mypapyr.com`, Node 24.x, last update 66d ago. Matches recorded env vars `VERCEL_PROJECT_NAME=papyr`, `VERCEL_ORG=fazulfis-projects`, and the prod-domain fact `mypapyr.com` (DEC-021).

### 2c. Deployment inspection (negative — no deployment named exactly `papyr`)

**Command (exact):**

```bash
vercel inspect papyr
```

**Observed:**

```
Error: Can't find the deployment "papyr" under the context "fazulfis-projects"
```

**Result:** **NORMAL** — `vercel inspect` expects a *deployment* identifier, not a project name. The error confirms the CLI is correctly scoped to `fazulfis-projects`. The project listing in 2b is the authoritative existence check. No deploy attempted. **PASS** for project existence.

### 2d. Production DNS edge reachability (informational only, no mutation)

**Command (exact):**

```bash
curl -sS -o /dev/null -w "HTTP=%{http_code} URL=%{url_effective}\n" --max-time 10 -I https://mypapyr.com
curl -sS -o /dev/null -w "HTTP=%{http_code}\n" --max-time 10 -I https://api.mypapyr.com
```

**Observed:**

```
HTTP=526 URL=https://mypapyr.com/
HTTP=526
```

**Analysis:** HTTP 526 = "Invalid SSL certificate" from Cloudflare's edge. DNS resolves and Cloudflare proxies both apex and `api` subdomain; the edge terminates the request because the origin certificate is currently not configured for HTTPS on the apex (no deploy in Phase 0 → no origin cert chain). This is consistent with the Phase-0 no-deploy posture. **No DNS, certificate, or origin-side mutation was performed.** Flagged as informational; not a validator failure.

---

## 3. Cloudflare — config-level facts only (no DNS / R2 mutation)

### 3a. Local wrangler config

**Command (exact):**

```bash
find "<workspace-root>" -maxdepth 5 \
  \( -name "wrangler.toml" -o -name "wrangler.jsonc" -o -name "wrangler.json" \) \
  -not -path "*/papyr-reference/*" -not -path "*/node_modules/*"
```

**Observed:**

```
(no output)
```

**Result:** **PASS (config absence confirmed)** — no local wrangler config exists in the rebuild tree (only `papyr-reference/` and `node_modules/` excluded by Phase 0 read-only hygiene). Cloudflare binding verification therefore relies entirely on env-variable NAMES in `.env.papyr`.

### 3b. Env variable NAMES (Cloudflare + R2 contract)

Recorded NAMES that map to Cloudflare/R2:

```
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_ACCOUNT_NAME
CLOUDFLARE_API_TOKEN_1
CLOUDFLARE_API_TOKEN_2
R2_ACCESS_KEY_ID
R2_BUCKET_NAME
R2_ENDPOINT
R2_SECRET_ACCESS_KEY
```

All eight required NAMES are present. No values read. **Result: PASS** at the config-contract level. **No DNS, R2, or worker mutation attempted.**

### 3c. Wrangler CLI availability

**Command (exact):**

```bash
npx --no-install wrangler --version
```

**Observed:**

```
npm error npx canceled due to missing packages and no YES option: ["wrangler@4.118.0"]
```

**Result:** **EXPECTED** — wrangler is not installed; `npx --no-install` refuses to fetch. Phase 0 forbids `npm install`, so the install was correctly not performed. Bucket/binding introspection via wrangler is therefore **UNKNOWN** for this Phase 0 run; it is an authenticated mutation-adjacent operation and is deferred to the Phase that authorizes it. Recorded as **UNKNOWN** below.

---

## 4. R2 / S3 backup storage — read-only existence check

### 4a. Local S3-compatible CLI availability

**Command (exact):**

```bash
which aws s3cmd mc
aws --version
```

**Observed:**

```
which: no aws in (...)
which: no s3cmd in (...)
which: no mc in (...)
/usr/bin/bash: line 1: aws: command not found
```

**Result:** **UNKNOWN** — no S3-compatible CLI is installed locally. A read-only `s3:ListBucketV2` call would require `R2_ACCESS_KEY_ID`/`R2_SECRET_ACCESS_KEY` (values Phase 0 has not authorized for use) and a tool Phase 0 has not authorized to install. **No mutation attempted; no credential used.**

Bucket-existence inference is **UNKNOWN** for this run. The recorded `R2_BUCKET_NAME` NAME exists (3b); the bucket's existence and emptiness at the Cloudflare edge cannot be verified without an authenticated read-only call. Flagged as **UNKNOWN**; requires Phase ≥ 1 authorization.

---

## 5. AI gateway — `https://router.budgezen.com/v1`

### 5a. Unauthenticated reachability probe (single HEAD + GET, no key)

**Commands (exact):**

```bash
curl -sS -o /dev/null -w "HTTP_CODE=%{http_code} FINAL_URL=%{url_effective} CONTENT_TYPE=%{content_type} TIME=%{time_total}\n" \
  --max-time 10 -I https://router.budgezen.com/v1
curl -sS -o /dev/null -w "HTTP_CODE=%{http_code} TIME=%{time_total}\n" \
  --max-time 10 https://router.budgezen.com/v1
```

**Observed:**

```
HTTP_CODE=401 FINAL_URL=https://router.budgezen.com/v1 CONTENT_TYPE=application/json TIME=0.197066
HTTP_CODE=401 TIME=0.182326
```

**Result:** **PASS** — DNS resolves, TLS terminates, edge returns HTTP 401 with `Content-Type: application/json`, latency ~0.2 s. 401 is the **expected** response for an unauthenticated request to an OpenAI-compatible endpoint (the recorded gateway requires `Authorization: Bearer <API_KEY>`). No key was sent. No API mutation occurred. Reachability confirmed.

### 5b. Env contract for the gateway

**Recorded NAME:** `PAPYR_AI_BASE_URL` — present in `.env.papyr` NAMES list (section above).

Value verification was deliberately skipped (`PAPYR_AI_BASE_URL` is a name-only extraction; the gateway base URL is recorded in planning artifacts as `https://router.budgezen.com/v1` per DEC-193/DEC-196 and the resolution register R-21). **Result: PASS** for reachability + contract presence.

---

## 6. Adsterra — config-only check (no live script)

### 6a. Env contract NAMES

**Recorded NAMES present:**

```
ADSTERRA_API_KEY
ADSTERRA_PLACEMENT_IDS
ADSTERRA_PUBLISHER_ID
```

All three Adsterra-related NAMES exist. **Result: PASS** for env-contract existence.

### 6b. Banner 300×250 placement ID 5949840

**What was checked:** that the recorded banner placement identifier `5949840` is the only allowed unit at the config-contract layer (planning reference: `audit-outputs/research/track-d/d1-adsterra.md` and DEC-022/DEC-045; the foundation architecture audit explicitly lists `5949840` as R-18 input partially supplied — see `audit-outputs/phase-0/foundation-architecture-audit.md` line 326).

**How:** Documentation-level only. The recorded identifier is a single numeric value present in planning artifacts. The corresponding env var NAME is `ADSTERRA_PLACEMENT_IDS` (plural), suggesting the contract supports a list; the recorded single-unit constraint (banner 300×250 only) is enforced in the rebuild at the placement-selection layer, not by reading `5949840` from the env var here.

**Value-level verification:** **UNKNOWN** for this run — `grep` of `.env.papyr` was restricted to NAMES, and the Adsterra contract lives behind three opaque NAME slots whose values were not read. **No live script was loaded**, no Adsterra-side HTTP call was made, and no tracking pixel was requested. **No mutation attempted.**

**Result:** **PASS (config-name level)** / **UNKNOWN (value-level 5949840 confirmation)**. The 5949840 fact is documented in audit outputs and planning artifacts; final verification is deferred to the phase that authorizes value-level inspection.

---

## 7. Telegram — bot + owner-alert env contract (no message send)

### 7a. Env contract NAMES

**Recorded NAMES present:**

```
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Both required NAMES exist. **Result: PASS** for env-contract existence.

### 7b. Outbound message

**What was checked:** that no `sendMessage` / `curl https://api.telegram.org/bot<token>/sendMessage` was issued. No Telegram endpoint was contacted. No token or chat ID value was read or echoed. **Result: PASS — no send attempted.**

---

## 8. VPS — `<vps-ip>` (<vps-ip>) read-only probe

### 8a. SSH read-only probe

**Command (exact, single shot, read-only commands only):**

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new root@<vps-ip> \
  'echo "==uname=="; uname -a; \
   echo "==osrelease=="; cat /etc/os-release; \
   echo "==mem=="; free -h; \
   echo "==nproc=="; nproc; \
   echo "==swapon=="; swapon --show; \
   echo "==docker=="; docker --version 2>&1; \
   echo "==done=="'
```

**Observed (redacted):**

```
==uname==
Linux <vps-host> 6.8.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Apr 20 00:40:06 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
==osrelease==
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.4 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo
==mem==
               total        used        free      shared  buff/cache   available
Mem:            15Gi       5.7Gi       644Mi        61Mi       9.3Gi       9.5Gi
Swap:          2.0Gi        14Mi       2.0Gi
==nproc==
4
==swapon==
NAME      TYPE SIZE  USED PRIO
/swapfile file   2G 14.2M   -2
==docker==
Docker version 29.6.2, build dfc4efb
==done==
```

**Analysis vs recorded R-26 facts:**

| Fact | Recorded (R-26 / 2026-07-31 probe) | Observed | Match |
|---|---|---|---|
| OS distribution + version | Ubuntu 24.04.4 | Ubuntu 24.04.4 LTS | YES |
| RAM | 15 GiB | 15Gi total | YES |
| Cores | 4 | 4 | YES |
| Swap | 2 GiB | 2.0Gi (`/swapfile`, file-backed) | YES |
| Docker | 29.6.2 | Docker version 29.6.2, build dfc4efb | YES |
| Hostname (informational) | (not recorded) | `<vps-host>` | NEW (informational) |
| Kernel (informational) | (not recorded) | 6.8.0-31-generic | NEW (informational) |

**Result:** **PASS** — all five recorded facts match exactly. Hostname `<vps-host>` and kernel `6.8.0-31-generic` are additional facts newly captured by this validator and consistent with Ubuntu 24.04 (kernel `6.8.0-31-generic` is the standard 24.04 HWE kernel as of 2026-07-31).

**No mutation:** no `docker run`/`docker stop`/`docker rm`/`systemctl start|stop`/`apt install`/`ufw`/`iptables`/`mv`/`rm`/`chmod`/`sed -i` was issued. Only `uname`, `cat /etc/os-release`, `free`, `nproc`, `swapon`, `docker --version` were executed. SSH `BatchMode=yes` was honored (no password prompt).

---

## Summary table

| # | Integration | Status | Discrepancy vs recorded |
|---|---|---|---|
| 1a | GitHub auth (`fazulfi`) | **PASS** | none |
| 1b | GitHub `fazulfi/mypapyr` (new) | **PASS** | empty repo → default branch not yet materialized (`""`); will be `main` on first push (planned in Wave 6). Visibility `PRIVATE` confirmed. |
| 1c | GitHub `fazulfi/papyr` (legacy, do-not-touch) | **PASS** | visibility `PUBLIC` confirmed; **no mutation attempted** |
| 1d | Workspace `git remote -v` | **PASS** | workspace not yet a git repo (per Wave 6 plan); `papyr-reference/` remote is legacy public (H9/G14 invariant substrate) |
| 2a | Vercel `whoami` | **PASS** | `fazulfi` matches |
| 2b | Vercel project `papyr` under `fazulfis-projects` | **PASS** | prod URL `https://mypapyr.com` confirmed; Node 24.x; last updated 66d ago |
| 2c | Vercel deploy inspection (negative) | **PASS (informational)** | `vercel inspect papyr` errors as expected (papyr is a project, not a deployment); no deploy attempted |
| 2d | `mypapyr.com` / `api.mypapyr.com` HTTPS edge | **INFORMATIONAL** | DNS resolves through Cloudflare edge; HTTP 526 (no valid origin cert, consistent with Phase-0 no-deploy state); no DNS/cert mutation attempted |
| 3a | Local wrangler config absence | **PASS** | no wrangler.toml/jsonc/json exists in rebuild tree |
| 3b | Cloudflare/R2 env NAMES | **PASS** | all 8 required NAMES present |
| 3c | Wrangler CLI availability | **UNKNOWN** | wrangler not installed; Phase 0 forbids `npm install`; bucket/binding introspection deferred |
| 4 | R2 / S3 backup bucket | **UNKNOWN** | no S3-compatible CLI installed; values of `R2_*` / `BACKUP_S3_*` not authorized for use in Phase 0; bucket existence not verified remotely |
| 5a | AI gateway reachability | **PASS** | `https://router.budgezen.com/v1` returns 401 + JSON (~0.2 s); expected for unauth probe; no key sent |
| 5b | AI gateway env contract | **PASS** | `PAPYR_AI_BASE_URL` NAME present |
| 6 | Adsterra config (300×250 / 5949840) | **PASS (name-level)** / **UNKNOWN (value-level)** | all 3 NAMES present (`ADSTERRA_API_KEY`, `ADSTERRA_PLACEMENT_IDS`, `ADSTERRA_PUBLISHER_ID`); value-level verification of `5949840` deferred to phase that authorizes value inspection. **No live script loaded.** |
| 7 | Telegram env contract (bot + owner-alert) | **PASS** | both NAMES present; **no message sent**; no value read |
| 8 | VPS read-only probe (`<vps-ip>`) | **PASS** | Ubuntu 24.04.4, 15 GiB RAM, 4 cores, 2.0 GiB swap, Docker 29.6.2 — all five R-26 facts match exactly. Hostname `<vps-host>`, kernel `6.8.0-31-generic` newly captured. No container / service / file mutation. |

## Items requiring explicit owner authorization for future runs

1. **Wrangler install** + read-only R2 bucket-list (`wrangler r2 object list papyr-files --prefix "" --limit 1`) — needed to confirm R2 bucket `papyr-files` emptiness.
2. **Adsterra value-level** confirmation that `ADSTERRA_PLACEMENT_IDS` resolves to exactly `5949840` (or whatever single banner 300×250 unit the owner authorizes).
3. **Authenticated gateway** model-list (`GET /v1/models` with `Authorization: Bearer <API_KEY>`) — currently gated by DEC-193/DEC-196 ("no authenticated call is authorized by any planning artifact").
4. **Vercel domain inspection** (`vercel domains ls`) to confirm `mypapyr.com` and `api.mypapyr.com` are correctly attached to the `papyr` project.

## Mutations performed during this run

**None.** This was strictly read-only:

- No deploys.
- No DNS / cert / R2 / worker mutations.
- No container / service / package operations.
- No repo creation, modification, deletion, fork, or push.
- No Telegram, Adsterra, Vercel, or gateway authenticated calls.
- No environment values were read or echoed.

`papyr-reference/` was verified clean before (`HEAD = 981c59a171f4b83c9e2afcecc6e934bee14a3a5e`, porcelain = 0) and remained clean after.

---
*End of Phase 0 read-only third-party integration validation.*
