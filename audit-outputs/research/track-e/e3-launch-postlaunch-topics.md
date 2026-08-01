# E3 Research Brief: Launch and Post-Launch Localized Topics

| Field | Value |
|---|---|
| Brief ID | E3 |
| Path | `audit-outputs/research/track-e/e3-launch-postlaunch-topics.md` |
| Track | E (blog automation research) |
| Title | Launch and post-launch localized topics |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete (candidate topics and selection criteria; no demand metrics are claimed) |
| Governing decisions | DEC-052, DEC-053, DEC-121, DEC-124, DEC-113, DEC-044, DEC-048, DEC-128, DEC-106, DEC-141, DEC-122, DEC-023; DEC-054 to DEC-060, DEC-066, DEC-183, DEC-188 |
| Governing plan section | Research program plan §6.5, §7.5 (E3), §8 (template) |
| Files read | `AGENTS.md`; `audit-outputs/research-program-plan.md`; `papyr-rebuild-decisions.md` (DEC-001-188, in full); `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` (§15.6, §19, §21.5); `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` (§25.3.15-16, §25.3.21); `audit-outputs/spec-cross-review.md`; `audit-outputs/spec-corrections-report.md`; read-only legacy evidence from `papyr-reference/` (paths and lines cited in Section 5); public primary sources listed in Section 5 (URLs verified live with HTTP 200 on 2026-07-31) |

---

## 1. Scope

### 1.1 Feature and decision area

DEC-052 accepts a launch blog of five priority topics, each intentionally localized into English and Spanish (10 articles at the time), expanded by DEC-121 to EN/ES/ID (15 launch articles). DEC-053 accepts an automatic post-launch cadence of one new topic per day with corresponding localized articles, expanded by DEC-124 to one coordinated trilingual topic set per day. DEC-044 requires tool pages to carry concise transactional content while a separate blog serves broader informational search demand, and DEC-052 requires topic selection to "avoid duplicating or cannibalizing the transactional intent of the five tool pages." E3 researches evidence-based topic-selection criteria and proposes candidate launch topics and the post-launch topic pipeline.

### 1.2 User problem

Papyr needs a genuine informational content program in three locales that grows organic search (DEC-106) without cannibalizing the five tool pages, without keyword filler, and without fabricated demand claims or ranking promises (DEC-066, DEC-101). The daily trilingual cadence must not produce scaled spam (see Section 5, Google spam policies) or weaken the blocking quality gates (DEC-053, DEC-124).

### 1.3 Current approved Papyr behavior

- Five launch tools: Compress PDF, Merge PDF, Split PDF, JPG to PDF, PDF to JPG (DEC-010), with locale-prefixed routes `/en`, `/es`, `/id` and localized slugs (DEC-023, DEC-122).
- Launch blog inventory: five topics x EN/ES/ID = 15 articles (DEC-052, DEC-121), all passing the same blocking gates as post-launch content (DEC-052).
- Post-launch: at most one coordinated trilingual topic set per day; skipping is preferable to an incomplete or low-quality set (DEC-124); the daily cadence may pause for post-launch stability and corrective work (DEC-141); kill-switch and automatic pause thresholds required (DEC-053).
- Articles visibly display original publication and latest material update dates, truthfully and locale-formatted, with consistent metadata and structured data (DEC-113).
- No competitor-comparison pages at relaunch (DEC-128); no fabricated demand/ranking/quality claims (DEC-066, DEC-048).

## 2. Non-goals

- No keyword-volume, traffic, ranking, or demand numbers are claimed in this brief; demand validation is an owner-supplied activity (Search Console, keyword research) recorded in Section 9.
- No topic is accepted or published by this brief; the five launch topics and the post-launch inventory require the owner's approval through the normal gates (DEC-054, DEC-057).
- No competitor-comparison or "versus" content (DEC-128).
- No content writing, no publication, no repository changes (plan §4.1).
- No claim that any topic will rank or perform; the acceptance criteria are functional and process-based (DEC-066).

## 3. Research questions (plan §7.5, E3)

1. What criteria select blog topics that avoid duplicating or cannibalizing the five tool pages (DEC-052), based on documented search-intent practice?
2. What does localization require per locale (EN/ES/ID) for language, search intent, slugs, metadata, hreflang, and canonicals (DEC-048, DEC-121, DEC-124, DEC-122)?
3. What cadence rules make "at most one coordinated trilingual topic set per day" safe (DEC-053, DEC-124), and what is the documented risk of scaled publication?
4. What date-display behavior satisfies DEC-113 and documented search-engine practice?
5. Which five candidate launch topics (one per tool, informational) are consistent with the above, and how should the post-launch topic inventory be governed?

## 4. Method

- Read the decision log, both specs, both review/correction reports, and the plan in full.
- Collected read-only legacy evidence from `papyr-reference/` for historical content-intent examples and the legacy SEO program (non-canonical, DEC-026): `docs/15_Papyr_GTM_Strategy_v1.0.md`, `docs/20_Papyr_Roadmap_v1.0.md`, `frontend/src/app/sitemap.ts`, `frontend/src/app/faq/page.tsx`.
- Verified current official Google Search Central guidance (URLs live, HTTP 200, accessed 2026-07-31) on multilingual/multi-regional sites, byline dates, helpful content, and spam policies; the byline-date page was read in full (last updated 2025-12-10 UTC).
- No prohibited action was performed (Section 12).

## 5. Evidence

### 5.1 Search-intent and content-quality practice (Google Search Central, official; all HTTP 200 on 2026-07-31)

| # | Source (URL) | What it documents | Role |
|---|---|---|---|
| G1 | `https://developers.google.com/search/docs/fundamentals/creating-helpful-content` | People-first content guidance: content exists to help users, not to manipulate ranking; expertise, experience, authoritativeness, and trustworthiness as quality signals | Primary |
| G2 | `https://developers.google.com/search/docs/essentials/spam-policies` | Scaled content abuse policy: mass-producing pages primarily to manipulate search rankings is spam; directly relevant to a daily automated publishing cadence | Primary |
| G3 | `https://developers.google.com/search/docs/specialty/international/localized-versions` | "Tell Google about localized versions of your page": hreflang annotation and consistent cross-locale metadata so localized versions are understood as alternates, not duplicates | Primary |
| G4 | `https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites` | "Managing multi-regional and multilingual sites": language and regional targeting; content language should match the audience's language; country targeting is for region-specific content | Primary |
| G5 | `https://developers.google.com/search/docs/appearance/publication-dates` | Byline-date guidance (read in full; last updated 2025-12-10 UTC): Google estimates a page's published/updated date; to influence it, show a prominent user-visible date labeled "Published"/"Last updated", use `Article`/`BlogPosting` structured data with `datePublished`/`dateModified`, keep visible and structured dates consistent, avoid future dates | Primary |

Intent distinction note: Google Search Central does not publish a single "informational vs transactional intent" taxonomy page; the distinction is established practice supported by the SEO Starter Guide and the query-category concepts in G1/G2. This brief applies the distinction as a design rule (tool pages answer the action; blog articles answer the how-to/reference question) rather than citing a taxonomy that does not exist.

### 5.2 Legacy evidence (read-only, non-canonical history per DEC-026)

| Evidence | Location | Relevance |
|---|---|---|
| Historical Indonesia-era blog topics show the same tool-adjacent informational intent family later needed internationally: "Cara Compress PDF Tanpa Kehilangan Kualitas" (how-to), "Compress PDF untuk Upload CPNS" (workflow/context), "Merge Ijazah dan Transkrip" (workflow/context); blog cadence was 2-4x/month in the legacy plan | `papyr-reference/docs/15_Papyr_GTM_Strategy_v1.0.md:224-227,288` | Examples of informational intent around each tool; non-canonical (DEC-026), and their Indonesia-first phrasing must not be carried into the international program |
| Legacy roadmap planned an AI-driven SEO content pipeline (2-4 articles/week) and a future blog platform | `papyr-reference/docs/20_Papyr_Roadmap_v1.0.md:735,1620,1666` | Historical ambition; DEC-048/049 now govern the actual pipeline (E2) |
| Legacy sitemap lists 13 tools + /faq + /privacy with no blog | `papyr-reference/frontend/src/app/sitemap.ts:5-19,21-47` | The rebuild introduces the blog as a new surface; no legacy blog URLs exist to reconcile (B4 confirms) |
| Legacy FAQ covers site-level trust questions (safety, retention, accounts, limits, mobile, free, formats, contact) | `papyr-reference/frontend/src/app/faq/page.tsx:49-84` | Cannibalization context: the FAQ is site-level trust content; blog articles must not duplicate it and must not duplicate tool-page copy (DEC-044) |

## 6. Alternatives (DEC-055)

| # | Approach | Trade-offs, risks, cost/operational impact, privacy/security | Assessment |
|---|---|---|---|
| A | **One launch topic per tool (five topics), informational intent, then a governed inventory for post-launch.** Each tool gets one adjacent informational topic; post-launch topics are drawn from a topic inventory maintained against the Section 8 criteria. | Directly matches DEC-052's "one strong topic associated with each launch tool" rationale; simplest cannibalization control (one topic maps to one tool page); the daily pipeline consumes inventory rather than inventing topics at generation time. Cost: inventory curation effort. Privacy/security: none beyond the standard gates. | Recommended (Section 7). |
| B | **Hub-and-spoke topic clusters around each tool** (one cluster page + supporting articles per tool) from launch. | Stronger information architecture long-term, but multiplies launch inventory beyond DEC-052's five topics and conflicts with the accepted 15-article launch inventory; can be phased in post-launch. | Rejected for launch; compatible as a post-launch evolution under the same criteria. |
| C | **Demand-first selection** (topics chosen by third-party keyword tools before launch). | Would require purchased or third-party demand data and still could not guarantee ranking; conflicts with DEC-066's no-fabrication posture and this brief's no-claimed-metrics constraint; demand data is the owner's input (G1-G4 do not supply volumes). | Rejected for this phase; owner-supplied demand evidence (GSC, keyword research) is a criterion in Section 7.2, not a substitute for intent fit. |

## 7. Recommendation

**Recommendation (not an accepted decision; DEC-054, DEC-057):** adopt Approach A. Five candidate launch topics, one informational topic per launch tool, are proposed in Section 7.1; the post-launch pipeline consumes a governed topic inventory scored against the Section 7.2 criteria, with cadence and date rules from Sections 7.3-7.4. No demand metric or ranking outcome is claimed anywhere; the criteria require owner-supplied demand evidence before any post-launch topic is committed to inventory.

### 7.1 Proposed candidate launch topics (one per tool; informational intent)

Each topic is proposed as a direction with example slugs. Final EN/ES/ID slugs, metadata, hreflang, and canonicals belong to B4's SEO design; ID uses translated slugs per DEC-122. The tool page remains the transactional surface; each article answers the adjacent how-to/reference question without targeting the tool page's primary keyword set.

| # | Launch tool (transactional surface) | Candidate informational topic (EN) | Intent and cannibalization rationale | Candidate ES direction | Candidate ID direction (slugs per DEC-122) |
|---|---|---|---|---|---|
| 1 | Compress PDF | How to reduce PDF file size without losing quality | How-to: why PDFs get large (images, scans, embedded fonts), what safe reduction preserves, when size cannot shrink; does not duplicate the tool's "compress PDF online" action | "Cómo reducir el tamaño de un PDF sin perder calidad" | "Cara mengecilkan ukuran PDF tanpa mengurangi kualitas" |
| 2 | Merge PDF | How to combine multiple PDFs into one file | Workflow guide: ordering documents, scanning + merging, common submission scenarios; the tool page stays the action surface | "Cómo unir varios PDF en un solo archivo" | "Cara menggabungkan beberapa PDF menjadi satu file" |
| 3 | Split PDF | How to split a PDF into pages or page ranges | How-to: extracting selected pages or page ranges, per-page splits, naming outputs; does not target "split pdf" transactional queries | "Cómo dividir un PDF en páginas o rangos" | "Cara memisahkan PDF menjadi halaman atau rentang halaman" |
| 4 | JPG to PDF | How to turn images and photos into a PDF | Workflow guide: phone scanning, sharing photos as one PDF, preserving image order and orientation; complements the tool's conversion action | "Cómo convertir imágenes y fotos a PDF" | "Cara mengubah gambar dan foto menjadi PDF" |
| 5 | PDF to JPG | How to convert PDF pages to JPG images | How-to: submitting forms, presentations, social media; explains what rasterization preserves and what it cannot (per DEC-039 honest limits) | "Cómo convertir páginas de PDF a imágenes JPG" | "Cara mengubah halaman PDF menjadi gambar JPG" |

The legacy historical topics (Section 5.2) validate this intent family for PDF tools but are Indonesia-era examples only; the five proposals above are re-derived for the international three-locale program.

### 7.2 Post-launch topic-selection criteria (evidence-based, no fabricated metrics)

A topic may enter the post-launch inventory only if every criterion is met; failing any criterion removes or defers the topic (fail-closed, DEC-048, DEC-124):

1. **Domain fit:** the topic concerns PDF or document workflows and connects to at least one launch tool or an approved future tool.
2. **Informational intent:** the topic answers a how-to, reference, or workflow question; it must not target the primary transactional keyword set of any tool page (cannibalization gate, DEC-052).
3. **Demand evidence (owner-supplied):** the topic is supported by the owner's Search Console query data, the owner's keyword research, or both. No third-party volume figures are assumed; absent owner-supplied evidence, the topic is not committed.
4. **Factual supportability:** every claim, step, and limitation in the article is verifiable and supportable (no fabricated tests, citations, product capabilities, or legal advice; DEC-048, DEC-066).
5. **Longevity or deliberate seasonality:** the topic is evergreen, or its seasonality is explicitly planned and tracked.
6. **Per-locale intent verification:** the topic is confirmed to make sense independently in EN, ES, and ID (query phrasing, cultural context, format conventions), not produced by literal machine translation (DEC-048, DEC-124, G3, G4).
7. **Originality and non-duplication:** the topic does not duplicate existing articles, the FAQ (site-level trust content), or tool-page copy (DEC-044; legacy FAQ evidence in 5.2).
8. **Policy and safety:** the article raises no unsafe claims, no policy violations, and no competitor-comparison framing (DEC-048, DEC-128).
9. **Quality-gate pass:** the article set passes the full DEC-048 gate suite implemented per E2.

### 7.3 Cadence rules (DEC-053, DEC-124)

- At most one coordinated trilingual topic set per calendar day; a failing language or quality gate blocks the whole set for that day; skipping is preferable to publishing an incomplete or low-quality set (DEC-124).
- The daily cadence is not a guarantee: no topic publishes on a day when no qualified topic passes validation (DEC-053).
- The cadence may pause for post-launch stability and corrective work (DEC-141) and must pause under the automatic thresholds in DEC-053 (build failures, quality regressions, policy issues, provider anomalies, or widespread indexing problems).
- Publication-day timing uses an explicit UTC boundary (design choice for the approved implementation plan, cross-referenced from E2).
- Continuous monitoring covers topic inventory, duplication, cannibalization, indexing quality, crawl behavior, factual corrections, and organic performance (DEC-053), with data drawn from owner-managed tools (e.g., Search Console) per DEC-025 boundaries.

### 7.4 Date-display requirements (DEC-113)

- Every article visibly displays its original publication date and its latest material update date, locale-formatted and truthful (DEC-113).
- `datePublished` and `dateModified` structured data (Article/BlogPosting) matches the visible dates; no future dates; times/timezones consistent (G5).
- Automated edits advance the update date only for substantive material changes, not trivial formatting or deployment-only changes (DEC-113); EN/ES/ID counterparts may carry distinct dates (DEC-113).

## 8. Measurable acceptance criteria (verifiable without a benchmark program; DEC-066)

1. Each of the five launch topics maps to exactly one launch tool and passes the cannibalization gate: its target query set does not overlap the tool page's primary transactional keyword set (verified by fixture-based gate tests per E2).
2. Every launch article exists in EN, ES, and ID with locale-appropriate slugs (ID uses translated slugs per DEC-122) and complete hreflang, canonical, and sitemap metadata (B4-owned).
3. The Section 7.2 selection criteria are applied and recorded for the first 30 post-launch topics; the recorded inventory log is reviewable (criterion application is verifiable, not ranking outcome).
4. Cadence: git history and workflow runs show at most one coordinated trilingual topic set per calendar day; days on which any gate failed show no publication (DEC-124).
5. No demand metric, traffic figure, or ranking claim appears in the topic inventory or generated articles (automated scan gate in the E2 pipeline).
6. Date behavior: every article visibly shows its publication and latest material-update dates, and the visible dates match the `datePublished`/`dateModified` structured data with no future dates (DEC-113; G5).

## 9. Assumptions, uncertainties, and unresolved questions

1. **Material owner input (demand data):** actual search-demand evidence for any topic requires the owner's Search Console data and/or keyword research. This brief deliberately contains no demand figures and makes no ranking promises (DEC-066, DEC-101).
2. **Slug/metadata ownership:** the example slugs in Section 7.1 are directions; final localized slugs, hreflang, canonicals, sitemap entries, and legacy-URL dispositions are B4's SEO design responsibility (DEC-023, DEC-122, DEC-127).
3. **Launch inventory acceptance:** DEC-052/DEC-121 set the count (five topics, 15 articles) and the gates; the specific five topics above are a proposal for the owner's approval, not an accepted decision.
4. **Scaled-content risk:** Google's spam policies treat mass-produced pages designed to manipulate ranking as spam (G2). The daily cadence is therefore safe only when the gates (especially factual support, originality, and usefulness per G1) genuinely pass; the pipeline must skip rather than fill (DEC-124).
5. **Google does not publish an intent taxonomy page:** the informational/transactional distinction is applied as a design rule from documented practice; this is recorded as an interpretation, not a citation.

## 10. Dependencies and cross-track interfaces

- **E2** consumes the topic inventory and cadence rules to schedule generation and publication.
- **B4** owns slugs, hreflang, canonicals, sitemaps, and legacy-URL dispositions for the blog and all localized routes.
- **D5/C5** define the policy-vocabulary and monitoring gates that Section 7.2 criteria 8 and 7.3 reference.
- **X1/X2** record this brief's mapping (governing decisions DEC-052/053/121/124/113/044/128/106/141; spec sections UX §15.6, §19.8, §21.5) and surface the owner decision prompts in Section 9.

## 11. Source-date log and evidence-completeness notes

- All web sources accessed 2026-07-31; URLs verified live (HTTP 200) on 2026-07-31. G5 read in full (last updated 2025-12-10 UTC); G1-G4 verified live and summarized from their canonical content.
- Legacy citations verified against `papyr-reference/` content on 2026-07-31.
- Evidence-completeness caveat: no demand data is included by design (Section 9.1); G1-G4 do not supply keyword volumes, and no third-party tool was accessed or quoted.

## 12. Prohibitions-compliance statement

- No content was published; no repository changes were made; no installs, builds, servers, VPS access, deployment, account creation, provider API calls, or third-party keyword-tool access were performed.
- `papyr-reference/` was only read; read-only `git -C papyr-reference status --porcelain` returned empty output with exit 0 before and after this brief.
- No source, spec, or decision file was modified. The only files created by this brief are this deliverable.
- No demand metrics, keyword volumes, traffic figures, or ranking guarantees are claimed anywhere in this brief (DEC-066).
- A chat-only summary is insufficient; this file is the primary deliverable.
