# Papyr product specification

## 1. Executive summary

Papyr is a fast, simple, free, and anonymous PDF utility platform for the web. A visitor arrives, selects one of five focused tools, provides files, understands where processing occurs, receives an honest result, and leaves without creating an account.

The launch catalogue contains exactly five tools:

1. Compress PDF.
2. Merge PDF.
3. Split PDF.
4. JPG to PDF.
5. PDF to JPG.

Every tool follows the same shared workflow and state model, from ready and selected through processing, completed, failed, and cancelled or expired. Processing is browser-first: most jobs run locally on the user's device, and work that needs native engines, stronger isolation, or a more predictable resource envelope moves to an explicit, disclosed server path. Server-processed objects are temporary, use opaque keys, and are removed no later than one hour after upload receipt.

English, Spanish, and Indonesian are first-class launch languages across every essential surface. Accessibility targets WCAG 2.2 Level AA. The launch catalogue is free to use and requires no account.

Status in one line: the five tools, their shared experience, and the Phase 6 privacy, analytics, advertising, and support capabilities described in this document are implemented; the Phase 5/6 baseline is deployed to production (release 1767ca8) and the Phase 6 enterprise completion shipped via PR #46 as backend release p6-complete-1786951216 and frontend release p6-ads-all-1786954951 (2026-08-17). This document remains the target-behaviour contract, and the implementation state is tracked in the status matrix in Section 13 and the roadmap.

## 2. Product promise and principles

The product direction, in priority order:

1. **Fast and simple task completion.** The highest priority is a short, clear path from arrival to completed PDF task: open tool, select files, configure only what is necessary, process, download.
2. **Honest and trustworthy.** Trust comes from clear product behaviour, truthful claims, transparent policies, and reliable operations. Processing location, progress stages, retention, and compression results are reported truthfully, never fabricated.
3. **Private by design.** No account is required. Browser-processed documents never leave the device. Server processing is disclosed before transfer and temporary by strict policy.
4. **Free and anonymous.** All five core tools remain free to use and download at launch, bounded by fair-use, safety, size, and capacity controls rather than accounts or paywalls.
5. **Product before promotion.** Task completion takes priority over advertising and promotional content. Ad placements, where present, never obstruct the workflow.

## 3. Audience and personas

### 3.1 Primary audience

Papyr serves a general web user who needs one common document task completed quickly, without learning a product or creating an account. Landing pages satisfy search intent directly and avoid dashboards, onboarding, and registration. The target regions at launch are the United States, Latin America, and Europe, served simultaneously.

### 3.2 Personas

| Persona | Context | Primary job | What Papyr must deliver |
| --- | --- | --- | --- |
| Single-task visitor | Searches for a tool, arrives on a tool page, wants the task done now | Compress a PDF so it fits in an email | One clear action, no account, honest result, no dead ends |
| Privacy-conscious professional | Handles documents they prefer not to upload | Merge or split PDFs locally | Working browser path, clear disclosure before any server transfer, strict retention |
| Mobile-first user | Works from a phone or tablet | Convert images to a PDF or a PDF to images on the go | Responsive layout, accessible touch targets, capability-aware routing |
| Returning anonymous user | Used a tool before, has no account | Run the same task again without friction | Consistent behaviour, predictable defaults, fast reset to a new job |

### 3.3 Jobs to be done

| ID | Job | Primary tool |
| --- | --- | --- |
| JTBD-01 | Make a PDF smaller so it can be emailed or uploaded | Compress PDF |
| JTBD-02 | Combine several PDFs into one ordered document | Merge PDF |
| JTBD-03 | Extract selected pages or one page per file from a PDF | Split PDF |
| JTBD-04 | Turn a set of images into a single PDF document | JPG to PDF |
| JTBD-05 | Turn PDF pages into shareable images | PDF to JPG |
| JTBD-06 | Complete any of the above without creating an account | All tools |
| JTBD-07 | Know where the file is being processed and how long it will be kept | All tools |

## 4. Launch catalogue and functional requirements

Functional requirements use stable identifiers. `FR-SHARED` applies to every tool; `FR-COMP`, `FR-MERGE`, `FR-SPLIT`, `FR-J2P`, and `FR-P2J` apply to the named tool. Requirement status is defined in Section 13.

### 4.1 Shared requirements

| ID | Requirement |
| --- | --- |
| FR-SHARED-01 | Each tool page must present one clear primary action and keep configuration minimal with predictable defaults. |
| FR-SHARED-02 | The interface must state where processing occurs (browser or server) and must never silently upload a file that was presented as remaining local. |
| FR-SHARED-03 | A server fallback must never be hidden. If a browser path cannot complete reliably, the user must be told before server upload begins. |
| FR-SHARED-04 | Progress must be truthful. Percentages appear only when grounded in measurable units such as bytes uploaded or pages processed; otherwise processing uses an honest stage label. |
| FR-SHARED-05 | A successful result must trigger an automatic download attempt and keep a persistent manual Download button that reuses the generated result without reprocessing. |
| FR-SHARED-06 | A blocked automatic download must leave the job in the completed state with the manual button available, not as a failure. |
| FR-SHARED-07 | Multi-file results must be delivered as a predictable archive plus individual downloads in the user's chosen order. |
| FR-SHARED-08 | A "process another file" action must reset the tool to its starting state without a full page reload. |
| FR-SHARED-09 | Password-protected PDFs must request a password only when required, with a distinct wrong-password error separate from corrupt or unsupported file errors. |
| FR-SHARED-10 | Inputs must be validated by actual file bytes and structure, not by file extension or browser MIME value alone. |
| FR-SHARED-11 | Output names must be safe and derived from the source name with a localized suffix, never exposing document contents or sensitive identifiers. |
| FR-SHARED-12 | Privacy information must be visible on every tool and linked to the full processing and retention disclosure. |

### 4.2 Compress PDF

Purpose: reduce PDF file size while preserving crisp on-screen quality, using one automatic high-quality profile.

| ID | Requirement |
| --- | --- |
| FR-COMP-01 | Compress PDF must expose exactly one automatic compression profile; no quality presets, target-size, DPI, or advanced controls. |
| FR-COMP-02 | The result must report the original size, the result size, and the actual percentage saved, including zero savings or a larger output when that is the truth. |
| FR-COMP-03 | Compress PDF must never fabricate a savings figure, never claim success as a size reduction that did not occur, and never silently substitute the original file. |
| FR-COMP-04 | Processing must always produce a new output artifact, even when the source was already optimized or the output is not smaller. |
| FR-COMP-05 | Compression must preserve searchable and selectable text, links, page geometry, and legibility whenever the source format permits. |
| FR-COMP-06 | Compress PDF uses the server processing path by default. The server path invokes the official, unmodified Ghostscript distribution as a separate hardened subprocess (see the technical architecture specification). |
| FR-COMP-07 | Active content detected in the input (JavaScript, launch actions, embedded attachments) must be sanitized from the output, with the general categories removed disclosed to the user without payload details. |

### 4.3 Merge PDF

Purpose: combine multiple PDFs into one file in the user's chosen order, with controls at the file level.

| ID | Requirement |
| --- | --- |
| FR-MERGE-01 | Merge PDF must accept multiple PDFs and preserve the user's explicit ordering in the result. |
| FR-MERGE-02 | The interface must allow reordering and removal of files before processing, with a keyboard-accessible alternative to drag-and-drop. |
| FR-MERGE-03 | Each selected file must be validated individually, with errors identifying the affected file. |
| FR-MERGE-04 | Each encrypted input must request and validate its password independently; passwords must never be reused across files unless the user enters them. |
| FR-MERGE-05 | The job must be all-or-nothing: it fails or is blocked if any selected source cannot be opened, authenticated, validated, or processed, and no partial output is presented as successful. |
| FR-MERGE-06 | Bookmark, metadata, annotation, link, form-field, and page-geometry preservation must be supported to the greatest extent the engine can do safely, with any unsupported or transformed features disclosed truthfully. |
| FR-MERGE-07 | Active content must be sanitized from the output. Inputs detected to contain active content route to the server sanitization path; when that path is unavailable, the job fails closed. |
| FR-MERGE-08 | Merge PDF is browser-first, with automatic server fallback for corrupt, encrypted-unsupported, oversized, or active-content inputs. |

### 4.4 Split PDF

Purpose: extract selected pages as separate PDFs using custom page ranges or one PDF per page.

| ID | Requirement |
| --- | --- |
| FR-SPLIT-01 | Split PDF must support custom page ranges and a one-file-per-page mode. |
| FR-SPLIT-02 | User-entered range order must be preserved in the outputs. Overlapping ranges are permitted and produce independent outputs. |
| FR-SPLIT-03 | The interface must preview the effective output sequence and any duplicated page membership before processing. |
| FR-SPLIT-04 | Range input must validate charset, start-after-end, out-of-bounds, and malformed tokens with actionable localized errors. |
| FR-SPLIT-05 | Multiple outputs must be delivered as a predictable archive with deterministic, ordered names, plus individual downloads. |
| FR-SPLIT-06 | Active content must be sanitized from outputs, with server-path routing and fail-closed behaviour as in FR-MERGE-07. |
| FR-SPLIT-07 | Split PDF is browser-first with automatic server fallback for inputs that exceed browser limits or carry active content. |

### 4.5 JPG to PDF

Purpose: convert images into a single PDF with automatic, safe fitting.

| ID | Requirement |
| --- | --- |
| FR-J2P-01 | JPG to PDF must accept JPG and JPEG inputs at minimum; PNG and WebP are accepted when implemented and tested. The user-facing name stays "JPG to PDF". |
| FR-J2P-02 | Each image must be fitted automatically to an appropriate standard page with safe margins, preserving aspect ratio, without cropping, and respecting EXIF orientation. No manual paper, orientation, DPI, or margin controls are exposed. |
| FR-J2P-03 | Page size and portrait or landscape orientation are selected per image; one PDF may contain mixed orientations. |
| FR-J2P-04 | Image order must remain user-adjustable before conversion, with ordering preserved in the result. |
| FR-J2P-05 | The interface must disclose that source metadata, including EXIF GPS, timestamps, and device information, may remain in the result. |
| FR-J2P-06 | Image inputs must be validated by actual bytes, decoded dimensions, and resource limits, never by extension alone. |
| FR-J2P-07 | JPG to PDF is browser-first for small jobs and routes larger jobs to the server automatically, with the routing disclosed and labelled truthfully. |

### 4.6 PDF to JPG

Purpose: convert PDF pages to high-quality JPG images with one automatic output profile.

| ID | Requirement |
| --- | --- |
| FR-P2J-01 | PDF to JPG must render every requested page at one documented high-quality output profile; no DPI or quality controls. |
| FR-P2J-02 | Page transparency must be composited onto white before JPEG encoding, deterministically, in both browser and server paths. |
| FR-P2J-03 | Repeated and overlapping page selections must be preserved as independent outputs in the requested order, with unambiguous naming, archive contents, and manifest entries. |
| FR-P2J-04 | If source pages are already low resolution, the interface must not imply that conversion creates missing detail. |
| FR-P2J-05 | PDF to JPG is browser-capable with server fallback for inputs that exceed browser limits. The source is always treated as untrusted for parser and infrastructure safety. |
| FR-P2J-06 | Multi-page results must be delivered as a predictable archive plus individual downloads in page-selection order. |

## 5. Shared workflow and state model

Every launch tool follows the same user-facing state model.

| State | Meaning | Required behaviour |
| --- | --- | --- |
| Ready | No valid input selected | Explain accepted inputs, limits, privacy, and processing behaviour; present the dropzone and the primary action |
| Selected | Input accepted and validated | Show the file or files, per-file validation results, and configuration controls only where needed |
| Uploading | Bytes are being transferred for a server job | Show determinate progress only from measured bytes |
| Queued | Server job waiting for a worker | Show an honest wait state; wait estimates appear only when grounded in real queue state |
| Processing | Work is executing in the browser or on the server | Show a truthful stage label with an indeterminate indicator; percentages only when grounded in measurable units |
| Completed | Result available for download | Attempt auto-download, keep a manual Download button, summarize the result honestly, and offer a process-another-file action |
| Failed | The job was rejected or failed | Show a stable, actionable error category without exposing engine internals; offer only valid recovery actions |
| Cancelled or expired | Work stopped or the result is gone | Stop work, invalidate download capabilities, and remove temporary data; expired server results cannot be restored |

Supporting transitions:

- **Preparing** precedes Selected when the page must read the input (for example, determining page count) before configuration is possible.
- **Finalizing** covers result assembly (archive creation, result signing) between processing and completed.
- A successful download does not trigger early deletion; server results remain available until their normal expiry.
- An accepted server job continues after the tab is closed; closing the tab is not a cancellation signal.
- A queued server job can be cancelled atomically by the user; once a worker has started, user cancellation is no longer offered.
- Refreshing the same tab resumes an active server job using minimal opaque task state; closing the tab ends client-side recovery.
- Reset revokes local buffers and object URLs, clears task state, and returns focus to an appropriate heading or control.

## 6. User experience and accessibility

### 6.1 UX principles

- One clear primary action per page.
- Minimal configuration and predictable defaults; optional controls use progressive disclosure.
- Tool pages follow one sequence: tool header, file selection, configuration when needed, processing, result and download, privacy information, related tools.
- Processing and results stay on one page; a successful job does not redirect to a separate result URL.
- Related tools and supporting content remain visible below the active workspace so navigation is available exactly when a task finishes.

### 6.2 Accessibility target

WCAG 2.2 Level AA is the acceptance target for tool pages, the homepage, legal pages, and support surfaces. Required behaviours include:

- Full keyboard operation of every control, including dropzones, sortable lists, dropdowns, accordions, the language switcher, and range inputs. Drag-and-drop always has a non-drag alternative.
- Visible focus indication on every interactive control.
- Semantic labels, heading hierarchy, landmark regions, a skip-to-content link, and wired error messages (`aria-invalid`, `aria-describedby`).
- No colour-only meaning; AA contrast for all text and interactive elements.
- Screen-reader announcements for validation, progress, completion, and failure, using polite status regions and alert roles.
- Respect for reduced-motion preferences for animations.
- Layouts function at 200% zoom and 320px width without loss of content or functionality.
- WCAG 2.2 target-size minimums for controls at all breakpoints.

Automated accessibility checks are necessary but not sufficient; representative manual keyboard and assistive-technology testing is required. Known exceptions are documented with impact and remediation, and no certification or universal-conformance claim is made.

### 6.3 Responsive behaviour

- Mobile-first layout using the existing breakpoint scale; no horizontal overflow.
- Desktop navbar with category navigation; mobile compact navigation with accessible expand and collapse.
- Tool pages use a narrow content shell with full-width actions; grids collapse on small screens.
- Spanish and Indonesian copy length must not break layouts at any breakpoint.

### 6.4 Supported browsers

The supported matrix is the latest two major versions of Chrome, Edge, Firefox, and Safari on desktop, current Safari on iOS and iPadOS, and Chrome on Android. Unsupported browsers receive a clear compatibility message or a server-processing path rather than silent failure. Progressive enhancement and ordinary file-input and download fallbacks are required where newer file APIs are unavailable.

## 7. Localization

- English, Spanish, and Indonesian are launch requirements across every tool, essential supporting surface, error state, result, metadata, navigation, and core accessibility text.
- Locale choice must be persistent and manually overridable. Locale-less entry redirects once according to supported browser language; an explicit manual choice takes precedence; unsupported languages fall back to English.
- URLs, metadata, canonical links, hreflang, sitemaps, internal links, errors, consent text, limits, and essential support content must remain aligned across locales.
- Every localized route carries an explicit locale prefix, including English. Indonesian tool URLs use translated, search-appropriate slugs.
- Translation is intentional localization suited to each market's search intent, not literal machine translation.
- Copy uses one neutral, direct register per locale, consistent across tools.

## 8. Privacy and retention

- No account is required for the launch catalogue, and no stored cross-device history is kept.
- Browser-processed documents remain entirely local to the device and are kept only for the active tab session; no persistent browser storage is used for documents.
- Server upload is disclosed before transfer, and workflow states label uploading, queued, and server processing truthfully when they occur.
- Server-side objects use opaque, non-identifying keys and have a target maximum retention of one hour from upload receipt. One hour is the hard upper bound; objects may be deleted earlier after processing, failure, or cancellation.
- An expired server result cannot be restored from server storage; the user runs a new job.
- Passwords are entered only when required, held in memory for the shortest practical time, and never written to logs, analytics, URLs, storage, backups, or error payloads.
- Filenames, document contents, extracted text, signed download URLs, and object keys are excluded from analytics and logs.
- The full processing and retention disclosure lives on the localized Privacy page, with an accessible path from every uploader.
- The result experience may offer a short categorized problem report that never attaches or uploads the document.

## 9. Limits and errors

- Limits must be documented per tool and enforced before expensive work begins. Per-tool limits may combine total bytes, per-file bytes, file count, page count, pixel count, page geometry, and estimated memory.
- Browser and server limits are distinct and both disclosed; the interface reflects the limits of the active processing path.
- Errors use stable categories: invalid input, unsupported encryption, limit exceeded, unavailable server processing, expired result, cancelled operation, rate limited, or internal processing failure.
- Threat-classified files are blocked with a safe localized rejection and are never processed or returned; cleanup runs promptly within the retention ceiling.
- Rate and abuse responses are clear, actionable, and retryable where appropriate. Ordinary users do not face a fixed daily quota.
- User-facing responses never reveal command lines, scanner signatures, stack traces, filesystem paths, object keys, signed URLs, or provider credentials.
- When active content is detected and sanitized, the user is told which general categories were removed without payload or exploit details. Sanitization is not presented as proof that no other threat exists.

## 10. Analytics boundaries

Analytics collect product and reliability signals, never document contents.

Allowed:

- Acquisition source, page and locale, tool selection, processing mode, coarse input size bands, funnel stages, timings, sanitized failure categories, download completion, and web performance metrics.

Prohibited from analytics, logs, monitoring, error reporting, and advertising systems:

- File contents, previews, rendered document text, filenames, object keys, signed URLs, passwords, full error payloads containing user data, and stable device fingerprints.
- Session replay of document workflows.
- Public usage counters; aggregate metrics remain private.

Event schemas require privacy review, a documented retention policy, and automated guards against sensitive-field leakage.

## 11. Advertising placement

Advertising at launch, where present, is limited to non-intrusive banner and native placements:

- Placements never obstruct upload, configuration, processing, result, download, consent, error recovery, navigation, accessibility, or responsive layout.
- Tool pages place advertising only after the primary tool interaction and result or download experience, within supporting content.
- Result pages keep advertising spatially and visually separated from download controls; no ad imitates a download button, result card, progress state, warning, or system action.
- Ad slots reserve stable dimensions to prevent layout shift, and scripts load asynchronously or lazily.
- Critical product functionality and legal, support, and status content remain fully available when ad scripts are blocked, disabled, or slow.
- Any placement that materially harms trust, performance, or task completion is removed or reduced.

## 12. Launch acceptance criteria

A launch workflow is complete only when it has all of the following:

- End-to-end browser and server behaviour as specified, with the shared workflow, truthful progress, automatic and manual download paths, and process-another-file reset.
- Automated tests for success, limits, cancellation, errors, and cleanup, including retention-expiry and sensitive-data-exclusion guards.
- Accessible interaction states meeting the WCAG 2.2 Level AA acceptance coverage in Section 6.
- Complete English, Spanish, and Indonesian copy across every essential surface.
- Truthful result reporting, including honest compression figures and processing-location disclosure.
- Documented per-tool limits enforced before expensive work.
- Analytics boundaries enforced by tested event schemas.
- Localized privacy, terms, and cookies or advertising pages that accurately describe processing, retention, and advertising behaviour.
- A working contact and support path and a public status surface that remains useful during backend incidents.
- Operational evidence of cleanup and retention behaviour, and verified rollback and monitoring capability, before public activation.

## 13. Status matrix

Status values are used consistently across the product and architecture specifications:

- **Available now**: present in the repository and demonstrated by source and automated tests.
- **Deployed**: merged to `main` and active in production.
- **In branch**: implementation present in a feature branch and pending the authorized release process.
- **Specified**: target behaviour fully defined in these specifications; implementation is planned.
- **Planned**: capability with defined direction whose exact design or implementation schedule is not yet fixed.

| Capability | Status | Where defined |
| --- | --- | --- |
| Frontend application foundation (shell, strict TypeScript, tooling, tests, build) | Available now | Repository `frontend/` |
| Backend service foundation (app factory, strict configuration, health and readiness endpoints, request correlation, stable error envelope, validation schemas, server task state machine) | Available now | Repository `backend/` |
| Deployment templates and environment placeholders | Available now | Repository `deploy/` |
| Continuous integration with 20 required checks (quality, security and supply chain, repository QA) | Available now | Repository `.github/workflows/ci.yml` |
| Shared trilingual shell: English, Spanish, and Indonesian locale routing, accessible navigation, supporting route shells, localized 404, and unit and E2E gates | Available now | Repository `frontend/src/` |
| Legal, support, and status route shells (privacy, terms, cookies and advertising, contact, status, roadmap) | Available now | Repository `frontend/src/app/[locale]/` |
| Blog route shell | Available now | Repository `frontend/src/app/[locale]/blog/` |
| Five-tool launch catalogue | Deployed | This document, Section 4; roadmap |
| Shared workflow and state model | Deployed | This document, Section 5; roadmap |
| Trilingual localization (English, Spanish, Indonesian) | Deployed | This document, Section 7; roadmap |
| Accessibility target (WCAG 2.2 Level AA) | Specified | This document, Section 6 |
| Anonymous, no-account launch | Deployed | This document, Sections 2 and 8; roadmap |
| Privacy and one-hour retention targets | Deployed | This document, Section 8; architecture specification; roadmap |
| Browser-first processing | Specified | Architecture specification |
| Server processing, queue, and bounded workers | Deployed | Architecture specification; roadmap |
| Compress server path with the Ghostscript subprocess boundary | Deployed | Architecture specification; roadmap |
| Analytics and error boundaries | Deployed | This document, Sections 9 and 10; roadmap |
| Full legal, support, and status content and functionality | Planned | Roadmap |
| Blog publishing programme | Planned | Roadmap |

## 14. Non-goals for the launch catalogue

The following are explicitly not part of the five-tool launch catalogue:

- User accounts, authentication, profiles, cloud history, saved files, or cross-device synchronization.
- Billing, subscriptions, payments, credits, trials, premium gates, or paid fast lanes.
- Team workspaces, organizations, API keys, or a public business API.
- OCR, signing, watermarking, rotation, protection or unlocking, or office-format conversion.
- A dedicated public beta or persistent staging environment.
- Session replay of document workflows, fingerprinting, or public usage counters.
- Competitor-comparison pages, interactive roadmap voting, or a newsletter at launch.

## 15. Related documents

- [Technical architecture specification](architecture.md)
- [Architecture overview](../architecture.md)
- [Integration inventory](../integrations.md)
- [Product roadmap](../roadmap.md)
- [Security policy](../../SECURITY.md)
- [Contribution guide](../../CONTRIBUTING.md)
- [Repository readme](../../README.md)
