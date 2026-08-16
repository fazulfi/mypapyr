# P6 Enterprise Completion — Decision Log

**Purpose:** records the resolution of every open owner decision (§12 of
`p6-enterprise-completion.md`) and each ADR from `p6-synthesis.md`, as the
delivery branch workstreams resolve them. The synthesis report is the
authoritative ADR record; this log tracks *resolution status* during execution.

---

| ADR | Decision | Resolution | Status | Recorded in |
| --- | --- | --- | --- | --- |
| ADR-01 (PT01-G1) | Analytics opt-out is a privacy-blocking defect: gate `<Analytics/>`/`<SpeedInsights/>` behind `isOptedOut()` via `beforeSend`. | Implemented — `PrivacyAnalytics` client wrapper with `analyticsBeforeSend`/`speedInsightsBeforeSend` returning `null`/`false` when opted out; layout renders `<PrivacyAnalytics/>`. 8 gate tests. | ✅ RESOLVED (WS-1) | `frontend/src/components/PrivacyAnalytics.tsx`, `privacy-analytics.test.tsx`, `layout.tsx` |
| ADR-01 / PT01-G2 | Event-activation policy: activate pageview/funnel/`adPresent` events vs keep schema-as-capability. | **Capability-only** — schema stays dormant; only `contact_submit` remains active. Matches §12 recommendation ("capability-only unless product needs"); avoids expanding the collection surface without a product requirement. | ✅ RESOLVED (WS-1) | this log |
| ADR-02 (PT04-G5) | Wire `PasswordInput` into Merge vs downgrade claim. | _Pending WS-2._ Recommended: wire. | ⏳ PENDING | — |
| ADR-03 (PT02-G3) | One-ad-per-page vs multi-placement. | _Pending WS-3._ Recommended: align docs to one-ad-per-page. | ⏳ PENDING | — |
| ADR-04 (PT02-G11) | Commit vs drop house-promo fallback. | **Commit** — committed as `7718d74` (WS-0), 21 tests green. | ✅ RESOLVED (WS-0) | git `7718d74` |
| ADR-05 (PT02-DOC) | Ads on legal/support surfaces: align claims vs remove banners. | _Pending WS-3/WS-6._ Recommended: align claims to code (banners disclosed on legal pages). | ⏳ PENDING | — |
| ADR-06 (P6-G8) | Primary/canonical domain: budgezen.com vs mypapyr.com. | _Pending WS-5._ Owner decision required. | ⏳ PENDING | — |
| ADR-07 | CI stays CI-only; deploy is a separate authorized procedure. | Adopted by plan structure; no CI deploy step added. | ✅ RESOLVED | plan §6 |
| ADR-08 | Do not claim P6 complete/deployed until BLOCKED-B/D clear. | Adopted; status language kept as "merged to main; deployment and backend security unverified". | ✅ RESOLVED | plan §9 |
| ADR-09 | Add full-project typecheck gate to CI (fix 4 tsc errors first). | _Pending WS-7._ | ⏳ PENDING | — |
| ADR-10 | Tests-first for every gap fix. | Adopted; each workstream adds failing tests before implementation. | ✅ RESOLVED | plan §6.3 |
