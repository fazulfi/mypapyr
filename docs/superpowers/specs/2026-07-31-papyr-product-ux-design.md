# Papyr Rebuild: Product and UX Design Specification

- **Document type:** Canonical design specification (English)
- **Date:** 2026-07-31
- **Status:** Approved by DEC-188; revised to incorporate DEC-189 to DEC-196; not an implementation authorization
- **Sibling document:** Technical Architecture Specification (DEC-185)
- **Decision baseline:** DEC-001 through DEC-196 in `papyr-rebuild-decisions.md`
- **Revision:** 2026-07-31 (incorporates DEC-189 through DEC-196 and the completed cross-domain reconciliation, X2)
- **Primary reference baseline:** `papyr-reference/` (read-only legacy clone), per DEC-143

---

## 1. Status

This specification is approved by DEC-188 and revised to incorporate DEC-189 to DEC-196; it is not an implementation authorization. It consolidates the accepted product and UX decisions DEC-001 through DEC-196 into one canonical document, grounded in the read-only legacy UI in `papyr-reference/` and the audit deliverables in `audit-outputs/`. This revision incorporates the completed cross-domain reconciliation (`audit-outputs/research/reconciliation-report.md`, X2) and the owner decisions DEC-189 through DEC-196 that resolved its open questions. Research findings and recommendations from the reconciliation remain non-normative design inputs until accepted (DEC-054, DEC-057); only accepted decisions are normative.

It is one of two coordinated specifications approved by DEC-183 and split by DEC-185. It covers product scope, users, information architecture, localization, the existing visual baseline, shell and homepage behavior, the five tool flows, shared states, advertising placement, content and legal surfaces, responsive and accessibility requirements, analytics and privacy boundaries, error and recovery behavior, SEO and content migration constraints, acceptance criteria, and unresolved items.

Writing this document is authorized by DEC-183 and DEC-184. It does not authorize implementation, infrastructure modification, VPS access, or deployment. Implementation remains blocked per DEC-060, DEC-057, and DEC-185 until the owner reviews and approves the design and an implementation plan.

Any material contradiction discovered between the accepted decisions and this specification must be surfaced to the owner rather than silently resolved (DEC-183).

## 2. Scope

This specification defines:

1. The product promise, primary users, and launch scope of the rebuilt Papyr.
2. The information architecture and locale strategy for EN, ES, and ID.
3. The existing visual baseline that the rebuild must preserve (DEC-143), including what to retain and which documented defects to correct.
4. The app shell, homepage, and per-tool page structure and interaction behavior.
5. Detailed flows for Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG.
6. Shared states, download behavior, retention UX, cancellation, refresh recovery, and reset behavior.
7. Advertising placement rules.
8. Content, legal, support, status, and blog surfaces.
9. Responsive behavior and WCAG 2.2 Level AA acceptance coverage.
10. Analytics and privacy UX boundaries.
11. Error and recovery behavior.
12. SEO and content migration constraints.
13. Acceptance criteria and unresolved items.

Processing internals, engine selection, queue behavior, server limits, security controls, deployment, and operations are responsibilities of the sibling Technical Architecture Specification and are referenced here only where the user experience depends on them.

## 3. Non-goals

The following are explicitly out of scope for this specification and for the relaunch:

1. **Implementation.** No scaffolding, product code, infrastructure, or deployment work is authorized by this document (DEC-060, DEC-183, DEC-185).
2. **Redesign.** The rebuild does not introduce a new aesthetic, a dashboard-style shell, a universal workspace, an unrelated design system, or a fashionable visual treatment (DEC-143).
3. **Accounts and personalization.** No authentication, profiles, cloud history, saved files, or cross-device synchronization (DEC-012).
4. **Paid access.** No subscriptions, payments, credits, trials, premium gates, or account-based upsells in the first year, and no paid fast lane (DEC-105, DEC-132, DEC-133, DEC-134).
5. **Benchmark program.** No benchmark corpora, matrices, comparative performance studies, quality-score programs, or benchmark reports (DEC-066).
6. **Session replay and fingerprinting.** No session replay on document workflows, no masking-only approaches, and no stable device fingerprints (DEC-025).
7. **Beyond the five tools at launch.** Rotate, protect/unlock, watermark, sign, OCR, PDF to Word, and PDF to Excel are post-launch candidates, not launch scope (DEC-009, DEC-010, DEC-094).
8. **Page-level merge editing.** Merge has no cross-document page-level editor in the MVP (DEC-040).
9. **Competitor comparison pages.** No alternative, versus, or competitor-comparison landing pages at relaunch (DEC-128).
10. **Newsletter at launch.** No newsletter subscription or email-marketing infrastructure in the one-month scope (DEC-107, DEC-109).
11. **Social media.** No mandatory social accounts or publishing program (DEC-112).
12. **Donations.** No donation, tip, or supporter-payment mechanisms (DEC-111).
13. **Public usage counters.** No public files-processed, users-served, or downloads-completed counters (DEC-126).
14. **Interactive roadmap.** No public voting, comments, or feature-request mechanisms on the roadmap (DEC-125).
15. **Intrusive advertising.** No popunders, interstitials, social bars, in-page push, forced redirects, or anti-adblock messaging (DEC-018).
16. **Public API and business offerings.** No business API, organizations, API keys, or enterprise plans in the first year (DEC-108).
17. **Public beta or staging phase.** The relaunch switches directly to production after pre-release verification (DEC-096).
18. **Alternative monetization.** No fallback ad network, sponsorship, or replacement monetization plan if Adsterra underperforms (DEC-135, DEC-136).

## 4. Sources and precedence

Precedence, from highest to lowest:

1. **Accepted rebuild decisions** in `papyr-rebuild-decisions.md` (DEC-001 through DEC-196). This is the authoritative decision baseline. Where this specification conflicts with a decision, the decision wins and the contradiction must be reported.
2. **The read-only legacy UI** in `papyr-reference/`, which is the binding visual and interaction baseline per DEC-143. Existing implementation behavior is retained unless a decision or a documented defect requires change.
3. **The audit deliverables** in `audit-outputs/`, which document the baseline precisely with file and line references:
   - `audit-outputs/ui-home-shell-audit.md` (shell, navbar, footer, homepage; 13 defect items D1-D13)
   - `audit-outputs/ui-five-tools-audit.md` (page-by-page audit of the five launch tools)
   - `audit-outputs/ui-docs-code-reconciliation.md` (documentation versus code reconciliation)
   - `audit-outputs/research/reconciliation-report.md` (X2 cross-domain reconciliation; classifies research findings as compatible recommendations, genuine conflicts resolved by DEC-189 through DEC-196, deferred defaults, and owner-side source blockers)
4. **Legacy documentation** in `papyr-reference/docs/` (for example `19_Papyr_UIUX_Spec_v1.0.md` and `32_Papyr_Brand_Guidelines_v1.0.md`). These are historical and non-canonical (DEC-026); they inform the baseline but do not override the code or the decisions.

Research findings, recommendations, and defaults recorded in the audit deliverables are design inputs, not decisions; only accepted decisions are normative (DEC-054, DEC-057).

### 4.1 Evidence conventions used in this document

- Decision citations use the DEC-ID, for example (DEC-143).
- Legacy source citations use paths relative to `papyr-reference/`, for example `frontend/src/app/globals.css:3-10`.
- Audit citations use `audit-outputs/<file>.md` with section or item references, for example `audit-outputs/ui-home-shell-audit.md §5` or `audit-outputs/ui-five-tools-audit.md §6`.
- The audits were static source inspections; visual claims were not browser-verified (see Section 21, items on rendered verification).

## 5. Product goals

The accepted product direction, in priority order:

1. **Fast and simple task completion.** The highest product priority is a fast, simple path from arrival to completed PDF task (DEC-008). The core flow is open tool, select files, configure only what is necessary, process, download.
2. **Speed, ease, and free as the first message.** The first thing a new visitor understands is that Papyr provides PDF tools that are fast, easy, and free (DEC-139).
3. **Fast and trustworthy brand character.** Professional, direct, calm, and easy to understand; no hype, unsupported superlatives, manipulative urgency, or overly technical user-facing language (DEC-101).
4. **Privacy and honesty as supporting evidence.** Trust comes from clear product behavior, honest claims, transparent policies, and reliable operations (DEC-110), including truthful processing-path and retention information (DEC-168), honest compression reporting (DEC-080), and honest progress stages (DEC-033).
5. **Free forever core tools.** All core public PDF tools remain free to use and download (DEC-132, DEC-133), bounded by fair-use, safety, file-size, capacity, and abuse controls (DEC-020, DEC-035, DEC-134).
6. **Organic growth through SEO and the localized blog.** Tool pages and blog content serve genuine user intent; approved Adsterra placements monetize traffic rather than act as an acquisition channel (DEC-106).
7. **90-day success judged by reliability and organic growth.** Reliable completion, fast UX, healthy Core Web Vitals, organic-search growth, and meaningful usage across all five tools; advertising revenue is a secondary indicator (DEC-024).
8. **UX ahead of advertising revenue.** When advertising and task completion conflict, user experience wins (DEC-102).

## 6. Users

The primary launch audience is a general user arriving to complete one PDF task quickly, usually without wanting to learn a product or create an account (DEC-007). Consequences for design:

1. Anonymous, no-sign-up usage is the default assumption (DEC-007, DEC-012).
2. Landing pages satisfy search intent directly and avoid dashboards and onboarding (DEC-007).
3. Time-to-first-action and cognitive load are minimized; optional controls use progressive disclosure (DEC-008).
4. First-year scope serves general individual web users; no business API, organization, or enterprise product (DEC-108).
5. The product is presented as a brand without a founder profile, personal photograph, or origin story (DEC-110).

Target regions are the United States, Latin America, and Europe, launched simultaneously (DEC-003, DEC-104). Indonesian content is preserved and Indonesian is a first-class launch locale (DEC-115, DEC-118), with the legacy Indonesia-first positioning dropped from the international identity (DEC-002, DEC-003, DEC-021).

## 7. Launch scope

The public relaunch requires, before launch (DEC-027, DEC-118):

1. Five production-ready tools: Compress PDF, Merge PDF, Split PDF, JPG to PDF, and PDF to JPG (DEC-009, DEC-010).
2. Complete English, Spanish, and Indonesian experiences for every tool and essential supporting surface (DEC-004, DEC-115, DEC-118).
3. Privacy, Terms, and Cookies/Advertising pages in all three locales (DEC-045).
4. A support email and a categorized contact form (DEC-046), routed to the owner-managed inbox (DEC-050).
5. A simple public status page, hosted on Vercel and automatically derived from health signals (DEC-116, DEC-119, DEC-161).
6. A concise informational roadmap (DEC-123, DEC-125) that states the free-forever core commitment (DEC-138).
7. Fifteen launch blog articles: five topics, each localized into EN, ES, and ID (DEC-052, DEC-121), stored as version-controlled MDX (DEC-049).
8. The full legacy public URL inventory audited with an explicit disposition for every URL (DEC-127); deferred legacy tool URLs return an intentional localized 410 Gone by default (DEC-194).
9. Direct activation on the production domain without a launch campaign (DEC-096, DEC-140).

The target is completion within one month (DEC-100). If the approved scope cannot be made production-ready in that window, the launch is delayed rather than cut or degraded (DEC-103). Launch completeness means five production-ready tools, not partial implementations (DEC-009). One incomplete or unreliable tool blocks the public launch unless a later explicit scope decision removes it (DEC-027).

## 8. Information architecture

### 8.1 Model

The rebuilt product uses the evolved directory model (DEC-142): a clear homepage presenting the five tools, with each dedicated tool page following a focused select, configure-if-needed, process, and download journey. The homepage is not replaced by a universal uploader, and the product is not reduced to context-free tool pages (DEC-142).

### 8.2 Routes and locale prefixes

Every localized route carries an explicit locale prefix, including English (DEC-023). English does not use unprefixed tool routes as canonical URLs. Route structure:

| Surface | Route pattern |
| --- | --- |
| Homepage | `/en/`, `/es/`, `/id/` |
| Compress PDF | `/en/compress-pdf`, `/es/<slug>`, `/id/<slug>` |
| Merge PDF | `/en/merge-pdf`, `/es/<slug>`, `/id/<slug>` |
| Split PDF | `/en/split-pdf`, `/es/<slug>`, `/id/<slug>` |
| JPG to PDF | `/en/jpg-to-pdf`, `/es/<slug>`, `/id/<slug>` |
| PDF to JPG | `/en/pdf-to-jpg`, `/es/<slug>`, `/id/<slug>` |
| Privacy | `/en/privacy`, `/es/<slug>`, `/id/<slug>` |
| Terms | `/en/terms`, `/es/<slug>`, `/id/<slug>` |
| Cookies/Advertising | `/en/cookies-advertising`, `/es/<slug>`, `/id/<slug>` |
| Contact/Support | `/en/contact`, `/es/<slug>`, `/id/<slug>` |
| Status | `<locale>/status` |
| Roadmap | `<locale>/roadmap` |
| Blog index | `<locale>/blog` |
| Blog article | `<locale>/blog/<slug>` |

Notes:

1. Exact slugs are selected during SEO design (Section 19); Indonesian tool and content URLs use translated, search-appropriate slugs (DEC-122), and EN/ES use their own localized slug policies (DEC-023).
2. Locale-less entry is redirected once according to supported browser-language preferences, with a persistent manual language switcher whose explicit choice takes precedence (DEC-047). Unsupported languages fall back to English (DEC-047).
3. Legacy unprefixed URLs require a deliberate redirect map under the SEO design (DEC-023, DEC-099, DEC-127). Deferred legacy tool URLs return an intentional localized 410 Gone by default, with a targeted relevant redirect only where credible traffic or intent evidence justifies it (DEC-194).
4. Tool pages remain available during backend outages; the frontend must not redirect ordinary tool traffic to the status page (DEC-163).

### 8.3 Navigation model

The existing categorized navbar model is retained (DEC-147). At launch it is populated only with the five available tools; deferred tools do not appear as active destinations, empty categories are omitted or sensibly consolidated, and no coming-soon links or dead destinations exist in primary navigation (DEC-152). Category labels and destinations are localized consistently across EN, ES, and ID (DEC-152). The mobile category accordion is preserved with corrected expansion, focus, keyboard, touch-target, active-page, and screen-reader behavior (DEC-155).

### 8.4 Catalog single source of truth

The legacy tool catalog exists in four divergent copies (`audit-outputs/ui-home-shell-audit.md` D2): `NAV_CATEGORIES` in `frontend/src/components/Navbar.tsx:83-117`, `FOOTER_TOOL_CATEGORIES` in `frontend/src/components/Footer.tsx:120-154`, `ALL_TOOLS` in `frontend/src/components/OtherTools.tsx:25-39`, and `TOOLS` in `frontend/src/app/page.tsx:360-452`, with the same tool labeled differently across surfaces. The rebuild uses one canonical catalog (id, href, short label, full label, localized labels per locale, description, icon) consumed by the navbar, footer, homepage grid, and Related Tools section (DEC-154), with exported data contracts and shape tests preserved (DEC-143; `audit-outputs/ui-home-shell-audit.md` §11 item 9).

### 8.5 Related tools

The existing Related Tools pattern is retained after the primary tool experience and supporting content on each tool page (DEC-154). Only available launch tools are linked; the current tool is excluded; content, ordering, labels, and slugs come from the canonical catalog; and the section remains visually subordinate to processing and download actions (DEC-154).

## 9. Localization: EN, ES, and ID

1. English is the canonical language for design documents; the public product is localized in EN, ES, and ID (DEC-184, DEC-115, DEC-118).
2. The launch gate requires complete and consistent UI copy, instructions, errors, processing disclosures, results, metadata, navigation, legal/support surfaces, and core accessibility text in all three locales (DEC-118).
3. Translation must be intentional localization, not literal machine translation; content must suit each market's search intent and cultural expectations (DEC-048, DEC-052, DEC-121, DEC-124).
4. The language selector remains in the navbar on desktop and mobile, shows the active locale, is keyboard and screen-reader accessible, and preserves the equivalent page when a localized counterpart exists (DEC-149).
5. Locale switching, hreflang, canonicals, sitemaps, and internal links must be generated consistently per locale (DEC-023, DEC-115).
6. Copy must be resilient to length growth in Spanish and Indonesian; legacy Indonesian context paragraphs are long and the EN/ES equivalents must not break layouts (Section 16; `audit-outputs/ui-docs-code-reconciliation.md` §7.2).
7. Copy tone is one neutral, direct register. The legacy split page uses the informal "kamu" while other tools use a neutral register (`audit-outputs/ui-five-tools-audit.md` §6 item 14); the rebuild uses one register per locale, consistent across tools.
8. No legacy Indonesia-first positioning, "no English tagline" rules, or Indonesian-only copy claims carry forward (DEC-002, DEC-003, DEC-021; `audit-outputs/ui-docs-code-reconciliation.md` §4.5).
9. The legacy `<html lang="id">` hardcoding (`frontend/src/app/layout.tsx:49`) is replaced with locale-aware document language and metadata (DEC-023, DEC-047).

## 10. Existing visual baseline (DEC-143)

The rebuilt website must look and feel like the existing Papyr website. The established visual identity, page composition, tool-directory presentation, component character, and familiar interaction patterns are the primary UI/UX reference, not inspiration for a visibly different redesign (DEC-143). This section records the baseline as audited and the corrections the rebuild must make. Everything here is retained unless a change is necessary for an approved requirement.

### 10.1 Design tokens

From `frontend/src/app/globals.css:3-10` and `audit-outputs/ui-home-shell-audit.md` §3.1:

| Token | Value | Role |
| --- | --- | --- |
| `--color-navy` | `#1e3a5f` | Brand and heading color, hero and logo lockup, primary homepage CTA background |
| `--color-accent` | `#2563eb` | Interactive accent, links, active states, icon tiles, tool-page primary actions |
| `--color-bg` | `#f9fafb` | Page and shell background |
| `--color-foreground` | `#171717` | Body text |
| `--font-sans` | `'DM Sans', system-ui, sans-serif` | Body font |

Supporting language uses Tailwind slate scale (borders slate-200, secondary text slate-500, tertiary slate-400/300, fills slate-100), emerald-500 for success checks, and rose-50/rose-200/rose-500 for error states (`audit-outputs/ui-five-tools-audit.md` §2; `audit-outputs/ui-docs-code-reconciliation.md` §4.2).

Token corrections (from `audit-outputs/ui-home-shell-audit.md` D4, D5):

1. `--color-background: #ffffff` is unused and `--font-dm-sans` (from next/font) is never consumed by any utility; wire the font variable correctly or drop the dead token.
2. Plain CSS `body` rules reference `@theme inline` tokens via `var()` (`globals.css:12-16`); with Tailwind v4 `@theme inline`, emission of these custom properties to `:root` is version-dependent (audit uncertainty U1). The rebuild must use utilities or a non-inline `@theme` so the body background, text color, and font never silently fall back.

### 10.2 Typography

DM Sans via next/font/google, `display: swap`, latin subset (`frontend/src/app/layout.tsx:9-14`). Type scale as audited (`audit-outputs/ui-home-shell-audit.md` §3.2):

- Hero H1: `clamp(40px,6vw,72px)`, semibold, `tracking-[-2px]`, navy (`frontend/src/app/page.tsx:497`)
- Section H2: 32px and 28px navy (`frontend/src/app/page.tsx:540,574`)
- Tool-page H1: `text-3xl md:text-4xl font-bold tracking-tight text-navy` (`frontend/src/app/compress/page.tsx:100`)
- Card titles 15px semibold; descriptions 13.5px; nav labels 12px (md) / 14px (lg); eyebrow 12px uppercase tracking-widest accent; footer links 13-14px

### 10.3 Spacing, radius, shadows, motion

From `audit-outputs/ui-home-shell-audit.md` §3.3 and §3.4:

- Content column: `max-w-[1200px] px-6` for homepage sections and footer; tool pages use `max-w-xl px-4 py-8 sm:py-12`.
- Section rhythm: hero `pt-24 pb-20`; tools grid `py-20`; privacy `py-[72px]`; footer tools `py-12`; footer bottom bar `py-10`.
- Radii: cards and icon tiles 10px; tool-page header tile 16px (`rounded-2xl`); nav CTA 8px; pills fully rounded.
- Shadows: resting `0_1px_3px_rgba(0,0,0,0.04)`; card hover `0_4px_20px_rgba(37,99,235,0.1)`; done card `0_4px_20px_rgba(37,99,235,0.06)`; download CTA `0_2px_12px_rgba(37,99,235,0.25)`.
- Motion: `animate-fade-up` 0.3s for state-card transitions; `animate-shimmer` 1.4s for indeterminate processing; chevron rotations; hover lift via `transition-all`. Reduced-motion behavior is required (Section 16).

Motion corrections: the rotate page's inline 1.2s shimmer variant bypasses the token (`audit-outputs/ui-docs-code-reconciliation.md` §3.3) and its loading spinner variant is outside the documented taxonomy; the rebuild standardizes on the tokenized shimmer and the stage-based processing model (DEC-033).

### 10.4 Component character

The baseline component language from the five-tools audit (`audit-outputs/ui-five-tools-audit.md` §2) is retained:

1. **Tool-page shell:** `mx-auto w-full max-w-xl px-4 py-8 sm:py-12`; 64px `rounded-2xl` accent icon tile; navy H1; one-line slate-500 subtitle; a short context paragraph.
2. **Feature badges:** three-card grid, `rounded-2xl bg-white p-5 border border-slate-100 shadow-sm`, icon plus small navy title.
3. **Dropzone:** `rounded-2xl border-2 border-dashed`, slate-300 border with `hover:border-accent/50`, drag-over to `border-accent bg-accent/5`; 56px accent icon tile; navy CTA line; slate-400 constraint line; hidden file input; `role="button"`, `tabIndex={0}`, Enter/Space activation.
4. **Processing card:** `rounded-2xl border border-slate-200 bg-white p-6`, status line, 6px shimmer bar.
5. **Done card:** accent border and shadow, 40px emerald-500 check circle, title, metadata line, full-width accent download button, outline secondary reset button.
6. **Error card:** `rounded-2xl border-rose-200 bg-rose-50/50`, rose alert icon, heading, message, full-width accent "Coba Lagi".
7. **PrivacyNotice:** always visible, `rounded-xl bg-slate-50 p-4 text-sm text-slate-500 border border-slate-100`, shield icon, per-model copy.
8. **Accordion FAQ:** grid-rows 0fr to 1fr with opacity transition, `duration-200` (`frontend/src/app/faq/page.tsx:104-120`).
9. **Sortable items:** order badge, drag handle, per-item remove control with `aria-label`.
10. **Inline SVG icons only**, no icon library, Lucide-style stroke, `currentColor` (`audit-outputs/ui-docs-code-reconciliation.md` §4.1).

### 10.5 Baseline strengths to preserve

From `audit-outputs/ui-home-shell-audit.md` §11:

1. Frosted sticky navbar (`bg-bg/92 backdrop-blur-md`, 52px, border-b).
2. Dropdown interaction model: hover or click open, outside-click close, route-change close, exact-route active state, CTA always visible at both breakpoints.
3. Native `<details>`/`<summary>` mobile accordion.
4. Sticky-footer flex shell (`html h-full`, `body min-h-full flex-col`, `main flex-1`).
5. Cohesive navy/accent/off-white token system applied app-wide.
6. Fluid hero type with the 1200px content column.
7. Motion discipline: 0.3s fade-up, shimmer processing, chevron rotations.
8. Credibility system: pill, trust badges, privacy section, FAQ, footer all state consistent guarantees.
9. Exported data contracts locked by tests.
10. SEO baseline: metadataBase, OG images, sitemap.
11. Consistent tool-page shell across tools.

### 10.6 Documented defects to correct

From `audit-outputs/ui-home-shell-audit.md` §12 (D1-D13), all corrected without changing the visual character:

1. **D1 Dead footer links:** "Syarat" and "Kontak" point to `#` (`frontend/src/components/Footer.tsx:161-162`); replaced by real localized routes (DEC-045, DEC-046) and covered by tests.
2. **D2 Four divergent catalog copies:** replaced by one canonical catalog (Section 8.4).
3. **D3 Width inconsistency:** navbar container `max-w-[1440px]` (`frontend/src/components/Navbar.tsx:146`) versus 1200px elsewhere; the audits could not determine intent (uncertainty U2). The rebuild documents and applies one width decision after owner confirmation (Section 21).
4. **D4 Dead tokens:** `--color-background` and `--font-dm-sans` resolved (Section 10.1).
5. **D5 `var()` reliance on `@theme inline` tokens:** resolved (Section 10.1).
6. **D6 Hardcoded `© 2026`:** year computed from runtime date.
7. **D7 Redundant homepage wrapper:** removed; the flex shell handles min-height and background.
8. **D8 Accessibility gaps:** skip-to-content link and `main` id, `aria-expanded` on hamburger and category buttons, focus-visible styling, Escape-to-close on dropdowns and the language switcher (Section 16).
9. **D9 Language switcher semantics:** the inert English row becomes a proper disabled/`aria-disabled` treatment where applicable; flag emoji replaced by accessible text labels (audit notes Windows letter-pair rendering).
10. **D10 No active-section indication:** the category button shows an active state when a tool inside it is active.
11. **D11 Logo lockup mismatch:** one lockup component with a size prop for navbar and footer.
12. **D12 Instant panel appearance:** dropdowns and the mobile menu get a short fade consistent with the motion language, or instant behavior is kept as a deliberate, documented choice (owner confirmation; Section 21).
13. **D13 Test blind spots:** interaction and render tests added for dropdown open/close, mobile menu, active states, and the language switcher (Section 20).

From `audit-outputs/ui-five-tools-audit.md` §6 (tool-level corrections), integrated into the per-tool flows in Section 12 and the shared states in Section 13.

From `audit-outputs/ui-docs-code-reconciliation.md` §7.3, these historical claims do not carry forward: Indonesia-first positioning and Indonesian-only copy rules, OpenClaw-related content, "6 tools" counts, the universal 1200px rule (replaced by the 1440px navbar plus 1200px content convention, pending D3), and the "semantic colors to be defined" note.

### 10.7 Approved visual changes only

Changes to the baseline are limited to consistency, responsive behavior, accessibility, localization resilience, truthful states, corrected interactions, performance, and removal of legacy defects (DEC-028, DEC-143). Material visual departures require explicit owner approval through comparison with the existing interface (DEC-143).

## 11. Shell and homepage

### 11.1 Root shell

From `frontend/src/app/layout.tsx:49-55` and `audit-outputs/ui-home-shell-audit.md` §4:

1. `html lang` is locale-aware, not hardcoded to `id`.
2. Sticky 52px frosted navbar; `main` with `flex-1`; footer; sticky-footer flex shell retained.
3. A skip-to-content link is added (D8).
4. Metadata uses locale-aware defaults with `metadataBase https://mypapyr.com`, per-locale title/description, and OG/Twitter images (DEC-021, DEC-023). The legacy Indonesian-only default title (`frontend/src/app/layout.tsx:18`) is replaced by localized international copy (DEC-003).
5. The shell stays visible during processing; only the tool workspace changes state (DEC-145).

### 11.2 Navbar

Baseline from `audit-outputs/ui-home-shell-audit.md` §5, with DEC-147, DEC-149, DEC-152, DEC-155 applied:

1. Frosted sticky bar with the category dropdown model for desktop and the native accordion for mobile.
2. Only the five launch tools appear as destinations; empty categories are omitted or consolidated (DEC-152).
3. The EN/ES/ID language selector lives in the navbar on desktop and mobile (DEC-149).
4. The CTA remains visible at both breakpoints; its target and copy are finalized in the copy pass (duplicate CTA targeting is an open item, Section 21 U3).
5. D8 accessibility corrections: `aria-expanded`, Escape handling, focus-visible, active-category indication (D10), and interaction tests (D13).

### 11.3 Footer

Baseline from `audit-outputs/ui-home-shell-audit.md` §6, with DEC-045, DEC-046, DEC-116, DEC-123 applied:

1. Tools directory section fed by the canonical catalog (D2).
2. Bottom bar links to real routes: Privacy, Terms, Cookies/Advertising, Contact/Support, Status, Roadmap (D1; DEC-045, DEC-046, DEC-116, DEC-123). No `#` placeholders.
3. Dynamic copyright year (D6) and one logo lockup component (D11).
4. The language switcher moves to the navbar per DEC-149; if the footer retains a secondary switcher it must follow the same semantics and Escape handling (D8, D9).

### 11.4 Homepage

Baseline from `frontend/src/app/page.tsx:486-593` and `audit-outputs/ui-home-shell-audit.md` §7, with DEC-043, DEC-148, DEC-150, DEC-151 applied. The homepage preserves the existing content depth adapted to five tools:

1. **Hero:** pill badge with the free/no-account/auto-delete guarantees, fluid clamp H1 with an accent span, short sub copy, primary CTA, trust badges row. Copy is rewritten for the international positioning while retaining the structure (DEC-043, DEC-139, DEC-150).
2. **Tool directory:** equal-weight five-card grid, one card per launch tool, same visual hierarchy and interaction pattern for all five, no featured treatment (DEC-148). Cards keep the existing card classes and hover behavior (DEC-143). The grid presents only the five launch tools; deferred tools do not appear (DEC-009, DEC-152).
3. **Privacy section:** three pillars retained with accurate, decision-consistent copy (DEC-150). Claims must be re-scoped against DEC-025 and DEC-168; legacy copy that says "no tracking" or "no personal data collected at all" conflicts with the accepted analytics and advertising model and must be corrected (`audit-outputs/ui-docs-code-reconciliation.md` §8.8, §6).
4. **How-it-works and FAQ sections:** retained at the existing depth, adapted to EN/ES/ID (DEC-150, DEC-157).
5. The homepage must not carry stale claims or references to the 13-tool legacy catalog (DEC-150).
6. Homepage advertising, if placed, follows the non-intrusive rules in Section 14 and must not disrupt the directory's scanability (DEC-148, DEC-018).

## 12. Five detailed tool flows

### 12.0 Shared flow anatomy

Each tool page follows the existing sequence (DEC-144): tool header, file dropzone, configuration when needed, processing state, result and download, privacy information, and related tools. Tool-specific configuration appears only after a valid file selection when relevant (DEC-144). Processing and results stay on one page; successful processing does not redirect to a separate result URL (DEC-153).

Shared elements per `audit-outputs/ui-five-tools-audit.md` §2, with corrections:

1. Tool header with internationalized use cases (legacy examples are Indonesia-specific, for example WhatsApp, KTP, lamaran kerja, and must be rewritten for the target regions while staying concrete).
2. Dropzone per the baseline contract, with a consistent constraint line and validation message template across tools (audit §6 items 9-10).
3. Processing card with a truthful stage line and shimmer bar (DEC-033).
4. Done card with auto-download attempt, persistent manual Download button, honest result summary, and "process another file" action (DEC-029, DEC-068, DEC-146, DEC-156).
5. Error card with recovery actions appropriate to the failure (DEC-158).
6. PrivacyNotice always visible; the detailed local-versus-server and retention disclosure lives on the Privacy page with an accessible path from the uploader (DEC-168). Workflow states such as uploading, queued, and server processing are still labeled truthfully when they occur; this is operational feedback, not a consent prompt (DEC-168).
7. Related Tools section following the single visibility rule below (DEC-154).
8. Empty-state copy present on every tool that requires a selection before processing (audit §6 item 11).
9. Accessible status and progress semantics per Section 16.
10. Heading hierarchy without h1-to-h3 jumps (audit §6 item 8).

**Related Tools visibility rule (one rule for all five tools):** Related Tools and supporting content remain visible below the active workspace in all states, matching the legacy Compress page behavior (`frontend/src/app/compress/page.tsx:135`), so that navigation is available exactly when users finish a task (DEC-145, DEC-154; `audit-outputs/ui-five-tools-audit.md` §6 item 1). The section stays subordinate: it must not distract from status, cancellation, errors, or completion, and it appears below the fold relative to the active workspace.

### 12.1 Compress PDF

**Purpose.** Reduce PDF file size while preserving crisp on-screen quality. One automatic, high-end compression mode optimized for premium screen viewing (DEC-014).

**Processing model.** Server-side by default (DEC-014, DEC-015). Compress uses the official unmodified open-source Ghostscript executable as a separate server-side subprocess, following the existing Papyr integration boundary; Papyr does not modify, link into, or embed Ghostscript source into proprietary application code (DEC-195). Ghostscript is obtained from an authoritative distribution, version-pinned, hardened, and invoked with appropriate safety flags including `-dSAFER`; applicable copyright and AGPL notices are preserved and the corresponding unmodified Ghostscript source is made available as required (DEC-195). Papyr does not claim that subprocess use eliminates every licensing obligation: the exact production distribution and integration model requires a focused license review before public launch, and if that review requires disclosure the owner does not accept, Compress moves to a permissive engine path or a commercial Ghostscript license before launch (DEC-195). If a browser processing path is introduced later it must follow DEC-030 and DEC-065. The legacy hardcoded `quality=ebook` query parameter (`frontend/src/components/PDFUploader.tsx:303`) is removed; the MVP exposes no quality controls at all (DEC-014).

**Flow.**

1. Tool header: "Compress PDF", subtitle, context paragraph with an international use case.
2. Dropzone with PDF constraint and size limit copy. The legacy auto-upload behavior is retained: selecting a valid file starts the job immediately, because Compress requires no configuration and auto-start minimizes time-to-first-action (DEC-008). This difference from the other tools is deliberate and documented; the dropzone states the file will be processed automatically, and the constraint line and validation template are unified with the other tools (audit §6 items 9-10).
3. On selection, the file is validated, and the job transitions through uploading, queued, processing, and ready stages. Upload percent is shown only for measured byte progress; processing uses an honest stage label with an indeterminate shimmer (DEC-033).
4. Result card reports the actual input size, output size, and real change honestly, including zero savings or a larger output (DEC-080). The legacy "−0%" pill from `formatPercent` flooring (`frontend/src/lib/format.ts:15-21`; audit §6 item 15) is replaced: when the output is not smaller, the UI states that clearly rather than showing a fabricated percentage.
5. Auto-download attempt plus persistent manual Download button; a blocked auto-download leaves the job in Ready state (DEC-029, DEC-068).
6. "Process another file" resets to the uploader state without a full reload (DEC-156).

**Encrypted input.** Detect password-protected PDFs and request a password only when needed (DEC-036, DEC-064). Wrong-password errors are distinct from corrupt or unsupported files (DEC-036).

**Active content.** If JavaScript, launch actions, embedded attachments, or other active features are detected, they are sanitized from the output (DEC-090) and the general categories removed are disclosed in a localized, concise message (DEC-091).

**Output naming.** Source-derived name with a safe, localized suffix (DEC-042); the legacy `compressed_<name>` pattern is the baseline and is formalized under the shared naming policy.

**Baseline corrections carried in** (`audit-outputs/ui-five-tools-audit.md` §6): auto-retry timer cleared on unmount/reset with a visible "retrying" label; validation message template unified; accessible progress semantics added; heading hierarchy fixed; OtherTools visibility unified.

### 12.2 Merge PDF

**Purpose.** Combine multiple PDFs into one file in the user's chosen order. Controls stay at the file level; no cross-document page editor in the MVP (DEC-040).

**Processing model.** Browser-first (DEC-011). Corrupt, encrypted-unsupported, or unsafe jobs automatically route to the server with visible transition messaging (DEC-030, DEC-065). When browser inspection detects PDF JavaScript, embedded attachments, launch actions, or other active content in any input, the job routes to the temporary server path for sanitization; Papyr does not build a separate browser sanitization engine (DEC-192). If the maintained malware-scanner or sanitization path is unavailable, affected jobs fail closed rather than bypassing the control (DEC-192). Ordinary safe files may still use the browser path within DEC-015 limits, and browser limits apply per DEC-015.

**Flow.**

1. Tool header.
2. Dropzone accepting multiple PDFs; after the first file the dropzone copy switches to "add more files" (legacy pattern at `frontend/src/app/merge/page.tsx:593-597`).
3. Sortable file list: drag-and-drop reorder plus keyboard-accessible alternatives (DEC-040). Drag handles receive `aria-label` and dnd-kit `announcements` provide keyboard reorder feedback (audit §6 item 7). Order badges, per-item remove with `aria-label`, file name and size, and the "{n} files · size" summary are retained (DEC-040).
4. Per-file validation with one unified message template that identifies the affected file (audit §6 items 9-10).
5. Password handling: each locked input is identified and its password requested and validated independently (DEC-064, DEC-074). Credentials are memory-only, never logged, and never reused across files unless the user enters them (DEC-036, DEC-074).
6. CTA "Merge PDF" enabled only with two or more valid files, with a helper message (legacy disabled pattern retained).
7. All-or-nothing semantics: the job is blocked or fails if any selected source cannot be opened, authenticated, validated, or processed; no partial output is presented as successful (DEC-076). The UI identifies the affected source safely and lets the user correct credentials, replace the file, or remove it; other valid sources stay in memory (DEC-076).
8. Processing card with a truthful browser or server stage line (DEC-033, DEC-030).
9. Done card with auto-download attempt, manual Download button, and honest summary of merged pages and size (DEC-029, DEC-146).

**Document features.** Merge preserves bookmarks, form fields, annotations, links, metadata, and page geometry to the greatest extent the engine can do safely (DEC-079). Unsupported or transformed features are disclosed truthfully; the product does not promise lossless preservation universally (DEC-079). Active content is sanitized from the output (DEC-090) with category-level disclosure (DEC-091); active-content-bearing inputs are routed to the server sanitization path rather than relying on browser page copying, and no malware-free guarantee may be claimed (DEC-192).

**Output naming.** Source-derived with a safe, localized suffix (DEC-042). The legacy hardcoded English `merged.pdf` (`frontend/src/lib/pdfUtils.ts:240-254`) is replaced by the shared naming policy.

### 12.3 Split PDF

**Purpose.** Extract selected pages as separate PDFs. Two modes in the MVP (DEC-038): custom page ranges and one PDF per page.

**Processing model.** Browser-first (DEC-011) with automatic server fallback for unsafe jobs (DEC-030, DEC-065). When browser inspection detects PDF JavaScript, embedded attachments, launch actions, or other active content in the input, the job routes to the temporary server path for sanitization; Papyr does not build a separate browser sanitization engine (DEC-192). If the maintained malware-scanner or sanitization path is unavailable, affected jobs fail closed (DEC-192). Ordinary safe files may still use the browser path within DEC-015 limits.

**Flow.**

1. Tool header.
2. Dropzone for a single PDF.
3. Preparing card ("reading document") while page count is determined (legacy two-step flow retained: `frontend/src/app/split/page.tsx:445-452`).
4. Ready state: file info row with remove control; mode selection (custom ranges or per-page); for custom ranges, the PageRangeInput with label, placeholder example, inline parse errors, live selected-pages preview, and quick-select chips (legacy pattern at `frontend/src/components/PageRangeInput.tsx:106-163`, corrected for order and overlap below); for per-page mode, a plain confirmation of output count.
5. **Range semantics change (DEC-077, DEC-078):** the legacy parser sorts and deduplicates the entered ranges (`PageRangeInput.tsx:19-89`); the rebuild preserves user-entered order and permits overlapping ranges as independent outputs. A request such as `8-10,1-2` produces the `8-10` result first and the `1-2` result second (DEC-078). The preview must make duplicated page membership and the effective output sequence visible before processing (DEC-077, DEC-078). Repeated identical ranges require unambiguous labels in output names and the manifest (DEC-077). Validation still covers charset, start-after-end, out-of-bounds, and malformed tokens with actionable localized errors (DEC-038).
6. CTA enabled only when the selection is valid; helper text when empty (legacy pattern).
7. Done card: auto-download of a ZIP when multiple outputs are produced, plus each generated file available for individual download (DEC-037). Single-output jobs download the file directly. The result manifest, ZIP ordering, and individual-download listing follow the user-entered order (DEC-078).
8. "Process another file" reset (DEC-156).

**Output naming.** Deterministic, safe, ordered names derived from the source plus the range or page identifiers, following DEC-042. The legacy `split_<range>.pdf` pattern (`frontend/src/app/split/page.tsx:320-328`) is the baseline and is extended to per-page mode and the ZIP manifest.

**Encrypted input.** Password requested only when required (DEC-036, DEC-064).

**Active content.** Sanitized from outputs with category-level disclosure (DEC-090, DEC-091); active-content-bearing inputs route to the server sanitization path, and no malware-free guarantee may be claimed (DEC-192).

### 12.4 JPG to PDF

**Purpose.** Convert JPG images into a single PDF with automatic, safe fitting (DEC-041).

**Processing model.** Hybrid, browser-first (DEC-011): small jobs process locally, larger jobs route to the server automatically. The legacy hardcoded 3MB threshold (`frontend/src/app/image-to-pdf/page.tsx:43`) is replaced by the limit policy established under DEC-015 and DEC-034; the routing behavior is disclosed on the Privacy page and labeled truthfully in workflow states (DEC-168).

**Flow.**

1. Tool header: "JPG to PDF" (the user-facing name is retained even though PNG and WebP are also accepted; DEC-187), subtitle, context paragraph.
2. Dropzone accepting JPG/JPEG, PNG, and WebP image inputs (DEC-187; legacy baseline `frontend/src/app/image-to-pdf/page.tsx:40-72`). Inputs are validated by actual file bytes, dimensions, and resource limits, not by extension alone (DEC-093).
3. Sortable thumbnail grid with order badges, always-visible remove and drag controls (the legacy hover-only `opacity-0 group-hover` controls are fixed: audit §6 item 6), and keyboard reordering (DEC-041; Section 16).
4. CTA enabled with at least one valid image, using the same disabled-until-valid affordance as the other tools (audit §6 item 12).
5. **Automatic fitting policy (no settings):** each image is fitted to an appropriate standard page with safe margins, preserving aspect ratio, no cropping, and EXIF orientation (DEC-041). Page size and portrait/landscape orientation are selected per image (DEC-082). Letter is selected only when the trusted coarse edge country code is the United States or Canada; every other country, missing code, or invalid code selects A4, and the active content locale never independently selects paper size (DEC-191). The selected standard is visible before processing even though no manual control exists (DEC-083, DEC-085, DEC-191).
6. **Metadata disclosure:** the interface and Privacy documentation disclose that source metadata, including EXIF GPS, timestamps, and device information, may remain in the result (DEC-084). This is an accepted privacy risk; the product makes no broad claim that generated files remove sensitive metadata (DEC-084).
7. Processing card with truthful browser or server stage line.
8. Done card: auto-download attempt, manual Download button, and a result summary that shows image count and size for both client and server paths (the legacy server path drops the returned `pdf_size`: audit §6 item 3).
9. "Create another PDF" reset (DEC-156).

**Output naming.** Source-derived, localized (DEC-042). The legacy `images.pdf` default is replaced by the shared naming policy.

**Server results.** Downloaded through short-lived signed URLs without proxying through the VPS (DEC-170); the download uses an anchor or equivalent that cannot be silently killed by popup blockers (the legacy `window.open` for the server path is fixed: audit §6 item 3).

### 12.5 PDF to JPG

**Purpose.** Convert PDF pages to high-quality JPG images with one automatic output profile (DEC-039).

**Processing model.** Browser-capable with server fallback (DEC-011, DEC-015, DEC-030). Rendering is sequential with a 16-megapixel per-page ceiling for browser processing (DEC-015). Server processing treats the source as untrusted input for parser and infrastructure safety even though rasterization excludes active content from the output (DEC-092).

**Flow.**

1. Tool header.
2. Dropzone for a single PDF.
3. Preparing card ("reading document") while page count is determined (legacy two-step flow: `frontend/src/app/pdf-to-image/page.tsx:455-462`).
4. Ready state: file info row with remove control; PageRangeInput for page selection with duplicate-preserving, order-preserving semantics (DEC-186), so repeated or overlapping page selections produce independent outputs in the requested order, with syntax and validation per DEC-038; CTA enabled only for a valid selection.
5. **Automatic output profile (no settings):** one high-quality profile with no DPI or JPEG-quality controls (DEC-039). Text and line art stay crisp for normal high-quality screen use within the 16-megapixel ceiling (DEC-015, DEC-039). If source pages are already low resolution, the UI does not imply that conversion creates missing detail (DEC-039).
6. **Transparency handling:** page transparency is composited onto white before JPEG encoding (DEC-081).
7. Processing card with a truthful stage line; when server processing occurs the stage says so (DEC-168, DEC-033).
8. Done card: for a single page, direct download; for multiple pages, ZIP auto-download plus individual downloads (DEC-037). ZIP ordering, individual-download listing, and manifest entries follow the user-entered page-selection order, with duplicates disambiguated (DEC-186, DEC-078). The legacy `file_type` distinction (PNG vs ZIP) is replaced by the ZIP-plus-individual model (DEC-037).
9. "Convert another file" reset (DEC-156).

**Encrypted input.** Password requested only when required (DEC-036, DEC-064).

**Output naming.** Source-derived with localized suffixes (DEC-042). Legacy `page.png` / `pages.zip` defaults are replaced by the shared naming policy. Repeated or overlapping page selections are disambiguated in output names, ZIP contents, individual downloads, and the manifest so every result is identifiable (DEC-186).

## 13. Shared states

This section defines the cross-tool state model and lifecycle behaviors (DEC-033, DEC-029, DEC-032, DEC-153).

### 13.1 State model

Every tool uses the same user-facing state set, with internal events mapped to it (DEC-033):

| State | Meaning | UI |
| --- | --- | --- |
| Idle | No valid input selected | Header, dropzone, badges (if applicable), privacy notice, related tools |
| Preparing | Reading and preparing the input (page counts, validity) before work starts | Preparing card with shimmer ("reading document") |
| Ready | Input valid, configuration expected or possible | File info row, configuration controls, primary CTA |
| Uploading | Bytes are being transferred for a server job | Determinate progress only from measured bytes (DEC-033) |
| Queued | Server job waiting for a worker | Queued card with honest wait language; estimate only when grounded in real queue state (DEC-033, DEC-035). The initial backend runs one active worker, so valid jobs may wait in the bounded fair queue and the wait language reflects that reality rather than promising immediate processing (DEC-189) |
| Processing | Work is executing (browser or server) | Stage label plus shimmer; percentage only when grounded in measured units such as pages processed or engine progress (DEC-033) |
| Finalizing | Result is being assembled and prepared for delivery (archive creation, result signing) | Stage label plus shimmer |
| Ready (done) | Result available for download | Result card with auto-download attempt, manual Download button, summary, expiry information where applicable, and process-another-file action (DEC-029, DEC-068, DEC-146, DEC-156) |
| Error | The job failed or was rejected | Inline error card with recovery actions (DEC-158) |

The canonical lifecycle stage vocabulary is preparing, uploading, queued, processing, finalizing, and ready (DEC-033). Idle, Ready (configuration), Ready (done), and Error are UI states that frame the lifecycle rather than stages of it: Ready (configuration) and Ready (done) both correspond to the lifecycle's ready stage and are distinguished by UI context. The Technical Architecture Specification (§13.2) uses the same canonical vocabulary for the server-job lifecycle (DEC-185).

Transitions are announced accessibly (Section 16). The processing stage must not replace the whole page or hide navigation (DEC-145).

### 13.2 Download behavior

1. Successful processing triggers an automatic download attempt (DEC-029). If the browser blocks or misses it, the job stays in Ready state with a visible manual Download button (DEC-068).
2. The manual button reuses the already generated result; it never re-uploads, reprocesses, or regenerates the file (DEC-068).
3. Multi-file results auto-download a ZIP and keep each file individually downloadable while the result is available (DEC-037).
4. Repeated downloads do not rerun processing (DEC-029).
5. Download names follow the safe, localized, source-derived naming policy (DEC-042).

### 13.3 Result availability and expiry

1. Local results are kept only for the active tab session; no IndexedDB, localStorage, or cross-session storage (DEC-032). Object URLs are revoked on unload, reset, or replacement (DEC-032).
2. Server results expire at the absolute one-hour deadline from upload receipt (DEC-013, DEC-070), even if the tab stays open (DEC-067). The UI shows the remaining availability window and warns before deletion (DEC-067).
3. A successful download does not trigger early deletion; the result remains available until its normal expiry (DEC-075).
4. An expired server result cannot be restored; the user runs a new job (DEC-067).
5. Refresh recovery for an active server job works within the same tab via minimal opaque task state in `sessionStorage`; closing the tab ends client-side recovery (DEC-072). Only opaque identifiers and minimal routing metadata are stored, never filenames, passwords, contents, previews, signed URLs, or analytics payloads (DEC-072).

### 13.4 Cancellation, reset, and tab lifecycle

1. Server jobs can be cancelled only while queued; once a worker has started, user cancellation is no longer offered (DEC-069). Race conditions between cancellation and worker pickup are handled with an explicit state transition; if processing already started, the UI reports that cancellation is no longer available (DEC-069).
2. Closing the tab does not cancel an accepted server job (DEC-071); it continues subject to queue, timeout, failure, and expiry rules.
3. "Process another file" clears the current tool state and returns to the uploader state without a full-page reload (DEC-156). Reset revokes local buffers and object URLs, clears nonessential task state, and does not delete a server result before its fixed expiry (DEC-156). Focus returns to an appropriate heading or uploader control (DEC-156).
4. Memory-pressure release of a local result is allowed, but the UI explains when repeat download is no longer available (DEC-032).

### 13.5 Honest progress

No fabricated percentages. Percentages appear only when grounded in measurable units such as bytes uploaded, pages processed, or explicit engine progress (DEC-033). Queue position or wait estimates are labeled as estimates and updated from real queue state (DEC-033); under the one-worker initial posture, bounded queuing is an expected state rather than an error (DEC-189). Long-running, stalled, retrying, cancelled, and failed states each have distinct messages and recovery actions (DEC-033).

## 14. Advertising placement

Monetization at launch is Adsterra banner and native advertising only (DEC-005, DEC-018). Placement rules:

1. **Formats:** non-intrusive banner and native placements only. Popunders, interstitials, social bars, in-page push, forced redirects, and anti-adblock messaging are excluded (DEC-018).
2. **Task flow protection:** ads never obstruct upload, configuration, processing, result, download, consent, error recovery, navigation, accessibility, or responsive layout (DEC-018, DEC-102).
3. **Tool pages:** advertising appears only after the primary tool interaction and result/download experience, within supporting content, never before the uploader (DEC-151).
4. **Result pages:** ads are spatially and visually separated from primary and fallback Download controls; no ad imitates a download button, result card, progress state, warning, or system action; mobile layouts preserve meaningful separation (DEC-131).
5. **Blog:** light banner/native placements that do not interrupt headings, obscure content, mimic editorial links, trigger layout shifts, or overwhelm mobile reading (DEC-129).
6. **Legal, support, and status pages:** the same light policy applies (accepted risk, DEC-130). Policy text, support controls, incident information, and status rendering must remain immediately readable and functional when advertising is blocked, unavailable, slow, or broken; status rendering and critical communication must not depend on Adsterra scripts (DEC-130).
7. **Layout stability and performance:** ad slots reserve stable dimensions to prevent layout shift; scripts load asynchronously or lazily; Core Web Vitals protections apply (DEC-018, DEC-129).
8. **Consent:** the approved behavior loads these non-intrusive ads without prior consent in all launch regions. The owner reaffirmed this accepted risk after review of the research findings (DEC-022, DEC-190); it is not evidence of GDPR, UK GDPR, Swiss FADP, ePrivacy, PECR, or US state compliance, and not proof of Adsterra policy conformance. Papyr must not state that the approach is compliant without qualified review (DEC-190). Before launch, Adsterra scripts, cookies, identifiers, recipients, and regional behavior must be reviewed against current terms and applicable law; if prior consent is required, Papyr must implement compliant controls, serve demonstrably non-tracking contextual ads, or suppress ads in affected regions (DEC-022, DEC-190). The product must not claim compliance without supporting evidence (DEC-022).
9. **UX priority:** any placement that materially harms trust, performance, or task completion is removed or reduced even at the cost of revenue (DEC-102). If Adsterra is not viable, Papyr operates without ads rather than degrading the product (DEC-135, DEC-136). Critical product functionality and legal, support, and status content remain available when ad scripts are blocked or disabled (DEC-190).

## 15. Content, legal, support, status, and blog surfaces

### 15.1 Tool pages as content

Each tool page carries concise, intent-aligned content: working tool first, then instructions, benefits, processing and privacy explanation, use cases, FAQ, and related tools (DEC-044). No competing comparison pages are created (DEC-128). Copy avoids unsupported superlatives and quantified quality claims (DEC-066, DEC-101).

### 15.2 Legal pages

Privacy Policy, Terms of Use, and Cookies/Advertising pages launch in EN, ES, and ID (DEC-045). They accurately describe local versus server processing, automatic server fallback, R2, providers, analytics boundaries, advertising behavior, user controls, and contact channels (DEC-045, DEC-168). The Privacy page is the home of the full processing and retention disclosure that the uploader intentionally does not carry (DEC-168). Legal copy discloses the accepted consent risk in practice without falsely claiming compliance (DEC-022, DEC-190, DEC-045). Documents expose effective dates and version history and require qualified legal review before launch (DEC-045). The pages carry light advertising only under the rules in Section 14 (DEC-130).

### 15.3 Support

Launch support is a public support email plus a simple categorized contact form, no accounts and no live chat (DEC-046), routed to one inbox managed by the project owner (DEC-050). The form minimizes personal-data collection, includes anti-spam and abuse protection, and never requests document uploads, contents, or passwords (DEC-046). Categories cover processing failure, advertising concern, privacy/data request, accessibility, security, and general feedback (DEC-046). Automated confirmations and form copy match the user's locale; submissions may share one operational queue (DEC-046). Contact submissions follow documented retention rules with redaction-safe error handling, so error states never resurface submitted content and retained submissions are deleted per policy (DEC-046). Legally required operator or contact information remains provided where applicable; brand-only presentation never conceals mandatory disclosures (DEC-110). The site avoids promising response times that cannot be sustained (DEC-050). Support analytics use aggregate categories and resolution timing without copying private message contents into general product analytics (DEC-050).

Result-local problem reporting is separate from general support: a short categorized report from the result experience that never uploads or attaches the document (DEC-117), with an optional reply email (DEC-120). Reports may include tool, processing path, sanitized error category, browser context, and user description, but never filenames, contents, passwords, signed URLs, or object keys (DEC-117). The optional email is used only for the submitted matter, never auto-added to a newsletter (DEC-120).

### 15.4 Status

A simple public status page shows material service availability and incidents in plain EN/ES/ID language without sensitive infrastructure details (DEC-116). It is hosted on Vercel so it stays useful during a backend VPS outage (DEC-119), and is updated automatically from approved health signals rather than owner-authored incident text (DEC-161). Status wording distinguishes observable service availability from guarantees about every engine or request (DEC-161). Per-tool availability may be exposed generally without infrastructure details (DEC-167). The page does not claim complete infrastructure independence (DEC-119).

### 15.5 Roadmap

A concise, informational roadmap distinguishes launched, planned, and exploratory capabilities, excludes internal security and infrastructure details, and carries the free-forever core commitment with accurate boundaries (DEC-123, DEC-125, DEC-138). It is read-only: no voting, comments, or feature requests (DEC-125). It is not shown in primary navigation as a dead or misleading destination (DEC-152).

### 15.6 Blog

The blog is a separate content surface from tool pages (DEC-044). Launch inventory is five topics, each intentionally localized into EN, ES, and ID (DEC-052, DEC-121). Articles visibly display original publication and latest material update dates, truthfully and locale-formatted (DEC-113). Content is version-controlled MDX in the repository (DEC-049); the automated LLM workflow calls the owner's OpenAI-compatible gateway at `https://router.budgezen.com/v1` with exact JSON model identifier `mypapyr` rather than the public `gpt5.6-sol` name and `Authorization: Bearer <API_KEY>` authentication (DEC-193, DEC-196). The gateway is accessed only from server-side or protected automation environments; authentication credentials never enter client code, repository content, logs, generated articles, or analytics (DEC-193, DEC-196). No internal spending guard is added at launch, but reliability controls remain mandatory and separate from spending: a bounded request timeout, finite retry count with backoff, idempotency where supported, one bounded publication workflow, repeated-failure pause, and a kill switch (DEC-196, DEC-048, DEC-053). The workflow uses blocking quality gates that fail closed, including factual support, duplication and cannibalization, search intent, originality, language quality, metadata, internal links, unsafe claims, policy violations, and malformed MDX (DEC-048). No fabricated expertise, authors, test results, citations, product capabilities, or claims (DEC-048). Publication is at most one coordinated topic per day after launch, EN+ES+ID together, with kill-switch and pause thresholds (DEC-053, DEC-124). The blog carries light advertising under Section 14 (DEC-129). The daily cadence may pause for stability and corrective work after launch (DEC-141). No newsletter at launch (DEC-109).

## 16. Responsive and accessibility (WCAG 2.2 AA)

### 16.1 Responsive behavior

1. Mobile-first layout with the existing Tailwind breakpoints (`sm`, `md`, `lg`) and the baseline fluid hero type (Section 10.3).
2. Navbar: desktop category dropdowns, mobile compact CTA plus the native accordion panel (DEC-155).
3. Tool pages: `max-w-xl` shell with full-width actions; feature grids collapse from 3 columns to 1; thumbnail grids from 3 to 2 columns; sortable lists stack full-width (audit evidence: `frontend/src/app/image-to-pdf/page.tsx:710`).
4. Footer and homepage sections wrap and stack within the 1200px content column.
5. No horizontal overflow; containers keep `px-6`/`px-4` gutters and the nav center section keeps `min-w-0` (audit evidence: `frontend/src/components/Navbar.tsx:163`).
6. Localized copy length must not break layouts (Section 9); Spanish and Indonesian text is verified at all breakpoints.

### 16.2 WCAG 2.2 Level AA acceptance coverage

WCAG 2.2 Level AA is the acceptance target for product pages, all five tools, blog, legal pages, and contact/support interfaces (DEC-062). Acceptance coverage includes:

1. **Keyboard operation:** all interactive controls operable by keyboard, including dropzones (Enter/Space), sortable reordering, dropdowns, accordions, the language switcher, range inputs, and reset actions. Drag-and-drop always has a non-drag alternative (DEC-040, DEC-062).
2. **Visible focus:** consistent `focus-visible` styling on every control. The legacy app has only one custom focus ring (in the sign overlay); the rebuild adds it app-wide (`audit-outputs/ui-docs-code-reconciliation.md` §3.4).
3. **Contrast:** text and interactive elements meet AA contrast, including slate-400/300 tertiary text and accent-tinted states. Contrast values from the legacy docs are re-verified with a contrast tool during implementation (`audit-outputs/ui-docs-code-reconciliation.md` §8.2).
4. **Semantic structure:** correct heading hierarchy (no h1-to-h3 jumps, audit §6 item 8), landmark regions, a `main` landmark, and a skip-to-content link (D8).
5. **Accessible names and errors:** labels on all inputs, `aria-label` on icon-only controls (drag handles, remove buttons, hamburger), and error text wired with `aria-invalid` and `aria-describedby` where appropriate (`audit-outputs/ui-five-tools-audit.md` §6 item 7).
6. **Status and progress announcements:** `role="status"` or `aria-live="polite"` on processing and ready transitions, `role="alert"` on error cards, and `role="progressbar"` with `aria-valuenow` on determinate upload progress (audit §6 item 7). Screen-reader announcements for dnd-kit reordering via the `announcements` API (audit §6 item 7, §8.5).
7. **Target sizing and spacing:** WCAG 2.2 target-size minimums for controls, verified at all breakpoints (DEC-062).
8. **Zoom and reflow:** layouts function at 200% zoom and 320px width without loss of content or functionality (DEC-062, DEC-031).
9. **Reduced motion:** the shimmer and fade-up animations respect `prefers-reduced-motion` (DEC-062).
10. **Localized content resilience:** announcements, labels, and errors are localized; message length growth does not break layouts (DEC-062, Section 9).

### 16.3 Browser support and testing

Officially supported browsers are the latest two major versions of Chrome, Edge, Firefox, and Safari on desktop, current Safari on iOS/iPadOS, and Chrome on Android (DEC-031). Progressive enhancement and ordinary file-input/download fallbacks are required where Chromium-specific file APIs are unavailable (DEC-031). Unsupported browsers receive a clear compatibility message or a server-processing path rather than silent failure (DEC-031).

Automated accessibility checks are necessary but insufficient; representative manual keyboard and assistive-technology testing is required (DEC-062). Known exceptions are documented with impact and remediation rather than silently treated as compliant, and public wording must not claim certification or universal conformance unless independently substantiated (DEC-062).

## 17. Analytics and privacy UX boundaries

1. Analytics collect detailed product events, funnels, attribution, performance, and sanitized error analytics, but never session replay on document workflows, fingerprinting data, or document-sensitive information (DEC-025).
2. Allowed: acquisition source, page and locale, tool selection, processing mode, coarse input bands, funnel stages, timings, sanitized failure categories, download completion, Web Vitals, and advertising performance where permitted (DEC-025).
3. Prohibited from analytics, monitoring, logs, and error reporting: file contents, previews, rendered document text, file names, object keys, signed URLs, passwords, full error payloads containing user data, and stable device fingerprints (DEC-025, DEC-042, DEC-117).
4. Event schemas require privacy review, data-retention policy, regional activation controls, and automated tests or audits guarding against sensitive-field leakage (DEC-025).
5. The uploader carries no dedicated processing disclosure; full local-versus-server and retention information lives on the Privacy page, with an accessible path from the uploader (DEC-168). Workflow states still label uploading, queued, and server processing truthfully when they occur (DEC-168).
6. JPG to PDF discloses that source metadata, including EXIF GPS and device information, may remain in the result (DEC-084); metadata is never sent to analytics or general logs (DEC-084).
7. Privacy copy is re-scoped: legacy claims such as "no tracking" and "no personal data at all" (`frontend/src/app/privacy/page.tsx:47,73`, `frontend/src/app/faq/page.tsx:61`) conflict with the accepted analytics and advertising model and are corrected (`audit-outputs/ui-docs-code-reconciliation.md` §6, §8.8).
8. No public usage counters; aggregate metrics stay private in a future admin dashboard that is not launch scope (DEC-126).
9. Password handling in the UI: passwords are entered only when required, held in memory for the shortest practical time, and never written to logs, analytics, URLs, dashboards, persistent queues, storage, backups, or error payloads (DEC-036, DEC-064, DEC-074).
10. Result-problem reports follow the data boundaries in Section 15.3 (DEC-117, DEC-120).
11. Regional monitoring and launch communication distinguish the US, LATAM, and Europe regions sufficiently to identify material failures in each, without prohibited user profiling (DEC-104).

## 18. Error and recovery behavior

1. **Inline error cards.** Ordinary processing failures use the existing inline error-card pattern with localized language and only valid retry, reset, password, or support-report actions for the failure type; error regions are announced without stealing focus (DEC-158).
2. **Safe rejection categories.** Rejections expose only safe general categories and never reveal exploit, scanner, or engine internals (DEC-169, DEC-171). Files classified as threats to infrastructure are blocked, never processed or returned, with a safe localized rejection and prompt cleanup (DEC-088). False-positive handling and support escalation never require users to email or upload the rejected document through the contact form or any other channel (DEC-088).
3. **Sanitization notice.** When active content is detected and removed, the UI shows the general categories removed without payload details (DEC-091). Sanitization is distinguished from malware detection, and the result does not imply that no other threat exists (DEC-091). For Merge and Split, active-content-bearing inputs route to the server sanitization path; when that path or the malware scanner is unavailable, affected jobs fail closed rather than bypassing the control, and no malware-free guarantee may be claimed (DEC-192).
4. **Routing transparency.** Jobs that fall back to the server show the transition visibly and do not claim the file stayed on-device (DEC-030, DEC-065). Failure classes such as security-policy failures, unsupported content, invalid passwords, user cancellation, and unsafe conditions fail closed rather than forcing a server upload (DEC-065).
5. **Retry semantics.** Server retry follows the legacy auto-retry pattern with a visible retrying label, a cleared timer on unmount or reset, and no indefinite retry loops (DEC-030; audit §6 item 4). If the server also cannot recover the file, the user receives a clear, actionable failure (DEC-030).
6. **Rate limiting and abuse controls.** Adaptive anonymous fair-use controls may delay, reject, or selectively challenge suspicious traffic with clear retry responses; ordinary users do not face a fixed daily quota (DEC-020). Messages are clear and actionable.
7. **Backend outage.** Tool pages stay accessible; browser-capable operations continue locally; server-dependent processing clearly communicates temporary unavailability; the frontend does not redirect ordinary tool traffic to the status page (DEC-163). Repeated submissions and misleading progress are prevented (DEC-163).
8. **Expiry.** Server results show an accurate countdown and warn before deletion; expired results cannot be restored (DEC-067).
9. **Blocked download.** A blocked auto-download leaves the job in Ready state with the manual button (DEC-068).
10. **Cancel and refresh.** Queued-job cancellation is honored atomically; refresh recovers an active job within the same tab via `sessionStorage` (DEC-069, DEC-072).
11. **Support escalation.** Result-problem reports and the contact form route to the owner-managed support process without requesting document attachments (DEC-046, DEC-050, DEC-117).

## 19. SEO and content migration constraints

1. **Locale-prefixed routes** for every localized page, including English; localized slugs, metadata, structured data, internal links, sitemaps, canonicals, and hreflang generated consistently per locale (DEC-023). Indonesian tool and content URLs use translated slugs (DEC-122).
2. **Locale-less entry** redirects once by supported browser language; manual choice overrides and is remembered with minimal non-sensitive storage; unsupported languages fall back to English; crawler and canonical behavior is not redirected unpredictably (DEC-047).
3. **Legacy URL inventory.** The complete legacy sitemap and indexable URL inventory is audited before relaunch, with an explicit retain/update, redirect, noindex, or removal disposition for every URL (DEC-127). Deferred legacy tool URLs return an intentional localized 410 Gone by default; a specific URL may instead receive a targeted relevant redirect only when credible traffic or intent evidence justifies it (DEC-194). The 410 experience explains that the tool is unavailable and links to relevant live tools without pretending the old capability still exists; sitemap, navigation, canonical links, and internal links exclude 410 URLs (DEC-194). Legacy pages that still attract meaningful traffic are retained and updated rather than discarded (DEC-114). Retention never preserves stale instructions, unavailable features, obsolete claims, or duplicate pages (DEC-114).
4. **Legacy archive.** After relaunch, the domain serves only the rebuilt product; the legacy application remains archived and is not exposed on a public legacy subdomain (DEC-099). Important legacy URLs receive intentional redirects or replacement responses, with the localized 410 default for deferred tool URLs (DEC-099, DEC-194).
5. **Indonesian preservation.** Valuable legacy Indonesian content is deliberately mapped, updated, and localized rather than left as an inconsistent island (DEC-115). The exact Indonesian coverage at relaunch is reconciled with the one-month schedule and the complete-over-deadline policy (DEC-115, DEC-118, DEC-103).
6. **Tool-page SEO.** Each tool page answers transactional intent with the tool first, followed by instructions, benefits, processing and privacy explanation, use cases, FAQs, and related tools (DEC-044). No invented superlatives or quantified performance claims (DEC-066).
7. **No competitor pages** at relaunch (DEC-128). Educational articles may discuss objective format or workflow choices without becoming disguised competitor pages (DEC-128).
8. **Blog SEO.** Launch of 15 articles (five topics, three locales) with blocking quality gates; post-launch cadence of at most one coordinated topic per day; truthful publication and update dates; no keyword filler or duplication (DEC-048, DEC-052, DEC-053, DEC-113, DEC-121, DEC-124).
9. **No launch campaign**; the relaunch is direct activation with a coordinated checklist covering deployment, redirects, indexing, monitoring, support, and status (DEC-140).
10. **No public counters** that could become misleading traffic claims (DEC-126).

## 20. Acceptance criteria

Launch acceptance is measured against the following criteria, which the owner verifies during design and implementation review. Every criterion traces to an accepted decision.

### 20.1 Launch completeness

1. All five tools are production-ready and the public launch happens only when the full EN/ES/ID set is complete (DEC-027, DEC-118).
2. Privacy, Terms, and Cookies/Advertising pages exist in all three locales with accurate processing and retention descriptions (DEC-045, DEC-168).
3. Support email and contact form are operational with an owner-managed inbox (DEC-046, DEC-050).
4. Public status page is live, Vercel-hosted, and automatically derived (DEC-116, DEC-119, DEC-161).
5. Roadmap is live, informational, read-only, and states the free-forever commitment (DEC-123, DEC-125, DEC-138).
6. Fifteen launch articles (five topics x EN/ES/ID) pass all blocking gates (DEC-052, DEC-121).
7. Full legacy URL inventory has explicit dispositions with no soft 404s or redirect chains (DEC-127); deferred legacy tool URLs return a localized 410 by default, with targeted redirects only on credible traffic or intent evidence (DEC-194).
8. Relaunch is direct production activation with a coordinated checklist and no beta label (DEC-096, DEC-140).

### 20.2 Visual continuity

1. The rebuilt site is recognizable as the existing Papyr: same color direction, typography character, card language, spacing rhythm, navigation model, uploader experience, and overall tone (DEC-143). Verified by side-by-side comparison of key surfaces (homepage, one tool page, navbar, footer) against the legacy clone.
2. Documented defects D1-D13 are corrected without changing the visual character (Section 10.6; `audit-outputs/ui-home-shell-audit.md` §12).
3. One canonical tool catalog drives nav, footer, homepage grid, and Related Tools (DEC-154; audit D2).

### 20.3 Interaction correctness

1. Tool pages follow the shared sequence: header, dropzone, configuration when needed, processing, result and download, privacy information, related tools (DEC-144).
2. Processing and results stay on one page; no redirect to a result URL (DEC-153).
3. Progress is stage-based and honest; no fabricated percentages (DEC-033).
4. Auto-download is attempted on success; a blocked auto-download leaves the job in Ready state with a manual Download button (DEC-029, DEC-068).
5. Multi-file results deliver a ZIP plus individual downloads in user-entered order (DEC-037, DEC-078).
6. "Process another file" resets to the uploader without a full-page reload and returns focus appropriately (DEC-156).
7. Server results show an accurate expiry countdown and warn before deletion; expiry is not extendable (DEC-067, DEC-070, DEC-075).
8. Queued-server-job cancellation works atomically; active processing cannot be cancelled by the user (DEC-069).
9. Same-tab refresh resumes an active server job via minimal `sessionStorage` state (DEC-072).
10. Closing the tab does not cancel an accepted server job (DEC-071).
11. Encrypted PDFs request passwords only when required, per file where applicable, with distinct wrong-password errors (DEC-036, DEC-064, DEC-074).
12. Active content is sanitized from outputs with category-level disclosure; Merge and Split active-content inputs route to the server sanitization path and fail closed when that path is unavailable (DEC-090, DEC-091, DEC-192).
13. Threat-classified files are blocked with safe localized rejections (DEC-088).

### 20.4 Tool-specific behavior

1. **Compress:** one automatic premium-screen mode, no quality controls; always produces a new artifact; reports actual sizes and real change honestly including zero or negative savings; never substitutes the original or fabricates a percentage (DEC-014, DEC-080). The production model uses the official unmodified Ghostscript executable as a separate server-side subprocess and passes its focused license review before launch; otherwise Compress moves to a permissive engine path or a commercial Ghostscript license before launch (DEC-195).
2. **Merge:** file-level reorder and removal only; keyboard reordering works and is announced; the whole job fails when any source is invalid; valid sources stay in memory for correction; document features are preserved to the safe extent supported (DEC-040, DEC-076, DEC-079).
3. **Split:** custom ranges and per-page modes; user-entered order preserved; overlaps allowed as independent outputs; preview shows effective sequence and duplicated membership; ZIP and individual downloads (DEC-038, DEC-037, DEC-077, DEC-078).
4. **JPG to PDF:** accepts JPG/JPEG, PNG, and WebP inputs while keeping the "JPG to PDF" name (DEC-187); automatic per-image fitting with margins, no cropping, EXIF orientation; Letter only for trusted US/CA edge country codes and A4 for every other, missing, or invalid code, with the locale never deciding paper size; selected standard visible before processing; metadata-preservation disclosure present (DEC-041, DEC-082, DEC-191, DEC-084).
5. **PDF to JPG:** one automatic high-quality profile; transparency composited onto white; sequential rendering within the 16-megapixel ceiling; page selections preserve duplicates and requested order with unambiguous output, ZIP, manifest, and naming; no promise of creating missing detail (DEC-039, DEC-081, DEC-015, DEC-186).

### 20.5 Accessibility

1. WCAG 2.2 AA acceptance coverage per Section 16 passes automated checks plus representative manual keyboard and assistive-technology testing (DEC-062).
2. Known exceptions are documented with impact and remediation; no certification claims are made (DEC-062).
3. Supported-browser matrix behavior is verified, including progressive-enhancement fallbacks and a clear unsupported-browser path (DEC-031).

### 20.6 Advertising and performance

1. Only banner and native formats load; all excluded formats are verified absent (DEC-018). The no-prior-consent position remains the owner-reaffirmed accepted risk, with no compliance claims (DEC-190).
2. Ad slots reserve stable dimensions; no ad obstructs task flow, downloads, consent, or navigation; result pages keep ads clearly separated from Download controls; tool pages place ads after the primary experience (DEC-018, DEC-102, DEC-131, DEC-151).
3. Status, legal, and support information remain fully readable and functional when ads are blocked or fail (DEC-130).
4. The 90-day operating dashboard measures job success and failure, processing and queue latency, uptime, Core Web Vitals, organic entrances, tool usage distribution, and completed downloads, distinguishing browser-local from server jobs without collecting document contents (DEC-024).
5. Exact numeric targets and baseline windows are defined before implementation planning is approved (DEC-024).

### 20.7 Localization

1. Complete EN/ES/ID coverage across tools, legal, support, status, metadata, and core accessibility text (DEC-118).
2. The navbar language selector works on desktop and mobile, shows the active locale, and preserves the equivalent page (DEC-149).
3. Locale-less entry detection, manual override memory, and unsupported-language fallback behave per DEC-047 without SEO duplication or redirect loops.
4. Localized copy survives length growth at all breakpoints (Section 9, Section 16).

### 20.8 Schedule

The relaunch targets one month (DEC-100). Scope and quality gates are not bypassed to meet the date (DEC-103); schedule risk is reported early and transparently (DEC-103).

## 21. Unresolved items requiring later research

These items are deliberately not decided by this specification. Each requires owner input, SEO design, or the research and approval gates in DEC-054 through DEC-057. Items whose underlying questions were resolved by DEC-189 through DEC-196 are narrowed to their still-open residuals rather than deleted, preserving numbering. Item 20 records a confirmed deferral with future work rather than an unresolved choice.

1. **Exact per-tool server limits** and browser-limit adjustments after anonymous reliability telemetry and real-device testing (DEC-015, DEC-034). Conservative defaults documented as design and safety choices, adjusted from production observations rather than benchmark-proven, and the procedure for raising them are technical-design responsibilities (DEC-066). The initial backend runs one active worker with one job at a time; raising worker concurrency requires later capacity evidence and explicit approval (DEC-189).
2. **Compress engine profile thresholds.** The engine selection is resolved: the official unmodified Ghostscript executable as a separate server-side subprocess, subject to a focused license review before public launch (DEC-195). The "premium screen quality" profile's internal thresholds (downsampling, re-encoding, quality floors) are set during technical design and validated through normal functional testing, without a benchmark program (DEC-014, DEC-066).
3. **Paper-standard regional rule wording.** The regional rule itself is resolved: Letter only for trusted US/CA edge country codes, A4 for every other, missing, or invalid code, and the active locale never deciding paper size (DEC-191). What remains is only the user-visible summary wording, finalized in the copy pass (DEC-191).
4. **Tool slugs for EN/ES/ID** and the legacy URL redirect map, selected during SEO design (DEC-023, DEC-122, DEC-127). Deferred legacy tool URLs default to a localized 410 Gone, with targeted redirects only on credible traffic or intent evidence (DEC-194); the five-tool slug table and any remaining non-tool dispositions stay in SEO design.
5. **Launch blog topic selection** for the five topics and the daily post-launch topic pipeline details (DEC-052, DEC-053, DEC-124).
6. **Indonesian coverage extent at relaunch**, reconciled with the one-month schedule and the complete-over-deadline policy (DEC-115, DEC-118, DEC-103).
7. **Contact form provider, anti-spam approach, and delivery monitoring** for the owner-managed inbox (DEC-046, DEC-050).
8. **Status page implementation details** and health-signal noise resistance (DEC-116, DEC-119, DEC-161).
9. **Adsterra script, cookie, identifier, and regional behavior review** against current terms and applicable law. The no-prior-consent gating decision itself is reaffirmed (DEC-190); the provider terms, exact ad-unit scripts, cookies, identifiers, and recipients still require review before launch, and a later legal or provider-policy determination that prior consent is mandatory remains binding over the preference (DEC-022, DEC-190, DEC-045).
10. **Legal review** of Privacy, Terms, and Cookies/Advertising copy before launch (DEC-045).
11. **Rendered visual verification** of the baseline: all three audits were static source inspections, so spacing, contrast, and font rendering claims must be spot-checked in a browser during implementation (`audit-outputs/ui-home-shell-audit.md` U7; `audit-outputs/ui-five-tools-audit.md` §8.1).
12. **Contrast re-verification** of the documented token combinations with a contrast tool (DEC-062; `audit-outputs/ui-docs-code-reconciliation.md` §8.2).
13. **Navbar width intent:** 1440px navbar container versus 1200px content elsewhere (D3) needs owner confirmation before unification (`audit-outputs/ui-home-shell-audit.md` U2).
14. **Duplicate CTA intent:** navbar "Try free" and hero CTA both target the Compress page in the legacy site; confirm whether the funnel is deliberate (U3).
15. **Homepage entrance animations:** the homepage has no entrance animations while tool pages use fade-up; decide whether to unify or keep the calm hero deliberately (U5), which also resolves the dropdown-panel transition question (D12).
16. **Merge error-state edge case:** legacy behavior keeps state at error when a valid file is added alongside an invalid one during an error state; confirm the desired auto-clear behavior (`audit-outputs/ui-five-tools-audit.md` §8.7).
17. **Privacy copy re-scoping** of legacy "no tracking" and "no personal data" statements against the accepted analytics and advertising model, with qualified review (DEC-025, DEC-022; `audit-outputs/ui-docs-code-reconciliation.md` §8.8).
18. **FAQ copy accuracy:** the officially accepted JPG-to-PDF input formats are JPG/JPEG, PNG, and WebP (DEC-187); FAQ and tool copy must state these accurately, correcting the legacy claims noted at `audit-outputs/ui-docs-code-reconciliation.md` §8.9.
19. **`@theme inline` token emission verification** so the body background, text color, and font never silently fall back (Section 10.1; `audit-outputs/ui-home-shell-audit.md` U1).
20. **Newsletter deferral (confirmed, not unresolved).** The newsletter is deferred at launch (DEC-107, DEC-109); no launch action, but provider and consent design return before any later implementation.
21. **Gateway capability documentation** before the blog automation technical design is finalized. Identity and authentication are resolved: the owner's OpenAI-compatible gateway at `https://router.budgezen.com/v1`, exact JSON model identifier `mypapyr` (never substituted with the public `gpt5.6-sol` name in requests), and `Authorization: Bearer <API_KEY>` from protected server-side or automation secrets only (DEC-193, DEC-196). Remaining documentation items are the exact request and response schema deviations, structured-output behavior, tool-use behavior, effective context, data retention, availability, and applicable safety or compliance policies (DEC-193, DEC-196). Provider integration stays isolated behind an interface so publishing can be paused or migrated (DEC-051, DEC-193).

## 22. Relationship to the Technical Architecture Specification

Per DEC-185, this Product and UX Design Specification and the Technical Architecture Specification are two coordinated documents sharing the same decision baseline. Boundaries:

1. This document owns user experience, interaction behavior, information architecture, localization, advertising placement, and acceptance criteria that are observable by users.
2. The Technical Architecture Specification owns processing engines, queue and worker design, server limits, security controls, validation internals, deployment, operations, monitoring, and analytics plumbing.
3. Where responsibilities meet (processing routing, retention timers, result delivery, limits), this document states the user-visible behavior and the architecture document states the mechanism. Requirements are not duplicated inconsistently between the two documents.
4. Implementation planning begins only after owner review and approval of both specifications and completion of the required research and reconciliation gates (DEC-185, DEC-060). The cross-domain reconciliation is complete (`audit-outputs/research/reconciliation-report.md`, X2); its compatible findings are design inputs, its owner-side contract and operational inputs remain to be supplied, and its readiness statement does not authorize implementation (DEC-057).
