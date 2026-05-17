from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.c013_quarterly_macro_v10 import run_c013_variants


VARIANTS = ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_d007_variants(
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
    """Run D001's carrier for one preconfigured composite threshold."""
    runs, candidates = run_c013_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_regime,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    runs["factor_macro_gate_mcap"] = runs.pop("macro_gate_mcap")
    candidates["factor_macro_gate_mcap"] = candidates.pop("macro_gate_mcap")
    return runs, candidates
