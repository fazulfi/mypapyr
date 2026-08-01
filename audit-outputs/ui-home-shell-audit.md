# Papyr UI Shell Audit - Global Visual System, Navbar, Footer, Homepage

- **Date:** 2026-07-31
- **Auditor:** subagent (code-grounded, read-only audit)
- **Workspace:** <workspace-root>
- **Legacy source (read-only, unchanged by this audit):** <workspace-root>\papyr-reference
- **Deliverable:** this file, per AGENTS.md mandatory delegated-output persistence rule
- **Stack:** Next.js 16.2.4, React 19.2.4, Tailwind CSS v4 (@tailwindcss/postcss ^4), TypeScript (frontend/package.json:23-51)

## 1. Scope and Method

Audited the global visual system, app shell (root layout), Navbar, Footer, and homepage of the legacy Papyr clone. Only read-only inspection was used (Read, Glob, Grep). No files under `papyr-reference/` were modified; no shell/install/build/browser/git operations were performed. Findings are grounded in source code and tests with file:line citations. Anything requiring rendered/browser confirmation is listed under Section 14 (Uncertainties).

## 2. Files Inspected

Primary:
- `frontend/src/app/globals.css` (45 lines) - design tokens, keyframes, custom utilities
- `frontend/src/app/layout.tsx` (59 lines) - root layout shell, fonts, metadata
- `frontend/src/app/page.tsx` (596 lines) - homepage (hero, tools grid, privacy section)
- `frontend/src/components/Navbar.tsx` (265 lines) - nav with dropdowns + mobile accordion
- `frontend/src/components/Footer.tsx` (229 lines) - footer with language switcher

Tests (directly relevant):
- `frontend/src/__tests__/navbar.test.ts` (123 lines)
- `frontend/src/__tests__/landing-page.test.ts` (115 lines)
- `frontend/src/__tests__/footer.test.ts` (123 lines)
- `frontend/src/__tests__/seo-analytics.test.ts` (126 lines)
- `frontend/e2e/smoke.spec.ts` (32 lines)

Supporting:
- `frontend/src/components/OtherTools.tsx` (69 lines) - shared "Alat lainnya" section on tool pages
- `frontend/src/app/compress/page.tsx` (138 lines) - representative tool page (shell pattern)
- `frontend/src/app/faq/page.tsx`, `frontend/src/app/privacy/page.tsx` - footer destinations
- `frontend/package.json` - framework versions
- `frontend/public/og/papyr.png` + 13 tool OG images - confirmed present (glob)

## 3. Global Visual System

### 3.1 Design tokens (globals.css:3-10, @theme inline)

| Token | Value | Usage observed |
| --- | --- | --- |
| --color-navy | #1e3a5f | Brand/heading color: h1 (page.tsx:497,540,574), card titles, logo lockup, primary CTA background (page.tsx:512), tool-page h1s (compress/page.tsx:100-101) |
| --color-accent | #2563eb | Interactive accent: nav CTA (Navbar.tsx:209), links/active states (Navbar.tsx:191), eyebrows, icon tiles (page.tsx:582), hero accent span (page.tsx:500) |
| --color-bg | #f9fafb | Page background: body (globals.css:13), navbar glass (Navbar.tsx:145), footer (Footer.tsx:169), home wrapper (page.tsx:486) |
| --color-background | #ffffff | **Never used** (dead token; no bg-background/text-background anywhere in src - grep) |
| --color-foreground | #171717 | Body text color via var(--color-foreground) (globals.css:14) |
| --font-sans | 'DM Sans', system-ui, sans-serif | Body font; font-sans utility on body (layout.tsx:50) |

The palette additionally leans on Tailwind default slate-* (borders slate-200, secondary text slate-500, tertiary slate-400/300, fills slate-100) and rose-200/rose-50 for error states on tool pages. All 13 tool pages and shared components (PDFUploader, OtherTools) use the same navy/accent/slate language - the token system is applied consistently app-wide.

### 3.2 Typography

- **Font:** DM Sans via next/font/google (layout.tsx:9-14), preload: true, display: swap. The generated variable --font-dm-sans is applied to <html> (layout.tsx:49) but **no utility references it**: font-sans resolves to --font-sans whose value is the literal string 'DM Sans', system-ui, sans-serif (globals.css:9), which matches the next/font-registered @font-face family name. It works, but the next/font variable is effectively unused (see D4).
- **Scale:** Hero h1 text-[clamp(40px,6vw,72px)] semibold tracking-[-2px] (page.tsx:497); section h2 32px (page.tsx:540) and 28px (page.tsx:574); card titles 15px semibold; descriptions 13.5px; nav labels 12px (md) / 14px (lg) (Navbar.tsx:171); eyebrow 12px uppercase tracking-widest (page.tsx:537-539, OtherTools.tsx:52-53); footer links 13-14px; tool-page h1 30px/36px (compress/page.tsx:100).
- **Color hierarchy:** headings navy; body foreground #171717; secondary slate-500; tertiary slate-400/slate-300; emphasis accent.

### 3.3 Spacing, radius, shadow language

- **Content column:** max-w-[1200px] px-6 for home sections (page.tsx:488,535,569) and footer (Footer.tsx:171,198). Navbar uses max-w-[1440px] (Navbar.tsx:146) - inconsistent (D3). Tool pages use max-w-xl (compress/page.tsx:94).
- **Section rhythm:** hero pt-24 pb-20 (page.tsx:488); tools grid py-20 (page.tsx:535); privacy py-[72px] (page.tsx:569); footer tools py-12 (Footer.tsx:171); footer bottom bar py-10 (Footer.tsx:198).
- **Radii:** cards 10px (page.tsx:550); icon tiles 10px (page.tsx:552); tool-page hero tile 16px rounded-2xl (compress/page.tsx:97); nav CTA 8px; pills fully rounded (page.tsx:490); footer logo 5px (Footer.tsx:202).
- **Shadows:** resting 0_1px_3px_rgba(0,0,0,0.04); hover 0_4px_20px_rgba(37,99,235,0.1) accent-tinted (page.tsx:550); dropdowns shadow-lg (Navbar.tsx:184, Footer.tsx:90).
- **Card pattern:** white, border-slate-200, hover -translate-y-0.5 + border-accent/60 (page.tsx:550; also nav CTA hover lift Navbar.tsx:209).

### 3.4 Motion

- fade-up 0.3s (globals.css:28-37, utility at 43-45): used across all tool pages and PDFUploader (63 matches in 12 files; e.g., split/page.tsx:375, ocr/page.tsx:403). **Not used on the homepage** (U5).
- shimmer 1.4s (globals.css:19-26, utility at 39-41): processing indicator on tool pages (e.g., split/page.tsx:415, merge/page.tsx:527).
- Chevron rotation transition-transform (Navbar.tsx:178); FAQ chevron duration-200 (faq/page.tsx:18).
- Hover lift via transition-all on CTAs and cards.
- Dropdown panels and the mobile menu open/close **instantly** (no transition) - see D12.

### 3.5 Shared shell patterns beyond the homepage

All tool pages follow one shell: mx-auto w-full max-w-xl px-4 py-8 sm:py-12 (compress/page.tsx:94), icon tile h-16 w-16 rounded-2xl bg-accent/10 text-accent (compress/page.tsx:97), navy h1, slate-500 copy, animate-fade-up stages, OtherTools footer section with border-t border-slate-200 (OtherTools.tsx:51). The "eyebrow" pattern (12px uppercase tracking-widest accent) is shared by homepage and OtherTools.

## 4. Layout Shell (layout.tsx)

- <html lang="id" className={dmSans.variable + ' h-full antialiased'}> (layout.tsx:49); <body className="flex min-h-full flex-col font-sans"> (layout.tsx:50).
- Order: <Navbar /> (51) / <main className="flex-1">{children}</main> (52) / <Footer /> (53) / <Analytics /> + <SpeedInsights /> (54-55).
- Sticky-footer pattern is correct: html h-full + body min-h-full flex-col + main flex-1 pushes footer to the viewport bottom on short pages.
- Navbar is sticky top-0 so it stays visible on scroll; no main id and no skip-to-content link exist (D8).
- Metadata (layout.tsx:16-41): title default "Papyr — Alat PDF Gratis untuk Indonesia" with template "%s | Papyr"; description; metadataBase https://mypapyr.com; OpenGraph locale id_ID, image /og/papyr.png (file exists); Twitter summary_large_image. privacy/page.tsx exports its own metadata; faq/page.tsx is a client component and inherits the defaults.

## 5. Navbar (Navbar.tsx)

- Client component. Sticky bar: sticky top-0 z-50 border-b border-slate-200 bg-bg/92 backdrop-blur-md (145) - frosted-glass treatment at 92% opacity.
- Container: mx-auto flex h-[52px] max-w-[1440px] items-center gap-4 px-6 (146) - fixed 52px height.
- **Logo** (148-160): 28px navy tile (h-7 w-7 rounded-md bg-navy) with white FileIcon + wordmark "Papyr" 17px semibold navy; click also resets all menus.
- **Desktop nav (>= md)** (163-204): hidden md:flex min-w-0 flex-1 items-center justify-center gap-1; 4 category buttons (Alat Dasar, Keamanan, Enhancement, Konversi) from exported NAV_CATEGORIES (83-117; 13 tools total: 4+2+2+5). Button styling: text-xs with px-2.5 below lg, text-sm with px-3 at lg+ (171); open state bg-slate-100 text-slate-900; chevron rotates 180deg.
- **Dropdown panel** (183-200): absolute left-0 top-full z-50 mt-1 w-56 rounded-lg border border-slate-200 bg-white py-2 shadow-lg; links px-4 py-2 text-sm; active tool (pathname === tool.href exact match) gets bg-accent/10 text-accent font-medium (190-193); click closes.
- **Open/close triggers** (128-142): onMouseEnter + onClick toggle on buttons; outside mousedown closes (128-136); route change closes both dropdown and mobile menu (139-142); link/logo/CTA clicks close.
- **Desktop CTA** (207-212): "Coba Gratis" -> /compress, bg-accent rounded-lg px-4 py-2 text-sm text-white shadow-sm, hover lift.
- **Mobile (< md)** (215-230): compact "Coba Gratis" CTA (px-3.5 py-1.5 text-[13px]) + hamburger button with aria-label switching "Buka menu"/"Tutup menu" (226); no aria-expanded (D8).
- **Mobile panel** (234-262): border-t border-slate-200 bg-white px-6 py-4 md:hidden; native details/summary accordion per category; summary bg-slate-50 rounded-lg px-4 py-3 text-sm font-semibold with marker:content-none; links pl-4 px-4 py-2.5 text-sm with same active treatment; link click closes the whole menu.

## 6. Footer (Footer.tsx)

- Client component (needed by LanguageSwitcher). border-t border-slate-200 bg-bg (169).
- **Tools section** (171-194): max-w-[1200px] px-6 py-12; heading "Alat" 18px navy (173); grid grid-cols-2 gap-8 sm:grid-cols-4 (175); category h3 14px semibold slate-900; links 14px slate-600, hover:text-accent; data from FOOTER_TOOL_CATEGORIES (120-154) - **byte-identical copy of NAV_CATEGORIES** (D2).
- **Bottom bar** (197-225): border-t; flex flex-wrap items-center justify-between gap-6 px-6 py-10; logo lockup 24px tile (h-6 w-6 rounded-[5px]) + 15px wordmark (202-206) - smaller than navbar lockup (D11); hardcoded "© 2026" (207) (D6); links row (211-221) from FOOTER_LINKS (158-163): Privasi -> /privacy (exists), FAQ -> /faq (exists), **Syarat -> "#", Kontak -> "#" (161-162) dead links (D1)**; link style 13px slate-500, hover:text-navy.
- **LanguageSwitcher** (64-116): button with globe icon + "Indonesia" (flag emoji) + chevron (80-87); dropdown absolute bottom-full right-0 mb-2 w-48 rounded-lg border bg-white py-1 shadow-lg - opens **upward** (90); Indonesia row highlighted with check (91-105); English row shows "Segera hadir" badge but is an **inert div styled like an item** (106-111) (D9); outside mousedown closes (68-76); no Escape handling.

## 7. Homepage (page.tsx)

- Wrapper min-h-screen bg-bg (486) - redundant with body background and the flex shell (D7).
- **Hero** (488-529): centered, pt-24 pb-20. Pill badge border-accent/30 bg-accent/10 with 6px accent dot + "Gratis · Tanpa akun · Auto-hapus" 12px accent (490-495). H1 clamp(40px,6vw,72px) semibold tracking-[-2px] navy with accent span "langsung bekerja." (497-501). Sub copy max-w-[520px] text-lg slate-500 (503-507). Primary CTA "Mulai gratis" -> /compress: bg-navy rounded-[10px] px-8 py-3.5 text-white shadow-md with hover lift (510-515). Trust badges row (518-528): Tanpa akun / Auto-hapus 1 jam / Bisa di HP, 13.5px slate-500, accent icons, flex-wrap justify-center gap-6.
- **Divider** (532): border-t border-slate-200 max-w-[1200px].
- **Tools grid** (535-565): py-20; eyebrow "Semua alat" (537-539); h2 "Semua yang kamu butuhkan untuk PDF" 32px navy (540-542); grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 (545); 13 cards from exported TOOLS (360-452): white, 10px radius, border-slate-200, p-6, subtle shadow, icon tile 40px bg-slate-100 text-slate-500 transitioning to group-hover:bg-accent/15 group-hover:text-accent (552), title 15px navy, desc 13.5px slate-500, "Gunakan alat" affordance 13px slate-400 -> accent (559-561).
- **Privacy section** (568-593): border-y border-slate-200 bg-slate-100; py-[72px]; eyebrow "Privasi utama"; h2 "File kamu tetap milikmu" 28px navy; grid grid-cols-1 gap-8 sm:grid-cols-3 (579); 3 items with 40px bg-accent/15 text-accent tiles + 15px navy title + 14px slate-500 copy (580-590). Copy claims: HTTPS transfer, permanent delete in 60 min, no storage/reading.
- No metadata export (inherits layout defaults); no entrance animations (U5).

## 8. Responsive Behavior

- **Breakpoints used:** sm (640): tools grid 2-col, privacy 3-col, footer 4-col; md (768): desktop nav mode, feature grids 3-col; lg (1024): tools grid 3-col, nav label/px bump. Mobile-first throughout.
- **Navbar:** < md hamburger + compact CTA + native accordion; >= md centered category dropdowns + full CTA. Sticky + frosted at all sizes; mobile panel is solid white.
- **Hero:** fluid clamp(40px,6vw,72px) type; content stacks; trust badges wrap.
- **Footer:** 2-col tool grid -> 4-col at sm; bottom bar flex-wrap so logo/links/switcher stack gracefully.
- **Tool pages:** max-w-xl px-4 py-8 sm:py-12; feature grids grid-cols-1 md:grid-cols-3 (compress/page.tsx:122).
- No horizontal overflow risks identified in the shell files (px-6 on all containers; min-w-0 guard on nav center section Navbar.tsx:163).

## 9. Navigation Interactions

- **Desktop dropdowns:** open on hover OR click; chevron rotates; close on outside mousedown, route change, link click, or re-click. Active tool link highlighted via exact pathname match. Category buttons themselves never indicate "a tool inside is active" (D10).
- **Mobile:** hamburger toggles panel; aria-label flips Buka/Tutup; native details accordion is keyboard-operable out of the box; any link click closes the panel; route change closes it too.
- **Keyboard gaps:** no Escape-to-close on dropdowns/switcher; no aria-expanded on hamburger or category buttons; no custom focus-visible styling; no skip link (D8).
- **Language switcher:** click toggle; opens upward; outside-click close; English option inert (D9).

## 10. Test Coverage

- navbar.test.ts: shape/order/count of NAV_CATEGORIES only (4 categories, 13 tools, unique hrefs, exact memberships). No rendering, no interaction tests.
- footer.test.ts: identical data assertions for FOOTER_TOOL_CATEGORIES. **FOOTER_LINKS is untested** - the dead "#" links (D1) are not caught.
- landing-page.test.ts: TOOLS shape (13 entries, unique ids/hrefs, valid React icon elements), exact order contract documented as "existing 6 first, then 7 new" (76-93), id/href asymmetry for img-to-pdf and pdf-to-img (101-114).
- seo-analytics.test.ts: sitemap = 16 URLs (home + 13 tools + faq + privacy) with priorities 1 / 0.8 / 0.5 / 0.3; analytics event taxonomy.
- smoke.spec.ts (Playwright): homepage title matches /Papyr/ and first h1/h2 visible; all 13 tool routes return 200. No interaction assertions.
- No component-rendering (RTL) tests exist for Navbar, Footer, or the homepage anywhere in frontend/src.

## 11. Strengths - the rebuild MUST preserve

1. **Frosted sticky navbar** (bg-bg/92 backdrop-blur-md, 52px, border-b) - distinctive and correctly layered (Navbar.tsx:145-146).
2. **Dropdown interaction model** - hover + click open, outside-click close, route-change close, exact-route active state, CTA always visible in both breakpoints (Navbar.tsx:128-142,168-176,189-193,215-222).
3. **Native details mobile accordion** - accessible, dependency-free, no JS state needed for open/close (Navbar.tsx:238-259).
4. **Sticky-footer flex shell** - html h-full / body min-h-full flex-col / main flex-1 (layout.tsx:49-53).
5. **Cohesive token system** - navy #1e3a5f + accent #2563eb + off-white #f9fafb applied consistently across all 13 tool pages, shared components, and the homepage.
6. **Fluid hero type** via clamp(40px,6vw,72px) + 1200px content column with px-6 gutters.
7. **Motion discipline** - 0.3s fade-up, shimmer processing state, chevron rotations; subtle and consistent on tool pages.
8. **Credibility system** - pill "Gratis · Tanpa akun · Auto-hapus", trust badges, privacy section, FAQ, and footer all state the same guarantees (no account, HTTPS, 1-hour auto-delete).
9. **Exported data contracts** - TOOLS / NAV_CATEGORIES / FOOTER_TOOL_CATEGORIES are exported and locked by tests; the rebuild should keep equivalent exported constants and their tests.
10. **SEO baseline** - lang="id", title template, metadataBase, per-page metadata on privacy, all 14 OG images present in public/og/, sitemap with priorities.
11. **Consistent tool-page shell** - icon tile + navy h1 + slate copy + eyebrow + OtherTools section across all 13 tools.

## 12. Defects - the rebuild should correct

- **D1 Dead footer links:** "Syarat" and "Kontak" point to "#" (Footer.tsx:161-162); FOOTER_LINKS has zero test coverage. Remove until real pages exist, or build the pages.
- **D2 Tool catalog duplicated 4x with divergent labels:** NAV_CATEGORIES (Navbar.tsx:83-117) and FOOTER_TOOL_CATEGORIES (Footer.tsx:120-154) are byte-identical copies; ALL_TOOLS (OtherTools.tsx:25-39) is a third copy with different wording ("Kompres PDF" vs "Kompres", "Tambah Watermark PDF" vs "Watermark", "Tanda Tangani PDF" vs "Tanda Tangan", "Hapus Password PDF" vs "Hapus Password", "OCR PDF" vs "OCR"); TOOLS (page.tsx:360-452) is a fourth (with icons/descriptions). Same tool has 2-3 different names across surfaces. Rebuild: one catalog (id, href, short label, full label, desc, icon) consumed by nav, footer, home grid, and OtherTools.
- **D3 Width inconsistency:** navbar container max-w-[1440px] (Navbar.tsx:146) vs max-w-[1200px] everywhere else (page.tsx:488,532,535,569; Footer.tsx:171,198). On screens >= 1440px the nav CTA and categories sit right of the page content alignment. Pick one width (see U2).
- **D4 Dead tokens:** --color-background: #ffffff (globals.css:7) never used; --font-dm-sans (layout.tsx:10) never consumed by any utility (font-sans uses the literal 'DM Sans' string from --font-sans). Either wire --font-sans: var(--font-dm-sans) (with non-inline @theme) or drop the variable.
- **D5 var() reliance on @theme inline tokens in plain CSS:** globals.css:13-15 use var(--color-bg), var(--color-foreground), var(--font-sans). With Tailwind v4 @theme inline, custom properties may not be emitted to :root, which would silently break body background/color/font-family (see U1). Rebuild should use utilities (bg-bg, text-foreground, font-sans) or a non-inline @theme for any direct var() use.
- **D6 Hardcoded "© 2026"** (Footer.tsx:207) - goes stale; compute the year.
- **D7 Redundant home wrapper:** min-h-screen bg-bg (page.tsx:486) duplicates the body background and the layout min-height shell; it also masks any body-bg failure (U1). No wrapper needed if the shell is correct.
- **D8 Accessibility gaps:** no skip-to-content link / no main id; no aria-expanded on hamburger (Navbar.tsx:223-229) or category buttons (Navbar.tsx:168-176); no focus-visible styling; dropdowns and language switcher don't close on Escape.
- **D9 Language switcher semantics:** the English row is an inert div styled like a menu item (Footer.tsx:106-111) - give it a disabled-button/aria-disabled treatment; flag emoji characters render as letter pairs on some platforms (Windows) - consider SVG/text labels.
- **D10 No active-section indication:** when a tool inside a category is active (e.g., /protect), the "Keamanan" button shows no active state - only the open dropdown link highlights (Navbar.tsx:189-193).
- **D11 Logo lockup mismatch:** nav tile 28px + 17px wordmark (Navbar.tsx:156-159) vs footer tile 24px + 15px wordmark (Footer.tsx:202-206). Rebuild with one lockup component and a size prop.
- **D12 Instant panel appearance:** dropdowns and mobile menu have no transition while chevrons animate (Navbar.tsx:183-200,234-262). Add a short fade/slide to match the motion language, or keep instant deliberately (U5-adjacent).
- **D13 Test blind spots:** nav/footer/home tests assert data shape only; no interaction or render tests; smoke e2e is title + 200s only. Add tests for dropdown open/close, mobile menu, active states, and the language switcher.

## 13. Preserve vs Correct (summary)

| Preserve (strengths) | Correct (defects) |
| --- | --- |
| Frosted sticky 52px navbar | D1 dead "#" links (Syarat, Kontak) |
| Hover+click dropdown model, outside-click & route-change close | D2 single tool catalog (4 copies -> 1) |
| Native details/summary mobile accordion | D3 width parity (1440 vs 1200) |
| Flex min-h-full shell with flex-1 main | D4 dead tokens (--color-background, --font-dm-sans) |
| Navy/accent/slate token palette + 10px card radii + accent-tinted hover shadows | D5 var() on @theme inline tokens in plain CSS |
| clamp() hero type, 1200px content column | D6 hardcoded year |
| fade-up/shimmer motion discipline | D7 redundant min-h-screen bg-bg wrapper |
| Credibility copy (1-hour delete, no account) | D8 skip link, aria-expanded, Escape, focus-visible |
| Exported data contracts + shape tests | D9 language switcher inert row + flag emoji |
| SEO metadata, OG assets, sitemap | D10 category active indication |
| Eyebrow pattern + tool-page shell | D11 logo lockup component with size prop |
| | D12 panel transitions (or deliberate instant) |
| | D13 interaction/render tests |

Non-goals for the rebuild (per owner direction): no redesign, no copy rewrites beyond fixing broken links, no new sections.


## 14. Uncertainties and Unresolved Questions

- **U1 (verify first): @theme inline var() emission.** globals.css uses @theme inline (line 3) but plain CSS body rules reference var(--color-bg), var(--color-foreground), var(--font-sans) (lines 13-15). Whether Tailwind v4 emits these custom properties to :root for an inline theme is version-dependent; the repo contains no compiled CSS artifact (.next output is not present) to confirm. Verification: build and grep the output CSS for --color-bg in a :root block, or inspect body computed background/font in a browser. If the variables are not emitted, body background/font silently fall back (masked on the homepage by the bg-bg wrapper, but font-family would fall back to system-ui site-wide). Rebuild must not carry this ambiguity.
- **U2: Intent of max-w-[1440px] navbar** (Navbar.tsx:146) vs 1200px elsewhere - deliberate breathing room or drift? Needs owner confirmation before unifying (D3).
- **U3: Duplicate CTAs to /compress** - nav "Coba Gratis" + hero "Mulai gratis" both target /compress. Likely deliberate funnel; confirm.
- **U4: "Segera hadir" English option** - keep visible-but-inert (current) or hide until implemented?
- **U5: Homepage has no entrance animations** while every tool page uses animate-fade-up - deliberate calm hero or inconsistency to correct? Affects D12 direction.
- **U6: Exact-match active check** (pathname === tool.href, Navbar.tsx:190) breaks for any future tool with sub-routes (e.g., /compress/result). Currently safe - all 13 tools are single-page.
- **U7: No rendered verification was possible in this audit** (browser tooling out of scope per task constraints); all visual claims are derived from source classes and should be spot-checked in the browser during rebuild validation.

## 15. Evidence Index (key locations)

- Tokens/keyframes/utilities: globals.css:3-16,19-45
- Font loading: layout.tsx:9-14; metadata: layout.tsx:16-41; shell: layout.tsx:49-55
- Nav data: Navbar.tsx:83-117; dropdowns: 163-204; mobile: 215-262; close logic: 128-142
- Footer data: Footer.tsx:120-163; tools section: 169-194; bottom bar: 197-225; language switcher: 64-116
- Home hero: page.tsx:486-529; tools grid: 535-565; privacy: 568-593; TOOLS: 360-452
- OtherTools catalog: OtherTools.tsx:25-39; section: 51-67
- Tool-page shell pattern: compress/page.tsx:94-135
- Tests: navbar.test.ts, footer.test.ts, landing-page.test.ts, seo-analytics.test.ts, e2e/smoke.spec.ts
- Versions: frontend/package.json:23-51
