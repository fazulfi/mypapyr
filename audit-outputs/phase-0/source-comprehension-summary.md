# Papyr Phase 0 — Source Comprehension Summary

| Field | Value |
|---|---|
| Document ID | PPR-PH0-SRC-001 |
| Title | Wave 1 read-only comprehension of every mandatory source-of-truth artifact feeding Phase 0 PR-01 and FD-01..FD-05 |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (read-only comprehension auditor; no writes outside this file) |
| Workspace | `<workspace-root>` |
| Plan under comprehension | `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (Phase 0 = PR-01, PR-02, PR-03; FD-01..FD-05 in Phase 1) |
| Primary deliverable | this file |
| Status | Complete for parent verification; every listed source was read in full (paginated where required) |
| Precedence applied | decisions > canonical specs > plan > audit/research evidence > legacy reference (arch §1.4, plan §1) |

---

## 0. Method and Verifications

1. Confirmed all 15 required source files exist at the absolute paths given in the task brief; no file was missing, no closest-match lookup was required (verified via `awk 'END{print NR}'` line counts reported below).
2. Read each source file in full (Read tool with `offset`/`limit` for the larger sources). No summaries were accepted on faith.
3. Cross-checked `papyr-reference/` cleanliness claim and the workspace git-state assumption used by `pr-01-safety-readiness.md`. No command was executed inside `papyr-reference/`; the existing audit evidence (`implementation-plan-final-review-dec201.md` §8, `reconciliation-report.md` §11, `source-and-decision-index.md` §9.3) was used.
4. No shell mutations, no installs, no network calls, no git writes, no `.env.papyr` reads, no chat transcription of secrets or tokens; redacted-name convention applied (`CLOUDFLARE_API_TOKEN`, `<vps-ip>`, etc.).
5. Decision precedence (plan §1; arch §1.4): latest DEC > canonical specs > plan > audit/research reconciliation & briefs > legacy behavior. Any conflict surfaced is recorded in §13.


---

## 1. `<workspace-root>\AGENTS.md`

- **Lines observed:** 52 (3,481 bytes).
- **Role:** Governing orchestrator rules for Sisyphus as the parent agent over `<workspace-root>`; not project documentation for the owner (AGENTS.md:5).

### Decision-grade bullets

1. **`papyr-reference/` is the read-only legacy Papyr clone.** No edit, format, install, file generation, or shell command that mutates its tracked or untracked contents is permitted without explicit owner authorization (AGENTS.md:9).
2. **`papyr-rebuild-decisions.md` is the living decision log.** Decisions are append-only; superseded decisions must carry a new ID rather than be silently rewritten (AGENTS.md:10).
3. **`audit-outputs/` is the durable home for every delegated subagent's useful output.** Every exploration/research/audit/review/planning/analysis subagent MUST persist its full output before reporting completion; chat-only is insufficient (AGENTS.md:13-25).
4. **Direct investigation persistence is mandatory for the parent agent too.** Substantial audit or multi-file reads must be recorded under `audit-outputs/` with concrete source paths (AGENTS.md:27-29).
5. **No conversation compression during active work.** Discoveries, research, audits, design reconciliation, and implementation tasks are exempted from compression; the owner has hard-banned it for this workflow (AGENTS.md:31-36).
6. **Execution boundaries are explicit.** Discovery and design do not authorize implementation. No installs, dev servers, migrations, infrastructure changes, or production code without explicit owner request; read-only inspection is the default (AGENTS.md:38-44).
7. **VPS mutation is gated by the same rule.** Every command inside `papyr-reference/` must be preceded and followed by a `git status` check that is reported to the parent (AGENTS.md:43).
8. **No git/push/deploy/credential rotation without explicit owner authorization** (AGENTS.md:44).
9. **Communication norms:** keep the conversation active; ask batches of three high-level questions; never invent workstreams (no benchmark program); label confirmed decisions vs. recommendations vs. defaults vs. risks vs. open questions; report errors directly and continue (AGENTS.md:46-51).
10. **Benchmark prohibition is project-wide and explicitly restated.** The owner rejected the benchmark program; subagents must not recreate one (AGENTS.md:50).

### Phase 0 / FD-01..FD-05 impact

- PR-01 (repository creation) operates at the workspace root per DEC-198; AGENTS.md:9 already excludes `papyr-reference/` from rebuild scope and forbids any repo command targeting the nested `.git`.
- Every audit-output file cited below was produced under this rule; this summary itself is a delegated-output persistence artifact (PPR-PH0-SRC-001).
- FD-04 (CI core gate) and FD-05 (root tooling conventions) must explicitly require that CI does not auto-deploy and that no secret/PII value is ever printed; AGENTS.md:44 backs the rule.
- Secret-handling rule for gateway (`router.budgezen.com/v1`) and Adsterra integrations in later phases must follow AGENTS.md:44 (no commits/pushes/deploys with credentials).


---

## 2. `<workspace-root>\papyr-rebuild-decisions.md`

- **Lines observed:** 2,401 (~197,835 bytes). All 202 `## DEC-NNN` headings present, DEC-001 at line 16, DEC-202 at line 2390 (grep-verified).
- **Role:** Authoritative, append-only decision baseline. Precedence over specs, plan, and audits (arch §1.4:1-5; AGENTS.md:10).

### Binding decisions the Phase 0 subagent must honor

1. **DEC-060 (line 742) — Coding gate.** No product-code implementation or scaffolding for the rebuild is permitted until MVP research, cross-domain reconciliation, design approval, and plan review are complete. PR-01's `git init` runs at the G-1 gate (plan:316); this is not a "coding" action, but every subsequent FD/BE/SH/TL task is.
2. **DEC-066 (line 811) — No benchmark program, ever.** The owner explicitly rejected the earlier DEC-061 (mixed corpus) and DEC-063 (`<vps-ip>` VPS) proposals; all numerical values in the plan are conservative design choices, not benchmark-proven. PR-01..FD-05 must contain no corpus, no matrix, no VPS workload, no comparative performance study.
3. **DEC-143 (line 1695) — Visual baseline preserved.** The rebuild looks and feels like the legacy site; corrections are limited to consistency, responsiveness, a11y, localization resilience, truthful states, performance, and defects D1–D13 (audit-outputs/ui-home-shell-audit.md:153-187). Material visual departures need owner approval.
4. **DEC-172 (line 2019) — Dedicated non-root SSH user with ** for any deployment-time admin; direct root SSH login disabled.
  - **DEC-179 monthly dependency review + prompt critical fixes.**ser with `sudo NOPASSWD`.** Direct root SSH login stays disabled; key-based auth required. PR-01 does not create this user (deployment-phase concern, gated G-2); FD-04 and FD-03 (compose skeleton) must not assume root SSH patterns.
5. **DEC-188 (line 2221) — Two canonical design specs approved.** Approval authorizes *implementation planning only*, not implementation. Implementation plan approval is a separate gate (DEC-202, line 2390).
6. **DEC-189 (line 2232) — One active worker at launch.** Stability over throughput; valid jobs may wait in the bounded fair queue. FD-01..FD-05 must scaffold with one-worker capacity in mind, not two-worker; DEC-189 explicitly supersedes the earlier 2-worker research default.
7. **DEC-190 (line 2244) — Adsterra no-prior-consent risk reaffirmed.** Launch with non-intrusive ads in all regions as accepted risk; no compliance claims; qualified legal review still required before launch (CT-01, R-19). FD-04 must not bake a CMP into CI.
8. **DEC-191 (line 2257) — Edge-country Letter rule.** US/CA → Letter; every other country, missing, or invalid → A4; the active content locale never decides paper size. R-14 supplies the trusted-header config (CF-IPCountry or Vercel) at TL-05 time, not Phase 0.
9. **DEC-192 (line 2268) — Active-content Merge/Split inputs route to server sanitization.** Fail-closed if scanner or sanitization unavailable. SEC-01 (early Phase 3 prerequisite) and SEC-02 (also early Phase 3) are the implementation vehicles (plan:720-748).
10. **DEC-193 / DEC-196 (lines 2281, 2318) — Gateway contract.** Base URL `https://router.budgezen.com/v1`, exact JSON model identifier `mypapyr` (never `gpt5.6-sol` in requests), `Authorization: Bearer <API_KEY>` from protected server-side secrets only; no authenticated call is authorized by any planning artifact. G-5 gate; CT-03 hard-blocks on R-21.
11. **DEC-194 (line 2293) — Deferred legacy tool URLs default to localized 410 Gone.** Sitemap, navigation, canonicals, internal links exclude 410 URLs; credible traffic evidence may supersede via G-11. SEO-01/SEO-02 in Phase 8; PR-03 records the disposition.
12. **DEC-195 (line 2305) — Ghostscript as unmodified subprocess, `-dSAFER`, AGPL notices preserved, focused license review before launch.** R-05 records the disposition; if the review is unacceptable, Compress moves to a permissive engine path or commercial license. FD-04 dependency scan must include Trivy/SBOM on Ghostscript-bearing images.
13. **DEC-197 (line 2332) — Specification revisions DEC-189..196 are canonical.** Plan must preserve the unresolved research and contract gates recorded in UX §21, arch §25.3, and the Open-decisions list. This is the binding reason every Section-6 R-row remains the source of owner input.
14. **DEC-198 (line 2344) — Workspace root `<workspace-root>` is the rebuild repo root.** Supersedes the nested `papyr-rebuild/` proposal; `papyr-reference/` excluded and never touched. PR-01 step 2 is the workspace-root tree creation; step 3 verifies `git -C papyr-reference status --porcelain` is empty; step 4 runs `git init` under G-1.
15. **DEC-199 (line 2356) — Engine and queue matrix approved (R-28).** Redis Streams consumer groups (C1 brief); pdf-lib (browser Merge/Split + browser JPG-to-PDF); pikepdf/qpdf (server Merge/Split fallback + sanitization); img2pdf+Pillow (server JPG-to-PDF); pypdfium2 (server PDF-to-JPG); pdf.js (browser rendering + page count); platform `createImageBitmap` (WebP decode). Every accepted risk, scope boundary, material condition, fallback, dependency/version review stays in force. Version/license checks remain at implementation (DEC-056, DEC-179). Plan §6.1 (lines 260-272) is the normative reference.
16. **DEC-200 + DEC-201 (lines 2368, 2379) — 90-day measures and final numeric targets.** Job success ≥98%, system failure ≤2%, uptime ≥99.5%, CWV pass rate ≥75%, completed downloads ≥85% of successful jobs, organic-traffic growth >0% vs first 28-day baseline at day 90; p95 queue wait ≤60 s/tool; p95 server processing ≤180 s/tool; p50 observed and reported per tool without a separate target; each of the five tools ≥5% of completed downloads during days 29–90. R-27 RESOLVED. Baseline = first 28 post-launch days; evaluation = day 90 from relaunch.
17. **DEC-202 (line 2390) — Implementation plan approved.** All four preconditions for plan execution are now met: DEC-198 (root), DEC-199 (matrix), DEC-200/201 (targets), and the verified PASS verdict (PPR-PLN-FR-001). However, every separately gated action (Section 7 of the plan: G-1..G-11) still requires explicit owner authorization at the moment of action.

### Additional binding constraints surfaced from the log

- **DEC-022 (line 279) + DEC-190 — Advertising:** Adsterra banner/native only, no popunders, no social bars, no in-page push, no forced redirects, no anti-adblock (DEC-018).
- **DEC-031 (line 391) — Supported browsers:** latest two major versions of Chrome, Edge, Firefox, Safari desktop; current Safari on iOS/iPadOS; Chrome on Android; progressive-enhancement fallbacks required.
- **DEC-062 (line 764) — WCAG 2.2 AA:** automated + manual keyboard + representative AT testing; documented exceptions register; no certification claims. Anchors FD-04 (CI) and VL-02 (axe-core).
- **DEC-115 + DEC-118 — Indonesian as third launch locale** with full coverage, or the launch is delayed (DEC-103).
- **DEC-174 — Minimal Redis metadata only.** No file contents, passwords, signed URLs, filenames, previews, or extracted content in persisted task records. Affects FD-04 (no logging PII) and BE-04 design.
- **DEC-175 — 30-day operational log retention.** Logs must exclude files/filenames/passwords/signed URLs/object keys/previews/extracted content/precise metadata/sensitive payloads.
- **DEC-176 — Secrets via protected VPS env config, not in repository/CI.** Affects FD-03 (env template is non-secret by design; mode-600 install per arch).
- **DEC-179 — Monthly dependency review + prompt critical fixes.** Anchors FD-04 dependency-scan job and PO-02 cadence.
- **DEC-202 — Plan approved but separately gated actions remain owner-gated.**

### Phase 0 / FD-01..FD-05 impact

- PR-01 must execute exactly the steps in plan lines 304-317 (no invented sub-steps). G-1 is owner-gated for step 4.
- PR-02's `scripts/check-docs-migration.sh` must assert DEC-001..DEC-201 presence per the plan line 328, plus `docs/canonical-docs-baseline.md` existence; the script is dependency-free (shell only) and runs in Phase 0 before any Python tooling exists.

---

TEST CONTENT HERE - multi-line
should work

## 3. `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md`

- **Lines observed:** 732 (~91,096 bytes). Status line confirms "Approved by DEC-188; revised to incorporate DEC-189 to DEC-196" (spec:5).
- **Role:** Canonical UX/product design; companion to the architecture spec per DEC-185; precedence below decisions (spec §4).

### Decision-grade bullets

1. **§1 Status + §3 Non-goals.** Implementation is blocked (DEC-060). No redesign, no accounts (DEC-012), no paid fast lane (DEC-105/132..134), no benchmark program (DEC-066), no session replay (DEC-025), no seven deferred tools at launch (DEC-009/010/094), no cross-document page-level Merge editor (DEC-040), no competitor pages (DEC-128), no newsletter (DEC-107/109), no social (DEC-112), no donations (DEC-111), no public counters (DEC-126), no roadmap voting (DEC-125), no intrusive ads (DEC-018), no public API (DEC-108), no public beta (DEC-096), no alternative monetization (DEC-135/136).
2. **§4 Precedence.** Decisions > legacy UI > audit deliverables (the three Phase 0 UI audits) > legacy docs (Doc19/Doc32, historical per DEC-026).
3. **§5 Product goals (priority order).** Speed and simplicity first (DEC-008); fast+easy+free first message (DEC-139); trustworthy character (DEC-101); honesty (DEC-110/168/080/033); free forever core (DEC-132/133); organic growth + SEO + blog (DEC-106); 90-day judged by reliability and organic growth (DEC-024); UX wins over ad revenue (DEC-102).
4. **§6 Users + regions.** Anonymous, no-sign-up default (DEC-007/012); US, LATAM, Europe simultaneous launch (DEC-003/104); Indonesian first-class (DEC-115/118); no founder profile, no personal photo, no origin story (DEC-110).
5. **§7 Launch scope (binding preconditions before launch).** Five tools production-ready (DEC-009/010); complete EN/ES/ID on tools + essential surfaces (DEC-004/115/118); legal trio in three locales (DEC-045); support email + categorized form (DEC-046/050); status page on Vercel auto-derived (DEC-116/119/161); read-only roadmap (DEC-123/125/138); 15 launch articles (DEC-052/121); legacy URL dispositions complete (DEC-127/194); direct activation on production (DEC-096/140). One incomplete tool blocks launch (DEC-027).
6. **§8 IA + locale routes.** Locale-prefixed everywhere including English (DEC-023); URL patterns per spec §8.2; locale-less entry redirects once with manual override (DEC-047); 410 default for deferred tool URLs with localized explanation, excluded from sitemap/nav/canonicals/links (DEC-194); tool pages stay accessible during backend outages (DEC-163). Categorized navbar retained (DEC-147), populated only with five tools (DEC-152), mobile `<details>` accordion preserved with corrections (DEC-155). **One canonical tool catalog** replaces the four divergent legacy copies (DEC-154; D2 in audit).
7. **§9 Localization.** EN/ES/ID intentional localization, not literal machine translation (DEC-048/052/121/124); selector in navbar (DEC-149); resilient to length growth; one neutral register per locale; legacy Indonesia-first positioning dropped (DEC-002/003/021); hardcoded `lang="id"` replaced (DEC-023/047).
8. **§10 Visual baseline (DEC-143).** Five primary tokens (`--color-navy #1e3a5f`, `--color-accent #2563eb`, `--color-bg #f9fafb`, `--color-foreground #171717`, `--font-sans 'DM Sans'`) plus slate / emerald / rose supporting palette. **D4 + D5 corrections resolve dead tokens and `@theme inline` emission ambiguity.** D1–D13 corrections are normative. Section 10.7 limits changes to the approved list.
9. **§11 Shell + homepage.** Locale-aware `html lang`, sticky 52px frosted navbar, `main flex-1` sticky-footer flex shell, skip-to-content link (D8), locale-aware metadata (DEC-021/023), shell stays visible during processing (DEC-145). Homepage keeps five-card equal-weight grid (DEC-148), drops legacy 13-tool references and un-scope-corrected "no tracking" claims (DEC-025/168/150).
10. **§12 Five tool flows.** Each tool page is one page (DEC-153); shared sequence header → dropzone → config (when needed) → processing → result/download → privacy → related tools (DEC-144). **Related Tools visibility rule is unified across all five tools**: always visible below the workspace, matching the legacy Compress pattern (DEC-145/154). Compress is server-only by default (DEC-014/015/195). Merge is browser-first with active-content routing to server sanitization (DEC-030/065/192). Split uses order-preserving, overlap-allowed semantics (DEC-038/077/078). JPG to PDF is hybrid with new routing under DEC-015/034 (not the hardcoded 3 MB legacy threshold). PDF to JPG is browser-capable with server fallback; sequential rendering with 16-MP ceiling (DEC-015); transparency composited on white (DEC-081); duplicate-preserving page selections with disambiguation (DEC-186).
11. **§13 Shared states.** Canonical vocabulary: preparing → uploading → queued → processing → finalizing → ready (DEC-033). Auto-download + persistent manual button (DEC-029/068). One-hour absolute server expiry even with tab open (DEC-013/067/070/075/166). Same-tab refresh recovery via opaque `sessionStorage` (DEC-072). Cancel allowed only while queued, atomic Lua transition (DEC-069); tab-close does not cancel accepted jobs (DEC-071). No fabricated percentages (DEC-033); one-worker initial posture makes queuing expected (DEC-189).
12. **§14 Advertising placement.** Adsterra banner + native only (DEC-018); never obstructs upload/config/processing/result/download/consent/error/nav/a11y/responsive (DEC-018/102); tool pages only after primary experience (DEC-151); separated from Download controls on result pages (DEC-131); layout-shift guards + async/lazy scripts (DEC-018/129); legal/support/status pages may carry light ads only under DEC-130 with status independent of Adsterra scripts (DEC-130). The no-prior-consent decision remains an accepted risk (DEC-022/190); no compliance claims (DEC-190); terms and ad-unit code still require owner review before launch (R-18).
13. **§15 Content/legal/support/status/blog.** Three legal pages in three locales (DEC-045); support is email + categorized contact form, no accounts, no live chat, no document uploads, owner-managed inbox (DEC-046/050); result-problem report carries only allowed fields (DEC-117) with optional reply email (DEC-120); status is simple, Vercel-hosted, auto-derived (DEC-116/119/161); roadmap is read-only informational (DEC-123/125/138); blog is MDX in the repo with five topics × three locales (DEC-049/052/121), publication and update dates truthful (DEC-113), `mypapyr` gateway identity (DEC-193/196), at most one trilingual set per day (DEC-053/124).
14. **§16 A11y (WCAG 2.2 AA, DEC-062).** Keyboard operation, visible focus (the legacy has only one custom focus ring; the rebuild adds it app-wide), contrast, semantic structure, accessible names/errors, status/progress announcements with `role`/`aria-live`/`aria-valuenow`, target sizing, zoom/reflow, reduced-motion, localized resilience.
15. **§17 Analytics + privacy UX boundaries.** Detailed product events but no session replay/fingerprinting/document-sensitive data (DEC-025). Allowed fields enumerated; prohibited fields enumerated. Uploader carries no dedicated disclosure; the Privacy page is the home of the full disclosure (DEC-168). JPG-to-PDF discloses possible EXIF GPS/device retention (DEC-084). Legacy "no tracking" and "no personal data at all" copy is wrong and must be corrected (DEC-025/022). Password handling is memory-only, never logged (DEC-036/064/074).
16. **§18 Error and recovery.** Inline error cards with localized text and safe retry/reset/password/support-report actions (DEC-158); safe rejection categories only (DEC-169/171); threat-classified files blocked with no upload-back path (DEC-088); sanitization disclosure shows general categories, never payloads (DEC-091); routing transparency when fallback to server happens (DEC-030/065); auto-retry with cleared timer and visible "retrying" label (DEC-030); backend outage keeps tool pages accessible, no redirect to status page (DEC-163); accurate expiry countdown (DEC-067).
17. **§19 SEO + content migration.** Locale-prefixed routes with per-locale sitemaps, hreflang, canonicals (DEC-023); legacy URL inventory with explicit dispositions (DEC-127); localized 410 default (DEC-194); retained pages must be updated, not frozen (DEC-114); Indonesian preservation by mapping and updating (DEC-115/118/103); no competitor pages (DEC-128); blog dates truthful (DEC-113); no public counters (DEC-126).
18. **§20 Acceptance criteria.** Every criterion traces to a DEC; §20.6 confirms the DEC-024 exact-numeric precondition is closed by DEC-200/201.
19. **§21 Unresolved items (still-open residuals).** 21 items narrowed where DEC-189..196 resolved the underlying question. **UX §21.9 (R-18) is owner-supplied: Adsterra publisher terms and exact ad-unit code.** UX §21.21 (R-21) is hard-blocked on the gateway contract fields beyond what DEC-193/196 fixed.

### Phase 0 / FD-01..FD-05 impact

- FD-01 (Next.js scaffold) must install Next.js + React + Tailwind v4 + TypeScript; the locale-aware layout (`html lang`, skip link, sticky-footer shell, metadataBase `https://mypapyr.com`) does not get built until Phase 2 (SH-01..SH-03) but the scaffolding must not preclude it.
- FD-03 deploy scaffold must keep `deploy/runbook-vps.md` consistent with spec §15 wording on support/status and with the one-worker assumption.
- FD-05 must encode the §16 WCAG 2.2 AA acceptance target as a binding convention document so that VL-02 and PR-02 don't invent it.

---

## 4. `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md`

- **Lines observed:** 1,203 (~113,966 bytes). Status line confirms "Approved by DEC-188; revised to incorporate DEC-189 to DEC-196" (arch:7).
- **Role:** Canonical technical architecture; sibling to the UX spec per DEC-185; covers engines, queue, server limits, security, deployment, operations.

### Decision-grade bullets

1. **§1.1–§1.5.** Approval authorizes documentation only; DEC-189..196 are design refinements, not implementation authorization (DEC-188/193/196). Precedence: decisions > specs > audits > legacy reference (DEC-026). Where values are marked "conservative default" or "implementation-level choice" they are design proposals, not yet decisions (DEC-054/057).
2. **§1.3 Non-goals.** No accounts (DEC-012), no business API (DEC-108), no payments (DEC-105/132..134), no donations (DEC-111), no newsletter (DEC-109), no social (DEC-112), no competitor pages (DEC-128), no public counters (DEC-126), no benchmark (DEC-066), no deadline prediction (DEC-073), no OCR/Word/Excel/Protect/Unlock/Watermark/Sign/Rotate at launch (DEC-010/094), no Guinevere/OpenClaw/BullMQ/Postgres (DEC-016), no staging (DEC-096), no horizontal multi-VPS at launch (DEC-098), no malware-free guarantee.
3. **§2 System topology (DEC-017).** Vercel frontend, Cloudflare DNS/API edge, VPS Nginx+FastAPI+Redis+one-worker, R2 temporary objects, S3 backups, Telegram alerts, Netdata + external uptime. Approved topology retained from the legacy deployment; the rebuild modernizes it into executable configuration.
4. **§3 Monorepo.** Single repo, frontend/backend/deploy/docs/audit boundaries explicit (DEC-159). `papyr-reference/` is a separate read-only reference, not the workspace.
5. **§4 Frontend (Vercel).** Next.js App Router; locale-prefixed routes including English (DEC-023); metadataBase `https://mypapyr.com` (DEC-021); static + capability-contract caching at the edge; coarse country context for §11.5 paper-policy (DEC-085/089/191); first-layer bot/attack filtering.
6. **§5 Cloudflare edge.** DNS, TLS, proxying `mypapyr.com` and `api.mypapyr.com`, coarse country signal, DDoS/bot defense. Trusted-header config is R-14 (resolved at TL-05 implementation; not Phase 0).
7. **§6 VPS Nginx + FastAPI.** TLS origin termination, rate enforcement, sensitive-path and bot filtering, proxying to API. Nginx rate-limit values are R-11 (resolved at SEC-05).
8. **§7 Docker Compose.** API, queue, workers, Redis, Nginx, scanner (DEC-162). Hardening baseline from the legacy `papyr-reference/deploy/docker-compose.yml`: non-root, read-only root with bounded tmpfs, cap_drop ALL + minimal cap_add, no-new-privileges, pids and ulimits, bounded egress, healthchecks.
9. **§8 Redis durable minimal-metadata queue (DEC-019/162/174).** Only opaque id, state, timing, expiry, route, non-sensitive refs. Persistence mode per R-09 (AOF appendfsync everysec + RDB secondary, noeviction, bounded maxmemory, TTL-bounded minimal metadata).
10. **§9 Bounded workers + fair scheduling (DEC-137/134).** One active worker, one concurrent job at launch (DEC-189). Default 180 s per-job timeout with per-tool overrides; queue caps 2000/15 min, 4 concurrent per origin.
11. **§10 Browser/server routing (DEC-011/015/030/065/031/165).** Layered routing: device-class caps + file-characteristic evaluation + capability feature detection; ordinary `input[type=file]` always works; at most one server transition per job; fail-closed classes never upload; no `navigator.deviceMemory`.
12. **§11 Five-tool processing responsibilities.** Compress: Ghostscript subprocess, `-dSAFER`, AGPL preserved, license review (DEC-195). Merge: pdf-lib browser + pikepdf server fallback + sanitization pass (DEC-090/091/192). Split: pdf-lib browser + pikepdf server + sanitization; user-order preserved, overlaps allowed (DEC-038/077/078). JPG to PDF: img2pdf+Pillow server; per-image Letter/A4 from trusted edge country (DEC-191); WebP via `createImageBitmap`. PDF to JPG: pypdfium2 server + pdf.js browser; transparency on white (DEC-081); 16-MP ceiling (DEC-015); duplicate/order-preserving selections (DEC-186).
13. **§12 R2 lifecycle (DEC-013/067/070/075/166).** Absolute one-hour deadline; active deletion by the application; R2 lifecycle rule on `tmp/` prefix with 1-day expiration + multipart abort as safety net; `tmp/<YYYY-MM-DD>/<32-hex-uuid><safe-ext>` key scheme.
14. **§13 Task state machine (DEC-033/069/071/072).** States queued, processing, done, failed, cancelled. `GET /api/v1/tools/{tool}/tasks/{task_id}/status` per DEC-164/arch §13.5; same-tab refresh recovery via opaque `sessionStorage`.
15. **§14 API capability + limits contract (DEC-164/165).** Versioned `/api/v1`; machine-readable per-tool server limits + failure-code enum; backend validation stays authoritative.
16. **§15 Signed downloads (DEC-170).** Short-lived signed R2 URLs; expiry never exceeds authoritative expiry; refreshable for the same valid result.
17. **§17 Validation, sanitization, malware, hardening (DEC-088/090..093/169/171).** Validate from bytes not extensions; threat-classified files blocked, never returned, no upload-back path; sanitization removes active content with category reporting; balanced validation + hardened isolation; ClamAV-class scanner as one layer with honest limits, fail-closed on unavailability.
18. **§18 Secrets, access, logging, backups (DEC-172..176/181).** Non-root SSH user with `sudo NOPASSWD`; secrets via protected VPS env config; 30-day log retention; complete recoverable backup scope excludes ephemeral workspaces/uploads/results/signed URLs/queue payloads; isolated monthly restore verification.
19. **§19 CI gate + manual deploy + rollback (DEC-160/177/178).** CI core gate (lint, unit, build, security-scan); no auto-deploy; manual owner-authorized production deployment; rollback to previous healthy image.
20. **§20 Monitoring, status, Telegram (DEC-180/182/116/119/161).** Netdata + multi-region external uptime + Vercel-hosted status; noise-resistant signal rules; Telegram relay for severity/dedup/payload limits; status remains useful during VPS outage.
21. **§21 Dependency maintenance (DEC-179).** Monthly review of native processors, container base images, frontend/backend packages, CI provider workflows, malware signatures; critical fixes handled promptly.
22. **§23 Data classification and prohibited data (DEC-025/036/042/072/174/175).** File contents, filenames, passwords, signed URLs, object keys, previews, extracted content never enter analytics/monitoring/logs/error reporting/backups/Telegram.
23. **§25 Research gates and unresolved implementation-level choices.** §25.3 lists 21 items (1..21). Items 25.3.1 (Compress engine — DEC-195 resolves), 25.3.10–11 (monitoring, R-12), 25.3.12 (Adsterra, R-18), 25.3.13 (legal review, R-19), 25.3.14 (contact form, R-20), 25.3.15 (legacy URLs, R-15), 25.3.16 (ID slugs, R-16), 25.3.17 (browser routing, R-17), 25.3.18 (post-launch legacy-tool sequence, deferred per DEC-094), 25.3.19 (operational overrides, R-12), 25.3.20 (backup, R-13), 25.3.21 (gateway, R-21).

### Phase 0 / FD-01..FD-05 impact

- FD-01 / FD-02 / FD-03 scaffold around the §2 topology without creating production assets. The Docker Compose skeleton in FD-03 names services `nginx`, `api`, `redis`, `workers`, and reserves `scanner` for SEC-03 (plan line 398).
- FD-04 CI core gate must mirror §19: lint, unit, build, security-scan, no deploy job. The Trivy/SBOM stages referenced in §19 are required for the Ghostscript image at TL-02.
- FD-05 must record the §25.3 R-row stop conditions as binding for later phases, not as a new artifact (PR-03 does the same for plan §6).
- DEC-172 governs any future SSH work; PR-01 does not create or change the user. The DEC-172 explicit "this decision does not authorize current VPS access" must be respected by FD-01..FD-05.

---

## 5. `<workspace-root>\docs\superpowers\plans\2026-07-31-papyr-rebuild-implementation-plan.md`

- **Lines observed:** 1,450 (post-DEC-201 sync). Header confirms 313 task checkboxes, 28 resolution rows R-01..R-28, 11 gates G-1..G-11 (verified by PPR-PLN-FR-001 §2 mechanical checks).
- **Role:** Approved by DEC-202 (line 2390). Authoritative execution sequence for the rebuild. Plan precedes audit/research in the precedence chain but follows decisions and specs.

### Decision-grade bullets

1. **Tech Stack (line 9) and Global Constraints (lines 11-45).** FastAPI; Redis Streams consumer groups (approved by DEC-199, R-28); Ghostscript as unmodified subprocess with `-dSAFER` (DEC-195, approved); pdf-lib, pikepdf, img2pdf+Pillow, pypdfium2, pdf.js, `createImageBitmap` (all approved by DEC-199 with documented risks, scope, conditions, fallbacks); Docker Compose; Nginx; Cloudflare R2; CI provider per R-02 (proposal: GitHub Actions, CI core gate only); Vitest, Playwright, Pytest, Ruff.
2. **No implementation without plan approval (DEC-060/197/202).** The plan itself is documentation until owner-explicit approval, but DEC-202 (line 2390) records that approval. The execution agent still requires G-1 for any repo operation.
3. **Five-tool launch scope (DEC-009/010).** Compress, Merge, Split, JPG to PDF, PDF to JPG. The seven deferred legacy tools are post-launch candidates only (DEC-094), never launch scope.
4. **Trilingual launch completeness (DEC-027/115/118/121).** All five tools + essential supporting surfaces complete in EN/ES/ID before launch; one incomplete tool blocks public launch (DEC-027).
5. **One active worker (DEC-189).** Queueing, fairness, timeouts, safety caps in force. Added concurrency needs capacity evidence + owner approval (DEC-098).
6. **One-hour server retention (DEC-013/067/070/075/166).** Active deletion by application + R2 lifecycle safety net; expiry never extended.
7. **Hybrid browser-first (DEC-011/015/030/065).** Compress server-default; at most one server transition per job; security-policy failures fail closed.
8. **DEC-090/091/192 sanitization requirement.** Merge/Split active-content-bearing inputs route to the server sanitization path; fail-closed when scanner or sanitization unavailable.
9. **DEC-143 visual baseline.** Limited to consistency, responsiveness, a11y, localization resilience, truthful states, corrected interactions, performance, and removal of D1–D13 defects.
10. **DEC-062 WCAG 2.2 AA target.** Automated + representative manual keyboard and AT testing; documented exceptions register; no certification claims.
11. **DEC-066 no benchmark.** All numeric values are conservative design/safety choices adjusted from production observability. Functional tests, integration tests, security checks, a11y checks, and CI verification are required and are not benchmarks.
12. **DEC-172 non-root SSH user with ** for any deployment-time admin; direct root SSH login disabled.
  - **DEC-179 monthly dependency review + prompt critical fixes.**ser with `sudo NOPASSWD` for authorized administration.** Direct root SSH login disabled; key-based auth required; not authorized by this plan.
13. **DEC-193/196 gateway identity.** Base URL `https://router.budgezen.com/v1`, exact JSON model identifier `mypapyr`, `Authorization: Bearer <API_KEY>` from protected server-side or automation secrets only. No authenticated call is authorized by any planning artifact.
14. **Phase table (lines 136-149).** P0 → P11 with explicit dependencies. **Critical Phase-3 re-architecture (PPR-PLN-CORR-001 §2.2): SEC-01 and SEC-02 are early Phase 3 prerequisites before TL-02..TL-04; P5 depends on P3 only; Phase 5 gate entry is "Phase 3 complete (SEC-01 and SEC-02 prerequisites satisfied)".**
15. **Task count verified.** 313 task checkboxes (`grep -c '^- \[ \]'`); 28 resolution rows (`grep -cE '^\| R-[0-9]{2} '`); 11 gates G-1..G-11. Both numbers are documented invariants checked at each review pass.
16. **§6 Owner Resolution Register.** All 28 R-rows. **R-01 (DEC-198), R-27 (DEC-200/201), R-28 (DEC-199) are RESOLVED.** The remaining 25 carry stop conditions; the plan never invents values for any open choice.
17. **§6.1 Engine and queue matrix (R-28, DEC-199).** Seven normative rows: Redis Streams consumer groups; pdf-lib browser happy path; pikepdf (qpdf) server fallback + sanitization; img2pdf+Pillow server JPG-to-PDF; pypdfium2 server PDF-to-JPG; pdf.js browser rendering + page count; pdf-lib + `createImageBitmap` WebP decode. Every row carries approved selection + accepted risks + scope + material conditions + fallbacks.
18. **§7 Separately gated actions (G-1..G-11).** Repository/git (G-1); VPS SSH (G-2); production deploy (G-3); provider accounts (G-4); gateway calls (G-5); Adsterra (G-6); legal review (G-7); credential rotation (G-8); vertical upgrade or new paid service (G-9); additional worker concurrency (G-10); per-URL 410 deviation (G-11). Every action requires explicit owner authorization at the moment it occurs.
19. **§8 Phase 0 (PR-01..PR-03, lines 296-347).** Goal = repository, branch strategy, resolution register before any code exists. Gate entry = owner approves the plan (DEC-060/197/202). Gate exit = repository exists per R-01 (DEC-198), branch strategy recorded, canonical docs baseline-recorded, every R-row has a recorded disposition.
20. **§8 Phase 1 (FD-01..FD-05, lines 349-429).** Goal = wire three workspaces + CI core gate. Gate exit = lint/test/build/security-scan jobs pass on the skeleton; core gate documented per DEC-177.
21. **PR-02 dependency-free design (MEDIUM-6 fix, PPR-PLN-CORR-001 §2.6).** `scripts/check-docs-migration.sh` uses `cmp -s` for byte-identical spec copies and `grep` for DEC-001..DEC-201 ID presence; **NOTE the plan line 328 currently says "DEC-001 through DEC-201" — this is the canonical target, not DEC-197, because the log has DEC-198..DEC-202 already appended; PR-02 must reconcile to DEC-001..DEC-202 at execution time. PR-02 has zero pytest references; no Python tooling prerequisite is created at Phase 0.**
22. **PR-03 pre-fills R-01 RESOLVED (DEC-198), R-28 RESOLVED (DEC-199), R-27 RESOLVED (DEC-201)** (plan line 343). The remaining 25 R-rows are owner-filled at execution time. Step 3 verifies `grep -c '^| R-' docs/resolution-register.md` returns 28.
23. **FD-01 frontend scaffold (plan lines 357-370).** Files: `frontend/package.json`, `tsconfig.json`, `next.config.ts`, `eslint.config.mjs`, `postcss.config.mjs`, `.prettierrc`, empty `src/app/globals.css`, minimal `src/app/page.tsx`. Scripts: `dev`, `build`, `start`, `lint`, `test` (Vitest), `test:e2e` (Playwright), `format:check`. Dependency floors: next, react, react-dom, tailwindcss v4, typescript. **Vitest is in the script list (no Vitest config required at scaffold time); the failing test in step 1 is a smoke test, not pytest.**
24. **FD-02 backend scaffold (plan lines 372-385).** Files: `backend/requirements.txt`, `requirements-dev.txt`, `ruff.toml`, `pytest.ini`, `app/__init__.py`, `app/main.py` with `/health`. Scripts: `ruff check`, `ruff format --check`, `pytest`. First failing test is `backend/tests/test_health.py`. **Dependency installation is owner-gated (G-4); PR-01..FD-02 only create files, do not install or run.**
25. **FD-03 deploy scaffold (plan lines 387-400).** Files: `deploy/docker-compose.yml`, `deploy/nginx/conf.d/production.conf`, `deploy/.env.production.example` (non-secret only), `deploy/runbook-vps.md` outline. Failing test: `docker compose -f deploy/docker-compose.yml config --quiet` (config-validation only, Docker not started). Service names: `nginx`, `api`, `redis`, `workers` (with `scanner` reserved for SEC-03).
26. **FD-04 CI core gate (plan lines 402-415).** Path contingent on R-02. **Proposal: `.github/workflows/ci.yml` on GitHub Actions**, modeled on legacy `papyr-reference/.github/workflows/ci.yml` plus production-build and security-scan stages per DEC-177. Workflow artifact has **no deploy job** and **no secret exposed to `pull_request_target`** (verified by `scripts/check-ci.sh`). CI secrets and environments are configured at execution under G-4.
27. **FD-05 root tooling conventions (plan lines 417-429).** Files: `README.md`, `CONTRIBUTING.md`, `docs/plan/index.md`. Commit prefixes: `feat`, `fix`, `docs`, `chore`, `test`, `ci`, `refactor`, `security`. TDD is mandatory. Phase plans may expand into their own files under `docs/superpowers/plans/`.
28. **Two LOW open observations in the latest plan (PPR-PLN-FR-001 §4.1 / §4.2).** SEC-05 step 2 hedges the nginx config validation script with "for example `scripts/check-nginx.sh`" and the script is not listed in SEC-05 Files (line 890). OP-04 step 2 references "the scope test" without naming the mechanism. **Both are non-blocking, recommended for the first correction pass.** PR-02 / FD-03 / SEC-05 / OP-04 must use the corrected name pattern (`scripts/check-nginx.sh`, `scripts/check-backup-scope.sh` or in-script assertion) at the corresponding execution times.
29. **§9 traceability.** Every UX spec section, every Arch spec section, and every DEC-001..DEC-201 maps to at least one phase or task (PPR-PLN-FR-001 §3 check 7). The plan explicitly preserves DEC-004's expansion by DEC-115/118, the DEC-061/063/086/087 superseded entries, and the R-28 engine-and-queue matrix.
30. **§10 self-review.** 12 checks, all green for the current plan. **papyr-reference HEAD = 981c59a171f4b83c9e2afcecc6e934bee14a3a5e; porcelain empty.** PR-01 step 3 replicates this verification at the workspace root.

### Phase 0 / FD-01..FD-05 impact

- PR-01..FD-05 are the only tasks Phase 0 / Phase 1 may execute. Every later phase task (BE-*, TL-*, SEC-*, PT-*, OP-*, SEO-*, CT-*, VL-*, PO-*) is blocked on the gate exits of its predecessor phases.
- The plan's PRECONDITION in §1 (line 54) is now fully met by DEC-200/201; the plan is approved by DEC-202 but separately gated actions (G-1..G-11) still require explicit owner authorization.

---

## 6. `<workspace-root>\docs\resolution-register.md`

- **Lines observed:** 38 (~4,325 bytes). Status header says: "Status of every open resolution item (R-01..R-28) that gates implementation tasks and stop conditions in the master implementation plan" (line 3).
- **Role:** Owner-facing register for the §6 R-rows of the implementation plan. PR-03 task creates the rebuild-repo copy under `docs/resolution-register.md`. The root-level file here is the up-to-date pre-Phase-0 register produced by the planning work.

### Decision-grade bullets

1. **R-01 RESOLVED (DEC-198).** Rebuild repository root is `<workspace-root>`; nested `papyr-rebuild/` superseded; `papyr-reference/` excluded and read-only (line 9). No stop condition remains.
2. **R-02 RESOLVED.** Git hosting confirmed: GitHub, repo `fazulfi/mypapyr`, private, default branch `main` (line 10). Owner instruction 2026-07-31 ("mypapyr aja jangan rebuild") is the binding direction. PR-01 step 4 records this and runs `git init` under G-1.
3. **R-03..R-26 PENDING.** Owner approval required at their listed stop conditions before BE-08/TL hard-code limits (R-03), TL-02 profile values (R-04), TL-02 license review outcome (R-05), TL-06 starting values (R-06), BE-05 worker bounds (R-07), BE-05 fair scheduling (R-08), BE-04 Redis persistence (R-09), SEC-03 scanner + budget (R-10), SEC-05 Nginx rate-limits (R-11), OP-01 monitoring (R-12), OP-04 backup (R-13), TL-05 trusted header (R-14), SH-01/SEO-01 slug table (R-15), SEO-01 ID slugs (R-16), TL-01 routing thresholds (R-17), PT-02 Adsterra terms + ad-unit (R-18), CT-02 legal review (R-19), PT-03 contact provider (R-20), CT-03 gateway docs (R-21 hard-blocker), CT-04 launch topics (R-22), VL-03 UI prompts (R-23), CT-01 privacy copy re-scope (R-24), SEO-01/CT-04 legacy traffic data (R-25), OP-04/VL-05 VPS host verification (R-26).
4. **R-26 RESOLVED.** Current VPS host state verified 2026-07-31: Ubuntu 24.04.4, 15 GiB RAM, 4 cores, 2 GiB swap, Docker 29.6.2 (line 34). Note this verification improves on the earlier legacy "~8 GB / 4 vCPU / 4.5 GB swap" assumption used in DEC-189's memory-envelope trade-off; future capacity decisions may benefit.
5. **R-27 RESOLVED (DEC-200 + DEC-201).** Full 90-day target set supplied; evaluation day 90 vs first-28-day baseline (line 35).
6. **R-28 RESOLVED (DEC-199).** Queue mechanism + engine matrix approved with all documented risks/conditions remaining in force (line 36).
7. **Owner-instruction date 2026-07-31.** R-02 row carries the verbatim owner quote "mypapyr aja jangan rebuild" — useful provenance for any later scope question.

### Phase 0 / FD-01..FD-05 impact

- PR-03 creates `docs/resolution-register.md` inside the rebuild repo with one row per R-01..R-28; pre-fills R-01 / R-28 / R-27 as RESOLVED; populates the remaining 25 from the root-level register; verifies 28 rows via `grep -c '^| R-'`; records the R-02 verbatim owner instruction.
- PR-01 step 3's `git -C papyr-reference status --porcelain` is the canonical gate-exit verifier; the resolution-register is the parallel decision-records gate.
- **Note (line 34 vs line 35 vs line 36):** the root-level register is the snapshot at plan approval time. PR-03 must mirror it; the rebuild-repo copy is the one read by later phases. Any post-PR-03 owner disposition is appended to the rebuild-repo copy as a new decision ID per AGENTS.md:10.

---


## 7. `<workspace-root>\audit-outputs\implementation-plan-final-review-dec201.md`

- **Lines observed:** 200 (~26,096 bytes). Document ID PPR-PLN-FR-001. Verdict: **PASS** (ready for explicit owner approval). 2 LOW observations recorded as non-blocking (SEC-05 nginx script naming; OP-04 scope-test naming).
- **Role:** Final independent review of the DEC-201-synchronized plan. Establishes that the 2 HIGH, 8 MEDIUM, 3 LOW findings from PPR-PLN-CR-001 are all fixed and the 28 R-rows are present (28 verified, 313 checkboxes verified, DEC-001..DEC-201 fully cited, no token placeholders, no benchmark content).

### Decision-grade bullets

1. **Mechanical verification battery (§2).** 16 checks, all green: 1,450 lines; 313 line-start `- [ ]` (the 314th raw occurrence is the inline-code mention at line 3, not a task step); 28 R-rows; 15 DEC-201 references; 2 placeholder hits (both self-verification prose); 2 benchmark hits (both DEC-066 prohibition); full DEC-001..DEC-201 coverage; no DEC outside the range; 0 stale proposal-framing on approved engines.
2. **Prior-finding closure (§3).** All 13 findings from PPR-PLN-CR-001 are correctly fixed in the current plan. HIGH-1 (engine matrix elevated without DEC-057) is fixed via the R-28 row + §6.1 matrix. HIGH-2 (Phase DAG violation) is fixed by moving SEC-01/SEC-02 to Phase 3 as early security prerequisites.
3. **LOW-14 (non-blocking).** SEC-05 step 2 hedges the nginx validation script as "for example `scripts/check-nginx.sh`" and the script is not in SEC-05 Files. Recommendation: add `scripts/check-nginx.sh` to SEC-05 Files, state creation in step 1, remove the "for example" hedge. **PR-02 / FD-03 must follow this naming convention at the corresponding execution time.**
4. **LOW-15 (non-blocking).** OP-04 step 2 references "the scope test" without naming the mechanism. Recommendation: name the scope-test mechanism (`scripts/check-backup-scope.sh` in Files, or assertions inside the backup script). **OP-04 must adopt a named check script at execution time.**
5. **DEC-201 closure (§5b).** Plan records the four DEC-201 numeric fields verbatim in meaning at lines 54, 257, 1433, 1450 and references at lines 55, 328, 330, 343, 1236, 1239, 1274, 1405, 1431. R-27's register row (line 257) is `(RESOLVED: DEC-201)`.
6. **`papyr-reference/` evidence (§8).** HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`; `git status --porcelain` empty, exit 0; top of history `981c59a docs(fase2): mark STEP-F2-063 complete`. Matches every prior evidence record. This review performed no write to any `papyr-reference/` path.

### Phase 0 / FD-01..FD-05 impact

- PR-01..FD-05 may safely rely on the plan's invariants: 313 checkboxes, 28 R-rows, full DEC-001..DEC-201 coverage, no benchmark content, no implementation authorization outside its own steps.
- PR-02's `scripts/check-docs-migration.sh` is not in the LOW list, but PR-02 must use the same naming convention as the LOW-corrected SEC-05/OP-04 scripts (i.e., name the script in the task Files list).
- FD-04's `scripts/check-ci.sh` must follow the same pattern: named in PR-02/FD-04 Files, executed with FAIL/PASS expectations, no `for example` hedges.

---

## 8. `<workspace-root>\audit-outputs\implementation-plan-cross-review-dec197.md`

- **Lines observed:** 238 (~33,992 bytes). Document ID PPR-PLN-CR-001. Verdict: **CONDITIONAL PASS** at the time (before DEC-199 / DEC-200 / DEC-201 / DEC-202 and the PPR-PLN-CORR-001 corrections). 2 HIGH, 8 MEDIUM, 3 LOW findings.
- **Role:** Original independent cross-review that exposed the HIGH-1 engine elevation issue, HIGH-2 DAG violation, and the 8 MEDIUM findings MEDIUM-3 through MEDIUM-10 plus LOW-11 through LOW-13. All findings were deterministically corrected in PPR-PLN-CORR-001 and verified fixed in PPR-PLN-FR-001.

### Decision-grade bullets (from this review — preserved for audit trail)

1. **HIGH-1 evidence (lines 49-72).** `grep -inE 'redis streams|pikepdf|img2pdf|pillow|pypdfium|pdf-lib|pdf\.js|clamav|qpdf'` over both specs returned **zero matches**; plan contained 10 matches. Neither approved spec named any of these technologies (X2 reconciliation §4 confirms: Ghostscript is approved by DEC-195/arch §11.2/§25.3; everything else is research-grade at the time). Plan's own §2 rule 4 promised DEC-057 compliance but no R-row carried these engines as proposals. **This is the source record for the HIGH-1 correction that produced R-28 and the §6.1 matrix.**
2. **HIGH-2 evidence (lines 74-85).** Phase table required P3+P4 before P5; Phase 5 gate entry said only P3. TL-02/TL-03/TL-04 (Phase 4) consumed SEC-02/SEC-01 (Phase 5). **Phase-ordering DAG violation; corrected by moving SEC-01/SEC-02 into Phase 3 as early security prerequisites (PPR-PLN-CORR-001 §2.2).**
3. **MEDIUM-3 wording fix (line 87-95).** DEC-024 numeric targets are a hard precondition to plan approval. Plan's "gates Phase 10 and Phase 11 acceptance, not the foundational phases" phrasing was misleading. **Resolved by DEC-200 + DEC-201; plan now records R-27 as fully resolved.**
4. **MEDIUM-4 R-15 stop condition (line 102-108).** R-15 stop condition named only SEO-01; Phase 2 gate didn't require it; SH-01 (Phase 2) consumes R-15 (slug table feeds route names). **Resolved by R-15 stop condition change to "before SH-01 and SEO-01" and adding R-15 to Phase 2 gate entry.**
5. **MEDIUM-5 R-05 in Phase 4 gate (line 110-114).** R-05 missing from Phase 4 gate while TL-02 Consumes R-05. **Resolved.**
6. **MEDIUM-6 PR-02 pytest (line 116-122).** PR-02 wrote and ran `pytest` at Phase 0 before any Python tooling. **Resolved by making PR-02 dependency-free with shell-only `scripts/check-docs-migration.sh`.**
7. **MEDIUM-7 unnamed verification commands (line 124-130).** Four tasks (`OP-03`, `SEC-04`, `VL-02`, `VL-04`) named no command. **Resolved by naming `scripts/check-telegram-relay.sh`, `scripts/check-compose.sh`, `npm run test:a11y -- axe`, `npm run test:perf -- lighthouse` and listing them in Files.**
8. **MEDIUM-8 CT-04 G-5 gating (line 132-138).** Generating the 15 launch articles is an authenticated gateway call; plan claimed no task performs a gated action. **Resolved by adding "with each generation run executed under the G-5 owner gate" to CT-04 Step 3.**
9. **MEDIUM-9 G-1 blog carve-out (line 140-146).** G-1 "per commit or push" conflicts with DEC-048 auto-merging pipeline. **Resolved by G-1 carve-out for DEC-048 + CT-03 + PO-04, activation owner-gated.**
10. **MEDIUM-10 GitHub Actions proposal (line 148-152).** Tech Stack asserted GitHub Actions normatively while R-02 unresolved. **Resolved by re-labeling as "CI provider per R-02 (proposal: GitHub Actions, CI core gate only)".**
11. **MEDIUM-11 traceability gaps (line 154-160).** DEC-004, DEC-044, DEC-046, DEC-062, DEC-163, DEC-167 missing from §9.3 clusters. **Resolved by adding them in PPR-PLN-CORR-001 §2.11.**
12. **LOW-12 R-14 owner/implementer ambiguity (line 162-166).** R-14 stop condition said "Owner **or implementer** confirms..." — record belongs to owner register. **Resolved by changing to "Owner confirms the trusted-header setup before TL-05".**
13. **LOW-13 runbook wording (line 168-172).** `deploy/runbook-vps.md (updates legacy)` could be misread as editing `papyr-reference/`. **Resolved by wording "canonical operations runbook (replaces the legacy `papyr-reference/docs/runbook-vps.md` as the operating reference; the legacy file is never modified)".**

### Phase 0 / FD-01..FD-05 impact

- This file is the historical evidence that produced the corrections in `implementation-plan-corrections-dec197.md`. PR-01..FD-05 must not reintroduce any of these 13 patterns.
- The MEDIUM-6 fix establishes the convention that Phase 0 scripts are dependency-free shell, not pytest. FD-04 `scripts/check-ci.sh` follows the same model.

---

## 9. `<workspace-root>\audit-outputs\implementation-plan-corrections-dec197.md`

- **Lines observed:** 166 (~17,754 bytes). Document ID PPR-PLN-CORR-001. Status: complete; all 2 HIGH, 8 MEDIUM, and 3 LOW findings corrected deterministically; no owner decision was made.
- **Role:** The evidence record for the deterministic corrections applied to the master implementation plan after PPR-PLN-CR-001.

### Decision-grade bullets

1. **HIGH-1 correction (lines 30-46).** Tech Stack relabeled: queue mechanism, every PDF/image engine (pdf-lib, pdf.js, pikepdf, img2pdf, Pillow, pypdfium2), and CI provider now marked as proposals under R-28 or R-02; Ghostscript remains normative under DEC-195. New §6.1 R-28 row + matrix added with seven rows, each carrying approved approach, accepted risks, scope, material conditions, and fallback. **All later plan uses reference this matrix verbatim.** DEC-199 later resolved the R-28 proposals as approved selections; the matrix is now Section 6.1 normative.
2. **HIGH-2 correction (lines 47-58).** Chose review option 1: moved SEC-01 and SEC-02 into Phase 3 as early security prerequisites, with P3 exit gate "SEC-01 and SEC-02 prerequisites verified". P5 depends on P3 only; P5 exit gate now "scanner fail-closed behavior, container hardening, and Nginx enforcement verified". This is the binding Phase 3 re-architecture for Phase 0 downstream tasks to inherit.
3. **MEDIUM-3 DEC-024 precondition wording (lines 60-62).** Section 1 precondition rewritten: the owner must define exact 90-day numeric targets + baseline windows as part of approving the plan; the R-27 disposition must be in the approval record; until recorded, no phase may start. **DEC-200/201 closed this; the misleading "gates Phase 10 and Phase 11" sentence is gone.**
4. **MEDIUM-4 R-15 stop condition (line 65).** Changed to "Owner approves slug table and disposition map before SH-01 (route names) and SEO-01"; Phase 2 gate entry adds R-15.
5. **MEDIUM-5 R-05 in Phase 4 gate (line 69).** Added.
6. **MEDIUM-6 PR-02 dependency-free (lines 72-75).** PR-02 rewritten with `scripts/check-docs-migration.sh` using `cmp -s` and `grep`; all pytest references removed. **Phase 0 has no Python tooling prerequisite.**
7. **MEDIUM-7 unnamed verification commands (lines 77-83).** Each unnamed command named: `scripts/check-telegram-relay.sh` (OP-03), `scripts/check-compose.sh` (SEC-04), `npm run test:a11y -- axe` (VL-02), `npm run test:perf -- lighthouse` (VL-04), `scripts/check-contrast.sh` (VL-03).
8. **MEDIUM-8 CT-04 G-5 gating (line 86).** Article generation runs "executed under the G-5 owner gate".
9. **MEDIUM-9 G-1 blog carve-out (line 90).** Carve-out added for DEC-048/CT-03/PO-04.
10. **MEDIUM-10 GitHub Actions contingent on R-02 (lines 92-94).** Tech Stack re-labeled; FD-04 Files/Interfaces note the workflow artifact is contingent.
11. **MEDIUM-11 traceability matrix gaps (lines 96-104).** DEC-004/044/046 added to SEO cluster; DEC-062 added to UI cluster; new DEC-163/167 row "Availability and failure isolation"; coverage note updated.
12. **LOW-12 R-14 owner-only (line 106).** R-14 stop condition changed to single owner confirmation; implementation-time re-check stays in TL-05 proposal text.
13. **LOW-13 runbook wording (line 110).** "Replaces the legacy `papyr-reference/docs/runbook-vps.md` as the operating reference; the legacy file is never modified".
14. **Verification §6 (lines 135-153).** 15 mechanical checks all PASS: file is 1,437 lines after corrections; 313 line-start checkboxes; 28 R-rows; 2 placeholder hits (both self-verification prose); 2 benchmark hits (both DEC-066 prohibition); full DEC-001..DEC-197 coverage; 0 hits for "the relay test runner" etc.; SEC-01 at line 711 / SEC-02 at 726 inside Phase 3 (line 561–749); Phase 4 at 741; Phase 5 at 839; consumers follow producers; `papyr-reference/` HEAD unchanged with empty porcelain.

### Phase 0 / FD-01..FD-05 impact

- The §6.1 R-28 matrix is the binding list of engines approved by DEC-199. Phase 0 tasks must not introduce additional engines.
- Phase 3 SEC-01/SEC-02 placement is binding; PR-01..FD-05 must not assume Phase 5 placement.
- The MEDIUM-7 naming convention is binding for every future check script in the plan; FD-04's `scripts/check-ci.sh` and any FD-05 helper must follow it.

---


## 10. `<workspace-root>\audit-outputs\research\reconciliation-report.md`

- **Lines observed:** 299 (~47,413 bytes). Document ID X2. Date 2026-07-31.
- **Role:** Final cross-domain reconciliation of 25 primary research briefs against DEC-001..DEC-188 baseline. Classifies findings into (A) compatible recommendations, (B) genuine conflicts requiring owner decision, (C) deferred defaults, (D) source/contract blockers. Collapses ~50 brief-level owner prompts into **7 high-level questions (Q1..Q7)**.

### Decision-grade bullets

1. **§3 Classification summary.** 18 compatible (Category A), 7 genuine conflicts (B), 12 deferred defaults (C), 5 source blockers (D). All categories A-1..A-19 are design inputs; **DEC-199 later approves the entire R-28 matrix (engine and queue), which subsumes Category A's engine recommendations.**
2. **§4 Category A compatible recommendations (lines 87-108).** Permissive-first engine matrix structure (A-1); pikepdf (qpdf) for Merge/Split server fallback and sanitization (A-2); pdf-lib browser happy path (A-3); img2pdf+Pillow hybrid JPG-to-PDF (A-4); pypdfium2+pdf.js PDF-to-JPG (A-5); layered browser routing (A-6); minimal custom queue over Redis Streams consumer groups (A-7); active deletion + R2 lifecycle safety net (A-8); layered hardening (A-9); Netdata + multi-region external uptime + Vercel status + Telegram (A-10); restic backups + monthly isolated restore verification (A-11); threat classification and fail-closed matrix (A-12); analytics boundary schema (A-13); Cloudflare-native contact delivery (A-14); EN disclosure + qualified legal review (A-15); WCAG 2.2 AA four-layer program (A-16); UI-baseline verification methods (A-17); scheduled content-bot workflow (A-18); launch topic criteria (A-19).
3. **§5 Category B genuine conflicts — the 7 high-level owner questions.** **Q1 — Ghostscript licensing/AGPL compliance** (single largest cross-track dependency; **resolved by DEC-195 + R-05 disposition**). **Q2 — VPS memory envelope** (resolved by **DEC-189 one-worker posture**). **Q3 — EEA/UK/CH advertising consent** (DEC-022 risk reaffirmed by DEC-190; **R-18 owner supply required before launch**). **Q4 — `gpt5.6-sol` provider contract** (DEC-193/196 fixed identity + auth; **R-21 remaining capability fields are the only true hard blocker**). **Q5 — Regional paper policy** (DEC-191: US/CA → Letter, otherwise A4; **R-14 records the trusted-header config at TL-05 time**). **Q6 — Browser-path sanitization + scanner** (DEC-192 active-content routing; **R-10 scanner choice remains an owner prompt**). **Q7 — Legacy URL dispositions** (DEC-194 localized 410 default; **R-15 + R-25 owner prompts at SEO-01 / CT-04**).
4. **§6 Category C defaults (lines 171-184).** C-1 per-tool server limits (C2 §7.1 table); C-2 queue caps and worker count; C-3 R2 lifecycle safety-net age; C-4 Nginx rate-zone values; C-5 monitoring provider and thresholds; C-6 backup retention; C-7 analytics micro-choices; C-8 support defaults; C-9 UI-baseline owner prompts (D3/U3/U5/D12/Merge edge case); C-10 blog topic selection; C-11 implementation-time re-checks; C-12 process-level notes. **C-1 through C-8 are the documented defaults feeding R-03..R-13 stop conditions.**
5. **§7 Category D source/contract blockers (lines 188-198).** **D-1** `gpt5.6-sol` provider docs (14 fields; only true hard design blocker; R-21). **D-2** Adsterra publisher terms + ad-unit code (R-18). **D-3** VPS host verification (R-26; now RESOLVED 2026-07-31, register line 34). **D-4** Legacy traffic/demand data (R-25). **D-5** AGPL commercial pricing (informational; R-05).
6. **§14 DEC-066 preservation statement (lines 286-290).** No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program. All numeric values are conservative design/safety choices adjusted from production observability (DEC-066).
7. **§11 papyr-reference cleanliness (lines 266-269).** HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`; porcelain empty; matches every prior evidence record.

### Phase 0 / FD-01..FD-05 impact

- X2 is the source of the §6 R-row stop-condition text used by PR-03 and by every later consuming task.
- The 7 collapsed owner questions (Q1..Q7) are the minimal set of remaining owner decisions. **Of those, only Q4 (R-21) is a hard blocker on a design path; Q1 (R-05), Q3 (R-18), and Q7 (R-15/R-25) are pre-launch inputs but not Phase 0 blockers.**
- DEC-066 is the binding rule for Phase 0; FD-04 dependency scan and PR-02 docs check must not invent benchmarks, comparisons, or quality scores.

---


## 11. `<workspace-root>\audit-outputs\research\research-brief-verification.md`

- **Lines observed:** 266 (~26,418 bytes). Document ID PPR-VER-001.
- **Role:** Read-only quality verification of the 25 primary research briefs (Tracks A-E). **25/25 PASS; 0 blocking defects; 2 minor observations; 3 open items.**

### Decision-grade bullets

1. **§1 Method.** All 25 briefs opened and read in full; placeholder scan clean (0 tokens in primary briefs; only legitimate prose hits at A4 §5.3 `placeholder` attribute and D2 §5 "Minimal placeholder legal pages"); DEC-066 compliance confirmed (every "benchmark" mention is a prohibition, non-goal, acceptance-criteria framing, or design-choice note).
2. **§5.4 Final count (lines 223-230).** 0 blocking defects; 2 minor observations (both in E1); 3 open items — **item 3 (all 25 briefs carry owner decision prompts) is the gate to the collapsed 7 questions in X2.**
3. **§4.9 No implementation authorization.** Every "authoriz*" hit is a prohibition statement or quoted decision text. No brief grants, implies, or requests implementation authorization.
4. **§4.11 papyr-reference cleanliness.** HEAD `981c59a`, porcelain empty, exit 0 (before and after).

### Phase 0 / FD-01..FD-05 impact

- PPR-VER-001 is the trust anchor for the briefs. PR-02's docs baseline may cite the briefs as research inputs; no brief content is normative beyond the R-row stop conditions that reference them.
- FD-05 conventions must state that research findings are design inputs, not decisions (DEC-054/057), and that no benchmark workstream is created.

---

## 12. `<workspace-root>\audit-outputs\research\source-and-decision-index.md`

- **Lines observed:** 605 (~124,705 bytes). Document ID X1.
- **Role:** Canonical cross-track source and decision map for the 25 primary research briefs. Contains K1..K18 conflict register and M1..M23 missing/stale/unavailable source register.

### Decision-grade bullets

1. **§3 Source precedence (lines 32-42).** decisions > specs > audits > legacy reference > historical legacy docs. External evidence ranks primary sources first (DEC-056).
2. **§7 Conflict register K1..K18 (lines 460-479).** Each surfaced, not resolved (DEC-183). K1 (paper-policy DEC-083 vs DEC-085/089 — **resolved by DEC-191**); K2 (VPS memory envelope — **resolved by DEC-189**); K3 (Ghostscript AGPL — **resolved by DEC-195**); K4 (ClamAV coverage vs DEC-171 — **R-10 owner prompt**); K9 (EEA/UK/CH consent — **DEC-022/190 reaffirmed**); K10 (`gpt5.6-sol` identity — **DEC-193/196 fixed**); K11 (browser-path sanitization — **DEC-192 fixed**); K12 (legacy URL dispositions — **DEC-194 + R-25**).
3. **§8 Missing/stale source register M1..M23 (lines 484-509).** M1 (Adsterra terms — R-18 owner input); M2 (`gpt5.6-sol` docs — R-21 hard blocker); M3 (AGPL pricing — informational); M4/M5 (legacy traffic/URL inventory — R-25); M9 (trusted-edge header config — R-14); M11 (Redis version pin — R-09 implementation-time re-check); M13 (VPS host state — **R-26 RESOLVED 2026-07-31**); M18 (pdf.js legacy floor — TL-06 re-check); M23 (Vercel analytics retention — PT-01 re-check).
4. **§9.2 Coverage mapping (lines 526-580).** Every UX §21 item and every arch §25.3 item maps to at least one brief, except arch §25.3.18 (post-launch legacy-tool restoration sequence) which is explicitly deferred under DEC-094.
5. **§9.4 Line counts (line 595).** Inputs read in full: AGENTS.md, research-program-plan.md, decision log (2,230 lines at that time), both specs (728 / 1,188 lines), 25 briefs (4,989 lines total).

### Phase 0 / FD-01..FD-05 impact

- X1 is the navigation index for the research. PR-02's docs baseline may reference X1 as the source for the brief inventory.
- M1, M2, M4, M5, M9, M18, M23 are the exact source-gaps the R-rows consume; Phase 0 tasks must not attempt to resolve them (they are owner/implementation-time inputs).

---


## 13. `<workspace-root>\audit-outputs\ui-home-shell-audit.md`

- **Lines observed:** 210 (~23,881 bytes). Date 2026-07-31.
- **Role:** Static read-only audit of the global visual system, app shell, Navbar, Footer, homepage of the legacy clone. Source for the D1..D13 defect list and U1..U7 uncertainties referenced by the UX spec §10.6.

### Decision-grade bullets

1. **§3 design tokens (lines 37-50).** `--color-navy #1e3a5f`, `--color-accent #2563eb`, `--color-bg #f9fafb`, `--color-background #ffffff` (**dead token**), `--color-foreground #171717`, `--font-sans 'DM Sans', system-ui, sans-serif`. DM Sans via next/font but the `--font-dm-sans` variable is never consumed by any utility (D4).
2. **§3.3 width inconsistency (D3).** Navbar container `max-w-[1440px]` (Navbar.tsx:146) vs `max-w-[1200px]` everywhere else (page.tsx:488,532,535,569; Footer.tsx:171,198). U2 asks owner intent. **This is UX §21.13 and R-23.**
3. **§3.4 motion (lines 66-72).** fade-up 0.3s; shimmer 1.4s; chevron rotations; dropdown panels open/close **instantly** (D12).
4. **§4 layout shell (lines 78-84).** `html lang="id"` hardcoded (layout.tsx:49); `body flex min-h-full flex-col font-sans`; `<main className="flex-1">`; Navbar sticky top-0; no `main` id and no skip-to-content link (D8).
5. **§5 Navbar (lines 86-96).** Frosted sticky (`bg-bg/92 backdrop-blur-md`, 52px, border-b); category dropdown model with hover+click, outside-click close, route-change close, exact-route active state; mobile `<details>` accordion; CTA "Coba Gratis" -> /compress. 13 tools in 4 categories (Alat Dasar, Keamanan, Enhancement, Konversi). **DEC-147/152/155 constrain the rebuild to a five-tool categorized navbar.**
6. **§6 Footer (lines 98-103).** Footer tools directory (`FOOTER_TOOL_CATEGORIES`, byte-identical copy of NAV_CATEGORIES — D2); bottom bar links row: Privasi/FAQ/Syarat (#)/Kontak (#) — D1 dead links; hardcoded © 2026 (D6); LanguageSwitcher with inert English row (D9) and no Escape handling (D8).
7. **§7 Homepage (lines 105-112).** Hero pill "Gratis · Tanpa akun · Auto-hapus"; H1 clamp(40px,6vw,72px); CTA "Mulai gratis" -> /compress; trust badges; tools grid 13 cards; privacy section "File kamu tetap milikmu"; **no entrance animations (U5)**; no metadata export.
8. **§10 test coverage (lines 130-137).** navbar.test.ts/footer.test.ts/landing-page.test.ts/seo-analytics.test.ts assert data shape only; no render/interaction tests; smoke.spec.ts = 200s only.
9. **§11 strengths to preserve (lines 139-151).** Frosted sticky navbar, dropdown interaction model, native details accordion, sticky-footer flex shell, cohesive token system, fluid hero type, motion discipline, credibility system, exported data contracts, SEO baseline, consistent tool-page shell.
10. **§12 defects to correct (lines 153-167).** **D1** dead "#" footer links; **D2** four divergent catalog copies; **D3** 1440 vs 1200 width; **D4** dead tokens (`--color-background`, `--font-dm-sans`); **D5** `var()` reliance on `@theme inline` tokens; **D6** hardcoded year; **D7** redundant `min-h-screen bg-bg` wrapper; **D8** a11y gaps (no skip link/main id, no aria-expanded, no focus-visible, no Escape close); **D9** language-switcher inert row + flag emoji; **D10** no active-section indication; **D11** logo-lockup mismatch; **D12** instant panel appearance; **D13** test blind spots.
11. **§13 non-goals (line 187).** No redesign, no copy rewrites beyond fixing broken links, no new sections.
12. **§14 uncertainties U1..U7 (lines 190-199).** U1 `@theme inline` emission; U2 navbar width; U3 duplicate CTA funnel; U4 inert English option; U5 homepage entrance animations; U6 exact-match active check; U7 no rendered verification was possible.

### Phase 0 / FD-01..FD-05 impact

- FD-01 scaffold must create `frontend/src/app/globals.css` as an empty token shell (plan line 360); SH-02 (Phase 2) resolves D4/D5/U1. FD-01 must not carry the legacy quality=ebook param into the scaffoldcy dead tokens.
- FD-05 conventions must record the D1..D13 defect list as the binding change-list for the visual baseline (UX §10.6; DEC-143), so later FD/SH/TL tasks correct exactly these defects and nothing else.
- R-23 (UX §21.13-16) is the owner input for U2/U3/U5/D12/Merge edge case; it is consumed at VL-03, not Phase 0.

---

## 14. `<workspace-root>\audit-outputs\ui-five-tools-audit.md`

- **Lines observed:** 303 (~37,404 bytes). Date 2026-07-31.
- **Role:** Page-by-page UX audit of Compress, Merge, Split, Image-to-PDF, PDF-to-Image in the legacy clone. Source for the shared state-card language, dropzone contract, and per-tool corrections in UX §12/§13.

### Decision-grade bullets

1. **§2 shared design system (lines 45-64).** Tokens, DM Sans, `animate-shimmer` 1.4s + `animate-fade-up` 0.3s; tool-page shell `mx-auto w-full max-w-xl px-4 py-8 sm:py-12`; tool header pattern (64px rounded-2xl accent icon tile, navy H1, slate-500 subtitle, context paragraph); feature badges 3-card grid; dropzone contract (`rounded-2xl border-2 border-dashed`, `role="button"` + tabIndex + Enter/Space); processing/done/error card classes; PrivacyNotice always visible with per-model copy; OtherTools section.
2. **§3.1 Compress (lines 69-100).** Server-only (PDFUploader -> `POST /api/compress?quality=ebook`), auto-upload on select, auto-retry on 5xx with cleared-timer note, before/after size panel with `formatPercent` (floors at 0 → "−0%"), `quality=ebook` hardcoded (audit §6 item 5; **UX §12.1 and DEC-014 remove quality controls entirely; R-04 profile thresholds**).
3. **§3.2 Merge (lines 102-131).** Client-only (pdf-lib), dnd-kit sortable list (PointerSensor 5px + KeyboardSensor, no announcements), all-or-nothing semantics (**DEC-076**), hardcoded English `merged.pdf` (**replaced by shared naming policy, DEC-042**).
4. **§3.3 Split (lines 133-160).** Client-only two-step flow, PageRangeInput charset whitelist `[\d\s,\-]`, sorted/deduped output (**corrected to order-preserving/overlap-allowed by DEC-077/078**), quick-select chips, informal "kamu" tone (audit §6 item 14).
5. **§3.4 Image-to-PDF (lines 162-188).** Hybrid with hardcoded 3MB threshold (`CLIENT_THRESHOLD_BYTES`, image-to-pdf/page.tsx:43; **replaced by DEC-015/034 routing**), magic-bytes validation (best-in-class), hover-only remove/drag controls (**fixed in UX §12.4**), server path uses `window.open` (**fixed to anchor, DEC-170**), `images.pdf` hardcoded name.
6. **§3.5 PDF-to-Image (lines 190-210).** Server-only, PageRangeInput, `file_type` PNG/ZIP, `page.png`/`pages.zip` names (**replaced by shared naming + ZIP+individual model, DEC-037/186**).
7. **§5 preserve / §6 correct (lines 248-279).** 11 preserve items; 16 correct items including the shared OtherTools visibility rule, download filename standardization, window.open fix, auto-retry timer, quality preset decision, hover-only controls, a11y semantics (role=status/alert/progressbar, aria-invalid/describedby, drag-handle labels), heading hierarchy, dropzone copy drift, validation template, empty-state copy, disabled-CTA consistency, failure-reason label, tone register, formatPercent flooring, hybrid threshold disclosure.
8. **§8 uncertainties (lines 290-300).** Visual rendering unverified; `package_output` internals not read; R2 cleanup not read; backend `pdf_size` unused; dnd-kit keyboard experience; Compress quality preset decision; Merge error-path edge case; `formatFileSize(0)` returns "0 KB".

### Phase 0 / FD-01..FD-05 impact

- FD-01 scaffold must include the shared state-card and dropzone patterns as component placeholders (they arrive fully in TL-01); the scaffold's `page.tsx` is minimal only.
- FD-05 conventions must record the 16 correct items as the binding tool-level change list (UX §12/§13), so TL-01..TL-06 correct exactly these defects.
- The Compress `quality=ebook` removal is a TL-02 decision (R-04); PR-01..FD-05 must not carry the legacy quality=ebook param into the scaffold

## 15. `<workspace-root>\audit-outputs\ui-docs-code-reconciliation.md`

- **Lines observed:** 341 (~42,707 bytes). Date 2026-07-31.
- **Role:** Claim-by-claim reconciliation of legacy `docs/19_Papyr_UIUX_Spec_v1.0.md` and `docs/32_Papyr_Brand_Guidelines_v1.0.md` against the legacy frontend implementation. Source for what is retained (pixel-accurate to code), what is stale, what is contradicted, what is missing, what is historical-only.

### Decision-grade bullets

1. **§1 Executive summary.** Design token layer is highly accurate (§3.1 accurate table). Catalog and navigation claims are the most stale (6-tool vs 13-tool, 1200px vs 1440px). Seven tools and several components are missing from both docs. Historical-only content concentrated in market/language claims (Indonesia-first) and OpenClaw/Twitter/X. Several internal self-inconsistencies in Doc19.
2. **§3 Doc19 claim matrix.** Accurate: §1.1 mobile-first shell; §2.1 typography scale; §2.2 palette tokens; §2.3 spacing; §2.4 radii; §2.5 shadows incl. custom accent shadows; §2.6 animations; §2.7 inline SVG icons; §3.1 navbar basics; §3.2 footer; §3.4 PageRangeInput; §3.5 PrivacyNotice; §3.7 upload zone; §3.8 feature badges; §3.9 sortable merge item; §3.10 sortable image item; §3.11 accordion; §3.12 rotate grid; §6.5 loading texts; §6.6 done state; §8.2 keyboard nav (with Rotate exception); §8.3 SR labels, lang, metadata. **Stale:** §3.3 PDFUploader for PDF-to-Image (only Compress uses it); §6.1 server flow only for Compress+PDF-to-Image; §3.1/§5.1 "6 link tool horizontal"; §5.5 sitemap table (9 routes); §9.1 "6 tool cards". **Contradicted:** §3.1/§4.2/§5.1 navbar 1200px (code is 1440px); §3.1/§5.1 desktop shows 6 flat tool links (code shows 4 category dropdowns); §6.1 "Progress bar real-time" (only Compress has percent; others use `fetch` without progress); §6.4 Rotate's non-standard error state; §8.2 Rotate's missing keyboard handlers. **Missing:** seven tools (protect/unlock/watermark/sign/pdf-to-word/pdf-to-excel/ocr) plus PasswordInput, signature suite, watermark suite, PDFPageViewer; footer tools directory; navbar category architecture; analytics layer; SEO infrastructure; Compress quality=ebook; server-disclosure copy; dead footer links; Rotate loading spinner variant.
3. **§4 Doc32 brand guidelines.** Accurate: §3.1 logo construction; §4.1 primary tokens; §5 typography; §6.1/6.2/6.3/6.4 spacing/grid; §7.1 cards; §7.4 icon containers; §8.1-8.3 iconography. **Stale:** §4.3 semantic colors "to be defined"; §4.4 primary button navy (only hero; tool-page primary is accent); §7.2 secondary button px-5 py-2 (navbar CTA is px-4 py-2); §8.4 icon table (6 tools vs actual 13); §3.2 "Icon only — mobile navbar collapsed" (full lockup renders). **Contradicted:** §6.1 universal 1200px (code navbar 1440px); §7.2 secondary button px-5 py-2; §3.1 logo radius rounded-md (footer uses rounded-[5px]). **Missing:** icons for seven tools; semantic color decisions; 1440px navbar convention; analytics disclosure patterns; new interaction surfaces (signature canvas, placement overlay, watermark config, PDF page viewer); error-state variants beyond standard card.
4. **§6 Conflicts with accepted rebuild decisions.** DEC-002/003/004 supersede Indonesia-first positioning; DEC-016 removes OpenClaw content; DEC-021 retains name and domain; DEC-028 anticipates the catalog/nav drift as the "correct what is stale" work; DEC-014 + DEC-195 govern Compress engine; DEC-023 locale-prefixed routes (not yet implemented); DEC-045 requires Privacy/Terms/Cookies pages (Doc32 has no cookies guidance, dead "Syarat"/"Kontak" must be resolved); DEC-011/015/030 processing disclosure copy already in code; DEC-025 re-scope privacy copy.
5. **§7 Recommendations (preserve / rewrite or extend / mark historical).** Retain: tokens, typography, spacing/radii/shadows, animations, iconography, component specs, touch-target table, contrast table (with re-verification). Rewrite: 13-tool catalog, navbar spec (4-category dropdown, 1440px container, hover+click, mobile details), footer spec, landing spec, OtherTools spec, server-flow taxonomy, loading taxonomy, error/done consistency, Compress quality, new components (PasswordInput, signature suite, watermark suite, PDFPageViewer), analytics/SEO, a11y roadmap, i18n, semantic colors, button taxonomy, icon inventory. Mark historical: Indonesia-first, OpenClaw, "6 tools", universal 1200px, "semantic colors to be defined", Doc19 §5.5 sitemap.
6. **§8 Uncertainties.** Historical code states unverifiable without git history; contrast ratios not re-measured; favicon binary; OG images not inspected in detail; Doc32 icon-table dating; backend surface for seven new tools not verified in this audit; document-ID cross-references; privacy/analytics statements in `privacy/page.tsx:47,73` and `faq/page.tsx:61` co-exist with Vercel Analytics instrumentation; FAQ copy staleness (FAQ says JPG/JPEG/PNG but image-to-pdf accepts WEBP — **DEC-187 makes JPG/JPEG/PNG/WebP official**).

### Phase 0 / FD-01..FD-05 impact

- The 13-tool catalog in legacy code becomes the 5-tool catalog (DEC-010) for launch; FD-04 / SH-04 (Phase 2) consume the canonical catalog, not the legacy 13-tool one.
- The pixel-accurate token table is the binding baseline for FD-01's empty token shell + SH-02's full token table (UX §10.1).
- The dead tokens D4/D5 corrections and the navbar/footer/spec corrections are the binding Phase 2/3 change list; FD-05 conventions must reference this audit's preserve/correct table.

---


---

## 16. Decision Precedence Conflicts

The standing precedence is **latest DEC > canonical specs > plan > audit/research evidence > legacy reference** (AGENTS.md:10; arch §1.4:74-83; plan §1:53; spec §4:69-78). Below are the material conflicts surfaced during this read-through and how each resolves.

1. **Engine and queue matrix.** X2 §4 categorized pdf-lib/pikepdf/img2pdf+Pillow/pypdfium2/pdf.js/`createImageBitmap` as research recommendations (Category A); PPR-PLN-CR-001 §3.1 flagged them as elevated without DEC-057; the plan pre-DEC-199 used proposal framing. **Resolved: DEC-199 approves the R-28 matrix; plan §6.1 and Tech Stack are normative (DEC-199 authoritative).** No remaining conflict.

2. **Phase DAG ordering (SEC-01/SEC-02 placement).** Plan pre-PPR-PLN-CORR-001 had Phase 5 SEC-01/SEC-02 while Phase 4 TL-02/TL-03/TL-04 consumed them — DAG violation. **Resolved: SEC-01/SEC-02 moved to Phase 3 as early security prerequisites (PPR-PLN-CORR-001 §2.2); plan §8 phase table updated.** No remaining conflict; PR-01..FD-05 must not assume Phase 5 placement.

3. **DEC-024 numeric precondition.** Plan pre-DEC-200 carried a misleading "gates Phase 10 and Phase 11" sentence suggesting the 90-day targets were a late-phase concern (PPR-PLN-CR-001 MEDIUM-3). **Resolved: DEC-200 approved the measure set; DEC-201 supplied the final four numeric fields; R-27 RESOLVED (register line 35).** Plan §1 PRECONDITION now states the precondition is fully met.

4. **R-15 stop condition vs Phase 2 gate.** Pre-correction plan had R-15 stop at SEO-01 only; SH-01 (Phase 2) consumed R-15 (route names depend on slugs) but the gate didn't require R-15. **Resolved: R-15 stop now "before SH-01 and SEO-01"; Phase 2 gate entry adds R-15.**

5. **GitHub Actions vs R-02.** Pre-correction plan asserted GitHub Actions normatively in Tech Stack while R-02 (hosting) was unresolved. **Resolved: Tech Stack re-labeled as "CI provider per R-02 (proposal: GitHub Actions, CI core gate only)"; FD-04 workflow artifact is contingent on R-02 disposition.** R-02 is RESOLVED (GitHub, `fazulfi/mypapyr`, private, main — register line 10); the proposal is now de facto selected.

6. **DEC-051 vs public record (`gpt5.6-sol`).** DEC-051/plan wording said the identifier "does not imply a specific vendor"; X1 K10 / X2 B-4 reconciled it with the public OpenAI GPT-5.6 Sol identification (released 2026-07-09). **Resolved: DEC-193 fixes the OpenAI-compatible gateway identity; DEC-196 fixes the model identifier (`mypapyr`, not `gpt5.6-sol`) and the bearer auth scheme.** R-21 remains the only true design-path hard blocker (provider contract fields beyond identity/auth).

7. **DEC-022 + DEC-190 advertising consent.** DEC-022 accepted no-prior-consent ads in all regions; D1 / D5 / X2 B-3 / DEC-190 reaffirmed after research review. **No silent reversal.** The decision baseline is unchanged; the owner-supplied Adsterra terms + ad-unit code (R-18) and qualified legal review (R-19) remain launch prerequisites; prior-consent may still be required by binding terms or law, and Papyr must implement CMP, contextual ads, or regional suppression in that case (DEC-022 consequence clause).

8. **DEC-083 vs DEC-085 paper policy.** DEC-083 said paper from locale + regional rule; DEC-085 (later) selected the trusted edge country code; DEC-089 completed the A4 fallback. **Resolved: DEC-191 confirms US/CA → Letter, otherwise A4; locale never decides paper; R-14 records the trusted-header config at TL-05 implementation time.**

9. **Browser sanitization gap (pdf-lib active content).** DEC-090 targeted server outputs; DEC-093 required equivalent browser safety. A4 §9.1 / D5 §6.2 flagged pdf-lib page copies can carry active content; no separate browser sanitization engine in MVP. **Resolved: DEC-192 routes active-content-bearing Merge/Split inputs to the server sanitization path; fail-closed when scanner or sanitization unavailable.** Implementation vehicle: SEC-01 + SEC-02 (early Phase 3).

10. **VPS memory envelope (K2).** Two 2 GiB workers + ClamAV 3–4 GiB + API + Redis + Nginx + Netdata exceed the legacy ~8 GB / 4 vCPU envelope at upper bounds; X2 §9.2 flagged this. **Resolved: DEC-189 sets the launch posture as one active worker, one concurrent job, designed around the conservative bound.** R-26 verified current host state (15 GiB RAM, 4 cores, 2 GiB swap, Docker 29.6.2) on 2026-07-31; register line 34.

11. **Local "naked" implicit assignment of image-to-pdf 3MB threshold.** Legacy code hardcoded 3MB (`image-to-pdf/page.tsx:43`); spec §12.4 says routing uses the limit policy from DEC-015/034. **Resolved by plan correction + UX spec.** No conflict in the rebuild, but Phase 0 scaffolds must not carry the hardcoded 3MB.

12. **PR-02 pytest dependency.** PR-02 originally ran pytest in Phase 0 before any Python tooling; phase ordering inconsistency (PPR-PLN-CR-001 MEDIUM-6). **Resolved: PR-02 rewritten as dependency-free shell-only with `cmp -s` and `grep`.** Future PR-02 must use this model.

13. **`papyr-reference/` HEAD and porcelain claim.** All sources (PPR-PLN-CR-001, PPR-PLN-CORR-001, PPR-PLN-OWN-001, PPR-PLN-FR-001, plan §10 item 8, X2 §11, X1 §9.3) agree: HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`, `git status --porcelain` empty, exit 0. **No conflict.**

14. **DEC-202 plan approval vs DEC-060 implementation gate.** DEC-202 approves the plan; DEC-060 says coding begins only after explicit owner approval of design and implementation plan. **Resolved: DEC-202 IS the explicit approval; both are satisfied.** Separately gated actions (G-1..G-11) still require their own owner authorization at the moment of action.

15. **R-28 (engine matrix) + ClamAV proposal framing.** R-28 approves the engines (DEC-199); ClamAV remains a proposal under R-10 (PPR-PLN-CR-001 §3.1 evidence; PPR-PLN-CORR-001 §2.1 confirmed). **No conflict; the engine matrix explicitly excludes ClamAV, and R-10 records the ClamAV candidate as a proposal at SEC-03 implementation time.**

16. **Compress engine Ghostscript vs permissive fallback.** A1/A2 recommended Ghostscript (AGPL/commercial); A5/A6 fully permissive. **Resolved: DEC-195 + R-05** with focused license review before launch and permissive/commercial fallback if unacceptable.

17. **DOC-187 JPG/JPEG/PNG/WebP acceptance.** FAQ legacy copy said JPG/JPEG/PNG only; code accepted WebP. **Resolved: DEC-187 makes JPG/JPEG/PNG/WebP official; R-24 owner approval corrects the FAQ copy.**

18. **Header lang="id" hardcoding.** Legacy layout set `html lang="id"` (layout.tsx:49); spec §9 / DEC-023/047 require locale-aware. **Resolved by UX spec; SH-03 (Phase 2) replaces.** No Phase 0 conflict; FD-01 scaffold must not lock the lang attribute.


---

## 17. Phase 0 Impact

What each source requires of Phase 0 (PR-01, PR-02, PR-03) and Phase 1 (FD-01..FD-05). Compiled from the per-source sections above; this is the operative handoff.

### PR-01 (Repository creation and branch strategy — plan lines 304-317)

- Create the new-repository directory tree at workspace root (DEC-198): `frontend/`, `backend/`, `deploy/`, `scripts/`, `docs/`. `.gitignore` must exclude `papyr-reference/`, `node_modules`, `.next`, `.env`, `__pycache__`, test artifacts, local caches (AGENTS.md:9; DEC-159; DEC-198).
- Log R-01 (DEC-198) and R-02 (GitHub, `fazulfi/mypapyr`, private, `main`; owner instruction 2026-07-31) before any git operation.
- Verify with `git -C papyr-reference status --porcelain` from workspace root; expected empty porcelain, exit 0; HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` (register line 10; PPR-PLN-FR-001 §8; X2 §11).
- Step 4 `git init` runs under G-1 (owner authorization); R-02 git hosting/remote setup is already resolved but repo creation itself is still owner-gated.
- Suggested commit subject: `chore: initialize rebuild repository skeleton at workspace root`.

### PR-02 (Canonical documentation baseline — plan lines 319-332)

- Create `scripts/check-docs-migration.sh` (shell-only, dependency-free). It exits non-zero when `papyr-rebuild-decisions.md` is absent, when the decision log does not contain every DEC-001 through DEC-**202** ID (note: plan line 328 says DEC-201, but the actual log now extends to DEC-202 per the latest amendment; PR-02 must reconcile this), when either spec under `docs/superpowers/specs/` is absent, or when `docs/canonical-docs-baseline.md` is absent.
- Step 2 verifies FAIL before `docs/canonical-docs-baseline.md` exists.
- Step 3 creates `docs/canonical-docs-baseline.md` documenting the canonical paths, the DEC-001..DEC-202 range, and governed-record status (DEC-006, DEC-026, DEC-198).
- Step 4 verifies PASS.
- **No pytest, no Python tooling prerequisite** (PPR-PLN-CORR-001 §2.6; MEDIUM-6 fix). `cmp -s` + `grep` only.
- Suggested commit subject: `docs: record canonical documentation baseline at repository root`.

### PR-03 (Resolution register — plan lines 334-347)

- Create `docs/resolution-register.md` inside the rebuild repo with one row per R-01..R-28 (5-column table mirroring the root-level `docs/resolution-register.md` format).
- Pre-fill: **R-01 RESOLVED (DEC-198)**, **R-02 RESOLVED** (with the verbatim owner instruction "mypapyr aja jangan rebuild" and date 2026-07-31), **R-27 RESOLVED (DEC-200 + DEC-201)**, **R-28 RESOLVED (DEC-199)**.
- The remaining 25 R-rows (R-03..R-26) carry their stop conditions verbatim from plan §6 lines 233-256. Owner-filled at execution time; PR-03 does not invent values.
- Step 3 verifies `grep -c '^| R-' docs/resolution-register.md` returns 28.
- Step 4 is owner review at the Phase 0 gate.
- Suggested commit subject: `docs: add owner resolution register`.

### FD-01 (Frontend workspace scaffold — plan lines 357-370)

- Create `frontend/package.json`, `tsconfig.json`, `next.config.ts`, `eslint.config.mjs`, `postcss.config.mjs`, `.prettierrc`, empty `frontend/src/app/globals.css`, minimal `frontend/src/app/page.tsx`.
- Scripts: `dev`, `build`, `start`, `lint`, `test` (Vitest), `test:e2e` (Playwright), `format:check`. Dependency floors: next, react, react-dom, tailwindcss v4, typescript.
- **Do not install dependencies in this phase**; PR-01..FD-05 are file creation only (G-4 for provider-side actions; no installs authorized by plan).
- **Do not lock `html lang="id"`** (DEC-023/047). The minimal `page.tsx` must leave the lang attribute set by SH-03 in Phase 2.
- The empty `globals.css` must not carry the dead tokens `--color-background` or the unused `--font-dm-sans` variable (audit D4/D5; UX §10.1 corrections).
- Suggested commit subject: `chore(frontend): scaffold Next.js workspace`.

### FD-02 (Backend workspace scaffold — plan lines 372-385)

- Create `backend/requirements.txt`, `requirements-dev.txt`, `ruff.toml`, `pytest.ini`, `backend/app/__init__.py`, `backend/app/main.py` (FastAPI shell with `/health` endpoint).
- Scripts: `ruff check`, `ruff format --check`, `pytest`. First failing test: `backend/tests/test_health.py` asserts `GET /health` returns 200 with `status: ok`.
- **Do not install dependencies or start the FastAPI server.** File creation only; CI runs pytest in Phase 4+ against a real Redis + R2 fixture.
- **Do not write any router or service.** Phase 3 tasks BE-01..BE-10 introduce the queue, R2, sanitization; FD-02 is the shell only.
- Suggested commit subject: `chore(backend): scaffold FastAPI workspace`.

### FD-03 (Deploy workspace scaffold — plan lines 387-400)

- Create `deploy/docker-compose.yml` skeleton (services: `nginx`, `api`, `redis`, `workers`; `scanner` reserved for SEC-03); `deploy/nginx/conf.d/production.conf` skeleton; `deploy/.env.production.example` (non-secret variable names only; **no real keys**); `deploy/runbook-vps.md` outline.
- Failing test: `docker compose -f deploy/docker-compose.yml config --quiet` (config-validation only; Docker is not started; exit 0 expected after step 4).
- `deploy/.env.production.example` must not contain real secrets (DEC-176); install mode 600 per arch §2.1.
- `deploy/runbook-vps.md` wording: "canonical operations runbook (replaces the legacy `papyr-reference/docs/runbook-vps.md` as the operating reference; the legacy file is never modified)" (PPR-PLN-CORR-001 LOW-13 fix).
- Suggested commit subject: `chore(deploy): scaffold compose and nginx skeleton`.

### FD-04 (CI core gate skeleton — plan lines 402-415)

- Path contingent on R-02 (resolved to GitHub). Proposal: `.github/workflows/ci.yml` on GitHub Actions.
- Add `scripts/check-ci.sh` that parses the workflow YAML and asserts **no `deploy` job exists** and **no secret is exposed to `pull_request_target`** events.
- Jobs: frontend lint, test, build; backend ruff and test; production build verification; security scanning (Trivy) on built images; **no auto-deploy** (DEC-160).
- CI secrets and environments are configured at execution under G-4.
- Follow the MEDIUM-7 naming convention from PPR-PLN-CORR-001 §2.7: name the script in the task Files list and in the verification command.
- Suggested commit subject: `ci: add core gate without deployment`.

### FD-05 (Root tooling conventions — plan lines 417-429)

- Create `README.md`, `CONTRIBUTING.md`, `docs/plan/index.md`.
- Commit prefixes: `feat`, `fix`, `docs`, `chore`, `test`, `ci`, `refactor`, `security`. TDD is mandatory. Phase plans may expand into their own files under `docs/superpowers/plans/`.
- `docs/plan/index.md` must link to `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` (verified by `grep -rn 'docs/superpowers/plans' docs/`).
- Conventions must explicitly record:
  - **DEC-066 no benchmark program.** No corpus, matrix, comparative performance study, quality-score program, VPS benchmark workload, or benchmark report.
  - **DEC-143 visual baseline.** Limited to D1–D13 corrections + the consistency/a11y/localization/performance change list. No new aesthetic.
  - **DEC-143 one canonical tool catalog** (UX §8.4 / D2 correction). Five tools at launch (DEC-010).
  - **DEC-066/WCAG 2.2 AA acceptance target** (DEC-062). Automated + representative manual keyboard and AT testing; documented exceptions register; no certification claims.
  - **DEC-031 supported browser matrix** (latest two major versions Chrome/Edge/Firefox/Safari desktop; current Safari iOS/iPadOS; Chrome Android; progressive enhancement).
  - **DEC-174/DEC-175 data minimization** for logs/Redis (no files/filenames/passwords/signed URLs/object keys/previews/extracted content).
  - **DEC-176 secrets** handled via protected VPS env config; legacy credentials rotated before production use.
  - **DEC-172 non-root SSH user with sudo NOPASSWD** for any deployment-time admin; direct root SSH login disabled.
  - **DEC-179 monthly dependency review + prompt critical fixes.**
- **Step 3: review conventions with the execution agent** so branch and commit boundaries are applied consistently.
- Suggested commit subject: `docs: add contribution and planning conventions`.

---

## 18. Cross-Source Synthesis (parent handoff)

1. **The rebuild is approved and ready to execute.** DEC-188 (specs), DEC-189 (one worker), DEC-190 (ad risk), DEC-191 (Letter rule), DEC-192 (active-content routing), DEC-193 (gateway), DEC-194 (410 default), DEC-195 (Ghostscript subprocess), DEC-196 (gateway identity), DEC-197 (DEC-189..196 revisions), DEC-198 (root), DEC-199 (engine matrix), DEC-200/201 (90-day targets), DEC-202 (plan approval) are all in force. R-01, R-27, R-28 are RESOLVED. R-26 is RESOLVED (current host state verified). R-02 is RESOLVED (GitHub, `fazulfi/mypapyr`, private, main).
2. **Phase 0 is fully unblocked.** PR-01's only owner-gated step is `git init` under G-1; PR-02 has no Python tooling prerequisite and runs dependency-free; PR-03 creates the register with 3 pre-filled RESOLVED rows. FD-01..FD-05 are file-creation only (no installs, no servers).
3. **Later phases retain their owner-gated actions.** G-1..G-11 (plan §7) cover repository, VPS, deploy, accounts, gateway, Adsterra, legal, credentials, spending, concurrency, per-URL deviation. Phase 0 must not preempt any of them.
4. **No benchmark workstream anywhere.** All numeric values in the plan are conservative design or safety choices adjusted from production observability. Phase 0 verification commands are functional tests, config checks, or CI gates — never benchmarks.
5. **No implementation authorization leaks.** Plan §10 item 9: "approval of this plan authorizes execution of the plan's tasks only. Separately gated actions in Section 7 remain individually owner-authorized."
6. **`papyr-reference/` is read-only and untouched.** Every audit cited here verified HEAD `981c59a171f4b83c9e2afcecc6e934bee14a3a5e` and empty porcelain. This comprehension summary wrote only to its target file.
7. **No `.env.papyr` was read.** No secret/token/credential/IP was transcribed. References are redacted (`CLOUDFLARE_API_TOKEN`, `<vps-ip>`, etc.).
8. **Compressed read of the precedent.** PR-01..FD-05 should proceed file-by-file, task-by-task, with the suggested commit subjects, against the exact file paths in the plan's §8 phase plans. Each task ends at a review-and-commit boundary; the parent will verify before the next task begins.

---

## 19. Files Touched by This Comprehension

- Created: `<workspace-root>\audit-outputs\phase-0\source-comprehension-summary.md` (this file).
- Modified: none. The 15 source files are unchanged. The decision log is unchanged. `papyr-reference/` is unchanged.
- No installs, builds, servers, VPS access, deployment, account creation, remote actions, or git writes were performed.

---

## 20. Compliance Statement

- No decision log entry, specification, audit, evidence, or `AGENTS.md` content was modified.
- No implementation, dependency installation, VPS/SSH access, deployment, account creation, provider authentication, or remote mutation was performed.
- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or referenced (DEC-066).
- No `.env.papyr`, secret, token, credential, IP, or chat-id value was transcribed. References use redacted names only.
- Findings are recommendations for the parent agent's Phase 0 PR-01 and FD-01..FD-05 execution, not accepted decisions; they rest on the existing decision baseline and the two approved specs.
- Chat-only summary is insufficient; this file is the primary deliverable.
