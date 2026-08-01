# Track B — Decision Log Evidence (Extraction)

## Provenance

- **Source document:** `<workspace-root>\papyr-rebuild-decisions.md` (READ-ONLY; unmodified)
- **Source length:** 2230 lines total, DEC-001 through DEC-188 plus an `## Open decisions` section
- **Extraction date:** 2026-07-31
- **Extractor:** Track B explore agent (browser routing, accessibility, i18n/paper policy, SEO/URL migration, UI baseline)
- **Extraction standard:** Exact verbatim quotes with source line ranges; no editorializing. Annotations added by the extractor are marked as such. Every verbatim block is reproduced inside a `markdown` code fence to preserve exact text.
- **Source document header:** Title `# Papyr Rebuild Decision Log` (line 1); `## Purpose` (lines 3–5); `## Status definitions` (lines 7–12). The document carries no separate version/date header; every decision DEC-001 through DEC-188 is dated `2026-07-31`. Statuses present: `Accepted`, `Accepted risk` (DEC-022, DEC-084, DEC-130), `Superseded by DEC-066` (DEC-061), `Superseded and broadened by DEC-066` (DEC-063), `Superseded by DEC-090` (DEC-086, DEC-087). Many `Accepted` decisions carry a `; refines/expands/supersedes/reinforces/clarifies/confirms DEC-xxx` suffix, preserved verbatim below.

## 1. Decision map — DEC-001 through DEC-188

One-line summary of every decision (decision ID, short title/topic from the document header, and the exact `Status` value). Line ranges for the full text of each decision are in Section 5.

| DEC | Short title / topic | Status (exact) |
| --- | --- | --- |
| DEC-001 | Rebuild instead of restoring the inactive deployment | Accepted |
| DEC-002 | Papyr remains a modern PDF-tools product | Accepted |
| DEC-003 | Target international markets | Accepted |
| DEC-004 | Launch in English and Spanish, then localize incrementally | Accepted |
| DEC-005 | Free tools monetized through Adsterra | Accepted |
| DEC-006 | Maintain one local decision log during discovery | Accepted |
| DEC-007 | Prioritize fast, task-oriented general users | Accepted |
| DEC-008 | Make speed and simplicity the primary product promise | Accepted |
| DEC-009 | Launch with five core PDF tools | Accepted |
| DEC-010 | Define the five-tool MVP catalog | Accepted |
| DEC-011 | Use hybrid, browser-first file processing | Accepted |
| DEC-012 | No user accounts in the MVP | Accepted |
| DEC-013 | Delete server-processed files within one hour | Accepted |
| DEC-014 | Compress automatically for premium screen quality | Accepted |
| DEC-015 | Start with conservative browser-processing limits | Accepted |
| DEC-016 | Remove Guinevere from the Papyr rebuild | Accepted |
| DEC-017 | Retain the Vercel, VPS, Cloudflare, and R2 production topology | Accepted |
| DEC-018 | Allow only non-intrusive banner and native advertising at launch | Accepted |
| DEC-019 | Use a Redis-backed queue with dedicated processing workers | Accepted |
| DEC-020 | Apply adaptive anonymous fair-use controls | Accepted |
| DEC-021 | Retain the Papyr name and mypapyr.com domain | Accepted |
| DEC-022 | Load advertising without prior consent in all launch regions | Accepted risk |
| DEC-023 | Prefix every localized route with its locale | Accepted |
| DEC-024 | Judge 90-day MVP success by reliability and organic growth | Accepted |
| DEC-025 | Use detailed product analytics without replaying document workflows | Accepted |
| DEC-026 | Create concise canonical documentation and preserve legacy history in an archive | Accepted |
| DEC-027 | Launch all five MVP tools together | Accepted |
| DEC-028 | Evolve the legacy visual design rather than replacing it | Accepted |
| DEC-029 | Auto-download successful results and retain a manual download control | Accepted |
| DEC-030 | Automatically route unsupported browser jobs to the server | Accepted |
| DEC-031 | Support the latest two major versions of mainstream browsers | Accepted |
| DEC-032 | Retain local results only for the active browser tab session | Accepted |
| DEC-033 | Show real processing stages and honest estimates | Accepted |
| DEC-034 | Define server input limits separately for each tool | Accepted |
| DEC-035 | Keep valid server jobs queued during normal capacity pressure | Accepted |
| DEC-036 | Request PDF passwords only when encryption is detected | Accepted |
| DEC-037 | Provide multi-file results as both ZIP and individual downloads | Accepted |
| DEC-038 | Support range-based and per-page Split PDF modes | Accepted |
| DEC-039 | Use automatic high-quality PDF-to-JPG output | Accepted |
| DEC-040 | Keep Merge PDF controls at the file level | Accepted |
| DEC-041 | Automatically fit each image to an appropriate PDF page | Accepted |
| DEC-042 | Derive output names from source names with safe localized suffixes | Accepted |
| DEC-043 | Preserve the legacy directory-style homepage structure | Accepted |
| DEC-044 | Combine concise tool-page SEO content with a supporting blog | Accepted |
| DEC-045 | Publish Privacy, Terms, and Cookies/Advertising pages at launch | Accepted |
| DEC-046 | Provide support through email and a contact form | Accepted |
| DEC-047 | Detect browser language for locale-less entry and remember manual choice | Accepted |
| DEC-048 | Fully automate LLM-assisted blog generation and publishing | Accepted |
| DEC-049 | Store blog content as version-controlled MDX in the repository | Accepted |
| DEC-050 | Make the project owner responsible for launch support | Accepted |
| DEC-051 | Use the owner's custom `gpt5.6-sol` provider for blog automation | Accepted |
| DEC-052 | Launch the blog with five topics localized into two languages | Accepted |
| DEC-053 | Publish one new localized blog topic per day after launch | Accepted |
| DEC-054 | Require deep research before approving every new feature | Accepted |
| DEC-055 | Require a structured research brief for each new feature | Accepted |
| DEC-056 | Prioritize primary sources and verify decisions in practice | Accepted |
| DEC-057 | Require owner approval for every researched feature | Accepted |
| DEC-058 | Run MVP research in parallel domain tracks | Accepted |
| DEC-059 | Re-research all five legacy tools from first principles | Accepted |
| DEC-060 | Block rebuild coding until MVP research and design are approved | Accepted |
| DEC-061 | Use a curated mixed corpus for five-tool benchmarking | Superseded by DEC-066 |
| DEC-062 | Target WCAG 2.2 Level AA across the public product | Accepted |
| DEC-063 | Do not benchmark on VPS `<vps-ip>` | Superseded and broadened by DEC-066 |
| DEC-064 | Support password-protected PDF input across applicable MVP tools | Accepted |
| DEC-065 | Automatically fall back to server processing after safe browser failure | Accepted |
| DEC-066 | Do not create or require a benchmark program for the rebuild | Accepted; supersedes benchmark requirements introduced in DEC-014, DEC-034, DEC-039, DEC-054 through DEC-056, DEC-059 through DEC-061, and DEC-063 where they conflict |
| DEC-067 | Enforce server-result expiry after one hour even while the tab remains open | Accepted |
| DEC-068 | Keep the manual Download button as the auto-download fallback | Accepted |
| DEC-069 | Allow server-job cancellation only while queued | Accepted |
| DEC-070 | Start the one-hour server-retention clock when upload is received | Accepted |
| DEC-071 | Continue accepted server jobs after the browser tab closes | Accepted |
| DEC-072 | Recover active server jobs after refresh only within the same tab session | Accepted |
| DEC-073 | Do not implement deadline-prediction admission control | Accepted |
| DEC-074 | Collect a separate password for each locked Merge input | Accepted |
| DEC-075 | Retain downloaded server results until their normal expiry | Accepted |
| DEC-076 | Fail the complete Merge job when any source is invalid | Accepted |
| DEC-077 | Allow overlapping Split ranges as independent outputs | Accepted |
| DEC-078 | Preserve user-entered order for Split outputs | Accepted |
| DEC-079 | Preserve Merge document features as safely as supported | Accepted |
| DEC-080 | Always generate a new Compress output artifact | Accepted; refines DEC-014 |
| DEC-081 | Composite transparent PDF pages onto white for JPG output | Accepted |
| DEC-082 | Select JPG-to-PDF page size and orientation per image | Accepted |
| DEC-083 | Choose JPG-to-PDF paper standards from locale | Accepted |
| DEC-084 | Preserve source metadata including location metadata where supported | Accepted risk |
| DEC-085 | Use coarse edge country codes for automatic paper selection | Accepted |
| DEC-086 | Preserve active PDF content where supported | Superseded by DEC-090 |
| DEC-087 | Require explicit confirmation before processing detected active PDF content | Superseded by DEC-090 |
| DEC-088 | Block files classified as threats to Papyr infrastructure | Accepted |
| DEC-089 | Fall back to A4 when the edge country is unavailable | Accepted |
| DEC-090 | Sanitize detected active content from processed PDF outputs | Accepted; supersedes DEC-086 and DEC-087 |
| DEC-091 | Show general categories of active content removed | Accepted |
| DEC-092 | Inspect PDF-to-JPG inputs for server safety without carrying active content into images | Accepted |
| DEC-093 | Validate and decode JPG-to-PDF image inputs in isolation | Accepted |
| DEC-094 | Return legacy feature groups gradually after the five-tool launch | Accepted |
| DEC-095 | Reuse existing infrastructure assets for the initial relaunch | Accepted |
| DEC-096 | Relaunch directly on the production domain after pre-release verification | Accepted |
| DEC-097 | Keep the owner accountable for operations with AI-assisted automation | Accepted |
| DEC-098 | Optimize the current architecture before vertically scaling the VPS | Accepted |
| DEC-099 | Archive the legacy application without keeping it publicly accessible | Accepted |
| DEC-100 | Target the public relaunch within one month | Accepted |
| DEC-101 | Position Papyr as fast and trustworthy | Accepted |
| DEC-102 | Keep user experience ahead of advertising revenue | Accepted |
| DEC-103 | Delay launch rather than cut readiness or approved scope | Accepted; refines DEC-100 |
| DEC-104 | Launch across all target regions simultaneously | Accepted |
| DEC-105 | Keep Papyr free and advertising-funded during the first year | Accepted |
| DEC-106 | Grow through SEO and the localized blog, then monetize with Adsterra | Accepted |
| DEC-107 | Offer an optional marketing newsletter | Accepted |
| DEC-108 | Focus the first year on individual web users | Accepted |
| DEC-109 | Defer the optional newsletter until after relaunch | Accepted; refines DEC-107 |
| DEC-110 | Present Papyr publicly as a product brand | Accepted |
| DEC-111 | Do not solicit donations or voluntary tips | Accepted |
| DEC-112 | Do not require social media for the relaunch | Accepted |
| DEC-113 | Display publication and update dates on blog articles | Accepted |
| DEC-114 | Preserve and update legacy content that still attracts traffic | Accepted |
| DEC-115 | Retain Indonesian as an additional content locale | Accepted; expands DEC-004 |
| DEC-116 | Provide a simple public service-status page | Accepted |
| DEC-117 | Allow concise result-problem reports without document upload | Accepted |
| DEC-118 | Launch all five tools completely in Indonesian | Accepted; refines DEC-027 and DEC-115 |
| DEC-119 | Host the public status experience on Vercel | Accepted; refines DEC-116 |
| DEC-120 | Allow optional reply email on result-problem reports | Accepted; refines DEC-117 |
| DEC-121 | Launch the initial blog topics in English, Spanish, and Indonesian | Accepted; expands DEC-052 |
| DEC-122 | Use localized Indonesian slugs | Accepted; refines DEC-023 |
| DEC-123 | Publish a simple high-level roadmap | Accepted |
| DEC-124 | Publish each post-launch topic in all three languages together | Accepted; expands DEC-053 |
| DEC-125 | Keep the public roadmap informational only | Accepted; refines DEC-123 |
| DEC-126 | Keep usage totals private and defer them to a future admin dashboard | Accepted |
| DEC-127 | Audit the complete legacy public URL inventory before relaunch | Accepted |
| DEC-128 | Exclude competitor-comparison pages from relaunch | Accepted |
| DEC-129 | Monetize blog pages with light non-intrusive advertising | Accepted |
| DEC-130 | Allow light advertising on legal, support, and status pages | Accepted risk |
| DEC-131 | Keep result-page advertising away from Download controls | Accepted |
| DEC-132 | Publicly commit that Papyr's core tools remain free forever | Accepted |
| DEC-133 | Extend the free-forever promise to all core public tools | Accepted; expands DEC-132 |
| DEC-134 | Use fair queuing when free capacity is constrained | Accepted; reinforces DEC-020 and DEC-035 |
| DEC-135 | Do not plan an alternative monetization model | Accepted |
| DEC-136 | Continue operating without ads when feasible | Accepted |
| DEC-137 | Use fair scheduling that prevents queue monopolization | Accepted; refines DEC-134 |
| DEC-138 | State the free-forever core commitment on the public roadmap | Accepted; refines DEC-123 and DEC-133 |
| DEC-139 | Lead with fast, easy, and free PDF tools | Accepted |
| DEC-140 | Relaunch by activating the rebuilt site without a launch campaign | Accepted |
| DEC-141 | Prioritize stability, then content growth, then the next tool after launch | Accepted |
| DEC-142 | Use an evolved directory-style product experience | Accepted |
| DEC-143 | Preserve the existing Papyr visual language and UX | Accepted; refines DEC-028 and DEC-142 |
| DEC-144 | Retain the existing tool-page sequence | Accepted; refines DEC-142 and DEC-143 |
| DEC-145 | Keep the page shell visible during processing | Accepted |
| DEC-146 | Retain the existing result-card pattern | Accepted; reinforces DEC-029 and DEC-068 |
| DEC-147 | Retain the existing categorized navigation model | Accepted; refines DEC-143 |
| DEC-148 | Present all five launch tools equally on the homepage | Accepted; clarifies DEC-143 |
| DEC-149 | Keep the language selector in the navbar | Accepted |
| DEC-150 | Preserve the existing homepage content depth | Accepted; refines DEC-043 and DEC-143 |
| DEC-151 | Place tool-page advertising after the primary tool experience | Accepted; refines DEC-018, DEC-102, DEC-129, and DEC-131 |
| DEC-152 | Apply the categorized navigation choice to the five-tool launch | Accepted; confirms DEC-147 |
| DEC-153 | Keep processing and results within one tool page | Accepted; refines DEC-142 and DEC-143 |
| DEC-154 | Retain the existing Related Tools section | Accepted; refines DEC-143 |
| DEC-155 | Preserve the existing mobile category accordion | Accepted; refines DEC-147 and DEC-152 |
| DEC-156 | Reset the tool flow with an explicit process-another-file action | Accepted; refines DEC-143 and DEC-153 |
| DEC-157 | Preserve accordion FAQs on tool pages | Accepted; refines DEC-044 and DEC-143 |
| DEC-158 | Preserve inline error cards | Accepted; refines DEC-143 |
| DEC-159 | Keep the rebuild in one monorepo | Accepted |
| DEC-160 | Production backend deployment is manually executed by the agent after approval | Accepted; refines DEC-097 |
| DEC-161 | Public service status is automatically derived | Accepted; refines DEC-116 and DEC-119 |
| DEC-162 | Deploy API, queue, workers, Redis, and Nginx as one Docker Compose stack | Accepted; refines DEC-017 and DEC-019 |
| DEC-163 | Keep tool pages available during backend outages | Accepted |
| DEC-164 | Version the rebuild API under `/api/v1` | Accepted |
| DEC-165 | Publish one machine-readable capability and limits contract | Accepted; refines DEC-034 |
| DEC-166 | Enforce temporary-file deletion through the application with R2 lifecycle as a safety net | Accepted; refines DEC-013, DEC-067, and DEC-070 |
| DEC-167 | Isolate processing-engine failures by tool | Accepted |
| DEC-168 | Put processing and retention disclosure on the Privacy page | Accepted; supersedes the pre-processing disclosure requirement in DEC-011 and DEC-030 |
| DEC-169 | Use balanced input validation with hardened container isolation | Accepted; refines DEC-088, DEC-090, DEC-092, and DEC-093 |
| DEC-170 | Deliver server results through short-lived R2 signed URLs | Accepted |
| DEC-171 | Add maintained malware scanning as a defense layer | Accepted; refines DEC-169 |
| DEC-172 | Use a dedicated SSH user with passwordless sudo for authorized administration | Accepted; refines DEC-160 |
| DEC-173 | Back up the complete recoverable VPS state to S3 | Accepted; refines DEC-095 and DEC-097 |
| DEC-174 | Persist only minimal task metadata in Redis | Accepted; refines DEC-019 and DEC-162 |
| DEC-175 | Retain sanitized operational logs for 30 days | Accepted |
| DEC-176 | Manage production secrets through protected VPS environment configuration | Accepted; refines DEC-017 and DEC-160 |
| DEC-177 | Use a core automated production deployment gate | Accepted |
| DEC-178 | Roll back backend releases using the previous healthy image | Accepted |
| DEC-179 | Review dependencies monthly and address critical security updates promptly | Accepted |
| DEC-180 | Send operational incident alerts through Telegram | Accepted |
| DEC-181 | Verify S3 backups through an isolated monthly restore | Accepted; refines DEC-173 |
| DEC-182 | Retain Netdata plus external uptime monitoring | Accepted; refines DEC-017 and DEC-161 |
| DEC-183 | Approve the complete high-level rebuild design | Accepted |
| DEC-184 | Write canonical rebuild design specifications in English | Accepted |
| DEC-185 | Separate Product and UX design from Technical Architecture | Accepted |
| DEC-186 | PDF-to-JPG page selection preserves duplicates and requested order | Accepted |
| DEC-187 | JPG-to-PDF officially accepts JPG, JPEG, PNG, and WebP at launch | Accepted |
| DEC-188 | Approve the written Product and UX and Technical Architecture specifications | Accepted |

## 2. Track B governing decisions (verbatim)

The following 34 decisions are quoted verbatim from `papyr-rebuild-decisions.md` (annotations `Source: lines N–M` are extractor metadata; the fenced text is the exact source text including the decision header line).

### DEC-001 (Source: lines 16–25)

```markdown
## DEC-001 — Rebuild instead of restoring the inactive deployment

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Rebuild Papyr rather than restoring the inactive website and preserving the existing system as-is.
- **Rationale:** The existing website is no longer active, while the repository contains production coupling, stale documentation, and unfinished scope that should not automatically carry into the new product.
- **Consequences:**
  - The old repository is a source of requirements and reusable patterns, not the default architecture.
  - Existing features, infrastructure, and documents must each justify their inclusion.
  - Implementation will begin only after discovery, design, and planning are approved.
```

### DEC-015 (Source: lines 185–200)

```markdown
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
```

### DEC-023 (Source: lines 292–302)

```markdown
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
```

### DEC-026 (Source: lines 329–340)

```markdown
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
```

### DEC-030 (Source: lines 378–389)

```markdown
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
```

### DEC-031 (Source: lines 391–401)

```markdown
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
```

### DEC-047 (Source: lines 584–594)

```markdown
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
```

### DEC-054 (Source: lines 668–680)

```markdown
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
```

### DEC-055 (Source: lines 682–692)

```markdown
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
```

### DEC-056 (Source: lines 694–704)

```markdown
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
```

### DEC-057 (Source: lines 706–716)

```markdown
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
```

### DEC-058 (Source: lines 718–728)

```markdown
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
```

### DEC-059 (Source: lines 730–740)

```markdown
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
```

### DEC-060 (Source: lines 742–752)

```markdown
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
```

### DEC-062 (Source: lines 764–774)

```markdown
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
```

### DEC-065 (Source: lines 799–809)

```markdown
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
```

### DEC-066 (Source: lines 811–823)

```markdown
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
```

### DEC-083 (Source: lines 1017–1027)

```markdown
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
```

### DEC-085 (Source: lines 1042–1052)

```markdown
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
```

### DEC-089 (Source: lines 1084–1094)

```markdown
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
```

### DEC-099 (Source: lines 1205–1215)

```markdown
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
```

### DEC-103 (Source: lines 1252–1261)

```markdown
## DEC-103 — Delay launch rather than cut readiness or approved scope

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-100
- **Decision:** If the approved relaunch scope is not production-ready within the one-month target, delay the public launch rather than reducing scope or bypassing quality gates.
- **Rationale:** The owner prioritizes a complete, trustworthy release over meeting the target date at the cost of readiness.
- **Consequences:**
  - One month is a target, not an unconditional deadline.
  - Schedule risk must be reported early and transparently.
  - Any later proposal to reduce launch scope still requires explicit owner approval.
```

### DEC-114 (Source: lines 1374–1384)

```markdown
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
```

### DEC-115 (Source: lines 1386–1395)

```markdown
## DEC-115 — Retain Indonesian as an additional content locale

- **Date:** 2026-07-31
- **Status:** Accepted; expands DEC-004
- **Decision:** Continue serving valuable legacy Indonesian content and support Indonesian as an additional locale alongside the required English and Spanish launch experiences.
- **Rationale:** Existing Indonesian search traffic and useful content should not be abandoned during the international repositioning.
- **Consequences:**
  - English and Spanish remain mandatory launch languages; Indonesian content must be deliberately mapped, updated, and localized rather than left as an inconsistent legacy island.
  - Locale routing, hreflang, canonicals, sitemaps, navigation, and metadata must include Indonesian wherever that version exists.
  - The exact amount of Indonesian tool, legal, support, and blog coverage needed at relaunch must be reconciled with the one-month schedule and DEC-103 without publishing misleading partial experiences.
```

### DEC-118 (Source: lines 1419–1428)

```markdown
## DEC-118 — Launch all five tools completely in Indonesian

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-027 and DEC-115
- **Decision:** The public relaunch requires complete Indonesian versions of all five MVP tools and essential supporting pages alongside English and Spanish.
- **Rationale:** Indonesian is now a first-class launch locale rather than only a legacy-content preservation measure.
- **Consequences:**
  - The launch gate becomes five production-ready tools across EN, ES, and ID.
  - Tool instructions, errors, processing disclosures, results, metadata, navigation, legal/support surfaces, and core accessibility text must be complete and consistent in all three locales.
  - The one-month target remains subordinate to completeness under DEC-103.
```

### DEC-122 (Source: lines 1463–1472)

```markdown
## DEC-122 — Use localized Indonesian slugs

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-023
- **Decision:** Indonesian tool and content URLs use translated, search-appropriate slugs under the `/id/` locale prefix rather than reusing English slugs by default.
- **Rationale:** Localized URLs better match the intended Indonesian search and navigation experience.
- **Consequences:**
  - Slugs must use natural, stable terminology selected during SEO design and avoid awkward literal translation.
  - Legacy Indonesian URLs require an explicit mapping to retained localized URLs, with redirects where paths change.
  - EN and ES retain their own localized slug policies, and all locale alternates must remain connected through hreflang and canonicals.
```

### DEC-127 (Source: lines 1517–1526)

```markdown
## DEC-127 — Audit the complete legacy public URL inventory before relaunch

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Audit the full legacy sitemap and indexable URL inventory before relaunch, not only pages currently known to receive traffic.
- **Rationale:** Thin, duplicate, stale, or conflicting pages can weaken the rebuilt information architecture and carry incorrect content into search results.
- **Consequences:**
  - Every legacy public URL must receive an explicit retain/update, redirect, noindex, or removal disposition.
  - The audit must reconcile locale mappings, canonicals, hreflang, sitemap inclusion, internal links, and the preservation policy in DEC-114.
  - Removal must avoid unnecessary soft 404s and redirect chains; retained pages must meet current content and policy standards.
```

### DEC-143 (Source: lines 1695–1706)

```markdown
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
```

### DEC-183 (Source: lines 2142–2151)

```markdown
## DEC-183 — Approve the complete high-level rebuild design

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner approves the complete high-level Papyr rebuild design covering Product and UX, technical architecture, security and data flow, testing, deployment, and operations as established through DEC-001–182.
- **Rationale:** Discovery has resolved the material product, interface, platform, privacy, security, and operating-model choices required to produce written design specifications.
- **Consequences:**
  - The approved decisions may now be consolidated into formal design specifications.
  - Approval authorizes documentation only; it does not authorize product implementation, infrastructure modification, VPS access, or production deployment.
  - Material contradictions discovered during specification writing must be surfaced for owner review rather than silently resolved.
```

### DEC-184 (Source: lines 2153–2161)

```markdown
## DEC-184 — Write canonical rebuild design specifications in English

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** English is the canonical language for the rebuild's product and technical design specifications.
- **Rationale:** English provides a consistent technical documentation baseline while the public product remains localized in EN, ES, and ID.
- **Consequences:**
  - Public-facing content and localized product requirements remain trilingual where already approved.
  - Historical Indonesian documentation remains historical source material and is not silently treated as current canonical specification.
```

### DEC-185 (Source: lines 2163–2172)

```markdown
## DEC-185 — Separate Product and UX design from Technical Architecture

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Produce two coordinated canonical design documents: one Product and UX Design Specification and one Technical Architecture Specification.
- **Rationale:** Separate documents keep user experience and system design focused, reviewable, and maintainable while sharing the same approved decision baseline.
- **Consequences:**
  - Each document must define its scope and cross-reference the other where responsibilities meet.
  - Requirements must not be duplicated inconsistently across the two specifications.
  - Implementation planning begins only after owner review and approval of both written specifications and completion of the required research/reconciliation gates.
```

### DEC-186 (Source: lines 2174–2183)

```markdown
## DEC-186 — PDF-to-JPG page selection preserves duplicates and requested order

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** PDF-to-JPG page selection preserves repeated and overlapping page selections as independent outputs in the order the user requested, matching the Split semantics of DEC-077 and DEC-078. Output files, the ZIP archive, the manifest, and output names must disambiguate every duplicate page selection so each result is identifiable.
- **Rationale:** The owner confirmed that PDF-to-JPG page selection follows the same duplicate-preserving, order-preserving semantics as Split rather than the legacy parser's sort-and-deduplicate behavior.
- **Consequences:**
  - Range syntax and validation follow DEC-038; repeated and overlapping selections are never merged, deduplicated, or silently rewritten.
  - The preview makes duplicated page membership and the effective output sequence visible before processing (DEC-077, DEC-078).
  - ZIP ordering, individual-download listing, manifest entries, and output names follow the user-entered order and uniquely identify each output.
```

### DEC-187 (Source: lines 2185–2195)

```markdown
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
```

### DEC-188 (Source: lines 2221–2230)

```markdown
## DEC-188 — Approve the written Product and UX and Technical Architecture specifications

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** The owner approves `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` and `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` as the canonical written design specifications for the Papyr rebuild.
- **Rationale:** Both documents were written from the accepted decision baseline, cross-reviewed, corrected, verified, and explicitly approved by the owner.
- **Consequences:**
  - The specifications may now govern the required structured research briefs and cross-domain reconciliation.
  - This approval does not authorize product implementation, VPS access, infrastructure changes, deployment, or production operations.
  - Implementation planning remains blocked until the research and reconciliation requirements in DEC-054 through DEC-060 are completed and reviewed.
```

## 3. Supporting decisions for browser routing and tool behaviors (verbatim)

The task brief enumerated 69 unique supporting-decision IDs (DEC-005 through DEC-182 as listed). All 69 are quoted verbatim below.

### DEC-005 (Source: lines 60–70)

```markdown
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
```

### DEC-013 (Source: lines 158–169)

```markdown
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
```

### DEC-014 (Source: lines 171–183)

```markdown
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
```

### DEC-018 (Source: lines 227–237)

```markdown
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
```

### DEC-019 (Source: lines 239–251)

```markdown
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
```

### DEC-020 (Source: lines 253–265)

```markdown
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
```

### DEC-022 (Source: lines 279–290)

```markdown
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
```

### DEC-025 (Source: lines 316–327)

```markdown
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
```

### DEC-034 (Source: lines 427–437)

```markdown
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
```

### DEC-035 (Source: lines 439–450)

```markdown
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
```

### DEC-036 (Source: lines 452–462)

```markdown
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
```

### DEC-037 (Source: lines 464–474)

```markdown
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
```

### DEC-038 (Source: lines 476–486)

```markdown
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
```

### DEC-039 (Source: lines 488–498)

```markdown
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
```

### DEC-040 (Source: lines 500–510)

```markdown
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
```

### DEC-041 (Source: lines 512–522)

```markdown
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
```

### DEC-045 (Source: lines 560–570)

```markdown
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
```

### DEC-046 (Source: lines 572–582)

```markdown
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
```

### DEC-048 (Source: lines 596–608)

```markdown
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
```

### DEC-049 (Source: lines 610–620)

```markdown
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
```

### DEC-050 (Source: lines 622–631)

```markdown
## DEC-050 — Make the project owner responsible for launch support

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Route launch support email and contact-form submissions to one inbox managed directly by the project owner.
- **Rationale:** Owner-operated support is sufficient for MVP volume and provides direct visibility into user problems without introducing an AI support agent or external helpdesk.
- **Consequences:**
  - The runbook must define inbox routing, priority categories, reusable response templates, escalation for privacy/security reports, spam handling, and continuity if the owner is unavailable.
  - The public site must avoid promising response times that cannot be sustained.
  - Support analytics may use aggregate categories and resolution timing but must not copy private message contents into general product analytics.
```

### DEC-051 (Source: lines 633–643)

```markdown
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
```

### DEC-052 (Source: lines 645–654)

```markdown
## DEC-052 — Launch the blog with five topics localized into two languages

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Public launch will include five priority blog topics, each published as an intentionally localized English and Spanish article, for ten initial article pages.
- **Rationale:** One strong topic associated with each launch tool provides initial informational coverage without delaying the complete five-tool release for a large content inventory.
- **Consequences:**
  - Topic selection must avoid duplicating or cannibalizing the transactional intent of the five tool pages.
  - Both locale versions require the same blocking quality, factual, metadata, link, and MDX validation gates.
  - The ten article pages form part of launch content acceptance, while their indexing or ranking is not a launch prerequisite.
```

### DEC-053 (Source: lines 656–666)

```markdown
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
```

### DEC-064 (Source: lines 787–797)

```markdown
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
```

### DEC-067 (Source: lines 825–835)

```markdown
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
```

### DEC-070 (Source: lines 861–871)

```markdown
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
```

### DEC-074 (Source: lines 909–919)

```markdown
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
```

### DEC-075 (Source: lines 921–931)

```markdown
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
```

### DEC-076 (Source: lines 933–943)

```markdown
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
```

### DEC-077 (Source: lines 945–955)

```markdown
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
```

### DEC-078 (Source: lines 957–967)

```markdown
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
```

### DEC-079 (Source: lines 969–979)

```markdown
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
```

### DEC-080 (Source: lines 981–991)

```markdown
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
```

### DEC-081 (Source: lines 993–1003)

```markdown
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
```

### DEC-082 (Source: lines 1005–1015)

```markdown
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
```

### DEC-084 (Source: lines 1029–1040)

```markdown
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
```

### DEC-088 (Source: lines 1072–1082)

```markdown
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
```

### DEC-090 (Source: lines 1096–1107)

```markdown
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
```

### DEC-091 (Source: lines 1109–1119)

```markdown
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
```

### DEC-092 (Source: lines 1121–1131)

```markdown
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
```

### DEC-093 (Source: lines 1133–1143)

```markdown
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
```

### DEC-094 (Source: lines 1145–1155)

```markdown
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
```

### DEC-097 (Source: lines 1181–1191)

```markdown
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
```

### DEC-104 (Source: lines 1263–1272)

```markdown
## DEC-104 — Launch across all target regions simultaneously

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Relaunch Papyr for the United States, Latin America, and Europe at the same time rather than using a regional rollout.
- **Rationale:** The owner wants the international product available across all selected markets from day one.
- **Consequences:**
  - English and Spanish experiences, regional routing, legal disclosures, advertising behavior, support, and operational readiness must cover all target regions before launch.
  - A regional compliance or provider constraint cannot be ignored; it must be resolved or the affected behavior suppressed while preserving product access where feasible.
  - Monitoring and launch communication must distinguish regions sufficiently to identify material failures without creating prohibited user profiling.
```

### DEC-110 (Source: lines 1330–1339)

```markdown
## DEC-110 — Present Papyr publicly as a product brand

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Public-facing pages communicate under the Papyr brand without requiring a founder profile, personal photograph, or personal origin story.
- **Rationale:** The owner prefers product-led trust rather than personal-brand positioning.
- **Consequences:**
  - Trust must come from clear product behavior, honest claims, accessible support, transparent policies, and reliable operations.
  - Legally required operator or contact information must still be provided where applicable; brand-only presentation is not permission to conceal mandatory disclosures.
  - Blog authorship must not fabricate people or credentials.
```

### DEC-113 (Source: lines 1363–1372)

```markdown
## DEC-113 — Display publication and update dates on blog articles

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Every blog article visibly displays both its original publication date and its latest material update date.
- **Rationale:** Readers and search engines should be able to distinguish original publication from substantive maintenance.
- **Consequences:**
  - Dates must be truthful, locale-formatted, and represented consistently in metadata and structured data.
  - Automated edits must not advance the update date for trivial formatting or deployment-only changes.
  - EN and ES counterparts may have distinct publication/update timestamps when their review or material content differs.
```

### DEC-116 (Source: lines 1397–1406)

```markdown
## DEC-116 — Provide a simple public service-status page

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Papyr will provide a simple public status page showing material service availability and incidents without exposing sensitive infrastructure details.
- **Rationale:** Users need a trustworthy way to distinguish a service incident from a problem with their own file or device.
- **Consequences:**
  - Status communication should cover user-relevant components and use plain EN/ES/ID language where supported.
  - Incident updates must be truthful and timely but omit hostnames, credentials, defensive controls, exploit details, and other sensitive operational information.
  - The status page complements internal monitoring and in-product outage messaging; it does not replace either.
```

### DEC-117 (Source: lines 1408–1417)

```markdown
## DEC-117 — Allow concise result-problem reports without document upload

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Users may report a broken or incorrect result directly from the result experience using a short categorized report that does not upload or attach their source or output document.
- **Rationale:** Result-local feedback provides actionable quality signals while avoiding unnecessary handling of sensitive files.
- **Consequences:**
  - Reports may include the tool, processing path, sanitized error/result category, browser context, and user-entered description, but never filenames, document contents, passwords, signed URLs, or object keys.
  - Submission must be optional, protected from spam, and clearly distinguish product feedback from urgent security or privacy support.
  - The report flow must integrate with the owner-managed support process without promising response times that cannot be maintained.
```

### DEC-119 (Source: lines 1430–1439)

```markdown
## DEC-119 — Host the public status experience on Vercel

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-116
- **Decision:** Serve Papyr's simple public status experience through the Vercel-hosted frontend so it remains independent of a backend VPS outage.
- **Rationale:** Vercel is already part of the approved topology and separates status visibility from the most processing-intensive infrastructure.
- **Consequences:**
  - Status data and health checks must avoid making the page depend solely on the failing VPS to render.
  - A broader Vercel or DNS outage may still affect availability; the page must not claim complete infrastructure independence.
  - Implementation must remain simple and avoid exposing internal operational details.
```

### DEC-120 (Source: lines 1441–1450)

```markdown
## DEC-120 — Allow optional reply email on result-problem reports

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-117
- **Decision:** A user may submit a result-problem report anonymously or optionally provide an email address for follow-up.
- **Rationale:** This preserves low-friction feedback while enabling direct clarification when the user wants a response.
- **Consequences:**
  - The email field must be clearly optional and used only for the submitted support matter, not automatically added to the future newsletter.
  - Reports require minimal retention, access controls, deletion policy, privacy disclosure, and safe operational routing.
  - Even with an email address, Papyr must not request the user to attach sensitive source or result documents through this flow.
```

### DEC-121 (Source: lines 1452–1461)

```markdown
## DEC-121 — Launch the initial blog topics in English, Spanish, and Indonesian

- **Date:** 2026-07-31
- **Status:** Accepted; expands DEC-052
- **Decision:** Each of the five initial blog topics must have intentionally localized English, Spanish, and Indonesian versions, producing 15 launch articles.
- **Rationale:** The owner wants the launch content strategy to support all three first-class product locales.
- **Consequences:**
  - Articles must be localized for language and search intent rather than mechanically translated.
  - Cross-locale metadata, hreflang, canonicals, internal links, and update tracking must cover all three versions.
  - The expanded content requirement remains subject to the complete-launch-over-deadline policy in DEC-103.
```

### DEC-124 (Source: lines 1485–1494)

```markdown
## DEC-124 — Publish each post-launch topic in all three languages together

- **Date:** 2026-07-31
- **Status:** Accepted; expands DEC-053
- **Decision:** The post-launch publishing cadence is at most one new topic per day, with its English, Spanish, and Indonesian versions released as one coordinated set.
- **Rationale:** All first-class locales should receive equivalent new content without becoming permanently delayed translation queues.
- **Consequences:**
  - One daily topic produces three intentionally localized pages; a failed language or quality gate blocks the whole set for that day.
  - Automation must preserve cross-locale linking, metadata, dates, and factual consistency while allowing culturally appropriate wording and search intent.
  - Skipping a day is preferable to publishing an incomplete or low-quality locale set.
```

### DEC-126 (Source: lines 1506–1515)

```markdown
## DEC-126 — Keep usage totals private and defer them to a future admin dashboard

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Do not display public counters such as files processed, users served, or downloads completed; trustworthy aggregate usage metrics may be shown later in a private admin dashboard.
- **Rationale:** Public vanity metrics add little user value and can create misleading claims, while private operational metrics can support product management.
- **Consequences:**
  - Relaunch scope excludes public counters and excludes the unfinished legacy admin-dashboard milestone.
  - Any future admin dashboard requires separate scope, authentication, authorization, privacy, security, and explicit approval.
  - Underlying metrics must follow DEC-025 and must not contain filenames, contents, passwords, object keys, signed URLs, or prohibited identifiers.
```

### DEC-137 (Source: lines 1629–1638)

```markdown
## DEC-137 — Use fair scheduling that prevents queue monopolization

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-134
- **Decision:** Server scheduling should balance waiting time and job complexity while preventing users or unusually heavy jobs from monopolizing capacity; it must not use pure smallest-job-first or unrestricted FIFO as the sole policy.
- **Rationale:** Fairness requires both reasonable progress for ordinary jobs and protection against starvation or resource capture.
- **Consequences:**
  - The approved design must define understandable fairness classes, concurrency bounds, and starvation prevention without exposing exploitable defensive detail.
  - No paid priority lane is permitted.
  - User-facing status should explain delays plainly without promising exact completion times that cannot be known.
```

### DEC-160 (Source: lines 1884–1894)

```markdown
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
```

### DEC-161 (Source: lines 1896–1905)

```markdown
## DEC-161 — Public service status is automatically derived

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-116 and DEC-119
- **Decision:** The public status experience is updated automatically from approved service health signals rather than through owner-authored incident updates.
- **Rationale:** Automated status avoids dependence on manual updates during operational incidents.
- **Consequences:**
  - Status must be hosted independently on Vercel and remain useful when the backend VPS is unavailable.
  - Health signals must be meaningful, resilient to transient noise, and must not expose sensitive infrastructure details.
  - Status wording must distinguish observable service availability from guarantees about every processing engine or user request.
```

### DEC-165 (Source: lines 1940–1949)

```markdown
## DEC-165 — Publish one machine-readable capability and limits contract

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-034
- **Decision:** The versioned backend API is the canonical source for server-processing capabilities and limits. The frontend reads and presents this machine-readable contract rather than maintaining an independent hardcoded copy.
- **Rationale:** One source of truth prevents UI/API drift and lets operational limits change without rebuilding misleading frontend copy.
- **Consequences:**
  - The contract must be cacheable safely, versioned, localized at the presentation layer, and have conservative frontend fallback behavior if unavailable.
  - Backend validation remains authoritative even when the frontend pre-validates inputs.
  - Browser-specific safety limits may remain frontend capability logic but must be clearly distinguished from server limits.
```

### DEC-166 (Source: lines 1951–1960)

```markdown
## DEC-166 — Enforce temporary-file deletion through the application with R2 lifecycle as a safety net

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-013, DEC-067, and DEC-070
- **Decision:** The application actively deletes temporary R2 objects according to each job's absolute one-hour deadline, while an R2 lifecycle rule provides independent backup cleanup.
- **Rationale:** Active deletion provides timely enforcement, and bucket lifecycle protection reduces the risk of orphaned files surviving application failures.
- **Consequences:**
  - Source, intermediate, and result objects share the original absolute expiry and retries never extend it.
  - Cleanup must be idempotent, observable without logging content or sensitive identifiers, and recoverable after restarts.
  - Lifecycle configuration must be verified against the promised retention instead of being treated as the primary timer.
```

### DEC-168 (Source: lines 1973–1983)

```markdown
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
```

### DEC-169 (Source: lines 1985–1995)

```markdown
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
```

### DEC-171 (Source: lines 2008–2017)

```markdown
## DEC-171 — Add maintained malware scanning as a defense layer

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-169
- **Decision:** Add a maintained general malware scanner to server-side input handling alongside format validation, PDF sanitization, resource controls, patched processing engines, and container isolation.
- **Rationale:** Defense in depth reduces reliance on any single parser, sanitizer, or container boundary.
- **Consequences:**
  - Scanner results are one security signal and must not support a claim that accepted or produced files are malware-free.
  - Scanner failure, update health, resource consumption, and safe rejection behavior must be operationally monitored.
  - User-facing rejection messages expose only safe general categories.
```

### DEC-172 (Source: lines 2019–2029)

```markdown
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
```

### DEC-173 (Source: lines 2031–2041)

```markdown
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
```

### DEC-174 (Source: lines 2043–2052)

```markdown
## DEC-174 — Persist only minimal task metadata in Redis

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-019 and DEC-162
- **Decision:** Redis may persist the minimum task metadata needed to survive service restarts, including opaque task identity, state, timing, expiry, processing route, and non-sensitive temporary object references.
- **Rationale:** Durable queue and status behavior should not require persisting user document contents or sensitive credentials in Redis.
- **Consequences:**
  - File contents, PDF passwords, signed URLs, original filenames, previews, extracted content, and unnecessary document metadata are prohibited from persisted task records.
  - Redis records expire no later than their applicable task and artifact lifecycle, except strictly sanitized aggregate operational metrics stored separately.
  - Redis persistence files and backup treatment must follow the same data-minimization rules.
```

### DEC-178 (Source: lines 2087–2096)

```markdown
## DEC-178 — Roll back backend releases using the previous healthy image

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Normal backend rollback uses the previously verified healthy container image and matching deployment configuration through Docker Compose.
- **Rationale:** Reusing a known artifact is faster and more deterministic than rebuilding an old commit or restoring the entire VPS during an application-release incident.
- **Consequences:**
  - Release artifacts and configuration compatibility must be traceable and retained for the defined rollback window.
  - Deployment procedures must verify health after rollback and distinguish application rollback from disaster recovery.
  - Full S3 restore remains a disaster-recovery mechanism, not the ordinary release rollback path.
```

### DEC-180 (Source: lines 2109–2118)

```markdown
## DEC-180 — Send operational incident alerts through Telegram

- **Date:** 2026-07-31
- **Status:** Accepted
- **Decision:** Telegram is the operational incident-alert channel for Papyr.
- **Rationale:** It preserves the existing fast notification workflow and provides one clear owner-facing alert destination.
- **Consequences:**
  - Alerts must be actionable, deduplicated, severity-aware, and must not contain user files, filenames, passwords, signed URLs, object keys, or sensitive payloads.
  - Telegram delivery failure must be visible within monitoring even though no second notification channel is required at launch.
  - Bot credentials follow the production secret-management policy.
```

### DEC-181 (Source: lines 2120–2129)

```markdown
## DEC-181 — Verify S3 backups through an isolated monthly restore

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-173
- **Decision:** Perform an isolated restore verification of the S3-backed VPS recovery set once per month.
- **Rationale:** A backup is only dependable when restoration is exercised rather than inferred from successful upload logs.
- **Consequences:**
  - Restore verification must not affect production or introduce user temporary files into retained test environments.
  - Results, duration, failures, and remediation are recorded without exposing credentials or sensitive configuration values.
  - Repeated restore failures trigger an operational alert and corrective work.
```

### DEC-182 (Source: lines 2131–2140)

```markdown
## DEC-182 — Retain Netdata plus external uptime monitoring

- **Date:** 2026-07-31
- **Status:** Accepted; refines DEC-017 and DEC-161
- **Decision:** Monitor Papyr through Netdata for VPS and service resource health plus independent external uptime checks for public availability.
- **Rationale:** Internal resource visibility and outside-in availability checks cover different failure modes and preserve the strongest parts of the existing operational model.
- **Consequences:**
  - Monitoring covers API, queue, workers, Redis, processing engines, storage integration, cleanup health, and relevant public endpoints without collecting document contents.
  - External checks feed the automated public status experience using noise-resistant health logic.
  - Alert routing uses Telegram under DEC-180.
```

## 4. Open decisions section (verbatim)

The entire `## Open decisions` section of `papyr-rebuild-decisions.md` is reproduced verbatim below (Source: lines 2199–2219). Note the document places this section between DEC-187 (ends line 2195) and DEC-188 (starts line 2221), after a horizontal rule at line 2197.

```markdown
## Open decisions

The discovery-era topics previously listed here (primary user segments, MVP tool set, processing boundaries, storage policy, limits and abuse prevention, privacy and advertising, brand and naming, SEO strategy, infrastructure and operations, analytics and launch criteria, and the Guinevere/OpenClaw disposition) have been resolved through DEC-001 through DEC-187. The genuinely unresolved or research-gated details that remain are listed below, each with its governing decisions and its canonical home in the two design specifications (Product and UX Design Specification Section 21; Technical Architecture Specification Section 25.3):

1. Exact per-tool server limits and browser-limit adjustments after anonymous reliability telemetry and real-device testing (DEC-015, DEC-034, DEC-066; UX spec §21.1, architecture spec §25.3.2).
2. Compress engine selection, license validation, and the premium-screen profile thresholds (DEC-014, DEC-059; architecture spec §25.3.1 and §25.3.6).
3. `gpt5.6-sol` provider documentation before technical design finalization: base URL, authentication, request/response schema, structured-output and tool-use capabilities, rate limits, cost, context limits, retry behavior, data retention, and availability (DEC-051; UX spec §21.21, architecture spec §25.3.21).
4. Paper-standard regional mapping where locale alone does not identify Letter versus A4 (DEC-083, DEC-085, DEC-089; UX spec §21.3, architecture spec §25.3.7).
5. Tool slugs, the legacy URL redirect map, and the full legacy URL disposition audit (DEC-023, DEC-122, DEC-127; UX spec §21.4, architecture spec §25.3.15-16).
6. Launch blog topics and the post-launch topic pipeline (DEC-052, DEC-053, DEC-124; UX spec §21.5).
7. Indonesian coverage extent at relaunch (DEC-115, DEC-118, DEC-103; UX spec §21.6).
8. Contact form provider, anti-spam approach, and delivery monitoring (DEC-046, DEC-050; UX spec §21.7, architecture spec §25.3.14).
9. Status page implementation details and health-signal composition (DEC-116, DEC-119, DEC-161; UX spec §21.8, architecture spec §25.3.11).
10. Adsterra script, cookie, identifier, and regional behavior review against current terms and applicable law, including whether prior consent is required (DEC-022, DEC-045; UX spec §21.9, architecture spec §25.3.12).
11. Legal review of Privacy, Terms, and Cookies/Advertising copy before launch (DEC-045; UX spec §21.10, architecture spec §25.3.13).
12. Worker bounds, fair-scheduling parameters, Redis persistence mode, malware scanner selection, rate-limit and fair-use thresholds, monitoring and alert thresholds, and backup configuration (DEC-019, DEC-020, DEC-035, DEC-137, DEC-171, DEC-173, DEC-174, DEC-180, DEC-181, DEC-182; architecture spec §25.3.3-5, §25.3.8-10, §25.3.20).
13. Browser capability detection and the exact routing thresholds that trigger server fallback (DEC-015, DEC-030, DEC-065; architecture spec §25.3.17).
14. Post-launch sequence for restoring legacy tools (DEC-094; architecture spec §25.3.18).
15. Baseline verification and owner-confirmation items: navbar width intent (D3), duplicate CTA intent (U3), homepage entrance animations (U5), the Merge error-state edge case, privacy copy re-scoping, FAQ copy accuracy, rendered visual verification, contrast re-verification, and `@theme inline` token emission (UX spec §21.11-19).

These items remain research-gated under DEC-054 through DEC-057 and DEC-060. None is an accepted product decision, and none authorizes implementation.
```

## 5. Source line ranges for every quoted decision

Line ranges refer to `<workspace-root>\papyr-rebuild-decisions.md` (1-based). Ranges cover the decision header through the final bullet line (the blank separator line after each block is excluded). `Where` indicates the section of this evidence file where the verbatim quote appears (2 = Track B governing; 3 = supporting).

| DEC | Source lines | Where |
| --- | --- | --- |
| DEC-001 | 16–25 | 2 |
| DEC-005 | 60–70 | 3 |
| DEC-013 | 158–169 | 3 |
| DEC-014 | 171–183 | 3 |
| DEC-015 | 185–200 | 2 |
| DEC-018 | 227–237 | 3 |
| DEC-019 | 239–251 | 3 |
| DEC-020 | 253–265 | 3 |
| DEC-022 | 279–290 | 3 |
| DEC-023 | 292–302 | 2 |
| DEC-025 | 316–327 | 3 |
| DEC-026 | 329–340 | 2 |
| DEC-030 | 378–389 | 2 |
| DEC-031 | 391–401 | 2 |
| DEC-034 | 427–437 | 3 |
| DEC-035 | 439–450 | 3 |
| DEC-036 | 452–462 | 3 |
| DEC-037 | 464–474 | 3 |
| DEC-038 | 476–486 | 3 |
| DEC-039 | 488–498 | 3 |
| DEC-040 | 500–510 | 3 |
| DEC-041 | 512–522 | 3 |
| DEC-045 | 560–570 | 3 |
| DEC-046 | 572–582 | 3 |
| DEC-047 | 584–594 | 2 |
| DEC-048 | 596–608 | 3 |
| DEC-049 | 610–620 | 3 |
| DEC-050 | 622–631 | 3 |
| DEC-051 | 633–643 | 3 |
| DEC-052 | 645–654 | 3 |
| DEC-053 | 656–666 | 3 |
| DEC-054 | 668–680 | 2 |
| DEC-055 | 682–692 | 2 |
| DEC-056 | 694–704 | 2 |
| DEC-057 | 706–716 | 2 |
| DEC-058 | 718–728 | 2 |
| DEC-059 | 730–740 | 2 |
| DEC-060 | 742–752 | 2 |
| DEC-062 | 764–774 | 2 |
| DEC-064 | 787–797 | 3 |
| DEC-065 | 799–809 | 2 |
| DEC-066 | 811–823 | 2 |
| DEC-067 | 825–835 | 3 |
| DEC-070 | 861–871 | 3 |
| DEC-074 | 909–919 | 3 |
| DEC-075 | 921–931 | 3 |
| DEC-076 | 933–943 | 3 |
| DEC-077 | 945–955 | 3 |
| DEC-078 | 957–967 | 3 |
| DEC-079 | 969–979 | 3 |
| DEC-080 | 981–991 | 3 |
| DEC-081 | 993–1003 | 3 |
| DEC-082 | 1005–1015 | 3 |
| DEC-083 | 1017–1027 | 2 |
| DEC-084 | 1029–1040 | 3 |
| DEC-085 | 1042–1052 | 2 |
| DEC-088 | 1072–1082 | 3 |
| DEC-089 | 1084–1094 | 2 |
| DEC-090 | 1096–1107 | 3 |
| DEC-091 | 1109–1119 | 3 |
| DEC-092 | 1121–1131 | 3 |
| DEC-093 | 1133–1143 | 3 |
| DEC-094 | 1145–1155 | 3 |
| DEC-097 | 1181–1191 | 3 |
| DEC-099 | 1205–1215 | 2 |
| DEC-103 | 1252–1261 | 2 |
| DEC-104 | 1263–1272 | 3 |
| DEC-110 | 1330–1339 | 3 |
| DEC-113 | 1363–1372 | 3 |
| DEC-114 | 1374–1384 | 2 |
| DEC-115 | 1386–1395 | 2 |
| DEC-116 | 1397–1406 | 3 |
| DEC-117 | 1408–1417 | 3 |
| DEC-118 | 1419–1428 | 2 |
| DEC-119 | 1430–1439 | 3 |
| DEC-120 | 1441–1450 | 3 |
| DEC-121 | 1452–1461 | 3 |
| DEC-122 | 1463–1472 | 2 |
| DEC-124 | 1485–1494 | 3 |
| DEC-126 | 1506–1515 | 3 |
| DEC-127 | 1517–1526 | 2 |
| DEC-137 | 1629–1638 | 3 |
| DEC-143 | 1695–1706 | 2 |
| DEC-160 | 1884–1894 | 3 |
| DEC-161 | 1896–1905 | 3 |
| DEC-165 | 1940–1949 | 3 |
| DEC-166 | 1951–1960 | 3 |
| DEC-168 | 1973–1983 | 3 |
| DEC-169 | 1985–1995 | 3 |
| DEC-171 | 2008–2017 | 3 |
| DEC-172 | 2019–2029 | 3 |
| DEC-173 | 2031–2041 | 3 |
| DEC-174 | 2043–2052 | 3 |
| DEC-178 | 2087–2096 | 3 |
| DEC-180 | 2109–2118 | 3 |
| DEC-181 | 2120–2129 | 3 |
| DEC-182 | 2131–2140 | 3 |
| DEC-183 | 2142–2151 | 2 |
| DEC-184 | 2153–2161 | 2 |
| DEC-185 | 2163–2172 | 2 |
| DEC-186 | 2174–2183 | 2 |
| DEC-187 | 2185–2195 | 2 |
| DEC-188 | 2221–2230 | 2 |
| Open decisions | 2199–2219 | 4 |

### Coverage checklist

- Section 2 requested 34 governing decisions: 34 quoted (none missing, none absent).
- Section 3 requested supporting decisions: the brief enumerated 69 unique IDs; 69 quoted (none missing, none absent). No requested decision number was found to be nonexistent.
- Section 4: the entire `## Open decisions` section quoted verbatim (lines 2199–2219).
- Every decision ID present in the source (DEC-001 through DEC-188) appears in the Section 1 topic table.


## Verification evidence

- Output file exists: `<workspace-root>\audit-outputs\research\track-b\_evidence-decisions.md` (confirmed present, non-empty).
- Source file unchanged: `<workspace-root>\papyr-rebuild-decisions.md` was read-only; no modifications performed.
- `papyr-reference/` unchanged: `git -C <workspace-root>\papyr-reference status --porcelain` returned empty output with exit code 0 (checked before extraction and after extraction).
- Verbatim integrity: all 103 quoted decision blocks (34 governing + 69 supporting) and the Open decisions block were mechanically diffed against the source by line range and matched byte-for-byte (0 mismatches after correcting one curly-quote transcription in DEC-094).
- Section completeness: Section 1 (188-row decision map), Section 2 (34 governing decisions), Section 3 (69 supporting decisions), Section 4 (entire Open decisions section), Section 5 (line-range index for every quoted decision) all present.
- No requested decision number was absent from the source; no requested decision is marked missing in this file.
- Constraints honored: no files modified under `papyr-reference/`; the only file written was this evidence file; extraction only, no editorializing.

### Track B research follow-up anchors (derived from quoted text; extractor annotation)

- Browser routing: DEC-011 (browser-first hybrid), DEC-015 (conservative limits), DEC-030 (auto fallback), DEC-031 (browser matrix), DEC-065 (fallback after safe failure), DEC-083/085/089 (paper policy), Open decisions items 1, 4, 13.
- Accessibility: DEC-062 (WCAG 2.2 AA), DEC-040 (keyboard alternative to drag-and-drop), DEC-143/144/147/149/153/155-158 (UI baseline accessibility requirements).
- i18n/paper policy: DEC-023 (locale prefixes), DEC-047 (locale detection), DEC-083/085/089 (paper standards), DEC-122 (ID slugs), DEC-004/115/118 (locales), Open decisions items 4, 5, 7.
- SEO/URL migration: DEC-044 (tool-page SEO + blog), DEC-099 (legacy archive), DEC-114 (retain legacy content), DEC-127 (legacy URL audit), DEC-023/122 (localized routes/slugs), Open decisions item 5.
- UI baseline: DEC-028 (evolve legacy design), DEC-143 (preserve visual language), DEC-142/144-158 (directory model and tool-page sequence), DEC-168 (privacy disclosure placement).
