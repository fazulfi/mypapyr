# Canonical Documentation Baseline

- **Record:** `docs/canonical-docs-baseline.md`
- **Purpose:** Canonical governed-record baseline for the Papyr rebuild at the workspace root (PR-02, plan lines 319-332)
- **Decision range:** DEC-001 through DEC-202 (202 decisions)
- **Governed-record status:** This baseline exists under DEC-198 (workspace root as repository root), per DEC-006 (single local decision log) and DEC-026 (concise canonical documentation; legacy history archived separately)
- **Verification:** `scripts/check-docs-migration.sh` must exit 0 (PASS) when every canonical record below is present

## Canonical document paths (relative to repository root)

| Document | Path | Governed-record status |
|---|---|---|
| Living decision log | `papyr-rebuild-decisions.md` | Canonical, append-only; every confirmed decision appended with a stable ID (DEC-006); DEC-001 through DEC-202 |
| Product & UX specification | `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` | Approved (DEC-188, revised through DEC-196, DEC-197) |
| Technical architecture specification | `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` | Approved (DEC-188, revised through DEC-196, DEC-197) |
| Canonical documentation baseline (this record) | `docs/canonical-docs-baseline.md` | Governed by DEC-006, DEC-026, DEC-198; verified by `scripts/check-docs-migration.sh` |

## Decision range

- Every decision ID from **DEC-001 through DEC-202** is recorded as a heading `## DEC-XXX — Title` in `papyr-rebuild-decisions.md`.
- The checker verifies each heading exactly (202 headings), plus the presence of the decision log, both specifications, and this baseline.

## Status under DEC-198

- The rebuild Git repository root is the workspace `<workspace-root>` itself (DEC-198).
- The decision log, both specifications, and the canonical documentation baseline are preserved as governed project records (DEC-198).
- `papyr-reference/` is a separate nested read-only legacy clone, excluded from the rebuild repository, and must never be modified or targeted by any repository operation (DEC-198).

## Status under DEC-006 and DEC-026

- **DEC-006:** Discovery decisions are recorded in the single local document `papyr-rebuild-decisions.md`, with stable IDs; prior decisions are superseded rather than rewritten.
- **DEC-026:** Active documentation has a single authoritative source; this baseline names the authoritative canonical documents for the rebuilt product, while legacy history is retained in the explicitly non-canonical `papyr-reference/` archive.

## Notes

- Plan text at lines 328 and 330 references "DEC-001 through DEC-201"; reconciliation C2 resolves the range to DEC-001..DEC-202 in the direction of the checker and decision log (see `audit-outputs/phase-0/implementation-readiness-reconciliation.md`, Section 6). The plan-text sync is an owner-gated governed-record edit at or before R2 (reconciliation C1/C2) and is not performed here.
