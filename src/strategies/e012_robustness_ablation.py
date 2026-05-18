from __future__ import annotations

from typing import Any

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e007_flow_rs_breadth import build_e007_flow_rs_breadth_top_sector_candidates
from src.strategies.e008_topk_grid import build_e008_topk_grid_candidates, topk_label
from src.strategies.e009_cost_stress import COST_SCENARIOS, SCENARIO_ORDER


SCORE_ABLATIONS: tuple[str, ...] = ("rs_only", "rs_breadth", "flow_rs_breadth")
TOP4_SECTOR_STOCK_COUNTS: tuple[int, ...] = (2, 1, 1, 1)
TOPK_GRID: tuple[tuple[int, ...], ...] = ((2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1))


def build_e012_score_ablation_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
) -> dict[str, pd.DataFrame]:
    return {
        "rs_only": _build_with_score(
            panel=panel,
            universe=universe,
            quarterly_regime=quarterly_regime,
            combined_scores=_score_view(combined_scores, "rs_only"),
            sector_mapping=sector_mapping,
            calendar=calendar,
            top_sector_counts=TOP4_SECTOR_STOCK_COUNTS,
        ),
        "rs_breadth": _build_with_score(
            panel=panel,
            universe=universe,
            quarterly_regime=quarterly_regime,
            combined_scores=_score_view(combined_scores, "rs_breadth"),
            sector_mapping=sector_mapping,
            calendar=calendar,
            top_sector_counts=TOP4_SECTOR_STOCK_COUNTS,
        ),
        "flow_rs_breadth": _build_with_score(
            panel=panel,
            universe=universe,
            quarterly_regime=quarterly_regime,
            combined_scores=combined_scores,
            sector_mapping=sector_mapping,
            calendar=calendar,
            top_sector_counts=TOP4_SECTOR_STOCK_COUNTS,
        ),
    }


def build_e012_topk_grid_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
) -> dict[str, pd.DataFrame]:
    return build_e008_topk_grid_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts_grid=TOPK_GRID,
    )


def validate_e012_cost_scenarios(cost_scenarios: dict[str, Any]) -> None:
    if tuple(cost_scenarios.keys()) != SCENARIO_ORDER:
        raise ValueError(f"E012 cost_scenarios must be exactly {list(SCENARIO_ORDER)} in order.")
    for scenario, expected in COST_SCENARIOS.items():
        actual = cost_scenarios[scenario]
        if tuple(actual.keys()) != ("commission_bps", "tax_bps_sell", "slippage_bps"):
            raise ValueError(f"E012 {scenario} cost keys must be commission_bps, tax_bps_sell, slippage_bps.")
        for key, expected_value in expected.items():
            if float(actual[key]) != expected_value:
                raise ValueError(f"E012 {scenario}.{key} must be {expected_value}.")


def topk_summary_label(counts: tuple[int, ...]) -> str:
    return topk_label(counts)


def _build_with_score(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_sector_counts: tuple[int, ...],
) -> pd.DataFrame:
    return build_e007_flow_rs_breadth_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=top_sector_counts,
    )


def _score_view(combined_scores: pd.DataFrame, score_type: str) -> pd.DataFrame:
    scores = combined_scores.loc[
        :, ["signal_date", "sector_code", "sector_name", "flow_score", "rs_score", "breadth_score", "combined_score"]
    ].copy()
    if score_type == "rs_only":
        score = pd.to_numeric(scores["rs_score"], errors="coerce")
    elif score_type == "rs_breadth":
        score = pd.concat(
            [
                pd.to_numeric(scores["rs_score"], errors="coerce"),
                pd.to_numeric(scores["breadth_score"], errors="coerce"),
            ],
            axis=1,
        ).mean(axis=1, skipna=False)
    else:
        raise ValueError(f"Unsupported score_type: {score_type!r}.")
    scores["combined_score"] = score
    return scores
