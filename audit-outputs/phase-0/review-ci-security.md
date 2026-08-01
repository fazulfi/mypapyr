# Wave 3 — Independent Review: CI and Security Gate (FD-04)

- **Reviewer**: parent agent (Sisyphus), direct execution
- **Reason for direct execution**: the delegated reviewer `bg_1374e28e` (session `ses_045e52e47ffeaTyMorTHLHRQOu`) reported COMPLETED in 2m42s but **never persisted its deliverable** — `audit-outputs/phase-0/review-ci-security.md` was missing entirely. Per `AGENTS.md` the file is the deliverable and a chat-only claim is insufficient, so the chat-only result was rejected and this review was re-executed directly.
- **Scope**: `.github/workflows/ci.yml` and `scripts/check-ci.sh`.
- **Mode**: read-only inspection plus one corrective edit (see §6, finding CI-F1).

## 1. Verdict

**ACCEPT — after remediation of one material finding (CI-F1) applied during this review.**

## 2. Guard script execution

| Run | Command | Output | Exit |
| --- | --- | --- | --- |
| Before fix | `bash scripts/check-ci.sh` | `check-ci: PASS` | 0 |
| After fix | `bash scripts/check-ci.sh` | `check-ci: PASS` | 0 |

The guard asserts: `ci.yml` exists, no deploy/CD job, no `pull_request_target`, no `secrets:` mapping, and all `uses:` entries SHA-pinned.

## 3. No-CD boundary (DEC-160 / DEC-177)

| Requirement | Evidence | Status |
| --- | --- | --- |
| Triggers limited to `push` and `pull_request` on `main` | `ci.yml:3-7` — `push: branches: [main]`, `pull_request: branches: [main]` | PASS |
| Never `pull_request_target` | grep over the whole file returns no occurrence | PASS |
| No deploy job | grep for `deploy\|ssh\|scp\|rsync\|vercel\|wrangler` (case-insensitive) → `NO_DEPLOY_KEYWORDS` | PASS |
| Legacy `deploy-vps.yml` not replicated | only `ci.yml` exists under `.github/workflows/` | PASS |

The keyword scan returning zero matches is the strongest available evidence that no deployment, no SSH, and no provider CLI invocation exists anywhere in the workflow.

## 4. Least-privilege and token hygiene

| Control | Evidence | Status |
| --- | --- | --- |
| Top-level `permissions: contents: read` | `ci.yml:9-10` | PASS |
| Per-job `permissions: {}` (empty, no token) | lines 20, 48, 74, 102, 131, 167, 194 — all 7 jobs | PASS |
| No `secrets:` mapping anywhere | grep returns no `secrets:` key | PASS |
| `persist-credentials: false` on every checkout | lines 28, 56, 82, 110, 139, 171, 198 — 7 occurrences, one per job | PASS |
| Concurrency with cancellation | `ci.yml:12-14`, `group: ${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true` | PASS |

Every job runs with an empty permission set and a credential-free checkout. No workflow step can obtain a write-scoped token.

## 5. Job inventory (7 jobs, all CI-only)

| Line | Job | Purpose |
| --- | --- | --- |
| 17 | `frontend-lint` | format + lint |
| 45 | `frontend-test` | unit tests, `npm run test:coverage` (line 68) |
| 70 | `frontend-build` | `next build` production-build verification |
| 99 | `backend-lint` | ruff check + ruff format --check |
| 128 | `backend-test` | `pytest tests/ -v --tb=short --cov=app --cov-fail-under=80` (line 156) |
| 164 | `security-trivy` | Trivy scan + SARIF artifact upload |
| 191 | `secret-scan-gitleaks` | gitleaks CLI secret scan |

The owner-required `>=80%` coverage gate is enforced in CI at `ci.yml:156` for the backend and via `test:coverage` at `ci.yml:68` for the frontend.

## 6. Finding CI-F1 (MATERIAL) — incorrect SHA-to-version pin, remediated

**Observed**: line 185 pinned `actions/upload-artifact@5d5d22a31266ced268874388b861e4b58bb5c2f3` with the trailing comment `# v4.6.0`.

**Verification against the GitHub API**:

- `repos/actions/upload-artifact/git/ref/tags/v4.6.0` → `65c4c4a1ddee5b72f698fdd19549f0f0fb45cf08`, which does **not** equal the pinned SHA.
- `repos/actions/upload-artifact/commits/5d5d22a3...` resolves to a real commit whose message is `Merge pull request #515 ... updating artifact dependency to version 2.1.1` — a v4.3.x-era commit, not v4.6.0.

**Impact**: the pin itself was immutable and therefore not a supply-chain hole, but the version comment was factually wrong. That defeats the purpose of the comment, which exists so a human or auditor can verify the SHA-to-version mapping, and it would have propagated a false claim into a public repository. `check-ci.sh` could not catch this because it validates pin *shape*, not pin *truth*.

**Remediation applied**: repinned to the verified v4.6.2 commit.

```
uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
```

Confirmed on disk at `ci.yml:185`. `scripts/check-ci.sh` re-run after the edit: `check-ci: PASS`, exit 0.

## 7. SHA pin verification (post-remediation)

All action references, each verified against the GitHub API tag-to-commit dereference:

| Action | SHA | Version comment | Verified |
| --- | --- | --- | --- |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `# v7.0.1` | yes |
| `actions/setup-node` | `820762786026740c76f36085b0efc47a31fe5020` | `# v7.0.0` | yes |
| `actions/setup-python` | `5fda3b95a4ea91299a34e894583c3862153e4b97` | `# v7.0.0` | yes |
| `aquasecurity/trivy-action` | `ed142fd0673e97e23eac54620cfb913e5ce36c25` | `# v0.36.0` | yes (annotated tag dereferenced) |
| `actions/upload-artifact` | `ea165f8d65b6e75b540449e92b4886f43607fa02` | `# v4.6.2` | yes (repinned in this review) |

No bare `@vN` reference remains. gitleaks is consumed as a pinned CLI download of `v8.30.1` (`ci.yml:204-208`) rather than a third-party action, then invoked as `gitleaks detect --source . --no-banner --redact` (line 211) — this avoids the proprietary-action licensing issue and keeps output redacted.

## 8. Uncertainties and honest disclosures

1. `security-trivy` and `secret-scan-gitleaks` were **not executed locally**. Docker is absent from this workstation and the gitleaks CLI is not installed; installing either is outside authorized Phase 0 scope. Both jobs are statically verified as correctly written but their runtime behaviour is unproven until the first CI run. This must be re-confirmed when CI executes on the pull request.
2. No backend container image is built or scanned. That is correct for this phase — the backend image is owned by SEC-04 in Phase 5, so image scanning is intentionally deferred rather than missing.
3. `check-ci.sh` validates pin *shape* only. Finding CI-F1 proves shape validation is insufficient. Recommendation for a later phase: extend the guard to resolve each SHA against its claimed tag via the API when network access is available.

## 9. Scope discipline

- Exactly one file was modified: `.github/workflows/ci.yml` line 185 (the CI-F1 remediation). No other file was touched.
- `papyr-reference/` verified unchanged after the edit: porcelain count `0`, HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`.
- No `.env.papyr` value was read or printed.
- No `git add`, `commit`, `push`, `init`, or `remote` operation was performed.
