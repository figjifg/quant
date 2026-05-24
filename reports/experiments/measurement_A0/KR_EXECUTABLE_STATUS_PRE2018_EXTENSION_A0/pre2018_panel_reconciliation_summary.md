# Pre-2018 Panel Reconciliation Summary

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0  
Method: for each acquired pre-2018 KRX status event, check whether the
ticker is in the 2010-2017 equity panel union, in the KR-LISTED-UNIVERSE-
COVERAGE-A0 lifecycle table, and/or has a W001 v2 terminal status.

## Headline: **7143** pre-2018 status events reconciled

| reconciliation_class | count |
|---|---:|
| `event_ticker_in_lifecycle_not_in_panel_without_terminal` | 3690 |
| `event_ticker_in_lifecycle_not_in_panel_with_terminal` | 2314 |
| `event_ticker_in_panel_and_lifecycle_with_terminal` | 527 |
| `event_ticker_in_panel_and_lifecycle_without_terminal` | 472 |
| `event_not_in_lifecycle_without_terminal` | 113 |
| `event_not_in_lifecycle_with_terminal` | 27 |
| `event_ticker_missing` | 7 |

## Interpretation

- `event_ticker_in_panel_and_lifecycle_*`: most-informative match — event
  ticker is present in the 2010-2017 panel AND in the listed-universe
  lifecycle.
- `event_ticker_in_panel_not_in_lifecycle_*`: event ticker is in the panel
  but absent from the monthly-snapshot lifecycle — likely intra-month
  listing/delisting or KONEX (excluded from lifecycle scope).
- `event_ticker_in_lifecycle_not_in_panel_*`: lifecycle has the ticker but
  panel did not include it (small caps below dynamic_top100 selection).
- `event_not_in_lifecycle_*`: out-of-scope or KONEX-like ticker.
- `_with_terminal` suffix: W001 v2 has a terminal status for the ticker.
- `_without_terminal` suffix: no W001 v2 terminal — could be a non-terminal
  event (managed / alert / temporary suspension) OR a coverage gap.

## Hard locks (preserved)

- No executable claim from panel presence.
- No survivorship-safe claim.
- No execution simulation.
