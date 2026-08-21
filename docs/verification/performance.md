# Phase 10 performance verification

Phase 10 establishes Papyr's Core Web Vitals and page-performance program under R-27. The program measures the user-visible experience on the English homepage and a representative tool page, with both mobile-throttled and desktop results recorded. The targets are grounded in DEC-200 and DEC-201.

## Measures and targets

| Measure | Mobile, throttled | Desktop | Interpretation |
| --- | ---: | ---: | --- |
| First Contentful Paint (FCP) | ≤ 1.8 s | ≤ 1.8 s | First meaningful browser paint |
| Largest Contentful Paint (LCP) | ≤ 2.5 s | ≤ 2.5 s | Main content becomes visible |
| Interaction to Next Paint (INP) | ≤ 200 ms | ≤ 200 ms | Responsiveness to user interaction |
| Cumulative Layout Shift (CLS) | ≤ 0.1 | ≤ 0.1 | Visual stability during loading and interaction |
| Total Blocking Time (TBT) | ≤ 300 ms | ≤ 300 ms | Lab proxy for main-thread contention |
| Lighthouse performance score | ≥ 90 | ≥ 90 | Overall lab performance score |
| Lighthouse accessibility score | ≥ 90 | ≥ 90 | Accessibility quality gate |
| Lighthouse best-practices score | ≥ 90 | ≥ 90 | Browser and delivery quality gate |
| Lighthouse SEO score | ≥ 90 | ≥ 90 | Crawlability and discoverability gate |

INP is a field-oriented Core Web Vital and is recorded when the measurement environment provides it. Lighthouse CI asserts the lab metrics available in the committed configuration, including FCP, LCP, CLS, and TBT. A passing lab run does not replace field validation.

## Running the program

From the frontend directory, build the production app and run the performance gate:

```bash
npm run build
npm run test:perf
```

`lhci autorun` starts the built Next.js app on port 3000, measures `/en` and `/en/compress-pdf`, asserts the configured scores and budgets, and writes local report artifacts to `frontend/.lighthouseci/`. Chrome must be installed and available to Lighthouse CI. The config currently uses one desktop profile; repeat the run with a mobile Lighthouse setting when establishing the mobile column in the results table.

The config is intentionally local-only. It does not upload results to a remote Lighthouse server. The filesystem target keeps JSON and HTML reports under `.lighthouseci/`; this generated directory is an artifact location, not a source-controlled baseline.

## Ad-slot layout stability

DEC-018 reserves ad dimensions so an eligible ad cannot move surrounding content after load. CLS is asserted at no more than 0.1 for the representative tool page, where the ad slot is part of the result-phase layout. When reviewing a failure, inspect both the initial viewport and the result transition: late ad creation, missing dimensions, and content inserted beside the Download control are regressions even when the overall performance score remains high.

## Field data and lab gates

`@vercel/speed-insights` provides field data collection through the existing privacy-reviewed client integration. It helps observe real-user LCP, INP, and CLS across device and network conditions, but it is not a pass/fail gate and does not replace the local Lighthouse CI run. Investigations should compare field trends with the controlled mobile and desktop lab measurements before changing performance budgets.

## Phase 10 baseline

The first accepted baseline is established in Phase 10. Record the measured values from the initial mobile-throttled and desktop runs below, then retain the corresponding `.lighthouseci/` artifacts for comparison during future performance work.

| Run | FCP | LCP | INP | CLS | TBT | Performance | Accessibility | Best practices | SEO | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mobile, throttled | — | — | — | — | — | — | — | — | — | Established in Phase 10 |
| Desktop | — | — | — | — | — | — | — | — | — | Established in Phase 10 |

## References

- DEC-018 — reserved ad-slot dimensions and layout-stability behavior.
- DEC-200 — Phase 10 performance measurement and Core Web Vitals program.
- DEC-201 — R-27 performance targets and verification expectations.
