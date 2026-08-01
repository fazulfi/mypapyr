# Papyr Rebuild — Owner Resolution Register

Status of every open resolution item (R-01..R-28) that gates implementation tasks and stop conditions in the master implementation plan.

Reference: `docs/superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md` §6 (Owner Resolution Register).

| ID | Item | Governing decisions | Status | Stop condition | Disposition date |
| --- | --- | --- | --- | --- | --- |
| R-01 | Rebuild repository root | DEC-198 | RESOLVED | none (root fixed at workspace root) | 2026-07-31 |
| R-02 | Git hosting and remote | Owner instruction 2026-07-31 ("mypapyr aja jangan rebuild") | RESOLVED | GitHub, repo `fazulfi/mypapyr`, private, default branch `main` | 2026-07-31 |
| R-03 | Exact per-tool server limits | arch 25.3.2; UX 21.1 | PENDING | Owner approval of C2 brief default table before BE-08/TL hard-code limits | |
| R-04 | Compress premium-screen profile thresholds | arch 25.3.6; UX 21.2 | PENDING | Owner approval before TL-02 | |
| R-05 | Ghostscript distribution/version pin/license review | arch 25.3.1 | PENDING | Authoritative dist, pinned version, `-dSAFER`, AGPL notice preservation, focused license review before launch | |
| R-06 | PDF-to-JPG output profile | arch 25.3.6; DEC-039 | PENDING | Owner approval before TL-06 | |
| R-07 | Per-worker memory/time bounds and queue caps | arch 25.3.3 | PENDING | Owner approval before BE-05 | |
| R-08 | Fair-scheduling classes and parameters | arch 25.3.4 | PENDING | Owner approval before BE-05 | |
| R-09 | Redis persistence/eviction/recovery | arch 25.3.5 | PENDING | Owner approval before BE-04 | |
| R-10 | Scanner selection/budget/update channel | arch 25.3.8 | PENDING | Owner approval before SEC-03 | |
| R-11 | Nginx rate-limit values and fair-use thresholds | arch 25.3.9 | PENDING | Owner approval before SEC-05 | |
| R-12 | Monitoring provider/thresholds/dedup | arch 25.3.10-11 | PENDING | Owner approval before OP-01 | |
| R-13 | Backup schedule/retention/restore target | arch 25.3.20 | PENDING | Owner approval before OP-04 | |
| R-14 | Trusted edge-country header config | arch 25.3.7 residual, 5.3 | PENDING | Owner confirmation of exact header before TL-05 | |
| R-15 | Tool slugs and full legacy URL disposition map | UX 21.4; arch 25.3.15 | PENDING | Owner approval before SH-01 and SEO-01 | |
| R-16 | Indonesian slug/content mapping | arch 25.3.16 | PENDING | Owner approval before SEO-01 | |
| R-17 | Browser capability detection/routing thresholds | arch 25.3.17 | PENDING | Owner approval of routing decision table before TL-01 | |
| R-18 | Adsterra terms/ad-unit code/cookies/identifiers/recipients | UX 21.9; arch 25.3.12 | PENDING | Owner supplies current publisher terms and ad-unit code; provider review before launch; owner approval before PT-02 | |
| R-19 | Qualified legal review of legal pages | UX 21.10; DEC-045 | PENDING | Qualified legal review before launch, then ES/ID localization | |
| R-20 | Contact form provider/anti-spam/delivery monitoring | UX 21.7; arch 25.3.14 | PENDING | Owner approval before PT-03 | |
| R-21 | Gateway capability documentation | UX 21.21; arch 25.3.21 | PENDING | Owner supplies remaining capability fields before CT-03; hard blocker for blog automation design | |
| R-22 | Launch blog topics and post-launch pipeline | UX 21.5; DEC-052/053/124 | PENDING | Owner approval before CT-04 | |
| R-23 | UI baseline owner prompts | UX 21.13-16 | PENDING | Owner answers during copy/design pass before VL-03 | |
| R-24 | Privacy copy re-scoping and FAQ copy accuracy | UX 21.17-18 | PENDING | Owner approval before CT-01 | |
| R-25 | Legacy traffic/demand data | D-4 | PENDING | Owner supplies before SEO-01 and CT-04 | |
| R-26 | Current VPS host state verification | D-3 | RESOLVED | Read-only probe 2026-07-31: Ubuntu 24.04.4, 15 GiB RAM, 4 cores, 2 GiB swap, Docker 29.6.2; assumption superseded | 2026-07-31 |
| R-27 | Numeric 90-day targets | DEC-200, DEC-201 | RESOLVED | Full target set supplied; evaluation day 90 vs first-28-day baseline | 2026-07-31 |
| R-28 | Queue mechanism and engine matrix | DEC-199 | RESOLVED | Matrix approved with all documented risks/conditions remaining in force | 2026-07-31 |

Legend: RESOLVED = owner disposition recorded and governing implementation. PENDING = blocks the listed consuming tasks until disposition.
