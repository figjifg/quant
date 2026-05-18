from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.features.volatility_targeting import apply_volatility_target_to_weights, volatility_scalars
from src.strategies.b011_gate_only_full_timeline import build_kospi_buy_and_hold_result
from src.strategies.c003_monthly_macro_gate import _empty_candidates, _run_segmented_cash
from src.strategies.c004_quarterly_macro_gate import _quarterly_execution_candidates, quarterly_execution_dates
from src.strategies.d004_position_sizing import run_quarterly_sized_mcap_backtest
from src.strategies.e014_rs_breadth_top4 import build_e014_rs_breadth_top4_candidates


VARIANTS = ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_g000_e014_vol_target_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    target_vol: float = 0.20,
    vol_window: int = 60,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame], pd.DataFrame, BacktestResult]:
    baseline_candidates = build_e014_rs_breadth_top4_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
    )
    baseline_candidates = _quarterly_execution_candidates(baseline_candidates, calendar, quarterly_regime, segments)
    baseline = run_quarterly_sized_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=baseline_candidates,
        costs=costs,
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    scalars = volatility_scalars(
        baseline.equity_curve,
        quarterly_regime["signal_date"],
        target_vol=target_vol,
        window=vol_window,
    )
    targeted = apply_volatility_target_to_weights(baseline_candidates, scalars)
    runs = {
        "factor_macro_gate_mcap": run_quarterly_sized_mcap_backtest(
            panel=panel,
            calendar=calendar,
            candidates=targeted,
            costs=costs,
            segments=segments,
            rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
        "cash": _run_segmented_cash(calendar=calendar, segments=segments),
    }
    return runs, {
        "factor_macro_gate_mcap": targeted,
        "kospi_buy_and_hold": _empty_candidates(),
        "cash": _empty_candidates(),
    }, scalars, baseline
