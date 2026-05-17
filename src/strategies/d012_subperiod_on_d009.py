from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.d008_subperiod_analysis import restrict_segments_to_trading_window
from src.strategies.d009_chatgpt_holistic import run_d009_variants


VARIANTS = ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_d012_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
    trading_start: object,
    trading_end: object,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame]]:
    """Run frozen D009 logic with trades restricted to one trading window."""
    trading_segments = restrict_segments_to_trading_window(
        segments=segments,
        trading_start=trading_start,
        trading_end=trading_end,
    )
    return run_d009_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_regime,
        market_breadth=market_breadth,
        costs=costs,
        segments=trading_segments,
        max_positions=max_positions,
    )
