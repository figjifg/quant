# Blocker Register Schema

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0

## Key

- Row-level, keyed by **`rcept_no`** (the OPENDART disclosure receipt number).
- Corrections are status rows too, so `correction_rcept_no` == `rcept_no`; the
  register uses a single combined key (`rcept_no`). `is_correction` flags whether a
  row is a correction.

## Columns (residual_blocker_register.csv)

- `rcept_no`, `rcept_dt`, `stock_code`, `event_category` — identity / context.
- `in_universe_status_table` — present in the 12,187-row universe status table.
- `body_format`, `parse_status`, `residual_class` — from the universe reconciliation.
- `is_correction`, `correction_action_class` — from the correction adjudication.
- `blocker_tags` (`|`-joined), `n_blocker_tags` — multi-label blocker tags.
- Fail-closed flags (always fixed): `manual_review_required=True`,
  `executable_or_safe=False`, `downstream_authoritative=False`,
  `parsed_clean_and_usable=False`, `strategy_ready=False`, `production_ready=False`.

## Membership

Register = (universe rows with parse_status in {no_label_match, label_no_value,
body_unavailable}) ∪ (all 166 correction rows). Cleanly-`extracted`
NON-correction universe rows are NOT blockers and are NOT in the register.
