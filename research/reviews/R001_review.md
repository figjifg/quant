# Review — R001 (Role-based signal refactor)

## Verdict
**promote** — refactor success. Zero semantic change verified across
all six prior experiments.

## One-line conclusion
신호 역할 4가지 (filter / trigger / ranking / exit) 가 `src/roles/`
디렉터리에 명시적으로 분리됐고, 모든 기존 실험(A001-A004, B001, B002)
산출물이 byte-identical 으로 재현됨.

## Verification

### Tests
- pytest: **104 passing**, unchanged from pre-refactor baseline.

### Byte-identical regression (all six experiments rerun)

| Experiment | trades.csv | signals.csv | equity_curve.csv | metrics.json | cost_sensitivity.csv |
|---|:-:|:-:|:-:|:-:|:-:|
| E001 (A001) | ✓ | ✓ | ✓ | ✓ | ✓ |
| E002 (A002) | ✓ | ✓ | ✓ | ✓ | ✓ |
| E003 (A003) | ✓ | ✓ | ✓ | ✓ | ✓ |
| E004 (A004) | ✓ | ✓ | ✓ | ✓ | ✓ |
| B001 | ✓ | ✓ | ✓ | ✓ | ✓ |
| B002 | ✓ | ✓ | ✓ | ✓ | ✓ |

Verified by md5sum comparison after `git update-index --refresh`. Codex's
intermediate report flagged 4 signals.csv files as DIFF, but those were
mtime-cache false positives — the final files match byte-for-byte.

## New structure

```
src/roles/
  __init__.py
  filters.py     — filter_flow_sign_both_positive (single function for now)
  triggers.py    — trigger_immediate (single function for now)
  rankings.py    — rank_by_combined_flow_5, rank_by_combined_flow_5_mcap,
                   rank_by_recent_return_5
  exits.py       — exit_time_cap, exit_volatility_stop_plus_cap,
                   exit_signal_reversal (parameter-builder functions)

src/strategies/  (renamed via filesystem rename — git sees delete+add but
                  diff preserved):
  a001_fixed_holding.py        (was e001_flow_filter.py)
  a002_cap_only.py             (new thin composer, was inline in engine)
  a003_market_gate.py          (was e003_market_gate.py)
  a004_strength_quintile.py    (was e004_strength_quintile.py)
  b001_mcap_normalized.py      (unchanged path, refactored internally)
  b002_signal_reversal.py      (unchanged path, refactored internally)
  baselines.py                 (refactored to import rank_by_recent_return_5)
```

Engine signature unchanged: `vol_stop_k`, `atr_features`,
`signal_exit_features` parameters preserved.

Config experiment_id strings unchanged (`E001`, `E002`, …) — historical
contract preserved.

Reports folder names unchanged (`E001_pipeline_sanity_fixed_holding`, etc.)
— historical record preserved.

## What this enables

Future experiment tickets can now declare explicitly which role they
touch:

- B003 candidate (filter exploration): test filter_flow_sign_both_positive
  vs new filter_combined_flow_sign vs filter_persistence_4_of_5, all
  with the same trigger / ranking / exit.
- B004 candidate (trigger exploration): introduce trigger_acceleration
  on top of the chosen filter.
- etc.

Each ticket touches one role only — the "한 번에 한 변수" principle
operationalized through the directory structure.

## Code-side metrics

Diff stat:
- 3 files deleted (`e001_*`, `e003_*`, `e004_*` strategy files)
- 4 files added (`a001_*`, `a002_*`, `a003_*`, `a004_*`)
- 4 new files under `src/roles/`
- 263 lines removed, 54 added in the existing modules (net reduction
  because role functions deduplicate repeated logic)

Code is genuinely cleaner. Strategy files are now thin composers, and
the role functions are first-class testable units.

## Engineering issues found / fixed
None this iteration. R001 was purely structural.

## Next experiment

The refactor unblocks the per-role signal exploration the user wanted
before continuing alpha development:

- **B003 candidate**: filter-role exploration. Hold trigger=immediate,
  ranking=combined_flow_5, exit=signal_reversal (B002 default) constant.
  Vary the filter across 3-5 candidates. Description only; no post-hoc
  promotion.
- **B004 candidate**: trigger-role exploration. Hold the best filter
  from B003 (pre-registered as the carrier), test trigger_immediate vs
  trigger_acceleration vs trigger_volume_confirm.
- **B005 candidate**: exit-role exploration with more variants (combined
  flow ≤ 0, time cap + signal exit OR, etc.).

The user already indicated preference for moving forward with B003-style
filter exploration. R001 makes that ticket cleaner to write.
