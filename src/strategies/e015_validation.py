from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult
from src.strategies.d008_subperiod_analysis import restrict_segments_to_trading_window
from src.strategies.e014_rs_breadth_top4 import build_e014_rs_breadth_top4_candidates


TOPK_STABILITY_GRID: tuple[tuple[int, ...], ...] = ((2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1))
SPIKE_EXCLUSION_GROUPS: tuple[tuple[int, ...], ...] = ((2020,), (2025,), (2026,), (2020, 2025, 2026))
PASS_THRESHOLDS = {
    "cumulative_vs_d013": 2.54,
    "sharpe_vs_d013": 0.53,
    "max_drawdown_floor": -0.45,
    "d013_3x_cumulative": 2.07,
    "d013_3x_sharpe": 0.47,
    "d013_spike_excluded_cumulative": 0.95,
    "top1_sector_contribution_ceiling": 0.50,
    "top1_stock_contribution_ceiling": 0.40,
    "topk_sharpe_floor": 0.40,
}


def build_e015_validation_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_sector_counts: tuple[int, ...] = (2, 1, 1, 1),
) -> pd.DataFrame:
    return build_e014_rs_breadth_top4_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=top_sector_counts,
    )


def e015_segments_for_trading_window(
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


def drawdown_summary(result: BacktestResult) -> dict[str, object]:
    equity = result.equity_curve.loc[:, ["date", "net_value"]].copy()
    if equity.empty:
        return {
            "peak_date": pd.NaT,
            "trough_date": pd.NaT,
            "recovery_date": pd.NaT,
            "max_drawdown": 0.0,
        }
    equity["date"] = pd.to_datetime(equity["date"], errors="raise").dt.normalize()
    equity["net_value"] = pd.to_numeric(equity["net_value"], errors="raise")
    running_peak = equity["net_value"].cummax()
    drawdown = equity["net_value"] / running_peak - 1.0
    trough_idx = drawdown.idxmin()
    trough_date = pd.Timestamp(equity.loc[trough_idx, "date"]).normalize()
    peak_idx = equity.loc[:trough_idx, "net_value"].idxmax()
    peak_date = pd.Timestamp(equity.loc[peak_idx, "date"]).normalize()
    peak_value = float(equity.loc[peak_idx, "net_value"])
    after_trough = equity.loc[trough_idx:]
    recovered = after_trough.loc[after_trough["net_value"].ge(peak_value)]
    recovery_date = pd.NaT if recovered.empty else pd.Timestamp(recovered.iloc[0]["date"]).normalize()
    return {
        "peak_date": peak_date,
        "trough_date": trough_date,
        "recovery_date": recovery_date,
        "max_drawdown": float(drawdown.loc[trough_idx]),
    }


def topk_label(counts: tuple[int, ...]) -> str:
    return f"top_{len(counts)}"
