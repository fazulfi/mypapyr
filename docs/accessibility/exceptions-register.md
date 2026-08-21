# Accessibility exceptions register

## Purpose

This register implements DEC-062 for Papyr's WCAG 2.2 AA accessibility programme. It records deliberate departures from the automated baseline, including the reason, ownership decision, and follow-up state.

## How to read

An empty register means no current exception has been approved. A row is not permission to ignore an accessibility defect: it is a time-bounded decision that must be reviewed against the stated WCAG 2.2 criterion. Status values are Open, Accepted, or Mitigated.

## Current exceptions

There are currently no registered accessibility exceptions. The automated baseline keeps the WCAG 2.2 A/AA rules enabled, including `target-size`, and the test suite treats violations as failures.

| ID | Rule | WCAG 2.2 criterion | Element/Route | Justification | Decision date | Status |
| --- | --- | --- | --- | --- | --- | --- |

## Review cadence

Review this register whenever an accessibility scan identifies a violation, when a route or shared component changes, and at least once per release. Accepted exceptions must include a concrete mitigation or removal plan before approval; mitigated rows remain historical evidence and should not be reused for new defects.
