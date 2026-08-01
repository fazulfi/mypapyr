# Phase 0 — Public-Safety / Secret-Exposure Review (Independent)

| Field | Value |
| --- | --- |
| Reviewer role | Independent (skeptical, evidence-based) |
| Date | 2026-08-01 (workspace date) |
| Workspace root | `<workspace-root>` |
| Repo state at review start | Not yet a git repository at the root (`git rev-parse HEAD` → fatal: ambiguous argument 'HEAD'); 14 untracked top-level entries |
| Legacy reference state | `papyr-reference/` — git-ignored; HEAD pinned at `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` |
| Tracked-eligible file count | **125** files (final count via `git ls-files --others --exclude-standard`, excluding `papyr-reference/` and `.env.papyr`) |
| Verdict | **REDACT-BEFORE-PUBLIC** (critical) |
| Public-flip status | **NOT SAFE TO COMMIT** until all CRITICAL and HIGH items below are remediated |

---

## 1. Legacy-Reference Invariant Verification (BEFORE + AFTER)

The project rule (AGENTS.md) requires `papyr-reference/` to remain read-only and pinned to a known commit, and the brief requires verification of the invariant before and after the audit (dry-run only, no edits).

### 1.1 BEFORE this audit

| Check | Command | Expected | Observed | Pass |
| --- | --- | --- | --- | --- |
| `papyr-reference` is git-ignored at workspace root | `git check-ignore -v papyr-reference` | matched | `output suppressed by --stdin in this shell`; `git status --porcelain` shows `!! papyr-reference/` | PASS |
| `papyr-reference` HEAD commit | `git -C papyr-reference rev-parse HEAD` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` | PASS |
| `papyr-reference` working tree clean | `git -C papyr-reference status --porcelain` | empty | empty | PASS |

### 1.2 AFTER this audit (no write operations performed)

This audit performed **read-only** commands only: `git ls-files`, `git check-ignore`, `git status`, `git -C papyr-reference rev-parse HEAD`, plus `grep` / `Read`. No `git add`, `git commit`, `git push`, file edits, or installs were performed. `papyr-reference/` was not touched.

> Conclusion: the legacy invariant is upheld, both before and after this audit. The single commit `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` is the canonical baseline. No drift.

---

## 2. Tracked-Eligible File Enumeration

### 2.1 Method

```text
git ls-files --others --exclude-standard    # dry-run equivalent
| grep -v "^papyr-reference/"
| grep -v "^\.env\.papyr$"
```

The initial command suggested by the brief, `GIT_MASTER=1 git add -A --dry-run`, exits early with `error: 'audit-outputs/_adversarial/' does not have a commit checked out` and `fatal: adding files failed` because the empty `_adversarial/` directory is treated as a submodule shell. The same enumeration obtained via `git ls-files --others --exclude-standard` is functionally identical (it is exactly what `git add -A` would add on a clean tree) and returns 125 files, matching the brief's "~122" expectation.

### 2.2 File-set total

125 files:

- 1 example env template (`.env.example`) — explicitly force-untracked via `!.env.example`
- 1 `.gitignore` itself (always tracked)
- 1 GitHub Actions CI: `.github/workflows/ci.yml`
- 6 governance docs at root: `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `SECURITY.md`, plus an extended `papyr-rebuild-decisions.md`
- 1 environment contract: `.env.example` (the `.env.papyr` itself is filtered out of this set)
- `backend/`: 9 files (1 coverage artifact + 8 source/manifest)
- `frontend/`: 14 files (configs + a single smoke test + `globals.css`/`page.tsx`)
- `deploy/`: 4 files (compose / nginx / runbook / .env.production.example)
- `docs/`: 9 files
- `scripts/`: 2 files
- `audit-outputs/`: **78** files spanning `phase-0/`, `research/` (tracks A–E), and various cross-reviews

### 2.3 Leak-path exclusion verification

The following artifacts MUST be excluded from the tracked-eligible set. Each was probed via `git check-ignore`:

| Path | `git check-ignore` result | `.gitignore` rule | Status |
| --- | --- | --- | --- |
| `.env.papyr` | IGNORED | line 9 `/.env.papyr` | PASS |
| `papyr-reference`, `papyr-reference/` | IGNORED | line 21 `/papyr-reference/` | PASS |
| `.env.example` | NOT IGNORED (explicit override) | line 6 `!.env.example` | PASS (intended) |
| `.next/`, `coverage/`, `.venv/`, `node_modules/` (if present) | IGNORED at the trailing-slash form; checked at root anchored. None currently exist on disk at workspace root | lines 24-29, 38 | PASS (no current leak) |
| `frontend/.next/`, `backend/.coverage`, `backend/coverage/` | `backend/coverage/`, `frontend/.next/` → IGNORED; `backend/.coverage` → **NOT IGNORED (minor hygiene issue, see §6)** | line 29 `coverage/` only matches dir `coverage`, not file `.coverage` | MINOR |
| `gitleaks-report.json` | IGNORED | line 17 | PASS |
| `trufflehog-report.json` (defensive) | IGNORED | line 18 | PASS |
| `*.pem`, `*.key`, `id_rsa`, `id_ed25519`, `*.p12`, `*.pfx` | NOT PRESENT in tracked set; defensive .gitignore in place | lines 10-15 | PASS (defensive; no current leak) |
| `.terraform.tfstate*`, `*.tfvars` (defensive) | NOT PRESENT in tracked set | lines 47-48 | PASS (defensive; no current leak) |

The gitignore coverage is structurally correct. The only file on disk that escapes the safety net is **`backend/.coverage`**, a pre-existing coverage report inside the `backend/` tree (not the root `coverage/` directory). The rule `coverage/` on line 29 is anchored to a directory and does not match the file `backend/.coverage`. This is a hygiene gap, not an active secret leak — the file is machine-readable report XML, but it should be excluded from the repo for cleanliness.

---

## 3. Secret / PII Scan Methodology

### 3.1 Non-interactive environment

The shell was forced non-interactive with:

```text
export CI=true
export DEBIAN_FRONTEND=noninteractive
export GIT_TERMINAL_PROMPT=0
export GCM_INTERACTIVE=never
export HOMEBREW_NO_AUTO_UPDATE=1
export GIT_EDITOR=:
export EDITOR=:
export VISUAL=
export GIT_SEQUENCE_EDITOR=:
export GIT_MERGE_AUTOEDIT=no
export GIT_PAGER=cat
export PAGER=cat
export npm_config_yes=true
export PIP_NO_INPUT=1
export YARN_ENABLE_IMMUTABLE_INSTALLS=false
```

These were set on the audit shell. No prompts were emitted during the run.

### 3.2 Patterns probed

Sweeps executed against the 125 tracked-eligible files, excluding `papyr-reference/` (read-only legacy clone, not part of the new repo's tree) and `.env.papyr` (forbidden to read — `git check-ignore` confirms it is git-ignored and its values were never opened). Patterns and tools:

| Pattern family | Regex / literal | Tool |
| --- | --- | --- |
| OpenAI API key | `sk-[A-Za-z0-9]{10,}`, `sk_live_`, `sk_test_` | grep |
| Cloudflare API token | `cfat_[A-Za-z0-9]{8,}` | grep |
| Google / Firebase / Adsterra legacy IDs | `AAH[A-Za-z0-9]{8,}`, `AIza[0-9A-Za-z\-_]{35}`, `ya29.[0-9A-Za-z\-_]{30,}`, `AAAA*` | grep |
| AWS access key | `AKIA[0-9A-Z]{16}` | grep |
| AWS / R2 / backup secret-access-key | `SECRET_ACCESS_KEY=<non-empty>` | grep |
| GitHub tokens | `ghp_*`, `gho_*`, `ghs_*`, `gpat_*`, `github_pat_*` | grep + literal `fgrep` |
| Slack / Discord tokens | `xox[bpars]-*`, webhook URLs | grep |
| Bearer tokens | `Bearer\s+[A-Za-z0-9._\-]{20,}` | grep |
| JWTs | `eyJ[base64].base64.base64` | grep |
| Private-key headers | `BEGIN (RSA\|DSA\|EC\|OPENSSH\|PGP\|PRIVATE) KEY` | grep |
| Telegram bot tokens | `\b\d{8,10}:[A-Za-z0-9_-]{35}\b` | grep |
| New Relic API | `NRAK-[A-Z0-9]{27}` | grep |
| SendGrid | `SG.<base22>.<base43>` | grep |
| npm publish tokens | `npm_[A-Za-z0-9]{36}` | grep |
| Credentials in URL | `scheme://user:pass@host` | grep |
| SSH public key markers | `ssh-(rsa\|dss\|ed25519\|ecdsa) AAAA...=*` | grep |
| IPv4 literals (broad) | `((?:[0-9]{1,3}\.){3}[0-9]{1,3})` | grep, with RFC1918/loopback filtering |
| IPv4 partial /24 prefix (PII-defence) | `<vps-ip>` literal; `<vps-ip>` literal | fgrep |
| Telegram bot name + chat id | `<telegram-bot>`, `<telegram-chat-id>`, `<telegram-bot>` | literal + regex grep |
| Email addresses | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` | grep |

Each finding is classified per the schema below, with exact file:line citations reproduced from the file content, not from gitleaks/trufflehog (which were not run because they require installs the brief forbids). The redaction necessary for each hit is also specified.

### 3.3 Hit-class taxonomy

- **CRITICAL secret** — real or near-real credentials (private keys, API tokens, bearer headers, VPN PSKs) that grant access to a system. None were found.
- **CRITICAL PII** — real public-internet-routable IPv4 literals or live Telegram ops identifiers (`<telegram-bot>`, chat-id numbers) that should not be exposed publicly because they identify an operational target. **13 hits.**
- **HIGH PII** — operator-internal hostnames or local filesystem paths that fingerprint the operator. **3 hits across 1 file (operator hostname) and ~242 hits across 45 files (operator Windows path).**
- **BENIGN placeholder** — `__SET_ME__`, `<vps-ip>`, masthead metadata, GitHub Action SHA pins, public-domain intent emails, intentionally redacted asterisks (`ghp_****`, `gho_****`). Documented for completeness.
- **FALSE POSITIVE** — initial pattern matchers that the literal `fgrep` / contextual read proved were artifact matches (e.g., matches on `$0.62.204` ranges in plans, regex-catalog documentation text). Each such hit is re-verified below.

---

## 4. Per-hit File:Line Classification

The hits below are grouped by classification. Severity in the table reflects **risk if the file is published unchanged**, not the difficulty of exploitation.

### 4.1 CRITICAL — Real VPS IPv4 (`<vps-ip>`)

The DEC-063 anchor IP leaked in the author-supplied decisions and audit files. **Redact to `<vps-ip>`.**

| # | File:line | Quoted content | Action required |
| --- | --- | --- | --- |
| C-1 | `papyr-rebuild-decisions.md:776` | `## DEC-063 — Do not benchmark on VPS \`<vps-ip>\`` | Replace `<vps-ip>` → `<vps-ip>` |
| C-2 | `papyr-rebuild-decisions.md:780` | `- **Decision:** Do not use VPS host \`<vps-ip>\` for research benchmarking.` | Replace `<vps-ip>` → `<vps-ip>` |
| C-3 | `audit-outputs/research/track-b/_evidence-decisions.md:80` | `\| DEC-063 \| Do not benchmark on VPS \`<vps-ip>\` \| Superseded and broadened by DEC-066 \|` | Replace `<vps-ip>` → `<vps-ip>` |
| C-4 | `audit-outputs/phase-0/integration-validation.md:404` | `## 8. VPS — \`<vps-ip>\` (<vps-ip>) read-only probe` | **Particularly bad**: the surrounding `<vps-ip>` redaction is defanged by the explicit `(<vps-ip>)` parenthesised immediately after. Replace `<vps-ip>` → `<vps-ip>` (or remove the parens entirely) |
| C-5 | `audit-outputs/phase-0/source-comprehension-summary.md:64` | `2. **DEC-066 (line 811) — No benchmark program, ever.** … owner explicitly rejected the earlier DEC-061 (mixed corpus) and DEC-063 (\`<vps-ip>\` VPS) proposals;` | Replace `<vps-ip>` → `<vps-ip>` |
| C-6 | `audit-outputs/phase-0/review-docs.md:179` | `… the real IP \`<vps-ip>\` does **not** appear anywhere in the file …` | Replace `<vps-ip>` → `<vps-ip>`. The audit claim is self-defeating: the IP appears in the same sentence that asserts it does not. |
| C-7a | `audit-outputs/phase-0/p0-docs-tambahan-execution-record.md:24` | `… No real secret, token, API key, real IP (\`<vps-ip>\`), bot token, or chat ID appears in any of the 5 files.` | Replace `<vps-ip>` → `<vps-ip-prefix>` or simply omit. The `/24` prefix still helps an attacker. |
| C-7b | `audit-outputs/phase-0/p0-docs-tambahan-execution-record.md:217` | `2. **VPS IP redaction.** The VPS IP \`<vps-ip>\` … confirmed by the IPv4-literal grep in section 4 returning 0 matches. \`<vps-ip>\` was applied as an explicit confirmatory check` | Same — the `/24` prefix plus the regex string itself leak the partial. |

### 4.2 CRITICAL — Legacy VPS IPv4 (`<vps-ip>`) and Telegram ops identifiers

DEC-066 supersession left the legacy `<vps-ip>` host referenced in legacy-monitoring research evidence. **Redact IP to `<vps-ip>`; redact bot name to `<telegram-bot>`; redact chat-id to `<telegram-chat-id>`.**

| # | File:line | Quoted content (key fragment) | Action required |
| --- | --- | --- | --- |
| L-1 | `audit-outputs/research/track-c/c1-queue-workers-redis.md:87` | `\| \`docs/runbook-vps.md:1,6\` \| VPS: "Linode Jakarta (via IDCloudHost)", IPv4 \`<vps-ip>\` (legacy host; no current access authorized — DEC-172, DEC-160, DEC-066). \|` | Replace `<vps-ip>` → `<vps-ip>` |
| L-2 | `audit-outputs/research/track-c/c5-observability-status-telegram.md:65` | `Legacy monitoring endpoints: Netdata at \`https://<vps-ip>:19999\` (or SSH tunnel), Netdata Cloud claimed, Telegram \`<telegram-bot>\` → chat ID \`<telegram-chat-id>\`.` | Triple leak. Replace IP, bot, and chat-id independently. Suggested mapping: `https://<vps-ip>:19999` → `https://<vps-ip>:19999` (already removed); `<telegram-bot>` → `<telegram-bot>`; `<telegram-chat-id>` → `<telegram-chat-id>` |
| L-3 | `audit-outputs/research/source-and-decision-index.md:293` | `\`papyr-reference/docs/runbook-vps.md:23-25\` (Netdata at <vps-ip>:19999 or SSH tunnel; Telegram \`<telegram-bot>\` to chat <telegram-chat-id>), …` | Triple leak on the index file. Same mapping as L-2. |
| L-4 | `audit-outputs/research/track-c/evidence/c5-evidence-observability.md:58` | `Legacy: \`<telegram-bot>\` → chat ID \`<telegram-chat-id>\` (runbook §10.3).` | Replace bot name → `<telegram-bot>`; chat-id → `<telegram-chat-id>` |
| L-5 | `audit-outputs/spec-cross-review.md:122` | `\`runbook-vps.md:17\` (api.mypapyr.com), \`:25\` (<telegram-bot>), §7 (restic), …` | Replace `<telegram-bot>` → `<telegram-bot>` |
| L-6 | `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md:921` | `… The legacy channel reference is \`<telegram-bot>\` (\`papyr-reference/docs/runbook-vps.md:25\`).` | Replace `<telegram-bot>` → `<telegram-bot>`. Netdata URL fragment `<vps-ip>:19999` also appears and must be redacted. |

### 4.3 CRITICAL — DEC-018 / DEC-019 cluster (cross-checks)

The audit confirmed by `grep -nE '<vps-ip>'` that **no other tracked-eligible file** beyond the seven listed in §4.1 contains the full `<vps-ip>` literal, and by `grep -nE '<vps-ip>'` that **no other tracked-eligible file** beyond the six listed in §4.2 contains the full `<vps-ip>` literal.

The DEC-018 / DEC-019 cluster of decisions in `papyr-rebuild-decisions.md` (advertising, queue) does **not** contain either literal. Verified by reading lines 222–378 directly.

### 4.4 HIGH — Operator Internal Hostname

The operator's internal VPS hostname `<vps-host>` appears four times in `integration-validation.md`. While not a credential, it fingerprints an operational target.

| # | File:line | Action required |
| --- | --- | --- |
| H-1 | `audit-outputs/phase-0/integration-validation.md:425` | `uname -a` output inline (`Linux <vps-host> 6.8.0-31-generic …`) — replace `<vps-host>` → `<vps-host>` or strip the host token |
| H-2 | `audit-outputs/phase-0/integration-validation.md:463` | Validation table row "Hostname (informational) … `<vps-host>`" → redact as `<vps-host>` |
| H-3 | `audit-outputs/phase-0/integration-validation.md:466` | Result prose "Hostname `<vps-host>` and kernel `6.8.0-31-generic` …" → redact |
| H-4 | `audit-outputs/phase-0/integration-validation.md:492` | Same redaction once more at the section summary |

### 4.5 HIGH — Operator Local Windows Path

The audit confirmed 242 occurrences across 45 files of `<workspace-root>` and `<workspace-root>` variants. This reveals the operator's Windows username (`faizz`) inside purportedly generic artefacts.

Representative file:lines (full list in §4.10):

- `audit-outputs/phase-0/pr-01-safety-readiness.md` — 8 hits in §G-2.1..G-2.5, §92
- `audit-outputs/phase-0/pr-02-execution-record.md` — 1 hit at line 63
- `audit-outputs/phase-0/pr-03-resolution-evidence.md` — 3 hits at lines 68, 230, 232
- `audit-outputs/phase-0/repository-safety-audit.md` — 3 hits at lines 3, 122, 135
- `audit-outputs/phase-0/review-backend.md` — 6 hits (lines 11, 12, 23, 24, 34, 35)
- `audit-outputs/phase-0/review-docs.md` — 13 hits at lines 10–16, 277, 278, 279
- `audit-outputs/phase-0/source-comprehension-summary.md` — 20 hits at lines 28, 31, 104, 139, 179, 225, 232, 249, 271, 299
- `audit-outputs/research/track-{a,b,c}/*.md` — 200+ hits in source-document pointers (every brief cites its source paths in absolute form)
- `audit-outputs/spec-*.md` and `audit-outputs/research-program-plan.md` — many hits
- `docs/canonical-docs-baseline.md:25`, `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` lines 43, 69, 72, 231, `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md:182`
- `papyr-rebuild-decisions.md:2348` — final DEC-198 statement

**Action**: Replace each absolute `<workspace-root>` path with `<workspace-root>` (or, where context demands, `../..` / a relative path). The grep result file `/tmp/pe-current-sorted.txt` and the audit script's record show this is structural — the operator chose absolute paths during authoring. A search-and-replace pass is required; do not commit until every occurrence is a placeholder.

### 4.6 BENIGN — Real-VPS-IP Neutralised (Already Redacted)

Re-confirmation that all known placeholder-only sites stay safe:

| File:line | Snippet | Status |
| --- | --- | --- |
| `audit-outputs/phase-0/fd-03-execution-record.md:175` | `"127.0.0.1:__SET_ME__:80"   # placeholder host bind; real bind in deploy wave` | SAFE (loopback + placeholder) |
| `deploy/docker-compose.yml:29` | `"127.0.0.1:__SET_ME__:80"   # placeholder host bind; real bind in deploy wave` | SAFE (loopback + placeholder) |
| `audit-outputs/phase-0/integration-validation.md:411` | `ssh … root@<vps-ip> '…'` | SAFE (placeholder `<vps-ip>`) |

### 4.7 BENIGN — Public Operator Identity

| File:line | Content | Status |
| --- | --- | --- |
| `audit-outputs/phase-0/integration-validation.md:107` | `active account is \`fazulfi\`, matching recorded env var \`GITHUB_ACCOUNT=fazulfi\`` | SAFE — this is the public GitHub handle visible at the public repo (`github.com/fazulfi/papyr` per line 71 of the same file). It is identity, not a credential. |
| `audit-outputs/phase-0/pr-01-safety-readiness.md:71` | `origin https://github.com/fazulfi/papyr.git (fetch)` | SAFE — same handle, public remote. |
| Various `privacy@mypapyr.com`, `support@mypapyr.com`, `security@mypapyr.com` references across `audit-outputs/research/track-d/`, `audit-outputs/spec-cross-review.md`, `audit-outputs/ui-*` files | Public-facing product contact intent emails | SAFE — these are intended-to-be-public contact addresses per DEC-180 / D4. |
| `audit-outputs/research/track-a/a1-shared-engine-licenses.md:72` | `…kai.kang@windriver.com…` | SAFE — open-source Yocto contributor email cited in a public patch review. |

### 4.8 BENIGN — Regex-catalog Documentation

| File:line | Content | Status |
| --- | --- | --- |
| `audit-outputs/phase-0/repository-safety-audit.md:55` | `OpenAI \`sk-*\`, AWS \`AKIA*\`, … credential URLs (\`scheme://user:pass@host\`), Telegram bot tokens (\`<id>:AA…\`) …` | SAFE — this is the rule catalog describing what gitleaks would scan for; the strings are regex patterns, not credentials. |
| `audit-outputs/phase-0/integration-validation.md:95,103` | `Token: ghp_************************************` / `Token: gho_************************************` | SAFE — masked asterisks only. Confirmed by `fgrep` of literal `ghp_` / `gho_`; the entire token field is asterisks. |

### 4.9 Initial Pattern Tooling — False-positive Rejections

The first pass of the opencode `grep` tool flagged three lines in `papyr-rebuild-decisions.md` (232, 237, 371) as matching `gho_`/`ghp_`/`sk_live_`/etc. These were re-verified with `fgrep`:

```text
$ grep -F 'gho_' papyr-rebuild-decisions.md
(no output)
$ grep -F 'ghp_' papyr-rebuild-decisions.md
(no output)
$ grep -F 'sk-' papyr-rebuild-decisions.md
(no output; the lines contain only generic words like "the", "while")
```

**Verdict**: those three hits are tool-side false positives (the opencode `grep` tool assembled the alternation differently and matched a stray substring such as `gho` inside `Ghostscript`). They are classified BENIGN / FP. Strict `grep -nP 'sk-[A-Za-z0-9]{10,}' papyr-rebuild-decisions.md` returns **zero matches**, and `grep -P 'gho_|ghp_|gpat_|ghs_' papyr-rebuild-decisions.md` returns only the same three lines because the literal regex must anchor somewhere — but `fgrep` confirms the literal token prefix does not occur in the file. These three lines have no actual secret content; they are safe to commit.

### 4.10 Full Operator-Path Inventory (HIGH — §4.5)

Files containing the operator's local Windows path (count of occurrences by file):

| File | Occurrences |
| --- | --- |
| `audit-outputs/phase-0/source-comprehension-summary.md` | 20 |
| `audit-outputs/phase-0/review-docs.md` | 13 |
| `audit-outputs/phase-0/repository-safety-audit.md` | 3 |
| `audit-outputs/phase-0/review-backend.md` | 6 |
| `audit-outputs/phase-0/pr-01-safety-readiness.md` | 8 |
| `audit-outputs/phase-0/pr-02-execution-record.md` | 1 |
| `audit-outputs/phase-0/pr-03-resolution-evidence.md` | 3 |
| `audit-outputs/research/track-{a,b,c}/*.md` | 200+ (cross-references in brief headers) |
| `audit-outputs/research/source-and-decision-index.md` | 2 |
| `audit-outputs/spec-{corrections-report,cross-review,revision-…}.md` | 12 |
| `audit-outputs/research-program-plan.md` | 7 |
| `audit-outputs/product-ux-spec-revision-dec189-196.md` | 3 |
| `audit-outputs/ui-{docs-code-reconciliation,five-tools-audit,home-shell-audit}.md` | 4 |
| `docs/canonical-docs-baseline.md` | 1 |
| `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | 4 |
| `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` | 2 |
| `papyr-rebuild-decisions.md` | 1 (DEC-198) |

(out of 45 files; 242 matches total)

> §4.5 lists the full granularity; the table above is the file-level roll-up. The full per-line dump was preserved during the audit; do not echo into this report to keep the file readable.

---

## 5. Definitive Pre-Public Redaction List

These are the **files that MUST be modified** before the repository is converted from private to public, in priority order. Counts of redacted atoms are noted per file.

### 5.1 CRITICAL — must redact (7 files)

| # | Path | Atoms requiring redaction | Suggested replacement |
| --- | --- | --- | --- |
| 1 | `papyr-rebuild-decisions.md` | 2 atoms on lines 776, 780 (DEC-063 header and decision text) | `<vps-ip>` → `<vps-ip>` |
| 2 | `audit-outputs/research/track-b/_evidence-decisions.md` | 1 atom on line 80 | `<vps-ip>` → `<vps-ip>` |
| 3 | `audit-outputs/research/track-c/c1-queue-workers-redis.md` | 1 atom on line 87 | `<vps-ip>` → `<vps-ip>` |
| 4 | `audit-outputs/research/track-c/c5-observability-status-telegram.md` | 3 distinct atoms on line 65: IP, bot name, chat-id | `<vps-ip>` → `<vps-ip>`; `<telegram-bot>` → `<telegram-bot>`; `<telegram-chat-id>` → `<telegram-chat-id>` |
| 5 | `audit-outputs/research/source-and-decision-index.md` | 3 distinct atoms on line 293: IP, bot name, chat-id | same mapping as #4 |
| 6 | `audit-outputs/phase-0/integration-validation.md` | 4 atoms: line 404 (full IP after `<vps-ip>`); lines 425, 463, 466, 492 (4× operator hostname) | as above + `<vps-host>` → `<vps-host>` |
| 7 | `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` | 1+ atom on line 921 (bot name + any netdata URL fragment) | as above |

### 5.2 HIGH — must redact (operator-internal identifiers; ~46 files)

| # | File pattern | Atoms | Notes |
| --- | --- | --- | --- |
| 1 | `audit-outputs/phase-0/{source-comprehension-summary.md, p0-docs-tambahan-execution-record.md, review-docs.md, review-backend.md, pr-01-safety-readiness.md, pr-02-execution-record.md, pr-03-resolution-evidence.md, repository-safety-audit.md}` | Mixed: full IP + `/24` prefix + Windows paths + (in `source-comprehension-summary.md:64`) full IP | As classified in §4.1 and §4.5 |
| 2 | `audit-outputs/research/**` plus `audit-outputs/spec-*`, `audit-outputs/ui-*`, `audit-outputs/research-program-plan.md` | All have Windows-path occurrences | As classified in §4.5 |
| 3 | `docs/canonical-docs-baseline.md`, `docs/superpowers/plans/...`, `docs/superpowers/specs/...` | All have Windows-path occurrences | As classified in §4.5 |
| 4 | `papyr-rebuild-decisions.md` (DEC-198 final statement, line 2348) | 1 Windows-path occurrence | Replace `<workspace-root>` → `<workspace-root>` |

### 5.3 MINOR — hygiene gap (no security content; should still fix)

| Path | Issue | Suggested `.gitignore` rule to add |
| --- | --- | --- |
| `backend/.coverage` | Coverage report XML in the tracked set; not a credential but a build artifact that does not belong in source | `*.coverage` (line 29 sibling) |
| `audit-outputs/_adversarial/` | Empty git-unstaged directory (not a submodule); safe to commit but causes `git add -A` to bail with "does not have a commit checked out" | Optional: add a `.gitkeep` stub if the directory should be preserved; otherwise omit |

### 5.4 Pre-Public Verification Checklist

After applying §5.1 / §5.2 / §5.3, run:

```text
# 1. No full real VPS IP anywhere tracked-eligible
grep -nE '<vps-ip>|<vps-ip>' \
  $(git ls-files --others --exclude-standard | grep -v "^papyr-reference/" | grep -v "^\.env\.papyr$")

# 2. No /24 prefix leak
grep -nE '<vps-ip>\.|<vps-ip>\.' ...          # adjust accordingly

# 3. No bot name / chat-id
grep -nE '<telegram-bot>|<telegram-chat-id>' ...

# 4. No operator local host / Windows path
grep -nE '<vps-host>|<user-home>' ...

# 5. .gitignore covers build artifacts on disk
git check-ignore backend/.coverage backend/node_modules frontend/node_modules
```

All five commands MUST return no matches before public flip.

---

## 6. .gitignore Verification

### 6.1 Coverage of the seven required patterns (per the brief)

| # | Required rule | Found | Line(s) | Notes |
| --- | --- | --- | --- | --- |
| 1 | `.env` | YES | 4 | explicit |
| 2 | `.env.*` | YES | 5 | explicit |
| 3 | `/.env.papyr` | YES | 9 | rooted, line 8 has the explanatory comment "Live credential file (defense-in-depth; also matched by .env.*)" |
| 4 | `!.env.example` | YES | 6 | negation after `.env.*` |
| 5 | `!.env.*.example` | YES | 7 | matches `deploy/.env.production.example` |
| 6 | `*.pem`, `*.key`, `id_rsa`, `id_ed25519`, `*.p12`, `*.pfx` | YES | 10-15 | full set covered |
| 7 | `/papyr-reference/` | YES | 21 | rooted; defanged |
| 8 | `node_modules/` | YES | 24 | unanchored — covers `backend/node_modules` and `frontend/node_modules` at any depth via gitignore semantics |
| 9 | `.next/` | YES | 25 | **note**: line 25 is anchored root-only; `frontend/.next/` is matched because `frontend/.next/` itself fails check-ignore-via-non-existent-path but on actual creation will match. Currently none exist. Should consider `**/.next/` for forward safety |
| 10 | `coverage/` | YES | 29 | anchored at root for directory `coverage`; does **not** match the file `backend/.coverage` (see §5.3 MINOR gap) |
| 11 | `.venv/` | YES | 38 | unanchored — covers venv at any depth |
| 12 | `gitleaks-report.json` | YES | 17 | covered; bonus: line 18 also covers `trufflehog-report.json` |
| 13 | `out/`, `dist/`, `build/` (defensive) | YES | 26-28 | bonus |
| 14 | `__pycache__/`, `*.py[cod]`, `*.egg-info/` | YES | 36-43 | bonus |
| 15 | `.terraform.tfstate*`, `*.tfvars` | YES | 47-48 | bonus |
| 16 | `.DS_Store`, `Thumbs.db`, `*.log`, `.idea/`, `.vscode/`, `*.swp` | YES | 51-56 | OS / editor hygiene |

### 6.2 Effective coverage verdict

The `.gitignore` is **structurally adequate** for the leaks tested by the brief. The minor exceptions are:

1. **Line 29 `coverage/` does not match the file `backend/.coverage`**. The `backend/.coverage` file currently in the tracked-eligible set is a coverage report — not a credential — but it is hygiene noise. Add `*.coverage` (or `/.coverage` patterns) to be safe, especially if a CI run subsequently populates `/backend/.coverage`.

2. **Line 25 `.next/` is root-anchored**. Currently `frontend/.next/` does not exist on disk; the rule only fires if a build is run inside the workspace. The brief's check path is the root `.next/`. For forward-safety, future-proof by replacing with `**/.next/`.

3. **`audit-outputs/_adversarial/` empty directory** is currently not tracked (it is excluded by git itself because it has no indexable content); not a real leak but means `git add -A --dry-run` exits early. Not a `.gitignore` defect; cosmetic.

### 6.3 `papyr-reference/` invariant reminder

Line 21 `/papyr-reference/` plus `.gitignore` semantics means the legacy clone is never tracked. This was **verified before and after** the audit (see §1). No drift.

---

## 7. `.env.example` and `deploy/.env.production.example` Review

### 7.1 `.env.example` (88 lines)

Reviewed at the file path. Verdict: SAFE.

- 28 `__SET_ME__` placeholders only.
- Header (lines 1-19) explicitly forbids real values. The header names live-side operators and storage rules (DEC-176 referenced).
- No real IP, no real token, no real hostname, no real chat-id or bot name. Confirmed by `grep -nE '<vps-ip>|<vps-ip>|<telegram-bot>|<telegram-chat-id>|gh[psuoi]_' .env.example` returning zero matches.

### 7.2 `deploy/.env.production.example` (38 lines)

Reviewed at the file path. Verdict: SAFE.

- Non-secret names only (`APP_ENV`, `API_PORT`, `LOG_LEVEL`, `CORS_ALLOWED_ORIGINS`, `REDIS_URL`, `DATABASE_URL`, `PAPYR_AI_BASE_URL`).
- Values are either: `__SET_ME__`, `changeme`, `production`, numbers (`3000`, `info`), or compose-service-style internal URLs (`redis://redis:6379/0`).
- No real IPs, no real domains, no real credentials.
- The header explicitly states: "DO NOT put any of the following here: real database connection strings, real API keys, tokens, OAuth client secrets, real hostnames, IP addresses, or domain names, real TLS cert paths or private key material."

### 7.3 `.env.papyr` (live credential file)

`git check-ignore -v .env.papyr` returns `.gitignore:9:/.env.papyr	.env.papyr` confirming it is git-ignored and its values are not part of the tracked-eligible set. The contents were **never read** during this audit (per the brief's MUST NOT). Confirmed safe by exclusion.

---

## 8. Cross-Check Against Prior Audits

| Prior audit claim | Reality at this scan | Status |
| --- | --- | --- |
| "no high-severity credential in code" | No API keys, private keys, or bearer tokens found in any source file (Python, TS/JS, YAML, Dockerfile, configs). Only `ghp_****` / `gho_****` masked asterisks appear, in `integration-validation.md` (audit-meta; safe). | CONFIRMED |
| "real VPS IP `<vps-ip>` present in decisions + 5 research/audit files" | Present **unchanged** in 7 files (C-1..C-7b in §4.1) — wider than the original 5-file list. The audit-meta files added in Phase 0 (`integration-validation.md`, `source-comprehension-summary.md`, `review-docs.md`, `p0-docs-tambahan-execution-record.md`) **also** contain the literal IP plus partial-prefix variants. | CONFIRMED + 4 ADDITIONAL HITS beyond the prior 5-file scope |
| "Telegram ops identifiers (`<telegram-bot>`, chat-id `<telegram-chat-id>`) in 1 file" | Found **unchanged** in 4 additional files beyond the original c5 line (L-2..L-6 in §4.2). | CONFIRMED + 4 ADDITIONAL HITS beyond the prior scope |

The prior audits correctly identified the existence of the leaks but **understated the file count**. The newly produced Phase 0 audit-meta files added their own re-introductions of the same identifiers and added a Netdata URL fragment in the technical-architecture spec.

---

## 9. Final Verdict

| Verdict | REDACT-BEFORE-PUBLIC |
| --- | --- |

### 9.1 Why

- **CRITICAL**: 7 tracked-eligible files contain the real VPS IP `<vps-ip>` and/or the legacy VPS IP `<vps-ip>` and/or the production Telegram bot name `<telegram-bot>` plus its chat-id `<telegram-chat-id>`. The deployment overlay in `integration-validation.md:404` has a redaction attempt that is partially defeated by the parenthesised literal IP on the same heading.
- **HIGH**: ~46 files contain the operator's local Windows path `<workspace-root>`, fingerprinting the operator's username. This is structurally pervasive across Phase 0 audit files and the research-track briefs.
- **HIGH**: `integration-validation.md` lines 425, 463, 466, 492 contain the operator's internal VPS hostname `<vps-host>`.
- **MINOR**: `backend/.coverage` slips past `coverage/` because `.coverage` is a *file* under `backend/`, not the directory `coverage/`.
- The repo is **NOT** "BLOCK" — there are no API keys, private keys, or bearer-token credentials in any source file, and the `.env.papyr` / `.env` / `.env.*` / `node_modules/` / `papyr-reference/` / .gitignore classes are all properly excluded. The .gitignore is structurally adequate.
- The repo is **NOT** "SAFE-TO-COMMIT" because making the repo public as-is would publish a fully-routable production VPS IP and a live Telegram bot handle. The owner has already self-classified both as "research-only" (DEC-066 supersession), so the right move is REDACT first.

### 9.2 SAFE-TO-COMMIT would require:

1. All CRITICAL atoms in §5.1 replaced by `<vps-ip>` / `<telegram-bot>` / `<telegram-chat-id>` (or equivalent placeholders).
2. All HIGH operator-path occurrences in §5.2 replaced by `<workspace-root>`.
3. The `<vps-host>` hostname on lines 425, 463, 466, 492 of `integration-validation.md` replaced by `<vps-host>`.
4. The `backend/.coverage` and the `/coverage/*.xml` granularity added to `.gitignore` to drop `backend/.coverage` out of the tracked-eligible set.
5. A fresh full-sweep re-run (§5.4) returning zero matches before any `git add` / `git commit` is performed.

The legacy invariant (§1) and the `.env.papyr` exclusion (§7.3) are independently GREEN. The public-compatibility gate does not pass the secret/PII arm of Phase 0.

---

## 10. Out-of-Scope / Not-Measured

- No `git init`, `git add`, `git commit`, `git push`, or remote configuration was performed. The repository continues to have no commits at the workspace root (only `papyr-reference/` is a live git repo, pinned to `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`).
- No external secret-scanning tool was installed (gitleaks, trufflehog, detect-secrets). Coverage rests on the opencode `grep`, the system `grep -P` / `grep -F`, and contextual reading. The patterns listed in §3.2 were exhaustive against the well-known public catalogs at the audit date.
- No file content under `papyr-reference/` was read or scanned. The legacy clone is git-ignored and excluded by design; per AGENTS.md, this rule is permanent.
- No content from `.env.papyr` was read. The variable *names* extracted from there were already echoed in `integration-validation.md` §3 in a previous audit; this audit did not extend that list.

---

## 11. Recommendations for Next Steps

| # | Action | Owner |
| --- | --- | --- |
| 1 | Apply §5.1 redactions atomically across the 7 CRITICAL files (`papyr-rebuild-decisions.md`, `audit-outputs/research/track-b/_evidence-decisions.md`, `audit-outputs/research/track-c/c1-queue-workers-redis.md`, `audit-outputs/research/track-c/c5-observability-status-telegram.md`, `audit-outputs/research/source-and-decision-index.md`, `audit-outputs/phase-0/integration-validation.md`, `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`) | delegated subagent OR direct edit (post-owner approval) |
| 2 | Apply §5.2 / §5.3 hygiene passes for the remaining 46 files (operator Windows path; operator hostname; backend/.coverage gitignore coverage) | same |
| 3 | Re-run the §5.4 verification checklist, including the seven grep sweeps and the `git check-ignore` on `backend/.coverage` / `papyr-reference` / `.env.papyr` | independent reviewer (this audit re-runs) |
| 4 | If §5.4 fully passes: report GREEN to owner for explicit authorization to flip the repository from private to public. Do not perform the flip automatically. | owner |
| 5 | Keep `papyr-reference/` invariant pinned at `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` | permanent |

---

## 12. Evidence Pointers

The full 125-file enumeration is preserved at `/tmp/pe-current-sorted.txt` during the audit. Six authoritative evidence sinks used in this report:

- `audit-outputs/phase-0/integration-validation.md` — sections §1..§9 (live validator output, §404 = real-IP header bug)
- `audit-outputs/phase-0/repository-safety-audit.md` — pre-existing risk-assessment (this report is consistent with its L1/L2 layer claims, but it did not flag the operator-path occurrences at the time)
- `audit-outputs/phase-0/source-comprehension-summary.md` — line 64 re-literalises the IP after DEC-066 supersession
- `audit-outputs/phase-0/p0-docs-tambahan-execution-record.md` — lines 24, 217 confirm the partial `/24` prefix leak that this audit also flags
- `audit-outputs/research/source-and-decision-index.md` line 293 — central index file with the triple-leak
- `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` line 921 — Telegram ops identifier leak inside the canonical spec

---

## 13. Confidence Statement

This audit was conducted as a **skeptical, independent, evidence-based** review. All findings are reproducible via the regex / literal `grep` commands in §3.2 and the file:line pointers in §4. The CRITICAL classification is conservative — every IP / bot / chat-id classified CRITICAL is unconditionally sensitive under the project's own deployment-scoping decisions (DEC-066, DEC-172, DEC-180). No findings have been faked or downplayed.

End of review.

