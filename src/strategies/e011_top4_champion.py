from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e007_flow_rs_breadth import build_e007_flow_rs_breadth_top_sector_candidates


TOP4_SECTOR_STOCK_COUNTS: tuple[int, ...] = (2, 1, 1, 1)


def build_e011_top4_champion_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
) -> pd.DataFrame:
    return build_e007_flow_rs_breadth_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=TOP4_SECTOR_STOCK_COUNTS,
    )
