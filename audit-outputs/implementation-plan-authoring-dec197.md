# Papyr Rebuild: Implementation Plan Authoring Evidence (DEC-197)

| Field | Value |
|---|---|
| Document ID | PPR-PLN-EVID-001 |
| Title | Evidence record for authoring the master implementation plan under DEC-197 |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent; planning and documentation task) |
| Status | Complete; primary deliverable is the master implementation plan |
| Governing decisions | DEC-060, DEC-197 (planning only; no implementation authorization); DEC-054 through DEC-057 (research and approval gates); DEC-066 (no benchmark program); DEC-143 (existing UI baseline) |
| Primary deliverables | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (canonical plan); this file (planning evidence) |
| Task constraints | Read, Grep, Glob, filesystem listing, and Write/Edit for the two assigned outputs only; read-only git status for `papyr-reference`; no web research, builds, tests, installs, servers, browser runtime, VPS/SSH, provider calls, or remote operations |

---

## 1. Method

1. Read `AGENTS.md` in full (governing orchestrator rules).
2. Read the complete living decision log `papyr-rebuild-decisions.md` in full (2,343 lines, DEC-001 through DEC-197 plus the Open decisions status list).
3. Read both approved canonical specifications in full:
   - `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` (732 lines)
   - `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` (1,203 lines)
4. Read the three research navigation and reconciliation deliverables in full:
   - `audit-outputs/research/reconciliation-report.md` (X2, 299 lines)
   - `audit-outputs/research/research-brief-verification.md` (PPR-VER-001, 266 lines)
   - `audit-outputs/research/source-and-decision-index.md` (X1, 605 lines)
5. Inspected the read-only legacy repository `papyr-reference/` directly (files listed in Section 3) to cite existing patterns and to ground the proposed fresh rebuild tree.
6. Verified `papyr-reference/` git cleanliness before and after the task.
7. Loaded the `superpowers:writing-plans` skill to apply its exact plan header and TDD task structure.
8. Authored the canonical master implementation plan at the assigned path, then authored this evidence file.
9. Ran the verification checklist in Section 8 against both output files.

Precedence applied: decisions, then the two specifications, then audit and research evidence, then the legacy reference (arch §1.4).

## 2. Inputs read and evidence anchors

### 2.1 Decision log (`papyr-rebuild-decisions.md`, 2,343 lines)

Read in full. Key anchors used by the plan:

- DEC-001 (`:16-26`): rebuild mandate; legacy is reference, not default architecture.
- DEC-006 (`:72-81`): single local decision log; migration into the rebuild repository is contemplated.
- DEC-009, DEC-010 (`:109-131`): five-tool MVP catalog (Compress, Merge, Split, JPG to PDF, PDF to JPG).
- DEC-011 (`:133-145`): hybrid browser-first processing.
- DEC-013 (`:158-169`), DEC-070 (`:861-871`), DEC-075 (`:921-931`), DEC-166 (`:1951-1960`): one-hour retention clock, active deletion plus lifecycle safety net.
- DEC-014 (`:171-183`), DEC-195 (`:2305-2316`): Compress premium-screen mode; unmodified Ghostscript subprocess with `-dSAFER`, AGPL notice preservation, focused license review before launch.
- DEC-015 (`:185-200`): conservative device-aware browser limits.
- DEC-019 (`:239-251`), DEC-162 (`:1907-1916`), DEC-174 (`:2043-2052`): Redis durable minimal-metadata queue, dedicated workers, one Compose stack.
- DEC-020 (`:253-265`): adaptive anonymous fair-use controls.
- DEC-022 (`:279-290`), DEC-190 (`:2244-2255`): accepted no-prior-consent advertising risk, reaffirmed; no compliance claims.
- DEC-023 (`:292-302`): explicit locale prefixes for every route.
- DEC-024 (`:304-314`): 90-day success criteria; exact numeric targets and baseline windows must be defined before implementation planning is approved (recorded as plan precondition R-27).
- DEC-025 (`:316-327`): analytics boundaries; no session replay, no document-sensitive data.
- DEC-027 (`:342-352`): launch gate is all five tools production-ready.
- DEC-034 (`:427-437`), DEC-066 (`:811-823`): per-tool server limits; no benchmark program; conservative defaults adjusted from production observability.
- DEC-036 (`:452-462`), DEC-064 (`:787-797`), DEC-074 (`:909-919`): password handling; per-locked-file Merge passwords.
- DEC-037 (`:464-474`): ZIP plus individual downloads.
- DEC-038 (`:476-486`), DEC-077 (`:945-955`), DEC-078 (`:957-967`): Split modes; overlapping independent ranges; user-entered order preserved.
- DEC-039 (`:488-498`), DEC-081 (`:993-1003`): one automatic PDF-to-JPG profile; white compositing.
- DEC-040 (`:500-510`), DEC-076 (`:933-943`), DEC-079 (`:969-979`): file-level Merge; all-or-nothing; feature preservation to safe engine extent.
- DEC-041 (`:512-522`), DEC-082 (`:1005-1015`): JPG-to-PDF automatic fitting; per-image page size and orientation.
- DEC-042 (`:524-534`): safe localized source-derived output naming.
- DEC-045 (`:560-570`): Privacy, Terms, Cookies/Advertising pages at launch with qualified legal review.
- DEC-046 (`:572-582`), DEC-050 (`:622-631`): support email and contact form to the owner-managed inbox; no unsupportable response-time promises.
- DEC-047 (`:584-594`): locale-less entry detection with manual-choice override.
- DEC-048 (`:596-608`), DEC-049 (`:610-620`): fully automated LLM blog workflow with blocking gates; version-controlled MDX.
- DEC-051 (`:633-643`), DEC-193 (`:2281-2291`), DEC-196 (`:2318-2330`): custom provider contract; OpenAI-compatible gateway at `https://router.budgezen.com/v1`, exact model identifier `mypapyr`, bearer auth, reliability controls separate from spending controls.
- DEC-052 (`:645-654`), DEC-053 (`:656-666`), DEC-113 (`:1363-1372`), DEC-121 (`:1452-1461`), DEC-124 (`:1485-1494`): blog topics, one trilingual set per day, truthful dates.
- DEC-054 through DEC-060 (`:668-752`): research gates; owner approval per feature; coding gate.
- DEC-062 (`:764-774`): WCAG 2.2 AA target.
- DEC-065 (`:799-809`): automatic server fallback after safe browser failure.
- DEC-066 (`:811-823`): no benchmark program; supersedes DEC-061 and DEC-063.
- DEC-067 (`:825-835`), DEC-068 (`:837-847`): expiry while tab open; manual download fallback.
- DEC-069 (`:849-859`), DEC-071 (`:873-883`), DEC-072 (`:885-895`): queued-only cancellation; tab-close continuation; same-tab refresh recovery via `sessionStorage` opaque tokens.
- DEC-080 (`:981-991`): always-new Compress artifact with honest reporting.
- DEC-083 (`:1017-1027`), DEC-085 (`:1042-1052`), DEC-089 (`:1084-1094`), DEC-191 (`:2257-2266`): paper policy; Letter limited to US/CA; A4 fallback; locale never decides.
- DEC-086, DEC-087 (`:1054-1070`): superseded by DEC-090.
- DEC-088 (`:1072-1082`): threat blocking with safe rejection.
- DEC-090 (`:1096-1107`), DEC-091 (`:1109-1119`), DEC-192 (`:2268-2279`): active-content sanitization with category disclosure; Merge and Split route to server sanitization; fail closed when scanner or sanitization path is unavailable.
- DEC-092 (`:1121-1131`): PDF-to-JPG untrusted-input handling without carrying active content into images.
- DEC-093 (`:1133-1143`): image validation in isolation by actual bytes and resource limits.
- DEC-094 (`:1145-1155`), DEC-141 (`:1673-1682`): post-launch legacy tool restoration; stability first.
- DEC-095 (`:1157-1167`): reuse existing infrastructure assets; new spending needs approval.
- DEC-096 (`:1169-1179`), DEC-140 (`:1662-1671`): direct production activation without a public beta or launch campaign.
- DEC-097 (`:1181-1191`): owner accountability with AI-assisted automation.
- DEC-098 (`:1193-1203`): optimize before vertical scaling; approval for upgrades.
- DEC-099 (`:1205-1215`): legacy application archived, not publicly accessible.
- DEC-100 (`:1219-1228`), DEC-103 (`:1252-1261`): one-month target; delay rather than cut.
- DEC-107 (`:1296-1306`), DEC-109 (`:1319-1328`): newsletter deferred.
- DEC-114 (`:1374-1384`), DEC-127 (`:1517-1526`), DEC-194 (`:2293-2303`): legacy URL preservation on traffic evidence; full inventory audit; 410 Gone default.
- DEC-115 (`:1386-1394`), DEC-118 (`:1419-1428`): Indonesian as a first-class launch locale; trilingual completeness gate.
- DEC-116 (`:1397-1406`), DEC-119 (`:1430-1439`), DEC-161 (`:1896-1905`): public status page, Vercel-hosted, automatically derived.
- DEC-117 (`:1408-1417`), DEC-120 (`:1441-1450`): result-problem reports without document upload; optional reply email.
- DEC-122 (`:1463-1472`): Indonesian localized slugs.
- DEC-123 (`:1474-1482`), DEC-125 (`:1496-1504`), DEC-138 (`:1640-1649`): informational roadmap; free-forever commitment statement.
- DEC-126 (`:1506-1515`): no public usage counters.
- DEC-128 (`:1528-1537`): no competitor-comparison pages.
- DEC-129 (`:1539-1548`), DEC-130 (`:1550-1560`), DEC-131 (`:1562-1571`): light advertising on blog, legal, support, status; separation from Download controls.
- DEC-132 (`:1573-1583`), DEC-133 (`:1585-1594`), DEC-134 (`:1596-1605`): free forever; fair queuing; no paid lane.
- DEC-137 (`:1629-1638`): fair scheduling preventing monopolization.
- DEC-142 (`:1684-1693`) through DEC-158 (`:1862-1871`): evolved directory model, existing visual language, tool-page sequence, shell visibility, result card, categorized navigation, equal-weight homepage grid, language selector in navbar, homepage content depth, ad placement after primary experience, five-tool navigation population, single-page tool flow, Related Tools, mobile accordion, process-another-file reset, accordion FAQs, inline error cards.
- DEC-159 (`:1873-1882`): one monorepo; legacy clone is separate read-only reference.
- DEC-160 (`:1884-1894`), DEC-177 (`:2076-2085`), DEC-178 (`:2087-2096`): manual deployment; core gate; previous-healthy-image rollback.
- DEC-164 (`:1929-1938`): `/api/v1` version prefix.
- DEC-165 (`:1940-1949`): machine-readable capability and limits contract.
- DEC-169 (`:1985-1995`), DEC-171 (`:2008-2017`): balanced validation; maintained malware scanner as one layer.
- DEC-170 (`:1997-2006`): short-lived signed R2 URLs.
- DEC-172 (`:2019-2029`): dedicated SSH user with passwordless sudo; no current access authorized.
- DEC-173 (`:2031-2041`), DEC-181 (`:2121-2129`): S3 backups; isolated monthly restore.
- DEC-175 (`:2054-2063`): 30-day sanitized logs.
- DEC-176 (`:2065-2074`): protected VPS environment-configuration secrets procedure; credential rotation.
- DEC-179 (`:2098-2107`): monthly dependency review.
- DEC-180 (`:2109-2118`), DEC-182 (`:2131-2140`): Telegram alerts; Netdata plus external uptime.
- DEC-183 (`:2142-2151`), DEC-184 (`:2153-2161`), DEC-185 (`:2163-2172`), DEC-188 (`:2221-2230`): design approval sequence; English canonical language; two coordinated specs.
- DEC-186 (`:2174-2183`): PDF-to-JPG page selection preserves duplicates and requested order.
- DEC-187 (`:2185-2195`): JPG/JPEG, PNG, WebP accepted at launch with the "JPG to PDF" name.
- DEC-189 (`:2232-2242`): one active worker, one concurrent job at launch.
- DEC-197 (`:2332-2342`): approves the revised specifications for implementation planning only; explicitly does not authorize implementation, dependency installation, VPS access, infrastructure changes, deployment, commits, pushes, provider authentication, or remote operations.

### 2.2 Product and UX Design Specification (732 lines)

Read in full. Anchors: status and scope (`:13-41`); non-goals including no benchmark and beyond-the-five-tools (`:43-65`); precedence (`:66-87`); product goals (`:88-99`); users (`:101-111`); launch scope (`:113-127`); IA and routes (`:129-174`); localization (`:175-185`); visual baseline with the token table and D1-D13 defect list (`:187-287`); shell and homepage (`:288-328`); the five detailed tool flows (`:330-461`); shared states, download behavior, expiry, cancellation, honest progress (`:463-512`); advertising placement (`:514-526`); legal, support, status, roadmap, blog surfaces (`:528-554`); responsive and WCAG 2.2 AA coverage (`:556-586`); analytics and privacy boundaries (`:588-601`); error and recovery behavior (`:602-614`); SEO and migration constraints (`:616-627`); acceptance criteria (`:629-697`); unresolved items 21.1-21.21 (`:699-723`); relationship to architecture (`:725-731`).

### 2.3 Technical Architecture Specification (1,203 lines)

Read in full. Anchors: scope, status, non-goals, precedence, design-versus-implementation authorization (`:17-102`); topology (`:105-173`); monorepo boundaries (`:176-206`); Vercel frontend (`:209-251`); Cloudflare edge and trusted country context (`:254-281`); VPS Nginx and FastAPI (`:284-325`); Compose services (`:328-372`); Redis queue (`:375-410`); bounded workers and fair scheduling (`:413-464`); routing (`:467-503`); five-tool responsibilities (`:506-571`); R2 lifecycle and one-hour deadline (`:574-611`); task state machine and recovery (`:615-668`); capability contract (`:671-697`); signed downloads (`:700-725`); availability (`:728-748`); validation, sanitization, malware, hardening (`:751-811`); secrets, access, logging, backups (`:815-860`); CI gate, manual deployment, rollback (`:863-899`); monitoring, status, Telegram (`:902-922`); dependency maintenance (`:925-935`); testing strategy (`:938-973`); data classification and prohibited data (`:977-1016`); operational acceptance (`:1019-1053`); research gates and unresolved choices 25.1-25.4 (`:1056-1102`); self-review record including the tooling-limitation note that no markdown lint scripts exist at the workspace root (`:1106-1137`); decision map appendix (`:1141-1169`); legacy source evidence index (`:1171-1203`).

### 2.4 Reconciliation and navigation deliverables

- `reconciliation-report.md` (X2): classification summary (Section 3); 19 compatible recommendations A-1..A-19 (Section 4); 7 genuine conflicts resolved by DEC-189..DEC-196 (Section 5); deferred defaults C-1..C-12 (Section 6); source and contract blockers D-1..D-5 (Section 7); readiness statement (Section 10); `papyr-reference` cleanliness evidence at HEAD `981c59a` (Section 11).
- `research-brief-verification.md` (PPR-VER-001): 25/25 briefs PASS; 0 blocking defects; DEC-066 compliance confirmed; no implementation authorization language.
- `source-and-decision-index.md` (X1): coverage matrix (Section 4); per-track detail (Section 5); shared-source dedup register (Section 6); conflict register K1-K18 (Section 7); missing-source register M1-M23 (Section 8); completeness check mapping every UX §21 and arch §25.3 item to briefs (Section 9.2).

## 3. Legacy repository inspection (`papyr-reference/`, read-only)

Files read directly to ground patterns cited in the plan:

| Path | Pattern evidenced | Plan use |
|---|---|---|
| `backend/main.py` (120 lines) | FastAPI shell, lifespan cleanup loop, slowapi rate limiter, CORS, 11 routers, `/health` | BE-01, BE-10 replace the per-process limiter and in-app cleanup |
| `backend/services/async_task.py` (207 lines) | In-memory `_tasks: dict[str, TaskInfo]`, states queued/processing/done/failed, 2-hour TTL, 120 s timeout | BE-04, BE-05, BE-06 replace this pattern per DEC-019 |
| `backend/services/compress_service.py` (157 lines) | Ghostscript subprocess, quality presets screen/ebook/printer, 30 s timeout, no `-dSAFER` | TL-02 corrects the missing `-dSAFER` gap per DEC-195 |
| `backend/routers/compress.py` (221 lines) | Endpoint flow: validate, process, R2 upload, signed URL, saved-percent | TL-02 service and router shape |
| `backend/utils/config.py` (113 lines) | Frozen `Settings` dataclass; `MAX_UPLOAD_SIZE_MB=20`, `FILE_RETENTION_MINUTES=60`, `RATE_LIMIT_PER_MINUTE=10` | BE-01 settings pattern; legacy mirrored limits removed under DEC-165 |
| `backend/utils/r2.py` (157 lines) | boto3 S3-compatible client, UUID hex keys, 3600 s signed URLs, idempotent delete | BE-03 key-hygiene and signed-URL baseline |
| `deploy/docker-compose.yml` (136 lines) | Hardening baseline: read_only, cap_drop ALL, no-new-privileges, tmpfs, resource limits, healthchecks, internal network, log rotation | FD-03, SEC-04 |
| `frontend/package.json` (52 lines) | Next 16.2.4, React 19.2.4, pdf-lib 1.17.1, pdfjs-dist, dnd-kit, Vitest, Playwright, Tailwind v4, Vercel Analytics | FD-01 dependency floors |
| `frontend/next.config.ts` (7 lines) | Empty config, no redirects or rewrites | SH-01, SEO-02 |
| `.github/workflows/ci.yml` (139 lines) | Frontend lint/test/build, backend Ruff and pytest | FD-04 core gate baseline |
| `frontend/src/app/layout.tsx` (59 lines) | Hardcoded `lang="id"`, Indonesian-only metadata, DM Sans, Navbar/Footer/Analytics/SpeedInsights | SH-03 metadata correction |
| `frontend/src/hooks/useAsyncTask.ts` (204 lines) | 3 s polling, 180 s timeout, status mapping | TL-01 useTaskPolling replacement |
| `frontend/src/lib/config.ts` (39 lines) | Mirrored limits (20 MB, 60 min) | TL-01 capabilities-client fallback |
| `frontend/src/app/` tree | Five tool page directories, sitemap.ts, robots.ts, globals.css | SH-02..SH-08, TL-02..TL-06 |
| `backend/tests/` tree | Test inventory including fixtures, edge cases, Indonesia files | Test-fixture patterns for P4 tasks |

Additional pattern references cited in the plan from the X1 index and both specs (not re-read in full): `backend/utils/pdf_validator.py`, `backend/utils/cleanup.py`, `backend/utils/logging_config.py`, `backend/routers/status.py`, `frontend/src/lib/pdfUtils.ts`, `frontend/src/components/PDFUploader.tsx`, `frontend/src/components/PageRangeInput.tsx`, `frontend/src/components/Footer.tsx`, `frontend/src/app/sitemap.ts`, `frontend/src/app/compress/page.tsx`, `frontend/src/app/image-to-pdf/page.tsx`, `frontend/src/app/split/page.tsx`, `frontend/src/lib/analytics.ts`, `frontend/src/components/__tests__/PasswordInput.test.ts`, `deploy/nginx/conf.d/production.conf`, `backend/Dockerfile.production`, `.github/workflows/deploy-vps.yml`, `docs/runbook-vps.md`, and the audit deliverables `audit-outputs/ui-five-tools-audit.md`, `ui-home-shell-audit.md`, `ui-docs-code-reconciliation.md`.

## 4. Git cleanliness of `papyr-reference/`

- Command (read-only): `git -C papyr-reference status --porcelain` plus `git rev-parse HEAD` and `git log --oneline -3`.
- Result: empty porcelain output; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (`981c59a docs(fase2): mark STEP-F2-063 complete`); top of history `8d0d09e`, `cce59e1`.
- This matches the HEAD recorded by PPR-VER-001, X1, X2, and the specs. Verified again after the two deliverables were written (Section 8).

## 5. Decomposition and plan-design decisions

1. **Master plan with gated phases.** The full rebuild spans eleven phases (P0 prerequisites through P11 post-launch). Each phase has an entry gate, an exit gate, and a review boundary. A single unbroken task list would be unmanageable and unreviewable; the phase decomposition makes each phase independently reviewable, satisfying the task instruction to decompose scope into phase plans when a single file would otherwise be unmanageably large. FD-05 documents the phase-plan expansion rule so each phase can be expanded into its own plan file under `docs/superpowers/plans/` at execution time using the same template and gates.
2. **TDD task skeleton.** Every implementation task follows the writing-plans sequence: write the failing test, verify it fails, minimal implementation, verify it passes, review and commit boundary. Verification commands are named per task (for example `pytest tests/ -v`, `npm test`, `npm run build`, `npm run test:e2e`, `docker compose -f deploy/docker-compose.yml config --quiet`, `scripts/check-ci.sh`) with expected outcomes.
3. **Resolution register instead of invented values.** Twenty-seven named resolution items R-01..R-27 map to the open choices recorded in UX §21, arch §25.3, the decision log Open decisions list, and X2 categories B and D. Each carries a proposal (from category-A research findings where one exists), governing decisions, and a stop condition. No consuming task may proceed past its item. This follows the specification convention that unresolved items are recorded as named choices rather than placeholder tokens (arch §26.1) and honors DEC-057 (owner approval per researched feature) and DEC-183 (surface, never silently resolve).
4. **Separately gated actions.** Eleven gates G-1..G-11 separate plan execution from VPS access, deployment, provider authentication, gateway calls, legal review, credential rotation, spending, concurrency increases, and per-URL disposition deviations. No task performs them; tasks only prepare artifacts.
5. **Precondition surfaced, not silently resolved.** DEC-024 requires exact numeric 90-day targets before implementation planning is approved; the plan records this as precondition R-27 in Section 1 and gates Phase 10 and Phase 11 acceptance accordingly.
6. **No benchmark obligations.** All verification commands in the plan are functional tests, config validations, CI gates, accessibility checks, or visual comparison checks framed as DEC-143 continuity verification (B5 brief §8 item 8 precedent), never a benchmark program.
7. **Category-A findings carried as proposals.** Per-tool limit defaults (C2), queue defaults (C1), lifecycle age (C3), rate values (C4), monitoring defaults (C5), and backup defaults (C6) are proposals inside resolution items subject to owner approval, not asserted requirements.
8. **Repository tree proposal.** The proposed monorepo at `papyr-rebuild/` implements arch §3 boundaries; the exact root is R-01 because arch §3.2 marks the structure as implementation-level subject to planning approval.
9. **Markdown structure.** The `ocs-markdown-autofix` skill was loaded; its auto-fix scripts (`bun run lint:md:fix`) are not available at the workspace root (no root package.json, no bun scripts), consistent with arch §26.5. Markdown conventions (ATX headings, consistent numbered sections, well-formed tables, checkbox lists, no placeholder tokens) were enforced manually.

## 6. Uncertainties and unresolved questions recorded

1. The exact rebuild repository root and git hosting remain owner decisions (R-01, R-02); the plan proposes defaults only.
2. Exact per-tool server limits, engine profile thresholds, worker and queue bounds, Redis persistence, scanner selection and budget, Nginx rate values, monitoring provider and thresholds, backup retention, and trusted-edge-header configuration remain open per arch §25.3 items 1-11, 17, 20 and are recorded as R-03 through R-17.
3. Adsterra publisher terms and ad-unit code (M1), the remaining gateway capability documentation (M2, R-21), current VPS host state (M13, R-26), and legacy traffic and demand data (M4/M5, R-25) are owner-supplied inputs; they block only their consuming phases.
4. UI baseline prompts (UX §21.13-16) and copy re-scoping items (UX §21.17-18) remain owner confirmations (R-23, R-24).
5. Implementation-time re-checks from the X1 register M6-M11, M14-M23 are not re-resolved here; they are assigned to consuming tasks (for example Redis pin at BE-04, Email Sending confirmation at R-20, pdf.js legacy floor at TL-06, Vercel analytics retention at PT-01).
6. No value was invented for any open choice; where the plan names a number, it is either a decision-bound value (for example 3600 s retention, 300 s signed-URL cap, 16-MP ceiling, one worker) or a category-A research proposal explicitly awaiting approval in the resolution register.

## 7. Files created by this task

1. `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (canonical master plan).
2. `audit-outputs/implementation-plan-authoring-dec197.md` (this evidence file).

No other file was created or modified. `papyr-reference/`, `AGENTS.md`, `papyr-rebuild-decisions.md`, both specifications, and all prior audit and research files were not modified.

## 8. Verification performed

| # | Check | Command or method | Result |
|---|---|---|---|
| 1 | Plan file exists | Read `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` | Present, complete through Section 10 |
| 2 | Required header | Read first lines | Starts with the writing-plans header: title, agentic-workers note, Goal, Architecture, Tech Stack, Global Constraints |
| 3 | Checkbox syntax | Grep `- \[ \]` | Every task step uses `- [ ]` |
| 4 | Placeholder scan on the plan | Grep `TODO|TBD|FIXME|XXX|lorem ipsum|WIP` | 0 hits; open choices are named resolution items R-01..R-27 |
| 5 | Placeholder scan on this evidence file | Same pattern | 0 hits (this paragraph is the scan record, not a token) |
| 6 | Benchmark scan | Grep `benchmark` on both outputs | Hits are only DEC-066 prohibition references and the self-review scan record |
| 7 | Authorization scan | Review of Sections 7 and 10 | No task performs VPS access, deployment, provider authentication, gateway calls, or git remote operations; all are G-1..G-11 owner-gated |
| 8 | Traceability | Section 9 tables | Every UX spec section (1-22), every arch spec section (1-26 plus appendices), and every decision DEC-001..DEC-197 maps to phases or tasks |
| 9 | Resolution coverage | Section 6 table | 27 rows, one per named open choice, each with proposal, governing decisions, and stop condition |
| 10 | Legacy cleanliness | `git -C papyr-reference status --porcelain` (before and after) | Empty, exit 0; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` unchanged |
| 11 | No implementation performed | Task log review | No installs, builds, servers, VPS access, deployments, provider calls, or remote operations were run; Read/Grep/Glob/filesystem listing and Write/Edit for the two outputs only |

## 9. Prohibitions-compliance statement

- No decision log, specification, brief, audit file, `AGENTS.md`, or `papyr-reference/` content was modified. The only files created are the two assigned deliverables.
- No benchmark program, corpus, matrix, comparative quality or performance study, or quality-score obligation is introduced (DEC-066).
- No implementation, scaffolding, dependency installation, repository initialization, git commit or push, service start, VPS/SSH access, deployment, account creation, provider authentication, API call, or remote mutation was performed (DEC-197, DEC-060, DEC-160).
- No web research was performed; all evidence cited is from the workspace decision log, the two specifications, the research deliverables, and read-only legacy inspection.
- Open decisions are surfaced as named resolution items with stop conditions; none was silently resolved (DEC-183).
- This file is the primary planning evidence; a chat-only summary is insufficient.
