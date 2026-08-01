# Papyr rebuild — planning index

This index is the entry point for planning documents in the Papyr rebuild. It links the master implementation plan to its supporting canonical records and lists any phase-specific plan files that have been spun out of the master.

## Master plan

- [Master implementation plan](../superpowers/plans/2026-07-31-papyr-rebuild-implementation-plan.md) — approved per DEC-202; the authoritative phase-by-phase execution plan for the rebuild.

## Canonical planning context

- [Canonical documentation baseline](../canonical-docs-baseline.md) — the governed-record baseline that names the authoritative canonical documents (DEC-006, DEC-026, DEC-198).
- [Owner resolution register](../resolution-register.md) — the disposition of every open resolution item (R-01..R-28) that gates implementation tasks and stop conditions in the master plan.

## Phase-specific plans

Each phase in the master plan MAY be expanded into its own plan file under `docs/superpowers/plans/` following the master's template and gates. When a phase plan is created it is appended to the table below with its relative path, scope, governing decisions, and current status.

| Phase | Plan file | Scope | Governing decisions | Status |
| --- | --- | --- | --- | --- |
| (none yet) | — | — | — | — |

The table is intentionally empty at the start of Phase 0. Phase plans are added only when an owner-gated decision authorizes the expansion.

## Conventions

Branching, commit messages, TDD discipline, and the phase-plan expansion rule are documented in [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md). Any change to a plan file is a governed-record change and must be logged in `papyr-rebuild-decisions.md` with a stable decision ID, and recorded in the owner resolution register where it affects a stop condition.