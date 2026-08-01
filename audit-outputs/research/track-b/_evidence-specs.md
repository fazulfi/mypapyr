# Track B Specification Evidence — Papyr Rebuild Research

| Field | Value |
|---|---|
| Deliverable | Track B (browser routing, accessibility, i18n/paper policy, SEO/URL migration, UI baseline) specification evidence extraction |
| Primary sources (read in full, read-only) | `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` (728 lines); `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` (1188 lines) |
| Extraction date | 2026-07-31 |
| Method | Full-file reads; verbatim quotes with source line ranges; item IDs preserved exactly (D1-D13, U1/U2/U3/U5/U7, UX section 21 items 1-21, arch section 25.3 items 1-21) |
| Evidence standard | Verbatim quotes inside fenced code blocks, each annotated with the source line range. Long tables quoted with relevant rows and row counts noted. |
| Skills applied | Context-grooming (structured evidence); ocs-markdown-autofix conventions (ATX headings, ordered lists, well-formed tables) |
| Constraints honored | No file modified except this evidence file; `papyr-reference/` unchanged; no installs, builds, servers, VPS access, or network-changing commands |

## Scope and method

Track B covers: browser routing (browser/server processing boundaries, capability detection, progressive enhancement), accessibility (WCAG 2.2 AA), i18n and paper policy (EN/ES/ID localization, locale routing, Letter/A4), SEO and URL migration (slugs, canonicals, hreflang, sitemaps, redirects), and the UI baseline (shell/nav/footer/homepage/tool surfaces, defects D1-D13, audit uncertainties U1-U7 as referenced by the specs).

Both specs were read in full (UX: lines 1-728; arch: lines 1-1188). All mandated sections are quoted verbatim below. Cross-check greps for `D/U` item IDs, `WCAG|accessib|aria-|keyboard|screen-reader|prefers-reduced-motion`, `A4|Letter|paper`, `hreflang|canonical|sitemap|robots|redirect|slug|SEO|metadataBase`, `locale|language|translat|lang`, and `browser|capabilit|progressive enhancement` were run against both files to ensure no Track-B mention was missed.

## 1. Specification headers and tables of contents

### 1.1 Product and UX Design Specification — header fields

Source: `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` lines 1-10.

```text
1: # Papyr Rebuild: Product and UX Design Specification
2:
3: - **Document type:** Canonical design specification (English)
4: - **Date:** 2026-07-31
5: - **Status:** For owner review (approved for writing by DEC-183; not an implementation authorization)
6: - **Sibling document:** Technical Architecture Specification (DEC-185)
7: - **Decision baseline:** DEC-001 through DEC-187 in `papyr-rebuild-decisions.md`
8: - **Primary reference baseline:** `papyr-reference/` (read-only legacy clone), per DEC-143
```

Canonical language: English (header field line 3; also UX section 9 item 1 line 173: "English is the canonical language for design documents; the public product is localized in EN, ES, and ID (DEC-184, DEC-115, DEC-118)").

### 1.2 Product and UX Design Specification — table of contents with line ranges

| Section | Title | Lines |
|---|---|---|
| 1 | Status | 12-20 |
| 2 | Scope | 22-40 |
| 3 | Non-goals | 42-63 |
| 4 | Sources and precedence | 65-82 |
| 4.1 | Evidence conventions used in this document | 77-82 |
| 5 | Product goals | 84-95 |
| 6 | Users | 97-107 |
| 7 | Launch scope | 109-123 |
| 8 | Information architecture | 125-169 |
| 8.1 | Model | 127-129 |
| 8.2 | Routes and locale prefixes | 131-157 |
| 8.3 | Navigation model | 159-161 |
| 8.4 | Catalog single source of truth | 163-165 |
| 8.5 | Related tools | 167-169 |
| 9 | Localization: EN, ES, and ID | 171-181 |
| 10 | Existing visual baseline (DEC-143) | 183-282 |
| 10.1 | Design tokens | 187-204 |
| 10.2 | Typography | 206-213 |
| 10.3 | Spacing, radius, shadows, motion | 215-225 |
| 10.4 | Component character | 227-240 |
| 10.5 | Baseline strengths to preserve | 242-256 |
| 10.6 | Documented defects to correct | 258-278 |
| 10.7 | Approved visual changes only | 280-282 |
| 11 | Shell and homepage | 284-324 |
| 11.1 | Root shell | 286-294 |
| 11.2 | Navbar | 296-304 |
| 11.3 | Footer | 306-313 |
| 11.4 | Homepage | 315-324 |
| 12 | Five detailed tool flows | 326-457 |
| 12.0 | Shared flow anatomy | 328-345 |
| 12.1 | Compress PDF | 347-368 |
| 12.2 | Merge PDF | 370-390 |
| 12.3 | Split PDF | 392-413 |
| 12.4 | JPG to PDF | 415-435 |
| 12.5 | PDF to JPG | 437-457 |
| 13 | Shared states | 459-508 |
| 13.1 | State model | 463-481 |
| 13.2 | Download behavior | 483-489 |
| 13.3 | Result availability and expiry | 491-497 |
| 13.4 | Cancellation, reset, and tab lifecycle | 499-504 |
| 13.5 | Honest progress | 506-508 |
| 14 | Advertising placement | 510-522 |
| 15 | Content, legal, support, status, and blog surfaces | 524-550 |
| 15.1 | Tool pages as content | 526-528 |
| 15.2 | Legal pages | 530-532 |
| 15.3 | Support | 534-538 |
| 15.4 | Status | 540-542 |
| 15.5 | Roadmap | 544-546 |
| 15.6 | Blog | 548-550 |
| 16 | Responsive and accessibility (WCAG 2.2 AA) | 552-582 |
| 16.1 | Responsive behavior | 554-561 |
| 16.2 | WCAG 2.2 Level AA acceptance coverage | 563-576 |
| 16.3 | Browser support and testing | 578-582 |
| 17 | Analytics and privacy UX boundaries | 584-596 |
| 18 | Error and recovery behavior | 598-610 |
| 19 | SEO and content migration constraints | 612-623 |
| 20 | Acceptance criteria | 625-693 |
| 20.1 | Launch completeness | 629-638 |
| 20.2 | Visual continuity | 640-644 |
| 20.3 | Interaction correctness | 646-660 |
| 20.4 | Tool-specific behavior | 662-668 |
| 20.5 | Accessibility | 670-674 |
| 20.6 | Advertising and performance | 676-682 |
| 20.7 | Localization | 684-689 |
| 20.8 | Schedule | 691-693 |
| 21 | Unresolved items requiring later research | 695-719 |
| 22 | Relationship to the Technical Architecture Specification | 721-728 |
### 1.3 Technical Architecture Specification — header fields

Source: `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` lines 1-13.

```text
1: # Papyr Technical Architecture Specification
2:
3: | Field | Value |
4: |---|---|
5: | Document ID | PPR-TA-001 |
6: | Title | Papyr Rebuild Technical Architecture Specification |
7: | Version | 1.0 (draft for owner review) |
8: | Date | 2026-07-31 |
9: | Canonical language | English (DEC-184) |
10: | Status | Draft, ready for owner review; not an implementation authorization |
11: | Decision baseline | papyr-rebuild-decisions.md, DEC-001 through DEC-187 |
12: | Companion document | Product and UX Design Specification (separate document per DEC-185) |
13: | Governing rules | AGENTS.md (Papyr Rebuild Orchestrator Rules) |
```

### 1.4 Technical Architecture Specification — table of contents with line ranges

| Section | Title | Lines |
|---|---|---|
| 1 | Scope, Status, and Authority | 17-97 |
| 1.1 | Status | 19-23 |
| 1.2 | Scope | 25-47 |
| 1.3 | Non-goals | 49-68 |
| 1.4 | Source precedence | 70-80 |
| 1.5 | Design versus implementation authorization | 82-90 |
| 1.6 | Conventions used in this document | 92-97 |
| 2 | System Context and Topology | 101-168 |
| 2.1 | Approved topology | 103-117 |
| 2.2 | Data flow at a glance | 119-135 |
| 2.3 | Components and responsibilities | 137-148 |
| 2.4 | Request flows | 150-168 |
| 3 | Monorepo Boundaries | 172-201 |
| 3.1 | Single repository | 174-178 |
| 3.2 | Directory and package boundaries | 180-194 |
| 3.3 | What is excluded from the monorepo | 196-201 |
| 4 | Vercel Next.js Frontend | 205-246 |
| 4.1 | Role and hosting | 207-211 |
| 4.2 | Routing and localization | 213-219 |
| 4.3 | Server and browser responsibilities | 221-227 |
| 4.4 | Frontend configuration and environment | 229-233 |
| 4.5 | Analytics and advertising | 235-240 |
| 4.6 | Availability behavior | 242-246 |
| 5 | Cloudflare Edge (Domain and API) | 250-276 |
| 5.1 | Domain and DNS | 252-254 |
| 5.2 | API edge routing | 256-258 |
| 5.3 | Edge-derived country context | 260-270 |
| 5.4 | TLS and security posture | 272-276 |
| 6 | VPS: Nginx and FastAPI `/api/v1` | 280-320 |
| 6.1 | VPS role | 282-286 |
| 6.2 | Nginx reverse proxy | 288-301 |
| 6.3 | FastAPI application boundary | 303-316 |
| 6.4 | API versioning | 318-320 |
| 7 | Docker Compose Services | 324-367 |
| 7.1 | Compose stack | 326-330 |
| 7.2 | Service inventory | 332-340 |
| 7.3 | Hardening baseline | 342-354 |
| 7.4 | Resource bounds and health | 356-361 |
| 7.5 | Startup dependencies and networking | 363-367 |
| 8 | Redis Durable Minimal-Metadata Queue | 371-405 |
| 8.1 | Role | 373-375 |
| 8.2 | What is persisted | 377-389 |
| 8.3 | Queue behavior | 391-398 |
| 8.4 | Redis operations and recovery | 400-405 |
| 9 | Bounded Workers and Fair Scheduling | 409-458 |
| 9.1 | Worker processes | 411-419 |
| 9.2 | Bounds | 421-426 |
| 9.3 | Fair scheduling policy | 428-440 |
| 9.4 | Queueing under pressure | 442-444 |
| 9.5 | Cancellation | 446-454 |
| 9.6 | Failure isolation per tool | 456-458 |
| 10 | Browser/Server Routing | 462-496 |
| 10.1 | Hybrid model | 464-466 |
| 10.2 | Browser-first jobs and limits | 468-479 |
| 10.3 | Automatic server fallback | 481-488 |
| 10.4 | Disclosure of processing location | 490-492 |
| 10.5 | Backend-outage behavior | 494-496 |
| 11 | Five-Tool Processing Responsibilities | 500-563 |
| 11.1 | Shared foundations | 504-512 |
| 11.2 | Compress PDF | 514-522 |
| 11.3 | Merge PDF | 524-532 |
| 11.4 | Split PDF | 534-542 |
| 11.5 | JPG to PDF | 544-553 |
| 11.6 | PDF to JPG | 555-563 |
| 12 | R2 Object Lifecycle and the Absolute One-Hour Deadline | 567-604 |
| 12.1 | Storage model | 569-571 |
| 12.2 | Retention clock | 573-581 |
| 12.3 | Active deletion and lifecycle safety net | 583-591 |
| 12.4 | Expiry-while-open and post-download retention | 593-598 |
| 12.5 | Object key hygiene | 600-604 |
| 13 | Task State Machine and Refresh Recovery Contract | 608-660 |
| 13.1 | States and transitions | 610-630 |
| 13.2 | Progress model | 632-634 |
| 13.3 | Timeouts, retries, and failures | 636-642 |
| 13.4 | Session recovery | 644-653 |
| 13.5 | Status API contract | 655-660 |
| 14 | API Capability and Limits Contract | 664-689 |
| 14.1 | Canonical machine-readable contract | 666-673 |
| 14.2 | Per-tool server limits | 675-677 |
| 14.3 | Fair-use controls | 679-681 |
| 14.4 | Error and rejection semantics | 683-689 |
| 15 | Signed Downloads | 693-717 |
| 15.1 | Signed R2 URLs | 695-699 |
| 15.2 | Expiry relationship | 701-705 |
| 15.3 | Download behavior | 707-717 |
| 16 | Availability and Failure Isolation | 721-740 |
| 16.1 | Failure domains | 723-728 |
| 16.2 | Per-tool readiness | 730-732 |
| 16.3 | Frontend during backend outage | 734-736 |
| 16.4 | Scaling policy | 738-740 |
| 17 | Input Validation, Sanitization, Malware Scanning, and Container Hardening | 744-803 |
| 17.1 | Defense layers | 746-757 |
| 17.2 | File validation | 759-765 |
| 17.3 | Active-content sanitization | 767-776 |
| 17.4 | Threat blocking | 778-780 |
| 17.5 | Malware scanning | 782-784 |
| 17.6 | Container and process hardening | 786-796 |
| 17.7 | Honest limits of these controls | 798-803 |
| 18 | Secrets, Access, Logging, and Backups | 807-850 |
| 18.1 | Secrets management | 809-818 |
| 18.2 | VPS access | 820-827 |
| 18.3 | Logging policy | 829-837 |
| 18.4 | Backups | 839-850 |
| 19 | CI Core Gate, Manual Deployment, and Rollback | 854-889 |
| 19.1 | CI core gate | 856-863 |
| 19.2 | Manual production deployment | 865-873 |
| 19.3 | Rollback | 875-883 |
| 19.4 | Release traceability | 885-889 |
| 20 | Monitoring, Status, and Telegram | 893-912 |
| 20.1 | Netdata and external uptime | 895-897 |
| 20.2 | Public status experience | 899-908 |
| 20.3 | Telegram alerts | 910-912 |
| 21 | Dependency Maintenance | 916-925 |
| 22 | Testing Strategy | 929-964 |
| 22.1 | Principles | 931-935 |
| 22.2 | Layers | 937-944 |
| 22.3 | Privacy and retention verification | 946-951 |
| 22.4 | Browser and device coverage | 953-958 |
| 22.5 | What testing is not | 960-964 |
| 23 | Data Classification and Prohibited Data | 968-1005 |
| 23.1 | Classes | 970-979 |
| 23.2 | Prohibited-data register | 981-993 |
| 23.3 | Retention summary | 995-1005 |
| 24 | Operational Acceptance Criteria | 1010-1043 |
| 24.1 | Launch gate | 1012-1014 |
| 24.2 | Reliability and performance criteria | 1016-1028 |
| 24.3 | Operating cadences | 1030-1043 |
| 25 | Research Gates and Unresolved Implementation-Level Choices | 1047-1088 |
| 25.1 | Research gate | 1049-1051 |
| 25.2 | Explicitly excluded features | 1053-1055 |
| 25.3 | Unresolved implementation-level choices | 1057-1081 |
| 25.4 | Owner decisions still required | 1083-1088 |
| 26 | Self-Review Record | 1092-1122 |
| 26.1 | Placeholder check | 1094-1096 |
| 26.2 | Contradiction check | 1098-1104 |
| 26.3 | Ambiguity check | 1106-1110 |
| 26.4 | Scope check | 1112-1115 |
| 26.5 | Tooling limitations | 1117-1122 |
| Appendix A | Decision Map | 1126-1154 |
| Appendix B | Legacy Source Evidence Index | 1156-1188 |
## 2. Product and UX Design Specification — verbatim quotes

### 2.1 UX Section 21 in FULL — Unresolved items requiring later research (lines 695-719)

All 21 items quoted verbatim. Item IDs referenced inside the section: D3 (item 13), U2 (item 13), U3 (item 14), U5 and D12 (item 15), U7 (item 11), U1 (item 19).

```text
695: ## 21. Unresolved items requiring later research
697: These items are deliberately not decided by this specification. Each requires owner input, SEO design, or the research and approval gates in DEC-054 through DEC-057. Item 20 records a confirmed deferral with future work rather than an unresolved choice.
699: 1. **Exact per-tool server limits** and browser-limit adjustments after anonymous reliability telemetry and real-device testing (DEC-015, DEC-034). Conservative defaults documented as design and safety choices, adjusted from production observations rather than benchmark-proven, and the procedure for raising them are technical-design responsibilities (DEC-066).
700: 2. **Compress engine profile thresholds.** The "premium screen quality" profile's internal thresholds (downsampling, re-encoding, quality floors) are set during technical design and validated through normal functional testing, without a benchmark program (DEC-014, DEC-066).
701: 3. **Paper-standard regional rule details.** How the active locale maps to Letter/A4 when the trusted edge country is missing or when EN spans US and non-US markets (DEC-083, DEC-085, DEC-089). A4 is the deterministic fallback; the user-visible summary wording is finalized in the copy pass.
702: 4. **Tool slugs for EN/ES/ID** and the legacy URL redirect map, selected during SEO design (DEC-023, DEC-122, DEC-127).
703: 5. **Launch blog topic selection** for the five topics and the daily post-launch topic pipeline details (DEC-052, DEC-053, DEC-124).
704: 6. **Indonesian coverage extent at relaunch**, reconciled with the one-month schedule and the complete-over-deadline policy (DEC-115, DEC-118, DEC-103).
705: 7. **Contact form provider, anti-spam approach, and delivery monitoring** for the owner-managed inbox (DEC-046, DEC-050).
706: 8. **Status page implementation details** and health-signal noise resistance (DEC-116, DEC-119, DEC-161).
707: 9. **Adsterra script, cookie, identifier, and regional behavior review** against current terms and applicable law, including whether prior consent is required (DEC-022, DEC-045).
708: 10. **Legal review** of Privacy, Terms, and Cookies/Advertising copy before launch (DEC-045).
709: 11. **Rendered visual verification** of the baseline: all three audits were static source inspections, so spacing, contrast, and font rendering claims must be spot-checked in a browser during implementation (`audit-outputs/ui-home-shell-audit.md` U7; `audit-outputs/ui-five-tools-audit.md` §8.1).
710: 12. **Contrast re-verification** of the documented token combinations with a contrast tool (DEC-062; `audit-outputs/ui-docs-code-reconciliation.md` §8.2).
711: 13. **Navbar width intent:** 1440px navbar container versus 1200px content elsewhere (D3) needs owner confirmation before unification (`audit-outputs/ui-home-shell-audit.md` U2).
712: 14. **Duplicate CTA intent:** navbar "Try free" and hero CTA both target the Compress page in the legacy site; confirm whether the funnel is deliberate (U3).
713: 15. **Homepage entrance animations:** the homepage has no entrance animations while tool pages use fade-up; decide whether to unify or keep the calm hero deliberately (U5), which also resolves the dropdown-panel transition question (D12).
714: 16. **Merge error-state edge case:** legacy behavior keeps state at error when a valid file is added alongside an invalid one during an error state; confirm the desired auto-clear behavior (`audit-outputs/ui-five-tools-audit.md` §8.7).
715: 17. **Privacy copy re-scoping** of legacy "no tracking" and "no personal data" statements against the accepted analytics and advertising model, with qualified review (DEC-025, DEC-022; `audit-outputs/ui-docs-code-reconciliation.md` §8.8).
716: 18. **FAQ copy accuracy:** the officially accepted JPG-to-PDF input formats are JPG/JPEG, PNG, and WebP (DEC-187); FAQ and tool copy must state these accurately, correcting the legacy claims noted at `audit-outputs/ui-docs-code-reconciliation.md` §8.9.
717: 19. **`@theme inline` token emission verification** so the body background, text color, and font never silently fall back (Section 10.1; `audit-outputs/ui-home-shell-audit.md` U1).
718: 20. **Newsletter deferral (confirmed, not unresolved).** The newsletter is deferred at launch (DEC-107, DEC-109); no launch action, but provider and consent design return before any later implementation.
719: 21. **`gpt5.6-sol` provider documentation** before technical design finalization: base URL, authentication, request/response schema, structured-output support, tool-use capabilities, rate limits, cost, context limits, retry behavior, data retention, and availability (DEC-051). Provider integration stays isolated behind an interface so publishing can be paused or migrated (DEC-051).
```
### 2.2 UX Section 16 in FULL — Responsive and accessibility (WCAG 2.2 AA) (lines 552-582)

```text
552: ## 16. Responsive and accessibility (WCAG 2.2 AA)
554: ### 16.1 Responsive behavior
556: 1. Mobile-first layout with the existing Tailwind breakpoints (`sm`, `md`, `lg`) and the baseline fluid hero type (Section 10.3).
557: 2. Navbar: desktop category dropdowns, mobile compact CTA plus the native accordion panel (DEC-155).
558: 3. Tool pages: `max-w-xl` shell with full-width actions; feature grids collapse from 3 columns to 1; thumbnail grids from 3 to 2 columns; sortable lists stack full-width (audit evidence: `frontend/src/app/image-to-pdf/page.tsx:710`).
559: 4. Footer and homepage sections wrap and stack within the 1200px content column.
560: 5. No horizontal overflow; containers keep `px-6`/`px-4` gutters and the nav center section keeps `min-w-0` (audit evidence: `frontend/src/components/Navbar.tsx:163`).
561: 6. Localized copy length must not break layouts (Section 9); Spanish and Indonesian text is verified at all breakpoints.
563: ### 16.2 WCAG 2.2 Level AA acceptance coverage
565: WCAG 2.2 Level AA is the acceptance target for product pages, all five tools, blog, legal pages, and contact/support interfaces (DEC-062). Acceptance coverage includes:
567: 1. **Keyboard operation:** all interactive controls operable by keyboard, including dropzones (Enter/Space), sortable reordering, dropdowns, accordions, the language switcher, range inputs, and reset actions. Drag-and-drop always has a non-drag alternative (DEC-040, DEC-062).
568: 2. **Visible focus:** consistent `focus-visible` styling on every control. The legacy app has only one custom focus ring (in the sign overlay); the rebuild adds it app-wide (`audit-outputs/ui-docs-code-reconciliation.md` §3.4).
569: 3. **Contrast:** text and interactive elements meet AA contrast, including slate-400/300 tertiary text and accent-tinted states. Contrast values from the legacy docs are re-verified with a contrast tool during implementation (`audit-outputs/ui-docs-code-reconciliation.md` §8.2).
570: 4. **Semantic structure:** correct heading hierarchy (no h1-to-h3 jumps, audit §6 item 8), landmark regions, a `main` landmark, and a skip-to-content link (D8).
571: 5. **Accessible names and errors:** labels on all inputs, `aria-label` on icon-only controls (drag handles, remove buttons, hamburger), and error text wired with `aria-invalid` and `aria-describedby` where appropriate (`audit-outputs/ui-five-tools-audit.md` §6 item 7).
572: 6. **Status and progress announcements:** `role="status"` or `aria-live="polite"` on processing and ready transitions, `role="alert"` on error cards, and `role="progressbar"` with `aria-valuenow` on determinate upload progress (audit §6 item 7). Screen-reader announcements for dnd-kit reordering via the `announcements` API (audit §6 item 7, §8.5).
573: 7. **Target sizing and spacing:** WCAG 2.2 target-size minimums for controls, verified at all breakpoints (DEC-062).
574: 8. **Zoom and reflow:** layouts function at 200% zoom and 320px width without loss of content or functionality (DEC-062, DEC-031).
575: 9. **Reduced motion:** the shimmer and fade-up animations respect `prefers-reduced-motion` (DEC-062).
576: 10. **Localized content resilience:** announcements, labels, and errors are localized; message length growth does not break layouts (DEC-062, Section 9).
578: ### 16.3 Browser support and testing
580: Officially supported browsers are the latest two major versions of Chrome, Edge, Firefox, and Safari on desktop, current Safari on iOS/iPadOS, and Chrome on Android (DEC-031). Progressive enhancement and ordinary file-input/download fallbacks are required where Chromium-specific file APIs are unavailable (DEC-031). Unsupported browsers receive a clear compatibility message or a server-processing path rather than silent failure (DEC-031).
582: Automated accessibility checks are necessary but insufficient; representative manual keyboard and assistive-technology testing is required (DEC-062). Known exceptions are documented with impact and remediation rather than silently treated as compliant, and public wording must not claim certification or universal conformance unless independently substantiated (DEC-062).
```
### 2.3 UX Section 17 in FULL — Analytics and privacy UX boundaries (lines 584-596)

```text
584: ## 17. Analytics and privacy UX boundaries
586: 1. Analytics collect detailed product events, funnels, attribution, performance, and sanitized error analytics, but never session replay on document workflows, fingerprinting data, or document-sensitive information (DEC-025).
587: 2. Allowed: acquisition source, page and locale, tool selection, processing mode, coarse input bands, funnel stages, timings, sanitized failure categories, download completion, Web Vitals, and advertising performance where permitted (DEC-025).
588: 3. Prohibited from analytics, monitoring, logs, and error reporting: file contents, previews, rendered document text, file names, object keys, signed URLs, passwords, full error payloads containing user data, and stable device fingerprints (DEC-025, DEC-042, DEC-117).
589: 4. Event schemas require privacy review, data-retention policy, regional activation controls, and automated tests or audits guarding against sensitive-field leakage (DEC-025).
590: 5. The uploader carries no dedicated processing disclosure; full local-versus-server and retention information lives on the Privacy page, with an accessible path from the uploader (DEC-168). Workflow states still label uploading, queued, and server processing truthfully when they occur (DEC-168).
591: 6. JPG to PDF discloses that source metadata, including EXIF GPS and device information, may remain in the result (DEC-084); metadata is never sent to analytics or general logs (DEC-084).
592: 7. Privacy copy is re-scoped: legacy claims such as "no tracking" and "no personal data at all" (`frontend/src/app/privacy/page.tsx:47,73`, `frontend/src/app/faq/page.tsx:61`) conflict with the accepted analytics and advertising model and are corrected (`audit-outputs/ui-docs-code-reconciliation.md` §6, §8.8).
593: 8. No public usage counters; aggregate metrics stay private in a future admin dashboard that is not launch scope (DEC-126).
594: 9. Password handling in the UI: passwords are entered only when required, held in memory for the shortest practical time, and never written to logs, analytics, URLs, dashboards, persistent queues, storage, backups, or error payloads (DEC-036, DEC-064, DEC-074).
595: 10. Result-problem reports follow the data boundaries in Section 15.3 (DEC-117, DEC-120).
596: 11. Regional monitoring and launch communication distinguish the US, LATAM, and Europe regions sufficiently to identify material failures in each, without prohibited user profiling (DEC-104).
```

### 2.4 UX Section 18 in FULL — Error and recovery behavior (lines 598-610)

Note: UX Section 18 is titled "Error and recovery behavior"; it is the spec's security-adjacent behavioral surface (safe rejection, routing transparency, failure handling). Security controls proper live in the Technical Architecture Specification.

```text
598: ## 18. Error and recovery behavior
600: 1. **Inline error cards.** Ordinary processing failures use the existing inline error-card pattern with localized language and only valid retry, reset, password, or support-report actions for the failure type; error regions are announced without stealing focus (DEC-158).
601: 2. **Safe rejection categories.** Rejections expose only safe general categories and never reveal exploit, scanner, or engine internals (DEC-169, DEC-171). Files classified as threats to infrastructure are blocked, never processed or returned, with a safe localized rejection and prompt cleanup (DEC-088). False-positive handling and support escalation never require users to email or upload the rejected document through the contact form or any other channel (DEC-088).
602: 3. **Sanitization notice.** When active content is detected and removed, the UI shows the general categories removed without payload details (DEC-091). Sanitization is distinguished from malware detection, and the result does not imply that no other threat exists (DEC-091).
603: 4. **Routing transparency.** Jobs that fall back to the server show the transition visibly and do not claim the file stayed on-device (DEC-030, DEC-065). Failure classes such as security-policy failures, unsupported content, invalid passwords, user cancellation, and unsafe conditions fail closed rather than forcing a server upload (DEC-065).
604: 5. **Retry semantics.** Server retry follows the legacy auto-retry pattern with a visible retrying label, a cleared timer on unmount or reset, and no indefinite retry loops (DEC-030; audit §6 item 4). If the server also cannot recover the file, the user receives a clear, actionable failure (DEC-030).
605: 6. **Rate limiting and abuse controls.** Adaptive anonymous fair-use controls may delay, reject, or selectively challenge suspicious traffic with clear retry responses; ordinary users do not face a fixed daily quota (DEC-020). Messages are clear and actionable.
606: 7. **Backend outage.** Tool pages stay accessible; browser-capable operations continue locally; server-dependent processing clearly communicates temporary unavailability; the frontend does not redirect ordinary tool traffic to the status page (DEC-163). Repeated submissions and misleading progress are prevented (DEC-163).
607: 8. **Expiry.** Server results show an accurate countdown and warn before deletion; expired results cannot be restored (DEC-067).
608: 9. **Blocked download.** A blocked auto-download leaves the job in Ready state with the manual button (DEC-068).
609: 10. **Cancel and refresh.** Queued-job cancellation is honored atomically; refresh recovers an active job within the same tab via `sessionStorage` (DEC-069, DEC-072).
610: 11. **Support escalation.** Result-problem reports and the contact form route to the owner-managed support process without requesting document attachments (DEC-046, DEC-050, DEC-117).
```

### 2.5 UX Section 15.6 in FULL — Blog (lines 548-550)

```text
548: ### 15.6 Blog
550: The blog is a separate content surface from tool pages (DEC-044). Launch inventory is five topics, each intentionally localized into EN, ES, and ID (DEC-052, DEC-121). Articles visibly display original publication and latest material update dates, truthfully and locale-formatted (DEC-113). Content is version-controlled MDX in the repository (DEC-049); the automated LLM workflow uses the owner's `gpt5.6-sol` provider (DEC-051) with blocking quality gates that fail closed, including factual support, duplication and cannibalization, search intent, originality, language quality, metadata, internal links, unsafe claims, policy violations, and malformed MDX (DEC-048). No fabricated expertise, authors, test results, citations, product capabilities, or claims (DEC-048). Publication is at most one coordinated topic per day after launch, EN+ES+ID together, with kill-switch and pause thresholds (DEC-053, DEC-124). The blog carries light advertising under Section 14 (DEC-129). The daily cadence may pause for stability and corrective work after launch (DEC-141). No newsletter at launch (DEC-109).
```
### 2.6 UX — other locale / language / i18n / translation mentions (verbatim)

UX Section 2 scope item 2 (line 27):

```text
27: 2. The information architecture and locale strategy for EN, ES, and ID.
```

UX Section 6 (line 107):

```text
107: Target regions are the United States, Latin America, and Europe, launched simultaneously (DEC-003, DEC-104). Indonesian content is preserved and Indonesian is a first-class launch locale (DEC-115, DEC-118), with the legacy Indonesia-first positioning dropped from the international identity (DEC-002, DEC-003, DEC-021).
```

UX Section 8.2 in FULL — Routes and locale prefixes (lines 131-157), route table (14 rows) plus notes:

```text
133: Every localized route carries an explicit locale prefix, including English (DEC-023). English does not use unprefixed tool routes as canonical URLs. Route structure:
135: | Surface | Route pattern |
136: | --- | --- |
137: | Homepage | `/en/`, `/es/`, `/id/` |
138: | Compress PDF | `/en/compress-pdf`, `/es/<slug>`, `/id/<slug>` |
139: | Merge PDF | `/en/merge-pdf`, `/es/<slug>`, `/id/<slug>` |
140: | Split PDF | `/en/split-pdf`, `/es/<slug>`, `/id/<slug>` |
141: | JPG to PDF | `/en/jpg-to-pdf`, `/es/<slug>`, `/id/<slug>` |
142: | PDF to JPG | `/en/pdf-to-jpg`, `/es/<slug>`, `/id/<slug>` |
143: | Privacy | `/en/privacy`, `/es/<slug>`, `/id/<slug>` |
144: | Terms | `/en/terms`, `/es/<slug>`, `/id/<slug>` |
145: | Cookies/Advertising | `/en/cookies-advertising`, `/es/<slug>`, `/id/<slug>` |
146: | Contact/Support | `/en/contact`, `/es/<slug>`, `/id/<slug>` |
147: | Status | `<locale>/status` |
148: | Roadmap | `<locale>/roadmap` |
149: | Blog index | `<locale>/blog` |
150: | Blog article | `<locale>/blog/<slug>` |
152: Notes:
154: 1. Exact slugs are selected during SEO design (Section 19); Indonesian tool and content URLs use translated, search-appropriate slugs (DEC-122), and EN/ES use their own localized slug policies (DEC-023).
155: 2. Locale-less entry is redirected once according to supported browser-language preferences, with a persistent manual language switcher whose explicit choice takes precedence (DEC-047). Unsupported languages fall back to English (DEC-047).
156: 3. Legacy unprefixed URLs require a deliberate redirect map under the SEO design (DEC-023, DEC-099, DEC-127).
157: 4. Tool pages remain available during backend outages; the frontend must not redirect ordinary tool traffic to the status page (DEC-163).
```

UX Section 8.3 (lines 159-161):

```text
161: The existing categorized navbar model is retained (DEC-147). At launch it is populated only with the five available tools; deferred tools do not appear as active destinations, empty categories are omitted or sensibly consolidated, and no coming-soon links or dead destinations exist in primary navigation (DEC-152). Category labels and destinations are localized consistently across EN, ES, and ID (DEC-152). The mobile category accordion is preserved with corrected expansion, focus, keyboard, touch-target, active-page, and screen-reader behavior (DEC-155).
```

UX Section 9 in FULL — Localization: EN, ES, and ID (lines 171-181), 9 items:

```text
173: 1. English is the canonical language for design documents; the public product is localized in EN, ES, and ID (DEC-184, DEC-115, DEC-118).
174: 2. The launch gate requires complete and consistent UI copy, instructions, errors, processing disclosures, results, metadata, navigation, legal/support surfaces, and core accessibility text in all three locales (DEC-118).
175: 3. Translation must be intentional localization, not literal machine translation; content must suit each market's search intent and cultural expectations (DEC-048, DEC-052, DEC-121, DEC-124).
176: 4. The language selector remains in the navbar on desktop and mobile, shows the active locale, is keyboard and screen-reader accessible, and preserves the equivalent page when a localized counterpart exists (DEC-149).
177: 5. Locale switching, hreflang, canonicals, sitemaps, and internal links must be generated consistently per locale (DEC-023, DEC-115).
178: 6. Copy must be resilient to length growth in Spanish and Indonesian; legacy Indonesian context paragraphs are long and the EN/ES equivalents must not break layouts (Section 16; `audit-outputs/ui-docs-code-reconciliation.md` §7.2).
179: 7. Copy tone is one neutral, direct register. The legacy split page uses the informal "kamu" while other tools use a neutral register (`audit-outputs/ui-five-tools-audit.md` §6 item 14); the rebuild uses one register per locale, consistent across tools.
180: 8. No legacy Indonesia-first positioning, "no English tagline" rules, or Indonesian-only copy claims carry forward (DEC-002, DEC-003, DEC-021; `audit-outputs/ui-docs-code-reconciliation.md` §4.5).
181: 9. The legacy `<html lang="id">` hardcoding (`frontend/src/app/layout.tsx:49`) is replaced with locale-aware document language and metadata (DEC-023, DEC-047).
```

UX Section 20.7 in FULL — Localization acceptance (lines 684-689):

```text
686: 1. Complete EN/ES/ID coverage across tools, legal, support, status, metadata, and core accessibility text (DEC-118).
687: 2. The navbar language selector works on desktop and mobile, shows the active locale, and preserves the equivalent page (DEC-149).
688: 3. Locale-less entry detection, manual override memory, and unsupported-language fallback behave per DEC-047 without SEO duplication or redirect loops.
689: 4. Localized copy survives length growth at all breakpoints (Section 9, Section 16).
```

### 2.7 UX — paper size / A4 / Letter mentions (verbatim)

UX Section 12.4 JPG to PDF, flow items 5-6 (lines 427-428):

```text
427: 5. **Automatic fitting policy (no settings):** each image is fitted to an appropriate standard page with safe margins, preserving aspect ratio, no cropping, and EXIF orientation (DEC-041). Page size and portrait/landscape orientation are selected per image (DEC-082). Letter-family geometry is used for US and Canada; A4-family for other markets, derived from the trusted edge country code, with A4 as the deterministic fallback (DEC-083, DEC-085, DEC-089). The selected standard is visible before processing even though no manual control exists (DEC-083, DEC-085).
428: 6. **Metadata disclosure:** the interface and Privacy documentation disclose that source metadata, including EXIF GPS, timestamps, and device information, may remain in the result (DEC-084). This is an accepted privacy risk; the product makes no broad claim that generated files remove sensitive metadata (DEC-084).
```

UX Section 20.4 item 4 (line 667):

```text
667: 4. **JPG to PDF:** accepts JPG/JPEG, PNG, and WebP inputs while keeping the "JPG to PDF" name (DEC-187); automatic per-image fitting with margins, no cropping, EXIF orientation; Letter for US/CA and A4 elsewhere with A4 fallback; selected standard visible before processing; metadata-preservation disclosure present (DEC-041, DEC-082, DEC-083, DEC-085, DEC-089, DEC-084).
```

UX Section 21 item 3 (line 701) — already quoted in full in Section 2.1; the governing paper-policy open item:

```text
701: 3. **Paper-standard regional rule details.** How the active locale maps to Letter/A4 when the trusted edge country is missing or when EN spans US and non-US markets (DEC-083, DEC-085, DEC-089). A4 is the deterministic fallback; the user-visible summary wording is finalized in the copy pass.
```

Supporting mention (line 178, Section 9 item 6): localized copy length resilience tied to Section 16 (quoted in 2.6 above).
### 2.8 UX — slug / URL / canonical / hreflang / SEO / sitemap / robots mentions (verbatim)

UX Section 19 in FULL — SEO and content migration constraints (lines 612-623), 10 items:

```text
612: ## 19. SEO and content migration constraints
614: 1. **Locale-prefixed routes** for every localized page, including English; localized slugs, metadata, structured data, internal links, sitemaps, canonicals, and hreflang generated consistently per locale (DEC-023). Indonesian tool and content URLs use translated slugs (DEC-122).
615: 2. **Locale-less entry** redirects once by supported browser language; manual choice overrides and is remembered with minimal non-sensitive storage; unsupported languages fall back to English; crawler and canonical behavior is not redirected unpredictably (DEC-047).
616: 3. **Legacy URL inventory.** The complete legacy sitemap and indexable URL inventory is audited before relaunch, with an explicit retain/update, redirect, noindex, or removal disposition for every URL (DEC-127). Legacy pages that still attract meaningful traffic are retained and updated rather than discarded (DEC-114). Retention never preserves stale instructions, unavailable features, obsolete claims, or duplicate pages (DEC-114).
617: 4. **Legacy archive.** After relaunch, the domain serves only the rebuilt product; the legacy application remains archived and is not exposed on a public legacy subdomain (DEC-099). Important legacy URLs receive intentional redirects or replacement responses (DEC-099).
618: 5. **Indonesian preservation.** Valuable legacy Indonesian content is deliberately mapped, updated, and localized rather than left as an inconsistent island (DEC-115). The exact Indonesian coverage at relaunch is reconciled with the one-month schedule and the complete-over-deadline policy (DEC-115, DEC-118, DEC-103).
619: 6. **Tool-page SEO.** Each tool page answers transactional intent with the tool first, followed by instructions, benefits, processing and privacy explanation, use cases, FAQs, and related tools (DEC-044). No invented superlatives or quantified performance claims (DEC-066).
620: 7. **No competitor pages** at relaunch (DEC-128). Educational articles may discuss objective format or workflow choices without becoming disguised competitor pages (DEC-128).
621: 8. **Blog SEO.** Launch of 15 articles (five topics, three locales) with blocking quality gates; post-launch cadence of at most one coordinated topic per day; truthful publication and update dates; no keyword filler or duplication (DEC-048, DEC-052, DEC-053, DEC-113, DEC-121, DEC-124).
622: 9. **No launch campaign**; the relaunch is direct activation with a coordinated checklist covering deployment, redirects, indexing, monitoring, support, and status (DEC-140).
623: 10. **No public counters** that could become misleading traffic claims (DEC-126).
```

UX Section 10.5 item 10 (line 255) — SEO baseline strength to preserve:

```text
255: 10. SEO baseline: metadataBase, OG images, sitemap.
```

UX Section 11.1 item 4 (line 293) — locale-aware metadata:

```text
293: 4. Metadata uses locale-aware defaults with `metadataBase https://mypapyr.com`, per-locale title/description, and OG/Twitter images (DEC-021, DEC-023). The legacy Indonesian-only default title (`frontend/src/app/layout.tsx:18`) is replaced by localized international copy (DEC-003).
```

UX Section 12.0 (line 330) — no redirect to a separate result URL:

```text
330: Each tool page follows the existing sequence (DEC-144): tool header, file dropzone, configuration when needed, processing state, result and download, privacy information, and related tools. Tool-specific configuration appears only after a valid file selection when relevant (DEC-144). Processing and results stay on one page; successful processing does not redirect to a separate result URL (DEC-153).
```

UX Section 20.1 item 7 (line 637) and 20.3 item 2 (line 649) — redirect/URL acceptance criteria:

```text
637: 7. Full legacy URL inventory has explicit dispositions with no soft 404s or redirect chains (DEC-127).
649: 2. Processing and results stay on one page; no redirect to a result URL (DEC-153).
```

UX Section 21 item 4 (line 702) — slug/redirect open item (also quoted in Section 2.1):

```text
702: 4. **Tool slugs for EN/ES/ID** and the legacy URL redirect map, selected during SEO design (DEC-023, DEC-122, DEC-127).
```
### 2.9 UX — UI baseline: documented defects D1-D13 (verbatim)

UX Section 10.6 in FULL — Documented defects to correct (lines 258-278). Core UI-baseline defect register for Track B (IDs D1-D13, plus audit uncertainty U2 under D3):

```text
258: ### 10.6 Documented defects to correct
260: From `audit-outputs/ui-home-shell-audit.md` §12 (D1-D13), all corrected without changing the visual character:
262: 1. **D1 Dead footer links:** "Syarat" and "Kontak" point to `#` (`frontend/src/components/Footer.tsx:161-162`); replaced by real localized routes (DEC-045, DEC-046) and covered by tests.
263: 2. **D2 Four divergent catalog copies:** replaced by one canonical catalog (Section 8.4).
264: 3. **D3 Width inconsistency:** navbar container `max-w-[1440px]` (`frontend/src/components/Navbar.tsx:146`) versus 1200px elsewhere; the audits could not determine intent (uncertainty U2). The rebuild documents and applies one width decision after owner confirmation (Section 21).
265: 4. **D4 Dead tokens:** `--color-background` and `--font-dm-sans` resolved (Section 10.1).
266: 5. **D5 `var()` reliance on `@theme inline` tokens:** resolved (Section 10.1).
267: 6. **D6 Hardcoded `© 2026`:** year computed from runtime date.
268: 7. **D7 Redundant homepage wrapper:** removed; the flex shell handles min-height and background.
269: 8. **D8 Accessibility gaps:** skip-to-content link and `main` id, `aria-expanded` on hamburger and category buttons, focus-visible styling, Escape-to-close on dropdowns and the language switcher (Section 16).
270: 9. **D9 Language switcher semantics:** the inert English row becomes a proper disabled/`aria-disabled` treatment where applicable; flag emoji replaced by accessible text labels (audit notes Windows letter-pair rendering).
271: 10. **D10 No active-section indication:** the category button shows an active state when a tool inside it is active.
272: 11. **D11 Logo lockup mismatch:** one lockup component with a size prop for navbar and footer.
273: 12. **D12 Instant panel appearance:** dropdowns and the mobile menu get a short fade consistent with the motion language, or instant behavior is kept as a deliberate, documented choice (owner confirmation; Section 21).
274: 13. **D13 Test blind spots:** interaction and render tests added for dropdown open/close, mobile menu, active states, and the language switcher (Section 20).
276: From `audit-outputs/ui-five-tools-audit.md` §6 (tool-level corrections), integrated into the per-tool flows in Section 12 and the shared states in Section 13.
278: From `audit-outputs/ui-docs-code-reconciliation.md` §7.3, these historical claims do not carry forward: Indonesia-first positioning and Indonesian-only copy rules, OpenClaw-related content, "6 tools" counts, the universal 1200px rule (replaced by the 1440px navbar plus 1200px content convention, pending D3), and the "semantic colors to be defined" note.
```

UX Section 10.1 token corrections (lines 201-204) — U1 and D4/D5 context:

```text
201: Token corrections (from `audit-outputs/ui-home-shell-audit.md` D4, D5):
203: 1. `--color-background: #ffffff` is unused and `--font-dm-sans` (from next/font) is never consumed by any utility; wire the font variable correctly or drop the dead token.
204: 2. Plain CSS `body` rules reference `@theme inline` tokens via `var()` (`globals.css:12-16`); with Tailwind v4 `@theme inline`, emission of these custom properties to `:root` is version-dependent (audit uncertainty U1). The rebuild must use utilities or a non-inline `@theme` so the body background, text color, and font never silently fall back.
```

UX Section 20.2 items 1-2 (lines 642-643) — visual-continuity acceptance referencing D1-D13:

```text
642: 1. The rebuilt site is recognizable as the existing Papyr: same color direction, typography character, card language, spacing rhythm, navigation model, uploader experience, and overall tone (DEC-143). Verified by side-by-side comparison of key surfaces (homepage, one tool page, navbar, footer) against the legacy clone.
643: 2. Documented defects D1-D13 are corrected without changing the visual character (Section 10.6; `audit-outputs/ui-home-shell-audit.md` §12).
```

### 2.10 UX — remaining accessibility / browser mentions (verbatim, short passages)

UX Section 2 scope item 9 (line 34):

```text
34: 9. Responsive behavior and WCAG 2.2 Level AA acceptance coverage.
```

UX Section 10.4 item 3 (line 233) — dropzone baseline accessibility contract:

```text
233: 3. **Dropzone:** `rounded-2xl border-2 border-dashed`, slate-300 border with `hover:border-accent/50`, drag-over to `border-accent bg-accent/5`; 56px accent icon tile; navy CTA line; slate-400 constraint line; hidden file input; `role="button"`, `tabIndex={0}`, Enter/Space activation.
```

UX Section 10.4 item 9 (line 239):

```text
239: 9. **Sortable items:** order badge, drag handle, per-item remove control with `aria-label`.
```

UX Section 12.0 items 9-10 (lines 342-343):

```text
342: 9. Accessible status and progress semantics per Section 16.
343: 10. Heading hierarchy without h1-to-h3 jumps (audit §6 item 8).
```

UX Section 12.2 Merge flow item 3 (line 380) — keyboard reordering:

```text
380: 3. Sortable file list: drag-and-drop reorder plus keyboard-accessible alternatives (DEC-040). Drag handles receive `aria-label` and dnd-kit `announcements` provide keyboard reorder feedback (audit §6 item 7). Order badges, per-item remove with `aria-label`, file name and size, and the "{n} files · size" summary are retained (DEC-040).
```

UX Section 12.4 JPG to PDF flow item 3 (line 425) — keyboard reordering:

```text
425: 3. Sortable thumbnail grid with order badges, always-visible remove and drag controls (the legacy hover-only `opacity-0 group-hover` controls are fixed: audit §6 item 6), and keyboard reordering (DEC-041; Section 16).
```

UX Section 13.1 (line 481) — accessible transition announcements:

```text
481: Transitions are announced accessibly (Section 16). The processing stage must not replace the whole page or hide navigation (DEC-145).
```

UX Section 15.3 support (line 536) — accessibility as a contact-form category (first sentence of the support paragraph):

```text
536: Launch support is a public support email plus a simple categorized contact form, no accounts and no live chat (DEC-046), routed to one inbox managed by the project owner (DEC-050). The form minimizes personal-data collection, includes anti-spam and abuse protection, and never requests document uploads, contents, or passwords (DEC-046). Categories cover processing failure, advertising concern, privacy/data request, accessibility, security, and general feedback (DEC-046).
```

UX Section 20.5 in FULL — Accessibility acceptance (lines 670-674):

```text
670: ### 20.5 Accessibility
672: 1. WCAG 2.2 AA acceptance coverage per Section 16 passes automated checks plus representative manual keyboard and assistive-technology testing (DEC-062).
673: 2. Known exceptions are documented with impact and remediation; no certification claims are made (DEC-062).
674: 3. Supported-browser matrix behavior is verified, including progressive-enhancement fallbacks and a clear unsupported-browser path (DEC-031).
```
## 3. Technical Architecture Specification — verbatim quotes

### 3.1 Arch Section 1.4 in FULL — Source precedence (lines 70-80)

```text
70: ### 1.4 Source precedence
72: When this specification or future documents conflict, the following precedence applies:
74: 1. `papyr-rebuild-decisions.md` is the authoritative record of confirmed product and engineering decisions. It is a living log; changes are recorded as new or superseding decision IDs, never by silent rewrite (AGENTS.md; DEC-006).
75: 2. This Technical Architecture Specification and the Product and UX Design Specification are the canonical design documents derived from that decision baseline. They must be consistent with each other (DEC-185).
76: 3. `audit-outputs/` contains durable research and audit results. These are evidence supporting design, not standalone requirements.
77: 4. `papyr-reference/` is the read-only legacy clone. It is a source of requirements history and reusable patterns, not the default architecture (DEC-001). Legacy behavior is reference material and must be re-justified (DEC-059). Legacy code and documentation never override an accepted decision.
78: 5. Historical legacy documents (BRD, SRS, TDD, ADR, UIUX spec, brand guidelines, migration evidence, step prompts) are non-canonical historical material under DEC-026 unless explicitly re-adopted.
80: Material contradictions discovered during specification writing must be surfaced for owner review rather than silently resolved (DEC-183).
```

### 3.2 Arch Section 4.2 in FULL — Routing and localization (lines 213-219)

```text
213: ### 4.2 Routing and localization
215: - Every localized route carries an explicit locale prefix, including English and Spanish, and the legacy unprefixed routes receive a deliberate redirect map (DEC-023).
216: - Indonesian is a first-class launch locale alongside English and Spanish for all five tools and essential supporting pages (DEC-115, DEC-118). Indonesian tool and content URLs use translated slugs under `/id/` (DEC-122).
217: - Locale-less entry redirects once according to supported browser-language preferences; a persistent manual language switcher overrides detection and its explicit choice is remembered with minimal non-sensitive storage (DEC-047).
218: - Locale resolution must avoid redirect loops, unpredictable crawler behavior, and SEO duplication (DEC-023, DEC-047).
219: - Canonical URLs, hreflang, sitemaps, and internal links are generated consistently per locale (DEC-023, DEC-115, DEC-122, DEC-127).
```

### 3.3 Arch Section 4.3 in FULL — Server and browser responsibilities (lines 221-227)

```text
221: ### 4.3 Server and browser responsibilities
223: Client components perform browser processing, upload, polling, and result presentation. Server components (Next.js server functions and middleware) handle locale detection, metadata, SEO output, and any server-only integration that does not expose secrets to the browser.
225: Browser processing runs in the user's browser within the conservative limits of DEC-015. The frontend owns browser-specific capability logic and limits, which must be clearly distinguished from server limits in the capability contract (DEC-165).
227: The tool pages remain accessible when the backend is unavailable. Browser-capable operations may continue locally; server-dependent processing clearly communicates temporary unavailability (DEC-163).
```

### 3.4 Arch Section 2.2 in FULL — Data flow at a glance (lines 121-135)

```text
121: Browser-only job:
123: 1. User selects files on a tool page.
124: 2. The frontend validates within conservative browser limits and processes locally in the browser (DEC-011, DEC-015).
125: 3. No bytes leave the device. Results are kept only for the active tab session (DEC-032) and served from memory or object URLs.
127: Server job:
129: 1. The frontend uploads the file through Cloudflare to `https://api.mypapyr.com/api/v1/...`.
130: 2. Nginx terminates TLS with origin certificates, applies rate limiting and request filtering, and proxies to the FastAPI application.
131: 3. The API validates the file, enforces per-tool limits and fair-use controls, writes minimal task metadata to Redis, and enqueues the job.
132: 4. A bounded worker claims the job, processes it inside a hardened container, and writes source, intermediate, and result objects to R2.
133: 5. The API exposes task status. The frontend polls while the tab is open and stores an opaque recovery token in `sessionStorage` (DEC-072).
134: 6. When ready, the frontend auto-downloads the result and keeps a manual Download control. Downloads use short-lived signed R2 URLs (DEC-170).
135: 7. All server-side objects are deleted no later than one hour after upload receipt; the application actively deletes them and an R2 lifecycle rule is the safety net (DEC-013, DEC-070, DEC-166).
```
### 3.5 Arch Section 10 in FULL — Browser/Server Routing (lines 462-496)

This is the arch spec's central browser-routing section for Track B.

```text
462: ## 10. Browser/Server Routing
464: ### 10.1 Hybrid model
466: Papyr uses a hybrid processing model that prefers local browser processing and routes operations to a server when quality, file complexity, device capability, or reliability requires it (DEC-011). Routing is based on measured capabilities and explicit rules rather than hidden arbitrary behavior (DEC-011).
468: ### 10.2 Browser-first jobs and limits
470: The conservative, device-aware browser-processing limits of DEC-015 apply:
472: - Modern desktop browser-first jobs: 100 MB total input, 500 PDF pages initially.
473: - Capable non-iOS mobile browser-first jobs: 50 MB total input, 200 PDF pages initially.
474: - iPhone and iPad browser-first jobs: 25 MB total input, 100 PDF pages initially.
475: - PDF to JPG browser-first: 200 pages on desktop, 50 pages on mobile, sequential page rendering, and a 16-megapixel per-page safety ceiling for broad iOS compatibility.
476: - JPG to PDF browser-first: 50 images and 100 megapixels total on desktop, 40 megapixels total on mobile.
477: - Compress PDF uses server-side processing by default (DEC-015).
479: Routing must also evaluate decoded image dimensions, page geometry, encryption, file corruption, estimated peak memory, and browser capabilities rather than relying only on file size (DEC-015). These are product safety limits, not browser hard limits; they may be raised only after anonymous reliability telemetry and representative real-device testing demonstrate acceptable failure rates (DEC-015).
481: ### 10.3 Automatic server fallback
483: - When a file is corrupt, encrypted, unsupported, or unsafe for reliable browser processing, the job automatically falls back to temporary server processing (DEC-030).
484: - When browser processing fails and the job is safe and supported on the server, the same job automatically transitions to server processing without a second confirmation prompt (DEC-065).
485: - Automatic fallback applies only to classified recoverable failures and must not create retry loops, duplicate jobs, duplicate downloads, or repeated uploads (DEC-065).
486: - Security-policy failures, unsupported content, invalid passwords, user cancellation, retention violations, and unsafe conditions fail closed rather than forcing a server upload (DEC-065).
487: - The server copy and result remain subject to the one-hour maximum retention and sensitive-data restrictions (DEC-065).
488: - If server processing also cannot recover the file, the product returns a clear, actionable failure rather than an indefinite retry loop (DEC-030).
490: ### 10.4 Disclosure of processing location
492: The user-visible disclosure behavior (no dedicated block on the uploader, full disclosure on the localized Privacy page, truthful workflow-state labels, accessible path) is specified canonically in the Product and UX Design Specification (§12.0, §15.2, §17.5). The architectural obligations retained here are that Privacy page content must remain accurate about browser processing, automatic server fallback, R2 storage, providers, and the absolute one-hour maximum retention, and that any legally mandatory notice or consent mechanism required by later review is not removed by this decision (DEC-168).
494: ### 10.5 Backend-outage behavior
496: When the backend is unavailable, tool pages remain accessible and browser-capable operations may continue locally; server-dependent processing clearly communicates temporary unavailability (DEC-163). The frontend does not redirect ordinary tool traffic to the status page and does not globally disable every tool (DEC-163). Availability and error messaging accurately distinguishes local and server processing paths, and unsafe fallback, repeated submissions, and misleading progress are prevented (DEC-163).
```
### 3.6 Arch Section 25 in FULL — Research Gates and Unresolved Implementation-Level Choices (lines 1047-1088)

This includes the complete Section 25.3 open-items list with all item IDs (1-21). Requested sub-items: 25.3.1 = Compress engine selection and license validation (line 1061); 25.3.2 = Exact per-tool server limits (line 1062); 25.3.7 = JPG to PDF paper-policy region mapping — i18n/paper (line 1067); 25.3.15 = Legacy URL inventory audit and disposition map — SEO/URL migration (line 1075); 25.3.16 = Indonesian slug and content mapping — i18n/URL (line 1076); 25.3.17 = Browser-processing capability detection — browser routing (line 1077).

```text
1047: ## 25. Research Gates and Unresolved Implementation-Level Choices
1049: ### 25.1 Research gate
1051: Every new feature and material capability change requires deep, evidence-based research before its design or implementation is approved (DEC-054), delivered as a structured research brief (DEC-055), grounded in primary sources and practical verification (DEC-056), and approved explicitly by the owner (DEC-057). The rebuild coding gate remains closed until required research is complete, findings are reconciled, design is approved, and an implementation plan is reviewed (DEC-060). No benchmark program is part of any gate (DEC-066).
1053: ### 25.2 Explicitly excluded features
1055: The following are confirmed non-goals rather than unresolved items: accounts (DEC-012), deadline-prediction admission control (DEC-073), paid priority lanes (DEC-134), benchmark programs (DEC-066), newsletters at relaunch (DEC-109), public counters (DEC-126), and competitor-comparison pages (DEC-128).
1057: ### 25.3 Unresolved implementation-level choices
1059: These areas are constrained by approved decisions but not yet resolved to exact values or selections. Each requires research, design, or owner confirmation before implementation:
1061: 1. Compress engine selection and license validation. Legacy uses Ghostscript; the engine must satisfy the automatic premium-screen profile (DEC-014) and licensing requirements (DEC-059, DEC-056).
1062: 2. Exact per-tool server limits (bytes, pages, pixel counts, output counts, estimated memory) as conservative design and safety defaults with a documented raising procedure, adjusted from production observations rather than benchmark-proven (DEC-034, DEC-066).
1063: 3. Worker count, per-worker memory and time bounds, and queue-depth safety caps, tuned from production observability (DEC-019, DEC-035, DEC-098).
1064: 4. Fair-scheduling class definitions, concurrency bounds, and starvation-prevention parameters without exposing defensive detail (DEC-137).
1065: 5. Redis persistence mode, eviction policy, and recovery procedure that satisfy minimal-metadata durability without document data (DEC-174, DEC-019).
1066: 6. The exact output profile for Compress and PDF to JPG (resolution, JPEG quality, downsample thresholds, quality floor) established through representative validation and production observation (DEC-014, DEC-039).
1067: 7. JPG to PDF paper-policy region mapping for English and Spanish markets where language alone does not identify paper preference, using the trusted edge country code and A4 fallback (DEC-083, DEC-085, DEC-089).
1068: 8. Malware scanner selection, update channel, and safe-failure behavior (DEC-171).
1069: 9. Nginx rate-limit values and fair-use thresholds, informed by expected traffic and load-informed telemetry (DEC-020, DEC-035).
1070: 10. Exact monitoring thresholds and alert deduplication rules for Netdata, uptime checks, and Telegram (DEC-180, DEC-182).
1071: 11. Public status provider and health-signal composition (DEC-116, DEC-119, DEC-161). The legacy runbook lists BetterStack as pending.
1072: 12. Adsterra script and cookie behavior review against current provider terms and applicable law before launch, including the accepted consent risk in DEC-022 and the format restrictions in DEC-018.
1073: 13. Legal review of Privacy, Terms, and Cookies pages and their exact processing disclosures (DEC-045, DEC-168, DEC-084, DEC-085).
1074: 14. Contact and result-problem report anti-spam and delivery mechanisms (DEC-046, DEC-117, DEC-120).
1075: 15. Legacy URL inventory audit and the complete retain/redirect/noindex/removal disposition map (DEC-127, DEC-114, DEC-099).
1076: 16. Indonesian slug and content mapping for tools, legal pages, and legacy URLs (DEC-115, DEC-122).
1077: 17. Browser-processing capability detection details (memory, dimensions, encryption, corruption) and the exact routing thresholds that trigger server fallback (DEC-015, DEC-030, DEC-065).
1078: 18. The post-launch sequence for restoring legacy tools, chosen later from demand, readiness, complexity, cost, and the approval gate (DEC-094).
1079: 19. Operational overrides and pause/disable controls for AI-assisted automation under owner accountability (DEC-097).
1080: 20. Backup schedule, retention window, and restore-target configuration for the S3-compatible destination (DEC-173, DEC-181).
1081: 21. `gpt5.6-sol` provider documentation before technical design finalization: base URL, authentication, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, and availability (DEC-051); cross-referenced from the Product and UX Design Specification §21.21.
1083: ### 25.4 Owner decisions still required
1085: - Approval of this Technical Architecture Specification and the companion Product and UX Design Specification (DEC-185).
1086: - Approval of the resulting implementation plan after research and reconciliation (DEC-060, DEC-185).
1087: - Explicit authorization for each production deployment (DEC-160).
1088: - Approval for any vertical VPS upgrade, new paid service, or material cost increase (DEC-095, DEC-098).
```
### 3.7 Arch — paper size / A4 / Letter mentions (verbatim)

Arch Section 5.3 in FULL — Edge-derived country context (lines 260-270):

```text
260: ### 5.3 Edge-derived country context
262: JPG to PDF paper selection uses a coarse country code supplied by the trusted Vercel or Cloudflare request edge: Letter for US and Canada, A4 for all other countries, with A4 as the deterministic fallback when no trusted signal is available (DEC-083, DEC-085, DEC-089).
264: The design must define:
266: - Which trusted headers carry the country code, and how to reject spoofed or untrusted values.
267: - That the country code is ephemeral for page-policy selection and does not become a persistent location profile (DEC-085).
268: - That privacy and analytics documentation accurately discloses country-level processing already performed by hosting or analytics providers (DEC-085).
270: No precise browser geolocation is requested (DEC-085).
```

Arch Section 11.5 in FULL — JPG to PDF processing responsibilities (lines 544-553):

```text
544: ### 11.5 JPG to PDF
546: - Automatically fits each image to an appropriate standard page without exposing A4, Letter, orientation, DPI, or margin controls (DEC-041).
547: - Page size and portrait/landscape orientation are selected per image; one PDF may contain mixed orientations (DEC-082).
548: - Letter-family geometry for US and Canada locale contexts, A4-family otherwise, determined from the trusted edge country code with A4 fallback (DEC-083, DEC-085, DEC-089). The selected standard is visible before processing (DEC-083, DEC-089).
549: - Fitting preserves aspect ratio, avoids cropping, and respects EXIF orientation, with deterministic page-size and margin rules (DEC-041, DEC-082).
550: - Image order remains user-adjustable before conversion (DEC-041, DEC-082).
551: - Source metadata, including EXIF GPS and device/software information, is preserved to the greatest extent supported (DEC-084, accepted risk). The interface and privacy documentation disclose that source metadata may remain in the result (DEC-084).
552: - The tool officially accepts JPG/JPEG, PNG, and WebP image inputs at launch while the user-facing name remains "JPG to PDF" (DEC-187). Image inputs are validated by actual bytes, rejected when unsupported or malformed, bounded for encoded and decoded resources, and decoded within an isolated processing boundary (DEC-093, DEC-187). Threat-classified files are blocked (DEC-088).
553: - Browser-first with a server fallback; legacy hybrid threshold of 3 MB (`papyr-reference/frontend/src/app/image-to-pdf/page.tsx:43`) is replaced by the DEC-015 limits and capability-based routing.
```

Arch Section 2.1 topology row (line 109) — edge country context role:

```text
109: | Edge | Cloudflare | DNS, TLS, proxying of `mypapyr.com` and `api.mypapyr.com`, coarse country signal, DDoS and bot defense |
```

Arch Section 1.3 non-goal (line 67) — legacy Indonesian-only positioning and legacy catalog:

```text
67: - Recreating the legacy 13-tool catalog, legacy Indonesian-only positioning, or legacy operational coupling (DEC-001, DEC-002, DEC-099).
```

Arch Section 25.3.7 (line 1067) — paper-policy open item (full item quoted in Section 3.6 above).
### 3.8 Arch — other browser / capability / progressive-enhancement mentions (verbatim)

Arch Section 1.2 scope bullet (line 31):

```text
31: - Browser-first and server processing boundaries, routing rules, and the five-tool processing model (DEC-009 to DEC-011, DEC-014, DEC-015, DEC-030, DEC-065).
```

Arch Section 14.1 in FULL — Canonical machine-readable contract (lines 666-673); note line 673 separates browser capability logic from server limits:

```text
666: ### 14.1 Canonical machine-readable contract
668: The versioned backend API is the canonical source for server-processing capabilities and limits (DEC-165). The frontend reads and presents this machine-readable contract rather than maintaining an independent hardcoded copy (DEC-165). Requirements:
670: - The contract is cacheable safely, versioned, and localized at the presentation layer (DEC-165).
671: - The frontend has conservative fallback behavior if the contract is unavailable (DEC-165).
672: - Backend validation remains authoritative even when the frontend pre-validates inputs (DEC-165).
673: - Browser-specific safety limits remain frontend capability logic but are clearly distinguished from server limits (DEC-165).
```

Arch Section 22.4 in FULL — Browser and device coverage (lines 953-958):

```text
953: ### 22.4 Browser and device coverage
955: - The supported matrix is the latest two major versions of Chrome, Edge, Firefox, and Safari on desktop, current Safari on iOS/iPadOS, and Chrome on Android (DEC-031).
956: - The matrix is represented in automated tests where feasible and supplemented by representative real-device testing, especially on iOS (DEC-031).
957: - Unsupported browsers receive a clear compatibility message or server-processing path rather than silently failing (DEC-031).
958: - Progressive enhancement and ordinary file-input/download fallbacks are required where Chromium-specific file APIs are unavailable (DEC-031).
```

Arch Section 2.3 component role (line 141) and Section 8.4 (line 404):

```text
141: - Frontend (Vercel): pages, locale routing, browser processing, upload, status polling, result presentation, disclosure links.
404: - A Redis outage degrades server-job admission and status; browser-only tools remain available (DEC-163).
```

Arch Section 11.3 Merge (line 532) and Section 11.6 PDF to JPG (line 559):

```text
532: - Browser-first in the MVP (DEC-011, DEC-015). Server path exists for fallback and for jobs exceeding browser limits (DEC-030, DEC-065).
559: - Text and line art remain crisp for normal high-quality screen use within the 16-megapixel per-page ceiling for browser processing (DEC-015, DEC-039).
```

Arch Section 16.1 (line 726) and Section 16.3 (line 736) — browser-capable tools during incidents:

```text
726: - A VPS or backend incident does not take down the informational site or browser-capable tools (DEC-163).
736: Tool pages remain accessible during backend outages; browser-capable operations continue locally; server-dependent processing communicates temporary unavailability clearly (DEC-163). The frontend does not globally disable tools or redirect to the status page (DEC-163).
```

Arch Section 24.2 (line 1028) — browser-local vs server metrics:

```text
1028: Metrics distinguish browser-local jobs from server-side jobs without collecting document contents (DEC-024). Exact numeric targets and baseline measurement windows are defined before implementation planning is approved (DEC-024).
```

Arch Section 25.3.17 (line 1077) — browser capability-detection open item (full item quoted in Section 3.6 above).
### 3.9 Arch — other locale / language / translation mentions (verbatim)

Arch Section 11 intro (line 502) — trilingual production readiness:

```text
502: The five-tool catalog is Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG (DEC-010). All five must be production-ready across EN, ES, and ID at relaunch (DEC-027, DEC-118). Each tool retains independently measurable acceptance criteria (DEC-059). Processing responsibilities below are grounded in the approved decisions and the legacy implementation evidence.
```

Arch Section 20.2 status experience (line 905):

```text
905: - Status communication covers user-relevant components in plain EN/ES/ID language where supported (DEC-116).
```

Arch Section 24.1 launch gate (line 1014):

```text
1014: The public relaunch occurs only when all five tools are production-ready in EN, ES, and ID (DEC-027, DEC-118), with complete processing behavior, localized UI and metadata, error states, analytics, privacy disclosure, executable tests, documentation, and operational support (DEC-027). Legally required operator or contact information remains provided where applicable (DEC-110). The relaunch is direct to production on the existing domain without a public beta or persistent staging environment (DEC-096), and is preceded by pre-release local, CI, preview-deployment, integration, security, accessibility, and smoke verification (DEC-096, DEC-177). Launch requires rollback capability, backups where applicable, health monitoring, and the complete five-tool trilingual gate (DEC-096).
```

Arch Section 22.2 E2E tests (line 941):

```text
941: - End-to-end tests: complete tool flows across the five tools in EN, ES, and ID, including auto-download and manual-download fallback, fallback routing, error states, and refresh recovery (DEC-027, DEC-029, DEC-068, DEC-072).
```

Arch Section 13.3 (line 640) and Section 15.3 (line 715) — localized user-facing text:

```text
640: - A task that exceeds its timeout fails clearly with a safe localized error (legacy precedent: `papyr-reference/backend/services/async_task.py` timeout handling; DEC-033).
715: - Download names are safe, localized where appropriate, and derived without sending original file names to analytics (DEC-029, DEC-042).
```

Arch Section 4.5 analytics (line 237) and Section 23.1 table row (line 978) — page and locale in analytics:

```text
237: - Analytics follow DEC-025: detailed product events, funnels, attribution, performance, and sanitized error analytics; no session replay on document workflows; no fingerprinting; no document-sensitive information.
978: | Analytics events | Acquisition, page and locale, tool, processing mode, coarse input bands, funnels, timings, sanitized failures, Web Vitals, ad performance | DEC-025 scope; privacy-reviewed schema, retention policy, regional activation, leakage guards |
```

### 3.10 Arch — SEO / canonical / hreflang / slug / redirect / sitemap / robots mentions (verbatim)

Arch Section 4.2 lines 215-219 are quoted in full in Section 3.2 (canonical URLs, hreflang, sitemaps, internal links; redirect map; translated slugs under `/id/`).

Arch Section 11.1 (line 508) — canonical catalog feeding localized slugs:

```text
508: - One canonical tool catalog feeding navigation, related-tools, metadata, and localized slugs (per the reconciliation audit, `audit-outputs/ui-home-shell-audit.md` D2 and `audit-outputs/ui-docs-code-reconciliation.md`).
```

Arch Section 6.4 (line 320) — legacy route disposition:

```text
320: The rebuild API exposes its public processing and task contracts under an explicit `/api/v1` prefix (DEC-164). Processing, task status, cancellation where applicable, limits, and related machine-readable endpoints use the same versioned contract (DEC-164). The frontend configuration and Nginx routing use one canonical API base (DEC-164). Legacy routes require an explicit migration or retirement disposition and must not remain accidentally active (DEC-164).
```

Arch Section 25.3.15 (line 1075) and 25.3.16 (line 1076) — URL-migration and slug open items (full items quoted in Section 3.6):

```text
1075: 15. Legacy URL inventory audit and the complete retain/redirect/noindex/removal disposition map (DEC-127, DEC-114, DEC-099).
1076: 16. Indonesian slug and content mapping for tools, legal pages, and legacy URLs (DEC-115, DEC-122).
```

### 3.11 Arch — accessibility mentions (verbatim)

Arch Section 19.1 (line 860), Section 22.1 (line 935), Section 22.2 (line 942):

```text
860: - Relevant E2E, accessibility, and preview smoke verification remain mandatory for initial relaunch readiness and for changes that affect their surfaces (DEC-177).
935: - Automated checks are necessary but insufficient for accessibility; representative manual keyboard and assistive-technology testing is required (DEC-062).
942: - Accessibility checks: automated scans plus manual keyboard and assistive-technology passes targeting WCAG 2.2 Level AA (DEC-062), across the supported browser matrix (DEC-031).
```

Arch Section 1.5 (line 89) — research findings are recommendations, not accepted decisions (gate context for all Track-B open items):

```text
89: - Research findings are recommendations, not accepted product decisions (DEC-054).
```
## 4. Consolidated unresolved / open item register (Track B)

Legend for Track-B relevance: B = browser routing; A = accessibility; I = i18n/locale; P = paper policy (A4/Letter); S = SEO/URL migration; UI = UI baseline verification. "—" = outside Track B (listed for completeness of each spec's open-item list).

### 4.1 Open items from the UX specification — Section 21 items 1-21 (lines 699-719)

| # | Item (short title) | Track B relevance | Where it appears in UX spec |
|---|---|---|---|
| 21.1 | Exact per-tool server limits and browser-limit adjustments | B | §21 item 1 (line 699); also §10.2 limits are arch §10 |
| 21.2 | Compress engine profile thresholds | — | §21 item 2 (line 700) |
| 21.3 | Paper-standard regional rule details (Letter/A4 mapping) | P, I | §21 item 3 (line 701); §12.4 item 5 (line 427); §20.4 item 4 (line 667) |
| 21.4 | Tool slugs for EN/ES/ID and legacy URL redirect map | S, I | §21 item 4 (line 702); §8.2 notes (lines 154-156); §19 (lines 612-623) |
| 21.5 | Launch blog topic selection | — (blog/i18n adjacent) | §21 item 5 (line 703) |
| 21.6 | Indonesian coverage extent at relaunch | I, S | §21 item 6 (line 704); §19 item 5 (line 618); §7 item 8 (line 120) |
| 21.7 | Contact form provider, anti-spam, delivery monitoring | — | §21 item 7 (line 705) |
| 21.8 | Status page implementation details | — | §21 item 8 (line 706) |
| 21.9 | Adsterra script/cookie/identifier/regional review | — (ads/privacy) | §21 item 9 (line 707); §14 item 8 (line 521) |
| 21.10 | Legal review of Privacy/Terms/Cookies copy | — (privacy) | §21 item 10 (line 708) |
| 21.11 | Rendered visual verification of the baseline | UI, A | §21 item 11 (line 709); references audit U7; §4.1 (line 82) |
| 21.12 | Contrast re-verification of tokens | A | §21 item 12 (line 710); §16.2 item 3 (line 569) |
| 21.13 | Navbar width intent (D3 / U2) | UI | §21 item 13 (line 711); §10.6 D3 (line 264) |
| 21.14 | Duplicate CTA intent (U3) | UI | §21 item 14 (line 712); §11.2 item 4 (line 303) |
| 21.15 | Homepage entrance animations (U5, resolves D12) | UI | §21 item 15 (line 713); §10.6 D12 (line 273) |
| 21.16 | Merge error-state edge case | UI | §21 item 16 (line 714) |
| 21.17 | Privacy copy re-scoping | I (copy), — | §21 item 17 (line 715); §17 item 7 (line 592) |
| 21.18 | FAQ copy accuracy (JPG/PNG/WebP formats) | I (copy) | §21 item 18 (line 716); §12.4 item 2 (line 424) |
| 21.19 | `@theme inline` token emission verification (U1) | UI | §21 item 19 (line 717); §10.1 item 2 (line 204) |
| 21.20 | Newsletter deferral (confirmed, not unresolved) | — | §21 item 20 (line 718) |
| 21.21 | `gpt5.6-sol` provider documentation | — | §21 item 21 (line 719); arch §25.3.21 (line 1081) |

### 4.2 Open items from the Technical Architecture Specification — Section 25.3 items 1-21 (lines 1061-1081)

| # | Item (short title) | Track B relevance | Where it appears in arch spec |
|---|---|---|---|
| 25.3.1 | Compress engine selection and license validation | — (engine) | §25.3 item 1 (line 1061) |
| 25.3.2 | Exact per-tool server limits (bytes/pages/pixels/outputs/memory) | B (routing boundary) | §25.3 item 2 (line 1062); §14.2 (lines 675-677) |
| 25.3.3 | Worker count, per-worker bounds, queue-depth caps | — | §25.3 item 3 (line 1063) |
| 25.3.4 | Fair-scheduling class definitions | — | §25.3 item 4 (line 1064) |
| 25.3.5 | Redis persistence mode / eviction / recovery | — | §25.3 item 5 (line 1065) |
| 25.3.6 | Compress and PDF-to-JPG output profiles | — (engine) | §25.3 item 6 (line 1066) |
| 25.3.7 | JPG-to-PDF paper-policy region mapping (Letter/A4) | P, I | §25.3 item 7 (line 1067); §5.3 (lines 260-270); §11.5 (lines 544-553) |
| 25.3.8 | Malware scanner selection | — | §25.3 item 8 (line 1068) |
| 25.3.9 | Nginx rate-limit values and fair-use thresholds | — | §25.3 item 9 (line 1069) |
| 25.3.10 | Monitoring thresholds and alert deduplication | — | §25.3 item 10 (line 1070) |
| 25.3.11 | Public status provider and health-signal composition | — | §25.3 item 11 (line 1071) |
| 25.3.12 | Adsterra script/cookie behavior review | — (ads/privacy) | §25.3 item 12 (line 1072) |
| 25.3.13 | Legal review of Privacy/Terms/Cookies and disclosures | — (privacy) | §25.3 item 13 (line 1073) |
| 25.3.14 | Contact/report anti-spam and delivery mechanisms | — | §25.3 item 14 (line 1074) |
| 25.3.15 | Legacy URL inventory audit and disposition map | S (URL migration) | §25.3 item 15 (line 1075); UX §19 item 3 (line 616), UX §21 item 4 (line 702) |
| 25.3.16 | Indonesian slug and content mapping | I, S | §25.3 item 16 (line 1076); UX §8.2 (line 154), UX §21 item 6 (line 704) |
| 25.3.17 | Browser-processing capability detection and routing thresholds | B | §25.3 item 17 (line 1077); §10 (lines 462-496) |
| 25.3.18 | Post-launch legacy-tool restoration sequence | — | §25.3 item 18 (line 1078) |
| 25.3.19 | Operational overrides / pause controls for automation | — | §25.3 item 19 (line 1079) |
| 25.3.20 | Backup schedule / retention / restore targets | — | §25.3 item 20 (line 1080) |
| 25.3.21 | `gpt5.6-sol` provider documentation | — | §25.3 item 21 (line 1081) |

### 4.3 Audit item IDs referenced by the two specs (Track B-relevant)

| ID | Meaning (as cited in the specs) | Spec references |
|---|---|---|
| D1 | Dead footer links ("Syarat", "Kontak" -> `#`) | UX §10.6 (line 262); §11.3 (line 311) |
| D2 | Four divergent catalog copies | UX §8.4 (line 165); §10.6 (line 263); §11.3 (line 310); §20.2 (line 644); arch §11.1 (line 508) |
| D3 | Navbar width inconsistency (1440px vs 1200px); owner confirmation required | UX §10.6 (line 264); §21 item 13 (line 711); §10.6 (line 278) |
| D4 | Dead tokens (`--color-background`, `--font-dm-sans`) | UX §10.1 (lines 201-203); §10.6 (line 265) |
| D5 | `var()` reliance on `@theme inline` tokens | UX §10.1 (line 204); §10.6 (line 266) |
| D6 | Hardcoded `© 2026` | UX §10.6 (line 267); §11.3 (line 312) |
| D7 | Redundant homepage wrapper | UX §10.6 (line 268) |
| D8 | Accessibility gaps (skip link, aria-expanded, focus-visible, Escape) | UX §10.6 (line 269); §11.1 (line 292); §11.2 (line 304); §16.2 item 4 (line 570); §11.3 (line 313) |
| D9 | Language switcher semantics / flag emoji | UX §10.6 (line 270); §11.3 (line 313) |
| D10 | No active-section indication | UX §10.6 (line 271); §11.2 (line 304) |
| D11 | Logo lockup mismatch | UX §10.6 (line 272); §11.3 (line 312) |
| D12 | Instant panel appearance (fade decision) | UX §10.6 (line 273); §21 item 15 (line 713) |
| D13 | Test blind spots (dropdown/menu/active/language-switcher) | UX §10.6 (line 274); §11.2 (line 304) |
| U1 | `@theme inline` token emission uncertainty | UX §10.1 (line 204); §21 item 19 (line 717) |
| U2 | Navbar width intent (paired with D3) | UX §10.6 (line 264); §21 item 13 (line 711) |
| U3 | Duplicate CTA targeting intent | UX §11.2 (line 303); §21 item 14 (line 712) |
| U5 | Homepage entrance-animation question (resolves D12) | UX §21 item 15 (line 713) |
| U7 | Rendered-visual-verification gap (static audits only) | UX §4.1 (line 82); §21 item 11 (line 709) |

### 4.4 Arch Section 25.4 — owner decisions still required (context, lines 1085-1088)

| Decision required | Source line |
|---|---|
| Approval of both design specifications (DEC-185) | 1085 |
| Approval of the implementation plan after research/reconciliation (DEC-060, DEC-185) | 1086 |
| Explicit authorization for each production deployment (DEC-160) | 1087 |
| Approval for vertical VPS upgrade, new paid service, or material cost increase (DEC-095, DEC-098) | 1088 |
## 5. Cross-spec keyword mention map (line-index for Track B follow-up)

Every Track-B keyword mention not already quoted above, with line references only (verbatim text is available in the source files; all quoted passages are in Sections 2-3 above).

| Topic | UX spec lines | Arch spec lines |
|---|---|---|
| locale / language / i18n / translation | 27, 107, 131-157, 159-161, 171-181, 270, 293, 303, 313, 334, 561, 576, 614, 618, 684-689 | 9, 141, 213-219, 502, 905, 941, 978, 1014 |
| paper size / A4 / Letter | 427, 667, 701 | 109, 262, 546, 548, 1067 |
| slug / URL / canonical / hreflang / SEO / sitemap / robots / redirect | 93, 133-157, 177, 255, 293, 330, 612-623, 637, 649, 688, 702 | 215-219, 223, 320, 508, 1075-1076 |
| accessibility / WCAG / keyboard / aria | 34, 161, 174, 176, 233, 239, 269, 292, 304, 313, 342-343, 380, 425, 481, 515, 536, 552-582, 590, 606, 653, 665, 670-674, 686 | 860, 935, 942, 953-958, 1014 |
| browser / capability / progressive enhancement | 351, 374, 396, 419, 441, 580, 606, 674, 699, 709 | 31, 109, 121-135, 141, 217, 221-227, 404, 462-496, 532, 553, 559-560, 673, 726, 736, 953-958, 1028, 1077 |

## 6. Verification evidence

Verification commands and results (run 2026-07-31 after the last write):

1. Output file exists and is non-empty: `_evidence-specs.md` present under `<workspace-root>/audit-outputs/research/track-b/`, byte count recorded after the final append.
2. All four mandated sections present in this file: (1) spec headers + tables of contents; (2) UX verbatim quotes; (3) arch verbatim quotes; (4) consolidated unresolved/open item register.
3. `git -C <workspace-root>\papyr-reference status --porcelain` returns empty (papyr-reference unchanged).

Open uncertainties / notes for the research program:

- The specs' audit cross-references use the `§` glyph (e.g., "audit §6 item 8"); line-numbered verbatim blocks in this file preserve them except where noted, and the source line numbers allow exact re-verification.
- UX §21 item 11 (U7) confirms that all three audits were static source inspections; rendered browser verification remains open — directly relevant to Track B UI baseline work.
- The paper-policy open items (UX §21 item 3, arch §25.3.7) are paired: the UX spec owns the user-visible mapping and wording; the arch spec owns the trusted edge-country mechanism (§5.3).
- The slug/redirect open items (UX §21 item 4, arch §25.3.15-16) are paired with UX §8.2 route table and UX §19 SEO constraints.
- Browser routing open item (arch §25.3.17) governs the concrete routing thresholds that UX §18 item 4 (routing transparency) must display.
