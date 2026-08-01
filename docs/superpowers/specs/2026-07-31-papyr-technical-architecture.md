# Papyr Technical Architecture Specification

| Field | Value |
|---|---|
| Document ID | PPR-TA-001 |
| Title | Papyr Rebuild Technical Architecture Specification |
| Version | 1.1 (incorporates DEC-189 to DEC-196 and the completed cross-domain reconciliation) |
| Date | 2026-07-31 |
| Canonical language | English (DEC-184) |
| Status | Approved by DEC-188; revised to incorporate DEC-189 to DEC-196; not an implementation authorization |
| Decision baseline | papyr-rebuild-decisions.md, DEC-001 through DEC-196 |
| Companion document | Product and UX Design Specification (separate document per DEC-185) |
| Governing rules | AGENTS.md (Papyr Rebuild Orchestrator Rules) |

---

## 1. Scope, Status, and Authority

### 1.1 Status

This document consolidates the approved high-level rebuild design into one canonical technical architecture specification. It is produced under DEC-183, which approved the complete high-level design covering technical architecture, security and data flow, testing, deployment, and operations as established through DEC-001 to DEC-182. DEC-185 requires this technical document to be written separately from the Product and UX Design Specification, sharing the same decision baseline and cross-referencing each other where responsibilities meet.

This is a design document. Per DEC-183, DEC-185, and DEC-060, approval authorizes documentation only. Product implementation, scaffolding, infrastructure modification, VPS access, and production deployment remain blocked until the owner reviews and approves this specification and the Product and UX Design Specification, and until the required research and reconciliation gates are complete.

The final cross-domain reconciliation (`audit-outputs/research/reconciliation-report.md`) has been completed, and the owner resolved its category-B questions through DEC-189 to DEC-196, incorporated in this revision. These decisions are documentation-level refinements under DEC-188; they do not authorize implementation, VPS access, gateway access, account operations, or remote mutation (DEC-188, DEC-193, DEC-196).

### 1.2 Scope

This specification covers:

- The approved production topology: Vercel Next.js frontend, Cloudflare domain and API edge, VPS hosting Nginx and FastAPI behind Docker, Cloudflare R2 for temporary server-processed files (DEC-017).
- The Redis-backed durable task queue with dedicated bounded workers, replacing the legacy in-memory task store (DEC-019, DEC-162).
- Browser-first and server processing boundaries, routing rules, and the five-tool processing model (DEC-009 to DEC-011, DEC-014, DEC-015, DEC-030, DEC-065).
- The R2 object lifecycle and the absolute one-hour server-retention deadline (DEC-013, DEC-067, DEC-070, DEC-075, DEC-166).
- The task state machine and the same-tab refresh recovery contract (DEC-033, DEC-069, DEC-071, DEC-072).
- The versioned `/api/v1` contract, the machine-readable capability and limits contract, and fair-use controls (DEC-164, DEC-165, DEC-020).
- Signed result downloads (DEC-170).
- Availability and failure isolation (DEC-163, DEC-167, DEC-098).
- Input validation, sanitization, malware scanning, and container hardening (DEC-088, DEC-090 to DEC-093, DEC-169, DEC-171).
- Secrets, access, logging, and backups (DEC-172 to DEC-176, DEC-181).
- CI core gate, manual deployment, and rollback (DEC-160, DEC-177, DEC-178).
- Monitoring, public status, and Telegram alerting (DEC-180, DEC-182, DEC-116, DEC-119, DEC-161).
- Dependency maintenance (DEC-179).
- The owner resolutions of the final cross-domain reconciliation: one-active-worker concurrency, the reaffirmed advertising risk, the US/Canada Letter rule, active-content Merge and Split routing to server sanitization, the `gpt5.6-sol` gateway contract, the localized 410 default for deferred tool URLs, and the Compress engine path (DEC-189 to DEC-196).
- Testing strategy (DEC-066, DEC-062, DEC-031, and the verification obligations attached to other decisions).
- Data classification and prohibited data (DEC-025, DEC-036, DEC-042, DEC-072, DEC-174, DEC-175).
- Operational acceptance criteria (DEC-024, DEC-027, DEC-096, DEC-100, DEC-103, DEC-118).
- Research gates and unresolved implementation-level choices (DEC-054 to DEC-060, DEC-066, DEC-073).

Product-facing behavior such as copy, layout, interaction states, localization, advertising placement, and the homepage structure is covered by the Product and UX Design Specification, which is the companion to this document. Where a behavior has architectural consequences, this document states the architectural requirement and references the product decision rather than duplicating the full product requirement.

### 1.3 Non-goals

The following are explicitly outside the scope of this technical design and the MVP relaunch:

- User accounts, authentication, cloud history, saved files, or cross-device synchronization (DEC-012).
- Public business API, organizational workspace, API keys, usage billing, or service-level contracts (DEC-108).
- Payments, subscriptions, credits, premium gates, or paid fast lanes (DEC-105, DEC-132 to DEC-134).
- Donations, tips, or supporter payments (DEC-111).
- A newsletter or email-marketing infrastructure at relaunch (DEC-109).
- Social-media account creation or publishing automation (DEC-112).
- Competitor-comparison landing pages (DEC-128).
- Public usage counters or the legacy admin dashboard (DEC-126).
- Any formal or informal benchmark program (DEC-066).
- Deadline-prediction admission control (DEC-073).
- OCR, PDF to Word, PDF to Excel, Protect, Unlock, Watermark, Sign, Rotate, and other legacy tools in the MVP catalog; these are post-launch candidates (DEC-010, DEC-094).
- Guinevere/OpenClaw runtime and agents, BullMQ, PostgreSQL/Drizzle, Guinevere's Telegram reporting bots, and persona or decision-engine infrastructure (DEC-016). Queue Redis remains governed by DEC-019 (§8), and Telegram operational incident alerts by DEC-180 (§20).
- A persistent staging environment or public beta phase (DEC-096).
- Horizontal multi-VPS architecture at launch (DEC-098).
- Recreating the legacy 13-tool catalog, legacy Indonesian-only positioning, or legacy operational coupling (DEC-001, DEC-002, DEC-099).
- Guarantees of malware-free files, perfect sanitization, or legal compliance; see Section 17.7 and Section 25.

### 1.4 Source precedence

When this specification or future documents conflict, the following precedence applies:

1. `papyr-rebuild-decisions.md` is the authoritative record of confirmed product and engineering decisions. It is a living log; changes are recorded as new or superseding decision IDs, never by silent rewrite (AGENTS.md; DEC-006).
2. This Technical Architecture Specification and the Product and UX Design Specification are the canonical design documents derived from that decision baseline. They must be consistent with each other (DEC-185).
3. `audit-outputs/` contains durable research and audit results. These are evidence supporting design, not standalone requirements.
4. `papyr-reference/` is the read-only legacy clone. It is a source of requirements history and reusable patterns, not the default architecture (DEC-001). Legacy behavior is reference material and must be re-justified (DEC-059). Legacy code and documentation never override an accepted decision.
5. Historical legacy documents (BRD, SRS, TDD, ADR, UIUX spec, brand guidelines, migration evidence, step prompts) are non-canonical historical material under DEC-026 unless explicitly re-adopted.

Material contradictions discovered during specification writing must be surfaced for owner review rather than silently resolved (DEC-183).

### 1.5 Design versus implementation authorization

This document defines the approved design direction, not a license to build. Concretely:

- Writing this specification does not authorize scaffolding, feature code, dependency installation, container builds, VPS access, DNS or provider changes, or deployment (DEC-060, DEC-183).
- DEC-189 to DEC-196 are documentation-level refinements of the approved design; they do not authorize implementation, VPS access, gateway access, account operations, or remote mutation (DEC-188, DEC-193, DEC-196).
- Implementation planning begins only after owner review and approval of both design specifications and completion of the required research and reconciliation gates (DEC-185).
- Every researched feature still requires explicit owner approval before entering approved design and implementation planning (DEC-057).
- Research findings are recommendations, not accepted product decisions (DEC-054).
- Where this document marks a value as a "conservative default" or an "implementation-level choice", that value is a design proposal subject to the research and approval gates in Section 25.

### 1.6 Conventions used in this document

- Decision citations use the form DEC-NNN and refer to `papyr-rebuild-decisions.md`.
- Legacy source citations use paths relative to `papyr-reference/` and are evidence of the current implementation that the rebuild modernizes or replaces. They are cited so reviewers can verify the baseline; they do not bind the rebuild.
- "Must", "must not", and "may" carry their usual normative meaning. "Should" marks a strong design recommendation that does not override an approved decision.
- Where the decisions leave an exact value open, this document states the constraint and marks the open choice explicitly in Section 25.

---

## 2. System Context and Topology

### 2.1 Approved topology

The production topology is retained from the legacy deployment and modernized (DEC-017):

| Layer | Component | Role |
|---|---|---|
| Hosting | Vercel | Next.js frontend, public site, status experience, edge country context |
| Edge | Cloudflare | DNS, TLS, proxying of `mypapyr.com` and `api.mypapyr.com`, coarse country signal, DDoS and bot defense |
| Compute | VPS | Nginx reverse proxy, FastAPI application, Redis, bounded PDF worker (one active at launch, DEC-189), cleanup and operational tooling |
| Storage | Cloudflare R2 | Temporary server-processed source, intermediate, and result objects |
| Backups | S3-compatible destination | Recoverable VPS state (DEC-173) |
| Alerts | Telegram | Operational incident alerts (DEC-180) |
| Monitoring | Netdata plus external uptime checks | VPS/service resource health plus outside-in availability (DEC-182) |

The legacy reference confirms this topology was deliberately migrated, hardened, and operated (`papyr-reference/docs/runbook-vps.md:1-30`; `papyr-reference/deploy/docker-compose.yml`; `papyr-reference/deploy/nginx/conf.d/production.conf`). The rebuild modernizes the topology and makes it reproducible through executable configuration rather than prose and manual evidence alone (DEC-017). Frontend and backend deployments remain independently operable (DEC-017).

### 2.2 Data flow at a glance

Browser-only job:

1. User selects files on a tool page.
2. The frontend validates within conservative browser limits and processes locally in the browser (DEC-011, DEC-015).
3. No bytes leave the device. Results are kept only for the active tab session (DEC-032) and served from memory or object URLs.

Server job:

1. The frontend uploads the file through Cloudflare to `https://api.mypapyr.com/api/v1/...`.
2. Nginx terminates TLS with origin certificates, applies rate limiting and request filtering, and proxies to the FastAPI application.
3. The API validates the file, enforces per-tool limits and fair-use controls, writes minimal task metadata to Redis, and enqueues the job.
4. A bounded worker claims the job, processes it inside a hardened container, and writes source, intermediate, and result objects to R2.
5. The API exposes task status. The frontend polls while the tab is open and stores an opaque recovery token in `sessionStorage` (DEC-072).
6. When ready, the frontend auto-downloads the result and keeps a manual Download control. Downloads use short-lived signed R2 URLs (DEC-170).
7. All server-side objects are deleted no later than one hour after upload receipt; the application actively deletes them and an R2 lifecycle rule is the safety net (DEC-013, DEC-070, DEC-166).

### 2.3 Components and responsibilities

The component boundaries follow DEC-017, DEC-019, and DEC-162. Each component has a single primary responsibility:

- Frontend (Vercel): pages, locale routing, browser processing, upload, status polling, result presentation, disclosure links.
- Edge (Cloudflare): public DNS, TLS, caching of static and capability-contract responses, coarse country context, first-layer bot and attack filtering.
- Nginx (VPS): TLS origin termination, request-size and rate enforcement, sensitive-path and bot filtering, proxying to the API.
- FastAPI (VPS): admission, validation, fair-use enforcement, queueing, task metadata, status, signed-URL issuance, cleanup coordination.
- Redis (VPS): durable minimal task metadata queue (DEC-174).
- Workers (VPS): bounded execution of PDF engine work; one active worker executing one concurrent job at launch (DEC-189).
- R2: temporary object store with enforceable expiry.
- Monitoring and alerting: Netdata, external uptime checks, public status page, Telegram.

### 2.4 Request flows

API admission flow (per tool):

1. Client requests the capability and limits contract for the tool.
2. Client validates locally, then uploads.
3. API validates bytes, structure, encrypted status, and resource risk (DEC-034, DEC-088, DEC-169).
4. Fair-use controls decide accept, queue, delay, or reject (DEC-020, DEC-035).
5. API records minimal metadata in Redis and enqueues.
6. Worker claims under fair scheduling (DEC-137), processes, uploads artifacts to R2.
7. API records terminal state and the authoritative expiry timestamp.
8. Client polls until ready, then downloads via signed URL.

Download flow:

1. Client requests a signed URL for the task result while the task is authorized and unexpired.
2. API verifies the capability token and task state, and issues a short-lived signed R2 GET URL (DEC-170).
3. Client downloads directly from R2. VPS bandwidth is not consumed for the file body.
4. A refreshed URL may be issued for the same valid result until expiry, without extending retention (DEC-170).

---

## 3. Monorepo Boundaries

### 3.1 Single repository

The rebuild lives in one repository containing the frontend, backend, deployment configuration, canonical documentation, and related test infrastructure, with explicit boundaries between them (DEC-159). Coordinated changes across web, API, operations, and documentation stay reviewable together (DEC-159). The legacy clone remains a separate read-only reference and is not the rebuild workspace (DEC-159, AGENTS.md).

The current workspace at `<workspace-root>` holds the decision log, `audit-outputs/`, the read-only `papyr-reference/`, and `docs/`. The rebuild repository itself is not yet created, consistent with the coding gate in DEC-060. The boundaries below describe the target monorepo design.

### 3.2 Directory and package boundaries

Proposed structure (implementation-level, subject to planning approval):

- Frontend workspace: the Next.js application, its unit tests, and Playwright E2E suites. Owns no server-processing logic.
- Backend workspace: the FastAPI application, task queue integration, worker entrypoints, services, validation, and backend tests. Owns no page rendering.
- Deployment configuration: Docker Compose stack, Nginx configuration, environment templates, CI workflow definitions, and the documented deployment and rollback procedures.
- Canonical documentation: the decision log (after migration), this specification, the Product and UX Design Specification, runbooks, and policy documents.
- Research and audit outputs: durable discovery evidence, kept separately from canonical docs (DEC-026).

Boundaries are explicit so that:

- CI can use path-aware jobs while preserving integrated release traceability (DEC-159).
- Frontend and backend deployments remain independently operable (DEC-017).
- Removed Guinevere functionality is not reintroduced as a monorepo package (DEC-159).

### 3.3 What is excluded from the monorepo

- `papyr-reference/` legacy clone: read-only historical reference, outside the rebuild repository (DEC-159, DEC-099).
- Runtime secrets: never committed; managed through the protected VPS environment-configuration procedure (DEC-176).
- Generated reports: SBOMs, vulnerability-scan output, and test reports are regenerated as CI artifacts, not maintained as canonical source documents (DEC-026).
- Legacy archive material: preserved only with explicit historical labeling under the archive strategy (DEC-026, DEC-099).

---

## 4. Vercel Next.js Frontend

### 4.1 Role and hosting

The frontend is a Next.js application hosted on Vercel (DEC-017). It serves the public site: locale-prefixed tool pages, homepage, FAQ, legal pages, contact and support surfaces, blog, and the public status experience (DEC-043 to DEC-046, DEC-116, DEC-119). The legacy frontend is a Next.js App Router application (`papyr-reference/frontend/src/app/`), and the rebuild retains that framework baseline while correcting documented defects (DEC-028, DEC-143).

Vercel hosts the status experience so it remains independent of a backend VPS outage (DEC-119). The page must not depend solely on the failing VPS to render (DEC-119), and must not claim complete infrastructure independence (DEC-119).

### 4.2 Routing and localization

- Every localized route carries an explicit locale prefix, including English and Spanish, and the legacy unprefixed routes receive a deliberate redirect map (DEC-023).
- Indonesian is a first-class launch locale alongside English and Spanish for all five tools and essential supporting pages (DEC-115, DEC-118). Indonesian tool and content URLs use translated slugs under `/id/` (DEC-122).
- Locale-less entry redirects once according to supported browser-language preferences; a persistent manual language switcher overrides detection and its explicit choice is remembered with minimal non-sensitive storage (DEC-047).
- Locale resolution must avoid redirect loops, unpredictable crawler behavior, and SEO duplication (DEC-023, DEC-047).
- Canonical URLs, hreflang, sitemaps, and internal links are generated consistently per locale (DEC-023, DEC-115, DEC-122, DEC-127). Deferred legacy tool URLs that return 410 Gone are excluded from sitemap, navigation, canonical links, and internal links (DEC-194).

### 4.3 Server and browser responsibilities

Client components perform browser processing, upload, polling, and result presentation. Server components (Next.js server functions and middleware) handle locale detection, metadata, SEO output, and any server-only integration that does not expose secrets to the browser.

Browser processing runs in the user's browser within the conservative limits of DEC-015. The frontend owns browser-specific capability logic and limits, which must be clearly distinguished from server limits in the capability contract (DEC-165).

The tool pages remain accessible when the backend is unavailable. Browser-capable operations may continue locally; server-dependent processing clearly communicates temporary unavailability (DEC-163).

### 4.4 Frontend configuration and environment

Public configuration is limited to build-time values such as the API base URL and site URL (legacy pattern: `papyr-reference/frontend/src/lib/config.ts`). Secrets must never appear in client-side code (DEC-051, DEC-193). The API base uses one canonical value shared with Nginx routing (DEC-164).

The legacy frontend mirrors backend limits in `frontend/src/lib/config.ts` (`maxUploadBytes: 20MB`, `fileRetentionMinutes: 60`). Under DEC-165 this duplication is removed for server capabilities: the machine-readable API contract becomes the canonical source, with conservative frontend fallback values if the contract is unavailable.

### 4.5 Analytics and advertising

- Analytics follow DEC-025: detailed product events, funnels, attribution, performance, and sanitized error analytics; no session replay on document workflows; no fingerprinting; no document-sensitive information.
- Advertising is limited to non-intrusive banner and native formats (DEC-018) loaded without prior consent in all launch regions as an accepted business and legal risk, reaffirmed after reconciliation (DEC-022, DEC-190). This is not a compliance claim: Papyr must not state that the approach is GDPR, PECR, ePrivacy, UK GDPR, or Swiss FADP compliant without qualified review (DEC-190). If binding terms, qualified legal review, or applicable law determines that prior consent is mandatory, Papyr must implement consent controls, use demonstrably non-tracking contextual ads, or suppress ads in the affected regions (DEC-022, DEC-190). UX takes priority over advertising (DEC-102). Critical product functionality and legal, support, and status content remain available if ad scripts are blocked or disabled (DEC-190).
- Ad slots reserve stable dimensions to prevent layout shift and must not obstruct upload, processing, consent, or download controls (DEC-018, DEC-102, DEC-131, DEC-151).
- Third-party advertising scripts load asynchronously or lazily where appropriate and remain subject to regional consent requirements (DEC-018, DEC-190).

### 4.6 Availability behavior

- The frontend does not redirect ordinary tool traffic to the status page and does not globally disable tools during a backend incident (DEC-163).
- Status and error messaging accurately distinguishes local and server processing paths (DEC-163).
- Unsafe fallback, repeated submissions, and misleading progress are prevented (DEC-163).

---

## 5. Cloudflare Edge (Domain and API)

### 5.1 Domain and DNS

The product retains the Papyr name and `mypapyr.com` domain (DEC-021). Cloudflare sits in front of the public domain and the API (DEC-017). DNS, proxy, and TLS settings are managed as reproducible configuration, with credentials rotated from legacy values before production use (DEC-017, DEC-176).

### 5.2 API edge routing

`api.mypapyr.com` is the public API origin (legacy: `papyr-reference/docs/runbook-vps.md:17`, `papyr-reference/deploy/nginx/conf.d/production.conf`). Cloudflare proxies API traffic to the VPS origin and forwards real client IP information so origin logging and rate limiting use real IPs (legacy nginx `set_real_ip_from` and `CF-Connecting-IP` in `production.conf`). The origin must validate and constrain trust in forwarded headers so a client cannot spoof them.

### 5.3 Edge-derived country context

JPG to PDF paper selection uses a coarse country code supplied by the trusted Vercel or Cloudflare request edge. Letter applies only when the trusted coarse edge country code is the United States or Canada; every other country, missing code, or invalid code selects A4, which is also the deterministic fallback when no trusted signal is available (DEC-083, DEC-085, DEC-089, DEC-191). The active content locale does not independently select paper size (DEC-191).

The design must define:

- Which trusted headers carry the country code, and how to reject spoofed or untrusted values.
- That the country code is ephemeral for page-policy selection, never becomes a persistent location profile, and is never sent to analytics (DEC-085, DEC-191).
- That privacy and analytics documentation accurately discloses country-level processing already performed by hosting or analytics providers (DEC-085).

No precise browser geolocation is requested (DEC-085).

### 5.4 TLS and security posture

- Public TLS is terminated at the Cloudflare edge with the origin using a valid origin certificate (legacy origin cert pattern in `production.conf`).
- Nginx applies security headers, disables server tokens, and drops unknown hostnames (legacy `production.conf` and `default.conf`).
- Cloudflare provides the first layer of bot and attack filtering; Nginx and the application provide additional layers (Section 17).

---

## 6. VPS: Nginx and FastAPI `/api/v1`

### 6.1 VPS role

The VPS runs the processing side of the product: Nginx, the FastAPI application, Redis, bounded PDF workers, and operational tooling as one Docker Compose stack (DEC-162). The legacy runbook documents the operated baseline including SSH access, monitoring, backups, and incident procedures (`papyr-reference/docs/runbook-vps.md`). The rebuild makes this reproducible and modernizes it (DEC-017).

No current VPS access, account creation, or configuration change is authorized by this specification (DEC-172, DEC-160).

### 6.2 Nginx reverse proxy

Nginx is the origin-facing reverse proxy and the only VPS service exposed to the public (DEC-162). Requirements:

- Terminate origin TLS for the API hostname.
- Enforce request-size, header, and body timeouts appropriate to the per-tool upload limits.
- Apply rate-limiting zones for API and status traffic (legacy pattern: `limit_req_zone` zones in `production.conf`).
- Filter sensitive paths and known malicious user agents early (legacy `map` blocks in `production.conf`).
- Proxy to the FastAPI service over the internal Docker network; no public exposure of Redis or worker ports (DEC-162).
- Forward client identity from the trusted Cloudflare edge only.
- Apply security headers, `server_tokens off`, and connection-drop catch-alls (legacy `production.conf`).
- Expose a health-check path for the API and for external uptime checks.

The legacy Nginx configuration is the hardening baseline (`papyr-reference/deploy/nginx/conf.d/default.conf`, `papyr-reference/deploy/nginx/conf.d/production.conf`) and is modernized under the rebuild's executable-configuration requirement (DEC-017).

### 6.3 FastAPI application boundary

The application layer owns admission and orchestration, not long-running processing. This is the core fix of DEC-019: API processes enqueue work and expose durable status rather than owning long-running processing in module-global memory. The legacy in-memory task store (`papyr-reference/backend/services/async_task.py`, `_tasks: dict[str, TaskInfo]`) demonstrates the failure modes being replaced: restart loss, cross-process inconsistency, and uncontrolled fire-and-forget execution (DEC-019).

The application is responsible for:

- Request parsing and file buffering.
- Validation, threat classification, and fair-use decisions (Section 14, Section 17).
- Writing minimal task metadata to Redis and enqueueing (Section 8).
- Exposing status, cancellation (queued only), limits, and download-authorization endpoints (Section 13, Section 14, Section 15).
- Coordinating active deletion of R2 objects by absolute deadline (Section 12).
- Issuing short-lived signed URLs (Section 15).

The application must not execute blocking native PDF work on the API event loop; that work belongs to bounded worker processes (DEC-019).

### 6.4 API versioning

The rebuild API exposes its public processing and task contracts under an explicit `/api/v1` prefix (DEC-164). Processing, task status, cancellation where applicable, limits, and related machine-readable endpoints use the same versioned contract (DEC-164). The frontend configuration and Nginx routing use one canonical API base (DEC-164). Legacy routes require an explicit migration or retirement disposition and must not remain accidentally active (DEC-164).

---

## 7. Docker Compose Services

### 7.1 Compose stack

The API, Redis, bounded workers, and Nginx operate as separate services managed through one production Docker Compose stack on the VPS (DEC-162). Service health checks, resource limits, restart behavior, persistent Redis state where required, internal networking, and startup dependencies are explicit (DEC-162).

The legacy stack (`papyr-reference/deploy/docker-compose.yml`) provides the hardening baseline: `read_only: true`, dropped capabilities, `no-new-privileges`, CPU and memory limits, ephemeral tmpfs writable areas, a read-only env file mount, internal ports only, healthchecks, and bounded log rotation. The rebuild extends this baseline with separate Redis and worker services.

### 7.2 Service inventory

| Service | Responsibilities | Public exposure |
|---|---|---|
| nginx | TLS, filtering, rate limiting, proxying | 80/443 only |
| api | FastAPI application, admission, task metadata, status, signed URLs, cleanup coordination | internal only |
| redis | Durable minimal task metadata and queue state | none |
| workers | Bounded execution of PDF engine jobs; one active worker, one concurrent job at launch (DEC-189) | none |
| monitoring agents | Netdata and related collection on the VPS | none (SSH tunnel or Netdata Cloud) |

### 7.3 Hardening baseline

Containers follow the hardening requirements of DEC-169 and the legacy precedent:

- Non-root execution with a dedicated application user (legacy: UID/GID 1001 in `backend/Dockerfile.production`).
- Read-only root filesystem with narrow writable volumes and tmpfs for ephemeral workspace.
- Dropped capabilities, `no-new-privileges`, and bounded CPU/memory/time/disk.
- No network access from processing services except the internal network and R2 (workers must not reach arbitrary external hosts).
- Bounded log rotation (legacy: `json-file` driver with size caps in `docker-compose.yml`).
- Pinned base images with quarterly refresh and digest pinning where the legacy precedent applies (`backend/Dockerfile.production`).
- `userns-remap` compatibility is preserved and documented, including the host UID mapping for mounted writable paths (legacy comments in `docker-compose.yml` and `Dockerfile.production`).

Container isolation is one defense layer, not the sole security boundary (DEC-169).

### 7.4 Resource bounds and health

- Every service declares CPU and memory limits and a healthcheck (DEC-162).
- The API healthcheck exercises the application `/health` endpoint (legacy precedent in `Dockerfile.production` and `docker-compose.yml`).
- Redis and worker health are monitored as first-class production concerns (DEC-019, DEC-182).
- Worker bounds are tuned from production observability, not from a benchmark program (DEC-066, DEC-098).

### 7.5 Startup dependencies and networking

- Compose declares startup dependencies so the API and workers start only after Redis is healthy, and Nginx starts only after the API is healthy (legacy `depends_on: condition: service_healthy` pattern).
- Redis and worker ports are never published to the host or public network (DEC-162).
- The stack supports controlled deployment and rollback under DEC-160 and DEC-178.

---

## 8. Redis Durable Minimal-Metadata Queue

### 8.1 Role

Redis is the coordination store for server-side PDF jobs (DEC-019). It replaces the legacy in-memory task store and fixes its restart loss, cross-process inconsistency, uncontrolled execution, and polling failures (DEC-019). Redis adds negligible coordination overhead relative to PDF processing time (DEC-019).

### 8.2 What is persisted

Redis persists the minimum task metadata needed to survive service restarts: opaque task identity, state, timing, expiry, processing route, and non-sensitive temporary object references (DEC-174).

Persisted task records must never contain:

- File contents, previews, extracted content, or unnecessary document metadata (DEC-174).
- PDF passwords (DEC-036, DEC-174).
- Signed URLs (DEC-170, DEC-174).
- Original filenames (DEC-174; see also DEC-025 and DEC-042).
- Analytics payloads or sensitive request data (DEC-174).

Redis records expire no later than their applicable task and artifact lifecycle, except strictly sanitized aggregate operational metrics stored separately (DEC-174). Redis persistence files and any backup treatment follow the same data-minimization rules (DEC-174).

### 8.3 Queue behavior

- API processes enqueue work and expose durable status (DEC-019).
- Available workers claim jobs immediately; the system must not introduce an artificial waiting period (DEC-019).
- Job state, progress, timeout, retry policy, cancellation, result expiry, and failure reasons are explicitly modeled (DEC-019).
- Queueing remains bounded by hard operational safety limits for queue length, storage, maximum wait, job expiry, and VPS health (DEC-035).
- Valid jobs remain queued during normal capacity pressure instead of being rejected with a retry response (DEC-035).
- Fair scheduling prevents starvation and queue monopolization (DEC-137; Section 9).

### 8.4 Redis operations and recovery

- Redis availability and recovery are production operational concerns covered by health checks, deployment configuration, and the runbook (DEC-019).
- The stack declares persistent Redis state where required, with restart behavior and backup treatment that honor data-minimization (DEC-162, DEC-174).
- A Redis outage degrades server-job admission and status; browser-only tools remain available (DEC-163).
- If Redis state is lost, any in-flight server jobs fail within their timeouts; the R2 lifecycle safety net still enforces the one-hour ceiling (DEC-166).

---

## 9. Bounded Workers and Fair Scheduling

### 9.1 Worker processes

PDF engines run in bounded worker processes so blocking native operations do not block the API event loop (DEC-019). Workers:

- Claim jobs from Redis under the scheduling policy.
- Execute engine work in hardened containers with bounded CPU, memory, time, and disk (DEC-169).
- Upload source, intermediate, and result objects to R2 with expiry metadata.
- Report progress where the engine provides measurable units (DEC-033).
- Continue independently of any client connection (DEC-071).

### 9.2 Bounds

- Worker concurrency, per-job memory, and per-job time are bounded and explicit (DEC-019, DEC-162, DEC-169).
- The initial production posture is one active worker executing one concurrent processing job (DEC-189). Worker limits, scanner settings, and other service memory budgets are designed around one concurrent processing job (DEC-189). Valid jobs may wait in the bounded fair queue when the worker is busy (DEC-189). Additional worker concurrency requires capacity evidence from production observability and explicit owner approval (DEC-189, DEC-098).
- Per-tool server input limits are independent (DEC-034; Section 14).
- Bounds are conservative design choices, adjusted from real production observations, never benchmark-proven (DEC-066).
- If production capacity becomes insufficient, optimize worker bounds, queue behavior, processing configuration, and resource use before vertically scaling the VPS; vertical upgrade costs require owner approval (DEC-098).

### 9.3 Fair scheduling policy

Scheduling balances waiting time and job complexity while preventing users or unusually heavy jobs from monopolizing capacity (DEC-137). It must not use pure smallest-job-first or unrestricted FIFO as the sole policy (DEC-137).

The approved design must define, without exposing exploitable defensive detail:

- Understandable fairness classes for jobs (DEC-137).
- Concurrency bounds per class and total (DEC-137).
- Starvation prevention: maximum wait bounds, stale-job expiry, and cleanup (DEC-035, DEC-137).
- Per-origin concurrency to prevent one client flooding the queue (DEC-020, DEC-035).
- No paid priority lane (DEC-134, DEC-137).

Under high demand, free access is preserved through fair queuing and adaptive fair-use controls; users may wait longer, and hard safety caps still apply (DEC-134).

### 9.4 Queueing under pressure

When all workers are busy (the expected condition during load with the initial one-active-worker posture, DEC-189), valid server jobs are accepted and queued rather than rejected (DEC-035). Users receive real queued status and an honest wait estimate where sufficient data exists (DEC-033, DEC-035). Jobs that exceed safety or abuse thresholds are rejected clearly before unnecessary upload or processing (DEC-035). Queue wait time and saturation are monitored as launch reliability indicators (DEC-035).

### 9.5 Cancellation

Users may cancel a server job only while it remains queued (DEC-069). Cancellation must:

- Atomically prevent worker pickup (DEC-069).
- Mark the terminal state clearly and schedule prompt cleanup of associated temporary data (DEC-069).
- Handle the race between cancellation and worker acquisition with an explicit state transition; if processing already started, the UI reports that cancellation is no longer available (DEC-069).

Closing the tab does not cancel a job (DEC-071). Operational timeouts, worker failures, and safety shutdowns are system-controlled and distinct from user cancellation (DEC-069).

### 9.6 Failure isolation per tool

A failed or unhealthy processing engine disables only the affected tool or processing path (DEC-167). Per-tool readiness influences admission before accepting work that cannot currently run (DEC-167). Jobs are not accepted into an unbounded wait for a known-unavailable engine (DEC-167). The public status experience and tool UI may expose general per-tool availability without infrastructure details (DEC-167).

---

## 10. Browser/Server Routing

### 10.1 Hybrid model

Papyr uses a hybrid processing model that prefers local browser processing and routes operations to a server when quality, file complexity, device capability, or reliability requires it (DEC-011). Routing is based on measured capabilities and explicit rules rather than hidden arbitrary behavior (DEC-011).

### 10.2 Browser-first jobs and limits

The conservative, device-aware browser-processing limits of DEC-015 apply:

- Modern desktop browser-first jobs: 100 MB total input, 500 PDF pages initially.
- Capable non-iOS mobile browser-first jobs: 50 MB total input, 200 PDF pages initially.
- iPhone and iPad browser-first jobs: 25 MB total input, 100 PDF pages initially.
- PDF to JPG browser-first: 200 pages on desktop, 50 pages on mobile, sequential page rendering, and a 16-megapixel per-page safety ceiling for broad iOS compatibility.
- JPG to PDF browser-first: 50 images and 100 megapixels total on desktop, 40 megapixels total on mobile.
- Compress PDF uses server-side processing by default (DEC-015).

Routing must also evaluate decoded image dimensions, page geometry, encryption, file corruption, estimated peak memory, and browser capabilities rather than relying only on file size (DEC-015). These are product safety limits, not browser hard limits; they may be raised only after anonymous reliability telemetry and representative real-device testing demonstrate acceptable failure rates (DEC-015).

### 10.3 Automatic server fallback

- When a file is corrupt, encrypted, unsupported, or unsafe for reliable browser processing, the job automatically falls back to temporary server processing (DEC-030).
- When browser processing fails and the job is safe and supported on the server, the same job automatically transitions to server processing without a second confirmation prompt (DEC-065).
- Automatic fallback applies only to classified recoverable failures and must not create retry loops, duplicate jobs, duplicate downloads, or repeated uploads (DEC-065).
- Security-policy failures, unsupported content, invalid passwords, user cancellation, retention violations, and unsafe conditions fail closed rather than forcing a server upload (DEC-065).
- The server copy and result remain subject to the one-hour maximum retention and sensitive-data restrictions (DEC-065).
- If server processing also cannot recover the file, the product returns a clear, actionable failure rather than an indefinite retry loop (DEC-030).
- Merge and Split inputs in which browser inspection detects PDF JavaScript, embedded attachments, launch actions, or other active content route to the temporary server sanitization path; Papyr does not build a separate browser sanitization engine for the MVP (DEC-192). Ordinary safe files may still use the browser path within DEC-015 limits (DEC-192).

### 10.4 Disclosure of processing location

The user-visible disclosure behavior (no dedicated block on the uploader, full disclosure on the localized Privacy page, truthful workflow-state labels, accessible path) is specified canonically in the Product and UX Design Specification (§12.0, §15.2, §17.5). The architectural obligations retained here are that Privacy page content must remain accurate about browser processing, automatic server fallback, R2 storage, providers, and the absolute one-hour maximum retention, and that any legally mandatory notice or consent mechanism required by later review is not removed by this decision (DEC-168). The initial processing disclosure and live stages must truthfully show that server processing may occur, including for active-content Merge and Split jobs routed under DEC-192.

### 10.5 Backend-outage behavior

When the backend is unavailable, tool pages remain accessible and browser-capable operations may continue locally; server-dependent processing clearly communicates temporary unavailability (DEC-163). The frontend does not redirect ordinary tool traffic to the status page and does not globally disable every tool (DEC-163). Availability and error messaging accurately distinguishes local and server processing paths, and unsafe fallback, repeated submissions, and misleading progress are prevented (DEC-163).

---

## 11. Five-Tool Processing Responsibilities

The five-tool catalog is Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG (DEC-010). All five must be production-ready across EN, ES, and ID at relaunch (DEC-027, DEC-118). Each tool retains independently measurable acceptance criteria (DEC-059). Processing responsibilities below are grounded in the approved decisions and the legacy implementation evidence.

### 11.1 Shared foundations

- Shared upload, ordering, page selection, progress, and download experiences across the five tools (DEC-010).
- A shared user-facing progress model for browser and server jobs (DEC-033).
- One canonical tool catalog feeding navigation, related-tools, metadata, and localized slugs (per the reconciliation audit, `audit-outputs/ui-home-shell-audit.md` D2 and `audit-outputs/ui-docs-code-reconciliation.md`).
- Output names derived from source names with safe, localized suffixes (DEC-042).
- Multi-file results delivered as ZIP plus individual downloads (DEC-037).
- Encryption detection and password request only when required (DEC-036, DEC-064).
- Active-content sanitization on PDF-producing server outputs (DEC-090).

### 11.2 Compress PDF

- One automatic high-quality compression mode for premium on-screen viewing; no presets, target-size, DPI, or advanced controls in the MVP (DEC-014). The legacy backend exposes `screen|ebook|printer` presets (`papyr-reference/backend/routers/compress.py`, `quality` query) while the legacy frontend hardcodes `ebook`; the rebuild removes the preset surface entirely under DEC-014.
- True high-quality compression requires a capable compression engine and is expected to use server-side processing (DEC-014, DEC-015). The engine is the official unmodified open-source Ghostscript executable invoked as a separate hardened server-side subprocess, following the existing Papyr integration boundary; Papyr does not modify, link into, or embed Ghostscript source into proprietary application code, and Ghostscript is obtained from an authoritative distribution, version-pinned, hardened, and invoked with safety flags including `-dSAFER` (DEC-195). Papyr preserves applicable Ghostscript copyright and AGPL notices and makes the corresponding unmodified source available as required, and must not claim that using an unmodified subprocess eliminates every licensing obligation (DEC-195). The exact production distribution and integration model requires a focused license review before public launch; if that review determines the chosen model requires disclosure the owner does not accept, Compress moves to a permissive engine path or a commercial Ghostscript license before launch (DEC-195; Section 25.3).
- Compression preserves searchable/selectable text, links, page geometry, and legibility whenever the source format permits (DEC-014).
- A newly processed output artifact is always generated, even when the source was already optimized or the output is not smaller (DEC-080). The result reports actual input size, output size, and real change honestly, including zero savings or a larger output (DEC-080).
- Papyr must not fabricate a compression percentage, claim success as size reduction when none occurred, or silently substitute the original file (DEC-080).
- If meaningful reduction cannot be achieved within the quality floor, the result says so honestly (DEC-014).
- Output handling follows safe localized naming (DEC-042) and the always-new-artifact rule (DEC-080).

### 11.3 Merge PDF

- File-level controls: reorder with drag-and-drop (keyboard-accessible alternative required) and remove unwanted files before processing; no cross-document page-level editor in the MVP (DEC-040).
- Processing preserves page order within each source document (DEC-040).
- The complete job fails when any selected source cannot be opened, authenticated, validated, or processed; no partial output is presented (DEC-076).
- Document features such as bookmarks, form fields, annotations, links, metadata, page geometry, and other supported features are preserved to the greatest extent the selected engine can do safely (DEC-079). Unsupported or transformed features require truthful user-facing limitations; security-relevant or unsupported interactive behavior is not preserved blindly (DEC-079).
- Detected active content (JavaScript, launch actions, embedded attachments, external actions) is removed or neutralized from generated outputs (DEC-090), with general categories disclosed to the user (DEC-091).
- When browser inspection detects active content in an input, the job routes to the temporary server sanitization path; Papyr does not build a separate browser sanitization engine for the MVP (DEC-192).
- Multiple encrypted inputs each receive an independently entered and validated password (DEC-074). Credentials are never reused across files unless the user enters them (DEC-074).
- Browser-first in the MVP (DEC-011, DEC-015). Server path exists for fallback and for jobs exceeding browser limits (DEC-030, DEC-065).

### 11.4 Split PDF

- Custom page ranges and a per-page mode are supported (DEC-038).
- Ranges may overlap; each entered range creates an independent output (DEC-077). The system must not silently merge, deduplicate, or rewrite user-entered ranges (DEC-077), and validation must make duplicated page membership visible (DEC-077).
- Outputs, ZIP ordering, individual-download listing, naming sequence, and manifest entries follow the order in which the user entered the custom ranges (DEC-078). Per-page mode continues in natural page order (DEC-078).
- Range input has clear syntax, validation, overlap handling, ordering, and actionable errors; the interface previews the exact outputs before processing (DEC-038).
- Per-page mode is subject to output-count, archive-size, memory, and device/server safety limits (DEC-038).
- Output names and ordering remain deterministic in both ZIP and individual-download views (DEC-038, DEC-037).
- Browser-first (DEC-011, DEC-015); server fallback per DEC-030 and DEC-065. Server outputs are sanitized per DEC-090. When browser inspection detects active content in an input, the job routes to the server sanitization path rather than a separate browser sanitization engine (DEC-192).

### 11.5 JPG to PDF

- Automatically fits each image to an appropriate standard page without exposing A4, Letter, orientation, DPI, or margin controls (DEC-041).
- Page size and portrait/landscape orientation are selected per image; one PDF may contain mixed orientations (DEC-082).
- Letter geometry applies only when the trusted coarse edge country code is the United States or Canada; every other country, missing code, or invalid code selects A4, with A4 as the deterministic fallback, and the active content locale does not independently select paper size (DEC-083, DEC-085, DEC-089, DEC-191). The selected standard is visible before processing (DEC-083, DEC-089), and the UI exposes no manual paper controls (DEC-041, DEC-191).
- Fitting preserves aspect ratio, avoids cropping, and respects EXIF orientation, with deterministic page-size and margin rules (DEC-041, DEC-082).
- Image order remains user-adjustable before conversion (DEC-041, DEC-082).
- Source metadata, including EXIF GPS and device/software information, is preserved to the greatest extent supported (DEC-084, accepted risk). The interface and privacy documentation disclose that source metadata may remain in the result (DEC-084).
- The tool officially accepts JPG/JPEG, PNG, and WebP image inputs at launch while the user-facing name remains "JPG to PDF" (DEC-187). Image inputs are validated by actual bytes, rejected when unsupported or malformed, bounded for encoded and decoded resources, and decoded within an isolated processing boundary (DEC-093, DEC-187). Threat-classified files are blocked (DEC-088).
- Browser-first with a server fallback; legacy hybrid threshold of 3 MB (`papyr-reference/frontend/src/app/image-to-pdf/page.tsx:43`) is replaced by the DEC-015 limits and capability-based routing.

### 11.6 PDF to JPG

- One automatic high-quality output profile in the MVP; no Standard/High/Maximum/DPI/JPEG-quality controls (DEC-039).
- Rendering resolution, JPEG quality, color handling, and downscaling thresholds are established through design, representative validation, and production observation, not a benchmark program (DEC-039, DEC-066).
- Text and line art remain crisp for normal high-quality screen use within the 16-megapixel per-page ceiling for browser processing (DEC-015, DEC-039).
- Transparent pages are composited onto white before JPEG encoding, deterministically, in both browser and server paths (DEC-081).
- The source PDF is treated and inspected as untrusted for parser and infrastructure safety even though active content is not represented in raster output (DEC-092). Rendering occurs with isolation, least privilege, bounded resources, and current patched dependencies (DEC-092).
- Page selections preserve repeated and overlapping selections as independent outputs in the requested order; output names, ZIP contents, individual downloads, and manifest entries disambiguate duplicates and follow user-entered order (DEC-186, DEC-078, DEC-037). Jobs that cannot safely meet the profile locally route to server processing (DEC-030, DEC-039).
- If source pages are already low resolution, the UI must not imply that conversion can create missing detail (DEC-039).

---

## 12. R2 Object Lifecycle and the Absolute One-Hour Deadline

### 12.1 Storage model

Cloudflare R2 stores temporary server-processed objects (DEC-017): source files, intermediate artifacts, and generated results. The legacy implementation uses UUID-based object keys that carry no user-identifiable information (`papyr-reference/backend/utils/r2.py`); the rebuild retains that key-hygiene requirement (DEC-174, DEC-025).

### 12.2 Retention clock

- The maximum one-hour retention period starts when the backend first accepts the uploaded file, not when processing begins or completes (DEC-070).
- One hour is a hard upper bound, not a guaranteed retention period; files may be deleted earlier after processing or download (DEC-013).
- Source, intermediate, and result files must all be deleted by the same absolute deadline unless safely deleted earlier (DEC-070).
- Retries, status polling, downloads, page focus, or an open tab never reset or extend the deadline (DEC-067, DEC-070, DEC-075).
- A successful download does not trigger early deletion; objects remain governed by the absolute one-hour expiry (DEC-075).
- An expired result cannot be restored from server storage; the user must run a new job (DEC-067).
- The API exposes the authoritative expiry timestamp so UI countdowns do not depend on client clock assumptions (DEC-070).

### 12.3 Active deletion and lifecycle safety net

The application actively deletes temporary R2 objects according to each job's absolute one-hour deadline, while an R2 lifecycle rule provides independent backup cleanup (DEC-166). Requirements:

- Cleanup is idempotent, observable without logging content or sensitive identifiers, and recoverable after restarts (DEC-166).
- Lifecycle configuration is verified against the promised retention rather than treated as the primary timer (DEC-166).
- Storage objects carry enforceable expiry metadata, with a scheduled cleanup path for failed or abandoned jobs (DEC-013).
- Cleanup behavior is verified through normal functional and integration tests (DEC-013, DEC-067).
- The legacy cleanup loop (`papyr-reference/backend/utils/cleanup.py`, 30-minute interval scanning for objects older than retention) is the baseline being replaced by per-job deadline tracking plus the lifecycle rule.

### 12.4 Expiry-while-open and post-download retention

- Server results expire no later than one hour after the clock starts even if the browser tab remains open and the result has not been downloaded (DEC-067).
- The result UI shows an accurate expiry time or countdown and warns before deletion (DEC-067).
- The manual Download button may retrieve the same generated result repeatedly while authorization and retention remain valid (DEC-075).
- The UI continues to show the remaining availability window after a successful download (DEC-075).

### 12.5 Object key hygiene

- Object keys are opaque and carry no filenames, user identifiers, passwords, or sensitive metadata (DEC-174, DEC-025).
- Object keys must not appear in analytics, application logs, support reports, or public status data (DEC-170, DEC-175, DEC-117, DEC-025).
- Cleanup telemetry records counts and timing, not content or sensitive identifiers (DEC-166).

---

## 13. Task State Machine and Refresh Recovery Contract

### 13.1 States and transitions

Server tasks use the following states (extending the legacy model in `papyr-reference/backend/services/async_task.py` with the decisions):

- `queued`: admitted, waiting for a worker.
- `processing`: claimed and being executed by a worker.
- `done`: result ready and downloadable.
- `failed`: terminal failure with a safe error category.
- `cancelled`: terminal state from user cancellation while queued (DEC-069).
- Expiry is not a separate state: the artifact lifecycle is driven by the absolute deadline (DEC-070).

Explicit transitions:

- queued -> processing (worker acquisition).
- queued -> cancelled (user cancellation, atomic with worker pickup prevention, DEC-069).
- processing -> done (result uploaded, expiry metadata set).
- processing -> failed (engine error, timeout, safety shutdown).
- done -> expired (deadline reached; result no longer accessible, DEC-067).
- failed -> expired (deadline reached; cleanup completed).

Job state, progress, timeout, retry policy, cancellation, result expiry, and failure reasons are explicitly modeled (DEC-019). Operational timeouts, worker failures, and safety shutdowns are system-controlled and distinct from user cancellation (DEC-069).

### 13.2 Progress model

The UI presents real lifecycle stages: preparing, uploading, queued, processing, finalizing, and ready, with an estimate only when supported by measured or engine-derived information (DEC-033). This is the shared canonical stage vocabulary with the Product and UX Design Specification (§13.1), which defines the user-facing state set (including the Idle, Ready/configuration, and Error framing states) and the mapping of internal events onto these stages (DEC-033, DEC-185). Percentages may be shown only when grounded in measurable units such as bytes uploaded, pages processed, or explicit engine progress (DEC-033). Queue position or wait estimates are labeled as estimates and updated from real queue state (DEC-033). Long-running, stalled, retrying, cancelled, and failed states require distinct messages and recovery actions (DEC-033).

### 13.3 Timeouts, retries, and failures

- Per-job timeouts are explicit and bounded (DEC-019).
- Retry policy is explicit and must not create retry loops or repeated uploads (DEC-019, DEC-065).
- A task that exceeds its timeout fails clearly with a safe localized error (legacy precedent: `papyr-reference/backend/services/async_task.py` timeout handling; DEC-033).
- Jobs may fail if they cannot complete within the one-hour deadline; no deadline prediction is offered (DEC-073).
- Users receive a clear, actionable failure rather than an indefinite retry loop when server processing cannot recover a file (DEC-030).

### 13.4 Session recovery

The user-visible refresh and reset behavior is specified canonically in the Product and UX Design Specification (§13.3-13.4); this section states the mechanism contract.

- A queued or processing server job continues after its originating tab closes (DEC-071). Tab closure is not a cancellation signal (DEC-071), and workers and cleanup operate independently of any active client connection (DEC-071).
- The minimum opaque task-access state is stored in `sessionStorage` so refreshing the same tab can resume status polling and result access while the job remains valid; closing the tab ends client-side recovery (DEC-072).
- Stored state is limited to opaque task identifiers or capability tokens and minimal expiry/routing metadata (DEC-072). Filenames, passwords, document contents, previews, signed result URLs, and analytics payloads are never stored (DEC-072).
- Tokens require sufficient entropy, narrow job scope, expiry enforcement, and protection against unauthorized status, cancellation, or download access (DEC-072).
- Successful expiry, cancellation, clear/reset, or invalidation removes the corresponding session state (DEC-072).
- `sessionStorage` is a narrowly approved exception for active server-job recovery and does not override the prohibition on persistent cross-session document storage (DEC-072, DEC-032).

### 13.5 Status API contract

- Task status is exposed under the versioned API (`/api/v1/.../status/{task_id}` style, DEC-164), replacing the legacy `/api/status/{task_id}` endpoint (`papyr-reference/backend/routers/status.py`).
- Unknown or expired task IDs return a distinct not-found response (legacy: 404 with "Task not found").
- Status responses include state, authoritative timestamps, the authoritative expiry timestamp, measurable progress where available, and safe error categories (DEC-033, DEC-070).
- Status polling is rate-managed and does not extend retention (DEC-070, DEC-067).

---

## 14. API Capability and Limits Contract

### 14.1 Canonical machine-readable contract

The versioned backend API is the canonical source for server-processing capabilities and limits (DEC-165). The frontend reads and presents this machine-readable contract rather than maintaining an independent hardcoded copy (DEC-165). Requirements:

- The contract is cacheable safely, versioned, and localized at the presentation layer (DEC-165).
- The frontend has conservative fallback behavior if the contract is unavailable (DEC-165).
- Backend validation remains authoritative even when the frontend pre-validates inputs (DEC-165).
- Browser-specific safety limits remain frontend capability logic but are clearly distinguished from server limits (DEC-165).

### 14.2 Per-tool server limits

Server-side input limits are defined independently for each tool rather than as one universal ceiling (DEC-034). The contract expresses limits that may combine total bytes, per-file bytes, file count, page count, pixel count, page geometry, estimated memory, and expected output size (DEC-034). The UI and API expose consistent per-tool limits before upload and return machine-readable validation failures (DEC-034). Conservative design and safety defaults, adjusted from production observations rather than benchmark-proven, and the procedure for safely raising limits are documented during technical design (DEC-034, DEC-066).

### 14.3 Fair-use controls

Server-side processing is protected by adaptive anonymous fair-use controls rather than mandatory accounts, rigid daily quotas, or a challenge on every upload (DEC-020). Controls may consider IP or network signals, job frequency, concurrent jobs, input size and complexity, queue pressure, abnormal traffic patterns, and processing cost (DEC-020). Normal users should not encounter a fixed daily quota unless measured capacity or abuse data later justifies one (DEC-020). Suspicious or high-cost traffic may be delayed, rejected with a clear retry response, or challenged selectively (DEC-020). Enforcement avoids retaining document contents and minimizes personal-data collection (DEC-020). Limits and responses are consistent across API processes rather than per-process counters (DEC-020). Thresholds require load-informed production telemetry, monitoring, and documented operational overrides (DEC-020).

### 14.4 Error and rejection semantics

- Machine-readable validation failures are returned for uploads that violate limits (DEC-034).
- Threat-classified files are blocked with a safe localized rejection that does not reveal exploit or scanner internals (DEC-088, DEC-169).
- Ordinary invalid files receive safe localized validation errors (DEC-088, DEC-093).
- Rate-limit and abuse responses are clear and retryable where appropriate (DEC-020; legacy 429 handling in `papyr-reference/backend/main.py`).
- Errors never include filenames, passwords, document contents, signed URLs, object keys, or sensitive payloads (DEC-025, DEC-036, DEC-042, DEC-088).

---

## 15. Signed Downloads

### 15.1 Signed R2 URLs

Successful server-processing results are downloaded through short-lived signed R2 URLs rather than being proxied through the VPS API (DEC-170). Direct temporary delivery avoids unnecessary VPS bandwidth and keeps the processing API focused on admission, task state, and authorization of result access (DEC-170).

The legacy implementation establishes the pattern: `generate_signed_url` with a 3600-second expiry and `Content-Disposition: attachment` force-download filename (`papyr-reference/backend/utils/r2.py`; `papyr-reference/backend/routers/compress.py`).

### 15.2 Expiry relationship

- Signed URL expiry never exceeds the artifact's authoritative absolute expiry (DEC-170).
- A refreshed signed URL may be issued for the same valid result until the artifact expires, without extending retention (DEC-170).
- Signed URLs are never written to analytics, application logs, browser persistence, support reports, or public status data (DEC-170, DEC-072, DEC-175).

### 15.3 Download behavior

The user-visible download behavior (auto-download attempt, manual button, blocked-download handling, ZIP plus individual downloads) is specified canonically in the Product and UX Design Specification (§13.2); this section states the delivery mechanism obligations.

- The result download starts automatically when processing completes, and a visible manual Download button remains available until the result expires or the local session is cleared (DEC-029, DEC-068).
- A blocked automatic download leaves the job in the Ready state, not failed, and the manual button uses the already generated result without rerunning processing (DEC-068).
- Repeated download attempts do not rerun processing (DEC-029).
- Multi-file results auto-download as a ZIP with each generated file also available for individual download (DEC-037).
- Download names are safe, localized where appropriate, and derived without sending original file names to analytics (DEC-029, DEC-042).
- Local results are kept only for the active tab session, with object URLs revoked on unload, reset, or replacement (DEC-032).
- Result-page advertising remains spatially and visually separated from Download controls (DEC-131).

---

## 16. Availability and Failure Isolation

### 16.1 Failure domains

- Frontend (Vercel), API/queue/workers (VPS), and storage (R2) are separate failure domains (DEC-017, DEC-163).
- A VPS or backend incident does not take down the informational site or browser-capable tools (DEC-163).
- The public status experience is hosted on Vercel and stays useful when the backend VPS is unavailable (DEC-119).
- Browser-only and server-dependent paths fail and recover independently (DEC-163).

### 16.2 Per-tool readiness

Processing-engine failures are isolated by tool (DEC-167). Admission is influenced by per-tool readiness so jobs are not accepted into an unbounded wait for a known-unavailable engine (DEC-167). General per-tool availability may be surfaced on the status experience and tool UI without infrastructure details (DEC-167).

### 16.3 Frontend during backend outage

Tool pages remain accessible during backend outages; browser-capable operations continue locally; server-dependent processing communicates temporary unavailability clearly (DEC-163). The frontend does not globally disable tools or redirect to the status page (DEC-163).

### 16.4 Scaling policy

If production capacity becomes insufficient, the first response is to optimize worker bounds, queue behavior, processing configuration, and resource use, then to upgrade the existing VPS, before introducing a multi-VPS architecture (DEC-098). The initial posture is one active worker executing one concurrent job; additional worker concurrency requires capacity evidence from production observability and explicit owner approval (DEC-189, DEC-098). Scaling actions are driven by real production observability, not a benchmark program (DEC-066, DEC-098). Optimization must not weaken output quality, privacy, security, retention, fairness, or reliability without renewed approval (DEC-098).

---

## 17. Input Validation, Sanitization, Malware Scanning, and Container Hardening

### 17.1 Defense layers

Server-side input handling uses layered defenses (DEC-169, DEC-171):

1. Edge and Nginx filtering (bot, path, size, rate).
2. Application-level file validation (structure, resource risk).
3. Maintained general malware scanning (DEC-171).
4. Active-content sanitization for PDF-producing outputs (DEC-090).
5. Bounded resource controls.
6. Hardened container isolation (DEC-169).

Validation is focused: it blocks unsupported files and credible security or resource-exhaustion threats without aggressively rejecting ordinary valid documents (DEC-169). Docker is one defense layer, not the sole security boundary (DEC-169).

### 17.2 File validation

- Validation inspects actual file structure and decoded-resource risk rather than trusting extension or MIME alone (DEC-169, DEC-093).
- PDF validation covers empty files, MIME type, extension, magic bytes (`%PDF`), size, page count, and encrypted status (legacy baseline: `papyr-reference/backend/utils/pdf_validator.py`).
- Image validation considers signatures, dimensions, pixel count, frame count where applicable, orientation data, decode expansion, and resource limits (DEC-093).
- Browser and server paths require equivalent safety outcomes even if their underlying decoders differ (DEC-093).
- EXIF preservation (DEC-084) does not authorize executing, logging, or trusting metadata fields (DEC-093).

### 17.3 Active-content sanitization

Merge PDF, Split PDF, and Compress PDF remove or safely neutralize detected JavaScript, launch actions, embedded attachments, and other active PDF features from generated outputs (DEC-090). Requirements:

- Embedded attachments are removed from the processed output and are not offered as separate downloads (DEC-090).
- Server processing treats all inputs as untrusted and never executes embedded actions or attachments (DEC-090).
- Files classified as infrastructure threats are blocked under DEC-088 rather than sanitized and returned (DEC-090).
- When active content is detected and sanitized, the user is told which general categories were found (JavaScript, embedded attachments, launch actions, external actions) without payloads or exploit-level details (DEC-091).
- Merge and Split inputs that browser inspection identifies as carrying active content are routed to this server sanitization path; Papyr does not build a separate browser sanitization engine for the MVP (DEC-192).
- Sanitization behavior and known coverage limitations require normal security and functional verification; Papyr must not claim perfect malware detection or universal sanitization (DEC-090).
- Removing active elements may reduce fidelity and is communicated honestly when detected (DEC-090).

### 17.4 Threat blocking

If security controls classify a file or its behavior as a threat to Papyr infrastructure, the job is blocked rather than processed for fidelity, sanitized, or returned (DEC-088). The file must not reach document engines beyond the minimum safely isolated inspection needed for classification (DEC-088). Cleanup runs promptly within the absolute retention ceiling, and the user receives a safe localized rejection without exploit details (DEC-088). Logs and security telemetry may retain minimal non-content indicators under a separately documented retention policy, but never the document, password, filename, signed URL, or sensitive payload (DEC-088, DEC-175).

### 17.5 Malware scanning

A maintained general malware scanner is added to server-side input handling alongside format validation, sanitization, resource controls, patched engines, and container isolation (DEC-171). Scanner results are one security signal and do not support a claim that accepted or produced files are malware-free (DEC-171). Scanner failure, update health, resource consumption, and safe rejection behavior are operationally monitored (DEC-171). When the maintained malware-scanner or sanitization path is unavailable, affected Merge and Split jobs fail closed rather than bypassing the control (DEC-192). User-facing rejection messages expose only safe general categories (DEC-171).

### 17.6 Container and process hardening

Processing services require (DEC-169):

- Non-root execution and least privilege.
- Bounded CPU, memory, time, and disk.
- Restricted network access.
- Hardened filesystem and capability settings.
- Maintained engines and current patched dependencies.

The legacy compose and Dockerfile establish the baseline (Section 7.3). PDF-to-JPG rendering and JPG-to-PDF decoding occur with isolation, least privilege, and bounded resources (DEC-092, DEC-093).

### 17.7 Honest limits of these controls

- Papyr does not claim perfect malware detection, universal sanitization, or complete isolation (DEC-090, DEC-171).
- Container isolation is one layer among several (DEC-169).
- Accepted files are not claimed malware-free; successful rasterization is not a claim that the source PDF was malware-free (DEC-092).
- Security controls are tuned through normal functional and security testing and production observations, not an invented benchmark program (DEC-169).

---

## 18. Secrets, Access, Logging, and Backups

### 18.1 Secrets management

Runtime production secrets are installed and rotated through a documented protected VPS environment-configuration procedure rather than committed to the repository or delivered wholesale by automatic CI deployment (DEC-176). Requirements:

- Environment files require restrictive ownership and permissions and are excluded from source control, images, backups where inappropriate, logs, and audit outputs (DEC-176).
- The rebuild requires rotation of legacy credentials and investigation of possible historical exposure before production use (DEC-017, DEC-176).
- Documentation identifies secret owners, rotation and revocation steps, and safe recovery without recording secret values (DEC-176).
- Credentials remain protected and are never exposed in chat, source control, logs, or audit artifacts (DEC-160).
- Telegram bot credentials follow the same secret-management policy (DEC-180).
- Blog-automation gateway API keys follow the same policy and are stored only in protected server-side or automation secrets; they are never committed, logged, returned to clients, inserted into generated MDX, or exposed through analytics (DEC-193, DEC-196).
- The legacy template pattern (`papyr-reference/deploy/.env.production.example`, mode-600 install at `/opt/papyr/production/.env`) is the baseline.

### 18.2 VPS access

- VPS access uses the owner's dedicated non-root SSH user; authorized configuration and deployment work may elevate through `sudo NOPASSWD` rather than logging in directly as root (DEC-172).
- Direct root SSH login remains disabled and key-based authentication remains required (DEC-172).
- The sudo policy is as narrow and auditable as practical for the documented deployment and administration procedures (DEC-172).
- Possession of the deployment user's key is effectively high privilege and requires strong secret handling, rotation, and revocation procedures (DEC-172).
- The legacy runbook documents the SSH baseline (`papyr-reference/docs/runbook-vps.md`), which the rebuild updates.
- This decision does not authorize current VPS access or configuration changes (DEC-172).

### 18.3 Logging policy

Non-content production operational logs are retained for 30 days (DEC-175). Requirements:

- Logs exclude files, filenames, passwords, signed URLs, object keys, previews, extracted content, precise document metadata, and sensitive request payloads (DEC-175, DEC-025, DEC-036, DEC-042).
- Access control, rotation, deletion, and any provider-side copies honor the retention policy (DEC-175).
- Security or legal requirements that materially change this period require explicit review and approval (DEC-175).
- The legacy structured-logging baseline is JSON-formatted and explicitly documents the same prohibitions (`papyr-reference/backend/utils/logging_config.py`).
- Logging is observable without logging content or sensitive identifiers; cleanup telemetry records counts and timing only (DEC-166).

### 18.4 Backups

The complete VPS state required for operational recovery is backed up to the approved S3-compatible backup destination (DEC-173). Requirements:

- Backup scope includes required configuration, deployment state, service data, and recovery material appropriate to retain (DEC-173).
- Ephemeral processing workspaces, uploads, intermediate artifacts, results, passwords, signed URLs, and temporary queue payloads are not recoverable state and must not be captured in backup archives (DEC-173).
- Backup encryption, credentials, retention, restore procedures, and periodic restore verification are documented (DEC-173).
- R2 temporary objects remain governed by their independent absolute one-hour expiry and are not part of the VPS backup set (DEC-173).
- An isolated restore verification of the S3-backed recovery set runs once per month; it must not affect production or introduce user temporary files into retained test environments, and results and failures are recorded without exposing credentials (DEC-181).
- Repeated restore failures trigger an operational alert and corrective work (DEC-181).
- Full S3 restore is a disaster-recovery mechanism, not the ordinary release rollback path (DEC-178).
- The legacy restic-based backup tooling is the baseline (`papyr-reference/docs/runbook-vps.md`, Section 7).

---

## 19. CI Core Gate, Manual Deployment, and Rollback

### 19.1 CI core gate

Before an authorized manual production deployment, the mandatory automated core gate consists of linting, unit tests, integration tests, production build verification, and security scanning (DEC-177). Requirements:

- Relevant E2E, accessibility, and preview smoke verification remain mandatory for initial relaunch readiness and for changes that affect their surfaces (DEC-177).
- A failing core gate blocks deployment unless the owner explicitly reviews and approves an exceptional response; failures are not silently bypassed (DEC-177).
- CI may automatically build, test, and scan artifacts but must not independently change production (DEC-160).
- The legacy CI workflow (`papyr-reference/.github/workflows/ci.yml`) shows the baseline jobs: frontend lint/test/build and backend Ruff and pytest. The rebuild redefines this as the core gate and adds the security-scan and production-build stages required by DEC-177.

### 19.2 Manual production deployment

Production backend deployment to the VPS is manually executed by the agent only after the owner gives explicit authorization for that deployment (DEC-160). Requirements:

- Each production deployment requires an explicit owner instruction, pre-deployment verification, rollback readiness, and post-deployment smoke checks (DEC-160).
- Credentials remain protected and are never exposed in chat, source control, logs, or audit artifacts (DEC-160).
- Post-deployment production smoke checks are required (DEC-177, DEC-160).
- The legacy automated deploy workflow (`papyr-reference/.github/workflows/deploy-vps.yml`) becomes the evidence base for a manual, agent-executed procedure; the deploy pipeline itself is reworked so it never changes production without explicit owner authorization (DEC-160, DEC-097).
- The owner remains accountable for deployment and high-risk production actions; AI-assisted automation supports routine observation and documented procedures but high-risk actions require explicit owner authorization (DEC-097).

### 19.3 Rollback

Normal backend rollback uses the previously verified healthy container image and matching deployment configuration through Docker Compose (DEC-178). Requirements:

- Release artifacts and configuration compatibility are traceable and retained for the defined rollback window (DEC-178).
- Deployment procedures verify health after rollback and distinguish application rollback from disaster recovery (DEC-178).
- Full S3 restore remains a disaster-recovery mechanism, not the ordinary release rollback path (DEC-178).
- Production rollback uses controlled release artifacts and deployment procedures, not a permanently running public legacy site (DEC-099).
- The legacy workflow's capture-previous-image and rollback steps (`deploy-vps.yml`) demonstrate the pattern to be preserved in the manual procedure.

### 19.4 Release traceability

- Container images are referenced by immutable digest or unique commit tag (legacy: `ghcr.io/fazulfi/papyr-backend:<sha>` plus digest capture).
- SBOMs are generated per release and retained as CI artifacts (legacy: syft CycloneDX with 90-day artifact retention).
- Deployments, rollbacks, and their outcomes are recorded in auditable form.

---

## 20. Monitoring, Status, and Telegram

### 20.1 Netdata and external uptime

Papyr is monitored through Netdata for VPS and service resource health plus independent external uptime checks for public availability (DEC-182). Coverage includes API, queue, workers, Redis, processing engines, storage integration, cleanup health, and relevant public endpoints, without collecting document contents (DEC-182). External checks feed the automated public status experience using noise-resistant health logic (DEC-182). Monitoring and launch communication distinguish the United States, Latin America, and Europe regions sufficiently to identify material failures in each, without prohibited profiling or collecting document content (DEC-104). The legacy runbook documents the Netdata and pending uptime-check baseline (`papyr-reference/docs/runbook-vps.md`, Sections 10.1 to 10.4).

### 20.2 Public status experience

A simple public status page shows material service availability and incidents without exposing sensitive infrastructure details (DEC-116). It is hosted on the Vercel frontend so it remains independent of a backend VPS outage (DEC-119). Status is updated automatically from approved service health signals rather than through owner-authored incident updates (DEC-161). Requirements:

- Health signals are meaningful, resilient to transient noise, and must not expose sensitive infrastructure details (DEC-161).
- Status wording distinguishes observable service availability from guarantees about every processing engine or user request (DEC-161).
- Status communication covers user-relevant components in plain EN/ES/ID language where supported (DEC-116).
- Incident updates are truthful and timely but omit hostnames, credentials, defensive controls, exploit details, and other sensitive operational information (DEC-116).
- The status page complements internal monitoring and in-product outage messaging; it does not replace either (DEC-116).
- The page must not claim complete infrastructure independence (DEC-119).

### 20.3 Telegram alerts

Telegram is the operational incident-alert channel (DEC-180). Alerts are actionable, deduplicated, severity-aware, and contain no user files, filenames, passwords, signed URLs, object keys, or sensitive payloads (DEC-180). Telegram delivery failure is visible within monitoring even though no second notification channel is required at launch (DEC-180). Bot credentials follow the production secret-management policy (DEC-180). The legacy channel reference is `<telegram-bot>` (`papyr-reference/docs/runbook-vps.md:25`).

---

## 21. Dependency Maintenance

A routine dependency review runs once per month, while critical security fixes are evaluated and applied promptly rather than waiting for the monthly cycle (DEC-179). Requirements:

- Updates require relevant tests and compatibility review before production deployment (DEC-179).
- Native processors, container base images, frontend/backend packages, GitHub Actions, and malware signatures are all within maintenance scope (DEC-179).
- Automated alerts may open work, but production changes still follow the approved manual deployment gate (DEC-179).
- Base images are refreshed quarterly and security-sensitive packages are upgraded within the container build pipeline (legacy precedent: `backend/Dockerfile.production`).
- The rebuild's MVP dependencies are limited to what the five tools require; the legacy stack's OCR and office-conversion dependencies (Tesseract, LibreOffice, Camelot, OpenCV; `papyr-reference/backend/requirements.txt`) are excluded until those tools are re-approved (DEC-010).
- Library, framework, and engine decisions require current official documentation and representative evidence under the research gates (DEC-054 to DEC-056).

---

## 22. Testing Strategy

### 22.1 Principles

- Testing verifies that the selected implementation behaves as specified; it is not a benchmark program (DEC-066). Functional tests, integration tests, security checks, accessibility checks, and production observability are normal verification, not comparative benchmarking.
- Normal implementation verification is required for every approved behavior, including the behaviors the benchmark decision explicitly excludes from study.
- Automated checks are necessary but insufficient for accessibility; representative manual keyboard and assistive-technology testing is required (DEC-062).

### 22.2 Layers

- Unit tests: frontend logic (page-range parsing, merge/split/pdf/image utilities, output naming), backend services (validation, sanitization, task state transitions, naming), and shared contracts.
- Integration tests: API admission and validation against per-tool limits, queue enqueue/claim/status behavior, R2 upload/delete integration with expiry enforcement, signed-URL issuance and refresh, cleanup idempotency and recovery (DEC-013, DEC-067, DEC-166, DEC-170).
- End-to-end tests: complete tool flows across the five tools in EN, ES, and ID, including auto-download and manual-download fallback, fallback routing, error states, and refresh recovery (DEC-027, DEC-029, DEC-068, DEC-072).
- Accessibility checks: automated scans plus manual keyboard and assistive-technology passes targeting WCAG 2.2 Level AA (DEC-062), across the supported browser matrix (DEC-031).
- Security checks: dependency and container scanning, secret scanning, sanitization and malware-scan behavior verification, threat-blocking behavior, and data-leakage guards on logs, analytics, and task records (DEC-090, DEC-171, DEC-088, DEC-025, DEC-174, DEC-175).
- Production smoke checks: post-deployment health verification (DEC-160, DEC-177).

### 22.3 Privacy and retention verification

- Automated tests and operational monitoring verify expiration and cleanup behavior (DEC-013, DEC-067).
- Event schemas require automated tests or audits that guard against sensitive-field leakage (DEC-025).
- Functional fixtures verify selected preservation behavior for Merge (DEC-079), white-compositing for PDF to JPG (DEC-081), and sanitization behavior with documented coverage limitations (DEC-090).
- Tests assert that passwords, filenames, signed URLs, object keys, and document contents never reach logs, analytics, persisted task records, or backups (DEC-036, DEC-042, DEC-174, DEC-175).

### 22.4 Browser and device coverage

- The supported matrix is the latest two major versions of Chrome, Edge, Firefox, and Safari on desktop, current Safari on iOS/iPadOS, and Chrome on Android (DEC-031).
- The matrix is represented in automated tests where feasible and supplemented by representative real-device testing, especially on iOS (DEC-031).
- Unsupported browsers receive a clear compatibility message or server-processing path rather than silently failing (DEC-031).
- Progressive enhancement and ordinary file-input/download fallbacks are required where Chromium-specific file APIs are unavailable (DEC-031).

### 22.5 What testing is not

- No benchmark corpora, benchmark matrices, comparative performance studies, quality-score programs, VPS benchmark workloads, or benchmark reports (DEC-066).
- Passing tests or research gates does not automatically authorize implementation (DEC-057).
- Test results are not a claim of malware-free files, perfect sanitization, or legal compliance (DEC-090, DEC-171, DEC-022).

---

## 23. Data Classification and Prohibited Data

### 23.1 Classes

| Class | Examples | Handling |
|---|---|---|
| Document content | Uploaded files, intermediates, results, previews, extracted text | R2 only, temporary, deleted by the absolute one-hour deadline (DEC-013, DEC-070, DEC-166); never in logs, analytics, backups, or persistent task records (DEC-025, DEC-174) |
| Sensitive transient data | PDF passwords, signed URLs, object keys, original filenames | Memory-only or narrowly scoped transient storage; never logged, analyzed, or persisted (DEC-036, DEC-042, DEC-170, DEC-174) |
| Session recovery tokens | Opaque task identifiers and capability tokens | `sessionStorage` only, same-tab recovery, expiry-enforced (DEC-072) |
| Sanitized operational metadata | Task state, timing, expiry, size buckets, error categories, queue depth | Redis minimal records expiring with task lifecycle (DEC-174); logs retained 30 days (DEC-175) |
| Analytics events | Acquisition, page and locale, tool, processing mode, coarse input bands, funnels, timings, sanitized failures, Web Vitals, ad performance | DEC-025 scope; privacy-reviewed schema, retention policy, regional activation, leakage guards |
| Secrets | R2 keys, SSH keys, bot tokens, provider credentials | Protected VPS environment configuration; rotation; never in source control, chat, logs, or artifacts (DEC-176, DEC-160) |

### 23.2 Prohibited-data register

The following are prohibited from the stated surfaces:

- File contents, previews, rendered document text, object keys, signed URLs, passwords, and full error payloads containing user data in analytics (DEC-025).
- Filenames in analytics, monitoring, logs, or error reporting (DEC-042, DEC-025).
- Passwords in logs, analytics, URLs, queue dashboards, persistent task records, storage metadata, or backups (DEC-036).
- File contents, filenames, passwords, signed URLs, object keys, previews, extracted content, and unnecessary document metadata in persisted Redis records and Redis persistence files (DEC-174).
- Files, filenames, passwords, signed URLs, object keys, previews, extracted content, precise document metadata, and sensitive request payloads in operational logs (DEC-175).
- Document contents and sensitive identifiers in backup archives; ephemeral processing state is not backed up (DEC-173).
- User files, filenames, passwords, signed URLs, object keys, and sensitive payloads in Telegram alerts (DEC-180).
- Submitted contact-form content in error states: errors are redaction-safe and never resurface submitted content; submissions are minimized, retained under documented rules, and deleted per the retention policy (DEC-046, DEC-050).
- Document contents and sensitive metadata in result-problem reports; reports carry only tool, path, sanitized category, browser context, and optional email (DEC-117, DEC-120).

### 23.3 Retention summary

| Surface | Retention |
|---|---|
| R2 temporary objects (source, intermediate, result) | Absolute one-hour maximum from upload receipt (DEC-070); active deletion plus lifecycle safety net (DEC-166) |
| Redis task metadata | No later than task and artifact lifecycle; separate sanitized aggregate metrics only (DEC-174) |
| Operational logs | 30 days (DEC-175) |
| S3 VPS recovery backups | Per documented retention policy; user files never included (DEC-173) |
| Browser local results | Active tab session only (DEC-032) |
| `sessionStorage` recovery tokens | Until job expiry, cancellation, reset, or invalidation (DEC-072) |
| Analytics | Per DEC-025 privacy review and retention policy |
| Contact and result-problem submissions | Per documented retention rules (DEC-046, DEC-117, DEC-120) |

---

## 24. Operational Acceptance Criteria

### 24.1 Launch gate

The public relaunch occurs only when all five tools are production-ready in EN, ES, and ID (DEC-027, DEC-118), with complete processing behavior, localized UI and metadata, error states, analytics, privacy disclosure, executable tests, documentation, and operational support (DEC-027). Legally required operator or contact information remains provided where applicable (DEC-110). The relaunch is direct to production on the existing domain without a public beta or persistent staging environment (DEC-096), and is preceded by pre-release local, CI, preview-deployment, integration, security, accessibility, and smoke verification (DEC-096, DEC-177). Launch requires rollback capability, backups where applicable, health monitoring, and the complete five-tool trilingual gate (DEC-096).

### 24.2 Reliability and performance criteria

The primary 90-day success criteria are reliable task completion, fast user experience, healthy Core Web Vitals, organic-search growth, and meaningful usage across all five launch tools; advertising revenue is a secondary indicator (DEC-024). Launch acceptance and operating dashboards must measure:

- Job success and failure rates.
- Processing and queue latency.
- Uptime.
- Core Web Vitals.
- Organic entrances.
- Tool usage distribution.
- Completed downloads.

Metrics distinguish browser-local jobs from server-side jobs without collecting document contents (DEC-024). Exact numeric targets and baseline measurement windows are defined before implementation planning is approved (DEC-024).

### 24.3 Operating cadences

| Activity | Cadence | Source |
|---|---|---|
| Dependency review | Monthly | DEC-179 |
| Critical security fixes | Prompt, outside the monthly cycle | DEC-179 |
| Isolated S3 restore verification | Monthly | DEC-181 |
| Netdata resource and service monitoring | Continuous | DEC-182 |
| External uptime checks | Continuous | DEC-182 |
| Public status updates | Automatic from health signals | DEC-161 |
| Telegram incident alerts | Event-driven | DEC-180 |
| VPS optimization before scaling | As production data requires | DEC-098, DEC-189 |
| Secret rotation and exposure investigation | Before production use; periodic thereafter | DEC-017, DEC-176 |
| Post-deployment smoke checks | Every authorized deployment | DEC-160, DEC-177 |

---

## 25. Research Gates and Unresolved Implementation-Level Choices

### 25.1 Research gate

Every new feature and material capability change requires deep, evidence-based research before its design or implementation is approved (DEC-054), delivered as a structured research brief (DEC-055), grounded in primary sources and practical verification (DEC-056), and approved explicitly by the owner (DEC-057). The rebuild coding gate remains closed until required research is complete, findings are reconciled, design is approved, and an implementation plan is reviewed (DEC-060). No benchmark program is part of any gate (DEC-066).

The 25 primary research briefs (Tracks A-E) were verified and reconciled in the final cross-domain reconciliation report (`audit-outputs/research/reconciliation-report.md`), and the owner resolved the report's category-B questions through DEC-189 to DEC-196, incorporated in this revision. Category-A recommendations remain recommendations subject to the approval gate (DEC-057) and are not requirements of this specification. Category-C defaults remain recorded conservative choices adjustable from production observability (DEC-066). Category-D source and contract inputs (Adsterra publisher terms and ad-unit code, current VPS host state, legacy traffic and demand data, and the remaining `gpt5.6-sol` gateway capability documentation) remain required before the affected technical designs finalize.

### 25.2 Explicitly excluded features

The following are confirmed non-goals rather than unresolved items: accounts (DEC-012), deadline-prediction admission control (DEC-073), paid priority lanes (DEC-134), benchmark programs (DEC-066), newsletters at relaunch (DEC-109), public counters (DEC-126), and competitor-comparison pages (DEC-128).

### 25.3 Unresolved implementation-level choices

These areas are constrained by approved decisions but not yet resolved to exact values or selections. Items below record the scope resolved by DEC-189 to DEC-196 and the remaining scope that requires research, design, or owner confirmation before implementation:

1. Compress Ghostscript distribution, hardening, and license validation. Engine selection is resolved: the official unmodified open-source Ghostscript executable runs as a separate hardened server-side subprocess with safety flags including `-dSAFER`, and Papyr does not modify, link into, or embed Ghostscript source into proprietary application code (DEC-195). Remaining: the exact production distribution and version pinning; preservation of applicable Ghostscript copyright and AGPL notices and availability of the corresponding unmodified source; and the focused license review of the chosen distribution and integration model required before public launch, with a permissive engine path or a commercial Ghostscript license as the fallback if the review outcome is unacceptable (DEC-195, DEC-059, DEC-056). Any future Ghostscript modification, linking, embedding, or architectural integration requires renewed license review and owner approval (DEC-195).
2. Exact per-tool server limits (bytes, pages, pixel counts, output counts, estimated memory) as conservative design and safety defaults with a documented raising procedure, adjusted from production observations rather than benchmark-proven, and designed around the one-concurrent-job memory budget of the initial single-worker posture (DEC-034, DEC-066, DEC-189).
3. Per-worker memory and time bounds and queue-depth safety caps. Worker count is resolved: one active PDF-processing worker with one job at a time at launch, with queueing, fairness, timeouts, and safety caps in force (DEC-189). Remaining: per-worker memory and time bounds and queue-depth safety caps under that posture, tuned from production observability (DEC-189, DEC-019, DEC-035, DEC-098).
4. Fair-scheduling class definitions, concurrency bounds, and starvation-prevention parameters without exposing defensive detail (DEC-137).
5. Redis persistence mode, eviction policy, and recovery procedure that satisfy minimal-metadata durability without document data (DEC-174, DEC-019).
6. The exact output profile for Compress and PDF to JPG (resolution, JPEG quality, downsample thresholds, quality floor) established through representative validation and production observation (DEC-014, DEC-039).
7. JPG to PDF paper-policy mapping. The region rule is resolved: Letter only when the trusted coarse edge country code is the United States or Canada; every other country, missing code, or invalid code selects A4; the active content locale does not independently select paper size; and the country code remains ephemeral and is never persisted or sent to analytics (DEC-191, DEC-083, DEC-085, DEC-089). Remaining: the implementation detail of which trusted headers carry the coarse country code and how spoofed or untrusted values are rejected (Section 5.3).
8. Malware scanner selection, update channel, and safe-failure behavior (DEC-171). The fail-closed posture is resolved: when the maintained malware-scanner or sanitization path is unavailable, affected Merge and Split jobs fail closed rather than bypassing the control (DEC-192).
9. Nginx rate-limit values and fair-use thresholds, informed by expected traffic and load-informed telemetry (DEC-020, DEC-035).
10. Exact monitoring thresholds and alert deduplication rules for Netdata, uptime checks, and Telegram (DEC-180, DEC-182).
11. Public status provider and health-signal composition (DEC-116, DEC-119, DEC-161). The legacy runbook lists BetterStack as pending.
12. Adsterra script and cookie behavior review against current provider terms and applicable law before launch. The consent risk posture is resolved: loading without prior consent in all launch regions remains an accepted business and legal risk, not a compliance claim, and Papyr must not state that the approach is GDPR, PECR, ePrivacy, UK GDPR, or Swiss FADP compliant without qualified review; if binding terms, qualified legal review, or applicable law determines that prior consent is mandatory, Papyr must implement consent controls, use demonstrably non-tracking contextual ads, or suppress ads in the affected regions (DEC-022, DEC-190, DEC-018).
13. Legal review of Privacy, Terms, and Cookies pages and their exact processing disclosures (DEC-045, DEC-168, DEC-084, DEC-085, DEC-190).
14. Contact and result-problem report anti-spam and delivery mechanisms (DEC-046, DEC-117, DEC-120).
15. Legacy URL inventory audit and the complete retain/redirect/410/noindex/removal disposition map. The default disposition is resolved: legacy URLs for tools not included in the five-tool MVP return an intentional localized 410 Gone response by default, and a specific URL may receive a targeted relevant redirect only when credible traffic or intent evidence justifies it; 410 URLs are excluded from sitemap, navigation, canonical links, and internal links (DEC-194, DEC-127, DEC-114, DEC-099). Remaining: the complete inventory of every deferred tool URL and its localized variants, and any per-URL exceptions supported by evidence.
16. Indonesian slug and content mapping for tools, legal pages, and legacy URLs (DEC-115, DEC-122).
17. Browser-processing capability detection details (memory, dimensions, encryption, corruption) and the exact routing thresholds that trigger server fallback (DEC-015, DEC-030, DEC-065). The active-content routing mechanism is resolved: when browser inspection detects PDF JavaScript, embedded attachments, launch actions, or other active content in a Merge or Split input, the job routes to the temporary server sanitization path rather than a separate browser sanitization engine (DEC-192).
18. The post-launch sequence for restoring legacy tools, chosen later from demand, readiness, complexity, cost, and the approval gate (DEC-094).
19. Operational overrides and pause/disable controls for AI-assisted automation under owner accountability (DEC-097).
20. Backup schedule, retention window, and restore-target configuration for the S3-compatible destination (DEC-173, DEC-181).
21. `gpt5.6-sol` gateway capability documentation before the blog automation technical design finalizes. Resolved contract fields (DEC-193, DEC-196): base URL `https://router.budgezen.com/v1`; exact gateway-facing model identifier `mypapyr` (the public name `gpt5.6-sol` is not substituted into API requests); `Authorization: Bearer <API_KEY>` authentication with the key stored only in protected server-side or automation secrets and never committed, logged, returned to clients, inserted into generated MDX, or exposed through analytics; gateway access only from server-side or protected automation environments; the provider adapter isolates gateway-specific configuration from the blog pipeline; the gateway is owner-managed and treated as having no known application-level rate or spending limit; and Papyr adds no internal spending guard at launch. Remaining capability documentation: request and response schema deviations, structured-output and tool-use behavior, effective context, data retention, availability, and applicable safety and compliance policy (DEC-193, DEC-196, DEC-051). Reliability controls remain mandatory and separate from spending controls: bounded request timeout, finite retry count with backoff, idempotency where supported, one bounded publication workflow, repeated-failure pause, and kill switch (DEC-196, DEC-048, DEC-053). Cross-referenced from the Product and UX Design Specification §21.21.

### 25.4 Owner decisions still required

- Review of this revision, which incorporates DEC-189 to DEC-196 and the completed reconciliation; the specifications remain approved under DEC-188 and subject to owner review of amendments.
- Approval of the resulting implementation plan after research and reconciliation (DEC-060, DEC-185).
- Explicit authorization for each production deployment (DEC-160).
- Approval for any vertical VPS upgrade, new paid service, or material cost increase (DEC-095, DEC-098).
- Explicit approval for any additional worker concurrency beyond the initial one active worker, based on capacity evidence (DEC-189, DEC-098).
- An explicit decision before any per-URL disposition deviates from the default 410 Gone response for a deferred tool URL (DEC-194).
- Approval of the blog automation technical design once the remaining `gpt5.6-sol` gateway capability documentation is supplied (DEC-196); no authenticated gateway call, account operation, or remote mutation is authorized by DEC-193 or DEC-196.

---

## 26. Self-Review Record

### 26.1 Placeholder check

This document contains no TODO, TBD, FIXME, or other placeholder tokens. Unresolved items are recorded as named choices in Section 25 with their governing decisions. No invented benchmark work, corpus, or report obligation is introduced (DEC-066).

### 26.2 Contradiction check

- The document was checked against the decision baseline DEC-001 to DEC-196 for internal consistency. Where decisions refine or supersede earlier ones (for example DEC-014 by DEC-080, DEC-086/DEC-087 by DEC-090, DEC-052 by DEC-121, DEC-116 by DEC-161, DEC-083 by DEC-191), the governing later decision is cited. The completed final cross-domain reconciliation (`audit-outputs/research/reconciliation-report.md`) surfaced seven owner questions (Q1-Q7), resolved through DEC-189 to DEC-196 and incorporated in this revision; no contradiction remains between the decisions, the reconciliation, and this document (DEC-183).
- Legacy source evidence is cited only as baseline, never as a binding requirement, consistent with DEC-001 and DEC-059.
- The superseded benchmark-related entries (DEC-061, DEC-063) are treated as history; DEC-066 governs, and this document contains no benchmark obligation.
- The pre-processing disclosure requirement superseded by DEC-168 is reflected accordingly in Section 10.4.
- No statement in this document asserts legal compliance, malware-free output, perfect sanitization, or complete isolation (DEC-022, DEC-090, DEC-171, DEC-169).

### 26.3 Ambiguity check

- Normative language ("must", "must not", "should") is used consistently per Section 1.6.
- Exact values that decisions leave open are explicitly marked as implementation-level choices in Section 25 rather than asserted as fixed.
- Design requirements are separated from implementation authorization in Section 1.5 and Section 25.1.

### 26.4 Scope check

- The document covers every area listed in the task scope: status, scope, non-goals, source precedence, monorepo boundaries, Vercel frontend, Cloudflare edge, VPS Nginx/FastAPI `/api/v1`, Docker Compose services, Redis queue, bounded workers and fair scheduling, browser/server routing, five-tool processing responsibilities, R2 lifecycle and one-hour deadline, task state machine and refresh recovery, API capability and limits contract, signed downloads, availability and failure isolation, input validation and sanitization, malware scanning and container hardening, secrets, access, logging, backups, CI gate and manual deployment and rollback, monitoring, status, Telegram, dependency maintenance, testing strategy, data classification and prohibited data, operational acceptance, research gates, and unresolved choices, plus the owner resolutions of the completed cross-domain reconciliation (DEC-189 to DEC-196).
- Product/UX concerns (copy, layout, interaction states, localization, advertising placement) are delegated to the companion Product and UX Design Specification per DEC-185 and are referenced here only where they constrain architecture.

### 26.5 Tooling limitations

- This specification was authored with read and write tools only, per the task constraints. No installs, builds, servers, VPS access, Docker operations, or network-changing commands were run.
- The markdown auto-fix workflow (`bun run lint:md:fix`) from the OCS markdown skill could not be executed: `<workspace-root>` has no root package.json or bun configuration exposing those scripts. Markdown conventions (consistent ordered-list numbering, ATX headings, well-formed tables, no placeholder text) were enforced manually instead.
- `papyr-reference/` was only read and remains unchanged (AGENTS.md).
- A correction pass on 2026-07-31 applied the owner-confirmed findings of `audit-outputs/spec-cross-review.md` and decisions DEC-186 and DEC-187: the non-goals wording (H-1), the VPS-authorization citation (M-1), the provider-documentation gate (M-2), PDF-to-JPG duplicate semantics (M-3, DEC-186), the shared progress vocabulary (M-4), JPG-to-PDF accepted formats (L-5, DEC-187), removal of superseded benchmark-default wording (L-2), regional monitoring and contact-handling requirements (L-3), and cross-reference reductions to the companion UX specification (L-4). Details and verification evidence are in `audit-outputs/spec-corrections-report.md`.
- A second revision pass on 2026-07-31 incorporated DEC-189 to DEC-196 and the completed final cross-domain reconciliation (`audit-outputs/research/reconciliation-report.md`): one-active-worker, one-concurrent-job concurrency (DEC-189); the reaffirmed no-prior-consent advertising risk (DEC-190); the US/Canada-only Letter rule (DEC-191); active-content Merge and Split routing to server sanitization with fail-closed behavior (DEC-192); the `gpt5.6-sol` gateway contract and mandatory reliability controls (DEC-193, DEC-196); the localized 410 Gone default for deferred tool URLs (DEC-194); and the official unmodified Ghostscript Compress subprocess with a license-validation gate (DEC-195). Section 25.3 items were narrowed accordingly without renumbering. Details and verification evidence are in `audit-outputs/architecture-spec-revision-dec189-196.md`.

---

## Appendix A. Decision Map

| Specification section | Governing decisions |
|---|---|
| 1. Scope, status, authority | DEC-001, DEC-006, DEC-026, DEC-054 to DEC-060, DEC-066, DEC-183 to DEC-196 |
| 2. System context and topology | DEC-002, DEC-009, DEC-011, DEC-017, DEC-019, DEC-162, DEC-163, DEC-170, DEC-189 |
| 3. Monorepo boundaries | DEC-006, DEC-026, DEC-099, DEC-159 |
| 4. Vercel frontend | DEC-004, DEC-017, DEC-018, DEC-022, DEC-023, DEC-025, DEC-028, DEC-031, DEC-032, DEC-047, DEC-102, DEC-115, DEC-118, DEC-119, DEC-122, DEC-143, DEC-151, DEC-163, DEC-165, DEC-168, DEC-190, DEC-193, DEC-194 |
| 5. Cloudflare edge | DEC-017, DEC-021, DEC-083, DEC-085, DEC-089, DEC-176, DEC-191 |
| 6. VPS Nginx and FastAPI | DEC-017, DEC-019, DEC-160, DEC-162, DEC-164 |
| 7. Docker Compose services | DEC-019, DEC-162, DEC-169, DEC-178 |
| 8. Redis queue | DEC-019, DEC-035, DEC-162, DEC-174 |
| 9. Bounded workers and fair scheduling | DEC-019, DEC-020, DEC-035, DEC-066, DEC-069, DEC-098, DEC-134, DEC-137, DEC-167, DEC-189 |
| 10. Browser/server routing | DEC-011, DEC-015, DEC-030, DEC-033, DEC-065, DEC-163, DEC-168, DEC-192 |
| 11. Five-tool processing | DEC-010, DEC-014, DEC-037 to DEC-043, DEC-064, DEC-074, DEC-076 to DEC-084, DEC-088, DEC-090 to DEC-093, DEC-118, DEC-186, DEC-187, DEC-191, DEC-192, DEC-195 |
| 12. R2 lifecycle and one-hour deadline | DEC-013, DEC-067, DEC-070, DEC-075, DEC-166, DEC-170, DEC-173, DEC-174 |
| 13. Task state machine and recovery | DEC-019, DEC-029, DEC-032, DEC-033, DEC-069, DEC-071, DEC-072, DEC-073 |
| 14. API capability and limits contract | DEC-020, DEC-034, DEC-064, DEC-088, DEC-164, DEC-165 |
| 15. Signed downloads | DEC-029, DEC-037, DEC-068, DEC-131, DEC-170 |
| 16. Availability and failure isolation | DEC-017, DEC-096, DEC-098, DEC-119, DEC-163, DEC-167 |
| 17. Validation, sanitization, malware, hardening | DEC-088, DEC-090 to DEC-093, DEC-169, DEC-171, DEC-192 |
| 18. Secrets, access, logging, backups | DEC-017, DEC-036, DEC-160, DEC-172 to DEC-176, DEC-181, DEC-193, DEC-196 |
| 19. CI gate, manual deployment, rollback | DEC-060, DEC-096, DEC-097, DEC-160, DEC-177, DEC-178, DEC-179 |
| 20. Monitoring, status, Telegram | DEC-104, DEC-116, DEC-119, DEC-161, DEC-180, DEC-182 |
| 21. Dependency maintenance | DEC-010, DEC-056, DEC-179 |
| 22. Testing strategy | DEC-013, DEC-025, DEC-027, DEC-031, DEC-062, DEC-066, DEC-067, DEC-079, DEC-081, DEC-090, DEC-160, DEC-177 |
| 23. Data classification and prohibited data | DEC-013, DEC-025, DEC-032, DEC-036, DEC-042, DEC-046, DEC-050, DEC-067, DEC-072, DEC-117, DEC-120, DEC-170, DEC-173 to DEC-176, DEC-180 |
| 24. Operational acceptance | DEC-024, DEC-027, DEC-096, DEC-100, DEC-103, DEC-110, DEC-118, DEC-160, DEC-177, DEC-181, DEC-189 |
| 25. Research gates and unresolved choices | DEC-022, DEC-034, DEC-037, DEC-051, DEC-054 to DEC-060, DEC-066, DEC-073, DEC-094, DEC-095, DEC-097, DEC-098, DEC-137, DEC-171, DEC-189 to DEC-196 |

## Appendix B. Legacy Source Evidence Index

The following paths under `papyr-reference/` were inspected as baseline evidence for this specification. They are read-only reference material (AGENTS.md, DEC-001, DEC-059).

| Path | What it evidences |
|---|---|
| `backend/main.py` | FastAPI application shell, lifespan cleanup loop, CORS allowlist, rate-limit handler, router mounting, `/health` |
| `backend/utils/config.py` | Centralized settings: `MAX_UPLOAD_SIZE_MB` (20), `FILE_RETENTION_MINUTES` (60), `RATE_LIMIT_PER_MINUTE` (10) |
| `backend/utils/r2.py` | R2 client, UUID object keys, `SIGNED_URL_EXPIRY_SECONDS`, force-download signed URLs |
| `backend/utils/cleanup.py` | Legacy 30-minute cleanup loop scanning for expired objects |
| `backend/utils/pdf_validator.py` | PDF validation order: empty, MIME, extension, magic bytes, size, page count, encrypted |
| `backend/utils/logging_config.py` | JSON structured logging with explicit no-content prohibitions |
| `backend/services/async_task.py` | Legacy in-memory task store, TTL 2 hours, states queued/processing/done/failed |
| `backend/services/encryption.py` | AES-128/AES-256 PDF encryption and decryption via PyMuPDF |
| `backend/routers/compress.py` | Legacy compress endpoint, quality presets, signed URL, saved-percent reporting |
| `backend/routers/status.py` | Legacy `/api/status/{task_id}` polling endpoint |
| `backend/routers/connectivity.py` | Legacy R2 connectivity test endpoint |
| `backend/Dockerfile.production` | Multi-stage build, non-root user, tini, healthcheck, four uvicorn workers, engine dependencies |
| `backend/requirements.txt` | Dependency inventory including non-MVP OCR/office stacks |
| `deploy/docker-compose.yml` | Production stack hardening: read-only fs, caps, limits, tmpfs, env mount, healthchecks |
| `deploy/nginx/conf.d/default.conf` | Default-host drop behavior |
| `deploy/nginx/conf.d/production.conf` | Rate zones, bot and path maps, real-IP handling, security headers, proxying |
| `deploy/.env.production.example` | Production environment template and install procedure |
| `.github/workflows/ci.yml` | Legacy CI jobs (frontend lint/test/build, backend Ruff and pytest) |
| `.github/workflows/deploy-vps.yml` | Legacy automated deploy: build, Trivy gate, SBOM, GHCR, SSH deploy, smoke, rollback |
| `docs/runbook-vps.md` | VPS operations baseline: SSH, deploy, rollback, logs, OOM, SSL, backups (restic), incident response, monitoring, compliance cadence |
| `frontend/src/lib/config.ts` | Legacy mirrored limits (20 MB, 60 minutes) |
| `frontend/src/lib/pdfUtils.ts` | Browser-side merge, split, image-to-PDF, page count, download helpers |
| `frontend/src/hooks/useAsyncTask.ts` | Legacy polling hook: 3-second interval, 180-second timeout, status mapping |
| `frontend/src/app/*` (five tool pages), `frontend/src/components/*` | Tool page and shared-component baseline documented in `audit-outputs/ui-five-tools-audit.md` and `audit-outputs/ui-home-shell-audit.md` |
| `audit-outputs/ui-five-tools-audit.md` | Page-by-page UX audit of the five launch tools with line-level evidence |
| `audit-outputs/ui-home-shell-audit.md` | Global visual system, navbar, footer, homepage audit |
| `audit-outputs/ui-docs-code-reconciliation.md` | Documentation versus implementation reconciliation |
