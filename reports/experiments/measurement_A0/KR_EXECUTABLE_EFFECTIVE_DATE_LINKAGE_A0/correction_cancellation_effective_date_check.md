# Correction / Cancellation Effective-Date Check

Date: 2026-05-25  
Phase: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0

## Sample-level correction-flagged events

- Correction-flagged samples (`[기재정정]` / `[첨부정정]` / etc.): **5**

## Relation distribution for correction-flagged samples

| relation | count |
|---|---:|
| `effective_date_unknown` | 5 |

## Conservative rules for corrections (design only)

Per the S2 phase finding (CLOSED AS PARTIAL), correction linkage was partial:
linking a `[기재정정]` report to its original requires `corp_code + base_form +
series_marker + 180-day window` join logic. That algorithm is design-only;
this phase does NOT run the full join.

Rules:

1. If a `[기재정정]` exists for a prior status event AND it carries a
   different effective date, the corrected effective date supersedes the
   original. The original effective date MUST NOT be used.
2. If a `[기재정정]` is NOT linkable to its original (correction-unlinked),
   classify both rows as `requires_manual_review` and DO NOT use either as
   authoritative.
3. If a status event has a subsequent `[변경]` or cancellation in
   `report_nm`, treat the prior event as withdrawn / no longer active.
4. If the correction occurs AFTER the original effective date has already
   passed, the historical execution status was based on the original event
   for that interval, and the correction applies prospectively.

## Implementation deferred

- Full corp_code + base_form correction join logic = S2 design contract.
- Not implemented here. Documented per `S2 D3 triage` and
  `C2-C3 design finalization` outputs.

## Hard locks (preserved)

- No correction logic wired into any production / paper / live path.
- No strategy testing.
- No execution simulation.
