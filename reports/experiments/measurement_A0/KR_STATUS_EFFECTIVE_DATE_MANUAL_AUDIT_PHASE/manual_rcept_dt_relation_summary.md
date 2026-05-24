# Manual rcept_dt Relation Summary

Date: 2026-05-25  
Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE

## Relation distribution

| relation | count |
|---|---:|
| `unknown` | 139 |
| `equal_to_rcept_dt` | 27 |
| `after_rcept_dt` | 18 |
| `before_rcept_dt` | 11 |

## Critical observations

- `equal_to_rcept_dt`: rcept_dt happens to coincide with effective date.
  This is NOT proof that rcept_dt can be defaulted as effective_date — only
  that the two values matched for these specific samples.
- `after_rcept_dt`: filing precedes effective date — common for suspension
  announcements that schedule a future effective day. Using rcept_dt would
  trigger the event too early in any future execution simulation.
- `before_rcept_dt`: filing AFTER the event — rare; correction or backfill.
- `range_contains_rcept_dt`: effective period spans the filing day.
- `unknown`: most common when body extraction returns no label/value.

## Hard locks (preserved)

- No rcept_dt defaulted to effective date.
- No panel / OHLCV used as effective-date proof.
