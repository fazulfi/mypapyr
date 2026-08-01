# Phase 0 — Current Tooling & Secure CI Research

**Deliverable for:** Papyr rebuild Phase 0 (pre-execution prerequisites) and the Phase 1 CI core gate (FD-04, DEC-177).
**Author:** Research subagent (LIBRARIAN)
**Retrieval date (all version/SHA data):** 2026-08-01 (Asia/Bangkok). Version numbers are point-in-time; re-verify at install time per DEC-056 ("versions are pinned at install time from current official releases").
**Scope:** CI only, fork-safe, `contents: read`-style least privilege, no production secrets, no deploy jobs (DEC-160/DEC-177 boundary). `papyr-reference/` was only read, never modified.

---

## 0. How to read this document

- **Authoritative fact** = observed from an official source (registry API, GitHub release/tag API, official docs, upstream source code) on the retrieval date, with URL.
- **Recommendation** = my proposal for Phase 0/1 tooling choices, labeled **RECOMMEND**.
- **Uncertainty** = explicitly flagged in §9 with the evidence gap.

---

## 1. Executive summary — recommended minimal dependency set

Recommended additions to the Phase 1 CI core gate (`.github/workflows/ci.yml`, per FD-04), all pinned to immutable SHAs (see §3 table):

| Purpose | Tool / Action | Version (2026-08-01) | License | Why / caveat |
|---|---|---|---|---|
| Checkout | `actions/checkout` | **v7.0.1** | MIT | Node 24 runtime; v7 blocks fork-PR checkout on `pull_request_target` (June 2026 security change). Legacy `@v4` runs on Node 20, which runners are dropping fall 2026. |
| Node setup | `actions/setup-node` | **v7.0.0** | MIT | Node 24 runtime; ESM internals; cache outputs. |
| Python setup | `actions/setup-python` | **v7.0.0** | MIT | ESM only vs v6; v6+ = Node 24 runtime. |
| Deps cache (optional) | `actions/cache` | **v6.1.0** | MIT | Node 24; note cache-poisoning guidance and read-only cache for untrusted triggers. |
| Artifacts (optional, e.g. Playwright report) | `actions/upload-artifact` / `actions/download-artifact` | **v7.0.1 / v8.0.1** | MIT | Digest (SHA-256) verification; download-artifact v8 fails on hash mismatch by default. |
| Vulnerability scan (PR + schedule) | `google/osv-scanner-action` reusable workflows | **v2.3.8** | Apache-2.0 | OSV.dev; no API key; needs `security-events: write` for SARIF upload. |
| PR dependency/license review | `actions/dependency-review-action` | **v5.0.0** | MIT | SPDX license allow/deny + vuln diff; `contents: read` only. Public repos free; private needs GHAS. |
| Code scanning | `github/codeql-action` | **v4.37.4** | MIT | Needs `security-events: write` (+`actions: read` for some modes). |
| Container/image scan | **Trivy** CLI | **v0.72.0** | Apache-2.0 | Plan (FD-04) requires Trivy on built images. |
| Secret scanning (defense-in-depth) | **gitleaks** CLI | **v8.30.1** | MIT | Prefer the CLI over `gitleaks-action` (action has a proprietary EULA — §5.2). |
| Workflow YAML lint | **actionlint** | **v1.7.12** | MIT | Catches workflow errors incl. permissions issues. |
| Shell lint | **ShellCheck** | **v0.11.0** | GPL-3.0 | Ubuntu 24.04 runner only ships 0.9.0 — install pinned binary (§5.3). |
| YAML lint | **yamllint** | **v1.38.0** | GPL-3.0 | For `.github` configs, compose, etc. |
| Markdown lint | **markdownlint-cli2** | **v0.23.2** | MIT | Docs are governed records; keeps them consistent. |
| Frontend runtime | **Node.js 24 LTS** | **24.18.1** | MIT | Active LTS (Krypton), security to 2028-04; Node 20 EOL 2026-04. |
| Frontend stack | **Next.js 16.2.12**, **React 19.2.4** (per plan), **TypeScript 6.0.x**, **ESLint 9.x**, **Prettier 3.9.6**, **Vitest 4.1.10**, **Playwright 1.62.1**, **Tailwind 4.3.3** | as listed | MIT/Apache | **Do NOT jump to TypeScript 7 yet** — typescript-eslint does not support it (§4.3). |
| Backend runtime | **Python 3.13.x** (3.13.14) in CI | 3.13.14 | PSF | 3.11 (legacy target) EOL 2027-10; 3.13 supported to 2029-10. |
| Backend stack | **FastAPI 0.141.1**, **uvicorn 0.52.0**, **pydantic 2.13.4**, **ruff 0.16.1**, **pytest 9.1.1**, **pytest-asyncio 1.4.0**, **pytest-cov 7.1.0**, **httpx 0.28.1**, **boto3 1.43.61** | as listed | MIT/BSD/Apache | Legacy pins are far behind (ruff 0.7.4). |
| Python manager (optional) | **uv 0.12.0** + `astral-sh/setup-uv` v9 | 0.12.0 | Apache-2.0 | Optional; plan's backend scripts assume `requirements*.txt` + pip/ruff/pytest, so uv is a Phase-1 decision, not Phase 0. |
| Package manager | **npm** (bundled with Node 24; npm 11.x) | — | MIT | **RECOMMEND keep npm** — `package-lock.json` exists and plan scripts use `npm test/lint/format:check`. pnpm 11.18.0 is a viable alternative (§4.6). |
| Cloudflare/R2 validation | **wrangler 4.118.0** + `cloudflare/wrangler-action` v4 | 4.118.0 | Apache-2.0 | `wrangler deploy --dry-run` runs **without** API token (§7). No secrets in CI. |

**Not in the minimal set (optional):** `step-security/harden-runner` v2.20.0 (egress control; adds a third-party action), `hadolint` 2.15.1 (Dockerfile lint), `pip-audit` 2.10.1 (Python-only vuln scan), `mypy` 2.3.0 (not in legacy dev requirements).

---

## 2. GitHub Actions platform state (authoritative, 2026-08-01)

### 2.1 Runner runtime migration — Node 20 → Node 24
- GitHub-hosted runners defaulted to **Node 24** on **2026-06-16** and will **drop Node 20 in fall 2026** (third-party summary of the migration; see https://starsling.dev/best-practices/github-actions/pin-action-shas retrieved 2026-07-22, which warns that checkout v4/setup-node v4/cache v4 "warn today and will fail later").
- New action majors are Node-24 based and require **Actions Runner ≥ 2.327.1** (hosted runners satisfy this): `setup-python` v6 breaking change note (https://github.com/actions/setup-python README), `dependency-review-action` v5 note (https://github.com/actions/dependency-review-action README).
- **Implication:** Phase 1 must use the new majors (checkout v7, setup-node v7, setup-python v7, cache v6, upload/download-artifact v7/v8). The legacy `ci.yml` pins (`checkout@v4`, `setup-node@v4`, `setup-python@v5`, Node 20, Python 3.11) are obsolete.

### 2.2 June 2026 security changes (authoritative changelogs)
- **Safer `pull_request_target` defaults for checkout** (2026-06-18): `actions/checkout` now blocks checking out untrusted fork PR code in `pull_request_target`/`workflow_run` unless explicitly opted out after risk review. Backported to older versions. https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout/ — implemented in checkout v7.0.0 release notes ("block checking out fork pr for pull_request_target and workflow_run", https://github.com/actions/checkout/releases/tag/v7.0.0).
- **Workflow trigger policies** (2026-06-18): enterprise/org/repo policy control over who/what can trigger workflows. https://github.blog/changelog/2026-06-18-control-who-and-what-triggers-github-actions-workflows/
- **Read-only Actions cache for untrusted triggers** (2026-06-26): less-trusted workflows (e.g. fork PRs) can no longer write to caches shared with privileged workflows. https://github.blog/changelog/2026-06-26-read-only-actions-cache-for-untrusted-triggers/
- **Actions network firewall** — technical preview (logs egress; future blocking). https://github.com/github-early-access/actions-native-egress-firewall/

### 2.3 Official security reference
- GitHub consolidated "Secure use reference" (authoritative for least-privilege, script injection, untrusted checkout, pinning): https://docs.github.com/en/actions/reference/security/secure-use (retrieved 2026-08-01). Key points:
  - `GITHUB_TOKEN` default should be read-only for `contents`; escalate per-job only.
  - Fork `pull_request` runs are read-only and have **no access to secrets**; `push`, `issue_comment`, `pull_request_target`, `workflow_run` are privileged surfaces.
  - Avoid `pull_request_target`/`workflow_run` with untrusted checkout; prefer `workflow_run` over `pull_request_target` when privilege separation is needed.
  - Inline scripts must pass untrusted context via an intermediate `env:` variable (script-injection mitigation), not by string interpolation into `run:`.
  - **Pin actions to a full-length commit SHA** — "currently the only way to use an action as an immutable release"; verify the SHA is from the action's repo, not a fork.
  - Dependabot keeps SHA-pinned actions updated **only when the version is kept as a trailing comment** (`@<sha> # v7.0.0`); Dependabot alerts are only created for actions using semantic-version tags, not SHA pins.

### 2.4 Action supply-chain integrity (native features + ecosystem tools)
- **Artifacts:** upload/download-artifact compute a SHA-256 `digest`; download-artifact v8 defaults `digest-mismatch: error` (fails on tamper). https://github.blog/changelog/2025-03-18-github-actions-now-supports-a-digest-for-validating-your-artifacts-at-runtime/ ; https://github.com/actions/download-artifact/releases
- **Release assets:** GitHub computes immutable SHA-256 digests for all release assets (viewable in UI/API/`gh`). https://github.blog/changelog/2025-06-03-releases-now-expose-digests-for-release-assets/ — used in §5 to pin CLI binary downloads.
- **Org policy enforcement:** admins can require full-SHA pinning via allowed-actions policy (2025-08-15). https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/
- **2026 roadmap:** GitHub announced a `dependencies:` section in workflow YAML to lock direct + transitive action SHAs (resolved via `gh`; fail-fast verification). This is a **roadmap item, not yet stable** — do not design around it, but expect it. https://github.blog/news-insights/product-news/whats-coming-to-our-github-actions-2026-security-roadmap/
- **Third-party lockfile tools** (verified active): `gjtorikian/gh-actions-lockfile` (https://github.com/gjtorikian/gh-actions-lockfile), `steph-owl/action-locker` (https://github.com/steph-owl/action-locker), `suzuki-shunsuke/pinact` (https://github.com/suzuki-shunsuke/pinact), `chains-project/ghasum` (https://github.com/chains-project/ghasum). Optional; not needed for the minimal gate.

> **UNCERTAINTY (§9.1):** A native "verify the SHA-256 of the downloaded action archive" input for `uses:` was **not confirmed** in official docs on 2026-08-01 (searched GitHub changelog + docs; no stable syntax found). Current official guidance remains full-SHA pinning + version comment + optional org policy. Do not rely on a `hash`-style input.

---

## 3. Immutable Action SHAs (retrieved 2026-08-01)

Resolved from `GET https://api.github.com/repos/<owner>/<repo>/tags?per_page=2` (commit SHA the tag points to). **Re-derive before committing Phase 1 workflow files** with:

```bash
# For lightweight tags:
gh api repos/actions/checkout/git/ref/tags/v7.0.1 --jq .object.sha
# Annotated tags return a tag object; dereference:
gh api repos/actions/checkout/git/ref/tags/v7.0.1 --jq '.object.type, .object.sha'
gh api repos/actions/checkout/git/tags/<tag-object-sha> --jq .object.sha
```

| `uses:` reference (pinned form) | Version comment | Commit SHA (2026-08-01) |
|---|---|---|
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-node` | v7.0.0 | `820762786026740c76f36085b0efc47a31fe5020` |
| `actions/setup-python` | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| `actions/cache` | v6.1.0 | `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` |
| `actions/upload-artifact` | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| `actions/download-artifact` | v8.0.1 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |
| `github/codeql-action/init` (+ `analyze`, `upload-sarif`) | v4.37.4 | `f205ea1c3313d32999d8d6a48b4f6530d4437b38` |
| `actions/dependency-review-action` | v5.0.0 | `a1d282b36b6f3519aa1f3fc636f609c47dddb294` |
| `google/osv-scanner-action/.github/workflows/osv-scanner-reusable-pr.yml` and `osv-scanner-reusable.yml` | v2.3.8 | `9a498708959aeaef5ef730655706c5a1df1edbc2` |
| `astral-sh/setup-uv` (only if adopting uv) | v9.0.0 | `c771a70e6277c0a99b617c7a806ffedaca235ff9` |
| `pnpm/action-setup` (only if adopting pnpm) | v6.0.9 | `0ebf47130e4866e96fce0953f49152a61190b271` |
| `cloudflare/wrangler-action` (optional validation job) | v4.0.0 | `ebbaa1584979971c8614a24965b4405ff95890e0` |
| `gitleaks/gitleaks-action` — **not recommended** (§5.2) | v3.0.0 | `e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e` |
| `step-security/harden-runner` (optional) | v2.20.0 | `bf7454d06d71f1098171f2acdf0cd4708d7b5920` |

Notes:
- `actions/setup-node` also publishes the `v7` alias to the same commit; use the explicit `v7.0.0` comment.
- `osv-scanner-action` reusable workflows internally SHA-pin their own steps (e.g., checkout `@8e8c483db84b4bee98b60c0593521ed34d9990e8 # v6.0.1`, upload-artifact `@bbbca2ddaa5d8feaa63e36b76fdaad77386f024f # v7.0.0`, codeql upload-sarif `@cdefb33c0f6224e58673d9004f47f7cb3e328b89 # v4.31.10`) — a good reference for the pin pattern: https://github.com/google/osv-scanner-action/blob/main/.github/workflows/osv-scanner-reusable.yml
- `actions/checkout` v7.0.0 (SHA `9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0`) is the release that introduced the fork-PR block; v7.0.1 is the current patch.

---

## 4. Runtime/toolchain versions (authoritative, 2026-08-01)

### 4.1 Node.js — use 24 LTS
- From `https://nodejs.org/dist/index.json` and https://endoflife.date/nodejs (updated 2026-07-30):
  - **Node 24 LTS "Krypton"**: latest **24.18.1** (2026-07-28); Active LTS until **2026-10-20**, security support until **2028-04-30**.
  - Node 26: Current since 2026-05-05; becomes LTS **2026-10-27** (too early to standardize on for Phase 1; revisit after Q4 2026).
  - Node 22: Maintenance LTS, security until 2027-04-30 (acceptable fallback).
  - Node 20: **EOL 2026-04-30** — do not use (legacy CI used Node 20).
- **RECOMMEND:** `node-version: 24` (or `24.18.x`) in `setup-node`; this matches the runner runtime and Next.js 16 (min Node 20.9, https://nextjs.org/docs/app/guides/upgrading/version-16).

### 4.2 Frontend packages (npm registry `latest`, 2026-08-01)
| Package | Latest | Legacy repo pin | Note |
|---|---|---|---|
| `next` | **16.2.12** | 16.2.4 | Upgrade within 16.x. TS 7 needs `experimental.useTypeScriptCli` (§4.3). |
| `typescript` | 7.0.2 | ^5 | **See §4.3 — pin 6.0.x, not 7.** |
| `eslint` | 10.8.0 | ^9 | ESLint 10 (Feb 2026) requires Node `^20.19 || ^22.13 || >=24`, removed eslintrc entirely. **RECOMMEND stay on ESLint 9.x until eslint-config-next 16.2.12 + typescript-eslint stack is validated on 10.** |
| `prettier` | 3.9.6 | ^3.8.3 | — |
| `vitest` | 4.1.10 | ^3.2.1 | v3→v4 is a major; verify breaking changes at Phase 1. |
| `@playwright/test` | 1.62.1 | ^1.60.0 | — |
| `tailwindcss` | 4.3.3 | ^4 | — |
| `pnpm` | 11.18.0 | n/a | Alternative manager; §4.6. |
| `markdownlint-cli2` | 0.23.2 | n/a | — |

### 4.3 TypeScript — do not jump to 7 yet (authoritative)
- **TypeScript 7.0 GA 2026-07-08** — 10x faster native (Go) port, but **ships no JavaScript compiler API**; TypeScript 7.1 is expected to ship a new API (~Oct 2026). Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- **typescript-eslint does not support TS 7**: supported range tops out below 6.1.0; the day-one support issue was closed "not planned". ESLint core is blocked behind it. Source: https://www.digitalapplied.com/blog/typescript-7-native-compiler-early-adopter-migration-readiness (2026-07-15) and typescript-eslint issues #12518/#12521.
- **Next.js** requires `experimental.useTypeScriptCli: true` to build with TS 7 (option added in Next 16.2.x backports; default checker still uses the JS API): https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli (docs version 16.2.12, updated 2026-07-23) and https://github.com/vercel/next.js/discussions/95633
- **RECOMMEND:** `typescript@6.0.x` (typescript-eslint-compatible, plain `next build` type check), while following TS 6 deprecation cleanup. Revisit TS 7 + `useTypeScriptCli` when 7.1 ships an API and typescript-eslint ports.

### 4.4 Backend packages (PyPI JSON API, 2026-08-01)
| Package | Latest | Legacy repo pin | License | Note |
|---|---|---|---|---|
| `fastapi` | **0.141.1** | 0.115.12 | MIT | Verify 0.116→0.141 breaking changes at Phase 1. |
| `uvicorn` | 0.52.0 | 0.34.2 | BSD-3-Clause | — |
| `pydantic` | 2.13.4 | (transitive) | MIT | — |
| `boto3` | 1.43.61 | 1.38.10 | Apache-2.0 | R2 S3 API. |
| `ruff` | **0.16.1** | 0.7.4 | MIT | Legacy pin is 2+ years behind; legacy `ruff.toml` config is expected to remain valid (verify at Phase 1). |
| `pytest` | 9.1.1 | 8.3.5 | MIT | v9 is a major; verify breaking changes. |
| `pytest-asyncio` | 1.4.0 | 0.25.3 | Apache-2.0 | Major jump; verify `asyncio_mode = auto` config still applies. |
| `pytest-cov` | 7.1.0 | 5.0.0 | MIT | — |
| `httpx` | 0.28.1 | 0.28.1 | BSD-3-Clause | unchanged |
| `mypy` | 2.3.0 | not in dev reqs | MIT | Optional. |
| `uv` | 0.12.0 | n/a | Apache-2.0 | Optional manager. |
| `yamllint` | 1.38.0 | n/a | GPL-3.0 | — |
| `pip-audit` | 2.10.1 | n/a | Apache-2.0 | Optional Python-only scanner. |

### 4.5 Python runtime
- From https://endoflife.date/api/python.json (2026-08-01): 3.14 (latest 3.14.6, EOL 2030-10), **3.13 (latest 3.13.14, EOL 2029-10)**, 3.12 (EOL 2028-10), 3.11 (latest 3.11.15, EOL 2027-10).
- **RECOMMEND:** `python-version: '3.13'` in `setup-python` for CI; keep the codebase's `ruff.toml target-version = "py311"` (or bump to `py313`) as a Phase 1 decision. 3.11 remains supported until 2027-10 if the owner prefers to minimize churn.

### 4.6 Package manager — keep npm
- Repo already has `frontend/package-lock.json`; plan scripts are `npm test/lint/format:check`; `setup-node` caches npm out of the box. **RECOMMEND npm (bundled 11.x with Node 24).**
- If pnpm is chosen later: pnpm 11.18.0 is current (pnpm 10 EOL 2027-04-30, per https://endoflife.date/api/pnpm.json), pin `pnpm/action-setup` v6.0.9 (§3), and commit `pnpm-lock.yaml`.

---

## 5. Static-analysis / scanning tool versions + install pattern

### 5.1 GitHub-native secret scanning (authoritative)
- **Secret scanning**: free for **public** repositories; private repositories need GitHub Code Security (formerly GHAS/Advanced Security). Push protection: free for all public repos (GA since 2023-05-09, https://github.blog/news-insights/product-news/push-protection-is-generally-available-and-free-for-all-public-repositories/), user-level push protection is on by default for public repos; private repos need the paid tier. Docs: https://docs.github.com/en/code-security/concepts/secret-security/push-protection ; https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository
- **Relevant detectors:** as of June 2026, Cloudflare account/user/global API keys are in push protection **by default for all repositories with secret scanning enabled, including free public repos**. https://github.blog/changelog/2026-06-17-secret-scanning-updates-june-2026/
- **RECOMMEND:** enable Secret scanning + Push protection in repo settings (free on public). Native scanning is the primary layer; gitleaks is a supplementary pre-merge check.

### 5.2 gitleaks — use the CLI, not the action
- gitleaks CLI **8.30.1** is MIT; the **`gitleaks/gitleaks-action` wrapper v3.0.0 carries a proprietary end-user license agreement** (its `action.yml` header: "You may use this code under the terms of the GITLEAKS-ACTION END-USER LICENSE AGREEMENT", https://github.com/gitleaks/gitleaks-action). **RECOMMEND installing the CLI directly** (pinned binary + digest, below) and running `gitleaks detect --redact --source .` on `pull_request`; this avoids the proprietary action entirely.
- Pinned install (digests from GitHub release API, 2026-08-01):
  - `gitleaks_8.30.1_linux_x64.tar.gz` sha256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`
  - checksums file `gitleaks_8.30.1_checksums.txt` sha256 `061476c21adaf5441516f96f185c1a4706a83cd6329b9b38762271b3d4a52fae`
  - Verify with `sha256sum -c gitleaks_8.30.1_checksums.txt` (or the single-file digest).

### 5.3 ShellCheck
- Ubuntu 24.04 runner image ships **ShellCheck 0.9.0** (https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md). For 0.11.0 install the pinned binary:
  - `shellcheck-v0.11.0.linux.x86_64.tar.xz` sha256 `8c3be12b05d5c177a04c29e3c78ce89ac86f1595681cab149b65b97c4e227198` (GitHub release asset digest, 2026-08-01; the release does **not** publish a checksums file, so use the release-asset digest).
- Used for `scripts/check-ci.sh` (FD-04) and any shell in the repo.

### 5.4 actionlint (workflow YAML lint)
- actionlint **1.7.12** (MIT). Pinned install:
  - `actionlint_1.7.12_linux_amd64.tar.gz` sha256 `8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8`
  - checksums file `actionlint_1.7.12_checksums.txt` sha256 `433028cf0ba3c42163ea1a668dedce30fcdbe84fe912b1a5e288c006eab8a4f5`
  - Alternative: Docker image `rhysd/actionlint:1.7.12` pinned by digest (docker supply chain is separate — digest-pin if used).
- Also consider `zgosalvez/github-actions-ensure-sha-pinned-actions` (or actionlint + a lockfile tool) to enforce SHA pinning in CI; optional for the minimal gate.

### 5.5 Trivy (planned by FD-04: "security scanning (Trivy) on built images")
- Trivy **0.72.0** (Apache-2.0). Release assets incl. `trivy_0.72.0_checksums.txt` (sha256 `ebe9d19a774b950e240b1017a038e9b5a002ea068e02023369ff6d241c10c580`) and `trivy_0.72.0_Linux-64bit.tar.gz` (sha256 `bbb64b9695866ce4a7a8f5c9592002c5961cab378577fa3f8a040df362b9b2ea`). Verify via `sha256sum -c trivy_0.72.0_checksums.txt`.
- Usage for the core gate: build the production image (Dockerfile.production) in CI, then `trivy image --exit-code 1 --severity HIGH,CRITICAL <image>` (or `--severity CRITICAL` per owner risk appetite). Trivy also scans `requirements*.txt`/`package-lock.json` via `trivy fs .` if image build is not desired. Existing legacy evidence of Trivy usage: `papyr-reference/docs/security/trivy-papyr-backend.json|.txt`.

### 5.6 osv-scanner (vulnerability scanning, no API key)
- CLI **v2.4.0** (Apache-2.0) — release assets `osv-scanner_linux_amd64` sha256 `15314940c10d26af9c6649f150b8a47c1262e8fc7e17b1d1029b0e479e8ed8a0`; `osv-scanner_SHA256SUMS` sha256 `9d6fff9bac4d77269c8b04a1b74b72cd087842106abd11d8e0426ab07b2dd441`. README: https://github.com/google/osv-scanner
- **GitHub Action**: separate repo `google/osv-scanner-action` (latest **v2.3.8**, SHA §3), consumed as reusable workflows:
  - PR diff scan: `google/osv-scanner-action/.github/workflows/osv-scanner-reusable-pr.yml@<sha> # v2.3.8`
  - Full/scheduled scan: `google/osv-scanner-action/.github/workflows/osv-scanner-reusable.yml@<sha> # v2.3.8`
  - The reusable workflows require `permissions: security-events: write` (to upload SARIF to Code scanning); they internally use `actions: read, contents: read, security-events: write`. Docs: https://google.github.io/osv-scanner/github-action/
  - License scanning: `osv-scanner --licenses "MIT,Apache-2.0" <dir>` via deps.dev (no key). https://google.github.io/osv-scanner/usage/license-scanning/
- **RECOMMEND:** use the reusable workflows for PR + scheduled scans; they already handle SARIF upload and fail-on-vuln. This is the strongest no-key vuln scanner for the plan's npm+requirements manifests.

### 5.7 dependency-review-action v5 (PR dependency + license gate)
- v5.0.0 runtime is Node 24 (runner ≥ 2.327.1). Minimal permissions: `permissions: contents: read`. Options: `fail-on-severity` (default `low`), `allow-licenses`/`deny-licenses` (SPDX; mutually exclusive), `license-check` (default true), `comment-summary-in-pr` (needs `pull-requests: write` — keep `never` for least privilege). Public repos free; private needs GHAS. https://github.com/actions/dependency-review-action (README, retrieved 2026-08-01)
- **License caveats for this project:** legacy runtime includes **AGPL/GPL-adjacent engines** (e.g., Ghostscript AGPL-3.0 — approved by DEC-195 as an unmodified subprocess; legacy PyMuPDF is AGPL-3.0 but the rebuild replaces it with pypdfium2 per the plan's approved stack). A CI `allow-licenses` allow-list must therefore be **decided by the owner with legal review (G-7)**, not invented in Phase 0. CI should fail on *introduced* non-compliant licenses only after that decision.

---

## 6. Dependabot configuration (authoritative syntax)

Docs: https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates (retrieved 2026-08-01). Recommended `.github/dependabot.yml` for the rebuild monorepo:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"   # keeps SHA-pinned actions updated when a trailing # vX.Y.Z comment exists
    directory: "/"
    schedule: { interval: "weekly" }
    groups: { actions: { patterns: ["*"] } }
    open-pull-requests-limit: 10
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule: { interval: "weekly" }
    versioning-strategy: increase          # update the manifest range, not just the lockfile
    groups: { frontend-minor-patch: { update-types: ["minor", "patch"] } }
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule: { interval: "weekly" }
    groups: { backend-minor-patch: { update-types: ["minor", "patch"] } }
```

Facts to honor:
- Dependabot updates actions only via GitHub repo syntax (`owner/repo@v6` or `@<commit>`), reads the version from a same-line trailing comment, and **does not alert on SHA-pinned actions without semver tags** (§2.3). SHA-pinned + comment is the recommended pattern.
- Dependabot security updates and alerts are free for public repos (and for private with Code Security); dependency graph is enabled for public repos.

---

## 7. Cloudflare / R2 validation without secrets

- **wrangler 4.118.0** (npm latest; Apache-2.0). `cloudflare/wrangler-action` v4 defaults to Wrangler v4 and supports `wranglerVersion`, `workingDirectory`, `preCommands`/`postCommands`, `command` (https://github.com/cloudflare/wrangler-action README).
- **`wrangler deploy --dry-run` does not require authentication.** Authoritative source (wrangler source, current): `const accountId = args.dryRun ? undefined : await requireAuth(config);` in `packages/wrangler/src/deploy/index.ts` (https://github.com/cloudflare/workers-sdk/blob/c09dbd7e/packages/wrangler/src/deploy/index.ts). Recent change (2026-03) also runs asset-directory validation during dry-run (https://github.com/cloudflare/workers-sdk/pull/13036). Third-party CI guidance agrees: "Dry-run does not need Cloudflare deploy credentials" (https://mayfield.io/blog/wrangler-deploy-dry-run-ci-before-merge/).
- **RECOMMEND for the CI core gate (no secrets):**
  - `wrangler deploy --dry-run` to validate wrangler config + bundling for any Workers-side artifact (if the rebuild keeps a Workers component).
  - `wrangler types` (or the equivalent config-schema validation) to validate bindings/types if Workers code exists.
  - **R2 live checks (e.g., `wrangler r2 bucket list`, object reads) require credentials and are out of scope** for fork-safe CI; keep R2 logic covered by unit tests with mocked boto3 (legacy tests already do this via `R2_*` env vars), and reserve live R2 validation for the owner-gated deploy path (G-4) or future OIDC federation. No R2 secrets may appear in `.github/workflows/`.
- Cloudflare secret scanning detectors (account/user/global API tokens) are push-protected by default on public repos (§5.1) — an extra safety net for R2/Cloudflare credentials.

---

## 8. No-CD, least-privilege workflow guidance (for FD-04 `ci.yml`)

Design targets (matching the plan's FD-04 step 1 assertion: "no `deploy` job exists and no secret is exposed to `pull_request_target` events"):

1. **Triggers (fork-safe):** `pull_request` (against `main`) + `push` (to `main`). **Do not use `pull_request_target`** for any job. Add `merge_group` only if merge queues are used. Add `concurrency: { group: <workflow>-<ref>, cancel-in-progress: true }` (legacy CI already does this).
2. **Permissions:** top-level `permissions: contents: read`; for jobs that don't need a token at all, `permissions: {}`; only CodeQL/osv jobs add `security-events: write` (CodeQL also needs `actions: read` when using the standard init/analyze flow). No job should request `id-token`, `deployments`, `packages`, or `pull-requests: write` (unless PR comments are explicitly wanted; keep `comment-summary-in-pr: never`).
3. **Checkout:** `actions/checkout@<sha> # v7.0.1` with `persist-credentials: false` (the token is not needed for CI-only). v7's fork-PR block is a bonus defense in depth; still avoid `pull_request_target`.
4. **No secrets anywhere.** All jobs use public registries; env values for tests are dummy strings (legacy pattern). No `secrets:` mapping, no `env` referencing repo secrets.
5. **Script injection:** any use of `github.event.*`/`github.ref` in `run:` must go through an `env:` variable, not string interpolation (§2.3).
6. **Job matrix (minimal gate):**
   - `lint` (frontend: eslint 9 + prettier check; backend: ruff check + ruff format --check; actionlint on workflows; yamllint; ShellCheck on `scripts/`; markdownlint on docs) — `permissions: {}` or `contents: read`.
   - `test` (frontend vitest; backend pytest; optional Playwright e2e in a separate job with artifact upload, `retention-days` ≤ 14).
   - `build` (frontend `next build` with dummy `NEXT_PUBLIC_*` env; production image build for Trivy scan per FD-04).
   - `security-scan` (osv-scanner reusable workflows on PR/schedule; dependency-review on PR; CodeQL init/analyze; Trivy on built image; gitleaks CLI on PR) — `security-events: write` only here.
7. **Cache note:** fork PRs get read-only cache (June 2026 platform change); avoid treating cache as trusted for release/privileged workflows (none exist here).
8. **Artifacts:** if uploaded, keep retention short and rely on upload/download-artifact digest verification (§2.4).
9. **Policy hardening (repo settings, not workflow files):** enable "Require actions to be pinned to a full-length commit SHA" and an allowed-actions list when the repo exists (owner-gated, G-1); enable secret scanning + push protection (free on public).

---

## 9. Uncertainties and unresolved questions

1. **Native action SHA-256 `hash` input: NOT confirmed.** As of 2026-08-01 I could not find a stable, documented input that verifies the SHA-256 of a downloaded action archive. Official guidance = full-SHA pinning + version comments + optional org policy; content-hash protection for actions is currently provided by third-party lockfile tools and the (roadmap) native `dependencies:` section. Design around SHA pinning.
2. **TypeScript 7 is a moving target.** typescript-eslint has no committed TS7 timeline; Next.js support requires the experimental `useTypeScriptCli` flag. Recommendation (TS 6.0.x) is deliberately conservative; re-evaluate at Phase 1 install time and after TS 7.1.
3. **ESLint 10 vs eslint-config-next 16.2.12:** ESLint 10 removed eslintrc and changed config lookup; whether `eslint-config-next` 16.2.12 is validated on ESLint 10 was not verified. Default to ESLint 9.x.
4. **Major-version upgrades in the backend stack** (ruff 0.7→0.16, pytest 8→9, pytest-asyncio 0.25→1.4, FastAPI 0.115→0.141): breaking-change lists were not exhaustively reviewed; verify each at Phase 1 (legacy `ruff.toml`, `pytest.ini` asyncio settings expected to carry over).
5. **Vitest 3→4 breaking changes** not reviewed; verify at Phase 1.
6. **License allow-list decision (owner/legal, G-7):** CI license gates should only be configured after the owner decides the policy, because approved engines include AGPL components (Ghostscript; legacy PyMuPDF replaced by pypdfium2 per plan). Phase 0 must not invent the allow-list.
7. **Hosting disposition R-02:** all GitHub-specific guidance here presumes GitHub Actions is approved (proposal per R-02). If another CI provider is chosen, the pinning/least-privilege principles transfer but the exact action references do not.
8. **osv-scanner-action tag ≠ osv-scanner CLI tag:** the reusable workflow repo tags independently (action v2.3.8 vs CLI v2.4.0). Keep them separate in the pin table.
9. **gitleaks-action license:** the wrapper is proprietary (EULA); the CLI is MIT. Recommended CLI-only approach avoids the license; confirm with owner if the action wrapper is preferred.
10. **Trivy severity/exit-code thresholds** are owner decisions (risk appetite); FD-04 requires the scan stage, not the specific threshold.

---

## 10. Verification evidence (commands/sources used, all run 2026-08-01)

- GitHub tags/SHAs: `curl https://api.github.com/repos/<owner>/<repo>/tags?per_page=2` for checkout, setup-node, setup-python, cache, upload/download-artifact, codeql-action, dependency-review-action, attest-build-provenance, setup-uv, pnpm/action-setup, wrangler-action, gitleaks-action, harden-runner, shellcheck, actionlint, hadolint, gitleaks, google/osv-scanner, trivy, google/osv-scanner-action.
- Release asset digests: `curl https://api.github.com/repos/.../releases/tags/<tag>` for shellcheck v0.11.0, actionlint v1.7.12, gitleaks v8.30.1, trivy v0.72.0, osv-scanner v2.4.0.
- npm versions: `curl https://registry.npmjs.org/<pkg>/latest` (next, typescript, eslint, prettier, vitest, @playwright/test, tailwindcss, pnpm, wrangler, @cloudflare/workers-types, markdownlint-cli2, license-checker-rseidelsohn).
- PyPI versions: `curl https://pypi.org/pypi/<pkg>/json` (fastapi, uvicorn, pydantic, ruff, mypy, pytest, pytest-asyncio, pytest-cov, httpx, boto3, uv, yamllint, pip-audit, pip-licenses).
- Node releases + LTS: `curl https://nodejs.org/dist/index.json`; EOL: https://endoflife.date/nodejs , https://endoflife.date/api/python.json , https://endoflife.date/api/pnpm.json .
- Official docs fetched: GitHub "Secure use reference" (https://docs.github.com/en/actions/reference/security/secure-use); GitHub changelog entries (2025-08-15 policy; 2026-03-10/2026-06-17 secret scanning; 2026-06-18/26 platform changes; 2025-03-18 artifact digest; 2025-06-03 release digests; 2026-03-26 Actions security roadmap); dependency-review-action README; wrangler-action README; osv-scanner README + https://google.github.io/osv-scanner/github-action/; setup-python README; setup-node v7.0.0 release notes; checkout v7.0.0 release notes; TypeScript 7 announcement + typescript-eslint status; ESLint 10 migration guide; Next.js 16 requirements + useTypeScriptCli docs; push protection/secret scanning docs; wrangler deploy source (`packages/wrangler/src/deploy/index.ts`); runner-images Ubuntu2404-Readme (ShellCheck 0.9.0).
- Local canonical sources read: `papyr-reference/.github/workflows/ci.yml`, `frontend/package.json`, `backend/requirements*.txt`, `backend/ruff.toml`, `backend/pytest.ini`, `backend/main.py`, `papyr-rebuild-decisions.md`, `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (Phases 0–1, FD-04, DEC-177). `papyr-reference/` unchanged.

---

## 11. Source index (primary links)

| Topic | URL |
|---|---|
| GitHub Actions security reference | https://docs.github.com/en/actions/reference/security/secure-use |
| Actions policy: block/SHA pin | https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/ |
| Safer pull_request_target defaults | https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout/ |
| Workflow trigger policies | https://github.blog/changelog/2026-06-18-control-who-and-what-triggers-github-actions-workflows/ |
| Read-only cache for untrusted triggers | https://github.blog/changelog/2026-06-26-read-only-actions-cache-for-untrusted-triggers/ |
| Actions 2026 security roadmap | https://github.blog/news-insights/product-news/whats-coming-to-our-github-actions-2026-security-roadmap/ |
| Artifact digest | https://github.blog/changelog/2025-03-18-github-actions-now-supports-a-digest-for-validating-your-artifacts-at-runtime/ |
| Release asset digests | https://github.blog/changelog/2025-06-03-releases-now-expose-digests-for-release-assets/ |
| Node.js releases | https://nodejs.org/dist/index.json ; https://endoflife.date/nodejs |
| TypeScript 7 | https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ ; https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli |
| ESLint 10 | https://eslint.org/blog/2026/02/eslint-v10.0.0-released/ ; https://eslint.org/docs/latest/use/migrate-to-10.0.0 |
| Next.js 16 requirements | https://nextjs.org/docs/app/guides/upgrading/version-16 |
| osv-scanner action | https://google.github.io/osv-scanner/github-action/ ; https://github.com/google/osv-scanner-action |
| dependency-review-action | https://github.com/actions/dependency-review-action |
| gitleaks | https://github.com/gitleaks/gitleaks ; action license: https://github.com/gitleaks/gitleaks-action |
| Trivy | https://github.com/aquasecurity/trivy/releases |
| ShellCheck | https://github.com/koalaman/shellcheck/releases |
| actionlint | https://github.com/rhysd/actionlint/releases |
| wrangler | https://github.com/cloudflare/wrangler-action ; dry-run source: https://github.com/cloudflare/workers-sdk/blob/c09dbd7e/packages/wrangler/src/deploy/index.ts |
| Dependabot | https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates |
| Secret scanning / push protection | https://docs.github.com/en/code-security/concepts/secret-security/push-protection ; https://github.blog/changelog/2026-06-17-secret-scanning-updates-june-2026/ |
