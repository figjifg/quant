from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult, run_candidate_backtest
from src.features.relative_flow import build_relative_flow_features
from src.roles.exits import exit_signal_reversal
from src.roles.filters import filter_flow_sign_both_positive, filter_relative_AND_absolute_positive
from src.roles.rankings import rank_by_combined_flow_5
from src.roles.triggers import trigger_acceleration


VARIANTS = ("f1_baseline", "f2_promote")
FEATURE_COLUMNS = (
    "날짜",
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_1",
    "combined_flow_5",
)
CANDIDATE_FEATURE_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_1",
    "combined_flow_5",
)
RELATIVE_FEATURE_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5_rel",
    "inv_5_rel",
)
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")


def build_b008_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    *,
    min_count: int = 30,
) -> tuple[dict[str, pd.DataFrame], dict[str, object], pd.DataFrame]:
    """Build B008's F1 baseline and F2 promote candidate on the B006 T3 carrier."""
    _require_columns(flow_features, FEATURE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")

    relative_features = build_relative_flow_features(flow_features, universe, min_count=min_count)
    _require_columns(relative_features, RELATIVE_FEATURE_COLUMNS, "relative_features")
    merged = universe.merge(
        flow_features.loc[:, list(CANDIDATE_FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )

    f1_filtered = filter_flow_sign_both_positive(merged)
    f2_filtered = filter_relative_AND_absolute_positive(merged, relative_features)
    candidates = {
        "f1_baseline": rank_by_combined_flow_5(trigger_acceleration(f1_filtered, flow_features)),
        "f2_promote": rank_by_combined_flow_5(trigger_acceleration(f2_filtered, flow_features)),
    }
    return candidates, exit_signal_reversal(flow_features), relative_features


def run_b008_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    costs: Costs,
    period_start: object,
    period_end: object,
    max_positions: int,
    min_count: int = 30,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame], dict[str, object], pd.DataFrame]:
    """Run B008's two fixed filter variants."""
    candidates, exit_kwargs, relative_features = build_b008_candidates(
        flow_features,
        universe,
        min_count=min_count,
    )
    runs = {
        variant: run_candidate_backtest(
            panel,
            calendar,
            candidates[variant],
            costs,
            period_start,
            period_end,
            max_positions=max_positions,
            **exit_kwargs,
        )
        for variant in VARIANTS
    }
    return runs, candidates, exit_kwargs, relative_features


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
