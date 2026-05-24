# OHLCV × Limit-Lock Overlap Audit

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0

## Method

Cross-tabulate rule-derived limit candidates (close_at_upper OR
close_at_lower) against W001 v2 tradable_state buckets.

## Result

| tradable_state | rows that are ALSO rule-derived limit candidates |
|---|---:|
| `panel_absence` | 123 |
| `true_suspension` | 63 |
| `delisting_transition` | 19 |
| `limit_lock_candidate` | 2 |
| `data_missing` | 1 |

## Interpretation

- Rows tagged `panel_absence` should NOT count as limit candidates — they
  reflect dynamic_top100 exclusion, not market behaviour.
- Rows tagged `true_suspension` overlap with limit candidates ONLY when the
  panel still contains the suspension day's close (proxied from prev close).
  Such overlaps are quarantine-priority; the limit candidate label is
  superseded by suspension.
- Rows tagged `data_missing` should not produce reliable limit candidates;
  any overlap is a defect.
- The `limit_lock_candidate` × rule-derived overlap shows how many of the 41
  W001 v2 candidates the rule confirms.

## Rule precedence (per `conservative_execution_rule_design.md`)

OHLCV quarantine and executable_status (`full_day_suspension`, `delisting_transition`, etc.)
OUTRANK the limit-lock candidate label. If a row is in `panel_absence` /
`true_suspension` / `delisting_transition` / `data_missing`, the limit
candidate label SHOULD be ignored in any downstream decision.

## Hard locks (preserved)

- OHLCV invariant signature rows take precedence over limit-lock candidates.
- No execution simulation.
