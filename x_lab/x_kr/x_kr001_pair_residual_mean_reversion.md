# X-KR001 Korean Pair / Residual Mean Reversion

Status: PRE-REGISTERED

X-Lab quarantine applies. This ticket does not modify or affect D013, H001, P08_IEF30, paper tracking, P08 weights, `engine.py`, or any frozen primary result.

## Hypothesis

Korean large-cap sector / beta-neutral residual dislocation mean reverts over short holding windows.

## Universe

KOSPI dynamic top 100 using the W001 repaired Korean equity infrastructure.

Input panels:
- `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- `research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`

Sector mapping:
- `configs/sector_mapping.yaml`
- PIT sector daily data when available under `data/processed/stock_sector_mapping_pit_daily.csv`

## Required W001 Infrastructure

The audit script must use:
- `src/utils/korean_calendar.py`
- `src/utils/corporate_action.py`
- `src/utils/tradability.py`
- `src/utils/sleeve_nav_simulator.py`
- `src/utils/random_placebo_engine.py`
- `src/utils/backtest_sanity_checks.py`

## Pre-Registered Variants

Exactly 6 variants are registered. No additional alpha variants are allowed.

1. Same-sector pair residual z-score > +2 / < -2, 5 trading-day hold.
2. Same-sector pair residual z-score > +2 / < -2, 10 trading-day hold.
3. Market beta residual z-score > +2 / < -2, 5 trading-day hold.
4. Market beta residual z-score > +2 / < -2, 10 trading-day hold.
5. Sector beta residual z-score > +2 / < -2, 5 trading-day hold.
6. Sector beta residual z-score > +2 / < -2, 10 trading-day hold.

Each variant is measured in both:
- Long-short diagnostic form.
- Long-only fallback form.

## Pair Construction

Same-sector pair list:
- Use sector mapping already held in the repo.
- Use KOSPI dynamic top 100 rows.
- Within each sector, rank stocks by market cap.
- Use rank 1-10 stocks in each sector.
- Choose the top 5-10 same-sector pairs per sector by similar market cap.
- Target total: 30-50 pair candidates.

Pair residual:
- 60 trading-day rolling log-spread regression.
- Residual = `log(P1) - beta * log(P2) - alpha`.
- Z-score = `(residual - rolling_mean) / rolling_std`.

## Signals And Exits

Pair residual:
- `z > +2`: short P1, long P2. Long-only fallback buys P2 only.
- `z < -2`: long P1, short P2. Long-only fallback buys P1 only.

Market beta residual:
- Each stock versus KOSPI proxy with 60 trading-day rolling beta.
- Residual = `stock_return - beta * kospi_return`.
- Use cumulative residual z-score.

Sector beta residual:
- Each stock versus same-sector basket with 60 trading-day rolling beta.
- Sector basket = equal-weight basket of sector members.
- Residual = `stock_return - beta * sector_basket_return`.

Exits:
- Exit when z crosses 0.
- Or exit after configured holding days.
- Or stop loss when adverse z extends beyond 3.

Execution:
- Signal date T is measured after KRX close.
- Execution date must be T+1 or later.
- No same-day execution is allowed.
- Daily NAV must maintain gross exposure <= 100%.

Portfolio construction:
- Top 5-10 signals per day.
- Equal weight.
- Long-short is diagnostic because borrow/short feasibility is unresolved.
- Long-only fallback is measured separately.

## Backtest Window And Costs

Window: 2018-2026, local panel availability.

Currency: KRW.

Cost layers:
- Gross diagnostic.
- After-cost: round-trip 30 bps approximation through 15 bps per turnover leg.
- Domestic ordinary small-shareholder tax alternative: capital gains tax 0.
- Diagnostic capital gains tax layer: 22% annual realized gains tax after KRW 2.5M exemption.

## Random / Placebo Controls

Use W001 random/placebo engine:
- Date-matched random pair / stock control, 1,000 trials.
- Same date, same count, same universe.
- Drop-bucket matched diagnostic where feasible.
- Time-shift placebo.

## Subperiods And Stress

Subperiods:
- 2018-2020.
- 2021-2023.
- 2024-2026.

Stress windows:
- COVID 2020-02 through 2020-03.
- 2022 full year.

## Kill Gate

CLOSE if any of the following hold:

1. After-cost Sharpe < 1.0.
2. No difference versus random pair / stock controls.
3. Top 10 pairs explain most returns.
4. Borrow/short feasibility is not realistic, so production long-short is disallowed.
5. Long-only fallback is weak, so retail deployment is disallowed.
6. Two or more subperiods fail.
7. Turnover, tax, or slippage eliminates alpha.

## Verdict Rule

- If any kill gate fails: CLOSE.
- If all kill gates pass: diagnostic PASS only, eligible for X030 paper candidate discussion / P08 import discussion.
- Regardless of result, X-Lab closure is recommended after this final timeboxed experiment.

## A0 Audit

The script must automatically apply the 12 A0 audit items: data lineage, point-in-time availability, survivorship safety, corporate action handling, calendar / tradability, daily NAV, no implicit leverage, benchmark alignment, random / placebo control, concentration / top contributor audit, cost / tax / turnover, and capacity / execution.

## Required Output Directory

`x_lab/x_kr/x_kr001_results/`

Required files:
- `config.yaml`
- `pair_list.csv`
- `variant_metrics.csv`
- `subperiod_breakdown.csv`
- `stress_windows.csv`
- `random_control.csv`
- `top_pair_contribution.csv`
- `turnover_tax_breakdown.csv`
- `pass_gate_evaluation.csv`
- `sanity_check_results.csv`
- `report.md`
