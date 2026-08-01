# B5 - UI-Baseline Verification Checklist

## 1. Header

- **Brief ID**: B5
- **Path**: `<workspace-root>\audit-outputs\research\track-b\b5-ui-baseline-verification.md`
- **Track**: B - Frontend, capability, and SEO research
- **Title**: UI-baseline verification checklist
- **Date**: 2026-07-31
- **Author role**: Sisyphus-Junior (executor subagent, Track B)
- **Status**: Draft (complete for owner review under DEC-057; findings are recommendations, not accepted decisions; the rendered pass executes during implementation, not research)
- **Governing plan**: `<workspace-root>\audit-outputs\research-program-plan.md` (deliverable B5 at §6.2, including the checklist-and-scope note at line 124; Track B questions §7.2; brief template §8; verification §11)
- **Governing decisions**: DEC-143 (primary); supporting DEC-028, DEC-062, DEC-066, DEC-149, DEC-155, DEC-168, DEC-054 through DEC-060, DEC-188
- **Spec sections served**: Product and UX Design Specification §10 (Existing visual baseline, lines 183-282), §11 (lines 284-324), §16 (lines 552-582), §20.2 (lines 640-644), §20.3 (lines 646-660), §21 items 11-19 (lines 709-717); Technical Architecture Specification §22.2 (line 941)
- **Files read**:
  - `<workspace-root>\AGENTS.md`
  - `<workspace-root>\audit-outputs\research-program-plan.md`
  - `<workspace-root>\papyr-rebuild-decisions.md` (DEC-001 through DEC-188, Open decisions)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-product-ux-design.md` (§10, §11, §16, §20, §21)
  - `<workspace-root>\docs\superpowers\specs\2026-07-31-papyr-technical-architecture.md` (§22)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-ui-audits.md` (B5 evidence: D1-D13, U1-U7, DEC-143 baseline, verification methods)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-legacy-frontend.md` (globals.css, tokens, component evidence)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-decisions.md` (decision-log extraction)
  - `<workspace-root>\audit-outputs\research\track-b\_evidence-specs.md` (spec extraction)
  - UI audits (read via the evidence file): `audit-outputs/ui-home-shell-audit.md`, `audit-outputs/ui-five-tools-audit.md`, `audit-outputs/ui-docs-code-reconciliation.md`, `audit-outputs/spec-cross-review.md`, `audit-outputs/spec-corrections-report.md`
  - Legacy (read-only): `papyr-reference/frontend/src/app/globals.css`, `frontend/src/app/layout.tsx`, `frontend/src/components/Navbar.tsx`, `frontend/src/components/Footer.tsx`, `frontend/src/app/page.tsx` (per `_evidence-legacy-frontend.md` §2-§4 and `_evidence-ui-audits.md`)
- **Template note**: The plan §8 lists 12 numbered sections. The header sub-fields above are expanded as their own labeled fields; combined with the 12 numbered sections this satisfies both the plan's template and the 16-section instruction for Track B briefs (header sub-fields counted individually), following the Track A A1 precedent.

---

## 2. Scope

Per plan §6.2 (line 124), B5 is a checklist-and-scope deliverable: it packages the owner-confirmation items (navbar width intent D3, duplicate CTA intent U3, homepage entrance animations U5 and D12, Merge error-state edge case), the contrast re-verification method (UX §21.12), the `@theme inline` token emission verification (UX §21.19), and the rendered visual verification standard (UX §21.11). It defines the checklist, the evidence standard, and the owner decision prompts now, and defers the actual rendered pass to implementation-time verification. It does not execute the pass.

The user problem served: the rebuild must look and feel like the existing Papyr (DEC-143) while correcting the documented defects (D1-D13) without changing the visual character (UX §20.2 item 2). Because all three UI audits were static source inspections (UX §21.11: "all three audits were static source inspections, so spacing, contrast, and font rendering claims must be spot-checked in a browser during implementation"), the rendered verification standard must be defined before implementation so the pass can be executed consistently.

The current approved Papyr behavior this brief must support: the existing visual language is the primary UI/UX reference (DEC-143, lines 1695-1706: "The rebuilt website must look and feel like the existing Papyr website... its established visual identity, page composition, tool-directory presentation, component character, and familiar interaction patterns are the primary UI/UX reference"); changes are limited to purposeful improvements including accessibility and removal of legacy defects (DEC-143 consequences); defects D1-D13 are corrected without changing the visual character (UX §10.6, §20.2).

## 3. Non-goals

- No execution of the rendered pass: running a browser against the legacy site requires a build or server start, which this research phase prohibits (plan §4.1). The checklist and evidence standard are the deliverables.
- No redesign or new aesthetic: DEC-143 forbids a visibly different product; B5 verifies continuity, it does not propose a redesign.
- No copy rewrites beyond the flagged owner items: the audits' non-goal ("no redesign, no copy rewrites beyond fixing broken links, no new sections", `ui-home-shell-audit.md` L187) governs.
- No implementation of the D1-D13 fixes: the defect register is input to design (UX §10.6); B5 defines how the fixes are verified.
- No benchmark program, corpus, or comparative quality/performance evaluation (DEC-066). Side-by-side visual comparison against the legacy baseline is a continuity check, not a benchmark.
- No new audits of the legacy codebase beyond the five persisted audits already completed.

## 4. Research questions

Restated from plan §7.2 (B5) and the plan §6.2 note:

1. What are the exact owner-confirmation prompts for D3 (navbar width intent), U3 (duplicate CTA intent), U5 and D12 (homepage entrance animations and panel transitions), and the Merge error-state edge case, with the evidence each prompt relies on?
2. What is the contrast re-verification method for the documented token combinations (UX §21.12, DEC-062)?
3. What is the `@theme inline` token emission verification method so the body background, text color, and font never silently fall back (UX §21.19, U1)?
4. What is the rendered visual verification standard for the DEC-143 baseline (UX §21.11), and what counts as passing evidence?
5. Which adjacent owner-confirmation and verification items from UX §21 (items 17-18) and the audits' uncertainty list must be tracked alongside?
6. Why is the rendered pass deferred to implementation, and what evidence boundary does that create?

## 5. Evidence

### 5.1 The DEC-143 baseline and its verification anchor

Source: `_evidence-ui-audits.md` §8 and `_evidence-specs.md` §2.9.

- DEC-143 (verbatim, `_evidence-decisions.md` §2): the rebuilt site "must look and feel like the existing Papyr website"; legacy frontend pages and components are concrete visual and interaction references; preserve recognizable branding, color direction, typography character, card language, spacing rhythm, navigation model, uploader experience, and overall visual tone; changes are limited to purposeful improvements (consistency, responsive behavior, accessibility, localization resilience, truthful states, corrected interactions, performance, removal of legacy defects); material visual departures require explicit owner approval through comparison with the existing interface.
- The audits ARE the DEC-143 baseline evidence (`spec-cross-review.md` L112, quoted in `_evidence-ui-audits.md` §8.1): "Token table, typography, spacing/radius/shadow/motion, component character, D1-D13 corrections, and approved-change limits (UX §10, §20.2) match the home-shell and five-tools audits exactly (verified against `globals.css:3-10`, `page.tsx:486-593`, `Navbar.tsx:145-146`, `compress/page.tsx:94-135`). No invented tokens or visual claims."
- UX §20.2 items 1-2 (lines 642-643): recognizability verified "by side-by-side comparison of key surfaces (homepage, one tool page, navbar, footer) against the legacy clone"; defects D1-D13 corrected without changing the visual character.

### 5.2 Baseline facts the checklist must verify (all confirmed, source-grounded)

Source: `_evidence-ui-audits.md` §8.2-8.5 and `_evidence-legacy-frontend.md` §3.

- **Tokens** (`globals.css:3-10`, `@theme inline`): `--color-navy #1e3a5f`, `--color-accent #2563eb`, `--color-bg #f9fafb`, `--color-background #ffffff` (dead), `--color-foreground #171717`, `--font-sans 'DM Sans', system-ui, sans-serif`.
- **Typography**: DM Sans via next/font; hero `clamp(40px,6vw,72px)` semibold with `tracking-[-2px]`; tool-page h1 30/36px; nav labels 12px (md) / 14px (lg); eyebrow 12px uppercase tracking-widest.
- **Spacing/radius/shadow**: 1200px content column (navbar 1440px, D3); section rhythm pt-24/pb-20, py-20, py-[72px]; radii 10px cards, 16px tool hero tile, 8px nav CTA; shadows `0 1px 3px rgba(0,0,0,0.04)` resting and `0 4px 20px rgba(37,99,235,0.1)` accent hover.
- **Motion**: `animate-shimmer` 1.4s, `animate-fade-up` 0.3s (globals.css:19-44); tool pages use fade-up for every state-transition card (63 matches in 12 files); homepage uses none (U5); dropdown panels appear instantly (D12); rotate has a 1.2s inline shimmer deviation (`rotate/page.tsx:567`).
- **Component inventory**: page shell (max-w-xl, icon tile, h1, subtitle, context paragraph), feature badge grid, dropzone contract (`role="button"`, `tabIndex={0}`, Enter/Space, hidden input, 20MB constraint line), processing/done/error state cards, PrivacyNotice (three model strings), PageRangeInput, sortable lists, before/after size panel, OtherTools section, exported data contracts (TOOLS, NAV_CATEGORIES, FOOTER_TOOL_CATEGORIES).
- **Shell**: frosted sticky navbar (bg-bg/92 backdrop-blur-md, 52px), native `<details>` mobile accordion, sticky-footer flex shell (layout.tsx:49-53), language switcher in footer (D9), dead footer links (D1).

### 5.3 Owner-confirmation items (the prompts)

Source: `_evidence-ui-audits.md` §1-§4, §11 (residual owner questions).

1. **D3 / U2 - Navbar width intent**: the navbar container is `max-w-[1440px]` (`Navbar.tsx:146`) while every other container is `max-w-[1200px]` (`page.tsx:488,532,535,569`; `Footer.tsx:171,198`). The audits could not determine intent (U2: "deliberate breathing room or drift?"), and the legacy docs claimed a universal 1200px. Owner question: (a) unify everything to 1200px; (b) keep the 1440px navbar as the documented convention ("1440px navbar + 1200px content", the reconciliation's recommendation); or (c) another value.
2. **U3 - Duplicate CTA intent**: navbar "Coba Gratis" (`Navbar.tsx:207-212`) and hero "Mulai gratis" (`page.tsx:510-515`) both target `/compress`; a third compact "Coba Gratis" exists in the mobile navbar. Owner question: is the deliberate funnel to Compress intended, or should the hero CTA change? (Legacy primary CTA color note: the hero is navy, all tool-page primary actions are accent blue.)
3. **U5 / D12 - Homepage entrance animations**: the homepage has no entrance animations while every tool page uses `animate-fade-up` (U5); dropdown panels and the mobile menu open/close instantly (D12). Owner question: (a) unify by adding fade-up to the homepage hero/sections; (b) keep the calm hero deliberately and document it; and separately, (c) add a short panel fade or keep instant behavior as a documented choice. This also determines what `prefers-reduced-motion` must suppress (B2).
4. **Merge error-state edge case**: in the legacy merge flow, `addFiles` sets state to idle only when `errors.length === 0`; adding a valid file alongside an invalid one while in `error` state adds the file but leaves state at `error` until "Coba Lagi" is clicked (files persist across error, list kept). Owner question: auto-clear the error when valid files are added (recommended in the audit), or keep the legacy behavior?
5. **Adjacent prompts (recorded, tracked)**: U4 - the inert English "Segera hadir" switcher row: keep visible-but-inert or hide until implemented (the rebuild implements EN at launch, so this becomes: how the switcher presents the active locale, owned by DEC-149); compress `quality=ebook` legacy lock (`ui-five-tools-audit.md` §8.6) - resolved by DEC-014's automatic premium mode but the ebook-preset reality must be documented; LIGHTHOUSE.md theme-script drift (`_evidence-legacy-frontend.md` §2.2, §10.2) - recorded, resolved by the @theme verification in §6.2 below.

### 5.4 UX §21 items 11-19 (the verification scope)

Source: `_evidence-specs.md` §2.1 (UX §21 in full).

| UX §21 item | Content | Owner of the check |
|---|---|---|
| 21.11 (line 709) | Rendered visual verification of the baseline: static audits only, so spacing, contrast, and font rendering claims must be spot-checked in a browser during implementation (audits U7) | This brief defines the standard (§6.3); the pass executes during implementation |
| 21.12 (line 710) | Contrast re-verification of the documented token combinations with a contrast tool (DEC-062) | This brief defines the method (§6.1) |
| 21.13 (line 711) | Navbar width intent D3 (U2) needs owner confirmation before unification | Owner prompt (§5.3 item 1) |
| 21.14 (line 712) | Duplicate CTA intent U3: confirm whether the funnel is deliberate | Owner prompt (§5.3 item 2) |
| 21.15 (line 713) | Homepage entrance animations U5, which also resolves D12 | Owner prompt (§5.3 item 3) |
| 21.16 (line 714) | Merge error-state edge case: confirm the desired auto-clear behavior | Owner prompt (§5.3 item 4) |
| 21.17 (line 715) | Privacy copy re-scoping of legacy "no tracking" / "no personal data" statements | Owned by D2 (legal/privacy copy) and UX §17 item 7; B5 records it in the tracked-items register |
| 21.18 (line 716) | FAQ copy accuracy: JPG/JPEG/PNG/WebP formats per DEC-187 | Owned by the copy pass (DEC-187 consequence); B5 records it in the tracked-items register |
| 21.19 (line 717) | `@theme inline` token emission verification (U1) | This brief defines the method (§6.2) |

### 5.5 The rendered-pass boundary

Source: plan §6.2 (line 124) and `_evidence-ui-audits.md` §7, §10.

- Plan §6.2: "Because running a browser against the legacy site requires a build or server start, which this phase prohibits, B5 defines the checklist, evidence standard, and owner decision prompts now and defers the actual rendered pass to implementation-time verification. It does not execute the pass."
- All three audits state the same boundary: `ui-home-shell-audit.md` L198 (U7): "No rendered verification was possible in this audit... all visual claims are derived from source classes and should be spot-checked in the browser during rebuild validation"; `ui-five-tools-audit.md` L292 and `ui-docs-code-reconciliation.md` L325 record the same for spacing, contrast, and font rendering.
- No numeric contrast ratio was measured in any audit; every file defers measurement to a tool-based pass (evidence §5.3 in `_evidence-ui-audits.md`).

## 6. Alternatives

### Verification-method options for the three technical checks

**Contrast (UX §21.12):**

- **Alternative A - Tool-based measurement at implementation (recommended)**: compute WCAG contrast ratios for the documented pairs with a color-contrast tool and record pass/fail per pair. Pairs to measure (from `_evidence-ui-audits.md` §5.2): navy #1e3a5f against bg #f9fafb and white (headings, primary CTA), foreground #171717 against bg, accent #2563eb against white (nav CTA, download buttons), slate-500/400/300 secondary and tertiary text, `text-accent/80` on the Compress "Sesudah" label, and `bg-slate-50` panel text. Targets: 4.5:1 for text, 3:1 for large text and non-text UI (WCAG 1.4.3, 1.4.11). Trade-offs: requires the tool at implementation; deterministic and recordable. Recommended.
- **Alternative B - Static ratio claims now**: would fabricate numbers the audits explicitly did not measure. Rejected.

**`@theme inline` emission (UX §21.19, U1):**

- **Alternative A - Build-time and computed-style verification (recommended)**: at implementation, (1) build and grep the compiled CSS for `--color-bg`, `--color-foreground`, and `--font-sans` in a `:root` block; or (2) inspect the body's computed background, text color, and font-family in a browser. If the variables are not emitted, use utilities (`bg-bg`, `text-foreground`, `font-sans`) or a non-inline `@theme` for any direct `var()` use (the audit's recommended fix, `_evidence-ui-audits.md` §6). Also resolve the dead tokens (D4: `--color-background`, `--font-dm-sans`). Recommended.
- **Alternative B - Assume Tailwind v4 emits them**: the audit records the repo contains no compiled CSS artifact, so this is unverifiable and was flagged "verify first" (U1). Rejected as the sole method.

**Rendered visual verification (UX §21.11):**

- **Alternative A - Side-by-side comparison at implementation (recommended)**: run the rebuilt site locally and the legacy clone locally (implementation phase permits this), and compare the key surfaces named by UX §20.2 (homepage, one tool page, navbar, footer) against the legacy baseline, at defined viewports (375 px, 768 px, 1280 px, 1440 px), capturing screenshots and recording pass/fail per surface against the §5.2 baseline facts. Also spot-check the audit's spacing, contrast, and font claims (U7). Recommended.
- **Alternative B - Execute the rendered pass during research**: requires a build or server start, prohibited by plan §4.1. Rejected and recorded as the execution-boundary rule.
- **Alternative C - Rely on the static audits alone**: the specs themselves reject this (UX §21.11: rendered claims "must be spot-checked in a browser"). Rejected.

### Program-shape options for the checklist

- **Alternative A - Single B5 checklist owned by implementation (recommended)**: one tracked checklist covering owner prompts, contrast, @theme, and rendered surfaces, with an evidence standard (screenshot + recorded pass/fail + exception note per item). This matches plan §6.2's checklist-and-scope design.
- **Alternative B - Defer everything to the accessibility program**: would lose the visual-continuity checks (DEC-143) that are not accessibility items. Rejected.

## 7. Recommendation

Recommendation only, not an accepted decision (DEC-054, DEC-057): adopt the recommended alternatives in §6 and the following checklist as the B5 deliverable. The owner answers the four core prompts in §5.3 (D3, U3, U5/D12, Merge edge case); the implementation verifies the three technical checks (§6.1-6.3); the rendered pass executes during implementation, not research.

### 7.1 Owner decision prompts (to be answered before or during design approval)

1. **D3**: choose one width convention: unify to 1200px, keep the 1440px navbar + 1200px content convention, or another value. Recorded as UX §21.13.
2. **U3**: confirm whether the duplicate Compress CTAs are a deliberate funnel (nav + hero + mobile nav) or whether the hero CTA should change. Recorded as UX §21.14.
3. **U5/D12**: decide homepage entrance animations (add fade-up to match tool pages, or keep the calm hero deliberately) and the panel transition behavior (short fade or documented instant). Recorded as UX §21.15.
4. **Merge error-state edge case**: confirm auto-clear of the error when valid files are added (audit recommendation) or retention of the legacy behavior. Recorded as UX §21.16.

Each prompt cites the evidence in §5.3; the audit files are the source of the exact legacy behavior.

### 7.2 Contrast re-verification method (UX §21.12)

- Execute during implementation with a color-contrast tool (WCAG ratio computation).
- Measure and record the pairs in §6.1 with their ratios and pass/fail against 4.5:1 (text) and 3:1 (large text and non-text).
- Any failing pair is either corrected within the DEC-143 baseline (an approved accessibility change, DEC-062, DEC-143) or recorded in the B2 exceptions register with impact and remediation (DEC-062).
- No ratio is published or claimed until measured; no certification claim is made (DEC-062).

### 7.3 `@theme inline` emission verification (UX §21.19)

- Execute during implementation: build and grep the compiled CSS for `--color-bg`, `--color-foreground`, and `--font-sans` in a `:root` block, or inspect body computed background, color, and font-family in a browser.
- If the custom properties are not emitted, switch direct `var()` uses in plain CSS to utilities (`bg-bg`, `text-foreground`, `font-sans`) or to a non-inline `@theme`, so the body background, text color, and font never silently fall back (U1/D5).
- Resolve the dead tokens (D4): wire `--font-dm-sans` correctly or drop it; drop or use `--color-background`.
- Record the result as pass/fail with the compiled-CSS or computed-style evidence.

### 7.4 Rendered visual verification standard (UX §21.11)

- Surface set: homepage, one representative tool page (Compress), navbar, footer, plus the five-tool state cards (processing, done, error) per UX §20.2 and the preserve inventory (§5.2).
- Viewports: 375 px, 768 px, 1280 px, 1440 px; capture screenshots of the rebuilt site and the legacy clone side by side.
- Check list against the §5.2 baseline facts: token colors render as declared; DM Sans renders with the correct fallback; spacing rhythm and radii match; fade-up/shimmer motion matches (respecting `prefers-reduced-motion`, B2); dropzone contract, state-card language, and OtherTools/Related Tools sections match; no h1-to-h3 jumps remain (D8); language switcher shows the active locale (D9, DEC-149).
- Evidence standard per surface: screenshot pair plus a recorded pass/fail and any exception note; exceptions are routed to the D1-D13 defect register or the B2 exceptions register as applicable.
- Record explicitly that this pass executes during implementation verification (arch §22.2), not during research, and that the static audits remain the source of the claims being spot-checked (U7).

### 7.5 Tracked-items register (adjacent items)

- **Privacy copy re-scoping (UX §21.17)**: owned by D2; verification item: legacy claims such as "no tracking" and "no personal data at all" (`frontend/src/app/privacy/page.tsx:47,73`, `faq/page.tsx:61`) are absent from the rebuilt Privacy page.
- **FAQ copy accuracy (UX §21.18)**: owned by the copy pass; verification item: FAQ and tool copy state JPG/JPEG, PNG, and WebP as the accepted formats (DEC-187), correcting the legacy claims.
- **Compress quality note**: the automatic premium-screen mode (DEC-014) replaces the legacy `quality=ebook` behavior; the legacy ebook-preset reality is documented in the tool flow, not repeated in copy.
- **LIGHTHOUSE.md drift**: the documented "theme inline script" does not exist in the legacy layout (doc/code drift); the rebuild's theme handling is verified by the §7.3 method instead.

## 8. Measurable acceptance criteria

Functional verification criteria, with no benchmark wording (DEC-066):

1. **Owner prompts answered**: the four core prompts (D3, U3, U5/D12, Merge edge case) have recorded owner answers before the design is finalized (UX §21.13-16).
2. **Contrast record**: every pair in §7.2 is measured and recorded with its ratio and pass/fail; failing pairs are corrected or documented in the B2 exceptions register.
3. **Token emission record**: the build/computed-style check for `--color-bg`, `--color-foreground`, and `--font-sans` is recorded as pass/fail; a fallback (utilities or non-inline `@theme`) is in place if the variables are not emitted; dead tokens are resolved (D4, D5, U1).
4. **Rendered pass record**: screenshots exist for the §7.4 surface set at the defined viewports for the rebuilt site and the legacy clone, with per-surface pass/fail and exception notes.
5. **Visual continuity**: the rebuilt site is recognizable as the existing Papyr per UX §20.2 item 1, verified by the side-by-side comparison; D1-D13 corrections are present without changing the visual character (UX §20.2 item 2).
6. **Reduced motion**: fade-up/shimmer and any new entrance animation respect `prefers-reduced-motion` (UX §16.2 item 9; B2).
7. **Fully resolved checklist**: the implementation's checklist carries no unresolved marker tokens; every item is either done, recorded, or explicitly deferred with a reason.
8. **No benchmarks**: the verification contains no comparative quality/performance study, corpus, matrix, or score program (DEC-066). Side-by-side visual comparison is a continuity check per DEC-143, not a benchmark.

## 9. Assumptions, uncertainties, and unresolved questions

1. **U2 (navbar width intent)**: genuinely unresolved; only the owner can answer whether the 1440px navbar is deliberate. Until answered, the reconciliation's "1440px navbar + 1200px content" convention is the working default (recommendation, not decision).
2. **U3 (duplicate CTA intent)**: unresolved; the audits judge the funnel "likely deliberate" but record no confirmation.
3. **U4 (inert English switcher row)**: superseded by the rebuild's EN launch (DEC-004); the residual question is how the switcher presents three active locales (DEC-149), which is a design item, not an open audit uncertainty.
4. **U5/D12 direction**: unresolved; the answer also determines the reduced-motion scope for any new homepage animation (B2).
5. **Merge error-state edge case**: unresolved; the audit recommends auto-clear, the owner decides (UX §21.16).
6. **Contrast values are unmeasured**: no audit measured a single ratio; every figure in the docs and audits is pending the §7.2 tool pass. This brief intentionally records no invented ratio.
7. **Tailwind v4 `@theme inline` emission** is version-dependent and unverified (U1); the §7.3 check is the authoritative resolution.
8. **OG-image internals and favicon**: the reconciliation flagged `opengraph-image.tsx`/`twitter-image.tsx` interplay and favicon handling as unverified; these are B4 (SEO metadata) and implementation items, recorded here for completeness.
9. **Historical doc states**: whether the legacy docs matched the code at their authored dates is unverifiable without git history (reconciliation §8.1); not needed for the baseline because the code is the DEC-143 reference.
10. **Material owner questions**: the four prompts in §7.1 plus (a) acceptance of the viewport set (375/768/1280/1440) and surface set for the rendered pass; (b) whether the side-by-side comparison should be captured against the archived legacy clone or against the documented baseline facts only.

## 10. Dependencies and cross-track interfaces

- **B2 (accessibility)**: supplies the SC-level targets for contrast (1.4.3, 1.4.11), focus visibility, and reduced motion; the B2 exceptions register receives the failing-contrast entries. B5 supplies the contrast method and the rendered-pass boundary B2's rendered checks need.
- **B1 (browser routing)**: the tool-page state cards (processing, done, error) verified in §7.4 include the routing-transparency states (local vs server); the rendered pass confirms they render as specified.
- **B3 (i18n/paper policy)**: the language switcher (D9) and localized copy-length resilience are verified in the rendered pass; the paper-standard disclosure visibility is a B3 acceptance item.
- **B4 (SEO/URL)**: metadata rendering (per-locale titles, OG images) is part of the rendered surface check; B4 owns the URL/metadata structure.
- **D2 (legal/privacy copy)**: the tracked items in §7.5 (privacy copy re-scoping, FAQ formats) are D2/copy ownership; B5 records them so they are not lost.
- **DEC-143 and the audits**: this brief is the bridge from the static audits (U7) to the implementation-time verification the specs require (UX §21.11, §20.2; arch §22.2).
- **X1/X2 (index/reconciliation)**: this brief contributes the four owner prompts and the §9.10 questions to the reconciliation decision-prompt list (plan §14).

## 11. Source-date log and evidence-completeness notes

- All audit files were created 2026-07-31; the evidence file `_evidence-ui-audits.md` was created 2026-07-31 and quotes every relevant passage verbatim with source path and line range. Legacy file:line references (e.g., `Navbar.tsx:146`, `page.tsx:510-515`, `globals.css:3-10`) are cited as recorded in the audits.
- No web research was required for this brief: all claims come from the five persisted audits, the two specs, and the decision log (plan §8 source priority).
- Completeness notes: (a) this brief deliberately contains no rendered verification because the phase prohibits builds and server starts (plan §4.1); (b) the B5 checklist maps every UX §21.11-19 item to an owner prompt, a method, or a tracked owner; (c) no benchmark or test-run evidence was created (DEC-066).
- Uncertainties from §9 are not resolved in this brief; they are recorded for the owner and for reconciliation (X2).

## 12. Prohibitions-compliance statement

- No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066).
- No installs, builds, server starts, browser execution, VPS/SSH access, deployment, or authenticated/mutating remote actions were performed (plan §4.1). The rendered pass was not executed.
- No product code, scaffolding, or infrastructure was created or modified; no decision log or specification was edited; no evidence file, audit file, or `papyr-reference/` file was modified.
- `papyr-reference/` was read-only; verified unchanged via `git -C papyr-reference status --porcelain` (empty output, exit 0) before and after this task.
- No contrast ratio, rendered-pixel, or visual-continuity claim is made beyond what the audits verified statically; all rendered claims are deferred to the implementation-time pass (U7, UX §21.11).
- Findings in this brief are recommendations, not accepted decisions (DEC-054, DEC-057).
