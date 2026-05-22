# O000 NAV update design

Status: design plus local sample runner.

## Scope

`src.ops.nav_update.compute_daily_nav(portfolios, as_of_date)` computes daily paper NAV for the 9 tracked portfolios and writes CSV under `paper_trading/operations/nav_history/`.

Inputs are local only:

- `research_input_data/inputs/global_etf/yf_SPY.csv`
- `research_input_data/inputs/global_etf/yf_QQQ.csv`
- `research_input_data/inputs/global_etf/yf_IEF.csv`
- `research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv`
- `reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv`

## Metrics

The output includes daily NAV, daily return, monthly return, quarterly return, YTD return, drawdown/MDD path, 63-day rolling volatility, and 63-day rolling Sharpe.

## Constraints

D013, H001 strategy code, and `src/backtest/engine.py` are not modified. No external network refresh is used.

Tax-professional confirmation is required before any live use.
