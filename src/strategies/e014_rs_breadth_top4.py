from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e007_flow_rs_breadth import build_e007_flow_rs_breadth_top_sector_candidates
from src.strategies.e012_robustness_ablation import _score_view


TOP4_SECTOR_STOCK_COUNTS: tuple[int, ...] = (2, 1, 1, 1)


def build_e014_rs_breadth_top4_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_sector_counts: tuple[int, ...] = TOP4_SECTOR_STOCK_COUNTS,
) -> pd.DataFrame:
    return build_e007_flow_rs_breadth_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=rs_breadth_score_view(combined_scores),
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=top_sector_counts,
    )


def rs_breadth_score_view(combined_scores: pd.DataFrame) -> pd.DataFrame:
    return _score_view(combined_scores, "rs_breadth")
