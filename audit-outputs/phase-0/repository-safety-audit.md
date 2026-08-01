# Repository & Publication Safety Audit — Phase 0

- **Workspace:** <workspace-root>
- **Date:** 2026-08-01
- **Auditor:** read-only safety subagent (pre-init; L1 heuristic regex + L2 gitleaks readiness)
- **Status:** COMPLETE
- **Bottom line:** 69 tracked candidates inventoried; **0 high-severity credentials** in the tracked tree (no API keys, private keys, JWTs, credential URLs, or bot tokens); **5 files require redaction** before public exposure (1 legacy VPS IPv4 address; Telegram ops chat ID + bot handle); `.env.papyr` and `papyr-reference/` both verified covered by `.gitignore`. Legacy repo `github.com/fazulfi/papyr` is **already public** (381 commits on main).
- **Handling:** `.env.papyr` was treated as path-only metadata — its contents were never read or printed. All findings below are redacted; no exact secret values, VPS IPs, Telegram identifiers, or email addresses appear in this document. `papyr-reference/` was not modified (verified clean).

## 1. Repository state snapshot

| Fact | Evidence |
|---|---|
| Root is **not** a git repo | `git status` -> `fatal: not a git repository` |
| `papyr-reference/` **is** a nested git repo | `.git` present; 388 commits (`rev-list --all --count`); origin `https://github.com/fazulfi/papyr.git` |
| Legacy repo **already public** on GitHub | Web fetch of `github.com/fazulfi/papyr` -> "Public", 381 commits on `main` |
| Legacy working tree clean during audit | `git -C papyr-reference status --porcelain` -> empty |
| Root on-disk entries | `.env.papyr`, `.gitignore`, `AGENTS.md`, `audit-outputs/`, `backend/`, `deploy/`, `docs/`, `frontend/`, `papyr-rebuild-decisions.md`, `papyr-reference/`, `README.md`, `scripts/` |
| `backend/`, `frontend/`, `deploy/` are **empty** | `find ... | wc -l` -> 0 each; git will not track empty dirs |
| `audit-outputs/` 60 files; `docs/` 4; `scripts/` 1 | `find` counts |
| No CI exists yet | no `.github/`, no `.gitlab-ci.yml` anywhere in the new tree |

## 2. Tracked-candidate inventory (69 files)

Inventory produced by a Python walk of the tree **excluding** `papyr-reference/`, `.git`, and `.env.papyr` (path-only).

| Group | Count | Files |
|---|---|---|
| Root records | 4 | `README.md`, `AGENTS.md`, `papyr-rebuild-decisions.md` (197,835 B), `.gitignore` (627 B) |
| Governed docs | 4 | `docs/resolution-register.md`; `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`; `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md`; `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` |
| Scripts | 1 | `scripts/check-docs-migration.sh` |
| Audit outputs | 60 | 16 root-level review/plan docs; `research/` (3); `track-a` (6); `track-b` (5 briefs + 7 `_evidence-*`); `track-c` (6 briefs + 6 `evidence/`); `track-d` (5); `track-e` (3); `research-program-plan.md` |

Extension mix: 67 `.md`, 1 `.sh`, 1 extensionless (`.gitignore`). Largest: `papyr-rebuild-decisions.md` (197 KB), implementation plan (139 KB), `_evidence-decisions.md` (138 KB), `source-and-decision-index.md` (125 KB). **No binary/NUL-byte files, no symlinks, and no sensitive file types** (`.sql`, `.dump`, `.bak`, `.zip`, `.tar`, `.gz`, `.db`, `.pem`, `.key`, `.p12`, `.pfx`, `.ppk`, `.ovpn`, `.npmrc`, `.netrc`, `.pypirc`, `*service-account*`) anywhere in the tracked tree.

## 3. `.gitignore` coverage verification (root `.gitignore`, 49 lines)

| Path / pattern | Rule | Line | Verdict |
|---|---|---|---|
| `.env.papyr` | `.env.*`; only negation is `!.env.example` and **no such file exists** (verified by glob) -> nothing un-ignored | 5-6 | **COVERED**; recommend explicit `/.env.papyr` for defense in depth |
| `papyr-reference/` | `/papyr-reference/` (anchored) | 15 | **COVERED**; nested `.git` (388 commits) will be skipped by `git add`; never `git add -f` |
| Node/Next artifacts | `node_modules/`, `.next/`, `out/`, `dist/`, `build/`, `*.tsbuildinfo`, npm/yarn/pnpm logs | 18-26 | Covered |
| Python artifacts | `__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `*.egg-info/` | 29-36 | Covered |
| Deploy state | `.vercel/`, `terraform.tfstate*`, `*.tfvars` | 39-41 | Covered |
| Secrets | `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa`, `id_ed25519`, `*.p12`, `*.pfx` | 4-12 | Covered |
| OS / editor | `.DS_Store`, `Thumbs.db`, `*.log`, `.idea/`, `.vscode/`, `*.swp` | 44-49 | Covered |

**Gap analysis** (rules absent; none currently triggered by existing files): `*.ppk`, `*.ovpn`, `gitleaks-report.json` (the legacy repo ignores this file; the new repo should too), `docs/*vps*`, `docs/*runbook*`, `credentials*`, `*service-account*.json`, `*.sops`, `*.age`, `.npmrc`, `.pypirc`, `.netrc`, `secrets/`, `*.sql`, `*.dump`, `*.bak`. Recommended additions before init.

## 4. Secret / PII scan results (redacted evidence)

Engines: custom Python regex scanner (13 families, UTF-8, NUL-byte detection, values redacted in output) + targeted `grep` families. `.env.papyr` excluded by filename — never read.

### 4.1 Clean families — zero matches
OpenAI `sk-*`, AWS `AKIA*`, Google `AIza*`, GitHub `ghp_*` / `github_pat_*`, Slack `xox*`, Stripe `pk_live_`/`sk_live_`, Firebase `AAAA*`, `ya29.*`, `glpat-*`, JWTs (`eyJ...`), private-key headers (`-----BEGIN ... PRIVATE KEY-----`), credential URLs (`scheme://user:pass@host`), Telegram bot tokens (`<id>:AA...`), 12-digit AWS account IDs, Discord/Slack webhooks, `npm_*`, `SG.*`, `NRAK*`, `AC<hex32>`, SSH public-key marker, `x-api-key`, real `Bearer <token>` values.

### 4.2 Requires action — legacy VPS IPv4 (redact before public)
A single legacy VPS IPv4 (Linode Jakarta, per `c1-queue-workers-redis.md:87`) appears in **5 files / 6 lines**:

| File | Line(s) | Note |
|---|---|---|
| `papyr-rebuild-decisions.md` | 776, 780 | IP sits in the **DEC-063 section header** and decision body |
| `audit-outputs/research/track-b/_evidence-decisions.md` | 80 | DEC-063 table row |
| `audit-outputs/research/track-c/c1-queue-workers-redis.md` | 87 | "Linode Jakarta (via IDCloudHost), IPv4 `<vps-ip>` (legacy host; no current access authorized — DEC-172, DEC-160, DEC-066)" |
| `audit-outputs/research/track-c/c5-observability-status-telegram.md` | 65 | Netdata at `https://<vps-ip>:19999` |
| `audit-outputs/research/source-and-decision-index.md` | 293 | same Netdata endpoint |

Recommended replacement: documentation range `203.0.113.x` or the token `<vps-ip>`.

### 4.3 Requires action — Telegram operational identifiers (redact before public)
| File | Line(s) | Content (redacted) |
|---|---|---|
| `audit-outputs/research/track-c/c5-observability-status-telegram.md` | 65 | Telegram ops bot handle + **real chat ID** + Netdata URL containing the VPS IP |
| `audit-outputs/research/source-and-decision-index.md` | 293 | same bot handle + chat ID |

No bot **token** exists anywhere (token family scanned clean). Handle + chat ID alone cannot send messages, but they disclose internal ops channels. Recommended replacement: `<chat-id>` / `@<ops-bot>`.

### 4.4 Review — contact emails (likely intended public)
| File | Line(s) | Note |
|---|---|---|
| `audit-outputs/research/track-d/d4-contact-support.md` | 62, 64, 106 | Legacy FAQ support address, legacy privacy contact, proposed public `mailto:` address — publishing a contact address is the documented plan (DEC-117 context) |
| `audit-outputs/ui-docs-code-reconciliation.md` | 115 | FAQ CTA email (same address family) |
| `audit-outputs/research/source-and-decision-index.md` | 355 | same |
| `audit-outputs/research/track-a/a1-shared-engine-licenses.md` | 72 | Third-party developer email embedded in a public Yocto patchwork citation URL — public source, low risk |

### 4.5 False positives — no action
| File | Line | Explanation |
|---|---|---|
| `audit-outputs/research/track-b/_evidence-legacy-frontend.md` | 403 | Indonesian UI copy "Kekuatan password: Kuat/Sedang/Lemah" matched the `password:` heuristic |
| `audit-outputs/research/track-d/d1-adsterra.md` | 66 | Adsterra payout terms (Paxum / PayPal / wire); no phone or personal data |

### 4.6 Placeholders and public identifiers — LOW, no action
- `Authorization: Bearer <API_KEY>` **placeholders** in 13 locations (Appendix B) — all literal `<API_KEY>` with "stored only in protected secrets" wording; documentation, not credentials.
- Public infrastructure identifiers already published by the legacy repo README: `mypapyr.com`, `api.mypapyr.com`, `frontend-ten-omega-35.vercel.app`, `papyr-files` (R2 bucket name), `Netdata Cloud`, env **variable names** (`SUPABASE_URL`, `HOSTINGER_API_TOKEN`, `SENTRY_DSN`) — names only, no values.

## 5. Public / private classification

| Classification | Files | Count |
|---|---|---|
| PUBLIC-SAFE as-is (zero pattern matches, or only public identifiers / placeholders) | `README.md`, `AGENTS.md`, `.gitignore`, `docs/resolution-register.md`, both specs, implementation plan, `scripts/check-docs-migration.sh`, large majority of `audit-outputs/**` | ~62 |
| REDACT-BEFORE-PUBLIC (VPS IP / Telegram ops) | `papyr-rebuild-decisions.md`, `_evidence-decisions.md`, `c1-queue-workers-redis.md`, `c5-observability-status-telegram.md`, `source-and-decision-index.md` | 5 |
| REVIEW (contact emails) | `d4-contact-support.md`, `ui-docs-code-reconciliation.md`, `a1-shared-engine-licenses.md` | 3 |
| EXCLUDED — never track | `.env.papyr` (real secrets; ignored by `.env.*`), `papyr-reference/` (entire dir + nested `.git`; ignored by `/papyr-reference/`) | - |
| UNTRACKABLE (empty dirs) | `backend/`, `frontend/`, `deploy/` — add `.gitkeep` only if structure must appear in repo | 3 |

## 6. Unsafe audit artifacts (ranked)

1. **`papyr-reference/`** — nested git repo (45 MB, 388 commits, origin = public legacy repo). Largest single artifact; excluded by `.gitignore:15`; must never be force-added.
2. **`audit-outputs/research/track-c/c5-observability-status-telegram.md`** — real Telegram chat ID + ops bot handle + Netdata URL with VPS IP (line 65). Most sensitive tracked file.
3. **`papyr-rebuild-decisions.md`** — VPS IP in a section header (776, 780); highest-visibility governed record (197 KB).
4. **`audit-outputs/research/source-and-decision-index.md`** — VPS IP + bot handle + chat ID (line 293).
5. **`audit-outputs/research/track-c/c1-queue-workers-redis.md:87`** — VPS IP + host facts.
6. **`audit-outputs/research/track-b/_evidence-decisions.md:80`** — VPS IP.
7. **`audit-outputs/research/track-d/d4-contact-support.md`** — 3 contact emails (low; intended public).
8. **`audit-outputs/research/track-a/a1-shared-engine-licenses.md:72`** — third-party email in a citation (low).
9. **`.env.papyr`** — the only real secrets file; ignored; never opened by this audit; must stay out of any repo packaging/backup.
10. **Business-sensitive (not secrets; owner decision)** — `d1-adsterra.md` (payout terms), `e1-gpt5-6-sol-contract.md`, `e2-automated-mdx-blog-pipeline.md`, `d5-security-threat-privacy.md` (defensive security research; DEC-1405 requires omitting "defensive controls, exploit details").

## 7. Secret / PII scanning strategy (layered, repeatable)

- **L1 — heuristic regex** (13 families, Appendix A): catches structural items gitleaks misses (raw IPs, chat IDs, emails).
- **L2 — gitleaks** (installed, v8.21.2): `gitleaks dir <workspace-root>` pre-init; `gitleaks detect --source . --staged` pre-commit; `gitleaks detect --source .` pre-push / full history; CI via `gitleaks/gitleaks-action@v2`. Note: gitleaks alone would likely report 0 even before redaction — IP/chat-ID/email items are not gitleaks rules, so L1 is mandatory.
- **L3 — GitHub secret scanning + push protection** (free for public repos) + gitleaks CI job on push/PR.
- **L4 — human review gate** for `audit-outputs/` web-evidence and business-sensitive track-d/e files.
- **L5 — rotation policy, already DEC-mandated**: `papyr-rebuild-decisions.md:2073` ("rebuild requires rotation of legacy credentials and investigation of possible historical exposure before production use") and `:224`; `:2289` ("Authentication credentials must never enter client code, repository content, logs, generated articles, or analytics"); `:1405` (incident updates must omit hostnames, credentials, defensive controls, exploit details).
- **L6 — future-code guardrails**: pre-commit hook (pre-commit framework + gitleaks) once the repo exists; keep `.env.*` rules; extend `.gitignore` per Section 3 gaps.

## 8. Exact pre-init gates (before `git init`)

| # | Gate | Command / check | Pass condition |
|---|---|---|---|
| G1 | Owner sign-off on Section 4.2 + 4.3 redactions; apply edits | edit the 5 listed files | diff shows only redactions |
| G2 | Extend `.gitignore` | append Section 3 gap list incl. `/.env.papyr`, `gitleaks-report.json` | diff shows new rules only |
| G3 | Re-run L1 scanner after redaction | Section 11 Python scanner | 0 matches in 4.2/4.3 families |
| G4 | L2 pre-init scan | `gitleaks dir <workspace-root>` | 0 findings |
| G5 | Verify legacy untouched | `git -C papyr-reference status --porcelain` | empty output |
| G6 | Confirm no `.env*` leak candidates | `find . -maxdepth 1 -name ".env*"` | only `.env.papyr` |
| G7 | **Then** initialize | `git init -b main` | repo created; remains private |

## 9. Exact post-init / pre-commit / pre-push gates

| # | Gate | Command / check | Pass condition |
|---|---|---|---|
| G8 | Ignore-rule proof | `git check-ignore -v .env.papyr` -> `.gitignore:5:.env.*`; `git check-ignore -v papyr-reference/README.md` -> `.gitignore:15:/papyr-reference/` | both resolve to rules |
| G9 | Staging review | `git status --porcelain` (expect 69 entries); grep for `papyr-reference|env.papyr` | empty grep output; no "embedded git repository" warning |
| G10 | Stage + index review | `git add -A`; `git diff --cached --name-only` | 69 files; no `.env*`; no `papyr-reference/`; no nested-repo warning (never `-f`) |
| G11 | Index secret scan | L1 Python scan + `git grep --cached -nE "<families>"` | 0 matches |
| G12 | Commit + history scan | first commit; `gitleaks detect --source .` | 0 findings |
| G13 | CI wiring | add `.github/workflows/gitleaks.yml` (gitleaks-action v2, push + PR) | workflow green |
| G14 | Remote separation | `git remote -v` | points to a **new** repo — never legacy `fazulfi/papyr` |
| G15 | Create repo (private) | `gh repo create <name> --private --source=. --push` (gh authed as `fazulfi`) | private repo pushed |
| G16 | GitHub security settings | enable secret scanning + push protection; verify Actions gitleaks green | configured |
| G17 | Public flip (owner-only) | Settings -> change visibility to public | after G13/G16 green + explicit authorization |

## 10. Exact pre-public gates (final, owner-gated)

| # | Gate | Pass condition |
|---|---|---|
| P1 | All G1-G17 pass with recorded evidence | evidence file attached |
| P2 | CI (gitleaks) green on pushed default branch | Actions page green |
| P3 | Secret scanning + push protection confirmed enabled | Settings -> Security shows enabled |
| P4 | No open secret-scanning alerts | alerts list empty |
| P5 | Owner reviews business-sensitive artifacts (Section 6.10) or documents their exclusion | decision recorded |
| P6 | Visibility changed to public (owner action only) | post-public: monitor alerts; re-run gitleaks periodically |

## 11. Evidence log (read-only commands used)

`ls -la`; `find` (per-dir counts, dotfiles, symlinks, sensitive file types); `git status` (root: not a repo); `git -C papyr-reference {status --porcelain, rev-list --all --count, remote -v, log --oneline -3, ls-files, grep -InE}`; `du -sh`; Python 13-family regex scanner (UTF-8, NUL-byte detection, redacted line dump); `grep -rInE` families (keys / tokens / creds / URLs / emails / IPs / markers); web fetch of `github.com/fazulfi/papyr` (repo visibility); `gitleaks version` (8.21.2); `gh auth status` (authed; token masked by gh). All scans excluded `papyr-reference/`, `.git`, and `.env.papyr`.

## 12. Uncertainties / unresolved questions

1. **Publish `audit-outputs/` at all?** Internal research evidence; contains monetization (d1), a GPT contract (e1), a blog pipeline (e2), security-threat research (d5). Owner decision; alternative is ignoring or trimming before public.
2. **Contact emails (Section 4.4)** — confirm the exact addresses are the intended public support/privacy contacts.
3. **`docs/canonical-docs-baseline.md`** — referenced by `scripts/check-docs-migration.sh:35-37` but does not exist -> the script currently FAILS. Governance gap, not a safety issue; confirm whether the baseline file should exist.
4. **Legacy public repo history** (`fazulfi/papyr`, 381 commits public) — recommend a separate gitleaks history audit; the new repo is unaffected (excluded).
5. **LICENSE absent** — legacy repo is proprietary ("All rights reserved"); the new public repo needs an explicit license decision.
6. **Root `.env.example`** does not exist despite the `!.env.example` un-ignore rule — optional safe addition.
7. **Empty `backend/`, `frontend/`, `deploy/`** will not appear in the repo — add `.gitkeep` before init if directory structure must be present.

## Appendix A — Regex families used (names only, values redacted in output)

api_key, jwt, private_key, cred_url, tg_token, assign_creds, email, ipv4, aws_acct_12digits, webhooks, npm_token, ssh_pubkey, bearer_token.

## Appendix B — `Authorization: Bearer <API_KEY>` placeholder locations (documentation, no values)

`papyr-rebuild-decisions.md:2322`; `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md:1092`; `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md:554,723`; `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md:40`; `audit-outputs/architecture-spec-revision-dec189-196.md:19,45,109,116`; `audit-outputs/product-ux-spec-revision-dec189-196.md:71,168`; `audit-outputs/spec-revision-cross-review-dec189-196.md:120,129`; `audit-outputs/spec-revision-final-corrections-dec189-196.md:99`; `audit-outputs/research/track-e/e1-gpt5-6-sol-contract.md:86`.
