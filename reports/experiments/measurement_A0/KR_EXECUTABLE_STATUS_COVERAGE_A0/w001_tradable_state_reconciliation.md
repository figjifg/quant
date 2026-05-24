# W001 Tradable_State Reconciliation

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0  
Method: for each S3 KRX status event (rcept_dt × ticker), look up the W001 v2
panel `tradable_state` value at that (date, ticker). Classify the agreement.

## Headline: **10774** S3 events reconciled against W001 tradable_state

| reconciliation_class | count |
|---|---:|
| `official_status_but_panel_absent` | 9551 |
| `requires_manual_review` | 762 |
| `proxy_only` | 304 |
| `official_resumption_but_repo_other` | 94 |
| `matched_status` | 63 |

## Interpretation

- `matched_status` = W001 v2 derivation agrees with the S3 official event.
- `official_X_but_repo_Y` = disagreement. Most often because the W001 v2
  panel only covers dynamic_top100 selections, so the ticker may not be in
  the panel on the event date (→ `panel_absence`).
- `official_status_but_panel_absent` = S3 has an event, but the ticker is
  not in the panel on that date. This is the dominant disagreement class,
  reflecting the panel's selection bias rather than a true mismatch.
- `proxy_only` = S3 category (managed / investment_alert / liquidation /
  short_term_overheated) has NO W001 v2 equivalent label. These events are
  visible in S3 but not surfaced in `tradable_state`.
- `requires_manual_review` = ambiguous report_nm (categorised as `other`).

## Per-defect ledger

See `w001_tradable_state_reconciliation_ledger.csv` for per-event rows.

## Hard locks (preserved)

- No assumption that W001 v2 `tradable_state` is official.
- No assumption that panel_absence = non-tradable.
- No execution simulation.
