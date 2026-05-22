# S000 Korean Short-Horizon Mean Reversion Feasibility

Status: diagnostic-only feasibility ticket. This is not a paper candidate.

## 사전 등록

Strict gate를 적용한다. 결과가 애매하면 kill이다. 모든 비용은 처음부터 반영한다.
PASS가 나오더라도 다음 단계는 S001 ticket 작성이지 live/paper candidate 승격이
아니다.

## Universe

- KOSPI dynamic top100/200 style universe from existing equity panels.
- Data source: `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
  and `dynamic_top100_2025_2026_krx_panel.csv`.
- Survivorship-safe dynamic membership only.
- Rows with `거래대금추정여부 == True` excluded from headline.
- No microcap, no leverage, no shorting.

## Signal

- 1d return < -3% -> enter next KRX trading day open, hold 1-5d.
- 3d cumulative return < -7% -> enter next KRX trading day open, hold 3d.
- 거래대금 zscore > 2 and 급락 -> enter next KRX trading day open, hold 1-3d.

All signals use `signal_date`; all entries use `execution_date >= T+1`.

## Backtest

- Top 10-20 events per quarter.
- Entry: T+1 open.
- Exit: configured holding horizon close.
- Cost: commission 0.25%, slippage 5bps, 양도세 22% on positive realized gains.
- Daily NAV.
- Benchmark/control: KOSPI/breadth proxy where available, equal-weight dynamic universe,
  and random event control.
- Liquidity filter: positive traded value and dynamic universe membership.

## Immediate Kill Criteria

- Gross edge weak -> kill.
- Net edge negative -> kill.
- Edge appears in one subperiod only -> kill.
- Random control is similar -> kill.
- Look-ahead timing violation -> kill.
- Cost sensitivity erases the effect -> kill.

## Required Output

`reports/experiments/S000_korean_short_mean_reversion_feasibility/`

- gross/net metrics.
- random control distribution.
- subperiod breakdown.
- verdict: PASS or FAIL.
