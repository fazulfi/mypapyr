# Public-Safety Remediation Record — Phase 0

Status: **COMPLETE — 0 sensitive literals remaining in tracked-eligible files**

This record closes the CRITICAL blocker raised in `review-public-safety.md`
(verdict: `REDACT-BEFORE-PUBLIC` / "NOT SAFE TO COMMIT until all CRITICAL and
HIGH items remediated").

## 1. Why remediation happened before the first commit

The owner directive requires the repository to be converted to public. Any
sensitive literal committed even once is embedded in Git history permanently and
cannot be removed by a later edit. Therefore redaction was executed **before the
first commit**, not merely before the visibility flip.

## 2. Redaction mapping applied

This record deliberately describes each original value **without reproducing it**.
Writing the raw literals here would re-leak exactly what the pass removed, and
would make this file fail the pre-commit secret scan.

| Original value (described) | Replacement | Class |
| --- | --- | --- |
| Current production VPS IPv4, plus its `/24` prefix form and escaped-regex variants | `<vps-ip>` | CRITICAL |
| Legacy VPS IPv4, plus escaped-regex variants | `<vps-ip>` | CRITICAL |
| Telegram ops bot handle, with and without the leading `@` | `<telegram-bot>` | CRITICAL |
| Telegram ops chat id (10-digit numeric) | `<telegram-chat-id>` | CRITICAL |
| Internal VPS hostname | `<vps-host>` | HIGH |
| Operator workspace path, Windows and POSIX separator forms | `<workspace-root>` | HIGH |
| Operator home path, Windows and POSIX separator forms | `<user-home>` | HIGH |

The exact literals remain recoverable by the owner from the gitignored
credential file and the platform consoles; they are intentionally absent from
every tracked file, including this one.

Patterns were applied longest-first so that short patterns could not shadow
longer, more specific ones.

## 3. Scope boundaries enforced

Excluded directories: `papyr-reference/`, `node_modules/`, `.venv/`, `venv/`,
`.git/`, `.next/`, `coverage/`, `.pytest_cache/`, `.ruff_cache/`,
`__pycache__/`, `_adversarial/`, `out/`, `dist/`, `build/`.

Excluded file: `.env.papyr`. This file holds live credentials, is gitignored via
`.gitignore:9` (`/.env.papyr`), is never tracked, and was never edited or read
for values. It still contains real values by design; it must never be committed.

`papyr-reference/` was never written to. Legacy invariant verified before and
after the pass.

## 4. Governed-record sanitization note

Two governed records were touched by the redaction pass:

- `papyr-rebuild-decisions.md` (DEC-063 heading and decision body)
- `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`

These edits are **sanitization only**. No decision semantics, no decision IDs, no
ordering, and no normative statements were altered — only the sensitive literal
was replaced by its placeholder. DEC-063 still records the same decision ("do not
benchmark on the VPS"), now expressed as `<vps-ip>` instead of the raw address.

## 5. Verification evidence

Verification grep run from the workspace root, excluding
`papyr-reference/`, `node_modules/`, `.venv/`, `.git/`, `.next/`, `coverage/`,
`__pycache__/`, and the gitignored `.env.papyr`:

| Pattern class | Files remaining |
| --- | --- |
| Current VPS IPv4 (prefix match) | 0 |
| Legacy VPS IPv4 (prefix match) | 0 |
| Telegram ops bot handle | 0 |
| Telegram ops chat id | 0 |
| Internal VPS hostname | 0 |
| Operator home path | 0 |

Placeholders (`<vps-ip>`, `<telegram-bot>`, `<telegram-chat-id>`, `<vps-host>`,
`<workspace-root>`, `<user-home>`) are now present in 67 files.

A confirmatory second run of the redaction script reported
`SCANNED_FILES=126, CHANGED_FILES=0, TOTAL_REPLACEMENTS=0` — the pass is
idempotent and the workspace is already clean.

Self-referential leaks were also closed: `review-public-safety.md` itself had 12
occurrences of the literals it was documenting, and
`integration-validation.md:404` and `review-docs.md:179` each printed the IP in
the same sentence that claimed it was redacted. All are now placeholder-only.

## 6. Gitignore and staging hygiene fixed in the same pass

| Item | Before | After |
| --- | --- | --- |
| `backend/.coverage` | `NOT_IGNORED` — rule `coverage/` matches directories only | `IGNORED` via new `.coverage` and `.coverage.*` rules |
| `audit-outputs/_adversarial/` | empty directory; broke `git add -A --dry-run` with "does not have a commit checked out" | removed; `git add -A --dry-run` now exits clean |

Tracked-eligible file count after hygiene fixes: **126**
(`git ls-files --others --exclude-standard`).

## 7. Legacy invariant

| Check | Result |
| --- | --- |
| `git -C papyr-reference status --porcelain` | 0 lines (clean) |
| `git -C papyr-reference rev-parse HEAD` | `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (unchanged) |

## 8. Honest disclosures

- `gitleaks` and `trufflehog` were **not** executed locally: neither binary is
  installed and installing them is out of Phase 0 scope. Pattern-based grep was
  substituted. The CI `secret-scan-gitleaks` job (pinned CLI v8.30.1) will run
  the real scanner on the first CI execution and is the authoritative gate.
- No real credentials (private keys, API tokens, bearer headers) were found in
  the tracked-eligible set at any point — the findings were network identifiers,
  operator identifiers, and local filesystem paths.
- Benign matches deliberately left untouched: `127.0.0.1:__SET_ME__:80` in
  `deploy/docker-compose.yml`, the public GitHub handle `fazulfi`, the public
  legacy remote URL, intended-public contact addresses at `mypapyr.com`, and
  GitHub Action SHA pins.

## 9. Remaining owner-gated item

Converting the repository to public visibility remains an owner-gated action and
is tracked separately. This record only certifies that the content is now free
of the identified sensitive literals.
