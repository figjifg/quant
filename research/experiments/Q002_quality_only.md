# Q002 — Quality Only

Status: APPROVED TO RUN after Q000/Q001 PASS

## Hypothesis

High-quality large-cap US stocks, defined by high ROIC, high free-cash-flow
margin, and low leverage, can produce better risk-adjusted next-quarter
returns than SPY 100% buy-and-hold.

This is a single-factor-family test. It is not a search over quality
definitions, weights, rebalance frequencies, or holding counts.

## Pre-registered Universe

- Universe: Q001 99 tickers, S&P 100-like current universe excluding MMC.
- Known bias: the universe is made of current surviving large-cap names and
  is not survivorship-free. Q002 results cannot be promoted to production
  without later survivorship-free validation.

## Pre-registered Signal

Quality score is a cross-sectional z-score composite at each quarterly
rebalance:

`Quality_Score = z(ROIC) + z(FCF_margin) - z(Leverage)`

Components:

- `ROIC = trailing_4Q_operating_income / (latest_equity + latest_long_term_debt)`
- `FCF_margin = (trailing_4Q_CFO - trailing_4Q_CapEx) / trailing_4Q_revenue`
- `Leverage = latest_long_term_debt / latest_equity`

All inputs must be point-in-time:

- SEC EDGAR `companyfacts` rows are available only on or after their `filed`
  date.
- Conservative availability gate: quarter end + 35 calendar days.
- No financial statement value may enter a signal before the PIT gate.
- Missing factor rows are excluded; no imputation.

## Portfolio / Benchmark

- Holdings: Top 30 `Quality_Score` names, equal weight.
- Rebalance: quarterly.
- Execution: first valid trading day after the PIT availability date.
- Benchmark: SPY 100% buy-and-hold, USD NAV.
- Costs: 0 bps gross-only diagnostic run. Cost and tax validation belong to
  Q007 / T-family and must not be folded into Q002.

## Required Metrics

- Total return, CAGR, daily Sharpe, max drawdown.
- SPY excess CAGR and information ratio.
- Average quarterly Top 30 turnover.
- Sector concentration.
- Subperiods: 2010-2015, 2016-2020, 2021-2026.
- Quartile test: Q1, Q2, Q3, Q4 and Q1-Q4 long-short return.

## Pass Criteria

- SPY 대비 CAGR 우수 + Sharpe 우수 = STRONG.
- SPY 대비 CAGR 비슷 + Sharpe 우수(MDD 작음) = OK.
- SPY 대비 CAGR 낮음 + Sharpe 비슷 = WEAK.
- SPY 대비 CAGR + Sharpe 모두 낮음 = FAIL.
- Long-short(Q1-Q4) 양수 = factor의 진짜 premium 보조 확인.

## Explicit Failure Modes To Avoid

- Current S&P 500 constituents as historical universe = survivorship bias.
- Financial statement data before filing date = look-ahead bias.
- Factor combination search for best Sharpe = overfitting.
- Changing the registered ROIC formula after seeing results.
- Promoting `P08_IEF30` or any combined portfolio before Q008.

## Expected Outputs

Write only under `reports/experiments/Q002_quality_only/`:

- `config.yaml`
- `quarterly_signals.csv`
- `top30_holdings.csv`
- `portfolio_daily_nav.csv`
- `spy_daily_nav.csv`
- `factor_metrics.csv`
- `turnover_by_quarter.csv`
- `subperiod_split.csv`
- `quartile_long_short_test.csv`
- `report.md`

## Next Step

After Q002, run Q003 Value only with its own pre-registered formula.
