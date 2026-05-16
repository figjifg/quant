from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult, run_candidate_backtest
from src.features.relative_flow import build_relative_flow_features
from src.roles.exits import exit_signal_reversal, exit_signal_reversal_rel, exit_signal_reversal_z
from src.roles.filters import (
    filter_flow_sign_both_positive,
    filter_relative_flow_sign_both_positive,
    filter_relative_flow_sign_both_positive_z,
)
from src.roles.rankings import rank_by_combined_flow_5, rank_by_combined_flow_5_rel, rank_by_combined_flow_5_z
from src.roles.triggers import trigger_immediate
from src.strategies.b002_signal_reversal import build_b002_candidates


VARIANTS = ("absolute_baseline", "relative_zscore", "relative_median_diff")
FEATURE_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_5",
    "fnv_5_z",
    "inv_5_z",
    "combined_flow_5_z",
    "fnv_5_rel",
    "inv_5_rel",
    "combined_flow_5_rel",
)
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")


def build_b005_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    *,
    min_count: int = 30,
) -> tuple[dict[str, pd.DataFrame], dict[str, dict[str, object]], pd.DataFrame]:
    """Build B005's three independent alpha-definition variants."""
    _assert_relative_variants_do_not_use_absolute_roles()
    _require_columns(flow_features, ("날짜", "종목코드", "fnv_5", "inv_5", "combined_flow_5"), "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")

    relative_features = build_relative_flow_features(flow_features, universe, min_count=min_count)
    merged = universe.merge(
        relative_features.loc[:, list(FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )

    absolute_candidates = build_b002_candidates(flow_features, universe)
    z_candidates = rank_by_combined_flow_5_z(
        trigger_immediate(filter_relative_flow_sign_both_positive_z(merged))
    )
    rel_candidates = rank_by_combined_flow_5_rel(
        trigger_immediate(filter_relative_flow_sign_both_positive(merged))
    )
    candidates = {
        "absolute_baseline": absolute_candidates,
        "relative_zscore": z_candidates,
        "relative_median_diff": rel_candidates,
    }
    exit_kwargs = {
        "absolute_baseline": exit_signal_reversal(flow_features),
        "relative_zscore": exit_signal_reversal_z(relative_features),
        "relative_median_diff": exit_signal_reversal_rel(relative_features),
    }
    return candidates, exit_kwargs, relative_features


def run_b005_variants(
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
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame], dict[str, dict[str, object]], pd.DataFrame]:
    """Run B005's three pre-registered variants."""
    candidates, exit_kwargs, relative_features = build_b005_candidates(
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
            **exit_kwargs[variant],
        )
        for variant in VARIANTS
    }
    return runs, candidates, exit_kwargs, relative_features


def _assert_relative_variants_do_not_use_absolute_roles() -> None:
    absolute_roles: set[Callable[..., object]] = {
        filter_flow_sign_both_positive,
        rank_by_combined_flow_5,
        exit_signal_reversal,
    }
    relative_roles: set[Callable[..., object]] = {
        filter_relative_flow_sign_both_positive_z,
        rank_by_combined_flow_5_z,
        exit_signal_reversal_z,
        filter_relative_flow_sign_both_positive,
        rank_by_combined_flow_5_rel,
        exit_signal_reversal_rel,
    }
    overlap = absolute_roles.intersection(relative_roles)
    if overlap:
        names = sorted(function.__name__ for function in overlap)
        raise AssertionError(f"B005 relative variants reference absolute-flow role functions: {names}")


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
