# Phase 8 SEO / URL Migration Completion Report

- **Status:** In branch; documentation reconciliation complete in this worktree. DNS/Cloudflare configuration verified read-only, and the R-25 traffic baseline was captured on 2026-08-20; see [`docs/seo/seo-slo.md`](../seo/seo-slo.md).
- **Branch:** `feat/full-p8-seo-url-migration`.
- **Scope:** SEO-01 governance, SEO-02 legacy URL behavior, SEO-03 metadata/sitemap polish, and evidence-based documentation reconciliation.
- **Release status:** No P8 commit, push, PR, or deployment was performed. P8 is not merged to `main` and is not a production release.

## Evidence-backed implementation

### SEO-01 — URL governance

- `docs/seo/slug-table.md` records the indexable route set: 42 URLs (5 tools × 3 locales, 8 supporting routes × 3 locales, and 3 locale home routes).
- `docs/seo/legacy-url-inventory.md` records exactly 15 locale-less legacy paths: 5 permanent redirects, 8 Gone responses, and 2 locale-dependent temporary redirects.
- `scripts/check-seo-inventory.sh` cross-checks the documentation against the code singletons and fails closed on missing, duplicate, conflicting, or unmapped entries.
- The repository CI workflow on this branch contains the `qa-seo-inventory` job. The documentation audit's committed-base ground truth is 23 jobs / 22 on pushes to `main`; the additional P8 job is in-branch and has not been merged.

### SEO-02 — redirect and Gone behavior

- 301, single-hop aliases: `/compress` → `/{locale}/compress-pdf`; `/merge` → `/{locale}/merge-pdf`; `/split` → `/{locale}/split-pdf`; `/image-to-pdf` → `/{locale}/jpg-to-pdf`; `/pdf-to-image` → `/{locale}/pdf-to-jpg`.
- Localized 410 paths: `/rotate`, `/protect`, `/unlock`, `/watermark`, `/sign`, `/pdf-to-word`, `/ocr`, `/pdf-to-excel`.
- Locale-dependent 307 paths: `/faq` and `/privacy`, resolving cookie → `Accept-Language` → EN.
- 301 responses do not set the locale cookie. Retired-tool exceptions remain blocked by R-25: no owner traffic evidence is available, so no 410 exception is claimed.

### SEO-03 — canonical, hreflang, sitemap, and robots

- `SEO_BASE_URL` is code-pinned to `https://budgezen.com` and is shared by layout metadata, sitemap, and robots.
- Indexable localized routes emit self-canonical metadata and `en`, `es`, `id`, and `x-default` alternates; no `es-419` is claimed.
- The sitemap emits 42 entries and excludes locale-less redirects, the `tool-unavailable` surface, and deferred legacy query variants.
- `robots.txt` points to the code-pinned canonical sitemap URL.
- Sitemap `lastModified` uses the committed deterministic constant `2026-08-18`; it is not generated from the current time.

## NOT_VERIFIED boundaries

- **Canonical host:** NOT_VERIFIED. Code currently pins `budgezen.com`, while deployment documentation identifies `mypapyr.com` as the VPS frontend host. No owner decision selecting the primary host is recorded.
- **Deployment host / release:** NOT_VERIFIED for P8. No P8 deployment occurred; no build identifier, live metadata response, or production redirect verification is claimed. Existing P6 deployment records do not establish a P8 deployment.
- **R-25 traffic:** NOT_VERIFIED. No owner-provided legacy traffic data is on record; the documented default is 410 for all eight deferred tools.
- **External indexing and ranking:** NOT_VERIFIED. No search-console, crawler, indexing, ranking, or traffic evidence is available. This report makes no ranking, indexing, discoverability, or SEO-performance claim.
- **SLO/certification:** NOT_VERIFIED. No SEO SLO, uptime guarantee, legal compliance, certification, or universal-conformance claim is made.
- **P7 status:** P7 remains in branch `feat/full-p7-enterprise-completion` and is not an ancestor of this branch's `origin/main` base; PR #47 is not treated as merged or deployed.

## Verification and release boundary

Completed repository-level evidence for this report:

- `bash scripts/check-seo-inventory.sh` — PASS: 15 legacy paths, all dispositions mapped, slug table consistent.
- Documentation audit evidence confirms 23 CI jobs on the audited P8 working state's committed workflow and 22 on pushes to `main` when dependency review is PR-only.
- Source and tests remain the authority for behavior; this report does not substitute local verification for production verification.

Before any P8 activation, an authorized release must verify the selected host on both candidate domains, `/sitemap.xml`, `/robots.txt`, representative 301/410/307 responses, canonical/hreflang output, sitemap count and lastmod, and the intended build identifier. Rollback remains the existing release pointer/digest procedure in `docs/release-checklist.md` and `deploy/runbook-vps.md`; no rollback drill is claimed here.

## Documentation changes

Documentation files changed by this task are limited to `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `README.md`, `docs/README.md`, `docs/roadmap.md`, `docs/release-checklist.md`, `docs/p6-completion-report.md`, `docs/specifications/product.md`, `docs/specifications/architecture.md`, `docs/seo/slug-table.md`, `docs/seo/legacy-url-inventory.md`, and this report. The pre-existing working tree also contains P8 source, tests, workflow, and guard changes; this task did not edit those files. No deploy, secret, or plan file was intentionally edited.

Unresolved blocker: owner selection of the canonical host and provision of R-25 traffic evidence remain required before changing the host value or making deferred-path exceptions; authorized deployment and external indexing verification remain outside this task.
