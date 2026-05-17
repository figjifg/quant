from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.d001_factor_aggregation import run_d001_variants


VARIANTS = ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_d008_variants(
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
    """Run frozen D001 logic with trades restricted to one trading window."""
    trading_segments = restrict_segments_to_trading_window(
        segments=segments,
        trading_start=trading_start,
        trading_end=trading_end,
    )
    return run_d001_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_regime,
        market_breadth=market_breadth,
        costs=costs,
        segments=trading_segments,
        max_positions=max_positions,
    )


def restrict_segments_to_trading_window(
    *,
    segments: tuple[tuple[object, object], ...],
    trading_start: object,
    trading_end: object,
) -> tuple[tuple[pd.Timestamp, pd.Timestamp], ...]:
    start = pd.Timestamp(trading_start).normalize()
    end = pd.Timestamp(trading_end).normalize()
    if start > end:
        raise ValueError("trading_start must be on or before trading_end.")

    restricted: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    for segment_start, segment_end in segments:
        left = max(pd.Timestamp(segment_start).normalize(), start)
        right = min(pd.Timestamp(segment_end).normalize(), end)
        if left <= right:
            restricted.append((left, right))
    if not restricted:
        raise ValueError("trading window does not overlap configured period segments.")
    return tuple(restricted)
