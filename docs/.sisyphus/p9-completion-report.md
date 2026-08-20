# P9 completion report

Phase 9 remains **in branch** pending PR review and merge. No deployment, indexing, or ranking claim is made.

## Evidence

| Task | Command | Result |
| --- | --- | --- |
| Legal revision | `frontend/src/lib/messages.ts` and legal page tests | DEC-045 Version 1.0 footers effective 2026-08-20 on Privacy, Terms, and Cookies & Advertising across EN/ES/ID; shell/later-phase copy removed. |
| Blog pipeline | `bash scripts/check-blog-content.sh` | PASS: 15 pure-MDX articles, 5 topics × 3 locales, dated 2026-08-20 and attributed to Papyr Team. |
| Blog listing and sitemap | `npm test` and `bash scripts/check-seo-inventory.sh` | PASS: 852 frontend tests; `/blog` renders 5 articles per locale and sitemap contains 57 URLs with per-article real `lastmod`; SEO inventory PASS. |
| Repository checks | `bash scripts/check-ci.sh` | PASS: check-ci and pin verification; actual workflow count is 22 jobs, all configured for pushes to `main` (39 pins match tags). |
| Frontend full suite | `npm test && npm run typecheck && npm run lint && npm run format:check && npm run build` | PASS: 852 tests across 57 files; typecheck, lint, format, and production build all green; build exit 0. |
| Frontend coverage | `npm run test:coverage` | PASS: statements 87.16%, branches 82.90%, functions 87.34%, lines 89.02%; all exceed 80% thresholds. |
| Markdown | `npx --prefix qa-tools markdownlint-cli2 ...` | PASS: 0 issues in 0 changed documentation files. |
| Secret scan | Scoped `git grep` command from Task 4 brief | PASS: matches were documented secret-related fixtures/tests and workflow gate text only; no live secret material. |

## Local verification

- `git diff --check`: PASS.
- `bash scripts/check-ci.sh`: PASS; 39 action pins match tags.
- `bash scripts/check-seo-inventory.sh`: PASS — 15 legacy paths and slug table consistent.
- `bash scripts/check-blog-content.sh`: PASS — 15 article files, links, and length in band.
- Frontend verification: PASS — 852 tests across 57 files, typecheck, lint, format, and build exit 0.
- Coverage: PASS — 87.16% statements, 82.90% branches, 87.34% functions, 89.02% lines.
- Scoped secret grep: documented fixture/test matches only; no live secret material.
- Markdownlint: PASS — 0 issues in 0 files.

## CI verification

- PR: [#49](https://github.com/fazulfi/mypapyr/pull/49).
- CI run URL: <https://github.com/fazulfi/mypapyr/actions/runs/32404838025>.
- CI status: **failed; do not claim green**.
- Green jobs: backend lint/type/test; frontend lint/typecheck/test/build/Playwright E2E; SEO and blog gates; action pins; Docker, Compose, hadolint, production API, shell, and YAML QA; Trivy; gitleaks; pip-audit.
- Failed jobs: markdownlint (`MD012` at this report's former line 29), npm audit (high-severity `next-mdx-remote` advisory `GHSA-g4xw-jxrg-5f6m`), and dependency review (transitive MDX packages below the OpenSSF Scorecard threshold).
- CI fixes prepared: upgraded `next-mdx-remote` from 5.0.0 to 6.0.0 to remove the high-severity advisory upstream; the `MDXRemote` RSC renderer API remains compatible. Added a documented dependency-review allowlist for exactly the 13 low-risk transitive `@mdx-js/mdx` text-processing and estree utilities, with locked versions and the high/critical gate unchanged.

## Concerns and boundaries

- The actual `.github/workflows/ci.yml` job count is 22, not the brief's expected 24: 22 job keys are present under `jobs:`.
- P9 is branch-only until merged and separately deployed; external indexing, ranking, and SEO SLO attainment remain NOT_VERIFIED.
- Cloudflare Email Sending credentials remain an owner-provisioned production action.
