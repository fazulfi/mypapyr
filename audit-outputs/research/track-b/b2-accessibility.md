# B2 - Accessibility and WCAG 2.2 AA

## 1. Header

- **Brief ID**: B2
- **Path**: `<workspace-root>\audit-outputs\research\track-b\b2-accessibility.md`
- **Track**: B - Frontend, capability, and SEO research
- **Title**: Accessibility and WCAG 2.2 Level AA research brief
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (executor subagent, Track B)
- **Status**: Draft (complete for owner review under DEC-057; findings are recommendations, not accepted decisions)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (deliverable B2 at §6.2; Track B questions §7.2; brief template §8; verification §11)
- **Governing decisions**: DEC-062 (primary); supporting DEC-040, DEC-054 through DEC-060, DEC-066, DEC-143, DEC-149, DEC-155, DEC-168, DEC-188
- **Spec sections served**: Product and UX Design Specification §16 (Responsive and accessibility, lines 552-582), §10.4 item 3 (line 233), §12.0 items 9-10 (lines 342-343), §12.2 item 3 (line 380), §12.4 item 3 (line 425), §20.5 (lines 670-674), §21.11-12 (lines 709-710); Technical Architecture Specification §22.1-22.2 (lines 935, 942), §22.4 (lines 953-958)
- **Files read**:
  - `<workspace-root>\AGENTS.md`
  - `<workspace-root>\audit-outputs\research-program-plan.md`
  - `<workspace-root>\papyr-rebuild-decisions.md` (DEC-001 through DEC-188, Open decisions)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (§10, §12, §16, §20, §21)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (§22, §25.3)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-b2-web.md` (WCAG/ARIA/tooling/manual-testing evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-decisions.md` (decision-log extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-specs.md` (spec extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-legacy-frontend.md` (§13 accessibility-relevant components)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-ui-audits.md` (§9.1 accessibility findings)
  - Legacy (read-only): components cited in `_evidence-legacy-frontend.md` §13 (`PDFUploader.tsx`, `PasswordInput.tsx`, `PageRangeInput.tsx`, `SignaturePad.tsx`, `faq/page.tsx`, `Navbar.tsx`, `Footer.tsx`)
- **Template note**: The plan §8 lists 12 numbered sections. The header sub-fields above are expanded as their own labeled fields; combined with the 12 numbered sections this satisfies both the plan's template and the 16-section instruction for Track B briefs (header sub-fields counted individually), following the Track A A1 precedent.

---

## 2. Scope

This brief defines what WCAG 2.2 Level AA acceptance coverage means for the Papyr rebuild, per DEC-062 (source lines 764-774): "Treat WCAG 2.2 Level AA as an acceptance target for product pages, all five tools, blog, legal pages, and contact/support interfaces." It covers:

- The success criteria that apply to the upload, ordering, progress, error, result, and download interactions, with the normative text for the criteria that matter most to a file-conversion app.
- The automated tools and the manual keyboard and assistive-technology methods that are standard for verifying them (DEC-062 consequence: "Automated checks are necessary but insufficient; representative manual keyboard and assistive-technology testing is required").
- The legacy accessibility gaps the audits documented, mapped to the rebuild's Section 16 requirements, so the fixes are verifiable, not aspirational.
- The interaction between accessibility and the existing UI baseline (DEC-143): the rebuild must not change the visual character, but accessibility corrections are explicitly among the approved changes (DEC-143 consequence: "Changes are limited to purposeful improvements such as... accessibility").

The user problem served: keyboard, screen-reader, low-vision, and motor-impaired users must be able to complete every tool flow, because Papyr serves broad task-oriented audiences across desktop and mobile (DEC-062 rationale) and must not require a drag gesture, a hover, a precise pointer, or a cognitive test to finish a job.

The current approved Papyr behavior this brief must support: WCAG 2.2 AA as acceptance target (DEC-062); keyboard alternatives for drag-and-drop reordering (DEC-040); visible focus, contrast, semantic structure, accessible names and errors, status/progress announcements, non-drag alternatives, zoom/reflow, target sizing, reduced-motion behavior, and localized content resilience (DEC-062 consequences); the dropzone interaction contract (UX §10.4 item 3, line 233); one-register localized copy that survives length growth (UX §16.1 item 6, §16.2 item 10); documented exceptions with impact and remediation, never certification claims (DEC-062).

## 3. Non-goals

- No redesign of the visual baseline: DEC-143 preserves the existing visual language; accessibility corrections are approved changes, not a new aesthetic.
- No certification or conformance claims: DEC-062 forbids claiming certification or universal conformance unless independently substantiated; this brief produces no such claim.
- No implementation of fixes: the brief defines the acceptance coverage and verification method; implementation happens after owner approval (DEC-057, DEC-060).
- No benchmark program, corpus, or comparative accessibility-score program (DEC-066). Automated scan counts and manual pass/fail records are verification, not benchmarks.
- No audit of the legacy site's full remediation backlog beyond the five-tool and shell surfaces the rebuild replaces; deferred legacy tools (DEC-094) are out of scope.
- No legal accessibility advice (e.g., ADA/EAA obligations): the brief records standards facts, not legal conclusions.

## 4. Research questions

Restated from plan §7.2 (B2):

1. What does WCAG 2.2 Level AA acceptance coverage require for upload, ordering, progress, error, result, and download interactions (DEC-062)?
2. Which success criteria are new in WCAG 2.2, and which of those apply at AA to this product?
3. What automated tools are standard, what coverage do their own documentation claim, and where do they stop?
4. What manual keyboard and assistive-technology methods are standard, and which screen-reader/browser combinations should representative testing use?
5. Which legacy accessibility gaps must the rebuild correct to meet Section 16, with file and line evidence?
6. What are the interfaces to B5 (contrast re-verification, rendered pass) and to the design specs' Section 16?

## 5. Evidence

### 5.1 WCAG 2.2 status and structure

Source: `audit-outputs/research/track-b/_evidence-b2-web.md` §1 (all URLs accessed 2026-07-31).

- WCAG 2.2 is a W3C Recommendation first published 5 October 2023; the current version at `https://www.w3.org/TR/WCAG22/` is the 12 December 2024 revision (page metadata `publishISODate 2024-12-12`; this version `https://www.w3.org/TR/2024/REC-WCAG22-20241212/`).
- WCAG 2.2 has **86 success criteria** (4.1.1 Parsing is removed and obsolete; it does not count toward conformance).
- WCAG 2.2 adds **9 new success criteria**, not 7: 2.4.11 Focus Not Obscured (Minimum, AA), 2.4.12 Focus Not Obscured (Enhanced, AAA), 2.4.13 Focus Appearance (AAA), 2.5.7 Dragging Movements (AA), 2.5.8 Target Size (Minimum, AA), 3.2.6 Consistent Help (A), 3.3.7 Redundant Entry (A), 3.3.8 Accessible Authentication (Minimum, AA), 3.3.9 Accessible Authentication (Enhanced, AAA). For an AA target the new criteria that apply are 2.4.11, 2.5.7, 2.5.8, 3.3.8, plus the new Level A criteria 3.2.6 and 3.3.7 (AA includes all of A).
- Conformance definition (quoted in the evidence): "For Level AA conformance, the web page satisfies all the Level A and Level AA success criteria, or a Level AA conforming alternate version is provided."
- Understanding index and How-to-Meet quickref verify live (HTTP 200): `https://www.w3.org/WAI/WCAG22/Understanding/`, `https://www.w3.org/WAI/WCAG22/quickref/`.

### 5.2 Success criteria most relevant to a file-conversion app

Source: `_evidence-b2-web.md` §2 (normative text machine-extracted from the 12 Dec 2024 revision and spot-checked by hand). The criteria table below lists the SCs that govern the six interaction families of DEC-062. Levels: A or AA.

| Interaction family | Governing SCs (level) |
|---|---|
| Upload | 1.1.1 Non-text Content (A); 1.3.1 Info and Relationships (A); 1.3.2 Meaningful Sequence (A); 2.1.1 Keyboard (A); 2.1.2 No Keyboard Trap (A); 3.3.1 Error Identification (A); 3.3.2 Labels or Instructions (A); 3.3.3 Error Suggestion (AA); 4.1.2 Name, Role, Value (A); 4.1.3 Status Messages (AA) |
| Ordering (sortable lists, ranges) | 2.1.1 Keyboard (A); 2.5.7 Dragging Movements (AA, NEW: every dragging operation must be achievable by a single pointer without dragging, unless essential); 2.5.8 Target Size (Minimum) (AA, NEW: 24x24 CSS px targets); 1.3.1 Info and Relationships (A); 4.1.2 Name, Role, Value (A) |
| Progress | 2.2.1 Timing Adjustable (A); 2.2.2 Pause, Stop, Hide (A); 4.1.3 Status Messages (AA); 1.3.1 Info and Relationships (A) |
| Error | 3.3.1 Error Identification (A); 3.3.2 Labels or Instructions (A); 3.3.3 Error Suggestion (AA); 3.3.4 Error Prevention (Legal, Financial, Data) (AA); 4.1.3 Status Messages (AA) |
| Result and download | 1.4.3 Contrast (Minimum) (AA); 2.1.1 Keyboard (A); 2.4.7 Focus Visible (AA); 2.4.11 Focus Not Obscured (Minimum) (AA, NEW); 4.1.3 Status Messages (AA) |
| Cross-cutting | 1.4.4 Resize Text (AA); 1.4.10 Reflow (AA, 320 CSS px); 1.4.11 Non-text Contrast (AA, 3:1); 1.4.12 Text Spacing (AA); 2.4.1 Bypass Blocks (A); 2.4.3 Focus Order (A); 2.4.4 Link Purpose (In Context) (A); 2.4.6 Headings and Labels (AA); 2.4.7 Focus Visible (AA); 2.5.3 Label in Name (A); 3.1.1 Language of Page (A); 3.1.2 Language of Parts (AA); 3.2.3 Consistent Navigation (AA); 3.2.4 Consistent Identification (AA); 3.2.6 Consistent Help (A, NEW); 3.3.7 Redundant Entry (A, NEW); 3.3.8 Accessible Authentication (Minimum) (AA, NEW); 2.3.3 Animation from Interactions (AAA, noted as the reference for reduced-motion behavior; UX §16.2 item 9 requires `prefers-reduced-motion`) |

Key normative texts (quoted in the evidence, §2): 2.5.7 requires "All functionality that uses a dragging movement for operation can be achieved by a single pointer without dragging, unless dragging is essential"; its Understanding page states "Success Criteria 2.1.1 Keyboard and 2.1.3 Keyboard (No Exception) require dragging features to be keyboard accessible" and that "providing a text input can be an acceptable single-pointer alternative to dragging"; 2.5.8 requires targets "at least 24 by 24 CSS pixels" with documented exceptions; 4.1.3 requires status messages "programmatically determined through role or properties such that they can be presented to the user by assistive technologies without receiving focus"; 1.4.10 requires no two-dimensional scrolling at 320 CSS px width (1280 px at 400% zoom).

### 5.3 WAI-ARIA 1.2 and APG patterns

Source: `_evidence-b2-web.md` §3.

- WAI-ARIA 1.2 is a W3C Recommendation of 6 June 2023 (`https://www.w3.org/TR/wai-aria-1.2/`). Relevant roles quoted: `dialog`, `alertdialog`, `progressbar`, `status`, `alert`, `tab`.
- APG patterns verified live: Dialog (Modal) `https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/`, Tabs, Alert, Alertdialog. The old Progressbar pattern URL returns 404 and the pattern index no longer lists it; the `progressbar` role remains normative in ARIA 1.2, MDN documents its implicit live-region behavior, and the HTML native `<progress>` element plus `aria-valuemin`/`aria-valuenow`/`aria-valuemax` is the current implementation reference.
- APG Dialog guidance that applies to the rebuild's dialogs (none currently exist in the five-tool flows, but password prompts, sanitization notices, and future features may use them): focus moves into the dialog on open, Tab/Shift+Tab cycle within it, Escape closes, focus returns to the invoker on close, `aria-modal="true"` only when application code prevents interaction with background content, and a visible close control is strongly recommended.
- APG Alert: alerts must not take focus and should not auto-dismiss ("It is also important to avoid designing alerts that disappear automatically").

### 5.4 Automated tools and their documented limits

Source: `_evidence-b2-web.md` §4.

| Tool | Version/status (accessed 2026-07-31) | Documented coverage | Documented limit |
|---|---|---|---|
| axe-core (Deque) | 4.12.1 (released 2026-06-09/10) | Rules tagged to WCAG 2.0/2.1/2.2 A, AA, AAA plus best practices; `target-size` rule for WCAG 2.2 currently disabled by default | README: "you can find on average 57% of WCAG issues automatically"; returns "incomplete" items needing manual review |
| axe DevTools (Deque) | current | Full rule set over 70 tests; "zero false positives" marketing | FAQ: automation "up to 80% with Deque's tools"; does not replace screen-reader testing |
| Lighthouse accessibility audits | page last updated 2025-10-22 | Weighted pass/fail audits; lists weights (e.g., accessible names, progressbar names, contrast, alt, labels, lang) | Manual checks not scored: trapped focus, tab order, focus directed to new content, keyboard-focusable controls, visual order vs DOM |
| WAVE (WebAIM) | no version published | Checks including WCAG 2.2 per the help page; detects issues in hidden content | "WAVE cannot tell you if your web content is accessible. Only a human can determine true accessibility." "The absence of errors DOES NOT mean your page is accessible or compliant." |
| HTML CodeSniffer | no version published | WCAG 2.1 + Section 508 only | Not a WCAG 2.2 source; use for quick client-side checks only |

W3C position (Evaluating Web Accessibility overview, quoted in evidence §5.1): "no tool alone can determine if a site meets accessibility standards. Knowledgeable human evaluation is required."

### 5.5 Manual keyboard and assistive-technology standards

Source: `_evidence-b2-web.md` §5.

- WAI Easy Checks (updated 2024-03-21): image alt, page title, headings, contrast, skip link, visible focus, language, zoom, labels, required fields, plus the keyboard checks (logical tab order, visible focus, all functionality by keyboard, no hover-only functionality).
- WebAIM Screen Reader User Survey #10 (Dec 2023 - Jan 2024, 1539 responses; latest as of access date): primary desktop screen readers JAWS 40.5%, NVDA 37.7%, VoiceOver 9.7%; commonly used NVDA 65.6%, JAWS 60.5%, VoiceOver 43.9%; browsers with primary SR: Chrome 52.3%, Edge 19.3%, Firefox 16.0%, Safari 8.0%; top combos JAWS+Chrome 24.7%, NVDA+Chrome 21.3%; mobile VoiceOver 70.6%, TalkBack 34.7%. Most problematic items include interactive elements (menus, tabs, dialogs) behaving unexpectedly, changing screens, and lack of keyboard accessibility.
- Documented workflows: NVDA (free; quick keys, browse/focus modes, Elements List NVDA+F7), JAWS (paid; Virtual Cursor vs Forms Mode), VoiceOver (macOS/iOS; rotor VO+U, works best with Safari), TalkBack (Android; swipe sequence testing per developer.android.com, updated 2026-04-16), and WebAIM keyboard testing (focus indicators, logical order, no tabindex >= 1, keyboard-trap checks, per-control keystroke table; "Be sure to test keyboard accessibility on mobile devices").
- SPA focus management (Deque, secondary/supporting): on client-side route change, move focus to the top-level heading of the new page (`tabindex="-1"`), announce the page change; keep focus from becoming lost or stale.
- `:focus-visible` (MDN): Baseline, widely available since March 2022; browsers show focus rings for keyboard navigation and script-managed focus but not for pointer clicks on buttons; use `@supports` fallback for older browsers; WCAG 2.1 SC 1.4.11 requires the visual focus indicator to be at least 3:1.

### 5.6 File-upload accessibility guidance

Source: `_evidence-b2-web.md` §6.

- MDN `<input type="file">`: label association; the `accept` attribute is only a hint and "you should make sure that the `accept` attribute is backed up by appropriate server-side validation"; hide the input with `opacity` instead of `visibility: hidden` or `display: none`, because "assistive technology interprets the latter two styles to mean the file input isn't interactive".
- MDN File drag and drop: the documented accessible drop-zone pattern is a `<label>` wrapping a hidden `<input type="file">` (no JavaScript needed for selection UX); caveat recorded: that example uses `display:none`, which conflicts with the `<input type="file">` article's `opacity:0` advice; the rebuild should prefer the `opacity:0` or a visually-hidden-but-focusable technique.
- Keyboard alternative to drag-and-drop is normative: WCAG 2.2 SC 2.5.7 and its Understanding page (sufficient technique G219; failure F108 "not providing a single pointer method that does not require a dragging movement").
- Status messages: `role="status"`/`aria-live="polite"` for normal updates, `role="alert"` for errors, `role="progressbar"` with `aria-valuenow` for determinate progress; do not move focus for status-only announcements (WCAG 4.1.3); avoid double-speaking by not adding both `role="alert"` and `aria-live="assertive"` (VoiceOver iOS note in MDN).
- Error summary patterns: WAI Forms tutorial User Notifications (heading, page title, or error list at top; each error references the corresponding control, describes the mistake, suggests correction, links to the control; inserted lists use `role="alert"`; inline errors associate with `aria-describedby`; focus the first errored input). GOV.UK error-summary pattern is secondary/supporting only.
- The WAI "Forms - File Uploads" tutorial page does not exist (verified 404/absent); closest primary sources are the Forms tutorials and the SCs above.

### 5.7 Approved requirements (specs)

Source: `_evidence-specs.md` §2.2 (UX §16 in full), §2.4 (UX §18), §2.9 (UX §10.6 defects), §2.10 (UX §12.0, §12.2, §12.4, §10.4).

- UX §16.2 items 1-10 (lines 567-576): keyboard operation of all controls including dropzones (Enter/Space), sortable reordering, dropdowns, accordions, language switcher, range inputs, reset actions; drag-and-drop always has a non-drag alternative (DEC-040); consistent `focus-visible` styling app-wide (legacy has only one custom focus ring); contrast including slate-400/300 tertiary text re-verified with a tool; correct heading hierarchy (no h1-to-h3 jumps), landmarks, `main`, skip-to-content link (D8); accessible names and errors with `aria-invalid` and `aria-describedby`; `role="status"`/`aria-live="polite"` on processing and ready transitions, `role="alert"` on error cards, `role="progressbar"` with `aria-valuenow` on determinate upload progress; dnd-kit `announcements` for keyboard reorder; target-size minimums; 200% zoom and 320 px reflow; `prefers-reduced-motion` for shimmer and fade-up; localized announcements, labels, and errors.
- UX §16.3 (lines 578-582): automated checks necessary but insufficient; representative manual keyboard and assistive-technology testing required; known exceptions documented with impact and remediation; no certification claims.
- UX §20.5 (lines 670-674): acceptance = Section 16 coverage passes automated checks plus manual keyboard and AT testing; exceptions documented; supported-browser matrix verified including progressive-enhancement fallbacks and the unsupported-browser path.
- UX §18 item 1 (line 600): inline error cards announced "without stealing focus" (DEC-158).
- UX §10.4 item 3 (line 233): dropzone contract with `role="button"`, `tabIndex={0}`, Enter/Space activation.
- Arch §22.2 (line 942): accessibility checks = automated scans plus manual keyboard and assistive-technology passes targeting WCAG 2.2 AA across the supported matrix.

### 5.8 Legacy accessibility gaps (evidence)

Source: `_evidence-ui-audits.md` §9.1 and `_evidence-legacy-frontend.md` §13.

- Shell gaps (D8, `ui-home-shell-audit.md` L162): no skip-to-content link, no `main` id, no `aria-expanded` on hamburger or category buttons, no custom focus-visible styling, no Escape-to-close on dropdowns or the language switcher.
- Language switcher (D9, L163): the English row is an inert div styled like a menu item; flag emoji render as letter pairs on some platforms; no Escape handling.
- All five tools (`ui-five-tools-audit.md` L98, L156, L188, L210, L241-242): no `aria-live`/`role="status"` on processing or done transitions; no `role="progressbar"`/`aria-valuenow` on determinate upload; error cards lack `role="alert"`; PageRangeInput error and live preview are plain `<p>` with no `aria-live`/`aria-invalid`/`aria-describedby`; heading structure jumps h1 to h3 badges (no h2) on every tool; drag handles unlabeled.
- image-to-pdf grid (`ui-five-tools-audit.md` L188): remove button and drag handle are `opacity-0` revealed only on `group-hover`, invisible on touch and for keyboard users, with no focus-visible fallback.
- Rotate upload zone has neither role, tabIndex, nor keydown handler (`ui-docs-code-reconciliation.md` L139, `rotate/page.tsx:428-432`) - rotate is a deferred tool, but the pattern is recorded.
- Merge dnd-kit has no `announcements`/`screenReaderInstructions` config (`ui-five-tools-audit.md` L131); FAQ accordion toggle has no `aria-expanded`/`aria-controls` (`_evidence-legacy-frontend.md` §13.6).
- Keyboard upload-zone pattern holds on 11 of 13 tools (`_evidence-ui-audits.md` §9.1.3); PDFUploader input has no explicit aria-label but the wrapper's visible copy gives an implicit label (`_evidence-legacy-frontend.md` §13.1).
- Filename defect adjacent to accessibility/localization: merge's hardcoded English `merged.pdf` output name (`ui-five-tools-audit.md` L127; DEC-042 requires safe localized suffixes).

## 6. Alternatives

### Alternative A - Automated-tool-only QA (axe-core in CI plus Lighthouse)

- **What it is**: run axe-core and Lighthouse in the CI gate and treat passing scans as accessibility completion.
- **Trade-offs**: cheapest and repeatable, but every primary source limits it: axe-core documents "on average 57% of WCAG issues automatically" (evidence §5.4), WAVE states "Only a human can determine true accessibility", Lighthouse keeps trapped-focus, tab-order, and focus-directing checks manual, and DEC-062 explicitly requires representative manual keyboard and AT testing ("Automated checks are necessary but insufficient").
- **Risks**: keyboard traps, focus management, screen-reader announcements, and drag alternatives are exactly the failures this product's six interaction families are prone to (evidence §5.8), and automation alone misses them.
- **Verdict**: rejected as the sole method; retained as one layer inside Alternative B.

### Alternative B - Layered program: automated scans + manual keyboard passes + representative assistive-technology passes + documented exceptions register (recommended)

- **What it is**: a four-layer verification program: (1) automated scans (axe-core in CI with the WCAG 2.2 `target-size` rule enabled at AA, plus Lighthouse on representative routes); (2) manual keyboard-only completion of every tool flow across the supported matrix (WebAIM keyboard techniques); (3) representative AT passes on the top documented combinations (NVDA+Chrome primary, JAWS+Chrome/Edge, VoiceOver+Safari, TalkBack on Android, per Survey #10); (4) an exceptions register recording known exceptions with impact and remediation (DEC-062 consequence), never a blanket conformance claim.
- **Trade-offs**: more calendar time and skilled labor than A; requires scripted AT procedures so passes are repeatable; the AT pass is per-locale for core accessibility text (DEC-118).
- **Risks**: AT environments drift; mitigated by pinning procedures to the documented workflows (evidence §5.5) and recording tool versions.
- **Cost/operational impact**: moderate, one-time per surface plus per-change regression; aligns with arch §22.2 (automated scans plus manual passes) and DEC-062.
- **Privacy/security**: no document content leaves the device during testing; test fixtures are synthetic (DEC-066; legacy fixtures precedent `frontend/e2e/fixtures/generate-fixtures.ts`).

### Alternative C - Target WCAG 2.2 AAA

- **What it is**: raise the acceptance bar to AAA across the product.
- **Trade-offs**: AAA adds criteria like 2.4.13 Focus Appearance, 2.5.5 Target Size (Enhanced), 2.3.3, and 3.3.6; several conflict with the approved visual baseline (DEC-143) and the no-settings simplicity of the tools.
- **Risks**: scope creep against the one-month launch target (DEC-103) with little user-value gain for a task tool.
- **Verdict**: rejected; DEC-062 fixes AA, and AAA criteria remain a future option.

## 7. Recommendation

Recommendation only, not an accepted decision (DEC-054, DEC-057): adopt **Alternative B** with the following concrete acceptance coverage for the six interaction families. This maps the DEC-062 consequences to verification actions and to the WCAG 2.2 AA criteria in §5.2.

### 7.1 Coverage map

| Interaction | WCAG 2.2 AA criteria to satisfy | Verification (automated + manual) |
|---|---|---|
| Upload (dropzone, file input, accept validation) | 1.1.1, 1.3.1, 2.1.1, 2.1.2, 3.3.1, 3.3.2, 3.3.3, 4.1.2, 4.1.3 | axe scan; keyboard Enter/Space opens picker; `opacity:0` hidden input stays focusable (MDN §5.6); label association; error identified with suggestion; `role="alert"` on error card |
| Ordering (sortable lists, page ranges, per-page mode) | 2.1.1, 2.5.7, 2.5.8, 1.3.1, 4.1.2, 4.1.3 | dnd-kit keyboard sensors with `announcements` (UX §16.2 item 6; DEC-040); single-pointer non-drag alternative (SC 2.5.7, G219); drag handles `aria-label`; 24x24 px targets; PageRangeInput wired with `aria-invalid`/`aria-describedby` and live preview announcement |
| Progress (upload, queued, processing) | 2.2.1, 2.2.2, 4.1.3, 1.3.1 | `role="progressbar"` + `aria-valuenow` on determinate upload; `role="status"`/`aria-live="polite"` on stage transitions; `prefers-reduced-motion` for shimmer (UX §16.2 item 9); no auto-updating content without pause/stop/hide where it applies |
| Error (validation, sanitization, fallback, expiry) | 3.3.1, 3.3.2, 3.3.3, 3.3.4, 4.1.3, 1.4.11 | `role="alert"` on error cards, announced without stealing focus (UX §18 item 1, DEC-158); error summary pattern (WAI User Notifications); sanitization category messages localized and accessible (DEC-091); expiry warnings announced (DEC-067) |
| Result and download (done card, auto-download, manual button, multi-file) | 1.4.3, 2.1.1, 2.4.7, 2.4.11, 4.1.3 | `role="status"` on done transition; focus stays manageable (no forced focus move on status-only updates); Download button reachable and announced; blocked auto-download leaves the manual control (DEC-068); multi-file names accessible and localized (DEC-042) |
| Cross-cutting (nav, footer, language switcher, legal/status pages, blog) | 1.4.3, 1.4.4, 1.4.10, 1.4.11, 1.4.12, 2.4.1, 2.4.3, 2.4.4, 2.4.6, 2.4.7, 2.5.3, 2.5.8, 3.1.1, 3.1.2, 3.2.3, 3.2.4, 3.2.6, 3.3.7 | skip link + `main` (D8); `aria-expanded` on hamburger/category buttons; Escape-to-close; `focus-visible` styling app-wide; language switcher keyboard- and screen-reader-accessible with `aria-disabled` treatment (D9, DEC-149); lang attribute per locale (replaces hardcoded `lang="id"` at `frontend/src/app/layout.tsx:49`); target sizes; reflow at 320 px and 200% zoom; headings without h1-to-h3 jumps (insert visually hidden h2 or demote badges, per audit §6 item 8) |

### 7.2 Program rules

1. **Automated layer**: axe-core in the CI gate with WCAG 2.2 AA tags and the `target-size` rule enabled; Lighthouse accessibility audits on representative routes (`/`, one tool, one legal page). Scans are pass/fail gates, not scores against other sites (DEC-066).
2. **Manual keyboard layer**: full task completion for each of the five tools plus navigation, language switching, and legal/status/blog pages, keyboard only, on desktop Chrome and Safari, and on a mobile browser with an external keyboard (WebAIM guidance, evidence §5.5).
3. **AT layer**: scripted passes with NVDA+Chrome and JAWS+Chrome/Edge on Windows (top combos per Survey #10), VoiceOver+Safari on macOS/iOS, and TalkBack on Android; the scripts cover the six interaction families; core accessibility text is verified in all three locales (DEC-118).
4. **Exceptions register**: any known exception is documented with impact and remediation, and public wording never claims certification or universal conformance (DEC-062).
5. **Reduced motion**: shimmer and fade-up respect `prefers-reduced-motion` (UX §16.2 item 9); the entrance-animation question (U5/D12) is owned by B5.
6. **Contrast**: token combinations re-verified with a contrast tool during implementation (UX §21.12); method owned by B5.

## 8. Measurable acceptance criteria

Functional verification criteria, with no benchmark wording (DEC-066):

1. **Automated scans**: axe-core with WCAG 2.2 A/AA tags reports zero serious and critical violations on every page in the launch set (five tools x three locales, legal, support, status, blog) across the supported matrix.
2. **Keyboard completion**: each of the five tools can be completed end-to-end with keyboard only, including file selection, ordering, range entry, reset, and download, with no keyboard trap and a visible focus indicator at every step.
3. **Non-drag alternative**: every sortable list has a keyboard and single-pointer alternative (SC 2.5.7); drag handles have accessible names; dnd-kit `announcements` announce reorder feedback.
4. **Target sizing**: interactive targets meet the 24x24 CSS px minimum (SC 2.5.8) at all breakpoints, with documented exceptions.
5. **Status and progress**: upload progress uses `role="progressbar"` with `aria-valuenow`; stage transitions and errors are announced via live regions without stealing focus; the done state is announced.
6. **Contrast**: measured contrast meets 4.5:1 for text and 3:1 for large text and non-text UI (1.4.3, 1.4.11), including slate-400/300 tertiary text and accent-tinted states (UX §16.2 item 3; method in B5).
7. **Reflow and zoom**: layouts function at 200% zoom and 320 CSS px width without loss of content or functionality (SC 1.4.10, 1.4.4), including localized copy length growth (UX §16.1 item 6).
8. **Reduced motion**: with `prefers-reduced-motion` set, shimmer and fade-up animations are suppressed or reduced to non-motion states (UX §16.2 item 9).
9. **Semantic structure**: skip-to-content link, `main` landmark, correct heading order, and per-locale `lang` attributes are present on every page (2.4.1, 1.3.1, 3.1.1).
10. **Localized accessibility text**: labels, errors, status messages, and announcements are complete and consistent in EN, ES, and ID (DEC-118).
11. **Exceptions**: the exceptions register exists at implementation review with impact and remediation per entry, and no certification claim appears in any public copy (DEC-062).
12. **No benchmarks**: the program contains no comparative quality/performance study, corpus, matrix, or score program (DEC-066).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Tool coverage claims are vendor claims**: the axe-core 57% figure and the axe DevTools "up to 80%" figure come from Deque's own documentation, not independent measurement (evidence §5.4); the program relies on them only as justification for keeping the manual layer.
2. **Survey freshness**: WebAIM Survey #10 (Dec 2023 - Jan 2024) is the latest published as of access date; market-share statements cite it explicitly and should be re-checked at implementation.
3. **WCAG 2.2 revision**: the live normative text is the 12 December 2024 revision; the brief quotes that revision. The original 5 October 2023 REC date remains correct for the original publication.
4. **WAI resource gaps**: the WAI "Keyboard Testing" page (404) and the WAI "Forms - File Uploads" tutorial (does not exist) are not available; the substitutes are documented in §5.5-5.6.
5. **APG progressbar pattern removed**: the pattern index no longer includes Progressbar (404); the ARIA 1.2 role plus MDN live-region guidance plus native `<progress>` is the current reference (evidence §3.7).
6. **HTML CodeSniffer** documents WCAG 2.1 only; it is not a WCAG 2.2 evidence source.
7. **Hidden-input technique conflict**: MDN's drop-zone example uses `display:none` while its `<input type="file">` article recommends `opacity:0`; the rebuild follows the `opacity:0` (or visually-hidden-focusable) advice (evidence §6.2-6.3, note 8).
8. **Rendered checks deferred**: all contrast, spacing, and font-rendering claims remain unverified until the implementation-time browser pass (UX §21.11-12; B5 owns the method).
9. **Material owner questions**: (a) acceptance of the representative AT combination list (NVDA+Chrome, JAWS+Chrome/Edge, VoiceOver+Safari, TalkBack) as the required manual scope; (b) whether a short external accessibility review is desired in addition to the internal program (cost/scope decision); (c) confirmation that no AAA criteria are adopted at launch.
10. **Reduced-motion scope**: whether the homepage entrance-animation decision (U5/D12) changes what must respect `prefers-reduced-motion`; owned by B5.

## 10. Dependencies and cross-track interfaces

- **B5 (UI-baseline verification)**: owns the contrast re-verification method (UX §21.12), the `@theme inline` emission verification (UX §21.19), the rendered visual pass (UX §21.11), and the owner-confirmation prompts (D3, U3, U5/D12, Merge error-state edge case). B2 supplies the SC-level requirements those checks must meet; B5 supplies the execution boundary.
- **B1 (browser routing)**: routing transparency, fallback transitions, and error states must be announced accessibly (DEC-062, UX §18); B1's state machine feeds B2's status/progress coverage.
- **B3 (i18n/paper policy)**: localized accessibility text is a launch gate item (DEC-118); the language switcher is keyboard- and screen-reader-accessible (DEC-149, D9); paper-standard disclosure must be perceivable before processing (DEC-083, DEC-085).
- **D2/D5 (legal, privacy, security copy)**: sanitization notices (DEC-091), safe rejection messages (DEC-088, DEC-169), and Privacy-page disclosures (DEC-168) are user-facing text subject to the same accessible and localized standards.
- **Arch §22.1-22.2**: automated scans plus manual passes are part of the required testing layers (lines 935, 942).
- **Track A tool briefs (A2-A6)**: browser-local tool flows (merge/split/jpg-to-pdf/pdf-to-jpg) implement the interaction families this brief covers; their acceptance criteria must include the B2 checks.
- **X1/X2 (index/reconciliation)**: this brief contributes the AT-combination list, the exceptions-register rule, and the owner questions in §9.9 to the reconciliation decision prompts (plan §14).

## 11. Source-date log and evidence-completeness notes

- All web sources accessed 2026-07-31; versions and page dates recorded inline in `_evidence-b2-web.md` (WCAG 2.2 REC 2023-10-05 / current revision 2024-12-12; WAI-ARIA 1.2 REC 2023-06-06; axe-core 4.12.1 2026-06-09/10; Lighthouse page 2025-10-22; Android TalkBack page 2026-04-16; MDN `:focus-visible` last modified 2026-04-17; WebAIM Survey #10 data Dec 2023 - Jan 2024).
- Legacy evidence read 2026-07-31; all paths under `papyr-reference/`; line references cited in §5.8.
- Completeness notes: (a) all SC quotes in the evidence file were machine-extracted from the spec HTML and spot-checked by hand; (b) no browser execution was performed during research (plan §4.1), so all rendered claims are deferred to implementation per UX §21.11; (c) no benchmark or test-run evidence was created (DEC-066).
- Uncertainties from §9 are not resolved in this brief; they are recorded for the owner and for reconciliation (X2).

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066).
- No installs, builds, server starts, VPS/SSH access, deployment, account creation, browser execution, or authenticated/mutating remote actions were performed (plan §4.1).
- No product code, scaffolding, or infrastructure was created or modified; no decision log or specification was edited; no evidence file, audit file, or `papyr-reference/` file was modified.
- `papyr-reference/` was read-only; verified unchanged via `git -C papyr-reference status --porcelain` (empty output, exit 0) before and after this task.
- No claim of WCAG 2.2 AA conformance, certification, or universal accessibility is made (DEC-062); this brief defines the acceptance coverage and verification program.
- Findings in this brief are recommendations, not accepted decisions (DEC-054, DEC-057).
