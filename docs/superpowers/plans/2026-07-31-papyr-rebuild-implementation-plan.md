# Papyr Rebuild Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild Papyr as a production-ready international PDF-tools product with five launch tools in EN, ES, and ID, delivered through an execution-ready sequence of gated phases and TDD tasks.

**Architecture:** A monorepo containing a Next.js App Router frontend (Vercel), a FastAPI backend behind Nginx on a VPS, Redis as the durable minimal-metadata task queue, one bounded PDF-processing worker (DEC-189), and Cloudflare R2 as the temporary object store with active deletion plus a lifecycle safety net. Browser-first hybrid processing routes to the server under explicit rules (DEC-011, DEC-015, DEC-030, DEC-065). The plan preserves the approved visual baseline (DEC-143), the five-tool catalog (DEC-010), trilingual launch completeness (DEC-027, DEC-115, DEC-118), the one-hour server retention ceiling (DEC-013, DEC-070), and the manual owner-authorized deployment boundary (DEC-160, DEC-177).

**Tech Stack:** Next.js App Router on Vercel; React; Tailwind CSS v4; FastAPI; a minimal custom queue over Redis Streams consumer groups (approved by DEC-199, R-28); Ghostscript as an unmodified subprocess (DEC-195, approved); pdf-lib (Merge/Split browser happy path and browser JPG-to-PDF support), pikepdf (qpdf) (Merge/Split server fallback and sanitization), img2pdf plus Pillow (JPG-to-PDF server), pypdfium2 (PDF-to-JPG server), pdf.js (browser rendering and page count), and platform `createImageBitmap` (WebP decode) (all approved by DEC-199, R-28, with the documented risks, scope boundaries, material conditions, and fallbacks in force); Docker Compose; Nginx; Cloudflare R2; CI provider per R-02 (proposal: GitHub Actions, CI core gate only); Vitest, Playwright, Pytest, Ruff.

## Global Constraints

The following constraints are copied from the approved decision baseline and both specifications. Every task in this plan implicitly includes them.

- **No implementation without plan approval.** DEC-060 and DEC-197: this plan is documentation. Execution starts only after the owner reviews and explicitly approves it.
- **No benchmark program.** DEC-066: no benchmark corpora, matrices, comparative performance studies, quality-score programs, VPS benchmark workloads, or benchmark reports. All numeric values are conservative design or safety choices adjusted from production observability. Normal functional tests, integration tests, security checks, accessibility checks, and CI verification are required and are not benchmarks.
- **Five-tool launch scope.** DEC-009, DEC-010: Compress PDF, Merge PDF, Split PDF, JPG to PDF, PDF to JPG. Deferred legacy tools (rotate, protect/unlock, watermark, sign, OCR, PDF to Word, PDF to Excel) are post-launch candidates only (DEC-094), never launch scope.
- **Trilingual launch completeness.** DEC-027, DEC-115, DEC-118, DEC-121: all five tools and essential supporting surfaces must be complete and consistent in EN, ES, and ID before launch; one incomplete tool blocks the public launch (DEC-027).
- **No accounts.** DEC-012: anonymous, no-sign-up usage; no authentication, profiles, cloud history, saved files, or cross-device sync.
- **Free forever core.** DEC-132, DEC-133, DEC-134, DEC-138: core public tools free forever; no paid fast lane; fair queuing and adaptive fair-use controls only.
- **Hybrid browser-first processing.** DEC-011, DEC-015, DEC-030, DEC-065: browser-first with automatic server fallback under measured-capability rules; Compress is server-side by default; at most one server transition per job; security-policy failures fail closed.
- **One active worker at launch.** DEC-189: one PDF-processing worker executing one concurrent job; queueing, fairness, timeouts, and safety caps in force; added concurrency needs capacity evidence and explicit owner approval.
- **One-hour server retention ceiling.** DEC-013, DEC-067, DEC-070, DEC-075, DEC-166: absolute one-hour maximum from upload receipt; active deletion by the application plus an R2 lifecycle safety net; expiry never extended.
- **No document-sensitive data outside temporary processing.** DEC-025, DEC-036, DEC-042, DEC-072, DEC-174, DEC-175, DEC-180: file contents, filenames, passwords, signed URLs, object keys, previews, and extracted content are prohibited from logs, analytics, persisted task records, backups, and Telegram alerts.
- **Sanitization of active PDF content.** DEC-090, DEC-091, DEC-192: Merge, Split, and Compress outputs have active content removed or neutralized with category-level disclosure; Merge and Split active-content inputs route to the server sanitization path; no browser sanitization engine; affected jobs fail closed when the scanner or sanitization path is unavailable.
- **Threat blocking.** DEC-088: files classified as threats to infrastructure are blocked, never processed or returned, with safe localized rejection.
- **Passwords only when required.** DEC-036, DEC-064, DEC-074: detected encrypted PDFs request a password only when needed, per locked file for Merge; memory-only handling; distinct wrong-password errors.
- **Signed R2 downloads.** DEC-170: server results download through short-lived signed R2 URLs; URL expiry never exceeds the authoritative absolute expiry.
- **Existing visual baseline.** DEC-143: the rebuild looks and feels like the existing Papyr website in `papyr-reference/`; changes limited to consistency, responsiveness, accessibility, localization resilience, truthful states, corrected interactions, performance, and removal of documented defects D1-D13.
- **Non-intrusive advertising only.** DEC-018, DEC-131, DEC-151, DEC-190: Adsterra banner and native formats only, without prior consent in all launch regions as an accepted risk; no compliance claims; no popunders, interstitials, social bars, in-page push, or forced redirects; ads never obstruct upload, processing, result, download, consent, or navigation.
- **Analytics boundaries.** DEC-025, DEC-126: detailed product events, funnels, attribution, performance, and sanitized errors; no session replay on document workflows; no fingerprinting; no public usage counters.
- **Manual deployment boundary.** DEC-160, DEC-177, DEC-097: CI builds, tests, and scans but never changes production; each production deployment requires explicit owner authorization, pre-deployment verification, rollback readiness, and post-deployment smoke checks.
- **Secrets.** DEC-176, DEC-193, DEC-196: runtime secrets live in protected VPS environment configuration; legacy credentials rotated before production use; gateway API keys stored only in protected server-side or automation secrets.
- **Supported browsers.** DEC-031: latest two major versions of Chrome, Edge, Firefox, and Safari on desktop; current Safari on iOS/iPadOS; Chrome on Android; progressive-enhancement fallbacks required.
- **WCAG 2.2 AA target.** DEC-062: automated checks plus representative manual keyboard and assistive-technology testing; known exceptions documented; no certification claims.
- **One-month target.** DEC-100, DEC-103: the relaunch targets one month; launch is delayed rather than cut or degraded; schedule risk reported early.
- **No newsletter at launch.** DEC-107, DEC-109: no subscription or email-marketing infrastructure in launch scope.
- **No competitor-comparison pages.** DEC-128: no alternative, versus, or competitor-comparison landing pages at relaunch.
- **Legacy URL dispositions.** DEC-127, DEC-194, DEC-114: every legacy URL gets an explicit disposition; deferred tool URLs return a localized 410 Gone by default; targeted redirects only on credible traffic or intent evidence; retained pages updated.
- **Gateway identity.** DEC-193, DEC-196: blog automation uses the owner OpenAI-compatible gateway at `https://router.budgezen.com/v1`, exact JSON model identifier `mypapyr`, and `Authorization: Bearer <API_KEY>` from protected secrets only; no authenticated call is authorized by any planning artifact.
- **Compress engine.** DEC-195: the official unmodified open-source Ghostscript executable as a separate hardened server-side subprocess with safety flags including `-dSAFER`; AGPL notices preserved; focused license review before launch; permissive or commercial fallback if the review outcome is unacceptable.
- **Open choices are named decisions.** This plan records open choices as named owner-decision items R-01 through R-28 with stop conditions (Section 6), following the specification convention (arch §26.1). Resolved items carry their resolution status in the register. It contains no TODO, TBD, FIXME, or placeholder tokens.
- **Rebuild repository root (DEC-198).** The workspace root `<workspace-root>` is the rebuild repository root (R-01 resolved). `papyr-reference/` is a separate nested read-only legacy clone excluded from the rebuild repository; its nested `.git` is never touched by any repository operation. No git operation is authorized by this plan.
- **Engine and queue matrix (DEC-199).** The R-28 matrix is approved as presented: Redis Streams consumer groups, pdf-lib, pikepdf (qpdf), img2pdf plus Pillow, pypdfium2, pdf.js, and platform `createImageBitmap`. Every documented accepted risk, scope boundary, material condition, fallback, and dependency and version review stays in force. Approval of the matrix is not implementation authorization.

---

## 1. Status and Authority

- **Governing decision:** DEC-197 approves the revised Product and UX and Technical Architecture specifications for implementation planning only.
- **Plan-approval gate:** product implementation, dependency installation, repository creation, commits, pushes, VPS access, infrastructure changes, deployment, provider authentication, and remote operations all remain blocked until the owner reviews and explicitly approves this implementation plan (DEC-060, DEC-057, DEC-197).
- **Sources:** decision baseline DEC-001 through DEC-201 in `papyr-rebuild-decisions.md` (DEC-198, DEC-199, DEC-200, and DEC-201 appended after DEC-197 record the repository root, the engine and queue matrix, the 90-day measures, and the final R-27 numeric targets); both approved specifications under `docs/superpowers/specs/`; the completed cross-domain reconciliation `audit-outputs/research/reconciliation-report.md` (X2); the source and decision index `audit-outputs/research/source-and-decision-index.md` (X1); the brief verification `audit-outputs/research/research-brief-verification.md` (PPR-VER-001).
- **Precedence:** decisions, then the two specifications, then audit and research evidence, then the read-only legacy reference (arch §1.4).
- **Plan-approval precondition (DEC-024, resolved by DEC-200 and DEC-201):** the owner defined the 90-day measures and baseline windows recorded in R-27 (job success at or above 98 percent; system failure at or below 2 percent; uptime at or above 99.5 percent; Core Web Vitals passing for at least 75 percent of visits; completed downloads at or above 85 percent of successful jobs; organic traffic growth greater than zero percent versus the first-28-day baseline at day 90; meaningful usage across all five tools; p50 and p95 processing and queue latency per tool; baseline is the first 28 post-launch days and evaluation is at day 90). DEC-200 approved these measures; DEC-201 supplies the exact numeric fields it left open: p95 queue wait at or below 60 seconds per tool, p95 server processing at or below 180 seconds per tool, p50 observed and reported per tool without a separate target, and each launch tool contributing at or above 5 percent of total completed downloads during days 29 through 90. Every DEC-024 exact-numeric field now has a value; the precondition is fully met and no field remains open. Plan approval itself remains pending the owner's explicit decision, and no phase may start before that approval.
- **Approval status:** this plan remains unapproved. Product implementation, dependency installation, repository creation, commits, pushes, VPS access, infrastructure changes, deployment, provider authentication, and remote operations all remain blocked until the owner reviews and explicitly approves it (DEC-060, DEC-057, DEC-197); DEC-198 through DEC-201 resolve the R-01, R-28, and R-27 dispositions only.

## 2. How to Use This Plan

1. An execution agent starts at Phase 0 and proceeds in phase order. Phases are independently reviewable: each has entry criteria (gate), exit criteria (gate), and a review boundary.
2. Every implementation task uses the TDD sequence: write the failing test, verify it fails, write the minimal implementation, verify it passes, then stop at a review and commit boundary. The test is the contract.
3. Where the approved specs resolve behavior, tasks specify exact file paths, interfaces, verification commands, and expected outcomes. Where the specs intentionally leave exact values open (per-tool limits, engine profile thresholds, provider selections), the consuming task is preceded by a resolution task in Section 6 that states what must be decided, who decides it, the evidence to consult, and a stop condition. The plan never invents values for open choices.
4. Category-A research recommendations (X2 Section 4) are design inputs only and remain subject to owner approval (DEC-057). Resolution tasks carry them as proposals with the governing decision cited. The exception is the R-28 engine and queue matrix, which the owner approved by DEC-199; all other category-A recommendations remain proposals until their resolution items are disposed.
5. Each task ends at a "Review and commit boundary". The boundary describes the exact atomic commit unit (the files that belong together and a suggested message subject) that will be created once the repository exists and the owner has authorized git operations at Phase 0. A reviewer gate sits at each boundary: a task is not done until its tests pass and the boundary is reviewed.
6. Phase-level verification commands are listed per phase. Global verification requirements (the CI core gate, DEC-177) are defined in Phase 1 and referenced afterward.
7. Separately gated actions (VPS access, deployment, provider accounts, legal review, gateway access, git remote operations) are listed in Section 7. No task in this plan performs them; tasks only prepare the artifacts those gated actions require.

## 3. Proposed Rebuild Repository Tree

Per DEC-198, the workspace root `<workspace-root>` is the rebuild repository root (resolution item R-01 resolved). `papyr-reference/` remains a nested read-only legacy clone excluded from the repository. Paths in this plan are relative to the workspace root. The `docs/` directory already contains the canonical specifications under `docs/superpowers/specs/` and this plan under `docs/superpowers/plans/`; the migration task in Phase 0 records these as governed project records (DEC-006, DEC-026, DEC-198).

```
<workspace-root>                workspace root (R-01 resolved by DEC-198; rebuild repository root)
├── frontend/                         Next.js App Router workspace (Vercel deployable)
│   ├── src/app/
│   │   ├── [locale]/                 locale-prefixed route group (en, es, id)
│   │   │   ├── layout.tsx            locale-aware shell
│   │   │   ├── page.tsx              homepage
│   │   │   ├── compress-pdf/         five tool routes (EN slugs; ES/ID per R-15)
│   │   │   ├── merge-pdf/
│   │   │   ├── split-pdf/
│   │   │   ├── jpg-to-pdf/
│   │   │   ├── pdf-to-jpg/
│   │   │   ├── privacy/              legal surfaces
│   │   │   ├── terms/
│   │   │   ├── cookies-advertising/
│   │   │   ├── contact/
│   │   │   ├── status/
│   │   │   ├── roadmap/
│   │   │   └── blog/                 MDX content surface
│   │   ├── sitemap.ts                per-locale sitemap with hreflang
│   │   ├── robots.ts
│   │   └── globals.css               design tokens (D4, D5 corrected)
│   ├── src/components/               Navbar, Footer, dropzone, state cards, catalog, shared UI
│   ├── src/lib/                      pdfUtils, naming, routing, capabilities client, analytics
│   ├── src/hooks/                    useTaskPolling (replaces legacy useAsyncTask)
│   ├── src/i18n/                     locale messages, ICU MessageFormat usage (B3)
│   ├── e2e/                          Playwright suites, fixtures, helpers
│   └── package.json
├── backend/                          FastAPI workspace (VPS deployable)
│   ├── app/
│   │   ├── main.py                   app shell, router mounting, /health
│   │   ├── config.py                 frozen Settings (replaces legacy utils/config.py)
│   │   ├── routers/                  versioned /api/v1 endpoints
│   │   ├── services/                 per-tool engine services
│   │   ├── queue/                    Redis Streams consumer groups (R-28, DEC-199), worker loop, fairness
│   │   ├── tasks/                    task state machine, session tokens, cleanup coordinator
│   │   ├── security/                 validation, sanitization, scanner client, threat classes
│   │   └── utils/                    r2, logging, naming, zip
│   ├── tests/                        pytest suites and fixtures
│   ├── Dockerfile.production         hardened multi-stage image
│   ├── requirements.txt
│   └── ruff.toml
├── deploy/                           Docker Compose stack, Nginx, env templates
│   ├── docker-compose.yml            nginx, api, redis, workers, scanner (DEC-162)
│   ├── nginx/conf.d/                 production and default hosts
│   ├── .env.production.example       non-secret template (mode-600 install per DEC-176)
│   └── runbook-vps.md                canonical operations runbook (replaces the legacy `papyr-reference/docs/runbook-vps.md` as the operating reference; the legacy file is never modified)
├── docs/                             canonical documentation (superpowers specs and plans; migrated decision log record per DEC-006, DEC-026, DEC-198)
├── scripts/                          dependency-free verification and configuration-check scripts
├── .github/workflows/                CI core gate only, contingent on R-02 (DEC-177, DEC-160); no auto-deploy
├── .gitignore                        excludes papyr-reference/, local caches, and secrets
├── papyr-reference/                  read-only legacy clone (DEC-099, DEC-159, DEC-198); excluded from the rebuild repository; never modified; its nested .git is never touched
├── audit-outputs/                    governed discovery records (DEC-198); preserved unless a later explicit decision changes the tracking policy
├── papyr-rebuild-decisions.md        living decision log (governed record, DEC-006, DEC-198)
└── AGENTS.md                         orchestrator rules (governed record)
```

Notes:

- `papyr-reference/` is a nested read-only legacy clone. It is excluded from the rebuild repository (for example through `.gitignore`), is never modified, and its nested `.git` is never targeted by any repository command (DEC-099, DEC-159, DEC-198, arch §3.3).
- `audit-outputs/`, `papyr-rebuild-decisions.md`, and the canonical `docs/superpowers/` specs and plans are governed project records preserved under DEC-198 unless a later explicit decision changes the tracking policy.
- Generated SBOMs, vulnerability-scan output, and test reports are CI artifacts, not maintained source documents (DEC-026).

## 4. Phase Architecture and Dependency Ordering

| Phase | Name | Depends on | Exit gate |
|---|---|---|---|
| P0 | Pre-execution prerequisites and owner gates | plan approval | repository exists at the workspace root per R-01 (DEC-198), branch strategy set, resolution register dispositions recorded |
| P1 | Monorepo foundation and CI core gate | P0 | lint, unit, build, and security-scan jobs pass on the wired skeleton |
| P2 | Frontend shell, locale routing, and canonical catalog | P1 | shell, homepage, and catalog verified across EN, ES, and ID with passing unit and E2E tests |
| P3 | Backend core and early security prerequisites: settings, queue, worker, task model, R2, cleanup, API contract, threat classification, sanitization | P1 | API admission, status, and download integration tests pass against a real Redis and R2 test fixture; SEC-01 and SEC-02 prerequisites verified |
| P4 | Five tools: shared foundations and per-tool flows | P2, P3 | each tool passes its browser, server, routing, and E2E acceptance tests in all three locales |
| P5 | Security and hardening: scanner, container hardening, Nginx enforcement, dependency maintenance | P3 | scanner fail-closed behavior, container hardening, and Nginx enforcement verified |
| P6 | Privacy, analytics, advertising, and support | P2, P4 | leakage tests, schema validation, ad placement checks, and support flows pass |
| P7 | Monitoring, status, backups | P3, P5 | status derivation, alert relay, backup, and restore-drill procedures verified |
| P8 | SEO and URL migration | P2, P4 | redirect map, 410 dispositions, hreflang, sitemap, and locale-less entry verified |
| P9 | Content, legal, and blog | P2, P4, P8 | legal review gate and gateway-documentation gate passed; 15 launch articles verified |
| P10 | Pre-launch verification and launch | all phases | five-tool trilingual launch gate passes; activation checklist complete; owner authorizes launch |
| P11 | Post-launch operations | P10 | 90-day dashboard live; cadences running; next-tool planning initiated |

Every phase ends with a review boundary. No phase may begin until its predecessor's exit gate is satisfied. Gates are owner-reviewed checkpoints, not automated pass-throughs (DEC-057).

## 5. Task Index

Task IDs are stable. Prefixes: `PR` (prerequisites), `FD` (foundation), `SH` (shell), `BE` (backend core), `TL` (tool), `SEC` (security), `PT` (privacy, ads, support), `OP` (operations), `SEO` (SEO and migration), `CT` (content, legal, blog), `VL` (verification, launch), `PO` (post-launch). Resolution tasks carry IDs R-01 through R-28 and live in Section 6.

| Task | Deliverable | Consumes | Produces for |
|---|---|---|---|
| PR-01 | Repository creation and branch strategy (owner-gated) | plan approval, R-01 disposition (DEC-198), R-02 | all |
| PR-02 | Canonical documentation baseline at repository root | PR-01 | all |
| PR-03 | Resolution register dispositions log | R-01..R-28 dispositions | all |
| FD-01 | Frontend workspace scaffold | PR-01 | SH, TL |
| FD-02 | Backend workspace scaffold | PR-01 | BE |
| FD-03 | Deploy workspace scaffold | PR-01 | BE, SEC, OP |
| FD-04 | CI core gate skeleton | FD-01..FD-03 | all |
| FD-05 | Root tooling conventions and scripts | FD-01 | all |
| SH-01 | Locale routing and middleware | FD-01 | SH-02..SH-06, SEO |
| SH-02 | Design tokens and global styles | FD-01 | SH, TL |
| SH-03 | Root shell, layout, skip link, metadata | SH-01, SH-02 | all |
| SH-04 | Canonical tool catalog | FD-01 | SH-05, SH-06, TL, SEO |
| SH-05 | Navbar (categorized, language selector) | SH-03, SH-04 | all |
| SH-06 | Footer | SH-03, SH-04 | all |
| SH-07 | Homepage | SH-04, SH-05 | all |
| SH-08 | Supporting surface shells (legal, contact, status, roadmap, blog) | SH-01 | P6, P7, P8, P9 |
| BE-01 | Backend settings and logging | FD-02 | all BE |
| BE-02 | Input validation library (PDF and image) | BE-01 | BE-08, TL, SEC |
| BE-03 | R2 client with key hygiene and signed URLs | BE-01 | BE-06..BE-08, TL |
| BE-04 | Redis minimal task store | BE-01 | BE-05, BE-06 |
| BE-05 | Queue, worker loop, and fair scheduling | BE-04 | BE-06, TL |
| BE-06 | Task state machine and status API | BE-04, BE-05 | TL, SH |
| BE-07 | Cleanup coordinator and lifecycle safety net | BE-03, BE-04 | TL, OP |
| BE-08 | Capability and limits contract API | BE-02 | TL, SEO |
| BE-09 | Signed download authorization and refresh | BE-03, BE-06 | TL |
| BE-10 | Fair-use and rate-limit enforcement | BE-04, BE-08 | SEC, OP |
| SEC-01 | Threat classification and fail-closed matrix (early security prerequisite) | BE-02, BE-08 | TL, PT |
| SEC-02 | Sanitization pass for PDF-producing outputs (early security prerequisite) | BE-02 | TL-02..TL-04 |
| TL-01 | Shared tool foundations (uploader, states, download, reset) | SH, BE-06, BE-08 | TL-02..TL-06 |
| TL-02 | Compress PDF | BE-03, BE-05, BE-06, SEC-01, SEC-02 | all |
| TL-03 | Merge PDF | TL-01, SEC-01, SEC-02 | all |
| TL-04 | Split PDF | TL-01, SEC-01, SEC-02 | all |
| TL-05 | JPG to PDF | TL-01, R-14 | all |
| TL-06 | PDF to JPG | TL-01 | all |
| SEC-03 | Maintained malware scanner integration | BE-02, SEC-01 | TL, OP |
| SEC-04 | Container hardening profiles and compose integration | FD-03 | OP, VL |
| SEC-05 | Nginx rate zones and request filtering | BE-10, SEC-04 | OP |
| SEC-06 | Dependency and image maintenance pipeline | FD-04 | PO |
| PT-01 | Analytics schema, redaction, and leakage tests | SH-01, TL-01 | OP, CT |
| PT-02 | Advertising slots and placement guards | SH-03, SH-08 | VL |
| PT-03 | Contact form and result-problem report | SH-08, BE-06 | OP, CT |
| PT-04 | Password handling surface verification | TL-02..TL-06 | VL |
| OP-01 | Netdata monitoring and health signals | SEC-04, BE-06 | OP-02, OP-03 |
| OP-02 | Public status page and noise-resistant derivation | OP-01, SH-08 | VL |
| OP-03 | Telegram alert relay | OP-01 | PO |
| OP-04 | Backups and monthly restore drill | SEC-04, BE-04 | PO |
| SEO-01 | Slug table and legacy URL disposition inventory | SH-04, R-15, R-16 | SEO-02, SEO-03 |
| SEO-02 | Redirect map and localized 410 implementation | SEO-01 | VL |
| SEO-03 | hreflang, canonical, sitemap, and locale-less entry verification | SEO-01, SH-01 | VL |
| CT-01 | Legal page copy baseline (EN) | R-19 gate, D2 brief | CT-02 |
| CT-02 | Legal page localization and version history | CT-01 | VL |
| CT-03 | Blog MDX pipeline and gates | R-21 gate, SEO-01 | CT-04 |
| CT-04 | Fifteen launch articles | CT-03, R-22 | VL |
| VL-01 | Five-tool trilingual E2E gate | TL-01..TL-06 | VL-02 |
| VL-02 | Accessibility verification program | VL-01 | VL-03 |
| VL-03 | Rendered visual verification and baseline comparison | VL-01, R-23 | VL-04 |
| VL-04 | Core Web Vitals and performance verification | VL-03 | VL-05 |
| VL-05 | Pre-launch smoke, rollback readiness, activation checklist | VL-01..VL-04, OP-02 | launch |
| PO-01 | 90-day operating dashboard | OP-01, PT-01 | PO |
| PO-02 | Monthly dependency review cadence | SEC-06 | PO |
| PO-03 | Monthly restore verification | OP-04 | PO |
| PO-04 | Post-launch blog cadence and pause controls | CT-03 | PO |
| PO-05 | Legacy tool restoration planning | R-25, R-26 | next plan |

## 6. Owner Resolution Register (Unresolved-Item Blockers and Stop Conditions)

The items below are the unresolved choices recorded in UX spec Section 21, arch spec Section 25.3, the decision log Open decisions list, and reconciliation categories B and D. Each is a named decision with a stop condition. No task that consumes a resolution item may proceed past the item until the owner disposes it. The governing specifications never require these values to be invented; they are recorded as open by design.

Status semantics: rows carry a status marker in the Item cell. `(RESOLVED: DEC-NNN)` means the owner decided the item and no stop condition remains (recorded in PR-03 with its disposition date). `(PARTIALLY RESOLVED: DEC-NNN)` means part of the item remains open and the remaining stop condition stays in force. Items without a marker remain pending.

| ID | Item (source) | Proposal and evidence to consult | Governed by | Stop condition |
|---|---|---|---|---|
| R-01 (RESOLVED: DEC-198) | Rebuild repository root location and name (arch §3.2 is implementation-level) | DEC-198 selects the workspace root `<workspace-root>` as the repository root; the previously proposed nested `papyr-rebuild/` directory is superseded; `papyr-reference/` remains a nested read-only legacy clone excluded from the repository | DEC-198, DEC-159, arch §3 | Resolved by DEC-198; no stop condition remains; the disposition is recorded in PR-03 |
| R-02 | Git hosting and remote (legacy evidence uses GitHub Actions) | GitHub recommended as default; repository creation is owner-gated; no remote action is authorized by this plan | DEC-159, DEC-177 | Owner confirms hosting and authorizes repository creation at P0 |
| R-03 | Exact per-tool server limits (arch §25.3.2; UX §21.1) | Carry the C2 brief default table (per-tool file count, bytes, pages, pixels, outputs, estimated memory, execution time, zip and result ceilings; global retention 3600 s, max wait 900 s, queue 2000, per-origin 4) as a proposal for owner approval; document the raising procedure | DEC-034, DEC-066, DEC-189, DEC-057 | Owner approves the proposed table before BE-08 and TL tasks hard-code limits |
| R-04 | Compress premium-screen profile thresholds (arch §25.3.6; UX §21.2) | Starting values from the A2 brief (downsampling, DCT re-encode in the ebook family, duplicate detection, compatibility level), validated by normal functional fixtures | DEC-014, DEC-066, DEC-195 | Owner approves profile starting values before TL-02 |
| R-05 | Ghostscript distribution, version pin, and license-review outcome (arch §25.3.1) | Authoritative distribution, pinned version, `-dSAFER`, AGPL notice preservation, source availability; focused license review before launch with permissive or commercial fallback | DEC-195, DEC-059, DEC-056 | License review outcome recorded; fallback path chosen if unacceptable |
| R-06 | PDF to JPG output profile (arch §25.3.6; DEC-039) | A6 brief starting point (profile in the high-quality family within the 16-MP ceiling), white compositing per DEC-081, validated by fixtures | DEC-039, DEC-066 | Owner approves starting values before TL-06 |
| R-07 | Per-worker memory and time bounds and queue caps (arch §25.3.3) | C1 brief defaults (worker memory bound, default 180 s timeout with per-tool overrides, caps per C2) as a proposal, designed around one concurrent job | DEC-189, DEC-019, DEC-035 | Owner approves bounds before BE-05 |
| R-08 | Fair-scheduling classes and parameters (arch §25.3.4) | C1 brief fairness classes (per-origin concurrency, no paid lane, starvation prevention) as a proposal | DEC-137, DEC-134 | Owner approves before BE-05 |
| R-09 | Redis persistence mode, eviction, recovery (arch §25.3.5) | C1 brief defaults (AOF appendfsync everysec plus RDB secondary, noeviction, bounded maxmemory, TTL-bounded minimal metadata) as a proposal; version pin confirmed at implementation (M11) | DEC-174, DEC-019, DEC-056 | Owner approves before BE-04 |
| R-10 | Scanner selection, budget, update channel (arch §25.3.8) | ClamAV candidate per C4/D5 with a documented tuned memory budget for the one-worker envelope and hourly signature updates; fail-closed posture already resolved (DEC-192) | DEC-171, DEC-189, DEC-057 | Owner approves scanner and budget before SEC-03 |
| R-11 | Nginx rate-limit values and fair-use thresholds (arch §25.3.9) | C4 brief defaults (admission 10 r/m burst 5, status 60 r/m burst 30, health unrate-limited, 429 status) as a proposal; real-IP zones on Cloudflare ranges | DEC-020, DEC-035 | Owner approves before SEC-05 |
| R-12 | Monitoring provider, thresholds, dedup rules (arch §25.3.10-11) | C5 brief defaults (Netdata plus multi-region external uptime; N-consecutive-failure noise-resistant logic; Telegram severity contract with dedup keys) as a proposal; provider accounts are owner actions | DEC-180, DEC-182, DEC-119 | Owner approves before OP-01; account creation remains a separately gated action |
| R-13 | Backup schedule, retention, restore target (arch §25.3.20) | C6 brief defaults (daily backup, retention window in the keep-last, keep-daily, keep-weekly, keep-monthly family, isolated monthly restore) as a proposal | DEC-173, DEC-181 | Owner approves before OP-04 |
| R-14 | Trusted edge-country header configuration (arch §25.3.7 residual, §5.3) | Cloudflare `CF-IPCountry` or Vercel `x-vercel-ip-country` with trusted-header validation and spoof rejection; the exact header choice is an implementation-time confirmation (M9) recorded by the owner | DEC-191, DEC-085 | Owner confirms the trusted-header setup before TL-05 |
| R-15 | Tool slugs and the full legacy URL disposition map (UX §21.4; arch §25.3.15) | B4 brief slug table as a proposal; complete legacy inventory audit; 410 default for deferred tools with per-URL exceptions only on credible traffic evidence | DEC-023, DEC-122, DEC-127, DEC-194, DEC-114 | Owner approves slug table and disposition map before SH-01 (route names) and SEO-01 |
| R-16 | Indonesian slug and content mapping (arch §25.3.16) | B4 and B3 locale facts as input; natural stable Indonesian slugs | DEC-122, DEC-115 | Owner approves before SEO-01 |
| R-17 | Browser capability detection and routing thresholds (arch §25.3.17) | DEC-015 limits are binding; B1 layered routing proposal for the measured signals (dimensions, geometry, encryption, corruption, estimated peak memory) | DEC-015, DEC-030, DEC-065, DEC-031 | Owner approves the routing decision table before the TL-01 routing layer |
| R-18 | Adsterra terms, ad-unit code, cookies, identifiers, recipients (UX §21.9; arch §25.3.12) | Owner supplies current publisher terms and the exact banner or native ad-unit code for `mypapyr.com`; provider review before launch | DEC-022, DEC-190, DEC-018 | Owner supplies inputs and approves the integration scope before PT-02 |
| R-19 | Qualified legal review of legal pages (UX §21.10; DEC-045) | EN disclosure baseline inventory from the D2 brief; qualified legal review before launch; then controlled ES/ID localization | DEC-045, DEC-190 | Legal review completed and recorded before CT-02 |
| R-20 | Contact form provider, anti-spam, delivery monitoring (UX §21.7; arch §25.3.14) | Cloudflare-native delivery proposal (Turnstile plus honeypot plus rate limit, Email Routing to the owner inbox); Email Sending beta vs free-path `email()` handler confirmed at implementation (M16) | DEC-046, DEC-050, DEC-056 | Owner approves provider and anti-spam stack before PT-03 |
| R-21 | Gateway capability documentation (UX §21.21; arch §25.3.21) | Remaining fields: request and response schema deviations, structured-output and tool-use behavior, effective context, data retention, availability, safety and compliance policy | DEC-193, DEC-196, DEC-051 | Owner supplies the documentation before CT-03; hard blocker for blog automation design |
| R-22 | Launch blog topics and post-launch topic pipeline (UX §21.5; DEC-052, DEC-053, DEC-124) | E3 brief five candidate topics (one per tool, informational intent) as a proposal; 9 selection criteria; at most one trilingual set per day | DEC-052, DEC-053, DEC-121, DEC-124 | Owner approves topics before CT-04 |
| R-23 | UI baseline owner prompts (UX §21.13-16) | Navbar width intent (D3), duplicate CTA funnel (U3), homepage entrance animations (U5 and D12), Merge error-state auto-clear | DEC-143, audit D1-D13 | Owner answers during the copy and design pass before VL-03 |
| R-24 | Privacy copy re-scoping and FAQ copy accuracy (UX §21.17-18) | Legacy "no tracking" and "no personal data" claims corrected; FAQ states JPG, JPEG, PNG, and WebP | DEC-025, DEC-187 | Owner approves corrected copy before CT-01 |
| R-25 | Legacy traffic and demand data (D-4) | Owner traffic knowledge for the DEC-114 meaningful-traffic test on deferred URLs; Search Console or keyword demand evidence for blog topics | DEC-114, DEC-127 | Owner supplies data before SEO-01 and CT-04 |
| R-26 | Current VPS host state verification (D-3) | Verify the ~8 GB, 4-core, 4.5 GB swap assumption and current host condition before first deployment; re-verify before any production deployment | DEC-172, DEC-160 | Owner verifies host state before OP-04 and VL-05; VPS access is a separately gated action |
| R-27 (RESOLVED: DEC-201) | Numeric 90-day success targets and baseline windows (DEC-024) | Approved by DEC-200: job success at or above 98 percent; system failure at or below 2 percent; uptime at or above 99.5 percent; Core Web Vitals passing for at least 75 percent of visits; completed downloads at or above 85 percent of successful jobs; organic traffic growth greater than zero percent versus the first-28-day baseline at day 90; all five tools receive meaningful usage; processing and queue latency measured as p50 and p95 per tool; baseline is the first 28 post-launch days and evaluation is at day 90 from relaunch. DEC-201 completes the set with the exact numeric fields DEC-200 left open: p95 queue wait at or below 60 seconds per tool; p95 server processing at or below 180 seconds per tool; p50 observed and reported per tool without a separate target; each launch tool at or above 5 percent of total completed downloads during days 29 through 90 | DEC-024, DEC-200, DEC-201 | Resolved by DEC-200 and DEC-201; no stop condition remains; the disposition is recorded in PR-03. The plan remains unapproved, and no phase may start before explicit owner approval |
| R-28 (RESOLVED: DEC-199) | Queue mechanism and PDF/image engine matrix (X2 A-2..A-5, A-7; X1 A1/A3-A6/C1) | Approved by DEC-199 exactly as presented in Section 6.1: queue data structure; browser engines; server engines; sanitization engine; every documented accepted risk, scope boundary, material condition, fallback, and dependency and version review stays in force | DEC-199, DEC-057, DEC-054, DEC-056, DEC-055 | Resolved by DEC-199. Matrix approval is not implementation authorization; version, license, and fallback checks remain in force |

### 6.1 Engine and queue matrix (R-28, approved by DEC-199)

Each row identifies one feature or queue selection, the approved approach, the accepted risks, the scope boundary, and the material conditions, as DEC-057 required at approval time. DEC-199 approves this matrix exactly as presented; the risks, scope boundaries, material conditions, and fallbacks below remain normative. Approval of the matrix is not implementation authorization (DEC-057, DEC-060).

| Item | Approved selection (evidence) | Accepted risks | Scope | Material conditions and fallbacks |
|---|---|---|---|---|
| Queue data structure | Minimal custom queue over Redis Streams consumer groups (X2 A-7, C1 brief) | Custom code carries maintenance burden versus a maintained framework (X2 C-2 records the framework-versus-custom preference as a deferred owner confirmation); Redis version pin confirmed at implementation (M11) | Server-job queue for the five tools: enqueue, claim, status, cancellation, stale reclaim, bounded caps | Approved by DEC-199; R-07 and R-09 dispositions apply; fail-closed under Redis loss with the R2 lifecycle safety net |
| Merge and Split browser happy path | pdf-lib (X2 A-3, A3/A4 briefs) | pdf-lib is unmaintained (A1 brief section 9 item 4); no encryption support; no document-level outlines, forms, or metadata merging; design-time dependency review and fallback plan required | Unencrypted happy path within DEC-015 limits; active-content-bearing files route to the server sanitization path (DEC-192) | Approved by DEC-199 with the documented fallback plan in force; design-time dependency review required (pdf-lib unmaintained); browser limits per DEC-015 |
| Merge and Split server fallback and sanitization engine | pikepdf (qpdf) (X2 A-2, A3/A4 briefs) | qpdf dependency surface; sanitization coverage is not universal (DEC-090 honest-limits rule) | Structure-preserving merge and split fallback; the DEC-090 sanitization pass with DEC-091 category reporting | Approved by DEC-199; sanitization limitations documented in code and copy; pypdf fallback available if a dependency review rejects pikepdf |
| JPG to PDF server engines | img2pdf (LGPL-3.0) plus Pillow (HPND) (X2 A-4, A5 brief) | img2pdf document-metadata capabilities require design-time verification; WebP decode must be validated and resource-bounded (DEC-093) | Lossless JPEG and PNG embedding, WebP decode, EXIF auto-orientation, per-image Letter or A4 sizing per R-14 and DEC-191 | Approved by DEC-199; design-time verification of img2pdf document-metadata capabilities required; metadata preservation remains best-effort (DEC-084) |
| PDF to JPG server engine | pypdfium2 (X2 A-5, A6 brief) | Rendering fidelity and white-compositing determinism require fixture verification (DEC-081) | Server rendering with explicit white fill within the R-06-approved profile and DEC-015 ceilings | Approved by DEC-199; output profile per R-06; white-compositing fixtures required |
| PDF to JPG and page-count browser engine | pdf.js (X2 A-5, A6 and B1 briefs) | pdf.js legacy build floor must be re-confirmed against the pinned version at implementation (M18) | Browser rendering and page counts within DEC-015 limits; sequential rendering with the 16-MP ceiling | Approved by DEC-199; legacy floor re-check at TL-06 implementation |
| Image decode and browser JPG to PDF | pdf-lib plus the platform `createImageBitmap` for WebP decode (X2 A-4, A5 and B1 briefs) | EXIF orientation handling differs by browser; decode expansion must be bounded (DEC-093) | Browser path within the R-17 routing table and DEC-015 limits | Approved by DEC-199; browser and server safety outcomes equivalent (DEC-093) |

Disposition handling: each resolution item is recorded in the Phase 0 log (PR-03) with status pending, approved, rejected, or deferred (and resolved or partially resolved where applicable), the governing decision citation, and the stop condition. An item marked deferred keeps its stop condition in force for the consuming task. Resolved items carry their disposition date; partially resolved items carry both the resolved fields and the remaining open fields.

## 7. Separately Gated Actions (Not Authorized by This Plan)

The following actions are distinct from plan execution and require separate, explicit owner authorization at the moment they occur. Tasks in this plan prepare artifacts for them but never perform them (DEC-197, DEC-160, DEC-097).

| Gate | Action | Authorization required from | Governing decisions |
|---|---|---|---|
| G-1 | Repository creation, git commits, pushes, remote setup | Owner at Phase 0 and per commit or push, except the owner-approved blog automation pipeline under DEC-048, CT-03, and PO-04, whose gate-passing PRs auto-merge through the normal build path; activation of that workflow is owner-gated | DEC-197, DEC-159, DEC-048 |
| G-2 | VPS SSH access, host-state verification, host configuration | Owner before any access | DEC-172, DEC-160 |
| G-3 | Production backend deployment and post-deployment smoke | Owner per deployment, with pre-deployment verification and rollback readiness | DEC-160, DEC-177 |
| G-4 | Provider account creation and authentication (Vercel, R2, Netdata Cloud, monitor provider, Telegram bot, Adsterra, S3 backup destination, GitHub) | Owner at the point of each action | DEC-095, DEC-097, DEC-173, DEC-180 |
| G-5 | Gateway access and any authenticated call to `https://router.budgezen.com/v1` | Owner; no authenticated call is authorized by any planning artifact | DEC-193, DEC-196 |
| G-6 | Adsterra publisher integration, script placement, and regional consent behavior confirmation | Owner after R-18 inputs are supplied | DEC-022, DEC-190 |
| G-7 | Qualified legal review of Privacy, Terms, and Cookies/Advertising pages | Owner engages the reviewer | DEC-045 |
| G-8 | Legacy credential rotation and exposure investigation before production use | Owner at deployment preparation | DEC-017, DEC-176 |
| G-9 | Vertical VPS upgrade, new paid service, or material cost increase | Owner before any spending | DEC-095, DEC-098 |
| G-10 | Additional worker concurrency beyond one active worker | Owner after capacity evidence | DEC-189, DEC-098 |
| G-11 | Any per-URL disposition deviating from the 410 Gone default | Owner per URL, on credible traffic or intent evidence | DEC-194 |

## 8. Phase Plans

### Phase 0: Pre-execution prerequisites and owner gates

**Goal:** establish the repository, the branch strategy, and the resolution register before any code exists.

**Gate entry:** owner approves this implementation plan (DEC-060, DEC-197).

**Gate exit:** repository exists at the workspace root per R-01 (DEC-198), branch strategy is recorded, canonical docs are baseline-recorded, and every resolution item has a recorded disposition.

#### PR-01: Repository creation and branch strategy

**Files:**
- Create: `.gitignore` (excludes `papyr-reference/`, local caches, and secrets), `README.md`

**Interfaces:**
- Consumes: R-01 disposition (resolved by DEC-198), R-02 disposition
- Produces: the git repository root (the workspace root per DEC-198) that every later task writes into

- [ ] **Step 1: Record the owner decision.** Log the R-01 disposition (DEC-198: the workspace root is the repository root; the nested `papyr-rebuild/` proposal is superseded) and the R-02 hosting choice in the resolution register (PR-03). No git operation runs before this is recorded.
- [ ] **Step 2: Prepare the repository skeleton.** Create the new-repository directory tree from Section 3 at the workspace root with `.gitignore` entries that exclude `papyr-reference/` (the nested read-only legacy clone, including its nested `.git`), node_modules, `.next`, `.env`, `__pycache__`, test artifacts, and local caches. No command in this step targets anything inside `papyr-reference/`. This step is file creation only; git initialization happens in step 4 under the G-1 gate.
- [ ] **Step 3: Verify the skeleton.** Run: `ls frontend backend deploy scripts docs` and `git -C papyr-reference status --porcelain` from the workspace root. Expected: the proposed new-repository directories exist, no production code or dependency files are present, and `papyr-reference/` remains clean (empty porcelain, exit 0).
- [ ] **Step 4: Initialize the repository.** Owner authorizes G-1, then run: `git init` in the workspace root and create the working branch per the recorded strategy (proposal: protected `main`, feature branches per task boundary). Verify with `git status --porcelain` that `papyr-reference/` is excluded and untracked; no git command ever targets the nested legacy repository or its `.git`.
- [ ] **Step 5: Review and commit boundary.** Commit the skeleton as the first atomic unit. Suggested subject: `chore: initialize rebuild repository skeleton at workspace root`.

#### PR-02: Canonical documentation baseline

**Files:**
- Create: `scripts/check-docs-migration.sh`, `docs/canonical-docs-baseline.md`

**Interfaces:**
- Consumes: PR-01, DEC-198
- Produces: the canonical-documentation baseline record inside the repository; the decision log and both specifications already live at the repository root as governed records (DEC-198), so no copies are created

- [ ] **Step 1: Write the failing check script.** Create `scripts/check-docs-migration.sh`: it exits non-zero when `papyr-rebuild-decisions.md` is absent, when the decision log does not contain every decision ID from DEC-001 through DEC-201, when either specification under `docs/superpowers/specs/` is absent, or when `docs/canonical-docs-baseline.md` is absent.
- [ ] **Step 2: Verify the check fails.** Run: `scripts/check-docs-migration.sh`. Expected: FAIL, baseline record absent.
- [ ] **Step 3: Create the baseline record.** Write `docs/canonical-docs-baseline.md` documenting the canonical document paths, the DEC-001 through DEC-201 decision range, and their governed-record status under DEC-198 (DEC-006, DEC-026).
- [ ] **Step 4: Verify the check passes.** Run: `scripts/check-docs-migration.sh`. Expected: PASS, all DEC IDs present and the baseline record exists.
- [ ] **Step 5: Review and commit boundary.** Commit the baseline. Suggested subject: `docs: record canonical documentation baseline at repository root`.

#### PR-03: Resolution register

**Files:**
- Create: `docs/resolution-register.md`

**Interfaces:**
- Consumes: Section 6 dispositions as the owner provides them
- Produces: the register every resolution task and consuming task reads

- [ ] **Step 1: Write the register shell.** Create the document with one row per resolution item R-01 through R-28: ID, item, governing decisions, status, stop condition, disposition date. Pre-fill the resolved statuses from Section 6: R-01 RESOLVED (DEC-198), R-28 RESOLVED (DEC-199), R-27 RESOLVED (DEC-201).
- [ ] **Step 2: Fill in recorded dispositions.** Copy the owner dispositions from Section 6 as they are made, without silently changing any item text.
- [ ] **Step 3: Verify coverage.** Run: `grep -c '^| R-' docs/resolution-register.md`. Expected: 28 rows, each with a non-empty status.
- [ ] **Step 4: Review the register with the owner** at the Phase 0 gate review.
- [ ] **Step 5: Review and commit boundary.** Commit the register. Suggested subject: `docs: add owner resolution register`.

### Phase 1: Monorepo foundation and CI core gate

**Goal:** wire the three workspaces and the CI core gate so later phases start from a verified baseline.

**Gate entry:** Phase 0 complete.

**Gate exit:** lint, test, build, and security-scan jobs pass on the skeleton; the core gate is documented per DEC-177.

#### FD-01: Frontend workspace scaffold

**Files:**
- Create: `frontend/package.json`, `frontend/tsconfig.json`, `frontend/next.config.ts`, `frontend/eslint.config.mjs`, `frontend/postcss.config.mjs`, `frontend/.prettierrc`, `frontend/src/app/globals.css` (empty token shell), `frontend/src/app/page.tsx` (minimal)

**Interfaces:**
- Consumes: PR-01
- Produces: the Next.js workspace with script names `dev`, `build`, `start`, `lint`, `test` (Vitest), `test:e2e` (Playwright), `format:check`; dependency floors: next, react, react-dom, tailwindcss v4, typescript

- [ ] **Step 1: Write the failing test.** Add a Vitest smoke test asserting the workspace exports a buildable config (for example, that `next.config.ts` exists and exports a config object).
- [ ] **Step 2: Verify the test fails.** Run: `npm test` in `frontend/`. Expected: FAIL, workspace has no test runner yet.
- [ ] **Step 3: Scaffold the workspace.** Create the package.json, configs, and a minimal `src/app/page.tsx`. Dependency versions are pinned at install time from current official releases (DEC-056); no dependency is installed in this planning phase.
- [ ] **Step 4: Verify the test passes.** Run: `npm test` and `npm run lint`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit the scaffold. Suggested subject: `chore(frontend): scaffold Next.js workspace`.

#### FD-02: Backend workspace scaffold

**Files:**
- Create: `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/ruff.toml`, `backend/pytest.ini`, `backend/app/__init__.py`, `backend/app/main.py` (minimal FastAPI shell with `/health`)

**Interfaces:**
- Consumes: PR-01
- Produces: the FastAPI workspace with script names `ruff check`, `ruff format --check`, `pytest`; the `/health` endpoint used by every later integration test

- [ ] **Step 1: Write the failing test.** Add `backend/tests/test_health.py` asserting `GET /health` returns 200 with `status: ok`.
- [ ] **Step 2: Verify the test fails.** Run: `pytest tests/test_health.py -v` in `backend/`. Expected: FAIL, no app module.
- [ ] **Step 3: Write the minimal implementation.** Create `app/main.py` with the FastAPI app and the `/health` endpoint only. No routers, no task store, no legacy modules.
- [ ] **Step 4: Verify the test passes.** Run: `pytest tests/ -v` and `ruff check .`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `chore(backend): scaffold FastAPI workspace`.

#### FD-03: Deploy workspace scaffold

**Files:**
- Create: `deploy/docker-compose.yml` (skeleton), `deploy/nginx/conf.d/production.conf` (skeleton), `deploy/.env.production.example`, `deploy/runbook-vps.md` (outline)

**Interfaces:**
- Consumes: PR-01
- Produces: the deployment workspace that SEC-04, OP-01, and OP-04 complete

- [ ] **Step 1: Write the failing test.** Add a shell test asserting the compose file is parseable: `docker compose -f deploy/docker-compose.yml config --quiet`. Expected: FAIL, file absent.
- [ ] **Step 2: Verify the test fails.** Run the command from the repo root. Expected: non-zero exit.
- [ ] **Step 3: Write the skeleton.** Create the compose file with service names `nginx`, `api`, `redis`, `workers` (and later `scanner` in SEC-03) and the env template with non-secret variable names only.
- [ ] **Step 4: Verify the test passes.** Run: `docker compose -f deploy/docker-compose.yml config --quiet`. Expected: exit 0. (Docker is not started; config validation only.)
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `chore(deploy): scaffold compose and nginx skeleton`.

#### FD-04: CI core gate skeleton

**Files:**
- Create: `.github/workflows/ci.yml` (contingent on R-02; path and provider per the approved hosting disposition), `scripts/check-ci.sh`

**Interfaces:**
- Consumes: FD-01..FD-03, R-02
- Produces: the core gate jobs: frontend lint, test, build; backend ruff and test; production build verification; security scanning (Trivy) on built images; the workflow never deploys (DEC-160); the artifact shape depends on the R-02 hosting disposition

- [ ] **Step 1: Write the failing gate test.** Add `scripts/check-ci.sh` that parses the CI workflow YAML (path per the R-02 hosting disposition; proposal: `.github/workflows/ci.yml` on GitHub Actions) and asserts no `deploy` job exists and no secret is exposed to `pull_request_target` events.
- [ ] **Step 2: Verify the test fails.** Run: `scripts/check-ci.sh`. Expected: FAIL, workflow absent.
- [ ] **Step 3: Write the workflow.** The workflow artifact is contingent on the R-02 hosting disposition; if GitHub Actions is approved, model the job structure on the legacy `papyr-reference/.github/workflows/ci.yml` and add the production-build and security-scan stages required by DEC-177; if a different CI provider is approved, produce the equivalent workflow artifact for that provider. CI secrets and environments are configured at execution under G-4.
- [ ] **Step 4: Verify the test passes.** Run: `scripts/check-ci.sh`. Expected: PASS. Also run the local equivalents of the jobs on the skeleton.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `ci: add core gate without deployment`.

#### FD-05: Root tooling conventions

**Files:**
- Create: `README.md` (complete), `CONTRIBUTING.md`, `docs/plan/index.md`

**Interfaces:**
- Consumes: FD-01..FD-04
- Produces: documented conventions: task branch naming, commit message prefixes (`feat`, `fix`, `docs`, `chore`, `test`, `ci`, `refactor`, `security`), the TDD requirement, and the phase-plan expansion rule (each phase may be expanded into its own plan file under `docs/superpowers/plans/` following this master plan's template and gates)

- [ ] **Step 1: Write the documentation files** with the conventions above, referencing this master plan by relative path.
- [ ] **Step 2: Verify internal links.** Run: `grep -rn 'docs/superpowers/plans' docs/`. Expected: the master plan link resolves to a real file.
- [ ] **Step 3: Review the conventions with the execution agent** so task branches and commit boundaries are applied consistently.
- [ ] **Step 4: Review and commit boundary.** Commit. Suggested subject: `docs: add contribution and planning conventions`.

### Phase 2: Frontend shell, locale routing, and canonical catalog

**Goal:** the app shell, locale routing, and the single canonical tool catalog, preserving the legacy visual baseline and correcting defects D1-D13 (UX §10.6).

**Gate entry:** Phase 1 complete; R-15 slug dispositions recorded (route names depend on them).

**Gate exit:** shell, homepage, and catalog verified across EN, ES, and ID with passing unit and E2E tests; `papyr-reference` frontend patterns cited as the visual reference.

#### SH-01: Locale routing and middleware

**Files:**
- Create: `frontend/src/app/[locale]/layout.tsx` (shell), `frontend/src/i18n/config.ts`, `frontend/src/i18n/messages/{en,es,id}.json`, `frontend/src/middleware.ts`
- Modify: `frontend/next.config.ts`

**Interfaces:**
- Consumes: FD-01, R-15 (slug table feeds route names)
- Produces: `getLocale()`, `Locale = "en" | "es" | "id"`, locale-less entry redirect per DEC-047, `x-default` to EN; every route carries an explicit locale prefix (DEC-023)

- [ ] **Step 1: Write the failing tests.** Unit tests asserting: locale-less `/` redirects once by supported browser language with manual-choice override; unsupported languages fall back to EN; every tool route resolves under each locale prefix.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` in `frontend/`. Expected: FAIL, no routing code.
- [ ] **Step 3: Write the minimal implementation.** Middleware that reads the manual choice (minimal non-sensitive storage), then `Accept-Language`, redirects once, and falls back to EN; `[locale]` route group with the three message catalogs (shell copy only).
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS. Run: `npm run build`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add locale routing and language detection`.

#### SH-02: Design tokens and global styles

**Files:**
- Create: `frontend/src/app/globals.css`

**Interfaces:**
- Consumes: FD-01, UX §10.1 token table
- Produces: `--color-navy #1e3a5f`, `--color-accent #2563eb`, `--color-bg #f9fafb`, `--color-foreground #171717`, DM Sans font wiring; dead tokens `--color-background` and `--font-dm-sans` resolved (D4); `@theme inline` emission verified so body variables never silently fall back (D5, UX §21.19)

- [ ] **Step 1: Write the failing test.** A build-and-grep or computed-style check asserting the body background, text color, and font resolve to the documented token values (B5 method, UX §21.19).
- [ ] **Step 2: Verify the test fails.** Run: `npm test`. Expected: FAIL, globals.css is an empty shell.
- [ ] **Step 3: Write the minimal implementation.** Apply the token table with utilities or a non-inline `@theme`, wire the DM Sans variable, and drop the dead tokens.
- [ ] **Step 4: Verify the test passes.** Run: `npm test` and `npm run build`. Expected: PASS with no silent fallback.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add design tokens and font wiring`.

#### SH-03: Root shell, layout, skip link, metadata

**Files:**
- Create: `frontend/src/app/[locale]/layout.tsx` (complete), `frontend/src/components/SkipLink.tsx`
- Modify: `frontend/src/app/layout.tsx` (locale-aware html lang, metadataBase, per-locale metadata)

**Interfaces:**
- Consumes: SH-01, SH-02
- Produces: locale-aware `html lang`, sticky-footer flex shell, skip-to-content link (D8), localized metadata and OG/Twitter images replacing the legacy Indonesian-only defaults (UX §11.1)

- [ ] **Step 1: Write the failing tests.** Render tests asserting the root shell renders `lang` per locale, a skip link is first in tab order, and metadata carries locale-aware title and description.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Complete the shell, add the SkipLink component, and replace the legacy hardcoded metadata (`papyr-reference/frontend/src/app/layout.tsx:16-41`) with per-locale values.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add locale-aware shell and skip link`.

#### SH-04: Canonical tool catalog

**Files:**
- Create: `frontend/src/lib/catalog.ts`

**Interfaces:**
- Consumes: FD-01, R-15 slug table, UX §8.4
- Produces: one catalog with `id`, `href` per locale, short label, full label, localized labels, description, icon; consumed by navbar, footer, homepage grid, Related Tools, and metadata (DEC-154); exported data contracts locked by shape tests (D2, DEC-143)

- [ ] **Step 1: Write the failing tests.** Shape tests asserting the catalog exports exactly five tools with the five required fields and localized labels for en, es, and id; a uniqueness test for hrefs per locale.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL, no catalog module.
- [ ] **Step 3: Write the minimal implementation.** Define the catalog from the five-tool set (DEC-010) with localized labels and per-locale hrefs from the R-15 slug table.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add canonical tool catalog`.

#### SH-05: Navbar

**Files:**
- Create: `frontend/src/components/Navbar.tsx`, `frontend/src/components/LanguageSwitcher.tsx`

**Interfaces:**
- Consumes: SH-03, SH-04
- Produces: frosted sticky navbar with the category dropdown model (desktop) and native accordion (mobile), populated only with the five launch tools (DEC-147, DEC-152, DEC-155); EN/ES/ID selector preserving the equivalent page (DEC-149); D8-D13 accessibility corrections (aria-expanded, Escape handling, focus-visible, active-category indication)

- [ ] **Step 1: Write the failing tests.** Interaction tests for dropdown open and close, outside-click and Escape close, mobile accordion expansion, active-category state, and language switcher semantics (D13).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port the legacy navbar patterns (`papyr-reference/frontend/src/components/Navbar.tsx`) into the new shell, applying the D8-D13 corrections and the five-tool population rule.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test` and `npm run test:e2e`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add categorized navbar and language switcher`.

#### SH-06: Footer

**Files:**
- Create: `frontend/src/components/Footer.tsx`, `frontend/src/components/LogoLockup.tsx`

**Interfaces:**
- Consumes: SH-03, SH-04
- Produces: footer with real routes (Privacy, Terms, Cookies/Advertising, Contact/Support, Status, Roadmap), dynamic year (D6), one logo lockup component (D11), tools section from the catalog (D2); no `#` placeholders (D1)

- [ ] **Step 1: Write the failing tests.** Render tests asserting all footer links point to real localized routes and the year is computed at runtime.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port the legacy footer patterns (`papyr-reference/frontend/src/components/Footer.tsx`) with the D1, D2, D6, and D11 corrections.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add footer with real routes`.

#### SH-07: Homepage

**Files:**
- Create: `frontend/src/app/[locale]/page.tsx`

**Interfaces:**
- Consumes: SH-04, SH-05
- Produces: hero (pill, fluid clamp H1, CTA, trust badges), equal-weight five-card tool directory (DEC-148), privacy section with decision-consistent copy (DEC-150), how-it-works, FAQ; no stale legacy claims (UX §11.4)

- [ ] **Step 1: Write the failing tests.** Render tests asserting the five equal-weight tool cards render from the catalog, the hero carries the fast-easy-free message, and no legacy 13-tool references or "no tracking" claims appear.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port the legacy homepage structure (`papyr-reference/frontend/src/app/page.tsx:486-593`) adapted to five tools with corrected copy (DEC-043, DEC-150).
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add homepage with five-tool directory`.

#### SH-08: Supporting surface shells

**Files:**
- Create: `frontend/src/app/[locale]/privacy/page.tsx`, `terms/page.tsx`, `cookies-advertising/page.tsx`, `contact/page.tsx`, `status/page.tsx`, `roadmap/page.tsx`, `blog/page.tsx` (shells)

**Interfaces:**
- Consumes: SH-01
- Produces: route shells for the legal, support, status, roadmap, and blog surfaces; full content arrives in P6, P7, and P9

- [ ] **Step 1: Write the failing tests.** Route tests asserting each supporting surface resolves under all three locales with a shell heading.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the shell pages** with localized headings and the shared page shell. Page copy is added in P6, P7, and P9.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test` and `npm run build`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add supporting surface shells`.

### Phase 3: Backend core and early security prerequisites

**Goal:** settings, validation, R2, Redis task store, queue and worker, task state machine, cleanup, capability contract, signed downloads, and fair use, replacing the legacy in-memory task store pattern (`papyr-reference/backend/services/async_task.py`); then the early security prerequisites (SEC-01 threat classification and SEC-02 sanitization pass) that the tool tasks consume.

**Gate entry:** Phase 1 complete; R-03, R-07, R-08, R-09, R-28 dispositions recorded.

**Gate exit:** integration tests pass against real Redis and an R2 test fixture; the one-worker posture is enforced (DEC-189); SEC-01 and SEC-02 are verified so TL-02..TL-04 can consume them.

#### BE-01: Backend settings and logging

**Files:**
- Create: `backend/app/config.py`, `backend/app/utils/logging.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: FD-02, R-09
- Produces: `Settings` frozen dataclass (legacy pattern: `papyr-reference/backend/utils/config.py`), JSON structured logging with the DEC-175 prohibited-field exclusions, `/health` wired

- [ ] **Step 1: Write the failing tests.** Tests asserting required settings raise on missing values, defaults apply, and the logging formatter redacts filenames, passwords, signed URLs, object keys, and contents (DEC-175, DEC-036, DEC-042).
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v` in `backend/`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port the settings pattern with the new variable set (R2, retention, queue, worker, scanner later) and the structured logging config.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v` and `ruff check .`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add settings and structured logging`.

#### BE-02: Input validation library

**Files:**
- Create: `backend/app/security/validation.py`

**Interfaces:**
- Consumes: BE-01
- Produces: `validate_pdf(bytes) -> PdfInspection` and `validate_image(bytes) -> ImageInspection` covering the legacy order (empty, MIME, extension, magic bytes, size, page count, encrypted status; `papyr-reference/backend/utils/pdf_validator.py`) plus decoded-resource risk for images (DEC-093)

- [ ] **Step 1: Write the failing tests.** Fixture-driven tests: empty file, wrong MIME, wrong extension, missing magic bytes, oversized, password-protected, corrupt, malformed image, image with declared dimensions exceeding resource limits.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port and extend the legacy validator, keeping rejections in safe general categories (DEC-169, DEC-088).
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add pdf and image validation`.

#### BE-03: R2 client with key hygiene and signed URLs

**Files:**
- Create: `backend/app/utils/r2.py`

**Interfaces:**
- Consumes: BE-01
- Produces: `upload_object`, `delete_object` (idempotent), `generate_signed_url(object_key, expires_at)`; keys `tmp/<YYYY-MM-DD>/<32-hex-uuid><safe-ext>` (C3 brief); signed URL expiry capped at `min(remaining, 300 s)` (DEC-170); `expires-at` custom metadata mirrored (C3)

- [ ] **Step 1: Write the failing tests.** Tests asserting key shape and no filename leakage, signed URL expiry never exceeds the authoritative expiry, delete is idempotent, and keys never appear in logs (DEC-170, DEC-025).
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port the legacy boto3 pattern (`papyr-reference/backend/utils/r2.py`) with the new key scheme and expiry cap.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add r2 client with key hygiene`.

#### BE-04: Redis minimal task store

**Files:**
- Create: `backend/app/queue/store.py`

**Interfaces:**
- Consumes: BE-01, R-09
- Produces: minimal task records (opaque id, state, timing, expiry, route, non-sensitive object refs) with TTL no later than task and artifact lifecycle; prohibited fields never written (DEC-174); persistence mode per the approved R-09 disposition

- [ ] **Step 1: Write the failing tests.** Tests asserting a record round-trips, expires at the recorded TTL, and rejects attempts to persist filenames, passwords, signed URLs, contents, or previews (DEC-174).
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** A thin Redis wrapper over hashes and TTL keys with a typed record model.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add redis minimal task store`.

#### BE-05: Queue, worker loop, and fair scheduling

**Files:**
- Create: `backend/app/queue/queue.py`, `backend/app/worker/worker.py`

**Interfaces:**
- Consumes: BE-04, R-07, R-08, R-28
- Produces: the minimal custom server-job queue over Redis Streams consumer groups per the R-28 disposition approved by DEC-199 (C1 brief); one worker replica claiming one job at a time (DEC-189); per-origin concurrency bound; queued-to-cancelled atomic transition via Lua (DEC-069); stale-claim reclaim; explicit per-job timeout with per-tool overrides

- [ ] **Step 1: Write the failing tests.** Integration tests: enqueue, claim, process, status transitions; cancellation while queued wins atomically; cancellation after pickup reports no-longer-available; a stuck claim is reclaimed; queue caps reject above the approved R-07 values.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The queue and worker loop following the C1 design, bounded by the approved R-07 and R-08 values.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add queue and worker loop`.

#### BE-06: Task state machine and status API

**Files:**
- Create: `backend/app/tasks/state_machine.py`, `backend/app/routers/status.py`

**Interfaces:**
- Consumes: BE-04, BE-05
- Produces: states `queued`, `processing`, `done`, `failed`, `cancelled` with the arch §13.1 transitions; `GET /api/v1/tools/{tool}/tasks/{task_id}/status` returning state, authoritative timestamps, expiry, measurable progress, and safe error categories (DEC-033, DEC-070); unknown or expired ids return distinct not-found (arch §13.5)

- [ ] **Step 1: Write the failing tests.** State-transition table tests covering every arch §13.1 transition and its guard, plus API tests for status responses and not-found behavior.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The state machine module and the versioned status router.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add task state machine and status api`.

#### BE-07: Cleanup coordinator and lifecycle safety net

**Files:**
- Create: `backend/app/tasks/cleanup.py`

**Interfaces:**
- Consumes: BE-03, BE-04
- Produces: active deletion of source, intermediate, and result objects by the absolute deadline; idempotent, observable with counts and timing only, recoverable after restarts (DEC-166); R2 lifecycle rule on `tmp/` with 1-day expiration plus multipart abort as the safety net (C3 brief)

- [ ] **Step 1: Write the failing tests.** Tests asserting objects are deleted by the deadline, deletion is idempotent, restart recovery completes pending deletions, cleanup telemetry contains no content or sensitive identifiers, and the lifecycle rule file matches the promised retention.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The cleanup coordinator over expired Redis records and the lifecycle rule declaration in the deploy workspace.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add cleanup coordinator and lifecycle safety net`.

#### BE-08: Capability and limits contract API

**Files:**
- Create: `backend/app/routers/capabilities.py`

**Interfaces:**
- Consumes: BE-02, R-03
- Produces: `GET /api/v1/capabilities` (cacheable, versioned) carrying per-tool server limits and the machine-readable failure codes (C2 brief, DEC-165); backend validation stays authoritative (DEC-165)

- [ ] **Step 1: Write the failing tests.** Contract tests asserting the endpoint returns the approved per-tool fields and that a violating upload returns the matching machine-readable code.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The capabilities router driven by the R-03-approved table, with the failure-code enum.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add capabilities and limits contract`.

#### BE-09: Signed download authorization and refresh

**Files:**
- Create: `backend/app/routers/download.py`

**Interfaces:**
- Consumes: BE-03, BE-06
- Produces: download authorization for a task whose result is valid and unexpired; refreshed signed URLs for the same result without extending retention (DEC-170, DEC-075)

- [ ] **Step 1: Write the failing tests.** Tests asserting authorization is denied for unknown, expired, or cancelled tasks, and refreshed URLs never exceed the authoritative expiry.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The download router using the state machine and the R2 client.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add signed download authorization`.

#### BE-10: Fair-use and rate-limit enforcement

**Files:**
- Create: `backend/app/security/fair_use.py`

**Interfaces:**
- Consumes: BE-04, BE-08
- Produces: adaptive anonymous fair-use controls consistent across API processes (Redis-shared counters, DEC-020); clear retryable responses; per-origin concurrency; no fixed daily quota for ordinary users

- [ ] **Step 1: Write the failing tests.** Tests asserting shared counters behave identically across simulated processes, suspicious traffic is delayed or rejected with clear retry responses, and ordinary usage is not quota-limited.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Redis-backed counters and admission logic replacing the legacy per-process limiter for server jobs (legacy: `papyr-reference/backend/main.py`).
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(backend): add shared fair-use controls`.

#### SEC-01: Threat classification and fail-closed matrix (early security prerequisite)

**Files:**
- Create: `backend/app/security/classification.py`

**Interfaces:**
- Consumes: BE-02, BE-08
- Produces: the threat-classification and fail-closed matrix from the D5 brief; anything not classifiable as safe fails closed (DEC-088, DEC-065); blocking precedes sanitization; safe localized rejections; the scanner and sanitization interface contracts that TL-03 and TL-04 fail-closed tests consume (the concrete scanner client lands in SEC-03 under R-10)

- [ ] **Step 1: Write the failing tests.** Fixture tests: each threat class blocks with a safe rejection and no engine reach beyond isolated inspection; unclassifiable inputs fail closed; logs keep only minimal non-content indicators (DEC-088, DEC-175); the scanner and sanitization interfaces are defined so a stub reporting scanner-unavailable exercises the fail-closed path.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The classification module, its integration point before engine dispatch, and the scanner and sanitization interface contracts.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `security(backend): add threat classification and fail-closed matrix`.

#### SEC-02: Sanitization pass (early security prerequisite)

**Files:**
- Create: `backend/app/security/sanitize.py`

**Interfaces:**
- Consumes: BE-02, R-28
- Produces: active-content sanitization using the approved pikepdf engine (DEC-199, R-28; A3 brief), removing JavaScript, embedded attachments, launch actions, and external actions with category reporting (DEC-090, DEC-091); used by Merge, Split, and Compress outputs

- [ ] **Step 1: Write the failing tests.** Fixture tests asserting each active-content category is removed or neutralized, attachments are removed and never offered as downloads, category reporting is accurate without payload details, and sanitization limitations are documented in code comments (DEC-090, DEC-091).
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The sanitization module behind the SEC-01 interface using the approved pikepdf engine (DEC-199, R-28; A3 brief) with the category model.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `security(backend): add active-content sanitization`.

### Phase 4: The five tools

**Goal:** shared tool foundations plus five production-ready tools with browser and server paths, routing, honest states, and trilingual UI.

**Gate entry:** Phases 2 and 3 complete (including the SEC-01 threat-classification and SEC-02 sanitization prerequisites produced in Phase 3); R-03, R-04, R-05, R-06, R-14, R-17 dispositions recorded.

**Gate exit:** each tool passes browser, server, routing, and E2E acceptance tests in all three locales.

#### TL-01: Shared tool foundations

**Files:**
- Create: `frontend/src/components/uploader/Dropzone.tsx`, `frontend/src/components/states/PreparingCard.tsx`, `frontend/src/components/states/ProcessingCard.tsx`, `frontend/src/components/states/DoneCard.tsx`, `frontend/src/components/states/ErrorCard.tsx`, `frontend/src/components/states/QueuedCard.tsx`, `frontend/src/lib/naming.ts`, `frontend/src/lib/zip.ts`, `frontend/src/lib/taskPolling.ts`, `frontend/src/hooks/useTaskPolling.ts`

**Interfaces:**
- Consumes: SH-03, BE-06, BE-08, R-17
- Produces: the shared state vocabulary (idle, preparing, ready, uploading, queued, processing, finalizing, done, error; UX §13.1); honest stage labels and shimmer (DEC-033); dropzone baseline contract (UX §10.4 item 3); auto-download attempt plus manual Download (DEC-029, DEC-068); ZIP plus individual downloads (DEC-037); process-another-file reset (DEC-156); safe localized naming (DEC-042); capabilities-client fallback values when the contract is unavailable (DEC-165); object URL revocation (DEC-032); expiry countdown (DEC-067); refresh recovery via `sessionStorage` opaque tokens (DEC-072); the routing decision table per R-17

- [ ] **Step 1: Write the failing tests.** Unit tests for naming (sanitization, length bounds, localized suffixes, duplicate disambiguation), ZIP ordering, state-transition rendering, and the capabilities-client fallback; E2E smoke for one tool using the shared foundations.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` and `npm run test:e2e`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The shared components and libraries modeled on the legacy patterns (`papyr-reference/frontend/src/lib/pdfUtils.ts`, `frontend/src/hooks/useAsyncTask.ts`, `frontend/src/components/PDFUploader.tsx`).
- [ ] **Step 4: Verify the tests pass.** Run: `npm test` and `npm run test:e2e`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(frontend): add shared tool foundations`.

#### TL-02: Compress PDF

**Files:**
- Create: `frontend/src/app/[locale]/compress-pdf/page.tsx`, `backend/app/services/compress_service.py`, `backend/app/routers/compress.py`

**Interfaces:**
- Consumes: TL-01, BE-03, BE-05, BE-06, SEC-02, R-04, R-05
- Produces: server-side Compress (DEC-014, DEC-015) with the unmodified Ghostscript subprocess including `-dSAFER` (DEC-195; the legacy `papyr-reference/backend/services/compress_service.py` lacks `-dSAFER`, a confirmed gap to correct); one automatic premium-screen profile (R-04); always-new artifact with honest size reporting including zero or negative savings (DEC-080); no fabricated percentage (UX §12.1); password requested only when required (DEC-036, DEC-064); sanitization disclosure (DEC-091); no quality controls (DEC-014)

- [ ] **Step 1: Write the failing tests.** Service tests with fixtures: valid PDF compresses and reports actual sizes; already-optimized input returns an honest not-smaller result; timeout and failure paths are distinct; password-protected input raises a distinct error; the command line contains `-dSAFER`; the output is always a new artifact. API tests: submit, status, download through the signed URL.
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The compress service (subprocess invocation with safety flags, bounded timeout per R-07) and the versioned router following the BE contract.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`, then the frontend E2E for the Compress flow (`npm run test:e2e`). Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(compress): add server-side compress tool`.

#### TL-03: Merge PDF

**Files:**
- Create: `frontend/src/app/[locale]/merge-pdf/page.tsx`, `backend/app/services/merge_service.py`, `backend/app/routers/merge.py`

**Interfaces:**
- Consumes: TL-01, SEC-01, SEC-02
- Produces: browser-first merge using the approved browser engine pdf-lib (DEC-199, R-28; A3 brief) for the unencrypted happy path and the approved server fallback engine pikepdf (DEC-199, R-28) for corrupt, encrypted-unsupported, unsafe, or active-content-bearing inputs (DEC-030, DEC-192); file-level controls only (DEC-040); per-file password handling (DEC-074); all-or-nothing semantics (DEC-076); feature preservation to the safe engine extent with truthful disclosure (DEC-079); sanitization with category disclosure (DEC-090, DEC-091); fail-closed when the scanner or sanitization path is unavailable (DEC-192)

- [ ] **Step 1: Write the failing tests.** Browser-path tests: happy path merges in user order; sortable reorder has a keyboard alternative and announcements; all-or-nothing failure on an invalid source with other sources retained in memory. Server-path tests: active-content detection routes to the server sanitization path; sanitization removes JavaScript and attachments with category reporting; scanner-unavailable jobs fail closed against the SEC-01 scanner interface (a stub reports unavailable).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` and `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The merge page, browser merge utilities, and the server merge service with the sanitization pass from SEC-02.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`, `pytest tests/ -v`, `npm run test:e2e`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(merge): add browser-first merge with server sanitization fallback`.

#### TL-04: Split PDF

**Files:**
- Create: `frontend/src/app/[locale]/split-pdf/page.tsx`, `frontend/src/components/PageRangeInput.tsx`, `backend/app/services/split_service.py`, `backend/app/routers/split.py`

**Interfaces:**
- Consumes: TL-01, SEC-01, SEC-02
- Produces: custom ranges and per-page modes (DEC-038); user-entered order preserved and overlaps allowed as independent outputs (DEC-077, DEC-078); range input with charset validation, live preview of the effective sequence and duplicated membership, actionable localized errors (DEC-038); browser-first using the approved browser engine pdf-lib (DEC-199, R-28) with the approved server fallback engine pikepdf (DEC-199, R-28) for unsafe or active-content-bearing inputs (DEC-192); deterministic naming and ZIP manifest (DEC-078)

- [ ] **Step 1: Write the failing tests.** Parser tests: `8-10,1-2` yields that exact output order; overlaps produce independent outputs; repeated identical ranges are disambiguated; invalid tokens produce actionable errors. Routing tests: active-content inputs route to the server sanitization path. E2E: ZIP plus individual downloads in user-entered order.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` and `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port the legacy range-input pattern (`papyr-reference/frontend/src/components/PageRangeInput.tsx`) with the DEC-077 and DEC-078 semantics change, and the server split service.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`, `pytest tests/ -v`, `npm run test:e2e`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(split): add order-preserving split tool`.

#### TL-05: JPG to PDF

**Files:**
- Create: `frontend/src/app/[locale]/jpg-to-pdf/page.tsx`, `backend/app/services/image_to_pdf_service.py`, `backend/app/routers/image_to_pdf.py`, `backend/app/services/paper_policy.py`

**Interfaces:**
- Consumes: TL-01, R-14
- Produces: hybrid browser-first conversion (DEC-011) with server fallback per the R-17 routing table; JPG, JPEG, PNG, and WebP acceptance with the "JPG to PDF" name retained (DEC-187); validation by actual bytes and resource limits (DEC-093); automatic per-image fitting, no cropping, EXIF orientation (DEC-041, DEC-082); Letter only for trusted US and CA edge codes, A4 otherwise, locale never decides paper (DEC-191); selected standard visible before processing (DEC-083); metadata-preservation disclosure (DEC-084); server downloads via signed URLs without popup-window reliance (DEC-170)

- [ ] **Step 1: Write the failing tests.** Paper-policy tests for US, CA, other, missing, and invalid codes plus locale independence (DEC-191). Image tests: JPG, PNG, and WebP accepted; malformed and oversized inputs rejected with safe errors; EXIF orientation respected; per-image page size and orientation; metadata disclosure present. Browser-path E2E with the shared foundations.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` and `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The paper-policy module consuming the trusted edge header (R-14), the image-to-PDF service using the approved server engines img2pdf plus Pillow (DEC-199, R-28; A5 brief), and the tool page.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`, `pytest tests/ -v`, `npm run test:e2e`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(jpg-to-pdf): add hybrid image to pdf tool`.

#### TL-06: PDF to JPG

**Files:**
- Create: `frontend/src/app/[locale]/pdf-to-jpg/page.tsx`, `backend/app/services/pdf_to_image_service.py`, `backend/app/routers/pdf_to_image.py`

**Interfaces:**
- Consumes: TL-01, R-06
- Produces: one automatic high-quality profile (R-06, DEC-039); transparency composited onto white deterministically in both paths (DEC-081); sequential rendering within the 16-MP per-page ceiling (DEC-015); page selections preserve duplicates and requested order with disambiguated outputs, ZIP, manifest, and names (DEC-186, DEC-078); server treats inputs as untrusted with isolation and bounded resources (DEC-092); no implied upscaling claim (DEC-039)

- [ ] **Step 1: Write the failing tests.** White-compositing fixture tests for both paths (DEC-081); duplicate and overlapping selection tests producing independent ordered outputs with disambiguated names (DEC-186); 16-MP ceiling enforcement; rasterization excludes active content but threat-classified inputs still block (DEC-092).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` and `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The render service using the approved server engine pypdfium2 with explicit white fill (DEC-199, R-28; A6 brief) and the tool page with sequential rendering.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`, `pytest tests/ -v`, `npm run test:e2e`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(pdf-to-jpg): add pdf to jpg tool`.

### Phase 5: Security and hardening

**Goal:** the maintained scanner, container hardening, Nginx enforcement, and dependency maintenance, completing the layered defenses (arch §17). The SEC-01 threat-classification and SEC-02 sanitization prerequisites are produced in Phase 3 and consumed by Phase 4 tool tasks.

**Gate entry:** Phase 3 complete (SEC-01 and SEC-02 prerequisites satisfied); R-10 and R-11 dispositions recorded.

**Gate exit:** scanner fail-closed behavior, container hardening, and Nginx enforcement verified (DEC-192, DEC-162).

#### SEC-03: Maintained malware scanner integration

**Files:**
- Create: `backend/app/security/scanner.py`, `deploy/scanner/clamd.conf`

**Interfaces:**
- Consumes: BE-02, SEC-01, R-10
- Produces: the approved scanner as a sidecar service with hourly signature updates, fail-closed admission on scanner unavailability or stale signatures for Merge and Split (DEC-192), scanner health monitored (DEC-171)

- [ ] **Step 1: Write the failing tests.** Tests asserting scanner-unavailable behavior fails closed for affected jobs, scanner results are one signal that never supports a malware-free claim, and rejection messages expose only safe categories (DEC-171, DEC-192).
- [ ] **Step 2: Verify the tests fail.** Run: `pytest tests/ -v`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The scanner client and the compose service with the approved budget (R-10), plus the fail-closed integration in the admission path.
- [ ] **Step 4: Verify the tests pass.** Run: `pytest tests/ -v`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `security(deploy): add maintained malware scanner with fail-closed admission`.

#### SEC-04: Container hardening profiles and compose integration

**Files:**
- Create: `scripts/check-compose.sh`
- Modify: `deploy/docker-compose.yml`, `backend/Dockerfile.production`

**Interfaces:**
- Consumes: FD-03
- Produces: per-service hardened profiles (non-root, read-only root with bounded tmpfs, cap_drop ALL plus minimal cap_add, no-new-privileges, pids and ulimits, bounded egress, healthchecks) modeled on the legacy baseline (`papyr-reference/deploy/docker-compose.yml`, `backend/Dockerfile.production`)

- [ ] **Step 1: Write the failing tests.** Create `scripts/check-compose.sh` asserting each service declares resource limits and a healthcheck, Redis and worker ports are never published, and the api service depends on healthy redis (DEC-162).
- [ ] **Step 2: Verify the tests fail.** Run: `scripts/check-compose.sh`. Expected: FAIL, services missing the required declarations.
- [ ] **Step 3: Write the minimal implementation.** Apply the hardening baseline to the new service set, including the worker profile with restricted egress to the internal network and the R2 endpoint only.
- [ ] **Step 4: Verify the tests pass.** Run: `scripts/check-compose.sh` and `docker compose -f deploy/docker-compose.yml config --quiet`. Expected: PASS, exit 0.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `security(deploy): add hardened service profiles`.

#### SEC-05: Nginx rate zones and request filtering

**Files:**
- Modify: `deploy/nginx/conf.d/production.conf`

**Interfaces:**
- Consumes: BE-10, SEC-04, R-11
- Produces: multi-zone rate limits on real client IPs from Cloudflare ranges (legacy `set_real_ip_from` pattern), request-size and body-timeout enforcement, sensitive-path and bot filtering, security headers, `server_tokens off`, health path unrate-limited (C4 brief)

- [ ] **Step 1: Write the failing tests.** Config-validation tests asserting the rate zones exist with the approved values, real-IP handling uses Cloudflare ranges, and the health path is excluded from rate limits.
- [ ] **Step 2: Verify the tests fail.** Run: the config validation script (for example `scripts/check-nginx.sh`). Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** Port and modernize the legacy production Nginx config with the R-11 values.
- [ ] **Step 4: Verify the tests pass.** Run: `scripts/check-nginx.sh`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `security(deploy): add nginx rate zones and filtering`.

#### SEC-06: Dependency and image maintenance pipeline

**Files:**
- Create: `backend/requirements.txt` (pinned), `deploy/deps-review.md` (procedure), `scripts/review-deps.sh`, CI security-scan job wiring

**Interfaces:**
- Consumes: FD-04
- Produces: the monthly dependency review procedure and the prompt critical-fix path (DEC-179); Trivy and SBOM generation as CI artifacts (legacy precedent in `papyr-reference/.github/workflows/deploy-vps.yml`); MVP dependencies limited to what the five tools require, excluding OCR and office stacks (DEC-010)

- [ ] **Step 1: Write the failing tests.** A CI-gate test asserting the dependency list contains no non-MVP packages (Tesseract, LibreOffice, Camelot, OpenCV families) and `scripts/review-deps.sh` documents the monthly cadence.
- [ ] **Step 2: Verify the test fails.** Run: `scripts/review-deps.sh --check`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The pinned dependency files and the review procedure.
- [ ] **Step 4: Verify the test passes.** Run: `scripts/review-deps.sh --check`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `chore(deps): add monthly review procedure and mvp-only pins`.

### Phase 6: Privacy, analytics, advertising, and support

**Goal:** privacy-reviewed analytics with leakage guards, decision-compliant ad placement, and the support surfaces.

**Gate entry:** Phases 2 and 4 complete; R-18 and R-20 dispositions recorded.

**Gate exit:** leakage tests, schema validation, ad placement checks, and support flows pass.

#### PT-01: Analytics schema, redaction, and leakage tests

**Files:**
- Create: `frontend/src/lib/analytics.ts`, `frontend/src/lib/analytics-schema.ts`, `frontend/src/__tests__/leakage.test.ts`

**Interfaces:**
- Consumes: SH-01, TL-01
- Produces: the allowed and prohibited field schema from the D3 brief (allowed: page, locale, referrer, UTM, tool, mode, coarse bands, funnel, timing, sanitized failure categories, outcomes, Web Vitals, ad presence where permitted; prohibited: contents, previews, rendered text, filenames, object keys, signed URLs, passwords, full error payloads, fingerprints); `beforeSend` redaction; opt-out; the raw-error string replaced by a closed enum (legacy leakage at `papyr-reference/frontend/src/lib/analytics.ts:1-69`); the automated leakage-test suite (DEC-025, arch §22.3)

- [ ] **Step 1: Write the failing tests.** Leakage tests: prohibited-string guards across event payloads, raw-error ban, coarse-band enforcement, redaction unit tests, schema-validation gate, and regional-behavior tests.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The analytics module with the closed schema, `beforeSend` redaction, and the opt-out flag; wire events into the shared tool foundations.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(analytics): add privacy-reviewed schema and leakage tests`.

#### PT-02: Advertising slots and placement guards

**Files:**
- Create: `frontend/src/components/ads/AdSlot.tsx`, `frontend/src/components/ads/placement.ts`

**Interfaces:**
- Consumes: SH-03, SH-08, R-18
- Produces: reserved-dimension banner or native slots (DEC-018) placed after the primary tool experience (DEC-151), separated from Download controls (DEC-131), lazy or async loaded, absent from critical status rendering (DEC-130); layout-shift guards

- [ ] **Step 1: Write the failing tests.** Placement tests asserting slots reserve stable dimensions, never render before the uploader on tool pages, never sit beside Download controls on result states, and status, legal, and support surfaces remain functional with scripts blocked (DEC-190).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The AdSlot component with the R-18-approved unit scope and the placement guard tests.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(ads): add non-intrusive placement with layout guards`.

#### PT-03: Contact form and result-problem report

**Files:**
- Create: `frontend/src/app/[locale]/contact/page.tsx` (complete), `frontend/src/components/support/ResultProblemReport.tsx`, `frontend/src/lib/support.ts`

**Interfaces:**
- Consumes: SH-08, BE-06, R-20
- Produces: the categorized contact form and the result-local problem report with the approved anti-spam stack (R-20), minimal data model (closed-enum category, length-limited message, optional email, sanitized page and locale context; no names, phones, or attachments), redaction-safe errors, locale-matched confirmations, delivery monitoring with counts only, no unsupportable response-time promises (DEC-046, DEC-050, DEC-117, DEC-120)

- [ ] **Step 1: Write the failing tests.** Form tests: each category submits; spam submissions are blocked by the anti-spam stack; error states never resurface submitted content; the result-problem report carries only the allowed fields (DEC-117); optional email is used only for the submitted matter (DEC-120).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The support surfaces wired to the R-20 delivery mechanism behind an interface, with retention rules documented.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(support): add contact form and result problem report`.

#### PT-04: Password handling surface verification

**Files:**
- Create: `frontend/src/components/PasswordInput.tsx` (corrected), `frontend/src/__tests__/password-handling.test.ts`

**Interfaces:**
- Consumes: TL-02..TL-06
- Produces: password entry only when required, per locked Merge file (DEC-074), memory-only handling, distinct wrong-password errors, no password material in logs, analytics, URLs, or storage (DEC-036, DEC-064)

- [ ] **Step 1: Write the failing tests.** Tests asserting password fields appear only for encrypted inputs, Merge validates each locked source independently, wrong-password errors are distinct from corrupt or unsupported files, and no password value reaches analytics, logs, or persistence (porting the legacy test pattern at `papyr-reference/frontend/src/components/__tests__/PasswordInput.test.ts`).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The corrected password component and per-file validation wiring in Merge.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(security): add password handling verification`.

### Phase 7: Monitoring, status, backups

**Goal:** observability without document content, an automatically derived public status page, Telegram alerts, and recoverable backups with a monthly restore drill.

**Gate entry:** Phases 3 and 5 complete; R-12 and R-13 dispositions recorded.

**Gate exit:** status derivation, alert relay, backup, and restore-drill procedures verified. Provider accounts remain owner-gated (G-4).

#### OP-01: Netdata monitoring and health signals

**Files:**
- Create: `deploy/monitoring/netdata-compose.yml` (or compose integration), `deploy/monitoring/health-signals.md`, `scripts/check-monitoring.sh`

**Interfaces:**
- Consumes: SEC-04, BE-06
- Produces: Netdata coverage for API, queue, workers, Redis, engines, storage integration, cleanup health, and public endpoints without document content (DEC-182); the noise-resistant health-signal definitions used by OP-02

- [ ] **Step 1: Write the failing tests.** Config tests asserting each monitored surface has a defined health signal and that no signal derives from document contents or filenames (DEC-182, DEC-175).
- [ ] **Step 2: Verify the tests fail.** Run: `scripts/check-monitoring.sh`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The monitoring compose integration and the health-signal document.
- [ ] **Step 4: Verify the tests pass.** Run: `scripts/check-monitoring.sh`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `chore(ops): add netdata coverage and health signals`.

#### OP-02: Public status page and noise-resistant derivation

**Files:**
- Create: `frontend/src/app/[locale]/status/page.tsx` (complete), `frontend/src/lib/status.ts`

**Interfaces:**
- Consumes: OP-01, SH-08
- Produces: Vercel-hosted status page updated automatically from approved health signals (DEC-161), remaining useful during a VPS outage (DEC-119), N-consecutive-failure across at least two regions before degraded or down (C5 brief), wording that distinguishes observable availability from guarantees (DEC-161), no claim of complete infrastructure independence (DEC-119)

- [ ] **Step 1: Write the failing tests.** Signal-derivation tests: a transient single-region failure does not flip state; a multi-region sustained failure does; the page renders without depending on the VPS health endpoint (DEC-119).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The status page and the derivation module over the OP-01 signal contract.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(status): add automatically derived public status page`.

#### OP-03: Telegram alert relay

**Files:**
- Create: `deploy/monitoring/telegram-relay.py` (or the approved mechanism), `deploy/monitoring/alerts.md`, `scripts/check-telegram-relay.sh`

**Interfaces:**
- Consumes: OP-01
- Produces: the incident-alert contract (severity info, warning, critical; dedup keys with open and resolved transitions; 30 to 60 minute re-notify; payload rules per DEC-180); delivery failure visible within monitoring; bot credentials per the secret policy (DEC-176)

- [ ] **Step 1: Write the failing tests.** Create `scripts/check-telegram-relay.sh` asserting deduplication, severity ordering, payload prohibitions (no files, filenames, passwords, signed URLs, or object keys; DEC-180), and delivery-failure visibility.
- [ ] **Step 2: Verify the tests fail.** Run: `scripts/check-telegram-relay.sh`. Expected: FAIL, relay and contract absent.
- [ ] **Step 3: Write the minimal implementation.** The relay and the alert contract document.
- [ ] **Step 4: Verify the tests pass.** Run: `scripts/check-telegram-relay.sh`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(ops): add telegram alert relay`.

#### OP-04: Backups and monthly restore drill

**Files:**
- Create: `deploy/backup/restic-backup.sh`, `deploy/backup/restore-drill.md`, `deploy/runbook-vps.md` (backup sections)

**Interfaces:**
- Consumes: SEC-04, BE-04, R-13
- Produces: restic to the S3-compatible destination (legacy pattern `papyr-reference/docs/runbook-vps.md` section 7), scope per DEC-173 (deployment tree minus ephemeral state, Redis exclusion by default per the C1 task-loss tolerance), encrypted repository, scheduled daily run, isolated monthly restore verification per DEC-181 with recorded outcomes and no credential exposure

- [ ] **Step 1: Write the failing tests.** Dry-run tests asserting the backup scope excludes ephemeral workspaces, uploads, results, signed URLs, and queue payloads (DEC-173), and the restore drill template records outcomes without credentials (DEC-181).
- [ ] **Step 2: Verify the tests fail.** Run: `bash -n deploy/backup/restic-backup.sh` and the scope test. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The backup script, scope manifest, and drill procedure with the approved R-13 values.
- [ ] **Step 4: Verify the tests pass.** Run: the scope test and `bash -n`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(ops): add backups and monthly restore drill`.

### Phase 8: SEO and URL migration

**Goal:** localized slugs, the legacy URL disposition map, and consistent per-locale SEO output.

**Gate entry:** Phases 2 and 4 complete; R-15, R-16, and R-25 dispositions recorded.

**Gate exit:** redirect map, 410 dispositions, hreflang, sitemap, and locale-less entry verified.

#### SEO-01: Slug table and legacy URL disposition inventory

**Files:**
- Create: `docs/seo/slug-table.md`, `docs/seo/legacy-url-inventory.md`, `scripts/check-seo-inventory.sh`

**Interfaces:**
- Consumes: SH-04, R-15, R-16
- Produces: the approved EN, ES, and ID slug table and the complete legacy URL inventory with retain, update, redirect, 410, noindex, or removal dispositions per URL (DEC-127, DEC-194)

- [ ] **Step 1: Write the failing tests.** Inventory tests asserting every legacy sitemap URL (baseline: `papyr-reference/frontend/src/app/sitemap.ts:21-47`, 16 indexable URLs) has a disposition and every disposition maps to a real mechanism.
- [ ] **Step 2: Verify the tests fail.** Run: `scripts/check-seo-inventory.sh`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The approved slug table and inventory from the R-15, R-16, and R-25 dispositions.
- [ ] **Step 4: Verify the tests pass.** Run: `scripts/check-seo-inventory.sh`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `docs(seo): add slug table and url disposition inventory`.

#### SEO-02: Redirect map and localized 410 implementation

**Files:**
- Create: `frontend/src/middleware.ts` (redirect map integration), `frontend/src/app/[locale]/not-found.tsx` (410 surface)

**Interfaces:**
- Consumes: SEO-01
- Produces: direct legacy-to-locale-prefixed 301 redirects, locale-less entry 302 or 307 per DEC-047, intentional localized 410 Gone for deferred tool URLs with an explanation and links to live tools (DEC-194), 410 URLs excluded from sitemap, navigation, canonicals, and internal links

- [ ] **Step 1: Write the failing tests.** Redirect tests for every row of the disposition map: 301 targets resolve, 410 URLs return 410 with the localized explanation and no internal links to them (DEC-194), no redirect chains or soft 404s (DEC-127).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` and `npm run test:e2e`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The redirect map in middleware and the 410 surface.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test` and `npm run test:e2e`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(seo): add redirect map and localized 410`.

#### SEO-03: hreflang, canonical, sitemap, and locale-less entry verification

**Files:**
- Modify: `frontend/src/app/sitemap.ts`, `frontend/src/app/robots.ts`, per-route metadata

**Interfaces:**
- Consumes: SEO-01, SH-01
- Produces: per-locale sitemap with hreflang alternates and real lastmod, self-referencing absolute canonicals, bidirectional self-referencing hreflang with no `es-419`, `x-default` to EN (B4 brief); crawler behavior not redirected unpredictably (DEC-047)

- [ ] **Step 1: Write the failing tests.** Output tests asserting sitemap entries, canonical, and hreflang consistency across all three locales and that locale-less entry avoids loops and duplicate indexing.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The sitemap, robots, and metadata generation from the catalog and the slug table.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test` and `npm run build`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(seo): add per-locale sitemap, canonical, and hreflang`.

### Phase 9: Content, legal, and blog

**Goal:** decision-true legal copy after qualified review, and the gated MDX blog pipeline with fifteen launch articles.

**Gate entry:** Phases 2, 4, and 8 complete; the R-19 (legal review) and R-21 (gateway documentation) gates passed; R-22 and R-24 dispositions recorded.

**Gate exit:** legal pages reviewed and localized; the blog pipeline passes its blocking gates; 15 launch articles verified.

#### CT-01: Legal page copy baseline (EN)

**Files:**
- Create: `frontend/src/i18n/messages/en/legal.json` (Privacy, Terms, Cookies/Advertising copy)

**Interfaces:**
- Consumes: R-19 gate, R-24
- Produces: the EN disclosure inventory from the D2 brief (local vs server processing, automatic fallback, R2, providers, analytics boundaries, advertising behavior, user controls, contact channels; DEC-045, DEC-168); no compliance claims (DEC-022, DEC-190); effective dates and version history (DEC-045); corrected "no tracking" and "no personal data" claims (R-24)

- [ ] **Step 1: Write the failing tests.** Copy-content tests asserting the required disclosure topics are present, prohibited claims (no-tracking, no-personal-data, compliance-style) are absent, and every provider and retention fact matches the accepted model.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the EN copy** from the R-24-approved wording and the D2 disclosure inventory, with the review record referenced.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(legal): add english legal copy baseline`.

#### CT-02: Legal page localization and version history

**Files:**
- Create: `frontend/src/i18n/messages/es/legal.json`, `frontend/src/i18n/messages/id/legal.json`

**Interfaces:**
- Consumes: CT-01
- Produces: controlled ES and ID localization of the reviewed EN base (D2 brief), self-consistent with the R-18 advertising outcome, with version history and effective dates (DEC-045, DEC-110)

- [ ] **Step 1: Write the failing tests.** Parity tests asserting all three locales carry the same disclosure topics and version metadata.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Write the localized copies** as intentional localization, not literal machine translation (DEC-048, DEC-124).
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(legal): add localized legal pages`.

#### CT-03: Blog MDX pipeline and gates

**Files:**
- Create: `frontend/content/blog/` MDX store, `frontend/src/lib/blog/schema.ts`, `frontend/mdx-components.tsx`, `.github/workflows/blog-automation.yml`, `frontend/src/lib/blog/provider-adapter.ts`, `frontend/src/app/[locale]/blog/` content layer

**Interfaces:**
- Consumes: R-21 gate (hard blocker), SEO-01
- Produces: version-controlled MDX (DEC-049), `@next/mdx` with a strict typed frontmatter schema and component allowlist, blocking quality gates that fail closed (factual support, duplication and cannibalization, search intent, originality, language quality, metadata, internal links, unsafe claims, policy violations, malformed MDX; DEC-048), a scheduled content-bot workflow producing gate-passing PRs through the normal build path (E2 brief), kill switch and pause thresholds (DEC-053), the provider adapter behind an interface with the R-21-resolved contract fields (DEC-193, DEC-196), and reliability controls (bounded request timeout, finite retry with backoff, idempotency where supported, one bounded publication workflow, repeated-failure pause, kill switch) separate from spending controls (DEC-196)

- [ ] **Step 1: Write the failing tests.** Gate tests: each blocking gate fails closed on a violating fixture; malformed MDX fails the build without affecting the deployed site; the allowlist rejects unknown components; the kill-switch flag and pause thresholds stop publication; the provider adapter injects no credentials into MDX, logs, or artifacts (DEC-193, DEC-196).
- [ ] **Step 2: Verify the tests fail.** Run: `npm test` and `npm run build`. Expected: FAIL.
- [ ] **Step 3: Write the minimal implementation.** The content layer, schema, allowlist, and workflow. The provider adapter implements only the R-21-resolved contract fields; unresolved fields keep their stop condition in force.
- [ ] **Step 4: Verify the tests pass.** Run: `npm test` and `npm run build`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(blog): add mdx pipeline with blocking gates`.

#### CT-04: Fifteen launch articles

**Files:**
- Create: `frontend/content/blog/{en,es,id}/<slug>.mdx` (15 files)

**Interfaces:**
- Consumes: CT-03, R-22, R-25
- Produces: five topics, one per tool, each intentionally localized into EN, ES, and ID (DEC-052, DEC-121); truthful publication and update dates (DEC-113); articles pass every CT-03 gate

- [ ] **Step 1: Write the failing tests.** Content tests asserting 15 articles exist, each topic has three locale versions, dates are truthful with no future dates, and every article passes the CT-03 gate suite.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Generate the articles** through the approved workflow for the R-22-approved topics, subject to the R-25 demand evidence, with each generation run executed under the G-5 owner gate (no authenticated gateway call is authorized by this plan).
- [ ] **Step 4: Verify the tests pass.** Run: `npm test` and `npm run build`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(blog): add fifteen launch articles`.

### Phase 10: Pre-launch verification and launch

**Goal:** the five-tool trilingual launch gate and coordinated production activation.

**Gate entry:** all earlier phases complete; R-23 and R-26 dispositions recorded.

**Gate exit:** launch gate passes; the owner authorizes launch (G-3). Launch is direct production activation without a beta label (DEC-096, DEC-140).

#### VL-01: Five-tool trilingual E2E gate

**Files:**
- Create: `frontend/e2e/five-tools.spec.ts`, `frontend/e2e/helpers.ts`

**Interfaces:**
- Consumes: TL-01..TL-06
- Produces: complete tool flows across the five tools in EN, ES, and ID covering the happy path, auto-download and manual-download fallback, routing transitions, error states, cancellation (queued only), refresh recovery, and reset (DEC-027, DEC-029, DEC-068, DEC-072)

- [ ] **Step 1: Write the failing E2E tests** for the full matrix.
- [ ] **Step 2: Verify the tests fail.** Run: `npm run test:e2e`. Expected: FAIL on the not-yet-complete flows.
- [ ] **Step 3: Fix the surfaced flows** until the suite is green, without changing approved behavior.
- [ ] **Step 4: Verify the tests pass.** Run: `npm run test:e2e`. Expected: PASS across the matrix.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `test(e2e): five-tool trilingual gate`.

#### VL-02: Accessibility verification program

**Files:**
- Create: `frontend/axe-config.js`, `docs/accessibility/exceptions-register.md`
- Modify: `frontend/package.json` (adds the `test:a11y` script and the axe-core dev dependency)

**Interfaces:**
- Consumes: VL-01
- Produces: axe-core in CI with the WCAG 2.2 target-size rule enabled, Lighthouse on representative routes, manual keyboard completion of every tool flow, representative AT passes (NVDA, JAWS, VoiceOver, TalkBack), and the documented exceptions register with impact and remediation (DEC-062, B2 brief)

- [ ] **Step 1: Write the failing checks.** Add the `test:a11y` script to `frontend/package.json` running axe-core with the axe-config, plus a manual keyboard checklist for every tool flow in the three locales.
- [ ] **Step 2: Verify the checks fail.** Run: `npm run test:a11y -- axe`. Expected: FAIL with reported violations.
- [ ] **Step 3: Fix the surfaced violations** and complete the manual keyboard and AT passes, recording exceptions in the register.
- [ ] **Step 4: Verify the checks pass.** Run: `npm run test:a11y -- axe` and the manual checklist. Expected: PASS with only documented exceptions.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(a11y): add accessibility program and exceptions register`.

#### VL-03: Rendered visual verification and baseline comparison

**Files:**
- Create: `frontend/e2e/visual.spec.ts`, `docs/verification/visual-baseline.md`, `scripts/check-contrast.sh`

**Interfaces:**
- Consumes: VL-01, R-23
- Produces: side-by-side comparison of key surfaces (homepage, one tool page, navbar, footer) against the legacy clone (DEC-143); contrast re-verification of the documented token combinations with a contrast tool (UX §21.12); `@theme inline` emission verification (UX §21.19); viewport coverage 375, 768, 1280, and 1440 (B5 brief)

- [ ] **Step 1: Write the failing visual checks.** Contrast pairs in `scripts/check-contrast.sh`, rendered surface comparisons in `frontend/e2e/visual.spec.ts`, and the `@theme` emission check.
- [ ] **Step 2: Verify the checks fail.** Run: `npm run test:e2e -- visual` and `scripts/check-contrast.sh`. Expected: FAIL.
- [ ] **Step 3: Correct the surfaced deviations** within the approved-change boundaries (DEC-143).
- [ ] **Step 4: Verify the checks pass.** Run: `npm run test:e2e -- visual` and `scripts/check-contrast.sh`. Expected: PASS with the R-23 prompts applied.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `test(visual): rendered baseline verification`.

#### VL-04: Core Web Vitals and performance verification

**Files:**
- Create: `frontend/lighthouserc.js`, `docs/verification/performance.md`
- Modify: `frontend/package.json` (adds the `test:perf` script and the Lighthouse CI dev dependency)

**Interfaces:**
- Consumes: VL-03
- Produces: Lighthouse runs on representative routes with results recorded against the R-27 measures and targets approved by DEC-200 and DEC-201; ad-slot layout stability verified (DEC-018)

- [ ] **Step 1: Write the failing checks.** Add the `test:perf` script to `frontend/package.json` running Lighthouse CI with `frontend/lighthouserc.js`, plus the ad-slot layout-shift guard.
- [ ] **Step 2: Verify the checks fail.** Run: `npm run test:perf -- lighthouse`. Expected: FAIL against the R-27 measures and targets approved by DEC-200 and DEC-201.
- [ ] **Step 3: Fix the surfaced regressions** within approved-change boundaries.
- [ ] **Step 4: Verify the checks pass.** Run: `npm run test:perf -- lighthouse`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `perf: core web vitals verification`.

#### VL-05: Pre-launch smoke, rollback readiness, activation checklist

**Files:**
- Create: `docs/verification/launch-checklist.md`, `deploy/runbook-vps.md` (deploy and rollback sections), `docs/verification/smoke.md`, `scripts/check-launch.sh`

**Interfaces:**
- Consumes: VL-01..VL-04, OP-02
- Produces: the coordinated activation checklist covering deployment, redirects, indexing, monitoring, support, and status (DEC-140); rollback readiness per DEC-178; pre-deployment verification and post-deployment smoke procedures per DEC-160 and DEC-177; launch is a manual owner-authorized action (G-3)

- [ ] **Step 1: Write the checklist and smoke tests** covering health, status derivation, redirects, the trilingual gate, and rollback-to-previous-image steps.
- [ ] **Step 2: Verify the checklist items fail** on the not-yet-deployed state. Run: `scripts/check-launch.sh`. Expected: FAIL with missing items listed.
- [ ] **Step 3: Complete the checklist** as deployment preparation proceeds under G-3.
- [ ] **Step 4: Verify the checklist passes.** Run: `scripts/check-launch.sh`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `docs(launch): activation checklist and rollback readiness`.

### Phase 11: Post-launch operations

**Goal:** the 90-day dashboard, monthly cadences, and next-tool planning.

**Gate entry:** launch authorized and complete (G-3).

**Gate exit:** dashboard live; cadences running; next-tool planning initiated per DEC-141.

#### PO-01: 90-day operating dashboard

**Files:**
- Create: `docs/operations/90-day-dashboard.md`, `scripts/check-dashboard.sh`

**Interfaces:**
- Consumes: OP-01, PT-01
- Produces: measurement of job success and failure, processing and queue latency, uptime, Core Web Vitals, organic entrances, tool usage distribution, and completed downloads, distinguishing browser-local from server jobs without document content, against the R-27 measures and targets approved by DEC-200 and DEC-201 (DEC-024)

- [ ] **Step 1: Write the failing dashboard tests** asserting each R-27 metric is produced from sanctioned signals only (no document content).
- [ ] **Step 2: Verify the tests fail.** Run: `scripts/check-dashboard.sh`. Expected: FAIL.
- [ ] **Step 3: Implement the dashboard collection** from OP-01 and PT-01 signals.
- [ ] **Step 4: Verify the tests pass.** Run: `scripts/check-dashboard.sh`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(ops): 90-day operating dashboard`.

#### PO-02: Monthly dependency review cadence

**Files:**
- Create: `docs/operations/dependency-review-log.md`

**Interfaces:**
- Consumes: SEC-06
- Produces: the monthly review record covering native processors, container base images, frontend and backend packages, the CI provider workflow definitions (proposal: GitHub Actions), and malware signatures (DEC-179); critical fixes handled promptly outside the monthly cycle

- [ ] **Step 1: Write the failing check** asserting the review log is current and every critical advisory has a tracked disposition.
- [ ] **Step 2: Verify the check fails.** Run: `scripts/review-deps.sh --log`. Expected: FAIL.
- [ ] **Step 3: Run the monthly review** and record dispositions.
- [ ] **Step 4: Verify the check passes.** Run: `scripts/review-deps.sh --log`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `chore(deps): monthly dependency review`.

#### PO-03: Monthly restore verification

**Files:**
- Create: `docs/operations/restore-drill-log.md`, `scripts/check-restore.sh`

**Interfaces:**
- Consumes: OP-04
- Produces: the monthly isolated restore record without production impact or credential exposure (DEC-181); repeated failures trigger an alert and corrective work

- [ ] **Step 1: Write the failing check** asserting the drill log is current.
- [ ] **Step 2: Verify the check fails.** Run: `scripts/check-restore.sh`. Expected: FAIL.
- [ ] **Step 3: Execute the drill** per the OP-04 procedure under G-4 as needed.
- [ ] **Step 4: Verify the check passes.** Run: `scripts/check-restore.sh`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `chore(ops): monthly restore verification`.

#### PO-04: Post-launch blog cadence and pause controls

**Files:**
- Modify: `.github/workflows/blog-automation.yml` (cadence config)

**Interfaces:**
- Consumes: CT-03
- Produces: at most one coordinated trilingual topic per day with the UTC boundary (DEC-124, DEC-053); skip rather than weaken gates; kill switch and pause thresholds active; cadence may pause for stability work (DEC-141)

- [ ] **Step 1: Write the failing cadence tests.** At most one set per day, skip behavior on gate failure, kill-switch and pause-threshold behavior.
- [ ] **Step 2: Verify the tests fail.** Run: `npm test`. Expected: FAIL.
- [ ] **Step 3: Implement the cadence controls.**
- [ ] **Step 4: Verify the tests pass.** Run: `npm test`. Expected: PASS.
- [ ] **Step 5: Review and commit boundary.** Commit. Suggested subject: `feat(blog): post-launch cadence and pause controls`.

#### PO-05: Legacy tool restoration planning

**Files:**
- Create: `docs/plan/next-tool-plan.md`

**Interfaces:**
- Consumes: R-25, R-26
- Produces: a restoration plan for the next legacy tool chosen from demand, readiness, complexity, cost, and the approval gate (DEC-094, DEC-141); each candidate stays subject to DEC-054 through DEC-057

- [ ] **Step 1: Write the planning document** comparing the candidate tools against the DEC-094 criteria with the owner's demand evidence.
- [ ] **Step 2: Verify the document** covers each DEC-094 criterion with no pre-approval of scope.
- [ ] **Step 3: Present the plan to the owner** for a separate decision.
- [ ] **Step 4: Review and commit boundary.** Commit. Suggested subject: `docs(plan): next legacy tool restoration plan`.

## 9. Requirements-to-Task Traceability Matrix

### 9.1 Product and UX Design Specification to phases and tasks

| UX spec section | Requirement area | Phase and tasks |
|---|---|---|
| 1-4 | Status, scope, sources, precedence | P0, PR-01..PR-03, this plan |
| 5 | Product goals | Global Constraints; SH-07; CT-01; VL-01 |
| 6 | Users | Global Constraints; SH-07 |
| 7 | Launch scope | VL-05; P0 gates |
| 8.1-8.5 | IA, routes, navigation, catalog, related tools | SH-01, SH-04, SH-05, SH-06, SEO-01 |
| 9 | Localization | SH-01, SH-05, TL-01, VL-01, CT-02, CT-04 |
| 10 | Existing visual baseline | SH-02, SH-03, SH-05, SH-06, SH-07, VL-03 |
| 11 | Shell and homepage | SH-03, SH-05, SH-06, SH-07 |
| 12.0 | Shared flow anatomy | TL-01 |
| 12.1 | Compress flow | TL-02 |
| 12.2 | Merge flow | TL-03 |
| 12.3 | Split flow | TL-04 |
| 12.4 | JPG to PDF flow | TL-05 |
| 12.5 | PDF to JPG flow | TL-06 |
| 13 | Shared states, downloads, expiry, cancellation, honest progress | TL-01, BE-06, BE-07, BE-09 |
| 14 | Advertising placement | PT-02 |
| 15.1-15.6 | Tool pages as content, legal, support, status, roadmap, blog | CT-01, CT-02, CT-03, PT-03, OP-02, SH-08 |
| 16 | Responsive and accessibility | VL-02, SH-01, SH-03, TL-01 |
| 17 | Analytics and privacy UX boundaries | PT-01 |
| 18 | Error and recovery behavior | TL-01, BE-06, BE-10, PT-03 |
| 19 | SEO and content migration constraints | SEO-01, SEO-02, SEO-03 |
| 20 | Acceptance criteria | VL-01..VL-05, PO-01 |
| 21.1-21.21 | Unresolved items | Section 6 (R-03..R-24) |
| 22 | Relationship to architecture | P0, FD-05 |

### 9.2 Technical Architecture Specification to phases and tasks

| Arch spec section | Requirement area | Phase and tasks |
|---|---|---|
| 1 | Scope, status, authority | P0, this plan |
| 2 | System context and topology | FD-03, BE-03, BE-05, SEC-04 |
| 3 | Monorepo boundaries | PR-01, PR-02, FD-01..FD-05 |
| 4 | Vercel Next.js frontend | SH-01..SH-08, TL-01, PT-01, PT-02 |
| 5 | Cloudflare edge | R-14, SEC-05, SEO-02 |
| 6 | VPS Nginx and FastAPI | BE-01..BE-10, SEC-05 |
| 7 | Docker Compose services | FD-03, SEC-04 |
| 8 | Redis durable minimal-metadata queue | BE-04, BE-05, BE-07 |
| 9 | Bounded workers and fair scheduling | BE-05, BE-10, R-07, R-08 |
| 10 | Browser and server routing | TL-01, R-17, TL-02..TL-06 |
| 11 | Five-tool processing responsibilities | TL-02..TL-06 |
| 12 | R2 lifecycle and one-hour deadline | BE-03, BE-07 |
| 13 | Task state machine and refresh recovery | BE-06, TL-01 |
| 14 | API capability and limits contract | BE-08, BE-10 |
| 15 | Signed downloads | BE-09, TL-05 |
| 16 | Availability and failure isolation | BE-06, OP-02, VL-05 |
| 17 | Validation, sanitization, malware, hardening | BE-02, SEC-01..SEC-05 |
| 18 | Secrets, access, logging, backups | BE-01, OP-04, PR-02, G-8 |
| 19 | CI gate, manual deployment, rollback | FD-04, VL-05, G-3 |
| 20 | Monitoring, status, Telegram | OP-01..OP-03 |
| 21 | Dependency maintenance | SEC-06, PO-02 |
| 22 | Testing strategy | FD-04, TL-01..TL-06, VL-01, VL-02, PT-01 |
| 23 | Data classification and prohibited data | BE-01, BE-04, BE-07, PT-01, OP-03 |
| 24 | Operational acceptance criteria | VL-05, PO-01 |
| 25.1-25.4 | Research gates and unresolved choices | Section 6 (R-03..R-28) |
| 26 | Self-review record | this plan (Section 10) |
| Appendix A | Decision map | this plan (Section 9.3) |
| Appendix B | Legacy source evidence index | PR-02, FD-01..FD-05 |

### 9.3 Decisions DEC-001 through DEC-201 to phases and tasks

| Decision cluster | Decisions (all listed) | Phase and tasks |
|---|---|---|
| Rebuild mandate and document governance | DEC-001, DEC-002, DEC-003, DEC-006, DEC-021, DEC-026, DEC-183, DEC-184, DEC-185, DEC-188, DEC-197 | P0, PR-01, PR-02, this plan |
| Business model and monetization | DEC-005, DEC-018, DEC-022, DEC-102, DEC-105, DEC-106, DEC-129, DEC-130, DEC-131, DEC-135, DEC-136, DEC-190 | PT-02, CT-01, VL-04, G-6 |
| Users, promise, and positioning | DEC-007, DEC-008, DEC-101, DEC-110, DEC-111, DEC-112, DEC-132, DEC-133, DEC-134, DEC-138, DEC-139, DEC-140 | SH-07, CT-01, VL-05 |
| Catalog and launch scope | DEC-009, DEC-010, DEC-094, DEC-107, DEC-108, DEC-109, DEC-126, DEC-128, DEC-141 | Global Constraints, FD-01, TL-02..TL-06, PO-05 |
| Processing model and limits | DEC-011, DEC-014, DEC-015, DEC-030, DEC-031, DEC-034, DEC-035, DEC-039, DEC-041, DEC-065, DEC-066, DEC-073, DEC-189 | TL-01..TL-06, BE-05, BE-08, R-03, R-04, R-06, R-17 |
| Accounts, privacy, and retention | DEC-012, DEC-013, DEC-032, DEC-067, DEC-070, DEC-075, DEC-166, DEC-168 | BE-03, BE-07, TL-01, CT-01 |
| Queue, workers, and Redis | DEC-019, DEC-020, DEC-035, DEC-137, DEC-162, DEC-174, DEC-189 | BE-04, BE-05, BE-10, R-07, R-08, R-09 |
| Analytics and data boundaries | DEC-024, DEC-025, DEC-042, DEC-084, DEC-085, DEC-104, DEC-117, DEC-120, DEC-126, DEC-175 | PT-01, BE-01, OP-01, R-27 |
| Passwords and encryption | DEC-036, DEC-064, DEC-074 | PT-04, TL-02..TL-06, SEC-01 |
| Tool-specific behavior | DEC-037, DEC-038, DEC-040, DEC-043, DEC-077, DEC-078, DEC-079, DEC-080, DEC-081, DEC-082, DEC-086 (superseded), DEC-087 (superseded), DEC-090, DEC-091, DEC-092, DEC-093, DEC-186, DEC-187, DEC-195 | TL-02..TL-06, SEC-02, R-04, R-05, R-06 |
| SEO, localization, and content | DEC-004 (expanded by DEC-115 and DEC-118), DEC-023, DEC-044, DEC-045, DEC-046, DEC-047, DEC-048, DEC-049, DEC-050, DEC-051, DEC-052, DEC-053, DEC-113, DEC-114, DEC-115, DEC-118, DEC-121, DEC-122, DEC-123, DEC-124, DEC-125, DEC-127, DEC-193, DEC-194, DEC-196 | SEO-01..SEO-03, CT-01..CT-04, SH-01, SH-07, PT-03, R-15, R-16, R-18, R-21, R-22, R-25 |
| UI and UX baseline | DEC-028, DEC-029, DEC-033, DEC-062, DEC-068, DEC-142, DEC-143, DEC-144, DEC-145, DEC-146, DEC-147, DEC-148, DEC-149, DEC-150, DEC-151, DEC-152, DEC-153, DEC-154, DEC-155, DEC-156, DEC-157, DEC-158 | SH-02..SH-07, TL-01, VL-02, R-23 |
| Design governance gates | DEC-054, DEC-055, DEC-056, DEC-057, DEC-058, DEC-059, DEC-060, DEC-061 (superseded), DEC-063 (superseded) | P0, Section 6, PR-03 |
| Infrastructure, deployment, and operations | DEC-016, DEC-017, DEC-095, DEC-096, DEC-097, DEC-098, DEC-099, DEC-159, DEC-160, DEC-162, DEC-164, DEC-165, DEC-170, DEC-172, DEC-176, DEC-177, DEC-178, DEC-179, DEC-181 | FD-03, FD-04, BE-08, BE-09, OP-04, VL-05, G-1..G-11 |
| Security | DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171, DEC-192 | SEC-01..SEC-05 |
| Availability and failure isolation | DEC-163, DEC-167 | TL-01, BE-08, OP-02 |
| Monitoring, status, and alerts | DEC-116, DEC-119, DEC-161, DEC-180, DEC-182 | OP-01..OP-03 |
| Backups | DEC-173, DEC-181 | OP-04, PO-03 |
| Paper policy | DEC-083, DEC-085, DEC-089, DEC-191 | TL-05, R-14 |
| Session recovery and cancellation | DEC-069, DEC-071, DEC-072 | BE-05, BE-06, TL-01 |
| Blog automation | DEC-048, DEC-049, DEC-051, DEC-052, DEC-053, DEC-113, DEC-121, DEC-124, DEC-193, DEC-196 | CT-03, CT-04, PO-04, R-21, R-22 |
| Launch and schedule | DEC-027, DEC-096, DEC-100, DEC-103, DEC-118, DEC-140 | VL-01..VL-05, P0 gates |
| Plan and owner decisions after DEC-197 | DEC-198 (repository root), DEC-199 (engine and queue matrix), DEC-200 (90-day measures), DEC-201 (final R-27 numeric targets) | Section 1, Section 6 (R-01, R-27, R-28), PR-01, PR-03, PO-01, VL-04 |

Coverage note: every accepted decision DEC-001 through DEC-201 maps to at least one phase or task. Superseded entries (DEC-061, DEC-063, DEC-086, DEC-087) are history and are governed by their successors (DEC-066, DEC-090). DEC-004 is expanded in effect by DEC-115 and DEC-118. DEC-200 approved the 90-day measures and DEC-201 supplied the final numeric fields (p95 queue wait at or below 60 seconds per tool; p95 server processing at or below 180 seconds per tool; p50 observed and reported per tool without a separate target; each launch tool at or above 5 percent of total completed downloads during days 29 through 90), fully resolving R-27 and the DEC-024 exact-numeric precondition. The plan itself remains unapproved pending explicit owner approval; no phase may start before that approval. Research findings from the 25 briefs are design inputs carried through the resolution register (including the R-28 engine and queue matrix approved by DEC-199), not standalone requirements (DEC-054, DEC-057).

## 10. Plan Verification and Self-Review

The following checks are performed on this plan before it is presented for approval:

1. **Header check:** the plan starts with the required header block from the writing-plans skill, including the agentic-workers note, Goal, Architecture, Tech Stack, and Global Constraints.
2. **Placeholder scan:** the plan contains no TODO, TBD, FIXME, XXX, lorem ipsum, or WIP tokens. Open choices are recorded as named resolution items R-01 through R-28 with stop conditions, following the specification convention (arch §26.1).
3. **Benchmark scan:** the plan contains no benchmark program, corpus, matrix, comparative quality or performance study, or quality-score obligation (DEC-066). All verification commands are functional tests, config checks, or CI gates.
4. **Authorization scan:** no task in this plan performs VPS access, deployment, provider authentication, gateway calls, or git remote operations. These are separated in Section 7 as owner-gated actions.
5. **Traceability check:** Section 9 maps every specification section and every decision DEC-001 through DEC-201 to phases and tasks.
6. **Boundary check:** every task ends at a review and commit boundary; commit boundaries are atomic units to be created after the owner authorizes git operations at Phase 0 (G-1).
7. **TDD check:** every implementation task follows the sequence write failing test, verify fail, minimal implementation, verify pass, review and commit boundary.
8. **Legacy cleanliness:** `papyr-reference/` remains unchanged; its HEAD is `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` and `git status --porcelain` is empty.
9. **No implementation authorization:** approval of this plan authorizes execution of the plan's tasks only. Separately gated actions in Section 7 remain individually owner-authorized.
10. **Root path consistency:** all implementation paths are relative to the workspace root per DEC-198; `papyr-rebuild/` appears only as a historical reference to the superseded proposal, never as an implementation path.
11. **Engine approval consistency:** the approved R-28 selections appear as approved selections with their normative risks, scope boundaries, material conditions, and fallbacks; no proposal-framing remains for the approved items.
12. **DEC-024 completeness and approval status:** DEC-200 approved the 90-day measures and DEC-201 supplied the final numeric fields (p95 queue wait at or below 60 seconds per tool; p95 server processing at or below 180 seconds per tool; p50 observed per tool without a separate target; each launch tool at or above 5 percent of total completed downloads during days 29 through 90), fully resolving R-27 and the DEC-024 exact-numeric precondition. This plan remains unapproved pending explicit owner approval; no phase may start before that approval.
