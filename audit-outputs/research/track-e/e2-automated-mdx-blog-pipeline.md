# E2 Research Brief: Automated Repository-Backed MDX Blog Pipeline

| Field | Value |
|---|---|
| Brief ID | E2 |
| Path | `audit-outputs/research/track-e/e2-automated-mdx-blog-pipeline.md` |
| Track | E (blog automation research) |
| Title | Automated MDX blog pipeline research |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete |
| Governing decisions | DEC-048, DEC-049, DEC-051, DEC-052, DEC-053, DEC-113, DEC-121, DEC-124, DEC-097, DEC-141, DEC-016, DEC-096; DEC-054 to DEC-060, DEC-066, DEC-183, DEC-188 |
| Governing plan section | Research program plan §6.5, §7.5 (E2), §8 (template) |
| Files read | `AGENTS.md`; `audit-outputs/research-program-plan.md`; `papyr-rebuild-decisions.md` (DEC-001-188, in full); `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` (§15.6, §21.21); `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` (§25.3.21); `audit-outputs/spec-cross-review.md`; `audit-outputs/spec-corrections-report.md`; read-only legacy evidence from `papyr-reference/` (paths and lines cited in Section 5); public primary sources listed in Section 5 (all URLs verified live with HTTP 200 on 2026-07-31 unless noted) |

---

## 1. Scope

### 1.1 Feature and decision area

DEC-048 accepts fully automated LLM-driven blog generation and publishing without human approval per article. DEC-049 requires blog content to live as version-controlled MDX in the Papyr repository, with the publishing automation "creat[ing] validated repository changes and trigger[ing] the normal preview/build/deployment path rather than writing directly into a production filesystem." E2 researches the safe, repository-backed MDX pipeline architecture that satisfies both decisions: generation, localization, blocking quality gates that fail closed, validation, scheduling, audit logs, pause and kill-switch controls, rollback, correction, and secret handling.

### 1.2 User problem

The multilingual content program (five launch topics x EN/ES/ID; then at most one coordinated trilingual topic set per day, DEC-052, DEC-053, DEC-121, DEC-124) must publish reliably and truthfully at scale with no human per-article approval, without ever publishing content that fails a quality gate, without breaking the deployed site, and without leaking secrets.

### 1.3 Current approved Papyr behavior

- Launch inventory: five topics x three locales = 15 articles (DEC-052, DEC-121).
- Post-launch: at most one coordinated trilingual topic set per day; a failed gate blocks the whole set for that day (DEC-124); skipping is preferable to weakening gates (DEC-053).
- Blocking gates: factual support, duplication and cannibalization, search intent, originality, language quality, metadata, internal links, unsafe claims, policy violations, malformed MDX (DEC-048); fail closed (DEC-048).
- No fabricated expertise, authors, test results, citations, product capabilities, legal advice, or performance claims (DEC-048, DEC-110).
- Content stored as MDX in the repository; automation creates validated repository changes through the normal build path (DEC-049).
- Provider: the owner's `gpt5.6-sol` provider (DEC-051); the provider contract is documented in E1 and the integration stays isolated behind an interface.
- Publication and material-update dates are visibly displayed and tracked (DEC-113); daily cadence may pause for post-launch stability and corrective work (DEC-141); the owner remains accountable with pause/disable controls for automation (DEC-097).
- No persistent staging environment or public beta; Vercel preview deployments are temporary validation mechanisms (DEC-096).

## 2. Non-goals

- No publication, no repository writes, no GitHub Actions execution, no account creation, no API calls, no installs or builds during research (plan §4.1).
- No implementation or scaffolding; this brief selects and compares architectures and leaves implementation to the approved design phase (DEC-057, DEC-060).
- No benchmark program, corpus, or comparative quality report (DEC-066).
- No reintroduction of the removed Guinevere/OpenClaw runtime, agents, BullMQ, Redis, or decision-engine infrastructure (DEC-016).
- The provider's exact request/response behavior is out of scope here; it is the E1 documentation contract's subject.

## 3. Research questions (plan §7.5, E2)

1. Which repository-backed architecture lets automation create validated MDX changes and trigger the normal preview/build/deployment path (DEC-049), without a persistent staging environment (DEC-096)?
2. How are schema validation and MDX component allowlisting enforced so that generated content (executable build input) cannot break the build or render arbitrary code (DEC-049)?
3. How are the DEC-048 blocking quality gates implemented so they fail closed, and what happens when a gate fails?
4. How are scheduling (one trilingual set per day), audit logs, pause/kill-switch, rollback, and correction implemented?
5. How are provider secrets handled so they never appear in MDX, logs, workflow artifacts, or client-side code (DEC-051)?
6. What do the ≥2 viable architectures cost operationally, and what are their privacy and security implications (DEC-055)?

## 4. Method

- Read the decision log, both specs, both review/correction reports, and the plan in full.
- Collected read-only legacy evidence from `papyr-reference/`: the existing CI workflow (the "normal build path"), the absence of any MDX/blog support in the legacy frontend, and the removed OpenClaw/Guinevere automation history (evidence only, DEC-016).
- Verified current official documentation for MDX-in-Next.js options, GitHub Actions controls, and Vercel build/preview behavior. All URLs verified live (HTTP 200) on 2026-07-31; package versions pulled from the npm registry on 2026-07-31.
- No prohibited action was performed (Section 12).

## 5. Evidence

### 5.1 Legacy baseline (read-only evidence from `papyr-reference/`)

| Evidence | Location | Relevance |
|---|---|---|
| Normal build path: frontend CI runs format check, ESLint, Vitest, then `next build` on push/PR to main/develop | `.github/workflows/ci.yml:3-11` (triggers), `:13-85` (frontend lint/test/build jobs) | The pipeline must route publication through this path (DEC-049); the content bot's commits/PRs must pass it |
| Frontend deploy model: Vercel git integration for the frontend; backend deploys via `deploy-vps.yml` (GHCR image, smoke test, rollback) on backend-path pushes | `.github/workflows/deploy-vps.yml:5-19,20-210` | Blog is frontend content; the frontend build path is the publication path; backend workflow is evidence of the repo's existing rollback pattern |
| Legacy frontend has no MDX/blog: no MDX or content dependencies in `frontend/package.json:23-34`; empty `frontend/next.config.ts:1-7`; sitemap has no blog URLs (`frontend/src/app/sitemap.ts:5-19,21-47`) | above | The rebuild introduces MDX as a new capability; no legacy MDX conventions to preserve |
| Historical automation (removed per DEC-016): OpenClaw "fully autonomous" content publication (`docs/29_Papyr_OpenClaw_v1.0.md:270`), planned blog in "Fase 5" (`:158,173`), SEO pipeline agent "2-4 articles/week" (`:244`), `content-generator.ts`/`publisher.ts`/`blog-api.ts` (`:627-629,701`), OpenAI-compatible chat-completions response shape (`:923`); Guinevere report-only content mode (`guinevere/soul/SOUL.md:13,40`; `guinevere/soul/HEARTBEAT.md:38-53,113`) | above | Evidence of the owner's prior automation ambitions and of a prior report-only/fully-autonomous split; does not bind the rebuild (DEC-016) |

### 5.2 Current MDX-in-Next.js options (official sources, versions as of 2026-07-31)

| Option | Latest version (npm, 2026-07-31) | License | Official source (URL, access date) | Maintenance status and allowlisting mechanism |
|---|---|---|---|---|
| `@next/mdx` | 16.2.12 | MIT | `https://nextjs.org/docs/app/guides/mdx` (200); `https://nextjs.org/docs/app/api-reference/file-conventions/mdx-components` (200); repo `vercel/next.js` package `next-mdx` | First-party Next.js plugin; App Router requires an `mdx-components.js|tsx` file, which is the documented component-mapping (allowlist) point; MDX compiled at build time, so malformed MDX or unknown components fail the build (fail-closed by construction) |
| `next-mdx-remote` | 6.0.0 | MPL-2.0 | npm registry (repository `hashicorp/next-mdx-remote`) | Runtime-rendered remote MDX; component allowlisting via the `components` prop; designed for remote/string MDX rather than repository-local build-time content |
| `contentlayer` | 0.3.4 | MIT | `https://github.com/contentlayerdev/contentlayer` (200); README (main branch, accessed 2026-07-31): "Contentlayer is no longer maintained due to lack of funding" | Unmaintained; not suitable for a new pipeline (DEC-056 primary-source status check) |
| `velite` | 0.4.0 | MIT | npm registry (repository `zce/velite`) | Maintained content SDK alternative; schema-validated content into typed data; not first-party Next.js |

Assessment: `@next/mdx` is the only first-party, maintained, build-time option for the existing Next.js 16 App Router baseline (legacy `frontend/package.json:29` pins `next: 16.2.4`; `@next/mdx` 16.2.12 matches the Next 16 line). Its `mdx-components` file convention provides the strict component allowlist DEC-049 requires, and build-time compilation makes malformed MDX a build failure rather than a runtime risk.

### 5.3 Automation controls (official GitHub documentation, all HTTP 200 on 2026-07-31)

| Control | Official source | Relevance to the pipeline |
|---|---|---|
| Scheduled workflow trigger (`schedule`, cron) | `https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows` | Daily scheduling of generation runs (UTC-timezone decision needed for "one set per day") |
| Secrets in GitHub Actions | `https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions` | Provider credential storage outside the repository (DEC-051, DEC-176) |
| Environments with protection rules | `https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment` | Production-sensitive secrets gated by environment; supports the kill switch and manual override (DEC-097) |
| Branch protection and required status checks | `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches` | Merge-only-with-checks policy so every published article set passes CI gates |
| Merging pull requests (auto-merge) | `https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request` | Automatic merge of gate-passing content sets |
| Vercel preview deployments and builds | `https://vercel.com/docs/deployments/preview-deployments` (200); `https://vercel.com/docs/builds` (200) | PR preview as the temporary validation mechanism (DEC-096); production build on merge to main |

## 6. Alternatives (DEC-055)

### 6.1 Architecture A — Scheduled content-bot workflow with gate-passing PR and auto-merge (recommended)

The pipeline runs on a schedule in GitHub Actions:

1. A scheduled workflow (daily, at a fixed UTC time) reads the topic inventory and the pause flag, and if publication is due, calls the provider (via E1's documented contract) to research, generate, localize (EN/ES/ID), and structure the article set.
2. All DEC-048 gates run inside the workflow or in CI (factual support, duplication/cannibalization against the MDX corpus, search intent, originality, language quality, metadata, internal links, unsafe claims, policy vocabulary, malformed MDX/schema). Any gate failure cancels the set for that day (DEC-124).
3. A passing set is written as MDX into a branch and opened as a pull request with a deterministic title/body (topic ID, dates, gate manifest).
4. Repository CI (the existing frontend build path extended with MDX schema/allowlist/build checks) runs against the PR. Branch protection requires these checks. Auto-merge merges the PR to main.
5. Vercel builds the production site from main; the PR preview deployment serves as the temporary validation artifact (DEC-096).

Trade-offs: strong audit trail (PR + git history + workflow logs); merge is the single controlled publication point; rollback is a `git revert` of the merge commit; preview isolation is free (Vercel PR previews); kill switch is a combination of disabling the workflow, an environment protection rule, and a repository pause flag read by the workflow. Weaknesses: slightly more moving parts than direct commit; requires branch protection and a scoped GitHub token; auto-merge policy must be configured carefully (required checks, no bypass). Cost/operational impact: GitHub Actions scheduled minutes plus Vercel preview builds; privacy/security: provider secret lives only in GitHub secrets/environments, never in the repo, MDX, or artifacts; content is generated into repository files that are public in the repo's normal content flow (consistent with publishing to the public site).

### 6.2 Architecture B — Direct-commit workflow (no PR)

The scheduled workflow generates, gates, and commits the MDX directly to main (or pushes to main). Vercel builds from main.

Trade-offs: simplest topology; the cadence is exact. Weaknesses: no PR review point; a flawed generation run reaches main (though build failure still blocks deploy); audit is git log + workflow run only; branch protection offers less protection (required status checks on push); the human correction path is less obvious. Privacy/security posture is otherwise identical to A. Cost/operational impact: lower (no PR management), but weaker fail-closed properties around reviewable change.

### 6.3 Architecture C — External scheduler (VPS cron or third-party service) pushing content

A scheduler outside the repository (VPS cron, external cron service) invokes generation and pushes commits/PRs.

Trade-offs: decouples scheduling from the repo, but reintroduces a production dependency outside the repo's automation, conflicts with the "no separate runtime" posture of the retained topology, adds a credential to a second surface (DEC-176, DEC-097), and complicates the kill switch. Rejected: it does not improve on A while increasing operational and secret surface.

### 6.4 Cross-cutting design points (apply to the recommended architecture)

| Concern | Design point | Evidence/decision basis |
|---|---|---|
| Schema and component allowlist | MDX frontmatter validated against a strict schema (fields: topic ID, locale, slug, title, description, published/updated dates, hreflang set, internal-link list, gate manifest) via a typed validator; only a fixed allowlist of components (defined in `mdx-components.tsx` for `@next/mdx`) may appear; unknown JSX or components fail the build | `@next/mdx` `mdx-components` file convention (5.2); DEC-049 "strict controls because generated content is executable build input" |
| Fail-closed quality gates | Each DEC-048 gate is an executable check; a failing gate marks the set unpublished and the workflow exits nonzero; no partial trilingual set is ever created (DEC-124); generated content must not include arbitrary components, raw HTML where disallowed, or external scripts | DEC-048, DEC-124 |
| Preview/build isolation | PR preview deployment validates the rendered set; main-merge production build is the only publication step; a failed content build never affects the currently deployed site (Vercel keeps the last healthy production build) | DEC-049, DEC-096; Vercel builds docs (5.3) |
| Audit trail | Git history (author = bot identity, message includes topic ID and gate manifest), workflow run logs (redaction-safe), and the MDX frontmatter gate manifest; no secrets, filenames-of-user-data, or document contents in logs (DEC-025, DEC-175) | DEC-048, DEC-049 |
| Pause and kill switch | (1) Repository pause flag read by the workflow; (2) workflow disabled via Actions UI; (3) environment protection rule on the deployment environment; (4) automatic pause thresholds: build failure, quality-gate regression, provider anomalies, or widespread indexing problems (DEC-053); cadence may also pause for post-launch stability work (DEC-141) | DEC-053, DEC-097, DEC-141 |
| Rollback | Documented `git revert` of the offending merge commit + rebuild (frontend), consistent with the legacy backend's "capture previous image and roll back on failed smoke" pattern (`.github/workflows/deploy-vps.yml:132-148,186-196`); full S3 restore remains disaster recovery, not the ordinary content rollback path (DEC-178) | DEC-178 (by analogy), DEC-049 |
| Correction | In-place MDX edits advance `dateModified` only for substantive material changes (DEC-113); trivial formatting/deployment-only changes do not; EN/ES/ID counterparts keep independent dates | DEC-113 |
| Secret handling | Provider credential in GitHub Actions secrets (or an environment secret), never in MDX, logs, workflow artifacts, or client-side code (DEC-051); local dev uses the owner's protected environment configuration (DEC-176); an audit scan gate rejects any PR whose diff or logs contain a secret-shaped token | DEC-051, DEC-176 |

## 7. Recommendation

**Recommendation (not an accepted decision; DEC-054, DEC-057):** adopt Architecture A (scheduled content-bot workflow with gate-passing PR and auto-merge) with `@next/mdx` as the MDX renderer, a strict typed frontmatter schema, the `mdx-components.tsx` allowlist, the DEC-048 gate suite as required CI checks under branch protection, and the cross-cutting controls in Section 6.4. The provider integration is a thin adapter behind an interface (DEC-051) whose contract is E1's matrix. This architecture satisfies every E2 research question: it routes publication through the normal build path (DEC-049), fails closed, keeps full audit and rollback in git, isolates preview from production without a persistent staging environment (DEC-096), and keeps the owner's pause/kill-switch and accountability controls (DEC-097). Architecture B remains a documented fallback if the owner later prefers the simplest topology; Architecture C is rejected.

## 8. Measurable acceptance criteria (verifiable without a benchmark program; DEC-066)

1. A generated article set in which any DEC-048 gate fails (factual, duplication/cannibalization, search intent, originality, language, metadata, links, unsafe claims, policy, schema/MDX) remains unpublished: the workflow exits nonzero and no merge occurs. Verified with functional fixture tests of each gate.
2. Every published article exists as a validated MDX file under a locale-prefixed path (`<locale>/blog/<slug>`) with complete frontmatter, and renders only allowlisted components. Verified by schema validation and build success.
3. The pipeline produces at most one coordinated trilingual EN/ES/ID set per calendar day, verifiable from git history dates and workflow runs (DEC-124).
4. A merge to main triggers the frontend build; a broken MDX file or an unknown JSX component fails the build before any deploy, and the deployed site remains the last healthy production build (DEC-049).
5. Rollback is a documented `git revert` + rebuild procedure exercised in a recovery drill (functional verification, not a benchmark).
6. The kill switch halts publication within one scheduled cycle (verified by a workflow-run test with the pause flag set and the workflow disabled).
7. No provider secret, API key, or credential-shaped token appears in committed MDX, workflow logs, or build artifacts (verified by an automated secret-scan gate on every content PR).
8. Correction behavior honors DEC-113: `dateModified` advances only for substantive material changes (verified by fixture tests of the date-update rule).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Dependency on E1:** the pipeline's generation stage cannot be designed in detail until the owner supplies the `gpt5.6-sol` provider documentation (E1 matrix). The architecture above is provider-agnostic behind the adapter.
2. **GitHub vs GitLab:** the design assumes GitHub Actions because the legacy repository's automation is GitHub-based (`.github/workflows/`). If the rebuild repository is hosted elsewhere, the same architecture maps to the equivalent CI/CD controls.
3. **Auto-merge policy:** exact branch protection settings (required checks list, bypass rules, bot identity) are implementation details for the approved design phase, not research conclusions.
4. **Cadence timezone:** "one topic per day" requires an explicit daily UTC boundary to avoid double or missed days; this is a design choice for the approved implementation plan (DEC-124).
5. **Historical contrast:** the removed OpenClaw stack was "fully autonomous without founder approval" (`docs/29_Papyr_OpenClaw_v1.0.md:270`); DEC-048 now accepts full automation but with blocking gates, audit, pause, rollback, and owner accountability (DEC-097). The rebuild deliberately adds the gates the legacy design lacked.
6. **Vercel deployment configuration** for the rebuild is not yet defined in this repo; preview-deployment behavior is assumed per Vercel's documented git integration.

## 10. Dependencies and cross-track interfaces

- **E1** supplies the provider contract (base URL, auth, schema, structured outputs, tool use, rate limits, cost, context, retry, retention, availability).
- **E3** supplies the launch topics and the post-launch topic inventory/pipeline that the scheduler consumes.
- **B4** supplies slugs, hreflang, canonicals, sitemap, and legacy-URL rules that the MDX frontmatter and metadata gates must enforce.
- **D5/C5** define the prohibited-data register and monitoring/alerting that the pause thresholds use (DEC-025, DEC-175, DEC-182).
- **X1/X2** record this brief's mapping and its interfaces to E1, E3, B4, C5, and D5.

## 11. Source-date log and evidence-completeness notes

- All web sources accessed and verified live (HTTP 200) on 2026-07-31. Package versions and licenses pulled from the npm registry on 2026-07-31.
- Legacy citations verified against `papyr-reference/` content on 2026-07-31 (paths and lines in Section 5.1).
- Evidence-completeness caveat: GitHub Actions and Vercel documentation pages were verified live and summarized from their canonical content; deeper feature pages (e.g., every merge-protection option) were not re-fetched in full.

## 12. Prohibitions-compliance statement

- No publication, no repository writes, no GitHub Actions execution, no installs, builds, servers, VPS access, deployment, account creation, or provider API calls were performed.
- `papyr-reference/` was only read; read-only `git -C papyr-reference status --porcelain` returned empty output with exit 0 before and after this brief.
- No source, spec, or decision file was modified. The only files created by this brief are this deliverable.
- No benchmark program or comparative quality report was created (DEC-066).
- A chat-only summary is insufficient; this file is the primary deliverable.
