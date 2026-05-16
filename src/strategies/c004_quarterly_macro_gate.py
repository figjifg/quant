from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.b004_regime_gate import build_gate_only_equal_weight_candidates
from src.strategies.b011_gate_only_full_timeline import build_kospi_buy_and_hold_result
from src.strategies.c003_monthly_macro_gate import (
    _empty_candidates,
    _run_segmented_cash,
    _segment_dates,
    run_monthly_mcap_backtest,
)


VARIANTS = ("macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_c004_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame]]:
    """Run C004's quarterly macro-gated top-mcap strategy and comparators."""
    gate = _quarterly_gate_series(quarterly_regime)
    candidates = build_gate_only_equal_weight_candidates(
        panel,
        universe,
        gate,
        max_positions=max_positions,
    )
    candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_regime, segments)

    runs = {
        "macro_gate_mcap": run_quarterly_mcap_backtest(
            panel=panel,
            calendar=calendar,
            candidates=candidates,
            costs=costs,
            segments=segments,
            rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(
            market_breadth,
            calendar=calendar,
            segments=segments,
        ),
        "cash": _run_segmented_cash(calendar=calendar, segments=segments),
    }
    return runs, {"macro_gate_mcap": candidates, "kospi_buy_and_hold": _empty_candidates(), "cash": _empty_candidates()}


def run_quarterly_mcap_backtest(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    initial_cash: float = 1.0,
    rebalance_dates: set[pd.Timestamp] | None = None,
) -> BacktestResult:
    """Run a quarterly open-to-open rebalance loop via C003's local engine."""
    return run_monthly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=costs,
        segments=segments,
        initial_cash=initial_cash,
        rebalance_dates=rebalance_dates,
    )


def quarterly_execution_dates(
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
) -> set[pd.Timestamp]:
    segment_dates = set(_segment_dates(calendar, segments))
    dates: set[pd.Timestamp] = set()
    for signal_date in pd.to_datetime(quarterly_regime["signal_date"], errors="raise"):
        try:
            execution_date = calendar.next_trading_day(pd.Timestamp(signal_date).normalize())
        except ValueError:
            continue
        if execution_date in segment_dates:
            dates.add(execution_date)
    return dates


def _quarterly_gate_series(quarterly_regime: pd.DataFrame) -> pd.Series:
    data = quarterly_regime.loc[:, ["signal_date", "regime_on"]].copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    return pd.Series(data["regime_on"].to_numpy(dtype=bool), index=pd.Index(data["signal_date"], name="signal_date"))


def _quarterly_execution_candidates(
    candidates: pd.DataFrame,
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
) -> pd.DataFrame:
    if candidates.empty:
        return candidates.copy()
    segment_dates = set(_segment_dates(calendar, segments))
    quarterly_signal_dates = set(pd.to_datetime(quarterly_regime["signal_date"], errors="raise").dt.normalize())
    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["execution_date"] = pd.to_datetime(data["execution_date"], errors="raise").dt.normalize()
    return data.loc[data["signal_date"].isin(quarterly_signal_dates) & data["execution_date"].isin(segment_dates)].copy()
