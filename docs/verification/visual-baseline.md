# Phase 10 visual baseline

## Purpose

VL-03 is the rendered visual verification gate for Papyr. It operationalizes DEC-143: compare the current product surface with the intended legacy-clone replacement direction through repeatable browser renders, rather than relying on source inspection alone. The current reality is the localized Next.js 16 application and its five tool workflows; Phase 10 establishes the first reproducible visual baseline for that surface.

The verification is hermetic. It does not call the processing backend, and requests to `highperformanceformat.com` are aborted before they can affect a render.

## Verification matrix

`frontend/e2e/visual.spec.ts` renders the following routes at each viewport width:

- `/en`
- `/en/compress-pdf`
- `/en/merge-pdf`
- `/en/split-pdf`
- `/en/jpg-to-pdf`
- `/en/pdf-to-jpg`
- `/en/privacy` as a supporting page
- `/en/nonexistent` as the localized 404 surface

The viewport matrix is 375, 768, 1280, and 1440 CSS pixels. The test runs in both configured Playwright projects, including Pixel 7. Every route/width pair checks horizontal overflow, computed token colors, and a visible `main#main-content`, then writes a full-page screenshot.

## Token and contrast contract

The canonical tokens are defined in the non-inline `@theme` block in `frontend/src/app/globals.css` and mirrored in `frontend/src/lib/design-tokens.ts`:

| Token | Value |
| --- | --- |
| Navy | `#1e3a5f` |
| Accent | `#2563eb` |
| Background | `#f9fafb` |
| Foreground | `#171717` |

The browser test rechecks the foreground/background and SkipLink contrast. `scripts/check-contrast.sh` parses and cross-checks the core hex tokens in both sources, computes sRGB relative luminance and WCAG ratios with Python 3, and fails closed for missing, malformed, mismatched, or low-contrast values. Support `oklch` values remain documented in `design-tokens.ts`; the guard focuses on the required core hex combinations.

The guarded combinations are foreground on background and navy on background at 4.5:1, accent on white at 4.5:1, and accent/background, navy/white, and foreground/white at the 3.0:1 large-text/UI threshold.

## Artifacts and commands

Screenshots are written to `frontend/test-results/visual/` with deterministic route-and-width filenames. The directory is a test artifact location and is not a source component or a committed baseline.

From the repository root, run the contrast guard and its mutation self-test:

```sh
bash scripts/check-contrast.sh
bash scripts/test-check-contrast.sh
```

From `frontend/`, run the visual gate with either command:

```sh
npm run test:e2e -- --grep visual
npx playwright test visual.spec.ts
```

The home page also records browser `layout-shift` entries during load and requires cumulative layout shift below 0.1. The check is intentionally limited to the browser's layout-shift signal and a non-zero document width; it does not require a live ad provider.

## Results

| Verification | Viewports | Result |
| --- | --- | --- |
| Route renders, token colors, main landmark, overflow, screenshots | 375, 768, 1280, 1440 | Established in Phase 10 |
| WCAG token contrast | Core documented combinations | Established in Phase 10 |
| Home hero and ad-region layout stability | Playwright desktop and Pixel 7 projects | Established in Phase 10 |
