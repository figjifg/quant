from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult, run_candidate_backtest
from src.roles.exits import exit_signal_reversal
from src.roles.filters import filter_flow_sign_both_positive, filter_persistence_4_of_5
from src.roles.rankings import rank_by_combined_flow_5
from src.roles.triggers import trigger_acceleration


VARIANTS = ("f1_baseline", "f3_promote")
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
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")


def build_b009_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    """Build B009's F1 baseline and F3 promote candidate on the B006 T3 carrier."""
    _require_columns(flow_features, FEATURE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")

    merged = universe.merge(
        flow_features.loc[:, list(CANDIDATE_FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )

    f1_filtered = filter_flow_sign_both_positive(merged)
    f3_filtered = filter_persistence_4_of_5(merged, flow_features)
    candidates = {
        "f1_baseline": rank_by_combined_flow_5(trigger_acceleration(f1_filtered, flow_features)),
        "f3_promote": rank_by_combined_flow_5(trigger_acceleration(f3_filtered, flow_features)),
    }
    return candidates, exit_signal_reversal(flow_features)


def run_b009_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    costs: Costs,
    period_start: object,
    period_end: object,
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame], dict[str, object]]:
    """Run B009's two fixed filter variants."""
    candidates, exit_kwargs = build_b009_candidates(flow_features, universe)
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
    return runs, candidates, exit_kwargs


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
