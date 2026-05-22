# R-family Event Results Comparison

Status: GENERATED FROM R001-R004 `metrics.json` files

## R001-R004 Summary

| Experiment | Holding | Events | Mean excess | Median excess | Hit rate | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| R001 | 21d | 1951 | 0.10% | -1.43% | 43.31% | WEAK |
| R004 | 21d | 5466 | -0.93% | -2.31% | 39.97% | FAIL |
| R003 | 21d | 5690 | -1.32% | -2.60% | 38.66% | FAIL |
| R002 | 21d | 370 | -3.44% | -4.26% | 31.89% | FAIL |
| R003 | 63d | 5008 | -0.31% | -3.31% | 42.15% | FAIL |
| R004 | 63d | 5034 | -0.47% | -3.54% | 41.50% | FAIL |
| R001 | 63d | 1837 | -1.94% | -4.59% | 38.92% | FAIL |
| R002 | 63d | 292 | -6.87% | -8.23% | 28.42% | FAIL |
| R004 | 126d | 4817 | -4.99% | -9.58% | 34.67% | FAIL |
| R003 | 126d | 4839 | -5.59% | -9.78% | 33.58% | FAIL |
| R001 | 126d | 1713 | -6.35% | -10.24% | 35.08% | FAIL |
| R002 | 126d | 268 | -12.32% | -14.21% | 29.10% | FAIL |

## Best By Holding Period

| Holding | Best experiment | Mean excess | Hit rate | Verdict |
| ---: | --- | ---: | ---: | --- |
| 21d | R001 | 0.10% | 43.31% | WEAK |
| 63d | R003 | -0.31% | 42.15% | FAIL |
| 126d | R004 | -4.99% | 34.67% | FAIL |

## Subperiod Consistency

| Experiment | Holding | 2018-2021 mean excess | 2022-2026 mean excess | Both positive |
| --- | ---: | ---: | ---: | --- |
| R001 | 21d | 1.34% | -0.81% | False |
| R001 | 63d | 1.40% | -4.55% | False |
| R001 | 126d | 1.20% | -12.62% | False |
| R002 | 21d | -4.62% | -3.23% | False |
| R002 | 63d | -2.21% | -7.93% | False |
| R002 | 126d | -1.81% | -14.84% | False |
| R003 | 21d | -0.92% | -1.55% | False |
| R003 | 63d | 2.49% | -2.25% | False |
| R003 | 126d | -1.16% | -8.80% | False |
| R004 | 21d | -0.46% | -1.28% | False |
| R004 | 63d | 2.46% | -2.86% | False |
| R004 | 126d | -0.06% | -9.23% | False |

## R-family Verdict

- R001 has slightly positive 21d mean excess, but hit rate is below 50% and longer horizons are negative, so it does not pass the pre-registered gate.
- R002, R003, and R004 fail all headline horizons on mean excess and hit rate.
- The strongest event type in this run is R001 at 21 trading days, but the result is WEAK, not investable evidence.

## Q-family vs R-family

| Family / experiment | Metric | Value | Verdict |
| --- | --- | ---: | --- |
| Q002 | excess CAGR vs SPY | 4.80% | STRONG |
| Q003 | excess CAGR vs SPY | 3.95% | STRONG |
| Q004 | excess CAGR vs SPY | 3.06% | STRONG |
| Q005 | excess CAGR vs SPY | 4.65% | STRONG |
| Q006 | excess CAGR vs SPY | 4.27% | STRONG |
| R001 | 21d mean excess vs KOSPI | 0.10% | WEAK |
| R004 | 21d mean excess vs KOSPI | -0.93% | FAIL |
| R003 | 21d mean excess vs KOSPI | -1.32% | FAIL |
| R002 | 21d mean excess vs KOSPI | -3.44% | FAIL |

Q-family direct results are survivor-universe diagnostics, but their reported SPY excess CAGR is materially stronger than the R-family event-study mean excess values. R-family currently does not beat Q-family on the pre-registered criteria.

## Recommended Next Steps

- Run R005 only as a cost/execution diagnostic if event-study costs are still needed for documentation; costs are unlikely to rescue negative gross excess returns.
- R006 portfolio combination should not promote R001-R004 standalone signals without a revised ticket, because the pre-registered R-family gate did not pass.
- If continuing R-family research, the next data task should parse DART filing bodies for announced buyback amount, cancellation size, dividend amount, and prior-year dividend comparison rather than relying on disclosure titles alone.
