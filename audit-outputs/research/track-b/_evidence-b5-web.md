# Evidence — B5: UI-Baseline Verification Checklist (Web/Primary Sources)

- **Track / Deliverable**: Track B, Deliverable B5 — UI-baseline verification checklist (contrast re-verification, `@theme inline` token emission, rendered visual verification standard)
- **Evidence file**: `audit-outputs/research/track-b/_evidence-b5-web.md`
- **Primary deliverable**: this file (chat response is a summary only)
- **Access date for all URLs**: 2026-07-31
- **Mode**: read-only, anonymous, no accounts, no authentication, no installs/builds/servers/browser execution
- **Evidence standard**: primary sources first (tailwindcss.com, w3.org/WAI/WCAG22, WAI Understanding pages, playwright.dev, dequeuniversity.com, developer.chrome.com, github.com); secondary sources marked *supporting only*
- **Related evidence**: `_evidence-b1-web.md`, `_evidence-b2-web.md`, `_evidence-b3-web.md`, `_evidence-legacy-frontend.md`, `_evidence-ui-audits.md` (same track-b folder)

## Method (what was fetched)

| # | URL | What it proves | Tool |
|---|-----|----------------|------|
| 1 | https://tailwindcss.com/docs/theme | `@theme`, `@theme inline`, `@theme static`, `:root` emission | jina-reader, full page |
| 2 | https://tailwindcss.com/docs/upgrade-guide | v3→v4 breaking changes; CSS-variable stance; confirms no dedicated `@theme inline` section | jina-reader, full page |
| 3 | https://www.w3.org/TR/WCAG22/ | Normative SC text (1.4.3, 1.4.11), glossary (relative luminance, contrast ratio, large scale), §5 Conformance | jina-reader, 2 pages |
| 4 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | Understanding SC 1.4.3 (thresholds, pt↔px, no rounding) | jina-reader, full page |
| 5 | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | Understanding SC 1.4.11 (3:1, adjacent colors, testing principles) | jina-reader, full page |
| 6 | https://www.w3.org/WAI/WCAG22/Understanding/conformance.html | Understanding Conformance (5 requirements, claims) | jina-reader, full page |
| 7 | https://dequeuniversity.com/rules/axe/4.10/color-contrast | axe-core color-contrast rule: what it checks, reports, documented limits | jina-reader, full page |
| 8 | https://webaim.org/resources/contrastchecker/ | WebAIM Contrast Checker: documented thresholds/usage | jina-reader, full page |
| 9 | https://playwright.dev/docs/api/class-pageassertions | `toHaveScreenshot` API (options, added-in versions) | jina-reader, full page |
| 10 | https://playwright.dev/docs/screenshots | `page.screenshot`, fullPage, buffer, element screenshots | jina-reader, full page |
| 11 | https://playwright.dev/docs/test-snapshots | Visual comparisons: golden files, pixelmatch, maxDiffPixels, stylePath, `--update-snapshots` | jina-reader, full page |
| 12 | https://playwright.dev/docs/emulation | Devices, viewport, colorScheme (evidence-capture inputs) | jina-reader, full page |
| 13 | https://github.com/mapbox/pixelmatch | pixelmatch README (threshold, includeAA, windowSize, return value) | jina-reader, full page |
| 14 | https://www.browserstack.com/docs/percy | Percy product docs (capabilities, snapshots, baselines) | webfetch, markdown |
| 15 | https://www.browserstack.com/docs/percy/overview/visual-testing-basics | Percy visual regression method (capture → compare → review → approve) | webfetch, markdown |
| 16 | https://developer.chrome.com/docs/chromium/new-headless | Chromium headless: unified mode, `--screenshot`, `--window-size`, `--dump-dom`, `--print-to-pdf` | jina-reader, full page |
| 17 | https://api.github.com/repos/tailwindlabs/tailwindcss/releases/latest | Current Tailwind release **v4.3.3** (published 2026-07-16) | webfetch (GitHub API JSON) |

---

## 1. Tailwind CSS v4 theme system: `@theme`, `@theme inline`, `:root` emission

### 1.1 Source and version

- **URL**: https://tailwindcss.com/docs/theme
- **Page title**: "Theme — Tailwind CSS" (docs site is versionless; content documents Tailwind CSS v4.x)
- **Current Tailwind version (verified 2026-07-31)**: **v4.3.3** — https://api.github.com/repos/tailwindlabs/tailwindcss/releases/latest (`tag_name: "v4.3.3"`, `published_at: "2026-07-16T11:55:08Z"`, non-prerelease). The docs' own statements ("Tailwind CSS v4.0 is a new major version", "in v4 you import Tailwind using a regular CSS `@import`") confirm the docs target the v4 line.
- **Access date**: 2026-07-31

### 1.2 What `@theme` is (verbatim)

> "Theme variables are special CSS variables defined using the `@theme` directive that influence which utility classes exist in your project."

> "Tailwind also generates regular CSS variables for your theme variables so you can reference your design tokens in arbitrary values or inline styles"

### 1.3 Why `@theme` instead of `:root` (verbatim)

> "Theme variables aren't _just_ CSS variables — they also instruct Tailwind to create new utility classes that you can use in your HTML."

> "Defining regular CSS variables with `:root` can still be useful in Tailwind projects when you want to define a variable that isn't meant to be connected to a utility class. Use `@theme` when you want a design token to map directly to a utility class, and use `:root` for defining regular CSS variables that shouldn't have corresponding utility classes."

### 1.4 Emission as CSS custom properties in `:root` (verbatim)

Section "Using your theme variables" states:

> "All of your theme variables are turned into regular CSS variables when you compile your CSS:

> ```css
> :root {
>   --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
>   --font-serif: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
>   --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
>   --color-red-50: oklch(0.971 0.013 17.38);
>   /* ... */
> }"

**Implication (documented)**: by default each `--theme-*` variable is emitted as a real CSS custom property on `:root` whose *value is the authored value* (e.g. `--color-mint-500: oklch(0.72 0.11 178)`), and utility classes reference it via `var(--color-mint-500)`.

### 1.5 `@theme inline` — exactly what "inline" means (verbatim)

Section "Referencing other variables":

> "When defining theme variables that reference other variables, use the `inline` option:

> ```css
> @theme inline {
>   --font-sans: var(--font-inter);
> }
> ```

> Using the `inline` option, the utility class will use the theme variable _value_ instead of referencing the actual theme variable:

> ```css
> .font-sans {
>   font-family: var(--font-inter);
> }
> ```

> Without using `inline`, your utility classes might resolve to unexpected values because of how variables are resolved in CSS."

Documented failure mode (verbatim):

> "For example, this text will fall back to `sans-serif` instead of using `Inter` like you might expect:

> ```html
> <div id="parent" style="--font-sans: var(--font-inter, sans-serif);">
>   <div id="child" style="--font-inter: Inter; font-family: var(--font-sans);">
>     This text will use the sans-serif font, not Inter.
>   </div>
> </div>
> ```

> This happens because `var(--font-sans)` is resolved where `--font-sans` is defined _(on `#parent`)_, and `--font-inter` has no value there since it's not defined until deeper in the tree _(on `#child`)_."

**Meaning (documented)**: "inline" changes the *emission strategy* — with `@theme`, utilities (and, per the docs' model, the emitted CSS-variable machinery) reference the token by `var()` indirection; with `@theme inline`, Tailwind inlines the variable's *value expression* into the utility instead of emitting an indirection, so `var(--font-sans)` inside the compiled output becomes `var(--font-inter)` rather than a reference that could resolve at the wrong DOM depth.

### 1.6 Related documented options on the same page

- **`@theme static`** (verbatim): "By default only used CSS variables will be generated in the final CSS output. If you want to always generate all CSS variables, you can use the `static` theme option."
- Namespace table maps `--color-*`, `--font-*`, `--text-*`, `--font-weight-*`, `--breakpoint-*`, etc. to utility/variant APIs (relevant to which tokens the rebuild's baseline must verify per namespace).
- Default theme variables arrive via `@import "./theme.css" layer(theme)` inside `node_modules/tailwindcss/index.css` (`@layer theme, base, components, utilities;`).

### 1.7 Upgrade-guide interaction with CSS variables (Question 6)

- **URL**: https://tailwindcss.com/docs/upgrade-guide
- **Page title**: "Upgrading your Tailwind CSS projects from v3 to v4" (documents v4.0 breaking changes; v4.3.x is current)
- **Finding**: The fetched upgrade guide **does not contain a dedicated `@theme inline` section**. It documents the CSS-variable ecosystem shift instead:
  - Verbatim: "Since v4 includes CSS variables for all of your theme values, we recommend using those variables instead of the `theme()` function whenever possible".
  - Verbatim (prefix example): "The generated CSS variables _will_ include a prefix to avoid conflicts with any existing variables in your project: `:root { --tw-font-display: ...; --tw-breakpoint-3xl: 120rem; ... }`".
  - Verbatim: "We've removed this [resolveConfig] in v4 in hopes that people can use the CSS variables we generate directly instead ... If you need access to a resolved CSS variable value in JS, you can use `getComputedStyle` to get the value of a theme variable on the document root".
- **Net documented guidance**: in v4 the *generated* artifact is CSS custom properties on `:root`; `@theme inline` (documented in the Theme docs, §1.5) is the mechanism for value-level (non-indirect) emission; the upgrade guide does not separately document `inline`. State this gap explicitly rather than inventing content.

---

## 2. WCAG 2.2 contrast standard — exact normative text

### 2.1 Spec source

- **URL**: https://www.w3.org/TR/WCAG22/
- **Page title**: "Web Content Accessibility Guidelines (WCAG) 2.2" — W3C Recommendation; original publication **05 October 2023**; per the spec's own change log, "**2024-12-12: Republished WCAG 2.2**, incorporating the following errata" (the fetched page includes this entry). Access date: 2026-07-31.
- The spec states: "WCAG 2.2 extends Web Content Accessibility Guidelines 2.1 [WCAG21]... Content that conforms to WCAG 2.2 also conforms to WCAG 2.0 and WCAG 2.1."

### 2.2 Relative luminance (glossary definition, verbatim)

> "**relative luminance** — the relative brightness of any point in a colorspace, normalized to 0 for darkest black and 1 for lightest white

> Note 1: For the sRGB colorspace, the relative luminance of a color is defined as L = 0.2126 * **R** + 0.7152 * **G** + 0.0722 * **B** where **R**, **G** and **B** are defined as:
>
> - if RsRGB <= 0.04045 then **R** = RsRGB/12.92 else **R** = ((RsRGB+0.055)/1.055) ^ 2.4
> - if GsRGB <= 0.04045 then **G** = GsRGB/12.92 else **G** = ((GsRGB+0.055)/1.055) ^ 2.4
> - if BsRGB <= 0.04045 then **B** = BsRGB/12.92 else **B** = ((BsRGB+0.055)/1.055) ^ 2.4
>
> and RsRGB, GsRGB, and BsRGB are defined as:
>
> - RsRGB = R8bit/255
> - GsRGB = G8bit/255
> - BsRGB = B8bit/255
>
> The "^" character is the exponentiation operator. (Formula taken from [SRGB].)"

Also (spec Note 2): "Before May 2021 the value of 0.04045 in the definition was different (0.03928)... It has no practical effect on the calculations."

### 2.3 Contrast ratio (glossary definition, verbatim)

> "**contrast ratio** — (L1 + 0.05) / (L2 + 0.05), where
>
> - L1 is the relative luminance of the lighter of the colors, and
> - L2 is the relative luminance of the darker of the colors.
>
> Note 1: Contrast ratios can range from 1 to 21 (commonly written 1:1 to 21:1).
>
> Note 2: Because authors do not have control over user settings as to how text is rendered (for example font smoothing or anti-aliasing), the contrast ratio for text can be evaluated with anti-aliasing turned off.
>
> Note 3: For the purpose of Success Criteria 1.4.3 and 1.4.6, contrast is measured with respect to the specified background over which the text is rendered in normal usage. If no background color is specified, then white is assumed."

### 2.4 SC 1.4.3 Contrast (Minimum) — Level AA (verbatim)

> "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1, except for the following:
>
> - **Large Text**: Large-scale text and images of large-scale text have a contrast ratio of at least 3:1;
> - **Incidental**: Text or images of text that are part of an inactive user interface component, that are pure decoration, that are not visible to anyone, or that are part of a picture that contains significant other visual content, have no contrast requirement.
> - **Logotypes**: Text that is part of a logo or brand name has no contrast requirement."

### 2.5 "Large scale (text)" definition (glossary, verbatim)

> "**large scale (text)** — with at least 18 point or 14 point bold or font size that would yield equivalent size for Chinese, Japanese and Korean (CJK) fonts"

Understanding SC 1.4.3 (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) adds the pixel equivalents:

> "The ratio between sizes in points and CSS pixels is `1pt = 1.333px`, therefore `14pt` and `18pt` are equivalent to approximately `18.5px` and `24px`."

and the no-rounding rule:

> "The 3:1 and 4.5:1 contrast ratios referenced in this success criterion are intended to be treated as threshold values. When comparing the computed contrast ratio to the Success Criterion ratio, the computed values should not be rounded (e.g., 4.499:1 would not meet the 4.5:1 threshold)."

### 2.6 SC 1.4.11 Non-text Contrast — Level AA (verbatim)

> "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s):
>
> - **User Interface Components**: Visual information required to identify user interface components and states, except for inactive components or where the appearance of the component is determined by the user agent and not modified by the author;
> - **Graphical Objects**: Parts of graphics required to understand the content, except when a particular presentation of graphics is essential to the information being conveyed."

Understanding SC 1.4.11 (https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) — key points (paraphrased from fetched text): same 3:1 threshold as large text in 1.4.3; threshold values not rounded ("2.999:1 would not meet the 3:1 threshold"); inactive components exempt; adjacent-colors definition ("the colors adjacent to the component"); focus indicators must contrast with the adjacent background (in combination with 2.4.7); hover effects are not "required to identify" state and do not themselves need 3:1; documented Testing Principles list the high-level process for identifying UI-component indicators and graphical objects and testing least-contrasting areas.

---

## 3. Contrast verification tooling (documented)

### 3.1 axe-core `color-contrast` rule

- **URL**: https://dequeuniversity.com/rules/axe/4.10/color-contrast
- **Page title**: "color-contrast | axe accessibility rules" (Deque University rule documentation for axe-core **4.10**; the current axe-core rule docs line; accessed 2026-07-31)
- **What it checks** (verbatim): "All text elements must have sufficient contrast between text in the foreground and background colors behind it in accordance with WCAG 2 AA contrast ratio thresholds."
- **Thresholds as documented by Deque** (verbatim): "Ensure color contrast of at least 4.5:1 for small text or 3:1 for large text, even if text is part of an image. Large text has been defined in the requirements as 18pt (24 CSS pixels) or 14pt bold (19 CSS pixels). Note: Elements found to have a 1:1 ratio are considered 'incomplete' and require a manual review."
- **How it reports**: rule outcome categories per axe (violations pass/fail/incomplete) — the page documents the analyzer output (Contrast Ratio + Pass/Fail against WCAG AA/AAA for Small Text and "Large Text, UI Components, & Graphical Objects") and lists axe DevTools / axe-core as the analysis tools.
- **Documented limitations** (verbatim):
  - "This rule will not report on text elements that have a `background-image`, are obscured by other elements or are images of text."
  - Foreground transparency/opacity is "more difficult to detect and account for due to: 1:1 colors in foreground and background; CSS background gradients; Background colors in CSS pseudo-elements; Background colors created with CSS borders; Overlap by another element in the foreground...; Elements moved outside the viewport via CSS." (Background transparency/opacity is stated to be "taken into account".)
  - Child elements of disabled buttons are ignored "to avoid a false value".

### 3.2 WebAIM Contrast Checker

- **URL**: https://webaim.org/resources/contrastchecker/
- **Page title**: "WebAIM: Contrast Checker" (accessed 2026-07-31)
- **Documented behavior** (verbatim): "Enter a foreground and background color in RGB hexadecimal format or choose a color using the Color Picker... WCAG 2.0 level AA requires a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text. WCAG 2.1 requires a contrast ratio of at least 3:1 for graphics and user interface components (such as form input borders). WCAG Level AAA requires a contrast ratio of at least 7:1 for normal text and 4.5:1 for large text. Large text is defined as 14 point (typically 18.66px) and bold or larger, or 18 point (typically 24px) or larger." (Note: WebAIM's 18.66px figure for 14pt bold is its own rendering of the pt→px conversion; the W3C Understanding page uses 18.5px for 14pt — flagging this so the checklist cites the normative source.)
- Output shown: Pass/Fail for WCAG AA/AAA across Normal Text / Large Text / "Graphical Objects and User Interface Components"; supports alpha (foreground transparency), eyedropper, and links to WAVE for page-wide analysis.

### 3.3 Programmatic contrast verification (documented methods)

- **axe-core in CI** — the rule docs (3.1) describe axe-core as "an open-source JavaScript accessibility rules library... available as a GitHub repository, browser plugin, or framework integration", i.e. the documented programmatic route for automated contrast checks in a pipeline. (Deque University page, axe-core 4.10.)
- **WCAG formula is directly implementable** — the normative formulas in §2.2/§2.3 are the documented basis for any programmatic checker; the spec notes "Tools are available that automatically do the calculations when testing contrast and flash" (WCAG 2.2 glossary, Note 5 under relative luminance).
- **Manual/UI tooling as re-verification** — WebAIM Contrast Checker (§3.2) is the widely referenced manual checker; WAVE is cited on the same page for page-wide contrast analysis ("WAVE can analyze contrast ratios for all page text elements at once").
- **Documented limits of automation overall**: WCAG 2.2 itself frames testing as "a combination of automated testing and human evaluation" (Understanding Conformance, §5 below); axe documents specific non-reportable cases (background images, obscured text, images of text); Understanding SC 1.4.3 documents that evaluation should use user-agent colors from markup/stylesheets, not on-screen anti-aliased pixels.

---

## 4. Rendered visual verification standard tooling (documented capabilities; no execution performed)

### 4.1 Playwright screenshot assertions (`toHaveScreenshot`)

- **URL**: https://playwright.dev/docs/api/class-pageassertions
- **Page title**: "PageAssertions | Playwright" (API docs; accessed 2026-07-31; the page cites feature versions up to "Added in: v1.62" for `signal`, indicating the current docs track the 1.6x line)
- Verbatim: "This function will wait until two consecutive page screenshots yield the same result, and then compare the last screenshot with the expectation." "Note that screenshot assertions only work with Playwright test runner."
- Documented options (all verbatim from the API page): `animations` ("disabled" default — stops CSS animations/transitions/Web Animations; infinite animations canceled to initial state), `caret` ("hide" default), `clip` (x/y/width/height), `fullPage` ("When true, takes a screenshot of the full scrollable page... Defaults to `false`"), `mask`/`maskColor`, `maxDiffPixelRatio`, `maxDiffPixels`, `omitBackground`, `scale` ("css" default vs "device"), `stylePath` (v1.41+; stylesheet applied during the screenshot for hiding dynamic elements), `threshold` ("perceived color difference in the YIQ color space... Defaults to `0.2`"), `timeout`.
- Formats: `.png` or `.webp` (both "lossless").

### 4.2 Screenshots guide (capture capabilities)

- **URL**: https://playwright.dev/docs/screenshots — page title "Screenshots | Playwright"
- Verbatim: "Full page screenshot is a screenshot of a full scrollable page, as if you had a very tall screen and the page could fit it entirely. `await page.screenshot({ path: 'screenshot.png', fullPage: true });`" Also documents buffer capture ("you can get a buffer with the image and post-process it or pass it to a third party pixel diff facility") and element screenshots (`page.locator('.header').screenshot(...)`).

### 4.3 Visual comparisons (golden-file workflow)

- **URL**: https://playwright.dev/docs/test-snapshots — page title "Visual comparisons | Playwright"
- Verbatim: "Playwright Test includes the ability to produce and visually compare screenshots using `await expect(page).toHaveScreenshot()`. On first execution, Playwright test will generate reference screenshots. Subsequent runs will compare against the reference."
- **Environment determinism warning** (verbatim): "Browser rendering can vary based on the host OS, version, settings, hardware, power source (battery vs. power adapter), headless mode, and other factors. For consistent screenshots, run tests in the same environment where the baseline screenshots were generated."
- Snapshot naming encodes browser+platform: `example-test-1-chromium-darwin.png` — "the browser name and the platform. Screenshots differ between browsers and platforms due to different rendering, fonts and more, so you will need different snapshots for them."
- Update workflow: `npx playwright test --update-snapshots`.
- Options: "Playwright Test uses the pixelmatch library" — `maxDiffPixels`, `stylePath` (both documented with config-level defaults via `expect.toHaveScreenshot`).

### 4.4 pixelmatch (pixel-level diffing)

- **URL**: https://github.com/mapbox/pixelmatch — page title "mapbox/pixelmatch" README (accessed 2026-07-31; README is versionless, describes the npm package)
- Verbatim: "A small, simple and fast JavaScript pixel-level **image comparison library**, originally created to compare screenshots in tests." Features: "accurate **anti-aliased pixels detection** and **perceptual color difference** metrics"; OKLab-based color difference; "no dependencies... very fast".
- API: `pixelmatch(img1, img2, output, width, height[, options])` returns "the number of mismatched pixels". Options: `threshold` (0–1, default 0.1, "Smaller values make the comparison more sensitive"), `includeAA`, `diffColor`, `windowSize` ("maximum number of differing pixels in any N×N sliding window... robust to scattered noise"), etc. CLI: `pixelmatch image1.png image2.png output.png 0.1`.

### 4.5 Percy (managed visual regression)

- **URLs**: https://www.browserstack.com/docs/percy ("Percy | BrowserStack Docs" landing) and https://www.browserstack.com/docs/percy/overview/visual-testing-basics ("Visual Testing with Percy | BrowserStack Docs"). Note: legacy `docs.percy.io/docs/visual-testing` returns 404; current canonical docs live under `browserstack.com/docs/percy`. Access date 2026-07-31.
- Verbatim ("How Percy addresses visual regression"): "Percy is a visual testing tool that helps detect visual regressions by: **Capturing Screenshots**: Takes snapshots of web pages or application states across a range of browsers and multiple responsive widths on desktop and mobile devices. **Comparing Versions**: Compares new screenshots against previously approved ones (baseline) to highlight any unintended visual differences. **Highlighting Changes**: Provides a visual difference view, making it easy to spot pixel-level changes. **Automating Approvals**: Allows teams to review and approve changes through an intuitive UI... **Integrating with CI/CD**: ..."
- Workflow documented: projects → builds (each build contains snapshots) → approval workflow (approve individual snapshots, groups, or whole builds; approval updates PR/commit status; auto-approve on main branch by default; baseline selection logic documented). Landing page also documents "grouped snapshots, noise filtering", "Percy-specific CSS" (ignoring areas), and "20,000+ real devices".
- Primary-source caveat: the Percy pages describe the hosted product (requires an account to run); capabilities are cited as documentation only.

### 4.6 Chromium headless screenshot modes

- **URL**: https://developer.chrome.com/docs/chromium/new-headless — page title "Headless Chrome | Chrome for Developers" (accessed 2026-07-31; page references Chrome 132.0.6793.0 as the old-headless split point and Chrome 123+ flags, so it tracks ~2024-2025 Chrome; no explicit page version stamp)
- Verbatim: "To use Headless mode, pass the `--headless` command-line flag: `chrome --headless`"
- Verbatim: "Chrome now has unified Headless and headful modes. Since Chrome 132.0.6793.0 the old Headless mode is only available as a standalone binary named `chrome-headless-shell`."
- Documented screenshot-relevant flags: `--dump-dom`, `--screenshot` ("takes a screenshot of the target page and saves it as `screenshot.png` in the current working directory. This is especially useful in combination with the `--window-size` flag. `chrome --headless --screenshot --window-size=412,892 https://developer.chrome.com/`"), `--print-to-pdf` / `--no-pdf-header-footer`, `--timeout`, `--virtual-time-budget`, `--remote-debugging-port` for debugging.

### 4.7 What evidence a rendered verification pass should capture (synthesis from documented capabilities)

This subsection is **analysis** grounded in the cited documented capabilities; the capability citations are primary, the checklist items are the researcher's synthesis for B5.

| Evidence to capture | Documented capability | Primary source |
|---|---|---|
| Viewport sizes (desktop + mobile) | `viewport` config / `test.use({ viewport })`, `devices['Desktop Chrome']`, `devices['iPhone 13']`, `page.setViewportSize()` | Playwright Emulation docs (https://playwright.dev/docs/emulation) |
| Full-page screenshots | `fullPage: true` in `page.screenshot` / `toHaveScreenshot` | Playwright Screenshots + PageAssertions docs |
| Per-component / per-state captures | element screenshots (`locator.screenshot`), `clip`, `mask`/`maskColor`, per-state tests; Percy "snapshots of web pages or application states" | Playwright Screenshots/PageAssertions; Percy visual-testing-basics |
| Browser + platform identity of each baseline | snapshot filename encodes `chromium-darwin`-style suffix; docs warn baselines differ per browser/platform | Playwright Visual comparisons docs |
| Deterministic conditions (animations off, caret hidden, volatile elements hidden) | `animations: "disabled"` (default), `caret: "hide"` (default), `stylePath` for volatile/dynamic elements | Playwright PageAssertions / Visual comparisons docs |
| Light/dark color schemes (contrast-relevant) | `colorScheme: 'light' \| 'dark'` emulation | Playwright Emulation docs |
| Diff output + thresholds | `maxDiffPixels`, `maxDiffPixelRatio`, `threshold` (YIQ); pixelmatch diff image + windowed density | Playwright Visual comparisons; pixelmatch README |
| Same environment for baseline and run | documented warning (OS, version, headless mode, power source) | Playwright Visual comparisons docs |
| Rendered artifacts retained | committed golden files; `--update-snapshots` review workflow | Playwright Visual comparisons docs |

---

## 5. WCAG 2.2 conformance structure

### 5.1 Normative text (https://www.w3.org/TR/WCAG22/ §5, verbatim)

Intro to §5: "This section lists requirements for conformance to WCAG 2.2. It also gives information about how to make conformance claims, which are optional."

**Conformance Requirement 1 — Conformance Level** (5.2.1):

> "One of the following levels of conformance is met in full.
> - For Level A conformance (the minimum level of conformance), the web page satisfies all the Level A success criteria, or a conforming alternate version is provided.
> - For Level AA conformance, the web page satisfies all the Level A and Level AA success criteria, or a Level AA conforming alternate version is provided.
> - For Level AAA conformance, the web page satisfies all the Level A, Level AA and Level AAA success criteria, or a Level AAA conforming alternate version is provided."

Note 2: "It is not recommended that Level AAA conformance be required as a general policy for entire sites because it is not possible to satisfy all Level AAA success criteria for some content."

**Conformance Requirement 2 — Full pages** (5.2.2):

> "Conformance (and conformance level) is for full web page(s) only, and cannot be achieved if part of a web page is excluded."

Note 3 (responsive variations — directly relevant to a viewport-based verification checklist):

> "A full page includes each variation of the page that is automatically presented by the page for various screen sizes (e.g. variations in a responsive web page). Each of these variations needs to conform (or needs to have a conforming alternate version) in order for the entire page to conform."

**Conformance Requirement 3 — Complete processes** (5.2.3):

> "When a web page is one of a series of web pages presenting a process (i.e., a sequence of steps that need to be completed in order to accomplish an activity), all web pages in the process conform at the specified level or better. (Conformance is not possible at a particular level if any page in the process does not conform at that level or better.)"

**Conformance Requirement 4 — Only Accessibility-Supported Ways of Using Technologies** (5.2.4) and **Conformance Requirement 5 — Non-Interference** (5.2.5): quoted fully in the fetched spec text; CR5 additionally requires that SC 1.4.2, 2.1.2, 2.3.1, 2.2.2 apply to *all* content on the page.

**Conformance Claims** (5.3.1, verbatim):

> "Conformance claims are **not required**. Authors can conform to WCAG 2.2 without making a claim. However, if a conformance claim is made, then the conformance claim **must** include the following information:
> 1. **Date** of the claim
> 2. **Guidelines title, version and URI** "Web Content Accessibility Guidelines 2.2 at https://www.w3.org/TR/WCAG22/"
> 3. **Conformance level** satisfied: (Level A, AA or AAA)
> 4. **A concise description of the web pages**, such as a list of URIs for which the claim is made, including whether subdomains are included in the claim.
> 5. A list of the **web content technologies relied upon**."

Optional components (5.3.2, verbatim, selected): "A list of success criteria beyond the level of conformance claimed that have been met... A list of the specific technologies that are 'used but not relied upon.' A list of user agents, including assistive technologies that were used to test the content... A machine-readable metadata version of the conformance claim."

Statement of Partial Conformance — Third Party Content (5.4): monitored-and-repaired within two business days, or a statement "This page does not conform, but would conform to WCAG 2.2 at level X if the following parts from uncontrolled sources were removed." Statement of Partial Conformance — Language (5.5) has its own form.

### 5.2 Understanding Conformance (https://www.w3.org/WAI/WCAG22/Understanding/conformance.html)

- Page title: "Understanding Conformance" (WAI; accessed 2026-07-31; the Understanding pages in the WCAG 2.2 set have no separate version stamp but belong to the WCAG 2.2 recommendation set)
- Verbatim: "To conform to WCAG 2, you need to satisfy the success criteria, that is, there is no content which violates the success criteria. ... if there is no content to which a success criterion applies, the success criterion is satisfied."
- Verbatim: "All WCAG 2 success criteria are written as testable criteria for objectively determining if content satisfies them. Testing the success criteria would involve a combination of automated testing and human evaluation."
- Understanding Requirement 2 repeats the full-page rule and its responsive note; Understanding Requirement 3 explains Complete processes with the online-store/checkout example ("All pages in the series from start to finish (checkout) conform in order for any page that is part of the process to conform."); Understanding Requirement 5 explains Non-Interference.
- Conformance Claims: "It is not required to make any conformance claim in order to conform. If one does make a claim, however, all the information required in a conformance claim must be provided." Documents schema.org metadata option for machine-readable claims (example claim with `accessibilitySummary`), and: "Conformance claims are not usually located on each web page within the scope of conformance."
- Partial conformance (third party): "if the page does not conform to WCAG only for reasons that are legitimately outside the author's control then the author can make a claim of partial conformance... Be sure to monitor any content that can change without approval from the web page author, as a page which once conformed may suddenly fail to conform."

---

## 6. Cross-cutting findings and uncertainties

### 6.1 Findings

1. **Tailwind v4 current**: 4.3.3 (published 2026-07-16). The theme docs describe `@theme` (token→utility + CSS variable emission), `@theme inline` (value inlining for variable-referencing tokens, with the documented var-resolution failure mode), `@theme static` (always emit all variables), and default `:root` emission.
2. **WCAG 2.2 is the operative standard** (W3C Recommendation 2023-10-05, republished 2024-12-12 with errata). Contrast thresholds: 4.5:1 normal / 3:1 large (1.4.3, AA), 3:1 non-text (1.4.11, AA), 7:1 / 4.5:1 enhanced (1.4.6, AAA). Large = 18pt or 14pt bold; 14pt≈18.5px, 18pt≈24px; no rounding of computed ratios.
3. **Automated contrast checking has documented blind spots**: axe-core does not report background-image text, obscured text, or images of text; foreground transparency/gradients/pseudo-elements/borders/overlap are documented as difficult. WCAG frames conformance testing as automated + human evaluation.
4. **Rendered visual verification is a documented, standard practice**: Playwright's `toHaveScreenshot` (v1.23+) with golden files, pixelmatch underneath, per-browser/platform baselines, environment determinism requirements; Percy adds managed baseline/review/approval workflows; Chromium headless provides CLI screenshot capture.
5. **Conformance claims** require date, guideline title/version/URI, level, page description, and relied-upon technologies; full-page conformance includes responsive variations; complete processes must conform as a whole.

### 6.2 Uncertainties / gaps (stated honestly)

- The Tailwind **upgrade guide** fetched does not document `@theme inline` (documented instead in the Theme docs). If a dedicated upgrade-guide note for `inline` exists elsewhere on tailwindcss.com (e.g. release posts), it was not fetched in this pass.
- `docs.percy.io` (legacy) 404s; the current Percy docs are under browserstack.com/docs/percy, and the two Percy pages fetched are product-marketing-style documentation. Deque docs for axe-core rules were fetched for **4.10**; a newer rule version may exist but 4.10 is the current stable rule-docs line referenced by the fetched page.
- The Chromium headless page has no explicit "last updated" stamp; its content references Chrome 132/123 era behavior (verified flags quoted as-is).
- WebAIM's "14pt bold = 18.66px" differs from W3C's "≈18.5px"; the checklist should cite W3C (normative) and treat WebAIM as supporting.
- Percy, BrowserStack, and axe DevTools are commercial services (accounts required to run); cited for documented capabilities only, per task constraints.

### 6.3 Implication for B5 checklist (analysis)

A compliant UI-baseline verification checklist grounded in the above should require: (a) computed-color contrast checks per WCAG 2.2 formulas with **no rounding**, at 4.5:1/3:1 text and 3:1 non-text (plus 1.4.11 adjacent-color and focus-indicator cases), using user-agent colors rather than anti-aliased pixels, with manual review for axe-incomplete cases; (b) Tailwind-level token verification that `@theme` tokens emit as `:root` custom properties and that any variable-referencing tokens use `@theme inline` so utilities inline values (avoiding the documented `var()` resolution failure); (c) rendered verification per Playwright's golden-file workflow — pinned environment, viewport matrix (desktop + mobile per full-page conformance note), fullPage + element/state captures, animations disabled, caret hidden, stylePath for volatile content, committed baselines reviewed via `--update-snapshots`; and (d) any conformance claim structured per §5.3.1 with date, guideline URI, level, page scope (all responsive variations), and relied-upon technologies.

---

## 7. Verification evidence for this deliverable

- [x] Output file exists at `<workspace-root>\audit-outputs\research\track-b\_evidence-b5-web.md` (written 2026-07-31)
- [x] File is non-empty and contains no placeholder tokens (`TBD`, `TODO`, `lorem`, `<...>` unused)
- [x] Section 1 quotes the official Tailwind docs for `@theme` / `@theme inline` / `:root` emission, with current version (v4.3.3, GitHub releases API)
- [x] Section 2 quotes WCAG 2.2 formulas exactly (relative luminance, contrast ratio, 1.4.3, 1.4.11, large-scale definition, Understanding pages)
- [x] Section 3 documents contrast tooling with versions/dates (axe-core 4.10 rule docs, WebAIM, programmatic routes, documented limitations)
- [x] Section 4 documents rendered-verification tooling with versions/dates (Playwright API "added in" versions, pixelmatch, Percy, Chromium headless)
- [x] Section 5 quotes the WCAG 2.2 conformance structure (levels, full pages, complete processes, claims)
- [x] Every claim carries URL + page title + access date (2026-07-31) + version/date where available; secondary sources marked
- [x] `papyr-reference/` untouched; no installs/builds/servers/browser execution performed; no authenticated access used
