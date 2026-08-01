# CI gitleaks allowlist decision — Phase 0

## Verdict

The `Security (gitleaks secret scan)` job failed on CI run `30676842781` with
`leaks found: 2`. Both findings were verified false positives. The gate was
kept enabled and a narrow, documented allowlist was added instead of disabling,
weakening, or bypassing the scan.

## Findings

Local reproduction with the same pinned CLI (`gitleaks 8.30.1`) matched CI
exactly: 19 commits scanned, ~3.32 MB, 2 findings, both `RuleID = generic-api-key`,
both `Entropy = 3.5724695`, secret redacted in every output.

| # | File | Line | Introduced by commit | Nature |
| --- | --- | --- | --- | --- |
| 1 | `audit-outputs/research/track-b/_evidence-legacy-frontend.md` | 403 | `9595253` docs(audit): add discovery research track evidence | Indonesian UI copy for the legacy password-strength indicator |
| 2 | `audit-outputs/phase-0/repository-safety-audit.md` | 89 | `8fcec71` docs(audit): add phase 0 execution records and review evidence | The safety audit's own false-positive table, quoting finding 1 |

## Why these are false positives

Both lines contain the Indonesian sentence describing the legacy password
strength meter. The literal is the word `password` followed by a colon and an
ordinary Indonesian adjective list. The upstream `generic-api-key` rule treats
`password:` followed by a high-entropy-looking token as a candidate credential,
so ordinary prose in Indonesian trips it.

No credential exists at either location. The independent repository safety
audit had already classified this exact string as a false positive in its own
"False positives — no action" table before gitleaks ever ran in CI, so finding 2
is that classification being re-detected by the scanner it describes.

## Remediation applied

`.gitleaks.toml` was added at the repository root. It sets `useDefault = true`
so the entire upstream ruleset stays active, then attaches an allowlist to the
single rule `generic-api-key`. The allowlist is constrained on two axes at once:

- `regexes` matches only the exact Indonesian sentence.
- `paths` restricts the exemption to the two documented evidence files.

Any other file, or any other string in those two files, still fails the scan.
The CI step now runs `gitleaks detect --source . --config .gitleaks.toml --no-banner --redact`.

## What was deliberately not done

- The gitleaks job was not disabled, skipped, or made non-blocking.
- `--redact` was not removed.
- The scan was not switched to `--no-git`, so full history is still scanned.
- No broad path exclusion (such as exempting all of `audit-outputs/`) was added.
- No finding was deleted from the evidence files to make the scanner quiet.

## Verification

| Check | Command | Result |
| --- | --- | --- |
| gitleaks with config | `gitleaks detect --source . --config .gitleaks.toml --no-banner --redact` | `no leaks found`, exit 0, 19 commits, 3.32 MB |
| CI guard script | `bash scripts/check-ci.sh` | PASS |
| Legacy clone untouched | `git -C papyr-reference status --porcelain` / `rev-parse HEAD` | empty / `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` |

## Disclosure

The local gitleaks binary is the pinned `v8.30.1` Windows build, matching the
pinned Linux build downloaded by the CI job. Before this step the scanner had
never been executed locally because it was not installed; that limitation was
disclosed in the CI security review rather than being papered over.
