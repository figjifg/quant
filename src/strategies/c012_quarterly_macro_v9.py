from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.b004_regime_gate import build_gate_only_equal_weight_candidates
from src.strategies.b011_gate_only_full_timeline import build_kospi_buy_and_hold_result
from src.strategies.c003_monthly_macro_gate import _empty_candidates, _run_segmented_cash
from src.strategies.c004_quarterly_macro_gate import (
    _quarterly_execution_candidates,
    _quarterly_gate_series,
    quarterly_execution_dates,
    run_quarterly_mcap_backtest,
)


VARIANTS = ("macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_c012_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame]]:
    """Run C012's quarterly seven-signal KR rates macro-gated top-mcap strategy."""
    gate = _quarterly_gate_series(quarterly_regime)
    candidates = build_gate_only_equal_weight_candidates(
        panel,
        universe,
        gate,
        max_positions=max_positions,
    )
    candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_regime, segments)

    runs = {
        "macro_gate_mcap": run_quarterly_mcap_backtest(
            panel=panel,
            calendar=calendar,
            candidates=candidates,
            costs=costs,
            segments=segments,
            rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(
            market_breadth,
            calendar=calendar,
            segments=segments,
        ),
        "cash": _run_segmented_cash(calendar=calendar, segments=segments),
    }
    return runs, {"macro_gate_mcap": candidates, "kospi_buy_and_hold": _empty_candidates(), "cash": _empty_candidates()}
