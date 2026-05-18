from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.d008_subperiod_analysis import restrict_segments_to_trading_window
from src.strategies.e011_top4_champion import build_e011_top4_champion_candidates


def build_e013_top4_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
) -> pd.DataFrame:
    return build_e011_top4_champion_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
    )


def e013_segments_for_trading_window(
    *,
    segments: tuple[tuple[object, object], ...],
    trading_start: object,
    trading_end: object,
) -> tuple[tuple[object, object], ...]:
    return restrict_segments_to_trading_window(
        segments=segments,
        trading_start=trading_start,
        trading_end=trading_end,
    )
