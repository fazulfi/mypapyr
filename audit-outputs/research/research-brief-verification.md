# Papyr Primary Research Briefs — Read-Only Quality Verification

| Field | Value |
|---|---|
| Document ID | PPR-VER-001 |
| Title | Verification of the 25 Papyr primary research briefs (Tracks A-E) |
| Date | 2026-07-31 |
| Verifier role | Sisyphus-Junior (executor subagent, read-only quality verification) |
| Scope | Exactly 25 primary briefs: A1-A6, B1-B5, C1-C6, D1-D5, E1-E3 under `audit-outputs\research\` |
| Governing inputs | `AGENTS.md` (read in full); `audit-outputs\research-program-plan.md` (read in full; §8 template, §11 verification assertions, §4 prohibitions) |
| Primary deliverable | this file |
| Status | Verification complete; 25/25 briefs PASS with 0 blocking defects, 2 minor observations, 3 open items |

---

## 1. Method and checks performed

Every primary brief was **opened and read in full** (not merely listed). Supporting evidence files (`_evidence-*.md`, `track-c/evidence/*.md`) were scanned but are not primary briefs and are out of scope for the pass/fail matrix. All verification actions were read-only.

| # | Check | Command / method | Result |
|---|---|---|---|
| 1 | Inventory of the 25 primary briefs at their exact plan paths | `filesystem_directory_tree` + `filesystem_list_directory_with_sizes` on `audit-outputs\research\` (tracks a, b, c, d, e) | All 25 files exist at their plan §6 paths; no missing or extra primary briefs |
| 2 | Full read of every brief | `read` on all 25 files (A1-A6, B1-B5, C1-C6, D1-D5, E1-E3) | All 25 read in full; content assessed below |
| 3 | Template section coverage (plan §8: 12 elements) | `grep '^## \d+\.'` per primary brief, plus full-read confirmation of header fields | 25/25 cover all 12 template elements; 1 minor heading substitution (E1 §8, see §6.2) |
| 4 | Placeholder scan | `grep -i 'TODO\|TBD\|FIXME\|XXX\|lorem ipsum\|placeholder\|WIP'` over `audit-outputs\research\**\*.md` | **0 placeholder tokens** in the 25 primary briefs; 2 prose hits that are legitimate (A4 §5.3 HTML `placeholder` attribute; D2 §5 Alternative C "Minimal placeholder legal pages" — a rejected alternative's name) |
| 5 | Benchmark/corpus/comparative scan | `grep -i 'benchmark\|corpus\|comparative\|quality-score\|score program'` per track on primary briefs only | Every hit is a legitimate DEC-066 reference: prohibition statements (§12), non-goals (§3), acceptance-criteria framing, or "design choices validated by functional testing, not benchmarks" (§7/§9). **No benchmark program, corpus, matrix, comparative report, or quality-score program exists in any brief** (see §6.1) |
| 6 | Implementation-authorization scan | `grep -i 'authoriz\|approved for implementation\|proceed to implement\|begin implementation\|go-ahead\|green.?light\|is decided'` over the research tree | Zero authorization language in primary briefs; every "authoriz*" hit is a prohibition statement or quoted decision text (e.g., D5 quoting DEC-093; C1 "no current access authorized") |
| 7 | Recommendation-as-nondecision scan | `grep -c 'not an accepted decision'` | All 25 briefs contain the label (E3 twice) |
| 8 | Decision-change scan | Full-read check for any brief claiming to modify the decision log | No brief rewrites or silently changes a decision; DEC-183 escalation language present where material (D5 §6.7, B3 §5.1, E1 §5.1, C2 §9) |
| 9 | `papyr-reference/` cleanliness | `git -C papyr-reference status --porcelain` (before and after verification) | Empty output, exit 0, both runs; HEAD `981c59a` — unchanged |
| 10 | X1/X2 existence check | `glob` for `*.md` in `audit-outputs\research\` | `source-and-decision-index.md` (X1) and `reconciliation-report.md` (X2) do not exist yet — expected: they are Wave 3/4 deliverables (plan §6.6, §10), and this verification gates reconciliation |

No file was modified by this verification except this deliverable. No installs, builds, servers, VPS access, deployment, account creation, or remote actions were performed.

---

## 2. File inventory with byte sizes

| # | Brief | Path | Bytes (KB) | Lines |
|---|---|---|---|---|
| 1 | A1 | `track-a\a1-shared-engine-licenses.md` | 35.50 | 230 |
| 2 | A2 | `track-a\a2-compress-pdf.md` | 18.55 | 144 |
| 3 | A3 | `track-a\a3-merge-pdf.md` | 16.30 | 132 |
| 4 | A4 | `track-a\a4-split-pdf.md` | 14.70 | 135 |
| 5 | A5 | `track-a\a5-jpg-to-pdf.md` | 16.35 | 139 |
| 6 | A6 | `track-a\a6-pdf-to-jpg.md` | 16.77 | 139 |
| 7 | B1 | `track-b\b1-browser-capability-routing.md` | 34.77 | 252 |
| 8 | B2 | `track-b\b2-accessibility.md` | 36.10 | 261 |
| 9 | B3 | `track-b\b3-i18n-locale-paper-policy.md` | 31.83 | 238 |
| 10 | B4 | `track-b\b4-seo-url-migration.md` | 39.99 | 310 |
| 11 | B5 | `track-b\b5-ui-baseline-verification.md` | 29.29 | 231 |
| 12 | C1 | `track-c\c1-queue-workers-redis.md` | 28.23 | 200 |
| 13 | C2 | `track-c\c2-per-tool-server-limits.md` | 37.03 | 309 |
| 14 | C3 | `track-c\c3-r2-lifecycle.md` | 19.33 | 162 |
| 15 | C4 | `track-c\c4-vps-processing-hardening.md` | 25.71 | 179 |
| 16 | C5 | `track-c\c5-observability-status-telegram.md` | 21.46 | 176 |
| 17 | C6 | `track-c\c6-backups-restores.md` | 18.95 | 163 |
| 18 | D1 | `track-d\d1-adsterra.md` | 24.45 | 197 |
| 19 | D2 | `track-d\d2-legal-privacy-copy.md` | 25.60 | 223 |
| 20 | D3 | `track-d\d3-analytics-privacy.md` | 22.28 | 202 |
| 21 | D4 | `track-d\d4-contact-support.md` | 21.81 | 196 |
| 22 | D5 | `track-d\d5-security-threat-privacy.md` | 28.20 | 246 |
| 23 | E1 | `track-e\e1-gpt5-6-sol-contract.md` | 23.62 | 174 |
| 24 | E2 | `track-e\e2-automated-mdx-blog-pipeline.md` | 22.62 | 179 |
| 25 | E3 | `track-e\e3-launch-postlaunch-topics.md` | 20.98 | 172 |

All files non-empty (plan §11 assertion 1). Total primary-brief payload: ~627 KB across 25 files.

---

## 3. Verification matrix (25 rows)

Legend: **P** = PASS; **P\*** = PASS with minor observation (details in §6.2). Column meanings:

- **Templ** = plan §8 template coverage (header, scope, non-goals, research questions, evidence, alternatives, recommendation, measurable acceptance criteria, assumptions/uncertainties, dependencies/interfaces, source-date log, prohibitions-compliance statement).
- **Src/date** = primary sources with URLs/identifiers and access dates (DEC-056), and legacy `papyr-reference/` file:line citations where applicable.
- **Dec/spec** = explicit linkage to governing decisions and spec sections.
- **Options** = at least two viable alternatives compared, or documented single-feasible path (DEC-055).
- **Rec** = recommendation explicitly labeled as a recommendation, not an accepted decision (DEC-054/057).
- **Owner Qs** = explicit, answerable owner decision prompts present.
- **Placeholder** = no TODO/TBD/FIXME/lorem tokens.
- **DEC-066** = no benchmark program/corpus/comparative/score content; all "benchmark" mentions are prohibition/reference use.
- **Git** = `papyr-reference/` verified unchanged (empty porcelain, exit 0).

| # | Brief (path) | Bytes (KB) | Templ | Src/date | Dec/spec | Options | Rec | Owner Qs | Placeholder | DEC-066 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A1 `track-a\a1-shared-engine-licenses.md` | 35.50 | P | P | P | P | P | P | P | P | **PASS** |
| 2 | A2 `track-a\a2-compress-pdf.md` | 18.55 | P | P | P | P | P | P | P | P | **PASS** |
| 3 | A3 `track-a\a3-merge-pdf.md` | 16.30 | P | P | P | P | P | P | P | P | **PASS** |
| 4 | A4 `track-a\a4-split-pdf.md` | 14.70 | P | P | P | P | P | P | P | P | **PASS** |
| 5 | A5 `track-a\a5-jpg-to-pdf.md` | 16.35 | P | P | P | P | P | P | P | P | **PASS** |
| 6 | A6 `track-a\a6-pdf-to-jpg.md` | 16.77 | P | P | P | P | P | P | P | P | **PASS** |
| 7 | B1 `track-b\b1-browser-capability-routing.md` | 34.77 | P | P | P | P | P | P | P | P | **PASS** |
| 8 | B2 `track-b\b2-accessibility.md` | 36.10 | P | P | P | P | P | P | P | P | **PASS** |
| 9 | B3 `track-b\b3-i18n-locale-paper-policy.md` | 31.83 | P | P | P | P | P | P | P | P | **PASS** |
| 10 | B4 `track-b\b4-seo-url-migration.md` | 39.99 | P | P | P | P | P | P | P | P | **PASS** |
| 11 | B5 `track-b\b5-ui-baseline-verification.md` | 29.29 | P | P | P | P | P | P | P | P | **PASS** |
| 12 | C1 `track-c\c1-queue-workers-redis.md` | 28.23 | P | P | P | P | P | P | P | P | **PASS** |
| 13 | C2 `track-c\c2-per-tool-server-limits.md` | 37.03 | P | P | P | P | P | P | P | P | **PASS** |
| 14 | C3 `track-c\c3-r2-lifecycle.md` | 19.33 | P | P | P | P | P | P | P | P | **PASS** |
| 15 | C4 `track-c\c4-vps-processing-hardening.md` | 25.71 | P | P | P | P | P | P | P | P | **PASS** |
| 16 | C5 `track-c\c5-observability-status-telegram.md` | 21.46 | P | P | P | P | P | P | P | P | **PASS** |
| 17 | C6 `track-c\c6-backups-restores.md` | 18.95 | P | P | P | P | P | P | P | P | **PASS** |
| 18 | D1 `track-d\d1-adsterra.md` | 24.45 | P | P | P | P | P | P | P | P | **PASS** |
| 19 | D2 `track-d\d2-legal-privacy-copy.md` | 25.60 | P | P | P | P | P | P | P | P | **PASS** |
| 20 | D3 `track-d\d3-analytics-privacy.md` | 22.28 | P | P | P | P | P | P | P | P | **PASS** |
| 21 | D4 `track-d\d4-contact-support.md` | 21.81 | P | P | P | P | P | P | P | P | **PASS** |
| 22 | D5 `track-d\d5-security-threat-privacy.md` | 28.20 | P | P | P | P | P | P | P | P | **PASS** |
| 23 | E1 `track-e\e1-gpt5-6-sol-contract.md` | 23.62 | P* | P | P | P | P | P | P | P | **PASS** |
| 24 | E2 `track-e\e2-automated-mdx-blog-pipeline.md` | 22.62 | P | P | P | P | P | P | P | P | **PASS** |
| 25 | E3 `track-e\e3-launch-postlaunch-topics.md` | 20.98 | P | P | P | P | P | P | P | P | **PASS** |

**Result: 25 PASS / 0 NEEDS-FIX.**

---

## 4. Evidence per check category

### 4.1 Template coverage (plan §8) — 25/25

- **Tracks A and B (12 files)**: each has numbered `## 1. Header` through `## 12. Prohibitions-compliance statement` (verified by `grep '^## \d+\.'`; e.g., A1 lines 3-223, B1 lines 3-245).
- **Track C (C1, C3, C4, C5, C6)** and **Tracks D and E (13 files)**: header is a field table (Brief ID, Path, Track, Title, Date, Author role, Status, Governing decisions, Spec sections, Files read) followed by numbered sections `## 1. Scope` … `## 12. Prohibitions-compliance statement` (C) or `## 1. Scope` … `## 11.` (D) / `## 12.` (E). The header table satisfies template element 1; all other elements are numbered and substantive. C2 uses `## 1. Header` like Tracks A/B.
- **Status field**: present in all 25 headers with an explicit draft/complete state ("Draft (complete for owner review; no accepted product decision)" A/B; "Complete (draft for owner review under DEC-057)" C; "Complete (recommendation; no approved decision)" D; "Complete" E). No brief is marked "superseded", and none claims to supersede an accepted decision — correct.
- **Section-substance check** (full reads): every brief's Scope states the user problem and current approved behavior; Non-goals exist and include "no benchmark" where applicable; Research questions are restated from plan §7; Evidence contains primary sources with URLs and access dates plus legacy `papyr-reference/` file:line citations; Alternatives compare ≥2 approaches with trade-offs/risks/cost/privacy; Recommendation is labeled as such; Measurable acceptance criteria are functional and benchmark-free; Assumptions/uncertainties/unresolved include explicit owner questions; Dependencies list cross-track interfaces; Source-date log records access dates and completeness; Prohibitions-compliance statement is present and accurate.

### 4.2 Source/date evidence (DEC-056) — 25/25

- Every brief records web sources with URLs and access date **2026-07-31** (A1 §5.1/§11; B1-B5 §11 referencing the `_evidence-bN-web.md` files; C1-C6 §11 referencing `evidence/cN-evidence-*.md`; D1-D5 §10 tables; E1-E3 §5/§11 with per-source access dates and HTTP-200 currency checks).
- Primary sources dominate (official docs, standards, license texts, vendor policies, registries, legacy source). Secondary sources are explicitly marked supporting (e.g., A1 §5.1 "secondary, supporting" rows; E1 S1/S2 "Secondary (supporting only)"; D1 §4.3 "supporting, not provider-binding").
- Legacy evidence cites `papyr-reference/` paths with line references throughout (e.g., A1 §5.2, A2 §5.2 table, C1 §5.1 table, B4 §5.3, D2 §4.2, E2 §5.1).

### 4.3 Decision/spec linkage — 25/25

- Every header lists governing decisions and spec sections served (e.g., B1 lists DEC-011/015/030/031/065 primary plus arch §10/§14.1/§22.4/§25.3.17 and UX §16.3/§18/§21.1; C2 lists DEC-034/035/066/070/165; D5 lists DEC-088/090/092/093/169/171/036/064/074/175/174/166/170/013/067/070/179/182).
- Track A briefs cite A1 for shared engine/license evidence per plan §6.1; C2 cites A2-A6 and C1 as consumed findings per plan §6.3 Wave 2.

### 4.4 Options requirement (DEC-055) — 25/25

- Each brief compares at least two viable approaches (A1: four engine families; A2: four alternatives; A3: four; A4: four; A5: four; A6: four; B1: A-D; B2: A-C; B3: A-C; B4: slug + redirect alternatives; B5: verification-method options; C1: A-C; C2: policy A/B + enforcement layers; C3: A-D; C4: scanner/isolation/Nginx alternatives; C5: A1-A3 + B1-B2; C6: A1-A3 + B1-B2; D1: A/B/C (+C1/C2 variants); D2: A/B/C; D3: A/B/C; D4: A/B/C; D5: A/B/C; E1: A1/A2/A3; E2: A/B/C architectures; E3: A/B/C).
- Where only one path is feasible, it is recorded with rationale (A2 §6 item 4: browser-side compression "not feasible… one feasible path only" under DEC-015; E1 records A2's rejection rationale).

### 4.5 Recommendation-as-nondecision wording (DEC-054/057) — 25/25

- A1-A6: "**Recommendation (not an accepted decision — DEC-054, DEC-057)**" (§7 of each; A1 also §12).
- B1-B5: "Recommendation only, not an accepted decision (DEC-054, DEC-057)" (§7/§12).
- C1-C6: "**Recommendation (not an accepted decision)**" (§7/§12).
- D1-D5: "Recommendation (recommendation only, not an accepted decision)" (§6/§11-12).
- E1-E3: "**Recommendation (not an accepted decision; DEC-054, DEC-057)**" (§7/§12).
- `grep -c 'not an accepted decision'` returned ≥1 in all 25 files (E3: 2).

### 4.6 Owner-question quality — 25/25

Explicit, answerable owner decision prompts appear in every brief (usually §9, sometimes §7/§11):

- A1 §9 item 9 (AGPL compliance path, permissive-only acceptance, pdf-lib carry); A2 §9 items 1 and 6; A3 §9 item 5; A4 §9 item 5; A5 §9 item 5; A6 §9 item 6.
- B1 §9.9; B2 §9.9; B3 §9.10; B4 §9.9; B5 §9.10 (the four core prompts D3/U3/U5-D12/Merge edge case at §7.1).
- C1 §7 owner decision prompts; C2 §9 unresolved (owner prompts 1-5); C3 §7 prompts; C4 §7 prompts; C5 §7 prompts; C6 §7 prompts.
- D1 §8; D2 §9; D3 §8; D4 §8; D5 §8.
- E1 §9.1-9.2 (owner-supplied provider docs as the blocking gap; the DEC-051 reconciliation question); E2 §9; E3 §9.1 (owner-supplied demand data).

Prompts are specific and decision-grade (e.g., B5 §7.1 D3: "unify to 1200px, keep the 1440px navbar + 1200px content convention, or another value"), never rhetorical.

### 4.7 Placeholder scan — clean (0 tokens in primary briefs)

- `grep -i 'TODO|TBD|FIXME|XXX|lorem ipsum|placeholder|WIP'` over all of `audit-outputs\research\` returned 13 hits, of which **zero are in the 25 primary briefs** except two prose uses:
  - A4 `a4-split-pdf.md:75` — "range input UX (label, **placeholder**, inline errors…)" — the HTML `placeholder` attribute of the legacy range input, a legitimate feature reference, not a token.
  - D2 `d2-legal-privacy-copy.md:113-115` — Alternative C is named "**Minimal placeholder legal pages at launch**" — a description of a rejected alternative (not viable under DEC-045/168/110), not a leftover token.
- The remaining 11 hits are in `_evidence-*.md` files (out of scope): self-verification notes ("no placeholder tokens", "placeholder scan clean") and factual references (e.g., `_evidence-legacy-frontend.md:451` describing legacy `href="#"` dead links as placeholders).

### 4.8 DEC-066 compliance — all 25 briefs clean (legitimate references only)

Benchmark-word scan (per track, primary briefs only): A 22 hits across 6 files, B 32 across 5 (evidence files excluded), C 23 across 6, D 16 across 5, E 6 across 2. Full-read review classifies **every** hit into one of four legitimate categories:

1. **Prohibitions-compliance statements** (§12 of every brief): "No benchmark program, corpus, matrix, comparative quality/performance report, or quality-score program was created or run (DEC-066)."
2. **Non-goals** (§3): "No benchmark program or comparative quality study (DEC-066)."
3. **Acceptance-criteria framing** (§8): "verifiable without a benchmark program; DEC-066" / "Functional verification criteria, with no benchmark wording".
4. **Design-choice explanations** (§7/§9): profile thresholds, limits, and caps "are design choices validated by functional testing and production observation, not benchmark results" (e.g., A2 §9 item 2, C2 §7, C1 §7, B1 §7.2 rule 10, A6 §9 item 1).

No brief contains a benchmark design, corpus, comparison matrix, quality-score program, or VPS benchmark workload; none instructs running one; none reports comparative performance data. **All DEC-066 mentions are legitimate historical/prohibition references, not violations.** (E1 contains zero benchmark mentions; its cost/speed facts are quoted public list prices with sources, not measurements.)

### 4.9 No implementation authorization — clean

- Authorization-language scan returned 30 hits, all in decision-log evidence files (quoted decision text), evidence files, or prohibition statements within briefs. In the 25 primary briefs: D5 §4.1 quotes DEC-093 ("never authorizes executing/logging/trusting metadata"); D1 §4.5 ("neither is authorized in this research phase"); C1 §5.1 ("no current access authorized — DEC-172, DEC-160"); C5 §7 ("without explicit owner authorization (DEC-097, DEC-160)"). None grants, implies, or requests implementation authorization.
- Every brief's §12 and recommendation section defer to DEC-057 owner approval; plan §3 gates (DEC-060, DEC-188) are honored.

### 4.10 No silently changed decisions — clean

- **D5 §6.7** explicitly preserves DEC-022: "no evidence in this track changes its status… recorded as a supporting finding and a reconciliation input (X2), not a decision rewrite"; it *reinforces* the risk record (D1 evidence) and escalates rather than rewrites.
- **B3 §5.1** records the DEC-083-vs-DEC-085 reading as an interpretation question for the owner, not a silent resolution.
- **E1 §5.1** flags that the public record identifies `gpt5.6-sol` with OpenAI's GPT-5.6 Sol family, contradicting the DEC-051/plan wording "does not imply a specific vendor"; it is recorded as a reconciliation item for the owner (DEC-183), not silently resolved.
- **C2 §9** surfaces the C1↔C4↔C2 memory-envelope tension as an escalation, not a fix.
- **B1 §9.9(c)**, **C1 §7 prompts**, **D1 §8**, **D3 §8**, **E2 §9**, **E3 §9** all defer decisions to the owner.

### 4.11 `papyr-reference/` unchanged — verified

- `git -C papyr-reference status --porcelain` returned empty output with exit 0 before and after verification; HEAD `981c59a` (`docs(fase2): mark STEP-F2-063 complete`). No tracked or untracked change.

---

## 5. Defect list and final count

### 5.1 Blocking defects

**Count: 0.** No brief fails any plan §11 per-brief assertion (file exists and non-empty; all template sections present and substantive; ≥2 alternatives or recorded single path; primary sources with URLs/dates; legacy file:line citations; recommendation labeled as such; measurable benchmark-free acceptance criteria; no TODO/TBD/FIXME tokens; prohibitions-compliance statement present and accurate; `papyr-reference` clean).

### 5.2 Minor observations (non-blocking; count: 2)

| # | Brief | Location | Observation | Disposition |
|---|---|---|---|---|
| M1 | E1 | `e1-gpt5-6-sol-contract.md` §8 (heading at line 125) | Section 8 is titled "The DEC-051 documentation contract (known/unknown matrix)" instead of "Measurable acceptance criteria" (plan §8 template element 8). The acceptance function for a documentation-contract brief is served by the known/unknown matrix itself plus §9's owner-supplied gaps and §12's compliance statement; no numeric acceptance criteria apply to a contract-formatting deliverable. | No change required; the substitution is deliberate and the section is substantive. Recorded for completeness so reconciliation does not flag it as missing. |
| M2 | E1 | `e1-gpt5-6-sol-contract.md` §11 (line 165) | Evidence-completeness caveat: "the API reference pages themselves were not fully re-fetched beyond the HTTP currency check" — canonical content summarized from official announcement and catalog pages fetched in full. | Acceptable per DEC-056 (sources carry URL + access date); recorded as an honest completeness note, not a defect. |

### 5.3 Non-issues checked and cleared (count: 5)

| Item | Location | Finding |
|---|---|---|
| "placeholder" prose hits | A4:75; D2:113-115 | Legitimate prose, not tokens (see §4.7) |
| "benchmark" prose hits | all 25 briefs | Legitimate DEC-066 prohibition/reference usage only (see §4.8) |
| "authoriz" prose hits | D5:54; D1:100; C1:87; C5:118 | Prohibition statements and quoted decision text only (see §4.9) |
| Template heading variants | C1/C3-C6/D1-D5/E1-E3 header tables; A/B/C2 numbered `## 1. Header` | Both forms satisfy plan §8 element 1; C2 carries an explicit template note; A1/B1 carry template notes reconciling the 12-section plan with the per-track 16-section instruction |
| Section-7/8 heading substitutions | D2 §7 "Disclosure inventory" (acceptance criteria at §8); E1 §8 (M1) | All required content present; numbering shifts are internal consistency, not omissions |

### 5.4 Final count

- **Blocking defects: 0**
- **Minor observations: 2** (M1, M2 — both in E1, both non-blocking)
- **Open items (not defects, surfaced for the owner): 3**
  1. X1 (`source-and-decision-index.md`) and X2 (`reconciliation-report.md`) do not yet exist — expected Wave 3/4 deliverables (plan §6.6); this verification is the gate before reconciliation, so creation is the next planned step, not a defect.
  2. E1 §5.1/§9.2 reconciliation item: the public record identifies `gpt5.6-sol` with OpenAI's GPT-5.6 Sol family (released 2026-07-09); the owner must confirm which access path their "custom provider" uses before design finalization (DEC-051, DEC-183).
  3. All 25 briefs carry owner decision prompts (≈50 distinct prompts across briefs, per §4.6) that require owner disposition under DEC-057 before design and implementation planning; the highest-priority cross-cutting ones are the AGPL licensing path (A1/A2), per-tool server limits (C2 §7.1 table), the C1↔C4↔C2 memory envelope (C2 §9), and the Adsterra consent/suppression choice (D1).

---

## 6. Analysis

### 6.1 DEC-066 legitimacy analysis

The task required distinguishing legitimate historical references to DEC-066 and the benchmark prohibition from violations. The scan confirms the two categories cleanly:

- **Legitimate (present, correct)**: every brief's §3 Non-goals and §12 Prohibitions-compliance statement cite DEC-066 verbatim; acceptance criteria are repeatedly framed "no benchmark wording"; numeric proposals (A2's premium-profile starting points, C1's queue caps, C2's limit table, C3's lifecycle age, B1's routing caps) are each explicitly labeled "conservative design/safety choices… adjusted from production observations," with explicit statements that nothing was measured (e.g., C2 §7: "none is a benchmark result — no benchmark was run"; A1 §11(c): "No benchmark or test-run evidence was created").
- **Absent (correct)**: no brief contains a benchmark program, test corpus, comparison matrix, quality-score scheme, performance report, or instruction to build one. B5 §7.4's side-by-side visual comparison is explicitly framed as a DEC-143 continuity check, "not a benchmark" (B5 §8 item 8).

**Conclusion: no DEC-066 violation in any of the 25 primary briefs.**

### 6.2 Template-completeness analysis (including the M1 observation)

25/25 briefs deliver all 12 plan-§8 template elements. The only heading-level deviation is E1 §8 (M1), where the "Measurable acceptance criteria" slot is occupied by the documentation-contract matrix — the brief's actual deliverable. Because plan §11 assertion 2 requires "all template sections present and substantive" and the matrix is substantive and fulfills the section's verification purpose for this deliverable type, E1 is graded PASS with a recorded observation rather than NEEDS-FIX. No corrective edit is required; the observation exists so the reconciliation writer (X2) does not misread the substitution as an omission.

### 6.3 Structural consistency

- All briefs are dated 2026-07-31 and self-consistent with the plan's wave structure (C2 explicitly consumed A2-A6 and C1; B1/B4/B5 defer to Track A where required; E1 gates E2; D1/D2/D3 are interdependent and cross-referenced).
- No brief modifies another brief, the decision log, the specs, or `papyr-reference/`; each brief's §12 confirms its writes were confined to its own deliverable (and its evidence file where applicable).
- Every web-sourced fact carries an access date; legacy claims carry file:line references; secondary sources are marked as such — consistent with DEC-056.

---

## 7. Verification statement

- Required inputs were read in full: `AGENTS.md` and `audit-outputs\research-program-plan.md`.
- All 25 primary briefs were opened and read in full; none was modified.
- Scans performed: placeholder tokens, benchmark/corpus/comparative wording, implementation-authorization language, "not an accepted decision" labeling, template section coverage, decision-change language, `papyr-reference` git cleanliness (twice).
- `papyr-reference/` verified unchanged: `git -C papyr-reference status --porcelain` empty, exit 0 (before and after); HEAD `981c59a`.
- No installs, builds, servers, VPS access, deployment, account creation, remote actions, or modifications to any brief, decision log, spec, evidence file, AGENTS.md, or `papyr-reference/` were performed.
- This file is the primary deliverable; a chat-only summary is insufficient.

**Result: 25/25 primary research briefs PASS verification (0 blocking defects, 2 minor observations, 0 NEEDS-FIX). Reconciliation (X2) may proceed.**
