# Variance Decomposition 2010-2026

## Purpose

C002 Task 1 tests the C001 v2 architecture premise by estimating how much of
the Korean equity proxy's daily return variance is explained by macro factors.
This is not a backtest and does not evaluate P1-P5.

## Input Data

Dependent variable:
- `research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv`
- column: `cap_weighted_return`

Caveat from B011: this is the dynamic top-100 cap-weighted breadth proxy, not a
true broad KOSPI total-return index. It has survivorship and universe-rotation
bias. C002 uses it because it is the available 2010-2026 local Korean equity
return series.

Macro factors:
- eight FRED series documented in `docs/macro_factors_schema.md`
- US after-close factors are aligned to Korean signal date T using the latest
  source observations from T-1 or earlier, resolving to the prior US trading
  day across weekends and US holidays.
- USDKRW is aligned through Korean signal date T.

## Methodology

The implemented C002 decomposition is a hierarchical OLS decomposition:

```text
KOSPI_proxy_return(t) = alpha + beta_macro * macro_changes(t) + epsilon(t)
```

Macro changes:
- VIX, DXY, USDCNY, USDKRW: daily percent change after timing-safe alignment.
- US 2y, US 10y, US 3m, BAA10Y spread: daily first difference after
  timing-safe alignment.

Hierarchical shares:
- `macro_share = R2` from the macro-only regression.
- `sector_share = deferred`.
- `idiosyncratic_share = 1 - R2` because no sector layer was computed.

Sector decomposition is deferred because this repo does not contain a clean
KOSPI sector index source or a reliable security-to-sector classification table.
Using ad hoc name lists or inferred sectors would create a new data source and
a fragile classification step outside this ticket's data approvals.

## Results

Artifacts:
- `reports/experiments/C002_macro_layer_foundation/variance_decomposition_summary.csv`
- `reports/experiments/C002_macro_layer_foundation/macro_regression_coefficients.csv`
- `reports/experiments/C002_macro_layer_foundation/full_2010_2026_regression_series.csv`
- `reports/experiments/C002_macro_layer_foundation/sub_2010_2017_regression_series.csv`
- `reports/experiments/C002_macro_layer_foundation/sub_2018_2026_regression_series.csv`
- `reports/experiments/C002_macro_layer_foundation/macro_aligned_levels.csv`
- `reports/experiments/C002_macro_layer_foundation/macro_factor_changes_with_kospi.csv`
- `reports/experiments/C002_macro_layer_foundation/fred_series_coverage.csv`

| Window | Start | End | Observations | Macro R2 | Sector R2 | Idiosyncratic share |
|---|---:|---:|---:|---:|---:|---:|
| Full 2010-2026 | 2010-01-06 | 2026-05-04 | 3478 | 23.571614% | deferred | 76.428386% |
| 2010-2017 | 2010-01-06 | 2017-12-28 | 1707 | 28.756563% | deferred | 71.243437% |
| 2018-2026 | 2018-01-04 | 2026-05-04 | 1771 | 23.137779% | deferred | 76.862221% |

## C001 F-Arch-1 Check

C001 v2 defines F-Arch-1 as macro R2 below 30%. The full-period macro R2 is
23.571614%, below that threshold. This document records the quantitative check;
it does not make any prediction PASS/FAIL judgment and does not run C003.

## Limitations

- The Korean equity series is the B011 dynamic top-100 proxy, not a clean KOSPI
  index.
- Sector decomposition is deferred pending clean sector index or sector
  classification data.
- The analysis uses daily OLS on overlapping macro changes, so R2 is descriptive
  variance attribution, not a causal estimate.
