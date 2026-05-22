# X-ETF001 Time-Series Momentum Scan

Status: PRE-REGISTERED

X-Lab quarantine applies. This ticket does not modify or affect D013, H001, P08_IEF30, paper tracking, P08 weights, or any frozen primary result.

## Hypothesis

ETF time-series momentum is clearly superior to the P08 proxy benchmark.

## Universe

Primary universe: 13 ETFs excluding MCHI.

`SPY`, `QQQ`, `IWM`, `IEF`, `TLT`, `SHY`, `GLD`, `UUP`, `DBC`, `VWO`, `EWY`, `EWJ`, `EWZ`

Secondary robustness universe: the same 13 ETFs plus `MCHI`, using the common-start window after MCHI and the 12-month lookback are available.

## Pre-Registered Variants

Exactly 40 variants are registered: 4 signals x 5 portfolios x 2 rebalance frequencies. No additional variants are allowed in X-ETF001.

Signals:
- 3-month total return, 63 trading days.
- 6-month total return, 126 trading days.
- 12-month total return, 252 trading days.
- 12-month minus 1-month return, 252 trading days skipping the most recent 21 trading days.

Portfolios:
- Top1 equal weight.
- Top2 equal weight.
- Top3 equal weight.
- Positive momentum Top3 with SHY fallback. Positive assets only; unused slots are allocated to SHY.
- Equal-weight all positive momentum. If none are positive, allocate 100% to SHY.

Rebalance:
- Monthly: first trading day after month-end signal, next trading day execution.
- Quarterly: first trading day after quarter-end signal, next trading day execution.

Currency: KRW total return is primary.

## Execution Rules

Signal is measured at rebalance-date close. Trade occurs on the next trading day. Same-day execution is not allowed. Daily NAV must use total exposure no greater than 100%, with no leverage.

## Cost Layers

Layer 1 Gross:
- No trading cost and no tax.
- Used only to inspect strategy structure.

Layer 2 After-cost:
- Round-trip 30 bps on turnover.
- ETF-to-ETF rotation has no recurring FX spread; initial/final FX treatment is documented separately.
- Used to check whether turnover kills results.

Layer 3 After-tax:
- Korean overseas ETF capital gains tax of 22%.
- Annual KRW 2.5M exemption.
- HIFO lot accounting.
- Dividend withholding 15%; because local ETF prices use adjusted close, report must carry the adjusted-close caveat.
- Report after-tax NAV, Sharpe, CAGR, and MDD.

## Controls And Diagnostics

Random TopK control:
- Same rebalance dates.
- Same universe.
- Same K for Top1/Top2/Top3.
- Positive momentum variants use matched selected count.
- 1,000 random trials.
- Percentile reported for each strategy versus the random distribution.

Equal-weight benchmark:
- 13 ETF equal-weight portfolio, quarterly rebalance.

Subperiods:
- 2011-2014.
- 2015-2019.
- 2020-2026.
- COVID 2020-02 through 2020-03.
- 2022 full year.

Required per-variant fields:
- CAGR, Sharpe, MDD, Calmar, volatility.
- Turnover and taxable turnover.
- Gross, after-cost, and after-tax NAV.
- Three subperiod results.
- COVID and 2022 stress windows.
- Average asset exposure.
- Top asset contribution.
- QQQ exposure and contribution.
- Random percentile.
- Equal-weight comparison.

Family-level outputs:
- Top 10 by after-cost Sharpe.
- Top 10 by after-tax Sharpe.
- Top 10 by MDD.
- Monthly vs quarterly comparison.
- Signal window comparison.
- Top1/Top2/Top3 comparison.
- QQQ timing dependence correlation.
- Random TopK explainability test.

## Pass Gate

CLOSE if any:
- Best after-cost Sharpe <= P08 proxy Sharpe + 0.05, approximately 1.06 or lower.
- No difference versus random TopK rotation.
- No difference versus equal-weight 13 ETF.
- Result is explained by QQQ exposure alone.
- No 2022 or COVID defense.
- Monthly result dies after turnover/tax.
- Result depends on one signal, rebalance frequency, or asset.
- Fails to beat P08 proxy in at least two of three subperiods.

DIAGNOSTIC PASS if all:
- After-cost Sharpe >= P08 proxy + 0.10, approximately 1.11 or higher.
- CAGR >= P08 proxy or defensive role is clear.
- MDD improves by at least 5 percentage points versus QQQ.
- Random percentile >= 90%.
- Beats P08 proxy in at least two of three subperiods.
- Not a QQQ clone.

DEEP VALIDATION CANDIDATE if one role:

Role A Balanced:
- After-cost Sharpe >= 1.15.
- CAGR >= P08 proxy.
- MDD no worse than P08_IEF30 full, -23.43%.
- Random percentile >= 95%.

Role B Defensive:
- MDD improves by 2-3 percentage points versus P08 proxy.
- CAGR drag versus P08 proxy <= 1.5 percentage points.
- 2022 defense is clear.
- Turnover and tax are acceptable.

Role C Growth:
- CAGR >= P08_IEF30 full + 1 percentage point, 16.43% or higher.
- Sharpe >= QQQ, 1.017 or higher.
- MDD is at least 5 percentage points lower than QQQ.
- Not a QQQ clone.

## A0 Audit

The X-ETF001 script must automatically apply the 12 A0 audit items: local-only data, frozen primary isolation, no engine modification, common evaluation window, no same-day lookahead, fixed 40 variants, KRW primary currency, three cost layers, random TopK control, equal-weight comparison, stress/subperiod reporting, and pass-gate evaluation without post-result threshold changes.

## Required Output Directory

`x_lab/x_etf/x_etf001_results/`

Required files:
- `config.yaml`
- `variant_metrics.csv`
- `top_rankings.csv`
- `subperiod_breakdown.csv`
- `stress_windows.csv`
- `random_control.csv`
- `qqq_exposure_test.csv`
- `equal_weight_comparison.csv`
- `pass_gate_evaluation.csv`
- `secondary_mchi_robustness.csv`
- `report.md`

X-ETF002 may start only after X-ETF001 results are reviewed.
