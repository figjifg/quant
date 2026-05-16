# C002 Predictions Quantified

## Scope

This document converts C001 v2 P1-P5 into exact formulas for C003. It does not
compute the predictions, run a backtest, or assign PASS/FAIL.

## Common Definitions

Let `T` be a Korean trading `signal_date`.

Macro timing:
- `USDKRW(T)` uses `DEXKOUS` aligned through Korean signal date `T`.
- `US3M(T)` uses `DGS3MO` aligned with the US after-close rule: Korean signal
  date `T` may only use the latest US observation dated `T-1` or earlier,
  resolving to the prior US trading day across weekends and US holidays.

Outcome:

```text
y(T) = product_{i=1..252}(1 + KOSPI_proxy_return(T+i)) - 1
```

`KOSPI_proxy_return` is the same C002 proxy used in the variance
decomposition: `krx_market_breadth_kospi_2010_2026.csv` column
`cap_weighted_return`.

A prediction row is eligible only when all required lookback values at
`T-252`, all condition values at `T`, and all forward returns through `T+252`
exist. C003 should report eligible row counts for every condition.

## P1: USDKRW Single

Formula:

```text
usdkrw_yoy(T) = USDKRW(T) / USDKRW(T-252) - 1
```

Conditions:
- P1-A, KRW strength: `usdkrw_yoy(T) <= 0`
- P1-B, large KRW weakness: `usdkrw_yoy(T) >= 0.05`
- P1-C, neutral: `0 < usdkrw_yoy(T) < 0.05`

Pre-registered thresholds for C003:
- `mean(y | P1-A) >= 0.10`
- `mean(y | P1-B) <= 0.00`
- Difference test between P1-A and P1-B uses block bootstrap CI; the original
  t-test target is retained as diagnostic only because forward windows overlap.

## P2: Fed Phase

Formula:

```text
us3m_delta_252(T) = US3M(T) - US3M(T-252)
```

Conditions:
- P2-A, easing: `us3m_delta_252(T) < 0`
- P2-B, strong tightening: `us3m_delta_252(T) > 1.0`

Pre-registered thresholds for C003:
- `mean(y | P2-A) >= 0.05`
- `mean(y | P2-B) <= 0.00`

## P3: Combined Core Hypothesis

Condition:

```text
P3(T) = (usdkrw_yoy(T) <= 0) AND (us3m_delta_252(T) < 0)
```

Pre-registered thresholds for C003:
- `mean(y | P3) >= 0.20`
- `mean(y | P3) > mean(y | P1-A only)`
- `mean(y | P3) > mean(y | P2-A only)`

Here `P1-A only` means P1-A true and P2-A false. `P2-A only` means P2-A true
and P1-A false.

## P4: XOR

Condition:

```text
P4(T) = (usdkrw_yoy(T) <= 0) XOR (us3m_delta_252(T) < 0)
```

Pre-registered threshold for C003:
- `-0.05 <= mean(y | P4) <= 0.10`

## P5: Neither / Adverse Macro

Condition:

```text
P5(T) = (usdkrw_yoy(T) >= 0.05) AND (us3m_delta_252(T) > 1.0)
```

Pre-registered threshold for C003:
- `mean(y | P5) <= 0.00`

## Bootstrap Methodology For C003

Daily signal rows have overlapping 252-trading-day forward returns. C003 should
therefore use a moving block bootstrap:

1. Build eligible daily rows with `T`, condition flags, and `y(T)`.
2. Use block length `252` Korean trading days.
3. Sample contiguous blocks with replacement until the synthetic sample length
   is at least the original eligible sample length.
4. Truncate each synthetic sample to the original eligible sample length.
5. Recompute each conditional mean and difference statistic.
6. Use at least 10,000 bootstrap replications with a fixed random seed recorded
   in the C003 output.
7. Report 2.5%, 50%, and 97.5% bootstrap quantiles for each conditional mean
   and each required difference.

Statistical decision thresholds:
- Effect-size thresholds are the pre-registered mean return thresholds above.
- Bootstrap significance is met when the 95% CI for a directional inequality
  excludes the opposite side of zero or the required comparison boundary.
- If any condition has fewer than five eligible rows, report it as sample-size
  limited in C003 rather than forcing a statistical verdict.
