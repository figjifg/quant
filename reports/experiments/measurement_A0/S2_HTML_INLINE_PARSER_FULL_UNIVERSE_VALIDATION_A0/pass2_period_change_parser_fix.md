# Pass-2 Period-Change Parser Fix

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 2)
Parser version: 1.0.0 → **1.1.0**.

## Scope of change

ONLY `period_change_disclosure` handling. No other parser behavior changes.

## Trigger condition

`PERIOD_CHANGE_RE = re.compile(r"기간변경")` matches `report_nm` AND
`event_category == "suspension_related"`.

Examples that trigger:

- `주권매매거래정지기간변경`
- `매매거래정지기간변경(구주권 제출)`
- `[기재정정]주권매매거래정지기간변경`

Examples that do NOT trigger:

- `주권매매거래정지(불성실공시법인 지정)` (ordinary suspension)
- `주권매매거래정지해제` (resumption)
- `상장폐지결정` (delisting — also out-of-scope)

## Behavior change

When trigger fires, `select_after_change_period_hit()` is called BEFORE the
default `suspension_period → suspension_start → effective_generic` arbitration.

Heuristic:

1. Normalise body text (NBSP / 「：」 / whitespace).
2. Locate ALL positions of after-change markers:
   `변경후 / 변경 후 / 정정후 / 정정 후 / 변경된 / 정정된`.
3. If any after-change marker found: pick the FIRST suspension_period (or
   suspension_start) hit whose `pos > LAST after-change marker position`. This
   selects the period that appears AFTER the marker.
4. If no after-change marker found OR no hit qualifies: fall back to the LAST
   suspension_period hit in the body (heuristic — after-change period typically
   appears later in the body).
5. If both fail: fall through to default behavior.

## What this fix does NOT do

- Does NOT change parsing for ordinary `suspension_related` disclosures
  (verified by `test_ordinary_suspension_unchanged`).
- Does NOT change parsing for `resumption_related`.
- Does NOT add delisting / liquidation / managed / alert parser.
- Does NOT change negative-control gate behavior
  (verified by `test_period_change_negative_control_still_blocks`).
- Does NOT change correction handling
  (verified by `test_period_change_correction_still_forces_manual_review`).
- Does NOT use `rcept_dt` as fallback.
- Does NOT mark any parser result strategy-ready.

## Side effect

`out.notes` is set to `"period_change_disclosure: after-change period selected"`
on rows where the after-change selection fired. Used for traceability / defect
delta in Pass-2 outputs.
