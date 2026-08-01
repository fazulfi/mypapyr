# Evidence File — UI-Baseline Verification Checklist (Track B, Deliverable B5)

- **Date**: 2026-07-31
- **Extractor**: subagent (codebase search specialist), delegated by Sisyphus
- **Deliverable**: this file (primary deliverable, per AGENTS.md mandatory delegated-output persistence). A chat-only summary is insufficient.
- **Purpose**: Extract, deduplicate, and organize verbatim evidence from five persisted audit files into the item-ordered structure required for the B5 UI-baseline verification checklist. No new findings were invented; every quote below is verbatim from a source file with path + line range. Nothing was modified except this output file.
- **Sources consumed (read in full, read-only)**:
  1. `<workspace-root>\audit-outputs\ui-docs-code-reconciliation.md` (341 lines)
  2. `<workspace-root>\audit-outputs\ui-five-tools-audit.md` (303 lines)
  3. `<workspace-root>\audit-outputs\ui-home-shell-audit.md` (210 lines)
  4. `<workspace-root>\audit-outputs\spec-cross-review.md` (148 lines)
  5. `<workspace-root>\audit-outputs\spec-corrections-report.md` (146 lines)
- **Conventions**: `[CONFIRMED]` = verified fact (code-grounded), `[RECOMMENDATION]` = suggested fix for the rebuild, `[OWNER QUESTION]` = open item awaiting owner confirmation, `[UNCERTAINTY]` = explicitly unresolvable in the source. Item IDs (D1-D13, U1-U7, H-1, M-1..M-4, L-1..L-6, §8.x, §6.x) are preserved as in the sources.
- **Verification**: `git -C <workspace-root>\papyr-reference status --porcelain` returned empty output, exit 0 (run 2026-07-31). `papyr-reference/` was only read, never modified.

---

## 1. NAVBAR WIDTH INTENT (owner confirmation item D3)

### 1.1 The observed inconsistency

- `ui-home-shell-audit.md` L60 (`§3.3`):
  > "**Content column:** max-w-[1200px] px-6 for home sections (page.tsx:488,535,569) and footer (Footer.tsx:171,198). Navbar uses max-w-[1440px] (Navbar.tsx:146) - inconsistent (D3)."

- `ui-home-shell-audit.md` L89 (`§5 Navbar`):
  > "- Container: mx-auto flex h-[52px] max-w-[1440px] items-center gap-4 px-6 (146) - fixed 52px height."

- `ui-home-shell-audit.md` L157 (`§12 Defects, D3`) — [CONFIRMED] defect statement:
  > "**D3 Width inconsistency:** navbar container max-w-[1440px] (Navbar.tsx:146) vs max-w-[1200px] everywhere else (page.tsx:488,532,535,569; Footer.tsx:171,198). On screens >= 1440px the nav CTA and categories sit right of the page content alignment. Pick one width (see U2)."

### 1.2 The owner question (U2)

- `ui-home-shell-audit.md` L193 (`§14 Uncertainties, U2`) — [OWNER QUESTION], unanswered in all five files:
  > "**U2: Intent of max-w-[1440px] navbar** (Navbar.tsx:146) vs 1200px elsewhere - deliberate breathing room or drift? Needs owner confirmation before unifying (D3)."

### 1.3 Docs-vs-code contradiction (reconciliation view)

- `ui-docs-code-reconciliation.md` L135 (`§3.3 Contradicted` table, first row) — [CONFIRMED]:
  > "| §3.1 L292 / §4.2 L605 / §5.1: Navbar container `max-w-[1200px]` | Navbar container is `max-w-[1440px]` | `Navbar.tsx:146` |"

- `ui-docs-code-reconciliation.md` L215 (`§4.3 Contradicted` table, first row) — [CONFIRMED]:
  > "| §6.1 L364 "Konten tidak pernah lebih lebar dari ini [1200px]" | Navbar container is 1440px | `Navbar.tsx:146` |"

- `ui-docs-code-reconciliation.md` L18 (executive summary item 3) — [CONFIRMED] context:
  > "Catalog and navigation claims are the most stale. Both docs describe a 6-tool Papyr with 6 flat navbar links; the code implements **13 tools**, a **4-category dropdown navbar**, a **1440px navbar container** (docs say 1200px), a footer **tools directory section**, a **13-card landing grid** (doc says 6), and an **OtherTools grid of 12 cards** (doc says 5)."

### 1.4 Recommendation for the canonical spec

- `ui-docs-code-reconciliation.md` L294 (`§7.2 Rewrite or extend`) — [RECOMMENDATION]:
  > "- **Navbar spec**: 4-category dropdown architecture, 1440px container, hover+click behavior, outside-click close, mobile `<details>` accordion, active states."

- `ui-docs-code-reconciliation.md` L315 (`§7.3 Mark historical`) — [RECOMMENDATION]:
  > "- Universal 1200px rule (Doc32 §6.1) — replaced by the 1440px navbar + 1200px content convention."

- `ui-docs-code-reconciliation.md` L223 (`§4.4 Missing`, item 3) — [CONFIRMED] gap:
  > "3. The 1440px navbar container and the footer tools-directory pattern."

- `ui-home-shell-audit.md` L146 (`§11 Strengths`, item 6) — [CONFIRMED] adjacent baseline fact (content column, not navbar):
  > "6. **Fluid hero type** via clamp(40px,6vw,72px) + 1200px content column with px-6 gutters."

- `spec-cross-review.md` L112 — [CONFIRMED] the width fact was used in the DEC-143 verification, citing `Navbar.tsx:145-146`:
  > "**DEC-143 visual preservation:** Token table, typography, spacing/radius/shadow/motion, component character, D1-D13 corrections, and approved-change limits (UX §10, §20.2) match the home-shell and five-tools audits exactly (verified against `globals.css:3-10`, `page.tsx:486-593`, `Navbar.tsx:145-146`, `compress/page.tsx:94-135`). No invented tokens or visual claims."

### 1.5 Status summary

- Confirmed fact: navbar container is `max-w-[1440px]` (`Navbar.tsx:146`); every other container is `max-w-[1200px]` (`page.tsx:488,532,535,569`; `Footer.tsx:171,198`).
- Confirmed contradiction: Doc19 §3.1 L292 / §4.2 L605 / §5.1 and Doc32 §6.1 L364 all claim a universal 1200px max.
- Open owner question: U2 — deliberate breathing room or drift? No answer is recorded in any of the five files.

---

## 2. DUPLICATE CTA INTENT (U3)

### 2.1 The owner question (U3)

- `ui-home-shell-audit.md` L194 (`§14 Uncertainties, U3`) — [OWNER QUESTION], unanswered in all five files:
  > "**U3: Duplicate CTAs to /compress** - nav "Coba Gratis" + hero "Mulai gratis" both target /compress. Likely deliberate funnel; confirm."

### 2.2 The two CTAs (evidence of the duplication)

- `ui-home-shell-audit.md` L94 (`§5 Navbar`) — [CONFIRMED] navbar CTA:
  > "- **Desktop CTA** (207-212): "Coba Gratis" -> /compress, bg-accent rounded-lg px-4 py-2 text-sm text-white shadow-sm, hover lift."

- `ui-home-shell-audit.md` L108 (`§7 Homepage`) — [CONFIRMED] hero CTA:
  > "Primary CTA "Mulai gratis" -> /compress: bg-navy rounded-[10px] px-8 py-3.5 text-white shadow-md with hover lift (510-515)."

- `ui-home-shell-audit.md` L95 (`§5 Navbar`) — [CONFIRMED] mobile variant of the same funnel:
  > "- **Mobile (< md)** (215-230): compact "Coba Gratis" CTA (px-3.5 py-1.5 text-[13px]) + hamburger button with aria-label switching "Buka menu"/"Tutup menu" (226); no aria-expanded (D8)."

### 2.3 Docs-side confirmation of both CTAs

- `ui-docs-code-reconciliation.md` L82 (`§3.1 Accurate` row) — [CONFIRMED]:
  > "| §3.1 L286-309 navbar basics: sticky top-0 z-50, h-[52px], bg-bg/92 blur, border-b slate-200, logo h-7 w-7 + text-[17px], CTA "Coba Gratis", mobile mini CTA px-3.5 py-1.5 text-[13px], hamburger aria-label, auto-close on route change | `Navbar.tsx:145-146,156-160,207-229` |"

- `ui-docs-code-reconciliation.md` L107 (`§9.1 Accurate` row) — [CONFIRMED]:
  > "| §9.1 L970-1015 landing hero (pill with dot, H1 "Alat PDF yang langsung bekerja.", navy CTA "Mulai gratis", trust badges) | `page.tsx:488-528` — classes and copy verified verbatim (tool card count contradicted — §3.3) |"

- `ui-docs-code-reconciliation.md` L190 (`§4.1 Accurate` row) — [CONFIRMED] the navy-button claim is accurate only for the hero:
  > "| §7.2 L441-452 primary button | `page.tsx:512` — verbatim (hero CTA; tool-page action buttons differ — §4.2/4.3) |"

- `ui-docs-code-reconciliation.md` L206 (`§4.2 Stale` row) — [CONFIRMED] nuance relevant to CTA semantics:
  > "| §4.4 L270 "Primary button bg #1E3A5F (navy) — CTA utama" | True for the hero CTA only; every tool-page primary action button (merge, split, convert, download) is accent blue | `page.tsx:512` (navy) vs `merge:639-643`, `split:488-492`, `PDFUploader:498`, `pdf-to-image:401` (accent) |"

### 2.4 Status summary

- Confirmed fact: two always-visible CTAs target `/compress` — navbar "Coba Gratis" (accent blue, `Navbar.tsx:207-212`) and hero "Mulai gratis" (navy, `page.tsx:510-515`); a third compact "Coba Gratis" exists in the mobile navbar.
- Open owner question: U3 — likely deliberate funnel; no owner confirmation is recorded in any of the five files.

---

## 3. HOMEPAGE ENTRANCE ANIMATIONS (U5 and D12)

### 3.1 The owner questions

- `ui-home-shell-audit.md` L196 (`§14 Uncertainties, U5`) — [OWNER QUESTION], unanswered in all five files:
  > "**U5: Homepage has no entrance animations** while every tool page uses animate-fade-up - deliberate calm hero or inconsistency to correct? Affects D12 direction."

- `ui-home-shell-audit.md` L166 (`§12 Defects, D12`) — [RECOMMENDATION] tied to U5:
  > "**D12 Instant panel appearance:** dropdowns and mobile menu have no transition while chevrons animate (Navbar.tsx:183-200,234-262). Add a short fade/slide to match the motion language, or keep instant deliberately (U5-adjacent)."

### 3.2 The observed asymmetry

- `ui-home-shell-audit.md` L68 (`§3.4 Motion`) — [CONFIRMED]:
  > "- fade-up 0.3s (globals.css:28-37, utility at 43-45): used across all tool pages and PDFUploader (63 matches in 12 files; e.g., split/page.tsx:375, ocr/page.tsx:403). **Not used on the homepage** (U5)."

- `ui-home-shell-audit.md` L112 (`§7 Homepage`) — [CONFIRMED]:
  > "- No metadata export (inherits layout defaults); no entrance animations (U5)."

- `ui-home-shell-audit.md` L72 (`§3.4 Motion`) — [CONFIRMED] the D12 half of the question:
  > "- Dropdown panels and the mobile menu open/close **instantly** (no transition) - see D12."

- `ui-home-shell-audit.md` L147 (`§11 Strengths`, item 7) — [CONFIRMED] the motion language the homepage does not participate in:
  > "7. **Motion discipline** - 0.3s fade-up, shimmer processing state, chevron rotations; subtle and consistent on tool pages."

### 3.3 The tool-page motion baseline (what the homepage is compared against)

- `ui-five-tools-audit.md` L48 (`§2 Shared Design System Baseline`) — [CONFIRMED]:
  > "- **Animations** (`globals.css:19-44`): `animate-shimmer` (1.4s infinite gradient sweep) used for indeterminate processing bars; `animate-fade-up` (0.3s, translateY(10px)) used for every state-transition card. All state cards animate in — consistent across all five tools."

- `ui-five-tools-audit.md` L251 (`§5 Preserve`, item 2) — [CONFIRMED]/[RECOMMENDATION]:
  > "2. **State-card language** — done (accent border + emerald check), processing (shimmer), error (rose) cards with `animate-fade-up`; identical classes."

- `ui-docs-code-reconciliation.md` L80 (`§3.1 Accurate` row for Doc19 §2.6) — [CONFIRMED]:
  > "| §2.6 L250-259 animations | `globals.css:19-44` (shimmer 1.4s ease-in-out infinite; fade-up 0.3s ease forwards); accordion `duration-200` `faq/page.tsx:113`; `hover:-translate-y-0.5` `page.tsx:512` |"

- `ui-docs-code-reconciliation.md` L140 (`§3.3 Contradicted` row) — [CONFIRMED] known deviation inside the motion token system (relevant to standardizing D12/U5 motion decisions):
  > "| §2.6 L252 `animate-shimmer` 1.4s | Rotate processing uses an inline 1.2s shimmer variant, bypassing the token | `rotate/page.tsx:567` (`animate-[shimmer_1.2s_ease-in-out_infinite]`) |"

- `ui-docs-code-reconciliation.md` L285 (`§7.1 Retain as-is`) — [RECOMMENDATION]:
  > "- Animation keyframes: shimmer 1.4s and fade-up 0.3s, transition conventions, hover lift (Doc19 §2.6; Doc32 §9) — with a note to standardize rotate's 1.2s inline variant."

- `ui-docs-code-reconciliation.md` L299 (`§7.2`) — [RECOMMENDATION]:
  > "- **Loading taxonomy**: add the spinner variant (rotate) or standardize on shimmer; document the 1.2s deviation decision."

### 3.4 Status summary

- Confirmed fact: homepage renders zero `animate-fade-up` usages; tool pages use it for every state-transition card (63 matches in 12 files); navbar/footer dropdown panels appear instantly.
- Open owner questions: U5 (homepage entrance animations — deliberate or inconsistent?) and, linked, D12 (panel transitions or deliberate instant). No owner answers are recorded in the five files.

---

## 4. MERGE ERROR-STATE EDGE CASE

### 4.1 The flagged edge case (owner-confirmation candidate)

- `ui-five-tools-audit.md` L298 (`§8 Uncertainties, item 7`) — [OWNER QUESTION], unanswered in all five files:
  > "7. **Merge error path when adding files fails while state === 'error'** — `addFiles` sets state to idle only when `errors.length === 0`; if a valid file is added alongside an invalid one, state stays 'error' until "Coba Lagi" is clicked (the file IS added though). Confirm desired behavior (auto-clear error when valid files are added)."

### 4.2 The surrounding merge error-state behavior (context for the edge case)

- `ui-five-tools-audit.md` L106 (`§3.2 Merge`) — [CONFIRMED]:
  > "**State machine**: `'idle' | 'processing' | 'done' | 'error'` (:35). Files persist across error → "Coba Lagi" (returns to idle, list kept, :543-552)."

- `ui-five-tools-audit.md` L112 (`§3.2 Merge`) — [CONFIRMED]:
  > "- Error card (:536-554): "Terjadi Kesalahan" + message + "Coba Lagi"."

- `ui-five-tools-audit.md` L113 (`§3.2 Merge`) — [CONFIRMED]:
  > "- Upload zone + sortable file list rendered in `idle | error` (:557-681)."

- `ui-five-tools-audit.md` L121 (`§3.2 Merge`) — [CONFIRMED] multi-file error display:
  > "- Per-file validation (:368-400): non-PDF → `"<name>" bukan file PDF.`; >20MB → `"<name>" terlalu besar (maks 20MB).`; 0 bytes → `"<name>" kosong.`. Multiple errors joined into one message."

- `ui-five-tools-audit.md` L124 (`§3.2 Merge`) — [CONFIRMED] empty state:
  > "- Empty state: "Belum ada file. Upload minimal 2 PDF." (:657-661)."

- `ui-five-tools-audit.md` L125 (`§3.2 Merge`) — [CONFIRMED] disabled-CTA rule:
  > "- CTA "Gabungkan PDF" disabled until >= 2 files, with helper "Upload minimal 2 file PDF untuk menggabungkan." (:635-652). Disabled style: `bg-slate-200 text-slate-400 cursor-not-allowed`."

- `ui-five-tools-audit.md` L232 (`§4 Cross-Tool Consistency Matrix`, error-behavior row) — [CONFIRMED]:
  > "| Error → "Coba Lagi" behavior | reset to idle (file dropped) | idle (files kept) | ready if parsed else idle | idle (images kept) | ready if parsed else idle |"

- `ui-docs-code-reconciliation.md` L101 (`§3.1 Accurate` row for Doc19 §6.4) — [CONFIRMED] the standard error visual merge matches:
  > "| §6.4 L795-813 error visuals (rose-50/50, rose-200, alert circle, "Terjadi Kesalahan", "Coba Lagi") | `PDFUploader.tsx:517-533`; `merge:536-554`; `split:424-442` (rotate deviates — §3.3) |"

### 4.3 Related merge findings with bearing on error-state UX

- `ui-five-tools-audit.md` L131 (`§3.2 Merge`, A11y) — [CONFIRMED]:
  > "**A11y**: dropzone role=button OK; remove buttons labeled; drag handles unlabeled (SR announces bare "button"); dnd-kit has no `announcements`/`screenReaderInstructions` config, so keyboard reorder feedback is not announced; no aria-live on status changes; h1 → h3 jump in badges (no h2)."

- `ui-five-tools-audit.md` L276 (`§6 Correct`, item 13) — [RECOMMENDATION] mislabeled failure reason on client-side tools incl. merge:
  > "13. **`'server_error'` failure reason on client-side tools** (split/merge/image-to-pdf client path) — mislabeled; use a distinct reason like `'processing_error'` or `'client_error'`."

- `ui-five-tools-audit.md` L256 (`§5 Preserve`, item 6) — [CONFIRMED]/[RECOMMENDATION]:
  > "6. **Merge/image-to-pdf sortable lists** — pointer + keyboard sensors with 5px activation distance, order badges, per-item remove with aria-label."

### 4.4 Status summary

- Confirmed fact: merge keeps files across error→"Coba Lagi" (returns to idle with list kept); the upload zone and sortable list render in both `idle` and `error` states; per-file validation errors are joined into one message.
- Edge case: adding a valid file alongside an invalid one while in `error` state adds the file but leaves state at `error` until "Coba Lagi" is clicked (`addFiles` resets to idle only when `errors.length === 0`).
- Open owner question: confirm desired behavior (auto-clear error when valid files are added). No answer recorded in the five files.

---

## 5. CONTRAST RE-VERIFICATION METHOD (UX §21.12)

### 5.1 The re-verification recommendation

- `ui-docs-code-reconciliation.md` L289 (`§7.1 Retain as-is`, last bullet) — [RECOMMENDATION]:
  > "- Contrast table (Doc19 §8.4) — after one re-verification pass with a color-contrast tool."

- `ui-docs-code-reconciliation.md` L325 (`§8 Uncertainties`, item 2) — [UNCERTAINTY]:
  > "2. **Contrast ratios** (Doc19 §8.4): hex values match code, but ratios were not re-measured (static inspection only; no browser tooling)."

- `ui-docs-code-reconciliation.md` L72 (`§3.1 Accurate` row for Doc19 §1.4) — [UNCERTAINTY] the only specific color pair named:
  > "| §1.4 L98-102 aria-labels, semantic HTML, navy contrast claim | `Navbar.tsx:226`; `merge/page.tsx:324`; `layout.tsx:50-53`; navy `#1e3a5f` `globals.css:4` (ratio plausible but not re-measured — see Uncertainties) |"

### 5.2 Contrast-relevant color pairs and tokens identified across the audits

- `ui-five-tools-audit.md` L292 (`§8 Uncertainties`, item 1) — [UNCERTAINTY]:
  > "1. **Visual rendering unverified** — static source audit only; no browser run. Actual spacing, contrast, and font rendering were not confirmed (e.g., `text-accent/80` on "Sesudah" label, `bg-slate-50` panel contrast)."

- `ui-home-shell-audit.md` L56 (`§3.2 Typography`) — [CONFIRMED] the color hierarchy to be measured:
  > "- **Color hierarchy:** headings navy; body foreground #171717; secondary slate-500; tertiary slate-400/slate-300; emphasis accent."

- `ui-home-shell-audit.md` L47 (`§3.1 tokens`) — [CONFIRMED]:
  > "| --color-foreground | #171717 | Body text color via var(--color-foreground) (globals.css:14) |"

- `ui-home-shell-audit.md` L43-45 (`§3.1 tokens`) — [CONFIRMED]:
  > "| --color-navy | #1e3a5f | Brand/heading color: h1 (page.tsx:497,540,574), card titles, logo lockup, primary CTA background (page.tsx:512), tool-page h1s (compress/page.tsx:100-101) |"
  > "| --color-accent | #2563eb | Interactive accent: nav CTA (Navbar.tsx:209), links/active states (Navbar.tsx:191), eyebrows, icon tiles (page.tsx:582), hero accent span (page.tsx:500) |"
  > "| --color-bg | #f9fafb | Page background: body (globals.css:13), navbar glass (Navbar.tsx:145), footer (Footer.tsx:169), home wrapper (page.tsx:486) |"

- `ui-docs-code-reconciliation.md` L76 (`§3.1 Accurate` row for Doc19 §2.2) — [CONFIRMED] the five primary tokens are exact in code:
  > "| §2.2 L156-198 palette: five hex tokens; slate roles; semantic rose/emerald; accent tints 5/10/15/20/30/50/60 | `globals.css:4-8` (all five exact); `PDFUploader.tsx:454,517-524`; `page.tsx:550,582`; `PDFUploader.tsx:369-371` |"

- `ui-home-shell-audit.md` L198 (`§14, U7`) — [UNCERTAINTY]/[RECOMMENDATION] the verification method itself:
  > "**U7: No rendered verification was possible in this audit** (browser tooling out of scope per task constraints); all visual claims are derived from source classes and should be spot-checked in the browser during rebuild validation."

### 5.3 Status summary

- No numeric contrast ratio was measured or recorded in any of the five files; every audit explicitly defers measurement to a tool-based pass (color-contrast tool / browser spot-check) during rebuild validation.
- The concrete pairs to measure: navy #1e3a5f vs bg #f9fafb/white (headings, primary CTA), foreground #171717 vs bg, accent #2563eb vs white (nav CTA, download buttons), slate-500/slate-400/slate-300 secondary/tertiary text, `text-accent/80` on the Compress "Sesudah" label, `bg-slate-50` panel contrast.

---

## 6. @THEME INLINE TOKEN EMISSION (UX §21.19)

### 6.1 The flagged risk (U1 — "verify first")

- `ui-home-shell-audit.md` L192 (`§14 Uncertainties, U1`) — [UNCERTAINTY] (verification-first item):
  > "**U1 (verify first): @theme inline var() emission.** globals.css uses @theme inline (line 3) but plain CSS body rules reference var(--color-bg), var(--color-foreground), var(--font-sans) (lines 13-15). Whether Tailwind v4 emits these custom properties to :root for an inline theme is version-dependent; the repo contains no compiled CSS artifact (.next output is not present) to confirm. Verification: build and grep the output CSS for --color-bg in a :root block, or inspect body computed background/font in a browser. If the variables are not emitted, body background/font silently fall back (masked on the homepage by the bg-bg wrapper, but font-family would fall back to system-ui site-wide). Rebuild must not carry this ambiguity."

### 6.2 The defect statement (D5)

- `ui-home-shell-audit.md` L159 (`§12 Defects, D5`) — [CONFIRMED]/[RECOMMENDATION]:
  > "**D5 var() reliance on @theme inline tokens in plain CSS:** globals.css:13-15 use var(--color-bg), var(--color-foreground), var(--font-sans). With Tailwind v4 @theme inline, custom properties may not be emitted to :root, which would silently break body background/color/font-family (see U1). Rebuild should use utilities (bg-bg, text-foreground, font-sans) or a non-inline @theme for any direct var() use."

### 6.3 Related token-emission findings (D4, D7)

- `ui-home-shell-audit.md` L158 (`§12 Defects, D4`) — [CONFIRMED]/[RECOMMENDATION] dead tokens adjacent to the @theme question:
  > "**D4 Dead tokens:** --color-background: #ffffff (globals.css:7) never used; --font-dm-sans (layout.tsx:10) never consumed by any utility (font-sans uses the literal 'DM Sans' string from --font-sans). Either wire --font-sans: var(--font-dm-sans) (with non-inline @theme) or drop the variable."

- `ui-home-shell-audit.md` L161 (`§12 Defects, D7`) — [CONFIRMED]/[RECOMMENDATION] masking interaction with U1:
  > "**D7 Redundant home wrapper:** min-h-screen bg-bg (page.tsx:486) duplicates the body background and the layout min-height shell; it also masks any body-bg failure (U1). No wrapper needed if the shell is correct."

- `ui-home-shell-audit.md` L39 (`§3.1`) — [CONFIRMED] the @theme inline usage:
  > "### 3.1 Design tokens (globals.css:3-10, @theme inline)"

- `ui-home-shell-audit.md` L48 (`§3.1 tokens`) — [CONFIRMED] the font token that is directly var()-referenced:
  > "| --font-sans | 'DM Sans', system-ui, sans-serif | Body font; font-sans utility on body (layout.tsx:50) |"

- `ui-home-shell-audit.md` L54 (`§3.2 Typography`) — [CONFIRMED] the unused next/font variable:
  > "- **Font:** DM Sans via next/font/google (layout.tsx:9-14), preload: true, display: swap. The generated variable --font-dm-sans is applied to <html> (layout.tsx:49) but **no utility references it**: font-sans resolves to --font-sans whose value is the literal string 'DM Sans', system-ui, sans-serif (globals.css:9), which matches the next/font-registered @font-face family name. It works, but the next/font variable is effectively unused (see D4)."

### 6.4 Status summary

- Confirmed fact: `globals.css:3` uses `@theme inline`; plain CSS at `globals.css:13-15` references `var(--color-bg)`, `var(--color-foreground)`, `var(--font-sans)` directly; no compiled `.next` CSS artifact exists in the repo to confirm whether Tailwind v4 emits these custom properties to `:root`.
- Verification method specified: build and grep output CSS for `--color-bg` in a `:root` block, or inspect body computed background/font in a browser.
- Recommended fix: use utilities (`bg-bg`, `text-foreground`, `font-sans`) or a non-inline `@theme` for any direct `var()` use.
- No owner decision is recorded in the five files; U1 is explicitly labeled "verify first".

---

## 7. RENDERED VISUAL VERIFICATION STANDARD (UX §21.11)

### 7.1 The shared stance across all audits: source-derived claims need browser spot-checks

- `ui-home-shell-audit.md` L198 (`§14, U7`) — [UNCERTAINTY]/[RECOMMENDATION]:
  > "**U7: No rendered verification was possible in this audit** (browser tooling out of scope per task constraints); all visual claims are derived from source classes and should be spot-checked in the browser during rebuild validation."

- `ui-home-shell-audit.md` L12 (`§1 Scope and Method`) — [CONFIRMED] the audit's own standard:
  > "Only read-only inspection was used (Read, Glob, Grep). No files under `papyr-reference/` were modified; no shell/install/build/browser/git operations were performed. Findings are grounded in source code and tests with file:line citations. Anything requiring rendered/browser confirmation is listed under Section 14 (Uncertainties)."

- `ui-five-tools-audit.md` L292 (`§8 Uncertainties`, item 1) — [UNCERTAINTY]:
  > "1. **Visual rendering unverified** — static source audit only; no browser run. Actual spacing, contrast, and font rendering were not confirmed (e.g., `text-accent/80` on "Sesudah" label, `bg-slate-50` panel contrast)."

- `ui-docs-code-reconciliation.md` L325 (`§8 Uncertainties`, item 2) — [UNCERTAINTY]:
  > "2. **Contrast ratios** (Doc19 §8.4): hex values match code, but ratios were not re-measured (static inspection only; no browser tooling)."

- `ui-docs-code-reconciliation.md` L324 (`§8 Uncertainties`, item 1) — [UNCERTAINTY]:
  > "1. **Historical code states**: Whether Doc19 (Jun 2025) and Doc32 (Jun 2026) matched the codebase at their authored dates cannot be verified without git history (git operations were out of scope)."

- `ui-five-tools-audit.md` L296 (`§8 Uncertainties`, item 5) — [UNCERTAINTY]/[RECOMMENDATION] interaction-level rendered verification:
  > "5. **dnd-kit keyboard experience** — KeyboardSensor is configured, but without `announcements` the live-region feedback cannot be verified statically; needs a screen-reader pass in the rebuild."

### 7.2 Cross-review spot-verification as the applied standard

- `spec-cross-review.md` L23-24 (`§1`) — [CONFIRMED] how the cross-review verified legacy citations:
  > "Spot-verification of legacy citations was performed against `papyr-reference/` (read-only):
  > `docs/runbook-vps.md:17,25,§7,§10.1-10.4`; `backend/services/async_task.py:47`; `backend/routers/status.py:4,14,17,28`; `backend/utils/config.py:101-102`; `backend/utils/r2.py:24`; `frontend/src/hooks/useAsyncTask.ts:6-7,32`; `deploy/nginx/conf.d/{production,default}.conf`; `deploy/docker-compose.yml`; `backend/Dockerfile.production`; `.github/workflows/{ci,deploy-vps}.yml`; `frontend/src/lib/{config,pdfUtils,format}.ts`. All exist and match the cited content."

- `spec-cross-review.md` L128 (`§5 Uncertainties`, item 3) — [UNCERTAINTY] boundary of that standard:
  > "3. **Unread legacy internals:** arch Appendix B claims about `Dockerfile.production` healthcheck and `production.conf` rate-zone details were verified for existence but not re-audited line-by-line; the existing audits corroborate the compress/cleanup/r2 specifics cited."

### 7.3 Status summary

- No file defines a formal rendered-visual checklist with screenshot expectations; the shared standard is: static source-derived claims + browser spot-check during rebuild validation (U7), a color-contrast tool pass for Doc19 §8.4, and a screen-reader pass for dnd-kit interactions.
- The closest to an executable checklist is the union of `ui-home-shell-audit.md` §11 (preserve) / §12 (defects) and `ui-five-tools-audit.md` §5 (preserve) / §6 (correct), extracted in Section 8 below.

---

## 8. DEC-143 VISUAL BASELINE

### 8.1 The decision linkage

- `spec-cross-review.md` L110 (`§4 Verified-Clean Areas`) — [CONFIRMED]:
  > "- **Source precedence:** UX §4 (lines 65-75) and arch §1.4 (lines 70-80) are internally coherent and mutually reconcilable via DEC-143 (binding visual/UX baseline) versus DEC-001/DEC-059 (architecture must be re-justified). No conflict."

- `spec-cross-review.md` L112 (`§4 Verified-Clean Areas`) — [CONFIRMED] the audits ARE the DEC-143 baseline evidence:
  > "**DEC-143 visual preservation:** Token table, typography, spacing/radius/shadow/motion, component character, D1-D13 corrections, and approved-change limits (UX §10, §20.2) match the home-shell and five-tools audits exactly (verified against `globals.css:3-10`, `page.tsx:486-593`, `Navbar.tsx:145-146`, `compress/page.tsx:94-135`). No invented tokens or visual claims."

- `ui-docs-code-reconciliation.md` L266 (`§6 Conflicts with Accepted Rebuild Decisions`) — [CONFIRMED]:
  > "| DEC-028 (evolve visual identity, baseline) | The reconciliation confirms the documented tokens are pixel-accurate in code — a low-risk baseline to retain; the catalog/nav drift (§3.2/3.3) is exactly the "correct what is stale" work DEC-028 anticipates. |"

- `ui-docs-code-reconciliation.md` L16-17 (executive summary items 1-2) — [CONFIRMED] overall verdict:
  > "1. **Design token layer is highly accurate.** Every color token, font setting, spacing token, radius, shadow, and animation keyframe documented in both docs matches `globals.css` and the components exactly. This is the strongest, safest material for the future canonical spec."
  > "2. **Component specifications are largely accurate.** PDFUploader, PageRangeInput, PrivacyNotice, accordion, sortable merge/image items, rotate grid, and the done/error/processing state cards match their documented classes nearly to the pixel."

### 8.2 Color system (tokens to preserve)

- `ui-home-shell-audit.md` L41-48 (`§3.1 tokens`) — [CONFIRMED] full token table:
  > "| Token | Value | Usage observed |
  > | --- | --- | --- |
  > | --color-navy | #1e3a5f | Brand/heading color: h1 (page.tsx:497,540,574), card titles, logo lockup, primary CTA background (page.tsx:512), tool-page h1s (compress/page.tsx:100-101) |
  > | --color-accent | #2563eb | Interactive accent: nav CTA (Navbar.tsx:209), links/active states (Navbar.tsx:191), eyebrows, icon tiles (page.tsx:582), hero accent span (page.tsx:500) |
  > | --color-bg | #f9fafb | Page background: body (globals.css:13), navbar glass (Navbar.tsx:145), footer (Footer.tsx:169), home wrapper (page.tsx:486) |
  > | --color-background | #ffffff | **Never used** (dead token; no bg-background/text-background anywhere in src - grep) |
  > | --color-foreground | #171717 | Body text color via var(--color-foreground) (globals.css:14) |
  > | --font-sans | 'DM Sans', system-ui, sans-serif | Body font; font-sans utility on body (layout.tsx:50) |"

- `ui-home-shell-audit.md` L50 (`§3.1`) — [CONFIRMED]:
  > "The palette additionally leans on Tailwind default slate-* (borders slate-200, secondary text slate-500, tertiary slate-400/300, fills slate-100) and rose-200/rose-50 for error states on tool pages. All 13 tool pages and shared components (PDFUploader, OtherTools) use the same navy/accent/slate language - the token system is applied consistently app-wide."

- `ui-docs-code-reconciliation.md` L282 (`§7.1`) — [RECOMMENDATION]:
  > "- All five color tokens and the slate/semantic/accent-tint usage tables (Doc19 §2.2; Doc32 §4.1-4.2)."

- `ui-docs-code-reconciliation.md` L205 (`§4.2 Stale`) — [CONFIRMED] semantic colors are now de-facto standardized:
  > "| §4.3 L254-258 semantic colors "Green (to be defined) / Red (to be defined) / Amber (to be defined)" + note "gunakan Tailwind default (green-600, red-600, amber-600)" | The codebase has standardized since: emerald-500 success circles, rose-50/rose-200/rose-500 error cards, no amber warning UI exists | `PDFUploader.tsx:454,517-524`; `merge:489,537`; `rotate:576,603` |"

- `ui-docs-code-reconciliation.md` L306 (`§7.2`) — [RECOMMENDATION]:
  > "- **Semantic colors**: officialize emerald success / rose error / amber (future) with exact tokens."

### 8.3 Typography scale (to preserve)

- `ui-home-shell-audit.md` L55 (`§3.2`) — [CONFIRMED]:
  > "- **Scale:** Hero h1 text-[clamp(40px,6vw,72px)] semibold tracking-[-2px] (page.tsx:497); section h2 32px (page.tsx:540) and 28px (page.tsx:574); card titles 15px semibold; descriptions 13.5px; nav labels 12px (md) / 14px (lg) (Navbar.tsx:171); eyebrow 12px uppercase tracking-widest (page.tsx:537-539, OtherTools.tsx:52-53); footer links 13-14px; tool-page h1 30px/36px (compress/page.tsx:100)."

- `ui-docs-code-reconciliation.md` L283 (`§7.1`) — [RECOMMENDATION]:
  > "- Typography: DM Sans, `--font-dm-sans`, fallback, antialiased, latin subsets, and the full type scale with tracking/leading rules (Doc19 §2.1; Doc32 §5)."

### 8.4 Spacing, radius, shadow system (to preserve)

- `ui-home-shell-audit.md` L60-63 (`§3.3`) — [CONFIRMED]:
  > "- **Content column:** max-w-[1200px] px-6 for home sections (page.tsx:488,535,569) and footer (Footer.tsx:171,198). Navbar uses max-w-[1440px] (Navbar.tsx:146) - inconsistent (D3).
  > - **Section rhythm:** hero pt-24 pb-20 (page.tsx:488); tools grid py-20 (page.tsx:535); privacy py-[72px] (page.tsx:569); footer tools py-12 (Footer.tsx:171); footer bottom bar py-10 (Footer.tsx:198).
  > - **Radii:** cards 10px (page.tsx:550); icon tiles 10px (page.tsx:552); tool-page hero tile 16px rounded-2xl (compress/page.tsx:97); nav CTA 8px; pills fully rounded (page.tsx:490); footer logo 5px (Footer.tsx:202).
  > - **Shadows:** resting 0_1px_3px_rgba(0,0,0,0.04); hover 0_4px_20px_rgba(37,99,235,0.1) accent-tinted (page.tsx:550); dropdowns shadow-lg (Navbar.tsx:184, Footer.tsx:90)."

- `ui-home-shell-audit.md` L64 (`§3.3`) — [CONFIRMED]:
  > "- **Card pattern:** white, border-slate-200, hover -translate-y-0.5 + border-accent/60 (page.tsx:550; also nav CTA hover lift Navbar.tsx:209)."

- `ui-docs-code-reconciliation.md` L284 (`§7.1`) — [RECOMMENDATION]:
  > "- Spacing scale, radii, and shadow system incl. the three custom accent shadows (Doc19 §2.3-2.5; Doc32 §6.3, §7.1)."

### 8.5 Component inventory (to preserve)

- `ui-home-shell-audit.md` L141-151 (`§11 Strengths`) — [CONFIRMED] the shell-level inventory:
  > "1. **Frosted sticky navbar** (bg-bg/92 backdrop-blur-md, 52px, border-b) - distinctive and correctly layered (Navbar.tsx:145-146).
  > 2. **Dropdown interaction model** - hover + click open, outside-click close, route-change close, exact-route active state, CTA always visible in both breakpoints (Navbar.tsx:128-142,168-176,189-193,215-222).
  > 3. **Native details mobile accordion** - accessible, dependency-free, no JS state needed for open/close (Navbar.tsx:238-259).
  > 4. **Sticky-footer flex shell** - html h-full / body min-h-full flex-col / main flex-1 (layout.tsx:49-53).
  > 5. **Cohesive token system** - navy #1e3a5f + accent #2563eb + off-white #f9fafb applied consistently across all 13 tool pages, shared components, and the homepage.
  > 6. **Fluid hero type** via clamp(40px,6vw,72px) + 1200px content column with px-6 gutters.
  > 7. **Motion discipline** - 0.3s fade-up, shimmer processing state, chevron rotations; subtle and consistent on tool pages.
  > 8. **Credibility system** - pill "Gratis · Tanpa akun · Auto-hapus", trust badges, privacy section, FAQ, and footer all state the same guarantees (no account, HTTPS, 1-hour auto-delete).
  > 9. **Exported data contracts** - TOOLS / NAV_CATEGORIES / FOOTER_TOOL_CATEGORIES are exported and locked by tests; the rebuild should keep equivalent exported constants and their tests.
  > 10. **SEO baseline** - lang="id", title template, metadataBase, per-page metadata on privacy, all 14 OG images present in public/og/, sitemap with priorities.
  > 11. **Consistent tool-page shell** - icon tile + navy h1 + slate copy + eyebrow + OtherTools section across all 13 tools."

- `ui-five-tools-audit.md` L45-63 (`§2 Shared Design System Baseline`) — [CONFIRMED] the five-tool component inventory:
  > "- **Tokens** (`globals.css:3-10`): `--color-navy: #1e3a5f`, `--color-accent: #2563eb`, `--color-bg: #f9fafb`. Font: DM Sans (`app/layout.tsx:9-14`), `<html lang="id">` (`app/layout.tsx:49`).
  > - **Animations** (`globals.css:19-44`): `animate-shimmer` (1.4s infinite gradient sweep) used for indeterminate processing bars; `animate-fade-up` (0.3s, translateY(10px)) used for every state-transition card. All state cards animate in — consistent across all five tools.
  > - **Page shell**: `mx-auto w-full max-w-xl px-4 py-8 sm:py-12` (identical on all five pages).
  > - **Tool header pattern** (identical structure on all five pages): 1. 64px rounded-2xl accent icon tile (`h-16 w-16 rounded-2xl bg-accent/10 text-accent`), 2. `h1` `text-3xl font-bold tracking-tight text-navy md:text-4xl`, 3. one-line subtitle `text-base text-slate-500`, 4. context paragraph `mt-2 text-sm text-slate-400 max-w-md` with a real-world use case (WhatsApp, KTP, lamaran kerja, media sosial).
  > - **Feature badges**: 3-card grid `grid-cols-1 gap-4 md:grid-cols-3`, each `rounded-2xl bg-white p-5 border border-slate-100 shadow-sm`, icon + `h3 text-sm font-semibold text-navy`.
  > - **Dropzone pattern** (identical classes everywhere): `rounded-2xl border-2 border-dashed bg-white px-5 py-14 text-center transition-all`, `border-slate-300 hover:border-accent/50`, drag-over → `border-accent bg-accent/5`; 56px accent icon tile; `text-base font-semibold tracking-tight text-navy` CTA line; `text-xs text-slate-400` constraints line; hidden `<input type="file">`; the dropzone is a `<div role="button" tabIndex={0}>` with Enter/Space keydown handlers (e.g., `merge/page.tsx:561-566`).
  > - **Processing card**: `rounded-2xl border border-slate-200 bg-white p-6` with status line, 6px shimmer bar (`h-1.5 rounded-full bg-slate-100` + `animate-shimmer`), optional footnote.
  > - **Done card**: `rounded-2xl border border-accent/20 bg-white p-6 shadow-[0_4px_20px_rgba(37,99,235,0.06)]`; 40px emerald-500 circle with white check; title + metadata line; full-width accent download CTA (`rounded-xl bg-accent px-5 py-4 text-base font-semibold text-white shadow-[0_2px_12px_rgba(37,99,235,0.25)] hover:bg-accent/90`); secondary outline reset CTA (`rounded-xl border border-slate-200 bg-transparent px-5 py-3 text-sm font-medium text-slate-500 hover:bg-slate-50`).
  > - **Error card**: `rounded-2xl border border-rose-200 bg-rose-50/50 p-6`; rose alert icon + "Terjadi Kesalahan" header; message; full-width accent "Coba Lagi" button.
  > - **PrivacyNotice**: always visible on all five pages, `mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-500 border border-slate-100`, shield icon + one of three model strings (`PrivacyNotice.tsx:28-33`).
  > - **OtherTools**: `mt-16 border-t border-slate-200` section, h2 "Alat lainnya" (uppercase tracking-widest accent), 2-column link grid of the other 12 tools (`OtherTools.tsx:25-66`)."

- `ui-five-tools-audit.md` L248-260 (`§5 Preserve`) — [RECOMMENDATION] (the preserve list IS the baseline inventory):
  > "1. **Page shell + header anatomy** — max-w-xl container, icon tile, H1, subtitle, context paragraph with an Indonesia-specific use case. Consistent across all five and the strongest part of the design.
  > 2. **State-card language** — done (accent border + emerald check), processing (shimmer), error (rose) cards with `animate-fade-up`; identical classes.
  > 3. **Dropzone interaction contract** — dashed border, drag-over highlight, `role="button"` + tabIndex + Enter/Space, hidden input, 20MB constraint line.
  > 4. **PrivacyNotice always visible** with accurate per-model copy (server/client/hybrid) — including pdf-to-image's "Auto-hapus 1 jam" promise which matches backend retention (signed URL 3600s, `config.ts:31-33`).
  > 5. **PageRangeInput UX** — labeled input, placeholder example, inline parse errors, live selected-pages preview, quick-select chips (First/Last/All). Parser errors are specific and localized (out-of-bounds, start>end, bad token).
  > 6. **Merge/image-to-pdf sortable lists** — pointer + keyboard sensors with 5px activation distance, order badges, per-item remove with aria-label.
  > 7. **image-to-pdf magic-bytes validation** — best-in-class file validation; worth extending to the PDF tools (PDF header `%PDF` check) in the rebuild.
  > 8. **Compress before/after size panel** with saved-percentage pill — the clearest result feedback; good template for other result cards.
  > 9. **Analytics discipline** — task_started/completed/failed with tool names and failure reasons, device category.
  > 10. **Per-tool metadata layouts** with localized titles and per-tool OG images.
  > 11. **Client-side privacy framing in processing footnotes** — accurate and reassuring ("file tidak dikirim ke server")."

- `ui-docs-code-reconciliation.md` L287 (`§7.1`) — [RECOMMENDATION] component-level preserve list:
  > "- Component specs: upload zone, feature badge card, sortable file/image items, accordion, rotate page grid, PageRangeInput, PrivacyNotice (classes + three messages), done/error/processing cards, FAQ page, Privacy page (Doc19 §3.4-3.12, §6.4-6.6, §9.9-9.10)."

### 8.6 Approved-change limits (what the baseline permits changing)

- `ui-docs-code-reconciliation.md` L307 (`§7.2`) — [RECOMMENDATION]:
  > "- **Button taxonomy**: two documented conventions — navy hero CTA and accent tool-page primary actions — with exact padding values (px-8 py-3.5; px-4 py-2 navbar; px-3.5 py-1.5 mobile)."

- `ui-docs-code-reconciliation.md` L293-303 (`§7.2`) — [RECOMMENDATION] the "correct what is stale" scope:
  > "- **Catalog and routes**: 13 tools with per-tool privacy models (server: compress, pdf-to-image, protect, unlock, ocr, pdf-to-word, pdf-to-excel; client: merge, split, rotate, sign; hybrid: image-to-pdf, watermark), per-tool processing mode (browser/server/hybrid), and per-tool limits.
  > - **Navbar spec**: 4-category dropdown architecture, 1440px container, hover+click behavior, outside-click close, mobile `<details>` accordion, active states.
  > - **Footer spec**: tools directory section, bottom bar, language switcher, and a dead-link policy (resolve Syarat/Kontak).
  > - **Landing spec**: 13-card grid, hero, privacy pillars; keep the exact card classes.
  > - **OtherTools spec**: 12 cards, grid-cols-2, heading.
  > - **Server-flow taxonomy**: which tools use XHR-with-progress (compress only) vs fetch-without-progress, and the disclosure copy patterns.
  > - **Loading taxonomy**: add the spinner variant (rotate) or standardize on shimmer; document the 1.2s deviation decision.
  > - **Error/done consistency**: absorb rotate's and sign's variants into explicit specs (or standardize them).
  > - **Compress quality**: document the automatic-mode decision (DEC-014) and the ebook preset reality.
  > - **New component specs**: PasswordInput, signature suite, watermark suite, PDFPageViewer.
  > - **Analytics and SEO**: event schema, sitemap/robots/OG-image conventions, per-tool metadata patterns."

- `spec-corrections-report.md` L22-27 (`§1`, DEC-187) — [CONFIRMED] one owner-confirmed baseline change already recorded (accepted formats):
  > "### DEC-187 — JPG-to-PDF officially accepts JPG, JPEG, PNG, and WebP at launch
  > - Status: Accepted.
  > - Content: JPG/JPEG, PNG, and WebP accepted at launch; user-facing name remains "JPG to PDF"; validation by actual bytes and DEC-093 safety controls; DEC-088 threat blocking applies; copy/FAQ/legal disclosures state actual formats."

### 8.7 Status summary

- DEC-143 (binding visual/UX baseline) is verified against the audits: token table, typography, spacing/radius/shadow/motion, component character, and D1-D13 co
orrections all match `globals.css:3-10`, `page.tsx:486-593`, `Navbar.tsx:145-146`, `compress/page.tsx:94-135`. No invented tokens or visual claims were found.
- Preserve inventory: 5 color tokens + slate/semantic/accent tints, DM Sans type scale, spacing/radius/three-accent-shadow system, fade-up/shimmer motion, inline-SVG iconography, page-shell + header anatomy, dropzone contract, feature badges, processing/done/error state cards, PrivacyNotice (3 models), PageRangeInput, sortable lists, before/after panel, per-tool metadata, exported data contracts (TOOLS / NAV_CATEGORIES / FOOTER_TOOL_CATEGORIES).

---

## 9. OTHER FINDINGS — accessibility, i18n, SEO

### 9.1 Accessibility

#### 9.1.1 Shell-level (navbar/footer/homepage)

- `ui-home-shell-audit.md` L162 (`§12 Defects, D8`) — [CONFIRMED]/[RECOMMENDATION]:
  > "**D8 Accessibility gaps:** no skip-to-content link / no main id; no aria-expanded on hamburger (Navbar.tsx:223-229) or category buttons (Navbar.tsx:168-176); no focus-visible styling; dropdowns and language switcher don't close on Escape."

- `ui-home-shell-audit.md` L127 (`§9 Navigation Interactions`) — [CONFIRMED]:
  > "- **Keyboard gaps:** no Escape-to-close on dropdowns/switcher; no aria-expanded on hamburger or category buttons; no custom focus-visible styling; no skip link (D8)."

- `ui-home-shell-audit.md` L143 (`§11 Strengths`, item 3) — [CONFIRMED] what IS accessible:
  > "3. **Native details mobile accordion** - accessible, dependency-free, no JS state needed for open/close (Navbar.tsx:238-259)."

- `ui-home-shell-audit.md` L163 (`§12 Defects, D9`) — [CONFIRMED]/[RECOMMENDATION]:
  > "**D9 Language switcher semantics:** the English row is an inert div styled like a menu item (Footer.tsx:106-111) - give it a disabled-button/aria-disabled treatment; flag emoji characters render as letter pairs on some platforms (Windows) - consider SVG/text labels."

- `ui-home-shell-audit.md` L83 (`§4 Layout Shell`) — [CONFIRMED]:
  > "Navbar is sticky top-0 so it stays visible on scroll; no main id and no skip-to-content link exist (D8)."

#### 9.1.2 Tool-page level (all five tools)

- `ui-five-tools-audit.md` L98 (`§3.1 Compress`, A11y) — [CONFIRMED]:
  > "**A11y semantics**: dropzone `role="button"` + Enter/Space (:356-371); no `aria-live`/`role="status"` on progress or result; progress bar has no `role="progressbar"`/`aria-valuenow`; error card has no `role="alert"`."

- `ui-five-tools-audit.md` L156 (`§3.3 Split`, PageRangeInput A11y) — [CONFIRMED]:
  > "**A11y gap**: input has label + helper, but error text and live preview are plain `<p>` with no `aria-live`/`aria-invalid`/`aria-describedby` wiring."

- `ui-five-tools-audit.md` L188 (`§3.4 Image-to-PDF`, A11y) — [CONFIRMED]:
  > "**A11y gaps (worst of the five)**: remove button and drag handle are `opacity-0` revealed only on `group-hover` (:320-337) — invisible on touch devices and for keyboard users; a focused-but-not-hovered control stays invisible (no `focus-visible` fallback). Drag handle has no aria-label. No live-region announcements."

- `ui-five-tools-audit.md` L210 (`§3.5 PDF-to-Image`, A11y) — [CONFIRMED]:
  > "**A11y**: same gaps as Split (no live regions on PageRangeInput; no progressbar role; drag N/A here — single file only)."

- `ui-five-tools-audit.md` L241-242 (`§4 Cross-Tool Consistency Matrix`) — [CONFIRMED]:
  > "| aria-live / role=status / progressbar semantics | none | none | none | none | none |
  > | Heading structure | h1 → h3 badges (no h2) | h1 → h3 badges | h1 → h3 badges | h1 → h3 badges | h1 → h3 badges |"

- `ui-five-tools-audit.md` L270 (`§6 Correct`, item 7) — [RECOMMENDATION]:
  > "7. **Accessibility semantics** — add to all five: `role="status"`/`aria-live="polite"` on processing and done transitions, `role="alert"` on error cards, `role="progressbar"` + `aria-valuenow` on the determinate upload bar, `aria-invalid`/`aria-describedby` wiring in PageRangeInput (error + live preview), and `aria-label` on drag handles ("Ubah urutan <name>"). Consider dnd-kit `announcements` for keyboard reorder feedback."

- `ui-five-tools-audit.md` L271 (`§6 Correct`, item 8) — [RECOMMENDATION]:
  > "8. **Heading hierarchy** — feature-badge cards use `h3` directly under `h1` (no h2). Either demote badges to plain text with `font-semibold` or insert a visually-hidden h2."

- `ui-five-tools-audit.md` L269 (`§6 Correct`, item 6) — [RECOMMENDATION]:
  > "6. **Hover-only controls in image-to-pdf grid** — remove button + drag handle are `opacity-0 group-hover:opacity-100` with no `focus-visible` fallback; invisible on touch/keyboard. Make them always visible (at reduced opacity) or `focus-visible:opacity-100`."

#### 9.1.3 Keyboard-nav coverage (docs claim vs code)

- `ui-docs-code-reconciliation.md` L105 (`§3.1 Accurate` row for Doc19 §8.2) — [CONFIRMED]:
  > "| §8.2 keyboard nav (upload zone tabIndex + Enter/Space) | `PDFUploader.tsx:357-362`; `merge:561-566`; `split:509-514`; `image-to-pdf:650-655`; `pdf-to-image:519-524`; `protect:354`, `unlock:334`, `sign:370`, `ocr:417`, `pdf-to-word:372`, `pdf-to-excel:388` — **exception: rotate** (see §3.3) |"

- `ui-docs-code-reconciliation.md` L139 (`§3.3 Contradicted`) — [CONFIRMED]:
  > "| §8.2 L925 upload zone keyboard pattern (`tabIndex={0}`, `onKeyDown`) | Rotate upload zone has neither role, tabIndex, nor keydown handler | `rotate/page.tsx:428-432` (only onClick/onDrop/onDragOver) — §9.8 documents this page, making the doc self-inconsistent |"

- `ui-docs-code-reconciliation.md` L106 (`§3.1 Accurate` row for Doc19 §8.3) — [CONFIRMED]:
  > "| §8.3 screen reader labels, lang, metadata titles | "Buka menu"/"Tutup menu" `Navbar:226`; "Hapus {filename}" `merge:324`, `image-to-pdf:324`; "Hapus file" `split:472`, `pdf-to-image:482`, `rotate:480`; `lang="id"` `layout:49`; per-tool metadata in all 13 `layout.tsx` files (e.g., `compress/layout.tsx:4`) |"

- `ui-docs-code-reconciliation.md` L304 (`§7.2`) — [RECOMMENDATION] (a11y roadmap carried from the docs):
  > "- **Accessibility roadmap** (still valid from Doc19 §8.5/§10.3): skip link, aria-live regions, `role="progressbar"`, focus-visible rings (only the sign overlay has one today), prefers-reduced-motion."

- `ui-docs-code-reconciliation.md` L145 (`§3.4 Missing`, item 2) — [CONFIRMED]:
  > "2. **Components**: `PasswordInput.tsx`, `SignaturePad.tsx`, `SignatureUpload.tsx`, `SignatureType.tsx`, `SignaturePlacementOverlay.tsx` (uses `focus-visible:ring-2` — the only custom focus ring in the app), `WatermarkConfig.tsx`, `WatermarkPreview.tsx`, `PDFPageViewer.tsx` — none specified in Doc19."

### 9.2 i18n / language

- `ui-five-tools-audit.md` L127 (`§3.2 Merge`, Result UX) — [CONFIRMED]:
  > "**Result UX**: Programmatic download via `downloadPDF(mergedData, 'merged.pdf')` (:451-455, `pdfUtils.ts:240-254` creates blob + temp `<a>`). **Filename is hardcoded English `merged.pdf`** — inconsistent with Indonesian copy and with split's generated filename."

- `ui-five-tools-audit.md` L265 (`§6 Correct`, item 2) — [RECOMMENDATION]:
  > "2. **Download filename inconsistency** — `merged.pdf` is hardcoded English; split generates `split_<range>.pdf`; image-to-pdf always `images.pdf`. Standardize: derive a name from the source file(s), e.g. `merged_<first>.pdf`, `gambar_ke_pdf.pdf`, or per-tool Indonesian defaults."

- `ui-five-tools-audit.md` L140 (`§3.3 Split`) — [CONFIRMED]:
  > "Note: uses informal "kamu" — the only tool header doing so."

- `ui-five-tools-audit.md` L197 (`§3.5 PDF-to-Image`) — [CONFIRMED]:
  > "Context "Konversi slide presentasi, sertifikat, atau halaman dokumen jadi gambar untuk di-share di media sosial atau grup WhatsApp." (:377-380) — mixes English "di-share"."

- `ui-five-tools-audit.md` L277 (`§6 Correct`, item 14) — [RECOMMENDATION]:
  > "14. **Informal "kamu" only in split header** (and "di-share" in pdf-to-image) — pick one tone register (recommend keeping the neutral register used by compress/merge/image-to-pdf)."

- `ui-home-shell-audit.md` L195 (`§14 Uncertainties, U4`) — [OWNER QUESTION], unanswered:
  > "**U4: "Segera hadir" English option** - keep visible-but-inert (current) or hide until implemented?"

- `ui-home-shell-audit.md` L103 (`§6 Footer`) — [CONFIRMED]:
  > "- **LanguageSwitcher** (64-116): button with globe icon + "Indonesia" (flag emoji) + chevron (80-87); dropdown absolute bottom-full right-0 mb-2 w-48 rounded-lg border bg-white py-1 shadow-lg - opens **upward** (90); Indonesia row highlighted with check (91-105); English row shows "Segera hadir" badge but is an **inert div styled like an item** (106-111) (D9); outside mousedown closes (68-76); no Escape handling."

- `ui-docs-code-reconciliation.md` L305 (`§7.2`) — [RECOMMENDATION]:
  > "- **i18n**: EN/ES launch posture per DEC-004, locale-prefixed routes per DEC-023, copy-length resilience (current Indonesian context paragraphs are long for English/Spanish in some places)."

- `ui-docs-code-reconciliation.md` L163 (`§3.5 Historical-only`) — [CONFIRMED]:
  > "| §1.5 L104-113 "Indonesia-First" principle | Code is still 100% Indonesian, so the *description* is accurate; the *principle* is superseded by DEC-003/004. |"

- `ui-docs-code-reconciliation.md` L236 (`§4.5 Historical-only`) — [CONFIRMED]:
  > "| §10.1 L731 "Seluruh UI Papyr menggunakan Bahasa Indonesia" + `lang="id"` | True today (`layout.tsx:49`), but contradicts accepted DEC-004 (EN/ES launch) |"

### 9.3 SEO / metadata / links

- `ui-home-shell-audit.md` L84 (`§4 Layout Shell`) — [CONFIRMED]:
  > "Metadata (layout.tsx:16-41): title default "Papyr — Alat PDF Gratis untuk Indonesia" with template "%s | Papyr"; description; metadataBase https://mypapyr.com; OpenGraph locale id_ID, image /og/papyr.png (file exists); Twitter summary_large_image. privacy/page.tsx exports its own metadata; faq/page.tsx is a client component and inherits the defaults."

- `ui-home-shell-audit.md` L150 (`§11 Strengths`, item 10) — [CONFIRMED]:
  > "10. **SEO baseline** - lang="id", title template, metadataBase, per-page metadata on privacy, all 14 OG images present in public/og/, sitemap with priorities."

- `ui-home-shell-audit.md` L135 (`§10 Test Coverage`) — [CONFIRMED]:
  > "- seo-analytics.test.ts: sitemap = 16 URLs (home + 13 tools + faq + privacy) with priorities 1 / 0.8 / 0.5 / 0.3; analytics event taxonomy."

- `ui-docs-code-reconciliation.md` L149 (`§3.4 Missing`, item 6) — [CONFIRMED]:
  > "6. **SEO infrastructure**: `sitemap.ts`, `robots.ts`, `opengraph-image.tsx`, `twitter-image.tsx`, per-tool metadata (13 layout files) — Doc19 §8.3 mentions metadata titles but no SEO spec."

- `ui-docs-code-reconciliation.md` L126 (`§3.2 Stale`) — [CONFIRMED]:
  > "| §5.5 L705-718 sitemap table (9 routes) | Seven routes are missing; also no /terms or /contact despite footer links | `sitemap.ts:5-19` (13 tools), `:35-46` (faq, privacy); `Footer.tsx:161-162` |"

- `ui-docs-code-reconciliation.md` L152 (`§3.4 Missing`, item 9) — [CONFIRMED]:
  > "9. **Dead footer links**: "Syarat" and "Kontak" are `href="#"` with no routes (`Footer.tsx:161-162`; glob for terms/contact/about/blog → none). Doc19 §5.4 lists them as functional navigation."

- `ui-home-shell-audit.md` L155 (`§12 Defects, D1`) — [CONFIRMED]/[RECOMMENDATION]:
  > "**D1 Dead footer links:** "Syarat" and "Kontak" point to "#" (Footer.tsx:161-162); FOOTER_LINKS has zero test coverage. Remove until real pages exist, or build the pages."

- `ui-docs-code-reconciliation.md` L327 (`§8 Uncertainties`, item 4) — [UNCERTAINTY]:
  > "4. **OG images**: `opengraph-image.tsx` / `twitter-image.tsx` were noted but not inspected in detail (metadata references `/og/papyr.png`; the route handlers generate it at request time)."

- `ui-five-tools-audit.md` L62 (`§2 Shared Design System Baseline`) — [CONFIRMED]:
  > "- **Metadata**: each tool has its own `layout.tsx` with title/description/OG + per-tool OG image (`/og/compress.png`, `/og/merge.png`, `/og/split.png`, `/og/image-to-pdf.png`, `/og/pdf-to-image.png`). All Indonesian."

- `ui-five-tools-audit.md` L259 (`§5 Preserve`, item 10) — [RECOMMENDATION]:
  > "10. **Per-tool metadata layouts** with localized titles and per-tool OG images."

- `ui-docs-code-reconciliation.md` L270 (`§6 Conflicts`) — [CONFIRMED]:
  > "| DEC-045 (Privacy/Terms/Cookies pages) | Footer dead links ("Syarat"/"Kontak") must be resolved; Docs 19/32 give no terms/cookies guidance. |"

### 9.4 Status summary

- Accessibility: baseline gaps are D8 (skip link, aria-expanded, Escape, focus-visible), tool-page live-region/progressbar/alert semantics absent on all five, PageRangeInput error/preview not aria-wired, image-to-pdf hover-only controls, h1→h3 heading jumps, unlabeled drag handles, sign overlay is the only custom focus ring. Keyboard upload-zone pattern holds on 11 of 13 tools (rotate exception).
- i18n: code is 100% Indonesian today; known defects are the English `merged.pdf` filename, mixed register ("kamu", "di-share"), inert English switcher row (U4 open), and the DEC-004 EN/ES supersession.
- SEO: baseline is strong (lang="id", title template, metadataBase, 14 OG images, 16-URL sitemap with priorities, per-tool metadata); defects are the dead Syarat/Kontak links (D1) and the stale 9-route sitemap in Doc19.

---

## 10. VERIFICATION / CORRECTION STATUS OF EACH FILE

### 10.1 `audit-outputs/ui-docs-code-reconciliation.md` (341 lines)

- Status: primary deliverable of its own audit; documents-vs-code claim-by-claim (Doc19 UI/UX spec + Doc32 Brand guidelines vs `papyr-reference/` frontend). Nothing corrected in place; all findings recorded. Lines 5-7 state scope and method; line 10 names `ui-five-tools-audit.md` as the complementary artifact.
- What was confirmed (file's own §9, L336-341):
  > "## 9. Verification Statement
  > - `papyr-reference/` was only read; nothing was modified, formatted, installed, or executed there.
  > - This deliverable was created at `<workspace-root>\audit-outputs\ui-docs-code-reconciliation.md`.
  > - Headings: `# Papyr UI/UX & Brand Documentation vs. Frontend Implementation — Reconciliation Audit`; `## 1. Executive Summary`; `## 2. Files Inspected (Evidence Base)`; `## 3. Claim-by-Claim — docs/19_Papyr_UIUX_Spec_v1.0.md` (3.1 Accurate / current; 3.2 Stale; 3.3 Contradicted; 3.4 Missing; 3.5 Historical-only; 3.6 Doc-internal inconsistencies); `## 4. Claim-by-Claim — docs/32_Papyr_Brand_Guidelines_v1.0.md` (4.1-4.5); `## 5. Implementation Surface Absent from Both Docs`; `## 6. Conflicts with Accepted Rebuild Decisions`; `## 7. Recommendations for the Future Canonical Design Spec` (7.1 Retain; 7.2 Rewrite or extend; 7.3 Mark historical); `## 8. Uncertainties & Unresolved Questions`; `## 9. Verification Statement`."

- Tool deviation note (file L8) — the prior deliverable was written via bash heredoc because the subagent had no Write tool:
  > "**Tool deviation note**: The subagent toolset exposed no Write/Edit tool, so this deliverable file was created with bash heredoc writes (the only file-write shell use; no other shell operations were performed). All other investigation used Read/Glob/Grep per the delegation constraints."

### 10.2 `audit-outputs/ui-five-tools-audit.md` (303 lines)

- Status: primary deliverable of its own audit; page-by-page UX audit of Compress, Merge, Split, Image-to-PDF, PDF-to-Image. Baseline principle (file L7):
  > "**Baseline principle**: Existing UI/UX is the owner-approved baseline; this audit documents it exactly, then lists deviations and preserve/correct recommendations for the rebuild. No redesign proposed."
- Confirmed clean (file L41):
  > "Verification: `papyr-reference/` was only read, never modified. No commands were run inside `papyr-reference/`."
- Closing (file L301-303):
  > "## 9. Chat-Only Summary Is Insufficient
  > Per AGENTS.md, this file is the primary deliverable. The parent agent must read it before using these findings."
- Corrected items list: §6 items 1-16 (the "Correct" list, extracted in Sections 8.6 and 9.x above). Test-coverage gaps: §7 (no unit tests for PDFUploader/PageRangeInput/PrivacyNotice/OtherTools; e2e only for merge/split; no e2e for Compress/Image-to-PDF/PDF-to-Image).

### 10.3 `audit-outputs/ui-home-shell-audit.md` (210 lines)

- Status: primary deliverable of its own audit; global visual system, Navbar, Footer, homepage. Confirmed clean (file L12):
  > "Only read-only inspection was used (Read, Glob, Grep). No files under `papyr-reference/` were modified; no shell/install/build/browser/git operations were performed. Findings are grounded in source code and tests with file:line citations. Anything requiring rendered/browser confirmation is listed under Section 14 (Uncertainties)."
- Defects confirmed: D1-D13 (file §12, L153-167); strengths confirmed: 11 items (file §11, L139-151); owner questions: U1-U7 (file §14, L190-198). Non-goals (file L187):
  > "Non-goals for the rebuild (per owner direction): no redesign, no copy rewrites beyond fixing broken links, no new sections."
- Evidence index (file L200-210) lists the key file:line locations for rebuild verification.

### 10.4 `audit-outputs/spec-cross-review.md` (148 lines)

- Status: primary deliverable of its own review; product/UX vs technical architecture vs decision log vs the three UI audits. Verified-clean areas listed in §4 (L108-122). Final recommendation (file §6, L131-141) — conditional pass:
  > "**Conditional pass (PASS with required corrections).**
  > No blocker findings. One high-severity internal contradiction (H-1, arch §1.3 vs §8) must be corrected before owner approval, and the medium items (M-1 to M-4) should be resolved or explicitly acknowledged — M-3 requires an owner decision. All low items are editorial. Per DEC-183, these contradictions are hereby surfaced rather than silently resolved; none changes the overall design direction, and both specifications are otherwise internally and mutually consistent, fully grounded in DEC-001-185 and the persisted audits, free of benchmark obligations, placeholders, unsupported claims, and implementation authorization."
- Suggested owner actions (file L137-141): approve H-1 wording correction (and optionally log annotation DEC-016/DEC-019); decide M-3 (PDF-to-JPG page-selection order/overlap semantics); acknowledge M-1, M-2, M-4 and the low items.
- Verification statement (file L143-148): `papyr-reference/` only read; neither spec, decision log, AGENTS.md, nor any existing audit-outputs file modified.
- Findings that later became corrections: H-1, M-1, M-2, M-3, M-4, L-1, L-2, L-3, L-4, L-5, L-6.

### 10.5 `audit-outputs/spec-corrections-report.md` (146 lines)

- Status: primary deliverable of the executor subagent applying owner-confirmed decisions and cross-review corrections. Files changed (only these, file L6-9): `papyr-rebuild-decisions.md`, `2026-07-31-papyr-product-ux-design.md`, `2026-07-31-papyr-technical-architecture.md`. Files verified unchanged (file L10):
  > "- **Files verified unchanged:** `papyr-reference/` (read-only git status, porcelain output empty, exit 0), `AGENTS.md`, all other `audit-outputs/` files."
- Owner decisions applied (file §1): DEC-186 (PDF-to-JPG page selection preserves duplicates and requested order) and DEC-187 (JPG-to-PDF officially accepts JPG/JPEG/PNG/WebP); Open decisions section rewritten to resolved-by-DEC-001..187.
- Corrections applied (file §2): H-1 (arch §1.3 non-goal wording, Redis/Telegram), M-1 (superseded DEC-063 citation removed), M-2 (gpt5.6-sol provider documentation gate added, UX §21.21 + arch §25.3.21), M-3 (PDF-to-JPG range semantics resolved per DEC-186), M-4 (progress vocabulary reconciled: canonical stages preparing/uploading/queued/processing/finalizing/ready; UX §13.1 renamed Loading→Preparing, added Finalizing), L-1 (14→13 defect items), L-2 (pre-benchmark wording removed from both specs; residual occurrence only in decision-log DEC-034 history, line 437), L-3 (DEC-046/088/104/110 fragments added), L-4 (arch restatement reduced, canonical homes named), L-5 (JPG-to-PDF formats per DEC-187), L-6 (newsletter deferral recategorized).
- Verification performed (file §4, L112-125): placeholder scan clean; pre-benchmark scan zero in both specs; consistency greps (Telegram, Guinevere, DEC-185 baselines, DEC-063, "14 defect items", "Loading card" gone); list continuity UX §21 items 1-21 and arch §25.3 items 1-21; markdown structure manually checked; LSP diagnostics unavailable (no Markdown LSP server); lint scripts unavailable (no root package.json); `git -C papyr-reference status --porcelain` empty, exit 0.
- Limitations (file §5, L127-131): no authoritative markdownlint pass; appended DEC-186/187 not linter-validated; optional DEC-019 log annotation not executed (append-only policy).
- Verification statement (file §7, L141-146): `papyr-reference/` only read and unchanged; only the three assigned documents modified; AGENTS.md and all other audit-outputs files not modified.

### 10.6 Cross-file verification chain

- All five files were created 2026-07-31 and each asserts `papyr-reference/` was only read. The corrections report re-confirms empty `git status --porcelain` after the spec/decision-log edits (file L125). The current run re-confirmed empty porcelain output, exit 0.

---

## 11. CONFLICTS AND INTER-FILE NOTES

1. **Navbar width — no conflict, convergent.** `ui-home-shell-audit.md` (D3, U2) and `ui-docs-code-reconciliation.md` (§3.3, §4.3) agree the navbar is `max-w-[1440px]` at `Navbar.tsx:146` and that Doc19/Doc32 claim 1200px. The reconciliation's §4.1 row lists "navbar basics" as accurate while §3.3/§4.3 list the width as contradicted — internally consistent: the width was the only navbar claim in error.
2. **fade-up scope — no conflict.** `ui-five-tools-audit.md` L48 says fade-up is used for "every state-transition card" (tool pages) while `ui-home-shell-audit.md` L68 says "Not used on the homepage"; these are different scopes, not contradictory.
3. **Defect count discrepancy (fixed).** `spec-cross-review.md` L-1 (L81-82) flagged the UX spec's "14 defect items D1-D13" as a miscount (13 items); `spec-corrections-report.md` L-1 (L67-70) records the fix to "13 defect items D1-D13".
4. **DEC-186/187 status.** Only `spec-corrections-report.md` records them (appended after DEC-185); the other four files predate them and cannot contradict them. `spec-cross-review.md` L-5 (JPG-to-PDF PNG/WEBP acceptance) is resolved by DEC-187; M-3 (PDF-to-JPG range semantics) is resolved by DEC-186.
5. **Redis/Telegram non-goal.** H-1 (arch §1.3) was corrected in `spec-corrections-report.md`; the decision log still lacks an explicit DEC-019-narrows-DEC-016 annotation (documented limitation, file L131/L135).
6. **"pre-benchmark" residual.** Zero occurrences in both specs after L-2; the sole remaining occurrence is `papyr-rebuild-decisions.md` line 437 inside DEC-034's history, intentionally kept (append-only), with DEC-066 governing.
7. **Residual owner questions (unanswered in all five files):** U2 (navbar width intent), U3 (duplicate /compress CTAs), U4 (English "Segera hadir" option), U5 (homepage entrance animations), D12 direction (panel transitions), five-tools §8.7 (merge error-path auto-clear), five-tools §8.6 (compress `quality=ebook` lock), reconciliation §8 uncertainties (contrast re-measure, favicon binary, OG image internals, backend surface of the 7 new tools, privacy-statement accuracy vs Vercel Analytics, FAQ copy staleness on WEBP).

---

## 12. OUTPUT VERIFICATION

- File exists and is non-empty: `<workspace-root>\audit-outputs\research\track-b\_evidence-ui-audits.md`.
- All 10 required sections present: 1 Navbar width (D3/U2), 2 Duplicate CTA (U3), 3 Homepage entrance animations (U5/D12), 4 Merge error-state edge case, 5 Contrast re-verification method (UX §21.12), 6 @theme inline token emission (UX §21.19), 7 Rendered visual verification standard (UX §21.11), 8 DEC-143 visual baseline, 9 Other a11y/i18n/SEO findings, 10 Verification/correction status per file.
- `git -C <workspace-root>\papyr-reference status --porcelain` returned empty output with exit 0 on 2026-07-31 (run immediately before writing this file). `papyr-reference/` remains unchanged.
- No file other than this deliverable was created, modified, or deleted.
