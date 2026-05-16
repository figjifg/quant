from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult, run_candidate_backtest
from src.roles.exits import exit_signal_reversal
from src.roles.filters import filter_flow_sign_both_positive, filter_persistence_4_of_5
from src.roles.rankings import rank_by_combined_flow_5
from src.roles.triggers import trigger_acceleration
from src.strategies.baselines import run_b0_cash


VARIANTS = ("carrier_t3_f3", "t3_f1_baseline", "cash")
TRADED_VARIANTS = ("carrier_t3_f3", "t3_f1_baseline")
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


def build_b010_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    """Build B010's frozen carrier and T3+F1 old-data baseline."""
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
        "carrier_t3_f3": rank_by_combined_flow_5(trigger_acceleration(f3_filtered, flow_features)),
        "t3_f1_baseline": rank_by_combined_flow_5(trigger_acceleration(f1_filtered, flow_features)),
        "cash": pd.DataFrame(columns=list(CANDIDATE_FEATURE_COLUMNS) + ["rank_score"]),
    }
    return candidates, exit_signal_reversal(flow_features)


def run_b010_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame], dict[str, object]]:
    """Run B010 variants across disjoint old-data windows without bridging 2016."""
    candidates, exit_kwargs = build_b010_candidates(flow_features, universe)
    runs = {
        variant: _run_segmented_candidate(
            panel=panel,
            calendar=calendar,
            candidates=candidates[variant],
            costs=costs,
            segments=segments,
            max_positions=max_positions,
            exit_kwargs=exit_kwargs,
        )
        for variant in TRADED_VARIANTS
    }
    runs["cash"] = _run_segmented_cash(
        panel=panel,
        calendar=calendar,
        flow_features=flow_features,
        universe=universe,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    return runs, candidates, exit_kwargs


def _run_segmented_candidate(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
    exit_kwargs: dict[str, object],
) -> BacktestResult:
    trade_frames: list[pd.DataFrame] = []
    equity_frames: list[pd.DataFrame] = []
    initial_cash = 1.0
    for start, end in segments:
        result = run_candidate_backtest(
            panel,
            calendar,
            candidates,
            costs,
            start,
            end,
            max_positions=max_positions,
            initial_cash=initial_cash,
            **exit_kwargs,
        )
        trade_frames.append(result.trades)
        equity_frames.append(result.equity_curve)
        if not result.equity_curve.empty:
            initial_cash = float(result.equity_curve["net_value"].iloc[-1])
    return BacktestResult(
        trades=pd.concat(trade_frames, ignore_index=True),
        equity_curve=pd.concat(equity_frames, ignore_index=True),
    )


def _run_segmented_cash(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
) -> BacktestResult:
    trade_frames: list[pd.DataFrame] = []
    equity_frames: list[pd.DataFrame] = []
    initial_cash = 1.0
    for start, end in segments:
        result = run_b0_cash(
            panel,
            calendar,
            flow_features,
            universe,
            costs,
            start,
            end,
            max_positions=max_positions,
            initial_cash=initial_cash,
        )
        trade_frames.append(result.trades)
        equity_frames.append(result.equity_curve)
        if not result.equity_curve.empty:
            initial_cash = float(result.equity_curve["net_value"].iloc[-1])
    return BacktestResult(
        trades=pd.concat(trade_frames, ignore_index=True),
        equity_curve=pd.concat(equity_frames, ignore_index=True),
    )


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
