# PT-01 Dossier: Analytics Schema, Redaction, and Leakage Tests

## Summary

Created the privacy-reviewed analytics system for Phase 6. Three source modules and two
test files implementing the closed event field schema, privacy redaction pipeline, and
automated leakage guards.

## Files Created

| File | Purpose |
|---|---|
| `src/lib/analytics-schema.ts` | Closed event field schema with ALLOWED_FIELDS, PROHIBITED_FIELD_NAMES, bandSize, ErrorCategory, CoarseSizeBand, FunnelStage, Outcome, ProcessingMode, ToolId types |
| `src/lib/analytics.ts` | Send pipeline: redactPayload, isOptedOut, trackEvent, trackPageView, useAnalytics, errorCategoryFor — all SSR-guarded and opt-out-aware |
| `src/__tests__/leakage.test.ts` | 26 leakage guard tests (jsdom): prohibited key stripping, raw-error ban, bandSize boundaries, opt-out, schema validation gate, prohibited-name shape check |
| `src/lib/__tests__/analytics.test.ts` | 10 unit tests (jsdom): hook pre-binding, trackEvent/trackPageView, SSR guard via window=undefined |

## Design Decisions

### Private prohibited-name lookup
`PROHIBITED_FIELD_NAMES` is exported as a read-only array (numeric keys only — no
prohibited name appears as an object key in any exported shape). The fast case-insensitive
lookup is a private `Record<string, true>`, exported via `isProhibitedFieldName(key)`.

### Value-level coercion
The redaction layer checks both keys and values: if an allowed field's value looks like a
document filename (contains `.pdf`, `.jpg`, `.png`, `.webp` etc.) or matches a prohibited
name, it's coerced to `"[redacted]"`.

### Error category mapping
Raw error strings are never sent. The `errorCategoryFor()` function maps error strings to
a closed `ErrorCategory` enum (invalid-file, limit-exceeded, server-unavailable, expired,
cancelled, internal, encrypted, blocked).

### Opt-out detection
Checks `navigator.doNotTrack`, `navigator.globalPrivacyControl`, and the app-level
`window._papyrAnalyticsOptOut` flag. Reads the global `navigator` (not `window.navigator`)
for robustness in jsdom environments.

### Locked signatures
`redactPayload<T>(data, allowedKeys?)` and `trackEvent(name, data)` are marked as
consumed by PT-03 — signatures must not change once created.

## Vitest Output

```
 RUN  v4.1.10 C:/Users/faizz/mypapyr/frontend


 Test Files  2 passed (2)
      Tests  36 passed (36)
   Start at 06:40:48
   Duration  2.11s (transform 187ms, setup 0ms, import 260ms, tests 44ms, environment 3.24s)
```

Total: 36 tests across 2 files, all passing.
TypeScript strict: clean in all new files (no `any`, no `@ts-ignore`).
Pre-existing TS error in `src/__tests__/supporting-pages.test.tsx` is unrelated.