from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.c014_quarterly_macro_v11 import run_c014_variants


VARIANTS = ("macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_c019_variants(
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
    """Run C019's quarterly nine-signal USDJPY macro-gated top-mcap strategy."""
    return run_c014_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_regime,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
