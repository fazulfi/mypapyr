# Papyr Rebuild Decision Log

## Purpose

This document records product and engineering decisions made during discovery for the Papyr rebuild. It is a living decision log, not an approved implementation specification.

## Status definitions

- **Proposed**: Direction discussed but not yet confirmed.
- **Accepted**: Explicitly selected by the project owner.
- **Superseded**: Replaced by a later decision.
- **Deferred**: Intentionally postponed.

---

## DEC-001 — Rebuild instead of restoring the inactive deployment

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Rebuild Papyr rather than restoring the inactive website and preserving the existing system as-is.
- **Rationale:** The existing website is no longer active, while the repository contains production coupling, stale documentation, and unfinished scope that should not automatically carry into the new product.
- **Consequences:**
  - The old repository is a source of requirements and reusable patterns, not the default architecture.
  - Existing features, infrastructure, and documents must each justify their inclusion.
  - Implementation will begin only after discovery, design, and planning are approved.

## DEC-002 — Papyr remains a modern PDF-tools product

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr will remain a PDF-tools product, rebuilt as a modern international service.
- **Rationale:** The project owner selected a modern PDF-tools direction rather than a document workspace or an unrelated product pivot.
- **Consequences:**
  - The product retains the core PDF utility category but does not require one-to-one parity with all 13 legacy tools.
  - Feature scope, user experience, and processing architecture will be reconsidered during discovery.
  - The legacy Indonesia-first positioning will not be retained.

## DEC-003 — Target international markets

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Target the United States, Latin America, and Europe rather than focusing on Indonesia.
- **Rationale:** These are the markets explicitly selected by the project owner for the relaunch.
- **Consequences:**
  - Product positioning, SEO research, privacy compliance, performance, and localization must support multiple regions.
  - “Europe” and “Latin America” must be broken down into prioritized languages and countries during planning.
  - Indonesian copy and Indonesia-specific market assumptions are historical references only.

## DEC-004 — Launch in English and Spanish, then localize incrementally

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Launch with English and Spanish. Expand localization incrementally so other target-region languages are covered over time.
- **Rationale:** English and Spanish provide broad initial coverage while keeping launch scope manageable.
- **Consequences:**
  - Internationalization must be architectural, not added as an afterthought.
  - Initial SEO, UI copy, metadata, legal copy, and QA must cover English and Spanish.
  - Additional language sequencing and translation governance remain to be decided.

## DEC-005 — Free tools monetized through Adsterra

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr's initial business model will offer free PDF tools and monetize traffic using Adsterra.
- **Rationale:** The project owner selected advertising rather than SaaS subscriptions, portfolio-only goals, or delayed monetization.
- **Consequences:**
  - SEO traffic, repeat utility, page performance, and ad-view inventory become core business concerns.
  - Ad placement must not obstruct uploads, downloads, consent, or user trust.
  - Adsterra policy, eligible formats, privacy requirements, geographic consent, and Core Web Vitals impact require explicit research and validation.
  - Revenue assumptions should not be finalized before traffic and geography data are available.

## DEC-006 — Maintain one local decision log during discovery

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Record discovery decisions in a single local document at `papyr-rebuild-decisions.md` before the rebuild repository is created.
- **Rationale:** The current workspace is empty, and the project owner requested an immediate written record without cloning the legacy repository first.
- **Consequences:**
  - Every confirmed discovery decision will be appended here using a stable decision ID.
  - When the rebuild repository exists, this log can be migrated into the canonical documentation structure.
  - Changes to prior decisions will be represented as superseding records rather than silently rewriting history.

## DEC-007 — Prioritize fast, task-oriented general users

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The primary launch audience is a general user arriving to complete one PDF task quickly, usually without wanting to learn a product or create an account.
- **Rationale:** The project owner selected fast general users over narrower student, professional, or small-business segments.
- **Consequences:**
  - Each tool should minimize time-to-first-action and cognitive load.
  - Anonymous, no-sign-up usage is the default assumption unless a later decision supersedes it.
  - Landing pages must satisfy search intent directly and avoid forcing users through dashboards or onboarding.
  - Advertising must not obstruct upload, processing, or download actions.
  - Advanced workflow and team features are lower priority than reliability, speed, and clarity.

## DEC-008 — Make speed and simplicity the primary product promise

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr's highest product priority is a fast and simple path from arrival to completed PDF task.
- **Rationale:** Speed, simplicity, privacy, free access, and output quality are all desired principles, but the project owner selected speed and simplicity as the tie-breaker when trade-offs occur.
- **Consequences:**
  - The core flow should be open tool, upload or select files, configure only what is necessary, process, and download.
  - Privacy, quality, and generous free access remain required product principles, but must be balanced against task completion speed.
  - Optional controls should use progressive disclosure rather than appearing upfront.
  - Performance budgets and usability completion time should become launch acceptance criteria.
  - Advertisements must not interrupt or obscure the critical task flow.

## DEC-009 — Launch with five core PDF tools

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The first public release will contain five core PDF tools rather than recreating all 13 legacy tools at once.
- **Rationale:** A focused initial catalog supports a faster relaunch and allows stronger quality, usability, localization, SEO, and testing for each tool.
- **Consequences:**
  - The five tools must be selected explicitly based on user demand, search opportunity, technical feasibility, and operating cost.
  - The remaining legacy tools are candidates for later releases, not automatically abandoned.
  - Shared processing and UI foundations should support incremental addition of tools.
  - Launch completeness means five production-ready tools, not partial implementations of a larger catalog.

## DEC-010 — Define the five-tool MVP catalog

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The initial catalog will contain Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG.
- **Rationale:** These tools address common, task-oriented use cases while avoiding the heavier dependencies and operational complexity required by OCR and office-document conversion in the first release.
- **Consequences:**
  - Shared upload, ordering, page selection, progress, and download experiences should be designed across these five tools.
  - OCR PDF, PDF to Word, Sign PDF, Protect PDF, and other legacy capabilities are deferred candidates for later phases.
  - Architecture must not prematurely include LibreOffice, Tesseract, Camelot, or other dependencies unnecessary for this catalog.
  - Each selected tool requires an English and Spanish landing page, metadata, help copy, and executable QA coverage.

## DEC-011 — Use hybrid, browser-first file processing

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Use a hybrid processing model that prefers local browser processing and routes operations to a server when quality, file complexity, device capability, or reliability requires it.
- **Rationale:** This model balances task speed, privacy, infrastructure cost, and output quality across the five-tool MVP.
- **Consequences:**
  - Merge PDF, Split PDF, and JPG to PDF are browser-first candidates.
  - Compress PDF and demanding PDF to JPG jobs may require server processing or fallback.
  - Routing must be based on measured capabilities and explicit rules rather than hidden arbitrary behavior.
  - The UI must clearly disclose whether a file stays on-device or is uploaded temporarily.
  - Exact file-size, page-count, image-dimension, memory, and device limits remain open pending browser and library research.

## DEC-012 — No user accounts in the MVP

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** All five MVP tools must be usable anonymously without registration or login.
- **Rationale:** Papyr targets task-oriented visitors arriving from search who need to complete a PDF job immediately; mandatory or optional account features would add friction and infrastructure without supporting the core promise.
- **Consequences:**
  - The MVP will not include authentication, user profiles, cloud history, saved files, or cross-device synchronization.
  - Processing status and results must work within an anonymous browser session.
  - Server-side abuse controls cannot depend on user identity and must instead use privacy-conscious rate limits and operational safeguards.
  - Analytics and advertising consent must not be conflated with account creation.

## DEC-013 — Delete server-processed files within one hour

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Any source file, intermediate artifact, and generated result uploaded for server-side processing must be deleted automatically no later than one hour after upload or creation.
- **Rationale:** A one-hour maximum provides a short recovery and download window while limiting privacy exposure, storage cost, and operational liability.
- **Consequences:**
  - One hour is a hard upper bound, not a guaranteed retention period; files may be deleted earlier after processing or download.
  - Storage objects must carry enforceable expiry metadata, with a scheduled cleanup path for failed or abandoned jobs.
  - The product must disclose the retention policy before upload and must not imply permanent availability of result links.
  - Application logs, analytics, backups, and error reporting must not contain file contents or accidentally preserve uploaded documents.
  - Automated tests and operational monitoring must verify expiration and cleanup behavior.

## DEC-014 — Compress automatically for premium screen quality

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Compress PDF will use one automatic, high-end compression mode optimized for premium on-screen viewing rather than exposing quality presets in the MVP.
- **Rationale:** Papyr should produce a consistently polished result without forcing task-oriented users to understand DPI, image codecs, or compression trade-offs. The intended output is smaller while remaining crisp for reading, sharing, and normal high-quality screen use.
- **Consequences:**
  - The UI will not offer Strong, Balanced, High Quality, target-size, DPI, or other advanced controls in the MVP.
  - Compression must preserve searchable/selectable text, links, page geometry, and legibility whenever the source format permits.
  - Images may be intelligently downsampled and re-encoded for premium screen use; exact thresholds and measurable quality floors will be specified after engine benchmarking.
  - Papyr must not degrade an already optimized file merely to claim a larger reduction.
  - If meaningful reduction cannot be achieved within the quality floor, the result must say so honestly.
  - True high-quality compression requires a capable compression engine and is expected to use server-side processing rather than relying only on pdf-lib or PDF.js.

## DEC-015 — Start with conservative browser-processing limits

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Adopt conservative, device-aware browser-processing limits for the MVP and route heavier or riskier jobs to the server automatically.
- **Rationale:** PDF memory use can greatly exceed compressed file size, Web Workers do not increase the browser process memory budget, and iOS Safari has substantially tighter practical canvas and memory constraints than desktop browsers. Reliability takes priority over maximizing local processing coverage at launch.
- **Consequences:**
  - Modern desktop browser-first jobs are initially limited to 100 MB total input and 500 PDF pages.
  - Capable non-iOS mobile browser-first jobs are initially limited to 50 MB total input and 200 PDF pages.
  - iPhone and iPad browser-first jobs are initially limited to 25 MB total input and 100 PDF pages.
  - PDF to JPG is initially limited to 200 pages on desktop and 50 pages on mobile, with sequential page rendering and a 16-megapixel per-page safety ceiling for broad iOS compatibility.
  - JPG to PDF is initially limited to 50 images and 100 megapixels total on desktop or 40 megapixels total on mobile.
  - Compress PDF uses server-side processing by default.
  - Routing must also evaluate decoded image dimensions, page geometry, encryption, file corruption, estimated peak memory, and browser capabilities rather than relying only on file size.
  - These are product safety limits, not browser hard limits. They may be raised only after anonymous reliability telemetry and representative real-device testing demonstrate acceptable failure rates.
  - Users must see whether processing will occur locally or via temporary upload before it begins.

## DEC-016 — Remove Guinevere from the Papyr rebuild

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Remove Guinevere from the rebuilt Papyr product and its active roadmap rather than rebuilding, deferring, or operating it as a parallel Papyr workstream.
- **Rationale:** The project owner explicitly chose to remove Guinevere after reviewing its relationship to the legacy Papyr roadmap and its separate runtime, infrastructure, and operational scope.
- **Consequences:**
  - The rebuild will not include Guinevere agents, BullMQ, Redis, PostgreSQL/Drizzle, Telegram reporting, heartbeat, persona, or decision-engine infrastructure.
  - Legacy Guinevere code and documentation may be preserved only as historical archive material during repository reconciliation.
  - The unmerged Guinevere feature branch will not define requirements for the rebuilt product.
  - Product monitoring, security checks, SEO analytics, and operational alerting must use simpler dedicated systems where needed rather than relying on Guinevere.

## DEC-017 — Retain the Vercel, VPS, Cloudflare, and R2 production topology

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Retain the proven production topology of Next.js on Vercel, FastAPI behind Nginx and Docker on a VPS, Cloudflare in front of the public domains and API, and Cloudflare R2 for temporary server-processed files.
- **Rationale:** The legacy repository confirms that this topology was deliberately migrated, hardened, monitored, and operated. It also supports the capable native PDF engines required for Papyr's high-quality processing goals.
- **Consequences:**
  - The rebuild will modernize and make this topology reproducible rather than replacing it with a serverless-only architecture.
  - Frontend and backend deployments remain independently operable.
  - VPS configuration, Nginx behavior, backups, monitoring, and disaster recovery must be represented by executable configuration or automation rather than only prose and manual evidence.
  - All legacy credentials must be rotated, and historical migration evidence must be reviewed for exposed secret material.
  - R2 retention and cleanup must enforce the one-hour maximum established by DEC-013.

## DEC-018 — Allow only non-intrusive banner and native advertising at launch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** At launch, Adsterra monetization is limited to non-intrusive banner and native advertising placements.
- **Rationale:** These formats support the advertising business model while protecting Papyr's speed, simplicity, Core Web Vitals, and task-completion experience.
- **Consequences:**
  - Popunders, interstitials, social bars, in-page push, forced redirects, and anti-adblock messaging are excluded from launch.
  - Ad slots must reserve stable dimensions to prevent layout shift and must not obstruct upload, processing, consent, or download controls.
  - Third-party advertising scripts must load asynchronously or lazily where appropriate and remain subject to regional consent requirements.
  - Any future use of a more intrusive format requires a new explicit decision supported by measured revenue, performance, trust, and task-completion data.

## DEC-019 — Use a Redis-backed queue with dedicated processing workers

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Use a Redis-backed task queue and dedicated workers for server-side PDF jobs, with immediate dispatch whenever worker capacity is available.
- **Rationale:** Redis adds negligible coordination overhead relative to PDF processing time while fixing the legacy in-memory task store's restart loss, cross-process inconsistency, uncontrolled fire-and-forget execution, and random polling failures across Uvicorn workers.
- **Consequences:**
  - API processes enqueue work and expose durable status rather than owning long-running processing in module-global memory.
  - Available workers should claim jobs immediately; the system must not introduce an artificial waiting period.
  - Job state, progress, timeout, retry policy, cancellation, result expiry, and failure reasons must be explicitly modeled.
  - PDF engines run in bounded worker processes so blocking native operations do not block the API event loop.
  - Queue depth, wait time, execution time, failures, retries, and stuck jobs require monitoring.
  - Redis availability and recovery become production operational concerns and must be covered by health checks, deployment configuration, and the runbook.

## DEC-020 — Apply adaptive anonymous fair-use controls

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Protect server-side processing with adaptive anonymous fair-use controls rather than mandatory accounts, a rigid daily quota for ordinary users, or a challenge on every upload.
- **Rationale:** Papyr must remain immediate and frictionless for legitimate task-oriented visitors while controlling automated abuse, queue saturation, and VPS operating cost.
- **Consequences:**
  - Controls may consider IP or network signals, job frequency, concurrent jobs, input size and complexity, queue pressure, abnormal traffic patterns, and processing cost.
  - Normal users should not encounter a fixed daily quota unless measured capacity or abuse data later justifies one.
  - Suspicious or high-cost traffic may be delayed, rejected with a clear retry response, or challenged selectively.
  - Enforcement must avoid retaining document contents and should minimize personal-data collection.
  - Limits and responses must be consistent across API processes rather than using independent per-process counters.
  - Thresholds require load testing, production telemetry, monitoring, and documented operational overrides.

## DEC-021 — Retain the Papyr name and mypapyr.com domain

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Retain the Papyr product name and `mypapyr.com` domain for the international rebuild.
- **Rationale:** The existing identity and domain remain the chosen foundation; the rebuild will modernize their market positioning rather than delay launch for a complete renaming exercise.
- **Consequences:**
  - Visual identity, voice, messaging, and localized copy may be redesigned while retaining the Papyr name.
  - Canonical URLs, SEO information architecture, email identity, legal documents, and deployment configuration should use `mypapyr.com` and its intended subdomains.
  - Legacy Indonesia-first positioning must not be carried into the new international identity.
  - Trademark, naming-conflict, and international pronunciation checks remain necessary before public launch but do not constitute an automatic rebrand.

## DEC-022 — Load advertising without prior consent in all launch regions

- **Date:** 2026-07-31
- **Status:** Accepted risk
- **Decision:** Load the approved non-intrusive Adsterra banner and native advertisements in all launch regions without first requiring consent through a CMP.
- **Rationale:** The project owner explicitly selected the simplest advertising flow and does not want a prior-consent interaction before advertisements are displayed.
- **Consequences:**
  - This decision is recorded as an accepted compliance risk, not as evidence that the approach satisfies GDPR, UK GDPR, Swiss privacy law, ePrivacy requirements, US state privacy requirements, or Adsterra policy.
  - Advertising remains limited by DEC-018 to non-intrusive banner and native formats; this limitation does not itself remove third-party tracking or consent obligations.
  - Before public launch, the actual Adsterra scripts, cookies, identifiers, data recipients, and regional behavior must be reviewed against current provider terms and applicable legal requirements.
  - If prior consent is legally or contractually required, Papyr must either implement compliant consent controls, serve demonstrably non-tracking contextual advertisements, or suppress advertisements in the affected regions.
  - A legal or provider-policy requirement supersedes this implementation preference; the product must not claim compliance without supporting evidence.

## DEC-023 — Prefix every localized route with its locale

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Use an explicit locale prefix for every localized route, including English and Spanish.
- **Rationale:** A symmetric route structure such as `/en/...` and `/es/...` makes locale resolution explicit and provides a consistent foundation for adding more languages later.
- **Consequences:**
  - English does not use unprefixed tool routes as canonical URLs.
  - Localized tool slugs, metadata, structured data, internal links, sitemaps, canonicals, and hreflang annotations must be generated consistently per locale.
  - Requests without a locale require a documented redirect or locale-selection policy that avoids redirect loops and SEO duplication.
  - Legacy unprefixed URLs require a deliberate redirect map to preserve useful backlinks and search equity where applicable.

## DEC-024 — Judge 90-day MVP success by reliability and organic growth

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The primary 90-day success criteria are reliable task completion, fast user experience, healthy Core Web Vitals, organic-search growth, and meaningful usage across all five launch tools. Advertising revenue is a secondary indicator during this period.
- **Rationale:** A dependable product and growing search footprint are prerequisites for sustainable advertising revenue and provide a stronger early signal than revenue alone.
- **Consequences:**
  - Launch acceptance and operating dashboards must measure job success and failure, processing and queue latency, uptime, Core Web Vitals, organic entrances, tool usage distribution, and completed downloads.
  - Metrics must distinguish browser-local jobs from server-side jobs without collecting document contents.
  - Exact numeric targets and baseline measurement windows must be defined before implementation planning is approved.
  - Revenue, fill rate, and advertising impact remain monitored but do not justify degrading the core task flow during the first 90 days.

## DEC-025 — Use detailed product analytics without replaying document workflows

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Collect detailed product events, funnels, attribution, performance, and sanitized error analytics, but do not use session replay on document-tool workflows and do not collect fingerprinting data or document-sensitive information.
- **Rationale:** Papyr needs enough instrumentation to improve reliability, SEO conversion, tool completion, and advertising performance without recording the documents or sensitive interactions users entrust to the service.
- **Consequences:**
  - Analytics may cover acquisition source, page and locale, tool selection, processing mode, coarse input bands, funnel stages, timings, sanitized failure categories, download completion, Web Vitals, and advertising performance where permitted.
  - Analytics must never include file contents, previews, rendered document text, file names, object keys, signed URLs, passwords, full error payloads containing user data, or stable device fingerprints.
  - Session replay must be disabled on uploader, editor, processing, and result workflows; masking alone is not considered sufficient protection.
  - Event schemas require a privacy review, data-retention policy, regional activation controls, and automated tests or audits that guard against sensitive-field leakage.
  - This analytics scope does not override applicable consent or opt-out obligations, including the accepted compliance risk recorded in DEC-022.

## DEC-026 — Create concise canonical documentation and preserve legacy history in an archive

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Create a new concise set of canonical documents for the rebuilt product and preserve useful legacy product, engineering, roadmap, migration, and execution history in a clearly separated archive.
- **Rationale:** The legacy repository contains valuable design and operational history, but active documents are duplicated, stale, provider-inconsistent, and mixed with generated reports and execution artifacts.
- **Consequences:**
  - Active documentation must have a single authoritative source for product scope, architecture, API, deployment, operations, security, privacy, localization, monetization, testing, and contribution guidance.
  - Historical BRD, SRS, TDD, ADR, roadmap, migration evidence, superseded OpenClaw/Guinevere material, and completed step prompts may be retained under an explicitly non-canonical archive.
  - Archived documents must carry clear historical or superseded labeling and must not be linked as current operating instructions.
  - Generated SBOM, vulnerability-scan output, and test reports should be regenerated as CI artifacts rather than maintained as canonical source documents.
  - Contradictory duplicate changelogs, API specifications, and deployment runbooks must be consolidated rather than independently updated.

## DEC-027 — Launch all five MVP tools together

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The public relaunch will occur only when Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG are all production-ready in English and Spanish.
- **Rationale:** A complete five-tool catalog provides a coherent initial product, stronger internal linking and SEO coverage, and a consistent quality signal at relaunch.
- **Consequences:**
  - Individual tools may be exercised in internal or restricted testing, but none defines the full public relaunch independently.
  - Launch readiness requires complete processing behavior, localized UI and metadata, error states, analytics, privacy disclosure, executable tests, documentation, and operational support for every tool.
  - One incomplete or unreliable tool blocks the public MVP launch unless a later explicit scope decision removes it from the catalog.
  - Shared foundations should be validated early to reduce the risk of five independent late-stage integrations.

## DEC-028 — Evolve the legacy visual design rather than replacing it

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Use Papyr's existing visual identity and interface patterns as the baseline for the international rebuild rather than pursuing a total redesign.
- **Rationale:** The project owner wants the rebuilt product to remain visually recognizable as the current Papyr while improving execution quality.
- **Consequences:**
  - Existing color, typography, component character, page composition, and core interaction patterns should be audited and retained where they remain effective.
  - Changes should focus on consistency, responsive behavior, accessibility, localization resilience, interaction clarity, performance, and polished states rather than visual novelty.
  - Legacy defects, misleading behavior, dead links, inaccessible interactions, and layouts that fail with English or Spanish copy are not protected merely because they exist today.
  - Any substantial departure from the baseline requires an explicit design rationale and approval during the design review.

## DEC-029 — Auto-download successful results and retain a manual download control

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Start the result download automatically after successful processing and keep a visible manual Download button available until the result expires or the local session is cleared.
- **Rationale:** Automatic download minimizes task-completion time, while a persistent manual control provides recovery when browser policy, network behavior, or user action blocks or loses the first download.
- **Consequences:**
  - The completion state must remain understandable even when automatic download is blocked.
  - Repeated download attempts must not rerun processing unnecessarily.
  - Server result links remain bounded by the one-hour maximum retention policy; local results require timely object-URL cleanup.
  - Download names must be safe, localized where appropriate, and derived without sending original file names to analytics.

## DEC-030 — Automatically route unsupported browser jobs to the server

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Automatically fall back to temporary server processing when a file is corrupt, encrypted, unsupported, or unsafe for reliable browser processing.
- **Rationale:** Automatic routing protects the fast and simple task flow by avoiding a second confirmation step when local processing cannot complete reliably.
- **Consequences:**
  - Before processing begins, the interface must clearly disclose that Papyr may upload the file temporarily if local processing is unsuitable, satisfying the transparency requirement in DEC-011 and DEC-015.
  - The transition must be visible in status messaging and must not misleadingly claim that the file remained on-device.
  - Passwords may be requested only when required and must never enter logs, analytics, URLs, or persistent storage.
  - Server fallback remains subject to file limits, abuse controls, queue capacity, security validation, and the one-hour deletion maximum.
  - If server processing also cannot recover the file, Papyr must return a clear, actionable failure rather than an indefinite retry loop.

## DEC-031 — Support the latest two major versions of mainstream browsers

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Officially support the latest two major versions of Chrome, Edge, Firefox, and Safari on desktop, together with current Safari on iOS/iPadOS and Chrome on Android.
- **Rationale:** This provides broad international coverage while keeping browser-processing, accessibility, and regression testing manageable.
- **Consequences:**
  - Progressive enhancement and ordinary file-input/download fallbacks are required where Chromium-specific file APIs are unavailable.
  - The browser support matrix must be represented in automated tests where feasible and supplemented by representative real-device testing, especially on iOS.
  - Unsupported browsers should receive a clear compatibility message or server-processing path rather than silently failing.
  - Browser-version support advances over time; compatibility with older versions is best-effort unless a later decision expands the matrix.

## DEC-032 — Retain local results only for the active browser tab session

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Keep a locally generated result available for repeat download only while the current browser tab session remains active.
- **Rationale:** Session-scoped retention supports download recovery without introducing persistent browser storage or retaining documents across visits.
- **Consequences:**
  - Local results must not be written to IndexedDB, localStorage, caches, or other cross-session application storage.
  - Object URLs and associated buffers must be revoked and released when the tab unloads, the user clears the job, or a replacement job makes them unnecessary.
  - Reloading or reopening the page may require the user to process the source again.
  - Memory-pressure handling may release a result earlier, but the UI must explain when repeat download is no longer available.

## DEC-033 — Show real processing stages and honest estimates

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Present real lifecycle stages such as preparing, uploading, queued, processing, finalizing, and ready, together with an estimate only when supported by measured or engine-derived information. Do not display fabricated percentage progress.
- **Rationale:** Honest stage-based feedback preserves trust and remains useful when PDF engines cannot report granular progress.
- **Consequences:**
  - Browser and server jobs require a shared user-facing progress model even if their internal events differ.
  - Percentages may be shown only when grounded in measurable units such as bytes uploaded, pages processed, or explicit engine progress.
  - Queue position or wait estimates must be labeled as estimates and updated from real queue state.
  - Long-running, stalled, retrying, cancelled, and failed states require distinct messages and recovery actions.

## DEC-034 — Define server input limits separately for each tool

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Establish server-side input limits independently for Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG rather than applying one universal file-size and page-count ceiling.
- **Rationale:** Each operation has a different CPU, memory, disk, rendering, archive-output, and worst-case complexity profile, so a shared limit would either be unsafe for expensive tools or unnecessarily restrictive for simpler ones.
- **Consequences:**
  - Final limits must be based on representative VPS benchmarks, concurrency targets, timeouts, decoded image dimensions, output expansion, and queue behavior.
  - The UI and API must expose consistent per-tool limits before upload and return machine-readable validation failures.
  - Limits may combine total bytes, per-file bytes, file count, page count, pixel count, page geometry, estimated memory, and expected output size.
  - Conservative pre-benchmark defaults and the procedure for safely raising limits must be documented during technical design.

## DEC-035 — Keep valid server jobs queued during normal capacity pressure

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When all processing workers are busy, continue accepting and queuing valid server-side jobs rather than immediately rejecting ordinary users with a retry response.
- **Rationale:** The project owner prefers successful eventual processing over requiring users to resubmit whenever the VPS experiences temporary demand spikes.
- **Consequences:**
  - Users must receive real queued status and an honest wait estimate where sufficient data exists.
  - Queueing remains bounded by hard operational safety limits for queue length, storage, maximum wait, job expiry, and VPS health; this decision does not require accepting unlimited work until failure.
  - Jobs that exceed safety or abuse thresholds may still be rejected clearly before unnecessary upload or processing.
  - Fair scheduling, per-origin concurrency, stale-job expiry, cancellation, and cleanup are required to prevent starvation and unbounded backlog.
  - Queue wait time and saturation must be monitored as launch reliability indicators.

## DEC-036 — Request PDF passwords only when encryption is detected

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Detect password-protected PDFs and request a password only when required to perform the selected operation.
- **Rationale:** Conditional password entry avoids unnecessary friction for ordinary files while allowing supported encrypted documents to proceed.
- **Consequences:**
  - Passwords must be held only as briefly as required in process memory and must never be written to logs, analytics, URLs, queue dashboards, persistent task records, storage metadata, or backups.
  - API and worker boundaries must use secret-safe transport and redaction behavior.
  - Incorrect-password errors must be distinguishable from corrupt or unsupported PDFs without exposing sensitive engine details.
  - Password values must be cleared after success, failure, cancellation, or timeout to the extent supported by the runtime.

## DEC-037 — Provide multi-file results as both ZIP and individual downloads

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When one Split PDF or PDF to JPG job produces multiple files, auto-download a ZIP archive and also keep each generated file available for individual download while the result remains available.
- **Rationale:** A ZIP completes the task efficiently, while individual downloads let users retrieve or retry only the outputs they need.
- **Consequences:**
  - Multi-file jobs require deterministic, safe, ordered file names and a result manifest.
  - Creating the ZIP must not duplicate large buffers unnecessarily or violate browser/server memory and output-size limits.
  - Individual downloads must reuse existing results rather than rerun conversion.
  - Local result availability follows DEC-032; server result availability follows the one-hour maximum in DEC-013.

## DEC-038 — Support range-based and per-page Split PDF modes

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Split PDF will support custom page ranges and a mode that produces one PDF for every page.
- **Rationale:** These two modes cover the common need to extract selected sections and the common need to separate an entire document without exposing unnecessary advanced controls.
- **Consequences:**
  - Range input must support clear syntax, validation, overlap handling, ordering, and actionable errors.
  - The interface should preview or summarize the exact outputs before processing.
  - Per-page mode is subject to output-count, archive-size, memory, and device/server safety limits.
  - Output names and ordering must remain deterministic in both ZIP and individual-download views.

## DEC-039 — Use automatic high-quality PDF-to-JPG output

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** PDF to JPG will use one automatic high-quality output profile in the MVP rather than exposing Standard, High, Maximum, DPI, or JPEG-quality controls.
- **Rationale:** A strong automatic default supports Papyr's speed, simplicity, and high-end quality goals without requiring general users to understand rendering parameters.
- **Consequences:**
  - Rendering resolution, JPEG quality, color handling, and downscaling thresholds must be established through visual-quality, file-size, memory, and performance benchmarks.
  - Text and line art should remain crisp for normal high-quality screen use within the established 16-megapixel per-page safety ceiling for browser processing.
  - Jobs that cannot safely meet the profile locally must route to server processing according to DEC-030.
  - If source pages are already low resolution, the UI must not imply that conversion can create missing detail.

## DEC-040 — Keep Merge PDF controls at the file level

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Merge PDF will let users reorder uploaded PDFs with drag-and-drop and remove unwanted files before processing, without adding a cross-document page-level editor in the MVP.
- **Rationale:** File-level ordering covers the core merge task with substantially less cognitive load, rendering work, memory pressure, and implementation complexity than page-level composition.
- **Consequences:**
  - The interface must make file order, page counts, removal, and validation clear before merging.
  - Keyboard-accessible alternatives are required for drag-and-drop reordering.
  - Page-level rearrangement or removal across input documents is deferred and must not be implied by launch copy.
  - Processing preserves page order within each source document.

## DEC-041 — Automatically fit each image to an appropriate PDF page

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** JPG to PDF will automatically choose an appropriate standard page orientation and fit each image with safe margins, without exposing A4, Letter, orientation, DPI, or margin controls in the MVP.
- **Rationale:** Automatic fitting keeps the conversion immediate for general users and avoids confusing physical-unit and print-layout decisions.
- **Consequences:**
  - The fitting algorithm must preserve aspect ratio, avoid cropping, respect EXIF orientation, and use deterministic page-size and margin rules.
  - Portrait and landscape images may produce correspondingly oriented pages within the same PDF.
  - The selected standard-size policy must be tested for both US and international expectations and documented in the technical specification.
  - Image order remains user-adjustable before conversion, consistent with the simple task flow.

## DEC-042 — Derive output names from source names with safe localized suffixes

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Generate output names from the relevant source name plus a safe, understandable suffix appropriate to the operation and locale.
- **Rationale:** Source-derived names make downloaded results easier to identify than generic Papyr filenames without adding a naming step to the workflow.
- **Consequences:**
  - Names must be sanitized for filesystem and archive safety, bounded in length, and robust across Unicode and duplicate inputs.
  - Multi-input operations require a deterministic naming rule that does not expose unrelated local paths or metadata.
  - Localized suffixes must remain understandable and stable enough for repeated downloads and support workflows.
  - Original and generated file names must not be sent to analytics, monitoring, logs, or error reporting.

## DEC-043 — Preserve the legacy directory-style homepage structure

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Keep the existing Papyr homepage concept as the baseline: a concise hero, immediately visible tool directory, trust and privacy cues, simple process explanation, and supporting FAQ rather than a universal uploader or account dashboard.
- **Rationale:** The project owner explicitly requested the existing homepage approach, consistent with the broader decision to evolve rather than redesign Papyr.
- **Consequences:**
  - The homepage catalog must be reduced and rewritten around the five launch tools and international English/Spanish positioning.
  - Tool access and task intent take priority over corporate storytelling or a long marketing preamble.
  - Legacy sections may be corrected, reordered, localized, or removed when stale, inaccessible, misleading, or no longer relevant.
  - Homepage advertising must obey the non-intrusive placement and performance requirements in DEC-018.

## DEC-044 — Combine concise tool-page SEO content with a supporting blog

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Each tool page will contain concise but complete intent-aligned content, while a separate English and Spanish blog supports broader informational search demand.
- **Rationale:** Tool pages should answer transactional intent without burying the utility, while articles can address tutorials, comparisons, troubleshooting, and document-workflow questions in appropriate depth.
- **Consequences:**
  - Tool pages should place the working tool first, followed by useful instructions, benefits, privacy and processing disclosure, use cases, FAQs, and related tools.
  - Blog content must be genuinely useful, localized intentionally, internally linked, and distinct from tool-page copy rather than mass-produced keyword filler.
  - Blog architecture requires locale-aware URLs, metadata, canonicals, hreflang, sitemap inclusion, author/editorial policy, and freshness ownership.
  - Article production volume and publishing cadence remain to be defined; the blog must not block engineering of the five production-ready tools unless required launch content is explicitly scoped.

## DEC-045 — Publish Privacy, Terms, and Cookies/Advertising pages at launch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Launch with separate Privacy Policy, Terms of Use, and Cookies/Advertising disclosure pages in English and Spanish.
- **Rationale:** Papyr temporarily processes documents, uses analytics and third-party advertising, serves multiple jurisdictions, and therefore needs clear user-facing disclosures beyond a minimal footer statement.
- **Consequences:**
  - The documents must accurately describe local versus server processing, one-hour maximum server retention, R2, infrastructure providers, analytics boundaries, advertising behavior, user controls, and contact channels.
  - English and Spanish versions require controlled translation and synchronized updates; they must not contradict product behavior.
  - Legal copy must disclose the accepted consent risk in practice without falsely claiming compliance.
  - These documents require qualified legal review before public launch and must expose effective dates and version history.

## DEC-046 — Provide support through email and a contact form

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Offer both a public support email address and a simple categorized contact form at launch, without requiring an account or adding live chat.
- **Rationale:** Email and a structured form provide accessible support and actionable issue reports while keeping operational overhead appropriate for the MVP.
- **Consequences:**
  - The contact form must minimize personal-data collection, include anti-spam and abuse protection, and never request document uploads, document contents, or PDF passwords.
  - Users need clear categories for processing failure, billing/advertising concern, privacy/data request, accessibility, security, and general feedback.
  - Form submissions require delivery monitoring, retention rules, redaction-safe error handling, and an expected response statement.
  - English and Spanish support entry points may share an operational queue, but automated confirmations and form copy must match the user's locale.

## DEC-047 — Detect browser language for locale-less entry and remember manual choice

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When a user enters without a locale prefix, redirect once according to supported browser-language preferences, while providing a persistent manual language switcher whose explicit selection takes precedence.
- **Rationale:** Automatic detection improves the first visit for Spanish-speaking users without forcing a language-selection screen or permanently overriding user intent.
- **Consequences:**
  - Explicit user choice must override browser detection and be remembered with minimal non-sensitive storage.
  - Unsupported languages fall back to English until additional locales are launched.
  - Search crawlers, shared URLs, locale-prefixed routes, and canonical/hreflang behavior must not be redirected unpredictably.
  - Redirect status, caching, and middleware behavior require SEO testing to avoid loops, duplicate indexing, or incorrect geo-language assumptions.

## DEC-048 — Fully automate LLM-assisted blog generation and publishing

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Use an LLM-driven workflow to research, generate, localize, validate, schedule, and publish blog articles automatically without requiring human approval for every article.
- **Rationale:** The project owner explicitly selected full automatic publishing to operate the multilingual content program with minimal manual publishing work.
- **Consequences:**
  - Automatic publishing requires blocking quality gates for factual support, duplication and cannibalization, search intent, originality, language quality, metadata, internal links, unsafe claims, policy violations, and malformed MDX.
  - The system must fail closed: content that does not pass every required gate remains unpublished.
  - Publication must support rate limits, scheduling, audit logs, pause controls, rollback, correction, removal, and periodic human quality audits.
  - English and Spanish articles must be intentionally localized; literal machine translation is not sufficient.
  - The workflow must not fabricate expertise, authors, test results, citations, product capabilities, legal advice, or performance claims.
  - Exact model, research sources, editorial templates, cadence, and launch inventory remain separate decisions.

## DEC-049 — Store blog content as version-controlled MDX in the repository

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Store published and pending blog content as MDX within the Papyr repository rather than introducing a headless CMS or building a custom database editor.
- **Rationale:** Repository-managed MDX keeps content versioned, reviewable, portable, and integrated with the Next.js build while avoiding another production service.
- **Consequences:**
  - The publishing automation must create validated repository changes and trigger the normal preview/build/deployment path rather than writing directly into a production filesystem.
  - MDX parsing, frontmatter, component allowlisting, locale pairing, schema validation, and build safety require strict controls because generated content is executable build input.
  - Failed content builds must not affect the currently deployed site.
  - Content history, rollback, scheduling metadata, and publication state must remain auditable through Git and workflow records.

## DEC-050 — Make the project owner responsible for launch support

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Route launch support email and contact-form submissions to one inbox managed directly by the project owner.
- **Rationale:** Owner-operated support is sufficient for MVP volume and provides direct visibility into user problems without introducing an AI support agent or external helpdesk.
- **Consequences:**
  - The runbook must define inbox routing, priority categories, reusable response templates, escalation for privacy/security reports, spam handling, and continuity if the owner is unavailable.
  - The public site must avoid promising response times that cannot be sustained.
  - Support analytics may use aggregate categories and resolution timing but must not copy private message contents into general product analytics.

## DEC-051 — Use the owner's custom `gpt5.6-sol` provider for blog automation

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Use the project owner's custom LLM provider and the model identifier `gpt5.6-sol` for the automated blog workflow.
- **Rationale:** The project owner explicitly selected this existing custom provider/model rather than a standard Gemini, OpenAI, or lowest-cost routing strategy.
- **Consequences:**
  - The model identifier is recorded exactly as supplied and does not imply a specific vendor, public model family, API protocol, endpoint, or capability.
  - Authentication, base URL, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, and availability must be documented before technical design is finalized.
  - Provider integration must be isolated behind an interface so publishing can be paused or migrated if the custom service is unavailable or fails quality requirements.
  - Secrets must be managed outside the repository and must never appear in generated MDX, logs, workflow artifacts, or client-side code.

## DEC-052 — Launch the blog with five topics localized into two languages

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Public launch will include five priority blog topics, each published as an intentionally localized English and Spanish article, for ten initial article pages.
- **Rationale:** One strong topic associated with each launch tool provides initial informational coverage without delaying the complete five-tool release for a large content inventory.
- **Consequences:**
  - Topic selection must avoid duplicating or cannibalizing the transactional intent of the five tool pages.
  - Both locale versions require the same blocking quality, factual, metadata, link, and MDX validation gates.
  - The ten article pages form part of launch content acceptance, while their indexing or ranking is not a launch prerequisite.

## DEC-053 — Publish one new localized blog topic per day after launch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** After launch, automatically publish one new topic per day with corresponding English and Spanish localized articles.
- **Rationale:** The project owner selected an aggressive daily publishing cadence to grow Papyr's informational search footprint.
- **Consequences:**
  - The system may publish at most one approved topic pair per day and must skip publication rather than weaken blocking quality gates.
  - Topic inventory, duplication, cannibalization, indexing quality, crawl behavior, factual corrections, and organic performance require continuous monitoring.
  - A kill switch and automatic pause thresholds are required for build failures, quality regressions, policy issues, provider anomalies, or widespread indexing problems.
  - Daily cadence must not be misrepresented as a guarantee when no qualified topic passes validation.

## DEC-054 — Require deep research before approving every new feature

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Every new Papyr feature and material capability change must undergo deep, evidence-based research before its design or implementation is approved.
- **Rationale:** The project owner explicitly requires decisions to be grounded in thorough investigation rather than assumptions, shallow comparisons, copied legacy behavior, or unverified LLM output.
- **Consequences:**
  - Research applies to user-facing features, PDF processing behavior, infrastructure, third-party services, analytics, advertising, localization, SEO automation, security, privacy, and operational tooling.
  - Each research package must define the user problem, current Papyr behavior, relevant legacy evidence, external authoritative sources, feasible alternatives, trade-offs, risks, cost and operational impact, security/privacy implications, and measurable acceptance criteria.
  - Library, framework, API, model, and provider decisions require current official documentation and representative implementation or benchmark evidence where applicable.
  - Performance- or quality-sensitive processing decisions require reproducible benchmarks with representative documents and target devices or VPS capacity.
  - Research findings are recommendations, not accepted product decisions; implementation remains blocked until the owner explicitly approves the resulting design.
  - Material assumptions, source dates, unresolved uncertainties, and accepted risks must be recorded in canonical documentation.

## DEC-055 — Require a structured research brief for each new feature

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Before a new feature may enter design, produce a dedicated structured research brief covering the problem, evidence, alternatives, trade-offs, risks, recommendation, and measurable acceptance criteria.
- **Rationale:** A consistent artifact makes research reviewable, comparable, and reusable during design, implementation, testing, and later maintenance.
- **Consequences:**
  - Each brief must identify scope, non-goals, assumptions, unresolved questions, dependencies, cost, operational impact, privacy/security implications, and source dates.
  - At least two viable approaches should be compared unless evidence demonstrates that only one is feasible.
  - Prototype, benchmark, compatibility matrix, legal review, or threat analysis may be required when the feature's risk demands it, even though the brief is the universal minimum artifact.
  - Research briefs become canonical design inputs and must link to resulting decisions and acceptance tests.

## DEC-056 — Prioritize primary sources and verify decisions in practice

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Base technical and provider research primarily on current official documentation, standards, source code, licenses, security advisories, and contractual or legal terms, then verify material claims through representative benchmarks, prototypes, or real implementations where applicable.
- **Rationale:** Official claims alone may omit practical limitations, while community material alone may be stale or unreliable; combining primary evidence with reproducible validation produces stronger decisions.
- **Consequences:**
  - Secondary sources may support discovery but cannot be the sole basis for material architecture, security, privacy, licensing, or provider decisions.
  - Research must record source URLs or identifiers, publication or access dates, versions, benchmark environment, test corpus, and known limitations.
  - Conflicting evidence must be surfaced rather than resolved through unsupported assumptions.
  - External library and service behavior must be rechecked when versions or provider terms materially change.

## DEC-057 — Require owner approval for every researched feature

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** A feature may proceed from research into approved design and implementation planning only after the project owner explicitly approves it.
- **Rationale:** Quality gates and recommendations inform product decisions but do not replace owner control over scope, cost, risk, or product direction.
- **Consequences:**
  - Passing automated or research gates does not automatically authorize implementation.
  - Approval must identify the selected approach, accepted risks, scope boundaries, and material conditions.
  - Rejected or deferred features remain documented with their evidence and status rather than silently disappearing.
  - Material design changes after approval require renewed owner confirmation.

## DEC-058 — Run MVP research in parallel domain tracks

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** After product discovery, conduct deep research concurrently across PDF processing, platform and infrastructure, frontend and SEO, privacy and advertising, and operations rather than completing these domains sequentially.
- **Rationale:** The domains have substantial independent research work, while their findings can later be reconciled into one architecture and product design.
- **Consequences:**
  - Each track requires a bounded scope, named deliverables, dependencies, evidence standards, and a synthesis checkpoint.
  - Parallel work must not produce conflicting implicit decisions; cross-domain assumptions and interfaces must be surfaced explicitly.
  - Architecture design remains blocked until required track findings are collected and reconciled.
  - Research duplication should be avoided by maintaining a shared source and decision index.

## DEC-059 — Re-research all five legacy tools from first principles

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Research Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG fully from first principles even though legacy implementations exist.
- **Rationale:** Legacy code is useful evidence but does not prove that its engines, UX, limits, security, quality, licensing, compatibility, or processing boundaries remain optimal for the international rebuild.
- **Consequences:**
  - Existing behavior is reference material, not an automatically accepted requirement.
  - Each tool requires its own research brief, alternatives, representative corpus, quality and performance benchmarks, failure analysis, browser/device validation, and server-capacity implications.
  - Shared engine and interface decisions may be researched jointly, but each tool must retain independently measurable acceptance criteria.
  - Reuse of legacy code or dependencies requires positive evidence rather than convenience alone.

## DEC-060 — Block rebuild coding until MVP research and design are approved

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Do not begin product-code implementation or scaffolding for the rebuild until all required MVP research briefs are complete, their cross-domain findings are reconciled, the resulting design is approved, and an implementation plan has been reviewed.
- **Rationale:** The project owner wants architecture and feature choices established through deep research before code creates momentum, lock-in, or rework.
- **Consequences:**
  - Discovery documents, research artifacts, benchmarks, and design work may proceed; application scaffolding, feature code, production infrastructure changes, and deployment changes may not.
  - The legacy repository remains read-only reference during this gate unless the owner explicitly authorizes a separate preservation or security action.
  - Coding begins only after explicit approval of the written design and implementation plan.
  - New material uncertainties discovered during implementation may pause affected work and return it to research/design review.

## DEC-061 — Use a curated mixed corpus for five-tool benchmarking

- **Date:** 2026-07-31
- **Status:** Superseded by DEC-066
- **Decision:** This proposed benchmarking program was initially accepted during questioning but was later rejected by the project owner.
- **Rationale:** The assistant introduced benchmarking without an owner request and incorrectly allowed it to become a presumed requirement.
- **Consequences:**
  - No benchmark corpus or benchmark-report obligation follows from this decision.
  - This entry remains only to preserve an accurate decision history; DEC-066 governs.

## DEC-062 — Target WCAG 2.2 Level AA across the public product

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Treat WCAG 2.2 Level AA as an acceptance target for product pages, all five tools, blog, legal pages, and contact/support interfaces.
- **Rationale:** Papyr serves broad task-oriented audiences across desktop and mobile, and accessibility must be designed into upload, ordering, progress, error, result, and download interactions rather than added later.
- **Consequences:**
  - Acceptance coverage includes keyboard operation, visible focus, contrast, semantic structure, accessible names and errors, status/progress announcements, non-drag alternatives, zoom/reflow, target sizing, reduced-motion behavior, and localized content resilience.
  - Automated checks are necessary but insufficient; representative manual keyboard and assistive-technology testing is required.
  - Known exceptions must be documented with impact and remediation rather than silently treated as compliant.
  - Public wording must not claim certification or universal conformance unless independently substantiated.

## DEC-063 — Do not benchmark on VPS `<vps-ip>`

- **Date:** 2026-07-31
- **Status:** Superseded and broadened by DEC-066
- **Decision:** Do not use VPS host `<vps-ip>` for research benchmarking.
- **Rationale:** Research is separate from deployment, and the project owner subsequently clarified that no benchmark program was requested anywhere.
- **Consequences:**
  - No account, SSH, sudo, firewall, package, daemon, container, secret, benchmark workload, or production configuration change on this VPS is authorized during research.
  - The earlier request to create a new `nopasswd` user belongs to a future deployment stage; its exact SSH and sudo policy remains unresolved.
  - DEC-066 removes benchmarking generally, not only on this host.

## DEC-064 — Support password-protected PDF input across applicable MVP tools

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Compress PDF, Merge PDF, Split PDF, and PDF to JPG must detect encrypted input and request a password only when needed, then process the document when the supplied credentials and document permissions permit it; JPG to PDF is unaffected because its inputs are images.
- **Rationale:** Users should not need a separate unlock product before using the applicable launch tools.
- **Consequences:**
  - Wrong, missing, unsupported, and permission-restricted credentials require clear localized errors without revealing sensitive details.
  - Multi-file Merge must identify which source requires authentication and must not confuse credentials between files.
  - Password handling remains governed by DEC-036: memory-only, shortest practical lifetime, and exclusion from logs, analytics, URLs, dashboards, persistent queues, storage, backups, and error payloads.
  - Engine and library research must verify encryption compatibility and licensing rather than assuming all PDF security handlers are supported.

## DEC-065 — Automatically fall back to server processing after safe browser failure

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When browser processing fails and the job is safe and supported on the server, automatically transition the same job to temporary server processing without a second confirmation prompt.
- **Rationale:** The project owner prioritizes completion speed and a low-friction recovery path, relying on the pre-processing disclosure that server fallback may occur.
- **Consequences:**
  - Before processing starts, the interface must clearly disclose that the file may be uploaded automatically if local processing cannot complete; the local/server state and transition reason must remain visible.
  - Automatic fallback is allowed only for classified recoverable failures and must not create retry loops, duplicate jobs, duplicate downloads, or repeated uploads.
  - Security-policy failures, unsupported content, invalid passwords, user cancellation, retention violations, and unsafe conditions must fail closed rather than forcing a server upload.
  - The server copy and result remain subject to the one-hour maximum retention and sensitive-data restrictions.

## DEC-066 — Do not create or require a benchmark program for the rebuild

- **Date:** 2026-07-31
- **Status:** Accepted; supersedes benchmark requirements introduced in DEC-014, DEC-034, DEC-039, DEC-054 through DEC-056, DEC-059 through DEC-061, and DEC-063 where they conflict
- **Decision:** The Papyr rebuild will not include a formal or informal benchmark program for the five tools, their engines, browser processing, VPS capacity, quality, performance, memory use, or comparative alternatives.
- **Rationale:** The project owner did not request benchmarking; the assistant introduced it as a recommendation and incorrectly escalated it into a requirement.
- **Consequences:**
  - Do not create benchmark corpora, benchmark matrices, comparative performance studies, quality-score programs, VPS benchmark workloads, or benchmark reports.
  - Deep research remains required, but it must use relevant authoritative evidence without inventing a benchmark workstream.
  - Normal implementation verification remains required later: functional tests, integration tests, security checks, accessibility checks, and production observability verify that the selected implementation behaves as specified; they are not comparative benchmarks.
  - Tool limits and defaults must be conservative, documented as design choices or operational safeguards, and adjusted from real production observations rather than represented as benchmark-proven.
  - Public copy must not make unsubstantiated superlative or quantified performance/quality claims.
  - Existing references to benchmarking elsewhere in this log are historical context and are overridden by this decision wherever inconsistent.

## DEC-067 — Enforce server-result expiry after one hour even while the tab remains open

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Server-side source, intermediate, and result files expire no later than one hour after the applicable retention clock starts, even if the user's browser tab remains active and the result has not been downloaded.
- **Rationale:** The one-hour privacy limit is a hard maximum rather than an inactivity timer.
- **Consequences:**
  - The result UI must show an accurate expiry time or countdown and warn the user before deletion.
  - An expired result cannot be restored from server storage; the user must run a new job.
  - Active polling, page focus, retries, or an open tab must not extend retention.
  - Cleanup behavior must remain consistent with DEC-013 and be verified through normal functional and integration tests.

## DEC-068 — Keep the manual Download button as the auto-download fallback

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Attempt automatic download when a result becomes ready, while always retaining a visible manual Download button as the fallback when the browser blocks or misses the automatic download.
- **Rationale:** Browser download policy varies, and a ready result must remain recoverable without rerunning the job.
- **Consequences:**
  - A blocked automatic download must leave the job in the Ready state, not mark processing as failed.
  - The fallback button must use the already generated result and must not upload, process, or generate the file again.
  - The interface should make the fallback action obvious and communicate the remaining expiry window.
  - This decision refines DEC-029 without changing the one-hour server-retention limit.

## DEC-069 — Allow server-job cancellation only while queued

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Users may cancel a valid server job while it remains queued; once a worker has started processing, user-initiated cancellation is no longer offered.
- **Rationale:** Queue cancellation avoids unnecessary work without requiring unreliable or engine-specific interruption of an active PDF process.
- **Consequences:**
  - Queue cancellation must atomically prevent worker pickup, mark the terminal state clearly, and schedule prompt cleanup of associated temporary data.
  - Race conditions between cancellation and worker acquisition require an explicit state transition; if processing already started, the UI must report that cancellation is no longer available.
  - Closing the tab after processing starts does not cancel the job.
  - Operational timeouts, worker failures, or safety shutdowns remain system-controlled and are distinct from user cancellation.

## DEC-070 — Start the one-hour server-retention clock when upload is received

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Start the maximum one-hour retention period when the backend first accepts the uploaded file, not when processing begins or completes.
- **Rationale:** This creates a clear privacy ceiling for all server-side copies regardless of queue or processing duration.
- **Consequences:**
  - Source, intermediate, and result files must all be deleted by the same absolute deadline unless they were safely deleted earlier.
  - Queue admission and processing timeout rules must leave a practical download window; jobs that cannot reasonably finish before expiry must not be admitted or must fail clearly.
  - The API must expose the authoritative expiry timestamp so UI countdowns do not depend on client clock assumptions.
  - Retries and status polling must not reset or extend the deadline.

## DEC-071 — Continue accepted server jobs after the browser tab closes

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** A queued or processing server job continues after its originating browser tab closes, subject to normal queue, timeout, failure, and one-hour expiry rules.
- **Rationale:** Browser lifecycle events are unreliable, and already accepted work should not be lost merely because the user navigates away or closes the tab.
- **Consequences:**
  - Tab closure is not a cancellation signal.
  - Workers and cleanup must operate independently of an active client connection.
  - If the user no longer holds valid session access, the job may finish and expire without being downloaded.
  - This does not create cross-session history or an account-based recovery system.

## DEC-072 — Recover active server jobs after refresh only within the same tab session

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Store the minimum opaque task-access state in `sessionStorage` so refreshing the same tab can resume status polling and result access while the job remains valid; closing the tab ends client-side recovery.
- **Rationale:** Same-tab refresh recovery prevents accidental loss without introducing accounts, durable browser history, or shareable bearer links.
- **Consequences:**
  - Store only opaque task identifiers or capability tokens and minimal expiry/routing metadata; never store filenames, passwords, document contents, previews, signed result URLs, or analytics payloads.
  - Tokens require sufficient entropy, narrow job scope, expiry enforcement, and protection against unauthorized status, cancellation, or download access.
  - Successful expiry, cancellation, clear/reset, or invalidation must remove the corresponding session state.
  - `sessionStorage` is a narrowly approved exception for active server-job recovery and does not override DEC-032's prohibition on persistent cross-session document storage.

## DEC-073 — Do not implement deadline-prediction admission control

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Do not build a feature that predicts whether an uploaded job will finish before its one-hour retention deadline and admits or rejects the upload based on that estimate.
- **Rationale:** The project owner explicitly skipped this feature rather than adding queue-time prediction complexity.
- **Consequences:**
  - Papyr must not present speculative completion guarantees derived from a deadline predictor.
  - Accepted jobs remain subject to queue behavior, system timeout, failure handling, and the absolute one-hour expiry; a job may fail if it cannot complete in time.
  - This does not remove hard queue, storage, maximum-wait, health, abuse, or resource-safety controls required by DEC-035.
  - Any future deadline prediction is a new feature subject to the research and approval gates.

## DEC-074 — Collect a separate password for each locked Merge input

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When Merge PDF detects multiple encrypted inputs, identify each locked source and request and validate its password independently.
- **Rationale:** Source PDFs may use different credentials, and a single shared-password assumption would reject valid merge jobs or confuse users.
- **Consequences:**
  - The UI must associate each credential field with the correct local file without exposing the password or sending filenames to analytics.
  - Credentials must never be reused across files unless the user enters them and must follow the memory-only handling rules in DEC-036 and DEC-064.
  - The merge job may proceed only after all required sources are successfully authenticated and supported.
  - Validation errors must identify the affected source safely without echoing credential material.

## DEC-075 — Retain downloaded server results until their normal expiry

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** A successful download does not trigger early deletion; source, intermediate, and result objects remain governed by the existing absolute one-hour expiry from upload receipt.
- **Rationale:** Keeping the ready result until expiry preserves the manual Download fallback and permits re-download without rerunning processing.
- **Consequences:**
  - Download count or confirmation must not extend the expiry deadline.
  - The manual button may retrieve the same generated result repeatedly while authorization and retention remain valid.
  - Automatic cleanup still deletes all server-side copies at or before the fixed deadline.
  - The UI must continue to show the remaining availability window after a successful download.

## DEC-076 — Fail the complete Merge job when any source is invalid

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Merge PDF must not generate a partial output when any selected source cannot be opened, authenticated, validated, or processed; the entire job is blocked or fails.
- **Rationale:** Silent omission could produce a plausible but incomplete document and violate the user's intended composition.
- **Consequences:**
  - The interface must identify the affected source safely and let the user correct credentials, replace it, or remove it before retrying.
  - No output may be presented as successful unless every selected source is included in the intended order.
  - Other valid sources should not require re-selection within the active tab when the UI can retain them safely in memory.
  - Analytics may record a sanitized failure category but never the filename or document content.

## DEC-077 — Allow overlapping Split ranges as independent outputs

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Split PDF custom ranges may overlap; each entered range creates an independent output, so a page included in multiple ranges appears in each corresponding document.
- **Rationale:** Overlap can be intentional, and merging or rejecting ranges would unnecessarily constrain a valid use case.
- **Consequences:**
  - Validation and preview must make duplicated page membership visible before processing.
  - The system must not silently merge, deduplicate, or rewrite user-entered ranges.
  - Output names and the ZIP manifest must distinguish overlapping ranges deterministically.
  - Repeated identical ranges are permitted only if the design can label them unambiguously; otherwise that narrower case requires an explicit validation rule.

## DEC-078 — Preserve user-entered order for Split outputs

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Split PDF outputs, ZIP ordering, individual-download listing, naming sequence, and manifest entries follow the order in which the user entered the custom ranges rather than numeric page order.
- **Rationale:** Input order is an explicit part of the user's requested output sequence.
- **Consequences:**
  - A request such as `8-10,1-2` produces the `8-10` result first and the `1-2` result second.
  - The UI must preview the effective sequence before processing.
  - Sorting for display, archive generation, or filenames must not change semantic output order.
  - Per-page mode continues in natural page order unless the user-facing design later provides explicit reordering.

## DEC-079 — Preserve Merge document features as safely as supported

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Merge PDF should preserve bookmarks, form fields, annotations, links, metadata, page geometry, and other supported document features to the greatest extent the selected engine can do safely.
- **Rationale:** A visually correct merge can still damage useful document behavior if interactive or structural features are discarded unnecessarily.
- **Consequences:**
  - Research must document actual engine support and deterministic handling of conflicts such as duplicate form names, destinations, outlines, metadata, and object references without introducing a benchmark program.
  - Unsupported or transformed features require truthful user-facing limitations; Papyr must not promise lossless preservation universally.
  - Security-relevant actions, embedded content, and unsupported interactive behavior must not be preserved blindly when doing so creates risk.
  - Functional fixtures must verify the preservation behavior selected in the approved design.

## DEC-080 — Always generate a new Compress output artifact

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-014
- **Decision:** Compress PDF must produce a newly processed output artifact even when the source was already optimized, the size reduction is negligible, or the output is not smaller.
- **Rationale:** The project owner prefers consistent generation and delivery of a processed result rather than returning the original source unchanged.
- **Consequences:**
  - The result UI must report the actual input size, output size, and real change honestly, including zero savings or a larger output.
  - Papyr must not fabricate a compression percentage, claim success as size reduction when none occurred, or silently substitute the original file.
  - The premium-screen-quality and legibility requirements remain; generating a new artifact does not authorize avoidable quality damage.
  - The output filename must follow the safe localized naming policy in DEC-042.

## DEC-081 — Composite transparent PDF pages onto white for JPG output

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** PDF to JPG must render page transparency against a white background before JPEG encoding.
- **Rationale:** JPEG has no alpha channel, and white is the conventional document-page background that best preserves expected appearance.
- **Consequences:**
  - Transparent and partially transparent content must be composited deterministically rather than defaulting to black or undefined engine behavior.
  - Color and appearance limitations must be documented where blending or transparency groups cannot be reproduced exactly.
  - The same rule applies consistently to browser and server processing paths.
  - Functional visual fixtures must verify that transparent regions do not become black or otherwise unexpected.

## DEC-082 — Select JPG-to-PDF page size and orientation per image

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** For a mixed image set, JPG to PDF automatically selects an appropriate standard page size and portrait or landscape orientation independently for each image.
- **Rationale:** Per-image fitting avoids forcing diverse photos into a layout derived from the first image or a single global orientation.
- **Consequences:**
  - One output PDF may contain mixed page orientations and, where the locale-aware policy requires it, independently selected standard page geometry.
  - Each image must preserve its aspect ratio and EXIF orientation while fitting within safe margins without cropping.
  - Ordering remains the user's selected image order.
  - The interface should summarize the automatic policy without adding manual paper or margin controls prohibited by DEC-041.

## DEC-083 — Choose JPG-to-PDF paper standards from locale

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** JPG to PDF automatically uses Letter-family page geometry for US and Canada locale contexts and A4-family geometry for other launch markets, with per-image portrait or landscape orientation.
- **Rationale:** Locale-aware defaults fit common regional document expectations while preserving the no-settings simplicity of the tool.
- **Consequences:**
  - The applicable locale must be derived deterministically from the active Papyr locale and an explicitly documented regional rule; browser geolocation permission is not required.
  - Because English spans both US and non-US markets and Spanish spans multiple regions, research/design must define a non-invasive fallback that does not pretend language alone always identifies paper preference.
  - The selected standard must be visible before processing, even though the MVP offers no manual control.
  - Mixed orientation is allowed; arbitrary image-sized pages are not the default policy.

## DEC-084 — Preserve source metadata including location metadata where supported

- **Date:** 2026-07-31
- **Status:** Accepted risk
- **Decision:** Preserve PDF metadata and image metadata, including EXIF GPS, timestamps, device/software information, author, creator, and title, to the greatest extent supported by the selected transformations and output formats.
- **Rationale:** After explicit warning that metadata can reveal location and identity, the project owner selected maximum metadata preservation.
- **Consequences:**
  - This is an accepted privacy risk and weakens any broad claim that generated files remove sensitive metadata.
  - Before JPG to PDF or other relevant processing, the interface and privacy documentation must disclose that source metadata may remain in the result.
  - Papyr must not send metadata fields to analytics or general logs merely because they are preserved in the user-owned output.
  - Format conversion may inherently discard unsupported metadata; preservation is best effort, not a promise of byte-for-byte fidelity.
  - A future metadata-removal option is a separate feature requiring research and explicit approval.

## DEC-085 — Use coarse edge country codes for automatic paper selection

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Use the coarse country code supplied by the trusted Vercel or Cloudflare request edge to select Letter for US and Canada and A4 for other countries, without requesting precise browser geolocation.
- **Rationale:** Edge-derived country context is more accurate than language alone and avoids prompting for precise location access.
- **Consequences:**
  - The code must define trusted headers, behavior when headers are absent or spoofable outside the trusted edge, and a deterministic A4 fallback.
  - Country code use must be ephemeral for page-policy selection and must not become a persistent location profile under this decision.
  - Privacy and analytics documentation must accurately disclose any broader country-level processing already performed by hosting or analytics providers.
  - The selected paper standard must be visible before conversion.

## DEC-086 — Preserve active PDF content where supported

- **Date:** 2026-07-31
- **Status:** Superseded by DEC-090
- **Decision:** The earlier choice to preserve active PDF content was reversed after clarifying its malware and exploit implications.
- **Rationale:** The project owner subsequently selected sanitization of active content.
- **Consequences:**
  - This entry remains only as decision history; DEC-090 governs output behavior.

## DEC-087 — Require explicit confirmation before processing detected active PDF content

- **Date:** 2026-07-31
- **Status:** Superseded by DEC-090
- **Decision:** The earlier confirmation-before-preservation flow is no longer required because detected active content will be sanitized rather than intentionally preserved.
- **Rationale:** Confirmation does not add value when the approved output policy removes the risky active elements.
- **Consequences:**
  - This entry remains only as decision history; DEC-090 and DEC-091 govern sanitization and user communication.

## DEC-088 — Block files classified as threats to Papyr infrastructure

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** If security controls classify a file or its behavior as a threat to Papyr infrastructure, block the job instead of processing it for fidelity, sanitizing it, or returning an output.
- **Rationale:** User confirmation cannot authorize infrastructure compromise, malware execution, resource abuse, or unsafe payload handling.
- **Consequences:**
  - The file must not reach document engines beyond the minimum safely isolated inspection needed for classification.
  - Cleanup must run promptly within the absolute retention ceiling, and the user receives a safe localized rejection without exploit details that would aid evasion.
  - Logs and security telemetry may retain minimal non-content indicators needed for defense under a separately documented retention policy, but must not retain the document, password, filename, signed URL, or sensitive payload.
  - False-positive handling and support escalation must not require users to email or upload the rejected document through the contact form.

## DEC-089 — Fall back to A4 when the edge country is unavailable

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** If no trusted edge country code is available for JPG to PDF paper selection, use A4 as the deterministic default.
- **Rationale:** A4 is the most broadly used international paper standard and avoids introducing a manual setting solely for ambiguous region detection.
- **Consequences:**
  - US and Canada use Letter only when the trusted country signal is available; missing, invalid, or untrusted signals fall back to A4.
  - The selected standard remains visible before conversion.
  - No precise geolocation request or persistent country profile is introduced.
  - This decision completes the fallback rule required by DEC-083 and DEC-085.

## DEC-090 — Sanitize detected active content from processed PDF outputs

- **Date:** 2026-07-31
- **Status:** Accepted; supersedes DEC-086 and DEC-087
- **Decision:** Merge PDF, Split PDF, and Compress PDF must remove or safely neutralize detected JavaScript, launch actions, embedded attachments, and other active PDF features from generated outputs rather than preserving them or asking the user to accept their risk.
- **Rationale:** After clarifying the relationship between active PDF content and malware or exploit delivery, the project owner chose the safer sanitization policy.
- **Consequences:**
  - Embedded attachments are removed from the processed output and are not offered as separate downloads; the prior attachment question is therefore not applicable.
  - Server processing must still treat all inputs as untrusted and must never execute embedded actions or attachments.
  - Sanitization behavior and known coverage limitations require normal security and functional verification; Papyr must not claim perfect malware detection or universal sanitization beyond what is actually implemented.
  - Files classified as infrastructure threats remain blocked under DEC-088 rather than sanitized and returned.
  - Removing active elements may reduce fidelity and should be communicated honestly when detected.

## DEC-091 — Show general categories of active content removed

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When active PDF content is detected and sanitized, tell the user which general categories were found, such as JavaScript, embedded attachments, launch actions, or external actions, without exposing payloads or exploit-level details.
- **Rationale:** Category-level disclosure gives useful transparency without overwhelming users or leaking dangerous implementation details.
- **Consequences:**
  - Messages must be localized, accessible, concise, and distinguish sanitization from malware detection.
  - Do not display scripts, attachment contents, suspicious URLs, object internals, signatures, or scanner rules.
  - Sanitized category counts may be included in job-local UI state but must not include document contents or sensitive metadata in general product analytics.
  - The result must not imply that no other threat exists merely because listed categories were removed.

## DEC-092 — Inspect PDF-to-JPG inputs for server safety without carrying active content into images

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** PDF to JPG must treat and inspect source PDFs as untrusted for parser and infrastructure safety even though active PDF content is not represented in raster JPG outputs.
- **Rationale:** Rasterization prevents JavaScript, attachments, and launch actions from surviving in the image result, but malicious or malformed input can still target the PDF parser or exhaust resources.
- **Consequences:**
  - Rendering must occur with isolation, least privilege, bounded resources, current patched dependencies, and the threat-blocking policy in DEC-088.
  - Active-content categories need not trigger output sanitization reporting when rasterization inherently excludes them, but infrastructure-threatening inputs remain blocked.
  - Papyr must not execute actions, open attachments, or follow external references while rendering.
  - Successful rasterization is not a claim that the source PDF was malware-free.

## DEC-093 — Validate and decode JPG-to-PDF image inputs in isolation

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** JPG to PDF must verify image type from file bytes, reject unsupported or malformed inputs, enforce encoded and decoded resource limits, and decode images within an appropriately isolated processing boundary.
- **Rationale:** Extensions and declared MIME types are untrusted, and image decoders can be targeted by malformed files or decompression bombs.
- **Consequences:**
  - Validation must consider signatures, dimensions, pixel count, frame count where applicable, orientation data, decode expansion, and resource limits rather than extension alone.
  - Threat-classified files are blocked under DEC-088; ordinary invalid images receive safe localized validation errors.
  - EXIF preservation selected in DEC-084 does not authorize executing, logging, or trusting metadata fields.
  - Browser and server paths require equivalent safety outcomes even if their underlying decoders differ.

## DEC-094 — Return legacy feature groups gradually after the five-tool launch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** After the five-tool MVP is publicly relaunched, restore the remaining useful legacy Papyr capabilities progressively rather than limiting the roadmap to only PDF essentials or only document conversion.
- **Rationale:** The project owner intends the broader tool set to return over time while preserving a focused initial launch.
- **Consequences:**
  - Rotate, protect/unlock, watermark, sign, PDF to Word, OCR, PDF to Excel, and other retained legacy capabilities remain post-launch candidates rather than MVP scope.
  - Exact sequencing is intentionally unresolved and must be chosen later from user demand, operational readiness, complexity, cost, and the research/approval gate.
  - “All gradually” does not authorize bulk implementation or automatic restoration of obsolete behavior.
  - Each material capability still requires explicit owner approval before design and implementation planning.

## DEC-095 — Reuse existing infrastructure assets for the initial relaunch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Base initial operating costs on the existing VPS, existing `mypapyr.com` domain, and Cloudflare R2 free tier rather than provisioning a new infrastructure budget or replacement hosting stack.
- **Rationale:** These assets are already available and align with the retained Vercel, VPS, Cloudflare, and R2 topology.
- **Consequences:**
  - Research and design must verify current ownership, access, expiration, capacity, provider terms, and operational condition without assuming that “already available” means correctly configured or cost-free forever.
  - New paid services or upgrades require separate justification and owner approval.
  - Vercel, monitoring, email, backups, egress, overages, taxes, or renewal costs must still be documented when applicable.
  - This decision does not authorize deployment changes during the research gate.

## DEC-096 — Relaunch directly on the production domain after pre-release verification

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The public relaunch will switch directly to production on the existing domain without a public beta phase or a separately operated private staging environment.
- **Rationale:** The project owner prefers a direct production relaunch once the approved scope is ready.
- **Consequences:**
  - The absence of a persistent staging environment does not remove pre-release local, CI, preview-deployment, integration, security, accessibility, and smoke verification.
  - Vercel preview deployments and isolated backend test execution may be used as temporary validation mechanisms but are not public product phases.
  - Production activation requires rollback capability, backups where applicable, health monitoring, and the complete five-tool EN/ES launch gate in DEC-027.
  - Users must not see an unfinished beta label unless the owner later changes this decision.

## DEC-097 — Keep the owner accountable for operations with AI-assisted automation

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The project owner remains accountable for deployment, monitoring, incidents, backups, and dependency maintenance, while AI-assisted automation supports routine observation, reporting, and documented procedures.
- **Rationale:** The operating model should reduce manual burden without granting an automated agent unchecked production authority.
- **Consequences:**
  - High-risk actions such as production deploy, destructive cleanup outside policy, secret rotation, firewall or access changes, rollback, and provider configuration changes require explicit owner authorization unless a later narrowly scoped policy says otherwise.
  - Automation must produce auditable outputs, fail safely, protect secrets, and have pause/disable controls.
  - Canonical runbooks must enable the owner to understand and perform critical operations without depending on opaque agent behavior.
  - This decision does not restore the removed Guinevere runtime; any automation must be designed separately under the normal research and approval process.

## DEC-098 — Optimize the current architecture before vertically scaling the VPS

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** If production capacity becomes insufficient, first optimize worker bounds, queue behavior, processing configuration, and resource use, then upgrade the existing VPS before introducing a multi-VPS architecture.
- **Rationale:** This preserves operational simplicity and uses the retained topology efficiently before adding distributed-system complexity.
- **Consequences:**
  - Scaling actions must be driven by real production observability rather than the benchmark program rejected in DEC-066.
  - Optimization must not weaken output quality, privacy, security, retention, fairness, or reliability requirements without renewed approval.
  - Vertical upgrade costs require owner approval.
  - Horizontal scaling remains a later option if a single appropriately sized VPS is demonstrably inadequate.

## DEC-099 — Archive the legacy application without keeping it publicly accessible

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** After relaunch, the existing domain serves only the rebuilt product; the legacy application remains as preserved source/history and is not exposed through a public legacy subdomain.
- **Rationale:** One public version avoids user confusion, duplicated SEO surfaces, and ongoing security and maintenance obligations for obsolete software.
- **Consequences:**
  - Important legacy URLs require intentional redirects or replacement responses under the localized URL strategy.
  - Historical code and documentation remain clearly labeled and cannot be mistaken for the active production source of truth.
  - Production rollback should use controlled release artifacts and deployment procedures, not a permanently running public legacy site.
  - Secrets or sensitive evidence in repository history still require separate remediation even when the application is archived.

---

## DEC-100 — Target the public relaunch within one month

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Target the complete Papyr relaunch within one month while retaining the five-tool, English-and-Spanish, production-readiness gate.
- **Rationale:** The project owner selected a time-bound relaunch rather than an open-ended schedule.
- **Consequences:**
  - Planning must ruthlessly protect the approved MVP and defer non-launch capabilities.
  - The target does not authorize bypassing security, privacy, accessibility, testing, or owner-approval gates.
  - If the complete launch scope cannot be made production-ready within one month, surface the conflict early and seek an explicit scope or schedule decision rather than silently cutting quality.

## DEC-101 — Position Papyr as fast and trustworthy

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr's brand character is fast and trustworthy: professional, direct, calm, and easy to understand.
- **Rationale:** This supports task-oriented users and reinforces the primary product promise of speed and simplicity.
- **Consequences:**
  - Visual design, copy, status messages, support communication, and documentation must consistently express clarity and confidence without hype.
  - Papyr must avoid unsupported superlatives, fabricated quality claims, manipulative urgency, and overly technical user-facing language.
  - The existing identity may evolve under DEC-028, but this character is the tie-breaker for brand decisions.

## DEC-102 — Keep user experience ahead of advertising revenue

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When advertising and task completion conflict, user experience takes priority.
- **Rationale:** Papyr's long-term value depends on users completing PDF tasks quickly and trusting the product.
- **Consequences:**
  - Ads must not obstruct upload, controls, progress, results, downloads, error recovery, navigation, accessibility, or responsive layout.
  - The non-intrusive format restrictions in DEC-018 remain the launch policy.
  - Ad placement or provider behavior that materially harms trust, performance, or completion must be removed or reduced even if it lowers short-term revenue.

## DEC-103 — Delay launch rather than cut readiness or approved scope

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-100
- **Decision:** If the approved relaunch scope is not production-ready within the one-month target, delay the public launch rather than reducing scope or bypassing quality gates.
- **Rationale:** The owner prioritizes a complete, trustworthy release over meeting the target date at the cost of readiness.
- **Consequences:**
  - One month is a target, not an unconditional deadline.
  - Schedule risk must be reported early and transparently.
  - Any later proposal to reduce launch scope still requires explicit owner approval.

## DEC-104 — Launch across all target regions simultaneously

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Relaunch Papyr for the United States, Latin America, and Europe at the same time rather than using a regional rollout.
- **Rationale:** The owner wants the international product available across all selected markets from day one.
- **Consequences:**
  - English and Spanish experiences, regional routing, legal disclosures, advertising behavior, support, and operational readiness must cover all target regions before launch.
  - A regional compliance or provider constraint cannot be ignored; it must be resolved or the affected behavior suppressed while preserving product access where feasible.
  - Monitoring and launch communication must distinguish regions sufficiently to identify material failures without creating prohibited user profiling.

## DEC-105 — Keep Papyr free and advertising-funded during the first year

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr remains fully free to users and is monetized only through approved advertising during its first year; no paid plan is part of the launch or first-year roadmap.
- **Rationale:** The owner prioritizes organic growth and a simple, no-account PDF-tools experience.
- **Consequences:**
  - Do not add subscriptions, payments, premium feature gates, trials, credits, or account-based upsells during this period without superseding approval.
  - Advertising remains subordinate to user experience under DEC-102 and restricted to the formats in DEC-018.
  - Infrastructure and feature decisions must remain sustainable within existing assets and approved costs rather than depending on future subscription revenue.

## DEC-106 — Grow through SEO and the localized blog, then monetize with Adsterra

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr's primary growth engine after relaunch is organic search supported by useful English and Spanish tool pages and blog content; approved Adsterra placements monetize that traffic rather than acting as an acquisition channel.
- **Rationale:** This aligns the free utility product with durable search demand and the already selected advertising model.
- **Consequences:**
  - Content must serve genuine user intent and avoid keyword filler, duplication, and tool-page cannibalization.
  - Organic visibility and useful traffic take precedence over maximizing publication volume or ad density.
  - Paid user acquisition and a required social-media program are outside the current strategy unless approved later.

## DEC-107 — Offer an optional marketing newsletter

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr may offer an optional newsletter for content and product updates without making subscription part of PDF processing or access to the tools.
- **Rationale:** The owner wants an owned communication channel while preserving the no-account, immediate-use product model.
- **Consequences:**
  - Subscription requires explicit opt-in, clear expectations, unsubscribe capability, minimal data collection, and accurate privacy disclosure.
  - Newsletter consent must remain separate from support/contact submissions, analytics, advertising, and tool usage.
  - Provider selection, retention, regional legal requirements, and operational ownership require approval before implementation.
  - No document, filename, processing history, password, or sensitive tool data may enter the mailing system.

## DEC-108 — Focus the first year on individual web users

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** During the first year, Papyr serves general individual users through the public website and does not offer a business API, organizational workspace, enterprise plan, or business-specific support product.
- **Rationale:** A narrow audience and product model protects the five-tool relaunch and avoids introducing accounts, billing, API operations, and enterprise obligations.
- **Consequences:**
  - Architecture need not prematurely support public API customers, organizations, API keys, usage billing, or service-level contracts.
  - Ordinary organizations may still use the public tools under the same published terms and fair-use controls as other users.
  - Business/API offerings require separate research and explicit future approval.

## DEC-109 — Defer the optional newsletter until after relaunch

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-107
- **Decision:** Do not include newsletter subscription or email-marketing infrastructure in the one-month relaunch scope; consider it only after the rebuilt product is live.
- **Rationale:** The launch should remain focused on the five tools, localized content, and production readiness.
- **Consequences:**
  - Relaunch pages must not contain inactive newsletter forms or imply that email updates are available.
  - Future newsletter implementation remains subject to the consent, privacy, provider, and operational requirements in DEC-107.
  - Deferral does not block transactional replies to user-initiated support requests under DEC-046.

## DEC-110 — Present Papyr publicly as a product brand

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Public-facing pages communicate under the Papyr brand without requiring a founder profile, personal photograph, or personal origin story.
- **Rationale:** The owner prefers product-led trust rather than personal-brand positioning.
- **Consequences:**
  - Trust must come from clear product behavior, honest claims, accessible support, transparent policies, and reliable operations.
  - Legally required operator or contact information must still be provided where applicable; brand-only presentation is not permission to conceal mandatory disclosures.
  - Blog authorship must not fabricate people or credentials.

## DEC-111 — Do not solicit donations or voluntary tips

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr will not add donation, tip, or supporter-payment mechanisms alongside its advertising-funded model.
- **Rationale:** The owner wants a simple free product monetized through the already approved advertising strategy.
- **Consequences:**
  - Relaunch and first-year planning exclude donation buttons, crowdfunding links, and payment-provider integration for voluntary support.
  - Monetization remains governed by DEC-018, DEC-102, and DEC-105.
  - Any future donation model requires explicit approval and separate legal, payment, and disclosure review.

## DEC-112 — Do not require social media for the relaunch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Official social-media accounts and an active social publishing program are not required for the Papyr relaunch.
- **Rationale:** Product readiness, SEO, the localized blog, and user support are higher priorities within the one-month target.
- **Consequences:**
  - Relaunch scope excludes mandatory social account creation, posting calendars, and social automation.
  - Papyr must not show empty or inactive social links merely for appearance.
  - A future official channel may be approved separately if it has a clear operational purpose and owner.

## DEC-113 — Display publication and update dates on blog articles

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Every blog article visibly displays both its original publication date and its latest material update date.
- **Rationale:** Readers and search engines should be able to distinguish original publication from substantive maintenance.
- **Consequences:**
  - Dates must be truthful, locale-formatted, and represented consistently in metadata and structured data.
  - Automated edits must not advance the update date for trivial formatting or deployment-only changes.
  - EN and ES counterparts may have distinct publication/update timestamps when their review or material content differs.

## DEC-114 — Preserve and update legacy content that still attracts traffic

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Legacy public pages or articles that still receive meaningful traffic should be retained and updated for the rebuilt Papyr rather than discarded solely because the site structure is changing.
- **Rationale:** Existing search visibility and useful user intent are assets worth preserving when the content remains relevant.
- **Consequences:**
  - Each retained page must be audited for factual accuracy, product alignment, language, search intent, duplication, and policy consistency.
  - Retention does not permit stale instructions, unavailable features, obsolete infrastructure claims, or duplicate pages that compete with canonical EN/ES content.
  - URL, localization, canonical, and redirect treatment must be defined during the SEO design, especially for legacy Indonesian pages.
  - Pages without continuing user value may still be redirected or retired through an explicit content-mapping decision.

## DEC-115 — Retain Indonesian as an additional content locale

- **Date:** 2026-07-31
- **Status:** Accepted; expands DEC-004
- **Decision:** Continue serving valuable legacy Indonesian content and support Indonesian as an additional locale alongside the required English and Spanish launch experiences.
- **Rationale:** Existing Indonesian search traffic and useful content should not be abandoned during the international repositioning.
- **Consequences:**
  - English and Spanish remain mandatory launch languages; Indonesian content must be deliberately mapped, updated, and localized rather than left as an inconsistent legacy island.
  - Locale routing, hreflang, canonicals, sitemaps, navigation, and metadata must include Indonesian wherever that version exists.
  - The exact amount of Indonesian tool, legal, support, and blog coverage needed at relaunch must be reconciled with the one-month schedule and DEC-103 without publishing misleading partial experiences.

## DEC-116 — Provide a simple public service-status page

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr will provide a simple public status page showing material service availability and incidents without exposing sensitive infrastructure details.
- **Rationale:** Users need a trustworthy way to distinguish a service incident from a problem with their own file or device.
- **Consequences:**
  - Status communication should cover user-relevant components and use plain EN/ES/ID language where supported.
  - Incident updates must be truthful and timely but omit hostnames, credentials, defensive controls, exploit details, and other sensitive operational information.
  - The status page complements internal monitoring and in-product outage messaging; it does not replace either.

## DEC-117 — Allow concise result-problem reports without document upload

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Users may report a broken or incorrect result directly from the result experience using a short categorized report that does not upload or attach their source or output document.
- **Rationale:** Result-local feedback provides actionable quality signals while avoiding unnecessary handling of sensitive files.
- **Consequences:**
  - Reports may include the tool, processing path, sanitized error/result category, browser context, and user-entered description, but never filenames, document contents, passwords, signed URLs, or object keys.
  - Submission must be optional, protected from spam, and clearly distinguish product feedback from urgent security or privacy support.
  - The report flow must integrate with the owner-managed support process without promising response times that cannot be maintained.

## DEC-118 — Launch all five tools completely in Indonesian

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-027 and DEC-115
- **Decision:** The public relaunch requires complete Indonesian versions of all five MVP tools and essential supporting pages alongside English and Spanish.
- **Rationale:** Indonesian is now a first-class launch locale rather than only a legacy-content preservation measure.
- **Consequences:**
  - The launch gate becomes five production-ready tools across EN, ES, and ID.
  - Tool instructions, errors, processing disclosures, results, metadata, navigation, legal/support surfaces, and core accessibility text must be complete and consistent in all three locales.
  - The one-month target remains subordinate to completeness under DEC-103.

## DEC-119 — Host the public status experience on Vercel

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-116
- **Decision:** Serve Papyr's simple public status experience through the Vercel-hosted frontend so it remains independent of a backend VPS outage.
- **Rationale:** Vercel is already part of the approved topology and separates status visibility from the most processing-intensive infrastructure.
- **Consequences:**
  - Status data and health checks must avoid making the page depend solely on the failing VPS to render.
  - A broader Vercel or DNS outage may still affect availability; the page must not claim complete infrastructure independence.
  - Implementation must remain simple and avoid exposing internal operational details.

## DEC-120 — Allow optional reply email on result-problem reports

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-117
- **Decision:** A user may submit a result-problem report anonymously or optionally provide an email address for follow-up.
- **Rationale:** This preserves low-friction feedback while enabling direct clarification when the user wants a response.
- **Consequences:**
  - The email field must be clearly optional and used only for the submitted support matter, not automatically added to the future newsletter.
  - Reports require minimal retention, access controls, deletion policy, privacy disclosure, and safe operational routing.
  - Even with an email address, Papyr must not request the user to attach sensitive source or result documents through this flow.

## DEC-121 — Launch the initial blog topics in English, Spanish, and Indonesian

- **Date:** 2026-07-31
- **Status:** Accepted; expands DEC-052
- **Decision:** Each of the five initial blog topics must have intentionally localized English, Spanish, and Indonesian versions, producing 15 launch articles.
- **Rationale:** The owner wants the launch content strategy to support all three first-class product locales.
- **Consequences:**
  - Articles must be localized for language and search intent rather than mechanically translated.
  - Cross-locale metadata, hreflang, canonicals, internal links, and update tracking must cover all three versions.
  - The expanded content requirement remains subject to the complete-launch-over-deadline policy in DEC-103.

## DEC-122 — Use localized Indonesian slugs

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-023
- **Decision:** Indonesian tool and content URLs use translated, search-appropriate slugs under the `/id/` locale prefix rather than reusing English slugs by default.
- **Rationale:** Localized URLs better match the intended Indonesian search and navigation experience.
- **Consequences:**
  - Slugs must use natural, stable terminology selected during SEO design and avoid awkward literal translation.
  - Legacy Indonesian URLs require an explicit mapping to retained localized URLs, with redirects where paths change.
  - EN and ES retain their own localized slug policies, and all locale alternates must remain connected through hreflang and canonicals.

## DEC-123 — Publish a simple high-level roadmap

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr may publish a concise roadmap showing broad future direction without a detailed feature backlog or firm delivery dates.
- **Rationale:** Users can understand where the product is heading without creating unreliable promises.
- **Consequences:**
  - The roadmap must clearly distinguish launched, planned, and exploratory capabilities.
  - It must not expose internal security work, infrastructure details, speculative dates, or unapproved features as commitments.
  - Roadmap changes require normal content review, and the internal decision log remains the authoritative discovery record.

## DEC-124 — Publish each post-launch topic in all three languages together

- **Date:** 2026-07-31
- **Status:** Accepted; expands DEC-053
- **Decision:** The post-launch publishing cadence is at most one new topic per day, with its English, Spanish, and Indonesian versions released as one coordinated set.
- **Rationale:** All first-class locales should receive equivalent new content without becoming permanently delayed translation queues.
- **Consequences:**
  - One daily topic produces three intentionally localized pages; a failed language or quality gate blocks the whole set for that day.
  - Automation must preserve cross-locale linking, metadata, dates, and factual consistency while allowing culturally appropriate wording and search intent.
  - Skipping a day is preferable to publishing an incomplete or low-quality locale set.

## DEC-125 — Keep the public roadmap informational only

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-123
- **Decision:** The public roadmap does not include public voting, feature-request submission, comments, or other interactive prioritization mechanisms.
- **Rationale:** The owner wants a simple statement of direction without creating moderation overhead or implied commitments.
- **Consequences:**
  - General product feedback may still use the approved support channels, but the roadmap itself remains read-only.
  - Public popularity signals do not determine implementation priority; future features remain subject to research and explicit owner approval.

## DEC-126 — Keep usage totals private and defer them to a future admin dashboard

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Do not display public counters such as files processed, users served, or downloads completed; trustworthy aggregate usage metrics may be shown later in a private admin dashboard.
- **Rationale:** Public vanity metrics add little user value and can create misleading claims, while private operational metrics can support product management.
- **Consequences:**
  - Relaunch scope excludes public counters and excludes the unfinished legacy admin-dashboard milestone.
  - Any future admin dashboard requires separate scope, authentication, authorization, privacy, security, and explicit approval.
  - Underlying metrics must follow DEC-025 and must not contain filenames, contents, passwords, object keys, signed URLs, or prohibited identifiers.

## DEC-127 — Audit the complete legacy public URL inventory before relaunch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Audit the full legacy sitemap and indexable URL inventory before relaunch, not only pages currently known to receive traffic.
- **Rationale:** Thin, duplicate, stale, or conflicting pages can weaken the rebuilt information architecture and carry incorrect content into search results.
- **Consequences:**
  - Every legacy public URL must receive an explicit retain/update, redirect, noindex, or removal disposition.
  - The audit must reconcile locale mappings, canonicals, hreflang, sitemap inclusion, internal links, and the preservation policy in DEC-114.
  - Removal must avoid unnecessary soft 404s and redirect chains; retained pages must meet current content and policy standards.

## DEC-128 — Exclude competitor-comparison pages from relaunch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Do not create alternative, versus, or competitor-comparison landing pages for the initial relaunch.
- **Rationale:** Tool quality, localized educational content, and trustworthy search intent are higher priorities than comparison-keyword expansion.
- **Consequences:**
  - Launch content must not use unsupported superiority claims or competitor trademarks merely to capture search traffic.
  - Neutral comparison content may be reconsidered later through the normal research and approval process.
  - Ordinary educational articles may discuss objective format or workflow choices without becoming disguised competitor pages.

## DEC-129 — Monetize blog pages with light non-intrusive advertising

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Blog pages may carry light banner/native Adsterra placements while preserving reading quality and the UX-first policy.
- **Rationale:** The blog is part of Papyr's organic growth engine and can contribute to the advertising-funded model without becoming ad-heavy.
- **Consequences:**
  - Ads must not interrupt headings, obscure content, mimic editorial links, trigger layout shifts, or overwhelm mobile reading.
  - Stable reserved slots, lazy/async loading, accessibility, performance, regional policy handling, and DEC-018 restrictions apply.
  - Placements that materially harm engagement, trust, search performance, or Core Web Vitals must be reduced or removed under DEC-102.

## DEC-130 — Allow light advertising on legal, support, and status pages

- **Date:** 2026-07-31
- **Status:** Accepted risk
- **Decision:** Privacy, Terms, Cookies/Advertising, Contact, Support, and public Status pages may use the same light non-intrusive banner/native advertising policy as the blog.
- **Rationale:** The owner selected consistent advertising coverage rather than keeping trust-oriented pages ad-free.
- **Consequences:**
  - Legal, support, incident, consent, and safety information must remain immediately readable and functional when advertising is blocked, unavailable, slow, or broken.
  - Ads must be clearly separated from policy text, support controls, incident information, and navigation and must not create misleading endorsement or consent patterns.
  - Status rendering and critical communication must not depend on Adsterra scripts.
  - This is recorded as an accepted trust and third-party dependency risk; DEC-018 and DEC-102 still require removal of placements that materially harm users.

## DEC-131 — Keep result-page advertising away from Download controls

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Result pages may contain approved advertising, but ads must be spatially and visually separated from primary and fallback Download controls.
- **Rationale:** Users must never confuse an advertisement with the action that retrieves their processed file.
- **Consequences:**
  - No ad may imitate a download button, result card, progress state, warning, or system action.
  - Download, expiry, retry, and result-problem reporting remain visually dominant and accessible.
  - Mobile layouts must preserve meaningful separation rather than collapsing ads beside or between essential actions.

## DEC-132 — Publicly commit that Papyr's core tools remain free forever

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr may state publicly that its core PDF tools are free forever rather than merely free during the first year.
- **Rationale:** The owner selected permanent free access as part of Papyr's product promise.
- **Consequences:**
  - The five launch tools and the essential ability to complete and download their outputs must not later be placed behind payment, subscriptions, credits, or mandatory accounts.
  - Advertising and any future approved revenue streams must not revoke or materially degrade the promised free core experience.
  - This commitment does not promise unlimited abusive use, unlimited file sizes, perpetual operation of every future experimental feature, or exemption from fair-use and safety controls.
  - Any future paid offering must be genuinely additive and cannot contradict the public free-core promise without explicitly superseding this decision and addressing user trust.

## DEC-133 — Extend the free-forever promise to all core public tools

- **Date:** 2026-07-31
- **Status:** Accepted; expands DEC-132
- **Decision:** Every core public PDF utility that Papyr releases, including useful legacy tools restored after the MVP, remains free to use and download.
- **Rationale:** Permanent free access applies to Papyr's core utility product, not only the initial five tools.
- **Consequences:**
  - Restored core tools cannot be placed behind subscriptions, credits, payment, or mandatory accounts.
  - The promise remains compatible with fair-use, safety, file-size, capacity, and abuse controls.
  - A future capability can be classified as non-core only through explicit owner approval before public positioning or implementation.

## DEC-134 — Use fair queuing when free capacity is constrained

- **Date:** 2026-07-31
- **Status:** Accepted; reinforces DEC-020 and DEC-035
- **Decision:** When server demand is high, preserve free access through fair queuing and adaptive fair-use controls rather than introducing payment priority or silently degrading processing quality.
- **Rationale:** Capacity pressure should not contradict the free-core promise or create a pay-to-complete experience.
- **Consequences:**
  - Users may wait longer, and hard safety, queue, storage, expiry, and health caps still apply.
  - Queue state and delays must be communicated honestly.
  - Papyr must not create a paid fast lane under the current product model.

## DEC-135 — Do not plan an alternative monetization model

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** If Adsterra underperforms or must be reduced for user experience, Papyr will not automatically replace it with another ad network, sponsorship, donations, or paid access under the current plan.
- **Rationale:** The owner prefers Adsterra or operating without revenue over expanding monetization complexity.
- **Consequences:**
  - Papyr may reduce or remove harmful Adsterra placements even if that results in lower or zero revenue.
  - No fallback monetization integration belongs in the relaunch or first-year roadmap.
  - Any future alternative requires explicit owner approval and must preserve the free-core and UX-first commitments.

## DEC-136 — Continue operating without ads when feasible

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** If Adsterra is not viable or must be removed, Papyr should continue without advertising while the owner can sustainably cover the existing operating costs.
- **Rationale:** Product access and user experience matter more than preserving advertising revenue.
- **Consequences:**
  - Ads are not a dependency for tool availability, processing, downloads, status, legal information, or support.
  - Cost sustainability must remain visible to the owner; material new spending still requires approval.
  - If operation becomes financially unsustainable, continuation requires a new explicit decision rather than silently degrading or paywalling the core tools.

## DEC-137 — Use fair scheduling that prevents queue monopolization

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-134
- **Decision:** Server scheduling should balance waiting time and job complexity while preventing users or unusually heavy jobs from monopolizing capacity; it must not use pure smallest-job-first or unrestricted FIFO as the sole policy.
- **Rationale:** Fairness requires both reasonable progress for ordinary jobs and protection against starvation or resource capture.
- **Consequences:**
  - The approved design must define understandable fairness classes, concurrency bounds, and starvation prevention without exposing exploitable defensive detail.
  - No paid priority lane is permitted.
  - User-facing status should explain delays plainly without promising exact completion times that cannot be known.

## DEC-138 — State the free-forever core commitment on the public roadmap

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-123 and DEC-133
- **Decision:** The public roadmap explicitly states that Papyr's core public PDF tools will remain free forever.
- **Rationale:** Permanent free access is a defining product direction, not only an internal implementation constraint.
- **Consequences:**
  - Roadmap and homepage language must remain consistent and accurately bounded by fair-use, safety, and capacity policies.
  - The statement must not imply unlimited resources, guaranteed availability, or that every experimental or non-core future service is covered.
  - Future roadmap edits cannot quietly weaken the commitment.

## DEC-139 — Lead with fast, easy, and free PDF tools

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The first message a new visitor should understand is that Papyr provides PDF tools that are fast, easy, and free.
- **Rationale:** This directly expresses the primary user job and the product's speed-and-simplicity positioning.
- **Consequences:**
  - Homepage and tool-page hierarchy must lead with immediate utility rather than infrastructure, technical processing details, or lengthy marketing copy.
  - Privacy, trustworthy behavior, output quality, and the free-forever commitment support the promise with clear evidence.
  - Copy must remain honest and avoid unsupported absolute speed or quality claims.

## DEC-140 — Relaunch by activating the rebuilt site without a launch campaign

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Make the rebuilt Papyr directly available on the production domain when ready, without a dedicated launch campaign or mandatory announcement article.
- **Rationale:** The owner prefers to focus effort on the product, search visibility, and reliable operation.
- **Consequences:**
  - Deployment, redirects, indexing, monitoring, support, and status communication still require a coordinated activation checklist.
  - The absence of a campaign does not permit an unannounced breaking migration for existing indexed URLs.
  - Normal blog publishing begins under the approved content plan rather than requiring a launch-story post.

## DEC-141 — Prioritize stability, then content growth, then the next tool after launch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** During the first 30 days after relaunch, priorities are ordered: (1) stability and corrective work, (2) localized content growth, and (3) development of the next legacy tool.
- **Rationale:** Reliable completion and rapid correction should be established before accelerating acquisition or expanding product surface.
- **Consequences:**
  - Incidents, processing failures, support signals, security, accessibility, and material performance regressions take precedence over the publishing cadence and new features.
  - The daily localized blog cadence may pause when operational work requires attention or content gates fail.
  - Work on the next tool begins only when the rebuilt core is sufficiently stable and still requires separate research and owner approval.

## DEC-142 — Use an evolved directory-style product experience

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Base the rebuilt Papyr product and UX on an evolved version of its existing directory model: a clear homepage presenting the five tools, with each dedicated tool page following a focused select, configure-if-needed, process, and download journey.
- **Rationale:** This approach preserves Papyr's strongest familiar pattern while supporting search intent, immediate task completion, the one-month target, and deliberate modernization without a disruptive redesign.
- **Consequences:**
  - Do not replace the homepage with a universal uploader or reduce the product to nearly context-free tool pages.
  - Tool functionality remains visually primary; trust, instructions, SEO content, related tools, and light advertising support the task without obstructing it.
  - Existing interaction patterns may be retained only when accurate, accessible, responsive, and consistent with the approved processing and disclosure policies.

## DEC-143 — Preserve the existing Papyr visual language and UX

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-028 and DEC-142
- **Decision:** The rebuilt website must look and feel like the existing Papyr website. Its established visual identity, page composition, tool-directory presentation, component character, and familiar interaction patterns are the primary UI/UX reference rather than inspiration for a visibly different redesign.
- **Rationale:** The owner wants continuity with the existing product while rebuilding its implementation and correcting weaknesses.
- **Consequences:**
  - Existing frontend pages and components in the read-only legacy clone must be used as concrete visual and interaction references during design and implementation.
  - Preserve recognizable branding, color direction, typography character, card language, spacing rhythm, navigation model, uploader experience, and overall visual tone unless a change is necessary for an approved requirement.
  - Changes are limited to purposeful improvements such as consistency, responsive behavior, accessibility, localization resilience, truthful states, corrected interactions, performance, and removal of legacy defects.
  - Do not introduce a new aesthetic, dashboard-style shell, universal workspace, unrelated design system, or fashionable visual treatment that makes Papyr feel like a different product.
  - Material visual departures require explicit owner approval through comparison with the existing interface.

## DEC-144 — Retain the existing tool-page sequence

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-142 and DEC-143
- **Decision:** Each of the five launch tool pages follows the existing Papyr sequence: tool header, file dropzone, configuration when needed, processing state, result and download, privacy information, and related tools.
- **Rationale:** The existing sequence is familiar, task-focused, and suitable for the approved directory-style product experience.
- **Consequences:**
  - Tool-specific configuration appears only after a valid file selection when relevant.
  - The sequence is standardized across tools while preserving necessary tool-specific controls.
  - Legacy ordering inconsistencies are corrected without introducing a different page model.

## DEC-145 — Keep the page shell visible during processing

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Navigation and supporting page structure remain visible while a tool processes a file; only the tool workspace changes state.
- **Rationale:** A stable shell preserves orientation and avoids an unnecessary full-screen processing experience.
- **Consequences:**
  - Processing must not replace the whole page or hide navigation.
  - Supporting content may remain below the active workspace but must not distract from status, cancellation policy, errors, or completion.
  - Layout must remain stable across idle, processing, error, and result states.

## DEC-146 — Retain the existing result-card pattern

- **Date:** 2026-07-31
- **Status:** Accepted; reinforces DEC-029 and DEC-068
- **Decision:** Successful jobs use an evolved version of the existing Papyr result card with automatic download attempt, a persistent manual Download control, an honest result summary, and an action to process another file.
- **Rationale:** The existing result pattern clearly completes the task and already aligns with the approved download behavior.
- **Consequences:**
  - Auto-download failure must leave the job in Ready state and preserve the same manual result.
  - Summary details vary by tool but must not use fabricated savings, progress, or quality claims.
  - Advertising must remain spatially and visually separate from result and download controls under DEC-131.

## DEC-147 — Retain the existing categorized navigation model

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-143
- **Decision:** Preserve Papyr's existing category-based navbar rather than replacing it with a flat list of the five launch tools.
- **Rationale:** The existing navigation is part of Papyr's familiar interface and can accommodate restored tools later without another navigation redesign.
- **Consequences:**
  - Launch categories expose only available destinations and must not create dead links for deferred tools.
  - Desktop and mobile navigation must preserve the existing character while correcting keyboard, focus, expansion-state, and accessibility defects.
  - Category structure must remain compatible with localized labels and slugs.

## DEC-148 — Present all five launch tools equally on the homepage

- **Date:** 2026-07-31
- **Status:** Accepted; clarifies DEC-143
- **Decision:** The homepage preserves the existing equal-weight tool-directory grid; Compress PDF does not receive a special oversized or featured treatment.
- **Rationale:** The owner requires the homepage presentation to remain consistent with the existing Papyr interface.
- **Consequences:**
  - All five cards follow the same visual hierarchy and interaction pattern.
  - Ordering may follow the existing product logic, but visual prominence must not imply that one tool is a separate primary product.
  - Advertising and supporting content must not disrupt the directory's scanability.

## DEC-149 — Keep the language selector in the navbar

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The EN/ES/ID language selector remains available in the navbar across desktop and mobile experiences.
- **Rationale:** Persistent placement makes locale switching easy to discover throughout the product.
- **Consequences:**
  - The control must show the active locale and use accessible keyboard and screen-reader behavior.
  - Switching locale should preserve the equivalent page or tool where a localized counterpart exists.
  - The implementation must remain compact on mobile without becoming a footer-only control.

## DEC-150 — Preserve the existing homepage content depth

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-043 and DEC-143
- **Decision:** Preserve the existing homepage's overall content depth while adapting it to the five-tool launch: concise hero, equal-weight tool directory, trust and privacy explanation, short how-it-works section, FAQ, and footer.
- **Rationale:** This keeps the rebuilt homepage familiar and sufficiently informative without turning it into a dashboard or a content-heavy landing page.
- **Consequences:**
  - Supporting sections must remain visually subordinate to the five-tool directory.
  - Copy and structure must be complete in EN, ES, and ID.
  - Stale claims and obsolete tool references from the legacy homepage must not be carried forward.

## DEC-151 — Place tool-page advertising after the primary tool experience

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-018, DEC-102, DEC-129, and DEC-131
- **Decision:** On tool pages, approved light banner or native advertising may appear only after the primary tool interaction and result/download experience, within supporting content rather than before the uploader.
- **Rationale:** Tool completion and user trust take priority over advertising revenue.
- **Consequences:**
  - Upload, configuration, processing, result, and download controls must not be displaced or interrupted by advertising.
  - Ads must remain visually distinct from product controls and must not imitate download or continuation actions.
  - Reserved dimensions, asynchronous or lazy loading, accessibility, layout stability, and Core Web Vitals protections remain required.

## DEC-152 — Apply the categorized navigation choice to the five-tool launch

- **Date:** 2026-07-31
- **Status:** Accepted; confirms DEC-147
- **Decision:** At launch, retain Papyr's categorized navigation and populate it only with the five available tools; deferred tools must not appear as active destinations.
- **Rationale:** This preserves the existing Papyr navigation language while remaining truthful about launch scope and accommodating future tool restoration.
- **Consequences:**
  - Empty categories must be omitted or sensibly consolidated without changing the familiar visual model.
  - No coming-soon links or dead destinations are permitted in primary navigation.
  - Category labels and destinations must be localized consistently across EN, ES, and ID.

## DEC-153 — Keep processing and results within one tool page

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-142 and DEC-143
- **Decision:** Preserve Papyr's existing single-page tool flow: the same tool page transitions from selection and configuration through processing to the result and download state.
- **Rationale:** The existing flow is direct, familiar, and avoids unnecessary navigation for task-oriented users.
- **Consequences:**
  - Successful processing must not redirect to a separate result URL.
  - State transitions must be accessible, announced appropriately, and recoverable according to the approved same-tab session rules.
  - The Ready state keeps both automatic download behavior and a visible manual Download control.

## DEC-154 — Retain the existing Related Tools section

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-143
- **Decision:** Preserve the existing Related Tools pattern after the primary tool experience and supporting content on each tool page.
- **Rationale:** It provides familiar, non-disruptive discovery of other Papyr utilities without crowding the active workflow.
- **Consequences:**
  - Only available launch tools may be linked; the current tool must be excluded.
  - Content, ordering, labels, and localized slugs must come from one canonical tool catalog rather than duplicated arrays.
  - Related Tools must remain visually subordinate to processing and download actions.

## DEC-155 — Preserve the existing mobile category accordion

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-147 and DEC-152
- **Decision:** Preserve Papyr's existing mobile category accordion navigation rather than replacing it with a flat list or full-screen drawer.
- **Rationale:** It retains the existing mobile interaction language and scales naturally as tools return after launch.
- **Consequences:**
  - Expansion state, focus management, keyboard operation, touch targets, active-page indication, and screen-reader semantics must be corrected.
  - Only launch-available destinations appear as active links.
  - The EN/ES/ID selector remains compact and available within the mobile navigation experience.

## DEC-156 — Reset the tool flow with an explicit process-another-file action

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-143 and DEC-153
- **Decision:** Preserve the existing explicit “process another file” action in the result state. Activating it clears the current tool state and returns the same page to its uploader state without a full-page reload.
- **Rationale:** This keeps the result focused while giving users a predictable way to start another task.
- **Consequences:**
  - Reset must revoke local buffers and object URLs and clear nonessential task state safely.
  - Reset must not delete a server result before its fixed expiry or invalidate an already-issued reusable download result.
  - Focus must return to an appropriate heading or uploader control after reset.

## DEC-157 — Preserve accordion FAQs on tool pages

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-044 and DEC-143
- **Decision:** Preserve the existing compact accordion FAQ pattern on individual tool pages.
- **Rationale:** It keeps complete supporting information available without overwhelming the primary workflow.
- **Consequences:**
  - Questions and answers must be localized in EN, ES, and ID and remain accurate for each tool.
  - Accordion controls require correct expanded state, keyboard support, focus visibility, and screen-reader semantics.
  - FAQ structured data must match visible content and must not contain duplicated or misleading claims.

## DEC-158 — Preserve inline error cards

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-143
- **Decision:** Preserve the existing inline error-card pattern within the tool workflow rather than using transient toast notifications or blocking modals for ordinary processing failures.
- **Rationale:** Inline errors keep context visible and provide persistent recovery actions without interrupting the entire page.
- **Consequences:**
  - Errors must use clear localized language and offer only valid retry, reset, password, or support-report actions for the failure type.
  - Error regions must be announced accessibly without stealing focus unexpectedly.
  - Technical details, infrastructure identifiers, sensitive input data, and exploit information must not be exposed.

## DEC-159 — Keep the rebuild in one monorepo

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Keep the Papyr rebuild in one repository containing the frontend, backend, deployment configuration, canonical documentation, and related test infrastructure, with explicit boundaries between them.
- **Rationale:** Papyr is one product and coordinated changes across its web interface, processing API, operations, and documentation should remain reviewable together.
- **Consequences:**
  - The legacy clone remains a separate read-only reference and is not the rebuild workspace.
  - Removed Guinevere functionality must not be reintroduced as a monorepo package.
  - CI may use path-aware jobs while preserving integrated release traceability.

## DEC-160 — Production backend deployment is manually executed by the agent after approval

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-097
- **Decision:** Production backend deployment to the VPS is not automatic after merge. Sisyphus executes the documented deployment procedure manually only after the owner gives explicit authorization for that deployment.
- **Rationale:** The owner wants the agent to perform deployment work while retaining an explicit control point for production changes.
- **Consequences:**
  - CI may automatically build, test, and scan artifacts but must not independently change production.
  - Each production deployment requires an explicit owner instruction, pre-deployment verification, rollback readiness, and post-deployment smoke checks.
  - Credentials remain protected and must not be exposed in chat, source control, logs, or audit artifacts.
  - This decision does not authorize any current VPS access or deployment activity.

## DEC-161 — Public service status is automatically derived

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-116 and DEC-119
- **Decision:** The public status experience is updated automatically from approved service health signals rather than through owner-authored incident updates.
- **Rationale:** Automated status avoids dependence on manual updates during operational incidents.
- **Consequences:**
  - Status must be hosted independently on Vercel and remain useful when the backend VPS is unavailable.
  - Health signals must be meaningful, resilient to transient noise, and must not expose sensitive infrastructure details.
  - Status wording must distinguish observable service availability from guarantees about every processing engine or user request.

## DEC-162 — Deploy API, queue, workers, Redis, and Nginx as one Docker Compose stack

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-017 and DEC-019
- **Decision:** On the VPS, operate the FastAPI application, Redis, bounded PDF workers, and Nginx as separate services managed through one production Docker Compose stack.
- **Rationale:** This preserves the existing containerized operational model while giving the queue and processing workers clear runtime boundaries.
- **Consequences:**
  - Service health checks, resource limits, restart behavior, persistent Redis state where required, internal networking, and startup dependencies must be explicit.
  - Redis and worker ports must not be publicly exposed.
  - The stack must support controlled deployment and rollback under DEC-160.

## DEC-163 — Keep tool pages available during backend outages

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When the backend is unavailable, Papyr tool pages remain accessible. Browser-capable operations may continue locally, while server-dependent processing clearly communicates temporary unavailability.
- **Rationale:** A backend incident should not unnecessarily take down the informational site or safe client-side capabilities.
- **Consequences:**
  - The frontend must not redirect ordinary tool traffic to the status page or globally disable every tool.
  - Availability and error messaging must accurately distinguish local and server processing paths.
  - Unsafe fallback, repeated submissions, and misleading progress must be prevented.

## DEC-164 — Version the rebuild API under `/api/v1`

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The rebuild backend exposes its public processing and task contracts under an explicit `/api/v1` prefix.
- **Rationale:** An explicit version boundary supports future contract evolution without silently breaking deployed clients.
- **Consequences:**
  - Processing, task status, cancellation where applicable, limits, and related machine-readable endpoints use the same versioned contract.
  - Frontend configuration and Nginx routing must use one canonical API base.
  - Legacy routes require an explicit migration or retirement disposition and must not remain accidentally active.

## DEC-165 — Publish one machine-readable capability and limits contract

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-034
- **Decision:** The versioned backend API is the canonical source for server-processing capabilities and limits. The frontend reads and presents this machine-readable contract rather than maintaining an independent hardcoded copy.
- **Rationale:** One source of truth prevents UI/API drift and lets operational limits change without rebuilding misleading frontend copy.
- **Consequences:**
  - The contract must be cacheable safely, versioned, localized at the presentation layer, and have conservative frontend fallback behavior if unavailable.
  - Backend validation remains authoritative even when the frontend pre-validates inputs.
  - Browser-specific safety limits may remain frontend capability logic but must be clearly distinguished from server limits.

## DEC-166 — Enforce temporary-file deletion through the application with R2 lifecycle as a safety net

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-013, DEC-067, and DEC-070
- **Decision:** The application actively deletes temporary R2 objects according to each job's absolute one-hour deadline, while an R2 lifecycle rule provides independent backup cleanup.
- **Rationale:** Active deletion provides timely enforcement, and bucket lifecycle protection reduces the risk of orphaned files surviving application failures.
- **Consequences:**
  - Source, intermediate, and result objects share the original absolute expiry and retries never extend it.
  - Cleanup must be idempotent, observable without logging content or sensitive identifiers, and recoverable after restarts.
  - Lifecycle configuration must be verified against the promised retention instead of being treated as the primary timer.

## DEC-167 — Isolate processing-engine failures by tool

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** A failed or unhealthy processing engine disables only the affected tool or processing path; healthy tools and engines remain available.
- **Rationale:** Independent failure domains improve availability and provide users with more accurate service status.
- **Consequences:**
  - Per-tool readiness must influence admission before accepting work that cannot currently run.
  - The public status experience and tool UI may expose general per-tool availability without infrastructure details.
  - Jobs must not be accepted into an unbounded wait for a known-unavailable engine.

## DEC-168 — Put processing and retention disclosure on the Privacy page

- **Date:** 2026-07-31
- **Status:** Accepted; supersedes the pre-processing disclosure requirement in DEC-011 and DEC-030
- **Decision:** The uploader does not carry a dedicated local-versus-server processing or retention disclosure. Full processing-path and temporary-retention information is provided on the localized Privacy page.
- **Rationale:** The owner prefers to keep the primary tool interface minimal and place detailed privacy explanations in the dedicated legal surface.
- **Consequences:**
  - The Privacy page must clearly and accurately explain browser processing, automatic server fallback, R2 storage, providers, and the absolute one-hour maximum retention.
  - Actual workflow states such as uploading, queued, and server processing must still be labeled truthfully when they occur; this is operational feedback, not a separate consent prompt.
  - The uploader must provide an accessible path to the Privacy page without adding a long disclosure block.
  - This decision does not remove any legally mandatory notice or consent mechanism if later review determines one is required.

## DEC-169 — Use balanced input validation with hardened container isolation

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-088, DEC-090, DEC-092, and DEC-093
- **Decision:** Apply focused validation that blocks unsupported files and credible security or resource-exhaustion threats without aggressively rejecting ordinary valid documents. Treat Docker as one defense layer, not the sole security boundary.
- **Rationale:** The product should remain usable for normal files while safely processing untrusted PDFs and images through native parsers and converters.
- **Consequences:**
  - Processing services require non-root execution, least privilege, bounded CPU/memory/time/disk, restricted network access, hardened filesystem and capability settings, and maintained engines.
  - Validation must inspect actual file structure and decoded-resource risk rather than trusting extension or MIME alone.
  - Rejections expose only safe general categories and must not reveal exploit or scanner internals.
  - Security controls must be tuned through normal functional/security testing and production observations, not an invented benchmark program.

## DEC-170 — Deliver server results through short-lived R2 signed URLs

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Successful server-processing results are downloaded through short-lived signed R2 URLs rather than being proxied through the VPS API.
- **Rationale:** Direct temporary delivery avoids unnecessary VPS bandwidth and keeps the processing API focused on admission, task state, and authorization of result access.
- **Consequences:**
  - Signed URL expiry must never exceed the artifact's authoritative absolute expiry.
  - URLs must not be written to analytics, application logs, browser persistence, support reports, or public status data.
  - A refreshed signed URL may be issued for the same valid result until the artifact expires, without extending retention.

## DEC-171 — Add maintained malware scanning as a defense layer

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-169
- **Decision:** Add a maintained general malware scanner to server-side input handling alongside format validation, PDF sanitization, resource controls, patched processing engines, and container isolation.
- **Rationale:** Defense in depth reduces reliance on any single parser, sanitizer, or container boundary.
- **Consequences:**
  - Scanner results are one security signal and must not support a claim that accepted or produced files are malware-free.
  - Scanner failure, update health, resource consumption, and safe rejection behavior must be operationally monitored.
  - User-facing rejection messages expose only safe general categories.

## DEC-172 — Use a dedicated SSH user with passwordless sudo for authorized administration

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-160
- **Decision:** VPS access uses the owner's dedicated non-root SSH user, while authorized configuration and deployment work may elevate through `sudo NOPASSWD` rather than logging in directly as root.
- **Rationale:** The owner requires root-capable automated administration through the normal user account without interactive password prompts.
- **Consequences:**
  - Direct root SSH login remains disabled and key-based authentication remains required.
  - The sudo policy should be as narrow and auditable as practical for the documented deployment and administration procedures.
  - Possession of the deployment user's key is effectively high privilege and requires strong secret handling, rotation, and revocation procedures.
  - This decision does not authorize current VPS access or configuration changes.

## DEC-173 — Back up the complete recoverable VPS state to S3

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-095 and DEC-097
- **Decision:** Back up the complete VPS state required for operational recovery to the approved S3-compatible backup destination. Papyr's user files remain temporary R2 objects rather than durable VPS application data.
- **Rationale:** A full operational backup supports VPS recovery while preserving the architecture in which the backend processes files but does not retain them as permanent local records.
- **Consequences:**
  - Backup scope includes required configuration, deployment state, service data, and recovery material that is appropriate to retain.
  - Ephemeral processing workspaces, uploads, intermediate artifacts, results, passwords, signed URLs, and temporary queue payloads are not recoverable state and must not be captured in backup archives.
  - Backup encryption, credentials, retention, restore procedures, and periodic restore verification must be documented.
  - R2 temporary objects remain governed by their independent absolute one-hour expiry and are not part of the VPS backup set.

## DEC-174 — Persist only minimal task metadata in Redis

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-019 and DEC-162
- **Decision:** Redis may persist the minimum task metadata needed to survive service restarts, including opaque task identity, state, timing, expiry, processing route, and non-sensitive temporary object references.
- **Rationale:** Durable queue and status behavior should not require persisting user document contents or sensitive credentials in Redis.
- **Consequences:**
  - File contents, PDF passwords, signed URLs, original filenames, previews, extracted content, and unnecessary document metadata are prohibited from persisted task records.
  - Redis records expire no later than their applicable task and artifact lifecycle, except strictly sanitized aggregate operational metrics stored separately.
  - Redis persistence files and backup treatment must follow the same data-minimization rules.

## DEC-175 — Retain sanitized operational logs for 30 days

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Retain non-content production operational logs for 30 days.
- **Rationale:** Thirty days provides useful diagnostic and incident history without creating indefinite operational-data retention.
- **Consequences:**
  - Logs must exclude files, filenames, passwords, signed URLs, object keys, previews, extracted content, precise document metadata, and sensitive request payloads.
  - Access control, rotation, deletion, and any provider-side copies must honor the retention policy.
  - Security or legal requirements that materially change this period require explicit review and approval.

## DEC-176 — Manage production secrets through protected VPS environment configuration

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-017 and DEC-160
- **Decision:** Runtime production secrets are installed and rotated through a documented protected VPS environment-configuration procedure rather than committed to the repository or delivered wholesale by automatic CI deployment.
- **Rationale:** Manual production control matches the approved deployment model and limits secret exposure to the runtime host and authorized administration path.
- **Consequences:**
  - Environment files require restrictive ownership and permissions and must be excluded from source control, images, backups where inappropriate, logs, and audit outputs.
  - The rebuild requires rotation of legacy credentials and investigation of possible historical exposure before production use.
  - Documentation must identify secret owners, rotation and revocation steps, and safe recovery without recording secret values.

## DEC-177 — Use a core automated production deployment gate

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Before an authorized manual production deployment, the mandatory automated core gate consists of linting, unit tests, integration tests, production build verification, and security scanning.
- **Rationale:** These checks provide a consistent baseline for every deployment without forcing unrelated browser and accessibility suites to block backend-only operational changes.
- **Consequences:**
  - Relevant E2E, accessibility, and preview smoke verification remain mandatory for initial relaunch readiness and for changes that affect their surfaces.
  - A failing core gate blocks deployment unless the owner explicitly reviews and approves an exceptional response; failures must not be silently bypassed.
  - Post-deployment production smoke checks remain required under DEC-160.

## DEC-178 — Roll back backend releases using the previous healthy image

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Normal backend rollback uses the previously verified healthy container image and matching deployment configuration through Docker Compose.
- **Rationale:** Reusing a known artifact is faster and more deterministic than rebuilding an old commit or restoring the entire VPS during an application-release incident.
- **Consequences:**
  - Release artifacts and configuration compatibility must be traceable and retained for the defined rollback window.
  - Deployment procedures must verify health after rollback and distinguish application rollback from disaster recovery.
  - Full S3 restore remains a disaster-recovery mechanism, not the ordinary release rollback path.

## DEC-179 — Review dependencies monthly and address critical security updates promptly

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Conduct a routine dependency review once per month, while evaluating and applying critical security fixes promptly rather than waiting for the monthly cycle.
- **Rationale:** This balances maintenance stability with timely response to material vulnerabilities in exposed frameworks and native document-processing engines.
- **Consequences:**
  - Updates require relevant tests and compatibility review before production deployment.
  - Native processors, container base images, frontend/backend packages, GitHub Actions, and malware signatures are all within maintenance scope.
  - Automated alerts may open work, but production changes still follow the approved manual deployment gate.

## DEC-180 — Send operational incident alerts through Telegram

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Telegram is the operational incident-alert channel for Papyr.
- **Rationale:** It preserves the existing fast notification workflow and provides one clear owner-facing alert destination.
- **Consequences:**
  - Alerts must be actionable, deduplicated, severity-aware, and must not contain user files, filenames, passwords, signed URLs, object keys, or sensitive payloads.
  - Telegram delivery failure must be visible within monitoring even though no second notification channel is required at launch.
  - Bot credentials follow the production secret-management policy.

## DEC-181 — Verify S3 backups through an isolated monthly restore

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-173
- **Decision:** Perform an isolated restore verification of the S3-backed VPS recovery set once per month.
- **Rationale:** A backup is only dependable when restoration is exercised rather than inferred from successful upload logs.
- **Consequences:**
  - Restore verification must not affect production or introduce user temporary files into retained test environments.
  - Results, duration, failures, and remediation are recorded without exposing credentials or sensitive configuration values.
  - Repeated restore failures trigger an operational alert and corrective work.

## DEC-182 — Retain Netdata plus external uptime monitoring

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-017 and DEC-161
- **Decision:** Monitor Papyr through Netdata for VPS and service resource health plus independent external uptime checks for public availability.
- **Rationale:** Internal resource visibility and outside-in availability checks cover different failure modes and preserve the strongest parts of the existing operational model.
- **Consequences:**
  - Monitoring covers API, queue, workers, Redis, processing engines, storage integration, cleanup health, and relevant public endpoints without collecting document contents.
  - External checks feed the automated public status experience using noise-resistant health logic.
  - Alert routing uses Telegram under DEC-180.

## DEC-183 — Approve the complete high-level rebuild design

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner approves the complete high-level Papyr rebuild design covering Product and UX, technical architecture, security and data flow, testing, deployment, and operations as established through DEC-001–182.
- **Rationale:** Discovery has resolved the material product, interface, platform, privacy, security, and operating-model choices required to produce written design specifications.
- **Consequences:**
  - The approved decisions may now be consolidated into formal design specifications.
  - Approval authorizes documentation only; it does not authorize product implementation, infrastructure modification, VPS access, or production deployment.
  - Material contradictions discovered during specification writing must be surfaced for owner review rather than silently resolved.

## DEC-184 — Write canonical rebuild design specifications in English

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** English is the canonical language for the rebuild's product and technical design specifications.
- **Rationale:** English provides a consistent technical documentation baseline while the public product remains localized in EN, ES, and ID.
- **Consequences:**
  - Public-facing content and localized product requirements remain trilingual where already approved.
  - Historical Indonesian documentation remains historical source material and is not silently treated as current canonical specification.

## DEC-185 — Separate Product and UX design from Technical Architecture

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Produce two coordinated canonical design documents: one Product and UX Design Specification and one Technical Architecture Specification.
- **Rationale:** Separate documents keep user experience and system design focused, reviewable, and maintainable while sharing the same approved decision baseline.
- **Consequences:**
  - Each document must define its scope and cross-reference the other where responsibilities meet.
  - Requirements must not be duplicated inconsistently across the two specifications.
  - Implementation planning begins only after owner review and approval of both written specifications and completion of the required research/reconciliation gates.

## DEC-186 — PDF-to-JPG page selection preserves duplicates and requested order

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** PDF-to-JPG page selection preserves repeated and overlapping page selections as independent outputs in the order the user requested, matching the Split semantics of DEC-077 and DEC-078. Output files, the ZIP archive, the manifest, and output names must disambiguate every duplicate page selection so each result is identifiable.
- **Rationale:** The owner confirmed that PDF-to-JPG page selection follows the same duplicate-preserving, order-preserving semantics as Split rather than the legacy parser's sort-and-deduplicate behavior.
- **Consequences:**
  - Range syntax and validation follow DEC-038; repeated and overlapping selections are never merged, deduplicated, or silently rewritten.
  - The preview makes duplicated page membership and the effective output sequence visible before processing (DEC-077, DEC-078).
  - ZIP ordering, individual-download listing, manifest entries, and output names follow the user-entered order and uniquely identify each output.

## DEC-187 — JPG-to-PDF officially accepts JPG, JPEG, PNG, and WebP at launch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The JPG-to-PDF tool officially accepts JPG/JPEG, PNG, and WebP image inputs at launch. The user-facing tool name remains "JPG to PDF". Inputs are validated by actual bytes (magic bytes and structure), dimensions, pixel count, frame count where applicable, orientation data, decode expansion, and resource limits per DEC-093.
- **Rationale:** The owner confirmed the legacy baseline behavior, which accepts PNG and WebP alongside JPG, as an explicit launch requirement rather than undocumented drift.
- **Consequences:**
  - Non-JPG input support is an explicit, documented product decision.
  - DEC-093 safety controls and DEC-088 threat blocking apply to every accepted format.
  - The interface, constraint copy, FAQ copy governance, and legal and Privacy disclosures must state the actual accepted formats without implying that the tool is renamed or broadened beyond its stated purpose.
  - The output remains one PDF under the automatic fitting policy of DEC-041 and DEC-082.

---

## Open decisions

The discovery-era topics previously listed here (primary user segments, MVP tool set, processing boundaries, storage policy, limits and abuse prevention, privacy and advertising, brand and naming, SEO strategy, infrastructure and operations, analytics and launch criteria, and the Guinevere/OpenClaw disposition) have been resolved through DEC-001 through DEC-196. This section is a status list, not decision history; DEC-188 through DEC-196 are appended after it in the log, and the scope they resolved is recorded in the two design specifications (Product and UX Design Specification Section 21; Technical Architecture Specification Section 25.3). The genuinely unresolved or research-gated details that remain are listed below, each with its governing decisions and its canonical home in the two design specifications (Product and UX Design Specification Section 21; Technical Architecture Specification Section 25.3):

1. Exact per-tool server limits and browser-limit adjustments after anonymous reliability telemetry and real-device testing (DEC-015, DEC-034, DEC-066; UX spec §21.1, architecture spec §25.3.2).
2. Compress license validation and the premium-screen profile thresholds. Engine selection is resolved: the official unmodified open-source Ghostscript executable runs as a separate hardened server-side subprocess (DEC-014, DEC-059, DEC-195; architecture spec §25.3.1 and §25.3.6).
3. `gpt5.6-sol` remaining provider capability documentation before technical design finalization: request and response schema deviations, structured-output and tool-use behavior, effective context, data retention, availability, and applicable safety/compliance policy. The base URL, exact gateway-facing model identifier, and authentication scheme are resolved (DEC-051, DEC-193, DEC-196; UX spec §21.21, architecture spec §25.3.21).
4. Paper-standard mapping implementation detail: which trusted headers carry the coarse edge country code and how spoofed or untrusted values are rejected. The region rule is resolved: Letter only for trusted US/CA edge codes, every other code selects A4, locale never decides (DEC-083, DEC-085, DEC-089, DEC-191; UX spec §21.3, architecture spec §25.3.7 and Section 5.3).
5. Tool slugs, the legacy URL redirect map, and the full legacy URL disposition audit (DEC-023, DEC-122, DEC-127; UX spec §21.4, architecture spec §25.3.15-16).
6. Launch blog topics and the post-launch topic pipeline (DEC-052, DEC-053, DEC-124; UX spec §21.5).
7. Indonesian coverage extent at relaunch (DEC-115, DEC-118, DEC-103; UX spec §21.6).
8. Contact form provider, anti-spam approach, and delivery monitoring (DEC-046, DEC-050; UX spec §21.7, architecture spec §25.3.14).
9. Status page implementation details and health-signal composition (DEC-116, DEC-119, DEC-161; UX spec §21.8, architecture spec §25.3.11).
10. Adsterra script, cookie, identifier, and regional behavior review against current terms and applicable law. The prior-consent position is reaffirmed: approved light banner/native advertising loads without prior consent in all launch regions as an accepted risk (DEC-022, DEC-045, DEC-190; UX spec §21.9, architecture spec §25.3.12).
11. Legal review of Privacy, Terms, and Cookies/Advertising copy before launch (DEC-045; UX spec §21.10, architecture spec §25.3.13).
12. Per-worker memory and time bounds, fair-scheduling parameters, Redis persistence mode, malware scanner selection, rate-limit and fair-use thresholds, monitoring and alert thresholds, and backup configuration. Worker count is resolved: one active PDF-processing worker with one job at a time at launch (DEC-019, DEC-020, DEC-035, DEC-137, DEC-171, DEC-173, DEC-174, DEC-180, DEC-181, DEC-182, DEC-189; architecture spec §25.3.3-5, §25.3.8-10, §25.3.20).
13. Browser capability detection and the exact routing thresholds that trigger server fallback (DEC-015, DEC-030, DEC-065; architecture spec §25.3.17).
14. Post-launch sequence for restoring legacy tools (DEC-094; architecture spec §25.3.18).
15. Baseline verification and owner-confirmation items: navbar width intent (D3), duplicate CTA intent (U3), homepage entrance animations (U5), the Merge error-state edge case, privacy copy re-scoping, FAQ copy accuracy, rendered visual verification, contrast re-verification, and `@theme inline` token emission (UX spec §21.11-19).

These items remain research-gated under DEC-054 through DEC-057 and DEC-060. None is an accepted product decision, and none authorizes implementation.

## DEC-188 — Approve the written Product and UX and Technical Architecture specifications

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner approves `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` and `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` as the canonical written design specifications for the Papyr rebuild.
- **Rationale:** Both documents were written from the accepted decision baseline, cross-reviewed, corrected, verified, and explicitly approved by the owner.
- **Consequences:**
  - The specifications may now govern the required structured research briefs and cross-domain reconciliation.
  - This approval does not authorize product implementation, VPS access, infrastructure changes, deployment, or production operations.
  - Implementation planning remains blocked until the research and reconciliation requirements in DEC-054 through DEC-060 are completed and reviewed.

## DEC-189 — Launch server processing with one active worker

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The initial production backend runs one active PDF-processing worker with one job at a time. Queueing, fairness, timeouts, and safety caps remain in force. Additional worker concurrency requires later capacity evidence and explicit approval.
- **Rationale:** The researched memory envelope shows that two 2 GiB workers, ClamAV, FastAPI, Redis, Nginx, Netdata, and the host operating system may exceed the existing VPS capacity. The owner chose the safer initial operating posture: “1 worker aja dulu.”
- **Consequences:**
  - Stability and security margin take priority over throughput at relaunch.
  - Valid jobs may wait in the bounded fair queue when the worker is busy.
  - Worker limits, scanner settings, and other service memory budgets must be designed around one concurrent processing job.
  - Scaling follows DEC-098 and requires production observability plus explicit approval; no benchmark program is introduced.

## DEC-190 — Retain the accepted no-prior-consent advertising risk

- **Date:** 2026-07-31
- **Status:** Accepted risk reaffirmed
- **Decision:** The owner reaffirms DEC-022: approved light Adsterra banner/native advertising may be shown in all launch regions without introducing prior-consent gating solely as a result of the current research findings.
- **Rationale:** After being presented with the research finding that EEA, UK, and Switzerland may require prior consent for tracking-based advertising, the owner explicitly selected “Terima risiko lama.”
- **Consequences:**
  - This remains an accepted business/legal risk, not a compliance claim.
  - Papyr must not state that the approach is GDPR, PECR, ePrivacy, UK GDPR, or Swiss FADP compliant without qualified review.
  - Current Adsterra publisher terms, exact ad-unit scripts, cookies, identifiers, and recipients still require review before launch.
  - If binding terms, qualified legal review, or applicable law determines prior consent is mandatory, Papyr must implement consent controls, use demonstrably contextual non-tracking ads, or suppress ads in affected regions as already required by DEC-022.
  - Critical product functionality and legal/support/status content must remain available if ad scripts are blocked or disabled.

## DEC-191 — Use edge country with Letter limited to the United States and Canada

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** JPG-to-PDF selects Letter only when the trusted coarse edge country code is the United States or Canada. Every other country, missing code, or invalid code selects A4. The active content locale does not independently select paper size.
- **Rationale:** The owner accepted the research recommendation to preserve the simple US/Canada rule rather than extending Letter to every country recorded by CLDR as de facto Letter-using.
- **Consequences:**
  - DEC-085 and DEC-089 are the operative mechanism and fallback; this decision resolves the ambiguity in DEC-083.
  - Country code remains ephemeral and is not persisted as a profile or sent to analytics.
  - The UI may disclose the automatically selected paper size but does not expose manual controls in the MVP.

## DEC-192 — Route active-content Merge and Split inputs to server sanitization

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** When browser inspection detects PDF JavaScript, embedded attachments, launch actions, or other active content in a Merge or Split input, the job is routed to the temporary server path for sanitization. Papyr does not build a separate browser sanitization engine for the MVP.
- **Rationale:** The owner accepted the safer and simpler researched approach. Browser-only page copying cannot guarantee the sanitization required by DEC-090 and DEC-093.
- **Consequences:**
  - The initial processing disclosure and live stages must truthfully show that server processing may occur.
  - The server removes or neutralizes active content according to DEC-090 before returning output.
  - If the maintained malware-scanner or sanitization path is unavailable, affected jobs fail closed rather than bypassing the control.
  - Ordinary safe files may still use the browser path within DEC-015 limits.
  - No malware-free guarantee may be claimed.

## DEC-193 — Use the owner’s OpenAI-compatible gateway for `gpt5.6-sol`

- **Date:** 2026-07-31
- **Status:** Accepted with contract details pending
- **Decision:** Blog automation integrates `gpt5.6-sol` through the owner’s OpenAI-compatible gateway at `https://router.budgezen.com/v1`. The gateway is accessed only from server-side or protected automation environments.
- **Rationale:** The owner identified the previously unresolved access path as an OpenAI-compatible gateway and supplied its base URL.
- **Consequences:**
  - The provider adapter must isolate the gateway-specific configuration from the blog pipeline.
  - Authentication credentials must never enter client code, repository content, logs, generated articles, or analytics.
  - Before technical design is final, the remaining contract fields still require documentation: exact model identifier, authentication scheme, request and response schema deviations, structured-output and tool-use behavior, rate limits, billed cost, effective context, retry semantics, data retention, availability, and applicable safety/compliance policies.
  - No authenticated call, account operation, or remote mutation is authorized by this decision.

## DEC-194 — Return deferred legacy tool URLs as 410 Gone by default

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** At relaunch, legacy URLs for tools not included in the five-tool MVP return an intentional localized 410 Gone response by default. A specific URL may instead receive a targeted relevant redirect only when credible traffic or intent evidence justifies it.
- **Rationale:** The owner accepted the research recommendation rather than redirecting unrelated URLs to the homepage or maintaining out-of-scope coming-soon pages.
- **Consequences:**
  - The URL disposition inventory must identify every deferred tool URL and its localized variants.
  - Sitemap, navigation, canonical links, and internal links must exclude 410 URLs.
  - The 410 experience should explain that the tool is unavailable and link to relevant live tools without pretending the old capability still exists.
  - Meaningful legacy traffic evidence may supersede a specific disposition through a later explicit decision consistent with DEC-114 and DEC-127.

## DEC-195 — Use unmodified Ghostscript as a separate Compress executable

- **Date:** 2026-07-31
- **Status:** Accepted with license validation required
- **Decision:** Compress PDF uses the official unmodified open-source Ghostscript executable as a separate server-side subprocess, following the existing Papyr integration boundary. Papyr does not modify, link into, or embed Ghostscript source into proprietary application code.
- **Rationale:** The owner wants the free open-source processing tool already used by the existing Papyr implementation. The separate-process boundary avoids unnecessarily replacing the stronger compression engine while keeping proprietary Papyr code distinct.
- **Consequences:**
  - Ghostscript must be obtained from an authoritative distribution, version-pinned, hardened, and invoked with appropriate safety flags including `-dSAFER`.
  - Papyr must preserve applicable Ghostscript copyright and AGPL notices and make the corresponding unmodified Ghostscript source available as required.
  - Papyr must not claim that using an unmodified subprocess eliminates every licensing obligation; the exact production distribution and integration model requires a focused license review before public launch.
  - Any future Ghostscript modification, linking, embedding, or architectural integration requires renewed license review and owner approval.
  - If review determines the chosen production model requires disclosure the owner does not accept, Compress must move to a permissive engine path or a commercial Ghostscript license before launch.

## DEC-196 — Fix the custom gateway request identity and authentication

- **Date:** 2026-07-31
- **Status:** Accepted with remaining capability details pending
- **Decision:** Requests to the owner-managed OpenAI-compatible gateway use base URL `https://router.budgezen.com/v1`, exact JSON model identifier `mypapyr`, and `Authorization: Bearer <API_KEY>` authentication. The API key is stored only in protected server-side or automation secrets.
- **Rationale:** The owner supplied the exact model string and authentication pattern required to remove ambiguity from DEC-193.
- **Consequences:**
  - The internal provider adapter must not substitute the public model name `gpt5.6-sol` into API requests; `mypapyr` is the gateway-facing identifier.
  - No API key may be committed, logged, returned to clients, inserted into generated MDX, or exposed through analytics.
  - The gateway is owner-managed and treated as having no known application-level rate or spending limit.
  - Papyr does not add an internal spending guard at launch, as explicitly selected by the owner.
  - Reliability controls remain mandatory and separate from spending controls: bounded request timeout, finite retry count with backoff, idempotency where supported, one bounded publication workflow, repeated-failure pause, and kill switch per DEC-048 and DEC-053.
  - Structured-output behavior, tool-use behavior, request/response deviations, effective context, retention, availability, and safety policy remain documentation items before the blog automation technical design is finalized.

## DEC-197 — Approve the DEC-189 through DEC-196 specification revisions

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner approves the revised `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` and `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md`, including the incorporation of DEC-189 through DEC-196 and the final cross-domain reconciliation.
- **Rationale:** The revised documents were independently cross-reviewed, received all required deterministic corrections, were verified against the decision log and reconciliation report, and were explicitly approved by the owner.
- **Consequences:**
  - These revisions are the current canonical Product and UX and Technical Architecture specifications for implementation planning.
  - The implementation plan must preserve the unresolved research and contract gates recorded in Product and UX Section 21, Technical Architecture Section 25.3, and the decision log's Open decisions status list.
  - This approval authorizes implementation planning only. It does not authorize product implementation, dependency installation, VPS access, infrastructure changes, deployment, commits, pushes, provider authentication, or remote operations.
  - Product implementation remains blocked until the owner reviews and explicitly approves the implementation plan.

## DEC-198 — Use the workspace root as the rebuild Git repository root

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The rebuild Git repository root is the workspace `<workspace-root>` itself, not a nested `papyr-rebuild/` directory. `papyr-reference/` remains a separate nested read-only legacy clone and is excluded from the rebuild repository. `audit-outputs/`, this decision log, and the canonical specifications and plans are preserved as governed project records unless a later explicit decision changes the tracking policy.
- **Rationale:** The owner selected the existing workspace root as the repository root, keeping the decision log, governed records, and rebuild code in one place while keeping the legacy clone separate and read-only.
- **Consequences:**
  - All plan paths become relative to the workspace root; the previously proposed nested `papyr-rebuild/` directory is superseded.
  - `papyr-reference/` and its nested `.git` are excluded from the rebuild repository and must never be modified or targeted by any repository operation.
  - No `git init`, commit, push, or repository operation is authorized by this decision.
  - The execution Phase 0 repository-initialization step remains owner-gated (plan gate G-1).

## DEC-199 — Approve the engine and queue matrix (R-28)

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner approves the complete R-28 engine and queue matrix exactly as presented: a minimal custom queue over Redis Streams consumer groups; pdf-lib for the Merge/Split browser happy path and browser JPG-to-PDF support; pikepdf (qpdf) for the Merge/Split server fallback and sanitization; img2pdf plus Pillow for the JPG-to-PDF server path; pypdfium2 for the PDF-to-JPG server path; pdf.js for browser rendering and page count; and the platform `createImageBitmap` for WebP decode.
- **Rationale:** The owner accepted the researched selections with their documented trade-offs.
- **Consequences:**
  - Every documented accepted risk, scope boundary, material condition, fallback, dependency and version review, and DEC-057 approval limit recorded in the R-28 matrix remains in force.
  - This is approval of the matrix, not implementation authorization. Product implementation remains blocked until the owner reviews and explicitly approves the implementation plan (DEC-060, DEC-197).
  - The implementation plan's Tech Stack, proposed tree, and task interfaces change from proposal framing to approved selections while keeping the version, license, and fallback checks.
  - Dependency and version verification at implementation time (for example the pdf-lib maintenance review, the pdf.js legacy floor, and the Redis version pin) remains required (DEC-056, DEC-179).

## DEC-200 — Approve the 90-day success measures (partial resolution of R-27)

- **Date:** 2026-07-31
- **Status:** Accepted with remaining open fields
- **Decision:** The owner approves the following 90-day measures as the R-27 disposition: job success rate at or above 98 percent; system failure rate at or below 2 percent; uptime at or above 99.5 percent; Core Web Vitals passing for at least 75 percent of visits; completed downloads at or above 85 percent of successful jobs; organic traffic increasing relative to the first 28 post-launch days, represented as greater than zero percent growth evaluated at day 90 from relaunch; all five tools receiving meaningful usage; and processing and queue latency measured as p50 and p95 per tool without an initial numeric target. The baseline is the first 28 post-launch days and evaluation is at day 90 from relaunch.
- **Rationale:** The owner approved the proposed target set, which intentionally omitted numeric latency targets and a numeric per-tool usage threshold.
- **Consequences:**
  - This partially resolves resolution item R-27 and the DEC-024 gate. DEC-024 requires exact numeric targets and baseline measurement windows before implementation planning is approved; the baseline windows and most targets are now exact, but two fields remain without exact numeric values: latency targets and the per-tool meaningful-usage threshold.
  - The implementation plan remains unapproved, and the plan-approval gate stays blocked on those two fields until the owner supplies them.
  - No latency target or per-tool usage threshold value is invented by this decision or by the implementation plan.

## DEC-201 — Supply the final R-27 numeric targets (complete resolution of R-27)

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner supplies the exact numeric fields DEC-200 left open, completing the R-27 target set: p95 queue wait at or below 60 seconds per tool; p95 server processing at or below 180 seconds per tool; p50 latency remains observed and reported per tool without a separate numeric target; and each of the five launch tools contributes at or above 5 percent of total completed downloads during days 29 through 90 of the 90-day evaluation period. The baseline remains the first 28 post-launch days and evaluation is at day 90 from relaunch (DEC-200).
- **Rationale:** Every DEC-024 success field now has an exact numeric value with its baseline and evaluation window recorded, so no field remains open for the implementation plan to invent.
- **Consequences:**
  - This completes the numeric fields left open by DEC-200 and fully resolves resolution item R-27 and the DEC-024 exact-numeric-target precondition for implementation planning.
  - The implementation plan records R-27 as resolved, and the DEC-024 plan-approval precondition is fully met; the plan itself still awaits explicit owner approval.
  - This decision does not approve the implementation plan. The plan remains pending explicit owner approval, and no phase may start before that approval (DEC-060, DEC-197).

## DEC-202 — Approve the Papyr rebuild master implementation plan

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner explicitly approves `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md`, synchronized through DEC-201 and independently reviewed with a PASS verdict.
- **Rationale:** The plan now incorporates the approved specifications, completed structured research and reconciliation, resolved R-01/R-27/R-28 decisions, complete DEC-001 through DEC-201 traceability, TDD-oriented tasks, phase gates, and verified implementation boundaries.
- **Consequences:**
  - Product implementation may begin and must follow the approved plan, its phase ordering, stop conditions, resolution register, tests, review gates, and global constraints.
  - This approval does not authorize VPS or SSH access, deployment, provider authentication, production changes, commits, pushes, or other remote operations. Those actions remain separately gated and require explicit owner authorization where specified.
  - `papyr-reference/` remains a read-only legacy reference and must not be modified.
  - Material scope, architecture, risk, or dependency changes require renewed owner approval before implementation proceeds beyond the affected gate.

