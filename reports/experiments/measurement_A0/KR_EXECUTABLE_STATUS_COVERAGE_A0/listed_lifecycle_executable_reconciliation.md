# Listed-Lifecycle × Executable-Status Reconciliation

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0

## Method

Cross-check S3 KRX status event tickers against:
- W001 v2 `listing_status_terminal` (per-ticker terminal status),
- KR-LISTED-UNIVERSE-COVERAGE-A0 lifecycle coverage table (ever-listed tickers).

## Headline

| classification | count |
|---|---:|
| `s3_event_with_lifecycle_and_terminal` | 1723 |
| `s3_event_not_in_lifecycle` | 132 |

## Interpretation

- `s3_event_with_lifecycle_and_terminal`: S3 status event ticker is in both
  the official lifecycle table AND has a W001 v2 terminal status — fully
  consistent.
- `s3_event_in_lifecycle_no_terminal`: S3 event ticker is in lifecycle but
  W001 v2 has no terminal — typically because S3 event is non-terminal (e.g.,
  managed/investment_alert) OR because terminal mapping is incomplete.
- `s3_event_not_in_lifecycle`: S3 event ticker is NOT in the official
  lifecycle table — either out-of-window, KONEX (excluded), or vendor edge
  case.
- `w001_terminal_without_s3_event`: W001 v2 has terminal status but no
  corresponding S3 event — terminal may have been inferred from panel
  disappearance without DART backing.

## Implications for execution simulation

- Tickers with `s3_event_with_lifecycle_and_terminal` are safe to gate via
  S3 + W001 v2 in any future execution check.
- Tickers in `w001_terminal_without_s3_event` need manual review or further
  source acquisition before they can be safely gated.

## Hard locks (preserved)

- No execution simulation.
- No survivorship-safe claim.
